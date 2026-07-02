"""Integration: a signed /v5/order/create → book-walk fill → stored one-way position (o9_live)."""
import json
import sys
import time

sys.path.insert(0, '/home/joe/thecodes')
from fastapi.testclient import TestClient
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import services.fakeapi.app as appmod
from services.fakeapi.fill import OrderBookWalker
from services.fakeapi.store import FxStore
from services.fakeapi.engine import MatchingEngine
from optimus9.live.exchange import HmacSigner


def test_signed_order_fills_and_stores():
    cfg = get_db_config(); cfg["database"] = "o9_live"
    db = DatabaseManager(**cfg); db.connect()
    for t in ("fx_fill", "fx_order", "fx_position"):
        db.execute("TRUNCATE TABLE %s" % t)
    appmod.LIVE_BOOK["FARTCOINUSDT"] = {"bids": [["0.14000", "500000"]], "asks": [["0.14020", "500000"]]}
    appmod._ENGINE = MatchingEngine(FxStore(db), OrderBookWalker(5.5), lambda s: appmod.LIVE_BOOK.get(s))

    c = TestClient(appmod.app)
    signer = HmacSigner("o9-fake-key", "o9-fake-secret")
    body = {"category": "linear", "symbol": "FARTCOINUSDT", "side": "Sell",
            "orderType": "Market", "qty": "66000", "orderLinkId": "o9-e1"}
    raw = json.dumps(body, separators=(",", ":")); ts = int(time.time() * 1000)
    h = signer.auth_headers(ts, 5000, raw); h["Content-Type"] = "application/json"
    r = c.post("/v5/order/create", content=raw, headers=h).json()

    assert r["retCode"] == 0
    assert r["result"]["orderId"].startswith("fx-")
    pos = db.execute("SELECT * FROM fx_position WHERE symbol='FARTCOINUSDT'", fetch=True)[0]
    assert pos["side"] == "Sell" and abs(float(pos["size"]) - 66000) < 1e-6
    assert db.execute("SELECT COUNT(*) c FROM fx_fill", fetch=True)[0]["c"] == 1

    appmod._ENGINE = None  # reset the lazy singleton for other tests
    db.disconnect()
