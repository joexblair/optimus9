"""O9LiveApp — the live loop orchestrator (SRP: wire decide→size→execute per bar; own nothing else).

Collector-triggered: each closed 5s bar (at seam+301ms) calls `on_bar(now_ms, price)`. It reads the
current position FROM THE EXCHANGE (adapter — the client mirrors the exchange truth), asks the
StrategyLoop for this bar's intent, sizes it, and places the order(s) via the adapter. Realtime; the
same object serves fake-API and real Bybit (only the adapter's client differs). No batch, no replay.
"""
from __future__ import annotations


class O9LiveApp:
    def __init__(self, strategy, sizer, adapter, symbol, mode="fixed", equity_fn=None, log=print):
        self.strategy = strategy      # StrategyLoop (decide)
        self.sizer = sizer            # PositionSizer (size)
        self.adapter = adapter        # ExchangeAdapter (execute) — fake or real Bybit
        self.symbol = symbol
        self.mode = mode
        self.equity_fn = equity_fn or (lambda: 500.0)
        self.log = log

    def position(self) -> dict | None:
        """The live position, read back from the exchange (not a local guess)."""
        lst = self.adapter.positions()
        if not lst:
            return None
        p = lst[0]
        return {"side": p["side"], "size": float(p["size"])}

    def on_bar(self, now_ms: int, price: float) -> list:
        """One realtime bar → 0+ orders. `now_ms` = seam+301ms; `price` = the just-closed bar's close."""
        pos = self.position()
        placed = []
        for intent in self.strategy.decide(now_ms, pos):
            orders = self.sizer.size(intent, self.equity_fn(), price, mode=self.mode)
            for o in orders:
                oid = self.adapter.place(o)
                placed.append({"action": intent.action, "side": o.side, "qty": o.qty, "order_id": oid})
                self.log("o9-live: %s %s %g → %s" % (intent.action, o.side, o.qty, oid))
        return placed
