"""
cf15_rig.py (Joe 0627→0628) — the lr (latch-release) BACKTEST harness. The mechanic now lives in
optimus9/analysis/lr.py (lr_detect + lr_walk); this builds the window, runs them for the single
06-17→06-22 span, and writes cf15_walk. cf15_superscope.py loops run_window across the 8 windows.
(File/table still carry the cf15 name — Joe's analysing cf15_walk live; rename to lr_* is a flagged cleanup.)
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_detect, lr_walk, lr_exit, lr_config


def ms(dt): return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)


def run_window(db, start_ms, end_ms):
    """Build the window + run lr_detect → lr_walk for (start_ms, end_ms]. Dials from lp_config. Returns rows."""
    cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                        mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
    W = bm.BiasWindow(db, end_ms, cfg=cfg)
    lrcfg = lr_config(db)
    entries = lr_detect(W, lrcfg, start_ms=start_ms)
    walk = lr_walk(W, entries, lrcfg)
    exits = lr_exit(W, entries, lrcfg, curl_fam='s7', exit_on='curl')   # exit time/pct — best config (swappable)
    return [w + (ex[1], round(ex[5], 3)) for w, ex in zip(walk, exits)]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    lrcfg = lr_config(db)
    R1 = ms(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc))
    START = ms(dtm.datetime(2026, 6, 17, tzinfo=timezone.utc))    # window starts 06-17 00:00 (warmup precedes)
    rows = run_window(db, START, R1)
    db.execute('DROP TABLE IF EXISTS cf15_walk')
    db.execute('''CREATE TABLE cf15_walk (trade_ms BIGINT, trade_dt DATETIME, breach_side TINYINT,
                  trade_dir TINYINT, mae FLOAT, mfe FLOAT, mfe_ok TINYINT, mfe_swing_side TINYINT,
                  exit_ms BIGINT, exit_dt DATETIME, exit_pct FLOAT, wob_n INT, floor FLOAT)''')
    db.executemany('INSERT INTO cf15_walk VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                   [r[:8] + (r[9], dtm.datetime.utcfromtimestamp(r[9] / 1000), r[10], lrcfg.wob_n, lrcfg.floor) for r in rows])
    if rows:
        mae = np.array([r[4] for r in rows]); mfe = np.array([r[5] for r in rows])
        ok = np.array([r[6] for r in rows]); side = np.array([r[7] for r in rows])
        print(f"cf15_walk: {len(rows)} trades  ·  06-17 00:00 → 06-22  (WOB_N={lrcfg.wob_n} FLOOR={lrcfg.floor})")
        print(f"  mfe_swing_side (entry on favourable leg):  {side.sum()}/{len(rows)} = {side.mean()*100:.0f}%")
        print(f"  mfe_ok (favourable reached {lrcfg.target}%):       {ok.sum()}/{len(rows)} = {ok.mean()*100:.0f}%")
        print(f"  MAE  median {np.median(mae):.2f}%  mean {mae.mean():.2f}%  max {mae.max():.2f}%")
        print(f"  MFE  median {np.median(mfe):.2f}%  mean {mfe.mean():.2f}%  max {mfe.max():.2f}%")
    else:
        print("cf15_walk: 0 trades")
    db.disconnect()


if __name__ == '__main__':
    main()
