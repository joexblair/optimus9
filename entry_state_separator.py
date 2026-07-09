"""entry_state_separator.py — does a line's STATE at the entry bar predict stop vs signal-exit? (Joe 0709)

The value at the entry bar carries almost nothing (best AUC 0.535 on 63 tests, noise floor 0.53). Joe: the
level is the wrong object. Use the line's history — has it BREACHED (crossed the 85/15 boundary), and has it
BREACHED THEN REVERSED.

Per line, four binary states at the entry bar, all side-signed (es=+1 means the trade is short):
  oob_with        the line is outside the boundary on the trade's own side
  oob_against     outside on the opposite side
  swept_with      travelled DIRECTLY from the opposite extreme to this one, no retrace (oob_2_oob, a latch)
  breach_rev      was outside on the trade's side within `LB` bars AND has since turned back toward the trade

Reported as exit-rate when the state holds vs when it does not, with a split-half check. Baseline exit rate is
~50.1% (1657 signal-exits / 3306). A state that matters moves that number and holds in both halves.

Read-only. Run:  python3 entry_state_separator.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import _mage_rev, _rolling_any, lr_exit_v2, oob_2_oob, v2_walk_ad
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
LB = 60            # bars (5 min) to look back for "was breached"
WOB = 2            # reversal confirmation bars
LINES = ('s2m', 's2M', 's2r', 's3m', 's3M', 's3r', 's4m', 's4M', 's4r', 's5m', 's5M', 's5r',
         's7m', 's7M', 's7r', 's15m', 's15M', 's15r', 's30m', 's30M', 's30r')


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts)
    hi, lo = lr.hi, lr.lo
    ent = v2_walk_ad(W, lr)
    bar_es = {e[3]: e[1] for e in ent}

    bars, lab = [], []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        if reason not in ('SL', 'exit'):
            continue
        bars.append(int(np.searchsorted(ts, int(tms)))); lab.append(1 if reason == 'exit' else 0)
    bars = np.array(bars); y = np.array(lab)
    es = np.array([bar_es.get(k, 0) for k in bars], int)
    half = np.median(bars)
    base = y.mean()
    print("entries=%d  signal-exits=%d  stops=%d  baseline exit-rate=%.1f%%\n" % (y.size, y.sum(), y.size - y.sum(), 100 * base))

    rows = []
    for n in LINES:
        v = np.asarray(W.line(n), float)
        oh, ol = v >= hi, v <= lo                       # outside high / outside low
        dh, dl = oob_2_oob(v, hi, lo)                   # swept directly to high / to low
        rv = _mage_rev(v, WOB)                          # +1 up-turn, -1 down-turn
        wh, wl = _rolling_any(oh, LB), _rolling_any(ol, LB)

        # es=+1 -> trade is SHORT (bd=-1): "the trade's side" of the board is HIGH.
        with_hi = es == 1
        feats = {
            'oob_with':    np.where(with_hi, oh[bars], ol[bars]),
            'oob_against': np.where(with_hi, ol[bars], oh[bars]),
            'swept_with':  np.where(with_hi, dh[bars], dl[bars]),
            'breach_rev':  np.where(with_hi, wh[bars] & (rv[bars] == -1), wl[bars] & (rv[bars] == 1)),
        }
        for fn, m in feats.items():
            m = m.astype(bool)
            nt = int(m.sum())
            if nt < 150 or nt > y.size - 150:
                continue
            et, ef = y[m].mean(), y[~m].mean()
            h1 = y[m & (bars < half)].mean() if (m & (bars < half)).sum() > 40 else np.nan
            h2 = y[m & (bars >= half)].mean() if (m & (bars >= half)).sum() > 40 else np.nan
            rows.append((abs(et - base), n, fn, nt, et, ef, h1, h2))

    rows.sort(reverse=True)
    print("%-6s %-12s %6s %9s %9s %8s %8s  %s" % ("line", "state", "n", "exit% on", "exit% off", "1st", "2nd", "both sides?"))
    for (_, n, fn, nt, et, ef, h1, h2) in rows[:14]:
        same = np.isfinite(h1) and np.isfinite(h2) and (h1 - base) * (h2 - base) > 0
        print("%-6s %-12s %6d %8.1f%% %8.1f%% %7.1f%% %7.1f%%  %s"
              % (n, fn, nt, 100 * et, 100 * ef, 100 * h1, 100 * h2, "yes" if same else "NO"))

    print("\nbaseline %.1f%%.  A state worth using moves exit%% well past it AND holds in both halves." % (100 * base))
    dev.disconnect()


if __name__ == "__main__":
    main()
