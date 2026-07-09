"""entry_state_filter_ab.py — do the breach-state rules pay? (Joe 0709)

entry_state_separator.py found three states that shift the exit-rate and hold across both halves of 42d:
  s7M oob_against  n=228  exit 38.6% vs 51.0%   (7-min Mage outside the boundary AGAINST the trade)
  s4r oob_with     n=500  exit 44.8% vs 51.1%   (4-min r already outside WITH the trade)
  s7M oob_with     n=806  exit 55.2% vs 48.5%

Exit-rate is not money. This scores the actual book under each rule and their combination:
  R1  reject s7M oob_against
  R2  reject s4r oob_with
  R3  keep ONLY s7M oob_with
  R1+R2, R1+R2+R3

Reported: kept n, net %, mean/trade, win %, breakeven win %, stop rate — and the same on each half of the
window, because a rule that only works in one half is a fit.

84 states were screened. On n=3306 several will clear a threshold by chance. The split-half columns are the
guard, not the headline.

Read-only. Run:  python3 entry_state_filter_ab.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import lr_exit_v2, oob_2_oob, v2_walk_ad
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

SPAN_D = 42
COST = 0.20


def score(name, net, sl, bars, half):
    a = np.asarray(net, float)
    if a.size < 30:
        print("  %-24s n=%-5d (too few)" % (name, a.size)); return
    w, l = a[a > 0], a[a <= 0]
    be = 100.0 * abs(l.mean()) / (w.mean() + abs(l.mean())) if w.size and l.size else float('nan')
    b = np.asarray(bars)
    m1, m2 = a[b < half], a[b >= half]
    print("  %-24s n=%-5d net=%+8.2f%%  mean=%+.4f%%  win=%4.1f%%  be=%4.1f%%  stop=%4.1f%%   halves %+.4f%% / %+.4f%%"
          % (name, a.size, a.sum(), a.mean(), 100.0 * (a > 0).mean(), be,
             100.0 * np.mean(sl), m1.mean() if m1.size else 0, m2.mean() if m2.size else 0))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts = np.asarray(W.ts); hi, lo = lr.hi, lr.lo
    ent = v2_walk_ad(W, lr)
    bar_es = {e[3]: e[1] for e in ent}

    s7M = np.asarray(W.line('s7M'), float)
    s4r = np.asarray(W.line('s4r'), float)

    rec = []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        k = int(np.searchsorted(ts, int(tms)))
        es = bar_es.get(k, 0)
        if es == 0:
            continue
        wh = es == 1                                              # trade side is the HIGH side of the board
        rec.append(dict(k=k, net=bd * (xpx - epx) / epx * 100.0 - COST, sl=1 if reason == 'SL' else 0,
                        s7M_against=(s7M[k] <= lo) if wh else (s7M[k] >= hi),
                        s7M_with=(s7M[k] >= hi) if wh else (s7M[k] <= lo),
                        s4r_with=(s4r[k] >= hi) if wh else (s4r[k] <= lo)))
    half = np.median([r['k'] for r in rec])
    print("42d · breach arm · cost %.2f%%\n" % COST)

    def run(name, keep):
        sub = [r for r in rec if keep(r)]
        score(name, [r['net'] for r in sub], [r['sl'] for r in sub], [r['k'] for r in sub], half)

    run("baseline", lambda r: True)
    run("R1 reject s7M_against", lambda r: not r['s7M_against'])
    run("R2 reject s4r_with", lambda r: not r['s4r_with'])
    run("R3 keep only s7M_with", lambda r: r['s7M_with'])
    run("R1+R2", lambda r: not r['s7M_against'] and not r['s4r_with'])
    run("R1+R2+R3", lambda r: not r['s7M_against'] and not r['s4r_with'] and r['s7M_with'])
    dev.disconnect()


if __name__ == "__main__":
    main()
