"""Trace v4-lineage's baton chain on one leg, to the depth the mech is confirmed to.

WHAT THIS IS AND IS NOT. It is NOT the v4-lineage walker - no walker exists, because #17 (the open
mech) is held back by Joe on purpose. It is the reproducible proof of the one piece he confirmed on
1022: the SECOND WALK TO IB that settles a baton-pass whose new rider has already reversed.

Run it and it reproduces the 2026-08-31 trace in v4_lineage.md SS5 line for line.

usage: v4_lineage_trace.py '2026-08-31 19:00:00' '2026-08-31 21:30:00' 5 low
"""
import sys
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
from optimus9.analysis.jig import lift_off


def first_rev_at_or_after(R, t, side, frm, B):
    """the line's FIRST reversal at or after `frm`. -> (run, raw bar, stamp)

    THE STAMP IS THE BAR IT MAY BE ACTED ON, the raw bar is the anchor. jig.lift_off returns the
    bar the line left its extreme and its contract says the event is not knowable until
    `bar + wob - 1`; K.lift_stamp owns that arithmetic. The 1023 audit found this walk acting on
    the raw bar, 7 bars = 35 s before it existed, at LIFT_WOB 8.

    NO OOB FILTER, Joe 1023: *"the oob filter can't be applied to a reversal test"*. This had read
    "THE REVERSAL IS OOB-ANCHORED: a lift_off bar where the line IS oob" - which re-broke his 1022
    ruling *"I need to be able to test a reversal anywhere on the board"*. The oob condition lives
    on v4-ws5rbackstop's SIGNAL, where his spec puts it, not on the reversal detector.

    ANCHORED FORWARD FROM A BAR, NOT PICKED FROM A WINDOW. The first version of this took the
    LONGEST same-side oob run inside [A, B] and the window therefore chose the anchor: on
    2026-08-31 a 03:30-05:00 window picked the ws5r reversal at 03:55:25 and a 03:25-06:00 window
    picked a different one, giving two different verdicts for the same leg. The caller supplies the
    bar the walk starts from - for a backstop signal that is the ws5r reversal that fired it - and
    the window no longer decides anything.
    """
    a = R[t]
    m = (a >= K.OOB_HI) if side > 0 else (a <= K.OOB_LO)
    d = np.diff(np.r_[False, m, False].astype(np.int8))
    runs = [(int(s), int(e)) for s, e in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1)]
    L = [int(b) for b in lift_off(a, side, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB)
         if int(frm) <= b <= B]
    if not L:
        return None, None, None
    b = L[0]
    r = next((q for q in runs if q[0] <= b <= q[1]), None)
    return r, b, K.lift_stamp(b)


def ib_cross(R, t, frm, B):
    """the first ib cross at or after `frm` whose dwell is PROVEN. -> (cross, confirm, need)

    `need = int(TF x LIN_IB_DWELL)` bars in bounds from the cross bar. The CONFIRM bar is
    `cross + need - 1`, and it is the bar a caller may act on - before it, the dwell is a claim
    about bars nobody has seen. The whole dwell must fit at or before B.

    A BAR LOOP ON PURPOSE. v4_fast.ib_cross does the same thing with run arrays; keeping two
    independent forms is what makes `v4_fast.check()` worth running. The 1023 audit found the
    previous pair diverging at the B boundary on 111 of 339 probes.
    """
    a, need = R[t], K.lin_ib_dwell(t)
    k = int(frm)
    while k + need - 1 <= B:
        if K.ib(a[k]):
            j = k
            while j + 1 <= B and K.ib(a[j + 1]):
                j += 1
            if (j - k + 1) >= need:
                return k, k + need - 1, need
            k = j + 1
        else:
            k += 1
    return None, None, 0


