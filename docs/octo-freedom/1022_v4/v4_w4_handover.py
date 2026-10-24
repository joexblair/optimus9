"""The ws4r handover - arm B of Joe's 1024 A/B. NOT YET NAMED by him; he calls it *"w4r to ws1Mage
ib"*, so this file is named for the lines and not for a coined shorthand.

WHY IT EXISTS. Joe 1024, on the 2026-09-01 01:16 leg: *"both EXHAUST times are ~0.8% past the low
pivot at 0130. this is our old nemesis: the slower the r, the more loss of profit"*, and *"what we
need is a better method to create EXHAUST if ws4r has a baton-pass candidate (ie ws5r)"*.

WHERE IT PLUGS IN, his 1024 framing and it is not a separate trigger:

    use the existing lineage code UNTIL ws4r is seen to be oob. when ws4r is oob, the new mech
    finsihes the lineage flow
    -ie, if exhaust prints when ws4r is not oob (ws3r oob and reversing, ws4r infence), that will
     handled by the banked lineage and continues to exhaust
    --if ws3r is able to pass the baton to ws4r, then "w4r to ws1Mage ib" takes over the walk and
      continues to exhaust

So the banked walk runs as it always has. At the moment the baton passes from ws3 to ws4 AND ws4r
is oob at that pass bar, this takes over and runs to EXHAUST.

    the pass bar   Joe 1024: *"ws3r reversal (or is it ib now? I'm not sure). ie, which ever
                   option passes the baton from ws3r"*. Under the banked LIN_PASS 'ib' that is the
                   ib cross's CONFIRM bar, which is the same bar the receiver gate reads
                   R[nxt][pas] at.
    ws4 reverses   Joe 1024 *"yes, agreed"* to: ws4 takes the baton, reverses, and THEN this chain
                   runs instead of the pass to ws5. So step 1 is ws4's OWN reversal - the one the
                   banked walk was already waiting for - and his spec's *"after the ws4r reversal"*
                   is satisfied by it rather than replaced.

THE CHAIN, his spec with the 1024 rulings folded in:

    after the ws4r reversal
    -after the next same-side of 50 ws1r reversal
    --at the next ws2Mage same-side oob
    ---print exhaust at the ws1Mage same-side oob->ib cross, xwob 4
    ----a cross confirmed within the grace behind the ws4r reversal's knowable bar also counts,
         PROVIDED that cross fires after a same-side ws2Mage oob. grace 3 minutes
    ----the exhaust bar is whatever fires last: the LATEST of the cross's confirm bar, the ws1r
         reversal's knowable bar and the ws4r reversal's knowable bar

WHY THE *"PROVIDED"* CLAUSE IS THERE, because it is the one line that makes the grace causal. Joe
1024 ruled the racers as the cross confirm, the ws1r stamp and the ws4r stamp - *"the ws2Mage oob
bar is not in the list of racers"*. In the normal case that is safe: step 4 searches FORWARD from
the ws2Mage oob bar, so the cross confirm is already at or after it and the oob can never be last.
In the grace case it broke - a cross from behind the ws4r stamp made the ws1r stamp the latest,
and the ws2Mage oob falls AFTER the ws1r stamp, so the exhaust asserted an oob that had not yet
happened. Shown the 05:45 numbers he fixed it at the source: *"the grace lookback is flawed if this
scenario is possible. update: 'if the grace reaches back and finds the ws1Mage cross **that fires
after same-side ws2Mage oob**'"*. With the oob behind the cross, and the cross at or before the
action bar, the ordering holds and no floor or assert is needed.

THE RACE IS NOT HERE. Joe 1024's *"ws4r oob or ws5r oob, as a race"* belongs to the STANDALONE
test-script, where a near-miss ws4r killed the trigger outright. Inside the machine his second
bullet already covers it: ws4r in-fence means the banked lineage keeps walking. He confirmed the
*"whatever fires last"* race still applies - that is the action bar above, not the trigger.

CAUSAL. Every bar acted on is a stamp or a confirm bar. `lift_off` stamps are K.lift_stamp(b);
`oob_ib_cross` confirms at cross + xwob - 1. The grace reaches into the PAST only.

ARM A IS THE BANK. K.LIN_W4 is 0, so an arm-B run is off-ruled and refuses without
W_V4_EXPERIMENT=1. That is deliberate: this is a candidate, not the machine.
"""
import io
import sys

