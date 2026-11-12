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
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever
#   happens. Without it a refusal from v4_knobs.check() - an off-ruled run with no
#   W_V4_EXPERIMENT=1 - goes into the StringIO and the process exits 1 with NOTHING on
#   either stream. That cost a diagnosis on 1101.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import ln
    from optimus9.analysis.jig import anchor_floater, lift_off, mage_cascade, oob_ib_cross, mage_cascade_bar, MC_GAP
    import v4_lift_e as LE   # HIS 1110 e-cross reversal: every lift-off reader gets it (6B)
    from optimus9.compute.rule2_trajectory import opposed_extrema
finally:
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
    r4 = BD.line(4)                                    # ws4r, the LIVE value via the proxy
    c1r, c2r = np.asarray(CL['r'][1], float), np.asarray(CL['r'][2], float)
    c3r = np.asarray(CL['r'][3], float)
    c2m = np.asarray(CL['M'][2], float)
    #   CONDITION 2's b LINE, his 1031 update: *"gcws30b ex=5/95-fence replaces ws1b oob"*. Both
    #   lines sit in CL so LIN2_ARM_B_LINE picks one here and LIN2_T1_B_LINE picks for t1
    #   independently.
    akey = {'ws1b': 'b', 'gcws30b': 'g30b'}[str(K.LIN2_ARM_B_LINE)]
    b1 = np.asarray(CL[akey], float)
    newb = akey != 'b'
    if newb:
        #   HIS THREE wob-6 USES MAP ONTO THE TWO EDGES `b1_beyond` ALREADY OWNS: *"gcws30b uses a
        #   wob 6 for both to-oob and to-ib crosses, and for the dwell in ex-95/5-fence"*. The
        #   to-oob cross hold and the dwell beyond the fence are the SAME 6 bars - a cross that
        #   holds 6 bars past the fence IS a 6-bar dwell - so the entry takes 6 and the return
        #   takes 6. If he means three independent counts, the third needs its own knob.
        aw = max(1, int(K.LIN2_ARM_B_WOB))
        alo, ahi = 100.0 - float(K.LIN2_ARM_B_FNC), float(K.LIN2_ARM_B_FNC)
        b1o = np.asarray(CAD.b1_beyond(b1, int(side), hold=aw, dwell=aw,
                                       mask=K.beyond_mask(b1, int(side), alo, ahi)), bool)
    else:
        #   cws1b's oob READ THROUGH ITS ONE STATE, so his 1030 dwell reaches the arm as well as
        #   the cadences. At LIN2_B1_OOB_DWELL 0 and LIN2_B1_HOLD 0 this is K.oob bar for bar.
        alo, ahi, aw = K.OOB_LO, K.OOB_HI, int(K.LIN2_CROSS_WOB)
        b1o = np.asarray(CAD.b1_beyond(b1, int(side)), bool)
    w3 = bool(int(K.LIN2_ARM_WS3R_ON))
    for k in range(int(frm), int(B) + 1):
        if K.oob(r4[k], side):
            return k, 'ws4r', 'ws4r %.2f oob' % r4[k]
        #   HIS 1031 ARM: the b line beyond its own fence, AND at least one r line oob. His
        #   revision, verbatim: *"(ws1r or ws2r) + gcws30b"* - the r lines are an OR, not the
        #   conjunction his first wording read as. ws3r joins the SAME OR group at
        #   LIN2_ARM_WS3R_ON, because that is where his "add ws3r to the existing ws1r oob" puts
        #   it once the group is an OR.
        #   THE PRE-1031 ws1b ARM IS UNTOUCHED: it is ws1b oob AND ws1r oob, no OR and no ws2r.
        rgrp = (K.oob(c1r[k], side) or K.oob(c2r[k], side)
                or (w3 and K.oob(c3r[k], side))) if newb else K.oob(c1r[k], side)
        if b1o[k] and rgrp:
            assert newb or int(K.LIN2_B1_OOB_DWELL) > 1 or int(K.LIN2_B1_HOLD) > 1 \
                or K.oob(b1[k], side), \
                'ws1b arms off its held state with both knobs at the plain read'
            assert not newb or (float(b1[k]) >= ahi or float(b1[k]) <= alo) \
                or aw > 1, 'the arm b line is inside its fence on the bar it armed'
            nm = ('%s+(ws1r|ws2r%s)' % (K.LIN2_ARM_B_LINE, '|ws3r' if w3 else '')
                  if newb else 'ws1b+ws1r')
            if newb:
                oo = [n for n, v in (('ws1r', c1r[k]), ('ws2r', c2r[k]))
                      + ((('ws3r', c3r[k]),) if w3 else ()) if K.oob(v, side)]
                why = ('%s %.2f at or beyond the %.1f/%.1f fence, held %d bars, + %s oob'
                       ' (ws1r %.2f, ws2r %.2f%s)'
                       % (K.LIN2_ARM_B_LINE, b1[k], alo, ahi, aw, ' and '.join(oo),
                          c1r[k], c2r[k], ', ws3r %.2f' % c3r[k] if w3 else ''))
            else:
                why = ('ws1b %.2f + ws1r %.2f oob, ws1b dwell %d'
                       % (b1[k], c1r[k], K.LIN2_B1_OOB_DWELL))
            return k, nm, why
        if K.oob(c2m[k], side) and K.oob(c2r[k], side):
            return k, 'ws2Mage+ws2r', 'ws2Mage %.2f + ws2r %.2f oob' % (c2m[k], c2r[k])
    return None, None, 'no arm to the window end'


