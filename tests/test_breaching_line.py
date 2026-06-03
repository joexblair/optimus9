"""
Behaviour-by-example for breaching_line (Target-1 DoD). Spec: bl_machine_design.md.
predict_breach pinned by Joe's worked examples; exit methods + the dormancy model
(fence→0, curl-gated-to-OOB, 1→2→3 cascade, pegged-dormant) on synthetic series.
"""
import numpy as np

from optimus9.compute.breaching_line import BreachingLine, predict_breach


# ── prediction (Joe's examples, HI=85, K=75) ────────────────────────────────
def test_predict_hi_joes_examples():
    # m=56/M=120 → anchor 120, 35>10 → True ;  m=56/M=90 → anchor 90, 5>10 → False
    assert list(predict_breach(k=[75, 75], bb_m=[56, 56], bb_M=[120, 90])) == [1, 0]


def test_predict_lo_mirror():
    assert predict_breach(k=[20], bb_m=[5], bb_M=[44])[0] == -1


def test_fence_suppresses_prediction():
    assert predict_breach(k=[50], bb_m=[56], bb_M=[120])[0] == 0


def test_already_breached_is_not_predicted():
    assert predict_breach(k=[90], bb_m=[56], bb_M=[120])[0] == 0


# ── exit methods in isolation ───────────────────────────────────────────────
def _bl():
    # curl_lookback=1 so the short synthetic series exercise the curl on a 1-bar slope
    return BreachingLine(curl_floor=1.0, curl_lookback=1, pseudo_cross=15.0, flatten=0.5)


def test_exit3_cross_toward_ib():
    bl = _bl()
    assert bl._exit_cross_toward_ib(1, np.array([95., 80.]), np.array([84., 84.]), 1)
    assert bl._exit_cross_toward_ib(1, np.array([90., 86.]), np.array([84., 84.]), 1)   # pseudo
    assert bl._exit_cross_toward_ib(-1, np.array([5., 20.]), np.array([16., 16.]), 1)
    assert not bl._exit_cross_toward_ib(1, np.array([90., 92.]), np.array([84., 84.]), 1)


def test_exit2_fires_when_k_reverses_past_anchor():
    # hi breach: K peaks 90 at b2 (anchor = k[1] = 86); K falls below 86 at b4 →
    # exit2 (a clear K reversal) completes the journey.
    r = _bl().run(k=[50, 86, 90, 88, 80], bb_m=[50]*5, bb_M=[50]*5)
    assert list(r['state']) == [0, 1, 1, 2, 3]
    assert r['exit2'][4]


def test_exit2_silent_on_shallow_pullback():
    # K peaks 90 then only dips to 89 — never back past the anchor (86), so exit2
    # stays quiet and the journey never completes (the 16267 false-complete).
    r = _bl().run(k=[50, 86, 90, 89, 89], bb_m=[50]*5, bb_M=[50]*5)
    assert not any(r['exit2'])
    assert 3 not in list(r['state'])


def test_exit2_anchor_taken_at_tf9_seam():
    # Seams every 3 bars; K peaks 92 in TF9 bar B (b3-5). The anchor is the K just
    # before B's seam — k[2]=88 ("1 TF9 bar before max"), NOT k[3]=90 (1 5s bar).
    # K then dips to 89: above the TF9 anchor (88) so exit2 stays silent; a 5s
    # anchor (90) would have wrongly fired.
    seam = [True, False, False, True, False, False, True, False, False]
    k    = [50,   86,    88,    90,   92,    91,    89,   89,    89]
    r = _bl().run(k=k, bb_m=[50]*9, bb_M=[50]*9, seam=seam)
    assert r['k_anch'][4] == 88
    assert not any(r['exit2'])


# ── dormancy model ──────────────────────────────────────────────────────────
def test_fence_forces_state_0():
    # breached, then K returns to the 30:70 dead zone → dormant (state 0)
    r = _bl().run(k=[90, 50], bb_m=[50, 50], bb_M=[50, 50])
    assert list(r['state']) == [1, 0]


def test_curl_gated_to_oob():
    # K breaches then pulls to the engage band (IB, not fence); the slope would
    # "curl" but curl is gated to OOB → stays state 1
    r = _bl().run(k=[50, 90, 84], bb_m=[50]*3, bb_M=[50]*3)
    assert list(r['state']) == [0, 1, 1]


def test_lifecycle_dwell_at_2_then_complete():
    #        b0    b1    b2    b3(curl→2)  b4(BB OB→IB exit→3)
    r = _bl().run(k=[50, 90, 90, 86, 86], bb_m=[50]*5, bb_M=[50, 50, 50, 90, 50])
    assert list(r['state']) == [0, 1, 1, 2, 3]


def test_cascade_1_2_3_one_bar():
    # curl AND a BB OB→IB exit on the same bar → straight to 3 (through 2)
    r = _bl().run(k=[50, 90, 90, 86], bb_m=[50]*4, bb_M=[50, 90, 90, 50])
    assert list(r['state']) == [0, 1, 1, 3]


def test_pegged_stays_dormant_until_fresh_breach():
    #          b0  b1  b2  b3(→3) b4  b5  b6(IB)  b7(re-breach)
    k    = [50, 90, 90, 86,   90, 90, 84,    90]
    bb_M = [50, 90, 90, 50,   50, 50, 50,    50]
    r = _bl().run(k=k, bb_m=[50]*8, bb_M=bb_M)
    assert r['state'][3] == 3            # completed
    assert r['state'][4] == 3            # still OOB but pegged → no bobbing, stays 3
    assert r['state'][7] == 1            # IB then OOB again = fresh breach → re-armed


# ── exit3-before-curl grace (Joe, 2026-06-03): wait `grace` bars for the curl ──
def test_grace_exit3_then_curl_within_window_completes():
    # lo breach; e3 fires at b3 (bb_M crosses up through k), curl lands b4 (1 bar
    # later, within grace=2) → straight to 3.  bb_M only the e3 driver.
    k    = [50, 10, 10, 10, 12]
    bb_M = [50,  8,  8, 11, 11]
    r = _bl().run(k=k, bb_m=[50]*5, bb_M=bb_M)
    assert list(r['state']) == [0, 1, 1, 1, 3]


def test_grace_expires_curl_too_late_only_curls():
    # same e3 at b3, but curl not until b6 (3 bars later, > grace) → grace lapsed,
    # so the late curl alone only reaches state 2, not 3.
    k    = [50, 10, 10, 10, 10, 10, 12]
    bb_M = [50,  8,  8, 11, 11, 11, 11]
    r = _bl().run(k=k, bb_m=[50]*7, bb_M=bb_M)
    assert list(r['state']) == [0, 1, 1, 1, 1, 1, 2]
