"""domtf — THE domTF MECHANIC. One home, imported by every caller.

Joe 0822: "when I ask for a domTF walk, you will use the domTF mechs. import, don't
duplicate/split/fork ... I'm requiring this so that we don't miss anything as we effect our repairs
on domTF". Joe 0823, asked where it should live: "new module".

WHY THIS EXISTS. The domTF verdict - the blocking list and Joe's nested-opposition rule - was 23
lines inside build_ws_fin.py's main(). Nothing could import it, so report_domtf_walk.py copied it,
and the copy drifted: it omitted RESCUE_REJECTED_CURL from the opposition count. Two versions of
Joe's rule were live at once. That is the class of error Joe's instruction is aimed at.

SRP, and what is NOT in here:
  - loading lines from the cache or the database. Not domTF-specific; the caller's job.
  - writing tables. The caller's job.
  - anything from the wsf mechanic. Joe 0822: "stay away from wsf mechanic for now: we're working
    purely on fixing domTF".
Everything here takes plain arrays and returns plain data, the same contract jig.momo_landed uses.

THE KNOBS ARE PASSED, NOT DEFAULTED AT IMPORT. build_ws_fin.py learned this on 0814: a producer's
defaults bind at import time, so a caller that rebinds a module global afterwards silently gets the
old value while stamping the new one. Two walks were mislabelled that way.
"""
import numpy as np

from optimus9.compute import momo_core as MC
from optimus9.compute.momo_gated import momo_g, momo_window
from optimus9.analysis.jig import stall_mask

__all__ = ['blocking_at', 'cross_mask', 'inside_mask', 'stall_masks', 'guide_wire_dr']


def blocking_at(R, tfs, dr, bar, k_window, nested_opposition=True, nested_min=3,
                rescue_rejected_curl=True):
    """[PRODUCER] The domTF verdict at ONE bar: which timeframes are carrying the move.

    LIFTED VERBATIM from build_ws_fin.py main(), lines 479-501, on Joe 0822's instruction. The
    logic is unchanged - this is a move, not a rewrite.

        R          {tf_minutes: r array on the 5 s grid}
        tfs        the domTF ladder, DOMTF_MIN..DOMTF_MAX
        dr         +1 or -1
        bar        the bar index
        k_window   from momo_config, mmc_k_window. Each line's momentum window is k_window x its
                   own timeframe, in minutes. Passed in, never read from a global here.

    -> (blocking, opposing). `blocking` is empty when the nested-opposition rule fires.

    NESTED OPPOSITION, Joe 0813: "if a higher TF is showing bullish momo/curl, and it's matryoshka
    lines have curled to a bearish posture, then the verdict must be 'FREE'", and on the count:
    "there has to be a domino effect for the logic to be stable - ie more than 2 r lines must print
    a reversal or curl". More than 2 = at least 3.

    RESCUE_REJECTED_CURL, Joe 0813: a bend found FOR the move and thrown away because it points the
    other way counts as opposition. Asked whether such a bend is a vote the other way: "yes" / "if
    other lines are backing the curl line, it has considerable weight".
    """
    blk, opp = [], []
    for tf in tfs:
        with momo_window(k_window * tf):
            st, _s, _r2, _r = momo_g(R[tf], dr, bar)
            op, _s2, _r22, _r3 = momo_g(R[tf], -dr, bar)
        if st in ('momo', 'curl'):
            blk.append(tf)
        if op in ('momo', 'curl'):
            opp.append(tf)
        elif rescue_rejected_curl:
            with momo_window(k_window * tf):
                raw, rsl, _r2, _rw = MC.momo(R[tf], dr, bar)
                if raw == 'curl' and st == 'none':
                    nb = MC.MOMO_WINDOW_MIN * 12
                    yy = R[tf][bar - nb + 1:bar + 1] if bar - nb + 1 >= 0 else None
                    if yy is not None and np.isfinite(yy).all():
                        qa = np.polyfit(np.linspace(0.0, 1.0, len(yy)), yy, 2)[0]
                        aligned = (rsl > 0) if dr > 0 else (rsl < 0)
                        curved = (qa > 0) if dr > 0 else (qa < 0)
                        if not aligned or not curved:
                            opp.append(tf)
    if nested_opposition and blk and \
            sum(1 for o in opp if o < max(blk)) >= nested_min:
        blk = []
    return blk, opp