def div_verdict(CL, close, side, bar):
    """The cws1r divergence verdict AT `bar`. -> +1 bearish, -1 bullish, or None.

    *** HIS 1101 RULING: COMPLETELY DISABLED, AND ws1r IS THE WRONG LINE. *** *"divergence can be
    completely disabled"* / *"ws1r is not the best divergence test: ws1 works in small cycles that
    are not profitable.  ws3r seems to have more divergence potential (eyeballed)"*. His eyeball
    read IS the result on ws3r; nothing here measures it, because the line handed to the producer
    is ws1r at every call site. A ws3r arm would be a build he has not asked for.

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
        return None, 'ws1r %.2f is not oob at the arm - the gate stays shut' % c1r[k]
    if K.ex_fence(c2r[k], side) or K.ex_fence(c3r[k], side):
        return None, ('ws2r %.2f / ws3r %.2f - not both inside the fence at the arm'
                      % (c2r[k], c3r[k]))
    #   RULING 4 and 5: the oob->ib cross only, wob L2_CWS1R_WOB. `oob_ib_cross`'s third field is
    #   the oob side the run LEFT, which for this gate is the target side.
    #   WOB 12, Joe 1027: *"add the wob12 to all crosses to ib"*. This SUPERSEDES his own 1026
    #   ruling on the retest's gap 5, where he accepted L2_CWS1R_WOB 1 for this cross.
    xs = [(c, cf) for c, cf, sd in oob_ib_cross(c1r, K.OOB_HI, K.OOB_LO, int(K.LIN2_CROSS_WOB))
          if int(sd) == int(side) and int(cf) >= k]
    if not xs:
        return None, ('ws1r %.2f oob, ws2r %.2f + ws3r %.2f in - open, but no ws1r oob->ib'
                      ' cross to the data end' % (c1r[k], c2r[k], c3r[k]))
    cross, conf = int(xs[0][0]), int(xs[0][1])
    assert conf >= k, 'the retest cadence is before the arm that opened the gate'
    return conf, ('ws1r %.2f oob + ws2r %.2f / ws3r %.2f in - the gate opens; ws1r oob->ib'
                  ' cross %s, wob %d, cadence at %s'
                  % (c1r[k], c2r[k], c3r[k], ln.U(cross), K.LIN2_CROSS_WOB, ln.U(conf)))


def rider_at(BD, side, bar, lo=1, hi=None, cur=None, at_cadence=True):
    """The highest ws{TF}r that is ex-fence at `bar`. -> tf or None.

        --scan ws{1 to v4_mom_maxTF} for the highest ws{TF}r ex-fence, and make that TF the rider
    """
    hi = int(K.L2_MOM_MAXTF) if hi is None else int(hi)
    #   HIS 1031 JUMP BOUND. At LIN2_RIDER_JUMP 0 nothing is bounded and this is the pre-1031 scan.
    #   `cur` is the rider the walk holds now; his *"arm starts with rider=0"* makes the first
    #   cadence scan ws1..ws{0 + jump}.
    j = int(K.LIN2_RIDER_JUMP)
    if j > 0:
        hi = min(hi, int(0 if cur is None else cur) + j)
    #   A BATON-PASSING CONSUMER, so the fence test goes through `baton_ex_fence` - his 1029
    #   ruling. With LIN2_LATCH_EXFNC_ON 0 that call IS `ex_fence` and this line is unchanged.
    #   `at_cadence` admits his 1031 re-latch; every caller of this reads at a cadence marker or at
    #   the arm, and the arm is the walk's own origin marker.
    got = [t for t in range(int(lo), hi + 1)
           if t in BD.tfs and BD.baton_ex_fence(t, bar, side, at_cadence=at_cadence)]
    return max(got) if got else None


def _nrs(rider_since, arm):
    """The bar `LIN2_CAND_NOT_REVERSED` measures a candidate's reversals from. -> bar or None."""
    m = int(K.LIN2_CAND_NOT_REVERSED)
    return None if m == 0 else (int(rider_since) if m == 1 else int(arm))


def candidates(BD, side, bar, rider, cap=None, not_rev_since=None, at_cadence=False):
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
    #   A BATON-PASSING CONSUMER - `baton_ex_fence`, his 1029 ruling. `towards` is a trajectory
    #   read, not a fence test, so it is untouched.
    out = [t for t in range(int(rider) + 1, top + 1)
           if t in BD.tfs and BD.baton_ex_fence(t, bar, side, at_cadence=at_cadence)
           and towards(BD, t, bar, side)]
    if not_rev_since is None or not out:
        return out
    keep = []
    for t in out:
        revs = [st for _raw, st in _rev_pairs(BD, t, side)]
        if not any(int(not_rev_since) < st <= int(bar) for st in revs):
            keep.append(t)
    return keep


_RV = {}


def _rev_pairs(BD, tf, side):
    """ws{tf}r's reversals on `side`, EMERGING. -> [(the raw lift-off bar, its stamp)].

    ONE HOME for lineage2's reversal stamp. `candidates` had this inline and `_pass_bars` now needs
    the same bars for LIN2_PASS, so a second copy would be two answers to one question.

    THE WOB IS LIN2_REV_WOB 12, his 1026 static. The stamp is raw + wob - 1, which is the last bar
    of the hold and the first bar a consumer may act on; the raw bar is the anchor and the identity.
    """
    key = (id(BD), int(tf), int(side), int(K.LIN2_REV_WOB), tuple(LE.knobs()))
    if key not in _RV:
        w = max(1, int(K.LIN2_REV_WOB))
        _RV[key] = [(int(b), int(b) + w - 1)
                    for b in lift_off(BD.E[int(tf)], int(side), K.LIFT_PTS,
                                      K.gap_for(int(tf)), K.LIFT_TOL, w,
                                      e_path=LE.get(int(tf), len(BD.E[int(tf)]), int(side)))]
    return _RV[key]


_PB = {}


