"""
refine_s30r_placement — find the s30r combo that lands CLOSEST to the swing turn.

Each bias-gated s30r OOB entry → walk raw close 45min. stop = max adverse % on the path to
the +0.9% swing (the heat to capture it) — measured to the SWING, not to any exit line
(decoupled from the earlier near_zero/exit-speed confound). A "clean" entry = reaches +0.9%
AND stop ≤ 0.4% (s30r fired near the turn). Entries needing >0.4%, or never reaching the
swing, are filtered out. Rank s30r combos (k/rsi/stc) by lowest median clean-stop = closest
placement, gated on volume + net-positive presence in all 4×24h windows. Support/s30M is
irrelevant here (placement is the entry only).
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
OFFSETS = [0, 5, 10, 15]; DAY_MS = 86400000
MIN_CLEAN = 8                                  # per-window min clean entries to qualify
R_KLEN = list(range(2, 11)); R_RSI = list(range(6, 25, 2)); R_STC = list(range(6, 29, 2))   # 1080


def latched_bias(oob):
    bias = np.zeros(len(oob), np.int8); cur = 0
    for i in range(len(oob)):
        if oob[i] != 0 and (i == 0 or oob[i - 1] == 0):
            cur = -int(oob[i])
        bias[i] = cur
    return bias


def entries(line, bias):
    lo = line < LO; hi = line > HI
    lo_on = np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]]))
    hi_on = np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]]))
    bars = np.concatenate([lo_on, hi_on]).astype(np.int64)
    dirs = np.concatenate([np.ones(len(lo_on), np.int8), -np.ones(len(hi_on), np.int8)])
    keep = dirs == bias[bars]
    return bars[keep], dirs[keep]


def place(rc, bars, dirs, n):
    """Per entry → (won, clean, stop). stop = max adverse % before +0.9% (or cap)."""
    won = clean = 0; stops = []
    for e, d in zip(bars, dirs):
        seg = rc[e + 1:e + 1 + CAP]
        if len(seg) == 0:
            continue
        rel = (seg - rc[e]) / rc[e] * 100 * d
        hit = np.where(rel >= TAKE)[0]
        if len(hit) == 0:
            continue                            # never reached the swing → not a capture
        won += 1
        c = int(hit[0])
        stop = float(np.maximum(0.0, -rel[:c + 1]).max()) if c > 0 else 0.0
        if stop <= STOPMAX:
            clean += 1; stops.append(stop)
    return won, clean, stops


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    db.execute('DROP TABLE IF EXISTS s30r_placement')
    db.execute('''CREATE TABLE s30r_placement (
        srp_pk BIGINT AUTO_INCREMENT PRIMARY KEY, r_klen INT,r_rsi INT,r_stc INT,
        tot_ent INT, tot_won INT, tot_clean INT, won_pct FLOAT, clean_pct FLOAT,
        med_stop FLOAT, mean_stop FLOAT, min_clean INT, all_win TINYINT, KEY(all_win))''')
    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    s30r = [f for f in det._families if f['name'] == 's30r'][0]
    r_combos = [(k, r, s) for k in R_KLEN for r in R_RSI for s in R_STC]
    print(f'{len(r_combos)} s30r combos · 4×24h · stop filter ≤{STOPMAX}% · target +{TAKE}%')

    W = []; t0 = time.time()
    for off in OFFSETS:
        base, ts, win_start, _, _ = det._setup(dmax - off * DAY_MS)
        Mk = ts >= win_start
        rc = base['close'].to_numpy(float)[Mk]
        bias = latched_bias(bny30_oob_side(base))[Mk]
        W.append((base, Mk, rc, bias))
        print(f'  win off={off:>2}d ready ({time.time()-t0:.0f}s)')

    rows = []; t1 = time.time()
    for ci, (k, r, s) in enumerate(r_combos):
        per = []
        for base, Mk, rc, bias in W:
            line = det._line(base, {**s30r['k'], 'k_len': k, 'rsi_len': r, 'stc_len': s})[Mk]
            b, d = entries(line, bias)
            per.append(place(rc, b, d, len(rc)) + (len(b),))      # (won, clean, stops, ent)
        tot_ent = sum(p[3] for p in per); tot_won = sum(p[0] for p in per); tot_clean = sum(p[1] for p in per)
        allstops = [x for p in per for x in p[2]]
        min_clean = min(p[1] for p in per)
        rows.append((k, r, s, tot_ent, tot_won, tot_clean,
                     tot_won / tot_ent * 100 if tot_ent else 0,
                     tot_clean / tot_won * 100 if tot_won else 0,
                     float(np.median(allstops)) if allstops else None,
                     float(np.mean(allstops)) if allstops else None,
                     min_clean, int(min_clean >= MIN_CLEAN)))
        if (ci + 1) % 200 == 0:
            print(f'  {ci+1}/{len(r_combos)} ({time.time()-t1:.0f}s)')
    db.executemany('''INSERT INTO s30r_placement
        (r_klen,r_rsi,r_stc,tot_ent,tot_won,tot_clean,won_pct,clean_pct,med_stop,mean_stop,min_clean,all_win)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
    print(f'done: {len(r_combos)} combos in {time.time()-t1:.0f}s')

    print('\\n=== CLOSEST TO SWING — top 15 by lowest median clean-stop (≥8 clean/window) ===')
    print(f'{"klen":>4}{"rsi":>4}{"stc":>4}{"ent":>6}{"won":>6}{"clean":>6}{"won%":>6}{"cln%":>6}{"medStop":>8}{"meanStop":>9}{"minCln":>7}')
    for t in db.execute('''SELECT * FROM s30r_placement WHERE all_win=1 ORDER BY med_stop ASC LIMIT 15''', fetch=True):
        print(f'{t["r_klen"]:>4}{t["r_rsi"]:>4}{t["r_stc"]:>4}{t["tot_ent"]:>6}{t["tot_won"]:>6}{t["tot_clean"]:>6}'
              f'{t["won_pct"]:>6.1f}{t["clean_pct"]:>6.1f}{t["med_stop"]:>8.3f}{t["mean_stop"]:>9.3f}{t["min_clean"]:>7}')
    db.disconnect()


if __name__ == '__main__':
    main()
