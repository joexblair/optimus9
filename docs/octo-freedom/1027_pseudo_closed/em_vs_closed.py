"""EMERGING vs CLOSED REVERSALS on the dtf lines. Joe 1027.

    "this is emerging lines making a mess with its granular data again ... the strategy is built on
     the premise of the lines behaving in the manner that I see on the TV chart"

This measures the gap he is describing: for ws13..ws16, every CLOSED reversal (what he reads off
the chart) matched against the nearest EMERGING reversal (what the mech acts on), same side.

NO METHOD IS PROPOSED HERE. It is the baseline any replacement has to beat.

CLOSED is v4_closed_prev - the EMERGING value at the last 5 s bar of the most recently COMPLETED
bucket, held forward, midnight-anchored. That is the series whose reversals land where TV's closed
bars land. EMERGING is the raw 5 s series the mech reads today. Both at LIFT_WOB.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_fast as F, v4_closed_prev as CP
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
E = RS.load((RS.K0, RS.R0, RS.S0))
TFS = [13, 14, 15, 16]
print('# EMERGING vs CLOSED REVERSALS, %s .. %s' % (ln.U(A), ln.U(B)))
print('# CLOSED = v4_closed_prev, the series whose reversals land where TV\'s closed bars land.')
print('# EMERGING = the 5 s series the mech reads today. Both at LIFT_WOB %d.' % K.LIFT_WOB)
print('# a CLOSED reversal is MATCHED if an emerging reversal on the same side lands within the')
print('#   tolerance column; the lag is emerging bar minus closed bar, in minutes.')
print('')
print('| the line | side | closed reversals | emerging reversals | emerging per closed |'
      ' matched within 1 TF | median lag min | the TF width min |')
print('|---|---|---|---|---|---|---|---|')
for t in TFS:
    em = np.asarray(E[t], float)
    cl = CP.series(em, t * 60)
    for sd in (-1, +1):
        rc = [int(b) for b in F.revs(cl, t, sd) if A <= b <= B]
        re_ = [int(b) for b in F.revs(em, t, sd) if A <= b <= B]
        if not rc:
            print('| ws%dr | %s | 0 | %d | - | - | - | %d |'
                  % (t, 'LOW' if sd < 0 else 'HIGH', len(re_), t)); continue
        w = t * 60 // 5
        lags, hit = [], 0
        for b in rc:
            near = [x for x in re_ if abs(x - b) <= w]
            if near:
                hit += 1
                lags.append(min(near, key=lambda z: abs(z - b)) - b)
        lags_m = sorted((x * 5 / 60.0) for x in lags)
        print('| ws%dr | %s | %d | %d | %.1f | %d of %d | %s | %d |'
              % (t, 'LOW' if sd < 0 else 'HIGH', len(rc), len(re_), len(re_) / len(rc),
                 hit, len(rc),
                 ('%+.1f' % lags_m[len(lags_m) // 2]) if lags_m else '-', t))
