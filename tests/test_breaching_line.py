"""
Behaviour-by-example for breaching_line (Target-1 DoD). Spec: bl_machine_design.md.
predict_breach pinned by Joe's worked examples; exit methods + the 0→1→2→3→0
lifecycle pinned on hand-built synthetic series.
"""
import numpy as np

from optimus9.compute.breaching_line import BreachingLine, predict_breach


# ── prediction (Joe's examples, HI=85, K=75) ────────────────────────────────
def test_predict_hi_joes_examples():
    # m=56/M=120 → anchor 120, 35>10 → True ;  m=56/M=90 → anchor 90, 5>10 → False
    pred = predict_breach(k=[75, 75], bb_m=[56, 56], bb_M=[120, 90])
    assert list(pred) == [1, 0]


def test_predict_lo_mirror():
    # k=20, anchor=min(5,44)=5 OOB-lo, (15-5)=10 > (20-15)=5 → True
    assert predict_breach(k=[20], bb_m=[5], bb_M=[44])[0] == -1


def test_fence_suppresses_prediction():
    # K=50 sits inside the 30:70 fence → never predicted even with a wild anchor
    assert predict_breach(k=[50], bb_m=[56], bb_M=[120])[0] == 0


def test_already_breached_is_not_predicted():
    # K>=85 is an ACTUAL breach (handled by sig), not a prediction
    assert predict_breach(k=[90], bb_m=[56], bb_M=[120])[0] == 0


# ── exit methods in isolation ───────────────────────────────────────────────
def _bl():
    return BreachingLine(curl_floor=1.0, pseudo_cross=15.0, flatten=0.5)


def test_exit3_cross_toward_ib():
    bl = _bl()
    # dir +1: BB above K cuts down through it
    assert bl._exit_cross_toward_ib(1, np.array([95., 80.]), np.array([84., 84.]), 1)
    # dir +1 pseudo: within 15 and converging down, not yet crossed
    assert bl._exit_cross_toward_ib(1, np.array([90., 86.]), np.array([84., 84.]), 1)
    # dir -1: BB below K cuts up through it
    assert bl._exit_cross_toward_ib(-1, np.array([5., 20.]), np.array([16., 16.]), 1)
    # no cross / diverging
    assert not bl._exit_cross_toward_ib(1, np.array([90., 92.]), np.array([84., 84.]), 1)


def test_exit2_nonsubtle_roc():
    bl = _bl()
    assert bl._exit_nonsubtle_roc(np.array([5., -3.]), 1)      # reversal
    assert bl._exit_nonsubtle_roc(np.array([5., 0.2]), 1)      # flatten
    assert not bl._exit_nonsubtle_roc(np.array([5., 4.]), 1)   # subtle → no


# ── full lifecycle 0→1→2→3→0 (exit1: BB OB→IB) ──────────────────────────────
def test_lifecycle_breach_curl_complete_reset():
    bl = _bl()
    #        b0   b1   b2   b3(curl) b4(BB IB→exit) b5(reset)
    k    = [50,  90,  90,  84,      84,            50]
    bb_M = [50,  50,  50,  90,      50,            50]     # OB at b3, IB at b4
    bb_m = [50,  50,  50,  50,      50,            50]
    r = bl.run(k, bb_m, bb_M)
    assert list(r['state']) == [0, 1, 1, 2, 3, 0]
    assert r['exit1'][4]                       # completed via BB OB→IB


def test_curl_is_mandatory():
    bl = _bl()
    # breaches and holds OOB but never curls (flat slope) → never leaves state 1
    r = bl.run(k=[50, 90, 90, 90, 90], bb_m=[50]*5, bb_M=[50]*5)
    assert list(r['state']) == [0, 1, 1, 1, 1]
    assert 2 not in r['state'] and 3 not in r['state']
