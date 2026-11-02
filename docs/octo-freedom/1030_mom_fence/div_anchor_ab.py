"""THE DIVERGENCE AT A CADENCE: the cadence bar against the ws1Mage extremum, on his own examples.

His 1101 examples: *"--bullish 2324, floater 2312 / --bullish 0437, floater 0418"*.
His 1101 proposal: *"2324 is when the cadence fires.  maybe divergence will work better if it's
anchored on the ws1Mage extremum - walk back to look forward and find the target-side ws1Mage
extremum, anchor on it and test for divergence"*.

WHY. Anchored on the cadence bar, 23:24:00 reads price-matched: pxs rises +0.000100 from the
floater while ws1r rises +38.02, so both signs are positive. +0.000100 is 0.060% of price. He does
not read 2324 as price-matched, and the anchor is the lever he reached for.

NEITHER ARM IS CHOSEN HERE. Both are printed for every example and every side.

THE PICKER IS THE CASCADE'S OWN - jig.mage_cascade_bar in 'extrema' mode at MC_GAP, his 1017
number. Its walk back is unbounded and it asserts the bar it returns never exceeds the event bar.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever happens. An
#   import error inside it otherwise leaves an empty file and an exit code with no diagnosis.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import ln
    from v4_backstop_trades import prices
    from optimus9.analysis.jig import anchor_floater, mage_cascade_bar, MC_GAP
finally:
    sys.stderr = _e

close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
r1 = np.asarray(CL['r'][1], float)
px = np.asarray(close, float)
MG1 = np.asarray(LL.mage(1)[1], float)        # ws1Mage, the extremum source - his 1017 line
#   THE 08-14 0713 BAR JOINED THE LIST on 1101. It is the first t1 cadence after his 06:59:00 arm
#   and the bar the divergence ends that walk on - 14.1 min in, against the banked 14:07:20, a cost
#   of 414 min and 13 baton passes. His oob-count hypothesis does not separate it from the two
#   09-03 bars, so the anchor/floater pair is what is left to compare.
ROWS = [('his bullish 2324, floater 2312', '2026-09-03 23:24:00', '23:12'),
        ('his bullish 0437, floater 0418', '2026-09-03 04:37:00', '04:18'),
        ('the 0437 cadence bar itself', '2026-09-03 04:37:55', '04:18'),
        ('the 08-14 0713 cadence', '2026-08-14 07:13:05', '-')]
print('# THE DIVERGENCE AT A CADENCE - the two anchor arms, on his own examples')
print('# the verdict is +1 bearish / -1 bullish; the target side is +1 high / -1 low')
print('# his table: a rev-trade when verdict == target side. PM, a raw state of +-2, is refused')
print('# the extremum picker: jig.mage_cascade_bar "extrema", gap %d bars = %d min'
      % (MC_GAP, MC_GAP * 5 // 60))
print()
print('| his example | the cadence bar | target side | the anchor arm | the anchor bar |'
      ' ws1Mage there | the floater bar | his floater | pxs anchor-floater | ws1r anchor-floater |'
      ' they move | the raw state | the verdict | rev-trade? |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for lbl, t, hisfl in ROWS:
    k = ln.K(t)
    for sd in (-1, +1):
        for arm in ('cadence', 'extremum'):
            db = k
            if arm == 'extremum':
                pk = mage_cascade_bar(MG1, k, sd, mode='extrema', gap=MC_GAP)
                if pk is not None:
                    db = int(pk[0])
            assert db <= k, 'the anchor is after the cadence bar it serves'
            got = anchor_floater(r1, px, sd, db)
            if got is None:
                print('| %s | %s | %s | %s | %s | %.2f | - | %s | - | - | - | no reading | none | no |'
                      % (lbl, t, 'low' if sd < 0 else 'high', arm, ln.U(db), MG1[db], hisfl))
                continue
            st = int(got['state'])
            v = st if abs(st) == 1 else None
            f = got.get('floater')
            fb = int(f[0]) if f else None
            dpx = (px[db] - px[fb]) if fb is not None else float('nan')
            dr = (r1[db] - r1[fb]) if fb is not None else float('nan')
            mv = ('-' if fb is None else
                  ('the SAME way' if (dpx > 0) == (dr > 0) else 'OPPOSITE ways'))
            print('| %s | %s | %s | %s | %s | %.2f | %s | %s | %+.6f | %+.2f | %s | %+d | %s | %s |'
                  % (lbl, t, 'low' if sd < 0 else 'high', arm, ln.U(db), MG1[db],
                     ln.U(fb)[11:] if fb is not None else '-', hisfl, dpx, dr, mv, st,
                     'none' if v is None else ('%+d bearish' % v if v > 0 else '%+d bullish' % v),
                     'YES' if (v is not None and int(v) == int(sd)) else 'no'))
