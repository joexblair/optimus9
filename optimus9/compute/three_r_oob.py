"""three_r_oob — all three r lines out of bounds together. Joe 0925 named it `3roob`.

ONE JOB: given ws1r, ws2r, ws3r and a dr stretch, find the bars where all three sit out of bounds
on the dr side inside a rolling tolerance. It owns no threshold beyond the two it is handed, reads
no DB, and decides no trade.

JOE'S VERBATIM, 0925:
  "aside from the new `strat-3-r-oob` strategy, we've also (organically) created a `3 rs oob` mech
   that we can fire at every sig_utc"
  "1, use a 1min tolerance instead of a dwell / 2, unsure: let's start with anywhere in the stretch"
  "all 3 `r`s are oob at ~18:14. when all 3 are out together, there's really nowhere for them to go
   other than up - the trajectory can't last for long"

OOB IS 15/85. ALWAYS. Joe has three other fences and none of them is this one: 25/75 is Mage's,
17/83 is r-momo's, 27/73 is rule#1's, 40/60 is `SR_FENCE`.

THE TOLERANCE IS NOT A DWELL, AND A LINE ALREADY OOB STILL COUNTS. The first build read Joe's
"1 min tolerance" as the three CROSSINGS falling inside 60 s. That reading drops #6 itself, whose
ws2r crossed at 09-02 18:08:00, seven minutes before ws3r at 18:15:00. Joe's own example is the
counter-example, so the reading is wrong. The test is: at bar `i`, each line has been oob on the
dr side at some bar in [i - tol_bars, i].

THE EVENT BAR IS MINE. Joe set the tolerance and the fence and said nothing about which bar of a
qualifying run carries the label. This module takes the LAST bar of the earliest qualifying window
— the first bar at which the state is knowable. Stated when built, 0925, and the 28-row table Joe
tagged was produced under it.

CAUSAL. `last_oob` at bar `i` reads bars at or before `i`, and the window test is `i - last <= tol`.
Nothing looks forward.
"""
import numpy as np


def oob_mask(r, dr, oob):
    """Bars where `r` sits out of bounds on the dr side. -> bool array.

    dr -1 -> at or below oob[0]. dr +1 -> at or above oob[1].
    """
    r = np.asarray(r, float)
    return (r <= oob[0]) if int(dr) < 0 else (r >= oob[1])


def last_oob(r, dr, k0, k1, oob):
    """For each bar in [k0, k1], the index of the most recent oob bar at or before it.

    -> int array of length k1 - k0 + 1, holding -1 where no oob bar has been seen yet.
    """
    m = oob_mask(r, dr, oob)[int(k0):int(k1) + 1]
    out = np.full(len(m), -1, int)
    c = -1
    for i in range(len(m)):
        if m[i]:
            c = i
        out[i] = c
    return out


def held(lines, dr, k0, k1, tol_bars, oob=(15.0, 85.0)):
    """Is 3roob true at each bar of [k0, k1]. -> bool array.

    lines     {1: ws1r, 2: ws2r, 3: ws3r} on the 5 s grid
    tol_bars  Joe's 1 minute tolerance, 12 bars = 60 s at the 5 s grid
    oob       (15.0, 85.0). Always
    """
    k0 = int(k0); k1 = int(k1); tol = int(tol_bars)
    L = k1 - k0 + 1
    last = {t: last_oob(lines[t], dr, k0, k1, oob) for t in lines}
    out = np.zeros(L, bool)
    for i in range(L):
        out[i] = all(last[t][i] >= 0 and (i - last[t][i]) <= tol for t in lines)
    return out


def events(lines, dr, k0, k1, tol_bars, oob=(15.0, 85.0)):
    """Every 3roob event bar in [k0, k1]. -> list of bars, in order.

    An event is the START of a run of `held`, which is the last bar of that qualifying window —
    see the module docstring. A run already true at `k0` reports `k0`.
    """
    h = held(lines, dr, k0, k1, tol_bars, oob)
    if not len(h):
        return []
    starts = np.flatnonzero(h & ~np.concatenate(([False], h[:-1])))
    return [int(k0) + int(i) for i in starts]


def first_event(lines, dr, k0, k1, tol_bars, oob=(15.0, 85.0)):
    """The earliest 3roob event bar in [k0, k1]. -> bar or None."""
    e = events(lines, dr, k0, k1, tol_bars, oob)
    return e[0] if e else None
