"""THE OLD-SCHOOL DIVERGENCE ANCHOR. Joe 1014:

    "the anchor is set when ws{tf}r is on the target-side of 50, and has reversed. the reversal
     becomes the trigger for action: the first job is to find the target-side extrema of the r line
     that just reversed, and make that the anchor. the rest of the divergence mech stays the same"

AND HIS FOUR ANSWERS:

  THE PERSPECTIVE: *"use global dr to set the calculation's perspective. if dr -1, target-side is
    under 50 - test for divergence from the low side. if dr +1, target-side is over 50 - test for
    divergence from the high side"*. Global dr is `SC.DRv`, the ws1Mage + ws13m latch - the one
    source. It is read AT THE ANCHOR, because that is the bar the calculation is about.
  THE REVERSAL: *"let's use the TF width (120s for ws2)"*. So the extreme must hold for tf * 60 s =
    tf * 12 bars: nothing in that window reclaims it. The trigger is the bar the hold completes.
  THE BARS: *"the anchor bar is the extreme; the trigger bar is the bar when reversal is detected"*.
  THE MAGE TEST: *"use the r anchor and floater for the Mage test"*. So the Jig runs ONCE, on r, and
    the Mage line is read at the SAME two bars the r line's anchor and floater sit on.

CAUSAL: the anchor is the extreme at bar e, the trigger is e + tf*12, and the divergence reads only
bars at or before e. Nothing the trade acts on is later than the bar it acts on.
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
import _htfgate as HG
from optimus9.analysis.jig import anchor_floater, AF_BLOCK

SC, U, N = M.SC, M.U, M.N
A0 = SC.K(os.environ.get('W_FROM', '2026-07-11 00:00:00'))
A1 = SC.K(os.environ.get('W_TO', '2026-07-23 00:00:00'))
TF = int(os.environ.get('W_DIV_TF', 4))
HOLD = TF * 12                                   # tf * 60 s at the 5 s grid
SHOW = os.environ.get('W_SHOW_TRIGGERS', '0') == '1'

ib, em, rows, gate, restart = M.build()
PX = np.asarray(SC.PX, float)
RR = np.asarray(C.R[TF], float)
MG = np.asarray(ib.mg[TF], float)
DRV = np.asarray(SC.DRv, np.int8)

print()
print('| knob | value |')
print('|---|---|')
print('| TAPE | %d bars |' % N)
print('| the window | %s to %s |' % (U(A0), U(A1 - 1)))
print('| the timeframe | ws%d |' % TF)
print('| the reversal hold | %d bars = %d s, the TF width |' % (HOLD, HOLD * 5))
print('| the perspective | global dr at the anchor, SC.DRv |')
print('| the divergence | jig.anchor_floater on ws%dr, block %s bars |' % (TF, AF_BLOCK))
print('| the Mage test | ws%dMage read at the r anchor and r floater bars |' % TF)
print('| the hack | vetoes every opening |')

# ---- the anchors: a target-side extreme of ws{TF}r that holds for HOLD bars
trig = []
for e in range(1, N - HOLD - 1):
    d = int(DRV[e])
    if d == 0:
        continue
    v = RR[e]
    if not np.isfinite(v):
        continue
    if (v <= 50.0) if d > 0 else (v >= 50.0):
        continue                                  # not on the target side of 50
    w = RR[e + 1:e + HOLD + 1]
    if not np.all(np.isfinite(w)):
        continue
    held = (w.max() < v) if d > 0 else (w.min() > v)
    if not held:
        continue
    # e must be the extreme, not a point on a slope: the bar before must not beat it
    if (RR[e - 1] > v) if d > 0 else (RR[e - 1] < v):
        continue
    trig.append((e, e + HOLD, d))
day = [t for t in trig if A0 <= t[1] < A1]

print()
print('| what | figure |')
print('|---|---|')
print('| anchors on the tape | %d |' % len(trig))
print('| anchors in the window | %d |' % len(day))
print('| per day | %.1f |' % (len(day) / ((A1 - A0) * 5 / 86400.0)))

cands = []
if SHOW:
    print()
    print('# EVERY ANCHOR AND ITS DIVERGENCE READ')
    print('| the anchor, the extreme | the trigger | global dr | ws%dr at the anchor | the floater bar | ws%dr there | ws%dMage anchor | ws%dMage floater | r fired | Mage fired | the vote |'
          % (TF, TF, TF, TF))
    print('|---|---|---|---|---|---|---|---|---|---|---|')
for e, t, d in day:
    o = anchor_floater(RR, PX, d, e)
    if o is None:
        cands.append((e, t, d, 0, 0, None))
        continue
    _ak, ar, apx = o['anchor']
    fb, fr, fpx = o['floater']
    r_f = int(o['fired'])
    # THE MAGE TEST on the SAME two bars, Joe's rule
    ma, mf = float(MG[_ak]), float(MG[fb])
    if d > 0:
        m_f = +1 if (apx > fpx and ma < mf) else 0
    else:
        m_f = -1 if (apx < fpx and ma > mf) else 0
    nb = sum(1 for f in (r_f, m_f) if f == +1)
    nl = sum(1 for f in (r_f, m_f) if f == -1)
    cands.append((e, t, d, nb, nl, (ar, fb, fr, ma, mf, r_f, m_f)))
    if SHOW:
        print('| %s | %s | %+d | %.2f | %s | %.2f | %.2f | %.2f | %s | %s | %d bearish / %d bullish |'
              % (U(e), U(t), d, ar, U(fb), fr, ma, mf,
                 {1: 'BEARISH', -1: 'bullish', 0: 'none'}[r_f],
                 {1: 'BEARISH', -1: 'bullish', 0: 'none'}[m_f], nb, nl))


def run(need):
    legs, blocked, conflict = [], [], []
    k = A0
    for e, t, d, nb, nl, _x in cands:
        if t < k:
            continue
        wb, wl = nb >= need, nl >= need
        if wb and wl:
            conflict.append(t)
            continue
        if not (wb or wl):
            continue
        dr = +1 if wb else -1
        side, tf, endl, val = gate.oob_side(t)
        he = 0 if endl is None else (+1 if endl == 'HIGH' else -1)
        if not gate.permits_live(HG.cp_side_for(dr), side, t, t, he):
            blocked.append((t, dr, 'ws%d %.2f %s' % (tf, val, endl)))
            continue
        r = M.chain(t, dr, ib, em, rows, gate=gate)
        if r['close'] is None:
            continue
        legs.append((t, dr, r))
        k = r['end']
    return legs, blocked, conflict


_al = _dis = 0
for e, t, d, nb, nl, x in cands:
    if x is None:
        continue
    for f in (x[5], x[6]):
        if f == 0:
            continue
        _al += 1 if f == d else 0
        _dis += 1 if f != d else 0
print()
print('| the direction gate, what it would act on | count |')
print('|---|---|')
print('| readings that AGREE with global dr | %d |' % _al)
print('| readings that DISAGREE - the gate would stop these | %d |' % _dis)


# ---- THE MOMENTUM REPORT AT EACH OPEN. Joe 1014: *"how many of the losers/winners were trading
# against/with the dws/ws momentum report?"*. The report is the machine's own 7-line vote - ws12,
# ws15, ws20, ws30, dws8r, dws10r, dws15r - read through `rows`, which `machine.build()` returns.
# WITH = more lines mom-true toward the trade's OWN target board than toward the other.
def mom_at(bar, dr):
    """-> (toward the trade own board, toward the other, 'with'/'against'/'level')."""
    own = -dr
    n_own = sum(1 for _n, m in rows if bool(m[own][bar]))
    n_opp = sum(1 for _n, m in rows if bool(m[-own][bar]))
    # JOE'S NAMES, 1014: *"own board is the continuation vote, toward the other is the reversal
    # vote"*. My 'with / against the momentum' was my own coinage and is gone.
    tag = 'continuation' if n_own > n_opp else ('reversal' if n_opp > n_own else 'level')
    return n_own, n_opp, tag


def mom_table(legs, label):
    print()
    print('# THE MOMENTUM REPORT AT EACH OPEN, %s' % label)
    print('| # | opens | side | the continuation vote | the reversal vote | which | gross |')
    print('|---|---|---|---|---|---|---|')
    for i, (b, dr, r) in enumerate(legs, 1):
        a, o, t = mom_at(b, dr)
        print('| %d | %s | %s | %d of %d | %d of %d | %s | %+.4f%% |'
              % (i, U(b), 'SHORT' if dr > 0 else 'LONG', a, len(rows), o, len(rows), t,
                 r['gross_end']))
    print()
    print('| the cross-tab, %s | winners | losers | net gross |' % label)
    print('|---|---|---|---|')
    for t in ('continuation', 'reversal', 'level'):
        sel = [(b, dr, r) for b, dr, r in legs if mom_at(b, dr)[2] == t]
        w = sum(1 for _b, _d, r in sel if r['gross_end'] > 0)
        l = sum(1 for _b, _d, r in sel if r['gross_end'] < 0)
        g = sum(r['gross_end'] for _b, _d, r in sel)
        print('| the %s vote leads | %d | %d | %+.4f%% |' % (t, w, l, g))


for need in (2, 1):
    legs, blocked, conflict = run(need)
    tt = sum(r['gross_end'] for _b, _d, r in legs)
    print()
    print('# THE CHAIN AT %d OF 2' % need)
    print('| # | opens | side | close event | ends | why | gross |')
    print('|---|---|---|---|---|---|---|')
    for i, (b, dr, r) in enumerate(legs, 1):
        print('| %d | %s | %s | %s | %s | %s | %+.4f%% |'
              % (i, U(b), 'SHORT' if dr > 0 else 'LONG', U(r['close']), U(r['end']),
                 str(r['why_end']).replace('|', '·')[:42], r['gross_end']))
    print('| **TOTAL** | — | — | — | — | — | **%+.4f%%** |' % tt)
    print()
    print('| at %d of 2 | figure |' % need)
    print('|---|---|')
    print('| trades | %d |' % len(legs))
    print('| gross | %+.4f%% |' % tt)
    print('| winners | %d |' % sum(1 for _b, _d, r in legs if r['gross_end'] > 0))
    print('| losers | %d |' % sum(1 for _b, _d, r in legs if r['gross_end'] < 0))
    print('| the hack blocked | %d |' % len(blocked))
    print('| opposite-way conflicts | %d |' % len(conflict))
    mom_table(legs, 'at %d of 2' % need)
