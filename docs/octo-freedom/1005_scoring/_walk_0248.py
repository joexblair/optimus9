"""09-25 02:48 — lineage walk started by ws2Mage crossing to HIGH oob, exited by the x-cross.

JOE 1007: *"let's test the lineage to x-cross mech on a walk from the validated -dr 09-25 02:48.
let's use ws2Mage crossing to high oob as the trigger to start the lineage walk. the target is +dr -
we aren't flipping SHORTS and LONGS"*.

EVERYTHING IS READ ON THE +dr SIDE regardless of the octo-sig's own dr, which is -1 here. oob is
r >= 85, in-fence is r < 83, the x-cross is UNDER. The position is the +dr direction and is never
flipped.

THE TRIGGER is ws2Mage crossing UP through the oob_hi fence (85). Not a reversal flag - a level
crossing, which is what Joe asked for.
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

D, SIG = '2026-09-25', '02:48:50'
DRS = +1                                  # everything read on the +dr side, Joe 1007
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF = 100.0 - float(SC.LG['momo_fence_r'])            # 83.0
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
    ST[t] = stall_mask(SC.Rl[t], DRS, int(SC.LG['stall_n']), s_, n_)
_P('producers ready, +dr side')

band = lambda t, k: ('O' if float(R[t][k]) >= SC.HI else
                     ('x' if float(R[t][k]) >= EXF else '.'))
oobf = lambda t, k: float(R[t][k]) >= SC.HI
def xcond(h, k):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    return (xv < float(R[t1][k]) and xv < float(R[t2][k])
            and band(t1, k) == '.' and band(t2, k) == '.')

k_sig = SC.K('%s %s' % (D, SIG))
print('\n## %s %s   octo-sig dr %+d   walk read on dr %+d   position: +dr, never flipped'
      % (D, SIG, int(SC.DRv[k_sig]), DRS))

# 1. the trigger
trig = None
for k in range(k_sig, SC.TAPE_LAST + 1):
    if float(M2[k]) >= SC.HI and float(M2[k - 1]) < SC.HI:
        trig = k; break
print('\n# 1. ws2Mage CROSSES TO HIGH oob (>= %.0f)' % SC.HI)
if trig is None:
    print('- never, to the end of the tape'); raise SystemExit
print('| ts | +min from the octo-sig | ws2Mage prev | ws2Mage | pxs |')
print('|---|---|---|---|---|')
print('| **%s** | %+.1f | %.2f | %.2f | %.6f |'
      % (SC.U(trig), (int(SC.ts[trig]) - int(SC.ts[k_sig])) / 60000.0,
         float(M2[trig - 1]), float(M2[trig]), float(PX[trig])))

print('\n# THE r LADDER AT THE TRIGGER %s' % SC.U(trig))
print('| TF | r | band |'); print('|---|---|---|')
for t in LIN_TF:
    print('| ws%d | %.2f | %s |' % (t, float(R[t][trig]), band(t, trig)))

# 2. the lineage walk from the trigger, +dr side
p0 = float(PX[trig])
ev = [(k_sig, 'octo-sig %s (dr %+d)' % (SIG, int(SC.DRv[k_sig])), float(PX[k_sig])),
      (trig, 'TRIGGER — ws2Mage crosses high oob — lineage walk starts', p0)]
holder = None; qual = False; exit_k = None; why = None
for k in range(trig, SC.TAPE_LAST + 1):
    if holder is None:
        if oobf(1, k):
            holder, qual = 1, True
            ev.append((k, 'holder ws1 — r %.2f oob' % float(R[1][k]), float(PX[k]))); continue
        if any(oobf(t, k) for t in LIN_TF):
            holder = max(t for t in LIN_TF if oobf(t, k)); qual = True
            ev.append((k, 'holder ws%d — highest oob line at the trigger (r %.2f)'
                       % (holder, float(R[holder][k])), float(PX[k])))
        continue
    cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, k)]
    if cand:
        holder = max(cand); qual = True
        ev.append((k, 'baton -> ws%d oob (r %.2f)' % (holder, float(R[holder][k])), float(PX[k])))
        continue
    if qual and xcond(holder, k):
        t1, t2 = holder + 1, holder + 2
        ev.append((k, 'EXIT x-cross — ws%dx %.2f under ws%dr %.2f and ws%dr %.2f, both in-fence'
                   % (holder, float(X[holder][k]), t1, float(R[t1][k]), t2, float(R[t2][k])),
                   float(PX[k])))
        exit_k, why = k, 'x-cross'; break
    if ST[holder][k]:
        ev.append((k, 'EXIT final stalled — holder ws%d (r %.2f %s)'
                   % (holder, float(R[holder][k]), band(holder, k)), float(PX[k])))
        exit_k, why = k, 'final stalled'; break

if exit_k is not None:
    seg = PX[trig:exit_k + 1]; idx = np.arange(trig, exit_k + 1)
    ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
    jf, jm = int(seg.argmax()), int(seg.argmin())
    ev.append((int(idx[jf]), 'MFE %+.4f' % ((float(seg[jf]) - p0) / p0 * 100.0), float(seg[jf])))
    ev.append((int(idx[jm]), 'MAE %+.4f' % ((float(seg[jm]) - p0) / p0 * 100.0), float(seg[jm])))
ev.sort(key=lambda x: x[0])
print('\n# 2. THE WALK, timestamped   (pct is the +dr / LONG direction from the trigger)')
print('| ts | +min | event | pxs | pct from trigger |'); print('|---|---|---|---|---|')
for k, lbl, px in ev:
    print('| %s | %+.1f | %s | %.6f | %+.4f |'
          % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[trig])) / 60000.0, lbl, px, (px - p0) / p0 * 100.0))
if exit_k is not None:
    print('\n- exit reason: **%s**' % why)
    print('- realised trigger to exit, +dr direction: **%+.4f**'
          % ((float(PX[exit_k]) - p0) / p0 * 100.0))
