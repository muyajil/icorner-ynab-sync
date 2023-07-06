from datetime import datetime, timedelta
import subprocess
import traceback
import time
from icorner_ynab_sync.icorner_client import ICornerClient
from icorner_ynab_sync.ynab_client import YNABClient


def run_sync() -> None:
    icorner_client = ICornerClient()
    ynab_client = YNABClient()
    while not icorner_client.logged_in:
        icorner_client.login()
    n = 0
    for transaction in icorner_client.yield_transactions():
        t = ynab_client.map_icorner_to_ynab(transaction)
        print(t)
        ynab_client.update_or_create(t)
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
        SLEEP_HOURS = 6
        next_execution = datetime.now() + timedelta(hours=SLEEP_HOURS)
        print(f"Next execution at {next_execution}")
        time.sleep(60 * 60 * SLEEP_HOURS)
