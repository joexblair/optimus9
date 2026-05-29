"""
Tests for optimus9.compute.pk_vote_machine.

Pure-math unit tests. PKVoteMachine takes probe_states / probe_weights
dicts and returns long_pts / short_pts / neutral_pts / ratios / pk_raw.
No DB, no file I/O, no fixtures from conftest required.

r07 Step 2 — vote machine extracted from Pk5sGateComputer. These tests
verify the math is identical to the inline code that used to live in
Pk5sGateComputer.compute() lines 165-211.
"""
import numpy as np
from optimus9 import PKVoteMachine


# Synthetic constants. Small bar counts keep tests fast and debuggable;
# we're testing math, not data scale.
_N = 10
_POOL_ID = 1  # tcev_pk equivalent; any int works


def _make_states(values: list) -> np.ndarray:
    """Build a state array of length _N from a list of values."""
    assert len(values) == _N, f'values must be length {_N}'
    return np.array(values, dtype=np.float64)


def test_divergence_routes_to_directional_buckets():
    """State +1 contributes to long_pts; state -1 contributes to short_pts."""
    vm = PKVoteMachine(pm_suppress_str=0.0)  # disable PM suppression to isolate
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 1, 1, 0, -1, -1, -1, 0, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # Bars 1,2,3: state=+1, weight=5 → long_pts=5, others 0
    assert out['long_pts'][1] == 5.0
    assert out['short_pts'][1] == 0.0
    assert out['neutral_pts'][1] == 0.0

    # Bars 5,6,7: state=-1, weight=5 → short_pts=5
    assert out['short_pts'][5] == 5.0
    assert out['long_pts'][5] == 0.0

    # Bars 0,4,8,9: state=0 → all goes to neutral
    assert out['neutral_pts'][0] == 5.0
    assert out['long_pts'][0] == 0.0
    assert out['short_pts'][0] == 0.0


def test_pm_sentinels_route_to_neutral_at_full_weight():
    """PM_LONG (+2) and PM_SHORT (-2) contribute to neutral_pts, NOT directional buckets."""
    vm = PKVoteMachine(pm_suppress_str=0.0)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 2, 2, 0, 0, -2, -2, 0, 0, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # Bars 1,2: PM_LONG → neutral gets the weight, long_pts stays 0
    assert out['neutral_pts'][1] == 5.0
    assert out['long_pts'][1] == 0.0
    assert out['short_pts'][1] == 0.0

    # Bars 5,6: PM_SHORT → same pattern, short_pts stays 0
    assert out['neutral_pts'][5] == 5.0
    assert out['short_pts'][5] == 0.0


def test_pm_suppression_dampens_opposing_direction():
    """PM_SHORT evidence reduces long_pts via adj_long calculation."""
    vm = PKVoteMachine(pm_suppress_str=0.4)
    # Two probes contributing simultaneously: divergence long + PM short
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 1, 1, 0, 0, 0, 0, 0, 0]),   # long divergence
        (_POOL_ID, 'wide'):  _make_states([0, -2, -2, -2, 0, 0, 0, 0, 0, 0]),  # PM short
    }
    probe_weights = {(_POOL_ID, 'close'): 5, (_POOL_ID, 'wide'): 5}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # Bar 1: long_pts=5 (from close probe), pm_short_wt=5 (from wide probe)
    # adj_long = max(0, 5 - 5*0.4) = max(0, 3.0) = 3.0
    # active_w = adj_long + adj_short + neutral_pts = 3.0 + 0 + 5 (from PM→neutral) = 8
    # long_ratio = (3.0 / 8.0) * 10 = 3.75
    assert out['long_pts'][1]  == 5.0
    assert out['short_pts'][1] == 0.0
    assert out['neutral_pts'][1] == 5.0    # PM_SHORT routed here at full weight
    assert abs(out['long_ratio'][1] - 3.75) < 1e-9


def test_pm_suppression_clamped_at_zero():
    """When suppression exceeds long_pts, adj_long floors at 0 (not negative)."""
    vm = PKVoteMachine(pm_suppress_str=1.0)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),     # long, weight 2
        (_POOL_ID, 'wide'):  _make_states([0, -2, 0, 0, 0, 0, 0, 0, 0, 0]),    # PM short, weight 10
    }
    probe_weights = {(_POOL_ID, 'close'): 2, (_POOL_ID, 'wide'): 10}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # long_pts=2, pm_short_wt=10 → 2 - 10*1.0 = -8 → clamped to 0
    # adj_long must be 0, not negative
    assert out['long_pts'][1] == 2.0
    assert out['long_ratio'][1] == 0.0
    assert out['pk_raw'][1] == 0


