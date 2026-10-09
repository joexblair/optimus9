"""HOW LONG DOES A B-TRADE RUN BEFORE ITS LINEAGE WALK ARMS? 1009.

Joe 1009 on 07-15 09:36:15: *"should have closed by lineage at 09:56, ws4 last rider"*. It could not
- the walk was not armed until 10:28:15, 52.0 min after B opened, because `exit-armed` needs
ws2Mage to cross into oob. Until then the walk has no rider and no exit, so the leg's only floor is
`mae_stop_pct` 2.50.

This sizes that across every B-trade on the chain.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
os.environ['W_DGATE'] = 'vote'; os.environ['W_VOTE_TIE'] = 'c3'
import _chain10 as C, _chain_2day as T
SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
BFLIPSUF = ('exhaustion', 'reversal on stalled', 'reversal on x-cross', 'squashed x-cross')
legs = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    arm = next((j for j, t in tr if t.startswith('exit-armed')), None)
    kick = next((j for j, t in tr if t.startswith('KICKSTART')), None)
    p0 = float(PX[k]); s = 1 if d > 0 else -1
    seg = np.asarray(PX[k:xk + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * s, np.nan)
    legs.append(dict(k=k, xk=xk, d=d, why=why, arm=arm, kick=kick,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * s,
                     mae=-float(np.nanmin(rel)), mfe=float(np.nanmax(rel)),
                     opensB=any(why.endswith(z) for z in BFLIPSUF)))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
for i, L in enumerate(legs):
    L['isB'] = bool(i and legs[i - 1]['opensB'] and L['k'] == legs[i - 1]['xk'])
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
for lbl, sel in (('B-TRADES', [L for L in legs if L['isB']]),
                 ('every other leg', [L for L in legs if not L['isB']])):
    if not sel: continue
    dl = [mn(L['k'], L['arm']) for L in sel if L['arm'] is not None]
    na = [L for L in sel if L['arm'] is None]
    A = np.array(dl, float) if dl else np.zeros(0)
    print('\n# %s — %d legs' % (lbl, len(sel)))
    box(('the measure', 'value'),
        [('legs whose walk NEVER armed before the exit',
          '%d = %.1f%%' % (len(na), 100.0 * len(na) / len(sel))),
         ('legs whose walk armed', str(len(dl))),
         ('minutes from the open to exit-armed — median', '%.1f' % float(np.median(A)) if len(A) else '—'),
         ('  75th pct', '%.1f' % float(np.percentile(A, 75)) if len(A) else '—'),
         ('  90th pct', '%.1f' % float(np.percentile(A, 90)) if len(A) else '—'),
         ('  max', '%.1f' % float(A.max()) if len(A) else '—'),
         ('armed within 5 min', '%d = %.1f%%' % (int((A <= 5).sum()), 100.0 * (A <= 5).sum() / len(sel)) if len(A) else '—'),
         ('armed later than 30 min', '%d = %.1f%%' % (int((A > 30).sum()), 100.0 * (A > 30).sum() / len(sel)) if len(A) else '—'),
         ('summed realised, never-armed legs', '%+.4f' % sum(L['real'] for L in na)),
         ('of them, exited on mae breach',
          '%d of %d' % (sum(1 for L in na if L['why'] == 'mae breach'), len(na)))])
BS = [L for L in legs if L['isB']]
nab = [L for L in BS if L['arm'] is None]
print('\n# THE B-TRADES WHOSE WALK NEVER ARMED — every one')
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
box(('day', 'B opens', 'side', 'B closes', 'held min', 'on what', 'realised', 'MAE', 'MFE'),
    [(DAY(L['k']), U(L['k']), 'LONG' if L['d'] > 0 else 'SHORT', U(L['xk']),
      '%.1f' % mn(L['k'], L['xk']), L['why'], '%+.4f' % L['real'], '%.4f' % L['mae'],
      '%.4f' % L['mfe']) for L in nab])
