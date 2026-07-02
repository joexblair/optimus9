"""MatchingEngine — order lifecycle (SRP: apply a fill to the one-way position; decide grow/reduce).

Bybit one-way semantics: a same-side order ADDS (pyramids — size grows, avg_entry re-weights); an
opposite-side order REDUCES (realizes PnL on the closed portion), closing at size 0. Fill pricing is
delegated to OrderBookWalker; persistence to FxStore. This class owns only the position arithmetic.
"""
from __future__ import annotations


class MatchingEngine:
    def __init__(self, store, walker, book_provider):
        """book_provider: callable(symbol) -> book dict (live OrderBookFeed, or injected for tests)."""
        self._store = store
        self._walker = walker
        self._book = book_provider

    def submit(self, symbol, side, qty, order_type="Market", order_link_id="", reduce_only=False) -> dict:
        book = self._book(symbol)
        fill = self._walker.walk(book, side, float(qty))
        if fill is None:
            raise ValueError("no liquidity to fill")

        order_id = self._store.insert_order(symbol, side, order_type, fill.filled_qty,
                                            order_link_id=order_link_id, reduce_only=reduce_only)
        pos = self._store.open_position(symbol)
        realized = 0.0

        if pos is None:
            pos_id = self._store.create_position(symbol, side, fill.filled_qty, fill.avg_px, fill.fee)
            self._store.insert_fill(order_id, pos_id, symbol, side, fill, closed_qty=0.0)

        elif pos["side"] == side:                       # pyramid ADD — re-weight avg_entry
            old_sz, old_avg = float(pos["size"]), float(pos["avg_entry"])
            new_sz = old_sz + fill.filled_qty
            new_avg = (old_avg * old_sz + fill.avg_px * fill.filled_qty) / new_sz
            self._store.grow_position(pos["position_id"], new_sz, new_avg, fill.fee)
            self._store.insert_fill(order_id, pos["position_id"], symbol, side, fill, closed_qty=0.0)

        else:                                           # opposite side — REDUCE / close
            close_qty = min(fill.filled_qty, float(pos["size"]))
            direction = 1.0 if pos["side"] == "Buy" else -1.0     # long profits when exit>entry; short the reverse
            realized = direction * (fill.avg_px - float(pos["avg_entry"])) * close_qty - fill.fee
            self._store.reduce_position(pos["position_id"], float(pos["size"]) - close_qty, realized, fill.fee)
            self._store.insert_fill(order_id, pos["position_id"], symbol, side, fill, closed_qty=close_qty)

        return {"order_id": order_id, "fill": fill, "realized": round(realized, 8)}
