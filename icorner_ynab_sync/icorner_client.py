import os
import time
import requests
from icorner_ynab_sync.token_manager import TokenManager


class ICornerClient:
    def __init__(self):
        self.login_data = {
            "isiwebuserid": os.environ["ICORNER_USERNAME"],
            "isiwebpasswd": os.environ["ICORNER_PASSWORD"],
            "submit": "",
        }
        self.token_manager = TokenManager()
        self.session = requests.Session()
        self.logged_in = False
        if "LIMIT" in os.environ:
            self.limit = int(os.environ["LIMIT"])
        else:
            self.limit = None

    def login(self) -> None:
        _ = self.session.post("https://www.icorner.ch/cop-ch/", data=self.login_data)
        print("Waiting for token")
        self.token_manager.wait_for_token()
        token = None
        counter = 0
        while token is None:
            token = self.token_manager.consume()
            time.sleep(5)
            counter += 1
            if counter > 720:
                print("No token arrived in 1h sec, starting a new login flow.")
                return
        if counter > 36:
            print(f"Token {token} is too old.")
            return
        print(f"SMS Token {token}")
        _ = self.session.post(
            "https://www.icorner.ch/cop-ch/",
            data={
                "token": token,
                "submit": "",
            },
        )
        self.logged_in = True

    def get_page_data(self, page: int) -> dict:
        while True:
            try:
                while not self.logged_in:
                    self.login()
                r = self.session.get(
                    (
                        "https://www.icorner.ch/services/bff/accounts/"
                        f"{os.environ['ICORNER_ACCOUNT']}"
                        f"/transactions?page={page}&rows=50"
                    )
                )
                r.raise_for_status()
                return r.json()
            except Exception as e:
                print(e)
                self.logged_in = False

    def yield_transactions(self) -> None:
        page = 1
        hasMore = True
        transactions = []
        ids = set()
        while hasMore:
            data = self.get_page_data(page)
            # When we request a page currently
            # the response contains all the transactions
            # including those from previous pages.
            for transaction in data["transactions"]:
                if transaction["id"] not in ids:
                    ids.add(transaction["id"])
                    transactions.append(transaction)
            hasMore = data["hasMore"]
            page += 1
            if self.limit and len(transactions) >= self.limit:
                break
        if self.limit:
            yield from transactions[:self.limit]
        else:
            yield from transactions
