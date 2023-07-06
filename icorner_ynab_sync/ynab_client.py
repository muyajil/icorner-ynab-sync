import os
import requests
from requests_ratelimiter import LimiterSession
from datetime import datetime


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
    def api_endpoint(self) -> str:
        return f"https://api.ynab.com/v1/budgets/{self.budget_id}/transactions"

    def create_transaction(self, transaction: dict) -> None:
        r = self.session.post(
            self.api_endpoint,
            json={"transaction": transaction},
        )
        r.raise_for_status()

    def patch_transactions(self, transaction: dict) -> None:
        r = self.session.patch(
            self.api_endpoint,
            json={"transaction": transaction},
        )
        r.raise_for_status()

    def update_or_create(self, transaction) -> None:
        transaction["account_id"] = self.account_id
        try:
            self.patch_transactions(transaction)
        except requests.exceptions.HTTPError:
            self.create_transaction(transaction)

    def map_icorner_to_ynab(self, transaction: dict) -> str:
        amount = int(float(transaction["amount"]) * 1000)
        merchant = (
            transaction["merchant"] if "merchant" in transaction else "Cornercard"
        )
        if "originalAmount" in transaction:
            import_id = (
                "ico:v3:"
                + transaction["date"]
                + ":"
                + merchant[:5].lower()
                + ":"
                + str(int(float(transaction["originalAmount"]) * 1000))
            )
        else:
            import_id = (
                "ico:v3:"
                + transaction["date"]
                + ":"
                + merchant[:5].lower()
                + ":"
                + str(amount)
            )
        suffix = 0
        original_import_id = import_id
        while import_id in self.used_import_ids:
            import_id = original_import_id + str(suffix)
            suffix += 1

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
