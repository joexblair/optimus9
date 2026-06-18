"""
bias_pk_placement.py — the bias-machine PLACEMENT grind (success metric, Joe 0617).

Per pk update, the following trade (entry = next aligned s30 wob) is allowed 0.3% MAE; potential
profit = max favourable % before that adverse breach. Correctly-placed iff potential ≥ 0.9%.
A winning combo = the most correctly-placed pk updates. Exit is irrelevant → combos differ only
by trigger TF (gate = oob = s14M OR s14r). 8 rolling 7d windows.

Stores every pk's placement to bias_pk_placement; prints the trigger-TF leaderboard + the stats.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

H = bm.H; MAE_ALLOW, TARGET = 0.3, 0.9
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
print(f'{len(ends)} windows · trigger TFs {bm.TFS} · gate oob(s14M|s14r) · MAE {MAE_ALLOW} · target {TARGET}')

# res[tf] = list over windows of placement-lists
res = {tf: [] for tf in bm.TFS}; win_ends = []
for wi, end in enumerate(ends):
    W = bm.BiasWindow(db, end); win_ends.append(W.W1)
    for tf in bm.TFS:
        res[tf].append(W.placements(W.ups(W.trigs(tf), 'oob'), MAE_ALLOW, TARGET))
    print(f'  window {wi+1}/{len(ends)} → {dd(W.W1)} done')

# persist every placement
rows = []
for tf in bm.TFS:
    for wi, pls in enumerate(res[tf]):
        we = dts(win_ends[wi])
        for p in pls:
            rows.append([we, tf, dts(p['pk_t']), dts(p['et']), 'LONG' if p['bd'] == 1 else 'SHORT',
                         p['potential'], int(p['hit']), p['secs_to_target'], p['secs_to_stop'], p['anc'], p['flt']])
db.execute('DROP TABLE IF EXISTS bias_pk_placement')
db.execute('''CREATE TABLE bias_pk_placement (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    trigger_tf INT, pk_time DATETIME, entry_time DATETIME, direction VARCHAR(5), potential_pct FLOAT,
    hit_target TINYINT, secs_to_target INT, secs_to_stop INT, anchor FLOAT, floater FLOAT)''')
db.executemany('''INSERT INTO bias_pk_placement (window_end,trigger_tf,pk_time,entry_time,direction,potential_pct,
    hit_target,secs_to_target,secs_to_stop,anchor,floater) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
db.disconnect()

# ── leaderboard: most correctly-placed pk updates ──
print(f'\nLEADERBOARD — correctly-placed pk updates across {len(ends)} windows (potential ≥ {TARGET}%, ≤{MAE_ALLOW}% MAE)')
print(f'  {"tf":>3} | {"correct":>7} {"total":>6} {"rate":>5} | {"per-window correct":>20} | {"med s→0.9":>9}')
lb = []
for tf in bm.TFS:
    allp = [p for pls in res[tf] for p in pls]
    correct = sum(p['hit'] for p in allp); total = len(allp)
    perwin = [sum(p['hit'] for p in pls) for pls in res[tf]]
    tts = [p['secs_to_target'] for p in allp if p['hit'] and p['secs_to_target'] is not None]
    lb.append((correct, total, perwin, int(np.median(tts)) if tts else 0, tf))
for correct, total, perwin, medtt, tf in sorted(lb, reverse=True):
    rate = correct / total if total else 0
    pw = ' '.join(f'{c:>2}' for c in perwin)
    print(f'  {tf:>3} | {correct:>7} {total:>6} {rate:>5.0%} | {pw:>20} | {medtt:>7}s')

# ── stats of the collected trades (pooled, best TF) ──
btf = max(bm.TFS, key=lambda tf: sum(p['hit'] for pls in res[tf] for p in pls))
allp = [p for pls in res[btf] for p in pls]
pot = np.array([p['potential'] for p in allp])
stopped_first = sum((not p['hit']) and p['secs_to_stop'] is not None for p in allp)
print(f'\nstats @ best tf {btf} (n={len(allp)}):  potential median {np.median(pot):.2f}% · '
      f'p75 {np.percentile(pot,75):.2f}% · hit {np.mean([p["hit"] for p in allp]):.0%} · '
      f'stopped-before-0.9 {stopped_first/len(allp):.0%}')
print(f'→ db table bias_pk_placement ({len(rows)} rows)')
