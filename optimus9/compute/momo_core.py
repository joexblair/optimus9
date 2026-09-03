"""momo_core — the momentum verdict, and nothing else.

WHY THIS FILE EXISTS. Joe 0813: "RPL is in sunset, so we need to salvage" / "RPL will only poison
our ws spec, so you can't be reliant on it". momo() and its constants lived in build_exhv2.py at the
repo root, so every consumer of the momentum verdict imported RPL's exhaustion tool and, through it,
build_exhaust / build_rplwalk2 / rpl_walk. That import alone cost minutes per process. Measured 0813:
a ws script pulling momo_g took >300 s to start; the same script without it took 4.3 s.

RELOCATED, NOT COPIED. This is the SAME 50 lines, moved. build_exhv2 imports them back, so all 30
files that import build_exhv2 are untouched and predict_board.py:170 / vmomo.py / build_trades2.py
(vectorised mirrors that must match this formula) have nothing to re-sync against.

THE CONSTANTS ARE MODULE GLOBALS AND momo() READS THEM AT CALL TIME. Two things depend on that:
  - momo_gated.momo_window() rebinds MOMO_WINDOW_MIN / MOMO_SAMPLES per TF and restores them.
  - build_exhv2.main() rebinds them from argv (--r2 --slope --window --arc --dwell).
Both must now write to THIS module. build_exhv2.main() does so explicitly; a rebind of its own
globals would no longer reach momo() and the CLI flags would silently stop working.

THESE VALUES ARE RPL's. They were set on TF 4 / 15 / 22 exhaustion work and are untuned for the ws
finishers — see task #1 (URGENT) and task #6, which carries the second half: making the producer
take its constants as arguments so RPL and the finishers can hold separate banks.

NOTE ON MOMO_SLOPE_MIN. It is denominated PER SAMPLE, not per minute: momo() fits on
x = arange(len(y)), so the slope is r-units per sample STEP. Change MOMO_STEP_MIN and the same real
move reads as a different slope. Any new step needs its own slope floor derived with it.
REFACTORED 0818 (Joe: "refactor as you see fit"). momo() no longer measures - it reads momo_fit()
and picks a word. momo_fit() measures and decides nothing, so the numbers the verdict rests on stop
being destroyed inside the function. momo()'s 4-tuple is unchanged, by value and by type, so the
vectorised mirrors (predict_board.py:170, vmomo.py, build_trades2.py:93) have nothing to re-sync.
Checked by rebuilding the domTF walk and hashing v_ws_fin_walk against the pre-refactor baseline.
"""
import numpy as np

# THE NUMBERS LEFT THIS FILE 0903. They live in the momo_config table, one bank per machine, read
# by optimus9/compute/momo_config.py. Joe 0903: "I want the settings to be global per machine, ie
# dtf and wsf will have their own config" / "it seems like now is right for a SRP refactor".
#
# WHAT THIS FIXES. They were shared globals, so the 0903 bake-in of a dtf sweep (K_WINDOW 4->6,
# MOMO_SLOPE_MIN 1.0->1.2, MOMO_R2_MIN 0.50->0.70) moved wsf's verdict at the same time, with
# nothing on any row to say so. Version 1 of both banks holds exactly those values, so the split
# changed the shape and not one number.
#
# THIS FILE NOW OWNS THE VERDICT AND NONE OF THE NUMBERS. None until a machine is named:
#     with momo_config(momo_bank(db, 'wsf')):   ...
# There is deliberately no default. A default is what let one machine borrow another's numbers.
MOMO_R2_MIN = None          # the "fuzzy straight line". Joe's refs: momo 0.921 / sideways 0.024
MOMO_SLOPE_MIN = None       # the floor knob, r-units per 5-min sample. Joe's refs: 2.858 / 0.217
MOMO_WINDOW_MIN = None      # Joe 0731: was 45.
CURL_ARC_MIN = None         # Joe 0731: a CURL is not sideways. See the curl block in verdict().
CURL_VTX_LO, CURL_VTX_HI = None, None      # vertex must sit inside the window, not on its edge
MOMO_STEP_MIN = None        # sample spacing, minutes. 5 min = 60 bars at the 5 s grid
MOMO_STEP_BARS = None       # DERIVED from MOMO_STEP_MIN by momo_config, not a knob
MOMO_SAMPLES = None         # DERIVED from the window and the step by momo_config, not a knob
LEVEL_SLACK = None          # Joe 0731 "coin-toss it". Drawn uniform 0-15 on os.urandom entropy.
#                             The level gate slackens by LEVEL_SLACK * T, where the tracking score
#                             T = R2 * min(1, |slope|/momo_slope_min) clipped to [0,1].

_BOUND = None               # set by momo_config.momo_config() to "<machine> v<version>"


