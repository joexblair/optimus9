"""TRADE 1 OF 08-22 AS AN A/B PAIR, AND THE TWO CANDIDATE EXIT BARS FOR A. 1009.

Joe 1009: *"squashed x-cross at 00:16 is the end of A-trade"* and *"we'll also need the `close of
the B-trade` event - that's important data for the sweep to measure"*.

A closes on the squashed walk x-cross. B opens there on the flipped side and closes on the chain's
OWN exits - B is a leg, so `run_leg` already owns its close and no new mech is needed.

THE CAUSALITY SPLIT, measured both ways because it is not mine to settle:
  at the CROSS BAR    00:16:00. Joe's words. But "the oob run ended short of the dwell" is not
                      knowable there - the run ends 3 bars later - so A's close cannot depend on
                      it. It is causal ONLY if the squashed x-cross alone closes A whenever it
                      fires inside a ws12r oob run.
  at the RUN-END BAR  00:16:15. The first bar where "the run ended short" is knowable. Causal
                      under Joe's rule exactly as worded, 15 s later than his stamp.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

assert C.NOX and C.TRACE_NOX, 'run with W_NOX=1 W_TRACE_NOX=1'
SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
A_OPEN = SC.K('2026-08-22 23:23:45') if False else SC.K('2026-08-21 23:23:45')
AD = -1          # A is SHORT
XB = SC.K('2026-08-22 00:16:00')     # the squashed x-cross
RB = SC.K('2026-08-22 00:16:15')     # the bar the oob run returned in-bounds

def score(k, xk, d):
    p0 = float(PX[k]); sg = 1 if d > 0 else -1
    seg = PX[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sg, 0.0)
    return (float(PX[xk]) - p0) / p0 * 100.0 * sg, -float(rel.min()), float(rel.max())

print('# A-TRADE — opens %s SHORT, the ws12r oob event is 00:12:00' % U(A_OPEN))
rows = []
for lbl, b in (('A closes at the SQUASHED x-CROSS', XB), ('A closes at the RUN-END bar', RB)):
    r, mae, mfe = score(A_OPEN, b, AD)
    rows.append((lbl, U(b), '%.6f' % float(PX[b]), '%+.4f' % r, '%.4f' % mae, '%.4f' % mfe,
                 '%.4f' % (mfe / mae) if mae else '-'))
box(('the candidate exit', 'ts', 'pxs', 'A realised', 'A MAE', 'A MFE', 'MFE over MAE'), rows)

print('\n# B-TRADE — opens on the flipped side (LONG) and closes on the chain\'s own exits')
rows = []
for lbl, b in (('B opens at the SQUASHED x-CROSS', XB), ('B opens at the RUN-END bar', RB)):
    xk, why, mae_leg, cb, hand, tr = C.run_leg(b, -AD)
    if xk is None:
        rows.append((lbl, U(b), 'tape end', '-', '-', '-', '-', '-')); continue
    r, mae, mfe = score(b, xk, -AD)
    rows.append((lbl, U(b), U(xk), '%.1f' % ((xk - b) * 5 / 60.0), why,
                 '%+.4f' % r, '%.4f' % mae, '%.4f' % mfe))
box(('the candidate open', 'B opens', 'B closes', 'B held min', 'B closes on', 'B realised',
     'B MAE', 'B MFE'), rows)

print('\n# THE PAIR — what the sweep scores. fee 0.11%% per leg boundary, its own column')
rows = []
for lbl, b in (('A at the cross, B from the cross', XB), ('A at the run-end, B from the run-end', RB)):
    ar, amae, amfe = score(A_OPEN, b, AD)
    xk, why, _, _, _, _ = C.run_leg(b, -AD)
    br, bmae, bmfe = score(b, xk, -AD) if xk is not None else (0.0, 0.0, 0.0)
    rows.append((lbl, '%+.4f' % ar, '%+.4f' % br, '%+.4f' % (ar + br), '0.2200',
                 '%+.4f' % (ar + br - 0.22), '%.4f' % amae, '%.4f' % bmae))
box(('the reading', 'A realised', 'B realised', 'gross A+B', 'drag 2 legs', 'NET AFTER DRAG',
     'A MAE', 'B MAE'), rows)
