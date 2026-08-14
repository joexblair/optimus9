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
"""
import numpy as np

MOMO_R2_MIN = 0.50          # the "fuzzy straight line". Joe's refs: momo 0.921 / sideways 0.024
MOMO_SLOPE_MIN = 1.0        # the floor knob, r-units per 5-min sample. Joe's refs: 2.858 / 0.217
MOMO_WINDOW_MIN = 60        # Joe 0731: was 45. SWEEP KNOB.
CURL_ARC_MIN = 4.0          # Joe 0731: a CURL is not sideways. SWEEP KNOB - see the curl block in momo().
CURL_VTX_LO, CURL_VTX_HI = 0.05, 0.95      # vertex must sit inside the window, not on its edge
MOMO_STEP_MIN = 5           # sample spacing. 5 min = 60 bars at the 5 s grid
MOMO_STEP_BARS = MOMO_STEP_MIN * 12
MOMO_SAMPLES = MOMO_WINDOW_MIN // MOMO_STEP_MIN     # 60/5 = 12 samples (was 9 at 45 min)
LEVEL_SLACK = 13.9          # Joe 0731 "coin-toss it". Drawn uniform 0-15 on os.urandom entropy.
#                             The level gate slackens by LEVEL_SLACK * T, where the tracking score
#                             T = R2 * min(1, |slope|/momo_slope_min) clipped to [0,1].


def momo(r, dr, w):
    """(state, slope, r2, r_at_bar) for r line array `r`, bias dir `dr`, at bar `w`.
    state = momo | sideways | curl | none.

    MODULE-LEVEL (Joe 0801) so it can be re-read at any bar, not only the walk bar. It was a closure
    inside main(); the stash-and-test needs it per candidate cross, and a second copy in a measurement
    script would fork the logic. Body unchanged - the MOMO_*/CURL_*/LEVEL_SLACK globals main() rebinds
    from argv are module globals, so a CLI override still reaches here.
    """
    idx = np.array([w - k * MOMO_STEP_BARS for k in range(MOMO_SAMPLES - 1, -1, -1)])
    if idx[0] < 0:
        return 'none', 0.0, 0.0, float('nan')
    y = r[idx]
    if not np.isfinite(y).all():
        return 'none', 0.0, 0.0, float('nan')
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
    level = (rw >= 50 - slack) if dr > 0 else (rw <= 50 + slack)
    if abs(sl) < MOMO_SLOPE_MIN:
        if not level:
            return 'none', float(sl), float(r2), rw
        # CURL (Joe 0731): "s22 is a curl: it goes up, and then points down at the walk." A straight
        # line fitted to an arc flattens to a low net slope and reads sideways. Fit a quadratic over
        # the FULL 5s window - not the 12 point-samples, which hallucinate turns (18:49 s15 reads
        # arc 1.27 at 12 pts and 0.19 at 720) - and disqualify the sideways verdict when the vertex
        # falls inside the window with an arc of CURL_ARC_MIN or more. Joe's reference sideways
        # series has a vertex inside too, at arc 2.06, so the arc height is what separates them.
        nb = MOMO_WINDOW_MIN * 12                      # 5-min = 60 bars, so window_min * 12 bars
        if w - nb + 1 >= 0:
            yy = r[w - nb + 1:w + 1]
            if np.isfinite(yy).all():
                xx = np.linspace(0.0, 1.0, len(yy))
                qa, qb, _ = np.polyfit(xx, yy, 2)
                if abs(qa) > 1e-12:
                    vtx = -qb / (2 * qa); arc = abs(qa) * 0.25
                    if CURL_VTX_LO < vtx < CURL_VTX_HI and arc >= CURL_ARC_MIN:
                        return 'curl', float(sl), float(r2), rw
        return 'sideways', float(sl), float(r2), rw
    aligned = (sl > 0) if dr > 0 else (sl < 0)
    if level and aligned and r2 >= MOMO_R2_MIN:
        return 'momo', float(sl), float(r2), rw
    return 'none', float(sl), float(r2), rw
