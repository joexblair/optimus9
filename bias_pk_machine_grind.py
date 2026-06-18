"""
bias_pk_machine_grind.py — does feeding anchor/floater through the pk machine beat the raw call?

Baseline = the raw `anchor>floater` call (current ups_s6r_anchor) scored by the placement metric.
Test    = pk_feed (line_slope=osc(anc)−osc(flt), price_slope=px(anc)−px(flt) → _pk_state_from_slopes
          → close/wide probes 5/2 → PKVoteMachine → apply_decision_delay), swept over
          slope_floor 1..55 × decision_delay {0,1,2}. Same placement metric (MAE 0.4 / target 0.9,
          oob gate, s3 entry, cancel-on-opposite). One window (end 0607) — validate winner across 8 after.

⚠ decision_delay counts pk EVENTS here, not bars — flagged to Joe, pending confirm.
Writes bias_pk_machine; prints baseline vs the leaderboard.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

H = bm.H; MAE, TARGET, FLOOR = 0.4, 0.9, 30
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
end = next(x for x in ends if dd(x) == '0607')

W = bm.BiasWindow(db, end)
ups = W.ups_s6r_anchor('oob', 6)

def rate(calls):
    pls = W.placements(calls, MAE, TARGET)
    n = len(pls); c = sum(p['hit'] for p in pls)
    return c, n, (c / n if n else 0.0)

bc, bn, brate = rate(ups)
print(f'window {dd(end)} · BASELINE raw anchor>floater call: {bc}/{bn} = {brate:.0%}  (floor ≥{FLOOR})')

rows = []
for delay in (0, 1, 2):
    for sf in range(1, 56):
        calls = W.pk_feed(ups, sf, delay)
        c, n, r = rate(calls)
        rows.append([sf, delay, c, n, round(r, 4)])
db.execute('DROP TABLE IF EXISTS bias_pk_machine')
db.execute('''CREATE TABLE bias_pk_machine (pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    slope_floor INT, decision_delay INT, correct INT, total INT, rate FLOAT)''')
db.executemany('INSERT INTO bias_pk_machine (slope_floor,decision_delay,correct,total,rate) VALUES (%s,%s,%s,%s,%s)', rows)
db.disconnect()

elig = [r for r in rows if r[3] >= FLOOR]
print(f'\nLEADERBOARD — pk-machine feed, top 10 by rate (≥{FLOOR} placements):')
print(f'  {"slope":>5} {"delay":>5} | {"correct":>7} {"total":>5} {"rate":>5}')
for sf, delay, c, n, r in sorted(elig, key=lambda x: x[4], reverse=True)[:10]:
    print(f'  {sf:>5} {delay:>5} | {c:>7} {n:>5} {r:>5.0%}')
best = max(elig, key=lambda x: x[4]) if elig else None
if best:
    print(f'\nBEST pk-machine: slope_floor={best[0]} delay={best[1]} → {best[2]}/{best[3]} = {best[4]:.0%}'
          f'   vs baseline {brate:.0%}')
# how does rate move with slope_floor at delay 0?
d0 = sorted([r for r in rows if r[1] == 0], key=lambda x: x[0])
print('  rate vs slope_floor @delay0:  ' + ' '.join(f'{r[0]}:{r[4]:.0%}' for r in d0 if r[0] in (1,5,10,15,20,30,40,55)))
print(f'\n→ db table bias_pk_machine ({len(rows)} rows)')
