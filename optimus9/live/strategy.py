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
from optimus9.analysis.lr_v2 import (v2_walk, v2_walk_ad, lr_exit_v2, strand_rescue, v2_phase, v2_state_mask,
                                     cascade_substrate, v2_mech_events)
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

    def phase(self, W, positions: dict | None) -> dict:
        """Live cascade readout at bar T (SRP: reports, never trades). in_position: single side if only one
        leg open, else 0 (flat or hedged both-sides — the readout has no single side)."""
        sides = list(positions) if positions else []
        side = _SIDE_N[sides[0]] if len(sides) == 1 else 0
        return v2_phase(W, self._lr, in_position=side, exit_fam=self._gate_fam)

    def state_mask(self, W, since_ms=0):
        """Cascade-state mask at bar T for the UI mirror-grids (SRP: reports, never trades). (mask, es, armed).
        since_ms → the 3 latch states close on a trade (troubleshooting test — readout only)."""
        return v2_state_mask(W, self._lr, self._cascade, since_ms=since_ms)

    def substrate(self, W):
        """Agnostic PURE cascade substrate at bar T for the state-log (SRP: reports deterministic facts, both
        sides, es-free). Cannot diverge from the producer — the honest layer of the event log."""
        return cascade_substrate(W, self._lr)

    def mech_events(self, W):
        """Producer-truth mechanism OCCURRENCES at bar T (arm/gate/rtr/stale/trade) from v2_cascade — the SAME
        chain as the entries, per-arm (no thrash). Completes 'every board cell' alongside substrate()."""
        return v2_mech_events(W, self._lr)

    def decide(self, now_ms: int, position: dict | None = None) -> list[TradeIntent]:
        """Compat entry: build the window and return this bar's intents. Accepts the legacy single-position
        dict ({'side','size'}) and normalises it to the hedge per-side shape."""
        positions = {position["side"]: position} if position else {}
        return self.intents(self.window(now_ms), positions)

    def intents(self, W, positions: dict | None, legs: list | None = None) -> list[TradeIntent]:
        """Hedge model: each side (Buy/Sell) is an INDEPENDENT one-way machine — it opens/pyramids its own
        leg, shares ONE reversal take-profit for that leg's stack (s7r cascade closes that side together), and
        each leg carries its OWN −sl% stop (option B, Joe 0705). `positions` = {side: {'side','size'}} (empty =
        flat both sides); `legs` = O9Ledger.open_legs() (all open legs, both sides). This is what realises the
        backtest's overlapping opposite-side legs (the hedge premium) — opposite entries are no longer dropped."""
        positions = positions or {}
        ent = self._producer(W, self._lr)
        T = int(W.ts[-1])                 # the just-closed bar
        out: list[TradeIntent] = []

        # Exit walk read once → only when at least one side is held (skipped when fully flat, most bars).
        exits = strand_rescue(W, self._lr, ent,
                              lr_exit_v2(W, self._lr, ent, predict=self._predict, gate_fam=self._gate_fam)) if positions else []
        px_T = float(W.px[-1]); sl = float(self._lr.sl)

        for side in ("Buy", "Sell"):
            pos_s = positions.get(side)
            legs_s = [lg for lg in (legs or []) if lg["side"] == side]
            if pos_s:
                # SHARED take-profit: a REAL reversal exit ('exit'/'strand') for THIS side at T → close this
                # side's WHOLE stack. ('end' is lr_exit_v2's window-boundary sentinel = always T live → never
                # an exit; 'SL' is per-leg below, NOT a stack-wide close.)
                if any(x[1] == T and x[6] in ("exit", "strand") and _SIDE[x[2]] == side for x in exits):
                    close_side = "Sell" if side == "Buy" else "Buy"
                    out.append(TradeIntent("close", side=close_side, qty=float(pos_s["size"]), reason="exit", ts=T))
                else:
                    # PER-LEG stop-loss on THIS side's legs (each closes at its own −sl% from its own entry).
                    d = 1.0 if side == "Buy" else -1.0
                    for lg in legs_s:
                        entry = float(lg["entry_px"])
                        if (px_T - entry) / entry * 100.0 * d <= -sl:
                            close_side = "Sell" if side == "Buy" else "Buy"
                            out.append(TradeIntent("close", side=close_side, qty=float(lg["qty"]),
                                                   reason="SL", ts=T, led_id=int(lg["led_id"])))
            # a new entry printed on bar T for THIS side → open (flat on this side) or add (pyramid this side)
            for e in ent:
                if e[0] == T and _SIDE[e[2]] == side:
                    out.append(TradeIntent("open" if pos_s is None else "add", side=side,
                                           reason="entry" if pos_s is None else "pyramid", ts=T))
        return out
