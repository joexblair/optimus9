"""O9LiveApp + dynamic_leverage end to end on the o9_live_test DB: control knobs -> sizer -> order ->
ledger -> o9_sizing. A fake exchange and a fake producer; the ledger, control and sizer are the real ones."""
import sys

import pytest

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.live.app import O9LiveApp
from optimus9.live.control import O9Control
from optimus9.live.ledger import O9Ledger
from optimus9.live.sizing import PositionSizer, TradeIntent

SYM = "FARTCOINUSDT"
PX = 0.18291


class FakeExchange:
    def __init__(self):
        self.pos, self.orders, self._n = {}, [], 0

    def positions(self):
        return [{"side": s, "size": q} for s, q in self.pos.items() if q > 0]

    def place(self, o):
        self._n += 1
        oid = "fx-test-%d" % self._n
        self.orders.append((oid, o))
        side = o.side if not o.reduce_only else ("Buy" if o.side == "Sell" else "Sell")
        self.pos[side] = self.pos.get(side, 0) + (-o.qty if o.reduce_only else o.qty)
        return oid

    def executions(self):
        return [{"orderId": oid, "execPrice": PX} for oid, _ in self.orders]


class FakeProducer:
    def __init__(self, intents):
        self.queue = list(intents)

    def window(self, now_ms):
        return None

    def intents(self, W, positions, legs=None):
        return [self.queue.pop(0)] if self.queue else []


@pytest.fixture
def db():
    cfg = get_db_config(); cfg["database"] = "o9_live_test"
    d = DatabaseManager(**cfg); d.connect()
    d.execute("DROP TABLE IF EXISTS o9_control")
    d.execute("CREATE TABLE o9_control LIKE o9_live.o9_control")      # the live schema, before migration
    d.execute("CREATE TABLE IF NOT EXISTS o9_decision LIKE o9_live.o9_decision")
    for t in ("o9_ledger", "o9_account", "o9_decision"):
        d.execute("TRUNCATE TABLE %s" % t)
    d.execute("DROP TABLE IF EXISTS o9_sizing")
    yield d
    d.execute("DROP TABLE IF EXISTS o9_control")
    d.disconnect()


def _app(db, intents, stop_pct=0.70):
    ledger = O9Ledger(db, SYM, start_equity=888, clock=lambda: 1000)
    control = O9Control(db, clock=lambda: 1000)
    control.set_sizing(mode="dynamic_leverage")
    ex = FakeExchange()
    app = O9LiveApp(FakeProducer(intents), PositionSizer(max_order=66000, stop_pct=stop_pct), ex, ledger,
                    control, SYM, log=lambda *a: None)
    return app, ex, ledger


def test_every_open_is_sized_off_equity_and_banked(db):
    app, ex, ledger = _app(db, [TradeIntent("open", side="Buy", reason="octo-sig")])
    placed = app.on_bar(5000, PX)
    assert [p["qty"] for p in placed] == [10818]                          # 888 x 2.2284 / 0.18291
    r = db.execute("SELECT * FROM o9_sizing", fetch=True)
    assert len(r) == 1 and r[0]["order_id"] == placed[0]["order_id"]
    assert float(r[0]["lev_target"]) == 2.2284 and r[0]["n_live"] == 0 and float(r[0]["equity"]) == 888


def test_the_risk_knob_is_read_from_control_each_bar(db):
    app, ex, ledger = _app(db, [TradeIntent("open", side="Buy")])
    O9Control(db).set_sizing(risk_pct=1.0)                                # operator halves the budget
    placed = app.on_bar(5000, PX)
    assert placed[0]["qty"] == 5409                                       # 888 x (1.0/0.8975) / 0.18291


def test_a_second_live_leg_gets_half_the_budget(db):
    app, ex, ledger = _app(db, [TradeIntent("open", side="Buy"), TradeIntent("open", side="Sell")])
    a = app.on_bar(5000, PX)[0]["qty"]
    b = app.on_bar(10000, PX)[0]["qty"]
    assert (a, b) == (10818, 5409)
    assert [r["n_live"] for r in db.execute("SELECT n_live FROM o9_sizing ORDER BY kline_ms", fetch=True)] == [0, 1]


def test_no_stop_means_no_trade_rather_than_a_guess(db):
    app, ex, ledger = _app(db, [TradeIntent("open", side="Buy")], stop_pct=None)
    with pytest.raises(ValueError):
        app.on_bar(5000, PX)
    assert ex.orders == []
