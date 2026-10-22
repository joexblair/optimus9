"""`v4saviour`, Joe 1022. His spec is quoted verbatim in v4_spec.md SS6b; this walks it.

ONE MECH, NOTHING ELSE. No trade open, no v4-lineage, no x-cross. Joe 1022 held the open mech back
on purpose: *"not for v4-saviour.  I'm holding it back so that your SRP is on point"*. The caller
supplies the open bar and the target-side; this returns v4saviour's verdict and its trace.

EVERY KNOB COMES FROM v4_knobs. Importing that module refuses an off-ruled run.

THE PRINT IS THE USABLE EVENT. Joe 1022: *"when i say "print" about anything, I'll always be
refering to the usable event"*. So a lift-off is read at its STAMP, bar + LIFT_WOB - 1, never at the
bar it left its extreme. Every bar this walk acts on is a stamp or a cross, and all of them are at
or before the bar the verdict lands on. CAUSAL: asserted.

THE VERDICTS ARE NOT ARMED, REV-TRADE and STAYS OPEN. Joe 1022 named a fourth, `ENDS`, then
withdrew it: *"ENDS wasn't the best wording - I prefer your STAYS OPEN"*. There is no fourth.

EACH BRANCH NEEDS BOTH TESTS: a counter cascade AND its own Mage not past 50 towards the
target-side. Joe 1022 added the clause after omitting it - *"ws1Mage is not printing past 50
towards the target-side (ie LONG trade, >50. SHORT trade, <50)"* - then ruled the fall-through,
*"it should go on to ws2r"*, then extended it to the second branch: *"ws2Mage also has the past 50
gate - ws2r should produce a STAYS OPEN"*. So:
    branch A  ws1r ib cross + counter cascade + ws1Mage not past 50  -> REV-TRADE, else branch B
    branch B  ws2r ib cross + counter cascade + ws2Mage not past 50  -> REV-TRADE, else STAYS OPEN
THE ws1Mage ROUTE BACK, Joe 1022, nested under his branch-B walk line: *"IF any ws1Mage bar lands
outside of the past-50-gate (wob 8), route to the ws1r mage-cascade test.  mage-cascade test is
anchored on the most recent target-side extrema"*. So branch B is not a one-way door - while it
walks to ws2r oob, ws1Mage leaving the gate for `SAV_MAGE_GATE_WOB` bars re-enters the ws1r test.
ITS ANCHOR IS DIFFERENT. This read is Mage-driven, so the cascade bar is
`mage_cascade_bar(ws1Mage, stamp, target_side, gap=SAV_CASCADE_GAP)` in mode 'extrema' - his own
1017 producer, the coarse walk back to a same-side turn then that line's true extreme forward of it.
THE LOOK-BACK GAP IS v4saviour's OWN, Joe 1022: *"create a v4-saviour specific knob that looks back
in 1 minute jumps"* - `SAV_CASCADE_GAP` 12 bars, against the Jig's MC_GAP 48. Passed per call, so no
other consumer of the producer moves. That is NOT
the lift-off anchor #25 ruled for the r-driven reads; he named this one explicitly.
    MY STRUCTURAL READS, both stated rather than decided quietly:
    the ORDER     the route and the ws2r cross are both live during the walk, and he did not rank
                  them. Whichever lands FIRST in time is taken.
    a MISS        he did not say what happens when the routed cascade is NOT counter. The walk
                  CONTINUES - the route is an extra chance inside branch B, not a termination.

A FAILED xwob MEANS THE CROSS DID NOT HAPPEN, NOT THAT THE MECH IS OVER. STRUCTURAL, and stated.
An xwob exists to reject a flicker; rejecting one cannot abandon the event. Measured on 2026-09-01
21:08:00: ws1r prints 15.77, one bar 0.77 above the fence, and is back at 13.89 the next bar - the
line never left oob. The genuine cross of that same excursion is 21:08:35 at 17.21 and it holds.
The first version of this walker took only the FIRST oob run, saw the hold fail and returned STAYS
OPEN without looking; Joe caught it: *"how does it fail the 2-bar hold?  if you look at the bars,
ws1r keeps falling"*. Branch A now scans on through the later oob runs inside the cap, as branch B
already did. Joe's #33 *"first"* selects the first oob RUN to watch; it does not make a flicker the
mech's last word.

THE MAGE IS THE BRANCH'S OWN TF. Branch A reads ws1Mage, branch B reads ws2Mage - not ws1Mage twice.

THE ARM READS ws5r ON THE COUNTER-TARGET SIDE - the side the trade was BORN FROM, not the side it
is heading to. RULED, Joe 1022, after two passes at it:
    *"the target-side belongs to the open trade, but the calculations that created that trade all
     sit on the opposite side - ie, a LONG trade was born from a low-side position, and a SHORT
     spawns from a hig-side position"*
    target-side    the open trade's. LONG = high, SHORT = low
    counter-target the side it was born from. A LONG reads ws5r against the LOW oob fence 15, a
                   SHORT against the HIGH oob fence 85
His spec line says only *"a trade opened while ws5r was NOT oob"* and the side was the one thing
that moved the verdict. On the 2026-09-06 22:21:50 LONG, ws5r is 12.11: oob on the counter-target
LOW side, so NOT ARMED - which is the verdict he confirmed. Read on the TARGET side instead it is
not oob, arms, and returns REV-TRADE off the 22:28:45 ws1r cross. All seven test legs reconcile
under the counter-target read and only 2220 moves, which is why it is this one and not the other.
"""
import sys
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
import v4_knobs as K
from optimus9.analysis.jig import mage_cascade, mage_cascade_bar, lift_off


