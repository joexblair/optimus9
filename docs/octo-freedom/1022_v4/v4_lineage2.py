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
lines. `jig.away_toward` is a DIFFERENT read and is not used here: it tags a Mage trajectory, not
an r trajectory. Its perspective was ws1Mage's until 1027, when he settled it for the third time -
*"the actual toward/away perspective comes from the open (or invisible-incoming, if no trade is
open) trade: use the target-side"* - which is the same side this file already passes to `towards`.
WHETHER LINEAGE2'S CANDIDATE TEST SHOULD USE IT INSTEAD IS HIS, UNRULED. He said on 1027 that
*"ws9r should be holding an `away` tag at the t2"*, and at that bar the trajectory read says
`towards: yes`, so the two reads disagree on that line.

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

lin_hop IS LIFTED ONLY AT A t1 OR t2 CADENCE. Joe 1025 first: *"when baton is being passed between
cadence markers, linhop applies. at a cadence event, linhop doesn't apply"*. Then 1026, narrowing
it: *"jumping belongs only to t1 and t2"* / *"the t1 and t2 cadence is where we get to make
larger-that-linhop jumps"*. So:

    between cadences   riderTF + 1 .. riderTF + L2_LIN_HOP
    at a t1 or t2      riderTF + 1 .. L2_MOM_MAXTF - the whole board
    at a t3 or t4      riderTF + 1 .. riderTF + L2_LIN_HOP - no jump

WHAT t3 AND t4 ARE FOR, his 1026 words: *"t3 and t4 cadences exist primarily for uniformity: we
need the cadences to make decisions - without a cadence event, the walk would run past an
actionable set-up. the 08-30 1915 example highlights this"*.

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
from optimus9.analysis.jig import anchor_floater, lift_off, mage_cascade, oob_ib_cross
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
    """The cws1r divergence verdict AT `bar`. -> +1 bearish, -1 bullish, or None.

    Joe 1025: *"if cws2Mage + cws2r wins the race, check for a cws1r div and follow its verdict"*.

    MOVED OFF `jig.divergence` ON HIS 1026 WORD: *"good catch - move it to anchor_floater"*, after
    he ruled *"I instructed to not use jig.divergence"* and had it pseudo-disabled. `anchor_floater`
    IS the divergence read - it runs his four-step 0912 selection (anchor at the bar, the pivot,
    then the floater) and returns the comparison. `jig.divergence` is step 4 alone and cannot choose
    what to compare.

    THE `dr` IS THE TARGET SIDE, his 1026 ruling in one word: *"that will be target-side"*. Asked
    whether to pass `-side` or `+side`, that is `+side` - the walk's own target side, unchanged.

    THE RETURN CONVENTION DOES NOT MOVE. `anchor_floater`'s `state` is already +1 for a divergence
    supporting a SHORT - bearish - and -1 for one supporting a LONG, which is exactly what this
    function returned from `sig` before. So the caller's rev-trade comparison is untouched, and no
    sign was re-derived here.

    PM IS NOT A VERDICT. `abs(state) == 2` is price-matched - price and the oscillator AGREE, the
    trend continuing - which is the opposite of a divergence, so it returns None alongside `state`
    0 (inside AF_SLOPE_FLOOR). MINE and stated: the old read had no way to express PM at all, so
    these firings used to be invisible rather than refused.

    AT THE BAR, not at or before it. `jig.divergence` confirmed at an episode END, so the old read
    had to walk back to the latest confirmed one. `anchor_floater` reads AT `bar` and its own
    contract is *"CAUSAL. Every bar read is <= k"*, so the verdict is the arm bar's own.
    """
    got = anchor_floater(np.asarray(CL['r'][1], float), np.asarray(close, float),
                         int(side), int(bar))
    if got is None:
        return None
    st = int(got['state'])
    assert int(got['anchor'][0]) == int(bar), 'the divergence anchor is not the bar it was read on'
    return st if abs(st) == 1 else None


