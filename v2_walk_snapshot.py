"""v2_walk_snapshot.py — A/B the closed-mode alignment stamp (Joe 0709).

BEFORE = ALIGN_CLOSE_STAMP off (the faulted model: align_to_base maps every mid-window base bar onto its
OWN still-forming HTF bar, handing it that window's whole-span high/low/close = its own future).
AFTER  = ALIGN_CLOSE_STAMP on  (base bar sees the last COMPLETED HTF bar; Pine lookahead_off).

Two diffs, coarse->fine:
  1. LINE ARRAYS for all 21 cascade lines. The direct test. If none move, nothing downstream can.
  2. v2_walk_ad ENTRIES (count / bars / sides). The end-to-end test Joe asked for.

PREDICTION (stated before running, so it can be falsified): ZERO delta on both. Every cascade line is
value_mode='emerging', and the emerging path uses lookahead_resample (groupby cummax/cummin), never
resample+align_to_base. If anything moves, the "only closed lines are affected" scope claim is WRONG.

Read-only. Run:  python3 v2_walk_snapshot.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.indicator_computer import IndicatorComputer as IC
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_walk_ad

SPAN_D = 42
LINES = ('s2m', 's2M', 's2r', 's3m', 's3M', 's3r', 's4m', 's4M', 's4r', 's5m', 's5M', 's5r',
         's7m', 's7M', 's7r', 's15m', 's15M', 's15r', 's30m', 's30M', 's30r')


def snapshot(dev, now, label):
    """Build a fresh window under the CURRENT flag value and return (lines, entries)."""
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    lines = {n: np.asarray(W.line(n), float) for n in LINES}
    ent = v2_walk_ad(W, lr)
    print("  %-6s ALIGN_CLOSE_STAMP=%-5s bars=%d entries=%d" % (label, IC.ALIGN_CLOSE_STAMP, len(W.ts), len(ent)))
    return lines, ent


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    # Pin `now` ONE HOUR into the past. The collector keeps writing 5s bars, so a live `now` lets the
    # second window pick up a bar the first never saw -> a phantom shape delta that has nothing to do
    # with the flag. An hour back, the tape in range is frozen.
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    print("window: %dd, now=%d (pinned 1h back: tape in range is frozen)" % (SPAN_D, now))

    IC.ALIGN_CLOSE_STAMP = False
    l_off, e_off = snapshot(dev, now, "BEFORE")
    IC.ALIGN_CLOSE_STAMP = True
    l_on, e_on = snapshot(dev, now, "AFTER")
    IC.ALIGN_CLOSE_STAMP = False                                    # never leave it flipped

    print("\n=== 1. LINE ARRAYS (the direct test) ===")
    moved = []
    for n in LINES:
        a, b = l_off[n], l_on[n]
        if a.shape != b.shape:
            moved.append((n, -1, 'shape %s vs %s' % (a.shape, b.shape))); continue
        both_nan = np.isnan(a) & np.isnan(b)
        diff = ~(both_nan | np.isclose(a, b, rtol=0, atol=1e-12, equal_nan=True))
        nd = int(diff.sum())
        if nd:
            moved.append((n, nd, 'max|d|=%.6g' % np.nanmax(np.abs(a[diff] - b[diff]))))
    if moved:
        print("  LINES MOVED -> the scope claim is WRONG:")
        for n, nd, extra in moved:
            print("    %-6s bars_differing=%-8s %s" % (n, nd, extra))
    else:
        print("  all %d cascade lines BIT-IDENTICAL (prediction held)" % len(LINES))

    print("\n=== 2. v2_walk_ad ENTRIES (end-to-end) ===")
    print("  BEFORE %d entries | AFTER %d entries | delta %+d" % (len(e_off), len(e_on), len(e_on) - len(e_off)))
    b_off, b_on = {e[0]: e for e in e_off}, {e[0]: e for e in e_on}
    only_off = sorted(set(b_off) - set(b_on)); only_on = sorted(set(b_on) - set(b_off))
    shared = sorted(set(b_off) & set(b_on))
    side_flip = [t for t in shared if b_off[t][1] != b_on[t][1]]
    print("  identical bars=%d | only-BEFORE=%d | only-AFTER=%d | side flips=%d"
          % (len(shared), len(only_off), len(only_on), len(side_flip)))
    for t in only_off[:5]:
        print("    dropped by fix: %s es=%d" % (dtm.datetime.fromtimestamp(t / 1000, timezone.utc), b_off[t][1]))
    for t in only_on[:5]:
        print("    added by fix  : %s es=%d" % (dtm.datetime.fromtimestamp(t / 1000, timezone.utc), b_on[t][1]))

    verdict = (not moved) and not (only_off or only_on or side_flip)
    print("\nVERDICT: %s" % ("NO CHANGE — closed-stamp fix does not touch the lr book (as predicted)"
                             if verdict else "CHANGE DETECTED — the lr book DOES depend on the closed path"))
    dev.disconnect()


if __name__ == "__main__":
    main()
