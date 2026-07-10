"""arm_batch.py — run the ARM DELAY SPEC 0709 walk over EVERY s5m hunt in a window. (Joe 0710)

Read-only.  One row per hunt: where it armed, on which TF, where the TP fired, and what the trade did.

  python3 arm_batch.py --day 2026-07-08 --from 00:00 --to 12:00
  python3 arm_batch.py --day 2026-07-08 --from 00:00 --to 12:00 --bands 7:2,14:4,999:6 --detail
"""
import argparse
import datetime as dtm
from datetime import timezone

import numpy as np

from optimus9.analysis.jig import Jig
import arm_walk as AW

COST = 0.20


def ms(day, hm):
    return int(dtm.datetime.strptime(f'{day} {hm}', '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).timestamp() * 1000)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--day', default='2026-07-08')
    ap.add_argument('--from', dest='t0', default='00:00')
    ap.add_argument('--to', dest='t1', default='12:00')
    ap.add_argument('--tfs', default=','.join(str(x) for x in AW.DEFAULT_TFS))
    ap.add_argument('--bands', default=AW.DEFAULT_BANDS)
    ap.add_argument('--m-len', type=int, default=7)
    ap.add_argument('--m-mult', type=float, default=0.50)
    ap.add_argument('--tol', type=float, default=0.0)
    ap.add_argument('--brc-tol', type=float, default=1.0)
    ap.add_argument('--curl-tol', type=int, default=0)
    ap.add_argument('--tp-cap', type=int, default=120, help='minutes to look for the TP before giving up')
    ap.add_argument('--cancel-on', default='apex', choices=['apex', 's5m', 'none'])
    ap.add_argument('--no-permission', action='store_true', help='s5m permission drop does not cancel')
    ap.add_argument('--cancel-seam', default='bar', choices=['bar', 'pseam'])
    ap.add_argument('--arm-mode', default='both', choices=['both', 'latch'])
    ap.add_argument('--allib', default='ladder', choices=['ladder', 's5', 'off'])
    ap.add_argument('--latch', action='store_true', help='two-stage latch instead of the same-bar backstop')
    ap.add_argument('--tp-scan', action='store_true', help='TP on the highest OOB r above the arm TF')
    ap.add_argument('--detail', action='store_true')
    a = ap.parse_args()

    TFS = [int(x) for x in a.tfs.split(',')]
    bands = AW.parse_bands(a.bands)
    t0, t1 = ms(a.day, a.t0), ms(a.day, a.t1)
    end = t1 + (a.tp_cap + 30) * 60_000

    with Jig(end, hours=24, warmup=90, overrides=AW.overrides(TFS, a.m_len, a.m_mult)) as j:
        ts, px = np.asarray(j.ts, np.int64), j.px
        f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%H:%M:%S')
        s5m = j.causal.line('s5m')
        seam5 = (ts % 300_000) == 0
        sd = lambda k: 1 if s5m[k] >= AW.HI else (-1 if s5m[k] <= AW.LO else 0)

        ks = [int(k) for k in np.flatnonzero(seam5)]
        hunts = [(ks[i], sd(ks[i])) for i in range(1, len(ks))
                 if sd(ks[i]) and sd(ks[i]) != sd(ks[i - 1]) and t0 <= ts[ks[i]] <= t1]

        print(f"\n{a.day} {a.t0}-{a.t1}   {len(hunts)} s5m hunts   bands {a.bands}   tol {a.tol}   "
      f"cancel={a.cancel_on}/{a.cancel_seam} perm={not a.no_permission}   cost {COST}%")
        print(f"{'hunt':>9} {'es':>3} {'arm':>9} {'apex':>5} {'why':>18} {'tp':>9} {'held':>7}"
              f" {'net%':>8} {'MAE':>6} {'MFE':>6}")
        rows = []
        for (kh, es) in hunts:
            B = AW.board(j, TFS, es, a.tol, bands)
            ke = min(len(ts) - 1, kh + a.tp_cap * 60 // 5)
            ev, armed, cancel = AW.walk(B, kh, ke, a.brc_tol, a.curl_tol, a.cancel_on, a.cancel_seam, not a.no_permission, a.latch, a.arm_mode, a.allib)
            if a.detail:
                print(f"  --- hunt {f(kh)} es={es:+d} ---")
                for (b, tf, what) in ev:
                    print(f"      {f(b)}  TF{tf:<3} {what}")
            if armed is None:
                why = cancel[1] if cancel else 'no arm'
                print(f"{f(kh):>9} {es:+3d} {'-':>9} {'-':>5} {why[:18]:>18} {'-':>9} {'-':>7}"
                      f" {'-':>8} {'-':>6} {'-':>6}")
                continue
            kA, tf, why = armed
            xt = AW.tp_tf(B, kA, tf) if a.tp_scan else tf
            kx = AW.take_profit(B, kA, xt, min(len(ts) - 1, kA + a.tp_cap * 60 // 5))
            e = px[kA]; bd = -es
            if kx is None:
                net = held = None
            else:
                net = bd * (px[kx] - e) / e * 100 - COST
                held = (ts[kx] - ts[kA]) / 60000.0
            sg = px[kA:kA + 30 * 60 // 5]
            mae = (np.nanmax(sg) / e - 1) * 100 if bd < 0 else (1 - np.nanmin(sg) / e) * 100
            mfe = (1 - np.nanmin(sg) / e) * 100 if bd < 0 else (np.nanmax(sg) / e - 1) * 100
            print(f"{f(kh):>9} {es:+3d} {f(kA):>9} {tf:>5} {why[:18]:>18} "
                  f"{(f(kx) if kx else '-'):>9} {(f'{held:.0f}m' if held else '-'):>7}"
                  f" {(f'{net:+.3f}' if net is not None else '-'):>8} {mae:6.2f} {mfe:6.2f}")
            if net is not None:
                rows.append((net, mae, mfe, tf, held, xt))

        if rows:
            n = np.array([r[0] for r in rows])
            print(f"\n{len(rows)} trades   net mean {n.mean():+.4f}%   total {n.sum():+.2f}%"
                  f"   win {100*(n > 0).mean():.1f}%   MAE p50 {np.median([r[1] for r in rows]):.2f}%"
                  f"   held p50 {np.median([r[4] for r in rows]):.0f}m")
            from collections import Counter
            print("apex TFs: " + "  ".join(f"TF{t}x{c}" for t, c in sorted(Counter(r[3] for r in rows).items())))
            print("TP TFs:   " + "  ".join(f"TF{t}x{c}" for t, c in sorted(Counter(r[5] for r in rows).items())))


if __name__ == '__main__':
    main()
