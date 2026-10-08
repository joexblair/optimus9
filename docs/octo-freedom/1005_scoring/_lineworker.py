"""ONE CHAIN RUN AGAINST ONE LINE VARIANT. 1008. Launched in parallel, one process per variant.

    python3 _lineworker.py '<variant key>'

Reads `linemap.json` (written by `_buildlines.py`), swaps that variant's r or Mage arrays into
`_chain10`'s module state, runs chain 0 over the whole 95-day tape, and prints ONE json line.

WHAT A VARIANT TOUCHES, and nothing else:
  an r variant     C.RL ws1..ws25, C.R, C.ST (every stall mask derives from RL), T.R1 (the
                   re-entry router's ws1r) and C.REV (the divergence reversal arrays).
  a Mage variant   C.M2 (the arm, ws2Mage), C.G1 (the dip, ws1Mage) and T.MG (gate A's ws12Mage
                   against ws1Mage).
                   dr IS NOT TOUCHED because chain 0 never reads it - the sides alternate. A Mage
                   respec WOULD move dr, and that matters for any walk arm, not for this one.

THE KNOBS ARE HELD AT THE §25 STAGED WINNER, so a line variant is measured against the best
mech config found, not against the banked one.

NET AFTER DRAG at 0.11 per leg. Slippage unset.
"""
import os, sys, json, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.analysis.jig import stall_mask
from optimus9.analysis.lr_v2 import _mage_rev
import _chain10 as C
import _chain_2day as T

KEY = sys.argv[1]
MAP = json.load(open('/home/joe/.claude/jobs/6eb9931e/tmp/linemap.json'))
V = MAP[KEY]
SC, PX = C.SC, C.PX
N = len(SC.ts); FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
SEED, LAST = 1, N - 1
_ST = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _ST[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))

WIN = dict(mae_stop_pct=2.5, reent_xwob=18, lin_hop=2, stall_n=4, momo_fence_r=20.0,
           dip_fence=53.0, dip_dwell_bars=6, oob_gate_bars=72, ceil_hi=23, ceil_trig_tf=8,
           rrev_wob=1, div_lines=(1, 2, 3), oob_gate_fence=15.0)

def load(name):
    p = V['paths'][name]
    return np.asarray(np.load(p, mmap_mode='r'), float)

if V['role'] == 'r':
    C.RL = {t: load('ws%dr' % t) for t in range(1, 26)}
    C.R = {t: C.RL[t][:N] for t in C.RL}
    T.R1 = C.R[1]
    C.ST = {(t, dd): stall_mask(C.RL[t], dd, int(WIN['stall_n']), *_ST[t])
            for t in C.ALL_TF for dd in (-1, +1)}
else:
    MG = {t: load('ws%dMage' % t)[:N] for t in range(1, 13)}
    C.M2 = MG[2]; C.G1 = MG[1]; T.MG = MG
    C.ST = {(t, dd): stall_mask(C.RL[t], dd, int(WIN['stall_n']), *_ST[t])
            for t in C.ALL_TF for dd in (-1, +1)}

# the knobs, held at the staged winner
C.MAE_STOP = WIN['mae_stop_pct']; C.LIN_HOP = WIN['lin_hop']
C.CEIL_HI = WIN['ceil_hi']; C.TRIG_TF = WIN['ceil_trig_tf']
C.GATE_BARS = WIN['oob_gate_bars']; C.DIP_DWELL = WIN['dip_dwell_bars']
C.DIP_FENCE = WIN['dip_fence']; C.DIP_HI = C.DIP_FENCE; C.DIP_LO = 100.0 - C.DIP_FENCE
C.EXF_LO = WIN['momo_fence_r']; C.EXF_HI = 100.0 - C.EXF_LO
T.EXF_LO = C.EXF_LO; T.EXF_HI = C.EXF_HI
C.G_LO = WIN['oob_gate_fence']; C.G_HI = 100.0 - C.G_LO
C.DIV_TFS = list(WIN['div_lines']); C.RREV = WIN['rrev_wob']
C.REV = {t: _mage_rev(C.R[t], C.RREV) for t in C.DIV_TFS}
_idx = np.arange(N)
_fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m):
    w = int(WIN['reent_xwob'])
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = int(WIN['reent_xwob'])
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & _fin)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & _fin)], key=lambda z: z[1])

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

legs = []; k, d = SEED, +1; guard = 0
while True:
    guard += 1
    if guard > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    legs.append(dict(open=k, exit=xk, d=d, why=why, hand=bool(hand),
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, day=DAYOF(k)))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, LAST)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= LAST: break
    k = xk; d = -d

mae = mfe = real = 0.0
per = collections.defaultdict(float)
perl = collections.Counter(); pers = collections.Counter()
for r in legs:
    a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
    mae += a_; mfe += f_; real += r['real']; per[r['day']] += r['real']
    perl[r['day']] += 1
    pers[r['day']] += 1 if r['why'] == 'mae breach' else 0
n = len(legs); st = sum(1 for r in legs if r['why'] == 'mae breach'); drag = n * FEE
days = sorted(per)
print(json.dumps(dict(key=KEY, role=V['role'], label=V['label'], spec=V['spec'],
                      legs=n, pos=sum(1 for r in legs if r['real'] > 0), stops=st,
                      hand=sum(1 for r in legs if r['hand']),
                      mae=round(mae, 4), mfe=round(mfe, 4), gross=round(real, 4),
                      drag=round(drag, 4), net=round(real - drag, 4),
                      npl=round((real - drag) / n, 6) if n else 0.0,
                      sr=round(100.0 * st / n, 2) if n else 0.0,
                      mm=round(mfe / mae, 3) if mae else None,
                      third1=round(sum(per[x] for x in days[:len(days)//3]), 4),
                      third2=round(sum(per[x] for x in days[len(days)//3:2*len(days)//3]), 4),
                      third3=round(sum(per[x] for x in days[2*len(days)//3:]), 4),
                      perday={x: round(per[x], 4) for x in days},
                      perlegs={x: perl[x] for x in days},
                      perstops={x: pers[x] for x in days})), flush=True)
