"""THE CHAIN — each trade opens where the last one closed, arms on ws2Mage, exits on the lineage walk.

JOE 1007:
  the open   *"leg 1 didn't get the memo about ws2Mage oob - the `open` for leg 1 was 02:48"*
             -> the ws2Mage crossing is the ARM, never the open. The open is the octo-sig for leg 1
                and the previous leg's exit thereafter.
  the target *"05:16 is -dr, so your target is +dr"* -> the target flips every leg.
  the arm    *"let's use ws2Mage crossing to high oob as the trigger"* / *"-dr for ws2Mage is
             crossing under 15"* -> the arm is ws2Mage crossing the fence ON THE TARGET SIDE.

ONE LEG:
  OPEN        at the previous exit (or the octo-sig, for leg 1). Side = the target dr.
  exit-armed  the next ws2Mage crossing of the target-side fence - over 85 for +dr, under 15 for -dr.
  exit        the lineage walk from the arm, read on the target dr: x-cross or final stalled.

The chain runs until a leg finds no arm or no exit. NO LEG LIMIT - Joe has not named one.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%5.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D = os.environ.get('W_DAY', '2026-09-25')
START = os.environ.get('W_START', '02:48:50')     # the octo-sig that seeds the chain
FIRST_TARGET = int(os.environ.get('W_TARGET', '1'))   # leg 1 targets +dr
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
_P('producers ready')

def band(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
def oobf(t, k, d):
    v = float(R[t][k]); return (v >= SC.HI) if d > 0 else (v <= SC.LO)
def xcond(h, k, d):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    c = (xv < float(R[t1][k]) and xv < float(R[t2][k])) if d > 0 else \
        (xv > float(R[t1][k]) and xv > float(R[t2][k]))
    return c and band(t1, k, d) == '.' and band(t2, k, d) == '.'
def arm_bar(k_from, d):
    """next ws2Mage crossing of the fence on the target side."""
    for k in range(k_from + 1, SC.TAPE_LAST + 1):
        if d > 0 and float(M2[k]) >= SC.HI and float(M2[k - 1]) < SC.HI: return k
        if d < 0 and float(M2[k]) <= SC.LO and float(M2[k - 1]) > SC.LO: return k
    return None

k = SC.K('%s %s' % (D, START)); d = FIRST_TARGET
legs = []
for leg in range(1, 40):
    side = 'LONG' if d > 0 else 'SHORT'; sgn = 1 if d > 0 else -1
    p0 = float(PX[k])
    a = arm_bar(k, d)
    if a is None: print('\n- leg %d: no ws2Mage arm on the dr %+d side. chain ends.' % (leg, d)); break
    ev = [(k, 'OPEN %s' % side, p0),
          (a, 'exit-armed — ws2Mage %s %.0f (%.2f -> %.2f)'
           % ('over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO,
              float(M2[a - 1]), float(M2[a])), float(PX[a]))]
    holder = None; qual = False; xk = None; why = None
    for j in range(a, SC.TAPE_LAST + 1):
        if holder is None:
            c = [t for t in LIN_TF if oobf(t, j, d)]
            if c:
                holder = max(c); qual = True
                ev.append((j, 'lineage starts — holder ws%d (r %.2f oob)' % (holder, float(R[holder][j])),
                           float(PX[j])))
            continue
        cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, j, d)]
        if cand:
            holder = max(cand); qual = True
            ev.append((j, 'baton -> ws%d oob (r %.2f)' % (holder, float(R[holder][j])), float(PX[j])))
            continue
        if qual and xcond(holder, j, d):
            ev.append((j, 'EXIT x-cross — holder ws%d' % holder, float(PX[j])))
            xk, why = j, 'x-cross'; break
        if ST[(holder, d)][j]:
            ev.append((j, 'EXIT final stalled — holder ws%d (r %.2f %s)'
                       % (holder, float(R[holder][j]), band(holder, j, d)), float(PX[j])))
            xk, why = j, 'final stalled'; break
    if xk is None: print('\n- leg %d: no exit to the tape end. chain ends.' % leg); break
    seg = PX[k:xk + 1]; idx = np.arange(k, xk + 1)
    ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
    jf = int(seg.argmax()) if d > 0 else int(seg.argmin())
    jm = int(seg.argmin()) if d > 0 else int(seg.argmax())
    mfe = (float(seg[jf]) - p0) / p0 * 100.0 * sgn
    mae = (float(seg[jm]) - p0) / p0 * 100.0 * sgn
    real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
    ev.append((int(idx[jf]), 'MFE %+.4f' % mfe, float(seg[jf])))
    ev.append((int(idx[jm]), 'MAE %+.4f' % mae, float(seg[jm])))
    ev.sort(key=lambda z: z[0])
    print('\n## LEG %d — %s   open %s   target dr %+d' % (leg, side, SC.U(k), d))
    print('| ts | +min | event | pxs | pct %s |' % side); print('|---|---|---|---|---|')
    for kk, lbl, px in ev:
        print('| %s | %+.1f | %s | %.6f | %+.4f |'
              % (SC.U(kk), (int(SC.ts[kk]) - int(SC.ts[k])) / 60000.0, lbl, px,
                 (px - p0) / p0 * 100.0 * sgn))
    print('\n- arm %+.1f min, exit %+.1f min, MFE %+.4f, MAE %+.4f, **realised %+.4f** (%s), capture %.1f%%'
          % ((int(SC.ts[a]) - int(SC.ts[k])) / 60000.0, (int(SC.ts[xk]) - int(SC.ts[k])) / 60000.0,
             mfe, mae, real, why, (real / mfe * 100.0) if mfe > 0 else 0.0))
    legs.append(dict(leg=leg, side=side, open=SC.U(k), arm=SC.U(a), exit=SC.U(xk),
                     mfe=mfe, mae=mae, real=real, why=why,
                     hold=(int(SC.ts[xk]) - int(SC.ts[k])) / 60000.0))
    k = xk; d = -d

print('\n# THE CHAIN')
print('| leg | side | open | exit-armed | exit | hold min | MFE | MAE | realised | why |')
print('|---|---|---|---|---|---|---|---|---|---|')
for L in legs:
    print('| %d | %s | %s | %s | %s | %.1f | %+.4f | %+.4f | **%+.4f** | %s |'
          % (L['leg'], L['side'], L['open'], L['arm'], L['exit'], L['hold'],
             L['mfe'], L['mae'], L['real'], L['why']))
if legs:
    tot = sum(L['real'] for L in legs)
    print('| **total** | | %s | | %s | %.1f | %+.4f | | **%+.4f** | |'
          % (legs[0]['open'], legs[-1]['exit'], sum(L['hold'] for L in legs),
             sum(L['mfe'] for L in legs), tot))
    print('\n- %d legs, %d positive, worst MAE %+.4f'
          % (len(legs), sum(1 for L in legs if L['real'] > 0), min(L['mae'] for L in legs)))
