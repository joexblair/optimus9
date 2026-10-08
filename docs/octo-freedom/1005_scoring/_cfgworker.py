"""ONE CHAIN RUN AT ONE KNOB CONFIG, with per-day realised. 1008.

    python3 _cfgworker.py '<json config>'

Prints ONE json line carrying the whole per-day realised series, so ANY block - fit half, hold
half, thirds - can be scored afterwards without re-running the chain. That is the point: a config
runs once and is scored many ways.

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

CFG = json.loads(sys.argv[1])
SC, PX = C.SC, C.PX
N = len(SC.ts); FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
_ST = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _ST[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))
C.MAE_STOP = float(CFG['mae_stop_pct']); C.LIN_HOP = int(CFG['lin_hop'])
C.CEIL_HI = int(CFG['ceil_hi']); C.TRIG_TF = int(CFG['ceil_trig_tf'])
C.GATE_BARS = int(CFG['oob_gate_bars']); C.DIP_DWELL = int(CFG['dip_dwell_bars'])
C.DIP_FENCE = float(CFG['dip_fence']); C.DIP_HI = C.DIP_FENCE; C.DIP_LO = 100.0 - C.DIP_FENCE
C.EXF_LO = float(CFG['momo_fence_r']); C.EXF_HI = 100.0 - C.EXF_LO
T.EXF_LO = C.EXF_LO; T.EXF_HI = C.EXF_HI
C.G_LO = float(CFG['oob_gate_fence']); C.G_HI = 100.0 - C.G_LO
C.DIV_TFS = list(CFG['div_lines']); C.RREV = int(CFG['rrev_wob'])
C.REV = {t: _mage_rev(C.R[t], C.RREV) for t in C.DIV_TFS}
C.ST = {(t, dd): stall_mask(C.RL[t], dd, int(CFG['stall_n']), *_ST[t])
        for t in C.ALL_TF for dd in (-1, +1)}
w = int(CFG['reent_xwob']); _idx = np.arange(N)
fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m):
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = w
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin)], key=lambda z: z[1])

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

legs = []; k, d = 1, +1; g = 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    legs.append(dict(day=DAYOF(k), why=why, open=k, exit=xk, dd=d,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

per = collections.defaultdict(lambda: [0.0, 0, 0, 0.0, 0.0])   # real, legs, stops, mae, mfe
for r in legs:
    a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['dd'])
    e = per[r['day']]
    e[0] += r['real']; e[1] += 1; e[2] += 1 if r['why'] == 'mae breach' else 0
    e[3] += a_; e[4] += f_
print(json.dumps(dict(cfg=CFG, legs=len(legs),
                      per={k_: [round(v[0], 4), v[1], v[2], round(v[3], 4), round(v[4], 4)]
                           for k_, v in sorted(per.items())})), flush=True)
