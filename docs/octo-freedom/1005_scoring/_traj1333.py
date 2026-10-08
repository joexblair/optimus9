"""ws60r's TRAJECTORY AT 2026-08-22 13:33:50 — two readings, one line. 1008.

Joe 1008: *"my view of ws60r's trajectory at 08-22 13:33 is up, because at ~11:00 its value was
~20, and at 13:33 ws60r's value is ~50. 50 is higher than 20, therefore trajectory is up / lets
unpack the diff in the trajectory mech that was applied at 13:33"*.

WHAT THE CODE APPLIED, and where that definition came from. `step_dir` is the sign of
(value now - value immediately BEFORE its most recent step change). It compares ONE STEP. I wrote
that definition into 1007_ws12_baton.md for the no-op confluence - *"trajectory is the sign of
(ws1r now - ws1r at its last step change) ... so it needs no lookback window"* - and then reused it
for ws60r when Joe said *"per the traj spec"*. THE DEFINITION IS MINE AND HAS NEVER BEEN RULED.

JOE'S READING compares the value now against the value some distance back, which on a line that has
climbed 20 -> 50 over 2.5 hours gives UP regardless of the last single step.

NOTHING IS SCORED. The line's every step is printed so the two readings can be compared on the
actual values.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
R12 = C.R[C.TRIG_TF]
K = SC.K('2026-08-22 13:33:50')
DE = SC.K('2026-08-22 13:39:55')
print('# ws60r at 2026-08-22 13:33:50 = %.4f   ws12r = %.4f (low oob, fence %.0f)'
      % (float(R60[K]), float(R12[K]), SC.LO), flush=True)

# every step change ws60r made from 08-22 08:00 to 13:45
lo = SC.K('2026-08-22 08:00:00'); hi = SC.K('2026-08-22 13:45:00')
steps = []
prev = None
for j in range(lo, hi + 1):
    v = float(R60[j])
    if not np.isfinite(v): continue
    if prev is None or v != prev:
        steps.append((j, v, (v - prev) if prev is not None else float('nan')))
        prev = v
print('\n# EVERY ws60r STEP CHANGE, 08:00 to 13:45 on 2026-08-22')
box(('ts', 'ws60r', 'change from the previous step', 'step direction'),
    [(U(j), '%.4f' % v, ('%+.4f' % d) if np.isfinite(d) else '—',
      ('UP' if d > 0 else ('DOWN' if d < 0 else 'flat')) if np.isfinite(d) else '—')
     for j, v, d in steps])

# the two readings, at the crossing bar and the dwell-ending bar
def step_dir(k):
    cur = float(R60[k]); j = k
    while j > 0 and (not np.isfinite(R60[j - 1]) or float(R60[j - 1]) == cur): j -= 1
    if j <= 0: return 0, None, None
    return (1 if cur > float(R60[j - 1]) else (-1 if cur < float(R60[j - 1]) else 0),
            j - 1, float(R60[j - 1]))

print('\n# THE TWO READINGS, AT BOTH CANDIDATE BARS')
rows = []
for lbl, k in (('the ws12r oob crossing  13:33:50', K), ('the dwell-ending  13:39:55', DE)):
    sd, pb, pv = step_dir(k)
    rows.append((lbl, 'MINE — one step back', U(pb) if pb else '—',
                 '%.4f' % pv if pv is not None else '—', '%.4f' % float(R60[k]),
                 '%+.4f' % (float(R60[k]) - pv) if pv is not None else '—',
                 'UP' if sd > 0 else ('DOWN' if sd < 0 else 'flat')))
    for mins in (30, 60, 90, 120, 150, 180):
        b = k - int(mins * 60 / 5)
        if b < 0: continue
        pv2 = float(R60[b])
        rows.append((lbl, "JOE'S — %d min back" % mins, U(b), '%.4f' % pv2,
                     '%.4f' % float(R60[k]), '%+.4f' % (float(R60[k]) - pv2),
                     'UP' if float(R60[k]) > pv2 else ('DOWN' if float(R60[k]) < pv2 else 'flat')))
box(('the bar read', 'the reading', 'the reference bar', 'ws60r there', 'ws60r now',
     'difference', 'trajectory'), rows)

print('\n# ws60r AT JOE\'S REFERENCE, ~11:00')
for t in ('2026-08-22 10:30:00', '2026-08-22 11:00:00', '2026-08-22 11:30:00',
          '2026-08-22 12:00:00', '2026-08-22 12:30:00', '2026-08-22 13:00:00',
          '2026-08-22 13:30:00', '2026-08-22 13:33:50', '2026-08-22 13:39:55'):
    k_ = SC.K(t)
    print('  %s   ws60r %7.4f   ws12r %7.4f' % (t[-8:], float(R60[k_]), float(R12[k_])))
print('\n- the gate used MINE. Joe reads the climb since ~11:00. Both are printed above against the')
print('  same values, and the step list is the evidence for which the line actually did.')
