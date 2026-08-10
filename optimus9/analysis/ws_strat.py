"""ws_strat — the ws_strat_walk MECHANIC. Pure logic, no IO. Joe 0805.

Joe's spec, verbatim:

    starting at 08-04 12:00
    -walk forward on pxs
    -IF gcws30b has been oob for > {knob: 16} * 5s bars
    --IF gcws30b has crossed from OOB to IB, using XWOB={knob:2}
    ---store the crossover timestamp and the line values for:
        gcws30[b,Mage,r]
        ws[1,2,3,4,5,6][b,Mage,r]
    -loop the walk until cache end
    if a IB cross wob is incomplete, the OOB dwell is not affected      (Joe 0805)

SRP: this file decides WHERE the events are. optimus9/analysis/build_ws_strat_walk.py reads the
cache, writes ws_strat_walk and emits the pine. Same split as s46_momo.py / build_s46_event.py.

CAUSAL. Every array here is a backward-looking run count; nothing reads past its own bar. The IB
hold is the same discipline as s46's `sx_run_bars >= XWOB` stamped at +(XWOB-1) — an event is
stamped at the first bar it can be KNOWN, not the first bar it began.

OOB / IB use the jig's own definitions:
    OOB   v >= hi (85) or v <= lo (15)          jig.py:70-72 `sign()`
    IB    lo < v < hi, STRICTLY                 jig.py:610 `s_qualify_reset`
A NaN bar is neither, so it breaks both runs — which is the wanted behaviour: the gcws/ws x and m
lines go NaN on perfectly flat price (f_bb span==0), and a run must not span that.
"""
import numpy as np

# the lines banked at each event, in Joe's order. ws1x was appended 0805 because the gate read it;
# removed 0810 when Joe deleted the ws1x clause — nothing reads it now.
LINES = (['gcws30' + c for c in ('b', 'Mage', 'r')]
         + [f'ws{tf}{c}' for tf in (1, 2, 3, 4, 5, 6) for c in ('b', 'Mage', 'r')])


def run_len(mask):
    """Consecutive-True count ENDING AT each bar. The vectorised idiom cross_wob uses (jig.py:261-263),
    lifted because that producer returns the >= n BOOL and the walk needs the integer to bank."""
    m = np.asarray(mask, bool)
    idx = np.arange(len(m))
    reset = np.where(m, 0, idx + 1)              # last False position, carried forward
    return (idx + 1) - np.maximum.accumulate(reset)


def states(b, hi, lo, xwob):
    """The PER-BAR state of the walk. ONE definition, consumed by both walk() (the events) and
    build_ws_strat_walk.write_bars() (the per-bar debug table) — so the table and the events can
    never disagree about what a dwell or a confirmation bar is.

    THE DWELL (Joe 0805: "if a IB cross wob is incomplete, the OOB dwell is not affected").
    `dwell` counts OOB bars on ONE side. An IB excursion SHORTER than xwob does NOT touch it — the
    counter is carried across the excursion and keeps accumulating when the line goes back OOB.
    It resets on a CONFIRMED cross (ib_run reaching xwob), on a side flip, and on NaN. The dwell a
    candidate is gated on is the value at its LAST OOB BAR.

    Returns arrays, all the same length as `b`, all backward-looking:
        oob_hi/oob_lo/ib       per-bar membership. NaN is False in all three.
        hi_run/lo_run/ib_run   UNBROKEN consecutive-bar count ending at each bar (diagnostics)
        dwell                  the dwell counter at each bar
        dwell_side             +1/-1 the side that counter belongs to, 0 = none open
        conf                   rising edge of (ib_run >= xwob) = the confirmation bar of an IB run
    """
    b = np.asarray(b, float)
    n = len(b)
    oob_hi, oob_lo = b >= hi, b <= lo
    ib = (b > lo) & (b < hi)                       # STRICT — NaN is False on both comparisons
    ib_run = run_len(ib)
    held = ib_run >= max(1, int(xwob))             # IB held xwob bars — "in effect"
    conf = held & ~np.r_[False, held[:-1]]         # RISING EDGE = the confirmation bar

    dwell = np.zeros(n, np.int64); dside = np.zeros(n, np.int8)
    D = 0; side = 0; xw = max(1, int(xwob))
    for i in range(n):
        if oob_hi[i] or oob_lo[i]:
            s = 1 if oob_hi[i] else -1
            if s != side:
                D = 0; side = s                    # side flip starts a new counter
            D += 1
        elif ib[i]:
            if ib_run[i] >= xw:
                D = 0; side = 0                    # a CONFIRMED cross closes the session
            #                                        an IB run SHORTER than xwob leaves D untouched
        else:
            D = 0; side = 0                        # NaN
        dwell[i] = D; dside[i] = side
    return {'oob_hi': oob_hi, 'oob_lo': oob_lo, 'ib': ib,
            'hi_run': run_len(oob_hi), 'lo_run': run_len(oob_lo), 'ib_run': ib_run,
            'dwell': dwell, 'dwell_side': dside, 'conf': conf}


