"""Why does _lineworker's LIVE variant disagree with _sweep2's winner? 1008.

Both claim the same config. _sweep2 said net +4.0627 on 1636 legs; _lineworker's LIVE r said
-113.3843 on 1562. A systematic gap in my own harness invalidates the whole line sweep, so it gets
found before anything is reported.

Runs BOTH paths in ONE process and compares, leg by leg, to the first divergence.
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

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
_ST = {}
for t in C.ALL_TF:
    with momo_config(C.BANK[t]):
        with momo_window(int(C.BANK[t]['k_window']) * t):
            _ST[t] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))
WIN = dict(mae_stop_pct=2.5, reent_xwob=18, lin_hop=2, stall_n=4, momo_fence_r=20.0,
           dip_fence=53.0, dip_dwell_bars=6, oob_gate_bars=72, ceil_hi=23, ceil_trig_tf=8,
           rrev_wob=1, div_lines=(1, 2, 3), oob_gate_fence=15.0)
_idx = np.arange(N)

def knobs():
    C.MAE_STOP = WIN['mae_stop_pct']; C.LIN_HOP = WIN['lin_hop']
    C.CEIL_HI = WIN['ceil_hi']; C.TRIG_TF = WIN['ceil_trig_tf']
    C.GATE_BARS = WIN['oob_gate_bars']; C.DIP_DWELL = WIN['dip_dwell_bars']
    C.DIP_FENCE = WIN['dip_fence']; C.DIP_HI = C.DIP_FENCE; C.DIP_LO = 100.0 - C.DIP_FENCE
    C.EXF_LO = WIN['momo_fence_r']; C.EXF_HI = 100.0 - C.EXF_LO
    T.EXF_LO = C.EXF_LO; T.EXF_HI = C.EXF_HI
    C.G_LO = WIN['oob_gate_fence']; C.G_HI = 100.0 - C.G_LO
    C.DIV_TFS = list(WIN['div_lines']); C.RREV = WIN['rrev_wob']
    C.REV = {t: _mage_rev(C.R[t], C.RREV) for t in C.DIV_TFS}
    C.ST = {(t, dd): stall_mask(C.RL[t], dd, int(WIN['stall_n']), *_ST[t])
            for t in C.ALL_TF for dd in (-1, +1)}
    w = int(WIN['reent_xwob'])
    fin = np.isfinite(T.X1) & np.isfinite(T.R1)
    def holds(m):
        run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
        h = run >= w; cf = h & ~np.r_[False, h[:-1]]
        return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
    T.XWOB = w
    T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin)]
                       + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin)], key=lambda z: z[1])

def run():
    legs = []; k, d = 1, +1; g = 0
    while True:
        g += 1
        if g > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        legs.append((k, d, xk, why))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    return legs

# ---- path A: score39's own arrays, exactly as _sweep2 had them
RL0 = dict(C.RL); R0 = dict(C.R); R10 = T.R1
knobs(); A = run()
print('# A  score39 arrays            : %d legs' % len(A), flush=True)

# ---- path B: the SAME lines reloaded from the cache by _lineworker's loader
MAP = json.load(open('/home/joe/.claude/jobs/6eb9931e/tmp/linemap.json'))
V = MAP['r|LIVE']
C.RL = {t: np.asarray(np.load(V['paths']['ws%dr' % t], mmap_mode='r'), float)
        for t in range(1, 26)}
C.R = {t: C.RL[t][:N] for t in C.RL}
T.R1 = C.R[1]
knobs(); B = run()
print('# B  the cache paths reloaded  : %d legs' % len(B), flush=True)

print('\n# ARE THE ARRAYS THE SAME?')
rows = []
for t in (1, 2, 8, 12, 25):
    a = np.asarray(RL0[t], float); b = np.asarray(C.RL[t], float)
    same = a.shape == b.shape and np.array_equal(np.nan_to_num(a, nan=-999),
                                                 np.nan_to_num(b, nan=-999))
    rows.append(('ws%dr' % t, str(a.shape), str(b.shape), 'IDENTICAL' if same else 'DIFFERENT',
                 '%.6f' % float(np.nanmax(np.abs(a[:N] - b[:N]))) if a.shape == b.shape else '—'))
box(('line', 'score39 shape', 'cache shape', 'equal?', 'max abs diff over the first N'), rows)

print('\n# WHERE THE TWO CHAINS FIRST DIVERGE')
rows = []
for i in range(min(len(A), len(B))):
    if A[i] != B[i]:
        for j in range(max(0, i - 2), min(len(A), len(B), i + 3)):
            rows.append((str(j), U(A[j][0]), 'LONG' if A[j][1] > 0 else 'SHORT', U(A[j][2]),
                         A[j][3], U(B[j][0]), 'LONG' if B[j][1] > 0 else 'SHORT', U(B[j][2]),
                         B[j][3], 'SAME' if A[j] == B[j] else '** DIVERGES **'))
        break
else:
    rows.append(('—', '—', '—', '—', '—', '—', '—', '—', '—',
                 'the first %d legs are identical' % min(len(A), len(B))))
box(('leg', 'A open', 'A side', 'A exit', 'A why', 'B open', 'B side', 'B exit', 'B why',
     'verdict'), rows)
print('\n# A has %d legs, B has %d' % (len(A), len(B)), flush=True)
