"""
s30r_review — a bl_review-style per-entry ledger for the s30r champion (k5 r17 s9 / hlcc4),
matched columns. One row per bny30-bias-gated s30r OOB entry over a recent window. stop/profit
are swing geometry (find_pivots 0.9): stop_pct = entry → the adverse breach-extreme pivot
(the heat); profit_pct = that pivot → the next pivot (the reversion swing) — same derivation
as bl_review's gate-opens, but on RAW close (px_smooth understates heat; the champion's
~0.14 stop is a raw-close number). px_smooth kept as a reference column.

Table s30r_review mirrors bl_review's columns. Window = last LOOKBACK_H h (matches the pine).
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
from optimus9.analysis.bl_detect import BLDetect, GCA5M_RAW
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side, pine_aligned_signals
from optimus9.compute.swing_detect import find_pivots

LOOKBACK_H = 12
CHAMP = {'k_len': 5, 'rsi_len': 17, 'stc_len': 9, 'src': 'hlcc4'}
OOBH, OOBL = 85.0, 15.0
_T = 's30r_review'


def latched_bias(oob):
    b = np.zeros(len(oob), np.int8); cur = 0
    for i in range(len(oob)):
        if oob[i] != 0 and (i == 0 or oob[i - 1] == 0):
            cur = -int(oob[i])
        b[i] = cur
    return b


def dt(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=LOOKBACK_H, warmup_hours=12)
    s30r = [f for f in det._families if f['name'] == 's30r'][0]
    fam = {**s30r, 'k': {**s30r['k'], **CHAMP}}
    base, ts, win_start, _, pxs = det._setup()
    res = det._run_family(fam, base, ts)[3]
    state = np.asarray(res['state']).astype(int); e1 = np.asarray(res['exit1']).astype(bool)
    e2 = np.asarray(res['exit2']).astype(bool); e3 = np.asarray(res['exit3']).astype(bool)
    pred = np.asarray(res['predicted']).astype(int)
    kline = det._line(base, {'kind': 'k', 'tf_seconds': 30, **CHAMP})
    bias = latched_bias(bny30_oob_side(base))
    ai, ad = pine_aligned_signals(base, db, GCA5M_RAW, gate=False)
    rawpk = np.zeros(len(ts), np.int8); rawpk[ai] = ad

    M = ts >= win_start
    tsm = ts[M].astype('int64'); st = state[M]; kl = kline[M]; bm = bias[M]
    e1m, e2m, e3m = e1[M], e2[M], e3[M]; pkm = rawpk[M]; predm = pred[M]; pxm = np.asarray(pxs, float)[M]
    rc = base['close'].to_numpy(float)[M]; N = len(rc)

    CAP, TAKE = 540, 0.9
    # entries = bias-gated OOB onsets
    lo = kl < OOBL; hi = kl > OOBH
    lo_on = set(np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]])).tolist())
    hi_on = set(np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]])).tolist())
    rows = []
    for i in range(N):
        side = 1 if i in hi_on else (-1 if i in lo_on else 0)   # OOB side (unambiguous from line)
        if side == 0:
            continue
        tdir = -side                                            # mean-revert: low→long(+1), high→short(-1)
        if tdir != bm[i]:                                       # bny30 bias gate
            continue
        eb = (1 if e1m[i] else 0) | (2 if e2m[i] else 0) | (4 if e3m[i] else 0)
        seg = rc[i + 1:i + 1 + CAP]
        won = 0; stop = None; prof = None; s_at = p_at = None
        if len(seg):
            rel = (seg - rc[i]) / rc[i] * 100 * tdir            # favourable=+, on RAW close
            ht = np.where(rel >= TAKE)[0]
            cut = int(ht[0]) if len(ht) else len(rel) - 1       # heat measured up to the swing (or horizon)
            adv = np.maximum(0.0, -rel[:cut + 1])
            stop = round(float(adv.max()), 3); s_at = dt(tsm[i + 1 + int(np.argmax(adv))])
            if len(ht):                                         # reached the +0.9% swing
                won = 1; prof = round(float(rel[:cut + 1].max()), 3); p_at = dt(tsm[i + 1 + cut])
        rows.append(dict(bar_time=dt(tsm[i]), bl_line='s30r', event='entry_won' if won else 'entry_miss',
                         state=int(st[i]), breach_dir=side, predicted=int(predm[i]), raw_pk=int(pkm[i]),
                         px_smooth=round(float(pxm[i]), 2), breach_line=round(float(kl[i]), 2),
                         bb_main=None, exit_bits=eb, won=won, stop_pct=stop, stop_at=s_at,
                         profit_pct=prof, profit_at=p_at))

    cols = ['bar_time', 'bl_line', 'event', 'state', 'breach_dir', 'predicted', 'raw_pk',
            'px_smooth', 'breach_line', 'bb_main', 'exit_bits', 'won', 'stop_pct', 'stop_at', 'profit_pct', 'profit_at']
    db.execute(f'DROP TABLE IF EXISTS {_T}')
    db.execute(f'''CREATE TABLE {_T} (s3r_pk BIGINT AUTO_INCREMENT PRIMARY KEY, bar_time DATETIME,
        bl_line VARCHAR(16), event VARCHAR(12), state TINYINT, breach_dir TINYINT, predicted TINYINT,
        raw_pk TINYINT, px_smooth FLOAT, breach_line FLOAT, bb_main FLOAT, exit_bits TINYINT, won TINYINT,
        stop_pct FLOAT, stop_at DATETIME, profit_pct FLOAT, profit_at DATETIME)''')
    db.executemany(f"INSERT INTO {_T} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})",
                   [tuple(r[c] for c in cols) for r in rows])

    won = [r for r in rows if r['won']]; miss = [r for r in rows if not r['won']]
    ws = [r['stop_pct'] for r in won]; ms = [r['stop_pct'] for r in miss if r['stop_pct'] is not None]
    pp = [r['profit_pct'] for r in won]
    span = f"{dt(tsm[0])[5:]}–{dt(tsm[-1])[5:]} UTC"
    print(f'{_T}: {len(rows)} bias-gated entries (champion k5 r17 s9/hlcc4 · {span})')
    print(f'  reached +0.9% swing: {len(won)} ({len(won)/len(rows)*100:.0f}%)   missed: {len(miss)}')
    print(f'  WON  stop_pct (heat to swing): median {np.median(ws):.3f}  mean {np.mean(ws):.3f}  ← the 0.14 placement')
    print(f'  MISS stop_pct (heat, ran over): median {np.median(ms):.3f}  mean {np.mean(ms):.3f}  ← run-over risk')
    print(f'  WON  profit_pct (swing reached): median {np.median(pp):.3f}\\n')
    print(f'{"bar_time":>19} {"dir":>3} {"st":>2} {"pk":>2} {"breachln":>8} {"won":>4} {"stop%":>6} {"prof%":>6}')
    for r in rows[:22]:
        print(f'{r["bar_time"]:>19} {("S" if r["breach_dir"]==1 else "L"):>3} {r["state"]:>2} '
              f'{r["raw_pk"]:>2} {r["breach_line"]:>8.1f} {("WON" if r["won"] else "—"):>4} '
              f'{(r["stop_pct"] or 0):>6.3f} {(r["profit_pct"] or 0):>6.3f}')
    if len(rows) > 22:
        print(f'  … +{len(rows)-22} more in {_T}')
    db.disconnect()


if __name__ == '__main__':
    main()
