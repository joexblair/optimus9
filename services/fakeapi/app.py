"""FakeApiServer — the Bybit v5 contract (SRP: routing + universal envelope + error codes).

Skeleton: routes authenticate and return valid envelopes with stub results. The real behaviour —
OrderBookWalker fills, MatchingEngine one-way pyramid, StopMonitor backstop, FxStore persistence —
lands at milestone ③. Numerics are strings (Bybit uses Decimal-as-string). Business/auth errors
return HTTP 200 with a non-zero retCode, exactly like Bybit.
"""
from __future__ import annotations

import os
import time

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .auth import AuthEmulator
from .errors import FakeApiError
from .fill import OrderBookWalker
from .store import FxStore
from .engine import MatchingEngine

# test credentials from env (never hard-coded); the o9-live fake adapter signs with the same pair
_CREDS = {os.environ.get("O9_FAKE_API_KEY", "o9-fake-key"):
          os.environ.get("O9_FAKE_API_SECRET", "o9-fake-secret")}
_auth = AuthEmulator(_CREDS)
_TAKER_BPS = float(os.environ.get("O9_TAKER_BPS", "5.5"))   # config, not hard-coded

# symbol -> live order-book snapshot; OrderBookFeed updates this (⑤), tests set it directly
LIVE_BOOK: dict = {}
_ENGINE = None


def get_engine():
    """Lazy — so importing the app (fill/auth tests) needs no DB; built on first order."""
    global _ENGINE
    if _ENGINE is None:
        from optimus9.config import get_db_config
        from optimus9 import DatabaseManager
        db = DatabaseManager(**get_db_config()); db.connect()   # PK_DB_NAME=o9_live in the container env
        _ENGINE = MatchingEngine(FxStore(db), OrderBookWalker(_TAKER_BPS), lambda s: LIVE_BOOK.get(s))
    return _ENGINE

app = FastAPI(title="o9 fake-API (Bybit v5 mock)", version="0.1")


def _envelope(result: dict | None = None, ret_code: int = 0, ret_msg: str = "OK") -> dict:
    return {"retCode": ret_code, "retMsg": ret_msg, "result": result or {},
            "retExtInfo": {}, "time": int(time.time() * 1000)}


async def _require_auth(request: Request) -> str:
    """Verify against the SAME bytes the client signed: query string (GET) or raw body (POST)."""
    payload = request.url.query if request.method == "GET" else (await request.body()).decode()
    return _auth.verify(request.headers, payload)


@app.exception_handler(FakeApiError)
async def _on_fake_error(request: Request, exc: FakeApiError):
    return JSONResponse(status_code=200, content=_envelope(ret_code=exc.ret_code, ret_msg=exc.ret_msg))


@app.on_event("startup")
def _start_orderbook_feed():
    """If O9_LIVE_BOOK=<symbol> is set, stream the real book into LIVE_BOOK (else use /dev/book in tests)."""
    sym = os.environ.get("O9_LIVE_BOOK")
    if sym:
        from optimus9.live.feed import OrderBookFeed
        OrderBookFeed(sym, lambda s, b: LIVE_BOOK.__setitem__(s, b)).start()


@app.get("/health")
def health():
    """Liveness probe for the container-manager HealthGate."""
    return {"status": "ok", "ts": int(time.time() * 1000), "book": list(LIVE_BOOK)}


@app.post("/v5/order/create")
async def order_create(request: Request):
    await _require_auth(request)
    body = await request.json()
    try:
        res = get_engine().submit(
            body["symbol"], body["side"], body["qty"],
            order_type=body.get("orderType", "Market"),
            order_link_id=body.get("orderLinkId", ""),
            reduce_only=bool(body.get("reduceOnly", False)))
    except ValueError as e:            # e.g. empty book / no liquidity
        return _envelope(ret_code=110001, ret_msg=str(e))
    return _envelope({"orderId": res["order_id"], "orderLinkId": body.get("orderLinkId", "")})


@app.post("/v5/position/trading-stop")
async def trading_stop(request: Request):
    await _require_auth(request)  # the WIDE backstop SL (triggerBy=MarkPrice) — StopMonitor honours it at ③
    return _envelope({})


@app.post("/v5/position/set-leverage")
async def set_leverage(request: Request):
    await _require_auth(request)
    return _envelope({})


@app.get("/v5/position/list")
async def position_list(request: Request):
    await _require_auth(request)
    sym = request.query_params.get("symbol")
    p = get_engine()._store.open_position(sym) if sym else None
    lst = [] if not p else [{
        "symbol": p["symbol"], "side": p["side"], "size": str(p["size"]),
        "avgPrice": str(p["avg_entry"]), "leverage": str(p["leverage"]),
        "positionValue": str(round(float(p["size"]) * float(p["avg_entry"]), 8)), "unrealisedPnl": "0"}]
    return _envelope({"category": "linear", "list": lst})


@app.get("/v5/execution/list")
async def execution_list(request: Request):
    await _require_auth(request)
    sym = request.query_params.get("symbol")
    limit = int(request.query_params.get("limit", 50))
    rows = get_engine()._store._db.execute(
        "SELECT order_id, side, exec_price, exec_qty, fee, exec_ms FROM fx_fill WHERE symbol=%s "
        "ORDER BY exec_ms DESC LIMIT %s", (sym, limit), fetch=True) if sym else []
    lst = [{"orderId": r["order_id"], "side": r["side"], "execPrice": str(r["exec_price"]),
            "execQty": str(r["exec_qty"]), "execFee": str(r["fee"]), "execTime": str(r["exec_ms"])} for r in rows]
    return _envelope({"category": "linear", "list": lst})


@app.post("/dev/book")
async def dev_book(request: Request):
    """Test/dev only — inject an order-book snapshot until the live OrderBookFeed is wired (⑤)."""
    body = await request.json()
    LIVE_BOOK[body["symbol"]] = {"bids": body["bids"], "asks": body["asks"]}
    return {"ok": True}


@app.post("/dev/reset")
async def dev_reset():
    """Dev/ops — reset this mock exchange's OWN state (fx_order/fill/position). The engine is stateless
    (re-reads FxStore per order) so a TRUNCATE is a full reset — no engine rebuild. o9's ledger/account
    is o9's own store; the UI reset handler clears that side and calls this."""
    from optimus9.config import get_db_config
    from optimus9 import DatabaseManager
    db = DatabaseManager(**get_db_config()); db.connect()            # PK_DB_NAME=o9_live in the container env
    tables = ("fx_fill", "fx_order", "fx_position")                 # fixed names (DDL can't be parameterized)
    for t in tables:
        db.execute("TRUNCATE TABLE %s" % t)
    db.disconnect()
    return {"ok": True, "reset": list(tables)}
