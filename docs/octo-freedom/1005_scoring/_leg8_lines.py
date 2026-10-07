"""MEASUREMENT B — what was available on every bar of leg 8 between the pivot and the ws23 x-cross.

JOE 1007: *"at 10:25, we've overshot the pivot at 09:32 and lost ~0.9 profit - that's what set me on
this quest"* / *"my time is developing the >ws12 process"*.

LEG 8: LONG, open 09-25 08:10:00 at pxs 0.183763, rider ws23 from 09:35:00, x-cross exit 10:25:00.

WHAT IS PRINTED, nothing tested and nothing proposed:
  ws23r / ws23m / ws23Mage / ws23x   the rider's own four lines
  ws24r / ws25r                      the x-cross's two targets
  stalled                            stall_mask(ws23r, +1, stall_n) - the mech's own stall producer
  x < 24r / x < 25r                  the two halves of the x-cross condition, separately
  pivot                              swing_detect find_pivots at the BANKED 1.25 pct. A BACKTEST
                                     RULER, Joe 1006 - it cannot sit inside a causal mech.

SAMPLING: one row per minute, plus EVERY bar that is a pivot, a stall onset, or a fence crossing of
ws23r / ws24r / ws25r against oob 85 or the ex-fence 83. Joe's own unit for this kind of look, 0925:
*"show me per minute samples of ws11r after 20:36"*.
"""
import io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.compute.swing_detect import find_pivots
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

D, OPEN_TS, A_TS, B_TS, RIDER, DD = '2026-09-25', '08:10:00', '09:30:00', '10:26:00', 23, +1
SWING = float(SC.LG['swing'])
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
LN = {}
for role in ('r', 'm', 'Mage', 'x'):
    for t in (RIDER, RIDER + 1, RIDER + 2):
        try:
            LN[(t, role)] = SC.LD(t * 60, role)[:N]
        except Exception as e:
            LN[(t, role)] = None
PX = SC.PX[:N]
RL = SC.LD(RIDER * 60, 'r')
db = DatabaseManager(**get_db_config()); db.connect()
BK = momo_bank(db, RIDER); db.disconnect()
with momo_config(BK):
    with momo_window(int(BK['k_window']) * RIDER):
        s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
STL = stall_mask(RL, DD, int(SC.LG['stall_n']), s_, n_)
PIV = {p: kk for p, kk in find_pivots(PX, SWING)}
EXF_HI = 100.0 - float(SC.LG['momo_fence_r'])

k0, a, b = K(OPEN_TS), K(A_TS), K(B_TS)
p0 = float(PX[k0])
V = lambda t, role, j: (float(LN[(t, role)][j]) if LN[(t, role)] is not None else float('nan'))
fmt = lambda v: ('—' if not np.isfinite(v) else '%.2f' % v)
bandf = lambda v: ('O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')) if np.isfinite(v) else '—'

def is_event(j):
    if j in PIV: return True
    if STL[j] and not STL[j - 1]: return True
    for t in (RIDER, RIDER + 1, RIDER + 2):
        v, w = V(t, 'r', j), V(t, 'r', j - 1)
        if not (np.isfinite(v) and np.isfinite(w)): continue
        for f in (SC.HI, EXF_HI):
            if (v >= f) != (w >= f): return True
    xv, xw = V(RIDER, 'x', j), V(RIDER, 'x', j - 1)
    for t in (RIDER + 1, RIDER + 2):
        tv, tw = V(t, 'r', j), V(t, 'r', j - 1)
        if np.isfinite(xv) and np.isfinite(xw) and np.isfinite(tv) and np.isfinite(tw):
            if (xv < tv) != (xw < tw): return True
    return False

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    L = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))

print('# LEG 8 — swing %.2f pivots inside the leg (open %s, exit 10:25:00)' % (SWING, OPEN_TS))
pv = [(SC.U(p), PIV[p], '%.6f' % float(PX[p]),
       '%+.4f' % ((float(PX[p]) - p0) / p0 * 100.0),
       '%+.1f' % ((int(SC.ts[p]) - int(SC.ts[k0])) / 60000.0))
      for p in sorted(PIV) if k0 <= p <= K('10:25:00')]
box(('ts', 'kind', 'pxs', 'pct LONG', '+min from open'), pv or [('—', '—', '—', '—', '—')])

rows = []
for j in range(a, b + 1):
    if (int(SC.ts[j]) % 60000 != 0) and not is_event(j): continue
    xv = V(RIDER, 'x', j); r24, r25 = V(RIDER + 1, 'r', j), V(RIDER + 2, 'r', j)
    tags = []
    if j in PIV: tags.append('PIVOT %s' % PIV[j])
    if STL[j] and not STL[j - 1]: tags.append('stall onset')
    rows.append((SC.U(j), '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k0])) / 60000.0),
                 '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0),
                 fmt(V(RIDER, 'r', j)), bandf(V(RIDER, 'r', j)),
                 fmt(V(RIDER, 'm', j)), fmt(V(RIDER, 'Mage', j)), fmt(xv),
                 fmt(r24), bandf(r24), fmt(r25), bandf(r25),
                 'Y' if STL[j] else '-',
                 'Y' if (np.isfinite(xv) and np.isfinite(r24) and xv < r24) else '-',
                 'Y' if (np.isfinite(xv) and np.isfinite(r25) and xv < r25) else '-',
                 ', '.join(tags) or ''))
print('\n# EVERY MINUTE FROM %s TO %s, PLUS EVERY PIVOT, STALL ONSET AND FENCE CROSSING' % (A_TS, B_TS))
box(('ts', '+min', 'pct', 'ws23r', 'band', 'ws23m', 'ws23Mage', 'ws23x', 'ws24r', 'band',
     'ws25r', 'band', 'ws23 stalled', 'x<24r', 'x<25r', 'event'), rows)
print('\n- leg 8 open %s pxs %.6f; rider ws%d from 09:35:00; x-cross exit 10:25:00'
      % (OPEN_TS, p0, RIDER))
print('- oob %.0f, ex-fence %.0f, stall_n %s, stall step %d bars / %d samples'
      % (SC.HI, EXF_HI, SC.LG['stall_n'], s_, n_))
print('- rows printed %d of %d bars in the window' % (len(rows), b - a + 1))
