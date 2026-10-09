"""THE VOTE+C3 GATE AGAINST THE travel GATE, ON THE WHOLE CHAIN. 1009.

Joe 1009: *"maybe C3 is all we need - 1 miss out of 8 isn't trivial"* / *"we landed here because of
a tie in our test walk. let's apply C3 and recreate the tests"*.

W_DGATE=traj  the direction is `travel` over the reversal-truncated tail.
W_DGATE=vote  the 40-min UP/DOWN count on ws60r, C3 (ws5-ws11 traj majority) breaks a tie, and
              `travel` decides only if C3 ties too.

Both legs of the comparison run W_NOX=1 and W_SQX=1 so the only difference is the gate.
"""
import os, sys, importlib, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')

def walk(mode):
    os.environ['W_DGATE'] = mode
    for m in ('_chain10', '_trajmech', '_chain_2day'):
        sys.modules.pop(m, None)
    C = importlib.import_module('_chain10')
    T = importlib.import_module('_chain_2day')
    N = len(C.SC.ts); _i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
    def holds(m, w):
        run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
        h = run >= w; cf = h & ~np.r_[False, h[:-1]]
        return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
    T.XWOB = 18
    T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                       + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)],
                       key=lambda z: z[1])
    legs = []; dec = []
    k, d, g = 1, +1, 0
    while True:
        g += 1
        if g > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        p0 = float(C.PX[k]); sg = 1 if d > 0 else 0
        sg = 1 if d > 0 else -1
        legs.append((k, xk, d, why, (float(C.PX[xk]) - p0) / p0 * 100.0 * sg))
        for b, t in tr:
            if t.startswith('HANDOVER'):
                dec.append((b, d, 'HANDOVER', t))
            elif t.startswith('DELEGATION REFUSED'):
                dec.append((b, d, 'REFUSED', t))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    return C, legs, dec

OUT = {}
for mode in ('traj', 'vote'):
    C, legs, dec = walk(mode)
    OUT[mode] = (legs, dec)
    gross = sum(l[4] for l in legs)
    print('# W_DGATE=%-4s  legs %d  gross %+.4f  drag %.4f  NET %+.4f  decisions %d'
          % (mode, len(legs), gross, len(legs) * 0.11, gross - len(legs) * 0.11, len(dec)),
          flush=True)
SC, box, U = C.SC, C.box, C.SC.U
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
A, B = OUT['traj'], OUT['vote']
box(('the measure', 'W_DGATE=traj', 'W_DGATE=vote'),
    [('legs', str(len(A[0])), str(len(B[0]))),
     ('gross', '%+.4f' % sum(l[4] for l in A[0]), '%+.4f' % sum(l[4] for l in B[0])),
     ('drag', '%.4f' % (len(A[0]) * 0.11), '%.4f' % (len(B[0]) * 0.11)),
     ('NET AFTER DRAG', '%+.4f' % (sum(l[4] for l in A[0]) - len(A[0]) * 0.11),
      '%+.4f' % (sum(l[4] for l in B[0]) - len(B[0]) * 0.11)),
     ('gate decisions', str(len(A[1])), str(len(B[1])))])
ea = collections.Counter(l[3] for l in A[0]); eb = collections.Counter(l[3] for l in B[0])
box(('the exit', 'traj', 'vote', 'change'),
    [(w, str(ea.get(w, 0)), str(eb.get(w, 0)), '%+d' % (eb.get(w, 0) - ea.get(w, 0)))
     for w in sorted(set(ea) | set(eb))])
da = {(b, d): k for b, d, k, _ in A[1]}; db = {(b, d): k for b, d, k, _ in B[1]}
both = sorted(set(da) & set(db))
flip = [(b, d) for b, d in both if da[(b, d)] != db[(b, d)]]
box(('the gate decisions', 'count'),
    [('bars decided by BOTH gates', str(len(both))),
     ('of those, the SAME verdict', str(len(both) - len(flip))),
     ('of those, FLIPPED', '%d = %.1f%%' % (len(flip), 100.0 * len(flip) / len(both)) if both else '0'),
     ('bars only traj decided', str(len(set(da) - set(db)))),
     ('bars only vote decided', str(len(set(db) - set(da))))])
if flip:
    srcB = {(b, d): t for b, d, k, t in B[1]}
    print('\n# EVERY FLIPPED DECISION — what the vote gate said instead')
    box(('day', 'the bar', 'dr', 'traj said', 'vote said', 'the vote gate\'s own reason'),
        [(DAY(b), U(b), '%+d' % d, da[(b, d)], db[(b, d)],
          srcB[(b, d)].split('(gate OPEN — ')[-1].rstrip(')')
          if 'gate OPEN' in srcB[(b, d)] else srcB[(b, d)].split('— ')[-1][:120])
         for b, d in flip])
