import os
import requests
from requests.adapters import HTTPAdapter, Retry


class YNABTransactionLog:
    def __init__(self) -> None:
        self.session = requests.Session()
        self.budget_id = os.environ["YNAB_BUDGET_ID"]
        self.account_id = os.environ["YNAB_ACCOUNT_ID"]
        self.session.headers.update(
            {"Authorization": f"Bearer {os.environ['YNAB_API_KEY']}"}
        )
        self.session.mount(
            "https://",
            HTTPAdapter(
                max_retries=Retry(
                    total=5,
                    backoff_factor=1,
                    status_forcelist=[429],
                    allowed_methods=["GET", "POST", "PATCH"],
                )
            ),
        )

    def create_transaction(self, transaction: dict) -> None:
        r = self.session.post(
            f"https://api.ynab.com/v1/budgets/{self.budget_id}/transactions",
            json={"transaction": transaction},
        )
        r.raise_for_status()

    def patch_transactions(self, transaction: dict) -> None:
        r = self.session.patch(
            f"https://api.ynab.com/v1/budgets/{self.budget_id}/transactions",
            json={"transaction": transaction},
        )
        r.raise_for_status()

    def update_or_create(self, transaction) -> None:
        transaction["account_id"] = self.account_id
        try:
            self.patch_transactions(transaction)
        except requests.exceptions.HTTPError:
            self.create_transaction(transaction)
