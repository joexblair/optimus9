"""stop_sweep_6wk.py — sweep the hard-stop (MAE cap) over a 6-week window (Joe 0708). For each candidate stop S,
a trade whose realized MAE <= -S is CUT at -S; otherwise it keeps its natural (reversal-exit) return. Report the
S that maximizes total captured return — both additive (sum of net %) and compounding equity — plus how many
trades it rescues (caps) vs how many winners it clips (stopped-but-would-have-recovered). 'Rescue' = a losing
trade cut shallower; 'clip' = a trade that dipped to -S but recovered to a positive return we now forfeit.
Read-only. Run:  python3 stop_sweep_6wk.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue

SPAN_D = 42
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
        tr.append(dict(epx=float(px[e]), ret=float(seg[-1]), mae=float(np.nanmin(seg)), mfe=float(np.nanmax(seg))))
    dev.disconnect()
    return tr, lr.sl


def stats(tr, S):
    net_add = 0.0; acct = START; rescued = clipped = stopped = 0
    for t in tr:
        if S is not None and t['mae'] <= -S:
            stopped += 1
            eff = -S
            if t['ret'] > -S:      # would have ended better than -S → we CLIPPED a (partial) recovery
                clipped += 1
            else:                  # ended worse than -S → we RESCUED it (cut the deeper loss)
                rescued += 1
        else:
            eff = t['ret']
        net_add += eff - COST
        if acct > 0:
            acct += min(MAX_LOT, acct * LEV / t['epx']) * t['epx'] * (eff - COST) / 100.0
    return net_add, max(acct, 0.0), stopped, rescued, clipped


def main():
    tr, cur_sl = get_trades()
    grid = [None] + [round(0.2 + 0.05 * k, 2) for k in range(37)]
    print("=== stop sweep, %d trades / %dw (current lr.sl=%.2f%%) ===" % (len(tr), SPAN_D // 7, cur_sl))
    print("%-6s %10s %9s %8s %8s %8s" % ("stop%", "net_add%", "equity$", "stopped", "rescued", "clipped"))
    best_add = (None, -1e9); best_cmp = (None, -1e9)
    for S in grid:
        na, eq, st, rs, cl = stats(tr, S)
        if na > best_add[1]:
            best_add = (S, na)
        if eq > best_cmp[1]:
            best_cmp = (S, eq)
        if S is None or S in (0.5, 0.7, 0.9, 1.1, 1.5, 2.0) or S == cur_sl:
            print("%-6s %10.1f %9.0f %8d %8d %8d" % ("none" if S is None else "%.2f" % S, na, eq, st, rs, cl))
    print("\nBEST additive-net : stop=%s   BEST compounding: stop=%s   (current=%.2f%%)" %
          ("none" if best_add[0] is None else "%.2f%%" % best_add[0],
           "none" if best_cmp[0] is None else "%.2f%%" % best_cmp[0], cur_sl))


if __name__ == "__main__":
    main()