def div_state(CL, close, side, bar):
    """The RAW `anchor_floater` state at `bar`, unfiltered. -> int or None.

    `div_verdict` collapses PM and the noise band to None, which is right for the verdict and wrong
    for a tally: a PM firing and no reading at all become the same row. This returns the state so a
    report can separate them. It decides nothing.
    """
    got = anchor_floater(np.asarray(CL['r'][1], float), np.asarray(close, float),
                         int(side), int(bar))
    return None if got is None else int(got['state'])


def arm_retest(CL, side, arm, B):
    """v4-arm-lineage-retest's gate. -> (the cadence bar, why) or (None, why).

    HIS SPEC, 1026, verbatim:

        fire at arm:
        if cws1r is oob at arm
        -if cws2r and cws3r are in mom-fnc
        --walk cws1r to handover (ib) and follow the lineage process
        --if an exhaust is found, route to rev-trade

    and *"I'm adding arm as a cadence"*, narrowed by him to *"the gate's cadence is the cws1r
    oob->ib cross bar"* - so the arm OPENS the gate and decides nothing itself. At the arm cws1r is
    oob by definition of the gate, which is the board review's first HOLD branch.

    HIS NINE RULINGS, each one his and none of them mine:

        1  the ladder          CLOSED cws - *"my error: I meant to use cws, not ws"*
        2  "in mom-fnc"        not ex-fence on the TARGET side
        3  when 2 and 3 read   the arm bar only
        4  "handover (ib)"     the oob->ib cross only, not the second pass rule
        5  the wob             L2_CWS1R_WOB 1 bar = 5 s - SUPERSEDED 1027 by LIN2_CROSS_WOB 12
        6  the rider there     *"re-scan and ride the highest"*
        7  what this is        a gate in the walk; the other three mechs are off for lineage2 work
        8  the cadence bar     the cws1r oob->ib cross bar
        9  no cap              *"if cws1r is oob, it has no choice but to cross to ib"*
    """
    c1r = np.asarray(CL['r'][1], float)
    c2r = np.asarray(CL['r'][2], float)
    c3r = np.asarray(CL['r'][3], float)
    k = int(arm)
    if not K.oob(c1r[k], side):
        return None, 'cws1r %.2f is not oob at the arm - the gate stays shut' % c1r[k]
    if K.ex_fence(c2r[k], side) or K.ex_fence(c3r[k], side):
        return None, ('cws2r %.2f / cws3r %.2f - not both inside the fence at the arm'
                      % (c2r[k], c3r[k]))
    #   RULING 4 and 5: the oob->ib cross only, wob L2_CWS1R_WOB. `oob_ib_cross`'s third field is
    #   the oob side the run LEFT, which for this gate is the target side.
    #   WOB 12, Joe 1027: *"add the wob12 to all crosses to ib"*. This SUPERSEDES his own 1026
    #   ruling on the retest's gap 5, where he accepted L2_CWS1R_WOB 1 for this cross.
    xs = [(c, cf) for c, cf, sd in oob_ib_cross(c1r, K.OOB_HI, K.OOB_LO, int(K.LIN2_CROSS_WOB))
          if int(sd) == int(side) and int(cf) >= k]
    if not xs:
        return None, ('cws1r %.2f oob, cws2r %.2f + cws3r %.2f in - open, but no cws1r oob->ib'
                      ' cross to the data end' % (c1r[k], c2r[k], c3r[k]))
    cross, conf = int(xs[0][0]), int(xs[0][1])
    assert conf >= k, 'the retest cadence is before the arm that opened the gate'
    return conf, ('cws1r %.2f oob + cws2r %.2f / cws3r %.2f in - the gate opens; cws1r oob->ib'
                  ' cross %s, wob %d, cadence at %s'
                  % (c1r[k], c2r[k], c3r[k], ln.U(cross), K.LIN2_CROSS_WOB, ln.U(conf)))


def rider_at(BD, side, bar, lo=1, hi=None):
    """The highest ws{TF}r that is ex-fence at `bar`. -> tf or None.

        --scan ws{1 to v4_mom_maxTF} for the highest ws{TF}r ex-fence, and make that TF the rider
    """
    hi = int(K.L2_MOM_MAXTF) if hi is None else int(hi)
    got = [t for t in range(int(lo), hi + 1) if t in BD.tfs and BD.ex_fence(t, bar, side)]
    return max(got) if got else None


