"""entry_separator.py — is anything knowable AT the entry bar that predicts stop vs signal-exit? (Joe 0709)

The 42d causal book (breach arm) loses because it wins 42.1% against a 50.4% breakeven. Half the trades die at
the stop; the other half exit on signal at +0.83% and 84% win. The deficit is trade SELECTION.

For every entry, take each of the 21 cascade lines at the entry bar, side-signed (multiplied by es, so +1 means
"with the trade's direction"), and score how well it separates the two outcome groups.

Score = AUC (probability a random signal-exit outranks a random stop). 0.50 = no information. Reported both
directions, so a low AUC is as interesting as a high one.

MULTIPLE COMPARISONS: 21 lines x 3 forms = 63 tests. Under the null, the best of 63 lands near AUC 0.53 by
chance on n~3300. Anything below that is noise. Also reports a 2-fold time split (first half / second half of
the window) -- a real separator holds in both.

Read-only. Run:  python3 entry_separator.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import lr_exit_v2, v2_walk_ad
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
LINES = ('s2m', 's2M', 's2r', 's3m', 's3M', 's3r', 's4m', 's4M', 's4r', 's5m', 's5M', 's5r',
         's7m', 's7M', 's7r', 's15m', 's15M', 's15r', 's30m', 's30M', 's30r')


def auc(x, y):
    """P(x[y==1] > x[y==0]), ties at 0.5. Rank-based, NaN-safe."""
    ok = np.isfinite(x)
    x, y = x[ok], y[ok]
    if y.sum() == 0 or y.sum() == y.size:
        return float('nan')
    r = np.argsort(np.argsort(x)) + 1.0
    n1, n0 = y.sum(), y.size - y.sum()
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2.0) / (n1 * n0)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)
    ent = v2_walk_ad(W, lr)
    bar_es = {e[3]: e[1] for e in ent}

    e_bar, lab = [], []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        k = int(np.searchsorted(ts, int(tms)))
        if reason not in ('SL', 'exit'):
            continue
        e_bar.append(k); lab.append(1 if reason == 'exit' else 0)
    e_bar = np.array(e_bar); y = np.array(lab)
    print("entries scored: %d   signal-exits=%d   stops=%d\n" % (y.size, y.sum(), y.size - y.sum()))

    es = np.array([bar_es.get(k, 0) for k in e_bar], float)
    half = np.median(e_bar)
    rows = []
    for n in LINES:
        v = np.asarray(W.line(n), float)[e_bar]
        forms = {
            '%s (signed)' % n: es * v,               # + = with the trade's direction
            '%s |dist 50|' % n: np.abs(v - 50.0),    # how far from the middle of the board
            '%s raw' % n: v,
        }
        for fn, x in forms.items():
            a = auc(x, y)
            a1 = auc(x[e_bar < half], y[e_bar < half])
            a2 = auc(x[e_bar >= half], y[e_bar >= half])
            rows.append((abs(a - 0.5), fn, a, a1, a2))
    rows.sort(reverse=True)
    print("%-20s %7s %8s %8s   %s" % ("feature", "AUC", "1st half", "2nd half", "both halves same side?"))
    for (_, fn, a, a1, a2) in rows[:12]:
        same = (a1 - 0.5) * (a2 - 0.5) > 0
        print("%-20s %7.3f %8.3f %8.3f   %s" % (fn, a, a1, a2, "yes" if same else "NO"))

    best = rows[0]
    print("\nnoise floor: best of %d tests on n=%d lands near AUC 0.53 by chance." % (len(rows), y.size))
    print("best observed: %.3f (%s)  ->  %s" % (best[2], best[1],
          "above the floor" if abs(best[2] - 0.5) > 0.03 else "INSIDE the noise floor"))
    dev.disconnect()


if __name__ == "__main__":
    main()
