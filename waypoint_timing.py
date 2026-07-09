"""waypoint_timing.py (Joe 0706) — is the r-waypoint funnel CAUSAL/usable or hindsight?

At a fixed time T-min after entry (using ONLY bars up to T), count how many of s1r..s4r have reached
favorable-OOB, then measure P(final profit). If confluence-by-T separates winners with runway left, it's an
early hold/exit rule (low early-confluence → bail); if it only works late, it's hindsight. s5m arm, causal.
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

RT = 0.20; RLINES = ['s1r', 's2r', 's3r', 's4r']; HI, LO = 85.0, 15.0
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts)
V = {r: np.asarray(W.line(r), float) for r in RLINES}
ent = v2_walk(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()

T = []                                                    # (k0, bd, prof)
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k0 = int(np.argmin(np.abs(ts - int(tms))))
    T.append((k0, bd, (float(r) - RT) > 0))
base = 100 * np.mean([t[2] for t in T])
print('s5m-arm trades=%d · base P(profit)=%.0f%%\n' % (len(T), base))

for Tmin in (3, 5, 10, 15):
    B = Tmin * 12                                         # 5s bars in T minutes
    conf = []
    for k0, bd, prof in T:
        seg_end = k0 + B
        c = 0
        for rl in RLINES:
            seg = V[rl][k0:seg_end + 1]
            if np.nansum((seg >= HI) if bd == 1 else (seg <= LO)) > 0: c += 1
        conf.append((c, prof))
    print('=== confluence reached BY %2dmin after entry (causal) ===' % Tmin)
    print('  %-10s %8s %10s' % ('conf-by-T', 'n', 'P(final prof)'))
    for c in range(5):
        sub = [p for cc, p in conf if cc == c]
        if sub: print('  %-10d %8d %9.0f%%' % (c, len(sub), 100 * np.mean(sub)))
    lo = [p for cc, p in conf if cc == 0]; hi = [p for cc, p in conf if cc >= 2]
    print('  → EXIT rule: conf==0 by %dmin ⇒ P=%.0f%% (n=%d) · HOLD: conf>=2 ⇒ P=%.0f%% (n=%d)\n'
          % (Tmin, 100 * np.mean(lo) if lo else 0, len(lo), 100 * np.mean(hi) if hi else 0, len(hi)))