def _nrs(rider_since, arm):
    """The bar `LIN2_CAND_NOT_REVERSED` measures a candidate's reversals from. -> bar or None."""
    m = int(K.LIN2_CAND_NOT_REVERSED)
    return None if m == 0 else (int(rider_since) if m == 1 else int(arm))


def candidates(BD, side, bar, rider, cap=None, not_rev_since=None):
    """Baton-pass candidates above `rider` at `bar`. -> [tf], lowest first.

        -baton can only be received by an r line that is 1) ex v4mom-fnc and 2) tagged as `towards`

    `cap` is the top rung allowed: rider + `L2_LIN_HOP` between cadences, `L2_MOM_MAXTF` at one.

    `not_rev_since` is the THIRD TERM, OFF by default - `LIN2_CAND_NOT_REVERSED` 0. When a bar is
    passed, a rung is excluded if it has a reversal STAMPED in (not_rev_since, bar]. Joe 1027 asked
    for it as a test after 2026-08-30 11:33:00, where ws12r received the baton at 82.87 while
    carrying a reversal stamped 11:23:40. `towards` is a trajectory read and does not exclude a
    reversed line: a rung can lift off its extreme and still show net travel toward the side.
    The wob is LIN2_REV_WOB 12, MY choice - he named none for this term.
    """
    top = int(K.L2_MOM_MAXTF) if cap is None else min(int(cap), int(K.L2_MOM_MAXTF))
    out = [t for t in range(int(rider) + 1, top + 1)
           if t in BD.tfs and BD.ex_fence(t, bar, side) and towards(BD, t, bar, side)]
    if not_rev_since is None or not out:
        return out
    keep = []
    for t in out:
        revs = [int(b) + max(1, int(K.LIN2_REV_WOB)) - 1
                for b in lift_off(BD.E[int(t)], int(side), K.LIFT_PTS, K.gap_for(int(t)),
                                  K.LIFT_TOL, int(K.LIN2_REV_WOB))]
        if not any(int(not_rev_since) < st <= int(bar) for st in revs):
            keep.append(t)
    return keep


_PB = {}


def _pass_bars(BD, tf, side, frm, B):
    """The bars ws{tf}r hands the baton on, between cadences. -> a sorted list.

        --1) rider was oob and has crossed to ib
        --2) rider was between ex-v4mom-fnc and oob, and crossed to in-v4mom-fnc
    """
    #   CACHED OVER THE WHOLE TAPE, then sliced. The uncached form rebuilt `oob_ib_cross` over
    #   1.6M bars on every call, and the bar-loop walk calls it once per bar.
    key = (id(BD), int(tf), int(side))
    if key not in _PB:
        v = BD.line(tf)
        w = max(1, int(K.LIN2_CROSS_WOB))
        #   RULE 1, oob -> ib, WITH WOB 12 - Joe 1027. The pass bar is the cross's CONFIRM bar,
        #   c + w - 1, which is the first bar the ib state has held for w bars.
        a = [int(cf) for _c, cf, s in oob_ib_cross(v, K.OOB_HI, K.OOB_LO, w) if s == int(side)]
        #   RULE 2, ex-fence -> in-mom-fnc, WITH THE SAME WOB. The edge is where ex-fence turns
        #   off; the pass bar is edge + w - 1, and only if in-fence held every bar of that window.
        ex = np.array([K.ex_fence(x, side) for x in v], bool)
        edges = (np.flatnonzero(ex[:-1] & ~ex[1:]) + 1).astype(int)
        b = []
        for e in edges:
            e = int(e)
            if e + w - 1 >= len(ex):
                continue
            if not ex[e:e + w].any():              # in-fence for the whole hold
                b.append(e + w - 1)
        _PB[key] = (np.array(sorted(set(a) | set(b)), dtype=int), set(a), set(b))
    arr = _PB[key][0]
    i = int(np.searchsorted(arr, int(frm)))
    j = int(np.searchsorted(arr, int(B), side='right'))
    return [int(x) for x in arr[i:j]]


