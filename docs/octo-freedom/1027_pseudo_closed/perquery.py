"""THE PER-QUERY ERROR AT CADENCE SAMPLING. Joe 1027:

    "we're going to be testing and making decisions only at cadence intervals - if we need to
     lookback, we're going to be looking back in TF seam widths. would that hide the 7x?"

THE QUESTION ASKED AT EVERY CADENCE BAR is a STATE, not a count:
    "has ws{T}r reversed on side S within the last N TF seam widths?"
so several flickers inside one window collapse into a single yes. The count stops mattering; what
is left is whether the ANSWER agrees with the chart.

    AGREE         emerging and closed give the same yes/no at that cadence bar
    FALSE YES     emerging says reversed, closed says not - the kill signal the chart denies
    FALSE NO      emerging says not, closed says reversed - a walk kept alive that should have ended

THE CADENCE BARS ARE THE REAL ONES - t1 and t2 out of v4_l2_cadence, on the closed cws set, over
2026-08-30..09-06, both target sides. Not a synthetic every-N-bars sample, because the question is
about HIS cadences.

TWO WOB ARMS on the emerging read: LIFT_WOB 8 as banked, and 32 - the value the wob curve put at
2.9x flicker with coverage held. No knob is moved; both are passed explicitly.

THE LOOKBACKS ARE 1, 2 AND 3 TF SEAM WIDTHS - his own unit. Nothing else is truncated.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_cadence as CAD
from optimus9.analysis.jig import lift_off
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = CP.arm_lines(E)
TFS = [13, 14, 15, 16]
WOBS = [int(K.LIFT_WOB), 32]
SEAMS = [1, 2, 3]

#   HIS CADENCE BARS: t1 and t2, both target sides, over the window
CAD_BARS = sorted({int(b) for sd in (-1, +1)
                   for b, _ty, _w in (CAD.t1(CL, sd, A, B) + CAD.t2(CL, sd, A, B))})
print('# THE PER-QUERY ERROR AT HIS CADENCE BARS, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the query is a STATE: "has ws{T}r reversed on side S within N TF seam widths?"')
print('# the cadence bars are the real t1 and t2 from v4_l2_cadence, both sides: %d of them.'
      % len(CAD_BARS))
print('# the reference is the CLOSED read at LIFT_WOB %d - the chart\'s answer.' % K.LIFT_WOB)
print('# RULED_OK %s' % K.RULED_OK)
print('')
print('| the line | side | seams | wob | queries | agree %% | FALSE YES %% | FALSE NO %% |'
      ' emerging says yes %% | closed says yes %% |')
print('|---|---|---|---|---|---|---|---|---|---|')
CB = np.asarray(CAD_BARS, np.int64)
for t in TFS:
    em = np.asarray(E[t], float)
    cl = CP.series(em, t * 60)
    T = t * 60 // 5
    for sd in (-1, +1):
        rc = np.asarray(sorted(int(b) for b in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(t),
                                                        K.LIFT_TOL, int(K.LIFT_WOB))), np.int64)
        for w in WOBS:
            raw = lift_off(em, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, int(w))
            st = np.asarray(sorted(int(b) + int(w) - 1 for b in raw), np.int64)
            for ns in SEAMS:
                win = T * ns
                ey = np.array([bool(len(st[(st >= c - win) & (st <= c)])) for c in CB])
                cy = np.array([bool(len(rc[(rc >= c - win) & (rc <= c)])) for c in CB])
                n = len(CB)
                fy = int((ey & ~cy).sum()); fn = int((~ey & cy).sum())
                print('| ws%dr | %s | %d | %d | %d | %.1f%% | %.1f%% | %.1f%% | %.1f%% | %.1f%% |'
                      % (t, 'LOW' if sd < 0 else 'HIGH', ns, w, n,
                         100.0 * (ey == cy).mean(), 100.0 * fy / n, 100.0 * fn / n,
                         100.0 * ey.mean(), 100.0 * cy.mean()))
