"""DOES A ws60x CROSS OF ws60m LEAD ws60r's TURN BETTER THAN A CROSS OF ws60r DOES? 1009.

Joe 1009: *"what time to you get a ws60x cross m with a wob 24? that might be a better way to
handle this"*. On 07-15 the m-cross confirmed 14:21:45 DOWN and held 160.2 min, against an r-cross
whose last confirmed signal at 14:49 was a 4h-stale UP. This tests whether that holds tape-wide.

For every cross that holds `wob` bars, the lag until ws60r's own traj dir matches the cross. traj is
sampled on the 60-bar grid the gate already reads.
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
M60 = np.asarray(SC.LD(60 * 60, 'm'), float)[:N]
BLK, TAIL, LOOK, KIND = C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND
GRID = np.arange(LOOK * BLK + 10, N, BLK)
DIR = np.zeros(N, np.int8)
for j in GRID:
    DIR[j] = traj(R60, int(j), BLK, TAIL, LOOK, KIND, 0)['dir']
print('# traj dir on the %d-bar grid, %d sample bars' % (BLK, len(GRID)), flush=True)
rows = []
for tname, tgt in (('ws60m', M60), ('ws60r', R60)):
    xu = X60 < tgt
    for wob in (24, 48):
        for dirn, dn in ((-1, 'DOWN'), (+1, 'UP')):
            cond = xu if dirn < 0 else ~xu
            cr = np.flatnonzero(cond[1:] & ~cond[:-1]) + 1
            held = []; lags = []; already = 0; never = 0; holdlen = []
            for a in cr:
                h = 0
                while a + h < N and cond[a + h]: h += 1
                if h < wob: continue
                held.append(int(a)); holdlen.append(h)
                conf = a + wob - 1
                g = GRID[GRID >= conf]
                if not len(g): continue
                if DIR[int(g[0])] == dirn: already += 1; lags.append(0); continue
                hit = next((int(j) for j in g if DIR[int(j)] == dirn), None)
                if hit is None: never += 1
                else: lags.append(hit - conf)
            if not held: continue
            L = np.array(lags, float); H = np.array(holdlen, float)
            tt = len(lags) + never
            rows.append((tname, 'wob %d' % wob, dn, str(len(held)),
                         '%d = %.1f%%' % (already, 100.0 * already / tt) if tt else '—',
                         '%d' % never,
                         '%.1f' % (float(np.percentile(L, 75)) * 5 / 60.0) if len(L) else '—',
                         '%.1f' % (float(np.percentile(L, 90)) * 5 / 60.0) if len(L) else '—',
                         '%.1f' % (float(np.median(H)) * 5 / 60.0),
                         '%.1f' % (float(np.percentile(H, 90)) * 5 / 60.0)))
box(('the target line', 'the hold', 'cross dir', 'crosses that held',
     'ws60r traj ALREADY matched at the wob bar', 'never matched',
     'lag 75th pct min', 'lag 90th pct min', 'median hold min', 'hold 90th pct min'), rows)
print('- "already matched" is the cross telling you what traj already said - it adds nothing there.')
print('- the useful population is the complement: the crosses where traj had NOT yet turned.')