def _pass_bars(BD, tf, side, frm, B):
    """The bars ws{tf}r hands the baton on, between cadences. -> a sorted list.

        --1) rider was oob and has crossed to ib
        --2) rider was between ex-v4mom-fnc and oob, and crossed to in-v4mom-fnc
    """
    #   CACHED OVER THE WHOLE TAPE, then sliced. The uncached form rebuilt `oob_ib_cross` over
    #   1.6M bars on every call, and the bar-loop walk calls it once per bar.
    assert K.LIN2_PASS in ('ib', 'reversal', 'reversal+quarter'), \
        'LIN2_PASS %r is not a mode' % (K.LIN2_PASS,)
    #   THE ROUTING IS IN THE KEY. Without it an arm switch returns the first arm's
    #   cached bars - a hash-keyed cache failing silently with real-but-wrong arrays.
    key = (id(BD), int(tf), int(side), BD.baton_src(), K.LIN2_PASS,
           BD.read_src(tf, 'ib'), BD.read_src(tf, 'exfnc'), BD.read_src(tf, 'oob'))
    if key not in _PB:
        #   HIS 1031 MODES. 'reversal' and 'reversal+quarter' REPLACE both rules below - he said
        #   "swaps ib with reversal", so the pass bar becomes the rider's own reversal and neither
        #   the oob->ib cross nor the latch release produces one. THE LATCH IS STILL LIVE: it gates
        #   every candidate through `baton_ex_fence`, which is a different read from this one.
        if K.LIN2_PASS != 'ib':
            pr = _rev_pairs(BD, tf, side)
            if K.LIN2_PASS == 'reversal':
                r = [st for _raw, st in pr]
            else:
                #   THE LATER BAR WINS, his banked stamp rule: a new stamp rule is additive and
                #   takes max(), never swaps. At a low TF the quarter is SHORTER than the wob, so
                #   without the max the pass would land before the reversal was knowable.
                q = int(K.lin2_quarter_tf(tf))
                r = [max(int(st), int(raw) + q) for raw, st in pr]
            n = len(BD.line(tf))
            r = sorted(set(x for x in r if 0 <= x < n))
            assert all(x >= min(st for _w, st in pr) for x in r) if pr else True, \
                'a pass bar precedes every reversal stamp on this line'
            _PB[key] = (np.array(r, dtype=int), set(r), set())
            arr = _PB[key][0]
            i = int(np.searchsorted(arr, int(frm)))
            j = int(np.searchsorted(arr, int(B), side='right'))
            return [int(x) for x in arr[i:j]]
        #   HIS 1101 KNOB: the oob->ib CROSS reads `ib_line`, routed by LIN2_CP_IB. Banked
        #   'emerging', which is this line unchanged; 'closed_prev' is the other arm he asked to be
        #   buildable - *"I'm not sure about closed_prev for ib.  my gut says emerging: create a
        #   knob that tests both options"*.
        v = BD.ib_line(tf)
        w = max(1, int(K.LIN2_CROSS_WOB))
        #   RULE 1, oob -> ib, WITH WOB 12 - Joe 1027. The pass bar is the cross's CONFIRM bar,
        #   c + w - 1, which is the first bar the ib state has held for w bars.
        a = [int(cf) for _c, cf, s in oob_ib_cross(v, K.OOB_HI, K.OOB_LO, w) if s == int(side)]
        #   RULE 2, ex-fence -> in-mom-fnc, WITH THE SAME WOB. The edge is where ex-fence turns
        #   off; the pass bar is edge + w - 1, and only if in-fence held every bar of that window.
        #   UNDER THE LATCH the ex-fence edge IS the latch's release, his 1029 mech: a line stops
        #   being ex-fence when the barrage releases it or an opposite-side cross confirms, not
        #   when its value re-crosses. LIN2_CROSS_WOB 12 is NOT re-applied on top, and that is
        #   structural - the latch carries LIN2_EXFNC_LATCH_WOB on its on-edge and the barrage
        #   carries its own confirm on the off-edge, so stacking would count one hold twice.
        #   RULE 1 ABOVE IS UNTOUCHED: it is an oob read and oob is not latched.
        if int(K.LIN2_LATCH_EXFNC_ON):
            b = [int(x) for x in BD.latch_off_bars(tf, side)]
        else:
            ex = K.ex_fence_mask(v, side)        # ONE HOME for the fence test
            edges = (np.flatnonzero(ex[:-1] & ~ex[1:]) + 1).astype(int)
            b = []
            for e in edges:
                e = int(e)
                if e + w - 1 >= len(ex):
                    continue
                if not ex[e:e + w].any():          # in-fence for the whole hold
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
    #   THE KEY MUST MATCH `_pass_bars`' KEY. It was a 3-tuple against that function's 4-tuple,
    #   so the lookup below raised KeyError on the first call. Nothing called it, so nothing broke.
    #   THE ROUTING IS IN THE KEY. Without it an arm switch returns the first arm's
    #   cached bars - a hash-keyed cache failing silently with real-but-wrong arrays.
    key = (id(BD), int(tf), int(side), BD.baton_src(), K.LIN2_PASS,
           BD.read_src(tf, 'ib'), BD.read_src(tf, 'exfnc'), BD.read_src(tf, 'oob'))
    if key not in _PB:
        _pass_bars(BD, tf, side, 0, 0)
    _arr, a, b = _PB[key]
    hit = []
    if K.LIN2_PASS == 'reversal':
        return ('ws%d reversed, wob %d bars' % (int(tf), K.LIN2_REV_WOB)
                if int(bar) in a else 'not a pass bar')
    if K.LIN2_PASS == 'reversal+quarter':
        return ('ws%d reversed, then a quarter of its width - %d bars = %d s'
                % (int(tf), K.lin2_quarter_tf(tf), K.lin2_quarter_tf(tf) * 5)
                if int(bar) in a else 'not a pass bar')
    if int(bar) in a:
        hit.append('oob -> ib, held %d bars' % K.LIN2_CROSS_WOB)
    if int(bar) in b:
        hit.append('ex-fence -> in-fence, held %d bars' % K.LIN2_CROSS_WOB)
    return ' + '.join(hit) or 'not a pass bar'


