"""DID THE BREACH LEGS OPEN AGAINST A CLUSTER OF HTF MOMENTUM? 1009.

Joe 1009: *"the issue is that lineage stops too soon, because it can't see the higher momentum that
would tell lineage to keep walking. the MAE issue is not in the trade that attacts the stop, the
MAE issue starts when the incoming leg stops prematurely"* / *"how many of those trade opens fired
against a cluster of HTF lines that are printing momentum AGAINST the trade side"* / *"HTF: go all
the way to 90 (and occasionally I saw 120 as the momentum holder)"*.

MOMENTUM = each HTF r line's own `traj` direction, the mech Joe validated at 7 of 8 as C3. AGAINST
means traj dir == -d, the opposite of the leg's side.

THE BASELINE IS THE POINT. A count of HTF lines against, with no comparison, cannot say whether the
breach opens are unusual. Every leg is measured and the breaches are compared to the rest.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
from _trajmech import traj

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
HTF = [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 45, 60, 90, 120]
LINE = {}
for t in HTF:
    try:
        LINE[t] = np.asarray(SC.LD(t * 60, 'r'), float)[:N]
    except Exception as e:
        print('# ws%dr did not load: %r' % (t, e), flush=True)
HTF = [t for t in HTF if t in LINE]
print('# HTF r lines loaded: %s' % ', '.join('ws%d' % t for t in HTF), flush=True)
BLK, TAIL, LOOK, KIND = C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
legs = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); s = 1 if d > 0 else -1
    dirs = {t: traj(LINE[t], k, BLK, TAIL, LOOK, KIND, 0)['dir'] for t in HTF}
    legs.append(dict(k=k, xk=xk, d=d, why=why, dirs=dirs,
                     arm=next((j for j, t in tr if t.startswith('exit-armed')), None),
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * s))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
br = [L for L in legs if L['why'] == 'mae breach']
ot = [L for L in legs if L['why'] != 'mae breach']
print('# %d legs: %d mae breaches, %d other\n' % (len(legs), len(br), len(ot)), flush=True)

print('# EACH HTF LINE ON ITS OWN — how often its traj was AGAINST the leg side at the OPEN bar')
rows = []
for t in HTF:
    ab = sum(1 for L in br if L['dirs'][t] == -L['d'])
    wb = sum(1 for L in br if L['dirs'][t] == L['d'])
    fb = sum(1 for L in br if L['dirs'][t] == 0)
    ao = sum(1 for L in ot if L['dirs'][t] == -L['d'])
    rows.append(('ws%dr' % t, '%d/%d' % (ab, len(br)), '%.1f%%' % (100.0 * ab / len(br)),
                 '%d/%d' % (ao, len(ot)), '%.1f%%' % (100.0 * ao / len(ot)),
                 '%+.1f' % (100.0 * ab / len(br) - 100.0 * ao / len(ot)),
                 str(wb), str(fb)))
box(('the line', 'AGAINST on breaches', '%', 'AGAINST on every other leg', '%',
     'the gap in points', 'WITH on breaches', 'flat on breaches'), rows)

def cnt(L, band):
    return sum(1 for t in band if L['dirs'][t] == -L['d'])
BANDS = (('ws13-ws23', [t for t in HTF if 13 <= t <= 23]),
         ('ws45-ws120 — the four Joe named', [t for t in HTF if t >= 45]),
         ('ws13-ws90', [t for t in HTF if 13 <= t <= 90]),
         ('every HTF line ws13-ws120', HTF))
print('\n# THE CLUSTER — how many of the band were AGAINST, breaches vs the rest')
rows = []
for nm, band in BANDS:
    if not band: continue
    nb = np.array([cnt(L, band) for L in br], float)
    no = np.array([cnt(L, band) for L in ot], float)
    n = len(band)
    rows.append((nm, str(n),
                 '%.1f' % nb.mean(), '%.1f' % no.mean(),
                 '%.0f%%' % (100.0 * nb.mean() / n), '%.0f%%' % (100.0 * no.mean() / n),
                 '%d = %.1f%%' % (int((nb == n).sum()), 100.0 * (nb == n).sum() / len(br)),
                 '%.1f%%' % (100.0 * (no == n).sum() / len(ot)),
                 '%d = %.1f%%' % (int((nb >= n * 0.8).sum()), 100.0 * (nb >= n * 0.8).sum() / len(br)),
                 '%.1f%%' % (100.0 * (no >= n * 0.8).sum() / len(ot))))
box(('the band', 'lines in it', 'mean AGAINST on breaches', 'mean on the rest',
     'as a share, breaches', 'the rest', 'ALL against, breaches', 'ALL against, the rest',
     '80%+ against, breaches', '80%+ against, the rest'), rows)

print('\n# THE FULL DISTRIBUTION — ws13-ws120, %d lines' % len(HTF))
cb = collections.Counter(cnt(L, HTF) for L in br)
co = collections.Counter(cnt(L, HTF) for L in ot)
box(('HTF lines AGAINST at the open', 'breaches', '% of breaches', 'every other leg', '% of them'),
    [(str(i), str(cb.get(i, 0)), '%.1f%%' % (100.0 * cb.get(i, 0) / len(br)),
      str(co.get(i, 0)), '%.1f%%' % (100.0 * co.get(i, 0) / len(ot)))
     for i in range(len(HTF) + 1)])
