"""Risk (SRP: assess account/market state → a RiskVerdict; it COMPUTES, it does not decide/size/execute).

RiskGovernor reads risk_config (DB — no literals of its own) and maps state → RiskVerdict. RiskGate applies
that verdict to the intent stream: vetoes new opens/adds under stress or at the exposure cap, and exposes the
effective per-order leverage for the sizer. The StrategyLoop still DECIDES and the PositionSizer still SIZES —
this layer only computes risk and feeds it. Config is the single 'dial up as we learn' surface (base_appetite).
Thresholds are v2_walk-grounded (dd steps = its drawdown p90/p95; cap = its stack p99). See
docs/dynamic_risk_spec.md.

CLOSE/REDUCE intents are NEVER gated — you must always be able to exit.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RiskVerdict:
    leverage: float            # effective per-order leverage the sizer should use (base_leverage × factor × appetite)
    open_allowed: bool         # may open a new leg?
    add_allowed: bool          # may pyramid an existing leg?
    max_exposure: float        # gross exposure cap (× equity) — the gate basis + informational
    reason: str = "ok"         # audit: ok | cap | halt_dd


class RiskGovernor:
    """Reads risk_config once (cache); assess() maps state → verdict. No trading logic, no side effects."""

    def __init__(self, db=None, cache=None):
        self._cfg = cache if cache is not None else self._load(db)

    @staticmethod
    def _load(db) -> dict:
        rows = db.execute("SELECT name, val FROM risk_config", fetch=True) or []
        return {r["name"]: r["val"] for r in rows}

    def _f(self, name, default):
        v = self._cfg.get(name)
        return float(v) if v is not None else float(default)

    def assess(self, equity, drawdown_pct, vol_pctile, open_exposure_mult) -> RiskVerdict:
        """state → verdict.
        drawdown_pct       — % below high-water (realized + open-leg MtM; dd_ref=hwm_mtm)
        vol_pctile         — 0..100 rank of the s30 band width over vol_window
        open_exposure_mult — current gross exposure as a multiple of equity"""
        base_lev = self._f("base_leverage", 5.0)
        appetite = self._f("base_appetite", 1.0)
        max_exp = self._f("max_exposure_mult", 16.0)

        halt = drawdown_pct >= self._f("dd_halt_pct", 10.0)
        if halt:
            f = 0.0
        elif drawdown_pct >= self._f("dd_step2_pct", 3.5):
            f = self._f("dd_step2_factor", 0.25)
        elif drawdown_pct >= self._f("dd_step1_pct", 2.0):
            f = self._f("dd_step1_factor", 0.5)
        else:
            f = 1.0
        if vol_pctile >= self._f("vol_hi_pctile", 80.0):          # high vol → taper (whichever is tighter)
            f = min(f, self._f("vol_hi_factor", 0.5))

        leverage = base_lev * f * appetite
        over_cap = open_exposure_mult >= max_exp
        return RiskVerdict(
            leverage=round(leverage, 4),
            open_allowed=not halt,
            add_allowed=(not halt) and (not over_cap),
            max_exposure=max_exp,
            reason="halt_dd" if halt else ("cap" if over_cap else "ok"))


class RiskGate:
    """Applies a RiskVerdict to the intent stream (SRP: gate only — never sizes or decides). Drops vetoed
    opens/adds; closes & reduces always pass. `add_mode=taper` means adds still flow but at the reduced
    leverage (the sizer reads verdict.leverage); the hard veto is the cap / dd-halt."""

    @staticmethod
    def apply(verdict: RiskVerdict, intents: list) -> list:
        out = []
        for it in intents:
            if it.action == "add" and not verdict.add_allowed:
                continue
            if it.action == "open" and not verdict.open_allowed:
                continue
            out.append(it)                                        # close/reduce always survive
        return out
