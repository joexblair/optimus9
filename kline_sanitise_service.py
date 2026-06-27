"""
kline_sanitise_service.py (Joe 0627) — the folder-watch daemon for kline sanitisation.

Watches ./transfer/kline_sanitise/ for TradingView CSVs. On each new file: KlineSanitiser.reconcile()
overwrites the matching kline_collection OHLC with TV's truth (and carry-forward-flattens no-trade gaps),
then archives the CSV to processed/ (or failed/ on error). Every change is in kline_sanitise_log.

Run as a service:  python3 kline_sanitise_service.py   (or via systemd — kline-sanitise.service)
One-shot (process whatever's pending, no loop):  python3 kline_sanitise_service.py --once
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import os
import glob
import time
import shutil
from logger import get_logger
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.data.kline_sanitiser import KlineSanitiser

WATCH = '/home/joe/thecodes/transfer/kline_sanitise'
POLL_SECONDS = 10


def scan_once(sanitiser, log):
    """Process every pending CSV once: reconcile → archive. Returns the count processed."""
    done = 0
    for path in sorted(glob.glob(os.path.join(WATCH, '*.csv'))):
        name = os.path.basename(path)
        try:
            report = sanitiser.reconcile(path)
            log.info(f'sanitised {name}: {report}')
            shutil.move(path, os.path.join(WATCH, 'processed', name))
            done += 1
        except Exception as e:
            log.error(f'FAILED {name}: {e}')
            shutil.move(path, os.path.join(WATCH, 'failed', name))
    return done


def main(once=False):
    log = get_logger('KlineSanitiseService')
    for sub in ('processed', 'failed'):
        os.makedirs(os.path.join(WATCH, sub), exist_ok=True)
    db = DatabaseManager(**get_db_config()); db.connect()
    sanitiser = KlineSanitiser(db, tp_pk=1)
    log.info(f'watching {WATCH} (poll {POLL_SECONDS}s){" — one-shot" if once else ""}')
    if once:
        scan_once(sanitiser, log); db.disconnect(); return
    while True:
        scan_once(sanitiser, log)
        time.sleep(POLL_SECONDS)


if __name__ == '__main__':
    main(once='--once' in sys.argv)
