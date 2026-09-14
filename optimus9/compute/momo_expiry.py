"""momo_expiry — spec §18. Joe 0914.

    "if an r-line has already exited the r-momo-fence and reversed back into the fence (ie its
     dr-side momentum has expired), it can not be tagged as mom-true until it has travelled past
     the mid-zone-fence edge"

SRP: this module answers ONE question - is this line's dr-side momentum expired at bar k. It does
not run the momentum verdict, it does not decide a route, and it owns no fence of its own; every
threshold arrives as an argument.

THE STATE MACHINE, with Joe's 0914 answers folded in:

    ARMS    the line exits momo-fence-r on the dr side. NO WOB on the arming cross - Joe: "drop it",
            after being told no wob exists on that cross anywhere in the chain.
    BITES   the line reverses back inside momo-fence-r. From that bar it cannot be momentum-true.
    CLEARS  the line travels past the EXPIRY fence and holds it for `xwob` bars,
            or the dr flips - Joe: "clears on a dr flip".

CAUSAL. The walk runs forward from the last dr change to the bar and reads nothing after it. The dr
flip bounds the look-back, so the history is never unbounded.

MINE, and unruled: "holds xwob" is read as a run of `xwob` CONSECUTIVE bars at or beyond the expiry
fence. The alternative is a wob confirming the state rather than the run.
"""
import numpy as np


def fence_edges(knob):
    """A fence knob is a single number: 100 minus the closest edge. Joe 0914.

    momo_fence_r 17 -> (17, 83).  momo_expiry.fence 50 -> (50, 50).
    """
    return float(knob), 100.0 - float(knob)


def beyond(v, dr, lo, hi):
    """Is `v` past the fence on the dr side. dr +1 reads the high edge, dr -1 the low."""
    return (v >= hi) if dr > 0 else (v <= lo)


def expired(r, k, dr, i0, mfr_knob, ex_knob, xwob):
    """Is `r`'s dr-side momentum expired at bar k.

    r         the line, on the 5 s grid
    k         the bar being judged
    dr        +1 or -1
    i0        the bar the look-back starts at - the last dr change at or before k
    mfr_knob  momo-fence-r, as the single-number knob (17 -> 83/17)
    ex_knob   the expiry fence, as the single-number knob (50 -> 50/50)
    xwob      bars the line must hold past the expiry fence to clear

    -> (expired, arm_bar, bite_bar, clear_bar). Bars are None when that step never happened.
    """
    m_lo, m_hi = fence_edges(mfr_knob)
    e_lo, e_hi = fence_edges(ex_knob)
    armed = bitten = False
    arm = bite = clear = None
    run = 0
    for j in range(int(i0), int(k) + 1):
        v = r[j]
        if not np.isfinite(v):
            continue
        if beyond(v, dr, m_lo, m_hi):
            if not armed:
                armed, arm = True, j
            bitten, bite, run = False, None, 0   # outside again: the expiry is not in force
            continue
        if armed and not bitten:
            bitten, bite = True, j
        if bitten:
            run = run + 1 if beyond(v, -dr, e_lo, e_hi) else 0
            if run >= int(xwob):
                armed = bitten = False
                clear, run = j, 0
    return bitten, arm, bite, clear


def last_dr_change(DR, k):
    """The bar at or before k where the latch last changed the dr. 0 when it never has."""
    for j in range(int(k), 0, -1):
        if DR[j] != DR[j - 1] and DR[j] != 0:
            return j
    return 0
