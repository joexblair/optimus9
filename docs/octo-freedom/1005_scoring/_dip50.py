"""ws1Mage's 50 crossings after the ws12r gate, each with its dwell. Joe 1007:
*"what time do you see the dip, and what was it's dwell?"*

THE DIP, as my run took it: the first bar after the gate where ws1Mage crosses from >= 50 to < 50
at dr +1. Nothing in Joe's spec gave the dip a dwell, so my build gave it none - this file measures
what the dwell WOULD have been, for every crossing, so the right one can be named.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

D = os.environ.get('W_DAY', '2026-09-25')
DD = int(os.environ.get('W_DR', '1'))
A_TS = os.environ.get('W_FROM', '08:32:30')      # the gate bar from the mech run
B_TS = os.environ.get('W_TO', '09:30:00')
OPEN_TS = os.environ.get('W_OPEN', '08:10:00')
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
k0 = K(OPEN_TS); p0 = float(PX[k0])
pct = lambda k: (float(PX[k]) - p0) / p0 * 100.0 * (1 if DD > 0 else -1)
mn = lambda k: (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))

a, b = K(A_TS), K(B_TS)
below = lambda k: float(G1[k]) < 50.0
# the dip side: at dr +1 the dip is BELOW 50, inverted at dr -1
indip = below if DD > 0 else (lambda k: float(G1[k]) > 50.0)

print('# EVERY ws1Mage CROSSING OF 50 FROM %s TO %s  (leg d %+d, dip is %s 50)'
      % (A_TS, B_TS, DD, 'under' if DD > 0 else 'over'))
rows = []
for k in range(a + 1, b + 1):
    if indip(k) == indip(k - 1): continue
    # the run that starts at k, on whichever side k lands
    n = 0
    while k + n <= N - 1 and indip(k + n) == indip(k):
        n += 1
    rows.append((SC.U(k), '%+.1f' % mn(k), '%.2f' % float(G1[k - 1]), '%.2f' % float(G1[k]),
                 ('INTO the dip' if indip(k) else 'out of the dip'),
                 str(n), '%.1f' % (n * 5 / 60.0), '%.6f' % float(PX[k]), '%+.4f' % pct(k)))
box(('ts', '+min from open', 'ws1Mage prev', 'ws1Mage', 'direction', 'run bars', 'run min',
     'pxs', 'pct'), rows or [('—',) * 9])

print('\n# ws1Mage PER 15 s ACROSS THE DIP MY RUN TOOK (08:49:00 to 08:52:00)')
box(('ts', '+min from open', 'ws1Mage', 'below 50?', 'pxs', 'pct'),
    [(SC.U(k), '%+.1f' % mn(k), '%.2f' % float(G1[k]), 'Y' if float(G1[k]) < 50.0 else '-',
      '%.6f' % float(PX[k]), '%+.4f' % pct(k))
     for k in range(K('08:49:00'), K('08:52:00') + 1, 3)])

print('\n# ws1Mage PER MINUTE, THE GATE TO THE PIVOT')
box(('ts', '+min from open', 'ws1Mage', 'vs 50', 'pxs', 'pct'),
    [(SC.U(k), '%+.1f' % mn(k), '%.2f' % float(G1[k]),
      'below' if float(G1[k]) < 50.0 else 'above', '%.6f' % float(PX[k]), '%+.4f' % pct(k))
     for k in range(a, b + 1, 12)])