def test_pk_raw_fires_long_above_threshold():
    """When long_ratio exceeds threshold_long, pk_raw = +1."""
    vm = PKVoteMachine(pm_suppress_str=0.0)
    # All probes long, no opposing — should produce maximal long_ratio (10.0)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 1, 1, 1, 1, 1, 1, 1, 0]),
        (_POOL_ID, 'wide'):  _make_states([0, 1, 1, 1, 1, 1, 1, 1, 1, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5, (_POOL_ID, 'wide'): 3}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # Bar 1: long_pts=8, others 0, active_w=8, long_ratio=10.0
    assert abs(out['long_ratio'][1] - 10.0) < 1e-9
    assert out['pk_raw'][1] == 1


def test_pk_raw_fires_short_above_threshold():
    """When short_ratio exceeds threshold_short, pk_raw = -1."""
    vm = PKVoteMachine(pm_suppress_str=0.0)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, -1, -1, -1, 0, 0, 0, 0, 0, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # Bar 1: short_pts=5, active_w=5, short_ratio=10.0
    assert abs(out['short_ratio'][1] - 10.0) < 1e-9
    assert out['pk_raw'][1] == -1


def test_pk_raw_neutral_below_threshold():
    """Mixed votes below threshold produce pk_raw=0."""
    vm = PKVoteMachine(pm_suppress_str=0.0)
    # Equal long and short — ratios balance, both below threshold
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        (_POOL_ID, 'wide'):  _make_states([0, -1, 0, 0, 0, 0, 0, 0, 0, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5, (_POOL_ID, 'wide'): 5}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=7.0, threshold_short=7.0)

    # long_pts=5, short_pts=5, active_w=10. ratios = 5.0 each, below 7.0.
    assert out['long_ratio'][1] == 5.0
    assert out['short_ratio'][1] == 5.0
    assert out['pk_raw'][1] == 0


def test_zero_weight_probe_contributes_nothing():
    """Probes with weight=0 are skipped — same result as omitting them."""
    vm = PKVoteMachine(pm_suppress_str=0.0)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        (_POOL_ID, 'wide'):  _make_states([0, -1, 0, 0, 0, 0, 0, 0, 0, 0]),  # zero-weighted
    }
    probe_weights = {(_POOL_ID, 'close'): 5, (_POOL_ID, 'wide'): 0}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # Only close probe contributes. short_pts must be 0.
    assert out['short_pts'][1] == 0.0
    assert out['long_pts'][1] == 5.0


def test_zero_active_weight_produces_zero_ratios():
    """When no probes contribute, ratios = 0 (no division-by-zero)."""
    vm = PKVoteMachine(pm_suppress_str=0.0)
    # All states 0 → all weight goes to neutral → active_w > 0 but adj_long=0
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0] * _N),
    }
    probe_weights = {(_POOL_ID, 'close'): 5}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # neutral=5, active_w=5, long_ratio=0/5*10=0
    assert out['long_ratio'][1] == 0.0
    assert out['short_ratio'][1] == 0.0
    assert out['pk_raw'][1] == 0


