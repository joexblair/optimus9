"""THE NAKED WALK FROM 15:41 — EVERY LANDING BAR AS A LONG ENTRY. 09-25. 1008.

Joe 1008, correcting §14/§14a: *"the purpose of the lineage walk is not to create a SHORT trade and
ride it. it's sole job in this context is to walk naked to a bar that is more optimised for the
LONG trade. ie, we're not flipping short and long"*.

SO THE FRAME IS:
  15:41:00    the bar the chain would have entered LONG on. pxs 0.187001.
  the walk     runs on the dr -1 frame carrying NO POSITION. There is no MAE while it walks.
  the landing  wherever the walk terminates. The LONG is entered THERE.
  the measure  (a) how much better the LONG entry price is, and (b) what the LONG from that bar is
               worth under the unchanged mech - C.run_leg(landing, +1).

EVERY §14/§14a "SHORT realised" FIGURE IS THE ENTRY IMPROVEMENT, NOT A TRADE. A LONG entered
0.5382% lower is 0.5382% better off at every later bar; it is not 0.5382% of realised P&L.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
K = lambda s: SC.K('2026-09-25 %s' % s)
OPEN = K('15:41:00'); P0 = float(PX[OPEN])
MAE_STOP = C.MAE_STOP
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[OPEN])) / 60000.0)

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

LAND = [('15:41:00', 'no walk — enter LONG immediately (the chain as built)'),
        ('15:44:40', 'ws4x crosses ws4r, inside the ws4 rider window'),
        ('15:45:35', 'ws5x crosses ws5r, inside the ws5 rider window'),
        ('15:54:10', 'ws6x crosses ws6r, inside the ws6 rider window'),
        ('15:55:05', "xcond(ws6) — the walk's own exit test, what it takes"),
        ('15:58:20', 'xcond(ws4) and xcond(ws5), both outside their rider windows'),
        ('16:05:00', 'ws6 stall (stall_n 6)')]

print('\n# THE LONG ENTERED AT EACH LANDING BAR — 15:41:00 pxs %.6f is the bar being improved on'
      % P0)
rows = []
for ts, why in LAND:
    j = K(ts)
    pe = float(PX[j])
    imp = (P0 - pe) / P0 * 100.0          # a LOWER entry is a BETTER long. + = better.
    xk, w, mae, cb, hand, tr = C.run_leg(j, +1)
    if xk is None:
        rows.append((ts, mn(j), '%.6f' % pe, '%+.4f' % imp, why,
                     'none to the tape end', '—', '—', '—', '—', '—')); continue
    a_, f_ = (MAE_STOP, 0.0) if w == 'mae breach' else mm(j, xk, +1)
    real = (float(PX[xk]) - pe) / pe * 100.0
    rows.append((ts, mn(j), '%.6f' % pe, '%+.4f' % imp, why,
                 U(xk), '%.1f' % ((int(SC.ts[xk]) - int(SC.ts[j])) / 60000.0), w,
                 '%.4f' % a_, '%.4f' % f_, '%+.4f' % real))
box(('LONG entry bar', '+min from 15:41', 'entry pxs', 'entry better by %',
     'what put the walk there', 'the LONG exits', 'hold min', 'why', 'leg MAE', 'leg MFE',
     'realised'), rows)
print('- "entry better by %%" = (0.187001 - entry pxs) / 0.187001 * 100. A LOWER entry is a better')
print('  LONG. It is an entry improvement, NOT realised P&L.')
print('- leg MAE / MFE / realised are from C.run_leg(entry, +1) - the unchanged mech, LONG only.')
print('- a stopped leg scores MAE %.4f and MFE 0.0000, Joe 1007.' % MAE_STOP)
print('- THERE IS NO MAE WHILE THE WALK WALKS. It carries no position.')
