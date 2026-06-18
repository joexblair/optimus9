"""
bias_pk_cascade_grind.py — A/B the entry cascade across 8 windows (Joe 0618).

Matrix: ordering {co (forward-tol) · seq (sequential, 21-min cap)} × s3 variant {m · r · M · rM}
        × xm45 gate {off · on}  = 16 configs. osc=s12m, trig=s12m, oob, MAE 0.4 / target 0.9.
Scores the placement metric per window; ranks by rolled rate (≥ FLOOR trades) and shows correct count
+ per-window robustness. Writes bias_pk_cascade; prints the leaderboard + the winner's trace.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

H = bm.H; MAE, TARGET, FLOOR = 0.4, 0.9, 120
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')
CFGS = [(o, v, x) for o in ('co', 'seq') for x in (False, True) for v in ('m', 'r', 'M', 'rM')]

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
print(f'{len(ends)} windows · {len(CFGS)} configs · osc=s12m trig=s12m')

# res[cfg] = list over windows of (correct, total)
res = {c: [] for c in CFGS}; win_ends = []
db2 = DatabaseManager(**get_db_config()); db2.connect()
for wi, end in enumerate(ends):
    W = bm.BiasWindow(db2, end); win_ends.append(W.W1)
    W.set_osc(W._aligned(720, bm.GEN_M), 144)
    ups = W.ups(W.trigs(12), 'oob')
    for c in CFGS:
        W.set_entry(*c)
        pls = W.placements(ups, MAE, TARGET)
        res[c].append((sum(p['hit'] for p in pls), len(pls)))
    print(f'  window {wi+1}/{len(ends)} → {dd(W.W1)} done')
db2.disconnect()

rows = []
for c in CFGS:
    o, v, x = c
    for wi, (cc, n) in enumerate(res[c]):
        rows.append([dts := dtm.datetime.fromtimestamp(win_ends[wi]/1000, timezone.utc).strftime('%Y-%m-%d %H:%M'),
                     o, v, int(x), cc, n])
db.execute('DROP TABLE IF EXISTS bias_pk_cascade')
db.execute('''CREATE TABLE bias_pk_cascade (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    ordering VARCHAR(4), s3_variant VARCHAR(3), xm45 TINYINT, correct INT, total INT)''')
db.executemany('INSERT INTO bias_pk_cascade (window_end,ordering,s3_variant,xm45,correct,total) VALUES (%s,%s,%s,%s,%s,%s)', rows)
db.disconnect()

lb = []
for c in CFGS:
    cc = sum(x[0] for x in res[c]); nn = sum(x[1] for x in res[c])
    posw = sum(1 for (a, b) in res[c] if b and a / b >= 0.40)          # windows ≥40%
    lb.append((cc / nn if nn else 0, cc, nn, posw, c))
print(f'\nLEADERBOARD — rolled placement rate (≥{FLOOR} trades), 8 windows:')
print(f'  {"order":>5} {"s3":>3} {"xm45":>4} | {"rate":>5} {"correct":>7} {"trades":>6} {">=40% wins":>10}')
for rate, cc, nn, posw, (o, v, x) in sorted([l for l in lb if l[2] >= FLOOR], reverse=True):
    print(f'  {o:>5} {v:>3} {int(x):>4} | {rate:>5.0%} {cc:>7} {nn:>6} {posw:>7}/8')
# also the correct-count leader (volume-aware)
cl = max(lb, key=lambda l: l[1])
rl = max([l for l in lb if l[2] >= FLOOR], key=lambda l: l[0])
print(f"\n  rate winner (≥{FLOOR}):  {rl[4]} → {rl[0]:.0%} ({rl[1]}/{rl[2]})")
print(f"  count winner:         {cl[4]} → {cl[1]} correct ({cl[1]/cl[2]:.0%}, {cl[2]} trades)")
print(f'\n→ db table bias_pk_cascade ({len(rows)} rows)')