def test_multi_pool_aggregation():
    """Probes from multiple pools (multi-line SnF shape) accumulate correctly."""
    vm = PKVoteMachine(pm_suppress_str=0.0)
    probe_states = {
        (1, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        (1, 'wide'):  _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        (2, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        (2, 'wide'):  _make_states([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    }
    probe_weights = {
        (1, 'close'): 5, (1, 'wide'): 3,
        (2, 'close'): 4, (2, 'wide'): 2,
    }
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)

    # Bar 1: long contributions = 5 + 3 + 4 = 12
    #        neutral = 2 (pool 2 wide is state=0)
    #        active_w = 12 + 0 + 2 = 14
    #        long_ratio = 12/14 * 10 = 8.571...
    assert out['long_pts'][1] == 12.0
    assert out['neutral_pts'][1] == 2.0
    assert abs(out['long_ratio'][1] - (12.0 / 14.0 * 10.0)) < 1e-9
    assert out['pk_raw'][1] == 1  # 8.57 > 5.0 threshold


def test_pm_option_a_changes_active_w():
    """pm_option_a=True uses raw long/short_pts in denominator (Pine variant)."""
    vm_false = PKVoteMachine(pm_suppress_str=0.5, pm_option_a=False)
    vm_true  = PKVoteMachine(pm_suppress_str=0.5, pm_option_a=True)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        (_POOL_ID, 'wide'):  _make_states([0, -2, 0, 0, 0, 0, 0, 0, 0, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5, (_POOL_ID, 'wide'): 5}

    out_false = vm_false.aggregate(probe_states, probe_weights, 5.0, 5.0)
    out_true  = vm_true.aggregate(probe_states, probe_weights, 5.0, 5.0)

    # long_pts=5, pm_short_wt=5, adj_long = 5 - 5*0.5 = 2.5
    # neutral_pts = 5 (from PM_SHORT)
    #
    # pm_option_a=False: active_w = 2.5 + 0 + 5 = 7.5
    # long_ratio = 2.5/7.5 * 10 = 3.333...
    #
    # pm_option_a=True:  active_w = 5 + 0 + 5 = 10 (raw, not adjusted)
    # long_ratio = 2.5/10 * 10 = 2.5
    assert abs(out_false['long_ratio'][1] - (2.5 / 7.5 * 10.0)) < 1e-9
    assert abs(out_true['long_ratio'][1]  - 2.5) < 1e-9


def test_control_voter_weight_adds_to_denominator_only():
    """Control voter inflates active_w without contributing to any directional bucket."""
    vm_no_control   = PKVoteMachine(pm_suppress_str=0.0, control_voter_weight=0)
    vm_with_control = PKVoteMachine(pm_suppress_str=0.0, control_voter_weight=3)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5}

    out_no   = vm_no_control.aggregate(probe_states, probe_weights, 5.0, 5.0)
    out_with = vm_with_control.aggregate(probe_states, probe_weights, 5.0, 5.0)

    # No control: long_pts=5, active_w=5, ratio=10.0
    # With control_voter_weight=3: long_pts=5, active_w=5+3=8, ratio=5/8*10=6.25
    assert abs(out_no['long_ratio'][1] - 10.0) < 1e-9
    assert abs(out_with['long_ratio'][1] - 6.25) < 1e-9


def test_empty_probe_states_raises():
    """Empty probe_states dict must raise — no n to infer."""
    import pytest
    vm = PKVoteMachine()
    with pytest.raises(ValueError, match='probe_states must be non-empty'):
        vm.aggregate({}, {}, threshold_long=5.0, threshold_short=5.0)


def test_aggregation_matches_inline_pk5s_math():
    """
    Regression test: vote-folding output must match the inline math
    that used to live in Pk5sGateComputer.compute() lines 165-211.

    This is the "if I broke the extraction, this catches it" test. The
    expected values were calculated by hand from the original code's
    algebra with these inputs:
      - 1 pool, 2 probes (close + wide)
      - close: state=+1 bars 1-3 (divergence long), weight=5
      - wide:  state=-2 bars 1-3 (PM short),       weight=2
      - pm_suppress_str = 0.4
      - thresholds = 5.0 / 5.0

    Bar 1 expected:
      long_pts    = 5 (close +1, weight 5)
      short_pts   = 0
      neutral_pts = 2 (wide PM_SHORT → neutral at weight 2)
      pm_short_wt = 2
      adj_long    = max(0, 5 - 2*0.4) = 4.2
      adj_short   = 0
      active_w    = 4.2 + 0 + 2 = 6.2
      long_ratio  = 4.2/6.2 * 10 = 6.7741935...
      pk_raw      = +1 (6.77 > 5.0)
    """
    vm = PKVoteMachine(pm_suppress_str=0.4)
    probe_states = {
        (1, 'close'): _make_states([0, 1, 1, 1, 0, 0, 0, 0, 0, 0]),
        (1, 'wide'):  _make_states([0, -2, -2, -2, 0, 0, 0, 0, 0, 0]),
    }
    probe_weights = {(1, 'close'): 5, (1, 'wide'): 2}
    out = vm.aggregate(probe_states, probe_weights, 5.0, 5.0)

    # Bar 1 detailed check
    assert out['long_pts'][1]    == 5.0
    assert out['short_pts'][1]   == 0.0
    assert out['neutral_pts'][1] == 2.0

    expected_long_ratio = (4.2 / 6.2) * 10.0
    assert abs(out['long_ratio'][1] - expected_long_ratio) < 1e-9
    assert out['pk_raw'][1] == 1


# ── r07 Step 4: pm_additive_str ─────────────────────────────────────────

def test_pm_additive_default_zero_is_inert():
    """Default pm_additive_str=0.0 — PM probes route only to neutral (Step 3 behavior)."""
    vm = PKVoteMachine(pm_suppress_str=0.0)  # pm_additive_str defaults 0.0
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 2, 2, 0, 0, -2, -2, 0, 0, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)
    # PM_LONG → neutral only, long_pts stays 0
    assert out['neutral_pts'][1] == 5.0
    assert out['long_pts'][1]    == 0.0
    assert out['short_pts'][1]   == 0.0
    # PM_SHORT → neutral only, short_pts stays 0
    assert out['neutral_pts'][5] == 5.0
    assert out['short_pts'][5]   == 0.0
    assert out['long_pts'][5]    == 0.0


def test_pm_additive_single_dial_covers_close_and_wide():
    """pm_additive_str > 0 — one dial scales PM contribution from both close and wide probes."""
    vm = PKVoteMachine(pm_suppress_str=0.0, pm_additive_str=0.4)
    probe_states = {
        (_POOL_ID, 'close'): _make_states([0, 2, 2, 0, 0, -2, -2, 0, 0, 0]),
        (_POOL_ID, 'wide'):  _make_states([0, 0, 0, 2, 2,  0,  0, -2, -2, 0]),
    }
    probe_weights = {(_POOL_ID, 'close'): 5, (_POOL_ID, 'wide'): 3}
    out = vm.aggregate(probe_states, probe_weights,
                       threshold_long=5.0, threshold_short=5.0)
    # close PM_LONG (bar 1): close adds 5×0.4=2.0 to long_pts; wide=0 contributes nothing
    assert out['long_pts'][1] == 2.0
    # wide PM_LONG (bar 3): wide adds 3×0.4=1.2 to long_pts (SAME single dial as close)
    assert abs(out['long_pts'][3] - 1.2) < 1e-9
    # close PM_SHORT (bar 5): close adds 5×0.4=2.0 to short_pts
    assert out['short_pts'][5] == 2.0
    # wide PM_SHORT (bar 7): wide adds 3×0.4=1.2 to short_pts
    assert abs(out['short_pts'][7] - 1.2) < 1e-9
    # Neutral routing unchanged: PM at full weight + state-0 at full weight,
    # so both probes contribute their full weight to neutral_pts on every bar.
    assert out['neutral_pts'][1] == 8.0   # close PM_LONG (5) + wide N (3)
    assert out['neutral_pts'][3] == 8.0   # close N (5)        + wide PM_LONG (3)
    assert out['neutral_pts'][5] == 8.0   # close PM_SHORT (5) + wide N (3)
    assert out['neutral_pts'][7] == 8.0   # close N (5)        + wide PM_SHORT (3)


def test_pm_additive_with_suppression_worked_example():
    """
    r07 Step 4 worked example — additive + suppression + divergence interaction.

    Inputs (bar 1):
      - close probe: divergence long (+1, weight 5)
      - wide probe:  PM short        (-2, weight 5)
      - pm_suppress_str = 0.4
      - pm_additive_str = 0.5

    Hand-calculated:
      long_pts    = 5             (close +1)
      short_pts   = 5 × 0.5 = 2.5  (wide PM_SHORT additive)
      neutral_pts = 5             (wide PM_SHORT → neutral full weight)
      pm_short_wt = 5             (suppression evidence)
      adj_long    = max(0, 5 - 5×0.4) = 3.0
      adj_short   = max(0, 2.5 - 0)   = 2.5
      active_w    = 3.0 + 2.5 + 5 = 10.5
      long_ratio  = 3.0 / 10.5 × 10 ≈ 2.857
      short_ratio = 2.5 / 10.5 × 10 ≈ 2.381
      pk_raw      = 0 (both ratios under 5.0)
    """
    vm = PKVoteMachine(pm_suppress_str=0.4, pm_additive_str=0.5)
    probe_states = {
        (1, 'close'): _make_states([0, 1, 0, 0, 0, 0, 0, 0, 0, 0]),
        (1, 'wide'):  _make_states([0, -2, 0, 0, 0, 0, 0, 0, 0, 0]),
    }
    probe_weights = {(1, 'close'): 5, (1, 'wide'): 5}
    out = vm.aggregate(probe_states, probe_weights, 5.0, 5.0)

    assert out['long_pts'][1]    == 5.0
    assert out['short_pts'][1]   == 2.5
    assert out['neutral_pts'][1] == 5.0

    expected_long_ratio  = (3.0 / 10.5) * 10.0
    expected_short_ratio = (2.5 / 10.5) * 10.0
    assert abs(out['long_ratio'][1]  - expected_long_ratio)  < 1e-9
    assert abs(out['short_ratio'][1] - expected_short_ratio) < 1e-9
    assert out['pk_raw'][1] == 0
