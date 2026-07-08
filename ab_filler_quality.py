"""ab_filler_quality.py — is filler_invisible ON actually BETTER, not just different? (Joe 0708, step a)
For OFF and ON, build the world consistently (entries AND exits on that tape), resolve trades on the SAME
full-grid price path (self.base is kept intact either way), and score entry QUALITY: win%, MAE (median/mean/
tail=CVaR10), MFE, and compounding PnL (dynamic5x, no-stop + profit-max stop). Better entries = lower MAE,
higher win, higher PnL. Run on both the backtest (30d) and o9/live (8h) configs. Read-only.
Run:  python3 ab_filler_quality.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue

START, LEV, MAX_LOT, COST = 500.0, 5.0, 66000, 0.20


def trades_for(dev, lr, now, lookback, warmup, filler):
    W = bm.BiasWindow(dev, now, lookback=lookback, warmup=warmup, cfg=bm.BiasConfig(**BASE_BIAS),
                      lean=True, filler_invisible=filler)
    ent = v2_walk_ad(W, lr)
    resc = strand_rescue(W, lr, ent, lr_exit_v2(W, lr, ent, predict=False))
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    tr = []
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= len(px):
            continue
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * bd
        tr.append((float(px[e]), float(seg[-1]), float(np.nanmin(seg)), float(np.nanmax(seg))))
    return tr


def pnl(tr, stop):
    acct = START
    for (epx, ret, mae, mfe) in tr:
        if acct <= 0:
            return 0.0
        r = -stop if (stop is not None and mae <= -stop) else ret
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - COST) / 100.0
    return max(acct, 0.0)


def score(tr):
    rets = np.array([t[1] for t in tr]); maes = np.array([t[2] for t in tr]); mfes = np.array([t[3] for t in tr])
    win = float(np.mean(rets > COST))
    tail = float(np.mean(np.sort(maes)[:max(1, len(maes) // 10)]))          # CVaR10 of MAE (worst decile)
    best = max([pnl(tr, s) for s in [None] + [round(0.2 + 0.05 * k, 2) for k in range(37)]])
    return dict(n=len(tr), win=win, mae_med=float(np.median(maes)), mae_mean=float(np.mean(maes)),
                mae_tail=tail, mfe_med=float(np.median(mfes)), nostop=pnl(tr, None), best=best)


def ab(dev, lr, now, lookback, warmup, label):
    off, on = score(trades_for(dev, lr, now, lookback, warmup, False)), score(trades_for(dev, lr, now, lookback, warmup, True))
    print("\n=== %s ===" % label)
    print("  %-10s %8s %8s %9s %9s %9s %10s %10s" % ("filler", "n", "win%", "MAEmed", "MAEmean", "MAEtail", "PnL nostop", "PnL best"))
    for tag, s in (("OFF", off), ("ON ", on)):
        print("  %-10s %8d %7.1f%% %9.3f %9.3f %9.3f %10.0f %10.0f" %
              (tag, s["n"], 100 * s["win"], s["mae_med"], s["mae_mean"], s["mae_tail"], s["nostop"], s["best"]))
    better = (on["win"] >= off["win"]) + (on["mae_mean"] >= off["mae_mean"]) + (on["mae_tail"] >= off["mae_tail"]) + (on["best"] >= off["best"])
    print("  → ON improves %d/4 (win, MAEmean, MAEtail, PnL) — %s" %
          (better, "ON cleaner" if better >= 3 else "OFF cleaner" if better <= 1 else "mixed/neutral"))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    lr = lr_config(dev)
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    ab(dev, lr, now, 30 * 24, 48, "BACKTEST path (30d full window)")
    ab(dev, lr, now, 8, 6, "o9/LIVE path (8h buffer / 6h warmup)")
    dev.disconnect()


if __name__ == "__main__":
    main()
