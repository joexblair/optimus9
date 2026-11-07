"""fdm2 - his 1103 machine: the cadence-to-cadence walk, the bimodal decision, the rev-trade.

WHAT THIS REPLACED, and what it did NOT delete. His 1103 answer to "does today's bimodal logic
replace the old fdm-cadence body": *"yes, but don't delete the fdm work.  let's call this sandbox
`fdm2`"*. The old body - the two-stage level-3 test, the ws2-ws12 upward scan, the blast radius,
the 10-minute late-ws30r capture - is untouched in docs/octo-freedom/1103_fdm/. NOTHING of it is
read here, and his offline spec notes are out of the sandbox entirely: *"we're building in a sandbox
presently - so theses fdm_spec notes have no place"*.

NO lineage2. His *"this is a greenfield build - lineage2 has ZERO place in our current work"*.
`towards` is lifted from v4_lineage2.py:112 with the v4_l2_proxy Board replaced by the array the
Board was proxying - every fdm2 read is closed-prev, so BD.line(tf) IS CPR[tf] and BD.value(tf,
bar) IS CPR[tf][bar]. The producer underneath, rule2_trajectory.opposed_extrema, is not lineage2's.

HIS DECISION LOGIC, verbatim and complete:

    the bimodal decision that triggers at a cadence is simply, are there same-side ex-fence
    `towards` lines printing above ws3r?  if the answer is no, then rev-trade.  if the answer is
    yes walk to the next sameside cadence OR the sameside ws10x-cadence.  if the ws10x-cadence
    fires first, then test for reversal percentages
    -if the reversals pct >=40% then walk forward (the ws10x-grace-walk) and re-calculate at each
     ws1 bar (closed-prev)
    -if the ws10-xgrace-walk detects >50%, trade
    -if the 5 minutes expire, wait for the next cadence or ws10x-cadence

...with his five follow-up rulings folded in: no branch under 40%; "above" is IN TIMEFRAME; ONE
threshold at >=50%; the reversal window's origin is the CADENCE EVENT and the grace clock's origin
is the WS10X-CADENCE; no second ws10x-cadence in one walk. And his correction to his own line:
*"I was wrong to suggest testing for a higher reversal pct at the ws1 bar - the lift-off reversals
are emerging, so we should be testing per 5s bar"*.

THE POPULATION DOES NOT GROW DURING THE GRACE WALK - his 1103 "no". It is frozen at the
ws10x-cadence, over [the trade's open, the ws10x-cadence]. Both of his verified cases carry a
constant denominator across the grace walk, 21 at 1012 and 22 at 1841, which is the same reading.

THE REVERSAL IS TAKEN AT ITS STAMP, NOT AT ITS LIFT BAR. jig.lift_off's own contract: *"A wob of n
means the event is not KNOWABLE until bar + n - 1 ... the consumer adds the wob"*, and K.lift_stamp
is the one home for that arithmetic - LIFT_WOB 8 puts the stamp 7 bars = 35 s after the line left
its extreme. 1103_fdm/fdm_cadence_census.py counts the RAW lift bar, which is 35 s of lookahead;
every number here is on the stamp and will differ from that census where a lift landed inside the
last 7 bars of a window.

THE BAR ACCOUNTING, his 1103: *"let the router decide if a rev-trade signal means CLOSE then OPEN,
or just OPEN.  if it's close then open, consume 2 bars.  if it's only open, consume 1 bar"*.

    signal bar s   CLOSE price bar   OPEN price bar   bars
    ------------   ---------------   --------------   ----
    CLOSE+OPEN     s + 1             s + 2            2
    just OPEN      -                 s + 1            1

The two bars being s+1 and s+2, one each for the close and the open, IS MY READING of "consume 2
bars"; the alternative is both at s+2. The old lineage2 chain closed at s+1 and opened at s+1 -
ONE bar for both - so this ruling moves every leg's open by one bar.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v4_knobs as K
import v4_signal as SG
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever happens.
#   Without it a refusal from v4_knobs.check() - an off-ruled run with no W_V4_EXPERIMENT=1 - goes
#   into the StringIO and the process exits 1 with NOTHING on either stream.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import v4_closed_prev as CP
    import v4_backstop_trades as BT
    import ln
    from optimus9.analysis.jig import oob_ib_cross, lift_off
    from optimus9.analysis import jig as JIG
    from optimus9.compute.rule2_trajectory import opposed_extrema
    from optimus9.compute.breaching_line import predict_breach
finally:
    sys.stderr = _e

MECH = 'fdm2-rev-trade'
DRAG_PCT = 0.1975      # % round trip, o9-live drag_pct: 11.0 bps fee + 8.75 bps slippage


#   ── the arrays ────────────────────────────────────────────────────────────────────────────────
def load():
    """Every array fdm2 reads, built once. -> dict.

    CLOSED-PREV FOR EVERY VALUE READ, EMERGING FOR LIFT-OFF ONLY. His standing 1102 rule. The one
    other emerging array is ws10x, which carries his fallback's own ruling from the older spec and
    is the line the race is run on.
    """
    E = RS.load((RS.K0, RS.R0, RS.S0))
    hi = int(K.L2_MOM_MAXTF)
    CPR = {t: np.asarray(CP.series(E[t], int(t) * 60), float) for t in range(1, hi + 1)}
    EMR = {t: np.asarray(E[t], float) for t in range(1, hi + 1)}
    MGE = LL.mage()          # EMERGING Mage. v4saviour reads the live lines, not chart-matched
    CPM = {t: np.asarray(CP.series(MGE[t], int(t) * 60), float) for t in MGE}
    close, phi, plo = BT.prices()
    #   THE LIFT-OFF STAMPS, PRECOMPUTED PER (TF, SIDE). One lift_off call per pair instead of one
    #   per measuring bar: the grace walk re-counts every 5 s bar, 60 bars per window, and the
    #   producer's cost does not belong inside that loop.
    LIFT = {}
    for sd in (-1, +1):
        for t in range(1, hi + 1):
            b = lift_off(EMR[t], sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB)
            LIFT[(t, sd)] = np.asarray([K.lift_stamp(int(x)) for x in b], int)
    return dict(
        HI=hi, CPR=CPR, EMR=EMR, CPM=CPM, LIFT=LIFT,
        B1=np.asarray(CP.series(np.asarray(ln.line('ws1b'), float), 60), float),
        X10=np.asarray(ln.line('ws10x'), float),            # emerging, his fallback's own ruling
        M10=np.asarray(CP.series(MGE[10], 600), float),
        MGE={t: np.asarray(MGE[t], float) for t in MGE},
        SEAM60=CP.seam_bars(60),
        G30B=np.asarray(LL._g30b(), float),
        close=close, phi=phi, plo=plo)


#   ── the reads ─────────────────────────────────────────────────────────────────────────────────
def deeper(a, b, side):
    """Is `a` more deeply oob than `b` on `side` - further from 50. -> bool."""
    return (a > b) if int(side) > 0 else (a < b)


def ex2080(v, side):
    """Is `v` external of the 20/80 fence on `side`. -> bool.

    HIS D: *"ex 20/80"*, and "ex" INCLUDES oob - his standing rule - so the test is at-or-beyond.

    HIS 1103 CONVENTION, *"I use the smallest number to describe the fence's max"*: a fence knob
    holds the SMALLER end of its pair. FDM_FNC_2080 20.0 -> (20, 80) - high side at or above 80,
    low side at or below 20. The edge for the side comes from K.side_edge, the ONE home for the
    convention, which asserts the knob is at or under 50 so an upper-end value in a lower-end slot
    cannot pass silently. RMOM_FNC 75.0 is the one knob still held at its UPPER end, read raw by
    v4_l2_proxy for lineage2 and the live octo-v4 machine - it is not routed through here.
    """
    e = K.side_edge(K.FDM_FNC_2080, side)
    return (v >= e) if int(side) > 0 else (v <= e)


def ex2080_line(LN, tf, bar, side):
    """Is ws{tf}r ex-20/80 on `side` at `bar`, by FDM_EXF_READ. -> bool.

    HIS 1105: *"when testing for lines that are ex-20/80-fence, collect the closed-prev and the
    emerging value for each line. if either closed-prev or emerging values qualify then walk to
    the next cadence"*.

    ONE HOME for that rule. Every ex-20/80 test on the cadence side goes through here, so a
    reading cannot differ between the decision and the report that shows it.

      'either'       either read past the fence qualifies. THE BANK
      'closed_prev'  closed-prev alone, the read it replaced
      'emerging'     the emerging read alone

    THE EMERGING READ IS AN EXTREME, not one bar. His 1105: *"taking the values based on the
    highest/lowest emerging bar between the seams"*. It is the side's extreme over the
    FDM_EXF_EM_BARS 12 bars = 60 s ENDING at `bar` - the highest for a high side, the lowest for a
    low one. One minute is the span between his 1-minute closed-prev seams. At 1 the read is the
    single bar's value.

    CAUSAL: both reads are at `bar`. The emerging value at a bar is knowable at that bar - it is
    the forming value, not a later one - so reading it adds no lookahead.
    """
    m = str(K.FDM_EXF_READ)
    assert m in ('either', 'closed_prev', 'emerging'), 'FDM_EXF_READ is %r' % m
    t, b = int(tf), int(bar)
    if m != 'emerging' and ex2080(float(LN['CPR'][t][b]), side):
        return True
    if m == 'closed_prev':
        return False
    #   THE EMERGING SIDE IS THE SIDE'S EXTREME over the FDM_EXF_EM_BARS bars ENDING at `bar`,
    #   his 1105 *"the highest/lowest emerging bar between the seams"*. 12 bars = 60 s is one
    #   minute, the span between his 1-minute seams. At 1 it is the single bar's value.
    n = max(1, int(K.FDM_EXF_EM_BARS))
    a0 = max(0, b - n + 1)
    seg = np.asarray(LN['EMR'][t], float)[a0:b + 1]
    if not np.isfinite(seg).any():
        return False
    v = float(np.nanmax(seg) if int(side) > 0 else np.nanmin(seg))
    return bool(ex2080(v, side))


def towards(r, tf, bar, side):
    """Is ws{tf}r travelling TOWARD `side` at `bar`. -> bool.

    v4_lineage2.towards with the Board dropped: `r` is the array the Board was proxying. `travel`
    is the move from the block's opposed extreme to the bar, so a HIGH target wants travel > 0 and
    a LOW target travel < 0.
    """
    bi, best, _ = opposed_extrema(r, int(side), int(bar), K.traj_block(tf))
    if bi is None:
        return False
    travel = float(r[int(bar)]) - best
    if not np.isfinite(travel):
        return False
    ok = (travel > 0) if int(side) > 0 else (travel < 0)
    assert int(bi) <= int(bar), 'the opposed extreme is after the bar it is measured at'
    return bool(ok and int(bar) - int(bi) > K.traj_min_bars(tf)
                and abs(travel) >= float(K.TRAJ_MIN_TRAVEL))


#   ── the cadence event, his revised preamble ───────────────────────────────────────────────────
def cadence_events(LN, side, A, B, trace=False):
    """His cadence events on `side` in [A, B]. -> [(the event bar, the excursion start, why)].

    HIS 1103 REVISED PREAMBLE, and his names for its parts. The labels t1/t2/t3 were MINE and they
    collided with lineage2's cadence TYPES - his *"what is t1 and t2?  if they are the cadences
    from the earlier specs, then drop them"*. They are not: they were my labels for his own three
    lines, and they are gone.

        a cadence event prints on ws1b to ib, IF ws1,2Mage was more deeply oob (further away from
        50) than ws1,2,3r during ws1b's oob excursion
        -ws1Mage, ws1b, ws1r are all oob at some time during ws1b's oob excursion
        -ws3Mage must be ex 25/75 fence while ws1b is oob
        --this cadence event can only be tested on target-side

    TWO TESTS REMAIN, both his:

      the NESTLE        HIS WORD, from the fdm line he handed over at 1103: *"ws1r or ws2r or ws3r
                        oob AND are nestled inside of ws1Mage or ws2Mage"* / *"#nestled: ws1Mage or
                        ws2Mage is deeper oob when ws1-3r is less deeper oob"*. One pair suffices
                        and it needs no TF match - his *"it can be any mage deeper than any r"*.
                        It LATCHES: his *"once it qualifies it stays qualified until the cadence
                        window ends"*, which is why the scan takes the first qualifying bar.
      ws3Mage ex-fence  his *"ws3Mage must be ex 25/75 fence while ws1b is oob"*, at FDM_M3_FNC
                        25.0. HE HAS NOT NAMED THIS ONE.

    THE "all oob" LINE IS GONE, not overruled - it is IMPLIED. His 1103 correction *"ws1r, ws2r,
    ws3r are all qualifying lines"* makes its r clause any of the three and its Mage clause either
    of the two; the nestle already needs an oob r among ws1,2,3r with a ws1,2Mage deeper than it -
    a Mage deeper than an oob r is itself oob - and s0..s1 IS a ws1b oob run. As written it
    rejected 2026-08-03 16:45:00 on ws1r alone, whose deepest reading in that 2m55s excursion was
    20.24 against the 15.0 oob fence while ws2r reached 7.14.

    THE EXCURSION ANCHOR IS ws1b's, SETTLED 1103. His *"ws1Mage and ws2Mage oob's job is to nestle
    ws1,2,3r"* - the Mage lines do not anchor the window - and his reason for the b line: *"gcws30b
    swings with more force than gcws30Mage, so it prints ex-5/95-fence excursions that are
    meaningful"*. On closed-prev ws1Mage and ws1b *"always return to ib on the same 1min bar"*, so
    the window's close and the ws1b ib cross are one bar.

    The event is ws1b's oob->ib cross. Both tests are evaluated over the excursion that ENDS at
    that cross, so every read is at or before the event bar - the assert carries that.

    `trace=True` returns EVERY cross on `side` with its per-test verdict instead of only the
    passes, so a rejection can be read off the data rather than guessed at.
    """
    out, tr = [], []
    B1, CPR, CPM = LN['B1'], LN['CPR'], LN['CPM']
    e3 = K.side_edge(K.FDM_M3_FNC, side)
    oob = (B1 >= K.OOB_HI) if int(side) > 0 else (B1 <= K.OOB_LO)
    for c, cf, s in oob_ib_cross(B1, K.OOB_HI, K.OOB_LO, 1):
        if int(s) != int(side):
            continue
        inwin = int(A) <= int(c) <= int(B)
        if not inwin and not trace:
            continue
        j = int(c) - 1
        if j < 0 or not oob[j]:
            if trace:
                tr.append(dict(cross=int(c), inwin=inwin, s0=None, s1=None, nestle=None,
                               m3=None, why='the bar before the cross is not oob - no excursion'))
            continue
        while j > 0 and oob[j - 1]:
            j -= 1
        s0, s1 = j, int(c) - 1
        assert s1 < int(c), 'an excursion ends at or after its own ib cross'
        nestle = None
        for b in range(s0, s1 + 1):
            for rt in (1, 2, 3):
                rv = float(CPR[rt][b])
                if not ((rv >= K.OOB_HI) if side > 0 else (rv <= K.OOB_LO)):
                    continue
                for mt in (1, 2):
                    mv = float(CPM[mt][b])
                    if deeper(mv, rv, side):
                        nestle = (b, mt, mv, rt, rv)
                        break
                if nestle:
                    break
            if nestle:
                break
        m3seg = CPM[3][s0:s1 + 1]
        m3 = bool(((m3seg >= e3) if side > 0 else (m3seg <= e3)).any())
        #   HIS 1103 WS3MAGE GATE UPDATE. A cross gated because ws3Mage stayed infence is rescued
        #   when, inside the gcws30b-ex-fence-to-ws1b-ib window, ws3r went oob AND ws3Mage reached
        #   ex-FDM_M3_RESCUE_FNC 40/60. HIS WINDOW, NOT THE EXCURSION: it starts at gcws30b's cross
        #   beyond FDM_RE_B_FNC, which can sit well before ws1b goes oob.
        rsc = None
        if not m3 and int(K.FDM_M3_RESCUE_ON):
            #   THE RESCUE WINDOW'S OPENER IS THE ARM'S OWN, his 1103 *"follow whichever opener the
            #   arm uses"*. His spec wrote it as gcws30b ex-5/95 because that was the opener at the
            #   time; with FDM_RE_WIN_OPEN now a knob, the rescue reads the same opener the
            #   re-entry window does. v4_fdm_reentry._opens is that ONE home - duplicating the
            #   five arms here is where the two would drift apart.
            import v4_fdm_reentry as _RE
            gx = _RE._opens(LN['B1'], LN['G30B'], side)
            gx = gx[gx <= int(c)]
            if gx.size:
                w0 = int(gx[-1])
                r3 = CPR[3][w0:int(c) + 1]
                m3b = CPM[3][w0:int(c) + 1]
                er = K.side_edge(K.FDM_M3_RESCUE_FNC, side)
                r3ok = bool(((r3 >= K.OOB_HI) if side > 0 else (r3 <= K.OOB_LO)).any())
                m3ok = bool(((m3b >= er) if side > 0 else (m3b <= er)).any())
                assert w0 <= int(c), 'the rescue window opens after the cross it serves'
                if r3ok and m3ok:
                    rsc = (w0, float(np.nanmax(r3) if side > 0 else np.nanmin(r3)),
                           float(np.nanmax(m3b) if side > 0 else np.nanmin(m3b)))
                    m3 = True
        why = ('ws1b excursion %s..%s, the nestle is ws%dMage %.2f deeper than ws%dr %.2f at %s%s'
               % (ln.U(s0), ln.U(s1), nestle[1], nestle[2], nestle[3], nestle[4],
                  ln.U(nestle[0]),
                  '' if rsc is None else
                  ', ws3Mage RESCUED - the %s window opened %s, ws3r reached %.2f and'
                  ' ws3Mage reached %.2f'
                  % (K.FDM_RE_WIN_OPEN, ln.U(rsc[0]), rsc[1], rsc[2]))) if nestle else ''
        if trace:
            tr.append(dict(cross=int(c), inwin=inwin, s0=s0, s1=s1, nestle=nestle, m3=m3,
                           rsc=rsc, why=why))
        if nestle is None or not m3 or not inwin:
            continue
        out.append((int(c), int(s0), why))
    return tr if trace else out


#   ── the ws10x-cadence ─────────────────────────────────────────────────────────────────────────
#   ── fdm2-wsxcad-director, HIS NAME 1104 ───────────────────────────────────────────────────────
def x_of(LN, tf):
    """The ws{tf}x line, loaded once and kept. -> array, EMERGING.

    LAZY ON PURPOSE. All 30 ws{TF}x lines exist on the tape, but loading every one at startup
    costs the whole run when only the director's chosen line is read. That choice is MINE.
    """
    X = LN.setdefault('X', {})
    t = int(tf)
    if t not in X:
        X[t] = np.asarray(ln.line('ws%dx' % t), float)
    return X[t]


def x_race(LN, tf, side, frm, B):
    """The first ws{tf}x race cross strictly after `frm` on `side`. -> (confirm, which, cross)|None.

    x10_cadence WAS THIS FUNCTION WITH tf PINNED TO 10. His 1104 update 1 made the timeframe
    dynamic - *"instead of using a static TF10 to create the ws10x-cadence, we will set the TF
    dynamically"* - so the race moved here and x10_cadence now calls it with 10. Nothing about
    the ws10 behaviour changed: LN['M10'] and LN['CPM'][10] are the same array, both
    CP.series(MGE[10], 600).

    HIS THREE CANDIDATES, unchanged: to ib, to ws{tf}r, to ws{tf}Mage - first to confirm wins.
    His 1104 *"race:{ib, Mage, r}"* names the same three. Cross OVER on the low side, UNDER on
    the high side - his *"crosses under for a high target-side, crosses over for a low
    target-side"*, which is the banked x-cross rule.

    THE HOLD IS FDM_X10_WOB 24 bars = 120 s, shared with the ws10 race because he moved the
    timeframe and nothing else.
    """
    w = max(1, int(K.FDM_X10_WOB))
    X, R, M = x_of(LN, tf), LN['CPR'][int(tf)], LN['CPM'][int(tf)]
    #   WHICH BAR MUST FOLLOW THE CADENCE EVENT: the race's CROSS, or only its CONFIRM. At 'cross'
    #   a race that began before the cadence event is not this walk's race even when it confirms
    #   after it. THAT IS THE ARM HIS OWN 1841 NUMBER CAME FROM - 1103_fdm's census used it - so it
    #   is the default on precedent, not on preference. At 'confirm' the event's identity is its
    #   confirm bar and an in-flight race counts.
    cf_only = str(K.FDM_X10_FRM) == 'confirm'
    lo = max(1, int(frm) - w + 2) if cf_only else int(frm) + 1
    hits = []
    for c, cf, s in oob_ib_cross(X, K.OOB_HI, K.OOB_LO, w):
        if int(s) != int(side) or int(cf) > int(B):
            continue
        if (int(cf) if cf_only else int(c)) > int(frm):
            hits.append((int(cf), 'ib', int(c)))
            break
    for nm, other in (('ws%dr' % int(tf), R), ('ws%dMage' % int(tf), M)):
        for i in range(lo, int(B) + 1):
            a, b = X[i - 1], X[i]
            oa, ob = other[i - 1], other[i]
            if not np.isfinite([a, b, oa, ob]).all():
                continue
            crossed = (a >= oa and b < ob) if side > 0 else (a <= oa and b > ob)
            if not crossed:
                continue
            #   THE CONFIRM MUST FIT INSIDE `B`, not merely inside the tape. The ib arm above
            #   already tests `cf <= B`; these two arms tested only `i + w <= len(X)`, so a cross
            #   near `B` confirmed PAST it. Invisible while `B` was the tape end; the moment the
            #   stop began bounding the walk it produced a rev-trade 65 s past a leg's own exit -
            #   2026-08-19 20:12:40 SHORT, bound 20:51:00, signal 20:52:05 - and the 'a decision
            #   row is past the leg's exit' assert caught it.
            end = i + w
            if end > len(X) or i + w - 1 > int(B):
                break
            seg = [(X[j] < other[j]) if side > 0 else (X[j] > other[j]) for j in range(i, end)]
            if all(seg) and i + w - 1 > int(frm):
                hits.append((i + w - 1, nm, int(i)))
                break
    if not hits:
        return None
    bar, which, cross = min(hits, key=lambda x: x[0])
    assert bar > int(frm), 'a ws%dx-cadence is at or before the cadence event it follows' % int(tf)
    assert cross <= bar, 'a race confirms before its own cross'
    return bar, which, cross


def mom_state(LN, tf, bar, side, since, rev_since=None, read='closed_prev'):
    """fdm2-cad-mom-detector on one line, with fdm2's own arrays. -> 'towards' | 'away'.

    THE LIFT-OFF STAMPS COME FROM LN['LIFT'], already carrying the wob offset, so the detector
    never re-runs lift_off inside a per-bar walk.
    """
    src = LN['CPR'] if read == 'closed_prev' else LN['EMR']
    r = JIG.fdm2_cad_mom_detector(src[int(tf)], LN['EMR'][int(tf)], int(bar), int(side),
                                  int(since), K.LIFT_PTS, K.gap_for(int(tf)), K.LIFT_TOL,
                                  K.LIFT_WOB, stamps=LN['LIFT'][(int(tf), int(side))],
                                  rev_since=rev_since)
    return r['state']


def xcad_candidate(LN, side, bar, since):
    """`fdm-conf-xcross-candidate` - HIS KNOB NAME. The line whose x line races. -> (tf, above, why).

    HIS UPDATE 1, verbatim: *"we will set the TF dynamically based on the highest TF
    (`fdm-conf-xcross-candidate`) that is printing `away` while the TF lines above
    `fdm-conf-xcross-candidate` are `towards` and ex-20/80-fence"*.

    TWO READINGS OF *"the TF lines above"*, FDM_XCAD_RULE:

        'B'  the next FDM_XCAD_ABOVE 2 lines above it, each `towards` AND ex-20/80. HIS CHOICE for
             now - *"unsure.  use B for now, we can change it to A if the data doesn't match my
             eye's verdict"*
        'A'  every ex-20/80 line above it is `towards`, however many there are

    Both pick ws8r at his own 2026-08-07 16:11:00 example. At FDM_XCAD_ABOVE 3 that example yields
    NO candidate, so his example rules 3 out.

    THE CANDIDATE DOES NOT HAVE TO BE EX-20/80 ITSELF - FDM_XCAD_EXF 0, his flat *"no"*.
    THE SCAN IS ws1..ws{HI} and the HIGHEST qualifying line wins, his *"the highest TF"*.
    EVERY READ IS AT `bar` and the extremum anchor is `since`, so nothing after `bar` is touched.
    -> (None, (), why) when no line qualifies; FDM_XCAD_NONE says what that means to the caller.
    """
    hi, rule = int(LN['HI']), str(K.FDM_XCAD_RULE)
    assert rule in ('A', 'B'), 'FDM_XCAD_RULE is %r' % rule
    n_above = int(K.FDM_XCAD_ABOVE)
    st = {t: mom_state(LN, t, bar, side, since) for t in range(1, hi + 1)}
    exf = {t: ex2080_line(LN, t, bar, side) for t in range(1, hi + 1)}
    for t in range(hi, 0, -1):
        if st[t] != 'away':
            continue
        if int(K.FDM_XCAD_EXF) and not exf[t]:
            continue
        if rule == 'B':
            ab = [u for u in range(t + 1, t + 1 + n_above) if u <= hi]
            if len(ab) < n_above:
                continue
            ok = all(st[u] == 'towards' and exf[u] for u in ab)
        else:
            ab = [u for u in range(t + 1, hi + 1) if exf[u]]
            ok = bool(ab) and all(st[u] == 'towards' for u in ab)
        if ok:
            return t, tuple(ab), ('ws%dr is the highest away line and ws%s are towards%s'
                                  % (t, ', ws'.join(str(u) for u in ab),
                                     ' and ex-%g/%g' % K.fnc_pair(K.FDM_FNC_2080)
                                     if rule == 'B' else ' (rule A, the ex-fence lines above)'))
    return None, (), 'no line is away with its %s above towards' % (
        '%d lines' % n_above if rule == 'B' else 'ex-fence lines')


def xcad_tags(LN, side, bar, since):
    """The lines his update-2 clauses read, taken at the cadence event. -> (above, exf_towards, why).

    HIS 1104 NARROWING of his own update 2: *"I should have stated 'consider only the 2 TF above
    the highest ex-20/80-fence TF that is tagged `towards`' - at 1611, those 2 TFs are 11 and 12"*.

        exf_towards   the lines ex-20/80 on the side that read `towards` here. At 2026-08-07
                      16:11:00 HIGH those are ws9 and ws10, out of the ex-fence set ws7..ws10
        above         the FDM_XCAD_ABOVE 2 lines above the HIGHEST of them, so ws11 and ws12 -
                      the exact pair he named
        clause one    every line in `above` must read `away` at the test bar
        clause two    none of `exf_towards` may still read `towards` there, FDM_XCAD_C2_SCOPE
                      'tagged'

    WITH NO EX-20/80 `towards` LINE there is no highest one to measure from, so `above` is empty
    and clause two has nothing to fail on. The test then passes on its own terms. THAT READING IS
    MINE, and the report names it so a trivial pass is never mistaken for a measured one.
    """
    hi = int(LN['HI'])
    exf_tw = [t for t in range(1, hi + 1)
              if ex2080_line(LN, t, bar, side)
              and mom_state(LN, t, int(bar), side, int(since)) == 'towards']
    if not exf_tw:
        return (), (), 'no line is both ex-%g/%g and towards here' % K.fnc_pair(K.FDM_FNC_2080)
    top = max(exf_tw)
    ab = tuple(u for u in range(top + 1, top + 1 + int(K.FDM_XCAD_ABOVE)) if u <= hi)
    return ab, tuple(exf_tw), ('ws%d is the highest ex-%g/%g towards line, so the %d above it are'
                               ' ws%s' % (top, *K.fnc_pair(K.FDM_FNC_2080),
                                          int(K.FDM_XCAD_ABOVE),
                                          ', ws'.join(str(u) for u in ab) or 'none'))


_MOMO = {}

#   ── the cad walk's per-bar trace sink, HIS 1106 ASK ───────────────────────────────────────────
#   *"to make it real, you need to walk forward on the cad-walk after 0755 and pick when rev-trade
#   will fire"*. A reporting script sets this to a list before calling legs(); every bar of every
#   cad walk then records what decided it. None means no recording and no cost, which is the state
#   every chain run is in. IT IS A SINK, NOT A KNOB: it changes no verdict, and the rows it holds
#   are the SAME calls the decision made, not a second computation of them.
XCAD_TRACE = None


def _momo_lines(LN):
    """The x and m ladders fdm2-momo needs, built ONCE and only when the arm is on.

    LN already carries r, Mage and the lift stamps. It does not carry the per-timeframe x or m
    lines, and building 108 arrays costs real time, so this is lazy: an arm that is off pays
    nothing. The closed-prev forms go through v4_closed_prev.series, the same call load() uses.
    """
    if _MOMO:
        return _MOMO
    lo = int(K.FDM_STEP1_ABOVE_TF) + 1
    tfs = list(range(lo, int(LN['HI']) + 1))
    xe = {t: np.asarray(ln.line('ws%dx' % t), float) for t in tfs}
    me = {t: np.asarray(ln.line('ws%dm' % t), float) for t in tfs}
    _MOMO.update(tfs=tfs, XEM=xe, MEM=me,
                 XCP={t: np.asarray(CP.series(xe[t], t * 60), float) for t in tfs},
                 MCP={t: np.asarray(CP.series(me[t], t * 60), float) for t in tfs})
    #   r-pred once per (timeframe, read) over the whole tape. predict_breach is vectorised, so a
    #   per-bar call would be 1.6M times the work for the same answer.
    for read, kk, mm, gg in (('closed_prev', LN['CPR'], _MOMO['MCP'], LN['CPM']),
                             ('emerging', LN['EMR'], _MOMO['MEM'], LN['MGE'])):
        for t in tfs:
            _MOMO[('RP', read, t)] = predict_breach(np.asarray(kk[t], float), mm[t],
                                                    np.asarray(gg[t], float))
    for sd in (+1, -1):
        for t in tfs:
            _MOMO[('PIN', t, sd)] = JIG.at_extreme_mask(LN['EMR'][t], sd, K.LIFT_PTS,
                                                        K.gap_for(t), K.LIFT_TOL)
    return _MOMO


def momo_vote(LN, bar, side, report=False, ev=None):
    """`fdm2-momo` - HIS NAME, 1106. The three signals at ONE bar, and the vote. -> dict.

    HIS 1106 RCA, verbatim: *"if there is a walk verdict, there is no need to truncate the cad
    walk... but if the verdict flips inside of the cad walk's max time then we don't miss that
    **correcting** verdict (ie rev-trade)"*. The caller reads this at EVERY bar of the cad walk. A
    vote reaching FDM2_MOMO_VOTES is his `walk` verdict and vetoes the truncation test AT THAT BAR
    ONLY. His earlier wording *"fire only once when we're cad walking"* was read as a latch over
    the whole cad walk, and that reading is the one he corrected.

    THE THREE LIVE SIGNALS, AND THEIR CARRIER SETS ARE NOT THE SAME - his 1106 rulings 1 and 6:

      rpred   how many carriers breaching_line.predict_breach flags on `side`, over
              ws{FDM_STEP1_ABOVE_TF+1}..ws{FDM2_MOMO_MAX_TF}. HIS OWN mech, carried in as the
              benchmark rather than rebuilt. Its test is a FLOOR - FDM2_MOMO_FLOOR_RPRED 1, at
              least one carrier - because its median is 0 on every set and a median makes it a
              constant. HIS option A.
      mx      how many have Mage beyond x toward `side` over the SAME capped set - the 38-bar %B
              against the 5-bar %B. Its test is `count < FDM2_MOMO_MED_MX`: FEWER means more
              carriers can still arrive
      pin     how many sit within LIFT_TOL of their sampled extreme, over the FULL set
              ws{FDM_STEP1_ABOVE_TF+1}..ws{HI} - his ruling 6 was *"unsure.  report on both ws10
              and ws12"*, so the cap does not reach it. Read on EMERGING whatever
              FDM2_MOMO_READ says, because a pin is a lift-off read and that is his standing rule

    THE TWO MEDIANS ARE MEASURED over all 50,457 cad-walk bars on the 94.5-day tape - 417 cad walks
    by 121 bars - not over the 417 first bars the one-shot read saw. Both came back unchanged.

    REPORT-ONLY, HIS 1106 RULINGS 2 TO 6. None of these touches `votes` or `fires`. They are
    computed only when `report` is set, which the caller does at a verdict-transition bar, so the
    per-bar scan pays nothing for them:

      gated       ruling 2 - r-pred's count if it were gated by `towards`, read on CLOSED-PREV
                  (step1's own precedent). *"report-only on this"*
      cross       ruling 5 - how many carriers had x cross Mage inside FDM2_MOMO_XWIN
      cwalk/crev  ruling 3 - his four cases. A SHORT reading x cross UNDER Mage is a `walk` vote,
                  OVER is a `rev-trade` vote; a LONG is the mirror. *"Mage will follow x because
                  of matryoshka"*
      s2_either   ruling 3 - signal 2 under *"either one firing is enough"*: the count test OR a
                  `walk` cross
      votes_sub   ruling 4 - the vote with one subtracted when a `rev-trade` cross is present
      pin_cap     ruling 6 - pinned on the capped set, beside the live full-set count
      traj        ruling 3's third dimension - both lines' slope from the cadence event `ev` to
                  this bar on emerging, and the bar their fitted paths cross. NO HORIZON: the
                  crossing is derived from the two slopes and is unbounded

    CAUSAL: every read is AT `bar` or earlier. Nothing after it is touched, and the asserts carry
    it. The trajectory fit reads `ev`..`bar` inclusive and no bar beyond.
    """
    bar, side = int(bar), int(side)
    assert bar <= len(LN['close']) - 1, 'fdm2-momo was asked about a bar past the tape'
    M = _momo_lines(LN)
    read = str(K.FDM2_MOMO_READ)
    mg = LN['CPM'] if read == 'closed_prev' else LN['MGE']
    xs = M['XCP'] if read == 'closed_prev' else M['XEM']
    cap = int(K.FDM2_MOMO_MAX_TF)
    capped = [t for t in M['tfs'] if t <= cap]
    nr = nx = npn = npc = 0
    for t in capped:
        if int(M[('RP', read, t)][bar]) == side:
            nr += 1
        if (float(np.asarray(mg[t], float)[bar]) - float(np.asarray(xs[t], float)[bar])) * side > 0:
            nx += 1
        if M[('PIN', t, side)][bar]:
            npc += 1
    for t in M['tfs']:
        if M[('PIN', t, side)][bar]:
            npn += 1
    f_r = nr >= int(K.FDM2_MOMO_FLOOR_RPRED)
    f_x = nx < int(K.FDM2_MOMO_MED_MX)
    f_p = npn >= int(K.FDM2_MOMO_MED_PIN)
    v = int(f_r) + int(f_x) + int(f_p)
    out = {'bar': bar, 'votes': v, 'rpred': nr, 'mx': nx, 'pin': npn, 'read': read,
           'cap': cap, 'lines': len(capped), 'lines_full': len(M['tfs']),
           'fires': bool(v >= int(K.FDM2_MOMO_VOTES)),
           'why': ('fdm2-momo %d of 3 at %s on %s - r-pred %d of %d ws4..ws%d (floor %d), '
                   'Mage-beyond-x %d of %d ws4..ws%d (median %d, carry side is BELOW), '
                   'pinned %d of %d ws4..ws%d (median %d)'
                   % (v, ln.U(bar), read, nr, len(capped), cap,
                      int(K.FDM2_MOMO_FLOOR_RPRED), nx, len(capped), cap,
                      int(K.FDM2_MOMO_MED_MX), npn, len(M['tfs']), int(LN['HI']),
                      int(K.FDM2_MOMO_MED_PIN)))}
    if not report:
        return out

    #   ── REPORT-ONLY from here. Nothing below is read by `votes` or `fires`. ───────────────────
    xw = max(1, int(K.FDM2_MOMO_XWIN))
    ng = ncr = nw = nrv = 0
    for t in capped:
        if int(M[('RP', read, t)][bar]) == side and towards(LN['CPR'][t], t, bar, side):
            ng += 1
        dif = np.asarray(xs[t], float) - np.asarray(mg[t], float)
        w = dif[max(0, bar - xw): bar + 1]
        dirn = 0
        for q in range(1, len(w)):
            a, c = w[q - 1], w[q]
            if np.isfinite(a) and np.isfinite(c) and a != 0.0 and (a > 0) != (c > 0):
                dirn = -1 if a > 0 else +1          # -1 = x crossed UNDER Mage
        if dirn:
            ncr += 1
            #   HIS FOUR CASES: a SHORT (side -1) reading x UNDER Mage votes `walk`, OVER votes
            #   `rev-trade`. A LONG (side +1) is the mirror.
            if (dirn < 0) == (side < 0):
                nw += 1
            else:
                nrv += 1
    pc = int(K.FDM2_MOMO_FLOOR_RPRED)
    out.update(gated=ng, cross=ncr, cwalk=nw, crev=nrv, pin_cap=npc, xwin=xw,
               s2_either=bool(f_x or nw > 0),
               votes_sub=v - (1 if nrv > 0 else 0),
               fires_sub=bool(v - (1 if nrv > 0 else 0) >= int(K.FDM2_MOMO_VOTES)),
               gated_fires=bool(ng >= pc))
    traj = []
    if ev is not None and int(ev) <= bar:
        bb = np.arange(int(ev), bar + 1, dtype=float)
        for t in capped:
            xv = np.asarray(M['XEM'][t], float)[int(ev):bar + 1]
            gv = np.asarray(LN['MGE'][t], float)[int(ev):bar + 1]
            ok = np.isfinite(xv) & np.isfinite(gv)
            if ok.sum() < 2:
                continue
            sx, ix = np.polyfit(bb[ok], xv[ok], 1)
            sm, im = np.polyfit(bb[ok], gv[ok], 1)
            d, rel = (sx * bar + ix) - (sm * bar + im), sx - sm
            btc = (-d / rel) if rel != 0 else float('inf')
            away_x = (sx > 0) if side < 0 else (sx < 0)
            away_m = (sm > 0) if side < 0 else (sm < 0)
            traj.append(dict(tf=t, sx=float(sx * 12.0), sm=float(sm * 12.0), gap=float(d),
                             bars_to_cross=float(btc), away_x=bool(away_x),
                             away_m=bool(away_m), both_away=bool(away_x and away_m),
                             cross_away=bool(btc > 0 and np.isfinite(btc) and away_x)))
        assert int(ev) <= bar, 'the trajectory fit started after the bar it is read at'
    out['traj'] = traj
    out['traj_both_away'] = sum(1 for z in traj if z['both_away'])
    out['traj_cross_away'] = sum(1 for z in traj if z['cross_away'])
    out['why_report'] = (
        'REPORT-ONLY at %s - towards-gated r-pred %d of %d (closed-prev gate), x-crossed-Mage %d '
        'in %d bars = %d s (%d `walk`, %d `rev-trade`), signal 2 under "either" %s, the vote with '
        'a rev-trade cross subtracted %d of 3, pinned on ws4..ws%d %d, trajectory %d of %d with '
        'both lines away and %d with a fitted cross travelling away'
        % (ln.U(bar), ng, len(capped), ncr, xw, xw * 5, nw, nrv,
           'fires' if (f_x or nw > 0) else 'does not fire', out['votes_sub'], cap, npc,
           out['traj_both_away'], len(traj), out['traj_cross_away']))
    return out


def _trace_row(bar, b0, side, mv, ok, why):
    """One XCAD_TRACE row: what decided `bar` of the cad walk that started at `b0`. -> dict.

    `ok` is None when fdm2-momo's `walk` verdict vetoed the bar, so the truncation test never ran.
    """
    return dict(bar=int(bar), b0=int(b0), side=int(side), since_s=(int(bar) - int(b0)) * 5,
                vetoed=bool(mv is not None and mv['fires']),
                votes=(int(mv['votes']) if mv else None),
                rpred=(int(mv['rpred']) if mv else None),
                mx=(int(mv['mx']) if mv else None),
                pin=(int(mv['pin']) if mv else None),
                tested=ok is not None, ok=ok,
                why=(('`walk` verdict, the truncation test did not run - ' + mv['why'])
                     if ok is None else str(why)))


def xcad_seam(LN, side, s0, xb, B, ev=None):
    """His update 2 - the emerging re-read at the ws1 seam. -> dict.

        bar     the rev-trade bar, or None when this cad walk printed none
        b0      THE CAD WALK'S FIRST BAR, the ws1 seam + FDM_XCAD_SEAM_S. It comes back so the
                caller can stamp a CAD WALK row on it - his 1106 housekeeping
        votes   the fdm2-momo verdict TRANSITIONS, oldest first, empty when the arm is off
        why     the one line that says what happened

    A DICT AND NOT A TUPLE, because this contract grew three times on 1106 and a positional return
    makes every caller a place the next field can be dropped. Each one is handed back so the caller can stamp a row on that
    verdict's OWN bar rather than leaving the only trace of it inside this function's `why`
    string. His 1106 RCA made the vote a per-bar veto, so there can be several of them; the latch
    that produced exactly one is gone.

    HIS UPDATE 2, verbatim: *"when the ws{TF}x cross fires, walk to the next ws1 seam+15s and
    collect the emerging values of the lines that were tagged as `towards` at the cadence. if the
    emerging values show `away` for all of the `towards` tagged lines, AND there are no more
    ex-20/80-fence lines tagged as `towards`, THEN send a rev-trade to router"*.

      s0      the cadence WINDOW's open - the start of the reversal gate's span, his 1104 *"the
              target-side reversal must fire between the opening of the cadence window and the
              confirmed x-cross bar"*
      xb      the bar the walk starts from. FDM_XCAD_FRM 'confirm' is his *"the conf bar"*
    HIS 1104 NARROWING IS STRUCK OUT, 1106. `above` and `exf_tw` are gone from the signature: the
    two-lines-above clause is his *"unwanted drag"* and the tagged scope went with it, because the
    test is now the whole board at the bar being read. xcad_tags still runs in walk(), but only to
    name the qualifying lines in the SEAM row's text - it no longer feeds the decision.

    THERE IS ONE TEST, AND IT IS THE WHOLE BOARD AT THE BAR BEING READ. His 1106 *"any r printing
    "towards while ex-20/80-fence""*, which is his earlier mech update read wide - *"because there
    are towards lines that are ex-20/80-fence, the cadence cannot print a rev-trade"*. The
    FDM_XCAD_C2_SCOPE 'tagged' arm and the FDM_XCAD_ABOVE clause are both struck out.

    EVERY READ IN HERE IS EMERGING, both the value and the fence, because he asked for the
    emerging values at this bar. THAT READING IS MINE TOO.

    THE REVERSAL GATE'S SPAN runs from `s0` to THE BAR BEING READ, FDM_XCAD_REV_TO 'read'. His
    1104 correction of his own ruling: *"the window's end can't be the confirmed x-cross - that
    would mean the grace period has zero value"*. At 'confirm' the span ends at `xb` and the turn
    count is frozen for the whole walk, which is the arm he struck out. Either way the gate reads
    no bar past the one being read, so nothing after the test bar is touched.

    THE WALK IS THE GRACE WALK'S SHAPE, which he called *"the established walk"*: re-test every
    5 s bar and break out on the first pass. FDM_XCAD_WALK_MIN 10.0 min = 120 bars, his value.
    """
    hi = int(LN['HI'])
    seam = [int(b) for b in LN['SEAM60'] if int(b) > int(xb)]
    if not seam:
        return dict(bar=None, b0=None, votes=[],
                    why='no ws1 seam after %s before the tape ends' % ln.U(int(xb)))
    b0 = int(seam[0]) + int(round(float(K.FDM_XCAD_SEAM_S) / 5.0))
    if b0 > int(B):
        return dict(bar=None, b0=b0, votes=[],
                    why=('the seam+%gs bar %s is past the leg walk\'s end %s'
                         % (float(K.FDM_XCAD_SEAM_S), ln.U(b0), ln.U(int(B)))))
    rs = int(s0) if str(K.FDM_XCAD_REV_FROM) == 'window' else None
    #   THE GATE'S UPPER END. At FDM_XCAD_REV_TO 'read' the stamps are handed over unclipped and
    #   the detector's own [rev_since, bar] filter ends the span at the bar being read, so a turn
    #   that lands during the walk counts the moment its stamp lands. At 'confirm' the stamps are
    #   clipped here and the count cannot move for the whole walk.
    to_read = str(K.FDM_XCAD_REV_TO) == 'read'
    gate = {t: (np.asarray(LN['LIFT'][(t, int(side))], int) if to_read
                else np.asarray([b for b in LN['LIFT'][(t, int(side))]
                                 if (rs if rs is not None else 0) <= b <= int(xb)], int))
            for t in range(1, hi + 1)}

    def exf_passed(b):
        """HIS `passed`: is ANY r towards while ex-fence at bar `b`, on emerging. -> (bool, why).

        THE NAME AND THE POLARITY ARE HIS, 1107. This used to be `passes`, returning True when NO
        line qualified - the opposite of his word, which caused exactly the confusion he asked to be
        called out: *"if it's ever ambiguous, call me out"*. His `passed` means a line IS towards
        while ex-fence, which is the `walk` verdict. The caller now reads `not passed` to decide a
        rev-trade, so the two readings cannot be mixed up again.

        HIS 1106 SECOND RCA, verbatim: *"the whole purpose of momo is to walk forward in the absence
        of any `r` printing "towards while ex-20/80-fence"  -at 1207, there is a line that qualifies
        (ws30, and probably others) so the code's only option is to walk to the next cadence or
        wsx-cadence event"*, and on the two-lines-above clause: *"this is unwanted drag.  in this
        context, the mech that drives momo's initialisation is very simple: any r printing "towards
        while ex-20/80-fence""*.

        WHAT HE STRUCK OUT, and the bar it was caught on. Clause one asked whether the
        FDM_XCAD_ABOVE lines ABOVE the highest ex-20/80 `towards` line had turned away. At
        2026-08-23 12:07:15 the highest such line was ws30, so there was nothing above it, the
        clause passed because it had nothing to check, and the rev-trade closed a +4.978% LONG at
        12:08:10 - the trade he wanted held. Its own text printed the fault: "no line above to test
        away".

        THE LINE SET IS ws{FDM_STEP1_ABOVE_TF+1}..ws{HI}, his 1107 *"keep it the minTF at ws4"*.
        I FIRST WROTE THIS OVER ws1..ws30, reading his *"any r"* with his 1016 ruling that `board`
        means the full range; he settled it the other way, and this is the correction.

        CAUSAL: `ex2080_line` and the detector both read `b` or earlier, and the reversal gate's
        stamps are clipped to `b` by the detector itself.
        """
        lo = int(K.FDM_STEP1_ABOVE_TF) + 1
        st = {}
        for t in range(lo, hi + 1):
            st[t] = JIG.fdm2_cad_mom_detector(LN['EMR'][t], LN['EMR'][t], int(b), int(side),
                                              int(s0), K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                                              K.LIFT_WOB, stamps=gate[t], rev_since=rs)['state']
        hits = [t for t in range(lo, hi + 1)
                if st[t] == 'towards' and ex2080_line(LN, t, b, side)]
        if hits:
            return True, ('ws%s %s ex-%g/%g AND towards on ws%d..ws%d, so `passed` - walk on'
                          % (', ws'.join(str(t) for t in hits),
                             'is' if len(hits) == 1 else 'are',
                             *K.fnc_pair(K.FDM_FNC_2080), lo, hi))
        return False, ('no line on ws%d..ws%d is ex-%g/%g AND towards, so NOT `passed`'
                       % (lo, hi, *K.fnc_pair(K.FDM_FNC_2080)))

    #   ── fdm2-momo's vote, HIS 1106 RCA ────────────────────────────────────────────────────────
    #   HIS CORRECTION, verbatim: *"if there is a walk verdict, there is no need to truncate the
    #   cad walk.  there is no harm caused if the verdict continues to be `walk` after the intial
    #   `walk` verdict, but if the verdict flips inside of the cad walk's max time then we don't
    #   miss that **correcting** verdict (ie rev-trade) and are able to react accordingly"*.
    #
    #   SO THE VOTE IS A PER-BAR VETO AND NOT A LATCH. It is read at EVERY bar of the cad walk and
    #   it suppresses the truncation test AT THAT BAR ONLY. The bar its verdict stops being `walk`
    #   is decided by the cad walk's own test, which is what prints his *"correcting verdict"*.
    #   Nothing is sticky, nothing is silenced, and the cad walk runs its full length either way.
    #
    #   WHAT THIS REPLACED, kept because the number is his evidence against it: the vote was read
    #   ONCE, at b0 = the cad walk's first bar, and a fire returned no rev-trade for the whole cad
    #   walk. On the 94.5-day tape the 28 legs that shape held longer went +32.523% to +25.974%.
    #   The read bar was also the weakest-signal bar, which is the RCA he named.
    #
    #   THE ROWS ARE THE VERDICT'S TRANSITIONS: one at the first bar and one at every bar the
    #   verdict changes, so the flip he asked not to miss is itself a timestamped event. Every bar
    #   is READ; only a change is STAMPED, because 121 identical rows per cad walk buries the leg
    #   report they exist to serve. The counts of read and vetoed bars ride in the returned why.
    end = min(b0 + int(round(float(K.FDM_XCAD_WALK_MIN) * 60.0 / 5.0)), int(B))
    votes, prev, nv, nt, lastw, lastb = [], None, 0, 0, '', None
    for b in range(b0, end + 1):
        mv = None
        if int(K.FDM2_MOMO_ON):
            mv = momo_vote(LN, b, side)
            assert int(mv['bar']) == int(b), 'fdm2-momo answered about a bar it was not asked'
            if mv['fires'] != prev:
                #   THE REPORT-ONLY READS ARE TAKEN ONLY ON A TRANSITION BAR, which is the only
                #   bar that gets a row. His rulings 2 to 6 never vote, and the `towards` gate
                #   costs an opposed-extremum scan per line, so paying for them at all 121 bars
                #   would buy nothing. The second call reads the SAME bar.
                mv = momo_vote(LN, b, side, report=True, ev=ev)
                votes.append(mv)
                prev = mv['fires']
            if mv['fires']:
                nv += 1
                if XCAD_TRACE is not None:
                    XCAD_TRACE.append(_trace_row(b, b0, side, mv, None, None))
                continue
        passed, why = exf_passed(b)
        ok = not passed      # HIS POLARITY: `passed` means walk on, so the rev-trade needs NOT it
        nt += 1
        lastw, lastb = why, b
        if XCAD_TRACE is not None:
            XCAD_TRACE.append(_trace_row(b, b0, side, mv, bool(ok), why))
        if not ok:
            continue
        tail = ('' if not nv else
                ' - fdm2-momo voted walk on %d of the %d bars from %s'
                % (nv, b - b0, ln.U(b0)))
        if b == b0:
            return dict(bar=b0, b0=b0, votes=votes,
                        why='the ws1 seam+%gs bar %s - %s%s'
                            % (float(K.FDM_XCAD_SEAM_S), ln.U(b0), why, tail))
        return dict(bar=b, b0=b0, votes=votes,
                    why='the %.1f min cad walk from %s, truncated at %s - %s%s'
                        % (float(K.FDM_XCAD_WALK_MIN), ln.U(b0), ln.U(b), why, tail))
    return dict(bar=None, b0=b0, votes=votes,
                why='the seam+%gs bar %s and the %.1f min cad walk to %s never passed - %s'
                    % (float(K.FDM_XCAD_SEAM_S), ln.U(b0), float(K.FDM_XCAD_WALK_MIN), ln.U(end),
                       ('fdm2-momo voted walk on every one of the %d bars, so the one test was '
                        'never reached' % nv) if not nt else
                       ('%d bars tested, %d vetoed by fdm2-momo, the last test at %s - %s'
                        % (nt, nv, ln.U(int(lastb)), lastw))))


def xcad_probe(LN, side, s0, xb, lines, bar):
    """The emerging numbers behind his update-2 verdict, line by line. -> [dict].

    HIS 1104 *"collect the emerging values of the lines that were tagged as `towards` at the
    cadence"* and *"add this data to the report so I can review"*. xcad_seam returns a verdict;
    this returns the numbers that verdict came from, read at the SAME bar with the SAME gate, so
    the two can never disagree.

        tf / value / extremum / at / gap / rev / state / exf / at_event

    `at_event` is the line's state at the cadence event, which is what `tagged` means. It is here
    so a clause-one line that was ALREADY away at the event is visible as such.
    """
    rs = int(s0) if str(K.FDM_XCAD_REV_FROM) == 'window' else None
    to_read = str(K.FDM_XCAD_REV_TO) == 'read'
    out = []
    for t in lines:
        t = int(t)
        gate = (np.asarray(LN['LIFT'][(t, int(side))], int) if to_read
                else np.asarray([b for b in LN['LIFT'][(t, int(side))]
                                 if (rs if rs is not None else 0) <= b <= int(xb)], int))
        r = JIG.fdm2_cad_mom_detector(LN['EMR'][t], LN['EMR'][t], int(bar), int(side), int(s0),
                                      K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB,
                                      stamps=gate, rev_since=rs)
        out.append(dict(tf=t, value=float(LN['EMR'][t][int(bar)]), extremum=r['extremum'],
                        at=r['at'], gap=r['gap'], rev=r['rev'], state=r['state'],
                        exf=ex2080_line(LN, t, bar, side)))
    return out


def x10_cadence(LN, side, frm, B):
    """The first ws10x race cross strictly after `frm` on `side`.

    -> (the confirm bar, which, the cross bar) | None. THE CROSS BAR IS IN THE TUPLE because that
    is the bar on the chart: his *"I can't see a cadence at 0121"* was 01:21:55, the CONFIRM, while
    ws10x crossed at 01:20:00 and the 24-bar hold carried it 115 s to the confirm. Only the confirm
    was being printed.

    HIS THREE CANDIDATES: to ib, to ws10r, to ws10Mage - first to confirm wins. Cross OVER on the
    low side, UNDER on the high side, his fallback's own rule and the banked x-cross direction.

    THE HOLD IS FDM_X10_WOB 24 bars = 120 s, his 1103 ruling *"now that we have the grade period,
    we can leverage a smaller wob: use 24"*. 36 is the other arm, from his own 1841 example.
    """
    #   HIS 1104 UPDATE 1 MOVED THE RACE TO x_race, WITH THE TIMEFRAME AS AN ARGUMENT. This name
    #   stays because every caller, spec line and banked number says ws10x; it now pins 10.
    return x_race(LN, 10, side, frm, B)


#   ── the bimodal decision's two measures ───────────────────────────────────────────────
def step1(LN, side, bar):
    """His step 1 at `bar`. -> (the count printing both, the lines scanned).

        are there same-side ex-fence `towards` lines printing above ws3r?

    "above" is IN TIMEFRAME, his ruling, so the scan is ws{FDM_STEP1_ABOVE_TF+1}..ws30 - 27 lines.
    "printing" is AT THE BAR: the line's own closed-prev value is ex-20/80 there AND it is
    travelling toward the target side there. That is the literal reading and it is the one his 1841
    number came from, 10 of 27. The alternative - ex-fence at least once during the trade, which is
    the POPULATION's test below - is a different question and he worded it differently.
    """
    k = 0
    lo = int(K.FDM_STEP1_ABOVE_TF) + 1
    tfs = list(range(lo, int(LN['HI']) + 1))
    for tf in tfs:
        if ex2080_line(LN, tf, bar, side) and towards(LN['CPR'][tf], tf, bar, side):
            k += 1
    return k, len(tfs)


def population(LN, side, opn, bar):
    """The lines ex-20/80 at least once in [opn, bar]. -> [tf]. ws3..ws30 before the filter.

        recreate the table using lines that have been ex-20/80-fence at least once during the
        trade / the n of 7 will need to change to n of {count of lines that went ex fence}

    FROZEN BY THE CALLER. His 1103 "no" to the population growing during the grace walk means this
    is called ONCE, at the ws10x-cadence, and the list is held for the 5 minutes.
    """
    edge = K.side_edge(K.FDM_FNC_2080, side)
    out = []
    for tf in range(int(K.FDM_POP_LO), int(LN['HI']) + 1):
        seg = LN['CPR'][tf][int(opn):int(bar) + 1]
        if bool(((seg >= edge) if int(side) > 0 else (seg <= edge)).any()):
            out.append(tf)
    return out


def rev_from(ev, s0):
    """The bar the reversal count starts from, by FDM_REV_FROM. -> bar.

    HIS 1103 2-POLE ASK: *"add a 2-pole knob: 'from the cadence event bar' and 'from the cadence
    event bar's window open'"*.

      'event'    `ev`, the cadence event bar - ws1b's oob->ib cross
      'window'   `s0`, the FIRST bar of that cadence event's ws1b oob excursion

    Both are at or before the cadence event, so neither reads a later bar. 'window' always starts
    earlier, so it can only count the same reversals or more.
    """
    b = int(s0) if str(K.FDM_REV_FROM) == 'window' else int(ev)
    assert b <= int(ev), 'the reversal count starts after the cadence event it belongs to'
    return b


def reversed_tfs(LN, side, pop, a, b):
    """Which of `pop` have a lift-off STAMP in (a, b]. -> [tf], ascending.

    ONE HOME for the membership test - `reversed_since` is its length. His 1103 *"how many of the
    28 lines were ex-fence and contributed to the ws10x-cadence?"* needs the LIST, not just the
    count, and a second implementation of the same test is where the two would drift.
    """
    assert int(b) >= int(a), 'a reversal window ends before it starts'
    out = []
    for tf in pop:
        st = LN['LIFT'][(int(tf), int(side))]
        if st.size and bool(((st > int(a)) & (st <= int(b))).any()):
            out.append(int(tf))
    return out


def reversed_since(LN, side, pop, a, b):
    """How many of `pop` have a lift-off STAMP in (a, b]. -> int.

    A reversal is a lift-off off the extreme on the TARGET side: the lines were running to that
    extreme and one left it. The stamp, not the lift bar - a lift at b-2 is not knowable at b.

    `a` comes from rev_from, which is the cadence event bar or its window's open.
    """
    return len(reversed_tfs(LN, side, pop, a, b))


#   ── the walk ──────────────────────────────────────────────────────────────────────────────────
def walk(LN, side, opn, B):
    """The first rev-trade signal for a trade opened at `opn` with target side `side`.

    -> (the signal bar or None, the decision rows). Every row is chronological.

    ORDER OF EVENTS IS STRICT. A cadence event is the spine of his mech - *"the mech will be
    walking from cadence event to cadence event"* - so the grace walk is BOUNDED by the next
    cadence event and never steps over one. THAT BOUND IS MINE: he ruled what happens at an
    expiry and at a <40%, but not what a cadence event landing inside the 5 minutes does.
    A TIE between the next cadence event and the ws10x-cadence goes to the CADENCE EVENT, also
    mine - it is the primary test and the ws10x is his *"second chance"*.
    """
    rows = []
    g_pct, t_pct = float(K.FDM_X10_GRACE_PCT), float(K.FDM_X10_TRADE_PCT)
    g_bars = int(round(float(K.FDM_X10_GRACE_MIN) * 60.0 / 5.0))
    evs = cadence_events(LN, side, int(opn) + 1, int(B))
    #   HIS 1107 EVENT LIST, verbatim: *"actioanable events to cache (and to report on in the leg
    #   report) -cadence window open -cadence window closed -any race results -grace walk events
    #   -50% test decisions -4-pronged-exfence-test decisions -ws{TF}x cross -fdm-momo2 decisions
    #   -rev-trade signal -exit event"*. Each one now gets its OWN timestamped row instead of
    #   living inside another row's text. The 4-pronged test's rows land with the 1107 redesign.
    for i, (ev, s0, why) in enumerate(evs):
        rows.append(dict(bar=int(s0), stage='cad_window_open', ev=ev, k=0, n=0,
                         why='the cadence window opens - ws1b goes oob on the %s side, and this is '
                             'the first bar of the excursion the preamble reads'
                             % ('HIGH' if int(side) > 0 else 'LOW')))
        rows.append(dict(bar=int(ev), stage='cad_window_closed', ev=ev, k=0, n=0,
                         why='the cadence window closes - ws1b crosses back to ib after %d bars = '
                             '%.1f min oob. %s'
                             % (int(ev) - int(s0), (int(ev) - int(s0)) * 5 / 60.0, why)))
        nxt = int(evs[i + 1][0]) if i + 1 < len(evs) else None
        k, n = step1(LN, side, ev)
        if k == 0:
            rows.append(dict(bar=ev, stage='cad_rev_trade', ev=ev, k=0, n=n, cwhy=why,
                             why='cadence event, 0 of %d lines ws%d..'
                             'ws%d printing ex-%g/%g AND towards - his "if the answer is no, then '
                             'rev-trade"' % (n, int(K.FDM_STEP1_ABOVE_TF) + 1, LN['HI'],
                                             *K.fnc_pair(K.FDM_FNC_2080))))
            return ev, rows
        #   ── fdm2-wsxcad-director, HIS 1104 UPDATE 1 ───────────────────────────────────────
        #   THE RACE'S TIMEFRAME IS CHOSEN HERE, not pinned to ws10. His *"apply the update to
        #   the code so that ws10 does not interfere with the intention of the spec"*: at
        #   FDM_XCAD_ON 1 the ws10 race is not run at all, so it can neither end this leg nor
        #   truncate the director's own walk. At 0 every banked number is reproduced.
        xtf, xabove, xcwhy = (None, (), '')
        if int(K.FDM_XCAD_ON):
            xtf, xabove, xcwhy = xcad_candidate(LN, side, ev, opn)
            if xtf is None:
                #   ── HIS 1105 FALLBACK ───────────────────────────────────────────────────────
                #   *"IF the scan for TFs inside of {linhop} jumps shows no candidates, then scan
                #   the entire range for ex-20/80-fence lines instead. if any are found, the
                #   cadence verdict is 'keep on walking'"*. It sits BEFORE FDM_XCAD_NONE, so a
                #   board with any ex-fence line on the side keeps the trade open instead of
                #   rev-trading at the event.
                if str(K.FDM_XCAD_FALLBACK) == 'exfnc':
                    exf2 = [t for t in range(1, int(LN['HI']) + 1)
                            if ex2080_line(LN, t, ev, side)]
                    if exf2:
                        rows.append(dict(bar=ev, stage='cad_walk', ev=ev, k=k, n=n, cwhy=why,
                                         why='the director found no candidate - %s - BUT %d of %d'
                                         ' lines are ex-%g/%g on the side: ws%s. His "keep on'
                                         ' walking"'
                                         % (xcwhy, len(exf2), int(LN['HI']),
                                            *K.fnc_pair(K.FDM_FNC_2080),
                                            ', ws'.join(str(t) for t in exf2))))
                        continue
                #   HIS RULING: *"no candidates = rev-trade"*, validated against this function's
                #   own step-1 branch above, which already rev-trades on a count of 0.
                if str(K.FDM_XCAD_NONE) == 'rev-trade':
                    rows.append(dict(bar=ev, stage='cad_rev_trade', ev=ev, k=k, n=n, cwhy=why,
                                     why='the director found no candidate - %s. His "no'
                                     ' candidates = rev-trade"' % xcwhy))
                    return ev, rows
                rows.append(dict(bar=ev, stage='cad_no_action', ev=ev, k=k, n=n, cwhy=why,
                                 why='the director found no candidate - %s, and FDM_XCAD_NONE is'
                                 ' no-action' % xcwhy))
                continue
        rtf_tf = int(xtf) if xtf is not None else 10
        x10 = x_race(LN, rtf_tf, side, ev, int(B))
        xb = x10[0] if x10 is not None else None
        xnm = 'the ws%dx-cadence' % rtf_tf
        win = ('the next cadence event' if nxt is not None and (xb is None or nxt <= xb)
               else (xnm if xb is not None else 'nothing - the tape ends'))
        if xb is not None:
            rows.append(dict(bar=int(x10[2]), stage='cwsx_cross', ev=ev, k=k, n=n, xtf=rtf_tf,
                             which=x10[1], cross=x10[2],
                             why='ws%dx crosses to %s - the RAW cross bar, before the hold'
                                 % (rtf_tf, x10[1])))
            rows.append(dict(bar=int(xb), stage='cwsx_confirm', ev=ev, k=k, n=n, xtf=rtf_tf,
                             which=x10[1], cross=x10[2],
                             why='the ws%dx-cadence confirms - the cross at %s held FDM_X10_WOB %d '
                                 'bars = %d s to here'
                                 % (rtf_tf, ln.U(int(x10[2])), int(K.FDM_X10_WOB),
                                    int(K.FDM_X10_WOB) * 5)))
        rows.append(dict(bar=int(nxt) if (win == 'the next cadence event' and nxt is not None)
                         else (int(xb) if xb is not None else int(ev)),
                         stage='cad_race', ev=ev, k=k, n=n, xtf=rtf_tf,
                         why='the race from the cadence event %s is won by %s%s'
                             % (ln.U(ev), win,
                                '' if win != 'the next cadence event' else
                                ' - the ws%dx-cadence at %s is dropped'
                                % (rtf_tf, ln.U(int(xb)) if xb is not None else 'never'))))
        rows.append(dict(bar=ev, stage='cad_walk', ev=ev, k=k, n=n, cwhy=why, xtf=rtf_tf,
                         why='cadence event, %d of %d lines printing ex-%g/%g'
                         ' AND towards -> walk. the race runs on ws%d%s. %s is first%s'
                         % (k, n, *K.fnc_pair(K.FDM_FNC_2080), rtf_tf,
                            '' if xtf is None else ' (%s)' % xcwhy, win,
                            '' if xb is None else ' (ws%dx crosses to %s %s, %s confirms %s)'
                            % (rtf_tf, x10[1], ln.U(x10[2]), xnm, ln.U(xb)))))
        if win != xnm:
            continue
        #   ── HIS 1104 UPDATE 2: the emerging re-read at the ws1 seam ───────────────────────────
        #   IT RUNS BEFORE the population branch, because his update 2 ends *"THEN send a
        #   rev-trade to router"*. On a hold the population branch below still gets its turn -
        #   he narrowed update 2 and never dropped the 50% rule or the grace walk, so neither is
        #   deleted here. THAT IS MY READING and it is the one thing in this block that is mine.
        if int(K.FDM_XCAD_ON):
            sfrm = xb if str(K.FDM_XCAD_FRM) == 'confirm' else int(x10[2])
            #   xcad_tags STILL RUNS, but only to NAME the qualifying lines in the SEAM row's
            #   text. His 1106 struck its two-lines-above clause out of the decision - *"this is
            #   unwanted drag"* - so `sab` and `sexf` are no longer handed to the seam read.
            sab, sexf, stwhy = xcad_tags(LN, side, ev, opn)
            sm = xcad_seam(LN, side, s0, sfrm, int(B), ev=ev)
            sbar, swhy, smomo = sm['bar'], sm['why'], sm['votes']
            rows.append(dict(bar=int(sfrm), stage='cwlk_seam', ev=ev, k=k, n=n, xtf=rtf_tf,
                             why='the director\'s seam read from %s - %s. %s'
                             % (ln.U(int(sfrm)), stwhy, swhy)))
            #   HIS 1106 HOUSEKEEPING: *"the debug table needs to print `CADENCE EVENT` when there
            #   is a cadence event, and `CAD WALK` if the cad walk is starting"*. The cad walk's
            #   first bar gets its own row, so a reader sees where the 10-minute re-test began
            #   rather than having to find it inside the SEAM row's text.
            if sm['b0'] is not None:
                rows.append(dict(bar=int(sm['b0']), stage='cwlk_start', ev=ev, k=k, n=n, xtf=rtf_tf,
                                 why='the cad walk starts - the ws1 seam+%gs bar after %s, and it '
                                     're-tests every 5 s bar for FDM_XCAD_WALK_MIN %.1f min = %d '
                                     'bars'
                                     % (float(K.FDM_XCAD_SEAM_S), ln.U(int(sfrm)),
                                        float(K.FDM_XCAD_WALK_MIN),
                                        int(round(float(K.FDM_XCAD_WALK_MIN) * 60.0 / 5.0)))))
            #   EVERY fdm2-momo VERDICT TRANSITION GETS ITS OWN TIMESTAMPED ROW, so a leg report
            #   reads the verdict and its flip as events rather than as a clause inside the SEAM
            #   row's text. HIS 1106: the leg reports need every timestamped event prepared, and
            #   his RCA named the flip - *"we don't miss that **correcting** verdict"* - as the
            #   thing the one-shot latch threw away.
            for mv in smomo:
                rows.append(dict(bar=int(mv['bar']), stage='cwlk_momo_vote', ev=ev, k=k, n=n,
                                 xtf=rtf_tf, votes=int(mv['votes']),
                                 rpred=int(mv['rpred']), mx=int(mv['mx']),
                                 pin=int(mv['pin']),
                                 why=('`walk` verdict, no rev-trade from this bar - '
                                      if mv['fires'] else
                                      'the `walk` verdict ends here, the cad walk\'s own test '
                                      'decides this bar - ') + mv['why']
                                     + ('. ' + mv['why_report'] if 'why_report' in mv else '')))
            if sbar is not None:
                #   THIS ONE IS THE CAD WALK'S, not the cadence event's - his 1106 *"I'm calling
                #   this out specifically to ensure there is a strict distinction between `cadence
                #   event`'s verdicts and `cad walk`'s verdicts"*. It is the only rev-trade row
                #   that comes out of the seam read's own walk.
                rows.append(dict(bar=int(sbar), stage='cwlk_rev_trade', ev=ev, k=k, n=n, xtf=rtf_tf,
                                 which=x10[1], cross=x10[2],
                                 why='the director - %s' % swhy))
                return int(sbar), rows
        pop = population(LN, side, opn, xb)
        rf = rev_from(ev, s0)
        rtf = reversed_tfs(LN, side, pop, rf, xb)
        rv = len(rtf)
        pct = (rv / len(pop) * 100.0) if pop else 0.0
        #   HIS 1107 *"50% test decisions"* - its own row at the bar it is taken, whatever it
        #   decides, so the figures are not only visible inside the verdict it happens to produce.
        rows.append(dict(bar=xb, stage='cwsx_pct', ev=ev, k=k, n=n, pop=tuple(pop), rv=rv,
                         pct=pct, which=x10[1], cross=x10[2], rev_tfs=tuple(rtf), rf=rf,
                         xtf=rtf_tf,
                         why='the 50%% test at the ws%dx-cadence confirm - %d of %d reversed since '
                             '%s (%s) = %.1f%%, against FDM_X10_TRADE_PCT %g%% to trade and '
                             'FDM_X10_GRACE_PCT %g%% for the grace walk'
                             % (rtf_tf, rv, len(pop), ln.U(rf), K.FDM_REV_FROM, pct, t_pct,
                                g_pct)))
        if pct >= t_pct:
            rows.append(dict(bar=xb, stage='cwsx_rev_trade', ev=ev, k=k, n=n, pop=tuple(pop), rv=rv,
                             pct=pct, which=x10[1], cross=x10[2], rev_tfs=tuple(rtf),
                             rf=rf, xtf=rtf_tf,
                             why='%s - ws%dx crossed to %s %s and confirmed'
                             ' here. %d of %d reversed since %s (%s) = %.1f%% >= %g%% at the'
                             ' race bar itself'
                             % (xnm, rtf_tf, x10[1], ln.U(x10[2]), rv, len(pop), ln.U(rf),
                                K.FDM_REV_FROM, pct, t_pct)))
            return xb, rows
        if pct < g_pct:
            rows.append(dict(bar=xb, stage='cwsx_no_action', ev=ev, k=k, n=n, pop=tuple(pop), rv=rv,
                             pct=pct, which=x10[1], cross=x10[2], rev_tfs=tuple(rtf),
                             rf=rf, xtf=rtf_tf,
                             why='%s - ws%dx crossed to %s %s and confirmed'
                             ' here. %d of %d reversed since %s (%s) = %.1f%% < %g%% - no branch,'
                             ' wait for the next cadence event'
                             % (xnm, rtf_tf, x10[1], ln.U(x10[2]), rv, len(pop), ln.U(rf),
                                K.FDM_REV_FROM, pct, g_pct)))
            continue
        #   THE GRACE WALK. The clock starts at the ws10x-cadence, the COUNT carries on from its
        #   value there - his *"why would it reset?  the grace fires on a low pct, and the low pct
        #   can't be derived until the ws10x cadence"* - and the re-count is per 5 s bar, his own
        #   correction to his "at each ws1 bar".
        end = min(int(xb) + g_bars, int(B))
        if nxt is not None:
            end = min(end, int(nxt) - 1)
        rows.append(dict(bar=xb, stage='cwsx_grace_start', ev=ev, k=k, n=n, pop=tuple(pop), rv=rv,
                         pct=pct, which=x10[1], cross=x10[2], rev_tfs=tuple(rtf),
                         rf=rf,
                         xtf=rtf_tf,
                         why='%s - ws%dx crossed to %s %s and confirmed here. %d of'
                         ' %d reversed since %s (%s) = %.1f%% >= %g%% -> grace walk %s .. %s, %d'
                         ' bars = %.1f min, population frozen at %d lines'
                         % (xnm, rtf_tf, x10[1], ln.U(x10[2]), rv, len(pop), ln.U(rf),
                            K.FDM_REV_FROM, pct, g_pct,
                                                 ln.U(min(int(xb) + 1, int(B))), ln.U(end),
                                                 end - int(xb), (end - int(xb)) * 5 / 60.0,
                                                 len(pop))))
        hit = None
        for b in range(int(xb) + 1, end + 1):
            t2 = reversed_tfs(LN, side, pop, rf, b)
            p2 = (len(t2) / len(pop) * 100.0) if pop else 0.0
            if p2 >= t_pct:
                hit = (b, len(t2), p2, tuple(t2))
                break
        if hit is not None:
            rows.append(dict(bar=hit[0], stage='cwsx_rev_trade', ev=ev, k=k, n=n, pop=tuple(pop),
                             rv=hit[1], pct=hit[2], which=x10[1], cross=x10[2],
                             rev_tfs=hit[3], rf=rf, why='grace walk, %d of %d reversed '
                             'since %s (%s) = %.1f%% >= %g%%'
                             % (hit[1], len(pop), ln.U(rf), K.FDM_REV_FROM, hit[2], t_pct)))
            return hit[0], rows
        rows.append(dict(bar=end, stage='cwsx_grace_expired',
                         why='grace walk expired at %.1f%%, never '
                         'reached %g%% - wait for the next cadence'
                         % ((reversed_since(LN, side, pop, rf, end) / len(pop) * 100.0)
                            if pop else 0.0, t_pct)))
    return None, rows


def saviour(LN, side, opn):
    """v4saviour on one fdm2 leg, with fdm2's own banked settings. -> (the signal bar, the why rows)

    -> (None, rows) when it does not fire.

    HIS 1103: *"bank the config that produced branch B at 1404 and wire it into the sandbox"*. The
    settings are fdm2's own knobs, because v4_machine.py reads SAV_CASCADE_MIN 4 and
    SAV_CASCADE_ZOOM 2 and moving those would move the live octo-v4 machine.

      FDM_SAV_READ 'emerging'   every read is the emerging set and the extremum sampler takes no
                                seam lattice, because an emerging line steps on every 5 s bar
      FDM_SAV_TF_HI 3          the cascade ladder is ws1..ws3
      FDM_SAV_MIN 3            a cluster must cover 3 of those 3
      FDM_SAV_ZOOM 2           each cluster step compares across 2 rungs
      FDM_SAV_ARM 0            the ws5r walkback is skipped, so ws5r is not read

    THE RETURNED BAR IS A SIGNAL, NOT THE CLOSE. v4saviour's own accounting puts the close at its
    `fill` and the re-open at `fill + 1` - one bar for both. fdm2's router spends TWO: close at
    signal + 1, open at signal + 2. So `fill`, which is the ib cross bar and knowable there, is
    handed back as a SIGNAL and the router does the rest. THAT IS MY READING of the two rules
    meeting, and it keeps every fdm2 exit on one accounting.

    ONCE PER TRADE has its owner here: `legs` calls this once per leg, which is his #32 with the
    trade mech holding it.
    """
    import v4_saviour as SAV
    em = str(K.FDM_SAV_READ) == 'emerging'
    R = {t: (LN['EMR'][t] if em else LN['CPR'][t]) for t in (1, 2, 5)}
    RE = R if em else {t: LN['EMR'][t] for t in (1, 2, 5)}
    MG = {t: (LN['MGE'][t] if em else LN['CPM'][t]) for t in range(1, 13)}
    sb = None if em else LN['SEAM60']
    v = SAV.walk(int(opn), int(side), R, MG, ln.U, RE=RE, arm=bool(int(K.FDM_SAV_ARM)),
                 tf_hi=int(K.FDM_SAV_TF_HI), anchor='ws1mage', sample_bars=sb,
                 min_lines=int(K.FDM_SAV_MIN), zoom=int(K.FDM_SAV_ZOOM))
    rows = [dict(bar=int(opn), stage='SAVIOUR ' + str(v['verdict']),
                 why=' | '.join('%s @ %s: %s' % (a2, b2, c2) for a2, b2, c2 in v['why']))]
    if v.get('fill') is None:
        return None, rows
    f = int(v['fill'])
    assert f >= int(opn), 'a saviour signal precedes its own leg open'
    rows[0]['bar'] = f
    rows[0]['why'] = ('v4saviour %s from %s | %s'
                      % (v['verdict'], v.get('from_line', '-'), rows[0]['why']))
    return f, rows


def stop_bar(LN, opn, ex, side, cap):
    """The first bar the adverse excursion reaches `cap`. -> bar or None. Walked, not inferred.

    INTRA-BAR TIES GO TO THE ADVERSE SIDE. Inside one 5 s bar the high and the low are both there
    and their order is unknown, so a bar that breaches the cap is the stop even if it also moved
    favourably. That convention is MINE, carried unchanged from v4_chain.stop_bar, and it is the
    conservative one.
    """
    o = float(LN['close'][int(opn)])
    adv = np.asarray(LN['plo'][int(opn):int(ex) + 1], float) if side > 0 \
        else np.asarray(LN['phi'][int(opn):int(ex) + 1], float)
    pct = int(side) * (adv - o) / o * 100.0
    hit = np.flatnonzero(pct <= -float(cap))
    return int(opn) + int(hit[0]) if len(hit) else None


#   ── the chain ─────────────────────────────────────────────────────────────────────────────────
def legs(LN, open_at, B, resig=None, cap=None):
    """Every leg from `open_at` to `B`. -> list of leg dicts, chronological.

    THE DRIVER THAT OWNS THE STATE. fdm2 does not call v4_chain.legs: that module imports
    v4_lineage2 at module level, and importing it would drag the sealed stack into a greenfield
    build. The leg scoring, the stop and the flat-after-stop handling are the CHAIN's, not
    lineage2's, so they are carried here by value.

    THREE TRANSITIONS, no fourth:

        FLAT     -> a trade        the fdm re-entry fires. 1 bar, "just OPEN"
        a trade  -> the opposite   a rev-trade signal. 2 bars, "CLOSE then OPEN"
        a trade  -> FLAT           the FDM_MAE_CAP 1.1% stop. The re-entry is the only way back

    `cap` defaults to FDM_MAE_CAP, which his 1103 *"yes, move it to default"* turned ON. Passing
    None here does NOT turn it off - it takes the knob. An arm with no stop needs cap=0.0 and that
    is an off-ruled run.
    """
    cap = float(K.FDM_MAE_CAP) if cap is None else float(cap)
    close, phi, plo = LN['close'], LN['phi'], LN['plo']
    out = []
    opn, side = int(open_at[0]), int(open_at[1])
    src = str(open_at[2]) if len(open_at) > 2 else 'handed in'
    while opn < int(B):
        #   THE STOP IS FOUND FIRST, AND IT BOUNDS THE WALK. Before this the walk ran to `B` and
        #   the stop was applied after, so a leg that stopped still reported the rev-trade signal
        #   the walk had found LATER - on 2026-09-15 three legs printed a signal 3h10m, 3h26m and
        #   6h01m after their own exit bar. The signal and every decision row past the stop are
        #   bars past the leg's own exit, which is lookahead in the report.
        #   A TIE GOES TO THE STOP: the stop is a price event AT bar t, while a rev-trade signal at
        #   bar t does not close until t+1. That convention is MINE and it is stated here.
        stopped = stop_bar(LN, opn, int(B), side, cap) if cap > 0 else None
        bound = int(stopped) if stopped is not None else int(B)
        sig, rows = walk(LN, side, opn, bound)
        #   v4saviour, WIRED IN. THE EARLIEST SIGNAL WINS, which needs no priority rule: a walk
        #   forward meets whichever comes first. His #31 *"v4saviour priority"* was about
        #   v4-lineage's structure; here chronology settles it, and THAT IS MY READING.
        #   The saviour's own cap is 16 min from the open, so it can only ever fire early in a leg.
        src_sig = 'rev-trade'
        svrows = []
        if int(K.FDM_SAV_ON):
            sv, svrows = saviour(LN, side, opn)
            if sv is not None and int(sv) <= bound and (sig is None or int(sv) < int(sig)):
                sig, src_sig = int(sv), 'saviour'
        #   THE ROUTER'S CLOSE+OPEN ARM: the signal's close price bar is s+1 and the next open is
        #   s+2. His *"if it's close then open, consume 2 bars"*.
        if stopped is not None and (sig is None or int(sig) + 1 >= int(stopped)):
            ex, sig = int(stopped), None
        else:
            stopped = None
            ex = (int(sig) + 1) if sig is not None else int(B)
        #   W_FDM2_LEGDBG=on prints each leg's exit arithmetic BEFORE the asserts, so a failure
        #   names the leg instead of only the rule it broke. It lives here rather than in a
        #   fragment that re-implements this loop - that is how the 1841 three-row defect got in.
        if os.environ.get('W_FDM2_LEGDBG') == 'on':
            print('| %s | %s | %s | %s | %s | %s | %d |'
                  % (ln.U(opn), 'LONG' if side > 0 else 'SHORT',
                     ln.U(int(stopped)) if stopped is not None else '-',
                     ln.U(int(sig)) if sig is not None else '-', ln.U(ex),
                     ln.U(int(rows[-1]['bar'])) + ' ' + str(rows[-1]['stage']) if rows else '-',
                     len(rows)))
        #   EVERY ROW IS FILTERED BY THE LEG'S OWN EXIT, and only once `ex` is known. Filtering
        #   against the walk's `bound` instead let a saviour row at a bar between sig+1 and the
        #   stop through, and the 'a decision row is past the leg's exit' assert caught it on
        #   2026-08-03.
        rows = sorted([r for r in list(rows) + list(svrows) if int(r['bar']) <= ex],
                      key=lambda r: int(r['bar']))
        assert sig is None or int(sig) + 1 <= ex, 'a leg reports a signal after its own exit'
        assert not rows or int(rows[-1]['bar']) <= ex, 'a decision row is past the leg\'s exit'
        assert ex >= opn, 'a leg exits before it opens'
        o = float(close[opn])
        H = np.asarray(phi[opn:ex + 1], float)
        L = np.asarray(plo[opn:ex + 1], float)
        if side > 0:
            ap, vp = float(np.nanmin(L)), float(np.nanmax(H))
        else:
            ap, vp = float(np.nanmax(H)), float(np.nanmin(L))
        out.append(dict(
            opn=opn, side=side, src=src, sig=sig, exit=ex, rows=rows,
            ctype=('STOP at %.2f%%' % cap) if stopped is not None
                  else (src_sig if sig is not None else 'no rev-trade before the walk\'s end'),
            mae=min(abs(side * (ap - o) / o * 100.0), cap) if cap > 0
                else abs(side * (ap - o) / o * 100.0),
            mfe=side * (vp - o) / o * 100.0,
            rel=(-cap if stopped is not None else side * (float(close[ex]) - o) / o * 100.0),
            held_min=(ex - opn) * 5 / 60.0,
            stopped=stopped is not None))
        if sig is None and stopped is None:
            break
        if stopped is not None:
            #   FLAT. The way back in is the next re-entry signal AFTER the stop, and its side
            #   comes from the gcws30b window's own oob side - never from flipping the last trade.
            nxt = [g for g in (resig or []) if int(g['bar']) > int(ex)]
            if not nxt:
                break
            g = nxt[0]
            nb = SG.fire_bar(g)          # the "just OPEN, 1 bar" arm
            assert nb > int(ex), 'a re-entry fire bar is not after the stop that caused it'
            opn, side = nb, SG.target_side(SG.direction(int(g['side'])))
            src = 'fdm re-entry %s, window side %s' % (ln.U(int(g['bar'])),
                                                       'HIGH' if int(g['side']) > 0 else 'LOW')
            continue
        nb = int(sig) + 2
        assert nb > ex, 'a rev-trade opens at or before the bar that closed the trade'
        if nb >= int(B):
            break
        opn, side, src = nb, -side, 'rev-trade %s' % ln.U(int(sig))
    return out


def score(lg, drag=None):
    """The totals over a leg list. -> dict. Drag keeps its own entry AND its own total."""
    d = DRAG_PCT if drag is None else float(drag)
    n = len(lg)
    rel = sum(x['rel'] for x in lg)
    return dict(n=n, gross=rel, drag=d * n, net=rel - d * n,
                mae=sum(x['mae'] for x in lg), mfe=sum(x['mfe'] for x in lg),
                stops=sum(1 for x in lg if x['stopped']),
                min_held=min((x['held_min'] for x in lg), default=float('nan')),
                max_held=max((x['held_min'] for x in lg), default=float('nan')))