def pass_why(BD, tf, side, bar):
    """Which of the two rules made `bar` a pass bar for ws{tf}r. -> a string.

        --1) rider was oob and has crossed to ib
        --2) rider was between ex-v4mom-fnc and oob, and crossed to in-v4mom-fnc

    BOTH CARRY LIN2_CROSS_WOB 12 since 1027, so the bar reported is the last bar of the hold, not
    the cross itself. Reads the same cache `_pass_bars` built, so the two can never disagree.
    """
    key = (id(BD), int(tf), int(side))
    if key not in _PB:
        _pass_bars(BD, tf, side, 0, 0)
    _arr, a, b = _PB[key]
    hit = []
    if int(bar) in a:
        hit.append('oob -> ib, held %d bars' % K.LIN2_CROSS_WOB)
    if int(bar) in b:
        hit.append('ex-fence -> in-fence, held %d bars' % K.LIN2_CROSS_WOB)
    return ' + '.join(hit) or 'not a pass bar'


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
        st = div_state(CL, close, side, arm)
        row(bar=arm, stage='DIV', state=st,
            why='cws1r divergence %s | anchor_floater state %s' % (
                ('none' if v is None else ('+1 bearish' if v > 0 else '-1 bullish')),
                'no reading' if st is None else
                {1: '+1 divergence, SHORT', -1: '-1 divergence, LONG',
                 2: '+2 PM, trend SHORT', -2: '-2 PM, trend LONG',
                 0: '0 inside AF_SLOPE_FLOOR'}.get(st, str(st))))
        if v is not None and ((v > 0 and int(side) > 0) or (v < 0 and int(side) < 0)):
            return 'DIV REV-TRADE', int(arm), rows

    rider = rider_at(BD, side, arm)
    rider_since = int(arm)                             # the bar the CURRENT rider took the baton
    if rider is None:
        #   HIS 1026 RULING: this no longer ends the walk - *"drop the rider gate for t3 and t4"*
        row(bar=arm + 1, stage='NO RIDER', why='no cws1..cws%d r is ex-fence at the arm bar + 5s -'
                                               ' the walk continues, t3 and t4 stay reachable'
                                               % K.L2_MOM_MAXTF)
    else:
        row(bar=arm, stage='RIDER', why='cws%d r %.2f, the highest ex-fence'
                                        % (rider, BD.value(rider, arm)), rider=rider)

    #   v4-arm-lineage-retest. While the gate is open nothing else decides, so the walk starts at
    #   the gate's own cadence and the cadences before it are not served. His flow: *"the gate is
    #   open ... nothing is tested again until it moves"*.
    start = int(arm)
    if int(K.L2_ARM_RETEST):
        rt, rt_why = arm_retest(CL, side, arm, B)
        row(bar=arm, stage='RETEST', why=rt_why)
        if rt is not None:
            nr = rider_at(BD, side, rt)                # RULING 6: re-scan and ride the highest
            if nr is None:
                #   HIS OWN SPEC LINE, reached at the gate's cadence instead of at the arm:
                #   *"IF no rider is assigned ... the walk ends. pass to router for a rev-trade"*.
                row(bar=rt, stage='EXHAUST',
                    why='v4-arm-lineage-retest: no cws1..cws%d r is ex-fence at the gate cadence -'
                        ' the walk ends' % K.L2_MOM_MAXTF, rider=rider, ctype='retest')
                return 'EXHAUST', int(rt), rows
            row(bar=rt, stage='RIDER',
                why='v4-arm-lineage-retest: the re-scan rides cws%d %.2f, the highest ex-fence'
                    % (nr, BD.value(nr, rt)), rider=nr, ctype='retest')
            rider, start = int(nr), int(rt)

    #   THE MAGE-CASCADE VERDICT AT EVERY CADENCE, Joe 1027: *"in fact, let's get the mage-cascde
    #   verdict at every cadence event"*. It is RECORDED, not acted on - he has not ruled what the
    #   walk does with it. His own shape for that is *"get a mage-verdict, and if its verdict
    #   matches the trade direction then take no action (ie keep walking)"*, which is a SECOND
    #   ruling he has not yet given.
    def cascade_at(k):
        if BD.mage is None:
            return 'no Mage ladder'
        try:
            c = mage_cascade(BD.mage, int(k), tf_lo=min(BD.mage), tf_hi=max(BD.mage),
                             zoom=K.SAV_CASCADE_ZOOM, min_lines=K.SAV_CASCADE_MIN)
        except Exception as ex:
            return 'cascade failed %r' % ex
        return 'none' if c is None else str(c['verdict'])

    #   t1 and t2 read only cws1b and cws1r, so they are precomputed. t3 needs the live rider.
    fixed = {}
    #   t1, t2 and his 1026 cws1b counter-oob cadence all read only cws1b and cws1r, so all three
    #   are precomputed. Only the latch needs the live rider.
    #   THE BARRAGE joins them, Joe 1027: *"bank the barrage results and wire the mech into the
    #   chain"*. It reads the emerging ws1Mage and the emerging r ladder off the Board, so it is
    #   precomputed with the rest - it needs no rider.
    produced = (CAD.t1(CL, side, arm, B) + CAD.t2(CL, side, arm, B)
                + (CAD.counter_oob(CL, side, arm, B) if int(K.LIN2_COUNTER_OOB_ON) else [])
                + (CAD.barrage(BD, side, arm, B) if int(K.LIN2_BARRAGE_ON) else []))
    for b, ty, w in produced:
        if b >= start:
            fixed.setdefault(int(b), []).append((ty, w))
    t3_on, lat_on, last = False, False, int(start)
    #   t3's population is measured SINCE THE ARM - his 1026 ruling *"tested since the arm"* - so
    #   the retest moving the walk's start does not move t3's origin.
    t3 = CAD.T3(BD, side, arm)
    #   THE t3 REPLACEMENT, his 1026 2-staged latch. L2_T3_ON is banked 0 and LIN2_LATCH_ON 1, so
    #   this is the live mech and t3 is the A/B arm.
    lat = CAD.Latch(BD, side, arm)
    #   A PASS BAR THAT FINDS NOTHING leaves `last` where it is, so the loop re-reads the same bar
    #   on every later bar and breaks again. Recording it once makes the attempt visible; the
    #   break is unchanged, so no decision moves.
    tried = set()

    for bar in range(int(start), int(B) + 1):
        #   BETWEEN the cadences the baton moves invisibly, under lin_hop
        if rider is not None:
            while True:
                pb = [x for x in _pass_bars(BD, rider, side, last + 1, bar) if x <= bar]
                if not pb:
                    break
                got = candidates(BD, side, pb[0], rider, cap=rider + int(K.L2_LIN_HOP),
                                 not_rev_since=_nrs(rider_since, arm))
                if not got:
                    if (int(pb[0]), int(rider)) not in tried:
                        tried.add((int(pb[0]), int(rider)))
                        row(bar=pb[0], stage='NO PASS',
                            why='cws%d %.2f ATTEMPTS to hand over, between cadences - no'
                                ' candidate inside lin_hop %d'
                                % (rider, BD.value(rider, pb[0]), K.L2_LIN_HOP),
                            rider=rider, cands=(), cap=rider + int(K.L2_LIN_HOP),
                            ctype='between')
                    break
                row(bar=pb[0], stage='BATON', why='ws%d -> ws%d, between cadences, lin_hop %d'
                                                  % (rider, max(got), K.L2_LIN_HOP),
                    rider=rider, to=max(got), cands=tuple(got),
                    cap=rider + int(K.L2_LIN_HOP), ctype='between')
                rider = max(got)
                rider_since = int(pb[0])
                last = pb[0]

        #   WHICH CADENCES FIRE AT THIS BAR. t3 is the RISING EDGE of its own condition, so the
        #   state is carried across bars - without that it would fire on every bar it holds.
        here = list(fixed.get(bar, ()))
        if int(K.L2_T3_ON):
            t3.advance(bar)
            if rider is not None:
                ok, t3why = t3.at(bar, rider)
                if ok and not t3_on:
                    here.append(('t3', t3why))
                t3_on = ok
        #   LATCH 1 reads at every cadence bar - his *"2, at the cadence bar"*. It is armed
        #   BEFORE the cadence is served, so a latch-2 completion on the same bar can see it.
        if int(K.LIN2_LATCH_ON) and here:
            st = div_verdict(CL, close, side, bar)
            ok1, w1 = lat.arm1(bar, st, here[0][0])
            if ok1:
                row(bar=bar, stage='LATCH1', why=w1, rider=rider)

        #   LATCH 2 is the cadence t3 used to be: the RISING EDGE of its own condition, tested on
        #   every bar, and completing it exhausts the walk.
        if int(K.LIN2_LATCH_ON) and rider is not None and lat.live(bar):
            cap2 = int(rider) + int(K.L2_LIN_HOP)
            ok2, w2 = lat.at(bar, rider,
                             lambda: candidates(BD, side, bar, rider, cap=cap2))
            if ok2 and not lat_on:
                here.append(('latch', w2))
            lat_on = ok2
        elif lat_on:
            lat_on = False                             # the latch expired; re-arm the rising edge

        if not here:
            continue

        for ctype, cwhy in here:
            #   THE BARRAGE EXHAUSTS, and it is served BEFORE the cascade table. Joe 1027, asked
            #   whether it declares exhaust or fires as a cadence and lets the board review decide:
            #   *"both - a cadence keeps the walk's transactions uniform, and exhaust will fire"*.
            #   So the row is a cadence row AND the walk ends on it.
            #   WHY IT IS AHEAD OF THE CASCADE, AND THE READING IS MINE: a cascade verdict that
            #   MATCHES the trade takes no action, which would veto an exhaust he said WILL fire.
            #   Reading his sentence literally puts the barrage first. The cascade verdict is still
            #   recorded on the row so the other arm is measurable.
            if ctype == 'barrage':
                row(bar=bar, stage='EXHAUST', rider=rider, ctype=ctype,
                    why='barrage %s | mage-cascade %s | the walk ends' % (cwhy, cascade_at(bar)))
                return 'EXHAUST', int(bar), rows
            #   THE MAGE-CASCADE AT THE CADENCE. Joe 1027 gave the whole truth table, verbatim:
            #       if the trade is long and the verdict is up, take no action
            #       if the trade is long and the verdict is down, rev-trade
            #       if the trade is short and the verdict is up, rev-trade
            #       if the trade is short and and the verdict is down, take no action
            #   and `neither` is his earlier *"let the cadence decide"*.
            #   TRUST THE VERDICT, DO NOT RE-DERIVE IT. Joe 1027: *"trust the mage cascade's
            #   verdict - it's been validated many times. the issue isn't in mage cascade, it's how
            #   the mage-cascade is applied"*. `jig.mage_cascade` says `up` is the ladder RISING
            #   with TF and refuses to map it - *"NO dr IN OR OUT. A consumer maps `verdict` onto
            #   its own trade side"*. This table IS that mapping, and it is his.
            #   A MISMATCH REV-TRADES. It does not fall through to the board review, which is what
            #   the first build did.
            #   THE cws1b COUNTER-OOB CADENCE IS EXEMPT FROM NO ACTION ONLY, Joe 1027: *"cws1b
            #   counter-oob needs to fire immediately. the logic: if b is printing on the non target
            #   oob, the trade has failed and we need to recover lost profit asap"*. A mismatch still
            #   rev-trades on it, because that is an exit either way.
            if int(K.LIN2_CASCADE_NO_ACTION):
                mv = cascade_at(bar)
                lng = int(side) > 0                    # target side HIGH is a LONG
                if (mv == 'up' and not lng) or (mv == 'down' and lng):
                    #   THE KNOB IS NARROWED TO THE cws1b COUNTER-OOB CADENCE, Joe 1027:
                    #   *"narrow it - applies only to cws1b counter oob"*. Every other cadence
                    #   type always rev-trades on a mismatch.
                    act = (str(K.LIN2_MISMATCH_ACTION) if ctype == 'cws1b counter-oob'
                           else 'rev-trade')
                    row(bar=bar, stage='EXHAUST', rider=rider, ctype=ctype, mismatch=True,
                        why='%s %s | mage-cascade %s OPPOSES the %s - %s'
                            % (ctype, cwhy, mv, 'LONG' if lng else 'SHORT', act))
                    return ('CLOSE ONLY' if act == 'close-only' else 'EXHAUST'), int(bar), rows
                if ((mv == 'up' and lng) or (mv == 'down' and not lng)) \
                        and ctype != 'cws1b counter-oob':
                    row(bar=bar, stage='NO ACTION', rider=rider, ctype=ctype,
                        why='%s %s | mage-cascade %s matches the %s - no action, keep walking'
                            % (ctype, cwhy, mv, 'LONG' if lng else 'SHORT'))
                    last = int(bar)
                    continue
            if rider is None:
                got = candidates(BD, side, bar, 0)
                if got:
                    rider = max(got)
                    last = int(bar)
                    row(bar=bar, stage='RIDER',
                        why='%s %s | cws%d r %.2f picked up at a cadence, no prior rider'
                            % (ctype, cwhy, rider, BD.value(rider, bar)), rider=rider)
                    continue
                row(bar=bar, stage='NO RIDER',
                    why='%s %s | still no ex-fence line on the whole board' % (ctype, cwhy))
                last = int(bar)
                continue

            rv = BD.value(rider, bar)                      # STATE: closed, via the proxy
            no_ex = not BD.ex_fence(rider, bar, side)
            revd = BD.reversed_in(rider, side, last, bar)  # TIMING: emerging, via the proxy
            #   HIS 1026 RULING: only t1 and t2 lift lin_hop
            cap = None if ctype in ('t1', 't2') else rider + int(K.L2_LIN_HOP)
            got = candidates(BD, side, bar, rider, cap=cap,
                             not_rev_since=_nrs(rider_since, arm))
            row(bar=bar, stage='CADENCE',
                why='%s %s | rider cws%d %.2f, no-longer-exfence %s, reversed %s | mage-cascade %s'
                    % (ctype, cwhy, rider, rv, 'yes' if no_ex else 'no', 'yes' if revd else 'no',
                       cascade_at(bar)),
                cands=tuple(got), rider=rider, cap=cap, ctype=ctype)
            if got:
                row(bar=bar, stage='BATON',
                    why='ws%d -> ws%d, at a %s cadence, %s'
                        % (rider, max(got), ctype,
                           'whole board' if cap is None
                           else 'capped at ws%d by lin_hop %d' % (cap, K.L2_LIN_HOP)),
                    rider=rider, to=max(got), cands=tuple(got), cap=cap, ctype=ctype)
                rider = max(got)
                rider_since = int(bar)
                last = int(bar)
                continue
            if BD.oob(rider, bar, side) or (not no_ex and not revd):
                row(bar=bar, stage='HOLD', why='rider cws%d %.2f %s - no action' % (
                    rider, rv, 'oob' if BD.oob(rider, bar, side) else 'ex-fence and not reversed'),
                    rider=rider)
                last = int(bar)
                continue
            #   t4cadence: a non-oob rider that reversed with nowhere to pass
            tag = 't4' if (revd and not BD.oob(rider, bar, side)) else 'exhaust'
            row(bar=bar, stage='EXHAUST',
                why='%s at a %s cadence - rider cws%d %.2f, no candidate %s'
                    % (tag, ctype, rider, rv,
                       'on the whole board' if cap is None else 'inside lin_hop %d' % K.L2_LIN_HOP),
                rider=rider, cap=cap, ctype=ctype)
            return 'EXHAUST', int(bar), rows

    row(bar=None, stage='NO VERDICT', why='no exhaust to the window end')
    return 'NO VERDICT', None, rows
