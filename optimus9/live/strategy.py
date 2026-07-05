"""StrategyLoop — DECIDE (SRP: bar T's action, nothing about sizing or execution).

Stateless by design: each closed 5s bar, run the SAME backtest producer on a bounded window ending
at now, and read ONLY the latest bar. Window-ending-at-now == the backtest window → live == backtest
by construction; no latch state to desync, self-healing every bar. Side convention (verified vs
build_v2_walk): bd +1 = Buy/long, bd -1 = Sell/short; a close uses the opposite side.

Emits TradeIntent(s); never touches the exchange. Position is passed IN (read from the ledger/exchange):
None, or {'side': 'Buy'|'Sell', 'size': float}.
"""
from __future__ import annotations

import bias_machine as bm
from optimus9.analysis.lr_v2 import v2_walk, v2_walk_ad, lr_exit_v2, strand_rescue, v2_phase, v2_state_mask
from optimus9.live.sizing import TradeIntent

_SIDE = {1: "Buy", -1: "Sell"}
_SIDE_N = {"Buy": 1, "Sell": -1}


class StrategyLoop:
    def __init__(self, db, bias_cfg, lr_cfg, symbol, buffer_hours=24, warmup_hours=80,
                 predict=False, gate_fam="s7", producer=v2_walk_ad):
        self._db = db
        self._bias = bias_cfg             # BiasConfig — for BiasWindow (lines)
        self._lr = lr_cfg                 # LRConfig  — for the v2 cascade producer
        self._sym = symbol
        self._buf = buffer_hours          # bounded window; must reproduce the backtest line values (pin by measure)
        self._warm = warmup_hours
        self._predict = predict
        self._gate_fam = gate_fam
        self._producer = producer         # entries producer (W,cfg)->entries — DATA (Joe 0704): v2_walk_ad (arm-delay,
        #                                   the shipping stack) or v2_walk. NEVER baked; the loop consumes the stream.
        self._cascade = db.execute("SELECT state,bit,active FROM cascade_state", fetch=True) or []   # UI-grid registry (cached)

    def window(self, now_ms: int):
        """Build the bounded window ending at now (the shared input to intents + phase — build ONCE per bar)."""
        return bm.BiasWindow(self._db, now_ms, lookback=self._buf, warmup=self._warm, cfg=self._bias, lean=True)

    def phase(self, W, position: dict | None) -> dict:
        """Live cascade readout at bar T (SRP: reports, never trades). in_position from the live net side."""
        side = _SIDE_N.get(position["side"], 0) if position else 0
        return v2_phase(W, self._lr, in_position=side, exit_fam=self._gate_fam)

    def state_mask(self, W):
        """Cascade-state mask at bar T for the UI mirror-grids (SRP: reports, never trades). (mask, es, armed)."""
        return v2_state_mask(W, self._lr, self._cascade)

    def decide(self, now_ms: int, position: dict | None) -> list[TradeIntent]:
        """Compat entry: build the window and return this bar's intents (callers that don't need the phase)."""
        return self.intents(self.window(now_ms), position)

    def intents(self, W, position: dict | None, legs: list | None = None) -> list[TradeIntent]:
        """Option B exit model (Joe 0705): the pyramid stack shares ONE take-profit (the s7r-reversal cascade
        closes all legs together), but each leg carries its OWN stop-loss (per-leg −sl% from its own entry, so
        every leg gets a fighting chance to clear its MAE hump). `legs` = O9Ledger.open_legs() (per-leg entries)."""
        ent = self._producer(W, self._lr)
        T = int(W.ts[-1])                 # the just-closed bar
        out: list[TradeIntent] = []

        # Exit walk only read here → compute ONLY when holding (skipped when flat, most bars).
        if position:
            exits = strand_rescue(W, self._lr, ent,
                                  lr_exit_v2(W, self._lr, ent, predict=self._predict, gate_fam=self._gate_fam))
            # SHARED take-profit: a REAL reversal exit ('exit'/'strand') for the held side at T → close the WHOLE
            # stack. ('end' is lr_exit_v2's backtest window-boundary sentinel = ALWAYS T live → never an exit;
            # 'SL' is now per-leg below, NOT a stack-wide close.)
            if any(x[1] == T and x[6] in ("exit", "strand") and _SIDE[x[2]] == position["side"] for x in exits):
                close_side = "Sell" if position["side"] == "Buy" else "Buy"
                out.append(TradeIntent("close", side=close_side, qty=float(position["size"]), reason="exit", ts=T))
            elif legs:
                # PER-LEG stop-loss: each leg closes at its OWN −sl% from its OWN entry (partial close of that leg).
                px_T = float(W.px[-1]); sl = float(self._lr.sl)
                for lg in legs:
                    entry = float(lg["entry_px"]); d = 1.0 if lg["side"] == "Buy" else -1.0
                    if (px_T - entry) / entry * 100.0 * d <= -sl:
                        close_side = "Sell" if lg["side"] == "Buy" else "Buy"
                        out.append(TradeIntent("close", side=close_side, qty=float(lg["qty"]),
                                               reason="SL", ts=T, led_id=int(lg["led_id"])))

        # a new entry printed on bar T → open (flat) or add (same-side pyramid)
        for e in ent:
            if e[0] == T:
                side = _SIDE[e[2]]
                if position is None:
                    out.append(TradeIntent("open", side=side, reason="entry", ts=T))
                elif position["side"] == side:
                    out.append(TradeIntent("add", side=side, reason="pyramid", ts=T))
        return out
