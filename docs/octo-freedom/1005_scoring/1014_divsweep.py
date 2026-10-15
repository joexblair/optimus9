"""THE DIVERGENCE CHAIN ALONE, 12 DAYS, AND THE ws1cp TOLERANCE SWEPT. Joe 1014:

    "let's focus only on divergence chain for now
     first, we a need a larger sample window. use 07-11 to 07-22, full days
     second, we need to sweep the ws1cp tolerance to find the best gross
     third, we hold out and review"

THE WINDOW: 2026-07-11 00:00:00 to 2026-07-23 00:00:00, twelve full days.
THE HOLD-OUT: the first six days are the FIT half, the last six the HOLD-OUT. The tolerance is
  chosen on the fit half only and then scored on the hold-out. A value that only works on the half
  it was chosen from is a fit, not a finding.
THE MECH is unchanged: at every cp, the four lines ws1r, ws1Mage, ws2r, ws2Mage are read by the
  Jig's own `anchor_floater`; a HIGH cp needs BEARISH on 3 of 4 and opens a SHORT, a LOW cp needs
  BULLISH on 3 of 4 and opens a LONG. The hack keeps its veto.

ONE BUILD. `IB.SYNC` is mutated per value and the mech's cached per-line hold masks are dropped so
they rebuild. `ib.cps(a, b)` lists every cp in one pass - `next_cp_ib` scans bar by bar and over
twelve days that is hundreds of millions of steps.
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
from optimus9.analysis.jig import anchor_floater

SC, U, N = M.SC, M.U, M.N
A0 = SC.K('2026-07-11 00:00:00')
MID = SC.K('2026-07-17 00:00:00')
A1 = SC.K('2026-07-23 00:00:00')
NEED = 3
GRID = tuple(int(z) for z in os.environ.get('W_SYNC_GRID', '0,12,24,36,48,66,90,120').split(','))

ib, em, rows, gate, restart = M.build()
PX = np.asarray(SC.PX, float)
LINES = (('ws1r', C.R[1]), ('ws1Mage', ib.mg[1]), ('ws2r', C.R[2]), ('ws2Mage', ib.mg[2]))
_ARR = [np.asarray(a, float) for _n, a in LINES]

print()
print('| knob | value |')
print('|---|---|')
print('| TAPE | %d bars |' % N)
print('| the window | %s to %s, 12 full days |' % (U(A0), U(A1 - 1)))
print('| the fit half | %s to %s |' % (U(A0), U(MID - 1)))
print('| the hold-out half | %s to %s |' % (U(MID), U(A1 - 1)))
print('| the four lines | ws1r, ws1Mage, ws2r, ws2Mage |')
print('| the vote | %d of 4 |' % NEED)
print('| the hack | vetoes every opening |')
print('| the tolerance grid, in bars | %s |' % ', '.join(str(g) for g in GRID))

_vote_cache = {}


def permits(dr, bar):
    side, tf, endl, val = gate.oob_side(bar)
    he = 0 if endl is None else (+1 if endl == 'HIGH' else -1)
    return gate.permits_live(HG.cp_side_for(dr), side, bar, bar, he)


def vote(k, cps):
    """3-of-4 count at cp `k` on side `cps`. Cached - the cp list changes with the tolerance but a
    given (bar, side) always votes the same, so the Jig is never asked twice for one pair."""
    key = (k, cps)
    if key in _vote_cache:
        return _vote_cache[key]
    n = 0
    for arr in _ARR:
        o = anchor_floater(arr, PX, cps, k)
        if o is not None and int(o['fired']) == int(cps):
            n += 1
    _vote_cache[key] = n
    return n


def walk(sync, a, b):
    """The divergence chain over [a, b). -> [(bar, dr, result)]."""
    IB.SYNC = int(sync)
    if hasattr(ib, '_held'):
        del ib._held
    cps = ib.cps(a, b)                      # one pass, both sides
    legs = []
    k = a
    for cp, side in cps:
        if cp < k:
            continue                        # a trade is open through this cp
        if vote(cp, side) < NEED:
            continue
        dr = int(side)
        if not permits(dr, cp):
            continue
        r = M.chain(cp, dr, ib, em, rows, gate=gate)
        if r['close'] is None:
            continue
        legs.append((cp, dr, r))
        k = r['end']
    return legs


def tot(legs):
    return sum(r['gross_end'] for _b, _d, r in legs)


print()
print('| tolerance, bars | minutes | fit trades | fit gross | hold-out trades | hold-out gross | both halves | both gross |')
print('|---|---|---|---|---|---|---|---|')
res = {}
for g in GRID:
    f = walk(g, A0, MID)
    h = walk(g, MID, A1)
    res[g] = (f, h)
    print('| %d | %.1f | %d | %+.4f%% | %d | %+.4f%% | %d | %+.4f%% |'
          % (g, g * 5 / 60.0, len(f), tot(f), len(h), tot(h),
             len(f) + len(h), tot(f) + tot(h)), flush=True)

best = max(GRID, key=lambda g: tot(res[g][0]))
print()
print('| the hold-out test | value |')
print('|---|---|')
print('| the tolerance that wins the FIT half | %d bars = %.1f min |' % (best, best * 5 / 60.0))
print('| its fit gross | %+.4f%% over %d trades |' % (tot(res[best][0]), len(res[best][0])))
print('| its HOLD-OUT gross | %+.4f%% over %d trades |' % (tot(res[best][1]), len(res[best][1])))
bh = max(GRID, key=lambda g: tot(res[g][1]))
print('| the tolerance that wins the HOLD-OUT half | %d bars = %.1f min |' % (bh, bh * 5 / 60.0))
print('| its hold-out gross | %+.4f%% |' % tot(res[bh][1]))
print('| do they agree | %s |' % ('YES' if bh == best else 'NO'))

for g in GRID:
    f, h = res[g]
    if not (f or h):
        continue
    print()
    print('# TOLERANCE %d BARS = %.1f MIN, every trade' % (g, g * 5 / 60.0))
    print('| half | # | opens | side | ends | why | gross |')
    print('|---|---|---|---|---|---|---|')
    for nm, legs in (('fit', f), ('hold-out', h)):
        for i, (b, dr, r) in enumerate(legs, 1):
            print('| %s | %d | %s | %s | %s | %s | %+.4f%% |'
                  % (nm, i, U(b), 'SHORT' if dr > 0 else 'LONG', U(r['end']),
                     str(r['why_end']).replace('|', '·')[:42], r['gross_end']))
    print('| **TOTAL** | — | — | — | — | — | **%+.4f%%** |' % (tot(f) + tot(h)))
