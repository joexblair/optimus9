"""ws13r HIGH-SIDE REVERSALS AROUND 14:43, PER WOB OPTION. Joe 1027.

    "which option creates the closest high-side ws13r reversal following the 1443 pivot, without
     being turned back (reversed) while travelling to the pivot"

THE DATE IS ASSUMED 2026-08-31 - the 1432 barrage fire and its 1501 walk are that day, and he gave
no date. His times are estimates, so the raw list is printed too and the pivot can be re-read off it.

TRAVEL START is assumed the 14:32:40 barrage fire - the signal the line would be travelling from.
Both assumptions are stated and neither is a ruling.

PER OPTION: every HIGH-side ws13r reversal in 14:00..15:30, raw bar and STAMP (raw + wob - 1, the
bar it is actionable on), then the two answers he asked for.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
from optimus9.analysis.jig import lift_off
sys.stderr = _e

DAY = '2026-08-31'
A, B = ln.K('%s 14:00:00' % DAY), ln.K('%s 15:30:00' % DAY)
PIVOT = ln.K('%s 14:43:00' % DAY)
TRAVEL_FROM = ln.K('%s 14:32:40' % DAY)
T = 13 * 60 // 5
em = np.asarray(RS.load((RS.K0, RS.R0, RS.S0))[13], float)
cl = CP.series(em, 13 * 60)
OPTS = [('emerging wob 8 (banked)', em, 8), ('emerging wob 20', em, 20),
        ('emerging wob 32', em, 32), ('emerging wob 39 = T/4', em, 39),
        ('closed wob 8 (the chart)', cl, 8)]

print('# ws13r HIGH-SIDE REVERSALS, %s 14:00..15:30' % DAY)
print('# the date is ASSUMED %s - the 1432 barrage fire and its 1501 walk are that day.' % DAY)
print('# the pivot is ASSUMED %s and the travel start the %s barrage fire.'
      % (ln.U(PIVOT)[11:], ln.U(TRAVEL_FROM)[11:]))
print('# the STAMP is raw + wob - 1, the bar the reversal is actionable on. ws13r value at both.')
print('# RULED_OK %s' % K.RULED_OK)
print('')
print('| the option | the raw bar | the stamp | ws13r at raw | ws13r at stamp |')
print('|---|---|---|---|---|')
R = {}
for nm, line, w in OPTS:
    raw = sorted(int(b) for b in lift_off(line, +1, K.LIFT_PTS, K.gap_for(13), K.LIFT_TOL, int(w)))
    R[nm] = [(b, b + w - 1) for b in raw]
    shown = [(b, s) for b, s in R[nm] if A <= b <= B or A <= s <= B]
    if not shown:
        print('| %s | none in the window | - | - | - |' % nm); continue
    for b, s in shown:
        print('| %s | %s | %s | %.2f | %.2f |'
              % (nm, ln.U(b), ln.U(s), line[b], line[min(s, len(line) - 1)]))

print('')
print('## his two questions')
print('')
print('| the option | turned back travelling to the pivot? | the closest reversal AFTER the pivot |'
      ' its gap from the pivot | ws13r there |')
print('|---|---|---|---|---|')
for nm, line, w in OPTS:
    back = [(b, s) for b, s in R[nm] if TRAVEL_FROM < s <= PIVOT]
    after = [(b, s) for b, s in R[nm] if s > PIVOT]
    bk = ('YES - stamped %s' % ', '.join(ln.U(s)[11:] for _b, s in back)) if back else 'no'
    if not after:
        print('| %s | %s | none to the data end | - | - |' % (nm, bk)); continue
    b, s = after[0]
    print('| %s | %s | %s | %+.1f min | %.2f |'
          % (nm, bk, ln.U(s), (s - PIVOT) * 5 / 60.0, line[min(s, len(line) - 1)]))