def walk(CL, BD, close, side, frm, B, trace=None, arm_at=None):
    """One lineage2 walk. -> (the verdict, the bar, the rows).

        CL      the closed c-set from v4_core_arm.lines() plus 'M' - cws1b, cws1r, cws2r, cws2Mage
        BD      a `v4_l2_proxy.Board`, which owns both r ladders and the routing between them
        arm_at  a bar to START AT, skipping the arm race entirely. None runs the race.

    The arm race, then the rider, then one decision per cadence bar until a verdict.

    `arm_at` EXISTS FOR HIS test#1 ROUTE, Joe 1027: *"if we trigger the lineage2 walk at
    barrage-fire (08-31 1432) and scan the wsf range for the highest exfence line, then the high
    exfence ws9 takes the baton. exhaust fires at 1501. this lineage2 walk is the same as usual:
    decisions at cadences only"*. The race decides nothing on that route - the barrage bar IS the
    arm - so the race is skipped and the rider is scanned at that bar. Everything after is
    unchanged, which is what *"the same as usual"* requires.
    """
    rows = []

    def row(**kw):
        rows.append(kw)
        if trace is not None:
            trace.append(kw)

    if arm_at is not None:
        arm, which = int(arm_at), 'arm_at'
        row(bar=arm, stage='ARM', why='arm_at %s - the arm race is skipped, this bar IS the arm'
                                      % ln.U(arm))
    else:
        arm, which, why = arm_race(CL, BD, side, frm, B)   # all three on the CLOSED set, 1026
        if arm is None:
            row(bar=None, stage='NO ARM', why=why)
            return 'NO ARM', None, rows
        row(bar=arm, stage='ARM', why='%s: %s' % (which, why))

    if which == 'ws2Mage+ws2r':
        v = div_verdict(CL, close, side, arm)
        #   *"if the open trade ... is SHORT and the verdict is +1, the verdict is AGAINST the
        #   SHORT and router will create a rev-trade"*.
        #   *** THIS USED TO READ "A SHORT is side +1 here". THAT WAS WRONG. *** A SHORT's target
        #   side is the LOW one, -1. The condition below is `verdict == side` and it is RIGHT:
        #   anchor_floater's +1 supports a SHORT, so +1 against a LOW target side (-1) does NOT
        #   match and takes no action, while -1 bullish against a LOW target side DOES match and
        #   rev-trades - his 1101 table verbatim. The code was never changed, only this comment.
        st = div_state(CL, close, side, arm)
        row(bar=arm, stage='DIV', state=st,
            why='ws1r divergence %s | anchor_floater state %s' % (
                ('none' if v is None else ('+1 bearish' if v > 0 else '-1 bullish')),
                'no reading' if st is None else
                {1: '+1 divergence, SHORT', -1: '-1 divergence, LONG',
                 2: '+2 PM, trend SHORT', -2: '-2 PM, trend LONG',
                 0: '0 inside AF_SLOPE_FLOOR'}.get(st, str(st))))
        if v is not None and ((v > 0 and int(side) > 0) or (v < 0 and int(side) < 0)):
            return 'DIV REV-TRADE', int(arm), rows

    #   HIS 1031 RULE: *"arm starts with rider=0"*. At LIN2_RIDER_JUMP 0 the arm scans as it
    #   always did; with the bound on, the arm assigns nothing and the first cadence does the work.
    rider = None if int(K.LIN2_RIDER_JUMP) > 0 else rider_at(BD, side, arm)
    rider_since = int(arm)                             # the bar the CURRENT rider took the baton
    if rider is None:
        #   HIS 1026 RULING: this no longer ends the walk - *"drop the rider gate for t3 and t4"*
        row(bar=arm + 1, stage='NO RIDER',
            why=('the arm starts with rider 0 - his 1031 rule, jump bound %d TFs'
                 % int(K.LIN2_RIDER_JUMP)) if int(K.LIN2_RIDER_JUMP) > 0 else
                ('no ws1..ws%d r is LATCHED at the arm bar + 5s - the walk continues, t3 and t4'
                 ' stay reachable' % K.L2_MOM_MAXTF))
    else:
        #   "LATCHED", NOT "ex-fence". Joe 1031: *"label them as "latched" and print the current
