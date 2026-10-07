"""THE ~08:10 EPISODE, +/- 4 min, bar by bar. 09-25. 1007.

Joe 1007: *"we have 2 wob-validated crosses for the ~11:21 episode now. what do we have for ~08:10
(+/- 4 minutes)?"* / *"for context we're only wobbing the cross back towards 50. this makes it
possible to allow a thin ws1x spike to pierce down through ws1r before reversing back towards 50"*.

THE MECH AS JOE JUST STATED IT:
  the pierce   ws1x drops BELOW ws1r. NO WOB - a thin spike is allowed.
  the return   ws1x crosses back ABOVE ws1r and HOLDS xwob bars. The wob is on this leg only.
  conf         return bar + xwob - 1, the first bar the return is knowable.

Printed for the 08:10 window at bar resolution, and the pierce/return episodes for both windows.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
R1, X1 = C.R[1], C.X[1]
N = len(SC.ts)
EXF_LO = float(SC.LG['momo_fence_r'])
K = lambda t: SC.K('2026-09-25 %s' % t)

def episodes(a, b):
    """-> [(pierce_from, pierce_to, return_bar, above_run)] in [a, b]."""
    below = (X1 < R1) & np.isfinite(X1) & np.isfinite(R1)
    out = []; j = a
    while j <= b:
        if not below[j]:
            j += 1; continue
        p0 = j
        while j <= N - 1 and below[j]:
            j += 1
        p1 = j - 1
        rb = j if j <= N - 1 else None          # the return bar: first bar back above r
        run = 0
        if rb is not None:
            while rb + run <= N - 1 and not below[rb + run]:
                run += 1
        out.append((p0, p1, rb, run))
    return out

for lbl, a_, b_ in (('THE 08:10 WINDOW, 08:06:00 to 08:14:00', '08:06:00', '08:14:00'),
                    ('THE 11:21 WINDOW, 11:17:00 to 11:25:00', '11:17:00', '11:25:00')):
    print('\n# PIERCE / RETURN EPISODES — %s' % lbl)
    eps = episodes(K(a_), K(b_))
    box(('pierce from', 'to', 'pierce bars', 'ws1r at pierce start', 'ws1x min in pierce',
         'return bar', 'above-r run bars', 'wob 6?', 'wob 8?', 'ws1r at return',
         'ws1r <= 17 at return?', 'conf at wob 6'),
        [(SC.U(p0), SC.U(p1), str(p1 - p0 + 1), '%.2f' % float(R1[p0]),
          '%.2f' % float(np.nanmin(X1[p0:p1 + 1])),
          SC.U(rb) if rb else '—', str(run),
          'Y' if run >= 6 else '-', 'Y' if run >= 8 else '-',
          '%.2f' % float(R1[rb]) if rb else '—',
          ('Y' if float(R1[rb]) <= EXF_LO else '-') if rb else '—',
          SC.U(rb + 5) if (rb and run >= 6) else '—')
         for p0, p1, rb, run in eps] or [('—',) * 12])

print('\n# THE 08:10 WINDOW, EVERY BAR')
a, b = K('08:06:00'), K('08:14:00')
box(('ts', 'ws1r', 'ws1x', 'x vs r', 'ws1r <= 17?', 'pxs'),
    [(SC.U(k), '%.2f' % float(R1[k]), '%.2f' % float(X1[k]),
      'BELOW' if float(X1[k]) < float(R1[k]) else 'above',
      'Y' if float(R1[k]) <= EXF_LO else '-', '%.6f' % float(PX[k]))
     for k in range(a, b + 1)])
print('- ws1r min in the window: %.2f at %s; ex-fence is %.0f'
      % (float(np.nanmin(R1[a:b + 1])), SC.U(a + int(np.nanargmin(R1[a:b + 1]))), EXF_LO))
print('- ws1r at 08:10:00 exactly: %.2f' % float(R1[K('08:10:00')]))
