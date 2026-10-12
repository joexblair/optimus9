"""WALK ONE LEG FORWARD FOR rule#1 QUALIFIED **AND** ws12r OOB. 1009.

Joe 1009: *"until further notice, we're working one leg at a time until we've got a handle on the
mech / drop the x-cross mech - I was wrong to bring that online now / I'm going to use a mech from
octo-sig: rule#1 / walk forward from the open until rule#1 is met, and ws12r is oob. tell me the
timestamp when these two qualify"*.

rule#1 is `optimus9.compute.rule1_gate.gate` - his 0923/0924/0929 mech, unmodified. Its fence is
27/73, oob is 15/85, the window is the last 7 min and BACKWARD ONLY.

The walk tests EVERY bar from the open. The first bar where both hold is the answer.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from optimus9.compute.rule1_gate import gate
from optimus9.analysis.jig import Jig, anchor_floater
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts); TF = C.TRIG_TF
ts = np.asarray(SC.ts[:N], np.int64)
R = {t: np.asarray(C.R[t], float)[:N] for t in (1, 2, 3, TF)}
# rule#1's knobs live in v3_config, the same place build_wsf_trades.py:178-180 reads them.
# There is no rule1_config table - that was my guess and it does not exist.
# rule#1's knobs live in `trade_config`, read via TC.load - exactly what build_wsf_trades.py:155
# and :178-180 do. My first two guesses were wrong: there is no rule1_config table, and v3_config
# does not carry them either.
from optimus9.compute import trade_config as TC
db = DatabaseManager(**get_db_config()); db.connect()
# TC.WALK_V 4 is the WALK's config version and the only one carrying walk_rule1_back_min.
# TC.V 3 - the default - does not have it, so loading the default silently fell back to the
# signal gate's 7.0. report_leash_walk.py:124 loads WALK_V for exactly this reason.
V3 = TC.load(db, TC.WALK_V)
db.disconnect()
FENCE = (float(V3['rule1_fence_lo']), float(V3['rule1_fence_hi']))
# THE WALK'S OWN WINDOW, not the signal gate's. Two knobs exist and they differ:
#   rule1_back_min       7.0 min - the signal gate, build_wsf_trades.py:180
#   walk_rule1_back_min  5   min - THE WALK's, Joe 1001 asked 5 or 7 for that row and said *"5"*
# This script walks, so it reads the walk knob. Using the 7 was my error.
assert 'walk_rule1_back_min' in V3, \
    'wsf_trade_config v%d has no walk_rule1_back_min - do not fall back to the signal gate' % TC.WALK_V
BACK = int(float(V3['walk_rule1_back_min']) * 60 / 5)
_WK = 'walk_rule1_back_min'
FWD = int(float(V3.get('rule1_fwd_min', 0)) * 60 / 5)
CLAMP = str(V3.get('rule1_run_clamp', 'window'))
OOB = (15.0, 85.0)
print('# from trade_config v%s: fence %.0f/%.0f, back %.1f min = %d bars (%s), fwd %d, clamp %r'
      % (V3.get('_version'), FENCE[0], FENCE[1], BACK * 5 / 60.0, BACK, _WK, FWD, CLAMP),
      flush=True)
assert FWD == 0, 'rule1_fwd_min must be 0 - a forward read is not causal, Joe 0929'
with Jig(END_MS, hours=HOURS, warmup=WARMUP) as J:
    JT = np.asarray(J.ts, dtype=np.int64)
    G30R = np.asarray(J.causal.line('gcws30r'), float)
G30 = G30R[np.clip(np.searchsorted(JT, ts), 0, len(JT) - 1)]
OPEN = os.environ.get('X_OPEN', '2026-07-15 03:13:15')
DR = int(os.environ.get('X_DR', -1))
k0 = SC.K(OPEN)
print('# the leg opens %s, dr %+d. walking forward bar by bar.' % (OPEN, DR), flush=True)
oob12 = lambda j: (float(R[TF][j]) >= OOB[1]) if DR > 0 else (float(R[TF][j]) <= OOB[0])
# THE ws12r DWELL. Joe 1009: *"add the ws12r dwell"*. oob_gate_bars 72, so the dwell completes on
# the 73rd bar of an UNBROKEN oob run - the same test the >ws12 mech's handover uses. A bar only
# qualifies once its own run has survived that long.
DW = C.GATE_BARS + 1
ob = np.array([oob12(j) for j in range(N)], bool)
runstart = np.full(N, -1, np.int64)
cur = -1
for j in range(N):
    if ob[j]:
        if cur < 0: cur = j
        runstart[j] = cur
    else:
        cur = -1
print('# the ws%dr dwell is %d bars = %.1f min of UNBROKEN oob' % (TF, DW, DW * 5 / 60.0),
      flush=True)
hits = []
for j in range(k0, N):
    if not ob[j]:
        continue
    if j - int(runstart[j]) + 1 < DW:
        continue
    af = anchor_floater(R[1], PX, DR, j)
    g = gate(R[1], R[2], R[3], G30, DR, j, BACK, FENCE, OOB,
             int(af['fired']) if af else 0, fwd_bars=FWD, run_clamp=CLAMP)
    if g.get('open'):
        hits.append((j, g, af))
        if len(hits) >= int(os.environ.get('X_N', 1)):
            break
if not hits:
    print('\n# rule#1 and ws%dr oob never both hold after the open' % TF)
else:
    for j, g, af in hits:
        print('\n########## BOTH QUALIFY AT %s   —   %.1f min after the open'
              % (U(j), (int(ts[j]) - int(ts[k0])) / 60000.0))
        rs = int(runstart[j])
        box(('the test', 'value'),
            [('ws%dr at this bar' % TF, '%.4f' % float(R[TF][j])),
             ('ws%dr oob on dr %+d?' % (TF, DR), 'YES'),
             ('its oob run opened', U(rs)),
             ('the run has held', '%d bars = %.1f min' % (j - rs + 1, (j - rs + 1) * 5 / 60.0)),
             ('the %d-bar dwell' % DW, 'COMPLETE'),
             ('the dwell completed at', U(rs + DW - 1)),
             ('rule#1 gate', 'OPEN'),
             ('ws1r', '%.4f' % float(R[1][j])),
             ('ws2r', '%.4f' % float(R[2][j])),
             ('ws3r', '%.4f' % float(R[3][j])),
             ('gcws30r', '%.4f' % float(G30[j])),
             ('pxs', '%.6f' % float(PX[j]))]
            + [(str(kk), str(vv)) for kk, vv in sorted(g.items()) if kk != 'open'])