def past_mid_toward(mage, bar, target_side):
    """Is `mage` past 50 TOWARDS the target-side at `bar`. Joe 1022, the clause he had omitted:
    *"ws1Mage is not printing past 50 towards the target-side (ie LONG trade, >50. SHORT trade,
    <50)"*. LONG is target-side high, so "towards" is above 50; SHORT is below."""
    return K.past_mid(mage[int(bar)], target_side)


def _runs(a, side):
    """the contiguous oob runs on `side` -> [(first bar, last bar)]"""
    m = (a >= K.OOB_HI) if side > 0 else (a <= K.OOB_LO)
    d = np.diff(np.r_[False, m, False].astype(np.int8))
    return list(zip(np.flatnonzero(d == 1).astype(int), (np.flatnonzero(d == -1) - 1).astype(int)))


def _ib_cross(a, run_end, xwob):
    """the bar after an oob run, if it holds ib for `xwob` bars. -> bar or None"""
    x = int(run_end) + 1
    w = a[x:x + int(xwob)]
    if len(w) < int(xwob) or not np.isfinite(w).all():
        return None
    return x if bool(((w > K.OOB_LO) & (w < K.OOB_HI)).all()) else None


def _cascade_at(line, tf, side, at_or_before, MG):
    """the cascade read at the line's most recent lift-off STAMP at or before `at_or_before`.

    -> (the stamp, the lift-off bar, the verdict, the cascade dict) or (None, None, None, None)
    """
    gap = K.gap_for(tf)
    L = [int(b) for b in lift_off(line, side, K.LIFT_PTS, gap, K.LIFT_TOL, K.LIFT_WOB)]
    st = [b + K.LIFT_WOB - 1 for b in L]
    ok = [(s, b) for s, b in zip(st, L) if s <= int(at_or_before)]
    if not ok:
        return None, None, None, None
    s, b = ok[-1]
    assert s <= int(at_or_before), 'the cascade bar is past the event bar'
    c = mage_cascade(MG, s, zoom=K.SAV_CASCADE_ZOOM, min_lines=K.SAV_CASCADE_MIN)
    return s, b, (None if c is None else c['verdict']), c


