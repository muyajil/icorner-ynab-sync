from datetime import datetime
import uvicorn
import time
from icorner_ynab_sync.icorner_transaction_log import ICornerTransactionLog
from icorner_ynab_sync.ynab_transaction_log import YNABTransactionLog
from icorner_ynab_sync.sms_receiver import app

ICORNER_TRANSACTION_LOG = ICornerTransactionLog()
YNAB_TRANSACTION_LOG = YNABTransactionLog()


def run_sync() -> None:
    ICORNER_TRANSACTION_LOG.login()
    n = 0
    for transaction in ICORNER_TRANSACTION_LOG.yield_transactions():
        t = {
            "import_id": "icorner:v2:" + transaction["id"],
            "date": datetime.strptime(transaction["date"], "%Y%m%d").strftime(
                "%Y-%m-%d"
            ),
            "payee_name": transaction["merchant"] if "merchant" in transaction else "Cornercard",
            "amount": -int(float(transaction["amount"]) * 1000),
        }
        if transaction["status"] == "SETTLED":
            t["cleared"] = "cleared"
        if transaction["currency"] != "CHF":
            t["memo"] = f"Currency: {transaction['currency']}"
        YNAB_TRANSACTION_LOG.update_or_create(t)
        n += 1
    print(f"Synced {n} transactions")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    time.sleep(20)
    while True:
        run_sync()
        time.sleep(60 * 15)
