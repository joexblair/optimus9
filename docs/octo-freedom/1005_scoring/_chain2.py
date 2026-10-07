"""THE CHAIN with Joe's stash trick. 1007.

JOE:
  the trick   *"ws2Mage crossing oob is only the beginning of ws2's climb ... pxs keeps pace with
              the Mage until the Mage crosses into ib. stash the ws1x-cross until ws2Mage crosses
              into ib, then test for momentum again. if there's no momentum, then let the stashed
              ws1x-cross fire"*
  the wob     *"add a wob to ws2Mage crossing to IB"* - value NOT named, so it is SWEPT.
  ride up     *"test for momentum on each bar while ws2Mage is oob. if you see a higher TF than the
              current rider, ride it"*

THE LEG, with the trick:
  OPEN        the previous leg's exit (or the seed octo-sig).
  exit-armed  ws2Mage crosses the target-side fence (over 85 for +dr, under 15 for -dr).
  while ws2Mage is oob: every bar, if a HIGHER TF than the rider is mom-true, the rider moves up.
              An x-cross in this window is STASHED, not acted on.
  ib          ws2Mage crosses back inside the fence and HOLDS for IB_WOB bars.
              At that bar: if there is no momentum, a stashed x-cross fires. Otherwise the walk
              continues normally and the next x-cross or stall exits.

TWO READINGS OF "a higher TF", both run:
  hop2   the rider may only move within +LIN_HOP (2), as the lineage rule says
  any    the rider may move to ANY higher mom-true TF

MOMENTUM = mom-true, momo_g_why in ('momo','curl'), Joe 1006.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%6.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D = os.environ.get('W_DAY', '2026-09-25')
START = os.environ.get('W_START', '02:48:50')
FIRST = int(os.environ.get('W_TARGET', '1'))
MAXLEG = int(os.environ.get('W_MAXLEG', '40'))
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
NEED = sorted(set(LIN_TF) | {13, 14})
R = {t: SC.LD(t * 60, 'r') for t in NEED}
X = {t: SC.LD(t * 60, 'x') for t in LIN_TF}
M2 = SC.Mg[2]; PX = SC.PX
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(SC.Rl[t], dd, int(SC.LG['stall_n']), s_, n_)
_mt = {}
def mt(t, k, d):
    key = (t, k, d)
    if key in _mt: return _mt[key]
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            v = momo_g_why(SC.Rl[t], int(d), int(k))[0] in ('momo', 'curl')
    _mt[key] = v; return v
_P('producers ready')

def band(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
m2oob = lambda k, d: (float(M2[k]) >= SC.HI) if d > 0 else (float(M2[k]) <= SC.LO)
def xcond(h, k, d):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    c = (xv < float(R[t1][k]) and xv < float(R[t2][k])) if d > 0 else \
        (xv > float(R[t1][k]) and xv > float(R[t2][k]))
    return c and band(t1, k, d) == '.' and band(t2, k, d) == '.'
def arm_bar(k_from, d):
    for k in range(k_from + 1, SC.TAPE_LAST + 1):
        if d > 0 and float(M2[k]) >= SC.HI and float(M2[k - 1]) < SC.HI: return k
        if d < 0 and float(M2[k]) <= SC.LO and float(M2[k - 1]) > SC.LO: return k
    return None

def run_leg(k, d, ib_wob, hop_mode):
    """-> (exit_k, why, trace) or (None, why, trace)"""
    tr = []
    a = arm_bar(k, d)
    if a is None: return None, 'no arm', tr
    tr.append((a, 'exit-armed — ws2Mage %s fence' % ('over' if d > 0 else 'under')))
    rider = None; stash = None; ib_run = 0; ib_k = None
    for j in range(a, SC.TAPE_LAST + 1):
        if rider is None:
            c = [t for t in LIN_TF if oobf(t, j, d)]
            if c:
                rider = max(c); tr.append((j, 'rider ws%d (r %.2f oob)' % (rider, float(R[rider][j]))))
            continue
        in_oob = m2oob(j, d)
        if in_oob:
            ib_run = 0
            hi = LIN_TF[-1] if hop_mode == 'any' else min(rider + LIN_HOP, LIN_TF[-1])
            up = [t for t in range(rider + 1, hi + 1) if mt(t, j, d)]
            if up:
                rider = max(up)
                tr.append((j, 'ride up -> ws%d (mom-true, ws2Mage oob)' % rider)); continue
            if stash is None and xcond(rider, j, d):
                stash = j; tr.append((j, 'x-cross STASHED on ws%d' % rider))
            continue
        # ws2Mage is inside the fence
        ib_run += 1
        if ib_run == ib_wob:
            ib_k = j
            live = any(mt(t, j, d) for t in LIN_TF if t >= rider)
            tr.append((j, 'ws2Mage ib confirmed (wob %d) — momentum above ws%d: %s'
                       % (ib_wob, rider, 'YES' if live else 'NO')))
            if stash is not None and not live:
                tr.append((j, 'stashed x-cross FIRES')); return j, 'stashed x-cross', tr
        if ib_k is not None:
            cand = [t for t in range(rider + 1, min(rider + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, j, d)]
            if cand:
                rider = max(cand); tr.append((j, 'baton -> ws%d oob' % rider)); continue
            if xcond(rider, j, d): return j, 'x-cross', tr
            if ST[(rider, d)][j]: return j, 'final stalled', tr
    return None, 'tape end', tr

print('\n# THE SWEEP — ib wob x hop mode, chained from %s %s' % (D, START))
print('| ib wob | bars | seconds | hop mode | legs | positive | total realised | worst MAE |')
print('|---|---|---|---|---|---|---|---|')
best = None
for hop_mode in ('hop2', 'any'):
    for ib_wob in (1, 2, 3, 6, 12):
        k = SC.K('%s %s' % (D, START)); d = FIRST; legs = []
        for leg in range(MAXLEG):
            xk, why, tr = run_leg(k, d, ib_wob, hop_mode)
            if xk is None: break
            p0 = float(PX[k])
            sgn = 1 if d > 0 else -1
            seg = PX[k:xk + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
            mae = (float(seg.min() if d > 0 else seg.max()) - p0) / p0 * 100.0 * sgn
            legs.append(dict(real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, mae=mae, why=why))
            k = xk; d = -d
        if not legs: continue
        tot = sum(L['real'] for L in legs)
        print('| %d | %d | %d | %s | %d | %d | **%+.4f** | %+.4f |'
              % (ib_wob, ib_wob, ib_wob * 5, hop_mode, len(legs),
                 sum(1 for L in legs if L['real'] > 0), tot, min(L['mae'] for L in legs)))
        if best is None or tot > best[0]: best = (tot, ib_wob, hop_mode, legs)

if best:
    tot, ib_wob, hop_mode, legs = best
    print('\n- best: ib wob %d (%d s), hop mode %s, **%+.4f** over %d legs'
          % (ib_wob, ib_wob * 5, hop_mode, tot, len(legs)))
    w = {}
    for L in legs: w[L['why']] = w.get(L['why'], 0) + 1
    print('\n# WHY THE BEST CHAIN EXITED')
    print('| why | legs |'); print('|---|---|')
    for kk in sorted(w, key=lambda z: -w[z]): print('| %s | %d |' % (kk, w[kk]))