def candidates(b, hi, lo, xwob, S=None):
    """EVERY OOB->IB crossover the xwob hold confirms, BEFORE the oobw dwell gate is applied.
    The rejected ones are the whole point of the debug table (Joe 0805 asked why 23:30:30 produced
    no emit; the answer was a 16-bar dwell failing >18, which only a pre-gate list can show).

    Per candidate: cross / conf / side / oob — same fields walk() returns."""
    S = S if S is not None else states(b, hi, lo, xwob)
    out = []
    for c in np.flatnonzero(S['conf']):
        cross = c - (int(xwob) - 1)                # the first IB bar of this run
        z = cross - 1                              # the last OOB bar before it
        if z < 0:
            continue
        if S['oob_hi'][z]:
            side = 1
        elif S['oob_lo'][z]:
            side = -1
        else:
            continue                               # the bar before the IB run was NaN, not OOB
        out.append({'cross': int(cross), 'conf': int(c), 'side': side, 'oob': int(S['dwell'][z])})
    return out


def walk(b, hi, lo, oobw, xwob, i0=0, i1=None):
    """Joe's walk on ONE line (gcws30b). Returns a list of dicts, one per OOB->IB crossover.

        b     the line, on the 5 s grid
        hi/lo the boundaries (85 / 15)
        oobw  KNOB 16 — the OOB dwell must be STRICTLY longer than this, in 5 s bars (>16 => 85 s)
        xwob  KNOB 2 — bars the line must hold IB for the cross to be confirmed
        i0/i1 the walk window, as bar indices. The dwell is allowed to have STARTED before i0 —
              looking back at line history is not lookahead. i1 exclusive; None = to the cache end.

    Per event:
        cross  index of the FIRST IB bar          (Joe's "crossover timestamp")
        conf   index of the confirmation bar      cross + (xwob-1); the first bar the event is knowable
        side   +1 the dwell was on the hi side, -1 lo
        oob    the dwell in 5 s bars, measured at the last OOB bar
    """
    i1 = len(b) if i1 is None else int(i1)
    return [e for e in candidates(b, hi, lo, xwob)
            if e['oob'] > int(oobw)                # Joe's ">" — strictly longer than the knob
            and i0 <= e['cross'] < i1]


