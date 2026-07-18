"""
build_armdelay_walk.py (Joe 0704) — sizing/compounding/maxDD report for the ARM-DELAY stack, now via the
CANONICAL engine producer optimus9.analysis.lr_v2.v2_walk_ad (arm → arm_delay(big-leg → s5Mage reversal) →
gate_open → finisher_v2 both-windows → gcs5M). Exit = lr_exit_v2(predict=False)+strand_rescue with the DB stop
(lp_lr_sl=0.7). Causal/emerging. ONE continuous window (06-12→06-22). 5x dynamic sizing + compounding.
HOLD LIGHTLY — one config/window, un-OOS, cost=0.20% EST. → table armdelay_walk. (Leverage re-tune owed.)
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm; from datetime import timezone
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
def dt(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc)
START, LEV, MAXLOT, RT = 500.0, 5.0, 66000, 0.20
db = DatabaseManager(**get_db_config()); db.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
W = bm.BiasWindow(db, ms('2026-06-22 00:00'), lookback=240, warmup=80, cfg=cfg, lean=True); W._lines.force_emerging = True
ents = sorted(v2_walk_ad(W, lr))
resc = sorted(strand_rescue(W, lr, ents, lr_exit_v2(W, lr, ents, predict=False)), key=lambda x: x[0])
walk = {w[0]: w for w in lr_walk(W, ents, lr)}

acct = START; peak = START; maxdd = 0.0; mineq = START; capped = None; rows = []; nsl = 0
for i, (tms, exms, bd, epx, xpx, r, reason) in enumerate(resc):
    lot = min(MAXLOT, acct * LEV / float(epx))
    if lot >= MAXLOT and capped is None: capped = i
    pnl = lot * float(epx) * (r - RT) / 100.0
    acct += pnl; peak = max(peak, acct); maxdd = max(maxdd, (peak - acct) / peak); mineq = min(mineq, acct)
    nsl += 1 if reason == 'SL' else 0
    rows.append((tms, dt(tms), bd, round(walk[tms][4], 3), round(walk[tms][5], 3), dt(exms), round(r, 3),
                 reason, round(float(epx), 8), int(lot), round(pnl, 2), round(acct, 2)))
db.execute('DROP TABLE IF EXISTS armdelay_walk')
db.execute('''CREATE TABLE armdelay_walk (trade_ms BIGINT, trade_dt DATETIME, trade_dir TINYINT, mae FLOAT,
    mfe FLOAT, exit_dt DATETIME, ret FLOAT, reason VARCHAR(8), entry_px DECIMAL(14,8), lot INT, pnl_usdt FLOAT, equity FLOAT)''')
db.executemany('INSERT INTO armdelay_walk VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
netsum = sum(r - RT for (*_, r, _rr) in resc); wins = sum(1 for (*_, r, _rr) in resc if r - RT > 0)
print('ARM-DELAY walk via v2_walk_ad (stop=%.2f%%, 06-12→06-22, 5x compounding):' % lr.sl)
print('  trades=%d  SL=%d (%.0f%%)  win=%.0f%%  net/trade=%+.3f%%  $%.0f → $%.0f (%.1fx)  maxDD=%.0f%%  min-eq=$%.0f  cap@%s'
      % (len(rows), nsl, 100 * nsl / len(rows), 100 * wins / len(rows), netsum / len(rows), START, acct, acct / START, 100 * maxdd, mineq, capped))
print('  (validation: should ~match the scratch 608 trades / $18,508 / maxDD 19%)')
db.disconnect()
