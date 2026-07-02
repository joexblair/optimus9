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


@app.get("/health")
def health():
    """Liveness probe for the container-manager HealthGate."""
    return {"status": "ok", "ts": int(time.time() * 1000)}


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
    return _envelope({"category": "linear", "list": []})


@app.get("/v5/execution/list")
async def execution_list(request: Request):
    await _require_auth(request)
    return _envelope({"category": "linear", "list": []})
