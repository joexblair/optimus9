"""Sizing (SRP: turn an intent + account + price into concrete orders — nothing about deciding or executing).

TradeIntent is the seam from decide → size (an event, not a baked order). PositionSizer applies the
LAUNCH modes — smallest ($5 notional floor, cautious mainnet start) · fixed (max_order) · dynamic5x
(min(max_order, 5×equity/price)) · dynamic_leverage (Joe 1005: risk_pct of equity per entry over the
worst case per trade, min(max_order, lev×equity/price)) — plus the split modifier. Instrument constraints + max_order + leverage
are ctor args (config/DB-sourced, never hard-coded here). Conviction/liquidity inputs layer on later (b/c).
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class TradeIntent:
    action: str            # 'open' | 'add' | 'reduce' | 'close' | 'hold'
    side: str = ""         # 'Buy' | 'Sell'  (the order side; for close = the closing side)
    qty: float = 0.0       # reduce/close: the size to close. open/add: 0 → sizer computes
    reason: str = ""
    ts: int = 0
    led_id: int | None = None   # per-leg close (option B per-leg SL) → close just this ledger leg; None = whole stack


@dataclass
class Order:
    side: str
    qty: float
    order_type: str = "Market"
    reduce_only: bool = False
    order_link_id: str = ""


class PositionSizer:
    def __init__(self, min_qty=1.0, qty_step=1.0, min_notional=5.0, max_order=66000.0, leverage=5.0,
                 risk_pct=None, stop_pct=None, drag_pct=None):
        # all config/instrument-sourced by the caller; this class holds no literals of its own
        self.min_qty = min_qty
        self.qty_step = qty_step
        self.min_notional = min_notional
        self.max_order = max_order
        self.leverage = leverage
        # dynamic_leverage (Joe 1005): risk_pct + drag_pct come from o9_control each bar; stop_pct is the
        # stop the producer's trade book places (octo: wsf_trade_config mae_cap), handed in at startup
        self.risk_pct = risk_pct
        self.stop_pct = stop_pct
        self.drag_pct = drag_pct
        self.last_calc = None          # the sizing inputs + result of the last open/add, for o9_sizing

    def leverage_for(self, n_live: int = 0) -> float:
        """Dynamic leverage (Joe 1005, `docs/octo-freedom/1005_knobs.md` s3). The worst case per trade is
        known before entry - the stop the book places + the round-trip drag - so a risk budget converts
        straight to leverage. The budget is shared by the legs already open at this entry, so concurrent
        legs never stack past risk_pct in total (octo has no pyramid, so n_live is 0 there)."""
        if self.stop_pct is None or self.risk_pct is None or self.drag_pct is None:
            raise ValueError("dynamic_leverage needs risk_pct, stop_pct and drag_pct (got %r / %r / %r)"
                             % (self.risk_pct, self.stop_pct, self.drag_pct))
        return (float(self.risk_pct) / (int(n_live) + 1)) / (float(self.stop_pct) + float(self.drag_pct))

    def _floor_step(self, q: float) -> float:
        return math.floor(q / self.qty_step) * self.qty_step

    def _ceil_step(self, q: float) -> float:
        return math.ceil(q / self.qty_step) * self.qty_step

    def _valid(self, q: float, price: float) -> bool:
        return q >= self.min_qty and q * price >= self.min_notional

    def size(self, intent: TradeIntent, equity: float, price: float,
             mode: str = "smallest", split: int = 1, n_live: int = 0) -> list[Order]:
        """Return the concrete order(s) for this intent. Empty list if it can't be sized (too small).
        n_live = legs already open at this entry (dynamic_leverage shares its risk budget across them)."""
        if intent.action in ("close", "reduce"):
            return self._split_orders(intent.side, self._floor_step(intent.qty), split, price, reduce_only=True)
        if intent.action not in ("open", "add"):
            return []   # hold

        self.last_calc = None
        lev_target = None
        if mode == "smallest":
            q = max(self.min_qty, self._ceil_step(self.min_notional / price))   # $5 floor, rounded up
        elif mode == "fixed":
            q = self._floor_step(self.max_order)
        elif mode == "dynamic5x":
            q = self._floor_step(min(self.max_order, self.leverage * equity / price))
        elif mode == "dynamic_leverage":
            lev_target = self.leverage_for(n_live)
            q = self._floor_step(min(self.max_order, lev_target * equity / price))
        else:
            raise ValueError("unknown sizing mode: %s" % mode)

        dyn = mode == "dynamic_leverage"
        self.last_calc = dict(mode=mode, equity=float(equity), price=float(price), n_live=int(n_live),
                              risk_pct=self.risk_pct if dyn else None, stop_pct=self.stop_pct if dyn else None,
                              drag_pct=self.drag_pct if dyn else None, lev_target=lev_target, coins=q,
                              notional=q * price, lev_applied=(q * price / equity) if equity > 0 else None,
                              capped=bool(dyn and lev_target * equity / price > self.max_order))
        if not self._valid(q, price):
            return []
        return self._split_orders(intent.side, q, split, price, reduce_only=False)

    def _split_orders(self, side: str, qty: float, split: int, price: float, reduce_only: bool) -> list[Order]:
        split = max(1, int(split))
        if split == 1 or qty <= 0:
            return [Order(side, qty, reduce_only=reduce_only)] if qty > 0 else []
        slice_q = self._floor_step(qty / split)
        if not self._valid(slice_q, price):        # slices too small → don't split, one order
            return [Order(side, qty, reduce_only=reduce_only)]
        orders = [Order(side, slice_q, reduce_only=reduce_only) for _ in range(split - 1)]
        orders.append(Order(side, qty - slice_q * (split - 1), reduce_only=reduce_only))   # last carries remainder
        return orders
