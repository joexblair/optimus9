"""bias_sweep.py — can a slow s-line PREDICT the bearish legs, and let go of them afterwards? (Joe 0714)

HELD-OUT BY CONSTRUCTION. The 07-13 single-leg version of this scored 0.60 and I do not trust it: 1712
configs against one leg on one day is the +59% failure again (ci_initiatives, "Held-out window, always").

  LEGS      jig.score.swings(pct=3.0) -> jig.score.legs  ->  every DOWN leg of >= 3%.  Score-side/hindsight
            LABEL only; every feature is causal.  (Joe 0714: 3% captures the legs we're after.)
  SCORE     per DAY:  frac(predict == LO inside that day's down-legs) - frac(predict == LO outside them)
            A line that always predicts LO scores 0.  The subtraction IS the test.
  FIT       mean score over the FIT days.
  HELD-OUT  mean score over days the fit never saw.  This is the ONLY number that counts.
  WORST     the worst single day — a config that wins on average and dies on one day is not a filter.

Swept:  TF 30·45·60·90·120  ·  r k_len 5·7·9·11 × rsi 5·7·11·14·21 × stc 7·14·22·34  ·  m mult 0.40..1.00
        Mage 37|0.83|ohlc4 fixed.   Notation is k_len|rsi|stc (NOT the DB tuple order).

  python3 bias_sweep.py [days] [fit_days]        (default 11 days, first 6 = fit, last 5 = held-out)
"""
import sys, datetime as dtm
from datetime import timezone
import itertools
import numpy as np
from optimus9.analysis.jig import Jig

TFS = [30, 45, 60, 90, 120]
K_LENS = [5, 7, 9, 11]
RSIS = [5, 7, 11, 14, 21]
STCS = [7, 14, 22, 34]
MULTS = [0.40, 0.45, 0.50, 0.56, 0.65, 0.80, 1.00]
MAGE = ('bb', 37, 0.83, 'ohlc4')
M_LEN, M_SRC = 6, 'ohlc4'
SWING_PCT = 3.0
BAKED = (7, 5, 7, 0.56)          # the baked-in cascade config, scored as the baseline

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 11
FIT_DAYS = int(sys.argv[2]) if len(sys.argv) > 2 else 6

rname = lambda tf, k, r, s: f'r{tf}_{k}_{r}_{s}'
mname = lambda tf, mu: f'm{tf}_{int(mu * 100)}'
Mname = lambda tf: f'M{tf}'

ov = {}
for tf in TFS:
    sec = tf * 60
    ov[Mname(tf)] = (sec, MAGE, 'emerging')
    for mu in MULTS:
        ov[mname(tf, mu)] = (sec, ('bb', M_LEN, mu, M_SRC), 'emerging')
    for k, r, s in itertools.product(K_LENS, RSIS, STCS):
        ov[rname(tf, k, r, s)] = (sec, ('k', r, s, k, 'ohlc4'), 'emerging')   # DB order: rsi, stc, k_len

end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
print(f'{len(ov)} lines · {DAYS}d · fit={FIT_DAYS} held-out={DAYS - FIT_DAYS}', flush=True)

