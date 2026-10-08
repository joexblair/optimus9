"""min_travel, SIZED FROM REAL BARS — and what 2 x TF-width does to min_bars. 1008.

Joe 1008: *"I don't know what this is. give me an example of a min_travel value for 08-22 15:26
(confirmedd UP), and 19:00 (confirmed down)"* / *"I'm proposing we use ({knob:2,
'TRAJ_MULTI_TF_SAMP'} * TF-width) as a replacement"*.

WHAT min_travel IS, in one line: the smallest |travel| in r-points, measured from the dr-opposed
extrema to the test bar, that counts as trajectory. travel = ws60r(now) - ws60r(extrema).
At 0.0 any travel with the right sign passes, including floating-point dust - the module docstring
records -7.105427357601002e-14 passing on 09-02.

TRAJ_MULTI_TF_SAMP x TF-width, for ws60r: 2 x 60 min = 120 min = 1440 bars at the 5 s grid.
Against Joe 0924's flat 24 bars = 2 min. Both thresholds are applied to every bar below so the
difference is visible, not argued.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute.rule2_trajectory import trajectory
from optimus9.analysis.jig import AF_BLOCK
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
R12 = C.R[C.TRIG_TF]
TFW = 60                     # ws60r's TF-width in minutes
SAMP = 2                     # TRAJ_MULTI_TF_SAMP, Joe's proposal
MINB_JOE0924 = 24            # 2 min flat
MINB_NEW = int(SAMP * TFW * 60 / 5)   # 2 x 60 min = 1440 bars
print('# ws60r: TF-width %d min. TRAJ_MULTI_TF_SAMP %d -> min_bars %d bars = %.0f min'
      % (TFW, SAMP, MINB_NEW, MINB_NEW * 5 / 60.0))
print('# against Joe 0924 flat: %d bars = %.0f min. block %d bars = %.0f min'
      % (MINB_JOE0924, MINB_JOE0924 * 5 / 60.0, AF_BLOCK, AF_BLOCK * 5 / 60.0), flush=True)

BARS = [('2026-08-22 13:33:50', 'the bar we unpacked'),
        ('2026-08-22 15:26:15', 'JOE: confirmed UP'),
        ('2026-08-22 19:00:00', 'JOE: confirmed DOWN')]

print('\n# THE TRAVEL AT EACH BAR, BOTH DIRECTIONS — this is what min_travel would gate')
rows = []
for ts, lab in BARS:
    k = SC.K(ts)
    side = +1 if float(R12[k]) >= SC.HI else (-1 if float(R12[k]) <= SC.LO else 0)
    for ask, adir in (('UP', +1), ('DOWN', -1)):
        t = trajectory(R60, adir, k, AF_BLOCK, 0)       # min_bars 0 so nothing is filtered out
        rows.append((ts[-8:], lab, ask,
                     U(t['bar']) if t['bar'] is not None else '—',
                     '%.4f' % t['value'] if np.isfinite(t['value']) else '—',
                     '%.4f' % float(R60[k]),
                     '**%+.4f**' % t['travel'] if np.isfinite(t['travel']) else '—',
                     '%d' % t['bars'], '%.1f' % (t['bars'] * 5 / 60.0)))
box(('the bar', 'Joe\'s read', 'asking', 'dr-opposed extrema', 'ws60r there', 'ws60r now',
     'TRAVEL in r-points', 'bars since', 'min since'), rows)

print('\n# WHAT EACH min_travel VALUE WOULD DO, at min_bars 24 (Joe 0924 flat)')
rows = []
for mt in (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0):
    cells = []
    for ts, lab in BARS:
        k = SC.K(ts)
        up = trajectory(R60, +1, k, AF_BLOCK, MINB_JOE0924, mt)['has']
        dn = trajectory(R60, -1, k, AF_BLOCK, MINB_JOE0924, mt)['has']
        cells.append('UP' if up and not dn else ('DOWN' if dn and not up
                     else ('BOTH' if up and dn else 'NEITHER')))
    rows.append(('%.1f' % mt, *cells))
box(('min_travel, r-points', '13:33:50', '15:26:15  (Joe: UP)', '19:00:00  (Joe: DOWN)'), rows)

print('\n# THE SAME, at min_bars %d  (TRAJ_MULTI_TF_SAMP %d x %d min)' % (MINB_NEW, SAMP, TFW))
rows = []
for mt in (0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0):
    cells = []
    for ts, lab in BARS:
        k = SC.K(ts)
        up = trajectory(R60, +1, k, AF_BLOCK, MINB_NEW, mt)['has']
        dn = trajectory(R60, -1, k, AF_BLOCK, MINB_NEW, mt)['has']
        cells.append('UP' if up and not dn else ('DOWN' if dn and not up
                     else ('BOTH' if up and dn else 'NEITHER')))
    rows.append(('%.1f' % mt, *cells))
box(('min_travel, r-points', '13:33:50', '15:26:15  (Joe: UP)', '19:00:00  (Joe: DOWN)'), rows)

print('\n# SCALE — every ws60r travel the block walk finds across 08-22, both directions')
k0, k1 = SC.K('2026-08-22 00:00:00'), SC.K('2026-08-22 23:59:55')
tv = []
for k in range(k0, k1 + 1, 60):
    for adir in (+1, -1):
        t = trajectory(R60, adir, k, AF_BLOCK, 0)
        if np.isfinite(t['travel']) and t['travel'] != 0: tv.append(abs(t['travel']))
tv.sort()
box(('the percentile of |travel| over 08-22', 'r-points'),
    [('samples', str(len(tv)))]
    + [('%dth' % p, '%.4f' % tv[int(len(tv) * p / 100) - 1]) for p in (10, 25, 50, 75, 90, 99)]
    + [('max', '%.4f' % tv[-1])])

print('\n# THE TWO SAMPLES AROUND THE DIRECTION CHANGE AT 13:33:50 — "we follow the tail"')
k = SC.K('2026-08-22 13:33:50')
up = trajectory(R60, +1, k, AF_BLOCK, 0); dn = trajectory(R60, -1, k, AF_BLOCK, 0)
box(('the candidate extrema', 'ts', 'ws60r there', 'travel to 13:33:50', 'bars since', 'min since',
     'which is it'),
    [('the LOW the UP read uses', U(up['bar']), '%.4f' % up['value'], '%+.4f' % up['travel'],
      str(up['bars']), '%.1f' % (up['bars'] * 5 / 60.0), 'the OLDER of the two'),
     ('the HIGH the DOWN read uses', U(dn['bar']), '%.4f' % dn['value'], '%+.4f' % dn['travel'],
      str(dn['bars']), '%.1f' % (dn['bars'] * 5 / 60.0), 'the MORE RECENT of the two')])