def walk(R, start_tf, side, A, B, log=print):
    """The baton chain from `start_tf`. -> (the verdict, the bar, the rows).

    A is the bar the walk is ANCHORED on: every line's reversal is its first one at or after A, so
    the window never chooses the anchor. B bounds the forward search only.

    JOE'S 1022 RULE, verbatim in v4_lineage.md SS5. A rider that arrives with a reversal ALREADY in
    its lookback does not pass on that stale reversal: it walks to ib a SECOND time, and if the
    receiver of THAT pass is also already reversed, EXHAUST. His logic: *"the 2nd "walk to ib" gives
    enough time for a reversal to print without contention"*.

    THE 1023 CAUSALITY REPAIR, Joe's rulings. Every bar this walk acts on is a reversal STAMP or
    an ib CONFIRM bar, and the asserts below carry that claim rather than this sentence. The
    ex-fence gate reads R[nxt] AT the confirm bar - his option A. A receiver with no reversal in
    the data returns NO REVERSAL, not EXHAUST - his option B, because at `pas` "never reverses"
    and "reverses later" are the same observation and only the future separates them.
    """
    REV, RUN, ST = {}, {}, {}
    for t in range(start_tf, K.TF_CEILING + 3):
        RUN[t], REV[t], ST[t] = first_rev_at_or_after(R, t, side, A, B)
    rows = []

    def say(step, bar, read):
        rows.append((step, bar, read))
        log('| %s | %s | %s |' % (step, bar, read))

    assert K.LIN_PASS in ('ib', 'reversal'), 'LIN_PASS %r is not a mode' % (K.LIN_PASS,)

    def hand_over(tf):
        """The bar the baton leaves `tf` on, and the row that explains it. -> bar or None."""
        if K.LIN_PASS == 'reversal':
            say('the baton passes ON ws%d reversing' % tf, ln.U(ST[tf]),
                'his 1022 rule - no ib walk on the normal path')
            return ST[tf]
        cross, pas, held = ib_cross(R, tf, ST[tf], B)
        if pas is None:
            say('ws%d never crosses to ib' % tf, '-', 'the chain cannot advance')
            return None
        assert pas >= ST[tf], 'the ib confirm precedes the reversal stamp'
        say('ws%d walks to ib, dwell %d bars' % (tf, K.lin_ib_dwell(tf)), ln.U(pas),
            'crossed %s, dwell proven %d bars = %d s' % (ln.U(cross), held, held * 5))
        return pas

    rid = start_tf
    if ST.get(rid) is None:
        say('ws%d has no oob-anchored reversal' % rid, '-', '-')
        return 'NO REVERSAL', None, rows
    say('ws%d is the rider and reverses' % rid, ln.U(REV[rid]),
        'ws%dr %.2f, knowable %s' % (rid, float(R[rid][REV[rid]]), ln.U(ST[rid])))
    pas = hand_over(rid)
    if pas is None:
        return 'NO IB CROSS', None, rows

    while True:
        nxt = rid + 1
        if nxt > K.TF_CEILING:
            say('ws%d is the TF_CEILING' % rid, ln.U(pas), 'EXHAUST')
            return 'EXHAUST', pas, rows
        if not K.ex_fence(R[nxt][pas], side):
            say('ws%d -> ws%d, the receiver gate' % (rid, nxt), ln.U(pas),
                'ws%dr %.2f, not ex-fence - EXHAUST' % (nxt, float(R[nxt][pas])))
            return 'EXHAUST', pas, rows
        say('ws%d -> ws%d, the receiver gate' % (rid, nxt), ln.U(pas),
            'ws%dr %.2f, ex-fence YES' % (nxt, float(R[nxt][pas])))
        if ST.get(nxt) is None:
            say('ws%d has no oob-anchored reversal in the data' % nxt, ln.U(pas),
                'not knowable at this bar - NO REVERSAL, no trade')
            return 'NO REVERSAL', None, rows
        stale = K.looks_back(nxt) and ST[nxt] <= pas
        say('ws%d takes the baton' % nxt, ln.U(pas),
            'its reversal %s knowable %s, %s'
            % (ln.U(REV[nxt]), ln.U(ST[nxt]),
               'FOUND in its lookback' if stale else
               ('below the ws%d lookback floor - no lookback test' % K.LIN_LOOKBACK_FLOOR_TF
                if not K.looks_back(nxt) else 'not yet in its lookback')))
        if not stale:
            rid = nxt
            say('the normal path', ln.U(pas), 'ws%d waits for its own reversal' % rid)
            say('ws%d reverses' % rid, ln.U(REV[rid]),
                'ws%dr %.2f, knowable %s' % (rid, float(R[rid][REV[rid]]), ln.U(ST[rid])))
            pas = hand_over(rid)
            if pas is None:
                return 'NO IB CROSS', None, rows
            continue
        # HIS RULE: the second walk to ib
        c2, p2, h2 = ib_cross(R, nxt, pas, B)
        if p2 is None:
            say('the SECOND walk to ib on ws%d' % nxt, '-', 'it never crosses - the chain cannot advance')
            return 'NO IB CROSS', None, rows
        assert p2 >= pas, 'the second walk resolved before the baton-pass bar'
        say('the SECOND walk to ib on ws%d' % nxt, ln.U(p2),
            'dwell %d bars, held %d bars = %d s' % (K.lin_ib_dwell(nxt), h2, h2 * 5))
        n2 = nxt + 1
        if n2 > K.TF_CEILING:
            say('ws%d is the TF_CEILING' % nxt, ln.U(p2), 'EXHAUST')
            return 'EXHAUST', p2, rows
        if not K.ex_fence(R[n2][p2], side):
            say('ws%d -> ws%d, the receiver gate' % (nxt, n2), ln.U(p2),
                'ws%dr %.2f, not ex-fence - EXHAUST' % (n2, float(R[n2][p2])))
            return 'EXHAUST', p2, rows
        say('ws%d -> ws%d, the receiver gate' % (nxt, n2), ln.U(p2),
            'ws%dr %.2f, ex-fence YES' % (n2, float(R[n2][p2])))
        if ST.get(n2) is None:
            say('ws%d has no oob-anchored reversal in the data' % n2, ln.U(p2),
                'not knowable at this bar - NO REVERSAL, no trade')
            return 'NO REVERSAL', None, rows
        if K.looks_back(n2) and ST[n2] <= p2:
            say('ws%d is the second-new-rider' % n2, ln.U(p2),
                'its reversal %s knowable %s, FOUND in its lookback'
                % (ln.U(REV[n2]), ln.U(ST[n2])))
            say('EXHAUST', ln.U(p2), 'the second-new-rider carried a reversal too')
            return 'EXHAUST', p2, rows
        say('ws%d is the second-new-rider' % n2, ln.U(p2),
            'its reversal %s knowable %s, not yet in its lookback'
            % (ln.U(REV[n2]), ln.U(ST[n2])))
        rid = n2
        pas = hand_over(rid)
        if pas is None:
            return 'NO IB CROSS', None, rows