# ─────────────────────────────────────────────────────────────────────────────────────────────────
# THE GATE — Joe's spec, CORRECTED 0810 (ws1x removed):
#
#     now we need to gate ws30 signals
#     -unless ws1Mage is OOB
#     --unless ws1b is outside of a 100-{knob:22} fence
#     ---a gcws30 signal is gated
#
#     IF gcws30 has created a signal and ws1b is not oob THEN a 19-bar lookback is employed to
#     capture a ws1b oob. IF the lookback captures ws1b oob THEN 1) mark the gcws30 signal as
#     `ws1-exhausted`, 2) leave the gcws30 signal ungated                          (Joe 0805)
#
#     if ws1b is outside of the fence and has not reached oob when gcws30 signals, then a flag is
#     set to show that ws1b was weaker than s1Mage                                 (Joe 0810)
#
#     ungated = ws1Mage OOB  OR  ws1b outside the fence  OR  the lookback
#
# ws1x DELETED (Joe 0810: "delete ws1x reversing from the spec"). Out of the gate, out of LINES, out
# of the tables. Measured before removal: as an AND on the openers it withheld 235 of 247, leaving
# the lookback to do 119 of 131 opens — jig._mage_rev fires on the ONE bar the run-length hits +-wob,
# so as a same-bar condition it almost never coincided.
#
# THE INDENTATION IS LOGICAL. Joe 0810: "the layout is typically logical when I spec — I just had an
# error in my writing this time." A deeper level is nested INSIDE the one above it, so `--` under `-`
# reads as AND. Read the levels; when they disagree with the prose, ask which is the error.
#
# NOT SIDE-MATCHED. "is OOB" means OOB, either side. Joe 0805 accepted that reading.
#
# STRICTLY CAUSAL. Every clause is read AT THE CONFIRMATION BAR, and the lookback window ENDS at
# that bar. Nothing past the bar is read.
#
# STILL TO BUILD (Joe 0805, parked): "increase BB multi on Mage and b to pull the signals back
# 30sec - AB MAE and MFE". Needs new indicator_configs rows at the higher mults, a cache build per
# mult, and an exit rule or horizon for MAE/MFE — none of which exist yet.
# ─────────────────────────────────────────────────────────────────────────────────────────────────
GATE_FENCE = 22      # KNOB, JOE'S SPEC VALUE. ws1b must sit outside [fence, 100-fence] = [22, 78].
#                      The 0806 sweep took this to 10 on event count alone. At 10 the fence [10,90] is
#                      WIDER than the OOB band [15,85], which INVERTS the clause: a ws1b that is
#                      genuinely OOB (85..90 or 10..15) then sits INSIDE the fence and the clause goes
#                      silent. 12 of 87 signals were in that zone, 3 of them gated with ws1b OOB.
#                      At 22 the fence sits INSIDE the OOB band, so outside-fence is the LOOSER test
#                      Joe wrote — every OOB reading also clears it. Joe 0810: reverted to spec.
GATE_LB = 19         # KNOB. lookback for a ws1b OOB, in 5 s bars = 95 s, ending AT the conf bar.



def gate(events, W, hi, lo, fence=GATE_FENCE, lb=GATE_LB):
    """Joe's gate:

        now we need to gate ws30 signals
        -unless ws1Mage is OOB
        --unless ws1b is outside of a 100-{knob:22} fence
        ---a gcws30 signal is gated

        released = ws1Mage OOB  AND  ws1b outside the fence

    Joe 0810, in plain terms: "block (gate) a gcws30 signal unless s1Mage is oob AND s1b is outside
    of its fence". BOTH must qualify. GATED IS THE RESTING STATE — the lines have no power to block,
    only to RELEASE; a signal that nothing releases simply stays blocked.

    WAS WRONG UNTIL THIS BUILD: an if/elif chain, i.e. OR — either line released on its own. That
    gave 283 released of 361.

        gated       1 = blocked, 0 = passes
        by          'ws1Mage+ws1b' | 'lookback' | '' when gated (nothing released it)
        ws1b_weaker Joe 0810: "if ws1b is outside of the fence and has not reached oob when gcws30
                    signals, then a flag is set to show that ws1b was weaker than s1Mage".
                    The consequence clause is a COMPARISON, so both sides must hold: ws1Mage OOB
                    AND ws1b outside the fence AND ws1b not OOB. Without the ws1Mage term the flag
                    fires on 87 signals and its own words are false on 59 of them, because ws1b
                    cleared the fence while ws1Mage cleared nothing.
        ws1_exhausted   Joe 0805: ws1b NOT oob at the bar AND the 19-bar lookback finds a ws1b oob.
                    The lookback reads ws1b only — untouched by the 0810 ws1x deletion.
        lb_oob / lb_fence   what the lookback found (Joe 0805: the distinction may matter later)
    """
    M, B = W['ws1Mage'], W['ws1b']
    for e in events:
        c = e['conf']
        mage_oob = bool(M[c] >= hi or M[c] <= lo)
        b_fence = bool(B[c] > 100 - fence or B[c] < fence)
        b_oob = bool(B[c] >= hi or B[c] <= lo)
        w = B[max(0, c - int(lb) + 1):c + 1]                      # causal: window ENDS at the conf bar
        e['lb_oob'] = int((w >= hi).any() or (w <= lo).any())
        e['lb_fence'] = int((w > 100 - fence).any() or (w < fence).any())
        e['exhausted'] = int((not b_oob) and e['lb_oob'])
        e['ws1b_weaker'] = int(mage_oob and b_fence and not b_oob)
        if mage_oob and b_fence:                                  # BOTH — Joe 0810
            e['by'], e['gated'] = 'ws1Mage+ws1b', 0
        elif e['exhausted']:
            e['by'], e['gated'] = 'lookback', 0
        else:
            e['by'], e['gated'] = '', 1
    return events