def _require_bound():
    """Raise a plain error if no machine has been named. Called by every entry point that reads a
    knob, so a producer that forgets fails loudly instead of running on whatever was left behind."""
    if _BOUND is None:
        raise RuntimeError(
            "momo: the knobs are not bound to a machine.\n"
            "  from optimus9.compute.momo_config import momo_bank, momo_config\n"
            "  with momo_config(momo_bank(db, 'domtf')):   # or 'wsf'\n"
            "      ... call the verdict in here ...\n"
            "Joe 0903: the settings are global per machine, so a caller must say which machine.")


def momo_fit(r, dr, w, quad='auto'):
    """MEASURE ONLY. Every number the verdict rests on, in a dict. Decides nothing.

    Joe 0817 asked what proved the 11:34 reversal. The answer was a number this file computed and
    threw away: at 08-04 11:33:30 ws1r bends +17.65 under a downward read. momo() called that bar a
    curl, momo_g rejected it and returned 'none', and the +17.65 died inside the call. This function
    is where it now lives.

    `quad` - the bend is expensive (a quadratic over MOMO_WINDOW_MIN * 12 bars).
      'auto'  fit it exactly where momo() has always fitted it: flat slope AND level gate passed.
      True    always fit it. For callers that need the bend on every bar whatever the branch.
      False   never fit it.

    Keys, always present:
      ok            were the samples usable at all
      why           plain-words reason when ok is False
      slope r2      the straight-line fit over MOMO_SAMPLES points
      r_at_bar      the line's value at w
      trk slack     the tracking score, and the level gate's slack that follows from it
      level         did the value clear 50 by the slack, on dr's side
      aligned       does the slope point with dr
      flat          is |slope| under MOMO_SLOPE_MIN
      quad          was the bend fitted
      n_lin n_quad  how many points each fit used
    Keys present only once the bend is fitted:
      qa qb qc      the bend's coefficients
      vtx           where the bend turns: 0 at the window's start, 1 at its end
      arc           how much it bends
      quad_r2       how well the bend describes the window
      quad_aligned  does the bend point with dr (qa < 0 for dr < 0)
      quad_why      plain-words reason when the bend could not be measured
    """
    _require_bound()
    f = {'w': int(w), 'dr': int(dr), 'ok': False, 'why': None,
         'slope': 0.0, 'r2': 0.0, 'r_at_bar': float('nan'),
         'trk': 0.0, 'slack': 0.0, 'level': False, 'aligned': False, 'flat': False,
         'quad': False, 'n_lin': 0, 'n_quad': 0}
    idx = np.array([w - k * MOMO_STEP_BARS for k in range(MOMO_SAMPLES - 1, -1, -1)])
    if idx[0] < 0:
        f['why'] = 'not enough history for the samples'
        return f
    y = r[idx]
    if not np.isfinite(y).all():
        f['why'] = 'gap in the samples'
        return f
    x = np.arange(len(y), dtype=float)
    sl, ic = np.polyfit(x, y, 1)
    res = ((y - (sl * x + ic)) ** 2).sum(); tot = ((y - y.mean()) ** 2).sum()
    r2 = 1 - res / tot if tot > 1e-12 else 0.0
    rw = float(r[w])
    # TRACKING-WEIGHTED LEVEL GATE (Joe 0731). A hard gate at 50 rejects a line that is 0.63 away and
    # tracking cleanly (0520 06:26 s15: r 50.63, slope -1.891, R2 0.818). T scores how well the line
    # tracks; the gate slackens in proportion. A flat line earns T~0 and no slack.
    trk = max(0.0, min(1.0, float(r2) * min(1.0, abs(sl) / max(1e-9, MOMO_SLOPE_MIN))))
    slack = LEVEL_SLACK * trk
    f.update(ok=True, slope=float(sl), r2=float(r2), r_at_bar=rw, trk=float(trk),
             slack=float(slack), n_lin=len(y),
             level=bool((rw >= 50 - slack) if dr > 0 else (rw <= 50 + slack)),
             aligned=bool((sl > 0) if dr > 0 else (sl < 0)),
             flat=bool(abs(sl) < MOMO_SLOPE_MIN))
    if quad is True or (quad == 'auto' and f['flat'] and f['level']):
        _fit_bend(r, dr, w, f)
    return f


