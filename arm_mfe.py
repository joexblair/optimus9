"""arm_mfe.py — MAE/MFE at two anchors, measured to the real TP exit. No fixed horizon, no PnL. (Joe 0710)

Per trade (arm -> gate -> finisher -> far-side-mini TP):
  armed    : the arm bar.  MAE/MFE over [arm, exit].
  finished : the finisher trade bar.  MAE/MFE over [finished, exit].
Each event carries its own datetime.  Excursion runs to the exit the strategy actually takes — no window.

  python3 arm_mfe.py --days 2026-06-20..2026-07-09              (per-day summary)
  python3 arm_mfe.py --day 2026-07-08 --detail                  (one row per trade)
"""
import argparse
import datetime as dtm

import numpy as np

from optimus9.analysis.jig import Jig
import arm_walk as AW
from optimus9.analysis.lr_v2 import gate_open, s_qualify, fin_gate


def daterange(spec):
    a, b = spec.split('..')
    d0, d1 = dtm.date.fromisoformat(a), dtm.date.fromisoformat(b)
    out = []
    while d0 <= d1:
        out.append(d0.isoformat())
        d0 += dtm.timedelta(days=1)
    return out


def exc(px, k0, kx, bd):
    e = px[k0]
    path = bd * (px[k0:kx + 1] - e) / e * 100
    return float(np.nanmax(np.maximum(path, 0.0))), -float(np.nanmin(np.minimum(path, 0.0)))


def day_trades(day, cap):
    end = int(dtm.datetime.strptime(day + ' 23:59', '%Y-%m-%d %H:%M')
              .replace(tzinfo=dtm.timezone.utc).timestamp() * 1000) + (cap + 60) * 60_000
    TFS = AW.DEFAULT_TFS
    bands = AW.parse_bands(AW.DEFAULT_BANDS)
    rows = []
    with Jig(end, hours=24, warmup=90, overrides=AW.overrides(TFS, 7, 0.50)) as j:
        W, cfg = j.W, j.cfg
        ts, px = np.asarray(j.ts, np.int64), j.px
        f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, dtm.timezone.utc).strftime('%m-%d %H:%M:%S')
        s5m = j.causal.line('s5m')
        seam5 = (ts % 300_000) == 0
        sd = lambda k: 1 if s5m[k] >= 85 else (-1 if s5m[k] <= 15 else 0)
        ks = [int(k) for k in np.flatnonzero(seam5)]
        t0 = int(dtm.datetime.strptime(day + ' 00:00', '%Y-%m-%d %H:%M')
                 .replace(tzinfo=dtm.timezone.utc).timestamp() * 1000)
        t1 = int(dtm.datetime.strptime(day + ' 23:59', '%Y-%m-%d %H:%M')
                 .replace(tzinfo=dtm.timezone.utc).timestamp() * 1000)
        hunts = [(ks[i], sd(ks[i])) for i in range(1, len(ks))
                 if sd(ks[i]) and sd(ks[i]) != sd(ks[i - 1]) and t0 <= ts[ks[i]] <= t1]
        q15hi, q15lo = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
        q30hi, q30lo = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
        arms = {}
        for (kh, es) in hunts:
            B = AW.board(j, TFS, es, 0.0, bands)
            ke = min(len(ts) - 1, kh + cap * 60 // 5)
            _e, armed, _c = AW.walk(B, kh, ke, cancel_on='none', permission=False,
                                    latch=True, arm_mode='latch', allib='off')
            if armed:
                arms.setdefault((armed[0], es), {'tf': armed[1], 'B': B})
        for (kA, es), v in sorted(arms.items()):
            bd = -es
            cap_k = min(len(ts) - 1, kA + cap * 60 // 5)
            gates = gate_open(W, cfg, [(kA, es, bd, cap_k, 'arm')])
            ok = gates[0][3] if gates else None
            if ok is None:
                continue
            q15 = q15hi if bd == -1 else q15lo
            q30 = q30hi if bd == -1 else q30lo
            kT = fin_gate(q15, q30, ok, cap_k)
            if kT is None or kT >= cap_k:
                continue
            xt = AW.tp_tf(v['B'], kT, v['tf'])
            kx = AW.take_profit(v['B'], kT, xt, cap_k)
            if kx is None:
                kx = cap_k
            amf, ama = exc(px, kA, kx, bd)
            fmf, fma = exc(px, kT, kx, bd)
            rows.append(dict(tf=v['tf'], es=es, armed=f(kA), finished=f(kT), exit=f(kx),
                             arm_mfe=amf, arm_mae=ama, fin_mfe=fmf, fin_mae=fma,
                             delay=(ts[kT] - ts[kA]) / 60000.0, held=(ts[kx] - ts[kT]) / 60000.0))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', default=None)
    ap.add_argument('--day', default=None)
    ap.add_argument('--cap', type=int, default=240)
    ap.add_argument('--detail', action='store_true')
    cli = ap.parse_args()
    days = [cli.day] if cli.day else daterange(cli.days or '2026-06-20..2026-07-09')

    if cli.detail:
        print(f"\n{'armed':<16} {'finished':<16} {'exit':<16} {'apex':>4} {'delay':>6} {'held':>6}"
              f" | {'armMFE':>7} {'armMAE':>7} | {'finMFE':>7} {'finMAE':>7}")
        for day in days:
            for r in day_trades(day, cli.cap):
                print(f"{r['armed']:<16} {r['finished']:<16} {r['exit']:<16} {r['tf']:>4} "
                      f"{r['delay']:5.0f}m {r['held']:5.0f}m | {r['arm_mfe']:6.2f}% {r['arm_mae']:6.2f}%"
                      f" | {r['fin_mfe']:6.2f}% {r['fin_mae']:6.2f}%")
        return

    print("\narm-delay MAE/MFE to the TP exit · no fixed horizon, no PnL")
    print(f"{'day':<12} {'n':>4} | {'armMFE p50':>10} {'armMAE p50':>10} | {'finMFE p50':>10} {'finMAE p50':>10}"
          f" | {'finMFE>MAE':>10}")
    pool = []
    for day in days:
        rows = day_trades(day, cli.cap)
        if not rows:
            print(f"{day:<12}    0")
            continue
        af = np.array([r['arm_mfe'] for r in rows]); aa = np.array([r['arm_mae'] for r in rows])
        ff = np.array([r['fin_mfe'] for r in rows]); fa = np.array([r['fin_mae'] for r in rows])
        print(f"{day:<12} {len(rows):>4} | {np.median(af):9.3f}% {np.median(aa):9.3f}% |"
              f" {np.median(ff):9.3f}% {np.median(fa):9.3f}% | {100*(ff>fa).mean():9.1f}%")
        pool += rows
    af = np.array([r['arm_mfe'] for r in pool]); aa = np.array([r['arm_mae'] for r in pool])
    ff = np.array([r['fin_mfe'] for r in pool]); fa = np.array([r['fin_mae'] for r in pool])
    print(f"{'POOLED':<12} {len(pool):>4} | {np.median(af):9.3f}% {np.median(aa):9.3f}% |"
          f" {np.median(ff):9.3f}% {np.median(fa):9.3f}% | {100*(ff>fa).mean():9.1f}%")
    print(f"{'  means':<12} {'':>4} | {af.mean():9.3f}% {aa.mean():9.3f}% | {ff.mean():9.3f}% {fa.mean():9.3f}%")


if __name__ == '__main__':
    main()