#   value"*. The scan reads `baton_ex_fence`, which at LIN2_LATCH_EXFNC_ON 1 is the LATCH; a
#   latched line's value can sit inside the fence, and he caught this row claiming otherwise at
#   ws30 25.67 against a 25.0 fence.
        row(bar=arm, stage='RIDER', why='ws%d LATCHED, r %.2f - the highest latched rung'
                                        % (rider, BD.value(rider, arm)), rider=rider)

    #   v4-arm-lineage-retest. While the gate is open nothing else decides, so the walk starts at
    #   the gate's own cadence and the cadences before it are not served. His flow: *"the gate is
    #   open ... nothing is tested again until it moves"*.
    start = int(arm)
    gate_cad = None                     # the retest gate's own cadence, for the review list below
    if int(K.L2_ARM_RETEST):
        rt, rt_why = arm_retest(CL, side, arm, B)
        row(bar=arm, stage='RETEST', why=rt_why)
        if rt is not None:
            #   THE BOUND APPLIES HERE TOO - the gate's bar IS a cadence marker. He has not
            #   ruled it either way; stated, not decided quietly.
            nr = rider_at(BD, side, rt, cur=rider)     # RULING 6: re-scan and ride the highest
            if nr is None:
                #   HIS OWN SPEC LINE, reached at the gate's cadence instead of at the arm:
                #   *"IF no rider is assigned ... the walk ends. pass to router for a rev-trade"*.
                row(bar=rt, stage='EXHAUST',
                    why='v4-arm-lineage-retest: no ws1..ws%d r is LATCHED at the gate cadence -'
                        ' the walk ends' % K.L2_MOM_MAXTF, rider=rider, ctype='retest')
                return 'EXHAUST', int(rt), rows
            row(bar=rt, stage='RIDER',
                why='v4-arm-lineage-retest: the re-scan rides ws%d LATCHED, r %.2f - the highest'
                    ' latched rung' % (nr, BD.value(nr, rt)), rider=nr, ctype='retest')
            rider, start = int(nr), int(rt)
            #   THE GATE'S CADENCE JOINS THE REVIEW LIST. Joe 1030, shown that the board review
            #   never ran at 2026-08-30 22:02:55 and that his own spec line
            #   *"--walk cws1r to handover (ib) and follow the lineage process"* plus
            #   *"--if an exhaust is found, route to rev-trade"* both require it: *"7 - add the
            #   gate's cadence"*. Before this, `produced` carried t1, t2, the counter-oob cadence
            #   and the barrage only, so the gate's own bar was the one cadence never reviewed.
            gate_cad = (int(rt), 'retest', rt_why)

    #   THE MAGE-CASCADE VERDICT AT EVERY CADENCE, Joe 1027: *"in fact, let's get the mage-cascde
    #   verdict at every cadence event"*. It is RECORDED, not acted on - he has not ruled what the
    #   walk does with it. His own shape for that is *"get a mage-verdict, and if its verdict
    #   matches the trade direction then take no action (ie keep walking)"*, which is a SECOND
    #   ruling he has not yet given.
    def cascade_at(k):
        """The mage-cascade verdict for the cadence at `k`. -> 'up', 'down', 'neither' or a note.

        IT ANCHORS ON A ws1Mage EXTREMUM, not on the cadence bar. Joe 1029: *"were the mage
        cascades anchored on a ws1Mage's extremum? if not, they should be"* - and they were not.
        This walk passed the cadence bar straight in while every other consumer of the cascade in
        the tree picks the extremum bar first, which is his own 1017 design: *"in our current
        state, the most recent mage extrema is captured from ws1Mage"*.

        THE GAP IS 48 BARS = 4 MIN, his 1029 choice of the cascade's own default and his own 1017
        number. The saviour has a separate 12-bar value for its own read; this does not share it.

        MEASURED ON THE TWO BARS HE ASKED ABOUT, 2026-08-30: at 04:41:00 the cadence bar gives
        'down' with ws1Mage at 48.56, and the extremum at 04:40:00 gives 'up' with ws1Mage at
        -14.39. At 04:48:30 the cadence bar gives 'down' at 18.17, and the extremum at 04:47:20
        gives 'up' at -19.38. Both flip, because at the cadence bar ws1Mage has already climbed
        off its low so the first rung reads as falling.

        CAUSAL: the picker asserts its own bar never exceeds the event bar.
        """
        if BD.mage is None:
            return 'no Mage ladder'
        try:
            got = mage_cascade_bar(BD.mage[min(BD.mage)], int(k), int(side), mode='extrema',
                                   gap=MC_GAP)
            if got is None:
                return 'no same-side ws1Mage extremum before the tape starts'
            ab = int(got[0])
            assert ab <= int(k), 'the cascade anchor is after the cadence bar it serves'
            c = mage_cascade(BD.mage, ab, tf_lo=min(BD.mage), tf_hi=max(BD.mage),
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
                + (CAD.barrage(BD, side, arm, B) if int(K.LIN2_BARRAGE_ON) else [])
                + ([gate_cad] if gate_cad is not None else []))
    #   HIS 1031 FILTER. LIN2_CAD_TYPES 'all' is the bank and changes nothing; a type list keeps
    #   only those cadences in the review list. The mechs still RAN - their own ON knobs own that -
    #   so a barrage that fired is still a barrage, it just does not get to decide here.
    for b, ty, w in produced:
        if b >= start and K.cad_allowed(ty):
            fixed.setdefault(int(b), []).append((ty, w))
    t3_on, lat_on, last = False, False, int(start)
    #   t3's population is measured SINCE THE ARM - his 1026 ruling *"tested since the arm"* - so
    #   the retest moving the walk's start does not move t3's origin.
    t3 = CAD.T3(BD, side, arm)
    #   THE t3 REPLACEMENT, his 1026 2-staged latch. L2_T3_ON is banked 0 and LIN2_CAD_LATCH_ON 1, so
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
                            why='ws%d %.2f ATTEMPTS to hand over, between cadences - no'
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
                if ok and not t3_on and K.cad_allowed('t3'):
                    here.append(('t3', t3why))
                t3_on = ok
        #   LATCH 1 reads at every cadence bar - his *"2, at the cadence bar"*. It is armed
        #   BEFORE the cadence is served, so a latch-2 completion on the same bar can see it.
        if int(K.LIN2_CAD_LATCH_ON) and here:
            st = div_verdict(CL, close, side, bar)
            ok1, w1 = lat.arm1(bar, st, here[0][0])
            if ok1:
                row(bar=bar, stage='LATCH1', why=w1, rider=rider)

        #   LATCH 2 is the cadence t3 used to be: the RISING EDGE of its own condition, tested on
        #   every bar, and completing it exhausts the walk.
        if int(K.LIN2_CAD_LATCH_ON) and rider is not None and lat.live(bar):
            cap2 = int(rider) + int(K.L2_LIN_HOP)
            ok2, w2 = lat.at(bar, rider,
                             lambda: candidates(BD, side, bar, rider, cap=cap2))
            if ok2 and not lat_on and K.cad_allowed('latch'):
                here.append(('latch', w2))
            lat_on = ok2
        elif lat_on:
            lat_on = False                             # the latch expired; re-arm the rising edge

        if not here:
            continue

        for ctype, cwhy in here:
            #   *** HIS 1101 ORDER: THIS IS THE FIRST TASK AT A CADENCE. *** *"the test for
            #   "linhop reaching an ex-fence line" is the (almost) first task, and definitely
            #   before any lineage tasks fire.  that means the rider stays at ws1"* / *"I say
            #   "almost" because I'm not sure of the cadence's task order"*.
            #   IT NOW PRECEDES, in this order: the divergence test, the barrage exhaust, the
            #   mage-cascade verdict, the rider pickup, the matryoshka takeover, the candidate
            #   scan, HOLD, the ladder-top reset and the exhaust. His "almost" is unresolved, so
            #   that list is what he moves it against.
            #
            #   A RIDER OF 0 STILL HAS A REACH, and this is MY reading of his sentence, stated:
            #   the band is rider + 1 .. rider + L2_LIN_HOP by his own hop rule, so at the arm's
            #   rider 0 it is ws1..ws2. Skipping the test with no rider - which is what I built
            #   first - makes his own 0554 example impossible, because the rider only reached ws5
            #   through a pickup this test is meant to come before.
            _bh = str(K.LIN2_BOARD_HOLD)
            assert _bh in ('off', 'board_oob', 'board_oob_rev', 'linhop_exfnc'), \
                'LIN2_BOARD_HOLD %r is not an arm' % (_bh,)
            if _bh == 'linhop_exfnc':
                _r0 = int(rider or 0)
                _lo = _r0 + 1
                _hi = min(_r0 + int(K.L2_LIN_HOP), int(K.L2_MOM_MAXTF))
                _xf = [t for t in range(_lo, _hi + 1)
                       if BD.baton_ex_fence(t, bar, side, at_cadence=True)
                       and towards(BD, t, bar, side)]
                if _xf:
                    row(bar=bar, stage='HOLD', rider=rider, ctype=ctype,
                        why='ws%d..ws%d is lin_hop %d reach from rider ws%d and %d of it is'
                            ' ex-fence and printing towards at a %s cadence - %s - the tests are'
                            ' concluded and the walk goes to the next cadence'
                            % (_lo, _hi, K.L2_LIN_HOP, _r0, len(_xf), ctype,
                               ', '.join('ws%d %.2f' % (t, BD.value(t, bar)) for t in _xf)))
                    last = int(bar)
                    continue
            #   HIS 1101 DIVERGENCE TEST, AT EVERY CADENCE AND BEFORE THE LINEAGE TESTS. His
            #   *"ordered before lineage (ie lineage tests after devergence tests)"*, confirmed when
            #   asked. It sits ahead of the rider pickup, the candidate scan and HOLD, because at
            #   2026-09-03 04:37:55 HOLD takes the bar - a test placed after it could never fire.
            #   HIS TRUTH TABLE, 1101: bullish verdict with a LOW target side rev-trades; bearish
            #   with a HIGH target side rev-trades; neither match is no outcome. That is
            #   `verdict == side`, the SAME condition the arm uses, so no sign is re-derived.
            #   PM IS REFUSED BY `div_verdict` ITSELF - it returns None for abs(state) == 2 - which
            #   is his *"disable PM matching for lineage2"*. LIN2_DIV_PM_FLOOR is declared for the
            #   floor he has not set and is read by nothing.
            if int(K.LIN2_DIV_ON):
                #   WHICH BAR IT IS ANCHORED ON, his 1101 proposal. 'extremum' walks back for the
                #   target-side ws1Mage extremum with the SAME picker the cascade uses, so the walk
                #   is unbounded and the returned bar may never exceed this one - asserted there
                #   and again here.
                dat = str(K.LIN2_DIV_AT)
                assert dat in ('cadence', 'extremum'), 'LIN2_DIV_AT %r is not an arm' % dat
                db = int(bar)
                if dat == 'extremum' and BD.mage is not None:
                    _pk = mage_cascade_bar(BD.mage[min(BD.mage)], int(bar), int(side),
                                           mode='extrema', gap=MC_GAP)
                    if _pk is not None:
                        db = int(_pk[0])
                assert db <= int(bar), 'the divergence anchor is after the cadence bar it serves'
                dv = div_verdict(CL, close, side, db)
                ds = div_state(CL, close, side, db)
                dn = ('none' if dv is None else ('+1 bearish' if dv > 0 else '-1 bullish'))
                sn = 'high' if int(side) > 0 else 'low'
                if dv is not None and int(dv) == int(side):
                    row(bar=bar, stage='EXHAUST', rider=rider, ctype=ctype, state=ds,
                        why='%s %s | divergence %s with a %s target side, anchored on the %s bar'
                            ' %s - rev-trade (raw state %s)'
                            % (ctype, cwhy, dn, sn, dat, ln.U(db), ds))
                    return 'DIV REV-TRADE', int(bar), rows
                row(bar=bar, stage='DIV', rider=rider, ctype=ctype, state=ds,
                    why='%s | divergence %s with a %s target side, anchored on the %s bar %s -'
                        ' no outcome (raw state %s)' % (ctype, dn, sn, dat, ln.U(db), ds))
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
                    #   HIS 1030 GATE, in front of the reversal and nowhere else. A baton-pass
                    #   candidate anywhere in ws1..ws{LIN2_CASC_REV_GATE_HI} means a fast line is
                    #   still past the fence AND still `towards`, so the trade has a lead running
                    #   and the cascade's reversal is NOT honoured - the bar falls through to the
                    #   board review below.
                    #   THE RANGE IS NOT THE BATON'S. `candidates` scans UPWARD from the rung it is
                    #   handed, so rider 0 with the cap at ws4 asks about rungs the baton would
                    #   never reach. His word on that reading: *"agreed - that's my design"*.
                    gcd = (candidates(BD, side, bar, 0, cap=int(K.LIN2_CASC_REV_GATE_HI),
                                      at_cadence=True)
                           if int(K.LIN2_CASC_REV_GATE_ON) else ())
                    if gcd:
                        row(bar=bar, stage='CASCADE GATED', rider=rider, ctype=ctype,
                            why=('%s %s | mage-cascade %s OPPOSES the %s, but ws1..ws%d still'
                                 ' offer %s - the reversal is NOT honoured, the board decides'
                                 % (ctype, cwhy, mv, 'LONG' if lng else 'SHORT',
                                    K.LIN2_CASC_REV_GATE_HI,
                                    ', '.join('ws%d %.2f' % (t, BD.value(t, bar)) for t in gcd))))
                    else:
                        #   THE KNOB IS NARROWED TO THE ws1b COUNTER-OOB CADENCE, Joe 1027:
                        #   *"narrow it - applies only to cws1b counter oob"*. Every other cadence
                        #   type always rev-trades on a mismatch.
                        act = (str(K.LIN2_MISMATCH_ACTION) if ctype == 'ws1b counter-oob'
                               else 'rev-trade')
                        row(bar=bar, stage='EXHAUST', rider=rider, ctype=ctype, mismatch=True,
                            why='%s %s | mage-cascade %s OPPOSES the %s - %s'
                                % (ctype, cwhy, mv, 'LONG' if lng else 'SHORT', act))
                        return ('CLOSE ONLY' if act == 'close-only'
                                else 'EXHAUST'), int(bar), rows
                if ((mv == 'up' and lng) or (mv == 'down' and not lng)) \
                        and ctype != 'ws1b counter-oob':
                    row(bar=bar, stage='NO ACTION', rider=rider, ctype=ctype,
                        why='%s %s | mage-cascade %s matches the %s - no action, keep walking'
                            % (ctype, cwhy, mv, 'LONG' if lng else 'SHORT'))
                    last = int(bar)
                    continue
            if rider is None:
                got = candidates(BD, side, bar, 0, at_cadence=True)
                if got:
                    rider = max(got)
                    last = int(bar)
                    row(bar=bar, stage='RIDER',
                        why='%s %s | ws%d r %.2f picked up at a cadence, no prior rider'
                            % (ctype, cwhy, rider, BD.value(rider, bar)), rider=rider)
                    continue
                row(bar=bar, stage='NO RIDER',
                    why='%s %s | still no ex-fence line on the whole board' % (ctype, cwhy))
                last = int(bar)
                continue

            rv = BD.value(rider, bar)                      # the LIVE value, via the proxy
            #   LIN2_MATRY_WSF_TAKEOVER - HIS MECH, 1030. A slow rider is overtaken by the fast
            #   lines it is supposed to be led by. His spec and the six gaps he closed are at the
            #   knob; the two anchor arms are his *"test both"*.
            #   IT RUNS BEFORE THE CANDIDATE SCAN, his *"it fires even when candidates exist
            #   (because matryoshka is leading)"*.
            if int(K.LIN2_MATRY_WSF_TAKEOVER_ON) \
                    and int(rider) >= int(K.LIN2_MATRY_WSF_TAKEOVER_TF) \
                    and ctype in ('t1', 't2', 'retest'):
                ab = int(bar)
                at = str(K.LIN2_MATRY_WSF_TAKEOVER_AT)
                assert at in ('event', 'extremum'), \
                    'LIN2_MATRY_WSF_TAKEOVER_AT %r is not an arm' % at
                if at == 'extremum' and BD.mage is not None:
                    pk = mage_cascade_bar(BD.mage[min(BD.mage)], int(bar), int(side),
                                          mode='extrema', gap=MC_GAP)
                    if pk is not None:
                        ab = int(pk[0])
                assert ab <= int(bar), 'the scan anchor is after the cadence bar it serves'
                top = int(K.LIN2_MATRY_WSF_SCAN_HI)
                #   HIS TWO STATES ARE EVERY VALUE UNDER THE TARGET oob FENCE, so the test is one
                #   read through BD.oob - the same home every other oob read in the fork uses.
                ok = [t for t in range(1, top + 1)
                      if t in BD.tfs and not BD.oob(t, ab, int(side))]
                pair = next(((t, t + 1) for t in range(1, top)
                             if t in ok and (t + 1) in ok), None)
                if pair is not None:
                    row(bar=bar, stage='EXHAUST', rider=rider, ctype=ctype,
                        why=('%s %s | LIN2_MATRY_WSF_TAKEOVER: rider ws%d is at or over ws%d and'
                             ' ws%d %.2f + ws%d %.2f are both under the target oob fence at %s'
                             ' (%s anchor) - rev-trade'
                             % (ctype, cwhy, rider, K.LIN2_MATRY_WSF_TAKEOVER_TF,
                                pair[0], BD.value(pair[0], ab), pair[1], BD.value(pair[1], ab),
                                ln.U(ab), at)))
                    return 'EXHAUST', int(bar), rows
            #   THE RIDER'S OWN TEST IS A BATON-PASSING CONSUMER. Joe 1029, on being shown that
            #   under the latch a once-oob rider can only ever take the HOLD branch until a
            #   barrage fires: *"the consequences: expected"*.
            no_ex = not BD.baton_ex_fence(rider, bar, side)
            revd = BD.reversed_in(rider, side, last, bar)  # TIMING: emerging, via the proxy
            #   HIS 1026 RULING: only t1 and t2 lift lin_hop
            cap = None if ctype in ('t1', 't2') else rider + int(K.L2_LIN_HOP)
            #   HIS 1031 JUMP BOUND APPLIES HERE. *"at a cadence marker, the rider TF can only jump
            #   by {knob:8} TFs"* - and a baton pass at a cadence IS the rider advancing. The first
            #   build left this cap at None on a t1 and he caught it: *"this broke the max-jump
            #   rule"* on ws7 -> ws27, a jump of 20.
            #   IT DOES NOT CANCEL THE 1026 LIFT. lin_hop 2 still does not bind at a t1, because 8
            #   is wider than 2; the bound replaces the UNBOUNDED ceiling, not the lift.
            #   BETWEEN CADENCES IT NEVER BINDS: lin_hop 2 is already tighter than 8, and his rule
            #   names a cadence marker.
            capsrc = 'the whole board' if cap is None else 'lin_hop %d' % K.L2_LIN_HOP
            if int(K.LIN2_RIDER_JUMP) > 0:
                jcap = int(rider) + int(K.LIN2_RIDER_JUMP)
                if cap is None or jcap <= int(cap):
                    cap, capsrc = jcap, 'the jump bound %d' % K.LIN2_RIDER_JUMP
            #   at_cadence TRUE: this IS the cadence's own candidate scan, where his 1031
            #   re-latch is allowed to speak. The between-cadences scan above is not.
            got = candidates(BD, side, bar, rider, cap=cap, at_cadence=True,
                             not_rev_since=_nrs(rider_since, arm))
            row(bar=bar, stage='CADENCE',
                why='%s %s | rider ws%d %.2f, no-longer-exfence %s, reversed %s | mage-cascade %s'
                    % (ctype, cwhy, rider, rv, 'yes' if no_ex else 'no', 'yes' if revd else 'no',
                       cascade_at(bar)),
                cands=tuple(got), rider=rider, cap=cap, ctype=ctype)
            if got:
                row(bar=bar, stage='BATON',
                    why='ws%d -> ws%d, at a %s cadence, %s'
                        % (rider, max(got), ctype,
                           'whole board' if cap is None
                           else 'capped at ws%d by %s%s'
                                % (cap, capsrc,
                                   ' - past the ws%d ladder top, so it does not bind'
                                   % K.L2_MOM_MAXTF if int(cap) > int(K.L2_MOM_MAXTF) else '')),
                    rider=rider, to=max(got), cands=tuple(got), cap=cap, ctype=ctype)
                rider = max(got)
                rider_since = int(bar)
                last = int(bar)
                continue
            #   THE oob READ GOES THROUGH `baton_oob`, which at LIN2_LATCH_OOB_ON 0 IS the line
            #   value - his 1029 correction. At 1 it is the one latch read at depth, the arm he
            #   asked to A/B.
            if BD.baton_oob(rider, bar, side) or (not no_ex and not revd):
                row(bar=bar, stage='HOLD', why='rider ws%d %.2f %s - no action' % (
                    rider, rv,
                    'oob' if BD.baton_oob(rider, bar, side) else 'ex-fence and not reversed'),
                    rider=rider)
                last = int(bar)
                continue
            #   HIS 1031 TRICK, IN FRONT OF THE EXHAUST: *"when ws30 exhausts, set the rider to
            #   zero and test for baton pass candidates (same logic, max jump = 8 TFs)"*. The
            #   trigger is the LADDER TOP - his ws30 IS L2_MOM_MAXTF on that walk and there is
            #   nowhere above it to pass to; the rung-to-condition step is mine and stated.
            #   NO LIMIT ON REPEATS: he named none, so a rider that climbs back to the top and
            #   exhausts again resets again.
            if int(K.LIN2_TOP_RESET_ON) and int(rider) >= int(K.L2_MOM_MAXTF):
                rcap = int(K.LIN2_RIDER_JUMP) or None
                rgot = candidates(BD, side, bar, 0, cap=rcap, at_cadence=True)
                if rgot:
                    row(bar=bar, stage='TOP RESET', rider=rider, to=max(rgot),
                        cands=tuple(rgot), cap=rcap, ctype=ctype,
                        why='ws%d %.2f is the ladder top and exhausted - the rider resets to 0 and'
                            ' re-scans%s, taking ws%d'
                            % (rider, rv,
                               '' if rcap is None else ' capped at ws%d by the jump bound' % rcap,
                               max(rgot)))
                    rider = max(rgot)
                    rider_since = int(bar)
                    last = int(bar)
                    continue
                row(bar=bar, stage='TOP RESET EMPTY', rider=rider, cands=(), cap=rcap,
                    ctype=ctype,
                    why='ws%d %.2f is the ladder top and exhausted - the rider reset to 0 found no'
                        ' candidate%s' % (rider, rv,
                                          '' if rcap is None
                                          else ' at or below ws%d' % rcap))
            #   *** HIS 1101 BLANKET RULE, IN FRONT OF THE EXHAUST. *** *"0554 can't exhaust -
            #   ws3r is oob so it must walk to the next cadence"* / *"the oob rule doesn't apply to
            #   a rider - it's a blanket rule across the board"*. The FULL range ws1..L2_MOM_MAXTF,
            #   his standing meaning of "board", so a rung BELOW the rider counts too.
            #   WHERE IT SITS IS MINE AND STATED: after the ladder-top reset, immediately before
            #   the exhaust. The reset is not a verdict - it is the alternative to exhausting - so
            #   gating it would remove a mech he banked. This gates only the exhaust itself.
            #   *** HIS FOUR BOARD ARMS, ONE KNOB. *** LIN2_BOARD_HOLD picks which rule gates
            #   the exhaust. 'linhop_exfnc' is his 1101 third arm, banked: *"if a line that is
            #   inside of lin-hop's reach is ex-fence, then walk to the next cadence"*. The reach
            #   is the rider's own hop band, rider + 1 .. rider + L2_LIN_HOP 2.
            #   WITH NO RIDER THERE IS NO REACH, so the arm tests nothing and does not gate - the
            #   hop rule's own shape, his *"the max hops between a rider and a candidate"*.
            if _bh in ('board_oob', 'board_oob_rev'):
                #   *** HIS 1101 CORRECTION: oob AND NOT REVERSED. *** *"I must have made a
                #   mistake.  maybe the rule is oob and has not reversed"*. An oob rung that has
                #   turned no longer blocks; only one still running does.
                #   THE REVERSAL WINDOW IS THE ESTABLISHED ONE, and that is MY call, stated: it is
                #   `reversed_in(tf, side, last, bar)`, exactly the read the rider's own `revd`
                #   uses above, over the same window - since the previous cadence. The other
                #   reading is "since this rung became oob", which needs the oob run's start bar
                #   and is a different mech; it is not built.
                _ob = [t for t in range(1, int(K.L2_MOM_MAXTF) + 1)
                       if BD.oob(t, bar, side)
                       and (_bh == 'board_oob'
                            or not BD.reversed_in(t, side, last, bar))]
                if _ob:
                    row(bar=bar, stage='HOLD', rider=rider, ctype=ctype,
                        why='%d of ws1..ws%d are oob and not reversed since %s at a %s cadence -'
                            ' %s - the board holds and the walk goes to the next cadence'
                            % (len(_ob), K.L2_MOM_MAXTF, ln.U(int(last)), ctype,
                               ', '.join('ws%d %.2f' % (t, BD.value(t, bar)) for t in _ob)))
                    last = int(bar)
                    continue
            #   t4cadence: a non-oob rider that reversed with nowhere to pass
            tag = 't4' if (revd and not BD.baton_oob(rider, bar, side)) else 'exhaust'
            row(bar=bar, stage='EXHAUST',
                why='%s at a %s cadence - rider ws%d %.2f, no candidate %s'
                    % (tag, ctype, rider, rv,
                       'on the whole board' if cap is None
                       else 'at or below ws%d (%s)' % (cap, capsrc)),
                rider=rider, cap=cap, ctype=ctype)
            return 'EXHAUST', int(bar), rows

    row(bar=None, stage='NO VERDICT', why='no exhaust to the window end')
    return 'NO VERDICT', None, rows
