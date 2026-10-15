"""THE DIVERGENCE ACID TEST. Joe 1014, his spec verbatim:

    "divergence will test ws1 and ws2 at every cp, beginning at 07-17 00:00, using our modified
     ws1cp mech as the anchor
     -if there is no open trade at the time, open a trade in the direction of the divergence
      (BEARISH: SHORT, BULLISH: LONG) if 3 of 4 lines (ie ws[1,2][r,Mage])"

AND HIS CLARIFICATION, which fixes the direction:

    "the trade is only opened if divergence prints a counter-ws1cp-side verdict
     --ie a high ws1cp can only open a SHORT on a BEARISH div. low ws1cp can only open a LONG on a
       BULLISH div
     ---the inverse is NOT true"

So the cp's own side sets the read and the trade:
    a HIGH cp  ->  anchor_floater at dr +1  ->  needs BEARISH on 3 of 4  ->  opens a SHORT
    a LOW  cp  ->  anchor_floater at dr -1  ->  needs BULLISH on 3 of 4  ->  opens a LONG

THE FOUR LINES are his: ws1r, ws1Mage, ws2r, ws2Mage.
THE DIVERGENCE IS THE JIG'S, `optimus9.analysis.jig.anchor_floater` - his own 0912 four-step spec.
Nothing about it is rebuilt here.

THE TRADE OPENS ON THE cp BAR. The divergence is knowable there - it was proved at 2026-07-19
16:45:25 that the read fires at the cp and is gone by the ib bar. MY CHOICE, STATED.

THE HACK KEEPS ITS VETO, Joe 1014: *"we don't prioritise divergence over oob hack"*. A cp that
passes the 3-of-4 vote still has to clear the hack. Measured both ways: with the veto, 7 trades and
+4.6184%; with divergence outranking it, 12 trades and +3.9998%. `W_DIV_OVER_HACK=1` reaches the
second.

THE WALK ENDS on the first leg that ends on or after 2026-07-20 00:00:00, his boundary.
"""
import os
import sys

os.environ.setdefault('W_ARM', 'lastmile')
os.environ.setdefault('W_PASS', 'crossing_to_ib')
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import machine as M
import _chain10 as C
import _ibmech as IB
import _htfgate as HG
from optimus9.analysis.jig import anchor_floater, AF_BLOCK

SC, U, N = M.SC, M.U, M.N
START = SC.K(os.environ.get('W_FROM', '2026-07-17 00:00:00'))
UNTIL = SC.K(os.environ.get('W_UNTIL', '2026-07-20 00:00:00'))
NEED = int(os.environ.get('W_DIV_NEED', 3))          # Joe's "3 of 4"
# Joe 1014: *"we don't prioritise divergence over oob hack"*. The hack keeps its veto. 1 lets
# divergence outrank it, which was measured at +3.9998% over 12 trades against +4.6184% over 7 -
# the seven overrides net -0.2886% and the worst, -1.5278%, is the 2026-07-18 21:18:30 HIGH cp the
# hack exists to block.
OVER = os.environ.get('W_DIV_OVER_HACK', '0') == '1'

ib, em, rows, gate, restart = M.build()
PX = np.asarray(SC.PX, float)
LINES = (('ws1r', C.R[1]), ('ws1Mage', ib.mg[1]), ('ws2r', C.R[2]), ('ws2Mage', ib.mg[2]))

print()
print('| knob | live value |')
print('|---|---|')
print('| TAPE | %d bars |' % N)
print('| the walk | %s to the first leg ending on or after %s |' % (U(START), U(UNTIL)))
print('| W_IB_SYNC, the ws1r/ws1Mage tolerance | %d bars = %.1f min |' % (IB.SYNC, IB.SYNC * 5 / 60.0))
print('| the four lines | %s |' % ', '.join(n for n, _a in LINES))
print('| the vote | %d of 4 |' % NEED)
print('| the divergence | jig.anchor_floater, block %s bars |' % AF_BLOCK)
print('| divergence outranks the hack | %s |' % ('YES' if OVER else 'no, the hack vetoes'))


def next_cp(frm):
    """The next cp after `frm`, either side, earliest first. -> (cp, side) or (None, None)."""
    best = None
    for d in (+1, -1):
        cp, _dec, _via = ib.next_cp_ib(frm, d)
        if cp is not None and (best is None or cp < best[0]):
            best = (cp, d)
    return best if best else (None, None)


