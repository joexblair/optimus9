"""THE TWO POPULATIONS FOR A's CLOSE. 1009.

  READING a  the squashed walk x-cross closes A whenever it fires INSIDE a ws12r oob run. Causal
             at the cross bar - Joe's stamp - because nothing about the run's future is read.
  READING b  A closes only when the oob run then ENDS SHORT of the dwell. Joe's rule as worded,
             but knowable one bar after the run ends, not at the cross.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

assert C.NOX and C.TRACE_NOX, 'run with W_NOX=1 W_TRACE_NOX=1'
SC, box, U = C.SC, C.box, C.SC.U
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

c = collections.Counter(); A = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    c['legs'] += 1
    hit = None; short = False
    for b, t in tr:
        if hit is None and t.startswith('x-cross SQUASHED') and 'inside the ws' in t:
            hit = (b, t.split(' on ws')[1].split(' ')[0])
        if t.startswith('THE RUN ENDED SHORT') and 'a SQUASHED x-cross fired' in t:
            short = True
    if hit is not None:
        c['READING a — a squashed x-cross fired inside an oob run'] += 1
        A.append((DAY(hit[0]), U(hit[0]), 'LONG' if d > 0 else 'SHORT', hit[1],
                  'yes' if short else 'no', U(xk), why))
    if short:
        c['READING b — and that run then ended short of the dwell'] += 1
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

print('# A-TRADES CLOSED EARLY, by reading — %d legs on the chain' % c['legs'])
box(('the reading', 'A-trades it closes', 'of %d legs' % c['legs']),
    [('a  the squashed x-cross fires inside a ws12r oob run',
      str(c['READING a — a squashed x-cross fired inside an oob run']),
      '%.1f%%' % (100.0 * c['READING a — a squashed x-cross fired inside an oob run'] / c['legs'])),
     ('b  ...and that run then ended short of the dwell',
      str(c['READING b — and that run then ended short of the dwell']),
      '%.1f%%' % (100.0 * c['READING b — and that run then ended short of the dwell'] / c['legs']))])
print('\n# READING a — every A-trade it closes, %d rows' % len(A))
box(('day', 'the squashed x-cross / A closes', 'A\'s side', 'rider', 'did its run end short?',
     'where A exits with no rule', 'on what'), A)
