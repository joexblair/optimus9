"""THE fdm RE-ENTRY. Joe 1102: *"bank this and make it the reentry machine"*.

HIS SPEC AS IT NOW STANDS, after two 1103 rulings replaced gcws30b with ws1b:

    -IF there is no trade open (because of a STOP, or because the machine is starting)
    --IF ws1b crosses to oob                     <- the window OPENS here
    ---the window CLOSES when ws1b crosses back to ib
    ---the gate is ws1r AND (ws2r or ws3r), each SEEN oob anywhere inside the window
    ---tested at the window's close. If the test is true, open a trade

WHAT REPLACED WHAT, and both are his.

  1103, the close    *"make the window open on gcws30b ex-5/95, and close the window on ws1b to
                     ib"*. Before this, gcws30b's own ib cross closed it
  1103, the open     *"this table tells me that gcws30b is dangerous / replace gcws30b crossing to
                     ex-5/95 with ws1b crossing to oob"*. gcws30b is out of this mech entirely

WHAT THE TABLE SAID. Over the whole tape, 9538 gcws30b ex-5/95 opens on both sides, 2926 of them
with no ws1b oob inside 2 minutes - 30.7%. Of those 2926, 2142 were followed by a ws1r/ws2r/ws3r
oob on the event's own side at a MEDIAN LAG OF 0 s, so the r was already oob when gcws30b opened.
The 2026-09-15 14:00:00 HIGH open is the case he read it from: ws1r already 98.85 HIGH oob, and
ws1b stayed ib for 33 minutes before going oob at 14:33:00 - on the LOW side, the opposite way.

WHAT EACH PIECE IS, and every one of them is his:

  the window         ws1b's oob excursion on one side: the bar it crosses to oob, through to the
                     confirm bar of its oob->ib cross at FDM_RE_IB_XWOB
  the gate's fence   HIS 1103 UPDATE: *"a line passes if it printed oob at any one bar inside the
                     window"*, replacing his 1102 *"ex v4mom fence"*. FDM_RE_GATE_FNC moves
                     75.0 -> 15.0, oob's SMALLER end, per his 1103 convention *"I use the
                     smallest number to describe the fence's max"*. Every read goes through
                     K.side_edge, which derives the pair and asserts the knob is at or under 50.
                     oob 15/85 is TIGHTER than 75/25, so fewer windows pass
  the gate           SEEN, not dwelling: *"the lines need to be seen in the window, but do not
                     need to dwell for the window's full range"*. Membership is recorded as the
                     walk passes each bar and never expires inside the window
  the fire bar       the window's close. *"tested at gcws30b window's close.  if the test is true,
                     open a trade"* - the sentence survives its subject's replacement
  the side           the oob side the lines were found on, his 1102 answer, which is now ws1b's own
                     oob side. `v4_signal.direction` maps it and that mapping is banked: a HIGH oob
                     side opens a SHORT
  the long window    his 1103: *"a long running ws1b excursion is a sign of a trending leg that
                     hasn't stopped yet"*. NOTHING BOUNDS IT - the gate's membership span is the
                     whole excursion, however long

THE WINDOW IS NOW THE SAME SPAN AS THE CADENCE WINDOW, and that is worth stating plainly: both are
ws1b's oob excursion ending at its ib cross. The two mechs read DIFFERENT TESTS over it - the
cadence event needs the nestle and ws3Mage ex-25/75, the re-entry needs ws1r AND (ws2r or ws3r)
past the v4mom fence - and they fire for different reasons, one to decide an open trade and one to
open a trade from flat.

THE LINEAGE WALK IS GONE FROM THIS MECH. His 1101 draft had *"the highest TF is tagged as the
rider / follow the lineage walk (baton pass on rider to ib) / IF lineage prints exhaustion"*. On
1102 he dropped all three: *"drop the lineage walk. make the gate ws1r AND (ws2r or ws3r), tested
at gcws30b window's close"*. There is no rider here and no baton.

CAUSAL, AND THE ASSERTS CARRY IT. Membership is read at or before the bar it is recorded on. The
close is `oob_ib_cross`'s own confirm bar, which that producer documents as the first bar the cross
is KNOWABLE. The gate is evaluated at the close using only bars from the open to the close.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_signal as SG
    import ln
    from optimus9.analysis.jig import oob_ib_cross, lift_off
finally:
    sys.stderr = _e

MECH = 'fdm-reentry'


def _beyond(a, side, fnc):
    """Is `a` at or beyond the mirrored `fnc` pair on `side`. -> bool array.

    `fnc` IS THE KNOB, NOT AN EDGE. It holds the SMALLER end of its pair - his 1103 convention -
    and K.side_edge derives the end this `side` reads, asserting the value is at or under 50.
    Handing in an already-resolved edge, K.OOB_HI 85.0 for a high side, trips that assert: the
    one home cannot tell an upper-end edge from an upper-end knob, and that is the point.
    """
    x = np.asarray(a, float)
    e = K.side_edge(fnc, side)
    return (x >= e) if int(side) > 0 else (x <= e)


def _opens(B1, G, side):
    """The window's open bars on `side`, by FDM_RE_WIN_OPEN. -> int array.

    An open is the first bar the opening test holds after a bar it did not.

      'ws1b'      ws1b oob on `side`. THE BANK
      'gcws30b'   gcws30b beyond FDM_RE_B_FNC on `side`
      'both'      ws1b oob on `side` AND gcws30b beyond its fence on EITHER side
      'first'     whichever of those two holds
      'sameside'  both on `side`

    The last three are MINE - he asked whether other permutations exist and said to run them.
    """
    w1 = _beyond(B1, side, K.OOB_FNC)
    m = str(K.FDM_RE_WIN_OPEN)
    if m == 'ws1b':
        hold = w1
    else:
        assert G is not None, 'this window arm reads gcws30b and none was handed in'
        gs = _beyond(G, side, float(K.FDM_RE_B_FNC))
        ge = gs | _beyond(G, -int(side), float(K.FDM_RE_B_FNC))
        hold = {'gcws30b': gs, 'both': w1 & ge, 'first': w1 | ge,
                'sameside': w1 & gs}[m]
    return np.flatnonzero(hold[1:] & ~hold[:-1]) + 1


def windows(B1, side, G=None):
    """The re-entry windows on `side`. -> [(the open bar, the close bar)].

    The close is the CONFIRM bar of the closing line's oob->ib cross whose own cross bar is after
    the open - the banked mech, not a value test. FDM_RE_WIN_CLOSE picks the line, and gcws30b's
    cross is read at the oob pair, as it always was.

    A window with no closing cross after it is NOT returned: it has not closed, so it cannot fire.
    One window per close, so overlapping opens collapse onto the same close rather than firing
    twice - the walk resumes after each close.
    """
    w = max(1, int(K.FDM_RE_IB_XWOB))
    cl = str(K.FDM_RE_WIN_CLOSE)
    if cl == 'ws1b':
        L = np.asarray(B1, float)
    else:
        assert G is not None, 'this window arm closes on gcws30b and none was handed in'
        L = np.asarray(G, float)
    crosses = [(int(c), int(cf)) for c, cf, s1 in oob_ib_cross(L, K.OOB_HI, K.OOB_LO, w)
               if int(s1) == int(side)]
    out, used = [], -1
    for o in _opens(B1, G, side):
        if int(o) <= used:
            continue
        nxt = next(((c, cf) for c, cf in crosses if c > int(o)), None)
        if nxt is None:
            break
        c, cf = nxt
        assert cf >= c, 'an ib cross confirm bar precedes its own cross bar'
        assert c > int(o), 'a window closes at or before it opens'
        out.append((int(o), int(cf)))
        used = int(cf)
    return out


def _lift_table(a, tf, side):
    """The lift-off STAMPS on one line for one side. -> int array.

    The LIFT-OFF KNOBS ARE THE MACHINE'S: LIFT_PTS samples, K.gap_for(tf) bars apart, LIFT_TOL
    r-points of tolerance, LIFT_WOB bars of hold, and K.lift_stamp puts the bar where the event is
    KNOWABLE. Only the series handed in changes with FDM_RE_REV_READ.
    """
    b = lift_off(np.asarray(a, float), int(side), int(K.LIFT_PTS), K.gap_for(int(tf)),
                 float(K.LIFT_TOL), int(K.LIFT_WOB))
    return np.asarray([K.lift_stamp(int(x)) for x in b], int)


def _gate6(v, side):
    """Does ws6r hold the gate on `side`, so the walk waits for ws6 to reverse. -> bool.

    FDM_RE_WS6_GATE 'ex2080' is the bank, 'oob' the arm it replaced. ex-20/80 is a SUPERSET of
    oob, so the bank can only send more windows down the wait branch.
    """
    g = str(K.FDM_RE_WS6_GATE)
    if g == 'ex2080':
        e = K.side_edge(K.FDM_FNC_2080, side)
        return (float(v) >= e) if int(side) > 0 else (float(v) <= e)
    assert g == 'oob', "FDM_RE_WS6_GATE is 'ex2080' or 'oob', got %r" % (g,)
    return (float(v) >= float(K.OOB_HI)) if int(side) > 0 else (float(v) <= float(K.OOB_LO))


def _infence(v):
    """STRICTLY inside the FDM_FNC_2080 pair, both ends. -> bool.

    "ex" INCLUDES oob, his standing rule, so a line past EITHER end is not in-fence.
    """
    lo, hi = K.fnc_pair(K.FDM_FNC_2080)
    return bool(lo < float(v) < hi)


def _xcross(X, Rl, frm, side, wob):
    """HIS 1104 MOD: the first bar ws{tf}x's cross of its own r CONFIRMS, after `frm`.

    -> (the confirm bar, the cross bar) | None.

    HIS SPEC: *"IF a ws{a TF}x crosses the ws{a TF}r line using emerging values and wob 12"*, with
    his own correction on direction - *"under for highside"*, which is the banked x-cross rule:

        a HIGH side   x crosses UNDER its own r
        a LOW side    x crosses OVER its own r

    THE HOLD IS FDM_RE_XWOB 12 bars = 60 s, his value, and the confirm bar is cross + wob - 1 so
    the hold is read on the cross bar and the 11 bars after it, never further.

    NO SEARCH BOUND. His spec gives none, and a bound would be a cap he did not ask for.
    CAUSAL: the confirm bar is asserted to be the last bar the hold reads.
    """
    X, Rl = np.asarray(X, float), np.asarray(Rl, float)
    n, w = len(X), max(1, int(wob))
    for i in range(int(frm) + 1, n):
        a0, b0, oa, ob = X[i - 1], X[i], Rl[i - 1], Rl[i]
        if not np.isfinite([a0, b0, oa, ob]).all():
            continue
        crossed = (a0 >= oa and b0 < ob) if int(side) > 0 else (a0 <= oa and b0 > ob)
        if not crossed:
            continue
        end = i + w
        if end > n:
            break
        seg = [(X[j] < Rl[j]) if int(side) > 0 else (X[j] > Rl[j]) for j in range(i, end)]
        if all(seg):
            cf = i + w - 1
            assert cf >= i, 'a cross confirms before it crosses'
            return cf, i
    return None


def _xmod(EM, R, tf, frm, side, e_fence, hi_tf):
    """HIS 1104 MOD, one waiting point. -> (the fire bar, why) | (None, why).

    HIS SPEC, in order:
      1  ws{tf}r is ex-20/80 on the side and waiting to reverse
      2  ws{tf}x crosses ws{tf}r on EMERGING values and holds FDM_RE_XWOB 12 bars = 60 s
      3  ws{tf+1}r is in-fence
      4  rev-trade - his generic *"send a signal to the router, and let the router handle the
         decisions"*, which from flat is an OPEN

    `EM` IS THE EMERGING LADDER, not the re-entry's own reversal-read source. His spec says
    *"using emerging values"*, and the cross plus the ex-fence test both read it - they describe
    the same bar and the same line, so they take the same series. THAT PAIRING IS MY CALL.
    `R` is the chart-matched ladder and carries only the ws{tf+1}r in-fence test, at
    FDM_RE_XCROSS_UP_READ 'closed_prev', because his own example number 43 is that value.

    `e_fence` is the side's own edge of the fence ws{tf}r must be past. Test 1 is read AT THE
    CROSS BAR, because that is the bar his *"is ex-20/80-fence and waiting to reverse"* describes.
    `hi_tf` is the ladder's top, so a waiting point at the top has no line above it and cannot fire.
    """
    if int(tf) + 1 > int(hi_tf):
        return None, 'ws%d has no line above it on this ladder' % int(tf)
    try:
        X = np.asarray(ln.line('ws%dx' % int(tf)), float)
    except Exception as ex:
        return None, 'ws%dx does not load - %s' % (int(tf), type(ex).__name__)
    r = _xcross(X, EM[int(tf)], int(frm), int(side), int(K.FDM_RE_XWOB))
    if r is None:
        return None, 'ws%dx never crosses ws%dr after %s' % (int(tf), int(tf), ln.U(int(frm)))
    cf, cr = r
    vr = float(np.asarray(EM[int(tf)], float)[cr])
    if not ((vr >= e_fence) if int(side) > 0 else (vr <= e_fence)):
        return None, ('ws%dr is %.2f at the %s cross, not past %g'
                      % (int(tf), vr, ln.U(cr), e_fence))
    up = R if str(K.FDM_RE_XCROSS_UP_READ) == 'closed_prev' else EM
    vu = float(np.asarray(up[int(tf) + 1], float)[cr])
    if not _infence(vu):
        return None, ('ws%dr is %.2f at the %s cross, not in-fence'
                      % (int(tf) + 1, vu, ln.U(cr)))
    return cf, ('ws%dx crossed ws%dr %s and held %d bars to %s, ws%dr %.2f past %g, ws%dr %.2f'
                ' in-fence' % (int(tf), int(tf), ln.U(cr), int(K.FDM_RE_XWOB), ln.U(cf), int(tf),
                               vr, e_fence, int(tf) + 1, vu))


def signals(B1, R, side=None, G=None, EMR=None):
    """HIS 1104 RE-ENTRY: the ws5/ws6 reversal walk. -> list of signals, bar-ordered.

    HIS SPEC, verbatim and in his indentation:

        -if a cadence window opens
        --walk until ws5 reverses
        ---if ws5r reverses while ex-20/80-fence
        ----if ws6r is oob
        -----walk forward until ws6r reverses
        ----else if ws6r is not oob
        -----scan the wsf TFs above ws6 for a wsf ws{higher TF}r that is infence
        -----if a higher wsf TF r is infence
        ------open a trade on the last to fire, out of ws5r reversing or ws6r reversal or ws1b
              crossing to ib
        #all signals are sameside of the cadence

    IT REPLACED THE ws1r AND (ws2r or ws3r) GATE OUTRIGHT, his 1104 *"replace it"*. That gate
    tested membership over the window and fired at the window's close; this walks forward from the
    open and fires on the last of three named events.

    `B1` is ws1b, the line whose oob excursion IS the window. `R` is the CHART-MATCHED r ladder and
    `EMR` the emerging one, needed only when FDM_RE_REV_READ is 'emerging'. `side` runs both when
    None. THE SIDE IS THE WINDOW'S OOB SIDE and v4_signal.direction maps it - a HIGH oob window
    opens a SHORT.

    THE SIGNAL BAR IS THE LAST-TO-FIRE BAR, so the router's fire_bar puts the open one bar later,
    his "just OPEN, 1 bar". Every read is at or before that bar: the two reversals are STAMPS and
    the ib close is a CONFIRM bar, so nothing here is knowable later than the bar it is read on.
    The asserts carry that rather than a comment.

    HIS ONE ACCEPTED LOSS, 1104: *"the only one that we have to accept is 09-15 1331 - there's no
    available high side cadence to close the 1331 LONG before it is stopped"*. That window is not
    special-cased anywhere; it is accepted as the mech's own output.
    """
    sides = (-1, +1) if side is None else (int(side),)
    rd = str(K.FDM_RE_REV_READ)
    assert rd in ('closed_prev', 'emerging'), \
        "FDM_RE_REV_READ is 'closed_prev' or 'emerging', got %r" % (rd,)
    if rd == 'emerging':
        assert EMR is not None, 'the emerging read needs the emerging ladder handed in'
    SRC = R if rd == 'closed_prev' else EMR
    #   HIS 1104 MOD READS EMERGING, *"using emerging values"*, whatever the reversal read is.
    assert not int(K.FDM_RE_XCROSS_ON) or EMR is not None, \
        'his x-cross mod needs the emerging ladder handed in'
    #   HIS 1104 PAIR KNOBS: ws5 and ws6 are the default and the spec, and the pair lifts without
    #   a second copy of this walk. The scan floor follows the gate line by default - the mech's
    #   own shape - or sits at a fixed TF for his *"scan higher than ws12"* read.
    tf5, tf6 = int(K.FDM_RE_REV_TF), int(K.FDM_RE_GATE_TF)
    assert tf6 > tf5, 'the gate line must sit above the reversal line, got ws%d and ws%d' % (tf5, tf6)
    CLIMB = str(K.FDM_RE_CLIMB)
    assert CLIMB in ('off', 'value', 'reversal'), \
        "FDM_RE_CLIMB is 'off', 'value' or 'reversal', got %r" % (CLIMB,)
    assert int(K.FDM_RE_CLIMB_HI) > tf5, 'the climb ceiling must sit above the reversal line'
    fl = str(K.FDM_RE_SCAN_FLOOR)
    if fl == 'gate':
        lo5 = tf6 + 1
    else:
        assert fl == 'ws13', "FDM_RE_SCAN_FLOOR is 'gate' or 'ws13', got %r" % (fl,)
        lo5 = max(13, tf6 + 1)
    hi5 = int(K.FDM_RE_SCAN_HI)
    assert lo5 > tf6, 'the scan band starts above the gate line, his "the TFs above ws6"'
    assert hi5 >= lo5, 'the scan band ends below where it starts, ws%d..ws%d' % (lo5, hi5)
    out = []
    for sd in sides:
        L5 = _lift_table(SRC[tf5], tf5, sd)
        L6 = _lift_table(SRC[tf6], tf6, sd)
        e5 = K.side_edge(K.FDM_RE_WS5_FNC, sd)
        for o, c in windows(B1, sd, G):
            #   HIS "walk until ws5 reverses": the FIRST ws5 reversal after the window opens, and
            #   it is NOT bounded by the window's close - his *"regardless of when ws1b returns to
            #   ib"*.
            #   ── HIS 1104 MOD, waiting point one ───────────────────────────────────────────
            #   The walk is waiting for ws{tf5}r to reverse. If ws{tf5}x crosses ws{tf5}r first
            #   and holds, and the line above is in-fence, the signal fires at that confirm bar
            #   instead. The EARLIER of this and the normal path's fire bar wins, because a walk
            #   forward meets whichever comes first - the same rule the cadence walk uses and it
            #   needs no priority knob.
            xm, xwhy = (None, 'off')
            if int(K.FDM_RE_XCROSS_ON) and str(K.FDM_RE_XCROSS_TFS) in ('both', 'rev'):
                xm, xwhy = _xmod(EMR, R, tf5, int(o), sd, e5, int(K.L2_MOM_MAXTF))
            nx5 = L5[L5 > int(o)]
            if not nx5.size:
                #   NO ws{tf5} REVERSAL AT ALL. Before the mod this window produced nothing; now
                #   the mod can still carry it, so the early exit only applies when the mod is
                #   silent too.
                if xm is None:
                    continue
                fb = int(xm)
                if int(K.FDM_RE_FIRE_IB):
                    fb = max(fb, int(c))
                assert fb >= int(o), 'a mod fire bar precedes its own window open'
                out.append(dict(bar=fb, side=sd, src=int(o),
                                why='%s window %s..%s. HIS MOD, no ws%d reversal: %s%s'
                                % ('HIGH' if sd > 0 else 'LOW', ln.U(int(o)), ln.U(int(c)),
                                   tf5, xwhy,
                                   '' if fb == int(xm) else
                                   '; ws1b ib close %s is the last to fire' % ln.U(int(c)))))
                continue
            b5 = int(nx5[0])
            v5 = float(np.asarray(R[tf5], float)[b5])
            #   HIS "stop": the first ws5 reversal is the only test point. Not ex-fence there and
            #   the window produces nothing.
            if not ((v5 >= e5) if sd > 0 else (v5 <= e5)):
                continue
            v6 = float(np.asarray(R[tf6], float)[b5])
            held = _gate6(v6, sd)
            if CLIMB != 'off':
                #   HIS DYNAMIC CLIMB. Step up from the line above the one that reversed, while
                #   each rung's r is ex-fence, and stop at the first in-fence rung. 'reversal'
                #   makes each ex-fence rung print its own lift-off before the climb steps up, so
                #   the climb carries a bar as well as a verdict.
                rungs, b6, at = [], None, b5
                for t in range(tf5 + 1, int(K.FDM_RE_CLIMB_HI) + 1):
                    v = float(np.asarray(R[t], float)[at])
                    if _infence(v):
                        rungs.append((t, v, None))
                        break
                    if not _gate6(v, sd):
                        #   NEITHER in-fence NOR past the gate: the rung says nothing, so the
                        #   climb ends with no trade rather than stepping over it.
                        rungs = []
                        break
                    if CLIMB == 'reversal':
                        LT = _lift_table(SRC[t], t, sd)
                        nx = LT[LT > at]
                        if not nx.size:
                            rungs = []
                            break
                        at = int(nx[0])
                        b6 = at
                    rungs.append((t, v, b6))
                if not rungs or rungs[-1][2] is not None:
                    continue
                got = (rungs[-1][0],)
                scan = at
            else:
                if held:
                    nx6 = L6[L6 > b5]
                    if not nx6.size:
                        continue
                    b6 = int(nx6[0])
                    scan = b6
                else:
                    b6, scan = None, b5
                got = tuple(t for t in range(lo5, hi5 + 1)
                            if _infence(float(np.asarray(R[t], float)[scan])))
                if not got:
                    continue
            #   HIS LAST TO FIRE. FDM_RE_FIRE_IB 1 keeps ws1b's ib close in the set, his spec.
            evs = [('the ws5 reversal', b5)]
            if b6 is not None:
                evs.append(('the ws6 reversal', b6))
            if int(K.FDM_RE_FIRE_IB):
                evs.append(('the ws1b ib close', int(c)))
            lab, fire, by_mod = (*max(evs, key=lambda x: x[1]), False)
            assert all(fire >= v for _, v in evs), 'the fire bar precedes one of its own events'
            #   ── HIS 1104 MOD, waiting point two, and the race between the two paths ────────
            #   Waiting point two is the walk waiting for ws{tf6}r to reverse, which only exists
            #   on the `held` branch. Its search starts at the ws{tf5} reversal.
            if (int(K.FDM_RE_XCROSS_ON) and held
                    and str(K.FDM_RE_XCROSS_TFS) in ('both', 'gate')):
                e6 = K.side_edge(K.FDM_RE_WS5_FNC, sd)
                xm6, xwhy6 = _xmod(EMR, R, tf6, b5, sd, e6, int(K.L2_MOM_MAXTF))
                if xm6 is not None and (xm is None or int(xm6) < int(xm)):
                    xm, xwhy = int(xm6), 'ws%d waiting: %s' % (tf6, xwhy6)
            if xm is not None:
                xfb = int(xm)
                if int(K.FDM_RE_FIRE_IB):
                    xfb = max(xfb, int(c))
                if xfb < fire:
                    lab, fire, by_mod = 'HIS MOD - %s' % xwhy, xfb, True
            #   THE INVARIANT SPLITS, because his 1104 mod fires BEFORE the ws{tf5} reversal
            #   on purpose. The window-open half holds for every path; the reversal half holds
            #   only for the normal one, and the mod's exception is named rather than dropped.
            assert fire >= int(o), 'the fire bar precedes its own window open'
            assert fire >= b5 or by_mod, \
                'the fire bar precedes the ws%d reversal with no mod firing' % tf5
            out.append(dict(SG.signal(fire, sd, MECH, o,
                                      '%s window %s..%s, %.1f min, opened on %s. ws%d reversed %s'
                                      ' at %.2f, ex-%g/%g. ws%dr %.2f %s the %s gate%s. in-fence'
                                      ' %s: %s. last to fire %s'
                                      % ('HIGH' if sd > 0 else 'LOW', SG.why_time(o),
                                         SG.why_time(int(c)), (int(c) - o) * 5 / 60.0,
                                         K.FDM_RE_WIN_OPEN, tf5, SG.why_time(b5), v5,
                                         *K.fnc_pair(K.FDM_RE_WS5_FNC),
                                         tf6, v6, 'holds' if held else 'fails',
                                         K.FDM_RE_WS6_GATE,
                                         '' if b6 is None else
                                         ', ws%d reversed %s' % (tf6, SG.why_time(b6)),
                                         'ws%d..ws%d' % (lo5, hi5),
                                         ', '.join('ws%d' % t for t in got), lab)),
                            b5=b5, v5=v5, v6=v6, held6=held, b6=b6, scan=scan,
                            got=tuple(got), last=lab, close=int(c)))
    return sorted(out, key=lambda x: x['bar'])
