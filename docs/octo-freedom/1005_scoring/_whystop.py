"""WHY DOES LINEAGE STOP SO SOON? 1009.

Joe 1009: *"the real question is, why is lineage stopping so soon?"* and, before it, *"lineage
stops too soon, because it can't see the higher momentum that would tell lineage to keep walking"*.

The walk ends at the bar where BOTH hold: the rider is stalled, AND no TF in
`range(rider+1, min(rider+LIN_HOP, ceil)+1)` is oob. So at every `final stalled` exit there are
exactly three ways a higher line could have carried it and did not:

  REACHABLE      a TF inside lin_hop was oob - cannot happen, the baton would have taken it. Counted
                 as a correctness check on this diagnostic.
  BEYOND LIN_HOP oob, above the rider, at or under the ceiling, but more than `lin_hop` TFs up
  ABOVE CEILING  oob and above `ceil` - including ws45/60/90/120, which the walk can NEVER reach

and a fourth that is not about oob at all:

  TRENDING ONLY  not oob, but its own `traj` points WITH the leg. The candidate test reads oob
                 position only, so a hard-trending line that is mid-board is invisible.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
from _trajmech import traj

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
HI, LO = SC.HI, SC.LO
EXTRA = [45, 60, 90, 120]
RL = {}
for t in list(C.ALL_TF) + EXTRA:
    try: RL[t] = np.asarray(SC.LD(t * 60, 'r'), float)[:N]
    except Exception: pass
TFS = sorted(RL)
print('# lines: %s  |  ceil_hi %d, lin_hop %d, baton pass on %r'
      % (', '.join('ws%d' % t for t in TFS), C.CEIL_HI, C.LIN_HOP, C.PASS), flush=True)
BLK, TAIL, LOOK, KIND = C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND
oob = lambda t, j, d: (float(RL[t][j]) >= HI) if d > 0 else (float(RL[t][j]) <= LO)
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
    # THE ACTIVE CEILING IS DYNAMIC. `ceil` starts at BASE_HI and only rises to CEIL_HI when the
    # CEILING line prints. Using CEIL_HI for every leg was a defect in the first pass: it counted
    # ws13/ws14 as reachable on legs whose ceiling was still 12, which produced 7 impossible
    # 'REACHABLE inside lin_hop and oob' rows.
    rider = None; aceil = C.BASE_HI
    for j, t in tr:
        if t.startswith('KICKSTART'): rider = int(t.split('rider ws')[1].split(' ')[0])
        elif t.startswith('baton -> ws'): rider = int(t.split('baton -> ws')[1].split(' ')[0])
        elif 'CEILING' in t: aceil = C.CEIL_HI
    p0 = float(PX[k]); s = 1 if d > 0 else -1
    legs.append(dict(k=k, xk=xk, d=d, why=why, rider=rider, aceil=aceil,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * s))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
for i, L in enumerate(legs):
    L['next_breach'] = bool(i + 1 < len(legs) and legs[i + 1]['why'] == 'mae breach'
                            and legs[i + 1]['k'] == L['xk'])
fs = [L for L in legs if L['why'] == 'final stalled' and L['rider'] is not None]
print('# %d legs, %d exited on `final stalled` with a known rider, %d of those hand straight into '
      'a mae breach\n' % (len(legs), len(fs), sum(1 for L in fs if L['next_breach'])), flush=True)

def diag(L):
    j, d_, r, ac = L['xk'], L['d'], L['rider'], L['aceil']
    cap = min(r + C.LIN_HOP, ac)
    reach = [t for t in TFS if r < t <= cap and oob(t, j, d_)]
    beyond = [t for t in TFS if cap < t <= ac and oob(t, j, d_)]
    above = [t for t in TFS if t > ac and oob(t, j, d_)]
    trend = [t for t in TFS if t > r and not oob(t, j, d_)
             and traj(RL[t], j, BLK, TAIL, LOOK, KIND, 0)['dir'] == d_]
    return reach, beyond, above, trend

for nm, sel in (('EVERY `final stalled` EXIT', fs),
                ('THE ONES THAT HAND STRAIGHT INTO A BREACH', [L for L in fs if L['next_breach']])):
    if not sel: continue
    D = [diag(L) for L in sel]
    n = len(sel)
    print('\n# %s — %d legs' % (nm, n))
    box(('what a higher line was doing at the exit bar', 'legs', '% of them'),
        [('REACHABLE inside lin_hop and oob — must be 0',
          str(sum(1 for z in D if z[0])), '%.1f%%' % (100.0 * sum(1 for z in D if z[0]) / n)),
         ('BEYOND LIN_HOP — oob, above the rider, at or under the active ceiling',
          str(sum(1 for z in D if z[1])), '%.1f%%' % (100.0 * sum(1 for z in D if z[1]) / n)),
         ('ABOVE THE ACTIVE CEILING — oob and above it, unreachable by design',
          str(sum(1 for z in D if z[2])), '%.1f%%' % (100.0 * sum(1 for z in D if z[2]) / n)),
         ('either unreachable-oob case', str(sum(1 for z in D if z[1] or z[2])),
          '%.1f%%' % (100.0 * sum(1 for z in D if z[1] or z[2]) / n)),
         ('TRENDING ONLY — not oob, but its traj points WITH the leg',
          str(sum(1 for z in D if z[3])), '%.1f%%' % (100.0 * sum(1 for z in D if z[3]) / n)),
         ('NOTHING above the rider was oob or trending with it',
          str(sum(1 for z in D if not (z[1] or z[2] or z[3]))),
          '%.1f%%' % (100.0 * sum(1 for z in D if not (z[1] or z[2] or z[3])) / n)),
         ('the rider was ALREADY at its active ceiling',
          str(sum(1 for L in sel if L['rider'] >= L['aceil'])),
          '%.1f%%' % (100.0 * sum(1 for L in sel if L['rider'] >= L['aceil']) / n)),
         ('the active ceiling was still ws%d — ws13-ws23 unreachable too' % C.BASE_HI,
          str(sum(1 for L in sel if L['aceil'] == C.BASE_HI)),
          '%.1f%%' % (100.0 * sum(1 for L in sel if L['aceil'] == C.BASE_HI) / n))])
    rc = collections.Counter(L['rider'] for L in sel)
    box(('the rider it died on', 'legs', '% of them'),
        [('ws%d' % t, str(rc[t]), '%.1f%%' % (100.0 * rc[t] / n)) for t in sorted(rc)])
    ab = collections.Counter()
    for z in D:
        for t in z[2]: ab['ws%d' % t] += 1
    if ab:
        box(('the oob line above the ceiling', 'legs it was oob on', '% of them'),
            [(kk, str(v), '%.1f%%' % (100.0 * v / n)) for kk, v in sorted(ab.items(),
             key=lambda z: -z[1])])
