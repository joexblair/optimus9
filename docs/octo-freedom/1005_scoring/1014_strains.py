"""ONE CHAIN OR TWO? Joe 1014: *"do we run the 2 strains as a single chain, or do we create 2
chains? what's more lucrative?"*

THE SAME WINDOW FOR EVERY RUN so the totals are comparable: 2026-07-17 21:58:00, the first declared
open, to the first leg that ends on or after 2026-07-20 00:00:00.

    A  the main chain alone     the declared opens, the chain restart, the next permitted cross-back
    B  the divergence chain     3 of 4 on ws[1,2][r,Mage] at a cp, the hack keeping its veto
    C  one combined chain       every opener competes, earliest bar wins, ONE open trade at a time
    A + B                       two chains run side by side, each with its own open-trade state

THE HACK VETOES EVERY OPENING in all four, Joe 1014: *"we don't prioritise divergence over oob
hack"*.
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
START = SC.K('2026-07-17 21:58:00')
UNTIL = SC.K('2026-07-20 00:00:00')
NEED = 3

ib, em, rows, gate, restart = M.build()
PX = np.asarray(SC.PX, float)
LINES = (('ws1r', C.R[1]), ('ws1Mage', ib.mg[1]), ('ws2r', C.R[2]), ('ws2Mage', ib.mg[2]))
DECL = [(SC.K(ets), dr) for _l, ets, _c, dr in M.TRADES]


def permits(dr, bar):
    side, tf, endl, val = gate.oob_side(bar)
    he = 0 if endl is None else (+1 if endl == 'HIGH' else -1)
    return gate.permits_live(HG.cp_side_for(dr), side, bar, bar, he)


def next_cp(frm):
    best = None
    for d in (+1, -1):
        cp, _dec, _via = ib.next_cp_ib(frm, d)
        if cp is not None and (best is None or cp < best[0]):
            best = (cp, d)
    return best if best else (None, None)


def div_vote(k, cps):
    n = 0
    for _nm, arr in LINES:
        o = anchor_floater(np.asarray(arr, float), PX, cps, k)
        if o is not None and int(o['fired']) == int(cps):
            n += 1
    return n


def open_div(frm):
    """The next divergence opening after `frm`. -> (bar, dr) or (None, None)."""
    k = frm
    for _ in range(100000):
        cp, cps = next_cp(k)
        if cp is None or cp >= N - 1:
            return None, None
        if div_vote(cp, cps) >= NEED and permits(int(cps), cp):
            return cp, int(cps)
        k = cp
    return None, None


def open_cross(frm):
    """The next permitted cross-back opening after `frm`. -> (bar, dr) or (None, None)."""
    best = None
    for cps in (+1, -1):
        k = frm
        while True:
            cp, dec, _via = ib.next_cp_ib(k, cps)
            if dec is None:
                break
            if permits(HG.trade_side(cps), dec):
                if best is None or dec < best[0]:
                    best = (dec, HG.trade_side(cps))
                break
            k = dec
    return best if best else (None, None)


def open_restart(frm):
    rk, rdr, _a, _b = restart.next(frm)
    if rk is None or not permits(int(rdr), rk):
        return None, None
    return rk, int(rdr)


def run(openers, use_declared):
    """Walk one chain. `openers` is a list of callables taking a bar. -> [(bar, dr, result, src)]."""
    legs = []
    k = START
    if use_declared:
        for e, dr in DECL:
            r = M.chain(e, dr, ib, em, rows, gate=gate)
            legs.append((e, dr, r, 'declared'))
        k = legs[-1][2]['end']
    while k < N - 1 and k < UNTIL:
        cand = []
        for nm, fn in openers:
            b, dr = fn(k)
            if b is not None:
                cand.append((b, dr, nm))
        if not cand:
            break
        cand.sort()
        b, dr, nm = cand[0]
        r = M.chain(b, dr, ib, em, rows, gate=gate)
        if r['close'] is None:
            break
        legs.append((b, dr, r, nm))
        k = r['end']
    return legs


def tot(legs):
    return sum(r['gross_end'] for _b, _d, r, _s in legs)


print()
print('| knob | value |')
print('|---|---|')
print('| the window | %s to the first end on or after %s |' % (U(START), U(UNTIL)))
print('| the hack | vetoes every opening in all four runs |')
print('| the divergence vote | %d of 4 on ws1r, ws1Mage, ws2r, ws2Mage |' % NEED)

MAIN = [('restart', open_restart), ('cross-back', open_cross)]
DIV = [('divergence', open_div)]

A = run(MAIN, True)
B = run(DIV, False)
Cc = run(MAIN + DIV, True)

print()
print('| run | what it is | trades | gross | ends |')
print('|---|---|---|---|---|')
print('| A | the main chain alone | %d | %+.4f%% | %s |' % (len(A), tot(A), U(A[-1][2]['end'])))
print('| B | the divergence chain alone | %d | %+.4f%% | %s |'
      % (len(B), tot(B), U(B[-1][2]['end']) if B else '—'))
print('| C | ONE combined chain, one trade at a time | %d | %+.4f%% | %s |'
      % (len(Cc), tot(Cc), U(Cc[-1][2]['end'])))
print('| A + B | TWO chains side by side | %d | **%+.4f%%** | — |'
      % (len(A) + len(B), tot(A) + tot(B)))

for nm, legs in (('A, the main chain alone', A), ('B, the divergence chain alone', B),
                 ('C, one combined chain', Cc)):
    print()
    print('# %s' % nm)
    print('| # | opens | side | how it opened | ends | why | gross |')
    print('|---|---|---|---|---|---|---|')
    for i, (b, dr, r, src) in enumerate(legs, 1):
        print('| %d | %s | %s | %s | %s | %s | %+.4f%% |'
              % (i, U(b), 'SHORT' if dr > 0 else 'LONG', src, U(r['end']),
                 str(r['why_end']).replace('|', '·')[:44], r['gross_end']))
    print('| **TOTAL** | — | — | — | — | — | **%+.4f%%** |' % tot(legs))
