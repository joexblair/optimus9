"""OrderBookFeed — live Bybit order book for the fill model (SRP: maintain the book, push to a sink).

Subscribes `orderbook.{depth}.{symbol}`, applies snapshot+delta, and pushes a sorted book snapshot to a
sink (the fakeAPI's LIVE_BOOK) that OrderBookWalker reads. Runs in a daemon thread inside the fakeAPI so
fills walk the REAL book — the whole point of the forward-test. Reuses the existing BybitWebSocketClient.
"""
from __future__ import annotations

import sys
import threading
import time

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
        # Joe 1002 outage item #7: the book socket RECORDS what it receives, one line per second, beside
        # the collector's and the witness's (ws_liveness). Reconnect behaviour unchanged.
        import os
        from optimus9.data.ws_liveness import WsLiveness
        live = WsLiveness(os.environ.get("O9_BOOK_LIVENESS_LOG",
                                         "/home/joe/thecodes/ws_liveness_fakeapi_book.log"), "fakeapi-book")
        # Joe 1002: the book socket auto-restarts like the tick sockets - 60 s with no book message. No
        # gap-fill: Bybit sends a fresh snapshot on every subscribe, and `_on` replaces the book with it
        stall = float(os.environ.get("O9_BOOK_STALL_S", "60"))
        BybitWebSocketClient(liveness=live, stall_s=stall).stream(
            "orderbook.%d.%s" % (self.depth, self.symbol), self._on)

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
            # recv_ms / ts / cts: when this snapshot arrived, and Bybit's own times for it (ts = system,
            # cts = matching engine). The fill walker reads bids/asks only; the stamps let a fill record
            # how old its book was (outage item #7, the 1002 Bybit check's M5)
            self.sink(self.symbol, {"bids": [[p, s] for p, s in bids], "asks": [[p, s] for p, s in asks],
                                    "recv_ms": int(time.time() * 1000), "ts": msg.get("ts"), "cts": msg.get("cts")})
