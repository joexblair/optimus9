"""momo_seam — does the last timeframe-bar seam inside a fit window step toward dr.

WHY THIS FILE EXISTS. Joe 0912 ruled that a jump across a timeframe's own bar seam is not
crookedness: "the jump happens because it traversed the TF bar seam. this is the accepted nature of
emerging values" / "if the jump happend on the TF seam, there is no need for a threshold. the mech
should simply decide if the seam jump is towards dr" / "it's the final seam that matters".

SRP. momo_core decides the verdict and knows nothing about clocks or timeframes. This file knows
about clocks and timeframes and decides no verdict. The caller computes the fact here and hands it
to momo_core on the fit dict, the same way it hands over the series.

THE SEAM GRID IS MIDNIGHT-ALIGNED, NOT EPOCH-ALIGNED. Measured 0912 across all eleven dtf lines on
08-25: the modal offset of every line's large moves equals that day's midnight offset inside the
timeframe period, 11 matches out of 11. The offset changes every day, because 1440 minutes is not a
whole number of 13-, 14-, 17-, 19-, 21-, 22- or 23-minute bars - ws13 sits at 300 s on 08-25, 120 s
on 08-26 and 720 s on 08-27.

WHAT IT DOES NOT COVER. On 08-25 ws13 had 26 of its 96 moves above 5.0 r points land OFF the seam,
the largest 10.99, and 1,183 off-seam bars moved more than 1.0 r point. Joe 0912: "noted. we'll get
to them organically and consider the next move then".
"""
import numpy as np

_DAY_MS = 86_400_000


def seam_mask(ts, tf_min):
    """Per 5 s bar: is this bar the close of one of `tf_min`'s own bars.

        ts       the 5 s grid timestamps, epoch ms
        tf_min   the line's own timeframe, minutes

    A bar is a seam when (bar epoch ms - that day's midnight ms) divides exactly by the period.
    -> bool array, one per bar. Causal: it reads the clock, not the future.
    """
    ts = np.asarray(ts, np.int64)
    per = int(tf_min) * 60 * 1000
    return ((ts - (ts // _DAY_MS) * _DAY_MS) % per) == 0


def seam_toward_dr(r, seam, lo, hi, dr):
    """Did the LAST seam inside bars [lo, hi] step toward dr.

        r      the line, on the 5 s grid
        seam   seam_mask() for that line's timeframe
        lo hi  the fit window, inclusive. Use the first and last SAMPLE bars of the fit
        dr     +1 or -1

    The step across a seam bar k is r[k] - r[k-1]. Toward dr means negative at dr -1, positive at
    dr +1. Joe 0912 ruled the FINAL seam is the one that counts: earlier seams in the same window do
    not vote.

    -> True / False. False when the window holds no seam, or the step is zero, or either bar is NaN.
    """
    lo = max(1, int(lo)); hi = int(hi)
    if hi < lo:
        return False
    k = np.flatnonzero(seam[lo:hi + 1])
    if not len(k):
        return False
    k = lo + int(k[-1])
    a, b = float(r[k - 1]), float(r[k])
    if a != a or b != b:
        return False
    step = b - a
    return bool(step < 0.0) if dr < 0 else bool(step > 0.0)
