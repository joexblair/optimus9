"""THE BARRAGE, as a standalone scored list. Joe 1027.

HIS QUESTION, then his rulings:
    "if there was a tolerance that allowed for low-side ws1r reversing to pseudo fit 'inside the
     ws1Mage oob to ib' at 02:29, would it have detected a barrage of low-side reversals and
     declared exhaust?"
    "so the tolerance alone will not select 02:29. It needs a second condition - the barrage itself
     is the obvious candidate" / "agreed - let's see the outcome as a standalone list with maemfe"
    "dropping 0229 is ok - 0234 picked it up"
    "bank and commit. make this config the machine. test barrage on a wider window 08-30 to 09-06"

IT HAS NO DETECTION RULE OF ITS OWN ANY MORE. The first write of this file carried its own copy of
the three conditions with TOL_S and BARRAGE as module constants. They are now banked knobs and the
rule lives in `v4_l2_cadence.barrage`, which the chain also calls - so this file SCORES the
producer's output and decides nothing. A second copy of the rule would drift the moment a knob
moved, and it already differed in two ways: it counted ws1..ws30 and it had no MIN_TF term.

THE SCORING BAR IS THE CADENCE BAR, not the raw ws1r reversal. The producer returns the bar the
chain acts on - the last contributing reversal's stamp, which is 35 s after the raw reversal at
LIFT_WOB 8. The banked 1027 list scored from the raw bar, so its rise/fall figures are 35 s earlier
than these. The cadence bar is the only causal one.

NO TRADE SIDE IS DERIVED. The producer is asked for both target sides and the rise and the fall
from the cadence bar are both reported, so he can read whichever side he means. The banked rule is
that the side is an input.

NO EXIT RULE EXISTS for this mech, so the scale is sweep-pivots, which is what every other event
list in this fork uses: `SP.swing(bar, side, close)` with `side` the oob side the leg LEFT.

NO HORIZON. The rise and the fall run from the cadence bar to the window end he asked for, because
no cap exists unless he sets one.

usage: l2_barrage.py <start> <end>
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_sweep_pivots as SP
import v4_closed_prev as CP, v4_l2_proxy as PX, v4_l2_cadence as CAD
from v4_backstop_trades import prices
sys.stderr = _e

A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
BD = PX.Board(C, E, MGE=MGE)
close, PHI, PLO = prices()

print('# THE BARRAGE, %s .. %s' % (ln.U(A), ln.U(B)))
print('# LIN2_BARRAGE_TOL_S %d s | LIN2_BARRAGE_LINES %d | LIN2_BARRAGE_MIN_TF %d | ON %d'
      % (K.LIN2_BARRAGE_TOL_S, K.LIN2_BARRAGE_LINES, K.LIN2_BARRAGE_MIN_TF, K.LIN2_BARRAGE_ON))
print('# the tolerance and the line count are MEASURED off his 2026-08-30 02:29 instance - the')
print('#   02:27:50 cross to the 02:29:00 ws1r reversal, 6 lines inside it. MIN_TF 9 is his ruling')
print('#   "dropping 0229 is ok - 0234 picked it up", and it excludes that same 02:29 instance.')
print('# the rule is v4_l2_cadence.barrage - the SAME producer the chain calls. This file scores.')
print('# THE BAR IS THE CADENCE BAR: the last contributing reversal\'s stamp, 35 s after the raw')
print('#   ws1r reversal at LIFT_WOB %d. NO TRADE SIDE IS DERIVED. RULED_OK %s'
      % (K.LIFT_WOB, K.RULED_OK))
print('')

rows = []
for sd in (-1, +1):
    for bar, _ty, why in CAD.barrage(BD, sd, A, B):
        rows.append((int(bar), int(sd), why))
rows.sort()                                            # chronological ascending

print('| the cadence bar | the target side | the ws1Mage cross | the ws1r reversal | gap s |'
      ' lines | which | top | rise after % | fall after % | SP TF | the pivot | leg MFE % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for bar, sd, why in rows:
    #   the producer's `why` carries the mech's own figures; parsed back out so the table has one
    #   column per field rather than one prose cell
    xr = why.split('oob->ib ')[1].split(',')[0]
    rv = why.split('ws1r reverses ')[1].split(' (')[0]
    gp = why.split(' (')[1].split(' s)')[0]
    nl = why.split(', ')[2].split(' lines')[0]
    wh = why.split('with it (')[1].split(')')[0]
    tp = why.split('top ')[1].split(' -')[0]
    p0 = float(close[bar])
    hi = float(np.nanmax(PHI[bar:B + 1])); lo = float(np.nanmin(PLO[bar:B + 1]))
    sw = SP.swing(int(bar), int(sd), close)
    tail = ('| %s | %s | %.3f |' % (sw['tf'], ln.U(int(sw['pivot'])), sw['mfe_pct'])
            if sw and sw.get('close') is not None else '| - | no sweep-pivot scale | - |')
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %+.3f | %+.3f %s'
          % (ln.U(bar), 'HIGH' if sd > 0 else 'LOW', xr, rv, gp, nl, wh, tp,
             (hi - p0) / p0 * 100.0, (lo - p0) / p0 * 100.0, tail))

print('')
days = sorted({ln.U(b)[:10] for b, _s, _w in rows})
print('| the read | value |')
print('|---|---|')
print('| cadences | %d |' % len(rows))
print('| on the LOW target side | %d |' % sum(1 for r in rows if r[1] < 0))
print('| on the HIGH target side | %d |' % sum(1 for r in rows if r[1] > 0))
print('| days in the window | %d |' % (((B - A) * 5) // 86400 + 1))
print('| days with at least one cadence | %d |' % len(days))
print('| the rise/fall are measured | the cadence bar to the window end %s, no horizon |' % ln.U(B))

print('')
print('| the day | cadences |')
print('|---|---|')
for d in days:
    print('| %s | %d |' % (d, sum(1 for b, _s, _w in rows if ln.U(b)[:10] == d)))
