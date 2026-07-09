"""arm_fix_confirm.py — do the six live breach arms disappear under the causal big-leg test? (Joe 0709)

The six, all es=+1 src=s5m, across a rising leg 0.16381 -> 0.16753 on 07-06:
  20:40:40  20:51:10  21:22:45  21:23:00  21:23:45  21:28:40
The backtest armed once, at 21:29:40 / 0.16712, after the s5Mage reversal.

Three arm machines, same window, same lines:
  OLD-full   the shipped scan `range(i+1, cap)` over a full-history window   (what the backtest did)
  OLD-live   the same scan with cap := i+1                                    (what o9-live did: range empty
             => kc None => always fires at the breach. This reproduces the 115.)
  NEW        `cond[i]` only; da is None -> drop                               (the causal form)

NEW must be identical under both window regimes — that is the whole point. We check it explicitly rather than
assume it (window-invariance is a treacherous test: arm_delay's look-ahead survived it because `cap` bounded the
scan INSIDE the data).

Read-only; imports nothing from the patched arm_delay so old and new can be compared side by side.
Run:  python3 arm_fix_confirm.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_arm, bigleg_gate, _mage_rev

BAR = 5000
f = lambda m: dtm.datetime.fromtimestamp(m / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
SIX = ['07-06 20:40:40', '07-06 20:51:10', '07-06 21:22:45', '07-06 21:23:00', '07-06 21:23:45', '07-06 21:28:40']
BACKTEST_ARM = '07-06 21:29:40'


def old_full(setups, ch, cl, rev5M):
    out = []
    for (i, es, bd, cap, src) in setups:
        cond = ch if es == 1 else cl
        kc = next((k for k in range(i + 1, cap) if cond[k]), None)
        if kc is None:
            out.append(i); continue
        da = next((k for k in range(kc, cap) if rev5M[k] == bd), None)
        out.append(da if da is not None else i)
    return out


def old_live(setups, ch, cl, rev5M):
    """cap := i+1 — the live window ends at the arm bar. range(i+1, i+1) is empty => always the breach arm."""
    return [i for (i, es, bd, cap, src) in setups]


def new(setups, ch, cl, rev5M, cap_live=False):
    out = []
    for (i, es, bd, cap, src) in setups:
        cond = ch if es == 1 else cl
        c = (i + 1) if cap_live else cap
        if not cond[i]:
            out.append(i); continue
        da = next((k for k in range(i, c) if rev5M[k] == bd), None)
        if da is None:
            continue
        out.append(da)
    return out


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    lo = int(dtm.datetime(2026, 7, 6, 20, 30, tzinfo=timezone.utc).timestamp() * 1000)
    hi = int(dtm.datetime(2026, 7, 6, 21, 35, tzinfo=timezone.utc).timestamp() * 1000)
    end = int(dtm.datetime(2026, 7, 9, 7, 50, tzinfo=timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, end, lookback=72, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)
    setups = v2_arm(W, lr)
    ch, cl = bigleg_gate(W, lr)
    rev5M = _mage_rev(W.line('s5M'), lr.arm_wob)

    win = lambda bars: sorted({f(int(ts[b])) for b in bars if lo <= int(ts[b]) <= hi})
    of, ol = win(old_full(setups, ch, cl, rev5M)), win(old_live(setups, ch, cl, rev5M))
    nf, nl = win(new(setups, ch, cl, rev5M, False)), win(new(setups, ch, cl, rev5M, True))

    print("arms in the 20:30-21:35 window on 07-06\n")
    for tag, arms in (("OLD-full  (backtest)", of), ("OLD-live  (cap=i+1)", ol),
                      ("NEW  full window", nf), ("NEW  cap=i+1 (live)", nl)):
        print("  %-22s %d: %s" % (tag, len(arms), arms))

    print("\n--- the six live breach arms ---")
    for s in SIX:
        print("  %s  old-live=%-5s  NEW-live=%-5s  NEW-full=%-5s"
              % (s, s in ol, s in nl, s in nf))
    survivors = [s for s in SIX if s in nl or s in nf]
    print("\n  six cancelled under NEW: %s" % ("YES — all six gone" if not survivors else "NO — survivors %s" % survivors))
    print("  backtest arm %s present under NEW: full=%s live=%s"
          % (BACKTEST_ARM, BACKTEST_ARM in nf, BACKTEST_ARM in nl))

    print("\n--- window-invariance of NEW (the claim, tested not assumed) ---")
    a, b = new(setups, ch, cl, rev5M, False), new(setups, ch, cl, rev5M, True)
    same = sorted(a) == sorted(b)
    print("  NEW full-window arms=%d   NEW live-cap arms=%d   identical=%s" % (len(a), len(b), same))
    if not same:
        only_f, only_l = sorted(set(a) - set(b)), sorted(set(b) - set(a))
        print("  full-only=%d  live-only=%d   (a residual means something still reads the future)"
              % (len(only_f), len(only_l)))
        for x in only_f[:4]:
            print("    full-only  %s" % f(int(ts[x])))
        for x in only_l[:4]:
            print("    live-only  %s" % f(int(ts[x])))

    print("\n--- whole-window arm counts ---")
    print("  OLD-full=%d  OLD-live=%d  NEW=%d" % (len(old_full(setups, ch, cl, rev5M)),
                                                  len(old_live(setups, ch, cl, rev5M)), len(a)))
    dev.disconnect()


if __name__ == "__main__":
    main()
