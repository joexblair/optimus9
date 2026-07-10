"""arm_trade.py — the FULL flow: arm-delay ladder -> s3s4 gate -> finishers -> trade -> TP. (Joe 0710)

Read-only.  Reuses the shipped producers, no re-implementation:
  arm      arm_walk.walk (latch)                         -> (bar, es, apex TF)
  gate     lr_v2.gate_open  (reasons a / b / c)          -> the open bar
  finisher lr_v2.s_qualify (s15a, s30a) + fin_gate       -> the trade bar
           lr_v2.fin_unlatch(fin_lb, fin_fwd)            -> the arm-gated variant (--producer unlatch)
  TP       arm_walk.tp_tf + take_profit                  -> the exit bar

  python3 arm_trade.py --day 2026-07-09
  python3 arm_trade.py --day 2026-07-09 --producer unlatch --detail
"""
import argparse
import datetime as dtm
from datetime import timezone

import numpy as np

from optimus9.analysis.jig import Jig
from optimus9.analysis.lr_v2 import gate_open, s_qualify, fin_gate, fin_unlatch
import arm_walk as AW

COST = 0.20


def ms(day, hm):
    return int(dtm.datetime.strptime(f'{day} {hm}', '%Y-%m-%d %H:%M').replace(tzinfo=timezone.utc).timestamp() * 1000)


def excursion(px, kA, kx, bd):
    e = px[kA]
    path = bd * (px[kA:kx + 1] - e) / e * 100
    return (-float(np.nanmin(np.minimum(path, 0.0))), float(np.nanmax(np.maximum(path, 0.0))),
            float(path[-1]))


def build_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--day', default='2026-07-09')
    ap.add_argument('--from', dest='t0', default='00:00')
    ap.add_argument('--to', dest='t1', default='23:59')
    ap.add_argument('--tfs', default=','.join(str(x) for x in AW.DEFAULT_TFS))
    ap.add_argument('--bands', default=AW.DEFAULT_BANDS)
    ap.add_argument('--m-len', type=int, default=7)
    ap.add_argument('--m-mult', type=float, default=0.50)
    ap.add_argument('--tol', type=float, default=0.0)
    ap.add_argument('--cap', type=int, default=240, help='minutes the arm stays live for the gate/finishers')
    ap.add_argument('--producer', default='gate', choices=['gate', 'unlatch', 'arm'])
    ap.add_argument('--fin-lb', type=int, default=7)
    ap.add_argument('--fin-fwd', type=int, default=2)
    ap.add_argument('--detail', action='store_true')
    return ap


