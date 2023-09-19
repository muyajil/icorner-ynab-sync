import os
import requests
from requests_ratelimiter import LimiterSession
from datetime import datetime
import hashlib


class YNABClient:
    def __init__(self) -> None:
        self.session = LimiterSession(per_hour=200)
        self.budget_id = os.environ["YNAB_BUDGET_ID"]
        self.account_id = os.environ["YNAB_ACCOUNT_ID"]
        self.session.headers.update(
            {"Authorization": f"Bearer {os.environ['YNAB_API_KEY']}"}
        )
        self.used_import_ids = set()

    @property
    def transactions_endpoint(self) -> str:
        return f"https://api.ynab.com/v1/budgets/{self.budget_id}/transactions"

    @property
    def categories_endpoint(self) -> str:
        return f"https://api.ynab.com/v1/budgets/{self.budget_id}/categories"

    def get_available_amount(self, category_id) -> int:
        return (
            self.session.get(self.categories_endpoint + f"/{category_id}").json()[
                "data"
            ]["category"]["balance"]
            / 1000
        )

    def create_transaction(self, transaction: dict) -> None:
        r = self.session.post(
            self.transactions_endpoint,
            json={"transaction": transaction},
        )
        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            print(r.json())
            raise

    def patch_transactions(self, transaction: dict) -> None:
        r = self.session.patch(
            self.transactions_endpoint,
            json={"transaction": transaction},
        )
        r.raise_for_status()

    def update_or_create(self, transaction) -> None:
        transaction["account_id"] = self.account_id
        try:
            self.patch_transactions(transaction)
        except requests.exceptions.HTTPError:
            suffix = 0
            while True:
                try:
                    self.create_transaction(transaction)
                    break
                except requests.exceptions.HTTPError:
                    transaction["import_id"] += str(suffix)
                    suffix += 1
                    self.used_import_ids.add(transaction["import_id"])

    def map_icorner_to_ynab(self, transaction: dict) -> str:
        amount = int(float(transaction["amount"]) * 1000)
        merchant = (
            transaction["merchant"] if "merchant" in transaction else "Cornercard"
        )
        import_id_version = os.environ["IMPORT_ID_VERSION"]
        # NOTE: merchant comes with location before its settled
        merchant = merchant.split(",")[0]
        if "originalAmount" in transaction:
            import_id = (
                f"ico:{import_id_version}:"
                + transaction["date"]
                + ":"
                + merchant.lower()
                + ":"
                + str(int(float(transaction["originalAmount"]) * 1000))
            )
        else:
            import_id = (
                f"ico:{import_id_version}:"
                + transaction["date"]
                + ":"
                + merchant.lower()
                + ":"
                + str(amount)
            )

        import_id = hashlib.sha1(bytes(import_id, "utf-8")).hexdigest()
        import_id = import_id[:30]
        suffix = 0
        original_import_id = import_id
        while import_id in self.used_import_ids:
            import_id = original_import_id + str(suffix)
            suffix += 1

        self.used_import_ids.add(import_id)

        t = {
            "import_id": import_id,
            "date": datetime.strptime(transaction["date"], "%Y%m%d").strftime(
                "%Y-%m-%d"
            ),
            "payee_name": merchant,
            "amount": -amount,
        }

        if transaction["status"] == "SETTLED":
            t["cleared"] = "cleared"
        if transaction["currency"] != "CHF":
            t["memo"] = f"Currency: {transaction['currency']}"
        if "originalAmount" in transaction:
            t[
                "memo"
            ] = f"Original amount: {float(transaction['originalAmount']):.2f} {transaction['originalCurrency']}"
        return t
