"""waypoint_funnel.py (Joe 0706) — s1r/s2r/s3r/s4r OOB as waypoint checkpoints; profit-rate funnel.

For each s5m-arm real trade (lr_exit_v2), during its life does each r-line reach OOB on the bd-FAVORABLE side
(long → r>=85, short → r<=15)? That's a causal HOLD-decision checkpoint (known when it happens). Funnel:
P(profit | reached r_n) vs not, and P(profit | confluence>=k). Rising with confluence ⇒ waypoints = strength.
"""
import sys, datetime as dtm
from datetime import timezone
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2, strand_rescue

RT = 0.20
db = DatabaseManager(**get_db_config()); db.connect()
live = {x['ind_name'] for x in db.execute("SELECT ind_name FROM vw_indicator_configs_live WHERE ind_name IN ('s1r','s2r','s3r','s4r')", fetch=True)}
RLINES = [r for r in ['s1r', 's2r', 's3r', 's4r'] if r in live]
print('live r-lines:', RLINES)
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts); HI, LO = 85.0, 15.0
V = {r: np.asarray(W.line(r), float) for r in RLINES}
ent = v2_walk(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()

T = []
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k0 = int(np.argmin(np.abs(ts - int(tms)))); k1 = int(np.argmin(np.abs(ts - int(exms))))
    if k1 <= k0: k1 = k0 + 1
    prof = (float(r) - RT) > 0
    reached = {}
    for rl in RLINES:
        seg = V[rl][k0:k1 + 1]
        reached[rl] = bool(np.nansum((seg >= HI) if bd == 1 else (seg <= LO)) > 0)
    T.append((prof, reached, sum(reached.values())))

n = len(T); base = 100 * np.mean([t[0] for t in T])
print('\ns5m-arm trades=%d · base P(profit)=%.0f%%\n' % (n, base))
print('per-waypoint (reached favorable-OOB during the trade):')
print('%-5s %8s %14s %16s' % ('r', 'reached', 'P(prof|reached)', 'P(prof|NOT reach)'))
for rl in RLINES:
    yes = [t[0] for t in T if t[1][rl]]; no = [t[0] for t in T if not t[1][rl]]
    print('%-5s %6d/%d %13.0f%% %16.0f%%' % (rl, len(yes), n,
          100 * np.mean(yes) if yes else 0, 100 * np.mean(no) if no else 0))

print('\nconfluence funnel (# of r-lines that reached favorable-OOB):')
print('%-10s %8s %12s' % ('confluence', 'n trades', 'P(profit)'))
for c in range(len(RLINES) + 1):
    sub = [t[0] for t in T if t[2] == c]
    if sub: print('%-10d %8d %11.0f%%' % (c, len(sub), 100 * np.mean(sub)))
print('\ncumulative (>= k confluence):')
for c in range(len(RLINES) + 1):
    sub = [t[0] for t in T if t[2] >= c]
    if sub: print('  >=%d : n=%4d  P(profit)=%.0f%%' % (c, len(sub), 100 * np.mean(sub)))
