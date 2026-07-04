"""O9LiveApp — the live loop orchestrator (SRP: wire decide→size→execute per bar; own nothing else).

Collector-triggered: each closed 5s bar (at seam+301ms) calls `on_bar(now_ms, price)`. It reads the
current position FROM THE EXCHANGE (adapter — the client mirrors the exchange truth), asks the
StrategyLoop for this bar's intent, sizes it, and places the order(s) via the adapter. Realtime; the
same object serves fake-API and real Bybit (only the adapter's client differs). No batch, no replay.
"""
from __future__ import annotations

import time

from optimus9.live.sizing import TradeIntent


def _ms():
    return int(time.time() * 1000)


class O9LiveApp:
    def __init__(self, strategy, sizer, adapter, ledger, control, symbol, health=None, log=print):
        self.strategy = strategy      # StrategyLoop (decide)
        self.sizer = sizer            # PositionSizer (size)
        self.adapter = adapter        # ExchangeAdapter (execute) — fake or real Bybit
        self.ledger = ledger          # O9Ledger — o9's OWN record + tally (equity for sizing)
        self.control = control        # O9Control — operator state (sizing / halt / flatten), DB-backed
        self.health = health          # HealthStore — cascade phase + loop_ms (observability; None = off)
        self.symbol = symbol
        self.log = log

    def _write_phase(self, W, pos):
        if self.health:                                  # observability MUST NOT break the trading loop
            try:
                self.health.set_phase(self.strategy.phase(W, pos))
            except Exception as e:
                self.log("o9-live: health phase write failed: %s" % e)

    def _write_loop_ms(self, t0):
        if self.health:
            try:
                self.health.set_metrics(loop_ms=_ms() - t0)
            except Exception as e:
                self.log("o9-live: health loop_ms write failed: %s" % e)

    def position(self) -> dict | None:
        """The live position, read back from the EXCHANGE (authoritative), not a local guess."""
        lst = self.adapter.positions()
        if not lst:
            return None
        p = lst[0]
        return {"side": p["side"], "size": float(p["size"])}

    def _fill_price(self, order_id) -> float | None:
        for ex in self.adapter.executions():
            if ex.get("orderId") == order_id:
                return float(ex["execPrice"])
        return None

    def _execute(self, intent, price, mode, split, now_ms, placed):
        for o in self.sizer.size(intent, self.ledger.equity(), price, mode=mode, split=split):
            oid = self.adapter.place(o)
            fpx = self._fill_price(oid)
            if intent.action in ("open", "add"):
                self.ledger.record_open(o.side, o.qty, fpx, oid, intent.reason, now_ms)
                act = "add" if intent.action == "add" else ("open_long" if o.side == "Buy" else "open_short")
            else:
                self.ledger.record_close(fpx, oid, now_ms)
                act = "close"
            self.ledger.log_decision(now_ms, act, intent.reason, oid)
            placed.append({"action": intent.action, "side": o.side, "qty": o.qty, "order_id": oid, "fill": fpx})
            self.log("o9-live: %s %s %g @ %s → %s" % (intent.action, o.side, o.qty, fpx, oid))

    def on_bar(self, now_ms: int, price: float) -> list:
        """One realtime bar. Honours operator control (DB): flatten request → close; halted → no new trades;
        sizing mode/max/split from control. Position from the exchange; sizing off o9's OWN equity."""
        t0 = _ms()
        ctl = self.control.read()
        self.sizer.max_order = int(ctl["max_order"])
        placed = []

        if ctl["flatten_req"]:                               # kill-switch or exit button
            pos = self.position()
            if pos:
                close_side = "Sell" if pos["side"] == "Buy" else "Buy"
                self._execute(TradeIntent("close", side=close_side, qty=pos["size"], reason="operator_flatten"),
                              price, ctl["mode"], 1, now_ms, placed)
            self.control.clear_flatten()

        pos = self.position()
        W = self.strategy.window(now_ms)                     # build ONCE — shared by phase + intents
        self._write_phase(W, pos)                            # cascade block reflects the machine's view every bar

        if ctl["halted"]:
            self.ledger.log_decision(now_ms, "hold", "halted")
            self._write_loop_ms(t0)
            return placed

        intents = self.strategy.intents(W, pos)
        if not intents:
            self.ledger.log_decision(now_ms, "hold")
            self._write_loop_ms(t0)
            return placed
        for intent in intents:
            self._execute(intent, price, ctl["mode"], int(ctl["split"]), now_ms, placed)
        self._write_loop_ms(t0)
        return placed
