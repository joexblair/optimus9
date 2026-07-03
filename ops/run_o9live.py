"""Run o9-live REALTIME (processes-first, before containers): RealtimeDriver → O9LiveApp → BybitAdapter
→ fakeAPI (live book). Strategy reads the live tape; o9 records in o9_live; fills over HTTP to fakeAPI.
Needs a fakeAPI running (uvicorn services.fakeapi.app:app, O9_LIVE_BOOK=<symbol>, PK_DB_NAME=o9_live)."""
import os
os.environ.update({k: "1" for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS")})
import sys
sys.path.insert(0, "/home/joe/thecodes")
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.exchange import HmacSigner, BybitV5Client, BybitAdapter
from optimus9.live.sizing import PositionSizer
from optimus9.live.strategy import StrategyLoop
from optimus9.live.ledger import O9Ledger
from optimus9.live.app import O9LiveApp
from optimus9.live.driver import RealtimeDriver

FAKEAPI = os.environ.get("O9_FAKEAPI_URL", "http://127.0.0.1:8098")
SYM = os.environ.get("O9_SYMBOL", "FARTCOINUSDT")
MODE = os.environ.get("O9_SIZE_MODE", "fixed")

dev = DatabaseManager(**get_db_config()); dev.connect()          # live tape (own o9_live collector = later)
o9cfg = get_db_config(); o9cfg["database"] = "o9_live"
o9 = DatabaseManager(**o9cfg); o9.connect()
tp = dev.execute("SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s", (SYM,), fetch=True)[0]["tp_pk"]

bcfg = bm.BiasConfig(**BASE_BIAS)
strat = StrategyLoop(dev, bcfg, lr_config(dev), SYM, buffer_hours=6, warmup_hours=24)
adapter = BybitAdapter(BybitV5Client(FAKEAPI, HmacSigner("o9-fake-key", "o9-fake-secret")), SYM)
ledger = O9Ledger(o9, SYM, start_equity=float(os.environ.get("O9_START_EQUITY", "500")))
app = O9LiveApp(strat, PositionSizer(max_order=66000), adapter, ledger, SYM, mode=MODE)

print("o9-live REALTIME · fakeAPI=%s · symbol=%s · mode=%s · equity=$%.0f" % (FAKEAPI, SYM, MODE, ledger.equity()), flush=True)
RealtimeDriver(app, dev, tp).run(max_bars=None)                  # forever — trades when the strategy fires
