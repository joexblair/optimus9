"""THE ws4 DIVERGENCE TEST. Joe 1014:

    "let's drop ws1 and ws2, and use only ws4. the divergence test will fire whenever ws4Mage has
     crossed from oob to ib, and dwelled ib for 90 seconds. run the test on 07-15"

THE TRIGGER: ws4Mage crosses from oob to in-fence, then holds in-fence 18 bars = 90 s. The anchor is
  the bar that hold completes - the first bar the trigger is knowable.
THE LINES: ws4r and ws4Mage, the ws4 pair, mirroring his ws[1,2][r,Mage] set. TWO lines now, so his
  "3 of 4" has no analogue and BOTH thresholds are reported: 2 of 2 and 1 of 2.
THE DIRECTION GATE IS OFF, Joe 1014: *"disable the trade direction gate. eg, if it prints BULLISH,
  open a long trade"*. The verdict sets the side, not the end ws4Mage left:
      BEARISH  ->  a SHORT
      BULLISH  ->  a LONG
  So each line is now read at BOTH drs - `anchor_floater` refuses the wrong side of 50, so a line
  fires in at most one direction on a bar. A trigger where one line fires each way is a CONFLICT and
  opens nothing; those are counted and listed.
  WHAT THIS REPLACED: the end ws4Mage left used to force the read, from his cp rule *"a high ws1cp
  can only open a SHORT on a BEARISH div ... the inverse is NOT true"*. On 07-15 that gate let one
  trigger of 38 through at 2 of 2, for +0.6586%.
THE DIVERGENCE is the Jig's `anchor_floater`, unchanged.
THE HACK keeps its veto, his 1014 ruling.
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
A0 = SC.K(os.environ.get('W_FROM', '2026-07-15 00:00:00'))
A1 = SC.K(os.environ.get('W_TO', '2026-07-16 00:00:00'))
DWELL = int(os.environ.get('W_WS4_DWELL', 18))        # 90 s at the 5 s grid
# THE TIMEFRAME THE WHOLE MECH READS. Joe 1014 gave the mech on ws4, then *"swap ws4 with ws3"* and
# *"print also the reports for ws2 as a standalone"*. One knob so the trigger line, both divergence
# lines and the labels move together.
TF = int(os.environ.get('W_DIV_TF', 4))
TF = int(os.environ.get('W_DIV_TF', 4))              # the timeframe the whole mech reads

ib, em, rows, gate, restart = M.build()
PX = np.asarray(SC.PX, float)
MG4 = np.asarray(ib.mg[TF], float)
R4 = np.asarray(C.R[TF], float)
HI, LO = float(SC.HI), float(SC.LO)

print()
print('| knob | value |')
print('|---|---|')
print('| TAPE | %d bars |' % N)
print('| the day | %s to %s |' % (U(A0), U(A1 - 1)))
print('| the timeframe | ws%d |' % TF)
print('| the trigger | ws%dMage crosses oob -> in-fence, then holds in-fence %d bars = %d s |'
      % (TF, DWELL, DWELL * 5))
print('| the fence | oob is <= %.0f or >= %.0f |' % (LO, HI))
print('| the lines | ws%dr, ws%dMage |' % (TF, TF))
print('| the hack | vetoes every opening |')

# ---- the triggers: an oob -> ib cross, then DWELL bars in-fence
trig = []
for k in range(1, N):
    was = (MG4[k - 1] >= HI) or (MG4[k - 1] <= LO)
    now = LO < MG4[k] < HI
    if not (was and now):
        continue
    end = k + DWELL - 1
    if end >= N:
        break
    if not np.all((MG4[k:end + 1] > LO) & (MG4[k:end + 1] < HI)):
        continue
    left = +1 if MG4[k - 1] >= HI else -1        # the end it LEFT
    trig.append((k, end, left))
day = [t for t in trig if A0 <= t[1] < A1]

print()
print('| what | figure |')
print('|---|---|')
print('| triggers on the tape | %d |' % len(trig))
print('| triggers on this day | %d |' % len(day))

SHOW = os.environ.get('W_SHOW_TRIGGERS', '1') == '1'
print()
print('# EVERY TRIGGER, AND ITS DIVERGENCE READ' if SHOW else '# TRIGGERS: table suppressed')
print('| the cross | the anchor, dwell completes | the end it left | ws4Mage before | ws4Mage at the anchor | ws4r at the anchor | ws4r fired | ws4Mage fired | the vote |')
print('|---|---|---|---|---|---|---|---|---|')
cands = []
conflicts = []
for k, end, left in day:
    fired = []
    for nm, arr in (('ws%dr' % TF, R4), ('ws%dMage' % TF, MG4)):
        f = 0
        for d in (+1, -1):
            o = anchor_floater(arr, PX, d, end)
            if o is not None and int(o['fired']) != 0:
                f = int(o['fired'])
                break
        fired.append(f)
    nb = sum(1 for f in fired if f == +1)     # bearish
    nl = sum(1 for f in fired if f == -1)     # bullish
    cands.append((k, end, left, nb, nl, fired))
    if SHOW:
        print('| %s | %s | %s | %.2f | %.2f | %.2f | %s | %s | %d bearish / %d bullish |'
              % (U(k), U(end), 'HIGH' if left > 0 else 'LOW', MG4[k - 1], MG4[end], R4[end],
                 {1: 'BEARISH', -1: 'bullish', 0: 'none'}[fired[0]],
                 {1: 'BEARISH', -1: 'bullish', 0: 'none'}[fired[1]], nb, nl))


# ---- DOES THE VERDICT EVER DISAGREE WITH THE SIDE ws4Mage LEFT? That is the only thing the
# direction gate can act on. Joe 1014 turned the gate off; this counts what it would have stopped.
_al = _dis = 0
for k, end, left, nb, nl, fired in cands:
    for f in fired:
        if f == 0:
            continue
        if f == left:
            _al += 1
        else:
            _dis += 1
print()
print('| the direction gate, what it would act on | count |')
print('|---|---|')
print('| line-readings that AGREE with the end ws4Mage left | %d |' % _al)
print('| line-readings that DISAGREE - the gate would stop these | %d |' % _dis)


def run(need):
    """-> (legs, blocked, conflict). The verdict sets the side; the hack still vetoes."""
    legs = []
    blocked = []
    conflict = []
    k = A0
    for cp, end, left, nb, nl, _f in cands:
        if end < k:
            continue
        want_b = nb >= need
        want_l = nl >= need
        if want_b and want_l:
            conflict.append((end, nb, nl))
            continue
        if not (want_b or want_l):
            continue
        dr = +1 if want_b else -1          # BEARISH -> SHORT, BULLISH -> LONG
        side, tf, endl, val = gate.oob_side(end)
        he = 0 if endl is None else (+1 if endl == 'HIGH' else -1)
        if not gate.permits_live(HG.cp_side_for(dr), side, end, end, he):
            blocked.append((end, dr, 'ws%d %.2f %s' % (tf, val, endl)))
            continue
        r = M.chain(end, dr, ib, em, rows, gate=gate)
        if r['close'] is None:
            continue
        legs.append((end, dr, r))
        k = r['end']
    return legs, blocked, conflict



# ---- THE MOMENTUM REPORT AT EACH OPEN. Joe 1014: *"how many of the losers/winners were trading
# against/with the dws/ws momentum report?"*. The report is the machine's own 7-line vote - ws12,
# ws15, ws20, ws30, dws8r, dws10r, dws15r - read through `rows`, which `machine.build()` returns.
# WITH = more lines mom-true toward the trade's OWN target-side oob than toward the other.
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
    t = sum(r['gross_end'] for _b, _d, r in legs)
    print()
    print('# THE CHAIN AT %d OF 2' % need)
    print('| # | opens | side | close event | ends | why | gross |')
    print('|---|---|---|---|---|---|---|')
    for i, (b, dr, r) in enumerate(legs, 1):
        print('| %d | %s | %s | %s | %s | %s | %+.4f%% |'
              % (i, U(b), 'SHORT' if dr > 0 else 'LONG', U(r['close']), U(r['end']),
                 str(r['why_end']).replace('|', '·')[:42], r['gross_end']))
    print('| **TOTAL** | — | — | — | — | — | **%+.4f%%** |' % t)
    print()
    print('| at %d of 2 | figure |' % need)
    print('|---|---|')
    print('| trades | %d |' % len(legs))
    print('| gross | %+.4f%% |' % t)
    print('| winners | %d |' % sum(1 for _b, _d, r in legs if r['gross_end'] > 0))
    print('| losers | %d |' % sum(1 for _b, _d, r in legs if r['gross_end'] < 0))
    print('| triggers the hack blocked | %d |' % len(blocked))
    print('| triggers where the two lines fired opposite ways | %d |' % len(conflict))
    mom_table(legs, 'at %d of 2' % need)
    if blocked:
        print()
        print('| the hack blocked | the trade it wanted | the line out of bounds |')
        print('|---|---|---|')
        for b, dr, why in blocked:
            print('| %s | %s | %s |' % (U(b), 'SHORT' if dr > 0 else 'LONG', why))
