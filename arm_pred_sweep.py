"""arm_pred_sweep.py — tame the r prediction: sweep the m-line (mini BB) len x mult. (Joe 0710)

The prediction anchor is max(s{tf}m, s{tf}Mage) for a hi breach.  Only the m-line moves here:
    s{tf}m = {len} | {mult} | ohlc4        len  in [6,7,8]
                                           mult in [0.50, 0.53, 0.56, 0.59, 0.62]
Mage stays 37|0.7|ohlc4.  r stays 5|5|6|close.  tol = 4.0 (sweepable).

Per case, per (len, mult):
    TFs   = how many TFs predict at all inside the hunt window
    bars  = total predicted bars across all TFs (the noise floor)
    lag   = median (first r-pred per TF) - extreme, in minutes.  negative = before the turn.
    early = TFs whose first prediction is > 10 min before the extreme

Then the per-TF first-pred grid for one chosen (len, mult).

Read-only.  python3 arm_pred_sweep.py
"""
import datetime as dtm
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS
from arm_apex_probe import DAY, predict_tol, seam_mask

HI, LO = 85.0, 15.0
TFS = [6, 7, 8, 9, 10, 11, 12, 14, 16, 19]
LENS = [6, 7, 8]
MULTS = [0.50, 0.53, 0.56, 0.59, 0.62]
TOL = 4.0

# (label, day, hunt hh:mm, es, target hh:mm, pad minutes)
CASES = [('06:01 top', '2026-07-08', '05:40', 1, '06:01', 25),
         ('03:13 top', '2026-07-08', '02:30', 1, '03:13', 25),
         ('00:42 top', '2026-07-08', '00:19', 1, '00:50', 15)]


def ms(day, hm):
    return int(dtm.datetime.strptime(f'{day} {hm}', '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).timestamp() * 1000)


def mkey(L, M):
    return f'L{L}M{int(M*100)}'


def run_case(db, label, day, hunt, es, target, pad):
    t_h, t_t = ms(day, hunt), ms(day, target)
    end = t_t + (pad + 40) * 60_000
    ov = {}
    for tf in TFS:
        s = tf * 60
        ov[f's{tf}r'] = (s, ('k', 5, 6, 5, 'close'), 'emerging')
        ov[f's{tf}Mage'] = (s, ('bb', 37, 0.7, 'ohlc4'), 'emerging')
        for L in LENS:
            for M in MULTS:
                ov[f's{tf}m_{mkey(L, M)}'] = (s, ('bb', L, M, 'ohlc4'), 'emerging')
    W = bm.BiasWindow(db, end, lookback=24, warmup=90, cfg=bm.BiasConfig(**BASE_BIAS), line_overrides=ov, lean=True)
    ts, px = np.asarray(W.ts, np.int64), np.asarray(W.px, float)
    anchor = (int(ts[0]) // DAY) * DAY
    f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%H:%M:%S')

    s5m = np.asarray(W.line('s5m'), float)
    sm = seam_mask(ts, 300_000, anchor)
    kh = int(next(k for k in np.flatnonzero(sm) if k >= np.searchsorted(ts, t_h)
                  and (s5m[k] >= HI if es == 1 else s5m[k] <= LO)))
    ke = int(np.searchsorted(ts, t_t + pad * 60_000))
    seg = px[kh:ke]
    ext = kh + (int(np.nanargmax(seg)) if es == 1 else int(np.nanargmin(seg)))

    R = {tf: np.asarray(W.line(f's{tf}r'), float) for tf in TFS}
    G = {tf: np.asarray(W.line(f's{tf}Mage'), float) for tf in TFS}

    print(f"\n### {label}  hunt {f(kh)}  extreme {f(ext)}  ({(px[ext]/px[kh]-1)*100:+.2f}%)")
    print(f"{'len':>4} {'mult':>6} | {'TFs':>4} {'bars':>6} {'lag p50':>9} {'early>10m':>10} {'first pred':>11}")
    grids = {}
    for L in LENS:
        for M in MULTS:
            first, bars, tfs = [], 0, 0
            per = {}
            for tf in TFS:
                m = np.asarray(W.line(f's{tf}m_{mkey(L, M)}'), float)
                p = predict_tol(R[tf], m, G[tf], TOL)[kh:ke]
                hit = np.flatnonzero(p == es)
                bars += int(hit.size)
                if hit.size:
                    tfs += 1
                    k = kh + int(hit[0]); first.append((ts[k] - ts[ext]) / 60000.0); per[tf] = f(k)
                else:
                    per[tf] = '-'
            grids[(L, M)] = per
            lag = np.median(first) if first else float('nan')
            early = sum(1 for x in first if x < -10)
            fp = min(first) if first else float('nan')
            print(f"{L:>4} {M:>6.2f} | {tfs:>4} {bars:>6} {lag:>+8.1f}m {early:>10} {fp:>+10.1f}m")
    return grids, ext, f


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    all_grids = {}
    for c in CASES:
        all_grids[c[0]] = run_case(db, *c)
    # per-TF first-pred grid at the extremes of the sweep
    for (L, M) in [(6, 0.50), (7, 0.50), (8, 0.62)]:
        print(f"\n--- first r-pred per TF   m = {L}|{M:.2f}|ohlc4 ---")
        print(f"{'case':<12} " + " ".join(f"{'tf'+str(tf):>10}" for tf in TFS))
        for (label, (grids, _e, _f)) in all_grids.items():
            print(f"{label:<12} " + " ".join(f"{grids[(L, M)][tf]:>10}" for tf in TFS))
    db.disconnect()


if __name__ == '__main__':
    main()
