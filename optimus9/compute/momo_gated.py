"""momo_gated — build_exhv2.momo() with the two curl gates Joe added 0805.

THE DEFECT (found by Joe on n=6, 07-27 09:07:00, dr -1)
  momo() tests direction alignment ONLY on the `momo` branch. The flat branch checks the LEVEL, fits
  a quadratic, and returns `curl` without ever asking whether the slope or the arc points with the
  trade. On n=6 that armed a SHORT while s15r sat at 28.88 with slope +0.975 — rising against the
  trade — and with qa +22.635, a minimum, i.e. the down curl already ENDED, vertex at 0.259.

JOE'S CALLS 0805
  1 curl must pass the SAME alignment test as momo   -> dr -1 needs sl < 0 ; dr +1 needs sl > 0
  2 the arc must be CURL BEGINNING only              -> dr -1 needs qa < 0 (maximum: rises then FALLS)
                                                        dr +1 needs qa > 0 (minimum: falls then RISES)
  3 curl needs a QUADRATIC r2 floor                  -> CURL_R2_MIN, set from the errant 09:19 event
      Joe 0805: "curl should have a minimum. I don't know the value - use whatever value clears the
      errant 09:19 curl event". At 07-27 09:19:00 s22 on the 7|5|12 bank armed a SHORT on slope
      -0.059 with LINEAR r2 0.005 — a negative sign with no signal behind it. momo() floors its
      LINEAR fit at MOMO_R2_MIN 0.50; curl had no floor at all. The floor cannot be copied across:
      a genuine curl fits a STRAIGHT LINE badly by construction, so the floor sits on the QUADRATIC
      fit, which asks whether the parabola actually describes the data.

  qa is the quadratic's leading coefficient over momo()'s own 60-min window. qa > 0 opens upward = a
  MINIMUM; qa < 0 opens downward = a MAXIMUM. For a short the fall is BEGINNING at a maximum and
  ENDING at a minimum, so beginning-only means qa < 0. Mirrored for a long.

LOCATION. optimus9/compute/ — this is a per-bar classification of a line, the same concern as
swing_detect.py and indicator_computer.py. build_exhv2.py stays at the repo root; this imports it.

SRP. build_exhv2.momo() is NOT modified — predict_board.py:170 unpacks its 4-tuple, and vmomo.py /
build_trades2.py:93 are vectorised mirrors that must match it. This CALLS momo() for the base verdict
and applies the two gates on top, reusing momo()'s own constants so nothing forks.

`momo` and `sideways` and `none` pass through unchanged. Only `curl` is gated.
"""
import os
import sys
from contextlib import contextmanager

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import build_exhv2 as X            # repo root — momo() and its MOMO_*/CURL_* constants live there


def momo_g(r, dr, w):
    """(state, slope, r2, r_at_bar) — momo() with Joe's 0805 curl gates applied.

    Returns 'none' where momo() would have returned an ungated 'curl'."""
    st, sl, r2, rw = X.momo(r, dr, w)
    if st != 'curl':
        return st, sl, r2, rw
    # gate 1 — same alignment test momo() applies to its own branch (build_exhv2.py:159)
    if not ((sl > 0) if dr > 0 else (sl < 0)):
        return 'none', sl, r2, rw
    # gate 2 — arc must be CURL BEGINNING. Same window momo()'s curl block uses (build_exhv2.py:148).
    nb = X.MOMO_WINDOW_MIN * 12
    if w - nb + 1 < 0:
        return 'none', sl, r2, rw
    yy = r[w - nb + 1:w + 1]
    if not np.isfinite(yy).all():
        return 'none', sl, r2, rw
    xx = np.linspace(0.0, 1.0, len(yy))
    co = np.polyfit(xx, yy, 2)
    qa = co[0]
    if abs(qa) < 1e-12:
        return 'none', sl, r2, rw
    if not ((qa < 0.0) if dr < 0 else (qa > 0.0)):
        return 'none', sl, r2, rw
    # gate 3 — the QUADRATIC must actually describe the window
    if CURL_R2_MIN > 0.0 and quad_r2(yy, xx, co) < CURL_R2_MIN:
        return 'none', sl, r2, rw
    return 'curl', sl, r2, rw


def quad_r2(yy, xx, co):
    pred = co[0] * xx ** 2 + co[1] * xx + co[2]
    tot = ((yy - yy.mean()) ** 2).sum()
    return 1.0 - ((yy - pred) ** 2).sum() / tot if tot > 1e-12 else 0.0


# Gate 3 floor, chosen from the data per Joe 0805 "use whatever value clears the errant 09:19 curl":
#   errant 07-27 09:19:00 s22 quadratic r2 = 0.3238  -> 0.40 is the lowest 0.05 step above it.
#   Across the 2,289 bars already passing gates 1+2: min 0.1553 p10 0.4157 median 0.6735 max 0.8719,
#   so 0.40 sits below the 10th percentile and keeps 90.8% of them. The errant bar is an outlier.
CURL_R2_MIN = 0.40

STATE = {'none': 0, 'momo': 1, 'curl': 2, 'sideways': 3}


def states(r, dr, lo, hi):
    """gated state per bar over [lo, hi] inclusive, as int8. Same encoding as build_s46_lines.py:14."""
    s = np.zeros(hi - lo + 1, np.int8)
    for k, i in enumerate(range(lo, hi + 1)):
        s[k] = STATE.get(momo_g(r, dr, i)[0], 0)
    return s


@contextmanager
def momo_window(window_min):
    """[PRODUCER · Joe 0810] Run momo() over a window of `window_min` minutes instead of the module
    default of 60.

    WHY A CONTEXT MANAGER AND NOT AN ARGUMENT. momo() derives its sample grid from two MODULE
    globals read at call time:

        MOMO_STEP_BARS = MOMO_STEP_MIN * 12          # 60 bars = 5 min
        MOMO_SAMPLES   = MOMO_WINDOW_MIN // MOMO_STEP_MIN
        idx = [w - k * MOMO_STEP_BARS for k in range(MOMO_SAMPLES - 1, -1, -1)]

    MOMO_SAMPLES is computed ONCE at import, so a per-TF window means changing it between calls.
    The three alternatives all cost more:
      - adding a `window_min=` arg MODIFIES momo(), which this file exists to avoid, and would put
        predict_board.py:52 (a verbatim copy), vmomo.py and predict_walk.py out of sync;
      - a new implementation here FORKS the formula into a fourth copy.
    Joe 0810 confirmed this route. The mutation is contained and restored in a finally, so momo()
    stays the single implementation and no caller outside this block sees a changed global.

    NOT THREAD-SAFE, by construction — it mutates module state. Serial callers only.

    Joe 0810 on the window itself: "it should be dynamic. use this value: {knob:4} x {TF width}".
    MOMO_STEP_MIN stays 5 and does NOT scale, so the sample count varies with the window: 6 at a
    32-min window (TF8 x 4), 26 at 132 min (TF33 x 4). Queued for A/B — see task #1."""
    prev_w, prev_s = X.MOMO_WINDOW_MIN, X.MOMO_SAMPLES
    X.MOMO_WINDOW_MIN = int(window_min)
    X.MOMO_SAMPLES = max(2, int(window_min) // X.MOMO_STEP_MIN)
    try:
        yield X.MOMO_SAMPLES
    finally:
        X.MOMO_WINDOW_MIN, X.MOMO_SAMPLES = prev_w, prev_s
