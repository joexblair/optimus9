"""HOW LONG AFTER A HELD ws60x CROSS DOES ws60r TURN? — the lookback, measured. 1009.

Joe 1009: *"because BB lines lead K lines, the ws60r UP event that the current code consumes needs
to be reversed by the downward ws60x-cross-race that fired ~14:15 (+/-20 minutes) with a 24 or 48
bar xwob. 24 or 48 bars is enough validation to confirm the cross. ws60r then has no choice but to
turn DOWN and follow ws60x"* / *"the lookback needed for 'recent ws60x' is not clear to me on my TV
charts"*.

So: take every ws60x cross of ws60r that HOLDS xwob bars, and measure the bars until ws60r's own
traj dir matches the cross direction. The distribution of that lag IS the lookback. No threshold is
applied and no cap is placed on the search - a cross whose r never turns is reported as 'never'.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
os.environ['W_DGATE'] = 'vote'
import _chain10 as C
from _trajmech import traj
SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
X60 = np.asarray(SC.LD(60 * 60, 'x'), float)[:N]
BLK, TAIL, LOOK, KIND = C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND
# traj's dir at every bar is expensive to compute 1.6M times, so it is sampled on the 60-bar grid
# the sampler already uses - the same grid the gate reads.
GRID = np.arange(LOOK * BLK + 10, N, BLK)
DIR = np.zeros(N, np.int8)
for i, j in enumerate(GRID):
    DIR[j] = traj(R60, int(j), BLK, TAIL, LOOK, KIND, 0)['dir']
print('# traj dir sampled on the %d-bar grid, %d sample bars' % (BLK, len(GRID)), flush=True)
xu = X60 < R60
rows = []
for xwob in (24, 48):
    for dirn, nm in ((-1, 'DOWNWARD — ws60x crosses UNDER ws60r'),
                     (+1, 'UPWARD — ws60x crosses OVER ws60r')):
        cond = xu if dirn < 0 else ~xu
        cr = np.flatnonzero(cond[1:] & ~cond[:-1]) + 1
        lags = []; never = 0; already = 0
        for a in cr:
            h = 0
            while a + h < N and cond[a + h]: h += 1
            if h < xwob: continue
            conf = a + xwob - 1                    # the bar the hold completes
            g = GRID[GRID >= conf]
            if not len(g): continue
            if DIR[int(g[0])] == dirn: already += 1; lags.append(0); continue
            hit = None
            for j in g:
                if DIR[int(j)] == dirn: hit = int(j); break
            if hit is None: never += 1; continue
            lags.append((hit - conf))
        if not lags and not never: continue
        L = np.array(lags, float)
        tt = len(lags) + never
        rows.append(('xwob %d' % xwob, nm, str(tt),
                     '%d = %.1f%%' % (len(lags), 100.0 * len(lags) / tt),
                     str(already), str(never),
                     '%.1f' % (float(np.median(L)) * 5 / 60.0) if len(L) else '—',
                     '%.1f' % (float(np.percentile(L, 75)) * 5 / 60.0) if len(L) else '—',
                     '%.1f' % (float(np.percentile(L, 90)) * 5 / 60.0) if len(L) else '—',
                     '%.1f' % (float(L.max()) * 5 / 60.0) if len(L) else '—'))
print('\n# FROM THE BAR THE HOLD COMPLETES, HOW LONG UNTIL ws60r\'s traj MATCHES THE CROSS')
box(('the hold', 'the cross', 'crosses that held', 'r eventually turned', 'already turned at the '
     'hold bar', 'never turned', 'median lag min', '75th pct min', '90th pct min', 'max min'), rows)
print('- "already turned" means ws60r\'s traj matched the cross on the first grid bar at or after')
print('  the hold completed, so the lag is 0 and the cross added nothing.')
print('- "never turned" means no later grid bar to the tape end had traj matching the cross.')
