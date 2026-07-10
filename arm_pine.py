"""arm_pine.py — paint the arm-delay trades on TradingView as bgcolors via jig.score.emit_bgcolor. (Joe 0710)

Four streams, priority low->high (later paints over earlier on a shared bar):
  arm    grey    the arm bar
  long   green   a long finisher trade bar (bd=+1)
  short  red     a short finisher trade bar (bd=-1)
  exit   white   the TP exit bar
All causal/emerging.  s5m = 8|0.65|ohlc4 (arm_walk.S5M_OVERRIDE).  tol = 0.

  python3 arm_pine.py --day 2026-07-09
"""
import argparse
import datetime as dtm

import numpy as np

from optimus9.analysis.jig import Jig
import arm_walk as AW
from optimus9.analysis.lr_v2 import gate_open, s_qualify, fin_gate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--day', default='2026-07-09')
    ap.add_argument('--cap', type=int, default=240)
    ap.add_argument('--out', default=None)
    cli = ap.parse_args()
    day = cli.day
    out = cli.out or f"transfer/arm_{day.replace('-', '')}.pine"

    end = int(dtm.datetime.strptime(day + ' 23:59', '%Y-%m-%d %H:%M')
              .replace(tzinfo=dtm.timezone.utc).timestamp() * 1000) + (cli.cap + 60) * 60_000
    TFS = AW.DEFAULT_TFS
    bands = AW.parse_bands(AW.DEFAULT_BANDS)
    arm_ts, long_ts, short_ts, exit_ts = [], [], [], []
    n = 0
    with Jig(end, hours=24, warmup=90, overrides=AW.overrides(TFS, 7, 0.50)) as j:
        W, cfg = j.W, j.cfg
        ts, px = np.asarray(j.ts, np.int64), j.px
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
            ke = min(len(ts) - 1, kh + cli.cap * 60 // 5)
            _e, armed, _c = AW.walk(B, kh, ke, cancel_on='none', permission=False,
                                    latch=True, arm_mode='latch', allib='off')
            if armed:
                arms.setdefault((armed[0], es), {'tf': armed[1], 'B': B})
        for (kA, es), v in sorted(arms.items()):
            bd = -es
            cap_k = min(len(ts) - 1, kA + cli.cap * 60 // 5)
            gates = gate_open(W, cfg, [(kA, es, bd, cap_k, 'arm')])
            ok = gates[0][3] if gates else None
            if ok is None:
                continue
            q15 = q15hi if bd == -1 else q15lo
            q30 = q30hi if bd == -1 else q30lo
            kT = fin_gate(q15, q30, ok, cap_k)
            if kT is None or kT >= cap_k:
                continue
            kx = AW.take_profit(v['B'], kT, AW.tp_tf(v['B'], kT, v['tf']), cap_k) or cap_k
            arm_ts.append(int(ts[kA]))
            (long_ts if bd == 1 else short_ts).append(int(ts[kT]))
            exit_ts.append(int(ts[kx]))
            n += 1
        streams = [
            {'name': 'arm', 'ts': arm_ts, 'color': 'color.gray'},
            {'name': 'long', 'ts': long_ts, 'color': 'color.green'},
            {'name': 'short', 'ts': short_ts, 'color': 'color.red'},
            {'name': 'exit', 'ts': exit_ts, 'color': 'color.white'},
        ]
        painted = j.score.emit_bgcolor(streams, out, f"arm-delay {day} ({n} trades)  grey=arm green=long red=short white=exit")
    print(f"{n} trades ({len(long_ts)} long, {len(short_ts)} short) -> {painted} painted bars -> {out}")


if __name__ == '__main__':
    main()
