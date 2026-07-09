"""arm_gap_anatomy.py — WHY does live fire 115 arms the backtest never books? (Joe 0709)

Two questions, two tests.

Q1  Mechanism. Hypothesis: live re-evaluates every bar with cap<=T+1, so at the breach bar `i` it has not yet
    seen the big-leg gate `kc` and arms there. Later, once kc+da are inside its window, arm_delay re-times the
    SAME setup to `da` and live logs that too. The full-window backtest only ever keeps the final verdict `da`.
    => every live-only arm should be the BREACH arm of a setup the backtest arms LATER, at da.
    Test: for each live-only arm, distance to the next MATCHED arm of the same es. Should be small, positive,
    and bounded by the arm's cap. A flat/huge/negative distribution refutes it.

Q2  Was the gap collected before the read-grace was raised (301ms -> 2000ms, the desync fix)? If the live-only
    arms are concentrated in the 301ms era, the gap is (partly) desync, not arm_delay. o9_state_log.kline_ms
    carries the grace in its low bits: MOD(kline_ms, 5000) in {301, 700, 2000}.

Read-only. Run:  python3 arm_gap_anatomy.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_cascade

BAR = 5000
f = lambda m: dtm.datetime.fromtimestamp(m / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    c = get_db_config(); c['database'] = 'o9_live'; o9 = DatabaseManager(**c); o9.connect()

    rows = o9.execute("SELECT kline_ms, es, meta FROM o9_state_log WHERE state='arm' ORDER BY kline_ms",
                      fetch=True) or []
    live = {}                                                    # (bar, es) -> grace
    for r in rows:
        k = int(r['kline_ms'])
        live[(k // BAR * BAR - BAR, int(r['es'] or 0))] = k % BAR

    r = o9.execute("SELECT MIN(kline_ms) a, MAX(kline_ms) b FROM o9_state_log", fetch=True)[0]
    lo, hi = int(r['a']) // BAR * BAR, int(r['b']) // BAR * BAR
    W = bm.BiasWindow(dev, hi, lookback=int((hi - lo) / 3.6e6) + 8, warmup=48,
                      cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)
    chain = v2_cascade(W, lr)
    back = {(int(ts[i]), int(es)): (int(ts[cap - 1]) if cap - 1 < len(ts) else None)
            for (i, es, bd, cap, src, gb, gr, tk, path) in chain}

    live = {k: v for k, v in live.items() if lo <= k[0] <= hi}
    only = sorted(set(live) - set(back))
    matched = sorted(set(live) & set(back))
    print("live arms=%d  backtest arms=%d  matched=%d  live-only=%d\n" % (len(live), len(back), len(matched), len(only)))

    # ── Q2: which read-grace era did the live-only arms land in? ─────────────
    def mix(keys):
        m = {}
        for k in keys:
            m[live[k]] = m.get(live[k], 0) + 1
        return dict(sorted(m.items()))
    print("=== Q2 · read-grace era (MOD(kline_ms,5000)) ===")
    print("  ALL live arms  : %s" % mix(live))
    print("  live-ONLY arms : %s" % mix(only))
    print("  matched arms   : %s" % mix(matched))
    tot_only, tot_all = len(only), len(live)
    for g in sorted({v for v in live.values()}):
        n_all = sum(1 for k in live if live[k] == g)
        n_only = sum(1 for k in only if live[k] == g)
        print("  grace %4dms : %4d arms, %4d live-only  (%.1f%% of that era's arms are unmatched)"
              % (g, n_all, n_only, 100.0 * n_only / max(n_all, 1)))
    print("  overall unmatched rate: %.1f%%" % (100.0 * tot_only / max(tot_all, 1)))

    # ── Q1: is each live-only arm the BREACH arm of a setup the backtest arms later? ──
    print("\n=== Q1 · distance from a live-only arm to the NEXT matched arm, same es ===")
    by_es = {}
    for (b, es) in matched:
        by_es.setdefault(es, []).append(b)
    for es in by_es:
        by_es[es].sort()
    d, orphan = [], 0
    for (b, es) in only:
        arr = by_es.get(es, [])
        j = np.searchsorted(arr, b, side='right')
        if j >= len(arr):
            orphan += 1; continue
        d.append((arr[j] - b) // BAR)
    if d:
        D = np.array(d)
        print("  n=%d  orphans(no later matched arm)=%d" % (len(D), orphan))
        print("  bars: p10=%d p50=%d p90=%d max=%d   (seconds: p50=%ds p90=%ds)"
              % (np.percentile(D, 10), np.percentile(D, 50), np.percentile(D, 90), D.max(),
                 int(np.percentile(D, 50)) * 5, int(np.percentile(D, 90)) * 5))
        print("  within 90min (1080 bars): %.1f%%" % (100.0 * (D <= 1080).mean()))
    print("\n  first 6 live-only arms and their next matched arm:")
    for (b, es) in only[:6]:
        arr = by_es.get(es, [])
        j = np.searchsorted(arr, b, side='right')
        nxt = f(arr[j]) if j < len(arr) else "—"
        print("    %s es=%+d grace=%4d  ->  next matched %s" % (f(b), es, live[(b, es)], nxt))
    o9.disconnect(); dev.disconnect()


if __name__ == "__main__":
    main()
