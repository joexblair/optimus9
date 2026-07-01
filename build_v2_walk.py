"""
build_v2_walk.py (Joe 0701) — canonical v2_walk builder. The SHIPPING stack over the full window:
  entries (v2_walk) → cascade (lr_exit_v2, predict=False) → strand_rescue → per-trade equity map.
Sizing = DYNAMIC: proportional lots (notional = LEVERAGE × account) capped at MAX_LOT FARTCOIN coins, with
COMPOUNDING PnL — losses shrink the next lot (the survival mechanism), so it ramps to the 66k cap as the
account grows, then holds. Scenario params below → hoist to a config table later (see [[thresholds_constants]]).
Cost is the 0.20% estimate; the REAL round-trip (fees + Bybit order-book slippage) comes from o9-live.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2, strand_rescue

# --- scenario params (→ config table later) ---
R1_END = '2026-06-22 00:00'      # window end (bias_window anchor)
START_USDT = 500.0               # opening balance
LEVERAGE = 5.0                   # notional / account — Joe: safety-first 5x
MAX_LOT = 66000                  # FARTCOIN coin cap
RT_COST = 0.20                   # % round-trip (fees + slip, EST; real from o9-live Bybit order-book walk)
PREDICT = False                  # cascade predict arm (the s5m=0.4 lean)


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
def dt(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc)


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, ms(R1_END), cfg=cfg); lrcfg = lr_config(db)
ent = v2_walk(W, lrcfg)
resc = sorted(strand_rescue(W, lrcfg, ent, lr_exit_v2(W, lrcfg, ent, predict=PREDICT)), key=lambda x: x[0])
walk = {w[0]: w for w in lr_walk(W, ent, lrcfg)}

db.execute('DROP TABLE IF EXISTS v2_walk')
db.execute('''CREATE TABLE v2_walk (trade_ms BIGINT, trade_dt DATETIME, trade_dir TINYINT, mae FLOAT, mfe FLOAT,
    exit_dt DATETIME, exit_pct FLOAT, reason VARCHAR(8), entry_px DECIMAL(14,8), lot INT, notional FLOAT,
    pnl_usdt FLOAT, equity FLOAT)''')
acct = START_USDT; rows = []; capped_at = None
for i, (tms, exms, bd, epx, xpx, r, reason) in enumerate(resc):
    lot = min(MAX_LOT, acct * LEVERAGE / float(epx))
    if lot >= MAX_LOT and capped_at is None:
        capped_at = i
    notional = lot * float(epx)
    pnl = notional * (r - RT_COST) / 100.0
    acct += pnl
    w = walk[tms]
    rows.append((tms, dt(tms), bd, round(w[4], 3), round(w[5], 3), dt(exms), r, reason,
                 round(float(epx), 8), int(lot), round(notional, 2), round(pnl, 2), round(acct, 2)))
db.executemany('INSERT INTO v2_walk VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
print('v2_walk built: %d rows | $%.0f → $%.0f (%.1fx) | L=%gx cap=%dk@trade%s cost=%g%% RT'
      % (len(rows), START_USDT, acct, acct / START_USDT, LEVERAGE, MAX_LOT // 1000, capped_at, RT_COST))
db.disconnect()
