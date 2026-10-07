"""ws2Mage crossing UNDER 15 after 04:41 — the -dr trigger, and the walk from it.

JOE 1007: *"because the 04:41 trade is +dr, the target becomes -dr. -dr for ws2Mage is crossing
under 15"*. His TV read was ~05:06; the +dr crossing the code found was 04:34:45/04:35:30, so the
~05:06 he saw is this one, not that one.
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
FROM = '04:41:00'
DRS = -1                                   # the target is -dr, Joe 1007
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_LO = float(SC.LG['momo_fence_r'])      # 17.0
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
_P('producers ready, -dr side')

a = SC.K('%s %s' % (D, FROM)); b = SC.K('%s 06:00:00' % D)
print('\n# EVERY ws2Mage CROSSING DOWN THROUGH %.0f, after %s' % (LO, FROM))
print('| ts | ws2Mage prev | ws2Mage | bars held below | seconds held | rises back at |')
print('|---|---|---|---|---|---|')
first = None
for k in range(a, b + 1):
    if float(M2[k]) <= LO and float(M2[k - 1]) > LO:
        j = k
        while j <= SC.TAPE_LAST and float(M2[j]) <= LO: j += 1
        if first is None: first = k
        print('| **%s** | %.2f | %.2f | %d | %d | %s |'
              % (SC.U(k), float(M2[k - 1]), float(M2[k]), j - k, (j - k) * 5,
                 SC.U(j) if j <= SC.TAPE_LAST else '—'))
if first is None:
    print('| — | | | | | no crossing to 06:00 |'); raise SystemExit

print('\n# THE FIRST CROSSING THAT HOLDS FOR N CONSECUTIVE BARS')
print('| wob (bars) | wob (seconds) | first confirmed bar |'); print('|---|---|---|')
for wob in (1, 2, 3, 6, 12, 24, 60):
    f = None; run = 0
    for k in range(a, SC.TAPE_LAST + 1):
        if float(M2[k]) <= LO:
            run += 1
            if run >= wob: f = k; break
        else: run = 0
    print('| %d | %d | %s |' % (wob, wob * 5, SC.U(f) if f else '—'))

band = lambda t, k: ('O' if float(R[t][k]) <= LO else ('x' if float(R[t][k]) <= EXF_LO else '.'))
oobf = lambda t, k: float(R[t][k]) <= LO
def xcond(h, k):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    return (xv > float(R[t1][k]) and xv > float(R[t2][k])
            and band(t1, k) == '.' and band(t2, k) == '.')

trig = first
p0 = float(PX[trig])
print('\n# THE r LADDER AT THE TRIGGER %s  (-dr side)' % SC.U(trig))
print('| TF | r | band |'); print('|---|---|---|')
for t in LIN_TF:
    print('| ws%d | %.2f | %s |' % (t, float(R[t][trig]), band(t, trig)))

ev = [(trig, 'TRIGGER — ws2Mage crosses under %.0f — lineage walk starts (SHORT)' % LO, p0)]
holder = None; qual = False; exit_k = None; why = None
for k in range(trig, SC.TAPE_LAST + 1):
    if holder is None:
        c = [t for t in LIN_TF if oobf(t, k)]
        if c:
            holder = max(c); qual = True
            ev.append((k, 'holder ws%d — r %.2f oob' % (holder, float(R[holder][k])), float(PX[k])))
        continue
    cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oobf(t, k)]
    if cand:
        holder = max(cand); qual = True
        ev.append((k, 'baton -> ws%d oob (r %.2f)' % (holder, float(R[holder][k])), float(PX[k])))
        continue
    if qual and xcond(holder, k):
        t1, t2 = holder + 1, holder + 2
        ev.append((k, 'EXIT x-cross — ws%dx %.2f over ws%dr %.2f / ws%dr %.2f'
                   % (holder, float(X[holder][k]), t1, float(R[t1][k]), t2, float(R[t2][k])), float(PX[k])))
        exit_k, why = k, 'x-cross'; break
    if ST[holder][k]:
        ev.append((k, 'EXIT final stalled — holder ws%d (r %.2f %s)'
                   % (holder, float(R[holder][k]), band(holder, k)), float(PX[k])))
        exit_k, why = k, 'final stalled'; break
if exit_k is not None:
    seg = PX[trig:exit_k + 1]; idx = np.arange(trig, exit_k + 1)
    ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
    jf, jm = int(seg.argmin()), int(seg.argmax())
    ev.append((int(idx[jf]), 'MFE %+.4f' % ((p0 - float(seg[jf])) / p0 * 100.0), float(seg[jf])))
    ev.append((int(idx[jm]), 'MAE %+.4f' % ((p0 - float(seg[jm])) / p0 * 100.0), float(seg[jm])))
ev.sort(key=lambda x: x[0])
print('\n# THE WALK — SHORT, momentum on dr %+d' % DRS)
print('| ts | +min | event | pxs | pct SHORT |'); print('|---|---|---|---|---|')
for k, lbl, px in ev:
    print('| %s | %+.1f | %s | %.6f | %+.4f |'
          % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[trig])) / 60000.0, lbl, px, (p0 - px) / p0 * 100.0))
if exit_k is not None:
    print('\n- exit: **%s**   realised **%+.4f**' % (why, (p0 - float(PX[exit_k])) / p0 * 100.0))
