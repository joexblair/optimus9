"""rebaseline_fixed_arm.py — the 42d book on the FIXED arm. (Joe 0709)

Every downstream number was fitted on the breach-arm book, which no longer exists:
  fin_unlatch repair  +11.46% net        (A1)
  stack-close cost    -35.0%             (X3)
  first-leg gate      -22% .. -47%       (X3)
  stop optimum        0.90%
  exposure cap        16x

This produces the replacement baseline: entries, exits, per-trade net, stop rate, M1/M2 split, and the
per-leg-vs-stack-close spread — all on the arm as specced (a breach is never an arm).

strand_rescue excluded: gated on the completed SL, cannot run live.
Run:  python3 rebaseline_fixed_arm.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import lr_exit_v2, v2_cascade, v2_walk_ad
from optimus9.config import get_db_config
from optimus9.live.stack_model import PositionStack
from sweep_eval import BASE_BIAS

SPAN_D = 42
COST = 0.20
FEE_BPS = 5.5


def stats(name, net):
    a = np.asarray(net, float)
    if not a.size:
        print("  %-16s n=0" % name); return
    w, l = a[a > 0], a[a <= 0]
    print("  %-16s n=%-5d net=%+9.2f%%  mean=%+.4f%%  win=%4.1f%%  avgW=%+.3f%%  avgL=%+.3f%%"
          % (name, a.size, a.sum(), a.mean(), 100.0 * (a > 0).mean(),
             w.mean() if w.size else 0, l.mean() if l.size else 0))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)

    path_by_bar, seen, ent = {}, set(), []
    for (i, es, bd, cap, src, gb, gr, tk, path) in v2_cascade(W, lr):
        if tk is None or tk in seen:
            continue
        seen.add(tk); path_by_bar[tk] = path; ent.append((int(ts[tk]), es, bd, tk))
    m1 = sum(1 for p in path_by_bar.values() if p == 'M1')
    print("=== 42d on the FIXED arm ===")
    print("entries: %d   (M1 %d / M2 %d)   stop=%.2f%%   arm_bigleg=%s\n" % (len(ent), m1, len(ent) - m1, lr.sl, lr.arm_bigleg))

    rows = []
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= len(px):
            continue
        seg = px[e:x + 1]
        adverse = seg.min() if bd == 1 else seg.max()
        rows.append(dict(e=e, x=x, bd=int(bd), epx=float(epx), xpx=float(xpx), reason=reason,
                         path=path_by_bar.get(e, '?'),
                         net=bd * (xpx - epx) / epx * 100.0 - COST,
                         mae=abs(bd * (adverse - epx) / epx * 100.0)))
    print("=== per-trade net (per-leg exits, cost %.2f%%) ===" % COST)
    stats("ALL", [r['net'] for r in rows])
    for p in ('M1', 'M2'):
        stats(p, [r['net'] for r in rows if r['path'] == p])
    for rs in sorted({r['reason'] for r in rows}):
        stats("reason=" + rs, [r['net'] for r in rows if r['reason'] == rs])
    sl = sum(1 for r in rows if r['reason'] == 'SL')
    print("\n  stopped: %d/%d (%.1f%%)   MAE p50=%.3f%% p90=%.3f%%"
          % (sl, len(rows), 100.0 * sl / max(len(rows), 1),
             np.percentile([r['mae'] for r in rows], 50), np.percentile([r['mae'] for r in rows], 90)))

    # per-leg vs stack-close, unit notional, no governor
    ev = []
    for r in rows:
        ev.append((r['e'], 0, r['bd'], r['epx']))
        ev.append((r['x'], 1, r['bd'], r['xpx']))
    ev.sort(key=lambda z: (z[0], z[1]))
    out = {}
    for sc in (False, True):
        st = PositionStack(fee_bps=FEE_BPS); depth = 0
        for (bar, kind, bd, p) in ev:
            if kind == 0:
                st.add(bd, p, 1.0); depth = max(depth, st.get(bd).n_adds)
            else:
                if st.get(bd) is None:
                    continue
                st.close(bd, p) if sc else st.close(bd, p, qty=1.0)
        out[sc] = (st.realized, depth)
    print("\n=== exit model (unit notional, fee %.1fbps/side) ===" % FEE_BPS)
    print("  per-leg    net=%+8.3f units  depth_max=%d" % (out[False][0], out[False][1]))
    print("  stack-close net=%+8.3f units  depth_max=%d" % (out[True][0], out[True][1]))
    if out[False][0]:
        print("  stack-close cost: %+.1f%%" % (100.0 * (out[True][0] - out[False][0]) / abs(out[False][0])))
    dev.disconnect()


if __name__ == "__main__":
    main()
