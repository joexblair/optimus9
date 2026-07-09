"""replay — drive the v2 producer's trades through the REAL sizer + fake-exchange fill/store, to
populate o9_live.fx_* (the path to the first trade on the UI, and a stack-validation harness).

Batch (not per-bar) for speed: run v2_walk_ad + lr_exit_v2 + strand_rescue once → open/close events →
route each through PositionSizer → MatchingEngine (OrderBookWalker fill + FxStore). A synthetic book
stands in for the live OrderBookFeed (real book-walk cost arrives with the WS feed). One-way: an entry
opens/adds; the first exit while holding closes the net. Equity compounds realized PnL (for dynamic5x).
"""
from __future__ import annotations

import bias_machine as bm
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue
from optimus9.live.sizing import PositionSizer, TradeIntent
from services.fakeapi.fill import OrderBookWalker
from services.fakeapi.store import FxStore
from services.fakeapi.engine import MatchingEngine

_SIDE = {1: "Buy", -1: "Sell"}


def synth_book(price: float, spread_bps: float = 1.6, levels: int = 10, depth: float = 500000.0) -> dict:
    """A plausible deep FARTCOIN book around `price` (stand-in for the live feed)."""
    half = price * spread_bps / 10000.0 / 2.0
    step = price * 0.0001
    bids = [[round(price - half - i * step, 8), depth] for i in range(levels)]
    asks = [[round(price + half + i * step, 8), depth] for i in range(levels)]
    return {"bids": bids, "asks": asks}


def replay(strat_db, store_db, bias_cfg, lr_cfg, symbol, end_ms, mode="fixed", max_order=66000,
           leverage=5.0, taker_bps=5.5, start_equity=500.0, truncate=False):
    # strat_db = the tape (pk_optimizer, until the collector fills o9_live); store_db = o9_live fx_*
    db = store_db
    W = bm.BiasWindow(strat_db, end_ms, cfg=bias_cfg, lean=True)
    ent = v2_walk_ad(W, lr_cfg)                        # the SHIPPING producer (O9_PRODUCER=ad). Was v2_walk:
                                                       # this tool replayed a machine we do not run (register E2)
    exd = {x[0]: x for x in strand_rescue(W, lr_cfg, ent, lr_exit_v2(W, lr_cfg, ent, predict=False))}

    events = []                                        # (t, kind, bd, price)
    for (tms, es, bd, tj) in ent:
        x = exd[tms]                                   # (tms, exit_ms, bd, entry_px, exit_px, ret, reason)
        events.append((tms, "open", bd, float(x[3])))
        events.append((int(x[1]), "close", bd, float(x[4])))
    events.sort(key=lambda e: e[0])

    if truncate:
        for t in ("fx_fill", "fx_order", "fx_position"):
            db.execute("TRUNCATE TABLE %s" % t)

    book = {"b": None}
    engine = MatchingEngine(FxStore(db), OrderBookWalker(taker_bps), lambda s: book["b"])
    sizer = PositionSizer(max_order=max_order, leverage=leverage)
    store = engine._store
    equity, opens, closes = start_equity, 0, 0

    for (t, kind, bd, price) in events:
        book["b"] = synth_book(price)
        pos = store.open_leg(symbol)                   # idx=None → any open leg (one-way harness, unchanged behaviour)
        if kind == "open":
            side = _SIDE[bd]
            action = "add" if (pos and pos["side"] == side) else ("open" if pos is None else None)
            if action is None:
                continue                               # opposite side while holding — skip (one-way)
            for o in sizer.size(TradeIntent(action, side=side), equity, price, mode=mode):
                engine.submit(symbol, o.side, o.qty)
            opens += 1
        elif pos:                                      # close the net on the first exit while holding
            close_side = "Sell" if pos["side"] == "Buy" else "Buy"
            res = engine.submit(symbol, close_side, float(pos["size"]), reduce_only=True)
            equity += res["realized"]
            closes += 1

    return {"entries": len(ent), "opens": opens, "closes": closes, "equity": round(equity, 2)}


if __name__ == "__main__":
    import sys, datetime as dtm; from datetime import timezone
    sys.path.insert(0, "/home/joe/thecodes")
    from optimus9.config import get_db_config
    from optimus9 import DatabaseManager
    from optimus9.analysis.lr import lr_config
    from sweep_eval import BASE_BIAS

    def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
    cfg = get_db_config(); cfg["database"] = "o9_live"
    o9db = DatabaseManager(**cfg); o9db.connect()
    dev = DatabaseManager(**get_db_config()); dev.connect()
    r = replay(dev, o9db, bm.BiasConfig(**BASE_BIAS), lr_config(dev), "FARTCOINUSDT",
               ms("2026-06-22 00:00"), mode="dynamic5x", truncate=True)
    print("replay:", r)
    print("fx_position:", o9db.execute("SELECT COUNT(*) c, SUM(status='closed') closed FROM fx_position", fetch=True)[0])
    print("fx_fill:", o9db.execute("SELECT COUNT(*) c FROM fx_fill", fetch=True)[0])
    o9db.disconnect(); dev.disconnect()