def walk(open_bar, target_side, R, MG, U):
    """v4saviour on one trade. -> dict with `verdict`, `why` and the bars it used.

      open_bar      the bar the trade opened on
      target_side   +1 high, -1 low. Joe #4: LONG = high, SHORT = low
      R             {1: ws1r, 2: ws2r, 5: ws5r}
      MG            {tf: ws{tf}Mage} for tf 1..12, for the cascade
      U             a bar -> timestamp formatter
    """
    o = int(open_bar)
    s = target_side
    want = 'down' if s > 0 else 'up'            # the COUNTER verdict
    why = []
    r1, r2, r5 = R[1], R[2], R[5]

    # ---- the arm: ws5r NOT oob when the trade opened
    armed = not K.oob(r5[o], -s)       # the COUNTER-TARGET side, the side the trade was born from
    why.append(('the open', U(o), 'ws5r %.2f, target-side %s' % (float(r5[o]), 'high' if s > 0 else 'low')))
    why.append(('the arm, ws5r oob on the COUNTER-TARGET side (%s)'
                % ('low' if s > 0 else 'high'), U(o),
                'ws5r oob %s -> %s' % ('YES' if not armed else 'no', 'NOT ARMED' if not armed else 'armed')))
    if not armed:
        return {'verdict': 'NOT ARMED', 'why': why, 'open': o}

    # ---- the cap. ONE timer from the OPEN, covering the whole mech. Joe 1022 raised it to 16 min
    # and moved its start here, *"to also cover the cases where ws1r does not reach oob"*.
    cap = K.sav_cap_bars()
    lim = o + cap
    why.append(('the cap', '%s to %s' % (U(o), U(lim)),
                '%d bars = %.0f min from the open' % (cap, K.SAV_WS2_OOB_TEST)))

    # ---- the first ws1r oob run on the target-side at or after the open. First only, causal.
    runs = [x for x in _runs(r1, s) if x[0] >= o and x[0] <= lim]
    if not runs:
        why.append(('no ws1r oob run on the target-side inside the cap', U(lim),
                    'the cap expired - the trade stays open'))
        return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
    why.append(('the first ws1r oob run', '%s to %s' % (U(runs[0][0]), U(runs[0][1])),
                '%d bars, peak %.2f, %d run(s) inside the cap'
                % (runs[0][1] - runs[0][0] + 1, float(np.nanmax(r1[runs[0][0]:runs[0][1]+1])), len(runs))))

    # ---- its oob->ib cross, held SAV_IB_XWOB
    x1 = None
    for a1, b1 in runs:
        c1 = _ib_cross(r1, b1, K.SAV_IB_XWOB)
        if c1 is None:
            why.append(('the ws1r cross is a flicker', U(b1 + 1),
                        'ws1r %.2f, back oob inside the %d-bar hold - not a cross, scan on'
                        % (float(r1[b1 + 1]), K.SAV_IB_XWOB)))
            continue
        if c1 > lim:
            why.append(('the ws1r oob->ib cross', U(c1),
                        'ws1r %.2f, past the cap at %s - the trade stays open' % (float(r1[c1]), U(lim))))
            return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
        x1, rs, re = c1, a1, b1
        break
    if x1 is None:
        why.append(('no ws1r oob->ib cross held inside the cap', U(lim),
                    'the trade stays open'))
        return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
    why.append(('the ws1r oob run that crossed', '%s to %s' % (U(rs), U(re)),
                '%d bars, peak %.2f' % (re - rs + 1, float(np.nanmax(r1[rs:re+1])))))
    why.append(('the ws1r oob->ib cross', U(x1), 'ws1r %.2f, held %d bars' % (float(r1[x1]), K.SAV_IB_XWOB)))

    # ---- branch A: the cascade at the ws1r reversal print
    st, lb, vd, c = _cascade_at(r1, 1, s, x1, MG)
    if st is None:
        why.append(('the ws1r lift-off for the cascade', '-', 'none at or before the cross'))
        return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
    why.append(('the ws1r lift-off', U(lb), 'stamped %s, %d s before the cross' % (U(st), (x1 - st) * 5)))
    why.append(('the cascade at the stamp', U(st), '%s | %s' % (vd, c['why'] if c else '-')))
    # ---- branch A needs BOTH: a counter cascade AND ws1Mage not past 50 towards the target-side
    pm = past_mid_toward(MG[1], x1, s)
    why.append(('ws1Mage past 50 towards the target-side', U(x1),
                'ws1Mage %.4f, %s' % (float(MG[1][x1]), 'YES' if pm else 'no')))
    if vd == want and not pm:
        why.append(('branch A fires', U(x1), 'counter cascade and ws1Mage not past 50'
                                             ' - end the trade, rev-trade on the next bar'))
        return {'verdict': 'REV-TRADE', 'why': why, 'open': o, 'fill': x1, 'reopen': x1 + 1,
                'from_line': 'ws1r'}
    miss = 'the cascade is not counter' if vd != want else 'ws1Mage is past 50 towards the target-side'

    # ---- branch B: walk to ws2r target-side oob inside the SAME cap, which includes its ib cross
    why.append(('branch A does not fire - branch B', U(x1),
                '%s. walk to ws2r oob, inside the cap to %s' % (miss, U(lim))))
    # the ws1Mage route back: the first bar a SAV_MAGE_GATE_WOB run outside the gate completes
    gw = K.SAV_MAGE_GATE_WOB
    outg = np.array([not past_mid_toward(MG[1], k, s) for k in range(x1, lim + 1)])
    route = None
    runlen = 0
    for i, v in enumerate(outg):
        runlen = runlen + 1 if v else 0
        if runlen >= gw:
            route = x1 + i
            break
    if route is not None:
        why.append(('ws1Mage left the past-50 gate', U(route),
                    'held %d bars = %d s, ws1Mage %.4f at the stamp' % (gw, gw * 5, float(MG[1][route]))))

    r2runs = [y for y in _runs(r2, s) if y[0] >= x1]
    for ys, ye in r2runs:
        if ys > lim:
            break
        x2 = _ib_cross(r2, ye, K.SAV_IB_XWOB)
        if x2 is None or x2 > lim:
            continue
        if route is not None and route <= x2:
            break                      # the route lands first in time - take it
        why.append(('the ws2r oob run', '%s to %s' % (U(ys), U(ye)),
                    '%d bars, peak %.2f' % (ye - ys + 1, float(np.nanmax(r2[ys:ye+1])))))
        why.append(('the ws2r oob->ib cross', U(x2), 'ws2r %.2f, %d bars inside the cap'
                    % (float(r2[x2]), lim - x2)))
        st2, lb2, vd2, c2 = _cascade_at(r2, 2, s, x2, MG)
        if st2 is None:
            why.append(('the ws2r lift-off for the cascade', '-', 'none at or before the cross'))
            return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
        why.append(('the ws2r lift-off', U(lb2), 'stamped %s, %d s before the cross' % (U(st2), (x2 - st2) * 5)))
        why.append(('the cascade at the stamp', U(st2), '%s | %s' % (vd2, c2['why'] if c2 else '-')))
        pm2 = past_mid_toward(MG[2], x2, s)
        why.append(('ws2Mage past 50 towards the target-side', U(x2),
                    'ws2Mage %.4f, %s' % (float(MG[2][x2]), 'YES' if pm2 else 'no')))
        if vd2 == want and not pm2:
            why.append(('branch B fires', U(x2), 'counter cascade and ws2Mage not past 50'
                                                 ' - end the trade, rev-trade on the next bar'))
            return {'verdict': 'REV-TRADE', 'why': why, 'open': o, 'fill': x2, 'reopen': x2 + 1,
                    'from_line': 'ws2r'}
        miss2 = ('the cascade is not counter' if vd2 != want
                 else 'ws2Mage is past 50 towards the target-side')
        why.append(('branch B does not fire', U(x2),
                    '%s - the trade stays open, v4saviour is complete' % miss2))
        return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
    return _route(route, x1, lim, s, want, MG, why, o, U)


