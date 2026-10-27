"""THE ws1Mage ib-CROSS + ws1r REVERSAL + BARRAGE, as a standalone scored list. Joe 1027.

HIS QUESTION, then his ruling:
    "if there was a tolerance that allowed for low-side ws1r reversing to pseudo fit 'inside the
     ws1Mage oob to ib' at 02:29, would it have detected a barrage of low-side reversals and
     declared exhaust?"
    "so the tolerance alone will not select 02:29. It needs a second condition - the barrage itself
     is the obvious candidate" / "agreed - let's see the outcome as a standalone list with maemfe"

THE THREE CONDITIONS:
    1  ws1Mage crosses from oob to ib on a side
    2  ws1r reverses on the SAME side within the tolerance of that cross
    3  at least `BARRAGE` r lines reverse on that side between the cross and the ws1r reversal

BOTH THRESHOLDS ARE ANCHORED TO HIS 02:29 INSTANCE, not chosen:
    the tolerance  70 s - the measured gap from the 02:27:50 cross to the 02:29:00 ws1r reversal
    the barrage    6 lines - the measured count inside those 70 s (ws3, ws4, ws8, ws6, ws7, ws1)
  So 02:29 is admitted by construction and the list shows what else clears the same bar. Neither
  number is a preference and neither was swept.

NO TRADE SIDE IS DERIVED. A LOW-side instance could be read as a LONG and a HIGH-side as a SHORT,
but that is a mapping he has not made, so the excursions are reported BOTH WAYS - the max rise and
the max fall from the signal bar - and he can read whichever side he means. The banked rule is that
the side is an input.

NO EXIT RULE EXISTS for this mech, so the scale is sweep-pivots, which is what every other event
list in this fork uses: `SP.swing(bar, side, close)` with `side` the oob side the leg LEFT.

usage: l2_barrage.py <start> <end>
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_sweep_pivots as SP
from optimus9.analysis.jig import lift_off, oob_ib_cross
from v4_backstop_trades import prices
sys.stderr = _e

TOL_S = 70          # HIS 02:29 GAP, measured. Not a chosen value.
BARRAGE = 6         # HIS 02:29 COUNT, measured. Not a chosen value.

A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
E = RS.load((RS.K0, RS.R0, RS.S0))
M1 = np.asarray(ln.line('ws1Mage'), float)
close, PHI, PLO = prices()
rev = {s: {t: sorted(int(b) for b in lift_off(np.asarray(E[t], float), s, K.LIFT_PTS,
                                              K.gap_for(t), K.LIFT_TOL, int(K.LIFT_WOB)))
           for t in range(1, 13)} for s in (+1, -1)}

print('# THE ws1Mage ib-CROSS + ws1r REVERSAL + BARRAGE, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the tolerance %d s and the barrage %d lines are BOTH measured off his 2026-08-30 02:29'
      % (TOL_S, BARRAGE))
print('#   instance - the 02:27:50 cross to the 02:29:00 ws1r reversal, 6 lines reversing inside it.')
print('# NO TRADE SIDE IS DERIVED: the rise and the fall from the signal bar are both reported.')
print('# the scale is sweep-pivots - no exit rule exists for this mech. RULED_OK %s' % K.RULED_OK)
print('')
rows = []
for c, _cf, sd in oob_ib_cross(M1, K.OOB_HI, K.OOB_LO, 1):
    if not (A <= c <= B):
        continue
    w = int(TOL_S) // 5
    r1 = [b for b in rev[sd][1] if c <= b <= c + w]
    if not r1:
        continue
    sig = r1[0]
    lines = sorted(t for t in range(1, 13) if any(c <= b <= sig for b in rev[sd][t]))
    if len(lines) < BARRAGE:
        continue
    rows.append((c, sig, sd, lines))

print('| the ws1Mage cross | the oob side | the ws1r reversal | the gap s | lines reversing | which |'
      ' rise after % | fall after % | SP TF | the pivot | leg MFE % |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
for c, sig, sd, lines in rows:
    p0 = float(close[sig])
    hi = float(np.nanmax(PHI[sig:B + 1])); lo = float(np.nanmin(PLO[sig:B + 1]))
    sw = SP.swing(int(sig), int(sd), close)
    tail = ('| %s | %s | %.3f |' % (sw['tf'], ln.U(int(sw['pivot'])), sw['mfe_pct'])
            if sw and sw.get('close') is not None else '| - | no sweep-pivot scale | - |')
    print('| %s | %s | %s | %d | %d | %s | %+.3f | %+.3f %s'
          % (ln.U(c), 'HIGH' if sd > 0 else 'LOW', ln.U(sig), (sig - c) * 5, len(lines),
             ','.join('ws%d' % t for t in lines),
             (hi - p0) / p0 * 100.0, (lo - p0) / p0 * 100.0, tail))
print('')
print('| the read | value |')
print('|---|---|')
print('| instances | %d |' % len(rows))
print('| on the LOW side | %d |' % sum(1 for r in rows if r[2] < 0))
print('| on the HIGH side | %d |' % sum(1 for r in rows if r[2] > 0))
print('| his 02:29 instance present | %s |'
      % ('yes' if any(ln.U(r[0])[11:] == '02:27:50' for r in rows) else 'NO'))
print('| the rise is measured | the signal bar to the window end %s, no horizon applied |' % ln.U(B))