import numpy as np

import ln
import v4_knobs as K

_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.analysis.jig import oob_ib_cross
sys.stderr = _e

_G1 = {}
_M2 = None


def _g1_crosses(side):
    """The ws1Mage oob->ib cross CONFIRM bars that left `side`'s oob run. -> a sorted int array."""
    key = (side, K.LIN_W4_G1_XWOB)
    if key not in _G1:
        v = np.asarray(ln.line('ws1Mage'), float)
        xc = oob_ib_cross(v, K.OOB_HI, K.OOB_LO, K.LIN_W4_G1_XWOB)
        _G1[key] = np.array(sorted(cf for c, cf, s2 in xc if (s2 > 0) == (side > 0)), dtype=int)
    return _G1[key]


def _m2():
    global _M2
    if _M2 is None:
        _M2 = np.asarray(ln.line('ws2Mage'), float)
    return _M2


def _next_ws1r_rev(R, side, frm, B):
    """*"after the next same-side of 50 ws1r reversal"*. -> the stamp, or None.

    The detector is lineage's own - his 1024 fork 2b, *"use the same reversal mech that lineage
    uses to detect reversals"*. The side-of-50 test is on the VALUE, his fork 2: *"the same-side of
    50: the ws1r value below 50"*, read through K.side_of whose boundary ruling is its own.
    """
    import v4_fast as F                                # imported here: F imports this module
    for b in F.revs(R[1], 1, side):
        b = int(b)
        if b < frm or b > B:
            continue
        if K.side_of(R[1][b]) != side:
            continue
        return K.lift_stamp(b)
    return None


def _next_m2_oob(side, frm, B):
    """*"at the next ws2Mage same-side oob"*. -> bar, or None. oob is 15/85, always."""
    m = _m2()
    for b in range(int(frm), int(B) + 1):
        if K.oob(m[b], side):
            return b
    return None


def _m2_oob_at_or_before(side, bar):
    """Is there a same-side ws2Mage oob at or before `bar`. -> bool.

    His *"provided that cross fires after same-side ws2Mage oob"* - the clause that makes the grace
    causal. Scans back from `bar`; the ws2Mage oob runs are dense enough that this terminates fast,
    and it is bounded by the tape's start rather than by an invented lookback.
    """
    m = _m2()
    for b in range(int(bar), -1, -1):
        if K.oob(m[b], side):
            return True
    return False


def exhaust(R, side, s4, B):
    """The handover, from ws4's own reversal. -> (verdict, bar).

    The caller has already checked that the baton passed to ws4 and that ws4r was oob at the pass
    bar. `s4` is ws4's own reversal STAMP - the one the banked walk was waiting for - so his
    *"after the ws4r reversal"* is satisfied by it.
    """
    s1 = _next_ws1r_rev(R, side, s4, B)
    if s1 is None:
        return 'W4 NO WS1R', None
    ob = _next_m2_oob(side, s1, B)
    if ob is None:
        return 'W4 NO WS2MAGE OOB', None
    c = _g1_crosses(side)
    grace = max(0, int(K.LIN_W4_GRACE_S) // 5)
    cross = None
    if grace:                                          # a cross BEHIND the ws4r stamp, his grace
        w = c[(c >= s4 - grace) & (c < s4)]
        for cand in w[::-1]:                           # the most recent qualifying one
            if _m2_oob_at_or_before(side, int(cand)):
                cross = int(cand)
                break
    if cross is None:                                  # else the next one forward of the oob
        f = c[c >= ob]
        if not len(f):
            return 'W4 NO WS1MAGE IB', None
        cross = int(f[0])
    bar = max(cross, s1, s4)                           # *"whatever fires last"* - his three racers
    assert bar >= s4, 'the handover exhaust precedes the ws4r reversal'
    assert bar >= s1, 'the handover exhaust precedes the ws1r reversal'
    if bar > B:
        return 'W4 PAST THE WINDOW', None
    return 'EXHAUST', bar
