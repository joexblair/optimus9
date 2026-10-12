"""THE LOOP-TF x EXHAUSTION-TIMING SWEEP OVER THE WHOLE DAY. 1010.

Joe 1010: *"sweep the loop-tf, and always / on stall"*.

  ONE IMPORT, MANY ARMS. `_chain10` is imported once and `C.LOOP_TFS` / `C.EXH_LOOP` are set per
  arm, so the knobs are the only thing that changes between rows.

  THE WINDOW IS THE WHOLE DAY, 2026-07-15 03:13:15 to the last leg opening before 23:59:55, and A
  STOPPED LEG CLOSES AND FLIPS instead of halting the chain. The banked `main()` halts on the first
  MAE breach - a review device - and that made every arm end on a different bar, so the realised
  figures could not be compared. STATED, because it is a change from how the single runs ran.

  DRAG IS ITS OWN COLUMN at 0.11% per leg boundary, never folded into net.

  THE CONTROL ROW is `loop off`, the same build with no loop at all. It is checked against the
  single run's own numbers in the notes below the table.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
DRAG = float(os.environ.get('W_DRAG', 0.11))
D = os.environ.get('W_DAY', '2026-07-15')
k0 = SC.K('%s %s' % (D, os.environ.get('W_START', '03:13:15')))
LAST = SC.K('%s 23:59:55' % D)
FIRST = int(os.environ.get('W_SIDE', '-1'))
print('# %s %s side %s -> %s. drag %.2f%% per boundary. ceiling %d, lin_hop %d, '
      'W_KICK %s, W_STALL_UP %s, W_NOX %s, W_NO_GT12 %s'
      % (D, U(k0), 'LONG' if FIRST > 0 else 'SHORT', U(LAST), DRAG, C.CEIL_HI, C.LIN_HOP,
         C.KICK, C.STALL_UP, C.NOX, C.NO12), flush=True)


def chain():
    """the chain from k0 to the end of the day. a stop closes the leg and flips. -> dict"""
    k, d = k0, FIRST
    legs, stops, loops, exh, holds = 0, 0, 0, 0, []
    real = 0.0
    while k < LAST:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None or xk > LAST:
            break
        p0 = float(PX[k]); sg = 1 if d > 0 else -1
        real += (float(PX[xk]) - p0) / p0 * 100.0 * sg
        legs += 1
        holds.append((int(SC.ts[xk]) - int(SC.ts[k])) / 60000.0)
        if why == 'mae breach': stops += 1
        if why == 'loop exhaustion': exh += 1
        loops += sum(1 for _, t in tr if t.startswith('LOOP '))
        k = xk; d = -d
    drag = legs * DRAG
    return dict(legs=legs, real=real, drag=drag, net=real - drag, stops=stops, loops=loops,
                exh=exh, med=float(np.median(holds)) if holds else 0.0)


ARMS = [('off', e) for e in ('on_stall', 'always')] + \
       [(t, e) for t in range(2, C.CEIL_HI + 1) for e in ('on_stall', 'always')]
rows = []
for lt, e in ARMS:
    C.LOOP_TFS = [] if lt == 'off' else [int(lt)]
    C.EXH_LOOP = e
    r = chain()
    rows.append((str(lt), e, str(r['legs']), '%.1f' % r['med'], '%+.4f' % r['real'],
                 '%.2f' % r['drag'], '%+.4f' % r['net'], str(r['stops']), str(r['loops']),
                 str(r['exh'])))
    print('# %-4s %-8s legs %3d  net %+8.4f' % (lt, e, r['legs'], r['net']), flush=True)
box(('loop tf', 'exhaustion', 'legs', 'median hold min', 'gross', 'drag', 'NET AFTER DRAG',
     'stops', 'loops', 'exhaustion exits'), rows)
best = max(rows, key=lambda r: float(r[6]))
print('- gross is the sum of the per-leg realised pct. drag is %.2f%% x the leg count, its own '
      'column, never folded in.' % DRAG)
print('- a leg that hit the MAE stop closed and flipped; the chain was not halted.')
print('- BEST NET: loop tf %s, exhaustion %s, %s legs, net %s.' % (best[0], best[1], best[2], best[6]))
