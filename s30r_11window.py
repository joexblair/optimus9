"""
s30r_11window — consistency check of the top-20 placement combos across 11 windows
(every 3 days, ~33-day span). For each combo, per-window median stop-to-swing (≤0.4% filter,
+0.9% target) → mean/std/worst + how many of 11 windows qualify (≥8 clean). Plus each combo's
best maj and min BB exit joined from s30_grind_results (bias-gated 4-window edge). Answers:
do the slow-K placements hold across regimes, and what exit pairs with each.
"""
import sys, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side

TAKE, CAP, STOPMAX, HI, LO = 0.9, 540, 0.4, 85.0, 15.0
NWIN, STEP_D = 11, 3; DAY_MS = 86400000
MIN_CLEAN = 8


def latched_bias(oob):
    bias = np.zeros(len(oob), np.int8); cur = 0
    for i in range(len(oob)):
        if oob[i] != 0 and (i == 0 or oob[i - 1] == 0):
            cur = -int(oob[i])
        bias[i] = cur
    return bias


def place(rc, line, bias):
    lo = line < LO; hi = line > HI
    lo_on = np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]]))
    hi_on = np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]]))
    bars = np.concatenate([lo_on, hi_on]).astype(np.int64)
    dirs = np.concatenate([np.ones(len(lo_on), np.int8), -np.ones(len(hi_on), np.int8)])
    keep = dirs == bias[bars]; bars, dirs = bars[keep], dirs[keep]
    won = 0; stops = []
    for e, d in zip(bars, dirs):
        seg = rc[e + 1:e + 1 + CAP]
        if len(seg) == 0:
            continue
        rel = (seg - rc[e]) / rc[e] * 100 * d
        hit = np.where(rel >= TAKE)[0]
        if len(hit) == 0:
            continue
        won += 1; c = int(hit[0])
        stop = float(np.maximum(0.0, -rel[:c + 1]).max()) if c > 0 else 0.0
        if stop <= STOPMAX:
            stops.append(stop)
    return len(bars), won, stops


def best_exit(db, k, r, s, support):
    rows = db.execute(f'''SELECT m_bblen,m_bbmult,mask,mean_pnl,min_net,min_win,tot_n FROM s30_grind_results
        WHERE r_klen={k} AND r_rsi={r} AND r_stc={s} AND CAST(support AS BINARY)='{support}'
        AND all_pos=1 ORDER BY mean_pnl DESC LIMIT 1''', fetch=True)
    return rows[0] if rows else None


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    top = db.execute('SELECT r_klen,r_rsi,r_stc FROM s30r_placement WHERE all_win=1 ORDER BY med_stop ASC LIMIT 20', fetch=True)
    combos = [(t['r_klen'], t['r_rsi'], t['r_stc']) for t in top]
    print(f'top-{len(combos)} placement combos · {NWIN} windows every {STEP_D}d')

    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    s30r = [f for f in det._families if f['name'] == 's30r'][0]
    W = []; t0 = time.time()
    for i in range(NWIN):
        base, ts, ws, _, _ = det._setup(dmax - i * STEP_D * DAY_MS)
        Mk = ts >= ws
        if Mk.sum() < 1000:
            print(f'  win -{i*STEP_D}d: thin ({int(Mk.sum())} bars) — skipped'); continue
        W.append((base, Mk, base['close'].to_numpy(float)[Mk], latched_bias(bny30_oob_side(base))[Mk]))
    print(f'{len(W)} windows ready ({time.time()-t0:.0f}s)')

    print(f'\\n{"combo":>12} {"medStop windows: mean":>13}{"std":>7}{"worst":>7}{"won%":>6}{"qual":>6}  '
          f'{"best maj exit":>22}{"best min exit":>22}')
    out = []
    for (k, r, s) in combos:
        meds, wons, quals = [], [], 0
        for base, Mk, rc, bias in W:
            line = det._line(base, {**s30r['k'], 'k_len': k, 'rsi_len': r, 'stc_len': s})[Mk]
            ent, won, stops = place(rc, line, bias)
            if len(stops) >= MIN_CLEAN:
                quals += 1
            meds.append(np.median(stops) if stops else np.nan)
            wons.append(won / ent * 100 if ent else 0)
        meds = np.array(meds); valid = meds[~np.isnan(meds)]
        mj = best_exit(db, k, r, s, 'maj'); mn = best_exit(db, k, r, s, 'min')
        ej = f"bb{mj['m_bblen']}/{mj['m_bbmult']:.2f}/{mj['mask']} m{mj['mean_pnl']:.3f}" if mj else "—"
        en = f"bb{mn['m_bblen']}/{mn['m_bbmult']:.2f}/{mn['mask']} m{mn['mean_pnl']:.3f}" if mn else "—"
        mean_med = float(np.nanmean(meds)); std_med = float(np.nanstd(meds)); worst = float(np.nanmax(meds))
        out.append((k, r, s, mean_med, std_med, worst, float(np.mean(wons)), quals, len(valid)))
        print(f'  k{k:>2} r{r:>2} s{s:>2} {mean_med:>13.3f}{std_med:>7.3f}{worst:>7.3f}{np.mean(wons):>6.1f}'
              f'{quals:>4}/{len(W):<2}{ej:>22}{en:>22}')

    db.execute('DROP TABLE IF EXISTS s30r_consistency')
    db.execute('''CREATE TABLE s30r_consistency (sc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        r_klen INT,r_rsi INT,r_stc INT, mean_med FLOAT, std_med FLOAT, worst_med FLOAT,
        won_pct FLOAT, n_qual INT, n_valid INT)''')
    db.executemany('INSERT INTO s30r_consistency (r_klen,r_rsi,r_stc,mean_med,std_med,worst_med,won_pct,n_qual,n_valid) '
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', out)
    nfull = sum(1 for o in out if o[7] == len(W))
    print(f'\\n{nfull}/{len(combos)} combos qualify in ALL {len(W)} windows  → s30r_consistency')
    db.disconnect()


if __name__ == '__main__':
    main()
