"""settled_recon2.py — robust era-split recon (Joe 0708). The logged kline_ms suffix = the seam grace (301/700/2000ms),
so we can compare the m/M desync per delay era directly. Per-bar focused method (trusted), settled bars only
(r-diff small + >45min old), aligned only. If a longer grace closes the write-vs-read race, higher-delay eras show
smaller m/M gaps. Run:  python3 settled_recon2.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS


def main():
    o9c = get_db_config(); o9c['database'] = 'o9_live'; o9 = DatabaseManager(**o9c); o9.connect()
    dev = DatabaseManager(**get_db_config()); dev.connect()
    bcfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(dev)
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=12, warmup=6, cfg=bcfg, lean=True); tsW = np.asarray(W.ts)
    arms = o9.execute("SELECT DISTINCT kline_ms FROM o9_state_log WHERE state='arm' AND kline_ms>=%s ORDER BY kline_ms",
                      (now - 5 * 3600 * 1000,), fetch=True)
    eras = {}
    for a in arms:
        KL = int(a['kline_ms'])
        if now - KL < 45 * 60 * 1000:                             # too fresh — skip
            continue
        era = KL % 5000; tgt = KL - era
        j = int(np.searchsorted(tsW, tgt))
        if j >= len(tsW) or int(tsW[j]) != tgt:
            continue
        sl = o9.execute("SELECT sl_id FROM o9_state_log WHERE kline_ms=%s AND state='arm' ORDER BY sl_id LIMIT 1", (KL,), fetch=True)[0]['sl_id']
        live = {r['line']: float(r['val']) for r in o9.execute("SELECT line,val FROM o9_state_log_line WHERE sl_id=%s", (sl,), fetch=True)}
        rmax = max((abs(float(np.asarray(W.line(l), float)[j]) - live[l]) for l in live if l[-1] == 'r'), default=9)
        if rmax > 0.3:
            continue                                              # not settled — skip
        mm = np.mean([abs(float(np.asarray(W.line(l), float)[j]) - live[l]) for l in live if l[-1] in 'mM'])
        eras.setdefault(era, []).append(mm)
    print("=== m/M desync by grace era (settled bars, %s UTC) ===" % dtm.datetime.now(timezone.utc).strftime('%H:%M'))
    for era in sorted(eras):
        v = eras[era]
        print("  grace %4dms : %2d settled bars, median m/M diff = %.3f  max = %.3f" % (era, len(v), float(np.median(v)), max(v)))
    if 2000 in eras and (301 in eras or 700 in eras):
        base = np.median(eras.get(301) or eras.get(700))
        print("VERDICT: 2000ms grace m/M = %.0f%% of the shorter-grace gap" % (100 * np.median(eras[2000]) / base))
    o9.disconnect(); dev.disconnect()


if __name__ == "__main__":
    main()
