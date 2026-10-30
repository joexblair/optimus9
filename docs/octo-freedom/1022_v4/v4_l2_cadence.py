"""lineage2's FOUR CADENCES, and nothing else. Joe 1025.

ONE RESPONSIBILITY: say which bars a lineage2 walk is allowed to make a decision on. It runs no
walk, picks no rider and passes no baton.

WHY CADENCES EXIST, his framing:

    the key difference for lineage2: v4lineage tests `r` mom states on every bar, lineage2 tests
    them on a determined cadence

    the point of cadences: they are where decisions are made. testing at set points (like 0723)
    provides the opportunity to override a poor signal (ws6r exhaust) if a better signal (ws7
    ex-fence) has presented itself

TARGET-SIDE THROUGHOUT. Joe 1025: *"all calcs and decisions are target-side"*.

NO DWELL ON ANY ib CROSS HERE, his ruling: *"no dwell. the way I see it: because we're on closed
bars, we have an automatic wob. it also means I have TV values that are precisely aligned with what
the code sees"*. SUPERSEDED 1027: *"add the wob12 to all crosses to ib and crosses to
in-mom-fnc"*, so every cross INTO the gentler state now carries LIN2_CROSS_WOB and the actionable
bar is the LAST bar of the hold. Crosses the other way still carry no dwell.

STATE ON CLOSED, REVERSAL TIMING ON EMERGING - Joe's 1026 ruling, his words:

    add all lines to csw1-12. these closed lines will give us more accurate fence/exfence baton
    decisions
    with ws1-12, emerg: time the reversals
    best of both worlds

t3 READS THE BOARD PROXY, not two dicts. Joe 1026: *"build a proxy that sends the emerging values
to the gate decision"*. `v4_l2_proxy.Board` holds both ladders and routes each read - STATE to
closed, reversal TIMING to emerging, and t3's two GATES to whichever `L2_GATE_MODE` names, which is
'emerging' on his instruction. The routing table is in that one file. t1 and t2 are closed throughout, and both t1 qualifiers are cws1r - he corrected his
own handover: *"this is my wrong: both should be cws1r"*.

cws1r's REVERSAL CARRIES ITS OWN WOB, `L2_CWS1R_WOB` 1. Joe 1026: *"a lineage2-only wob 1 for
cws1r"* / *"cws1 is closed bar, so the wob is built-in"*. LIFT_WOB 8 filters 69.4% on the emerging
ws1r and 3.0% on cws1r, and on 99.2% of cws1r lift-offs the value does not move across the hold -
the wob is shorter than one cws1r bar. At wob 1 the stamp IS the raw bar, which is what cost his
2026-08-29 07:23 walk its cadence under wob 8.

t4 IS NOT DETECTED HERE. It is a consequence of the walk's own rider state - a non-oob rider that
reverses with no in-lin-hop candidate - so `v4_lineage2` raises it where the rider is known.
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
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
from optimus9.analysis.jig import lift_off, oob_ib_cross
sys.stderr = _e

HTF_LO = 7                                     # *"any of ws7r to ws12r (HTF lines)"* - Joe 1025
_LO = {}


def ws1r_revs(line, side):
    """ws1r's lift-off RAW bars at lineage2's own wob. -> a sorted int array, cached.

    `v4_fast.revs` keys its cache on K.LIFT_WOB 8, so it cannot serve `L2_CWS1R_WOB` 1 - this is a
    separate cache on the same producer, not a second detector.
    """
    key = (id(line), int(side), int(K.L2_CWS1R_WOB))
    if key not in _LO:
        _LO[key] = np.array(sorted(int(x) for x in lift_off(
            line, side, K.LIFT_PTS, K.gap_for(1), K.LIFT_TOL, K.L2_CWS1R_WOB)), dtype=int)
    return _LO[key]


def _stamp(b):
    """The bar a ws1r lift-off becomes actionable on, at lineage2's wob. -> bar.

    `K.lift_stamp` adds LIFT_WOB - 1; lineage2's ws1r wob is its own, so the arithmetic is here
    and there is one copy of it.
    """
    return int(b) + max(0, int(K.L2_CWS1R_WOB) - 1)


def _runs(a):
    """Contiguous True runs of `a`. -> [(start, end)] inclusive."""
    d = np.diff(np.r_[False, a, False].astype(np.int8))
    return list(zip(np.flatnonzero(d == 1).astype(int), (np.flatnonzero(d == -1) - 1).astype(int)))


def b1_beyond(b1, side, hold=None, dwell=None):
    """cws1b's ONE oob state. Every consumer in the fork reads it here. -> bool array.

    TWO RULES, BOTH HIS, ONE ON EACH EDGE:

    THE DWELL ON THE ENTRY, LIN2_B1_OOB_DWELL, Joe 1030: *"add a minimum oob dwell of 12 bars for
    cws1b"* and *"the dwell resets on each ws1b blip back to ib"*. The state turns on at the
    entry bar + D - 1 and only if cws1b was past the fence on EVERY bar of that window. One bar
    back inside restarts the count from zero, so a run shorter than D never counts as oob at all.
    It is taken on the RAW fence read, before the hold below, because the hold's whole job is to
    bridge a brief return and his ruling is that such a return resets the dwell. At D 0 or 1
    nothing moves.

    THE HOLD ON THE RETURN, LIN2_B1_HOLD, Joe 1029: *"could the ws1b test incorporate the wob 12?
    ie if ws1b to ib has not qualified its wob 12, then its value is not passed in"*, after
    *"what I'm trying to capture is the ws1b low oob excursion that runs from 0100 to 0121"*. A
    crossing back inside counts only once it has held H bars; until then cws1b still reads as
    beyond the fence. At H 0 or 1 nothing moves.

    CAUSAL ON BOTH EDGES. The entry asks whether the last D bars including this one were all past
    the fence. The return asks whether the last crossing inside is at least H bars old and stayed
    inside throughout. Neither reads a bar after the one it answers for.
    """
    raw = np.asarray(K.oob_mask(np.asarray(b1, float), int(side)), bool)
    d = int(K.LIN2_B1_OOB_DWELL) if dwell is None else int(dwell)
    if d > 1:
        n0 = len(raw)
        m = np.zeros(n0, bool)
        for a, b in _runs(raw):
            a, b = int(a), int(b)
            if b - a + 1 >= d:
                assert raw[a:a + d].all(), 'a dwell window has a bar that is not past the fence'
                m[a + d - 1:b + 1] = True
    else:
        m = raw
    h = int(K.LIN2_B1_HOLD) if hold is None else int(hold)
    if h <= 1:
        return m
    n = len(m)
    out = m.copy()
    i = 1
    while i < n:
        if (not m[i]) and m[i - 1]:
            j = i
            while j + 1 < n and not m[j + 1]:
                j += 1
            run = j - i + 1
            if run >= h:
                #   credited from its own confirm bar, i + h - 1. Before that it still reads beyond.
                out[i:i + h - 1] = True
            else:
                out[i:j + 1] = True
            i = j + 1
            continue
        i += 1
    return out


def _oob(line, side):
    """The oob mask, through `K.oob_mask` so the rule has one home - his 1026 point."""
    return K.oob_mask(line, side)


def t1(CL, side, A, B):
    """TYPE 1 - cws1b is oob. -> [(the cadence bar, why)].

        --if cws1b is oob
        ---walk to "%cws1b crossing from oob to ib%"
        ---IF (cws1r had "reversed on target-side of 50" while cws1b was oob) OR (cws1r reverses on
         target-side of 50 in the 2 minutes (CAUSALLY) following the cws1b oob to ib cross)
        ----fire a cadence event on the "%cws1b crossing from oob to ib%" bar or the "late cws1r
         reversing" bar, whichever is last

    THE REVERSAL IS lift_off ON cws1r, with the value's side of 50 tested at the stamp - the exact
    construct `v4_w4_handover._next_ws1r_rev` uses for his *"same-side of 50"* wording.

    THE RAW BAR IS WHAT THE WINDOWS BOUND, and the STAMP is only the fire bar. That is his standing
    rule, carried in `v4_fast.revs`: *"RAW, on purpose: the raw bar is the anchor and the identity
    of the reversal. Every caller that ACTS on one passes it through K.lift_stamp first"*.

    THE FIRST BUILD BOUNDED BOTH WINDOWS BY THE STAMP and so missed his 2026-08-29 07:48 example.
    His cws1b oob run is 07:46:00..07:46:55, its ib cross 07:47:00, and the 120 s grace reaches
    07:49:00. The cws1r reversal's raw bar is 07:49:00 - exactly on the edge, inside - and its
    stamp is 07:49:35, 35 s past. Bounding by the stamp threw the event away.

    *"WHICHEVER IS LAST"* is his standing race shape - `max(the ib cross bar, the reversal stamp)`.

    EVERY CADENCE ROW IS (bar, type, why). The TYPE is carried, not encoded in the `why` string,
    because the walk now treats the types differently - Joe 1026: *"jumping belongs only to t1 and
    t2"* - and a walk deciding behaviour by string-matching a report field is the defect that broke
    the trace when he shortened the detail column.
    """
    b1 = np.asarray(CL['b'], float)
    r1 = np.asarray(CL['r'][1], float)
    #   ws1b's state, held per LIN2_B1_HOLD. At 0 this is the plain read and nothing moves.
    oob = b1_beyond(b1, side)
    raws = ws1r_revs(r1, side)
    grace = max(0, int(K.L2_T1_GRACE_S) // 5)
    out = []
    #   WOB 12 ON THE CROSS, Joe 1027. `c` is still the cross bar - it is what the oob run is
    #   matched against - and `cf` = c + LIN2_CROSS_WOB - 1 is the first bar the cross may be ACTED
    #   on. The cadence fires on `cf`, or on the late reversal's stamp, whichever is last.
    for c, cf, s in oob_ib_cross(b1, K.OOB_HI, K.OOB_LO, int(K.LIN2_CROSS_WOB)):
        if s != int(side) or not (int(A) <= cf <= int(B)):
            continue
        run = next((r for r in _runs(oob) if r[1] == c - 1), None)
        if run is None:
            continue
        s0, s1 = run
        #   the DURING branch: the RAW reversal inside the oob run, cws1r on the target side of 50
        during = [int(x) for x in raws
                  if s0 <= x <= s1 and K.side_of(r1[_stamp(x)]) == int(side)]
        if during:
            bar = max(int(c), _stamp(during[-1]))            # *"whichever is last"*
            assert bar >= int(c), 'the t1 cadence precedes its own cws1b ib cross'
            out.append((bar, 't1', 'ws1b oob %s..%s, ws1r reversed %s during, stamp %s'
                        % (ln.U(s0)[11:], ln.U(s1)[11:], ln.U(during[-1])[11:],
                           ln.U(_stamp(during[-1]))[11:])))
            continue
        #   the GRACE branch: the RAW reversal forward of the cross, inside L2_T1_GRACE_S
        late = [int(x) for x in raws
                if c < x <= c + grace and K.side_of(r1[_stamp(x)]) == int(side)]
        if late:
            bar = max(int(c), _stamp(late[0]))               # *"whichever is last"*
            assert bar >= int(c), 'the t1 cadence precedes its own cws1b ib cross'
            out.append((bar, 't1', 'ws1b ib %s, ws1r reversed %s inside the %ds grace, stamp %s'
                        % (ln.U(c)[11:], ln.U(late[0])[11:], K.L2_T1_GRACE_S,
                           ln.U(_stamp(late[0]))[11:])))
    return out


def t2(CL, side, A, B):
    """TYPE 2 - cws1r is oob and cws1b is NOT oob. -> [(the cadence bar, why)].

        --IF cws1r is oob and cws1b is NOT oob
        ---fire a cadence event when cws1r crosses to ib

    cws1b's oob state is read at the CROSS bar, which is the bar the event fires on.
    """
    b1 = np.asarray(CL['b'], float)
    r1 = np.asarray(CL['r'][1], float)
    held = b1_beyond(b1, side)      # ws1b's state, held per LIN2_B1_HOLD
    out = []
    #   WOB 12 ON THE CROSS, Joe 1027: the cadence fires on the CONFIRM bar, c + wob - 1.
    for c, cf, s in oob_ib_cross(r1, K.OOB_HI, K.OOB_LO, int(K.LIN2_CROSS_WOB)):
        if s != int(side) or not (int(A) <= cf <= int(B)):
            continue
        if held[cf]:
            continue                               # that is t1's case, not t2's
        out.append((int(cf), 't2', 'ws1r ib cross %s confirmed %s at wob %d, ws1b %.2f not oob,'
                                   ' ws1b hold %d'
                    % (ln.U(c)[11:], ln.U(cf)[11:], K.LIN2_CROSS_WOB, b1[cf],
                       K.LIN2_B1_HOLD)))
    return out


def counter_oob(CL, side, A, B):
    """cws1b CROSSING INTO THE OOB OPPOSITE THE TARGET SIDE. -> [(the cadence bar, type, why)].

    HIS SPEC, 1026, verbatim: *"create a cadence when cws1b crosses to counter target-side oob (eg
    08-30 1921)"*, and on 1027 he marked it IMPORTANT and said *"go"*.

    HIS EXAMPLE LANDS EXACTLY. From 2026-08-30 19:19 cws1b reads 41.20, 26.38, then 14.16 at
    19:21:00 - the first bar at or past the LOW oob fence 15, inside a HIGH-target walk.

    NO WOB. He named no dwell, so the bar reported is the RAW cross bar - the first bar at or past
    the fence. A wob would be a value I picked.

    THE SIDE IS THE COUNTER ONE. A HIGH-target walk watches cws1b <= 15.0, a LOW-target walk
    cws1b >= 85.0. `K.oob_mask(v, -side)` is the one home for that test, so this cannot drift from
    every other oob read in the fork.

    cws1b IS NOT BOUNDED 0..100. Measured over 08-30..09-03 its firings include 105.07 and -18.11.
    The fence reads them the same way and nothing clips.

    THE TYPE STRING IS A DESCRIPTION, NOT A NAME. t1..t4 are HIS numbers; he has not numbered this
    one, so the rows carry 'cws1b counter-oob' until he names it.

    WHAT IT DOES AT THE CADENCE is nothing of its own - it is a cadence, so the walk's own board
    review runs there, exactly as it does at a t1 or a t2. Measured on today's walks before it was
    wired: 69 firings between the arm and the exhaust across 08-30..09-03, of which 62 would reach
    the exhaust branch, 5 HOLD and 2 pass the baton.
    """
    b1 = np.asarray(CL['b'], float)
    #   THE COUNTER SIDE'S oob, read through cws1b's ONE state so his 1030 dwell applies here too.
    #   At LIN2_B1_OOB_DWELL 0 this is the same mask K.oob_mask returned and nothing moves.
    m = np.asarray(b1_beyond(b1, -int(side)), bool)
    cr = np.flatnonzero(m[1:] & ~m[:-1]) + 1           # the rising edge: the first qualifying bar
    out = []
    for c in cr:
        c = int(c)
        if not (int(A) <= c <= int(B)):
            continue
        out.append((c, 'ws1b counter-oob',
                    'ws1b %.2f qualified the %s oob %s at dwell %d'
                    % (b1[c], 'LOW' if int(side) > 0 else 'HIGH', ln.U(c)[11:],
                       K.LIN2_B1_OOB_DWELL)))
    return out


def barrage(BD, side, A, B, tol_s=None, lines=None, min_tf=None, fence=None,
            fit=None, win_s=None, mode=None, cand=None, max_tf=None):
    """THE BARRAGE. -> [(the cadence bar, 'barrage', why)].

    HIS QUESTION, 1027, which is where the mech came from:

        if there was a tolerance that allowed for low-side ws1r reversing to pseudo fit "inside the
        ws1Mage oob to ib" at 02:29, would it have detected a barrage of low-side reversals and
        declared exhaust?

    then, shown that the tolerance alone selects nothing: *"It needs a second condition - the
    barrage itself is the obvious candidate, agreed"*, and *"bank the barrage results and wire the
    mech into the chain"*.

    THE THREE CONDITIONS, his:

        1  ws1Mage crosses from oob to ib on the side
        2  ws1r reverses on the SAME side within LIN2_BARRAGE_TOL_S of that cross
        3  at least LIN2_BARRAGE_LINES r lines reverse on that side between the cross and the
           ws1r reversal

    and a fourth he ruled on 1027 - *"dropping 0229 is ok - 0234 picked it up"* - so the barrage
    must also reach LIN2_BARRAGE_MIN_TF 9.

    WHAT IT DOES, his words: *"both - a cadence keeps the walk's transactions uniform, and exhaust
    will fire"*. So this produces a CADENCE, and `v4_lineage2.walk` exhausts on it. The exhaust is
    NOT routed through the mage-cascade truth table first - his *"exhaust WILL fire"* is read
    literally, and a cascade that matched the trade would otherwise veto it. That reading is MINE
    and it is the one open question on this mech; the arm that defers to the cascade is measured
    beside it rather than argued.

    THE SIDE IS THE WALK'S TARGET SIDE. A barrage on the side the walk is hunting says that side's
    move is spent. His own reading of the 02:29/02:34 pair is the climb that follows it: *"the
    climb from 0234 to the 0244 high-side exhaust is more lucrative than 0229 to 0244"* - a LOW
    barrage, then a climb to a HIGH exhaust. He wrote *"the incoming SHORT"* in the same sentence,
    which reads the other way; the climb clause is what is built, and the side is his to correct.

    THE CADENCE BAR IS THE LAST CONTRIBUTING REVERSAL'S STAMP, never a raw bar. Every reversal in
    the count has to be confirmed before the count is knowable, so the bar served is
    max(K.lift_stamp(b)) over the contributing lines. Two asserts carry that claim.

    THE WOB ON THE ws1Mage CROSS IS 1, not LIN2_CROSS_WOB 12. He narrowed that knob himself:
    *"I need wob12 only for r lines crossing back to ib, or to in-mom-fnc"*, and ws1Mage is not an
    r line.

    THE REVERSAL WOB IS LIFT_WOB 8, not LIN2_REV_WOB 12. The thresholds above were measured at
    LIFT_WOB, and LIN2_REV_WOB is the latch's own wob by his *"THIS MECH ONLY"* ruling.

    THE COUNT IS ws1..L2_MOM_MAXTF, which is 12. The Board carries ws1..ws30, and the first build
    of this function counted all of them - so the 2026-08-30 02:34 barrage read 8 lines instead of
    7 (ws14), 09:43 read 11 instead of 8 (ws15, ws18, ws19), and three instances appeared that are
    not in the banked list at all: 04:51:35 on ws16/ws18/ws24, 16:19:30 on ws13/ws15/ws27 and
    23:49:30 on ws14. Worse, LIN2_BARRAGE_MIN_TF 9 was being satisfied by a dtf line rather than by
    ws9..ws12. The thresholds were measured over ws1..ws12, so the count is bounded by his own
    ladder knob. dtf lines (>ws12, his 1017 band name) are not on the lineage2 board.

    THE THRESHOLDS CAN BE OVERRIDDEN BY A CALLER, for a sweep only. `tol_s`, `lines` and `min_tf`
    default to the banked knobs, which is what the chain gets. A sweep passes explicit values so
    there is still ONE copy of the rule - the alternative was a second detection loop in the sweep
    script, and that is exactly the drift that put dtf lines in the first count.
    """
    tol_s = int(K.LIN2_BARRAGE_TOL_S) if tol_s is None else int(tol_s)
    need = int(K.LIN2_BARRAGE_LINES) if lines is None else int(lines)
    min_tf = int(K.LIN2_BARRAGE_MIN_TF) if min_tf is None else int(min_tf)
    fence = str(K.LIN2_BARRAGE_FENCE) if fence is None else str(fence)
    assert fence in ('any', 'in', 'ex'), 'LIN2_BARRAGE_FENCE %r is not an arm' % fence
    fit = str(K.LIN2_BARRAGE_FIT) if fit is None else str(fit)
    assert fit in ('off', 'lines', 'cap'), 'LIN2_BARRAGE_FIT %r is not an arm' % fit
    #   HOW min_tf IS APPLIED. Joe 1028 chose 'membership' - *"B"* - so the legs run on the
    #   settings the pine emit was built with.
    #     'floor'       only lines at or above min_tf contribute at all. HIS definition, 1027.
    #     'membership'  the count is over ws1..ceil and at least ONE line must reach min_tf. What
    #                   out/l2_barrage.pine and the banked 24-cadence list were built on.
    mode = str(K.LIN2_BARRAGE_MIN_TF_MODE) if mode is None else str(mode)
    assert mode in ('membership', 'floor'), 'LIN2_BARRAGE_MIN_TF_MODE %r is not an arm' % mode
    #   THE COUNTING WINDOW IS ITS OWN TERM, Joe 1027 option A. He asked what the tolerance was
    #   for and then corrected the build: *"I thought tolerance allows for ws1mage and ws1r to
    #   sync"*. His own spec line put the count *"between the cross and the ws1r reversal"*, which
    #   made the tolerance cap the counting window as a SIDE EFFECT - one knob doing two jobs.
    #   Now the tolerance does the sync ONLY and the count has its own window off the cross.
    #     0   the window is the ws1r reversal bar - THE AS-BUILT BEHAVIOUR, so the bank cannot
    #         move on this change
    #     >0  the window is cross + win_s, independent of when ws1r reverses
    #   *"let the data supply the best value for it"* - out/l2_barrage_sweep.md is the grid.
    win_s = int(K.LIN2_BARRAGE_WIN_S) if win_s is None else int(win_s)
    #   WHEN THE FLOOR AND THE LINE COUNT CANNOT BOTH BE MET, Joe 1027 gave two mechanics and
    #   asked for both: *"1) dynamiclaly reduce the minimum required lines to fit them all inside
    #   the ws12cap / 2) dynamically increase the ws12 cap to include the minimum required lines"*.
    #     'off'    neither - the pool stays ws{min_tf}..ws{L2_MOM_MAXTF} and a short pool means the
    #              mech fires nothing. THE BANKED BEHAVIOUR.
    #     'lines'  his 1 - the required count drops to the pool's size
    #     'cap'    his 2 - the ceiling rises to ws{min_tf + lines - 1}, which admits dtf lines
    #              (>ws12) on purpose. That is the same bound I removed as a defect when it was
    #              UNINTENDED; here he is asking for it.
    avail = sorted(int(t) for t in BD.tfs)
    #   THE BARRAGE'S OWN CEILING, his 1029 knob. It used to be the shared L2_MOM_MAXTF 12, which
    #   is still the ladder's top rung everywhere else - the rider scan, the baton candidates, the
    #   cadence latch's range, t3's HTF set and v4_reentry. His words were "barrage maxTF", so the
    #   barrage gets its own and nothing else moves.
    ceil = int(K.LIN2_BARRAGE_MAX_TF) if max_tf is None else int(max_tf)
    assert ceil >= 1, 'LIN2_BARRAGE_MAX_TF %d is not a rung' % ceil
    if fit == 'cap':
        #   the pool the ceiling has to make room for starts at the arm's own floor
        ceil = max(ceil, (int(min_tf) if mode == 'floor' else 1) + int(need) - 1)
        ceil = min(ceil, avail[-1])                    # the ladder cannot be extended past ws%d
    pool = [t for t in avail if (int(min_tf) if mode == 'floor' else 1) <= t <= ceil]
    if fit == 'lines':
        need = min(int(need), len(pool))
    out = []
    for c, sig, first, m1v, exf in barrage_candidates(BD, side, cand=cand):
        if (sig - c) * 5 > tol_s:
            continue
        #   MIN_TF IS A FLOOR ON WHICH LINES MAY CONTRIBUTE, his correction 1027: *"my minTF isn't
        #   your minTF (my error). I meant 'the minimum TF allowed to contribute'"*, with his own
        #   example - ws1,ws2,ws3,ws4,ws5,ws7,ws9,ws12 restricted to ws5,ws7,ws9,ws12 at minTF 5.
        #   So the floor is applied BEFORE the count, not as a membership test after it.
        right = int(sig) if win_s <= 0 else int(c) + int(win_s) // 5
        lo = int(min_tf) if mode == 'floor' else 1
        inside = {t: b for t, b in first.items()
                  if b <= right and lo <= int(t) <= ceil}
        #   THE MEMBERSHIP ARM tests min_tf AFTER the count: at least one line must reach it
        if mode == 'membership' and min_tf and inside and max(inside) < int(min_tf):
            continue
        if fence != 'any':
            want = (fence == 'ex')
            inside = {t: b for t, b in inside.items() if bool(exf[t]) is want}
        if len(inside) < need:
            continue
        k = max(int(K.lift_stamp(b)) for b in inside.values())
        assert all(k >= b for b in inside.values()), \
            'the barrage cadence is before a reversal it counted, or before a fence read'
        #   WITH AN INDEPENDENT WINDOW a contributing reversal can land AFTER the ws1r one, so the
        #   cadence bar can be later than the ws1r stamp. It is still the max stamp of everything
        #   counted, which is the bar every term is knowable at.
        assert k >= int(K.lift_stamp(sig)) or win_s > 0, \
            'the cadence is before the ws1r stamp with the window tied to it'
        if not (int(A) <= k <= int(B)):
            continue
        if any(r[0] == k for r in out):
            continue                                   # one cadence per bar; the earlier cross owns it
        out.append((k, 'barrage',
                    'ws1Mage %.2f %s oob->ib %s, ws1r reverses %s (%d s), %d lines reverse with it'
                    ' (%s), top ws%d - confirmed %s'
                    % (m1v, 'LOW' if int(side) < 0 else 'HIGH', ln.U(c)[11:], ln.U(sig)[11:],
                       (sig - c) * 5, len(inside),
                       ','.join('ws%d' % t for t in sorted(inside)), max(inside), ln.U(k)[11:])))
    return out


def barrage_candidates(BD, side, cand=None):
    """THE BARRAGE'S RAW CANDIDATES, with NO threshold applied. -> [(cross, sig, first, m1v, exf)].

        cross  a ws1Mage oob->ib cross bar on `side`
        sig    the FIRST same-side ws1r reversal at or after that cross, at any distance
        first  {tf: the first same-side reversal of ws{tf}r at or after the cross}, ws1..L2_MOM_MAXTF
        m1v    ws1Mage's value at the cross bar
        exf    {tf: was ws{tf}r EX-FENCE on `side` at its own reversal bar}, read CLOSED

    THE FENCE READ IS CLOSED, at the RAW reversal bar. His 1026 rule is *"move everything except
    reversal detection to closed bars"*, so the reversal TIMING is emerging and the fence STATE at
    that bar is closed. It stays causal because the barrage acts at the reversal's STAMP, which is
    later than the bar the fence is read at - asserted in `barrage`.

    NO TOLERANCE AND NO HORIZON HERE. `sig` is found at whatever distance it happens, and `first`
    holds every line's first reversal after the cross whether or not it lands before `sig`. The
    three thresholds are applied by `barrage` on top of this, which is what lets a sweep vary them
    without a second copy of the rule and without recomputing the reversal detection per combo.

    A cross with no later ws1r reversal at all is dropped - there is nothing for a tolerance to
    admit. `cand` lets a caller pass a list this function already returned, so a sweep computes it
    once.
    """
    if cand is not None:
        return cand
    M1 = BD.mage_line(1, 'emerging')
    #   EVERY TF THE BOARD HAS, and the CEILING IS APPLIED BY `barrage`, not here. It used to be
    #   applied here at L2_MOM_MAXTF 12, which is correct for every arm but his 'cap' one - that
    #   arm raises the ceiling past ws12 on purpose, so the candidate set has to be
    #   ceiling-agnostic. With fit 'off' or 'lines' the ceiling is still 12 and nothing moves.
    tfs = sorted(int(t) for t in BD.tfs)
    #   SORTED ARRAYS AND searchsorted, NOT A LIST SCAN PER CROSS. The list form was
    #   O(crosses x tfs x reversals) and the ex-fence latch asks for this over the WHOLE tape to
    #   find its release bars - a window here would be a horizon nobody ruled. `np.searchsorted`
    #   returns the first index with b >= c, which is exactly what `nxt[0]` was.
    raws = {int(t): np.array(sorted(int(b) for b in F.revs(BD.E[int(t)], int(t), int(side))),
                             dtype=int) for t in tfs}
    out = []
    for c, _cf, sd in oob_ib_cross(M1, K.OOB_HI, K.OOB_LO, 1):
        if int(sd) != int(side):
            continue
        c = int(c)
        i1 = int(np.searchsorted(raws[1], c, side='left'))
        if i1 >= len(raws[1]):
            continue
        sig = int(raws[1][i1])
        first, exf = {}, {}
        for t, bs in raws.items():
            i = int(np.searchsorted(bs, c, side='left'))
            if i < len(bs):
                first[t] = int(bs[i])
                exf[t] = bool(BD.ex_fence(int(t), int(bs[i]), int(side)))
        out.append((c, sig, first, float(M1[c]), exf))
    return out


def chain_open(B1, MG, before=None, tf=None, lines=None, hi=None, lookback_s=None, xwob=None):
    """THE CHAIN'S OPEN - his ws1b firing mech. -> dict or None.

    Joe 1029, the flow verbatim:

        -there is no trade open  (either because of a STOP, or because the machine is cold-starting)
        -walk
        -if ws1b crosses from oob to ib (candidate-side)
        --if ws5Mage is oob or has been oob in the last 5 minutes on the candidate-side
        ---anchor on the ws5Mage extremum.  the anchor is for the next step to align with
        ---if at least 2 ws{>5}Mage wsf lines are printing a value that is away from the candidate
           side, at the anchor bar (ie: high candidate-side and line values are less than ws5Mage,
           low candidate-side and lines are printing values higher than ws5Mage)
        ----open the trade, direction: away from candidate-side

    and *"bank this and make it the machine"*.

    EVERY READ IS EMERGING. Joe 1029: *"closed_prev is also not an option. I know I suggested it
    earlier (for baton passing)"*. `B1` is emerging ws1b and `MG` the emerging Mage ladder; the
    caller hands them in so this function holds no opinion about where they came from.

    THE ANCHOR IS CAUSAL BY CONSTRUCTION: the extremum is taken over [run start, FIRING BAR]. The
    oob run may still be open at the fire, so reading past it would be lookahead. Asserted.

    THE SCAN RUNS BACKWARD from `before` with NO limit. Joe 1029: *"we're always going to have an
    incoming trade to start a window... option B is the answer"*.

    `candidate side` is the side ws1b was oob on before crossing in. The trade side is AWAY from
    it, which is his own wording and not a read of price.
    """
    tf = int(K.LIN2_CHAIN_OPEN_TF) if tf is None else int(tf)
    need = int(K.LIN2_CHAIN_OPEN_LINES) if lines is None else int(lines)
    hi = int(K.L2_MOM_MAXTF) if hi is None else int(hi)
    lb = int(K.LIN2_CHAIN_OPEN_LOOKBACK_S) if lookback_s is None else int(lookback_s)
    w = max(1, int(K.LIN2_CHAIN_OPEN_XWOB) if xwob is None else int(xwob))
    band = [t for t in range(tf + 1, hi + 1) if t in MG]
    assert band, 'no higher TF than ws%d in the Mage ladder - the count can never be met' % tf
    b1 = np.asarray(B1, float)
    m5 = np.asarray(MG[tf], float)
    #   FORWARD, NEVER BACKWARD. This searched backward from `before` and returned the LATEST
    #   firing ahead of it, which is a bar the chain can never reach: a firing opens the trade and
    #   no later firing is taken while it is open. On 2026-08-29 it returned 23:56:00 when the
    #   trade had already opened at 23:53:50. Joe 1029: *"ws1b crossing to ib is the fire bar"*.
    #   `before` NO LONGER LIMITS THE SEARCH. The chain's open is the EARLIEST firing in the
    #   series, which is the data's own boundary and not a cut-off chosen by me. It is kept only
    #   as an assert for a caller that believes the open precedes a bar.
    hits = []
    for c, cf, sd in oob_ib_cross(b1, K.OOB_HI, K.OOB_LO, w):
        f = int(cf) if w > 1 else int(c)
        hits.append((f, int(c), int(cf), int(sd)))
    #   THE GATE MASK IS HOISTED. It depends only on `sd`, which takes two values, and it was
    #   being rebuilt over the whole tape once per crossing - thousands of 1.6M-bar allocations
    #   for two distinct answers. Same values, same order, same result.
    GATE = {d: K.oob_mask(m5, d) for d in (-1, +1)}
    for f, c, cf, sd in sorted(hits):
        gate = GATE[int(sd)]
        if not (bool(gate[f]) or bool(gate[max(0, f - lb // 5):f + 1].any())):
            continue
        #   THE ANCHOR: the ws{tf}Mage extremum of the oob run that contains `f`, or of the most
        #   recent run inside the lookback. Bars after `f` are never read.
        j = f if gate[f] else None
        if j is None:
            for i in range(f, max(0, f - lb // 5) - 1, -1):
                if gate[i]:
                    j = i
                    break
        if j is None:
            continue
        i = j
        while i > 0 and gate[i - 1]:
            i -= 1
        seg = m5[i:j + 1]
        if not np.isfinite(seg).any():
            continue
        k = i + (int(np.nanargmax(seg)) if sd > 0 else int(np.nanargmin(seg)))
        assert k <= f, 'the anchor is after the firing bar - that read is lookahead'
        v0 = float(m5[k])
        got = tuple(t for t in band
                    if np.isfinite(MG[t][k])
                    and ((float(MG[t][k]) < v0) if sd > 0 else (float(MG[t][k]) > v0)))
        if len(got) < need:
            continue
        if before is not None:
            assert f <= int(before), \
                ('the earliest firing %d is after the bar the caller expected it to precede %d'
                 % (f, int(before)))
        return dict(bar=f, raw=c, conf=cf, cand_side=sd, side=-sd, anchor=k, trig=v0, lines=got)
    return None


def matryoshka(rider):
    """The rider's matryoshka - the lines t3 compares it against. -> a list, lowest first.

    Joe 1026: *"the sole reason for t3 is to use matryoshka logic: if >1 lines that are lower TF
    than the rider TF and have reversed, then it is likely that the rider TF will also reverse"*,
    and *"ws7 is the floor for t3"*. So it is ws`HTF_LO`..rider-1, and a rider at ws7 has none.
    """
    return [t for t in range(HTF_LO, int(rider))]


class Latch:
    """THE t3 REPLACEMENT. Joe 1026, verbatim:

        I see a potential replacement for t3, and it's 2-staged latch
        1st latch, the bearish divergence that fires on the 2151 t1 cadence
        2nd latch, ws7r reversing (with wob12) and no baton candidate options PLUS the supporting
        ws4,5,6r matryoshka reversals

    and *"10, yes - the old t3 is defunct"*.

    HIS RULINGS, 1026, each one his:

        the divergence read     `anchor_floater`'s `state`, not `jig.divergence`
        latch 1's bar           *"2, at the cadence bar"*
        latch 1's life          *"3, 10 minutes (knob)"* -> LIN2_CAD_LATCH_LIFE_S 600 s
        the rider range         *"4, the rider between ws{knob:5,'lin2_t3_min_tf'} and ws12"*
        the reversal wob        *"1 static wob12"* -> LIN2_REV_WOB 12, THIS MECH ONLY
        no baton candidate      *"6, inside linhop"*
        the support             *"7, 3 lines below the rider"* -> LIN2_SUPPORT_LINES 3, ALL of them
        the support window      *"8, since the cadence"*
        the read                *"9, whatever we're consuming in the live test"* -> emerging

    FIVE READINGS ARE MINE, each on PRECEDENT in this codebase, none of them a number I invented:

        WHICH SIDE LATCH 1 FIRES ON. He described a BEARISH divergence against a HIGH-target walk.
        `state` +1 is a divergence supporting a SHORT and a HIGH target is a LONG, so the reading
        generalises to `state == side` - which is EXACTLY the comparison the banked DIV branch in
        `v4_lineage2.walk` already makes (*"a +1 verdict against a +1 side is the rev-trade"*). Same
        comparison, not a new one.

        WHICH CADENCES LATCH 1 READS AT. All of them. With t3 defunct, t1 and t2 are the only
        cadence producers left, so *"at the cadence bar"* has no second reading.

        WHAT LATCH 2 COMPLETING DOES. The walk EXHAUSTS. Latch 2 already requires no baton
        candidate, which is the walk's own exhaust branch - *"else declare exhaustion and defer to
        the router for rev-trade"*. Completing the latch cannot reach any other outcome.

        THE SUPPORT LINES' SIDE. The target side, which is the side t3's own reversal read used.

        THE BAR A REVERSAL IS ACTED ON. Its STAMP, never its raw bar. Banked in `v4_fast`: *"the raw
        bar is the anchor and the identity of the reversal"*, and every caller that ACTS passes it
        through `K.lift_stamp` first. Here the stamp is raw + LIN2_REV_WOB - 1 = raw + 11 = 55 s.

    STATE PER WALK, advanced bar by bar, same shape as the T3 it replaces so the walk's loop does
    not change: `arm1` records latch 1 at a cadence, `at` tests latch 2.
    """

    def __init__(self, BD, side, arm):
        self.BD, self.side, self.arm = BD, int(side), int(arm)
        self.l1 = None                                 # the bar latch 1 fired on, or None
        self.l1_why = ''
        #   THE REVERSAL STAMPS AT THIS MECH'S OWN WOB, per line. LIN2_REV_WOB 12, not LIFT_WOB 8 -
        #   his 1026 ruling, and `lift_off` takes the wob as an argument so no detector is forked.
        self.stamps = {}
        for t in sorted(BD.tfs):
            out = []
            for raw in lift_off(BD.E[t], self.side, K.LIFT_PTS, K.gap_for(t),
                                K.LIFT_TOL, int(K.LIN2_REV_WOB)):
                raw = int(raw)
                if raw >= self.arm:
                    out.append((int(raw) + max(1, int(K.LIN2_REV_WOB)) - 1, raw))
            self.stamps[t] = sorted(out)

    def arm1(self, k, state, ctype):
        """Latch 1 at a cadence bar. `state` is `anchor_floater`'s state there. -> (bool, why)."""
        if state is None:
            return False, 'no divergence state at the cadence'
        if int(state) != self.side:
            return False, ('divergence state %+d does not oppose the %s target'
                           % (int(state), 'HIGH' if self.side > 0 else 'LOW'))
        self.l1 = int(k)
        self.l1_why = ('latch 1 at the %s cadence %s, divergence state %+d'
                       % (ctype, ln.U(int(k)), int(state)))
        return True, self.l1_why

    def _rev_in(self, tf, a, b):
        """A reversal of ws{tf}r that HAPPENED after `a` and is KNOWABLE by `b`. -> (stamp, raw).

        BOTH TESTS, not one. The raw bar must be after `a` and the stamp at or before `b`:

            raw > a    *"reversed since the cadence"* is about WHEN IT HAPPENED, and the banked rule
                       is that the raw bar is that moment - `v4_fast`: *"the raw bar is the anchor
                       and the identity of the reversal"*.
            stamp <= b the walk may not act on a reversal before it is knowable. `K.lift_stamp`'s
                       own contract, and every other caller in the fork obeys it.

        THE FIRST BUILD TESTED ONLY THE STAMP, which let a reversal whose raw bar PREDATED the
        cadence satisfy *"since the cadence"*. Measured on the 2026-08-30 06:31:10 latch: support
        ws10 raw 06:29:15 and ws11 raw 06:29:15 both sit BEFORE latch 1 at 06:30:00 and passed only
        because their stamps, 06:30:10, landed after it. Two of that firing's three support lines
        were admitted by the defect. Same family as the t1-grace bug of 1026, where I bounded the
        stamp instead of the raw bar and he ruled it the other way.
        """
        for st, raw in self.stamps.get(int(tf), ()):
            if int(raw) > int(a) and st <= int(b):
                return st, raw
        return None

    def live(self, k):
        """Is latch 1 still latched at `k`. -> bool. LIN2_CAD_LATCH_LIFE_S seconds from its own bar."""
        if self.l1 is None:
            return False
        return (int(k) - self.l1) * 5 <= int(K.LIN2_CAD_LATCH_LIFE_S)

    def at(self, k, rider, cand_fn):
        """Does latch 2 hold at `k`. -> (bool, why).

        `cand_fn` is a CALLABLE returning the walk's own candidate list INSIDE LIN_HOP at this bar -
        his *"6, inside linhop"* - passed in rather than recomputed here, so the latch and the walk
        cannot disagree.

        IT IS A CALLABLE, NOT A LIST, because the candidate scan runs `towards` on every rung and
        that is the expensive read on the board. Called eagerly on every bar it put the five-day
        chain past its 580 s budget. The cheap gates below run first and the scan only happens on a
        bar that has already passed them.
        """
        if self.l1 is None:
            return False, 'latch 1 has not fired'
        if not self.live(k):
            return False, ('latch 1 at %s expired - %d s of %d'
                           % (ln.U(self.l1), (int(k) - self.l1) * 5, K.LIN2_CAD_LATCH_LIFE_S))
        lo, hi = int(K.LIN2_T3_MIN_TF), int(K.L2_MOM_MAXTF)
        if rider is None or not (lo <= int(rider) <= hi):
            return False, ('rider %s is outside ws%d..ws%d'
                           % (('ws%d' % rider) if rider else 'none', lo, hi))
        #   THE REVERSAL TESTS FIRST - they are dict lookups. The candidate scan is last.
        rr = self._rev_in(rider, self.arm - 1, k)
        if rr is None:
            return False, 'the rider ws%d has no reversal at wob %d yet' % (rider, K.LIN2_REV_WOB)
        #   THE SUPPORT: the LIN2_SUPPORT_LINES lines immediately below the rider, every one of
        #   them reversed SINCE THE CADENCE - his *"8, since the cadence"*, which is latch 1's bar.
        sup = [t for t in range(int(rider) - int(K.LIN2_SUPPORT_LINES), int(rider))
               if t >= 1 and t in self.BD.tfs]
        if len(sup) < int(K.LIN2_SUPPORT_LINES):
            return False, ('only %d support line(s) exist below ws%d, need %d'
                           % (len(sup), rider, K.LIN2_SUPPORT_LINES))
        got = {t: self._rev_in(t, self.l1, k) for t in sup}
        miss = [t for t in sup if got[t] is None]
        if miss:
            return False, ('support %s has not reversed since the cadence %s'
                           % (', '.join('ws%d' % t for t in miss), ln.U(self.l1)))
        cands = cand_fn()                              # the expensive read, only on a live bar
        if cands:
            return False, ('%d baton candidate(s) inside lin_hop: %s'
                           % (len(cands), ', '.join('ws%d' % t for t in cands)))
        return True, ('latch 2: rider ws%d reversed raw %s stamp %s, no candidate inside lin_hop,'
                      ' support %s | %s'
                      % (rider, ln.U(rr[1]), ln.U(rr[0]),
                         ', '.join('ws%d raw %s stamp %s' % (t, ln.U(got[t][1]), ln.U(got[t][0]))
                                   for t in sup),
                         self.l1_why))


