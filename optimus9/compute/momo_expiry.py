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
    BITES   the line reverses back inside momo-fence-r AND HOLDS there for `return_bars`.
            From the bar it first came back inside it cannot be momentum-true; the state becomes
            KNOWABLE `return_bars - 1` bars later, when the hold completes.
    CLEARS  the line travels past the EXPIRY fence and holds it for `xwob` bars,
            or the dr flips - Joe: "clears on a dr flip".

THE RETURN HOLD, Joe 0915. Without it a 5-second brush against the fence armed and bit the expiry.
Measured over 08-25..08-28, ws2..ws12: 2,665 arm->bite pairs, of which 254 carried no flat-run -
and EVERY ONE of those 254 was an excursion of 60 s or less, 96% of them 15 s or less. There was
no case of a line making a real run past the fence and coming back without going sideways first,
which is Joe's own claim, confirmed.

    "I agree with your natural anchor, n can be 3 and swept"
    "my read on your summary: it's a happy accident - keep the wob"

3 BARS is the flat-run signal's own minimum - the shortest excursion that could contain a sideways
at all. It is an anchor to a competing mechanic, not a preference: the sweep showed no knee, the
miss rate falling smoothly from 9.5% at 1 bar to 3.8% at 12 and still falling.

THE WOB DOES NOT DO WHAT IT WAS ASKED TO DO, and Joe kept it knowing that. It was asked for to stop
sideways being missed; nothing was being missed. What it stops is the expiry firing on a brush.

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


def expired(r, k, dr, i0, mfr_knob, ex_knob, xwob, return_bars=1):
    """Is `r`'s dr-side momentum expired at bar k.

    r            the line, on the 5 s grid
    k            the bar being judged
    dr           +1 or -1
    i0           the bar the look-back starts at - the last dr change at or before k
    mfr_knob     momo-fence-r, as the single-number knob (17 -> 83/17)
    ex_knob      the expiry fence, as the single-number knob (50 -> 50/50)
    xwob         bars the line must hold past the expiry fence to clear
    return_bars  bars the line must hold back INSIDE momo-fence-r before the expiry bites.
                 1 = the old behaviour, bite on the first bar back inside.

    -> (expired, arm_bar, bite_bar, clear_bar). `bite_bar` is the bar the line FIRST came back
       inside; the state is knowable `return_bars - 1` bars after it. Bars are None when that step
       never happened.
    """
    m_lo, m_hi = fence_edges(mfr_knob)
    e_lo, e_hi = fence_edges(ex_knob)
    nb = max(1, int(return_bars))
    armed = bitten = False
    arm = bite = clear = None
    run = in_run = 0
    for j in range(int(i0), int(k) + 1):
        v = r[j]
        if not np.isfinite(v):
            continue
        if beyond(v, dr, m_lo, m_hi):
            if not armed:
                armed, arm = True, j
            bitten, bite, run, in_run = False, None, 0, 0   # outside again: not in force
            continue
        in_run += 1
        if armed and not bitten and in_run >= nb:
            bitten, bite = True, j - (in_run - 1)   # the bar it first came back inside
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
