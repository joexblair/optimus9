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

REFACTORED 0818. The gates now read momo_core.momo_fit() instead of calling momo() and then
re-fitting the same quadratic over the same slice - one fit per call, not two. Each rejection
carries a plain-words reason through momo_g_why(), because `none` meant six different things
in this file and four more in momo_core, and the one that matters - the bend pointing against
dr, which IS a reversal - looked exactly like no data.
"""
from contextlib import contextmanager

import numpy as np

from optimus9.compute import momo_core as X   # momo() and its MOMO_*/CURL_* constants live here.
#                                               Was `import build_exhv2` (repo root) until 0813,
#                                               which dragged in build_exhaust / build_rplwalk2 /
#                                               rpl_walk and cost minutes per process.
#                                               Joe 0813: "RPL is in sunset, so we need to salvage".


def momo_g(r, dr, w):
    """(state, slope, r2, r_at_bar) - momo() with Joe's 0805 curl gates applied.

    Returns 'none' where momo() would have returned an ungated 'curl'. Use momo_g_why() when you
    need to know WHICH gate rejected it - that is the difference between "no data" and "the line
    reversed", and the two used to print the same word."""
    st, _why, f = momo_g_why(r, dr, w)
    return st, f['slope'], f['r2'], f['r_at_bar']


def momo_g_why(r, dr, w, quad='auto', gate2=True):
    """(state, reason, fit) - the gated verdict, its reason, and every number behind it.

    REFACTORED 0818. This used to call momo() for the verdict and then re-fit the SAME quadratic
    over the SAME slice to run gates 2 and 3. It now reads one fit. Gate 2's number - the sign and
    size of the bend - is on the returned dict as `qa`, so a caller can see the reversal instead of
    only being told 'none'.

    gate2=False is WSF-CURL-MODE, named by Joe 0824: "a curl-detection mode that excludes gate 2,
    so that the curl and its dr can contribute to your modelling". Gates 1 and 3 still run. The
    DEFAULT IS True, so every existing caller - build_ws_fin, build_wsf_line_bar, jig, the s46 path
    - is untouched."""
    f = X.momo_fit(r, dr, w, quad=quad)
    st, why = X.verdict(f)
    if st != 'curl':
        return st, why, f
    ok, why = curl_gates(f, gate2=gate2)
    return ('curl' if ok else 'none'), why, f


def curl_gates(f, gate2=True):
    """(ok, reason) - Joe's three 0805 curl gates run against ONE fit.

    LIFTED OUT OF momo_g_why 0824 so that a caller holding the MEASUREMENTS but not the series -
    report_wsf_bar reads them back from wsf_line_bar - runs the same gates instead of a copy. The
    fork that this prevents already happened once, in report_domtf_walk.py.

    `f` needs five fields, and they are exactly the five banked per bar:
        aligned       the slope points with dr           wflb_aligned
        quad          a bend was measurable              wflb_bend_align IS NOT NULL
        quad_aligned  the bend points with dr            wflb_bend_align
        quad_r2       the bend's own r-squared           wflb_bendfit
        quad_why      why no bend, when quad is False    not banked, optional

    gate2=False drops the SECOND gate only. Gate 1 and gate 3 are unchanged, and so is the
    quad-missing check, because gate 3 needs the same measurement gate 2 does."""
    X._require_bound()
    # gate 1 - the same alignment test momo() applies to its own branch
    if not f['aligned']:
        return False, 'curl, but the slope points against dr'
    if not f['quad'] or f.get('quad_aligned') is None:
        return False, 'curl, but ' + (f.get('quad_why') or 'the bend could not be measured')
    # gate 2 - the bend must be a curl BEGINNING, not one that has already ended
    if gate2 and not f['quad_aligned']:
        return False, 'curl, but the bend points against dr'
    # gate 3 - the bend must actually describe the window
    if CURL_R2_MIN > 0.0 and f['quad_r2'] < CURL_R2_MIN:
        return False, 'curl, but the bend does not describe the window'
    return True, 'curl'


# Gate 3 floor, chosen from the data per Joe 0805 "use whatever value clears the errant 09:19 curl":
#   errant 07-27 09:19:00 s22 quadratic r2 = 0.3238  -> 0.40 is the lowest 0.05 step above it.
#   Across the 2,289 bars already passing gates 1+2: min 0.1553 p10 0.4157 median 0.6735 max 0.8719,
#   so 0.40 sits below the 10th percentile and keeps 90.8% of them. The errant bar is an outlier.
CURL_R2_MIN = None   # -> momo_config, mmc_curl_r2_min. The note above is the derivation;
#                      the VALUE now comes from the bank. Version 1 of both banks holds 0.40.

