"""arm_apex_v2.py — the spec rule: no HTF prediction -> stop climbing, arm on the apex's r curl. (Joe 0710)

Per bar k, all reads causal, everything through the jig:
  apex   : start at TFS[0]; while the next TF up has predicted (at any bar <= k), climb.
  arm    : the apex's r coarse-curls against es at its TF/4 seam AND the TF above it has not predicted by k.
  cancel : s5m returns IB or flips side (permission).

Two curl origins, printed side by side:
  --origin hunt     r curl searched from the hunt bar
  --origin breach   r curl searched from the apex r's IB->OOB crossing (no arm if it never breaches)

Read-only.  python3 arm_apex_v2.py --day 2026-07-08 --hunt 02:30 --target 03:13 --es 1
"""
import argparse
import datetime as dtm
from datetime import timezone

import numpy as np

from optimus9.analysis.jig import Jig

HI, LO = 85.0, 15.0
DAY = 86_400_000


def ms(day, hm):
    return int(dtm.datetime.strptime(f'{day} {hm}', '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).timestamp() * 1000)


def seam_mask(ts, seam_ms, anchor):
    return ((ts - anchor) % seam_ms) == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--day', default='2026-07-08')
    ap.add_argument('--hunt', required=True)
    ap.add_argument('--target', required=True)
    ap.add_argument('--tfs', default='6,7,8,9,10,11,12,14,16,19,22')
    ap.add_argument('--m-len', type=int, default=7)
    ap.add_argument('--m-mult', type=float, default=0.50)
    ap.add_argument('--tol', type=float, default=0.0)
    ap.add_argument('--pad', type=int, default=25)
    ap.add_argument('--horizon', type=int, default=30)
    ap.add_argument('--es', type=int, default=0)
    a = ap.parse_args()

    TFS = [int(x) for x in a.tfs.split(',')]
    t_h, t_t = ms(a.day, a.hunt), ms(a.day, a.target)
    end = t_t + (a.pad + a.horizon + 10) * 60_000
    ov = {}
    for tf in TFS:
        s = tf * 60
        ov[f's{tf}r'] = (s, ('k', 5, 6, 5, 'close'), 'emerging')
        ov[f's{tf}m'] = (s, ('bb', a.m_len, a.m_mult, 'ohlc4'), 'emerging')
        ov[f's{tf}Mage'] = (s, ('bb', 37, 0.7, 'ohlc4'), 'emerging')

    with Jig(end, hours=24, warmup=90, overrides=ov) as j:
        C = j.causal
        ts, px = np.asarray(j.ts, np.int64), j.px
        anchor = (int(ts[0]) // DAY) * DAY
        f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%H:%M:%S')

        s5m = C.line('s5m')
        sm = seam_mask(ts, 300_000, anchor)
        kh = int(np.searchsorted(ts, t_h))
        if a.es:
            es = a.es
            cand = [k for k in np.flatnonzero(sm) if k >= kh and (s5m[k] >= HI if es == 1 else s5m[k] <= LO)]
        else:
            cand = [k for k in np.flatnonzero(sm) if k >= kh and (s5m[k] >= HI or s5m[k] <= LO)]
            es = 1 if s5m[int(cand[0])] >= HI else -1
        kh = int(cand[0])
        ke = int(np.searchsorted(ts, t_t + a.pad * 60_000))
        seg = px[kh:ke]
        ext = kh + (int(np.nanargmax(seg)) if es == 1 else int(np.nanargmin(seg)))

        # per-bar "has predicted by now", per TF (causal cumulative OR inside the hunt)
        PRED = {tf: np.maximum.accumulate((C.predict_set(f's{tf}', tol=a.tol, maj='Mage')[kh:ke] == es).astype(np.int8))
                for tf in TFS}
        BR = {}
        for tf in TFS:
            r = C.line(f's{tf}r')
            oob = (r >= HI) if es == 1 else (r <= LO)
            x = np.flatnonzero(oob[kh + 1:ke] & ~oob[kh:ke - 1]) + 1
            BR[tf] = kh + int(x[0]) if len(x) else None
        CURL = {tf: sorted(int(np.searchsorted(ts, t))
                           for t in C.curl(*C.coarse(f's{tf}r', (tf * 60 // 4) * 1000), -es))
                for tf in TFS}

        print(f"\n=== {a.day}  hunt {f(kh)}  es={es:+d} -> {'SHORT' if es == 1 else 'LONG'}"
              f"  extreme {f(ext)} {px[ext]:.6f}  ·  tol={a.tol} ===")

        for origin in ('hunt', 'breach'):
            apex = TFS[0]; armed = None; climbs = []
            for k in range(kh, ke):
                if sm[k] and not (s5m[k] >= HI if es == 1 else s5m[k] <= LO):
                    break                                                    # permission dropped
                while True:
                    i = TFS.index(apex)
                    if i + 1 >= len(TFS) or not PRED[TFS[i + 1]][k - kh]:
                        break
                    apex = TFS[i + 1]; climbs.append((k, apex))
                i = TFS.index(apex)
                htf = TFS[i + 1] if i + 1 < len(TFS) else None
                if htf is not None and PRED[htf][k - kh]:
                    continue
                if not PRED[apex][k - kh]:
                    continue                                                 # apex itself must have predicted
                lo_bar = kh if origin == 'hunt' else BR[apex]
                if lo_bar is None:
                    continue
                if k in CURL[apex] and k >= lo_bar:
                    armed = (k, apex); break

            if armed is None:
                print(f"  origin={origin:<7} NO ARM   (apex ended at TF{apex})")
                continue
            k, tf = armed
            e = px[k]; sg = px[k:k + a.horizon * 60 // 5]; bd = -es
            mae = (np.nanmax(sg) / e - 1) * 100 if bd < 0 else (1 - np.nanmin(sg) / e) * 100
            mfe = (1 - np.nanmin(sg) / e) * 100 if bd < 0 else (np.nanmax(sg) / e - 1) * 100
            print(f"  origin={origin:<7} ARM {f(k)}  apex TF{tf}  px {e:.6f}"
                  f"  ({(ts[k]-ts[ext])/60000:+.1f} min vs extreme)  MAE {mae:.2f}  MFE {mfe:.2f}")
            print(f"     climb: " + " -> ".join(f"TF{t}@{f(b)}" for (b, t) in climbs) if climbs else "     climb: none")


if __name__ == '__main__':
    main()
