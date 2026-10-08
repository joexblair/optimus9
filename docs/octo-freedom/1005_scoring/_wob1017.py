"""THE TURN DETECTOR AT 10:17 — WHICH wob MAKES 10:21 THE TURN. 09-25. 1008.

Joe 1008: *"this is why I called out the direction of pxs - it can only go down to satisfy a LONG
entry, but a r line that doesn't reach the bottom is weak, and weak lets pxs climb"*.

So the landing is the TURN, and `a r line that doesn't reach the bottom` is why waiting past the
turn costs entry: weak travel lets pxs climb back. ws1r bottomed at 19.95, 4.95 above the 15 fence.

THE ONE THING STILL UNFIXED is which turn. `_mage_rev(ws1r, rrev_wob 2)` fires 23 times in the 8
minutes after 10:17:05, 12 of them UP, the first at 10:17:10. Joe reads ONE turn, at 10:21.

MEASURED HERE: for each `rrev_wob`, the first UP turn of ws1r after 10:17:05, the LONG entry it
gives, and the total number of UP turns it fires in the 8 min window. Reported to find a KNEE, not
to hand over a sweep.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
R = C.R
N = len(SC.ts); U = SC.U
LO = SC.LO
K0 = SC.K('2026-09-25 10:17:05')
K2 = SC.K('2026-09-25 10:25:00')
P0 = float(PX[K0])
R1 = R[1]
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[K0])) / 60000.0)
imp = lambda j: (P0 - float(PX[j])) / P0 * 100.0

print('\n# 10:17:05  pxs %.6f  LONG. ws1r minimum 19.95 at 10:20:05, %.2f above the %d fence.'
      % (P0, 19.95 - LO, LO))
print('# Joe\'s turn is 10:21. rrev_wob as banked in ws12_baton_config is %d.'
      % int(C.W['rrev_wob']))

rows = []
for wob in list(range(2, 41)):
    rv = _mage_rev(R1, wob)
    first = next((j for j in range(K0, N) if int(rv[j]) > 0), None)
    nup = sum(1 for j in range(K0, K2 + 1) if int(rv[j]) > 0)
    rows.append(dict(wob=wob, first=first, nup=nup,
                     imp=imp(first) if first else float('nan')))

print('\n# THE FIRST UP TURN OF ws1r AFTER 10:17:05, BY rrev_wob')
box(('rrev_wob', 'bars', 'seconds', 'the first UP turn', '+min', 'pxs there',
     'LONG entry better by %', 'UP turns in the 8 min window'),
    [(str(r['wob']), str(r['wob']), '%d' % (r['wob'] * 5),
      U(r['first']) if r['first'] else 'never', mn(r['first']) if r['first'] else '—',
      '%.6f' % float(PX[r['first']]) if r['first'] else '—',
      '%+.4f' % r['imp'] if r['first'] else '—', str(r['nup'])) for r in rows])

print('\n# WHERE THE LANDING JUMPS — the knee')
prev = None; jumps = []
for r in rows:
    if prev is not None and r['first'] != prev['first']:
        jumps.append((prev, r))
    prev = r
box(('from rrev_wob', 'its landing', 'to rrev_wob', 'its landing', 'the jump in min',
     'LONG entry before', 'LONG entry after', 'the entry gained'),
    [(str(a['wob']), U(a['first']), str(b['wob']), U(b['first']),
      '%.1f' % ((int(SC.ts[b['first']]) - int(SC.ts[a['first']])) / 60000.0),
      '%+.4f' % a['imp'], '%+.4f' % b['imp'], '%+.4f' % (b['imp'] - a['imp']))
     for a, b in jumps])

j1021 = [r for r in rows if r['first'] is not None
         and SC.K('2026-09-25 10:20:00') <= r['first'] <= SC.K('2026-09-25 10:22:00')]
print('\n# WHICH rrev_wob LANDS INSIDE 10:20:00-10:22:00, JOE\'S READ')
box(('rrev_wob', 'seconds', 'the landing', '+min', 'LONG entry better by %',
     'UP turns in the 8 min window'),
    [(str(r['wob']), '%d' % (r['wob'] * 5), U(r['first']), mn(r['first']),
      '%+.4f' % r['imp'], str(r['nup'])) for r in j1021]
    or [('none', '—', '—', '—', '—', '—')])
