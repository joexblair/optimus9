"""arm_spec_confirm.py — the spec'd arm: a breach is never an arm. (Joe 0709)

Rule under test (docs/arm_delay_research.md, base + big-leg clauses):
  s5m breach -> CANDIDATE. Not an arm.
  trigger = the s5m reversal. At that bar:
      big leg visible -> HOLD; trigger becomes the s5Mage reversal.
      no big leg      -> arm FIRES at the s5m reversal.
  Further breaches while pending on that side: same excursion, same candidate.
  Opposite-side s5m breach cancels.

Checks:
  1. The six live breach arms (20:40:40 ... 21:28:40) are GONE.
  2. Window-invariance, tested not assumed: run the SAME arm_delay on windows truncated at a sample of bars and
     require the arm set on [0, T] to equal the full-window arm set restricted to [0, T]. A per-bar state machine
     must satisfy this. Any disagreement means something still reads the future.

Run:  python3 arm_spec_confirm.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_arm, arm_delay

f = lambda m: dtm.datetime.fromtimestamp(m / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
SIX = ['07-06 20:40:40', '07-06 20:51:10', '07-06 21:22:45', '07-06 21:23:00', '07-06 21:23:45', '07-06 21:28:40']


class Trunc:
    """A view of W truncated at bar T — every line and ts clipped. Reproduces the live window edge exactly."""
    def __init__(self, W, T):
        self._W, self._T = W, T
        self.ts = W.ts[:T + 1]

    def line(self, name):
        return np.asarray(self._W.line(name), float)[:self._T + 1]

    def __getattr__(self, k):
        return getattr(self._W, k)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    end = int(dtm.datetime(2026, 7, 9, 7, 50, tzinfo=timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, end, lookback=72, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)

    full = arm_delay(W, lr, v2_arm(W, lr))
    fbars = sorted({int(ts[a[0]]) for a in full})
    print("full-window arms: %d\n" % len(full))

    lo = int(dtm.datetime(2026, 7, 6, 20, 30, tzinfo=timezone.utc).timestamp() * 1000)
    hi = int(dtm.datetime(2026, 7, 6, 21, 35, tzinfo=timezone.utc).timestamp() * 1000)
    win = [f(b) for b in fbars if lo <= b <= hi]
    print("=== 1. arms in 20:30-21:35 on 07-06 ===")
    print("  %s" % (win or "none"))
    survivors = [s for s in SIX if s in win]
    print("\n  the six breach arms: %s" % ("ALL GONE" if not survivors else "SURVIVORS %s" % survivors))
    print("  21:29:40 present: %s" % ('07-06 21:29:40' in win))

    print("\n=== 2. window-invariance (tested, not assumed) ===")
    n = len(ts)
    sample = [a[0] for a in full][::max(1, len(full) // 12)][:12]
    bad = 0
    for T in sample:
        WT = Trunc(W, T)
        armsT = {int(ts[a[0]]) for a in arm_delay(WT, lr, v2_arm(WT, lr))}
        expect = {b for b in fbars if b <= int(ts[T])}
        if armsT != expect:
            bad += 1
            only_t, only_f = sorted(armsT - expect), sorted(expect - armsT)
            print("  T=%s  MISMATCH  trunc-only=%d full-only=%d" % (f(int(ts[T])), len(only_t), len(only_f)))
            for x in (only_t[:2] + only_f[:2]):
                print("      %s" % f(x))
    print("  sampled %d truncation points; mismatches=%d  -> %s"
          % (len(sample), bad, "WINDOW-INVARIANT" if bad == 0 else "NOT invariant: something reads the future"))
    dev.disconnect()


if __name__ == "__main__":
    main()
