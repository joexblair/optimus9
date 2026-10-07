"""Walk the lineage from 19:46 on 09-25 and test Joe's x-cross condition at EVERY tag holder.

JOE 1007: *"before we run the AB, walk the lineage from 19:46 and confirm that the mech doesn't fire
before ws11"*.

THE CONDITION, literal: ws{holder}x crosses UNDER ws{holder+1}r AND ws{holder+2}r (dr +1), while
BOTH of those are in-fence. `oob` means the TAG HOLDER, which need not still be oob.

The walk itself is unchanged: start at ws1 momentum, baton passes to a candidate in holder+1 ..
holder+LIN_HOP whose r is oob, upward only, higher wins a same-bar tie.
"""
import io, contextlib, sys
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

D, DR = '2026-09-25', +1
START, END = '19:46:00', '21:10:00'
LIN_TF = SC.TF                               # ws1 .. ws12
LIN_HOP = int(SC.LG['lin_hop'])
EXF = 100.0 - float(SC.LG['momo_fence_r'])
NEED = sorted(set(LIN_TF) | {13, 14})        # holder+2 reaches ws14 from a ws12 holder
R = {t: SC.LD(t * 60, 'r') for t in NEED}
X = {t: SC.LD(t * 60, 'x') for t in LIN_TF}
_P('r for ws1..ws%d, x for ws1..ws%d' % (NEED[-1], LIN_TF[-1]))

db = DatabaseManager(**get_db_config()); db.connect()
BK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BK[t]):
        with momo_window(int(BK[t]['k_window']) * t):
            step, samples = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    ST[t] = stall_mask(SC.Rl[t], DR, int(SC.LG['stall_n']), step, samples)
_P('stall masks built')

def mt1(k):
    with momo_config(BK[1]):
        with momo_window(int(BK[1]['k_window']) * 1):
            return momo_g_why(SC.Rl[1], DR, int(k))[0] in ('momo', 'curl')

band = lambda t, k: ('O' if float(R[t][k]) >= SC.HI else
                     ('x' if float(R[t][k]) >= EXF else '.'))
oob = lambda t, k: float(R[t][k]) >= SC.HI
def cond(h, k):
    """Joe's x-cross condition for tag holder h at bar k. -> (fires, detail)"""
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return None, 'targets outside the loaded band'
    xv = float(X[h][k])
    u1, u2 = xv < float(R[t1][k]), xv < float(R[t2][k])
    f1, f2 = band(t1, k) == '.', band(t2, k) == '.'
    return (u1 and u2 and f1 and f2,
            'ws%dx %.2f | ws%dr %.2f %s x<r %s | ws%dr %.2f %s x<r %s'
            % (h, xv, t1, float(R[t1][k]), band(t1, k), 'Y' if u1 else '-',
               t2, float(R[t2][k]), band(t2, k), 'Y' if u2 else '-'))

a, b = SC.K('%s %s' % (D, START)), SC.K('%s %s' % (D, END))
print('\n# THE LINEAGE WALK FROM %s, with the x-cross condition at EVERY holder' % START)
print('| ts | +min | event | detail |'); print('|---|---|---|---|')
holder = None; hold_from = None; fired = []
rows = []
for k in range(a, b + 1):
    if holder is None:
        if mt1(k):
            holder, hold_from = LIN_TF[0], k
            rows.append((k, 'ws1 momentum - lineage starts, holder ws1', ''))
        continue
    cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oob(t, k)]
    if cand:
        nh = max(cand)
        rows.append((k, 'baton -> ws%d oob  (held ws%d for %.1f min)'
                     % (nh, holder, (int(SC.ts[k]) - int(SC.ts[hold_from])) / 60000.0), ''))
        holder, hold_from = nh, k
        continue
    ok, det = cond(holder, k)
    if ok:
        rows.append((k, '**X-CROSS FIRES on holder ws%d**' % holder, det))
        fired.append((k, holder))
        break
    if ST[holder][k]:
        rows.append((k, 'final stalled on holder ws%d' % holder, det or ''))
        break
for k, lbl, det in rows:
    print('| %s | %+.1f | %s | %s |' % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[a])) / 60000.0, lbl, det))

print('\n# PER HOLDER: did the condition EVER hold while that TF held the tag?')
print('| holder | held from | held to | bars | condition held at any bar? | first bar it held |')
print('|---|---|---|---|---|---|')
hs = [(r[0], r[1]) for r in rows]
seg = []
h = None; f = None
for k in range(a, b + 1):
    pass
# rebuild the holder timeline cleanly
holder = None; hold_from = None; tl = []
for k in range(a, b + 1):
    if holder is None:
        if mt1(k): holder, hold_from = LIN_TF[0], k
        continue
    cand = [t for t in range(holder + 1, min(holder + LIN_HOP, LIN_TF[-1]) + 1) if oob(t, k)]
    if cand:
        tl.append((holder, hold_from, k)); holder, hold_from = max(cand), k
    if fired and k >= fired[0][0]: break
if holder is not None:
    tl.append((holder, hold_from, fired[0][0] if fired else b))
for h, s, e in tl:
    first = None
    for k in range(s, e + 1):
        ok, _ = cond(h, k)
        if ok: first = k; break
    print('| ws%d | %s | %s | %d | %s | %s |'
          % (h, SC.U(s), SC.U(e), e - s + 1,
             '**YES**' if first is not None else 'no',
             SC.U(first) if first is not None else '—'))