with Jig(end_ms, hours=DAYS * 24, warmup=240, overrides=ov) as j:
    C = j.causal
    ts, px = np.asarray(j.ts, np.int64), np.asarray(j.px, float)
    n = len(ts)
    win0 = end_ms - DAYS * 24 * 3600_000
    win = ts >= win0
    dt = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M')

    # ---- the LABEL: every >=3% DOWN leg (hindsight; never fed to a feature) ----------------------
    lg = j.score.legs(pivots=j.score.swings(pct=SWING_PCT))
    down = np.zeros(n, bool)
    legs_in = []
    for L in lg:
        if L['dir'] == -1 and ts[L['end']] >= win0:
            down[L['start']:L['end'] + 1] = True
            legs_in.append(L)
    print(f'\n{len(legs_in)} DOWN legs >= {SWING_PCT}%  ({100 * down[win].mean():.0f}% of the {DAYS}d tape)')
    for L in legs_in:
        print(f"   {dt(L['start'])} -> {dt(L['end'])}   {L['amp_pct']:+.1f}%   "
              f"({(ts[L['end']] - ts[L['start']]) / 3600000:.1f}h)")

    # ---- per-day masks ---------------------------------------------------------------------------
    day_of = ((ts - win0) // (24 * 3600_000)).astype(int)
    days = [(day_of == d) & win for d in range(DAYS)]
    fit_d, out_d = list(range(FIT_DAYS)), list(range(FIT_DAYS, DAYS))

    R, M, MG = {}, {}, {}
    for tf in TFS:
        MG[tf] = C.line(Mname(tf))
        for mu in MULTS:
            M[(tf, mu)] = C.line(mname(tf, mu))
        for k, r, s in itertools.product(K_LENS, RSIS, STCS):
            R[(tf, k, r, s)] = C.line(rname(tf, k, r, s))
        print(f'  s{tf} lines built', flush=True)

    def score_days(lo):
        out = []
        for d in range(DAYS):
            m = days[d]
            din, dout = m & down, m & ~down
            if not din.any() or not dout.any():
                out.append(np.nan)
                continue
            out.append(float(lo[din].mean()) - float(lo[dout].mean()))
        return np.array(out)

    rows = []
    for tf in TFS:
        for k, r, s in itertools.product(K_LENS, RSIS, STCS):
            for mu in MULTS:
                lo = (C.predict(R[(tf, k, r, s)], M[(tf, mu)], MG[tf], 0.0) == -1)
                sc = score_days(lo)
                rows.append(dict(tf=tf, k=k, r=r, s=s, mu=mu, sc=sc,
                                 fit=np.nanmean(sc[fit_d]), out=np.nanmean(sc[out_d]),
                                 worst=np.nanmin(sc), day=float(lo[win].mean())))
        print(f'  s{tf} scored', flush=True)

    rows.sort(key=lambda z: -z['fit'])
    print()
    print('=== RANKED BY FIT (days 0-%d).  HELD-OUT is the only number that counts. ===' % (FIT_DAYS - 1))
    print(f'{"FIT":>6} {"HELD-OUT":>9} {"WORST":>7} {"on%":>5} | {"TF":>4} {"k|rsi|stc":>10} {"m":>5}')
    print('-' * 60)
    for z in rows[:20]:
        print(f'{z["fit"]:>6.2f} {z["out"]:>9.2f} {z["worst"]:>7.2f} {z["day"]:>5.0%} | '
              f'{z["tf"]:>4} {f"{z['k']}|{z['r']}|{z['s']}":>10} {z["mu"]:>5.2f}')

    print()
    print('=== RANKED BY HELD-OUT (what actually generalises) ===')
    rows.sort(key=lambda z: -z['out'])
    print(f'{"FIT":>6} {"HELD-OUT":>9} {"WORST":>7} {"on%":>5} | {"TF":>4} {"k|rsi|stc":>10} {"m":>5}')
    print('-' * 60)
    for z in rows[:20]:
        print(f'{z["fit"]:>6.2f} {z["out"]:>9.2f} {z["worst"]:>7.2f} {z["day"]:>5.0%} | '
              f'{z["tf"]:>4} {f"{z['k']}|{z['r']}|{z['s']}":>10} {z["mu"]:>5.2f}')

    print()
    print('=== RANKED BY WORST DAY (minimax — survives every regime in the sample) ===')
    rows.sort(key=lambda z: -z['worst'])
    for z in rows[:10]:
        print(f'{z["fit"]:>6.2f} {z["out"]:>9.2f} {z["worst"]:>7.2f} {z["day"]:>5.0%} | '
              f'{z["tf"]:>4} {f"{z['k']}|{z['r']}|{z['s']}":>10} {z["mu"]:>5.2f}')

    print()
    print('=== BASELINE — the baked-in cascade r (k7|rsi5|stc7, m 0.56) ===')
    bk, br, bs, bmu = BAKED
    for tf in TFS:
        z = next(x for x in rows if (x['tf'], x['k'], x['r'], x['s'], x['mu']) == (tf, bk, br, bs, bmu))
        print(f'  s{tf}r   fit {z["fit"]:>6.2f}   held-out {z["out"]:>6.2f}   worst {z["worst"]:>6.2f}   '
              f'on {z["day"]:>4.0%}')

    print()
    print('=== the FIT winner, day by day ===')
    rows.sort(key=lambda z: -z['fit'])
    z = rows[0]
    print(f'  s{z["tf"]}r = {z["k"]}|{z["r"]}|{z["s"]}|ohlc4 · m 6|{z["mu"]}|ohlc4')
    for d in range(DAYS):
        tag = 'FIT ' if d < FIT_DAYS else 'HELD'
        v = z['sc'][d]
        print(f'   day {d}  {tag}  score {v:>6.2f}' if np.isfinite(v) else f'   day {d}  {tag}  (no leg)')
