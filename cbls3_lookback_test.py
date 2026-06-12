"""
cbls3 lookback (task #8) — INSTRUMENTATION, not a verdict.

We are NOT deciding the swing-association rule or back-vs-forward here. We emit raw
per-trade rows so the data decides (or pivots). The real question this feeds: current
gated PK admission vs a dynamic latched-unlatch — which is more profitable over time.

Framework = real ≥0.9% swings (swing_detect.find_pivots, dialed to 0.9). Per bias-matched
PK within ±33 (30s) of its nearest c_bls3, entry = the PK bar (act-on-signal). Emit:
  trade_utc          the entry
  closest_swing_utc  nearest ZigZag pivot either side
  adverse_swing_utc  nearest pivot on the trade's adverse side (the dip/spike); often == closest
  pk_off_secs        signed (pk - c_bls3) — where profitable PKs sit relative to the cascade
  secs_to_won        entry → +0.9% on raw close (45-min cap)
  max_stop_needed    worst adverse before the win → near_zero tell (NOT stop=0)
Persists to cbls3_lookback_trades for pine recon + the data review.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect, GCA5M_RAW
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side, pine_aligned_signals
from optimus9.orchestration.bl_group_grind import _refold
from optimus9.compute.swing_detect import find_pivots

COMBO = {'b6b': 7, 'hb15b': 3, 'hb9b': 5, 'hs15r': 2, 'hs9r': 2, 's18b': 17, 's30r': 4, 's90b': 17}
TAKE, HORIZON = 0.9, 540                       # 0.9% · 45-min cap (540×5s)
WIN_BARS = 33 * 6                              # ±33 (30s) = ±198 5s bars around c_bls3
NEAR_ZERO = 0.10                               # max_stop ≤ this → near-zero entry
OFFSETS = [0, 9, 18]                           # window ends, days back
DAY_MS = 86400000


def latched_bias(oob):
    bias = np.zeros(len(oob), np.int8); cur = 0
    for i in range(len(oob)):
        if oob[i] != 0 and (i == 0 or oob[i - 1] == 0):
            cur = -int(oob[i])                 # OOB-low → long(+1), OOB-high → short(-1)
        bias[i] = cur
    return bias


def score(rc, entry, d):
    seg = rc[entry + 1:entry + 1 + HORIZON]
    if len(seg) == 0:
        return None
    rel = (seg - rc[entry]) / rc[entry] * 100.0 * d
    hit = np.where(rel >= TAKE)[0]
    if len(hit) == 0:
        adv = float(np.maximum(0.0, -rel).max()) if len(rel) else 0.0
        return (0, None, round(adv, 3))        # not won within cap; report heat seen
    w = int(hit[0])
    adv = float(np.maximum(0.0, -rel[:w]).max()) if w > 0 else 0.0
    return (1, (w + 1) * 5, round(adv, 3))


def nearest(arr, x):
    """nearest value in sorted arr to x; None if empty."""
    if len(arr) == 0:
        return None
    k = int(np.searchsorted(arr, x))
    cands = [c for c in (k - 1, k) if 0 <= c < len(arr)]
    return int(min(cands, key=lambda c: abs(arr[c] - x)))


def run_window(end_ms, db):
    det = BLDetect(db, lookback_hours=9 * 24, warmup_hours=12)
    for f in det._families:
        if f['name'] in COMBO:
            f['k'] = {**f['k'], 'k_len': COMBO[f['name']]}
    base, ts, win_start, _, px = det._setup(end_ms)
    oob = bny30_oob_side(base)
    bias = latched_bias(oob)
    ai, ad = pine_aligned_signals(base, db, GCA5M_RAW, gate=False)
    pk = np.zeros(len(ts), np.int8); pk[ai] = ad
    gated = np.where(pk == bias, pk, 0).astype(np.int8)
    states = [det._run_family(f, base, ts)[3]['state'] for f in det._families]
    combined = _refold(states)
    M = ts >= win_start
    tsm = ts[M].astype('int64'); cm = combined[M]; gm = gated[M]; rc = base['close'].to_numpy(float)[M]
    N = len(tsm)
    c_bars = np.array([i for i in range(1, N) if cm[i] == 3 and cm[i - 1] != 3])
    # swings: pivots split by kind. Low = adverse for longs, High = adverse for shorts.
    piv = find_pivots(rc, 0.9)
    piv_all = np.array(sorted(p[0] for p in piv))
    piv_lo = np.array(sorted(p[0] for p in piv if p[1] == 'L'))
    piv_hi = np.array(sorted(p[0] for p in piv if p[1] == 'H'))
    rows = []
    for j in range(N):
        if gm[j] == 0 or len(c_bars) == 0:
            continue
        ci = nearest(c_bars, j); c = int(c_bars[ci])
        if abs(j - c) > WIN_BARS:
            continue                           # not a lookback PK
        d = int(gm[j])
        sc = score(rc, j, d)
        if sc is None:
            continue
        won, s2w, mstop = sc
        cs = nearest(piv_all, j)
        adv_arr = piv_lo if d == 1 else piv_hi
        av = nearest(adv_arr, j)
        rows.append(dict(c_ts=int(tsm[c]), pk_ts=int(tsm[j]), dir=d, pk_off_secs=(j - c) * 5,
                         closest_swing_ts=int(tsm[piv_all[cs]]) if cs is not None else None,
                         adverse_swing_ts=int(tsm[adv_arr[av]]) if av is not None else None,
                         won=won, secs_to_won=s2w, max_stop_needed=mstop,
                         near_zero=int(mstop <= NEAR_ZERO)))
    return rows, len(c_bars), int((bias != 0).sum()), len(piv)


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    db.execute('DROP TABLE IF EXISTS cbls3_lookback_trades')
    db.execute('''CREATE TABLE cbls3_lookback_trades (
        clt_pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_off INT,
        c_ts BIGINT, pk_ts BIGINT, dir TINYINT, pk_off_secs INT,
        closest_swing_ts BIGINT, adverse_swing_ts BIGINT,
        won TINYINT, secs_to_won INT, max_stop_needed FLOAT, near_zero TINYINT)''')
    print(f'{"win":>4} {"c_bls3":>7} {"swings":>7} {"trades":>7} {"won%":>6} '
          f'{"med_s2w":>8} {"med_mstop":>9} {"nearzero%":>9} {"pk<c%":>6}')
    for off in OFFSETS:
        rows, ncb, _, npiv = run_window(dmax - off * DAY_MS, db)
        if rows:
            db.executemany('''INSERT INTO cbls3_lookback_trades
                (window_off,c_ts,pk_ts,dir,pk_off_secs,closest_swing_ts,adverse_swing_ts,won,secs_to_won,max_stop_needed,near_zero)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                [(off, r['c_ts'], r['pk_ts'], r['dir'], r['pk_off_secs'], r['closest_swing_ts'],
                  r['adverse_swing_ts'], r['won'], r['secs_to_won'], r['max_stop_needed'], r['near_zero']) for r in rows])
        won = [r for r in rows if r['won']]
        wr = len(won) / len(rows) * 100 if rows else 0
        ms2w = np.median([r['secs_to_won'] for r in won]) if won else float('nan')
        mms = np.median([r['max_stop_needed'] for r in won]) if won else float('nan')
        nz = np.mean([r['near_zero'] for r in rows]) * 100 if rows else 0
        pkc = np.mean([r['pk_off_secs'] < 0 for r in rows]) * 100 if rows else 0
        print(f'{off:>4} {ncb:>7} {npiv:>7} {len(rows):>7} {wr:>6.1f} '
              f'{ms2w:>8.0f} {mms:>9.3f} {nz:>9.1f} {pkc:>6.1f}')
    db.disconnect()
    print('raw rows → cbls3_lookback_trades')


if __name__ == '__main__':
    main()
