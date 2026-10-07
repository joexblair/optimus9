"""The ib-wob-6 / hop2 chain, every leg traced bar by bar. Joe 1007: *"wob6 is fine. where did the
07:51 exit move to, and how did it get there?"*"""
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

D, START, FIRST = '2026-09-25', '02:48:50', 1
IB_WOB, HOP_MODE, SHOW = 6, "hop2", (1, 2, 5, 6)       # the legs to print in full
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

def run_leg(k, d):
    tr = []; a = arm_bar(k, d)
    if a is None: return None, 'no arm', tr
    tr.append((a, 'exit-armed — ws2Mage %s %.0f (%.2f)'
               % ('over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO, float(M2[a]))))
    rider = None; stash = None; ib_run = 0; ib_k = None
    for j in range(a, SC.TAPE_LAST + 1):
        if rider is None:
            c = [t for t in LIN_TF if oobf(t, j, d)]
            if c:
                rider = max(c); tr.append((j, 'rider ws%d  (r %.2f oob)' % (rider, float(R[rider][j]))))
            continue
        if m2oob(j, d):
            ib_run = 0
            hi = min(rider + LIN_HOP, LIN_TF[-1])
            up = [t for t in range(rider + 1, hi + 1) if mt(t, j, d)]
            if up:
                rider = max(up)
                tr.append((j, 'RIDE UP -> ws%d  (mom-true, ws2Mage still oob %.2f)' % (rider, float(M2[j]))))
                continue
            if stash is None and xcond(rider, j, d):
                stash = j
                tr.append((j, 'x-cross STASHED on ws%d  (ws2Mage %.2f still oob)' % (rider, float(M2[j]))))
            continue
        ib_run += 1
        if ib_run == IB_WOB:
            ib_k = j
            live = any(mt(t, j, d) for t in LIN_TF if t >= rider)
            tr.append((j, 'ws2Mage ib CONFIRMED (%d bars, %.2f) — momentum at/above ws%d: %s'
                       % (IB_WOB, float(M2[j]), rider, 'YES' if live else 'NO')))
            if stash is not None and not live:
                tr.append((j, 'stashed x-cross (from %s) FIRES' % SC.U(stash)))
                return j, 'stashed x-cross', tr
        if ib_k is not None:
            cand = [t for t in range(rider + 1, min(rider + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, j, d)]
            if cand:
                rider = max(cand); tr.append((j, 'baton -> ws%d oob' % rider)); continue
            if xcond(rider, j, d): return j, 'x-cross', tr
            if ST[(rider, d)][j]: return j, 'final stalled', tr
    return None, 'tape end', tr

k = SC.K('%s %s' % (D, START)); d = FIRST; rows = []
for leg in range(1, 41):
    xk, why, tr = run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
    rows.append(dict(leg=leg, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, real=real, why=why))
    if leg in SHOW:
        print('\n## LEG %d — %s   open %s   pxs %.6f' % (leg, rows[-1]['side'], SC.U(k), p0))
        print('| ts | +min | event | pxs | pct |'); print('|---|---|---|---|---|')
        print('| %s | +0.0 | OPEN | %.6f | +0.0000 |' % (SC.U(k), p0))
        for j, lbl in tr:
            print('| %s | %+.1f | %s | %.6f | %+.4f |'
                  % (SC.U(j), (int(SC.ts[j]) - int(SC.ts[k])) / 60000.0, lbl, float(PX[j]),
                     (float(PX[j]) - p0) / p0 * 100.0 * sgn))
        print('| %s | %+.1f | **EXIT %s** | %.6f | **%+.4f** |'
              % (SC.U(xk), (int(SC.ts[xk]) - int(SC.ts[k])) / 60000.0, why, float(PX[xk]), real))
    k = xk; d = -d

print('\n# THE CHAIN, ib wob %d / %s' % (IB_WOB, HOP_MODE))
print('| leg | side | open | exit | hold min | realised | why |'); print('|---|---|---|---|---|---|---|')
for r in rows:
    print('| %d | %s | %s | %s | %.1f | **%+.4f** | %s |'
          % (r['leg'], r['side'], SC.U(r['open']), SC.U(r['exit']),
             (int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0, r['real'], r['why']))
print('| **total** | | %s | %s | | **%+.4f** | |'
      % (SC.U(rows[0]['open']), SC.U(rows[-1]['exit']), sum(r['real'] for r in rows)))
