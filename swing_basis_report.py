"""
swing_basis_report — px_smooth vs raw-close swing detection, from the source.
Runs swing_detect.compare_pivots on the live tape (px_smooth = optimus9_system DEMA, close =
raw 5s) over a 24h window and tables the diffs at swing time: which swings each basis catches,
the timing lag, and the price gap at the matched pivots.
"""
import sys
import numpy as np
from datetime import datetime, timezone
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.swing_detect import compare_pivots

LOOKBACK_H = 24


def dt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%m-%d %H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=LOOKBACK_H, warmup_hours=12)
    base, ts, win_start, _, px = det._setup()
    M = ts >= win_start
    tsm = ts[M].astype('int64')
    pxs = np.asarray(px, float)[M]                       # px_smooth (a)
    close = base['close'].to_numpy(float)[M]             # raw close (b)
    sys = det._sys
    rows = compare_pivots(pxs, close, 0.9, 12)

    nb = sum(r['status'] == 'both' for r in rows)
    na = sum(r['status'] == 'a_only' for r in rows)
    ncl = sum(r['status'] == 'b_only' for r in rows)
    lags = [r['lag'] for r in rows if r['status'] == 'both']
    diffs = [abs(r['diff_pct']) for r in rows if r['status'] == 'both']
    span = f"{dt(tsm[0])[6:]}–{dt(tsm[-1])[6:]} UTC"
    print(f"swing basis: px_smooth = DEMA({sys['pxsmooth_dema_src']},{sys['pxsmooth_dema_len']}) on "
          f"{sys['pxsmooth_dema_tf']}s  vs  raw close  |  24h ({span})")
    print(f"swings: {len(rows)} total  ·  both {nb}  ·  px_smooth-only {na}  ·  close-only {ncl}")
    if lags:
        print(f"matched: median lag {np.median(np.abs(lags)):.0f} bars ({np.median(np.abs(lags))*5:.0f}s, "
              f"signed median {np.median(lags):+.0f})  ·  median |price diff| {np.median(diffs):.4f}%  ·  max {max(diffs):.4f}%")
    print()
    print(f'{"swing UTC":>15} {"kind":>4} {"close_px":>10} {"pxsm_px":>10} {"lag_s":>6} {"diff%":>8} {"status":>10}')
    for r in rows:
        bar = r['b_bar'] if r['b_bar'] is not None else r['a_bar']
        cpx = f"{r['b_px']:.5f}" if r['b_px'] is not None else "—"
        ppx = f"{r['a_px']:.5f}" if r['a_px'] is not None else "—"
        lag = f"{r['lag']*5:+d}" if r['lag'] is not None else ""
        dff = f"{r['diff_pct']:+.4f}" if r['diff_pct'] is not None else ""
        print(f'{dt(tsm[bar]):>15} {r["kind"]:>4} {cpx:>10} {ppx:>10} {lag:>6} {dff:>8} {r["status"]:>10}')
    db.disconnect()


if __name__ == '__main__':
    main()
