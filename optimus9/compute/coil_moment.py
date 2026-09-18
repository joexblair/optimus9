"""coil_moment — the confluence moment, and the coil's confirmed release inside it.

TWO JOBS, both about GROUPING AND TIMING, not geometry. The coil numbers come from
stretchy_leash.py; the exit rule that consumes a release lives in coil_exit.py.

THE MOMENT (Joe 0917)
    a run of CONSECUTIVE wsf_dtf_v3 rows that all carry full leash support. The run ends when the
    next row prints below `support_min`, or with a different `dr`. Neither the clock nor the coil
    defines the end - the ROWS do, which is why a moment's `end` is only knowable when the next
    row prints.

THE RELEASE (Joe 0917)
    "the combined bar timestamp seems to need a lag during which it checks for a true release of
     the coil. test every 60 seconds"

    a turn-down candidate is bar t where the combined coil at t+1 is lower than at t; t is the
    peak. The candidate is CONFIRMED only if the coil never gets back above its value at t within
    `confirm_lag_s`. If it does, the release was false: reject t and carry on walking.

    The confirm window may read bars past the moment's last row - that is forward in TIME, not
    lookahead, and the verdict is only KNOWN at t + confirm_lag_s. The candidate peak itself must
    sit inside the moment.
"""
import numpy as np


def moments(rows):
    """Group `rows` into confluence moments.

    `rows` is an ordered sequence of dicts with:
        i        the 5 s bar index of the row
        dr       the row's dr
        ok       True when the row's leash support reached `support_min`

    -> list of dicts: i0, i1, dr, rows, brk (the bar of the row that broke the run, or None).
    """
    out, cur = [], []
    for j, a in enumerate(rows):
        if a['ok']:
            if cur and a['dr'] != cur[-1]['dr']:
                out.append((cur, j)); cur = []
            cur.append(a)
        else:
            if cur:
                out.append((cur, j)); cur = []
    if cur:
        out.append((cur, None))
    return [dict(i0=m[0]['i'], i1=m[-1]['i'], dr=m[0]['dr'], rows=len(m),
                 brk=(rows[b]['i'] if b is not None else None)) for m, b in out]


def release(cc, i0, i1, lag_bars, last_bar=None):
    """The first CONFIRMED turn-down of the combined coil inside [i0, i1].

    `cc(i)` returns the combined coil at bar i. `lag_bars` is confirm_lag_s / the grid.
    `last_bar` is the highest bar `cc` can be asked for - the confirm window is clipped to it so a
    moment near the end of the tape reads a SHORT window instead of running off the end. A clipped
    window can only fail to disconfirm, so a release confirmed on one is confirmed on less evidence
    than the rest; the caller sees it as confirmed either way.

    -> (bar, True) on a confirmed release, or (i1, False) when nothing confirms inside the moment.
       The caller decides what an unconfirmed moment means; coil_exit.py applies Joe's rule.
    """
    n = i1 - i0
    hi = i1 + lag_bars if last_bar is None else min(i1 + lag_bars, last_bar)
    v = np.array([cc(i) for i in range(i0, hi + 1)], float)
    for t in range(0, n + 1):
        if t + 1 > len(v) - 1:
            break
        if v[t + 1] >= v[t]:
            continue                                   # still coiling, not a turn
        w = v[t + 1:min(len(v), t + 1 + lag_bars)]     # the confirm window
        if lag_bars > 0 and len(w) and w.max() > v[t]:
            continue                                   # false release - the coil came back
        return i0 + t, True
    return i1, False
