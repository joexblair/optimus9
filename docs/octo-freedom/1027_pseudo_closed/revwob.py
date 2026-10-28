"""THE REVERSAL WOB, PRICED AGAINST THE CHART. Joe 1027:

    "the 7x reversal flicker is exactly the thing to optimise: we won't make it to ex-fence and the
     ensuing lift-off if a reversal drops us before we get there"

A reversal is what ENDS a lineage2 walk, so an emerging reversal with no counterpart on the closed
chart kills a walk that should have continued. This prices the wob: what it buys in unconfirmed
reversals and what it costs in lead time and coverage.

PER LINE, PER SIDE, PER WOB:
    detected      emerging reversals, stamped at raw + wob - 1 (the bar they are actionable on)
    coverage      how many CLOSED reversals have an emerging one inside the one TF before them
    unconfirmed   emerging reversals with NO closed reversal inside the one TF after - the kill
                  signal the chart never agreed with
    median lead   how far ahead of the closed reversal the emerging one is stamped, in minutes

THE WOB GRID IS TF-ANCHORED, not chosen: 1, 2, 4, the two banked values 8 (LIFT_WOB) and 12
(LIN2_REV_WOB), then T/8, T/4, T/2 and T, where T is the TF width in 5 s bars. A wob longer than
one TF holds a state longer than the bar that produced it, so T is the natural end of the domain.

THE MATCHING WINDOW IS ONE TF WIDTH - the lag the closed read carries by construction. Nothing
else is truncated.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
from optimus9.analysis.jig import lift_off
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
E = RS.load((RS.K0, RS.R0, RS.S0))
TFS = [13, 14, 15, 16]
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')

print('# THE REVERSAL WOB, PRICED AGAINST THE CLOSED CHART, %s .. %s' % (ln.U(A), ln.U(B)))
print('# a reversal ENDS a lineage2 walk, so an unconfirmed one kills a walk that should continue.')
print('# detected reversals are stamped at raw + wob - 1, the bar they become actionable on.')
print('# the reference is the CLOSED read at LIFT_WOB %d - where TV\'s closed bars put the turn.'
      % K.LIFT_WOB)
print('# the wob grid is TF-anchored: 1, 2, 4, 8 (LIFT_WOB), 12 (LIN2_REV_WOB), T/8, T/4, T/2, T.')
print('# RULED_OK %s' % K.RULED_OK)
print('')
for t in TFS:
    em = np.asarray(E[t], float)
    cl = CP.series(em, t * 60)
    T = t * 60 // 5
    wobs = sorted({1, 2, 4, 8, 12, max(1, T // 8), max(1, T // 4), max(1, T // 2), T})
    print('## ws%dr - the TF is %d min = %d bars of 5 s' % (t, t, T))
    print('')
    print('| side | wob bars | wob s | detected | coverage | unconfirmed | unconfirmed % |'
          ' median lead min |')
    print('|---|---|---|---|---|---|---|---|')
    for sd in (-1, +1):
        rc = [int(b) for b in lift_off(cl, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                                       int(K.LIFT_WOB)) if A <= b <= B]
        rc = sorted(rc)
        for w in wobs:
            raw = [int(b) for b in lift_off(em, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, int(w))]
            st = sorted(b + w - 1 for b in raw if A <= (b + w - 1) <= B)
            if not rc or not st:
                print('| %s | %d | %d | %d | - | - | - | - |'
                      % ('LOW' if sd < 0 else 'HIGH', w, w * 5, len(st)))
                continue
            sa = np.asarray(st); ca = np.asarray(rc)
            hit, leads = 0, []
            for c in rc:
                near = sa[(sa >= c - T) & (sa <= c)]
                if len(near):
                    hit += 1
                    leads.append((c - near[-1]) * 5 / 60.0)
            unconf = sum(1 for x in st if not len(ca[(ca >= x) & (ca <= x + T)]))
            print('| %s | %d | %d | %d | %d of %d | %d | %.1f%% | %s |'
                  % ('LOW' if sd < 0 else 'HIGH', w, w * 5, len(st), hit, len(rc), unconf,
                     100.0 * unconf / len(st), '%.1f' % _med(leads) if leads else '-'))
    print('')