STATE = {'none': 0, 'momo': 1, 'curl': 2, 'sideways': 3}


def states(r, dr, lo, hi):
    """gated state per bar over [lo, hi] inclusive, as int8. Same encoding as build_s46_lines.py:14."""
    s = np.zeros(hi - lo + 1, np.int8)
    for k, i in enumerate(range(lo, hi + 1)):
        s[k] = STATE.get(momo_g(r, dr, i)[0], 0)
    return s


MOMO_FIXED_SAMPLES = None   # -> momo_config, mmc_momo_fixed_samples. None until a machine is named.
# MOVED TO THE BANK 0903. The note below is the derivation and it still stands; the VALUE now
# comes from the momo_config table, one bank per machine. Version 1 of both banks holds 21.
# KNOB, Joe 0814, MADE GLOBAL BY JOE 0820: "set it to 21 (both in your caller, and the code's
# default)". 0 = the gap between samples stays at MOMO_STEP_MIN and the sample count is whatever the
# window divided by that gives. A positive value fixes the SAMPLE COUNT and scales the gap instead.
#
# WAS 0 UNTIL 0820, and that default was mine, never Joe's - this file's own note used to read
# "DEFAULT IS OFF because momo_window is shared with the s46 path, which has not been measured",
# and docs/domTF-finisher_spec.md M10 recorded "Say the word to make it global." Joe said it.
# The consumers that inherit 21 from here and have NOT been re-measured at it: build_momo_landed,
# build_handoff, build_ws_momo, s46_momo, build_s46_event, sweep_s46_momo and jig. build_ws_fin.py
# assigns 21 itself so it is unchanged.
#
# WHY. The window is K_WINDOW x the line's timeframe (Joe 0810: "it should be dynamic. use this
# value: {knob:4} x {TF width}") while the gap stayed at RPL's 5 minutes, so the sample count grew
# with the timeframe: 10 on a 13-minute line, 21 on a 27-minute one.
# MEASURED 08-04, how fast each line actually moves in r units per minute, median over 5-minute
# steps: ws13r 0.430, ws17r 0.363, ws21r 0.241, ws25r 0.221, ws27r 0.159 — the shortest line runs
# 2.71x the longest. With one fixed gap, MOMO_SLOPE_MIN 1.0 demands the SAME 0.200 r/min of every
# line, which is 2.15x what ws13r normally does and 0.80x what ws27r does. Fixing the count instead
# makes the demand track the line: the spread of demand-over-typical-rate falls from 0.80-2.15 to
# 0.84-1.23.
# COST, measured across 105 domTF signals on 08-04 at 21 samples: 4 verdicts change, 3 from held to
# free and 1 the other way, each one a single line crossing the momentum floor. Median hold 21.8 ->
# 19.2 minutes. It does NOT move Joe's three labelled bars.
# THE FLOOR THIS REMOVES, docs/task_register.md #60: at 0 the timeframes 1, 2 and 3 lines all get
# the same lattice - 2 points, 300 seconds apart - so "less width for smaller TFs" has nothing to
# act on below timeframe 4. At 21 the gap is 10 s at timeframe 1, 25 s at 2, 35 s at 3.
# STILL UNTUNED, task #1: the straight-line fit floor 0.50 and the curved fit floor 0.40 were set
# against a 12-point fit and are now applied to a 21-point one everywhere.


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
    X._require_bound()   # this reads MOMO_FIXED_SAMPLES and the step grid, so it is an entry point
    prev_w, prev_s, prev_b = X.MOMO_WINDOW_MIN, X.MOMO_SAMPLES, X.MOMO_STEP_BARS
    X.MOMO_WINDOW_MIN = int(window_min)
    if MOMO_FIXED_SAMPLES > 0:
        n = max(2, int(MOMO_FIXED_SAMPLES))
        X.MOMO_SAMPLES = n
        X.MOMO_STEP_BARS = max(1, int(round((int(window_min) * 12) / (n - 1))))
    else:
        X.MOMO_SAMPLES = max(2, int(window_min) // X.MOMO_STEP_MIN)
    try:
        yield X.MOMO_SAMPLES
    finally:
        X.MOMO_WINDOW_MIN, X.MOMO_SAMPLES, X.MOMO_STEP_BARS = prev_w, prev_s, prev_b
