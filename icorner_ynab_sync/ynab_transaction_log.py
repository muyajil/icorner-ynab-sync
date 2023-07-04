import os
import requests
from requests_ratelimiter import LimiterSession


class YNABTransactionLog:
    def __init__(self) -> None:
        self.session = LimiterSession(per_hour=199)
        self.budget_id = os.environ["YNAB_BUDGET_ID"]
        self.account_id = os.environ["YNAB_ACCOUNT_ID"]
        self.session.headers.update(
            {"Authorization": f"Bearer {os.environ['YNAB_API_KEY']}"}
        )

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
