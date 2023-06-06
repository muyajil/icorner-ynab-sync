from pathlib import Path


class TokenManager(object):
    def __init__(self) -> None:
        self.token_path = Path("/tmp/icorner_ynab_sync.token")
        self.lock_path = Path("/tmp/icorner_ynab_sync.lock")
        self.token_wait_path = Path("/tmp/icorner_ynab_sync.token_wait")

    def wait_for_token(self) -> None:
        self.token_wait_path.touch()

    def set_token(self, token: str) -> None:
        if self.token_wait_path.exists():
            self.lock_path.touch()
            with open(self.token_path, "w") as f:
                f.write(token)
            self.lock_path.unlink()

    def consume(self) -> str:
        if not self.token_path.exists() or self.lock_path.exists():
            return None
        with open(self.token_path) as f:
            token = f.read()
        self.token_path.unlink()
        self.token_wait_path.unlink()
        return token
