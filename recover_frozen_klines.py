"""
One-off recovery: the 06-04 06:21:55 → 06-05 09:36:15 kline freeze.

Root cause: the live tick socket choked (06-27) and the collector wrote its last
close (0.13840) every 5s for ~27h. The `ticks` table has ZERO rows for that window
(socket was dead), so the bars cannot be rebuilt from ticks — the synthetic Bybit
1m→5s backfill is the only real-price recovery available.

INSERT IGNORE won't overwrite the frozen rows, so they're deleted first, then a
window-mode synthetic backfill drops clean bars into the empty hole (rows on either
side are skipped by IGNORE).

Run:  python3 recover_frozen_klines.py
Then re-run:  python3 run.py bl_detect --lookback_hours 48  &&  python3 run.py bl_review
"""
import sys
sys.path.insert(0, '/home/joe/thecodes')

from optimus9.config import get_db_config
from optimus9 import DatabaseManager, BybitKlineClient, SyntheticBackfiller

KC_LO, KC_HI = 639216, 658828          # contiguous frozen span (close pinned at 0.13840)
FROZEN_FROM = '2026-06-04 07:00:00'    # a fully-frozen hour, for the before/after check
FROZEN_TO   = '2026-06-05 08:00:00'


def main() -> int:
    db = DatabaseManager(**get_db_config())
    db.connect()

    n = db.execute('SELECT COUNT(*) c FROM kline_collection '
                   'WHERE kc_tp_pk=1 AND kc_pk BETWEEN %s AND %s',
                   (KC_LO, KC_HI), fetch=True)[0]['c']
    print(f'[1] frozen rows in kc_pk {KC_LO}..{KC_HI}: {n}  (expected ~19613)')
    if n == 0:
        print('    nothing to delete — already recovered? aborting.')
        return 0

    db.execute('DELETE FROM kline_collection WHERE kc_tp_pk=1 AND kc_pk BETWEEN %s AND %s',
               (KC_LO, KC_HI))
    print(f'[2] deleted {n} frozen rows')

    got = SyntheticBackfiller(db, BybitKlineClient()).backfill(
        tp_pk=1, symbol='FARTCOINUSDT', lookback_days=2)      # window mode → fills the hole
    print(f'[3] synthetic backfill: {got} bars fetched (Bybit 1m→5s; existing rows IGNOREd)')

    chk = db.execute(
        '''SELECT COUNT(*) n, COUNT(DISTINCT kc_close) d, MIN(kc_close) mn, MAX(kc_close) mx
           FROM kline_collection WHERE kc_tp_pk=1
           AND kc_timestamp BETWEEN UNIX_TIMESTAMP(%s)*1000 AND UNIX_TIMESTAMP(%s)*1000''',
        (FROZEN_FROM, FROZEN_TO), fetch=True)[0]
    print(f"[4] ex-frozen window now: {chk['n']} bars, {chk['d']} distinct closes, "
          f"range {float(chk['mn']):.5f}..{float(chk['mx']):.5f}")
    print('    (was: 1 distinct close = 0.13840) — recovered if distinct >> 1')

    db.disconnect()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
