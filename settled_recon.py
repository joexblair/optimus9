"""settled_recon.py — verify the delay 301->700ms fix on SETTLED bars (Joe 0708). For each logged arm whose bar is
old enough to be finalized (we detect 'settled' by r-line diff ~0, since RSI/STC don't move on late ticks), diff the
live-logged m/M (BB) values vs a stable backtest. Split pre-restart (301ms) vs post-restart (700ms). If 700ms closed
the late-tick desync, post-restart settled bars have materially smaller m/M gaps. Run:  python3 settled_recon.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS

RESTART = int(dtm.datetime(2026, 7, 8, 8, 15, tzinfo=timezone.utc).timestamp() * 1000)   # loop reloaded onto delay=700
R_SETTLED = 0.5                                                # r-line diff below this ⇒ bar finalized (clean to compare)


def main():
    o9c = get_db_config(); o9c['database'] = 'o9_live'; o9 = DatabaseManager(**o9c); o9.connect()
    dev = DatabaseManager(**get_db_config()); dev.connect()
    bcfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(dev)
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=10, warmup=6, cfg=bcfg, lean=True); tsW = np.asarray(W.ts)
    arms = o9.execute("SELECT DISTINCT kline_ms FROM o9_state_log WHERE state='arm' AND kline_ms BETWEEN %s AND %s ORDER BY kline_ms",
                      (now - 4 * 3600 * 1000, now - 45 * 60 * 1000), fetch=True)
    pre, post, unsettled = [], [], 0
    for a in arms:
        KL = int(a['kline_ms']); tgt = KL - (KL % 5000)
        j = int(np.searchsorted(tsW, tgt))
        if j >= len(tsW) or int(tsW[j]) != tgt:
            continue
        sl = o9.execute("SELECT sl_id FROM o9_state_log WHERE kline_ms=%s AND state='arm' ORDER BY sl_id LIMIT 1", (KL,), fetch=True)[0]['sl_id']
        live = {r['line']: float(r['val']) for r in o9.execute("SELECT line,val FROM o9_state_log_line WHERE sl_id=%s", (sl,), fetch=True)}
        rmax = max((abs(float(np.asarray(W.line(l), float)[j]) - live[l]) for l in live if l[-1] == 'r'), default=9)
        if rmax > R_SETTLED:
            unsettled += 1; continue                          # bar not finalized yet — skip
        mm = [abs(float(np.asarray(W.line(l), float)[j]) - live[l]) for l in live if l[-1] in 'mM']
        (pre if KL < RESTART else post).append(np.mean(mm))
    md = lambda x: float(np.median(x)) if x else float('nan')
    print("=== settled-bar m/M desync: 301ms vs 700ms (skipped %d unsettled) ===" % unsettled)
    print("PRE-restart (301ms): %2d settled bars, median m/M diff = %.3f" % (len(pre), md(pre)))
    print("POST-restart (700ms):%2d settled bars, median m/M diff = %.3f" % (len(post), md(post)))
    if pre and post:
        print("VERDICT: 700ms %s the desync (%.0f%% of the 301ms gap)" %
              ("CLOSED" if md(post) < 0.5 * md(pre) else "reduced" if md(post) < md(pre) else "did NOT close",
               100 * md(post) / md(pre)))
    o9.disconnect(); dev.disconnect()


if __name__ == "__main__":
    main()
