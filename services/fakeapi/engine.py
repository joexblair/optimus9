"""MatchingEngine — order lifecycle (SRP: apply a fill to the addressed hedge leg; decide grow/reduce).

Bybit hedge semantics: each symbol holds two independent legs by positionIdx (1=long, 2=short). The
order's (side, reduceOnly) determines which leg and whether it opens/adds vs reduces/closes:
  open/add  long  = Buy  + idx1        close/reduce long  = Sell + reduceOnly + idx1
  open/add  short = Sell + idx2        close/reduce short = Buy  + reduceOnly + idx2
So positionIdx is a pure function of (side, reduceOnly) — the engine derives it when not passed and
validates it when passed. Fill pricing is delegated to OrderBookWalker; persistence to FxStore. This
class owns only the per-leg position arithmetic.
"""
from __future__ import annotations


class MatchingEngine:
    def __init__(self, store, walker, book_provider):
        """book_provider: callable(symbol) -> book dict (live OrderBookFeed, or injected for tests)."""
        self._store = store
        self._walker = walker
        self._book = book_provider

    @staticmethod
    def _derive_idx(side, reduce_only) -> int:
        """positionIdx implied by (side, reduceOnly) — Bybit hedge rule."""
        if reduce_only:
            return 2 if side == "Buy" else 1        # Buy closes the short leg; Sell closes the long leg
        return 1 if side == "Buy" else 2            # Buy opens the long leg; Sell opens the short leg

    def submit(self, symbol, side, qty, order_type="Market", order_link_id="",
               reduce_only=False, position_idx=None) -> dict:
        want = self._derive_idx(side, reduce_only)
        if position_idx is None:
            position_idx = want
        elif int(position_idx) != want:
            raise ValueError("side/reduceOnly/positionIdx mismatch: side=%s reduceOnly=%s idx=%s (expected %s)"
                             % (side, reduce_only, position_idx, want))

        book = self._book(symbol)
        fill = self._walker.walk(book, side, float(qty))
        if fill is None:
            raise ValueError("no liquidity to fill")

        order_id = self._store.insert_order(symbol, side, order_type, fill.filled_qty,
                                            order_link_id=order_link_id, reduce_only=reduce_only)
        pos = self._store.open_leg(symbol, position_idx)
        realized = 0.0

        if not reduce_only:                             # OPEN or ADD the addressed leg
            if pos is None:
                pos_id = self._store.create_position(symbol, side, fill.filled_qty, fill.avg_px, fill.fee,
                                                     position_idx=position_idx)
                self._store.insert_fill(order_id, pos_id, symbol, side, fill, closed_qty=0.0)
            else:                                       # pyramid ADD — re-weight avg_entry
                old_sz, old_avg = float(pos["size"]), float(pos["avg_entry"])
                new_sz = old_sz + fill.filled_qty
                new_avg = (old_avg * old_sz + fill.avg_px * fill.filled_qty) / new_sz
                self._store.grow_position(pos["position_id"], new_sz, new_avg, fill.fee)
                self._store.insert_fill(order_id, pos["position_id"], symbol, side, fill, closed_qty=0.0)

        else:                                           # REDUCE / close the addressed leg
            if pos is None:
                raise ValueError("reduceOnly with no open leg %d" % position_idx)
            close_qty = min(fill.filled_qty, float(pos["size"]))
            direction = 1.0 if pos["side"] == "Buy" else -1.0     # long profits when exit>entry; short the reverse
            realized = direction * (fill.avg_px - float(pos["avg_entry"])) * close_qty - fill.fee
            self._store.reduce_position(pos["position_id"], float(pos["size"]) - close_qty, realized, fill.fee)
            self._store.insert_fill(order_id, pos["position_id"], symbol, side, fill, closed_qty=close_qty)

        return {"order_id": order_id, "fill": fill, "realized": round(realized, 8), "position_idx": position_idx}
