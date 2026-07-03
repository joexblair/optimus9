"""O9LiveApp — the live loop orchestrator (SRP: wire decide→size→execute per bar; own nothing else).

Collector-triggered: each closed 5s bar (at seam+301ms) calls `on_bar(now_ms, price)`. It reads the
current position FROM THE EXCHANGE (adapter — the client mirrors the exchange truth), asks the
StrategyLoop for this bar's intent, sizes it, and places the order(s) via the adapter. Realtime; the
same object serves fake-API and real Bybit (only the adapter's client differs). No batch, no replay.
"""
from __future__ import annotations


class O9LiveApp:
    def __init__(self, strategy, sizer, adapter, ledger, symbol, mode="fixed", log=print):
        self.strategy = strategy      # StrategyLoop (decide)
        self.sizer = sizer            # PositionSizer (size)
        self.adapter = adapter        # ExchangeAdapter (execute) — fake or real Bybit
        self.ledger = ledger          # O9Ledger — o9's OWN record + tally (equity for sizing)
        self.symbol = symbol
        self.mode = mode
        self.log = log

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

    def on_bar(self, now_ms: int, price: float) -> list:
        """One realtime bar → 0+ orders. `now_ms` = seam+301ms; `price` = the just-closed bar's close.
        Position from the exchange; sizing from o9's OWN equity; every fill recorded in o9's ledger."""
        intents = self.strategy.decide(now_ms, self.position())
        if not intents:
            self.ledger.log_decision(now_ms, "hold")
            return []
        placed = []
        for intent in intents:
            for o in self.sizer.size(intent, self.ledger.equity(), price, mode=self.mode):
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
        return placed
