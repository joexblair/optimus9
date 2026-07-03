"""OrderBookFeed — live Bybit order book for the fill model (SRP: maintain the book, push to a sink).

Subscribes `orderbook.{depth}.{symbol}`, applies snapshot+delta, and pushes a sorted book snapshot to a
sink (the fakeAPI's LIVE_BOOK) that OrderBookWalker reads. Runs in a daemon thread inside the fakeAPI so
fills walk the REAL book — the whole point of the forward-test. Reuses the existing BybitWebSocketClient.
"""
from __future__ import annotations

import sys
import threading

sys.path.insert(0, "/home/joe/thecodes")
from optimus9.data.bybit_websocket_client import BybitWebSocketClient


class OrderBookFeed:
    def __init__(self, symbol: str, sink, depth: int = 50):
        self.symbol = symbol
        self.sink = sink                       # callable(symbol, {"bids":[[p,s]..],"asks":[[p,s]..]})
        self.depth = depth
        self._bids: dict = {}
        self._asks: dict = {}

    def start(self) -> threading.Thread:
        t = threading.Thread(target=self._run, name="orderbook-feed", daemon=True)
        t.start()
        return t

    def _run(self):
        BybitWebSocketClient().stream("orderbook.%d.%s" % (self.depth, self.symbol), self._on)

    def _on(self, msg: dict):
        d = msg.get("data", {})
        if msg.get("type") == "snapshot":
            self._bids = {float(p): float(s) for p, s in d.get("b", [])}
            self._asks = {float(p): float(s) for p, s in d.get("a", [])}
        else:                                  # delta: size 0 removes a level, else set
            for p, s in d.get("b", []):
                p, s = float(p), float(s)
                self._bids.pop(p, None) if s == 0 else self._bids.__setitem__(p, s)
            for p, s in d.get("a", []):
                p, s = float(p), float(s)
                self._asks.pop(p, None) if s == 0 else self._asks.__setitem__(p, s)
        bids = sorted(self._bids.items(), reverse=True)[:self.depth]
        asks = sorted(self._asks.items())[:self.depth]
        if bids and asks:
            self.sink(self.symbol, {"bids": [[p, s] for p, s in bids], "asks": [[p, s] for p, s in asks]})
