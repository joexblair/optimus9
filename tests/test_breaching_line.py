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
    assert list(predict_breach(k=[75, 75], predictor_min_bb=[56, 56], predictor_maj_bb=[120, 90])) == [1, 0]


def test_predict_lo_mirror():
    assert predict_breach(k=[20], predictor_min_bb=[5], predictor_maj_bb=[44])[0] == -1


def test_fence_suppresses_prediction():
    assert predict_breach(k=[50], predictor_min_bb=[56], predictor_maj_bb=[120])[0] == 0


def test_already_breached_is_not_predicted():
    assert predict_breach(k=[90], predictor_min_bb=[56], predictor_maj_bb=[120])[0] == 0


# ── exit methods in isolation ───────────────────────────────────────────────
def _bl(**kw):
    # curl_lookback=1 so the short synthetic series exercise the curl on a 1-bar slope
    return BreachingLine(curl_floor=1.0, curl_lookback=1, pseudo_cross=15.0, **kw)


def test_exit3_cross_toward_ib():
    bl = _bl()
    assert bl._exit_cross_toward_ib(1, np.array([95., 80.]), np.array([84., 84.]), 1)
    assert bl._exit_cross_toward_ib(1, np.array([90., 86.]), np.array([84., 84.]), 1)   # pseudo
    assert bl._exit_cross_toward_ib(-1, np.array([5., 20.]), np.array([16., 16.]), 1)
    assert not bl._exit_cross_toward_ib(1, np.array([90., 92.]), np.array([84., 84.]), 1)


def test_exit2_fires_when_k_reverses_past_anchor():
    # hi breach: K peaks 95 (ref settles at k[1]=88); K curls (b3) then falls to 86 —
    # past the 88 ref but still OOB (>85) — so exit2 completes before K returns IB.
    r = _bl().run(k=[50, 88, 95, 92, 86], predictor_min_bb=[50]*5, predictor_maj_bb=[50]*5)
    assert list(r['state']) == [0, 1, 1, 2, 3]
    assert r['exit2'][4]


def test_exit2_silent_on_shallow_pullback():
    # K peaks 90 then only dips to 89 — never back past the anchor (86), so exit2
    # stays quiet and the journey never completes (the 16267 false-complete).
    r = _bl().run(k=[50, 86, 90, 89, 89], predictor_min_bb=[50]*5, predictor_maj_bb=[50]*5)
    assert not any(r['exit2'])
    assert 3 not in list(r['state'])


def test_exit_mask_disables_exit2():
    # mask 5 = exit1(1) + exit3(4), exit2(2) OFF. The K-reversal series that completes
    # via exit2 under the default mask now stalls at state 2 — the raw condition is
    # still recorded, just not actioned.
    r = _bl(exit_mask=5).run(k=[50, 88, 95, 92, 86], predictor_min_bb=[50]*5, predictor_maj_bb=[50]*5)
    assert list(r['state']) == [0, 1, 1, 2, 2]
    assert r['exit2'][4]


def test_exit2_ref_taken_at_tf9_seam():
    # Seams every 3 bars; bl_line peaks 92 in TF9 bar B (b3-5). The ref is the bl_line
    # just before B's seam — k[2]=88 ("1 TF9 bar before max"), NOT k[3]=90 (1 5s bar).
    # bl_line then dips to 89: above the TF9 ref (88) so exit2 stays silent; a 5s
    # ref (90) would have wrongly fired.
    seam = [True, False, False, True, False, False, True, False, False]
    k    = [50,   86,    88,    90,   92,    91,    89,   89,    89]
    r = _bl().run(k=k, predictor_min_bb=[50]*9, predictor_maj_bb=[50]*9, seam=seam)
    assert r['exit2_ref'][4] == 88
    assert not any(r['exit2'])


def test_exit2_ref_does_not_reach_pre_breach():
    # The re-breach flaw: on a FRESH breach the seam-walk must not borrow structure
    # from before the breach. Two TF9 cycles of pre-breach history, then a fresh lo
    # breach at the bar-9 seam. 'prior' must NOT reach a 2-seams-back value (→ NaN);
    # 'now' pins to the breach-edge bl_line (k[8]=58), with idx 8 for exit2_ref_dt.
    seam = [True, False, False, True, False, False, True, False, False, True, False, False]
    k    = [50,   51,    52,    53,   54,    55,    56,   57,    58,    10,   9,     9]
    rp = _bl(exit2_ref='prior').run(k=k, predictor_min_bb=[50]*12, predictor_maj_bb=[50]*12, seam=seam)
    assert np.isnan(rp['exit2_ref'][9])               # did not reach pre-breach structure
    rn = _bl(exit2_ref='now').run(k=k, predictor_min_bb=[50]*12, predictor_maj_bb=[50]*12, seam=seam)
    assert rn['exit2_ref'][9] == 58                   # breach-edge bl_line
    assert rn['exit2_ref_idx'][9] == 8                # provenance for exit2_ref_dt


