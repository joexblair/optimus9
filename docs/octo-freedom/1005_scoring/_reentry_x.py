"""ws1x CROSSING ws1r AS THE RE-ENTRY TRIGGER, at xwob 6 and 8. 09-25. 1007.

Joe 1007: *"for #1, what happens to your view if we use ws1x-crossing ws1r with xwob 6 or 8?"*

A LONG re-entry off a low ws1r means x crossing OVER r - the inverse of the +dr exit cross.

THE CONVENTION, from jig.oob_ib_cross: the CROSS bar is the first bar of a run where x > r that
holds `xwob` consecutive bars; `conf` = cross + xwob - 1 is the first bar the cross is KNOWABLE.
A re-entry can only be placed at `conf`. Both are printed because the gap is the cost.

Joe's two hand-picked bars: 08:10:00 and 11:21:00.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
R1, X1 = C.R[1], C.X[1]
N = len(SC.ts)
K = lambda t: SC.K('2026-09-25 %s' % t)
d0, d1 = K('00:00:00'), K('23:59:55')

def crosses(xwob):
    """-> [(cross, conf)] where ws1x > ws1r holds xwob consecutive bars."""
    v = (X1 > R1) & np.isfinite(X1) & np.isfinite(R1)
    idx = np.arange(N)
    run = (idx + 1) - np.maximum.accumulate(np.where(v, 0, idx + 1))
    held = run >= max(1, xwob)
    conf = held & ~np.r_[False, held[:-1]]
    out = []
    for c in np.flatnonzero(conf):
        k = c - (xwob - 1)
        if k >= 1 and d0 <= k <= d1:
            out.append((int(k), int(c)))
    return out

print('# HOW OFTEN ws1x CROSSES OVER ws1r ON THE DAY')
box(('xwob bars', 'seconds', 'crosses on 09-25', 'per hour'),
    [(str(w), str(w * 5), str(len(crosses(w))), '%.1f' % (len(crosses(w)) / 24.0))
     for w in (1, 2, 4, 6, 8, 12)])

for wob in (6, 8):
    cx = crosses(wob)
    print('\n# xwob %d — THE CROSSES NEAREST JOE\'S TWO BARS' % wob)
    rows = []
    for lbl, ts in (("Joe's 08:10:00", '08:10:00'), ("Joe's 11:21:00", '11:21:00')):
        kj = K(ts)
        before = [z for z in cx if z[1] <= kj]
        after = [z for z in cx if z[1] > kj]
        for tag, z in (('last conf at or before', before[-1] if before else None),
                       ('first conf after', after[0] if after else None)):
            if z is None:
                rows.append((lbl, tag, '—', '—', '—', '—', '—', '—', '—')); continue
            k, c = z
            p_j, p_c = float(PX[kj]), float(PX[c])
            rows.append((lbl, tag, SC.U(k), SC.U(c),
                         '%+.1f' % ((int(SC.ts[c]) - int(SC.ts[kj])) / 60000.0),
                         '%.2f' % float(R1[c]), '%.2f' % float(X1[c]),
                         '%.6f' % p_c,
                         '%+.4f' % ((p_c - p_j) / p_j * 100.0)))
    box(('Joe bar', 'which cross', 'cross bar', 'conf bar', 'conf vs Joe min', 'ws1r at conf',
         'ws1x at conf', 'pxs at conf', 'LONG cost vs Joe bar'), rows)

print('\n# EVERY xwob 8 CROSS IN THE TWO RE-ENTRY WINDOWS')
for a_, b_ in (('07:40:00', '08:30:00'), ('11:00:00', '11:40:00')):
    cx = [z for z in crosses(8) if K(a_) <= z[1] <= K(b_)]
    print('\n## %s to %s — %d crosses' % (a_, b_, len(cx)))
    box(('cross bar', 'conf bar', 'ws1r at cross', 'ws1x at cross', 'ws1r at conf',
         'ws1r low oob at cross?', 'pxs at conf'),
        [(SC.U(k), SC.U(c), '%.2f' % float(R1[k]), '%.2f' % float(X1[k]),
          '%.2f' % float(R1[c]), 'Y' if float(R1[k]) <= SC.LO else '-',
          '%.6f' % float(PX[c])) for k, c in cx] or [('—',) * 7])

print('\n# THE SAME CROSS, GATED ON ws1r BEING LOW OOB AT THE CROSS BAR')
for wob in (6, 8):
    cx = [z for z in crosses(wob) if float(R1[z[0]]) <= SC.LO]
    print('- xwob %d: %d of %d crosses have ws1r <= %.0f at the cross bar'
          % (wob, len(cx), len(crosses(wob)), SC.LO))
    near = [z for z in cx if abs(int(SC.ts[z[1]]) - int(SC.ts[K('08:10:00')])) < 3600000
            or abs(int(SC.ts[z[1]]) - int(SC.ts[K('11:21:00')])) < 3600000]
    box(('cross bar', 'conf bar', 'ws1r at cross', 'ws1x at cross', 'pxs at conf'),
        [(SC.U(k), SC.U(c), '%.2f' % float(R1[k]), '%.2f' % float(X1[k]),
          '%.6f' % float(PX[c])) for k, c in near] or [('—',) * 5])
