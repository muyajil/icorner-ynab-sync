import os
import requests
from icorner_ynab_sync.token_manager import TokenManager


class ICornerTransactionLog:
    def __init__(self):
        self.login_data = {
            "isiwebuserid": os.environ["ICORNER_USERNAME"],
            "isiwebpasswd": os.environ["ICORNER_PASSWORD"],
            "submit": "",
        }
        self.token_manager = TokenManager()
        self.session = requests.Session()
        self.logged_in = False

    def login(self) -> None:
        _ = self.session.post("https://www.icorner.ch/cop-ch/", data=self.login_data)
        print("Waiting for token")
        token = None
        while token is None:
            token = self.token_manager.consume()
        print(f"SMS Token {token}")
        _ = self.session.post(
            "https://www.icorner.ch/cop-ch/",
            data={
                "token": token,
                "submit": "",
            },
        )
        self.logged_in = True

    def yield_transactions(self, page: int = 1) -> None:
        if not self.logged_in:
            raise Exception("Not logged in")

        hasMore = True
        while hasMore:
            r = self.session.get(
                f"https://www.icorner.ch/services/bff/accounts/{os.environ['ICORNER_ACCOUNT']}/transactions?page={page}&rows=100"
            )
            r.raise_for_status()
            data = r.json()

            for transaction in data["transactions"]:
                yield transaction
            hasMore = data["hasMore"]
            page += 1
