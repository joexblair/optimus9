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
    from optimus9.compute.rule2_trajectory import opposed_extrema
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
    MGE = LL.mage()
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
        G30B=np.asarray(LL._g30b(), float),
        close=close, phi=phi, plo=plo)


#   ── the reads ─────────────────────────────────────────────────────────────────────────────────
def deeper(a, b, side):
    """Is `a` more deeply oob than `b` on `side` - further from 50. -> bool."""
    return (a > b) if int(side) > 0 else (a < b)


def ex2080(v, side):
    """Is `v` external of the 20/80 fence on `side`. -> bool.

    HIS D: *"ex 20/80"*, and "ex" INCLUDES oob - his standing rule - so the test is at-or-beyond.
    """
    f = float(K.FDM_FNC_2080)
    return (v >= 100.0 - f) if int(side) > 0 else (v <= f)


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
    f3 = float(K.FDM_M3_FNC)
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
        m3 = bool(((m3seg >= 100.0 - f3) if side > 0 else (m3seg <= f3)).any())
        why = ('ws1b excursion %s..%s, the nestle is ws%dMage %.2f deeper than ws%dr %.2f at %s'
               % (ln.U(s0), ln.U(s1), nestle[1], nestle[2], nestle[3], nestle[4],
                  ln.U(nestle[0]))) if nestle else ''
        if trace:
            tr.append(dict(cross=int(c), inwin=inwin, s0=s0, s1=s1, nestle=nestle, m3=m3,
                           why=why))
        if nestle is None or not m3 or not inwin:
            continue
        out.append((int(c), int(s0), why))
    return tr if trace else out


#   ── the ws10x-cadence ─────────────────────────────────────────────────────────────────────────
def x10_cadence(LN, side, frm, B):
    """The first ws10x race cross strictly after `frm` on `side`. -> (the confirm bar, which)|None.

    HIS THREE CANDIDATES: to ib, to ws10r, to ws10Mage - first to confirm wins. Cross OVER on the
    low side, UNDER on the high side, his fallback's own rule and the banked x-cross direction.

    THE HOLD IS FDM_X10_WOB 24 bars = 120 s, his 1103 ruling *"now that we have the grade period,
    we can leverage a smaller wob: use 24"*. 36 is the other arm, from his own 1841 example.
    """
    w = max(1, int(K.FDM_X10_WOB))
    X10, R10, M10 = LN['X10'], LN['CPR'][10], LN['M10']
    #   WHICH BAR MUST FOLLOW THE CADENCE EVENT: the race's CROSS, or only its CONFIRM. At 'cross'
    #   a race that began before the cadence event is not this walk's ws10x even when it confirms
    #   after it. THAT IS THE ARM HIS OWN 1841 NUMBER CAME FROM - 1103_fdm's census used it - so it
    #   is the default on precedent, not on preference. At 'confirm' the event's identity is its
    #   confirm bar and an in-flight race counts.
    cf_only = str(K.FDM_X10_FRM) == 'confirm'
    lo = max(1, int(frm) - w + 2) if cf_only else int(frm) + 1
    hits = []
    for c, cf, s in oob_ib_cross(X10, K.OOB_HI, K.OOB_LO, w):
        if int(s) != int(side) or int(cf) > int(B):
            continue
        if (int(cf) if cf_only else int(c)) > int(frm):
            hits.append((int(cf), 'ib'))
            break
    for nm, other in (('ws10r', R10), ('ws10Mage', M10)):
        for i in range(lo, int(B) + 1):
            a, b = X10[i - 1], X10[i]
            oa, ob = other[i - 1], other[i]
            if not np.isfinite([a, b, oa, ob]).all():
                continue
            crossed = (a >= oa and b < ob) if side > 0 else (a <= oa and b > ob)
            if not crossed:
                continue
            end = i + w
            if end > len(X10):
                break
            seg = [(X10[j] < other[j]) if side > 0 else (X10[j] > other[j])
                   for j in range(i, end)]
            if all(seg) and i + w - 1 > int(frm):
                hits.append((i + w - 1, nm))
                break
    if not hits:
        return None
    bar, which = min(hits, key=lambda x: x[0])
    assert bar > int(frm), 'a ws10x-cadence is at or before the cadence event it follows'
    return bar, which


#   ── the bimodal decision's two measures ───────────────────────────────────────────────────────
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
        if ex2080(float(LN['CPR'][tf][int(bar)]), side) and towards(LN['CPR'][tf], tf, bar, side):
            k += 1
    return k, len(tfs)


def population(LN, side, opn, bar):
    """The lines ex-20/80 at least once in [opn, bar]. -> [tf]. ws3..ws30 before the filter.

        recreate the table using lines that have been ex-20/80-fence at least once during the
        trade / the n of 7 will need to change to n of {count of lines that went ex fence}

    FROZEN BY THE CALLER. His 1103 "no" to the population growing during the grace walk means this
    is called ONCE, at the ws10x-cadence, and the list is held for the 5 minutes.
    """
    f = float(K.FDM_FNC_2080)
    edge = (100.0 - f) if int(side) > 0 else f
    out = []
    for tf in range(int(K.FDM_POP_LO), int(LN['HI']) + 1):
        seg = LN['CPR'][tf][int(opn):int(bar) + 1]
        if bool(((seg >= edge) if int(side) > 0 else (seg <= edge)).any()):
            out.append(tf)
    return out