if __name__ == '__main__':
    A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
    tf, side = int(sys.argv[3]), (1 if sys.argv[4] == 'high' else -1)
    R = {t: ln.line('ws%dr' % t) for t in range(tf, K.TF_CEILING + 3)}
    print('# control ws5r 2026-09-03 00:35:00 = %.2f (DB-ruled known-good 12.48; the BANKED k6 rsi8 stc6 line reads 6.77 there)'
          % ln.line('ws5r')[ln.K('2026-09-03 00:35:00')])
    print('# RULED_OK %s. ib dwell int(TF x %.1f), oob %.1f/%.1f, ex-fence %s, ceiling ws%d'
          % (K.RULED_OK, K.LIN_IB_DWELL, K.OOB_LO, K.OOB_HI, K.fence(), K.TF_CEILING))
    print('# the reversal stamp adds LIFT_WOB - 1 = %d bars = %d s to every lift-off bar'
          % (K.LIFT_WOB - 1, (K.LIFT_WOB - 1) * 5))
    print()
    print('| the step | the bar | the reading |')
    print('|---|---|---|')
    v, b, _ = walk(R, tf, side, A, B)
    print()
    print('| the verdict | the bar |')
    print('|---|---|')
    print('| **%s** | %s |' % (v, ln.U(b) if b else '-'))