def _route(route, x1, lim, s, want, MG, why, o, U):
    """The ws1Mage route back to the ws1r cascade test, or the cap expiring. -> the verdict dict."""
    if route is None:
        why.append(('the cap expired', U(lim),
                    'no ws2r cross and no ws1Mage route inside it - the trade stays open'))
        return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
    cb = mage_cascade_bar(MG[1], route, s, mode=K.SAV_CASCADE_MODE, gap=K.SAV_CASCADE_GAP)
    if cb is None:
        why.append(('the ws1Mage extrema anchor', '-', 'no same-side extrema before the tape starts'))
        return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
    assert cb[0] <= route, 'the ws1Mage anchor is past the stamp'
    c = mage_cascade(MG, cb[0], zoom=K.SAV_CASCADE_ZOOM, min_lines=K.SAV_CASCADE_MIN)
    vd = None if c is None else c['verdict']
    why.append(('the ws1Mage target-side extrema anchor', U(cb[0]),
                'ws1Mage %.4f, %d s before the stamp' % (float(MG[1][cb[0]]), (route - cb[0]) * 5)))
    why.append(('the routed cascade at the anchor', U(cb[0]), '%s | %s' % (vd, c['why'] if c else '-')))
    if vd == want:
        why.append(('the route fires', U(route), 'counter cascade and ws1Mage outside the gate'
                                                 ' - end the trade, rev-trade on the next bar'))
        return {'verdict': 'REV-TRADE', 'why': why, 'open': o, 'fill': route, 'reopen': route + 1,
                'from_line': 'ws1r via the ws1Mage route'}
    why.append(('the route does not fire', U(route),
                'the cascade is not counter - the trade stays open, v4saviour is complete'))
    return {'verdict': 'STAYS OPEN', 'why': why, 'open': o}
