"""JOE'S 1009 RULE, COUNTED: A SQUASHED WALK x-CROSS INSIDE AN OOB RUN THAT ENDED SHORT.

Joe 1009: *"if oob ended before dwell completed, and a x-cross was squashed during the oob, then a
B-trade is created and the A-trade is closed"*, and *"squashed was my shorthand - I was refering to
the x-cross that we disabled 2 or 3 turns back"* - the LINEAGE WALK's x-cross exit, suppressed by
W_NOX=1 at _chain10:508. Not the ws12x/ws12r cross.

Walked on the real chain, so the rider the x-cross is tested on is the chain's own baton. The
population is every ws12r oob run a leg met.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

assert C.NOX and C.TRACE_NOX, 'run with W_NOX=1 W_TRACE_NOX=1'
SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
_idx = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])

c = collections.Counter(); fires = []; sq = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    c['legs'] += 1; c['exit: ' + why] += 1
    for b, t in tr:
        if t.startswith('x-cross SQUASHED'):
            c['squashed x-crosses recorded'] += 1
            sq.append((DAY(b), U(b), 'LONG' if d > 0 else 'SHORT',
                       t.split('ws')[1].split(' ')[0],
                       'yes' if 'inside the ws' in t else 'no'))
        elif t.startswith('THE RUN ENDED SHORT'):
            c['oob runs that ended short of the dwell'] += 1
            if 'a SQUASHED x-cross fired' in t:
                c['  THE RULE FIRES — a squashed x-cross was in it'] += 1
                fires.append((DAY(b), U(b), 'LONG' if d > 0 else 'SHORT',
                              t.split(' at ')[1].split(' on ')[0],
                              t.split(' on ws')[1].split(' ')[0],
                              'EDGE' if 'an EDGE' in t else 'already standing', U(xk), why))
                c['    of them, the cross was an EDGE' if 'an EDGE' in t
                  else '    of them, the cross was ALREADY STANDING'] += 1
            else:
                c['  no squashed x-cross in it — the rule does not fire'] += 1
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

print('# THE CHAIN, %d bars, W_NOX=1 (the walk x-cross is suppressed)' % N)
box(('the measure', 'count'), [(kk, str(v)) for kk, v in sorted(c.items())])
tot = c['oob runs that ended short of the dwell']
if tot:
    print('\n# THE RULE\'S RATE')
    box(('the measure', 'value'),
        [('oob runs that ended short of the dwell', str(tot)),
         ('of them, a squashed x-cross fired inside',
          '%d = %.1f%%' % (len(fires), 100.0 * len(fires) / tot)),
         ('new B-trades the rule creates', '**%d**' % len(fires))])
if fires:
    print('\n# EVERY FIRING — the bar the oob run ended is the bar A closes and B opens')
    box(('day', 'the run ends / B opens', 'A\'s side', 'the squashed x-cross', 'its rider',
         'edge or standing', 'where A actually exits today', 'on what'), fires)
    seen = set(); firstper = []
    for r in fires:
        kk = (r[0], r[6], r[7])
        if kk in seen: continue
        seen.add(kk); firstper.append(r)
    print('\n# THE FIRST FIRING PER A-TRADE — %d of the %d. A closes on the first one, so every '
          'later firing in the same leg is a path the rule never takes.' % (len(firstper), len(fires)))
    box(('day', 'the run ends / B opens', 'A\'s side', 'the squashed x-cross', 'its rider',
         'edge or standing', 'where A actually exits today', 'on what'), firstper)
if sq:
    print('\n# EVERY SQUASHED x-CROSS, %d rows — the walk would have exited on each with W_NOX=0'
          % len(sq))
    box(('day', 'ts', 'side', 'rider', 'inside a ws12r oob run?'), sq)