# ── dormancy model ──────────────────────────────────────────────────────────
def test_fence_forces_state_0():
    # breached, then K returns to the 30:70 dead zone → dormant (state 0)
    r = _bl().run(k=[90, 50], predictor_min_bb=[50, 50], predictor_maj_bb=[50, 50])
    assert list(r['state']) == [1, 0]


def test_ib_cross_resets_to_0():
    # OOB→IB rule: a breached line (90) that crosses back inside the boundary (84 IB,
    # still outside the 30:70 fence) flips to bls0 — the breach is over, machine re-arms
    # from idle. (Supersedes the old "curl gated to OOB keeps it at 1": IB → 0 now.)
    r = _bl().run(k=[50, 90, 84], predictor_min_bb=[50]*3, predictor_maj_bb=[50]*3)
    assert list(r['state']) == [0, 1, 0]


def test_exit1_bypasses_curl():
    # hi breach pegged high (90,90,90 — never curls); the BB (hb9M) was OOB then crosses
    # IB at b3 → exit1 completes straight from state 1, no mandatory curl.
    r = _bl().run(k=[50, 90, 90, 90], predictor_min_bb=[50]*4, predictor_maj_bb=[50, 90, 90, 50])
    assert list(r['state']) == [0, 1, 1, 3]
    assert r['exit1'][3]


def test_exit1_completes_same_bar_as_breach():
    # the exit_lookback window lets a line breach and flip to bls3 in ONE bar when the
    # BB has already crossed IB: at b1 K breaches (90) and hb9M is already IB (50) after
    # being OOB (90) within lookback → bls0→bls1→bls3 same bar.
    r = _bl().run(k=[50, 90], predictor_min_bb=[50, 50], predictor_maj_bb=[90, 50])
    assert list(r['state']) == [0, 3]
    assert r['exit1'][1]


def test_run_bb_oob_to_ib():
    # BB-type breach (run_bb): OOB → bls1, return IB → bls3 (the only exit), reset → 0.
    # No curl, no support — just the line crossing the boundary and back.
    r = _bl(exit_mask=1).run_bb(line=[50, 90, 92, 80, 80])
    assert list(r['state']) == [0, 1, 1, 3, 0]
    assert r['exit1'][3] and not r['exit1'][4]
    assert r['breach_dir'][1] == 1                     # hi breach
    # mask without exit1 → IB just resets (no bls3 completion)
    r0 = _bl(exit_mask=0).run_bb(line=[50, 90, 80])
    assert list(r0['state']) == [0, 1, 0]
    assert not any(r0['exit1'])


def test_lifecycle_dwell_at_2_then_complete():
    #        b0    b1    b2    b3(curl→2)  b4(BB OB→IB exit→3)
    r = _bl().run(k=[50, 90, 90, 86, 86], predictor_min_bb=[50]*5, predictor_maj_bb=[50, 50, 50, 90, 50])
    assert list(r['state']) == [0, 1, 1, 2, 3]


def test_cascade_1_2_3_one_bar():
    # curl AND a BB OB→IB exit on the same bar → straight to 3 (through 2)
    r = _bl().run(k=[50, 90, 90, 86], predictor_min_bb=[50]*4, predictor_maj_bb=[50, 90, 90, 50])
    assert list(r['state']) == [0, 1, 1, 3]


def test_pegged_stays_dormant_until_fresh_breach():
    #          b0  b1  b2  b3(→3) b4  b5  b6(IB)  b7(re-breach)
    k    = [50, 90, 90, 86,   90, 90, 84,    90]
    bb_M = [50, 90, 90, 50,   50, 50, 50,    50]
    r = _bl().run(k=k, predictor_min_bb=[50]*8, predictor_maj_bb=bb_M)
    assert r['state'][3] == 3            # completed
    assert r['state'][4] == 3            # still OOB but pegged → no bobbing, stays 3
    assert r['state'][7] == 1            # IB then OOB again = fresh breach → re-armed


# ── exit2/3 complete WITHOUT the curl (Joe, 2026-06-14: curl is a bane) ──
# The old exit3-before-curl `grace` contract is gone — a cross IS the reversal, so any
# enabled exit completes a breach directly from state 1.
def test_exit3_completes_from_state1_without_curl():
    # lo breach; e3 fires at b3 (bb_M crosses up through k) → completes directly at b3,
    # no curl/grace wait. (Was [0,1,1,1,3] under the old grace contract.)
    k    = [50, 10, 10, 10, 12]
    bb_M = [50,  8,  8, 11, 11]
    r = _bl().run(k=k, predictor_min_bb=[50]*5, predictor_maj_bb=bb_M)
    assert list(r['state']) == [0, 1, 1, 3, 3]


def test_exit3_completes_with_no_curl_at_all():
    # e3 at b3, no curl ever (k stays pegged). Old grace contract → only curled to 2;
    # now the cross completes at b3 regardless of the curl. (Was [0,1,1,1,1,1,2].)
    k    = [50, 10, 10, 10, 10, 10, 12]
    bb_M = [50,  8,  8, 11, 11, 11, 11]
    r = _bl().run(k=k, predictor_min_bb=[50]*7, predictor_maj_bb=bb_M)
    assert list(r['state']) == [0, 1, 1, 3, 3, 3, 3]
