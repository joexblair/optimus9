"""Walk one `no r block` trade as a timestamped event list. LG_DAY / LG_SIG select it."""
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
_P = lambda m: print('# [%5.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D = os.environ.get('W_DAY', '2026-09-28')
SIG = os.environ.get('W_SIG', '09:52:00')
ARM = os.environ.get('W_ARM', '12:12:10')
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
NEED = sorted(set(LIN_TF) | {13, 14})
R = {t: SC.LD(t * 60, 'r') for t in NEED}
X = {t: SC.LD(t * 60, 'x') for t in LIN_TF}
MG = SC.Mg
PX = SC.PX
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()

k_sig = SC.K('%s %s' % (D, SIG))
r = SC.classify(k_sig, SIG)
ex = int(r['m']['ex']); kw = int(r['kw'])
open_k = max(k_sig, kw, ex)
dr = int(SC.DRv[k_sig]); side = 'LONG' if dr > 0 else 'SHORT'
p0 = float(PX[open_k])
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    ST[t] = stall_mask(SC.Rl[t], dr, int(SC.LG['stall_n']), s_, n_)
def mt1(k):
    with momo_config(BANK[1]):
        with momo_window(int(BANK[1]['k_window']) * 1):
            return momo_g_why(SC.Rl[1], dr, int(k))[0] in ('momo', 'curl')
_P('producers ready')

band = lambda t, k: (('O' if float(R[t][k]) >= SC.HI else ('x' if float(R[t][k]) >= EXF_HI else '.'))
                     if dr > 0 else
                     ('O' if float(R[t][k]) <= SC.LO else ('x' if float(R[t][k]) <= EXF_LO else '.')))
oobf = lambda t, k: (float(R[t][k]) >= SC.HI) if dr > 0 else (float(R[t][k]) <= SC.LO)
sgn = 1 if side == 'LONG' else -1

print('\n## %s %s   dr %+d   side %s   grade %s   route %s'
      % (D, SIG, dr, side, (r.get('D') or {}).get('why'), r['m'].get('route')))
print('\n# AT THE g5extrema %s' % SC.U(ex))
print('| TF | r | band | Mage |'); print('|---|---|---|---|')
for t in LIN_TF:
    print('| ws%d | %.2f | %s | %.1f |' % (t, float(R[t][ex]), band(t, ex), float(MG[t][ex])))
print('\n| cascade ws1..ws12 | %s |'
      % ','.join('%.1f' % float(MG[t][ex]) for t in LIN_TF))

arm_k = SC.K('%s %s' % (D, ARM))
ev = [(ex, 'g5extrema — branch D reads here', float(PX[ex])),
      (open_k, 'OPEN %s' % side, p0),
      (arm_k, 'exit-armed', float(PX[arm_k]))]
holder = None; qual = False; exit_k = None
for k in range(arm_k, SC.TAPE_LAST + 1):
    if holder is None:
        if mt1(k):
            holder = LIN_TF[0]
            ev.append((k, 'ws1 momentum — lineage starts, holder ws1 (r %.2f %s)'
                       % (float(R[1][k]), band(1, k)), float(PX[k])))
        continue
    cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, k)]
    if cand:
        holder = max(cand); qual = True
        ev.append((k, 'baton -> ws%d oob (r %.2f)' % (holder, float(R[holder][k])), float(PX[k])))
        continue
    if ST[holder][k]:
        ev.append((k, 'EXIT final stalled — holder ws%d (r %.2f %s)'
                   % (holder, float(R[holder][k]), band(holder, k)), float(PX[k])))
        exit_k = k; break
seg = PX[open_k:exit_k + 1]; idx = np.arange(open_k, exit_k + 1)
ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
jf = int(seg.argmax()) if side == 'LONG' else int(seg.argmin())
jm = int(seg.argmin()) if side == 'LONG' else int(seg.argmax())
ev.append((int(idx[jf]), 'MFE %+.4f' % ((float(seg[jf]) - p0) / p0 * 100.0 * sgn), float(seg[jf])))
ev.append((int(idx[jm]), 'MAE %+.4f' % ((float(seg[jm]) - p0) / p0 * 100.0 * sgn), float(seg[jm])))
ev.sort(key=lambda x: x[0])
print('\n# THE WALK, timestamped')
print('| ts | +min | event | pxs | pct from open |'); print('|---|---|---|---|---|')
for k, lbl, px in ev:
    print('| %s | %+.1f | %s | %.6f | %+.4f |'
          % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[open_k])) / 60000.0, lbl, px,
             (px - p0) / p0 * 100.0 * sgn))
print('\n- realised open to close: **%+.4f**' % ((float(PX[exit_k]) - p0) / p0 * 100.0 * sgn))
print('\n# THE LADDER AT THE EXIT %s' % SC.U(exit_k))
print('| TF | r | band |'); print('|---|---|---|')
for t in LIN_TF:
    print('| ws%d | %.2f | %s |' % (t, float(R[t][exit_k]), band(t, exit_k)))
