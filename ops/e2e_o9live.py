"""E2E: O9LiveApp → BybitAdapter → real HTTP → running fakeAPI → book-walk fill → fx_position."""
import os
os.environ.update({k: '1' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')})
import sys, datetime as dtm
from datetime import timezone
import requests
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue
from optimus9.live.exchange import HmacSigner, BybitV5Client, BybitAdapter
from optimus9.live.sizing import PositionSizer
from optimus9.live.strategy import StrategyLoop
from optimus9.live.app import O9LiveApp
from optimus9.live.control import O9Control
from optimus9.live.ledger import O9Ledger
from sweep_eval import BASE_BIAS

URL = "http://127.0.0.1:8098"
SYM = "FARTCOINUSDT"


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


dev = DatabaseManager(**get_db_config()); dev.connect()          # dev tape (pk_optimizer)
o9cfg = get_db_config(); o9cfg["database"] = "o9_live"
o9 = DatabaseManager(**o9cfg); o9.connect()
for t in ("fx_fill", "fx_order", "fx_position", "o9_ledger", "o9_account"):
    o9.execute("TRUNCATE TABLE %s" % t)

bcfg = bm.BiasConfig(**BASE_BIAS); lc = lr_config(dev)
Wf = bm.BiasWindow(dev, ms("2026-06-22 00:00"), cfg=bcfg, lean=True)
ent = v2_walk_ad(Wf, lc)
exd = {x[0]: x for x in strand_rescue(Wf, lc, ent, lr_exit_v2(Wf, lc, ent, predict=False))}

strat = StrategyLoop(dev, bcfg, lc, SYM, buffer_hours=12, warmup_hours=40)
e = None
for cand in ent[-25:]:                                           # find a recent entry that reproduces live
    if any(i.action == "open" for i in strat.decide(cand[0] + 5000, None)):
        e = cand; break
assert e is not None, "no reproducing entry found"
entry_px = float(exd[e[0]][3])
print("target entry ts=%s bd=%s entry_px=%.5f" % (e[0], e[2], entry_px))

# inject a book around the entry price (until the live OrderBookFeed is wired)
half = entry_px * 1.6 / 10000 / 2
step = entry_px * 1e-4
book = {"symbol": SYM,
        "bids": [[round(entry_px - half - i * step, 8), 500000] for i in range(10)],
        "asks": [[round(entry_px + half + i * step, 8), 500000] for i in range(10)]}
print("dev/book:", requests.post(URL + "/dev/book", json=book, timeout=5).json())

client = BybitV5Client(URL, HmacSigner("o9-fake-key", "o9-fake-secret"))
adapter = BybitAdapter(client, SYM)
ledger = O9Ledger(o9, SYM, start_equity=500)
app = O9LiveApp(strat, PositionSizer(max_order=66000), adapter, ledger, O9Control(o9), SYM)

placed = app.on_bar(e[0] + 5000, entry_px)                       # seam+301ms on the entry bar
print("PLACED:", placed)
print("fx_position:", o9.execute("SELECT side, size, avg_entry FROM fx_position WHERE symbol=%s", (SYM,), fetch=True))
print("app.position() (exchange, via HTTP):", app.position())
print("o9_ledger (o9 OWN record):", o9.execute("SELECT side,qty,entry_px,status FROM o9_ledger WHERE symbol=%s", (SYM,), fetch=True))
print("o9_account (o9 tally):", o9.execute("SELECT equity,trade_count FROM o9_account WHERE acct_id=1", fetch=True))
dev.disconnect(); o9.disconnect()
