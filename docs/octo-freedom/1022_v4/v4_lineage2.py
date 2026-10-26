"""lineage2's WALK. A FORK. Joe 1025: *"I need a lineage2 fork of lineage - we're going to play with
a new idea... I don't want to make adjustents in lineage"*.

v4lineage (`v4_fast.walk`) IS UNTOUCHED. Nothing here imports its walk and nothing in the machine
calls this. The spec is `v4_lineage2.md`, his words verbatim.

ONE RESPONSIBILITY: the walk. The arm race, the rider, the baton, and the exhaust verdict.
`v4_l2_cadence` says WHERE a decision may be made; this file makes it.

THE `towards` TAG IS THE BANKED v4 TRAJECTORY READ, on the r line, with the TARGET SIDE as the
perspective. Joe 1025: *"the perspective is target-side for the whole ladder"*, and his baton rule
reads the r: *"baton can only be received by an r line that is 1) ex v4mom-fnc and 2) tagged as
`towards`"*. `rule2_trajectory.opposed_extrema` + `K.traj_block(tf)` + `K.traj_min_bars(tf)` is
exactly what `v4_confluence.raw_traj`/`has` already do, and `TRAJ_WIDTH` 21.0 was calibrated on r
lines. So `jig.away_toward` is NOT used - its perspective is ws1Mage's by his own 1019 ruling for a
different mech, and only dead v3 consumes it.

THE BOARD PROXY OWNS THE LADDER ROUTING. Joe 1026: *"build a proxy that sends the emerging values
to the gate decision"*. `v4_l2_proxy.Board` is handed both ladders and every read in this file goes
through it, so no call site here chooses a line set. Its own docstring carries the three-bucket
table; the summary is STATE on closed, reversal TIMING on emerging, and t3's two GATES on
`L2_GATE_MODE`, which is 'emerging'.

THREE BUCKETS - STATE ON CLOSED, REVERSAL TIMING ON EMERGING, t3'S GATES ON EMERGING. Joe's words:

    add all lines to csw1-12. these closed lines will give us more accurate fence/exfence baton
    decisions
    with ws1-12, emerg: time the reversals
    best of both worlds

    `C`  the CLOSED cws1r..cws12r set. Every STATE read: oob, ex-fence, the rider scan, the baton
         candidates, the baton-pass crosses, and the trajectory.
    `E`  the EMERGING ws1r..ws12r set. The reversal TIMING only - the rider's *"has reversed"*.

WHY IT MATTERS, measured on his own 2026-08-29 07:23 walk: emerging ws7r slips 80.11 -> 78.57
across 35 s and crosses below the 80 fence, which exhausted the walk 11 minutes early. Closed
cws7r reads 80.86 at both bars and does not move, because a 7-minute closed line steps only on its
own seam.

THE TRAJECTORY IS ON THE CLOSED LADDER, and that is MY reading, stated. He grouped the closed set
with *"fence/exfence baton decisions"*, and the trajectory is an input to the same decision as the
fence test - reading the fence on one ladder and the trajectory on the other for one decision would
split a single judgement across two line sets.

THE RIDER GATE DOES NOT END THE WALK. Joe 1026: *"drop the rider gate for t3 and t4"*, asked
whether t3 and t4 would fire after 2026-08-30 19:00 on a walk his 1025 spec had already killed:

    --IF no rider is assigned at the armed bar +5s
    ---the walk ends. pass to router for a rev-trade

That end is removed. With no rider the walk carries on to its cadences, and a rider is picked up at
the first cadence where the board offers one. t3 needs no rider at all - it is a board-level read -
and t4 becomes reachable once a rider exists.

WITH NO RIDER THE WHOLE BOARD IS THE CANDIDATE RANGE, ws1 to `L2_MOM_MAXTF`, and `lin_hop` does not
apply between cadences because there is no rung to hop FROM. That is the only reading available:
his hop rule is *"the max hops between a rider and a candidate baton receiver"*, and without a
rider there is no distance to measure. Stated, not defaulted.

THE ARM RACE READS CLOSED THROUGHOUT, 1026. I had left ws4r emerging on his 1025 spec and argued
that his *"more accurate fence/exfence baton decisions"* named baton decisions only. He corrected
it: *"1804 is printing the emerging value for ws4r. I thought we changed that"*. The arm's ws4r oob
test IS a fence read, so cws4r carries it and the whole race is on the closed set.

lin_hop APPLIES BETWEEN CADENCES, NOT AT ONE. Joe 1025, resolving the ws8->ws11 pass in his own
08-30 example: *"when baton is being passed between cadence markers, linhop applies. at a cadence
event, linhop doesn't apply"*, and the same for *"review the board from ws{riderTF} to
ws{v4mom-maxTF}"*.

CAUSAL. Every bar acted on is a cadence bar, a cross bar or a lift-off STAMP, and the asserts carry
that rather than comments.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import v4_knobs as K
import v4_fast as F
import v4_l2_cadence as CAD
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
from optimus9.analysis.jig import divergence, oob_ib_cross
from optimus9.compute.rule2_trajectory import opposed_extrema
sys.stderr = _e


def towards(BD, tf, bar, side):
    """Is ws{tf}r travelling TOWARD the target side at `bar`. -> bool.

    The banked v4 trajectory read, perspective = the target side. `travel` is the move from the
    block's opposed extreme to the bar, so a HIGH target wants travel > 0 and a LOW target
    travel < 0 - which is `v4_confluence.raw_traj`'s own `(travel > 0) if dr > 0 else (travel < 0)`
    with the trade direction replaced by the target side, his 1025 ruling.
    """
    bi, best, _ = opposed_extrema(BD.line(tf), int(side), int(bar), K.traj_block(tf))
    if bi is None:
        return False
    travel = BD.value(tf, bar) - best
    if not np.isfinite(travel):
        return False
    ok = (travel > 0) if int(side) > 0 else (travel < 0)
    bars = int(bar) - int(bi)
    return bool(ok and bars > K.traj_min_bars(tf) and abs(travel) >= float(K.TRAJ_MIN_TRAVEL))


def arm_race(CL, BD, side, frm, B):
    """*"race the arm"*. -> (the arm bar, which, why) or (None, None, why).

        --ws4r oob, or (cws1b + cws1r oob), or (cws2Mage + cws2r oob)

    The first bar at or after `frm` where any of the three qualifies. ALL THREE READ CLOSED LINES -
    his 1026 correction: *"1804 is printing the emerging value for ws4r. I thought we changed
    that"*. The arm's oob test is a fence read, so it belongs on the closed set with every other
    fence read in this fork.
    """
    r4 = BD.line(4)                                    # cws4r, CLOSED
    b1, c1r = np.asarray(CL['b'], float), np.asarray(CL['r'][1], float)
    c2m, c2r = np.asarray(CL['M'][2], float), np.asarray(CL['r'][2], float)
    for k in range(int(frm), int(B) + 1):
        if K.oob(r4[k], side):
            return k, 'cws4r', 'cws4r %.2f oob' % r4[k]
        if K.oob(b1[k], side) and K.oob(c1r[k], side):
            return k, 'cws1b+cws1r', 'cws1b %.2f + cws1r %.2f oob' % (b1[k], c1r[k])
        if K.oob(c2m[k], side) and K.oob(c2r[k], side):
            return k, 'cws2Mage+cws2r', 'cws2Mage %.2f + cws2r %.2f oob' % (c2m[k], c2r[k])
    return None, None, 'no arm to the window end'


def div_verdict(CL, close, side, bar):
    """The cws1r divergence verdict at or before `bar`. -> +1 bearish, -1 bullish, or None.

    Joe 1025: *"if cws2Mage + cws2r wins the race, check for a cws1r div and follow its verdict"*
    and *"for hi/lo, use the target-side"*. `jig.divergence` confirms at an episode END, so the
    verdict taken is the latest confirmed at or before the arm bar - causal, and asserted.
    """
    hi = K.OOB_HI if int(side) > 0 else 1e9       # the target-side fence only
    lo = K.OOB_LO if int(side) < 0 else -1e9
    got = [(int(b), int(v)) for b, v in divergence(np.asarray(CL['r'][1], float),
                                                   np.asarray(close, float), hi, lo)
           if int(b) <= int(bar)]
    if not got:
        return None
    b, v = got[-1]
    assert b <= int(bar), 'the divergence verdict is past the arm bar'
    return v


def rider_at(BD, side, bar, lo=1, hi=None):
    """The highest ws{TF}r that is ex-fence at `bar`. -> tf or None.

        --scan ws{1 to v4_mom_maxTF} for the highest ws{TF}r ex-fence, and make that TF the rider
    """
    hi = int(K.L2_MOM_MAXTF) if hi is None else int(hi)
    got = [t for t in range(int(lo), hi + 1) if t in BD.tfs and BD.ex_fence(t, bar, side)]
    return max(got) if got else None


def candidates(BD, side, bar, rider, cap=None):
    """Baton-pass candidates above `rider` at `bar`. -> [tf], lowest first.

        -baton can only be received by an r line that is 1) ex v4mom-fnc and 2) tagged as `towards`

    `cap` is the top rung allowed: rider + `L2_LIN_HOP` between cadences, `L2_MOM_MAXTF` at one.
    """
    top = int(K.L2_MOM_MAXTF) if cap is None else min(int(cap), int(K.L2_MOM_MAXTF))
    return [t for t in range(int(rider) + 1, top + 1)
            if t in BD.tfs and BD.ex_fence(t, bar, side) and towards(BD, t, bar, side)]


def _pass_bars(BD, tf, side, frm, B):
    """The bars ws{tf}r hands the baton on, between cadences. -> a sorted list.

        --1) rider was oob and has crossed to ib
        --2) rider was between ex-v4mom-fnc and oob, and crossed to in-v4mom-fnc
    """
    v = BD.line(tf)
    out = [int(c) for c, _cf, s in oob_ib_cross(v, K.OOB_HI, K.OOB_LO, 1)
           if s == int(side) and int(frm) <= c <= int(B)]
    #   (2) the ex-fence -> in-fence cross, on the target side
    ex = np.array([K.ex_fence(x, side) for x in v], bool)
    for k in range(max(1, int(frm)), int(B) + 1):
        if ex[k - 1] and not ex[k]:
            out.append(int(k))
    return sorted(set(out))


def walk(CL, BD, close, side, frm, B, trace=None):
    """One lineage2 walk. -> (the verdict, the bar, the rows).

        CL  the closed c-set from v4_core_arm.lines() plus 'M' - cws1b, cws1r, cws2r, cws2Mage
        BD  a `v4_l2_proxy.Board`, which owns both r ladders and the routing between them

    The arm race, then the rider, then one decision per cadence bar until a verdict.
    """
    rows = []

    def row(**kw):
        rows.append(kw)
        if trace is not None:
            trace.append(kw)

    arm, which, why = arm_race(CL, BD, side, frm, B)   # all three on the CLOSED set, 1026
    if arm is None:
        row(bar=None, stage='NO ARM', why=why)
        return 'NO ARM', None, rows
    row(bar=arm, stage='ARM', why='%s: %s' % (which, why))

    if which == 'cws2Mage+cws2r':
        v = div_verdict(CL, close, side, arm)
        #   *"if the open trade ... is SHORT and the verdict is +1, the verdict is AGAINST the
        #   SHORT and router will create a rev-trade"*. A SHORT is side +1 here, so a +1 verdict
        #   against a +1 side is the rev-trade; aligned means take no action.
        row(bar=arm, stage='DIV', why='cws1r divergence %s' % ('none' if v is None else
                                      ('+1 bearish' if v > 0 else '-1 bullish')))
        if v is not None and ((v > 0 and int(side) > 0) or (v < 0 and int(side) < 0)):
            return 'DIV REV-TRADE', int(arm), rows

    rider = rider_at(BD, side, arm)
    if rider is None:
        #   HIS 1026 RULING: this no longer ends the walk - *"drop the rider gate for t3 and t4"*
        row(bar=arm + 1, stage='NO RIDER', why='no cws1..cws%d r is ex-fence at the arm bar + 5s -'
                                               ' the walk continues, t3 and t4 stay reachable'
                                               % K.L2_MOM_MAXTF)
    else:
        row(bar=arm, stage='RIDER', why='cws%d r %.2f, the highest ex-fence'
                                        % (rider, BD.value(rider, arm)))

    cads = sorted(CAD.t1(CL, side, arm, B) + CAD.t2(CL, side, arm, B)
                  + CAD.t3(BD, side, arm, B), key=lambda z: z[0])
    cads = [(b, w) for b, w in cads if b >= arm]
    last = int(arm)
    for bar, cwhy in cads:
        if rider is None:
            #   NO RIDER YET. The whole board is in range and lin_hop does not apply - there is no
            #   rung to hop FROM. A t3 at this bar still ends the walk below.
            got = candidates(BD, side, bar, 0)
            if got:
                rider = max(got)
                last = int(bar)
                row(bar=bar, stage='RIDER', why='%s | cws%d r %.2f picked up at a cadence, no'
                                                ' prior rider'
                                                % (cwhy, rider, BD.value(rider, bar)))
                continue
            if cwhy.startswith('t3'):
                row(bar=bar, stage='EXHAUST', why='t3 with no rider - %s' % cwhy)
                return 'EXHAUST', int(bar), rows
            row(bar=bar, stage='NO RIDER', why='%s | still no ex-fence line on the whole board'
                                               % cwhy)
            last = int(bar)
            continue
        #   BETWEEN the cadences the baton moves invisibly, under lin_hop
        while True:
            pb = [b for b in _pass_bars(BD, rider, side, last + 1, bar)]
            if not pb:
                break
            got = candidates(BD, side, pb[0], rider, cap=rider + int(K.L2_LIN_HOP))
            if not got:
                break
            row(bar=pb[0], stage='BATON', why='ws%d -> ws%d, between cadences, lin_hop %d'
                                              % (rider, max(got), K.L2_LIN_HOP))
            rider = max(got)
            last = pb[0]
        rv = BD.value(rider, bar)                      # STATE: closed, via the proxy
        no_ex = not BD.ex_fence(rider, bar, side)
        revd = BD.reversed_in(rider, side, last, bar)  # TIMING: emerging, via the proxy
        #   AT a cadence, lin_hop does not apply - the whole board above the rider is in range
        got = candidates(BD, side, bar, rider)
        row(bar=bar, stage='CADENCE', why='%s | rider cws%d %.2f, no-longer-exfence %s, reversed %s'
                                          % (cwhy, rider, rv, 'yes' if no_ex else 'no',
                                             'yes' if revd else 'no'),
            cands=tuple(got))
        if got:
            row(bar=bar, stage='BATON', why='ws%d -> ws%d, at a cadence, whole board'
                                            % (rider, max(got)))
            rider = max(got)
            last = int(bar)
            continue
        if BD.oob(rider, bar, side) or (not no_ex and not revd):
            row(bar=bar, stage='HOLD', why='rider cws%d %.2f %s - no action' % (
                rider, rv, 'oob' if BD.oob(rider, bar, side) else 'ex-fence and not reversed'))
            last = int(bar)
            continue
        if no_ex or revd:
            #   t4cadence: a non-oob rider that reversed with nowhere to pass
            tag = 't4' if (revd and not BD.oob(rider, bar, side)) else 'exhaust'
            row(bar=bar, stage='EXHAUST', why='%s - rider cws%d %.2f, no candidate on the whole board'
                                              % (tag, rider, rv))
            return 'EXHAUST', int(bar), rows
    row(bar=None, stage='NO VERDICT', why='%d cadence(s) and no exhaust to the window end'
                                          % len(cads))
    return 'NO VERDICT', None, rows
