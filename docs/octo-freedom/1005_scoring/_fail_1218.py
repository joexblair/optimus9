"""09-26 12:18:00 — the worst `no r block` loss on 09-25/09-26, as a timestamped event walk.

realised -1.7188 under the stall exit. MFE over the holding window was +0.0687 at +1.6 min.
"""
import os, io, contextlib, re, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
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

D, SIG = '2026-09-26', '12:18:00'
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF = 100.0 - float(SC.LG['momo_fence_r'])
NEED = sorted(set(LIN_TF) | {13, 14})
R = {t: SC.LD(t * 60, 'r') for t in NEED}
X = {t: SC.LD(t * 60, 'x') for t in LIN_TF}
PX = SC.PX
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    ST[t] = stall_mask(SC.Rl[t], +1, int(SC.LG['stall_n']), s_, n_)
def mt1(k):
    with momo_config(BANK[1]):
        with momo_window(int(BANK[1]['k_window']) * 1):
            return momo_g_why(SC.Rl[1], +1, int(k))[0] in ('momo', 'curl')
_P('producers ready')

k_sig = SC.K('%s %s' % (D, SIG))
r = SC.classify(k_sig, SIG)
ex = int(r['m']['ex']); kw = int(r['kw'])
open_k = max(k_sig, kw, ex)
dr = int(SC.DRv[k_sig]); side = 'LONG' if dr > 0 else 'SHORT'
p0 = float(PX[open_k])
band = lambda t, k: ('O' if float(R[t][k]) >= SC.HI else
                     ('x' if float(R[t][k]) >= EXF else '.'))

print('\n## 09-26 %s   dr %+d   side %s   grade %s   route %s'
      % (SIG, dr, side, (r.get('D') or {}).get('why'), r['m'].get('route')))
print('\n# THE r LADDER AT THE g5extrema %s  (where branch D read)' % SC.U(ex))
print('| TF | r | band |'); print('|---|---|---|')
for t in LIN_TF:
    print('| ws%d | %.2f | %s |' % (t, float(R[t][ex]), band(t, ex)))

# the walk
arm_k = SC.K('%s 13:18:00' % D)
ev = [(ex, 'g5extrema — branch D reads here, ladder all in-fence', float(PX[ex])),
      (open_k, 'OPEN %s' % side, p0)]
holder = None; qual = False
xfire = None
for k in range(arm_k, SC.TAPE_LAST + 1):
    if holder is None:
        if mt1(k):
            holder = LIN_TF[0]; ev.append((k, 'ws1 momentum — lineage starts, holder ws1  (r %.2f %s)'
                                           % (float(R[1][k]), band(1, k)), float(PX[k])))
        continue
    cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1)
            if float(R[t][k]) >= SC.HI]
    if cand:
        holder = max(cand); qual = True
        ev.append((k, 'baton -> ws%d oob  (r %.2f)' % (holder, float(R[holder][k])), float(PX[k])))
        continue
    if qual and xfire is None:
        t1, t2 = holder + 1, holder + 2
        if t1 in R and t2 in R:
            xv = float(X[holder][k])
            if xv < float(R[t1][k]) and xv < float(R[t2][k]) and band(t1, k) == '.' and band(t2, k) == '.':
                xfire = k
                ev.append((k, 'x-cross condition holds on ws%d  (ws%dx %.2f < ws%dr %.2f, ws%dr %.2f)'
                           % (holder, holder, xv, t1, float(R[t1][k]), t2, float(R[t2][k])), float(PX[k])))
    if ST[holder][k]:
        ev.append((k, 'EXIT final stalled — holder ws%d  (r %.2f %s)'
                   % (holder, float(R[holder][k]), band(holder, k)), float(PX[k])))
        exit_k = k; break
ev.append((arm_k, 'exit-armed (octo-sig 13:18:00, allows SHORT only)', float(PX[arm_k])))
# MFE over the holding window
seg = PX[open_k:exit_k + 1]; idx = np.arange(open_k, exit_k + 1)
ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
j = int(seg.argmax()) if side == 'LONG' else int(seg.argmin())
ev.append((int(idx[j]), 'MFE %+.4f' % ((float(seg[j]) - p0) / p0 * 100.0 * (1 if side == 'LONG' else -1)),
           float(seg[j])))
jm = int(seg.argmin()) if side == 'LONG' else int(seg.argmax())
ev.append((int(idx[jm]), 'MAE %+.4f' % ((float(seg[jm]) - p0) / p0 * 100.0 * (1 if side == 'LONG' else -1)),
           float(seg[jm])))
ev.sort(key=lambda x: x[0])
print('\n# THE WALK, timestamped')
print('| ts | +min | event | pxs | pct from open |'); print('|---|---|---|---|---|')
for k, lbl, px in ev:
    print('| %s | %+.1f | %s | %.6f | %+.4f |'
          % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[open_k])) / 60000.0, lbl, px,
             (px - p0) / p0 * 100.0 * (1 if side == 'LONG' else -1)))
print('\n- realised open to close: **%+.4f**'
      % ((float(PX[exit_k]) - p0) / p0 * 100.0 * (1 if side == 'LONG' else -1)))