def reversed_since(LN, side, pop, a, b):
    """How many of `pop` have a lift-off STAMP in (a, b]. -> int.

    A reversal is a lift-off off the extreme on the TARGET side: the lines were running to that
    extreme and one left it. The stamp, not the lift bar - a lift at b-2 is not knowable at b.
    """
    assert int(b) >= int(a), 'a reversal window ends before it starts'
    n = 0
    for tf in pop:
        st = LN['LIFT'][(int(tf), int(side))]
        if st.size and bool(((st > int(a)) & (st <= int(b))).any()):
            n += 1
    return n


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
    for i, (ev, s0, why) in enumerate(evs):
        nxt = int(evs[i + 1][0]) if i + 1 < len(evs) else None
        k, n = step1(LN, side, ev)
        if k == 0:
            rows.append(dict(bar=ev, stage='REV-TRADE', ev=ev, k=0, n=n, why='cadence event, 0 of %d lines ws%d..'
                             'ws%d printing ex-%g/%g AND towards - his "if the answer is no, then '
                             'rev-trade"' % (n, int(K.FDM_STEP1_ABOVE_TF) + 1, LN['HI'],
                                             K.FDM_FNC_2080, 100.0 - float(K.FDM_FNC_2080))))
            return ev, rows
        x10 = x10_cadence(LN, side, ev, int(B))
        xb = x10[0] if x10 is not None else None
        win = ('the next cadence event' if nxt is not None and (xb is None or nxt <= xb)
               else ('the ws10x-cadence' if xb is not None else 'nothing - the tape ends'))
        rows.append(dict(bar=ev, stage='WALK', ev=ev, k=k, n=n, why='cadence event, %d of %d lines printing ex-%g/%g'
                         ' AND towards -> walk. %s is first%s'
                         % (k, n, K.FDM_FNC_2080, 100.0 - float(K.FDM_FNC_2080), win,
                            '' if xb is None else ' (ws10x %s to %s)' % (ln.U(xb), x10[1]))))
        if win != 'the ws10x-cadence':
            continue
        pop = population(LN, side, opn, xb)
        rv = reversed_since(LN, side, pop, ev, xb)
        pct = (rv / len(pop) * 100.0) if pop else 0.0
        if pct >= t_pct:
            rows.append(dict(bar=xb, stage='REV-TRADE', ev=ev, k=k, n=n, pop=tuple(pop), rv=rv,
                             pct=pct, which=x10[1], why='ws10x-cadence to %s, %d of %d reversed '
                             'since %s = %.1f%% >= %g%% at the cadence itself'
                             % (x10[1], rv, len(pop), ln.U(ev), pct, t_pct)))
            return xb, rows
        if pct < g_pct:
            rows.append(dict(bar=xb, stage='NO ACTION', ev=ev, k=k, n=n, pop=tuple(pop), rv=rv,
                             pct=pct, which=x10[1], why='ws10x-cadence to %s, %d of %d reversed '
                             'since %s = %.1f%% < %g%% - no branch, wait for the next cadence'
                             % (x10[1], rv, len(pop), ln.U(ev), pct, g_pct)))
            continue
        #   THE GRACE WALK. The clock starts at the ws10x-cadence, the COUNT carries on from its
        #   value there - his *"why would it reset?  the grace fires on a low pct, and the low pct
        #   can't be derived until the ws10x cadence"* - and the re-count is per 5 s bar, his own
        #   correction to his "at each ws1 bar".
        end = min(int(xb) + g_bars, int(B))
        if nxt is not None:
            end = min(end, int(nxt) - 1)
        rows.append(dict(bar=xb, stage='GRACE', ev=ev, k=k, n=n, pop=tuple(pop), rv=rv,
                         pct=pct, which=x10[1], why='ws10x-cadence to %s, %d of %d reversed since %s '
                         '= %.1f%% >= %g%% -> grace walk %s .. %s, %d bars = %.1f min, population '
                         'frozen at %d lines' % (x10[1], rv, len(pop), ln.U(ev), pct, g_pct,
                                                 ln.U(min(int(xb) + 1, int(B))), ln.U(end),
                                                 end - int(xb), (end - int(xb)) * 5 / 60.0,
                                                 len(pop))))
        hit = None
        for b in range(int(xb) + 1, end + 1):
            r2 = reversed_since(LN, side, pop, ev, b)
            p2 = (r2 / len(pop) * 100.0) if pop else 0.0
            if p2 >= t_pct:
                hit = (b, r2, p2)
                break
        if hit is not None:
            rows.append(dict(bar=hit[0], stage='REV-TRADE', ev=ev, k=k, n=n, pop=tuple(pop),
                             rv=hit[1], pct=hit[2], which=x10[1], why='grace walk, %d of %d reversed '
                             'since %s = %.1f%% >= %g%%'
                             % (hit[1], len(pop), ln.U(ev), hit[2], t_pct)))
            return hit[0], rows
        rows.append(dict(bar=end, stage='NO ACTION', why='grace walk expired at %.1f%%, never '
                         'reached %g%% - wait for the next cadence'
                         % ((reversed_since(LN, side, pop, ev, end) / len(pop) * 100.0)
                            if pop else 0.0, t_pct)))
    return None, rows


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
        sig, rows = walk(LN, side, opn, int(B))
        #   THE ROUTER'S CLOSE+OPEN ARM: the signal's close price bar is s+1 and the next open is
        #   s+2. His *"if it's close then open, consume 2 bars"*.
        ex = (int(sig) + 1) if sig is not None else int(B)
        stopped = stop_bar(LN, opn, ex, side, cap) if cap > 0 else None
        if stopped is not None:
            ex = int(stopped)
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
                  else ('rev-trade' if sig is not None else 'no rev-trade to the tape end'),
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
