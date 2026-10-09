"""THE 40-MINUTE UP/DOWN VOTE vs THE TRAVEL VERDICT, AT EVERY DWELL-ENDING. 1009.

Joe 1009: *"let's replace diff weight with a simple how many UPS vs how mnay DOWNS are in the tail,
backed by the Mage"* / *"I meant the last 40 minutes"* / *"I'm not really swayed by the Mage diffs -
they represent pxs bar on bar, and there's a lot of voliatility. I'm using ws60 Mage as a beacon -
it's consitently higher than ws60r"*.

So the vote is on ws60r's OWN diffs, counted not weighted, over 40 minutes = 8 samples at
TRAJ_BLOCK 60 bars = 5.0 min each. The Mage is recorded as a LEVEL - the `Mage-r` gap and its
stability across the window - not as a vote.

NOTHING IS WIRED IN. This measures what the vote WOULD have returned at each bar the chain actually
consulted ws60r, against what `travel` returned there.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
from _trajmech import traj

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
WIN = float(os.environ.get('W_VOTE_MIN', 40))          # Joe 1009: the last 40 minutes
BL = C.TRAJ_BLOCK * 5 / 60.0
ND = int(round(WIN / BL))
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
sg = lambda z: 0 if z == 0 else (1 if z > 0 else -1)
NM = {0: 'tied 0', 1: 'UP +1', -1: 'DOWN -1'}

def vote(k, d):
    s = traj(R60, k, C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND, d)
    sm = s['samples']
    if len(sm) < ND + 1:
        return None
    u = dn = fl = 0
    for i in range(ND):
        z = sg(float(R60[sm[i][0]]) - float(R60[sm[i + 1][0]]))
        u += z > 0; dn += z < 0; fl += z == 0
    gaps = [float(M60[sm[i][0]]) - float(R60[sm[i][0]]) for i in range(ND + 1)]
    return dict(up=u, down=dn, flat=fl, v=sg(u - dn), travel=s['travel'], tdir=s['dir'],
                tail=s['tail_used'], gap0=gaps[0], gmin=min(gaps), gmax=max(gaps),
                gspread=max(gaps) - min(gaps),
                gstep=max(abs(gaps[i + 1] - gaps[i]) for i in range(ND)))

# the chain, so the consultation bars are the real ones
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])

C.DG_READ.clear()
k, d, g, legs = 1, +1, 0, 0
SEEN = []
while True:
    g += 1
    if g > 20000: break
    before = set(C.DG_READ)
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    legs += 1
    for key in set(C.DG_READ) - before:
        SEEN.append(key)
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
print('# %d legs, %d ws60r consultations at a dwell-ending. the vote window is %.0f min = %d diffs'
      % (legs, len(SEEN), WIN, ND), flush=True)

c = collections.Counter(); rows = []; FL = []
for (b, dd) in sorted(SEEN):
    r = vote(b, dd)
    if r is None: c['skipped — fewer samples than the window needs'] += 1; continue
    c['consultations scored'] += 1
    c['  vote %s' % NM[r['v']]] += 1
    c['  travel %s' % NM[r['tdir']]] += 1
    agree = r['v'] == r['tdir']
    c['  the vote AGREES with travel' if agree else '  the vote DISAGREES with travel'] += 1
    og = 'HANDOVER' if r['tdir'] == dd else 'REFUSED'
    ng = ('HANDOVER' if r['v'] == dd else ('REFUSED' if r['v'] == -dd else 'TIED — no verdict'))
    c['    gate %s -> %s' % (og, ng)] += 1
    if r['v'] == 0: FL.append((b, dd, r))
    rows.append((DAY(b), U(b), '%+d' % dd, '%d' % r['up'], '%d' % r['down'], NM[r['v']],
                 '%+.4f' % r['travel'], NM[r['tdir']], 'yes' if agree else '*** NO',
                 '%+.2f' % r['gap0'], '%.2f' % r['gspread'], '%.2f' % r['gstep'], og, ng))
box(('the measure', 'count'), [(kk, str(v)) for kk, v in sorted(c.items())])
n = c['consultations scored']
if n:
    box(('the headline', 'value'),
        [('consultations scored', str(n)),
         ('the vote disagrees with travel', '%d = %.1f%%'
          % (c['  the vote DISAGREES with travel'],
             100.0 * c['  the vote DISAGREES with travel'] / n)),
         ('the vote TIES — 4 UP vs 4 DOWN', '%d = %.1f%%' % (len(FL), 100.0 * len(FL) / n)),
         ('gate decisions the vote would change',
          '%d = %.1f%%' % (sum(v for kk, v in c.items() if kk.startswith('    gate ')
                               and kk.split(' -> ')[0].split()[-1] != kk.split(' -> ')[1]),
                           100.0 * sum(v for kk, v in c.items() if kk.startswith('    gate ')
                                       and kk.split(' -> ')[0].split()[-1]
                                       != kk.split(' -> ')[1]) / n))])
print('\n# EVERY CONSULTATION — the vote beside the travel verdict')
box(('day', 'ts', 'leg dr', 'UP', 'DOWN', 'the vote', 'travel', 'travel dir', 'agree?',
     'Mage-r at the bar', 'gap spread over the window', 'biggest gap step', 'gate today',
     'gate on the vote'), rows)
