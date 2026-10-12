"""THREE 07-15 STALLS, WITH EVERY LINE ABOVE THE RIDER AT THE EXIT BAR. 1009.

Joe 1009: *"show me 3 example in 07-15"* - for the finding that the walk reads oob POSITION and
never direction, which bound on 326 of 326 `final stalled` exits.

Per stall: the leg, the rider it died on, its active ceiling, and then EVERY line above the rider
with its r value, whether it was oob, its own `traj` direction, and whether the walk could have
reached it. The last column is the whole point: a line can be trending hard WITH the leg and still
not be a candidate, because `cand` tests `oobf` only.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
from _trajmech import traj
from optimus9.compute.momo_config import momo_config, momo_bank
from optimus9.compute.momo_gated import momo_window, momo_g, momo_g_why

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts); HI, LO = SC.HI, SC.LO
EXTRA = [45, 60, 90, 120]
RL = {}
for t in list(C.ALL_TF) + EXTRA:
    try: RL[t] = np.asarray(SC.LD(t * 60, 'r'), float)[:N]
    except Exception: pass
TFS = sorted(RL)
BLK, TAIL, LOOK, KIND = C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND
# THE MOMENTUM STATE, PER LINE. Joe 1009: *"we need the momentum state printed in a column
# alongside traj / lineage relies on momentum"*. mom-true is `momo` OR `curl` via momo_g - Joe's
# 0805 curl gates ON, strip_mom_at_fence OFF. Called PER BAR inside each TF's own bank and window,
# not as a full-tape mask: 26 lines x 3 stall bars is 78 calls, a mask would be 26 tape walks.
_db = C.db if getattr(C, 'db', None) is not None else None
if _db is None:
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.config import get_db_config
    _db = DatabaseManager(**get_db_config())
_db.connect()
BANKS = {}
for t in TFS:
    try:
        BANKS[t] = momo_bank(_db, t)
    except Exception as e:
        BANKS[t] = None
        print('# ws%d has NO momo_config bank: %s' % (t, str(e)[:90]), flush=True)
try:
    _db.disconnect()
except Exception:
    pass
print('# banks: %s  |  NO BANK: %s'
      % (', '.join('ws%d(kw %d)' % (t, int(BANKS[t]['k_window'])) for t in TFS if BANKS[t]),
         ', '.join('ws%d' % t for t in TFS if not BANKS[t]) or 'none'), flush=True)
MOMNM = {'momo': 'momo', 'curl': 'curl', 'sideways': 'sideways', 'none': 'none'}

def momstate(t, j, d):
    """(the verdict, is it mom-true, the slope, the reason when it is not) at ONE bar."""
    bk = BANKS.get(t)
    if bk is None: return ('no bank', False, float('nan'), 'ws%d has no momo_config band' % t)
    with momo_config(bk):
        with momo_window(int(bk['k_window']) * int(t)):
            st, why, f = momo_g_why(RL[t], d, j)
    return (st, st in ('momo', 'curl'), f.get('slope', float('nan')), why)
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
DAYW = os.environ.get('X_DAY', '2026-07-15')
hits = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    rider = None; aceil = C.BASE_HI
    for j, t in tr:
        if t.startswith('KICKSTART'): rider = int(t.split('rider ws')[1].split(' ')[0])
        elif t.startswith('baton -> ws'): rider = int(t.split('baton -> ws')[1].split(' ')[0])
        elif 'CEILING' in t: aceil = C.CEIL_HI
    if why == 'final stalled' and rider is not None and DAY(xk) == DAYW:
        hits.append(dict(k=k, xk=xk, d=d, rider=rider, aceil=aceil, tr=list(tr)))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
print('# %d `final stalled` exits on %s\n' % (len(hits), DAYW), flush=True)
NM = {1: 'UP +1', -1: 'DOWN -1', 0: 'FLAT 0'}
for n, L in enumerate(hits[:int(os.environ.get('X_N', 3))], 1):
    j, d_, r, ac = L['xk'], L['d'], L['rider'], L['aceil']
    cap = min(r + C.LIN_HOP, ac)
    p0 = float(PX[L['k']]); s = 1 if d_ > 0 else -1
    print('\n########## STALL %d — the leg opens %s %s, stalls %s on ws%d   |   realised %+.4f'
          % (n, U(L['k']), 'LONG' if d_ > 0 else 'SHORT', U(j), r,
             (float(PX[j]) - p0) / p0 * 100.0 * s))
    print('# the active ceiling is ws%d, lin_hop %d, so the baton could only reach ws%d..ws%d'
          % (ac, C.LIN_HOP, r + 1, cap) if cap > r else
          '# the active ceiling is ws%d and the rider is ws%d — the baton had NOWHERE to go' % (ac, r))
    box(('ts', 'event'), [(U(b), t) for b, t in sorted(L['tr'])])
    rows = []
    for t in TFS:
        if t <= r: continue
        o = oob(t, j, d_)
        tj = traj(RL[t], j, BLK, TAIL, LOOK, KIND, 0)['dir']
        where = ('inside lin_hop' if t <= cap else
                 ('above lin_hop, under the ceiling' if t <= ac else 'ABOVE THE CEILING'))
        cand = 'YES' if (o and t <= cap) else 'no'
        st, mt, sl, why = momstate(t, j, d_)
        rows.append(('ws%dr' % t, '%.2f' % float(RL[t][j]), 'YES' if o else 'no', NM[tj],
                     'WITH' if tj == d_ else ('against' if tj == -d_ else 'flat'),
                     st, 'YES' if mt else 'no',
                     '%+.3f' % sl if sl == sl else '—',
                     where, cand))
    box(('the line', 'r at the stall bar', 'oob?', 'its traj', 'traj vs the leg side',
         'momentum verdict', 'MOM-TRUE?', 'momo slope', 'reachable?',
         'was it a baton candidate?'), rows)
    wt = [x for x in rows if x[4] == 'WITH']
    mt = [x for x in rows if x[6] == 'YES']
    both = [x for x in rows if x[4] == 'WITH' and x[6] == 'YES']
    box(('the count for this stall', 'value'),
        [('lines above ws%d' % r, str(len(rows))),
         ('of them oob — the ONLY thing the baton test reads', str(sum(1 for x in rows if x[2] == 'YES'))),
         ('of them trending WITH the leg', str(len(wt))),
         ('of them MOM-TRUE (momo or curl)', str(len(mt))),
         ('MOM-TRUE **and** trending WITH the leg', '**%d**' % len(both)),
         ('of those, NOT a baton candidate', '**%d**' % sum(1 for x in both if x[9] == 'no')),
         ('the highest MOM-TRUE line trending WITH the leg', both[-1][0] if both else 'none'),
         ('the momentum verdicts seen above the rider',
          ', '.join('%s x%d' % (v, sum(1 for x in rows if x[5] == v))
                    for v in sorted({x[5] for x in rows})))])
