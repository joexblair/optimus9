"""ExchangeAdapter — the execute layer (SRP: translate an Order/intent into venue API calls).

`ExchangeAdapter` is the exchange-AGNOSTIC contract, shaped by o9-live's needs (not any one venue's
API). `BybitAdapter` is impl #1; a future venue is a new impl, and o9-live's decide/size layers never
change. Fake-vs-real Bybit is purely how the injected BybitV5Client is built (base_url + signer).
Numerics go out as Bybit-style trimmed strings.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


def _num(x) -> str:
    return f"{float(x):.8f}".rstrip("0").rstrip(".")


class ExchangeAdapter(ABC):
    @abstractmethod
    def place(self, order) -> str: ...
    @abstractmethod
    def set_backstop(self, sl_price, trigger_by: str = "MarkPrice") -> dict: ...
    @abstractmethod
    def set_leverage(self, leverage) -> dict: ...
    @abstractmethod
    def positions(self) -> list: ...
    @abstractmethod
    def executions(self) -> list: ...


class BybitAdapter(ExchangeAdapter):
    """One adapter for one symbol; fake vs real Bybit differ only in the client's base_url + signer."""

    def __init__(self, client, symbol: str, category: str = "linear"):
        self._c = client
        self._sym = symbol
        self._cat = category

    def place(self, order) -> str:
        # hedge mode: positionIdx is the venue mapping (kept here, not in the venue-agnostic Order/sizer).
        # Bybit rule — open long=Buy→1, open short=Sell→2; close long=Sell→1, close short=Buy→2.
        idx = (2 if order.side == "Buy" else 1) if order.reduce_only else (1 if order.side == "Buy" else 2)
        body = {"category": self._cat, "symbol": self._sym, "side": order.side,
                "orderType": order.order_type, "qty": _num(order.qty), "positionIdx": idx}
        if order.reduce_only:
            body["reduceOnly"] = True
        if order.order_link_id:
            body["orderLinkId"] = order.order_link_id
        return self._c.post("/v5/order/create", body).get("orderId")

    def set_backstop(self, sl_price, trigger_by: str = "MarkPrice") -> dict:
        # the WIDE exchange failsafe (soft 0.5% is o9-live's StopManager); triggers on mark
        return self._c.post("/v5/position/trading-stop",
                            {"category": self._cat, "symbol": self._sym,
                             "stopLoss": _num(sl_price), "slTriggerBy": trigger_by})

    def set_leverage(self, leverage) -> dict:
        return self._c.post("/v5/position/set-leverage",
                            {"category": self._cat, "symbol": self._sym,
                             "buyLeverage": _num(leverage), "sellLeverage": _num(leverage)})

    def positions(self) -> list:
        return self._c.get("/v5/position/list", {"category": self._cat, "symbol": self._sym}).get("list", [])

    def executions(self) -> list:
        return self._c.get("/v5/execution/list", {"category": self._cat, "symbol": self._sym}).get("list", [])
