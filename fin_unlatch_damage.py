"""fin_unlatch_damage.py — how many M1 trades did the backtest authorise with a bar the entry never saw?

A1 (docs/causal_lookahead_register.md). fin_unlatch gates on an UNORDERED `.any()` over the box
[i-fin_lb, i+fin_fwd] -- which reaches fin_fwd bars PAST the unlatch -- then enters at the FIRST q15 >= i.

  e  = first q15 at/after the unlatch bar i          (the entry)
  P30 = the q30 fires inside the box

  CAUSAL      : some q30 fires at k <= e  -> the info existed by the entry bar.
  CONTAMINATED: every q30 fire in the box is > e -> the entry was authorised by a bar in its own future.

Live consequence of a contaminated trade: at T=e the box is clamped to cap<=T+1, so no q30 is visible and
the `.any()` is False -> no trade. Later, at T=j30, fin_unlatch returns e, and strategy.py:106 only acts when
tk==T -> tk=e != T -> DROPPED. So `contaminated` == the exact set of trades o9-live silently never takes,
while the backtest books every one of them.

Sibling fin_gate returns max(j15,j30) and is causal. Spec sec.4 ("walk FORWARD with 2x30s tolerance for a
late line") describes fin_gate's semantics, not fin_unlatch's.

Read-only, no engine change. Run:  python3 fin_unlatch_damage.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_arm, arm_delay, gate_open, s_qualify, fin_unlatch, fin_gate

SPAN_D = 42


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000   # pin: frozen tape
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)
    print("window %dd  fin_lb=%d bars (%ds)  fin_fwd=%d bars (%ds)"
          % (SPAN_D, lr.fin_lb, lr.fin_lb * 5, lr.fin_fwd, lr.fin_fwd * 5))

    # rebuild v2_cascade's own inputs so we see fin_unlatch's exact arguments
    setups = v2_arm(W, lr)
    if lr.arm_bigleg:
        setups = arm_delay(W, lr, setups)
    opens = {o[0]: o for o in gate_open(W, lr, setups)}
    q15h, q15l = s_qualify(W, lr, 's15m', 's15M', 's15r', lr.s15r_lb)
    q30h, q30l = s_qualify(W, lr, 's30m', 's30M', 's30r', lr.s30r_lb)

    m1 = clean = dirty = m2 = 0
    lags, seen = [], set()
    dirty_rows = []
    for (i, es, bd, cap, src) in setups:
        q15, q30 = (q15h, q30h) if es == 1 else (q15l, q30l)
        tk = fin_unlatch(q15, q30, i, cap, lr.fin_lb, lr.fin_fwd)
        if tk is None:                                        # M2 path (or no trade) — fin_gate is causal
            o = opens.get(i)
            if o is not None and fin_gate(q15, q30, o[3], cap) is not None:
                m2 += 1
            continue
        if tk in seen:                                        # v2_walk_ad dedups by bar
            continue
        seen.add(tk); m1 += 1

        w0, w1 = max(0, i - lr.fin_lb), min(cap, i + lr.fin_fwd + 1)
        p30 = np.flatnonzero(q30[w0:w1]) + w0                 # q30 fires inside the box
        if p30.size and int(p30.min()) <= tk:
            clean += 1                                        # evidence existed by the entry bar
        else:
            dirty += 1
            j30 = int(p30.min())                              # first q30, strictly after the entry
            lags.append(j30 - tk)
            dirty_rows.append((ts[tk], es, j30 - tk))

    tot = clean + dirty
    print("\n=== M1 (fin_unlatch) trades, %dd ===" % SPAN_D)
    print("  M1 trades      : %d   (M2/fin_gate trades: %d — causal by construction)" % (m1, m2))
    print("  causal         : %d  (%.1f%%)" % (clean, 100.0 * clean / max(tot, 1)))
    print("  CONTAMINATED   : %d  (%.1f%%)   <- live silently drops these" % (dirty, 100.0 * dirty / max(tot, 1)))
    if lags:
        L = np.array(lags)
        print("\n  authorising q30 lands AFTER the entry by (bars of 5s):")
        print("    min=%d  p50=%d  p90=%d  max=%d   (fin_fwd cap = %d)"
              % (L.min(), int(np.percentile(L, 50)), int(np.percentile(L, 90)), L.max(), lr.fin_fwd))
        print("\n  first 8 contaminated entries:")
        for (t, es, lag) in dirty_rows[:8]:
            print("    %s  es=%+d  q30 arrives %2d bars (%3ds) later"
                  % (dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc), es, lag, lag * 5))
    dev.disconnect()


if __name__ == "__main__":
    main()
