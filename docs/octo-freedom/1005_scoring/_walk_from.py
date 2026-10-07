"""Walk the lineage from any bar, on either dr side. W_DAY / W_FROM / W_SIDE select it.

JOE 1007: *"04:41 is exactly the pivot. I wonder where the walk will land if you opened a
non-sanctioned trade at 04:41"*. Non-sanctioned = not from an octo-sig; the bar is chosen by hand.

HOLDER AT THE START: the highest line already oob on the read side. If none is oob, the walk waits
for the first one, exactly as it does mid-lineage.
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
FROM = os.environ.get('W_FROM', '04:41:00')
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
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
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(SC.Rl[t], dd, int(SC.LG['stall_n']), s_, n_)
_P('producers ready')
k0 = SC.K('%s %s' % (D, FROM)); p0 = float(PX[k0])

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

print('\n## NON-SANCTIONED OPEN at %s %s   pxs %.6f' % (D, FROM, p0))
print('\n# THE LADDER AT THE OPEN, both sides')
print('| TF | r | +dr band | -dr band |'); print('|---|---|---|---|')
for t in LIN_TF:
    print('| ws%d | %.2f | %s | %s |' % (t, float(R[t][k0]), band(t, k0, +1), band(t, k0, -1)))

for d, side in ((-1, 'SHORT'), (+1, 'LONG')):
    sgn = -1 if d > 0 else 1          # +dr position is LONG, -dr position is SHORT
    sgn = 1 if side == 'LONG' else -1
    ev = [(k0, 'OPEN %s  (momentum read on dr %+d)' % (side, d), p0)]
    holder = None; qual = False; exit_k = None; why = None
    for k in range(k0, SC.TAPE_LAST + 1):
        if holder is None:
            c = [t for t in LIN_TF if oobf(t, k, d)]
            if c:
                holder = max(c); qual = True
                ev.append((k, 'holder ws%d — r %.2f oob' % (holder, float(R[holder][k])), float(PX[k])))
            continue
        cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, k, d)]
        if cand:
            holder = max(cand); qual = True
            ev.append((k, 'baton -> ws%d oob (r %.2f)' % (holder, float(R[holder][k])), float(PX[k])))
            continue
        if qual and xcond(holder, k, d):
            t1, t2 = holder + 1, holder + 2
            ev.append((k, 'EXIT x-cross — ws%dx %.2f vs ws%dr %.2f / ws%dr %.2f'
                       % (holder, float(X[holder][k]), t1, float(R[t1][k]), t2, float(R[t2][k])),
                       float(PX[k])))
            exit_k, why = k, 'x-cross'; break
        if ST[(holder, d)][k]:
            ev.append((k, 'EXIT final stalled — holder ws%d (r %.2f %s)'
                       % (holder, float(R[holder][k]), band(holder, k, d)), float(PX[k])))
            exit_k, why = k, 'final stalled'; break
    if exit_k is not None:
        seg = PX[k0:exit_k + 1]; idx = np.arange(k0, exit_k + 1)
        ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
        jf = int(seg.argmax()) if side == 'LONG' else int(seg.argmin())
        jm = int(seg.argmin()) if side == 'LONG' else int(seg.argmax())
        ev.append((int(idx[jf]), 'MFE %+.4f' % ((float(seg[jf]) - p0) / p0 * 100.0 * sgn), float(seg[jf])))
        ev.append((int(idx[jm]), 'MAE %+.4f' % ((float(seg[jm]) - p0) / p0 * 100.0 * sgn), float(seg[jm])))
    ev.sort(key=lambda x: x[0])
    print('\n# THE WALK — %s, momentum on dr %+d' % (side, d))
    print('| ts | +min | event | pxs | pct %s |' % side); print('|---|---|---|---|---|')
    for k, lbl, px in ev:
        print('| %s | %+.1f | %s | %.6f | %+.4f |'
              % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0, lbl, px,
                 (px - p0) / p0 * 100.0 * sgn))
    if exit_k is not None:
        print('\n- exit: **%s**   realised **%+.4f**'
              % (why, (float(PX[exit_k]) - p0) / p0 * 100.0 * sgn))
    else:
        print('\n- no exit to the end of the tape')
