"""recon_arm_events.py — do the backtest's ARM events match o9-live's? (Joe 0709)

o9-live logs an `arm` state event at each setup's unlatch bar (v2_mech_events), durably, in o9_state_log
(survives /api/reset). The backtest computes the same arms from v2_cascade over one full-history window.

The two SHOULD agree bar-for-bar: same code, same tape. They cannot, because `arm_delay` forward-scans
[i+1, cap) to decide whether to hold the arm to the s5Mage reversal, and in the backtest `cap` reaches bars
that did not exist when live had to commit (register A2). Live arms at the breach; the backtest re-times it.

This measures that gap directly:
  matched        same bar, same es
  live-only      live armed, the backtest did not  -> arm_delay suppressed/moved it using future bars
  backtest-only  the backtest armed, live did not  -> the re-timed arm bar

Control: `s7r_predict` is r-driven (RSI/STC), exact under the 2000ms read-grace. `s5m` is BB-driven and
desync-sensitive. If s7r_predict matches and s5m does not, the residual is desync, not look-ahead.

Read-only. Run:  python3 recon_arm_events.py
"""
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


def live_events(db, state):
    """-> {(bar_ms, es): meta}.

    o9_state_log.kline_ms is the DECISION INSTANT, not the bar: driver.py:41 `now_ms = ts + bar + delay`,
    where `ts` is the just-closed bar the producer actually acted on. So the acted bar is one bar BELOW the
    floor. Observed offsets are {301: 28868, 2000: 18205, 700: 1261} — the read-grace changed mid-window
    (301ms → 2000ms, the desync fix) — all < one bar, so `floor - BAR` recovers `ts` for every row.

    Getting this wrong produces a ~100% mismatch with every pair exactly 5s apart, which reads as total
    divergence rather than an off-by-one.
    """
    rows = db.execute("SELECT kline_ms, es, meta FROM o9_state_log WHERE state=%s ORDER BY kline_ms",
                      (state,), fetch=True) or []
    return {(int(r['kline_ms']) // BAR * BAR - BAR, int(r['es'] or 0)): (r['meta'] or '') for r in rows}


def report(name, live, back, lo, hi):
    live = {k: v for k, v in live.items() if lo <= k[0] <= hi}
    back = {k: v for k, v in back.items() if lo <= k[0] <= hi}
    m = set(live) & set(back)
    lo_only, bo_only = sorted(set(live) - set(back)), sorted(set(back) - set(live))
    tot = len(set(live) | set(back))
    print("\n=== %s ===" % name)
    print("  live=%d  backtest=%d  matched=%d  (%.1f%% of union)" % (len(live), len(back), len(m), 100.0 * len(m) / max(tot, 1)))
    print("  live-only     %4d  (live fired, backtest did not)" % len(lo_only))
    print("  backtest-only %4d  (backtest fired, live did not)" % len(bo_only))
    for k in lo_only[:5]:
        print("    live-only     %s es=%+d %s" % (f(k[0]), k[1], live[k]))
    for k in bo_only[:5]:
        print("    backtest-only %s es=%+d %s" % (f(k[0]), k[1], back[k]))
    return len(m), len(lo_only), len(bo_only)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    c = get_db_config(); c['database'] = 'o9_live'; o9 = DatabaseManager(**c); o9.connect()

    r = o9.execute("SELECT MIN(kline_ms) a, MAX(kline_ms) b FROM o9_state_log", fetch=True)[0]
    lo, hi = int(r['a']) // BAR * BAR, int(r['b']) // BAR * BAR
    print("live state_log span: %s -> %s  (%.1f h)" % (f(lo), f(hi), (hi - lo) / 3.6e6))

    hours = int((hi - lo) / 3.6e6) + 8
    W = bm.BiasWindow(dev, hi, lookback=hours, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)
    print("backtest window: %s -> %s  (%d bars)" % (f(int(ts[0])), f(int(ts[-1])), len(ts)))

    chain = v2_cascade(W, lr)
    b_arm = {(int(ts[i]), int(es)): src for (i, es, bd, cap, src, gb, gr, tk, path) in chain}
    b_gate = {(int(ts[gb]), int(es)): (gr or '') for (i, es, bd, cap, src, gb, gr, tk, path) in chain if gb is not None}
    b_trade = {(int(ts[tk]), int(es)): (path or '') for (i, es, bd, cap, src, gb, gr, tk, path) in chain if tk is not None}

    report("ARM  (the target)", live_events(o9, 'arm'), b_arm, lo, hi)
    report("s3s4_gate", live_events(o9, 's3s4_gate'), b_gate, lo, hi)
    report("trade", live_events(o9, 'trade'), b_trade, lo, hi)

    print("\n--- src mix ---")
    la = {k: v for k, v in live_events(o9, 'arm').items() if lo <= k[0] <= hi}
    for tag, d in (("live", la), ("backtest", {k: v for k, v in b_arm.items() if lo <= k[0] <= hi})):
        mix = {}
        for v in d.values():
            mix[v] = mix.get(v, 0) + 1
        print("  %-9s %s" % (tag, mix))
    o9.disconnect(); dev.disconnect()


if __name__ == "__main__":
    main()
