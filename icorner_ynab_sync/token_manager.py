import os
from pathlib import Path


class TokenManager(object):
    def __init__(self) -> None:
        self.token_path = Path("/tmp/icorner_ynab_sync.token")
        self.lock_path = Path("/tmp/icorner_ynab_sync.lock")

    def set_token(self, token: str) -> None:
        self.lock_path.touch()
        with open(self.token_path, "w") as f:
            f.write(token)
        self.lock_path.unlink()

    def consume(self) -> str:
        if not os.path.exists(self.token_path) or os.path.exists(self.lock_path):
            return None
        with open(self.token_path) as f:
            token = f.read()
        os.remove(self.token_path)
        return token
