"""AT WHAT ws1r LEVEL DOES ws1x ACTUALLY CROSS ws1r? 09-25, xwob 6. 1007.

Joe 1007: *"ws1x can only cross ws1r when ws1r is ex-fence. becasue the dr is +1, ws1r must be low
ex-fence before it can be crossed"*.

A testable claim. Both cross directions are binned by ws1r at the cross bar.
Joe 0925 on the scaling: *"the BB%B and K lines are scaled, it's in their calcs. K has a max,
whereas BB%B does not"* - so ws1x (BB%B) is unbounded and ws1r (K) is 0..100.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
R1, X1 = C.R[1], C.X[1]
N = len(SC.ts)
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
K = lambda t: SC.K('2026-09-25 %s' % t)
d0, d1 = K('00:00:00'), K('23:59:55')
XWOB = 6

def crosses(over):
    v = ((X1 > R1) if over else (X1 < R1)) & np.isfinite(X1) & np.isfinite(R1)
    idx = np.arange(N)
    run = (idx + 1) - np.maximum.accumulate(np.where(v, 0, idx + 1))
    held = run >= XWOB
    cf = held & ~np.r_[False, held[:-1]]
    return [int(c) - (XWOB - 1) for c in np.flatnonzero(cf)
            if int(c) - (XWOB - 1) >= 1 and d0 <= int(c) - (XWOB - 1) <= d1]

BANDS = [('<= 17  low ex-fence', lambda v: v <= EXF_LO),
         ('17 to 50', lambda v: EXF_LO < v <= 50),
         ('50 to 83', lambda v: 50 < v < EXF_HI),
         ('>= 83  high ex-fence', lambda v: v >= EXF_HI)]
print('# ws1r AT THE CROSS BAR, xwob %d, every cross on 09-25' % XWOB)
rows = []
for lbl, over in (('ws1x crosses OVER ws1r', True), ('ws1x crosses UNDER ws1r', False)):
    cx = crosses(over)
    for bl, fn in BANDS:
        s = [k for k in cx if fn(float(R1[k]))]
        rows.append((lbl, bl, str(len(s)), '%.1f%%' % (len(s) / len(cx) * 100.0),
                     '%.2f' % min((float(R1[k]) for k in s), default=float('nan')),
                     '%.2f' % max((float(R1[k]) for k in s), default=float('nan'))))
    rows.append((lbl, 'ALL', str(len(cx)), '100.0%',
                 '%.2f' % min(float(R1[k]) for k in cx),
                 '%.2f' % max(float(R1[k]) for k in cx)))
box(('cross direction', 'ws1r band at the cross', 'crosses', 'share', 'min ws1r', 'max ws1r'), rows)

print('\n# THE HIGHEST-ws1r OVER-CROSSES — the ones the claim says cannot exist')
cx = sorted(crosses(True), key=lambda k: -float(R1[k]))[:12]
box(('cross bar', 'ws1r', 'ws1x', 'x - r', 'pxs'),
    [(SC.U(k), '%.2f' % float(R1[k]), '%.2f' % float(X1[k]),
      '%+.2f' % (float(X1[k]) - float(R1[k])), '%.6f' % float(PX[k])) for k in cx])

print('\n# THE RANGE OF EACH LINE ON THE DAY — why a cross is possible at any r level')
box(('line', 'min', 'max', 'bounded?'),
    [('ws1r  (K)', '%.2f' % float(np.nanmin(R1[d0:d1 + 1])),
      '%.2f' % float(np.nanmax(R1[d0:d1 + 1])), 'yes, 0..100'),
     ('ws1x  (BB%B)', '%.2f' % float(np.nanmin(X1[d0:d1 + 1])),
      '%.2f' % float(np.nanmax(X1[d0:d1 + 1])), 'NO')])
print('- ws1x spends %.1f%% of the day above 100 and %.1f%% below 0'
      % (np.mean(X1[d0:d1 + 1] > 100) * 100.0, np.mean(X1[d0:d1 + 1] < 0) * 100.0))
