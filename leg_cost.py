"""leg_cost.py — what would a blanket bearish-leg filter DESTROY? (Joe 0714)

Joe: "we can't glaze over the bullish trades. run a 3% swing_detect AND a 0.9% swing_detect to see where we
need to avoid total filtering."

A 3% down-leg can run 21 hours.  Inside it are 0.9% UP retracements — real, tradeable moves.  A filter that
blocks every long across the whole 3% leg kills those too.  This measures the bill for that.

  MACRO   jig.score.swings(pct=3.0) -> DOWN legs   = the extended bearish context
  MICRO   jig.score.swings(pct=0.9) -> UP/DOWN legs = the fine structure inside it

  Every LONG print is bucketed:
    A  outside any macro down-leg                       (a filter would not touch it)
    B  inside a macro down-leg, on a micro UP leg       (a blanket filter KILLS these — the bill)
    C  inside a macro down-leg, on a micro DOWN leg     (a blanket filter kills these — and should)

  Reported on MAE / MFE only (Joe 0711: no net, no PnL).  MAE/MFE via jig.score.entry_quality — the
  packaged, exit-INDEPENDENT excursion to the next favourable swing.  Labels are hindsight; entries causal.

  python3 leg_cost.py [days]        (default 11)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
import bias_emit as BE

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 11
MACRO_PCT, MICRO_PCT = 3.0, 0.9

end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
TFS = sorted(set([1, 8, 15] + BE.RUNGS))

with Jig(end_ms, hours=DAYS * 24, warmup=120, overrides=BE.overrides(TFS)) as j:
    C = j.causal
    ts, px = np.asarray(j.ts, np.int64), np.asarray(j.px, float)
    n = len(ts)
    win0 = end_ms - DAYS * 24 * 3600_000
    win = ts >= win0
    dt = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M')

    macro = j.score.legs(pivots=j.score.swings(pct=MACRO_PCT))
    micro = j.score.legs(pivots=j.score.swings(pct=MICRO_PCT))

    mac_dn = np.zeros(n, bool)
    for L in macro:
        if L['dir'] == -1:
            mac_dn[L['start']:L['end'] + 1] = True
    mic_up = np.zeros(n, bool)
    for L in micro:
        if L['dir'] == 1:
            mic_up[L['start']:L['end'] + 1] = True

    print(f'{DAYS} days   ·   macro {MACRO_PCT}%  ·  micro {MICRO_PCT}%')
    print(f'  macro DOWN-leg tape:            {100 * mac_dn[win].mean():>4.0f}%')
    print(f'  of that, on a micro UP leg:     {100 * (mac_dn & mic_up)[win].sum() / max(mac_dn[win].sum(), 1):>4.0f}%'
          f'   <- the bullish tape a blanket filter would blind us to')
    print()

    # ---- the prints (cascade + ladder-delay, the promoted config) --------------------------------
    ent, tag = [], []
    for es, sd in ((+1, 'SHORT'), (-1, 'LONG')):
        fires = BE.cascade(j, es, **BE.BASE) & win
        pb, _ = BE.delay_entry(j, es, fires, tf_coarse=BE.BASE['tf_coarse'], **BE.CAND_DELAY)
        for k in pb:
            if not win[k]:
                continue
            ent.append((int(ts[k]), es, -es, int(k)))
            b = 'A' if not mac_dn[k] else ('B' if mic_up[k] else 'C')
            tag.append((sd, b, int(k)))

    q = j.score.entry_quality(ent)          # (trade_ms, dt, es, bd, mae, mfe, mfe_ok, mfe_side, price)
    rec = [(tag[i][0], tag[i][1], tag[i][2], float(q[i][4]), float(q[i][5])) for i in range(len(q))]

    BUCK = {'A': 'outside any macro down-leg',
            'B': 'IN down-leg, on a micro UP leg',
            'C': 'IN down-leg, on a micro DOWN leg'}
    for sd in ('LONG', 'SHORT'):
        rows = [r for r in rec if r[0] == sd]
        print(f'{sd}S — {len(rows)} prints over {DAYS} days')
        print(f'  {"bucket":<34} {"n":>4} {"MAEmed":>7} {"MAEp90":>7} {"MFEmed":>7} {"MFE/MAE":>8} {"MAE>2":>6}')
        print('  ' + '-' * 78)
        for b in ('A', 'B', 'C'):
            s = [r for r in rows if r[1] == b]
            if not s:
                print(f'  {BUCK[b]:<34} {0:>4}')
                continue
            m = np.array([r[3] for r in s])
            f = np.array([r[4] for r in s])
            print(f'  {BUCK[b]:<34} {len(s):>4} {np.median(m):>7.2f} {np.percentile(m, 90):>7.2f} '
                  f'{np.median(f):>7.2f} {np.median(f) / max(np.median(m), 1e-9):>8.2f} '
                  f'{100 * np.mean(m > 2):>5.0f}%')
        print()

    L = [r for r in rec if r[0] == 'LONG']
    b_rows = [r for r in L if r[1] == 'B']
    c_rows = [r for r in L if r[1] == 'C']
    print('THE BILL — what a blanket "block all longs inside a macro down-leg" filter destroys vs saves')
    print(f'  DESTROYS  {len(b_rows):>3} longs on micro UP legs   '
          f'(MFE/MAE {np.median([r[4] for r in b_rows]) / max(np.median([r[3] for r in b_rows]), 1e-9):.2f})'
          if b_rows else '  DESTROYS    0 longs')
    print(f'  SAVES     {len(c_rows):>3} longs on micro DOWN legs '
          f'(MFE/MAE {np.median([r[4] for r in c_rows]) / max(np.median([r[3] for r in c_rows]), 1e-9):.2f})'
          if c_rows else '  SAVES       0 longs')
