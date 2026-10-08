"""10:17 AND THE ws1r REVERSAL AT 10:21. 09-25. 1008.

Joe 1008: *"10:17 walked down to the reversl of ws1r at 10:21. at 10:21 it was infence - that's the
end of the walk. can you see why?"*

Leg 9 of arm 5: LONG, the walk starts 10:17:05 on frame -1, and my mech landed it at 10:36:05 on an
entry 0.5702% WORSE. Joe's landing is 10:21.

WHAT IS MEASURED, using the reversal detector already in the codebase - `_mage_rev(R[1], rrev_wob)`
with `rrev_wob` 2, the same one `_chain10` uses for the >ws12 divergence:

  every ws1r reversal in the window, its value, its fence state, and the LONG entry it gives
  the ws1r minimum in the window and the bar it sits on
  the pxs minimum in the window and the bar it sits on
  the bar my mech landed on, for the comparison

NO WINDOW IS APPLIED TO THE MECH. The print runs 10:17:05 to 10:40:00 because that is the span
containing both Joe's bar and mine; the reversal search itself is unbounded.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
R, X = C.R, C.X
N = len(SC.ts); U = SC.U
HI, LO = SC.HI, SC.LO
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
RREV = int(C.W['rrev_wob'])
K0 = SC.K('2026-09-25 10:17:05')
KEND = SC.K('2026-09-25 10:40:00')
MINE = SC.K('2026-09-25 10:36:05')
JOE = SC.K('2026-09-25 10:21:00')
P0 = float(PX[K0]); SIDE = +1   # LONG
R1 = R[1]
REV1 = _mage_rev(R1, RREV)
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[K0])) / 60000.0)
imp = lambda j: (P0 - float(PX[j])) / P0 * 100.0 * SIDE

def fen(v, d):
    if d > 0: return 'hi oob' if v >= HI else ('hi ex-f' if v >= EXF_HI else 'in-fence')
    return 'lo oob' if v <= LO else ('lo ex-f' if v <= EXF_LO else 'in-fence')

print('\n# 10:17:05  pxs %.6f  LONG  walk frame -1 (DOWNWARD lineage)' % P0)
print('# a LONG entry improves as pxs falls. rrev_wob %d. oob %.0f/%.0f, ex-fence %.0f/%.0f.'
      % (RREV, LO, HI, EXF_LO, EXF_HI))

print('\n# EVERY ws1r REVERSAL FROM 10:17:05 TO 10:40:00')
rows = []
for j in range(K0, KEND + 1):
    if int(REV1[j]) == 0: continue
    rows.append((U(j), mn(j), '%+d' % int(REV1[j]),
                 'UP — ends a DOWNWARD walk' if int(REV1[j]) > 0 else 'DOWN',
                 '%.2f' % float(R1[j]), fen(float(R1[j]), -1),
                 '%.6f' % float(PX[j]), '%+.4f' % imp(j)))
box(('ts', '+min', '_mage_rev(ws1r, 2)', 'the reversal direction', 'ws1r', 'ws1r on frame -1',
     'pxs', 'LONG entry better by %'), rows)

print('\n# THE THREE CANDIDATE LANDINGS')
jmin = K0 + int(np.argmin([float(R1[j]) for j in range(K0, KEND + 1)]))
pmin = K0 + int(np.argmin([float(PX[j]) for j in range(K0, KEND + 1)]))
first_up = next((j for j in range(K0, N) if int(REV1[j]) > 0), None)
box(('the landing', 'bar', '+min', 'ws1r there', 'ws1r on frame -1', 'pxs',
     'LONG entry better by %'),
    [("JOE'S — the first ws1r reversal UP", U(first_up), mn(first_up),
      '%.2f' % float(R1[first_up]), fen(float(R1[first_up]), -1),
      '%.6f' % float(PX[first_up]), '%+.4f' % imp(first_up)),
     ('MINE — the first bar ws1r is oob-low', U(MINE), mn(MINE),
      '%.2f' % float(R1[MINE]), fen(float(R1[MINE]), -1),
      '%.6f' % float(PX[MINE]), '%+.4f' % imp(MINE)),
     ('the ws1r minimum in the window', U(jmin), mn(jmin),
      '%.2f' % float(R1[jmin]), fen(float(R1[jmin]), -1),
      '%.6f' % float(PX[jmin]), '%+.4f' % imp(jmin)),
     ('the pxs minimum in the window', U(pmin), mn(pmin),
      '%.2f' % float(R1[pmin]), fen(float(R1[pmin]), -1),
      '%.6f' % float(PX[pmin]), '%+.4f' % imp(pmin))])

print('\n# ws1r BAR BY BAR, 10:17:05 TO 10:25:00 — the window holding Joe\'s 10:21')
rows = []
K2 = SC.K('2026-09-25 10:25:00')
prev = None
for j in range(K0, K2 + 1):
    v = float(R1[j])
    step = '—' if prev is None else ('%+.2f' % (v - prev))
    rows.append((U(j), mn(j), '%.2f' % v, step, fen(v, -1),
                 '%+d' % int(REV1[j]) if int(REV1[j]) else '',
                 '%.6f' % float(PX[j]), '%+.4f' % imp(j)))
    prev = v
box(('ts', '+min', 'ws1r', 'ws1r step', 'ws1r on frame -1', 'reversal', 'pxs',
     'LONG entry better by %'), rows)

print('\n# DID ws1r EVER REACH oob BEFORE IT REVERSED?')
lowest = min(float(R1[j]) for j in range(K0, first_up + 1)) if first_up else float('nan')
box(('the question', 'the answer'),
    [('the lowest ws1r from 10:17:05 to the reversal', '%.2f' % lowest),
     ('the oob-low fence it had to reach', '%.0f' % LO),
     ('did it get there?', 'YES' if lowest <= LO else 'NO — it reversed %.2f short of it'
      % (lowest - LO)),
     ('so my landing rule had to wait', 'until %s, %s min past the reversal'
      % (U(MINE), mn(MINE).lstrip('+')))])