class T3:
    """t3's state for ONE walk, advanced bar by bar. -> `.at(k, rider)` is (bool, why).

    WHY IT IS A STATE OBJECT. The naive form rescanned [arm, k] for every bar, which is O(bars^2)
    per line and took the 2026-08-30 walk past two minutes. The three things t3 needs are all
    cumulative: whether a line has EVER been ex-fence since the arm, and whether it has reversed
    while ex-fence since the arm. Both are running flags, so each bar costs O(lines).

    It holds no rider of its own - the rider is passed to `.at`, because it changes under the walk.
    """

    def __init__(self, BD, side, arm):
        self.BD, self.side, self.arm = BD, int(side), int(arm)
        self.seen = set()                              # lines that have been ex-fence since arm
        self.rev = set()                               # ... and reversed while ex-fence
        self._k = int(arm) - 1
        tfs = [t for t in range(HTF_LO, int(K.L2_MOM_MAXTF)) if t in BD.tfs]
        #   the reversal RAW bars whose ex-fence test passes, precomputed per line. The stamp is
        #   checked at `advance` time so nothing is counted before it is knowable.
        self._cand = {}
        for t in tfs:
            out = []
            for raw in F.revs(BD.E[t], t, self.side):  # TIMING: emerging, his one exception
                raw = int(raw)
                if raw < self.arm:
                    continue
                if K.ex_fence(BD.value(t, raw), self.side):   # *"reversed while ex-fence"*
                    out.append((K.lift_stamp(raw), t))
            self._cand[t] = sorted(out)
        self._tfs = tfs
        self._q = sorted(x for t in tfs for x in self._cand[t])
        self._qi = 0

    def advance(self, k):
        """Carry the cumulative flags to bar `k`. Call once per bar, in order."""
        k = int(k)
        assert k >= self._k, 't3 state cannot walk backwards'
        for j in range(self._k + 1, k + 1):
            for t in self._tfs:
                if t not in self.seen and self.BD.ex_fence(t, j, self.side):
                    self.seen.add(t)
        while self._qi < len(self._q) and self._q[self._qi][0] <= k:
            self.rev.add(self._q[self._qi][1])
            self._qi += 1
        self._k = k

    def at(self, k, rider):
        """Does t3 hold at `k` for `rider`. -> (bool, why). `advance(k)` must have been called."""
        assert int(k) == self._k, 't3 asked at a bar it has not advanced to'
        matry = matryoshka(rider)
        if len(matry) < int(K.L2_T3_MIN_MATRY):
            #   an early-out, not a second rule: a range of fewer than `L2_T3_MIN_MATRY` lines can
            #   never produce that many reversers, so the test below would fail anyway.
            return False, ('matryoshka ws%s has %d line(s), cannot reach %d reversals'
                           % (','.join(str(t) for t in matry) or '-', len(matry),
                              K.L2_T3_MIN_MATRY))
        pop = [t for t in matry if t in self.seen]
        rev = [t for t in pop if t in self.rev]
        if not pop:
            return False, 'no matryoshka line reached ex-fence since the arm'
        #   THE >= 2 IS ON THE LINES THAT ACTUALLY REVERSED, Joe 1026: *"use the >=2 applied to the
        #   lines that actually reversed"*. It was on the matryoshka RANGE, which let t3 fire on a
        #   SINGLE reversal: at 2026-08-30 20:11:00 the range {ws7, ws8} met the floor, only ws7
        #   had reached ex-fence, and round(0.75 x 1) = 1 - so one line satisfied a rule whose
        #   whole point is *"if >1 lines ... have reversed"*.
        need = max(int(K.L2_T3_MIN_MATRY), int(round(float(K.L2_T3_FRAC) * len(pop))))
        return (len(rev) >= need,
                '%d of %d ex-fence matryoshka line(s) reversed while ex-fence (ws%s), needs %d'
                ' = max(%d, round(%s x %d))'
                % (len(rev), len(pop), ','.join(str(t) for t in rev) or '-', need,
                   K.L2_T3_MIN_MATRY, K.L2_T3_FRAC, len(pop)))


