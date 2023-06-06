from datetime import datetime, timedelta
import subprocess
import traceback
import time
from icorner_ynab_sync.icorner_transaction_log import ICornerTransactionLog
from icorner_ynab_sync.ynab_transaction_log import YNABTransactionLog

ICORNER_TRANSACTION_LOG = ICornerTransactionLog()
YNAB_TRANSACTION_LOG = YNABTransactionLog()


def run_sync() -> None:
    while not ICORNER_TRANSACTION_LOG.logged_in:
        ICORNER_TRANSACTION_LOG.login()
    n = 0
    for transaction in ICORNER_TRANSACTION_LOG.yield_transactions():
        amount = int(float(transaction["amount"]) * 1000)
        merchant = transaction["merchant"] if "merchant" in transaction else "Cornercard"
        # TODO: Check what happens with EUR transactions that are settled
        import_id = (
            "ico:v3:"
            + transaction["date"]
            + ":"
            + merchant[:5].lower()
            + ":"
            + str(amount)
        )
        t = {
            "import_id": import_id,
            "date": datetime.strptime(transaction["date"], "%Y%m%d").strftime("%Y-%m-%d"),
            "payee_name": merchant,
            "amount": -amount,
        }
        if transaction["status"] == "SETTLED":
            t["cleared"] = "cleared"
        if transaction["currency"] != "CHF":
            t["memo"] = f"Currency: {transaction['currency']}"
        YNAB_TRANSACTION_LOG.update_or_create(t)
        n += 1
    print(f"Synced {n} transactions")


if __name__ == "__main__":
    subprocess.Popen(
        ["uvicorn", "--host", "0.0.0.0", "icorner_ynab_sync.sms_receiver:app"]
    )
    time.sleep(20)
    while True:
        try:
            run_sync()
        except Exception as e:
            print(e)
            print(traceback.format_exc())
        next_execution = datetime.now() + timedelta(hours=1)
        print(f"Next execution at {next_execution}")
        time.sleep(60 * 60 * 1)
