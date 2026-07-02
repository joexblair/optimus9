"""OrderBookWalker — the fill model (SRP: price a fill, nothing else).

Walks the LIVE order book for the order size → volume-weighted avg fill + slippage vs mid + taker
fee, per leg. This is the headline the forward-test exists to measure: the REAL entry-condition cost
(thin books during reversals), not a flat assumption. Taker rate is a ctor arg (config, not hard-coded).

Bybit book convention: `bids` sorted high→low, `asks` low→high, each level = [price, size] (strings).
A Buy takes liquidity from asks (cheapest first); a Sell takes from bids (highest first).
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Fill:
    avg_px: float       # volume-weighted average fill
    filled_qty: float   # coins actually filled (< requested if the book was thin)
    mid: float          # book mid at fill (slippage basis)
    slip_bps: float     # ADVERSE slippage vs mid, in bps (always ≥ 0 = a cost)
    fee: float          # taker fee on the filled notional
    exhausted: bool     # True if the book ran out before the full qty filled


class OrderBookWalker:
    def __init__(self, taker_bps: float = 5.5):
        self._taker = taker_bps

    def walk(self, book: dict, side: str, qty: float) -> Fill | None:
        bids, asks = book.get("bids") or [], book.get("asks") or []
        if not bids or not asks:
            return None
        mid = (float(bids[0][0]) + float(asks[0][0])) / 2.0
        levels = asks if side == "Buy" else bids   # Buy hits asks, Sell hits bids

        remaining, cost, filled = float(qty), 0.0, 0.0
        for px, sz in levels:
            px, sz = float(px), float(sz)
            take = min(remaining, sz)
            cost += take * px
            filled += take
            remaining -= take
            if remaining <= 1e-9:
                break
        if filled <= 0:
            return None

        avg = cost / filled
        # Buy fills above mid, Sell fills below mid — both adverse; sign so slip is a positive cost.
        slip_bps = (avg - mid) / mid * 10000.0 * (1.0 if side == "Buy" else -1.0)
        fee = avg * filled * self._taker / 10000.0
        return Fill(round(avg, 8), round(filled, 8), round(mid, 8),
                    round(slip_bps, 2), round(fee, 8), remaining > 1e-9)