def _fit_bend(r, dr, w, f):
    """The quadratic, written into `f`. Fitted over the FULL 5 s window (Joe 0731) - not the
    point-samples, which hallucinate turns: 18:49 s15 reads arc 1.27 at 12 points and 0.19 at 720.

    ONE FIT. It used to be fitted here and again in momo_gated.momo_g - the same slice with the same
    x at the same degree - so every gated curl paid for it twice."""
    f['quad_why'] = None
    nb = MOMO_WINDOW_MIN * 12                      # 5-min = 60 bars, so window_min * 12 bars
    if w - nb + 1 < 0:
        f['quad_why'] = 'not enough history for the bend'
        return
    yy = r[w - nb + 1:w + 1]
    if not np.isfinite(yy).all():
        f['quad_why'] = 'gap in the bend window'
        return
    xx = np.linspace(0.0, 1.0, len(yy))
    co = np.polyfit(xx, yy, 2)
    qa, qb, qc = float(co[0]), float(co[1]), float(co[2])
    f.update(quad=True, n_quad=len(yy), qa=qa, qb=qb, qc=qc,
             vtx=None, arc=None, quad_r2=None, quad_aligned=None)
    if abs(qa) <= 1e-12:
        f['quad_why'] = 'no bend to measure'
        return
    pred = qa * xx ** 2 + qb * xx + qc
    tot = ((yy - yy.mean()) ** 2).sum()
    f.update(vtx=-qb / (2 * qa), arc=abs(qa) * 0.25,
             quad_r2=float(1.0 - ((yy - pred) ** 2).sum() / tot) if tot > 1e-12 else 0.0,
             quad_aligned=bool((qa < 0.0) if dr < 0 else (qa > 0.0)))


def verdict(f):
    """(state, reason) from a fit. THE VERDICT ONLY - it measures nothing.

    The reason exists because `none` used to mean four different things in this file and six more in
    momo_gated, and a caller could not tell "no data" from "the line reversed"."""
    _require_bound()
    if not f['ok']:
        return 'none', f['why']
    if f['flat']:
        if not f['level']:
            return 'none', 'flat, and the wrong side of 50'
        # CURL (Joe 0731): "s22 is a curl: it goes up, and then points down at the walk." A straight
        # line fitted to an arc flattens to a low net slope and reads sideways. The bend disqualifies
        # the sideways verdict when its turning point falls inside the window with an arc of
        # CURL_ARC_MIN or more. Joe's reference sideways series has a turning point inside too, at
        # arc 2.06, so the arc height is what separates them.
        if (f['quad'] and f.get('vtx') is not None
                and CURL_VTX_LO < f['vtx'] < CURL_VTX_HI and f['arc'] >= CURL_ARC_MIN):
            return 'curl', 'curl'
        return 'sideways', 'sideways'
    if not f['level']:
        return 'none', 'sloped, and the wrong side of 50'
    if not f['aligned']:
        return 'none', 'sloped, pointing against dr'
    if f['r2'] < MOMO_R2_MIN:
        return 'none', 'sloped, but too crooked to call a line'
    return 'momo', 'momo'


def level_gate(r2, slope, dr):
    """The level the line had to reach at this bar, recomputed from a STORED fit.

    ONE IMPLEMENTATION, LIFTED OUT 0903. A caller holding the banked measurements but not the
    series runs this instead of its own copy. Same reason momo_gated.curl_gates was lifted out on
    0824, and the fork it prevents had already happened here: report_wsf_bar.py:168-169 carried its
    own MOMO_SLOPE_MIN 1.0 and LEVEL_SLACK 13.9 while build_wsf_walk_events read the shared ones,
    so the two printed different gates for the same bar and nothing said so.

        r2     the straight-line fit's r-squared, as banked (wflb_fit)
        slope  the straight-line fit's slope, as banked (wflb_slope)
        dr     +1 or -1

    -> the gate level, or None when either measurement is missing.

    THE SAME EXPRESSION momo_fit() uses on a live series, including its max(1e-9, ...) guard on the
    divisor, so a stored-fit gate and a live one cannot drift apart.
    """
    _require_bound()
    if r2 is None or slope is None:
        return None
    trk = max(0.0, min(1.0, float(r2) * min(1.0, abs(float(slope)) / max(1e-9, MOMO_SLOPE_MIN))))
    return (50 - LEVEL_SLACK * trk) if dr > 0 else (50 + LEVEL_SLACK * trk)


def momo_why(r, dr, w, quad='auto'):
    """(state, reason, fit) - momo() with its reason and its numbers kept."""
    f = momo_fit(r, dr, w, quad=quad)
    st, why = verdict(f)
    return st, why, f


def momo(r, dr, w):
    """(state, slope, r2, r_at_bar) for r line array `r`, bias dir `dr`, at bar `w`.
    state = momo | sideways | curl | none.

    MODULE-LEVEL (Joe 0801) so it can be re-read at any bar, not only the walk bar. It was a closure
    inside main(); the stash-and-test needs it per candidate cross, and a second copy in a
    measurement script would fork the logic.

    THE 4-TUPLE IS FROZEN. predict_board.py:170 unpacks it, and vmomo.py / build_trades2.py:93 are
    vectorised mirrors of the same formula. Use momo_why() for the reason and momo_fit() for the
    numbers - do not widen this return."""
    f = momo_fit(r, dr, w)
    return verdict(f)[0], f['slope'], f['r2'], f['r_at_bar']
