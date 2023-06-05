import os


class TokenManager(object):
    def __init__(self) -> None:
        self.token_path = "/tmp/icorner_ynab_sync.token"

    def set_token(self, token: str) -> None:
        with open(self.token_path, "w") as f:
            f.write(token)

    def consume(self) -> str:
        if not os.path.exists(self.token_path):
            return None
        with open(self.token_path) as f:
            token = f.read()
        os.remove(self.token_path)
        return token