def run_day(a, quiet=False):

    TFS = [int(x) for x in a.tfs.split(',')]
    bands = AW.parse_bands(a.bands)
    t0, t1 = ms(a.day, a.t0), ms(a.day, a.t1)
    end = t1 + (a.cap + 60) * 60_000

    with Jig(end, hours=24, warmup=90, overrides=AW.overrides(TFS, a.m_len, a.m_mult)) as j:
        W, cfg = j.W, j.cfg
        ts, px = np.asarray(j.ts, np.int64), j.px
        f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
        s5m = j.causal.line('s5m')
        seam5 = (ts % 300_000) == 0
        sd = lambda k: 1 if s5m[k] >= AW.HI else (-1 if s5m[k] <= AW.LO else 0)
        ks = [int(k) for k in np.flatnonzero(seam5)]
        hunts = [(ks[i], sd(ks[i])) for i in range(1, len(ks))
                 if sd(ks[i]) and sd(ks[i]) != sd(ks[i - 1]) and t0 <= ts[ks[i]] <= t1]

        # finishers, once
        q15hi, q15lo = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
        q30hi, q30lo = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)

        # 1) the arms, deduped
        arms = {}
        for (kh, es) in hunts:
            B = AW.board(j, TFS, es, a.tol, bands)
            ke = min(len(ts) - 1, kh + a.cap * 60 // 5)
            _ev, armed, _c = AW.walk(B, kh, ke, cancel_on='none', permission=False,
                                     latch=True, arm_mode='latch', allib='off')
            if armed:
                arms.setdefault((armed[0], es), {'tf': armed[1], 'why': armed[2], 'B': B, 'n': 0})
                arms[(armed[0], es)]['n'] += 1

        # 2) gate + finishers per arm
        rows = []
        for (kA, es), v in sorted(arms.items()):
            bd = -es
            cap = min(len(ts) - 1, kA + a.cap * 60 // 5)
            setups = [(kA, es, bd, cap, 'arm')]
            gates = gate_open(W, cfg, setups)
            ok = gates[0][3] if gates else None
            q15 = q15hi if bd == -1 else q15lo
            q30 = q30hi if bd == -1 else q30lo
            if a.producer == 'arm':
                kT, how = kA, 'arm'
            elif a.producer == 'unlatch':
                kT = fin_unlatch(q15, q30, kA, cap, a.fin_lb, a.fin_fwd); how = 'unlatch'
            else:
                kT = fin_gate(q15, q30, ok, cap) if ok is not None else None
                how = f"gate:{gates[0][4]}" if gates else 'no-gate'
            if a.detail:
                print(f"  {f(kA)} es={es:+d} apex TF{v['tf']}  gate={f(ok) if ok else '-'}"
                      f"  trade={f(kT) if kT else '-'}  ({how})")
            if kT is None or kT >= cap:
                rows.append(dict(kA=kA, es=es, tf=v['tf'], ok=ok, kT=None, n=v['n']))
                continue
            xt = AW.tp_tf(v['B'], kT, v['tf'])
            kx = AW.take_profit(v['B'], kT, xt, cap)
            if kx is None:
                rows.append(dict(kA=kA, es=es, tf=v['tf'], ok=ok, kT=kT, kx=None, n=v['n']))
                continue
            mae, mfe, gross = excursion(px, kT, kx, bd)
            rows.append(dict(kA=kA, es=es, tf=v['tf'], ok=ok, kT=kT, kx=kx, xt=xt, n=v['n'],
                             mae=mae, mfe=mfe, gross=gross, net=gross - COST,
                             delay=(ts[kT] - ts[kA]) / 60000.0, held=(ts[kx] - ts[kT]) / 60000.0, how=how))

        traded = [r for r in rows if r.get('kx') is not None]
        if quiet:
            return traded
        print(f"\n{a.day}  {len(hunts)} hunts -> {len(arms)} arms -> {len(traded)} trades"
              f"   producer={a.producer}  cap={a.cap}m  cost={COST}%")
        print(f"{'arm':<18} {'es':>3} {'apex':>4} {'gate':<18} {'trade':<18} {'delay':>6} {'held':>6}"
              f" {'MAE':>6} {'MFE':>6} {'gross':>7} {'net':>7}")
        for r in rows:
            if r.get('kx') is None:
                why = 'no trade' if r.get('kT') is None else 'no TP'
                print(f"{f(r['kA']):<18} {r['es']:+3d} {r['tf']:>4} "
                      f"{(f(r['ok']) if r['ok'] else '-'):<18} {why:<18}")
                continue
            print(f"{f(r['kA']):<18} {r['es']:+3d} {r['tf']:>4} {f(r['ok']):<18} {f(r['kT']):<18}"
                  f" {r['delay']:5.0f}m {r['held']:5.0f}m {r['mae']:6.2f} {r['mfe']:6.2f}"
                  f" {r['gross']:+7.3f} {r['net']:+7.3f}")
        if traded:
            n = np.array([r['net'] for r in traded])
            g = np.array([r['gross'] for r in traded])
            print(f"\n  n={n.size}  net mean {n.mean():+.4f}%  total {n.sum():+.2f}%  win {100*(n>0).mean():.1f}%"
                  f"  |  gross mean {g.mean():+.4f}%  MAE p50 {np.median([r['mae'] for r in traded]):.2f}%"
                  f"  delay p50 {np.median([r['delay'] for r in traded]):.0f}m")
        return traded


def main():
    run_day(build_args().parse_args())


if __name__ == '__main__':
    main()
