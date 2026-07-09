"""exit_asymmetry.py — where does the bleed live? (Joe 0709)

LIVE (o9_trade_archive, 13 trades, ~4.7h):
    6 x SL   gross -0.92% .. -0.99%   (losers ride to the full stop)
    7 x exit gross -0.22% .. +0.36%   (winners cut short)
  -> reward:risk ~ 1:3. Needs >75% win to break even. Live nets -$144.

Q1  Does the BACKTEST show the same asymmetry? If its winners run much further than +0.3%, or it stops out
    far less often, the bleed is localised to the EXIT with one number instead of a theory.
Q2  Joe: "is fin_unlatch harmful? if there is a grouping of high MAE then it might be." -> split every
    metric by finisher path M1 (fin_unlatch, arm-gated) vs M2 (fin_gate, s3s4-gated).

MAE/MFE are REALIZED (worst/best adverse-favourable excursion between the entry and exit bars, bd-signed),
computed from W.px -- not a forward scan past the exit, so no hindsight beyond the trade's own life.

strand_rescue is excluded (register B3: gated on the completed SL, cannot run live).
Read-only. Run:  python3 exit_asymmetry.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_cascade, lr_exit_v2

SPAN_D = 42
COST = 0.20


def pct(a):
    a = np.asarray(a, float)
    return a if a.size else np.array([0.0])


def block(name, net, mae, mfe):
    net, mae, mfe = pct(net), pct(mae), pct(mfe)
    w, l = net[net > 0], net[net <= 0]
    rr = (w.mean() / abs(l.mean())) if (w.size and l.size and l.mean() != 0) else float('nan')
    print("  %-22s n=%-5d net=%+8.2f%%  win=%4.1f%%  avgW=%+.3f%%  avgL=%+.3f%%  R:R=1:%.2f"
          % (name, net.size, net.sum(), 100.0 * (net > 0).mean(), w.mean() if w.size else 0,
             l.mean() if l.size else 0, (1 / rr) if rr == rr and rr else float('nan')))
    print("  %-22s MAE p50=%.3f%% p90=%.3f%% max=%.3f%%   MFE p50=%.3f%% p90=%.3f%%"
          % ("", np.percentile(mae, 50), np.percentile(mae, 90), mae.max(),
             np.percentile(mfe, 50), np.percentile(mfe, 90)))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)

    path_by_tk, seen, ent = {}, set(), []
    for (i, es, bd, cap, src, gb, gr, tk, path) in v2_cascade(W, lr):
        if tk is None or tk in seen:
            continue
        seen.add(tk); path_by_tk[tk] = path; ent.append((int(ts[tk]), es, bd, tk))
    print("entries: %d  (M1 %d / M2 %d)  stop=%.2f%%\n"
          % (len(ent), sum(1 for p in path_by_tk.values() if p == 'M1'),
             sum(1 for p in path_by_tk.values() if p == 'M2'), lr.sl))

    rows = []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= len(px):
            continue
        seg = px[e:x + 1]
        adverse = (seg.min() if bd == 1 else seg.max())
        favour = (seg.max() if bd == 1 else seg.min())
        rows.append(dict(path=path_by_tk.get(e, '?'), reason=reason,
                         net=bd * (xpx - epx) / epx * 100.0 - COST,
                         mae=abs(bd * (adverse - epx) / epx * 100.0),
                         mfe=abs(bd * (favour - epx) / epx * 100.0)))

    G = lambda f: ([r['net'] for r in rows if f(r)], [r['mae'] for r in rows if f(r)], [r['mfe'] for r in rows if f(r)])

    print("=== Q1: exit-reason mix + magnitude asymmetry (42d, cost %.2f%%) ===" % COST)
    reasons = sorted({r['reason'] for r in rows})
    for rs in reasons:
        n = sum(1 for r in rows if r['reason'] == rs)
        print("  %-10s %5d  (%.1f%%)" % (rs, n, 100.0 * n / len(rows)))
    print()
    block("ALL", *G(lambda r: True))
    for rs in reasons:
        block("reason=" + rs, *G(lambda r, rs=rs: r['reason'] == rs))

    print("\n=== Q2: is fin_unlatch harmful? M1 (arm-gated) vs M2 (post-s3s4-gate) ===")
    for p in ('M1', 'M2'):
        block(p, *G(lambda r, p=p: r['path'] == p))
    for p in ('M1', 'M2'):
        sub = [r for r in rows if r['path'] == p]
        if not sub:
            continue
        sl = sum(1 for r in sub if r['reason'] == 'SL')
        hi = sum(1 for r in sub if r['mae'] >= lr.sl)
        print("  %s: stopped=%d/%d (%.1f%%)   MAE>=stop(%.2f%%)=%d (%.1f%%)"
              % (p, sl, len(sub), 100.0 * sl / len(sub), lr.sl, hi, 100.0 * hi / len(sub)))
    dev.disconnect()


if __name__ == "__main__":
    main()
