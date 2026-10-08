"""THE ESTABLISHED `traj` MECH, APPLIED TO ws60r AT 2026-08-22 13:33:50. 1008.

Joe 1008: *"there's an established mech for `traj` - see if you can track it down before we build"*.

FOUND: `optimus9/compute/rule2_trajectory.py`, Joe 0924, task #22's FIRST mechanism.

  Joe 0924 verbatim: *"'trajectory' is detected when any of the 3 lines are travelling towards dr,
  for more than 2 minutes. this can be measured by looking back across the line to find its
  dr-opposed extrema"* / on the look-back: *"use the same mech the divergence uses to discover an
  extrema - look back in 5 minute windows"*.

  trajectory(r, dr, k, block, min_bars, min_travel) ->
     finds the dr-OPPOSED extrema behind k by the divergence's block walk (blocks of `block` bars,
     empty blocks skipped, stop at the first block that does not improve), then
     has = (bars since that extrema > min_bars) AND (travel runs towards dr) AND |travel| >= min_travel

  block      anchor_floater.AF_BLOCK = 60 bars = 300 s = 5 min, banked at jig.py:310
  min_bars   24 bars = 2 min, STRICTLY more. Joe 0924 "more than 2 minutes". His value, said in
             chat, not in a config table
  min_travel 0.0 — UNSET. Joe 0924: *"I would say the true threshold is in the OOS data"*

AND ITS DOCSTRING ALREADY DIAGNOSES THE BUG I SHIPPED, verbatim:
  *"WHY THE BAR-TO-BAR READING WAS WRONG. Measured at 09-03 02:52:20 before Joe ruled: all three of
  ws1r, ws2r, ws3r tick DOWN on that bar by 8.18, 8.63 and 9.91 r-points, so an unbroken-climb test
  returns 0 bars on every line."*
My `step_dir` is that bar-to-bar reading. Joe ruled it out on 0924; I reintroduced it on 1008.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute.rule2_trajectory import trajectory, opposed_extrema
from optimus9.analysis.jig import AF_BLOCK
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
R12 = C.R[C.TRIG_TF]
BLOCK, MINB = AF_BLOCK, 24
K = SC.K('2026-08-22 13:33:50'); DE = SC.K('2026-08-22 13:39:55')
print('# block %d bars = %.0f min, min_bars %d = %.0f min (strictly more), min_travel 0.0'
      % (BLOCK, BLOCK * 5 / 60.0, MINB, MINB * 5 / 60.0), flush=True)

def step_dir(k):
    cur = float(R60[k]); j = k
    while j > 0 and (not np.isfinite(R60[j - 1]) or float(R60[j - 1]) == cur): j -= 1
    return 0 if j <= 0 else (1 if cur > float(R60[j - 1]) else -1)

print('\n# ws60r AT THE TWO CANDIDATE BARS — THE ESTABLISHED MECH vs WHAT I SHIPPED')
rows = []
for lbl, k in (('the ws12r oob crossing  13:33:50', K), ('the dwell-ending  13:39:55', DE)):
    side = +1 if float(R12[k]) >= SC.HI else -1
    for ask, adir in (('is ws60r travelling UP', +1), ('is ws60r travelling DOWN', -1)):
        t = trajectory(R60, adir, k, BLOCK, MINB)
        rows.append((lbl, ask, 'YES' if t['has'] else 'no',
                     U(t['bar']) if t['bar'] is not None else '—',
                     '%.4f' % t['value'] if np.isfinite(t['value']) else '—',
                     '%.4f' % float(R60[k]),
                     '%+.4f' % t['travel'] if np.isfinite(t['travel']) else '—',
                     '%d' % t['bars'], '%.1f' % (t['bars'] * 5 / 60.0),
                     str(len(t['blocks']))))
box(('the bar read', 'the question', 'the established mech', 'dr-opposed extrema',
     'ws60r there', 'ws60r now', 'travel', 'bars since', 'min since', 'blocks walked'), rows)

print('\n# THE SAME TWO BARS, SIDE BY SIDE')
rows = []
for lbl, k in (('13:33:50  the ws12r oob crossing', K), ('13:39:55  the dwell-ending', DE)):
    side = +1 if float(R12[k]) >= SC.HI else -1
    up = trajectory(R60, +1, k, BLOCK, MINB)['has']
    dn = trajectory(R60, -1, k, BLOCK, MINB)['has']
    est = 'UP' if up and not dn else ('DOWN' if dn and not up else ('BOTH' if up and dn else 'NEITHER'))
    mine = 'UP' if step_dir(k) > 0 else ('DOWN' if step_dir(k) < 0 else 'flat')
    rows.append((lbl, '%.4f' % float(R12[k]), 'high oob' if side > 0 else 'low oob',
                 est, mine, 'AGREE' if est == mine else '**DIFFER**',
                 ('gate OPEN' if (est == 'UP' and side > 0) or (est == 'DOWN' and side < 0)
                  else 'gate closed'),
                 ('gate OPEN' if (mine == 'UP' and side > 0) or (mine == 'DOWN' and side < 0)
                  else 'gate closed')))
box(('the bar', 'ws12r there', 'which oob side', 'ESTABLISHED traj', 'my step_dir traj',
     'do they agree', 'the gate on the established mech', 'the gate on what I shipped'), rows)

print('\n# THE BLOCK WALK THAT FOUND THE EXTREMA — 13:33:50, asking "travelling UP" (dr +1)')
t = trajectory(R60, +1, K, BLOCK, MINB)
box(('block', 'from', 'to', 'the block\'s lowest ws60r', 'at', 'a new running low?'),
    [(str(i + 1), U(lo), U(hi - 1), '%.4f' % b if np.isfinite(b) else 'all NaN',
      U(m) if m is not None else '—', 'YES' if nb else 'no — the walk stops here')
     for i, (lo, hi, b, m, nb) in enumerate(t['blocks'])])
print('- the extrema the mech found: %s at %.4f, %d bars = %.1f min back, travel %+.4f'
      % (U(t['bar']), t['value'], t['bars'], t['bars'] * 5 / 60.0, t['travel']))
