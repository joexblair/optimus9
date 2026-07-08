"""MatchingEngine — one-way pyramid (add re-weights avg) → reduce (realizes PnL) → close.
Runs against the o9_live fx_* tables (dev target; truncated clean each run)."""
import sys

import pytest

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from services.fakeapi.fill import OrderBookWalker
from services.fakeapi.store import FxStore
from services.fakeapi.engine import MatchingEngine

SYM = "FARTCOINUSDT"
ENTRY = {"bids": [["0.14000", "500000"]], "asks": [["0.14020", "500000"]]}   # short sells @ 0.14000
EXIT = {"bids": [["0.13600", "500000"]], "asks": [["0.13620", "500000"]]}    # buy back @ 0.13620


@pytest.fixture
def db():
    cfg = get_db_config(); cfg["database"] = "o9_live_test"
    d = DatabaseManager(**cfg); d.connect()
    for t in ("fx_fill", "fx_order", "fx_position"):
        d.execute("TRUNCATE TABLE %s" % t)
    yield d
    d.disconnect()


def test_pyramid_then_reduce_realizes_pnl(db):
    book = {"v": ENTRY}
    eng = MatchingEngine(FxStore(db), OrderBookWalker(taker_bps=5.5), lambda s: book["v"])

    eng.submit(SYM, "Sell", 66000)                       # open short
    eng.submit(SYM, "Sell", 45000)                       # pyramid add
    pos = db.execute("SELECT * FROM fx_position WHERE symbol=%s", (SYM,), fetch=True)[0]
    assert pos["side"] == "Sell"
    assert abs(float(pos["size"]) - 111000) < 1e-6
    assert abs(float(pos["avg_entry"]) - 0.14000) < 1e-6   # both legs @ 0.14000 → avg 0.14000
    assert pos["entry_count"] == 2 and pos["status"] == "open"

    book["v"] = EXIT                                      # price drops
    r = eng.submit(SYM, "Buy", 111000, reduce_only=True)  # close the short

    closed = db.execute("SELECT * FROM fx_position WHERE symbol=%s", (SYM,), fetch=True)[0]
    assert closed["status"] == "closed"
    assert abs(float(closed["size"])) < 1e-6
    # short: (entry 0.14000 - exit 0.13620) * 111000 - exit_fee(~8.32) ≈ 421.8 - 8.32
    exit_fee = 0.13620 * 111000 * 5.5 / 10000
    assert abs(r["realized"] - ((0.14000 - 0.13620) * 111000 - exit_fee)) < 0.5
    assert r["realized"] > 400
    assert db.execute("SELECT COUNT(*) c FROM fx_fill", fetch=True)[0]["c"] == 3


def test_hedge_both_legs_open_and_close_independently(db):
    """Hedge mode: long (idx1) and short (idx2) held at once, each pyramids + closes on its own PnL."""
    book = {"v": ENTRY}                                  # Buy@0.14020 (ask), Sell@0.14000 (bid)
    eng = MatchingEngine(FxStore(db), OrderBookWalker(taker_bps=5.5), lambda s: book["v"])

    eng.submit(SYM, "Buy", 10000, position_idx=1)        # open LONG leg
    eng.submit(SYM, "Sell", 20000, position_idx=2)       # open SHORT leg — both open at once
    eng.submit(SYM, "Buy", 5000, position_idx=1)         # pyramid the long

    legs = {p["position_idx"]: p for p in
            db.execute("SELECT * FROM fx_position WHERE symbol=%s AND status='open'", (SYM,), fetch=True)}
    assert set(legs) == {1, 2}                            # TWO independent open legs
    assert legs[1]["side"] == "Buy" and abs(float(legs[1]["size"]) - 15000) < 1e-6
    assert legs[2]["side"] == "Sell" and abs(float(legs[2]["size"]) - 20000) < 1e-6
    assert legs[1]["entry_count"] == 2                    # pyramided; short untouched
    assert legs[2]["entry_count"] == 1

    book["v"] = EXIT                                      # price drops → long loses, short wins
    rl = eng.submit(SYM, "Sell", 15000, reduce_only=True, position_idx=1)   # close long
    rs = eng.submit(SYM, "Buy", 20000, reduce_only=True, position_idx=2)    # close short

    assert rl["realized"] < 0 and rs["realized"] > 0     # independent, opposite outcomes
    assert rl["position_idx"] == 1 and rs["position_idx"] == 2
    both = db.execute("SELECT status FROM fx_position WHERE symbol=%s", (SYM,), fetch=True)
    assert all(x["status"] == "closed" for x in both) and len(both) == 2


def test_side_reduceonly_positionidx_mismatch_rejected(db):
    """Guard: an explicit positionIdx inconsistent with (side, reduceOnly) is rejected."""
    book = {"v": ENTRY}
    eng = MatchingEngine(FxStore(db), OrderBookWalker(taker_bps=5.5), lambda s: book["v"])
    with pytest.raises(ValueError):
        eng.submit(SYM, "Buy", 10000, position_idx=2)    # Buy-open implies idx1, not idx2
