"""v2walk_ad_pnl.py — PnL reading for the DELAY-ARM shipping stack (v2_walk_ad entries -> lr_exit_v2 -> strand_rescue),
same compounding model as tide_v2_walk (dynamic 5x, 0.20% cost, hard stop via realized MAE), so it's directly
comparable to the greenfield PnL. Sweeps the stop -> profit-max. Run:  python3 v2walk_ad_pnl.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue

SPAN_D = 30
START, LEV, MAX_LOT, COST = 500.0, 5.0, 66000, 0.20


def get_trades():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ent = v2_walk_ad(W, lr)
    resc = strand_rescue(W, lr, ent, lr_exit_v2(W, lr, ent, predict=False))
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    tr = []
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= len(px):
            continue
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * bd
        tr.append(dict(ms=int(tms), epx=float(px[e]), ret=float(seg[-1]), mae=float(np.nanmin(seg)), reason=reason))
    dev.disconnect()
    return sorted(tr, key=lambda t: t['ms'])


def walk(trades, stop):
    acct = START
    for t in trades:
        if acct <= 0:
            return 0.0
        r = -stop if (stop is not None and t['mae'] <= -stop) else t['ret']
        lot = min(MAX_LOT, acct * LEV / t['epx'])
        acct += lot * t['epx'] * (r - COST) / 100.0
    return max(acct, 0.0)


def main():
    tr = get_trades()
    print("DELAY-ARM (v2_walk_ad) PnL — %d trades over %dd, compounding $%d @ %gx, %g%% cost" % (len(tr), SPAN_D, START, LEV, COST))
    stops = [None] + [round(0.2 + 0.05 * k, 2) for k in range(37)]
    best = (None, -1e9)
    print("%-6s %10s %6s %6s" % ("stop", "equity$", "mult", "win%"))
    for s in stops:
        acct = walk(tr, s)
        wins = np.mean([1 if (t['ret'] if (s is None or t['mae'] > -s) else -s) > COST else 0 for t in tr]) if tr else 0
        if acct > best[1]:
            best = (s, acct)
        if s is None or s in (0.3, 0.45, 0.6, 0.8, 1.0, 1.5) or s == best[0]:
            print("%-6s %10.0f %6.2f %6.2f" % ("none" if s is None else "%.2f" % s, acct, acct / START, wins))
    print("\nPROFIT-MAX: stop=%s -> $%.0f (%.2fx)  | no-stop $%.0f (%.2fx)" %
          ("none" if best[0] is None else "%.2f%%" % best[0], best[1], best[1] / START, walk(tr, None), walk(tr, None) / START))
    print("net-profitable (>$%d)? %s" % (START, best[1] > START))


if __name__ == "__main__":
    main()
