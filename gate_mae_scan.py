"""gate_mae_scan.py — Stage 1 of Joe's arm-to-gate challenge (0707).

Score every s3s4 gate-open by MAE (bd=-es signed) to the next >=0.9% swing; rank best-MAE (gate opened nearest the
turn). Capture the process window [proc_start, gate_open] where proc_start = the arm bar that started this gate
(first stab; refinable to the first-predict/rtr bar). Writes `gate_mae` (pk_optimizer) for Stage 3 to target. NO pnl.
Run:  python3 gate_mae_scan.py
"""
import time, bisect, datetime as dtm
from datetime import timezone
import numpy as np

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.compute.swing_detect import find_pivots
from optimus9.analysis.lr_v2 import v2_arm, gate_open

SWING_PCT = 0.9


def _dt(ms):
    return dtm.datetime.fromtimestamp(int(ms) / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    lr = lr_config(dev)
    W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS))
    ts = np.asarray(W.ts); px = np.asarray(W.px, float)
    days = (int(ts[-1]) - int(ts[0])) / 86400000.0
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [pp[0] + v0 for pp in find_pivots(px[v0:], SWING_PCT)]

    rows = []
    for (i, es, bd, open_k, reason, cap) in gate_open(W, lr, v2_arm(W, lr)):
        j = bisect.bisect_right(piv, int(open_k))
        if j >= len(piv):
            continue
        fav = -es * (px[open_k:piv[j] + 1] - px[open_k]) / px[open_k] * 100.0
        if not fav.size:
            continue
        mae, mfe = float(np.nanmin(fav)), float(np.nanmax(fav))
        span_s = (int(ts[open_k]) - int(ts[i])) / 1000.0
        rows.append((int(ts[open_k]), int(ts[i]), int(es), reason, round(mae, 4), round(mfe, 4), round(span_s, 0)))

    dev.execute("DROP TABLE IF EXISTS gate_mae")
    dev.execute("""CREATE TABLE gate_mae (
        id INT AUTO_INCREMENT PRIMARY KEY, gate_ms BIGINT, proc_start_ms BIGINT, gate_dt DATETIME, proc_start_dt DATETIME,
        es TINYINT, reason VARCHAR(2), mae FLOAT, mfe FLOAT, span_s INT, KEY k_mae (mae))""")
    dev.executemany("INSERT INTO gate_mae (gate_ms,proc_start_ms,gate_dt,proc_start_dt,es,reason,mae,mfe,span_s) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [(g, p, _dt(g), _dt(p), es, r, mae, mfe, sp) for (g, p, es, r, mae, mfe, sp) in rows])

    maes = np.array([r[4] for r in rows]); spans = np.array([r[6] for r in rows])
    print("scored %d gate-opens (%dd, %d swings)\n" % (len(rows), round(days), len(piv)))
    print("MAE distribution: p10=%+.3f p25=%+.3f MED=%+.3f p75=%+.3f  (best = closest to 0)" % (
        np.percentile(maes, 10), np.percentile(maes, 25), np.median(maes), np.percentile(maes, 75)))
    print("arm->open span: median=%.0fs  p75=%.0fs" % (np.median(spans), np.percentile(spans, 75)))
    print("\nTOP-15 best-MAE gates (tightest adverse):")
    print("%-19s %-19s %3s %5s %8s %8s %7s" % ("gate_open", "proc_start(arm)", "es", "rsn", "MAE", "MFE", "span_s"))
    for g, p, es, r, mae, mfe, sp in sorted(rows, key=lambda x: -x[4])[:15]:
        print("%-19s %-19s %+3d %5s %+8.3f %+8.3f %7.0f" % (_dt(g), _dt(p), es, r, mae, mfe, sp))
    dev.disconnect()


if __name__ == "__main__":
    main()
