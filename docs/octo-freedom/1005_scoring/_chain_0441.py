"""The chained trade: OPEN at 04:41 (the previous exit), exit-armed by ws2Mage crossing under 15,
exited by the lineage walk.

JOE 1007: *"the exit is perfect, but your start was the end of the previous trade - 04:41. recreate
and reap the profit"*.

THE SHAPE, same as the lazy-g port:
  OPEN         the bar the previous trade closed on - 04:41:00, the pivot
  exit-armed   ws2Mage crosses the OPPOSITE fence. The 04:41 trade targets -dr, so the arm is
               ws2Mage crossing UNDER 15.
  exit         the lineage walk from the arm - x-cross or final stalled, whichever first.
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

D = '2026-09-25'
OPEN_TS = '04:41:00'
DRS = -1                                    # the 04:41 trade targets -dr -> SHORT
SIDE = 'SHORT'
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_LO = float(SC.LG['momo_fence_r'])
NEED = sorted(set(LIN_TF) | {13, 14})
R = {t: SC.LD(t * 60, 'r') for t in NEED}
X = {t: SC.LD(t * 60, 'x') for t in LIN_TF}
M2 = SC.Mg[2]; PX = SC.PX; LO = SC.LO
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    ST[t] = stall_mask(SC.Rl[t], DRS, int(SC.LG['stall_n']), s_, n_)
_P('producers ready')

band = lambda t, k: ('O' if float(R[t][k]) <= LO else ('x' if float(R[t][k]) <= EXF_LO else '.'))
oobf = lambda t, k: float(R[t][k]) <= LO
def xcond(h, k):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    return (xv > float(R[t1][k]) and xv > float(R[t2][k])
            and band(t1, k) == '.' and band(t2, k) == '.')

k0 = SC.K('%s %s' % (D, OPEN_TS)); p0 = float(PX[k0])
arm = next((k for k in range(k0, SC.TAPE_LAST + 1)
            if float(M2[k]) <= LO and float(M2[k - 1]) > LO), None)
ev = [(k0, 'OPEN %s — the previous trade closed here' % SIDE, p0),
      (arm, 'exit-armed — ws2Mage crosses under %.0f (%.2f -> %.2f)'
       % (LO, float(M2[arm - 1]), float(M2[arm])), float(PX[arm]))]
holder = None; qual = False; exit_k = None; why = None
for k in range(arm, SC.TAPE_LAST + 1):
    if holder is None:
        c = [t for t in LIN_TF if oobf(t, k)]
        if c:
            holder = max(c); qual = True
            ev.append((k, 'lineage starts — holder ws%d (r %.2f oob)' % (holder, float(R[holder][k])),
                       float(PX[k])))
        continue
    cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, k)]
    if cand:
        holder = max(cand); qual = True
        ev.append((k, 'baton -> ws%d oob (r %.2f)' % (holder, float(R[holder][k])), float(PX[k])))
        continue
    if qual and xcond(holder, k):
        t1, t2 = holder + 1, holder + 2
        ev.append((k, 'EXIT x-cross — ws%dx %.2f over ws%dr %.2f / ws%dr %.2f, both in-fence'
                   % (holder, float(X[holder][k]), t1, float(R[t1][k]), t2, float(R[t2][k])),
                   float(PX[k])))
        exit_k, why = k, 'x-cross'; break
    if ST[holder][k]:
        ev.append((k, 'EXIT final stalled — holder ws%d (r %.2f %s)'
                   % (holder, float(R[holder][k]), band(holder, k)), float(PX[k])))
        exit_k, why = k, 'final stalled'; break

seg = PX[k0:exit_k + 1]; idx = np.arange(k0, exit_k + 1)
ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
jf, jm = int(seg.argmin()), int(seg.argmax())
ev.append((int(idx[jf]), 'MFE %+.4f' % ((p0 - float(seg[jf])) / p0 * 100.0), float(seg[jf])))
ev.append((int(idx[jm]), 'MAE %+.4f' % ((p0 - float(seg[jm])) / p0 * 100.0), float(seg[jm])))
ev.sort(key=lambda x: x[0])

print('\n## 09-25 %s %s — opened at the previous exit, armed by ws2Mage, exited by the lineage walk'
      % (OPEN_TS, SIDE))
print('\n| ts | +min | event | pxs | pct %s |' % SIDE); print('|---|---|---|---|---|')
for k, lbl, px in ev:
    print('| %s | %+.1f | %s | %.6f | %+.4f |'
          % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0, lbl, px, (p0 - px) / p0 * 100.0))
real = (p0 - float(PX[exit_k])) / p0 * 100.0
mfe = (p0 - float(seg[jf])) / p0 * 100.0
mae = (p0 - float(seg[jm])) / p0 * 100.0
print('\n| | value |'); print('|---|---|')
print('| open | %s  %.6f |' % (SC.U(k0), p0))
print('| exit-armed | %s  (+%.1f min) |' % (SC.U(arm), (int(SC.ts[arm]) - int(SC.ts[k0])) / 60000.0))
print('| exit | %s  %.6f  (%s) |' % (SC.U(exit_k), float(PX[exit_k]), why))
print('| hold | %.1f min |' % ((int(SC.ts[exit_k]) - int(SC.ts[k0])) / 60000.0))
print('| MFE | %+.4f |' % mfe); print('| MAE | %+.4f |' % mae)
print('| **REALISED** | **%+.4f** |' % real)
print('| capture of MFE | %.1f%% |' % (real / mfe * 100.0 if mfe else 0.0))

print('\n# THE TWO-TRADE CHAIN FROM THE 02:48 OCTO-SIG')
k_a = SC.K('%s 04:35:30' % D); k_b = SC.K('%s 04:41:00' % D)
t1 = (float(PX[k_b]) - float(PX[k_a])) / float(PX[k_a]) * 100.0
print('| leg | open | exit | side | realised |'); print('|---|---|---|---|---|')
print('| 1 | 04:35:30 | 04:41:00 | LONG (+dr) | %+.4f |' % t1)
print('| 2 | %s | %s | SHORT (-dr) | %+.4f |' % (OPEN_TS, SC.U(exit_k), real))
print('| **chain** | 04:35:30 | %s | | **%+.4f** |' % (SC.U(exit_k), t1 + real))
