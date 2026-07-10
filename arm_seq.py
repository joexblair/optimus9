"""arm_seq.py — the three open questions on the latch book. (Joe 0710)

Read-only.  Runs every s5m hunt in a window, dedupes to DISTINCT arms, then answers:

  Q1 concurrency   how many hunts collapse onto one arm; what the book looks like deduped.
  Q2 exit==hunt    how often a TP bar is also an s5m crossing bar (the exit that opens the next hunt).
  Q3 opposite-arm  sequential book with one position at a time.  Three policies for an opposite-side
                   arm arriving while a position is open:  skip · flip (close + reverse) · close-only.

  python3 arm_seq.py --day 2026-07-09 --from 00:00 --to 23:59
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
    ap.add_argument('--from', dest='t0', default='00:00')
    ap.add_argument('--to', dest='t1', default='23:59')
    ap.add_argument('--tfs', default=','.join(str(x) for x in AW.DEFAULT_TFS))
    ap.add_argument('--bands', default=AW.DEFAULT_BANDS)
    ap.add_argument('--m-len', type=int, default=7)
    ap.add_argument('--m-mult', type=float, default=0.50)
    ap.add_argument('--tol', type=float, default=0.0)
    ap.add_argument('--tp-cap', type=int, default=240)
    ap.add_argument('--allib', default='off', choices=['ladder', 's5', 'off'])
    a = ap.parse_args()

    TFS = [int(x) for x in a.tfs.split(',')]
    bands = AW.parse_bands(a.bands)
    t0, t1 = ms(a.day, a.t0), ms(a.day, a.t1)
    end = t1 + (a.tp_cap + 40) * 60_000

    with Jig(end, hours=24, warmup=90, overrides=AW.overrides(TFS, a.m_len, a.m_mult)) as j:
        ts, px = np.asarray(j.ts, np.int64), j.px
        f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
        s5m = j.causal.line('s5m')
        seam5 = (ts % 300_000) == 0
        sd = lambda k: 1 if s5m[k] >= AW.HI else (-1 if s5m[k] <= AW.LO else 0)
        ks = [int(k) for k in np.flatnonzero(seam5)]
        hunt_bars = [ks[i] for i in range(1, len(ks)) if sd(ks[i]) and sd(ks[i]) != sd(ks[i - 1])]
        hunts = [(k, sd(k)) for k in hunt_bars if t0 <= ts[k] <= t1]

        arms = {}
        for (kh, es) in hunts:
            B = AW.Board(j, TFS, es, a.tol, bands)
            ke = min(len(ts) - 1, kh + a.tp_cap * 60 // 5)
            _ev, armed, _c = AW.walk(B, kh, ke, cancel_on='none', permission=False,
                                     latch=True, arm_mode='latch', allib=a.allib)
            if not armed:
                continue
            kA, tf, why = armed
            xt = AW.tp_tf(B, kA, tf)
            kx = AW.take_profit(B, kA, xt, min(len(ts) - 1, kA + a.tp_cap * 60 // 5))
            if kx is None:
                continue
            net = -es * (px[kx] - px[kA]) / px[kA] * 100 - COST
            e = px[kA]; bd = -es
            path = bd * (px[kA:kx + 1] - e) / e * 100          # signed excursion, in-trade
            mae = -float(np.nanmin(np.minimum(path, 0.0)))      # worst against, +ve
            mfe = float(np.nanmax(np.maximum(path, 0.0)))       # best for, +ve
            i_mfe = int(np.nanargmax(path)); i_mae = int(np.nanargmin(path))
            w10 = path[:min(len(path), 10 * 60 // 5 + 1)]
            mfe10 = float(np.nanmax(np.maximum(w10, 0.0)))
            mae10 = -float(np.nanmin(np.minimum(w10, 0.0)))
            key = (kA, es)
            arms.setdefault(key, {'tf': tf, 'xt': xt, 'kx': kx, 'net': net, 'why': why, 'hunts': [],
                                  'mae': mae, 'mfe': mfe,
                                  't_mfe': i_mfe * 5 / 60.0, 't_mae': i_mae * 5 / 60.0,
                                  'mfe10': mfe10, 'mae10': mae10, 'kh': kh})
            arms[key]['hunts'].append(kh)

        rows = sorted(arms.items())
        print(f"\n{a.day} {a.t0}-{a.t1}   {len(hunts)} hunts -> {len(rows)} distinct arms   allib={a.allib}")

        # ── Q1 concurrency ──
        multi = [(k, v) for (k, v) in rows if len(v['hunts']) > 1]
        print(f"\nQ1  {sum(len(v['hunts']) for _k, v in rows)} hunt-rows collapse to {len(rows)} arms; "
              f"{len(multi)} arms were reached by >1 hunt (max {max((len(v['hunts']) for _k, v in rows), default=0)})")
        n = np.array([v['net'] for _k, v in rows])
        if n.size:
            print(f"    deduped book: mean {n.mean():+.4f}%  total {n.sum():+.2f}%  win {100*(n>0).mean():.1f}%  n={n.size}")

        # ── Q2 exit bar == hunt start bar ──
        hb = set(hunt_bars)
        exact = sum(1 for _k, v in rows if v['kx'] in hb)
        within = {w: sum(1 for _k, v in rows if any(abs(v['kx'] - b) * 5 <= w * 60 for b in hunt_bars)) for w in (1, 5, 10)}
        print(f"\nQ2  TP bar is exactly an s5m crossing bar: {exact}/{len(rows)}")
        for w, c in within.items():
            print(f"    TP bar within {w:>2} min of an s5m crossing: {c}/{len(rows)}")
        opp = sum(1 for _k, v in rows
                  if any(abs(v['kx'] - b) * 5 <= 300 and sd(b) == -_k[1] for b in hunt_bars))
        print(f"    ...and that crossing is on the OPPOSITE side of the trade: {opp}/{len(rows)}")

        # ── Q3 sequential book, one position at a time ──
        for policy in ('all', 'skip', 'flip', 'close'):
            book, open_pos = [], None
            for (kA, es), v in rows:
                if policy == 'all':
                    book.append(v['net']); continue
                if open_pos is None:
                    open_pos = (kA, es, v); continue
                okA, oes, ov = open_pos
                if kA >= ov['kx']:                                   # prior trade already closed
                    book.append(ov['net']); open_pos = (kA, es, v); continue
                if es == oes:
                    continue                                          # same side while open -> ignore
                if policy == 'skip':
                    continue
                early = -oes * (px[kA] - px[okA]) / px[okA] * 100 - COST   # close the open leg here
                book.append(early)
                open_pos = (kA, es, v) if policy == 'flip' else None
            if open_pos is not None:
                book.append(open_pos[2]['net'])
            b = np.array(book)
            if b.size:
                print(f"\nQ3  policy={policy:<6} n={b.size:<3} mean {b.mean():+.4f}%  total {b.sum():+.2f}%"
                      f"  win {100*(b>0).mean():.1f}%")

        # master trade: an arm that fires on the SAME side while an earlier arm is still open is a
        # pyramid leg of that earlier arm.  master = the first arm of the run.
        master = {}
        for (kA, es), v in rows:
            m = None
            for (mA, mes), mv in rows:
                if mA < kA and mes == es and kA < mv['kx'] and master.get((mA, mes)) is None:
                    m = (mA, mes); break
            master[(kA, es)] = m
        print(f"\n{'arm':<18} {'es':>3} {'apex':>5} {'tpTF':>5} {'held':>6} {'MAE':>6} {'MFE':>6}"
              f" {'tMFE':>6} {'tMAE':>6} {'cap':>6} {'net%':>8} {'hunts':>6}  master")
        for (kA, es), v in rows:
            held = (ts[v['kx']] - ts[kA]) / 60000
            cap = (v['net'] + COST) / v['mfe'] if v['mfe'] > 0 else float('nan')
            m = master[(kA, es)]
            print(f"{f(kA):<18} {es:+3d} {v['tf']:>5} {v['xt']:>5} {held:5.0f}m"
                  f" {v['mae']:6.2f} {v['mfe']:6.2f} {v['t_mfe']:5.0f}m {v['t_mae']:5.0f}m"
                  f" {cap:6.2f} {v['net']:+8.3f} {len(v['hunts']):>6}  "
                  f"{('pyramid of ' + f(m[0])) if m else '-'}")
        npy = sum(1 for k in master if master[k])
        print(f"  {npy}/{len(rows)} arms are pyramid legs of an earlier same-side arm")

        # the long-running losers
        L = [v for _k, v in rows if v['net'] < 0 and (ts[v['kx']] - ts[_k[0]]) / 60000 >= 60]
        S = [v for _k, v in rows if v['net'] < 0 and (ts[v['kx']] - ts[_k[0]]) / 60000 < 60]
        W = [v for _k, v in rows if v['net'] > 0]
        for nm, g in (('winners', W), ('losers <60m', S), ('losers >=60m', L)):
            if not g:
                continue
            mf = np.array([x['mfe'] for x in g]); ma = np.array([x['mae'] for x in g])
            nt = np.array([x['net'] for x in g]); tm = np.array([x['t_mfe'] for x in g])
            print(f"  {nm:<13} n={len(g):<3} MFE mean {mf.mean():.3f} max {mf.max():.3f} p50 {np.median(mf):.3f}"
                  f" | MAE mean {ma.mean():.3f} max {ma.max():.3f}"
                  f" | tMFE p50 {np.median(tm):.0f}m | net mean {nt.mean():+.3f}%")


if __name__ == '__main__':
    main()
