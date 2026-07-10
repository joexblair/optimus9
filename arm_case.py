"""arm_case.py — the standard per-hunt report for the ARM DELAY SPEC 0709 walk. (Joe 0710)

Read-only.  Logic lives in arm_walk.py; every read goes through optimus9.analysis.jig.
The per-TF table stops at the apex — rows above it never ran.

  python3 arm_case.py --day 2026-07-09 --hunt 18:08 --es 1
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
    ap.add_argument('--day', default='2026-07-09')
    ap.add_argument('--hunt', required=True, help='a hint; the hunt starts at the s5m crossing at/before it')
    ap.add_argument('--target', default=None, help='the turn, for the +/- min column')
    ap.add_argument('--tfs', default=','.join(str(x) for x in AW.DEFAULT_TFS))
    ap.add_argument('--bands', default=AW.DEFAULT_BANDS)
    ap.add_argument('--m-len', type=int, default=7)
    ap.add_argument('--m-mult', type=float, default=0.50)
    ap.add_argument('--tol', type=float, default=0.0)
    ap.add_argument('--brc-tol', type=float, default=1.0)
    ap.add_argument('--curl-tol', type=int, default=0)
    ap.add_argument('--cancel-on', default='apex', choices=['apex', 's5m'])
    ap.add_argument('--cancel-seam', default='pseam', choices=['bar', 'pseam'])
    ap.add_argument('--wob', type=int, default=1)
    ap.add_argument('--pad', type=int, default=60)
    ap.add_argument('--horizon', type=int, default=30)
    ap.add_argument('--es', type=int, default=0)
    a = ap.parse_args()

    TFS = [int(x) for x in a.tfs.split(',')]
    bands = AW.parse_bands(a.bands)
    t_h = ms(a.day, a.hunt)
    end = t_h + (a.pad + a.horizon + 40) * 60_000

    with Jig(end, hours=24, warmup=90, overrides=AW.overrides(TFS, a.m_len, a.m_mult)) as j:
        ts, px = np.asarray(j.ts, np.int64), j.px
        f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%H:%M:%S')
        s5m = j.causal.line('s5m')
        seam5 = (ts % 300_000) == 0
        sd = lambda k: 1 if s5m[k] >= AW.HI else (-1 if s5m[k] <= AW.LO else 0)

        kk = [int(k) for k in np.flatnonzero(seam5) if ts[k] <= t_h]
        kh = None
        for i in range(len(kk) - 1, 0, -1):
            s = sd(kk[i])
            if s and (a.es == 0 or s == a.es) and sd(kk[i - 1]) != s:
                kh = kk[i]; es = s; break
        if kh is None:
            raise SystemExit('no s5m crossing at/before --hunt')
        ke = min(len(ts) - 1, kh + a.pad * 60 // 5)

        B = AW.Board(j, TFS, es, a.tol, bands, a.wob)
        ev, armed, cancel = AW.walk(B, kh, ke, a.brc_tol, a.curl_tol, a.cancel_on, a.cancel_seam)
        kA = armed[0] if armed else (cancel[0] if cancel else ke - 1)
        top = armed[1] if armed else (ev[-1][1] if ev else TFS[0])

        kt = int(np.searchsorted(ts, ms(a.day, a.target))) if a.target else None
        seg = px[kh:ke]
        ext = kh + (int(np.nanargmax(seg)) if es == 1 else int(np.nanargmin(seg)))

        print(f"\n=== {a.day}  hunt {f(kh)} (s5m={s5m[kh]:.1f}, es={es:+d} -> {'SHORT' if es == 1 else 'LONG'})"
              f"  ·  m={a.m_len}|{a.m_mult}|ohlc4  tol={a.tol}  bands={a.bands}"
              f"  cancel={a.cancel_on}/{a.cancel_seam} ===")
        print(f"price at hunt {px[kh]:.6f} · extreme {f(ext)} {px[ext]:.6f} ({(px[ext]/px[kh]-1)*100:+.2f}%)"
              + (f" · turn {f(kt)} {px[kt]:.6f}" if kt else ""))
        ks = [k for k in np.flatnonzero(seam5) if kh <= k <= kA]
        if ks:
            print(f"s5m @300s seams {f(ks[0])}->{f(ks[-1])}:  "
                  f"{''.join('+' if s5m[k] >= AW.HI else ('-' if s5m[k] <= AW.LO else '.') for k in ks)}   (+hi -lo .IB)")

        g = lambda arr: f(kh + int(arr[0])) if len(arr) else '-'
        h = lambda L: f(min(L)) if L else '-'
        print(f"\n{'tf':>4} {'r pred':>10} {'m OOB':>10} {'r breach':>10} {'r back IB':>10}"
              f" {'r rev 5s':>10} {'r curl':>10} {'HTF pred':>10} {'seam':>6}")
        for i, tf in enumerate(TFS):
            if tf > top:
                break
            r = B.r[tf]; oob = B.oob[tf]
            pk = np.flatnonzero((B.pred[tf][kh:kA + 1] == es) & B.pseam[tf][kh:kA + 1])
            mk = np.flatnonzero(B.moob[tf][kh:kA + 1] == es)
            bk = np.flatnonzero(oob[kh + 1:kA + 1] & ~oob[kh:kA]) + 1
            ibk = np.flatnonzero(~oob[kh + 1:kA + 1] & oob[kh:kA]) + 1
            rev = B.C.reversal(r, a.wob)
            brc = B.first_breach(tf, kh, kA + 1)
            r0 = brc if brc is not None else kh
            rv = np.flatnonzero(rev[r0:kA + 1] == -es)
            rvs = (f(r0 + int(rv[0])) + ('' if brc is not None else '*')) if len(rv) else '-'
            hk = np.flatnonzero(B.pred[TFS[i + 1]][kh:kA + 1] == es) if i + 1 < len(TFS) else []
            print(f"{tf:>4} {g(pk):>10} {g(mk):>10} {g(bk):>10} {g(ibk):>10} {rvs:>10}"
                  f" {h([c for c in B.curl[tf] if kh <= c <= kA]):>10}"
                  f" {(g(hk) if i+1 < len(TFS) else 'n/a'):>10} {B.seam[tf]:>5}s")

        print("\nwalk:")
        for (b, tf, what) in ev:
            print(f"  {f(b)}  TF{tf:<3} {what}")
        if cancel:
            print(f"  {f(cancel[0])}  CANCEL — {cancel[1]}")
            return
        if armed is None:
            print("  NO ARM")
            return
        k, tf, why = armed
        e = px[k]; bd = -es
        sg = px[k:k + a.horizon * 60 // 5]
        mae = (np.nanmax(sg) / e - 1) * 100 if bd < 0 else (1 - np.nanmin(sg) / e) * 100
        mfe = (1 - np.nanmin(sg) / e) * 100 if bd < 0 else (np.nanmax(sg) / e - 1) * 100
        ref = kt if kt else ext
        print(f"  {f(k)}  ARM — {why}   px {e:.6f}  ({(ts[k]-ts[ref])/60000:+.1f} min vs turn)"
              f"  MAE {mae:.2f}  MFE {mfe:.2f}")
        kx = AW.take_profit(B, k, tf, min(len(ts) - 1, k + a.pad * 60 // 5))
        if kx:
            net = bd * (px[kx] - e) / e * 100 - COST
            print(f"  {f(kx)}  TP  — s{tf}m reversed OOB on the far side   px {px[kx]:.6f}"
                  f"   held {(ts[kx]-ts[k])/60000:.0f}m   net {net:+.3f}% (cost {COST}%)")
        else:
            print("  TP — s%dm never reversed OOB on the far side inside the window" % tf)


if __name__ == '__main__':
    main()
