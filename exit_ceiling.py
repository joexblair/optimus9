"""exit_ceiling.py — why is the average winner pinned at +1.03%? (Joe 0709)

`avgW` held at +1.03% across 9 stop widths (including no stop), 4 arm samplings, and 6 entry-state filters.
Nothing on the entry side moves it.

Two possibilities:
  (A) the exit takes everything the trade offers -> realized ~= the best excursion inside the trade's life,
      and little is left on the table afterwards. The ceiling is then the MARKET/entry, not the exit.
  (B) the exit fires at a roughly fixed distance -> the winners' distribution is TIGHT around +1.03% and a
      large favourable excursion continues after the exit. The ceiling is the EXIT.

PREDICTION (before the run): (B). Changing the entries and the stop room moved neither the mean nor avgW; if
the ceiling were entry quality or room, one of them would have moved it.

Measures, on the winners only (and the losers as a control):
  realized%          what the trade banked
  MFE_in%            best favourable excursion between entry and exit
  capture            realized / MFE_in   (1.0 = exited at the peak)
  MFE_after(H)%      best favourable excursion from the exit bar to exit+H, for H in {5, 15, 30, 60} minutes
  hold               minutes held

Read-only. Run:  python3 exit_ceiling.py
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
COST = 0.20
HORIZONS_MIN = (5, 15, 30, 60)
BAR_S = 5


def pct(a, q):
    return np.percentile(np.asarray(a, float), q) if len(a) else float('nan')


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    n = len(px)
    ent = v2_walk_ad(W, lr)

    rows = []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= n:
            continue
        seg = px[e:x + 1]
        best_in = seg.max() if bd == 1 else seg.min()
        d = dict(reason=reason, hold=(x - e) * BAR_S / 60.0,
                 realized=bd * (xpx - epx) / epx * 100.0 - COST,
                 mfe_in=abs(bd * (best_in - epx) / epx * 100.0))
        for H in HORIZONS_MIN:
            j = min(n - 1, x + H * 60 // BAR_S)
            fwd = px[x:j + 1]
            best_after = fwd.max() if bd == 1 else fwd.min()
            d['after_%d' % H] = bd * (best_after - xpx) / xpx * 100.0   # + = it kept running our way
        rows.append(d)

    win = [r for r in rows if r['realized'] > 0]
    los = [r for r in rows if r['realized'] <= 0]
    print("42d · breach arm · %d trades · winners %d · losers %d\n" % (len(rows), len(win), len(los)))

    for name, grp in (("WINNERS", win), ("losers", los)):
        rz = [r['realized'] for r in grp]
        mf = [r['mfe_in'] for r in grp]
        cap = [r['realized'] / r['mfe_in'] for r in grp if r['mfe_in'] > 0.05]
        hd = [r['hold'] for r in grp]
        print("%s  n=%d" % (name, len(grp)))
        print("  realized%%   mean %+.3f   p10 %+.3f  p25 %+.3f  p50 %+.3f  p75 %+.3f  p90 %+.3f   std %.3f"
              % (np.mean(rz), pct(rz, 10), pct(rz, 25), pct(rz, 50), pct(rz, 75), pct(rz, 90), np.std(rz)))
        print("  MFE_in%%     mean %+.3f   p50 %+.3f  p90 %+.3f" % (np.mean(mf), pct(mf, 50), pct(mf, 90)))
        print("  capture     mean %.3f    p50 %.3f   (1.0 = exited at the peak)" % (np.mean(cap), pct(cap, 50)))
        print("  hold (min)  p10 %.1f  p50 %.1f  p90 %.1f" % (pct(hd, 10), pct(hd, 50), pct(hd, 90)))
        print("  favourable excursion AFTER the exit:")
        for H in HORIZONS_MIN:
            a = [r['after_%d' % H] for r in grp]
            print("    +%2dmin   mean %+.3f%%   p50 %+.3f%%   p90 %+.3f%%   still-running %.0f%%"
                  % (H, np.mean(a), pct(a, 50), pct(a, 90), 100.0 * np.mean(np.asarray(a) > 0.1)))
        print()
    dev.disconnect()


if __name__ == "__main__":
    main()
