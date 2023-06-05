from fastapi import FastAPI
from icorner_ynab_sync.token_manager import TokenManager

app = FastAPI()
tm = TokenManager()


@app.post("/")
async def set_token(payload: dict):
    t = payload["message"][:6]
    tm.set_token(t)