def vote(k, cps):
    """The four-line divergence at cp bar `k` on cp side `cps`. -> (count, rows).

    A HIGH cp reads at dr +1 and needs BEARISH; a LOW cp reads at dr -1 and needs BULLISH. The
    sign of `fired` matches: +1 bearish, -1 bullish, so the test is `fired == cps`.
    """
    out = []
    n = 0
    for nm, arr in LINES:
        o = anchor_floater(np.asarray(arr, float), PX, cps, k)
        if o is None:
            out.append((nm, None, None, None, None, 0))
            continue
        _ak, ar, _apx = o['anchor']
        fb, fr, _fpx = o['floater']
        hit = int(o['fired']) == int(cps)
        n += 1 if hit else 0
        out.append((nm, ar, fb, fr, o['d_osc'], o['fired']))
    return n, out


print()
print('| # | the cp | cp side | the vote | the lines that fired | the trade | the hack | the chain ends | why it ends | gross |')
print('|---|---|---|---|---|---|---|---|---|---|')
k = START
legs = []
blocked = []
noquorum = 0
steps = 0
while k < N - 1 and k < UNTIL:
    steps += 1
    if steps > 20000:
        print('| — | the walk hit 20000 steps | — | — | — | — | — | — | — | — |')
        break
    cp, cps = next_cp(k)
    if cp is None:
        break
    n, rws = vote(cp, cps)
    if n < NEED:
        noquorum += 1
        k = cp
        continue
    dr = int(cps)                      # a HIGH cp places a SHORT, a LOW cp a LONG
    side, tf, endl, val = gate.oob_side(cp)
    he = 0 if endl is None else (+1 if endl == 'HIGH' else -1)
    want_cp = HG.cp_side_for(dr)
    ok = gate.permits_live(want_cp, side, cp, cp, he)
    hack = ('permits' if side is None else
            ('permits, ws%d %.2f %s' % (tf, val, endl) if ok
             else 'BLOCKS, ws%d %.2f %s' % (tf, val, endl)))
    if not ok:
        blocked.append((cp, cps, hack))
        if not OVER:
            k = cp
            continue
        hack = 'OVERRIDDEN - ' + hack
    r = M.chain(cp, dr, ib, em, rows, gate=gate)
    if r['close'] is None:
        k = cp
        continue
    legs.append((cp, dr, r, n, rws))
    fired = ', '.join(nm for nm, _a, _f, _r, _d, f in rws if int(f) == int(cps))
    print('| %d | %s | %s | %d of 4 | %s | %s | %s | %s | %s | %+.4f%% |'
          % (len(legs), U(cp), 'HIGH' if cps > 0 else 'LOW', n, fired,
             'SHORT' if dr > 0 else 'LONG', hack, U(r['end']),
             str(r['why_end']).replace('|', '·')[:48], r['gross_end']))
    k = r['end']

tot = sum(r['gross_end'] for _c, _d, r, _n, _w in legs)
print('| **TOTAL** | — | — | — | — | — | — | %s | — | **%+.4f%%** |'
      % (U(legs[-1][2]['end']) if legs else '—', tot))

print()
print('| what | figure |')
print('|---|---|')
print('| trades opened | %d |' % len(legs))
print('| cps that failed the %d-of-4 vote | %d |' % (NEED, noquorum))
print('| cps that passed the vote while the hack said no | %d |' % len(blocked))
print('| of those, opened anyway because divergence outranks it | %d |'
      % (len(blocked) if OVER else 0))
print('| gross | %+.4f%% |' % tot)
if legs:
    print('| winners | %d |' % sum(1 for _c, _d, r, _n, _w in legs if r['gross_end'] > 0))
    print('| losers | %d |' % sum(1 for _c, _d, r, _n, _w in legs if r['gross_end'] < 0))

if blocked:
    print()
    print('# EVERY cp THAT PASSED THE VOTE WHILE THE HACK SAID NO')
    print('| the cp | cp side | the hack |')
    print('|---|---|---|')
    for cp, cps, hack in blocked:
        print('| %s | %s | %s |' % (U(cp), 'HIGH' if cps > 0 else 'LOW', hack))

print()
print('# THE FOUR-LINE READ AT EVERY TRADE THAT OPENED')
print('| the cp | line | anchor r | floater bar | floater r | r anchor-floater | fired |')
print('|---|---|---|---|---|---|---|')
for cp, dr, r, n, rws in legs:
    for nm, ar, fb, fr, dosc, f in rws:
        print('| %s | %s | %s | %s | %s | %s | %s |'
              % (U(cp), nm,
                 '%.2f' % ar if ar is not None else '—',
                 U(fb) if fb is not None else 'none',
                 '%.2f' % fr if fr is not None else '—',
                 '%+.2f' % dosc if dosc is not None else '—',
                 {1: 'BEARISH', -1: 'bullish', 0: 'none'}[int(f)]))
