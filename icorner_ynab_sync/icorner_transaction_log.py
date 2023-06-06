import os
import time
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
        self.token_manager.wait_for_token()
        token = None
        counter = 0
        while token is None:
            if counter > 30:
                return
            token = self.token_manager.consume()
            time.sleep(5)
            counter += 1
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
                (
                    "https://www.icorner.ch/services/bff/accounts/"
                    f"{os.environ['ICORNER_ACCOUNT']}"
                    f"/transactions?page={page}&rows=100"
                )
            )
            r.raise_for_status()
            data = r.json()

            for transaction in data["transactions"]:
                yield transaction
            hasMore = data["hasMore"]
            page += 1
