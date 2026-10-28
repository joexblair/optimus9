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

SWEEP-PIVOTS HAS NO MAE, and it structurally cannot have one. `mfe_pct` is measured FROM the pivot,
and the pivot IS the extreme of the leg (`argmin`/`argmax` over the leg's span), so an adverse
excursion measured from the pivot is zero by construction. Joe 1027 asked why the aggregate had no
MAE in it; that is the reason, and it is not a reason to ship an MFE-only report.

SO THE PER-EVENT MAE IS MEASURED FROM THE CADENCE BAR, over the leg's own span - from the cadence
bar to `sw['close']`, the bar sweep-pivots itself ends the leg on. That is the excursion between
the bar the chain acts on and the bar the scale closes, favourable direction -side. THE BOUND IS
SWEEP-PIVOTS' OWN, not a horizon chosen here, which is why this pair can be aggregated and the
rise/fall pair cannot.

THE CADENCE BAR IS OFTEN NOT INSIDE THE LEG. `lag_s` is negative when the cadence precedes the
leg's open - at 2026-08-30 02:35:20 it is -185 s, so the span scored runs 185 s before the leg
starts. That is reported as it is; it is the real distance between the decision and the swing.

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
RISE, FALL, LEG = [], [], []                           # the maemfe summary's own columns
MAE, MFE = [], []                                      # from the cadence bar to the leg's close

print('| the cadence bar | the target side | the ws1Mage cross | the ws1r reversal | gap s |'
      ' lines | which | top | MAE % | MFE % | lag s | rise after % | fall after % | SP TF |'
      ' the pivot | leg MFE % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
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
    rise, fall = (hi - p0) / p0 * 100.0, (lo - p0) / p0 * 100.0
    RISE.append(rise); FALL.append(fall)
    #   THE PER-EVENT MAE/MFE: the cadence bar to the bar sweep-pivots closes the leg on. The
    #   favourable direction is -side, the same mapping `mfe_pct` uses.
    mae = mfe = None
    if sw and sw.get('close') is not None:
        LEG.append(float(sw['mfe_pct']))
        z = int(sw['close'])
        #   THE SPAN IS ORDERED, NOT ASSUMED. `lag_s` can be negative, so the cadence bar can sit
        #   before the leg's open; the span is then cadence -> leg close either way.
        a, b2 = min(int(bar), z), max(int(bar), z)
        seg = np.asarray(close[a:b2 + 1], float)
        pb, fav = float(close[int(bar)]), -int(sd)
        if np.isfinite(seg).any():
            up = (float(np.nanmax(seg)) - pb) / pb * 100.0
            dn = (float(np.nanmin(seg)) - pb) / pb * 100.0
            mfe, mae = (up, dn) if fav > 0 else (-dn, -up)
            MFE.append(mfe); MAE.append(mae)
    print('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %+.3f | %+.3f %s'
          % (ln.U(bar), 'HIGH' if sd > 0 else 'LOW', xr, rv, gp, nl, wh, tp,
             '-' if mae is None else '%+.3f' % mae,
             '-' if mfe is None else '%+.3f' % mfe,
             '-' if sw is None or sw.get('lag_s') is None else sw['lag_s'],
             rise, fall, tail))

#   THE MAE/MFE SUMMARY, Joe 1027: *"always include an maemfe summary when a detailed report is
#   created and shows the per-row maemfe"*. Two blocks, because the two columns are not the same
#   kind of measurement and averaging them together would hide that.
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
print('')
print('| the MAE/MFE read, the cadence bar to the leg close | value |')
print('|---|---|')
print('| events scored | %d of %d |' % (len(MAE), len(rows)))
if MAE:
    print('| sum MAE %% | %+.3f |' % sum(MAE))
    print('| sum MFE %% | %+.3f |' % sum(MFE))
    print('| median MAE %% | %+.3f |' % _med(MAE))
    print('| median MFE %% | %+.3f |' % _med(MFE))
    print('| worst MAE %% | %+.3f |' % min(MAE))
    print('| best MFE %% | %+.3f |' % max(MFE))
    print('| MFE > abs(MAE) | %d of %d |'
          % (sum(1 for m, f in zip(MAE, MFE) if f > abs(m)), len(MAE)))
    print('| MAE worse than -1.1%% (LIN2_MAE_CAP) | %d of %d |'
          % (sum(1 for m in MAE if m < -float(K.LIN2_MAE_CAP)), len(MAE)))
print('| the span | the cadence bar to sw[close], the bar sweep-pivots ends the leg on - NOT a'
      ' horizon chosen here |')
print('| why sweep-pivots has no MAE of its own | mfe_pct is measured FROM the pivot, and the'
      ' pivot IS the leg\'s extreme, so an adverse excursion from it is 0 by construction |')
print('')
print('| the sweep-pivot leg MFE read | value |')
print('|---|---|')
print('| events scaled | %d of %d |' % (len(LEG), len(rows)))
if LEG:
    print('| sum leg MFE %% | %+.3f |' % sum(LEG))
    print('| median leg MFE %% | %.3f |' % _med(LEG))
    print('| lowest leg MFE %% | %.3f |' % min(LEG))
    print('| highest leg MFE %% | %.3f |' % max(LEG))
    print('| at or above 1.0%% | %d of %d |' % (sum(1 for x in LEG if x >= 1.0), len(LEG)))
    print('| below 0.5%% | %d of %d |' % (sum(1 for x in LEG if x < 0.5), len(LEG)))
print('| what it measures | the event\'s own swing, scaled by sweep-pivots - the per-event read |')
print('')
print('| the rise/fall read | value |')
print('|---|---|')
print('| events | %d |' % len(rows))
if rows:
    print('| sum rise %% | %+.3f |' % sum(RISE))
    print('| sum fall %% | %+.3f |' % sum(FALL))
    print('| median rise %% | %+.3f |' % _med(RISE))
    print('| median fall %% | %+.3f |' % _med(FALL))
    print('| best rise %% | %+.3f |' % max(RISE))
    print('| worst fall %% | %+.3f |' % min(FALL))
    print('| rise > abs(fall) | %d of %d |'
          % (sum(1 for r, f in zip(RISE, FALL) if r > abs(f)), len(rows)))
print('| NO HORIZON | each row runs from its cadence bar to the window end %s, so an early row'
      ' sees the whole window and a late row sees hours. These are NOT per-event reads and the'
      ' aggregate above them is an aggregate of that. The horizon is Joe\'s to set |' % ln.U(B))
print('| NO TRADE SIDE | rise and fall are reported as measured, not mapped onto MAE/MFE - the'
      ' side is an input |')

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
