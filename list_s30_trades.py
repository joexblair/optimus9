"""
list_s30_trades — trade list for both s30r configs over the SAME last-12h window as the
pines. Entry = s30r OOB onset (mean-revert: OOB-low→long, OOB-high→short). NO bny30 gate,
NO latched bias — pure s30r. Each trade evaluated on the 0.33% stop / 0.9% target envelope
(45-min horizon, raw close): open UTC · dir · result (WON=reached +0.9% first / STOP=hit
-0.33% first / flat=neither in horizon) · max_stop (worst adverse %) · secs_to_won.
Writes a CSV per config + prints summary & head.
"""
import sys
import numpy as np
from datetime import datetime, timezone
sys.path.insert(0, '/home/joe/thecodes')
import logging
for nm in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(nm).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect

STOP, TAKE, CAP, HI, LO = 0.33, 0.9, 540, 85.0, 15.0
CONFIGS = [('prod  k3/r10/s12', {'k_len': 3, 'rsi_len': 10, 'stc_len': 12}),
           ('grind k9/r6/s6',  {'k_len': 9, 'rsi_len': 6,  'stc_len': 6})]


def utc(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%m-%d %H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=12, warmup_hours=12)
    base, ts, win_start, _, _ = det._setup()
    s30r = [f for f in det._families if f['name'] == 's30r'][0]
    M = ts >= win_start
    rc = base['close'].to_numpy(float)[M]; tsm = ts[M].astype('int64'); n = len(rc)

    for tag, ov in CONFIGS:
        line = det._line(base, {**s30r['k'], **ov})[M]
        lo = line < LO; hi = line > HI
        lo_on = np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]]))
        hi_on = np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]]))
        ent = sorted([(int(i), 1) for i in lo_on] + [(int(i), -1) for i in hi_on])
        rows = []
        for e, d in ent:
            seg = rc[e + 1:e + 1 + CAP]
            if len(seg) == 0:
                continue
            rel = (seg - rc[e]) / rc[e] * 100 * d
            won_i = np.where(rel >= TAKE)[0]
            stp_i = np.where(rel <= -STOP)[0]
            won_i = int(won_i[0]) if len(won_i) else 10 ** 9
            stp_i = int(stp_i[0]) if len(stp_i) else 10 ** 9
            if won_i < stp_i:
                res, cut, s2w = 'WON', won_i, (won_i + 1) * 5
            elif stp_i < won_i:
                res, cut, s2w = 'STOP', stp_i, None
            else:
                res, cut, s2w = 'flat', len(rel) - 1, None
            mstop = float(np.maximum(0.0, -rel[:cut + 1]).max()) if cut >= 0 else 0.0
            rows.append((int(tsm[e]), 'L' if d == 1 else 'S', res, round(mstop, 3), s2w))

        fn = f"/home/joe/thecodes/s30_trades_{tag.split()[0]}.csv"
        with open(fn, 'w') as f:
            f.write('open_utc,dir,result,max_stop_pct,secs_to_won\n')
            for r in rows:
                f.write(f'{utc(r[0])},{r[1]},{r[2]},{r[3]},{r[4] if r[4] is not None else ""}\n')
        nw = sum(r[2] == 'WON' for r in rows); ns = sum(r[2] == 'STOP' for r in rows); nf = sum(r[2] == 'flat' for r in rows)
        tot = len(rows)
        print(f'\n=== {tag}  ·  {tot} trades  ·  WON {nw} ({nw/tot*100:.0f}%)  STOP {ns} ({ns/tot*100:.0f}%)  flat {nf}  ·  {fn} ===')
        print(f'  bny30 gate/bias: NOT applied (entry = s30r OOB onset, mean-revert)')
        print(f'{"open UTC":>17} {"dir":>3} {"result":>6} {"max_stop":>8} {"s2won":>6}')
        for r in rows[:24]:
            print(f'{utc(r[0]):>17} {r[1]:>3} {r[2]:>6} {r[3]:>8.3f} {("" if r[4] is None else r[4]):>6}')
        if tot > 24:
            print(f'  … +{tot-24} more in the CSV')
    db.disconnect()


if __name__ == '__main__':
    main()
