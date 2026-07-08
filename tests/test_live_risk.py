"""RiskGovernor + RiskGate — verdict from state (v2_walk-grounded thresholds) and gating of the intent stream.
Cache-injected config (no DB). Mirrors the seeded risk_config defaults."""
import sys

sys.path.insert(0, "/home/joe/thecodes")
from optimus9.live.risk import RiskGovernor, RiskGate, RiskVerdict
from optimus9.live.sizing import TradeIntent

CFG = {"base_leverage": "5.0", "base_appetite": "1.0", "max_exposure_mult": "16.0",
       "dd_step1_pct": "2.0", "dd_step1_factor": "0.5", "dd_step2_pct": "3.5", "dd_step2_factor": "0.25",
       "dd_halt_pct": "10.0", "vol_hi_pctile": "80", "vol_hi_factor": "0.5"}


def gov():
    return RiskGovernor(cache=CFG)


def test_normal_full_leverage():
    v = gov().assess(equity=500, drawdown_pct=0.0, vol_pctile=50, open_exposure_mult=3.0)
    assert v.leverage == 5.0 and v.open_allowed and v.add_allowed and v.reason == "ok"


def test_drawdown_steps_deleverage():
    assert gov().assess(500, 2.5, 50, 3).leverage == 2.5      # >p90 → x0.5
    assert gov().assess(500, 4.0, 50, 3).leverage == 1.25     # >p95 → x0.25


def test_halt_zeros_leverage_and_vetoes_new_risk():
    v = gov().assess(500, 11.0, 50, 3)
    assert v.leverage == 0.0 and not v.open_allowed and not v.add_allowed and v.reason == "halt_dd"


def test_high_vol_tapers():
    v = gov().assess(500, 0.0, 85, 3)                          # calm dd, high vol
    assert v.leverage == 2.5                                   # base 5 × vol 0.5


def test_exposure_cap_vetoes_adds_only():
    v = gov().assess(500, 0.0, 50, open_exposure_mult=16.0)    # at cap
    assert v.add_allowed is False and v.open_allowed is True and v.reason == "cap"


def test_appetite_scales_whole_curve():
    v = RiskGovernor(cache={**CFG, "base_appetite": "1.5"}).assess(500, 0.0, 50, 3)
    assert v.leverage == 7.5                                   # 5 × 1.5


def test_gate_vetoes_adds_but_never_closes():
    v = RiskVerdict(leverage=0.0, open_allowed=False, add_allowed=False, max_exposure=16.0, reason="halt_dd")
    intents = [TradeIntent("open", side="Buy"), TradeIntent("add", side="Buy"),
               TradeIntent("close", side="Sell"), TradeIntent("reduce", side="Sell")]
    kept = [i.action for i in RiskGate.apply(v, intents)]
    assert kept == ["close", "reduce"]                        # opens/adds vetoed, exits survive


def test_gate_taper_keeps_adds_when_allowed():
    v = RiskVerdict(leverage=1.25, open_allowed=True, add_allowed=True, max_exposure=16.0)
    intents = [TradeIntent("add", side="Buy"), TradeIntent("open", side="Sell")]
    assert len(RiskGate.apply(v, intents)) == 2