def t3_at(BD, side, arm, k, rider):
    """Does t3 hold at bar `k` for this rider. -> (bool, why). The one-shot form, for a diagnostic.

    HIS 1026 REDEFINITION, which replaced the HTF-oob-and-75% version wholesale:

        the sole reason for t3 is to use matryoshka logic: if >1 lines that are lower TF than the
        rider TF and have reversed, then it is likely that the rider TF will also reverse

        t3 and t4 cadences exist primarily for uniformity: we need the cadences to make decisions -
        without a cadence event, the walk would run past an actionable set-up

    WHAT CHANGED FROM THE FIRST BUILD, each on his word:

        the set        was the fixed band ws7..ws12; is now ws7..rider-1. *"ws7 is the floor"*
        the state      was *"have been oob"*; is now EX-FENCE - *"requiring lines to be oob
                       excludes the lines that reached only ex-fence before reversing"*
        the reversal   must have happened WHILE EX-FENCE - *"make it: 'have reversed while
                       ex-fence'. tested since the arm"*
        the floor      at least `L2_T3_MIN_MATRY` 2 lines must have REVERSED - *"use the >=2
                       applied to the lines that actually reversed"*. His matryoshka wording is
                       *"if >1 lines ... have reversed"*, and the floor on the range let a single
                       reversal through

    `L2_T3_FRAC` 0.75 SURVIVES - his word - and applies to the lines that reached ex-fence.

    THE REVERSAL'S RAW BAR CARRIES THE EX-FENCE TEST, its STAMP carries the timing. His standing
    rule: the raw bar is when the reversal happened, the stamp is when it may be acted on. So
    *"reversed while ex-fence"* is read at the raw bar and the stamp must have landed by `k`.

    REVERSAL DETECTION IS THE ONE EMERGING READ LEFT, his 1026: *"move everything except reversal
    detection to closed bars"*. The ex-fence state is CLOSED.
    """
    matry = matryoshka(rider)
    if len(matry) < int(K.L2_T3_MIN_MATRY):
        return False, ('matryoshka ws%s has %d line(s), needs %d'
                       % (','.join(str(t) for t in matry) or '-', len(matry),
                          K.L2_T3_MIN_MATRY))
    pop, rev = [], []
    for t in matry:
        if t not in BD.tfs:
            continue
        seg = BD.line(t)[int(arm):int(k) + 1]
        if not len(seg) or not any(K.ex_fence(v, side) for v in seg):
            continue
        pop.append(t)
        for raw in F.revs(BD.E[t], t, side):          # TIMING: emerging, his one exception
            raw = int(raw)
            if not (int(arm) <= raw <= int(k)):
                continue
            if K.lift_stamp(raw) > int(k):
                continue                              # not knowable yet
            if K.ex_fence(BD.value(t, raw), side):    # *"reversed while ex-fence"*, at the raw bar
                rev.append(t)
                break
    if not pop:
        return False, 'no matryoshka line reached ex-fence since the arm'
    need = int(round(float(K.L2_T3_FRAC) * len(pop)))
    if need < 1:
        return False, 'need rounds to 0 from %d ex-fence line(s)' % len(pop)
    ok = len(rev) >= need
    return ok, ('%d of %d ex-fence matryoshka line(s) reversed while ex-fence (ws%s), needs %d'
                % (len(rev), len(pop), ','.join(str(t) for t in rev) or '-', need))
