"""O9Ledger — o9's own record + tally: open → close realizes o9's PnL → equity updates (vs o9_live)."""
import sys

import pytest

sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.live.ledger import O9Ledger

SYM = "FARTCOINUSDT"


@pytest.fixture
def db():
    cfg = get_db_config(); cfg["database"] = "o9_live_test"
    d = DatabaseManager(**cfg); d.connect()
    for t in ("o9_ledger", "o9_account"):
        d.execute("TRUNCATE TABLE %s" % t)
    yield d
    d.disconnect()


def test_open_close_realizes_and_tallies(db):
    lg = O9Ledger(db, SYM, start_equity=500, taker_bps=5.5, clock=lambda: 1000)
    assert lg.equity() == 500
    lg.record_open("Sell", 66000, 0.14000, "o1", "entry", 1000)
    assert lg.open_position() == {"side": "Sell", "size": 66000}

    realized = lg.record_close(0.13620, "o2", 2000)          # short: profit as price fell
    exp_gross = (0.14000 - 0.13620) * 66000
    exp_fee = (0.14000 + 0.13620) * 66000 * 5.5 / 10000
    assert abs(realized - (exp_gross - exp_fee)) < 0.5
    assert abs(lg.equity() - (500 + realized)) < 0.01
    assert lg.open_position() is None

    row = db.execute("SELECT status, net FROM o9_ledger WHERE symbol=%s", (SYM,), fetch=True)[0]
    assert row["status"] == "closed" and abs(float(row["net"]) - realized) < 0.01
    acct = db.execute("SELECT trade_count FROM o9_account WHERE acct_id=1", fetch=True)[0]
    assert acct["trade_count"] == 1