def cross_mask(causal, X, R, tfs, xwob):
    """[PRODUCER] The fast partner has crossed to the far side of its r line and held `xwob` bars.

    Delegates to Jig.cross_wob so there is ONE run counter in the system. Joe 0822: "if you've
    handrolled anything in the script: use the Jig to produce consistent results".

    Joe's direction rule, settled: reading UPWARD the x line crosses UNDER its target, reading
    DOWNWARD it crosses OVER. cross_wob's own `direction` is the side x ends up on, so it is the
    opposite sign of the read.

        causal   a Jig._Causal / rpl_cache._Cau - anything exposing cross_wob

    -> {+1: {tf: bool array}, -1: {tf: bool array}}, keyed by the DIRECTION BEING READ.

    NOTE for the consumer: cross_wob returns CONFIRMED-IN-EFFECT, true on every bar the x line
    stays on the crossed side. Its docstring says "the consumer takes the RISING EDGE for the
    confirmation moment".
    """
    return {+1: {tf: np.asarray(causal.cross_wob(X[tf], R[tf], -1, xwob)) for tf in tfs},
            -1: {tf: np.asarray(causal.cross_wob(X[tf], R[tf], +1, xwob)) for tf in tfs}}


def inside_mask(R, tfs, hi, lo):
    """[PRODUCER] The r line is strictly between the fences.

    Joe 0822 ruled this is NOT a condition on the handover cross: "this is a conflation of some sort
    - it defenitely wasn't my spec. r can be anywhere on the board, ie not restricted". Kept as a
    producer because jig.domtf_handover_median still takes the mask; callers that follow Joe's
    ruling pass all-True instead.
    """
    return {tf: (R[tf] > lo) & (R[tf] < hi) for tf in tfs}


def stall_masks(R, tfs, k_window, stall_n):
    """[PRODUCER] The stall, asked at every bar of every domTF line, on that line's OWN lattice.

    Joe 0810: "3 samples that have not exceeded the maxim". Joe 0814 raised it to 6.
    """
    lat = {}
    for tf in tfs:
        with momo_window(k_window * tf):
            lat[tf] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))
    return {dr: {tf: stall_mask(R[tf], dr, stall_n, *lat[tf]) for tf in tfs} for dr in (+1, -1)}


def guide_wire_dr(x, hi, lo, xwob):
    """[PRODUCER] domTF's direction from the guide-wire. THE GUIDE-WIRE IS ws13x.

    Joe 0823: "go back to the previous model (dr set on ib x oob), and use ws13x in place of ws27x".
    This is the ORIGINAL rule restored verbatim, with the line swapped. Nothing else changed.

    Joe's polarity, verbatim: "low oob ws27x = dr -1".

        the guide-wire is at or below `lo` and has been for `xwob` bars   -> dr -1
        the guide-wire is at or above `hi` and has been for `xwob` bars   -> dr +1
        the guide-wire is anywhere between the fences                     -> 0, NO DIRECTION

    IT IS A LEVEL TEST, NOT AN EVENT, AND IT DOES NOT LATCH. dr first becomes non-zero on the bar
    the run past the fence reaches `xwob` - which is the confirmed in-bounds-to-out-of-bounds
    crossing - and it returns to 0 the moment the line comes back between the fences. Joe 0823 on
    the consequence: "there is no direction, therefore no change to the domTF momentum tests".

        x      the guide-wire, on the 5 s grid
        hi/lo  85 / 15
        xwob   6 bars = 30 s past the fence

    Causal: every read is at or before its own bar.
    """
    x = np.asarray(x, float)
    idx = np.arange(len(x))
    out = np.zeros(len(x), np.int8)
    for side, sign in ((x <= float(lo), -1), (x >= float(hi), +1)):
        reset = np.where(side, 0, idx + 1)
        run = (idx + 1) - np.maximum.accumulate(reset)
        out[run >= max(1, int(xwob))] = sign
    return out
