"""WHAT C3's TIE-BREAK COST, PER TIE. 1009.

Joe 1009: *"show me the first 5 ties that C3 made worse"*.

C3 only acts when the 40-min vote ties, so every episode here is a tie. The comparison is run from
THE SAME LEG OPEN under both arms, so the chain's later divergence cannot contaminate it:

  arm TRAVEL  W_DGATE=vote W_VOTE_TIE=travel - the tie falls back to the old reading
  arm C3      W_DGATE=vote W_VOTE_TIE=c3     - Joe's ruling

A refusal opens a B-trade, so each arm is scored as A + B where a B exists, with the 0.11% per leg
boundary as its own column.
"""
import os, sys, importlib, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
BFLIPSUF = ('exhaustion', 'reversal on stalled', 'reversal on x-cross', 'squashed x-cross')

def load(tie):
    os.environ['W_DGATE'] = 'vote'; os.environ['W_VOTE_TIE'] = tie
    for m in ('_chain10', '_trajmech', '_chain_2day'):
        sys.modules.pop(m, None)
    return importlib.import_module('_chain10'), importlib.import_module('_chain_2day')

def rig(C, T):
    N = len(C.SC.ts); _i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
    def holds(m, w):
        run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
        h = run >= w; cf = h & ~np.r_[False, h[:-1]]
        return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
    T.XWOB = 18
    T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                       + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)],
                       key=lambda z: z[1])
    return N

def sc(C, k, xk, d):
    p0 = float(C.PX[k]); s = 1 if d > 0 else -1
    seg = np.asarray(C.PX[k:xk + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * s, np.nan)
    return (float(C.PX[xk]) - p0) / p0 * 100.0 * s, -float(np.nanmin(rel)), float(np.nanmax(rel))

def pair(C, k, d):
    """A from (k, d) plus B if A's exit opens a flip. -> dict"""
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: return None
    ar, amae, amfe = sc(C, k, xk, d)
    out = dict(axk=xk, awhy=why, ar=ar, amae=amae, amfe=amfe, bxk=None, bwhy=None, br=0.0, legs=1)
    if any(why.endswith(z) for z in BFLIPSUF):
        bb = C.run_leg(xk, -d)
        if bb[0] is not None:
            br, bmae, bmfe = sc(C, xk, bb[0], -d)
            out.update(bxk=bb[0], bwhy=bb[1], br=br, bmae=bmae, bmfe=bmfe, legs=2)
    return out

# ---- pass 1: walk the C3 arm and find every C3-attributable decision
C, T = load('c3'); N = rig(C, T)
SC, box, U = C.SC, C.box, C.SC.U
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
hits = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    for b, t in tr:
        if ('C3 broke the' in t) and (t.startswith('HANDOVER') or
                                      t.startswith('DELEGATION REFUSED')):
            hits.append(dict(open=k, d=d, bar=b, verdict='HANDOVER' if t.startswith('HANDOVER')
                             else 'REFUSED',
                             vote=t.split('C3 broke the ')[1].split(' tie')[0],
                             c3=t.split('traj ')[1].split(')')[0].split('.')[0].strip()))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
print('# %d C3-attributable gate decisions on the chain' % len(hits), flush=True)
resC3 = {(h['open'], h['d']): pair(C, h['open'], h['d']) for h in hits}

# ---- pass 2: the same leg opens under the travel tie-break
C2, T2 = load('travel'); rig(C2, T2)
resTR = {(h['open'], h['d']): pair(C2, h['open'], h['d']) for h in hits}

rows = []; tot = 0.0
for h in hits:
    key = (h['open'], h['d']); a, b = resTR[key], resC3[key]
    if a is None or b is None: continue
    na = a['ar'] + a['br'] - a['legs'] * 0.11
    nb = b['ar'] + b['br'] - b['legs'] * 0.11
    h['delta'] = nb - na; h['a'] = a; h['b'] = b; h['na'] = na; h['nb'] = nb
    tot += h['delta']
worse = sorted([h for h in hits if h.get('delta', 0) < 0], key=lambda z: z['open'])
print('# of them, %d made the pair WORSE, %d better, total delta %+.4f\n'
      % (len(worse), sum(1 for h in hits if h.get('delta', 0) > 0), tot), flush=True)
NSH = int(os.environ.get('X_N', 5))
for n, h in enumerate(worse[:NSH], 1):
    a, b = h['a'], h['b']
    print('\n########## TIE %d of %d — the leg opens %s %s, the dwell-ending is %s'
          % (n, len(worse), U(h['open']), 'LONG' if h['d'] > 0 else 'SHORT', U(h['bar'])))
    print('# the 40-min vote tied %s, and C3 read ws5-ws11 traj %s -> %s'
          % (h['vote'], h['c3'], h['verdict']))
    box(('the arm', 'the gate said', 'A closes', 'on what', 'A realised', 'A MAE', 'A MFE',
         'B opens', 'B closes', 'on what', 'B realised', 'legs', 'drag', 'NET'),
        [('tie-break TRAVEL', 'HANDOVER' if h['verdict'] == 'REFUSED' else 'REFUSED',
          U(a['axk']), a['awhy'], '%+.4f' % a['ar'], '%.4f' % a['amae'], '%.4f' % a['amfe'],
          U(a['axk']) if a['bxk'] else '—', U(a['bxk']) if a['bxk'] else '—',
          a['bwhy'] or '—', '%+.4f' % a['br'] if a['bxk'] else '—', str(a['legs']),
          '%.4f' % (a['legs'] * 0.11), '%+.4f' % h['na']),
         ('tie-break C3', h['verdict'],
          U(b['axk']), b['awhy'], '%+.4f' % b['ar'], '%.4f' % b['amae'], '%.4f' % b['amfe'],
          U(b['axk']) if b['bxk'] else '—', U(b['bxk']) if b['bxk'] else '—',
          b['bwhy'] or '—', '%+.4f' % b['br'] if b['bxk'] else '—', str(b['legs']),
          '%.4f' % (b['legs'] * 0.11), '%+.4f' % h['nb'])])
    print('- C3 cost this tie %+.4f' % h['delta'])
print('\n\n# EVERY C3-ATTRIBUTABLE TIE, the %d of them' % len(hits))
box(('day', 'the leg opens', 'dr', 'the dwell-ending', 'the vote tie', 'C3 read',
     'C3 said', 'NET with travel', 'NET with C3', 'delta'),
    [(DAY(h['open']), U(h['open']), '%+d' % h['d'], U(h['bar']), h['vote'], h['c3'],
      h['verdict'], '%+.4f' % h['na'], '%+.4f' % h['nb'], '%+.4f' % h['delta'])
     for h in sorted(hits, key=lambda z: z['open']) if 'delta' in h])
