"""hs30_cross.py — the ARM, measured. (Joe 0714)

`hs30` = the 30-MINUTE set. The `h` nulls the DB `s30` = 30-SECOND collision.

THE EVENT (Joe, confirmed verbatim):
    SHORT   hs30r OOB-high (>=85)  AND  hs30m crosses BELOW hs30r
    LONG    hs30r OOB-low  (<=15)  AND  hs30m crosses ABOVE hs30r

This is the cross the current bias-model dev arms on, and it has never been measured. No base rate, no
MAE/MFE, no read on how bad the bad ones are — so every candidate filter (the mo model included) has been
scored against an unknown denominator. This is the A/B base.

TWO CONFIGS, head to head (Joe: "AB test"):
    A  lp-cascade spec      hs30m = bb 10|0.60|hlc3    hs30r = k 5|6|6|hl2
    B  bias-cascade uniform hs30m = bb  6|0.56|ohlc4   hs30r = k 7|5|7|ohlc4

TWO CROSS GRIDS. `jig.causal.cross` needs an evaluation cadence and there is no default — so it is an axis,
not a silent pick:
    bar   1800s — one sample per 30-min bar. Joe's 11:00 / 14:30 both land on bar boundaries.
    fine    30s — catches the cross intra-bar, as the emerging lines actually move.

SCORE  jig.score.entry_quality -> MAE/MFE to the next favourable swing. EXIT-INDEPENDENT.
       MAE/MFE only — no net, no PnL (Joe 0711). Per week.
Causal/emerging throughout; every read via the jig.

  python3 hs30_cross.py [days] [warmup_hours] [swing_pct]        (default 32d, 600h, 2%)
"""
import sys, datetime as dtm
from datetime import timezone
import collections
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
WARM = int(sys.argv[2]) if len(sys.argv) > 2 else 600
SWING = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0

CFGS = {
    'A_spec':    dict(m=dict(length=10, mult=0.60, src='hlc3'),
                      r=dict(k_len=5, rsi=6,  stc=6,  src='hl2')),
    'B_uniform': dict(m=dict(length=6,  mult=0.56, src='ohlc4'),
                      r=dict(k_len=7, rsi=5,  stc=7,  src='ohlc4')),
}
GRIDS = {'bar': 1800_000, 'fine': 30_000}


def overrides():
    o = {}
    for tag, c in CFGS.items():
        o.update(bbline(f'{tag}m', 30, **c['m']))
        o.update(kline(f'{tag}r', 30, **c['r']))
    return o


end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
win0 = end_ms - DAYS * 24 * 3600_000
print(f'{DAYS}d · {WARM}h warmup · swing {SWING}%', flush=True)

with Jig(end_ms, hours=DAYS * 24, warmup=WARM, overrides=overrides()) as j:
    C, ts = j.causal, np.asarray(j.ts, np.int64)
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)

    for tag in CFGS:
        rs = C.sign(f'{tag}r')                                  # +1 OOB-high · -1 OOB-low · 0 in-band
        for gname, gms in GRIDS.items():
            x = C.cross(f'{tag}m', f'{tag}r', gms)              # +1 m crossed ABOVE r · -1 BELOW
            # SHORT: r OOB-high AND m crosses below   ·   LONG: r OOB-low AND m crosses above
            hit = np.flatnonzero(((rs == 1) & (x == -1)) | ((rs == -1) & (x == 1)))
            hit = hit[ts[hit] >= win0]
            ent = [(int(ts[i]), int(rs[i]), -int(rs[i]), int(i)) for i in hit]
            if not ent:
                print(f'{tag}/{gname}: 0 crosses'); continue
            q = j.score.entry_quality(ent, swing_pct=SWING)

            wk, sides = collections.defaultdict(list), collections.defaultdict(list)
            for i, r in enumerate(q):
                mae, mfe = float(r[4]), float(r[5])
                wk[f"{dt(ent[i][0]).isocalendar()[0]}-W{dt(ent[i][0]).isocalendar()[1]:02d}"].append((mae, mfe))
                sides['SHORT' if ent[i][2] == -1 else 'LONG'].append((mae, mfe))

            print(f'\n=== {tag}  ·  grid {gname} ({gms//1000}s)  ·  {len(q)} crosses ===')
            print(f"  {'':<12} {'n':>4} {'MAEmed':>7} {'MAEp90':>7} {'MFEmed':>7} {'MFEp90':>7} "
                  f"{'MFE/MAE':>8} {'MAE>2':>6}")

            def row(lab, rows):
                a = np.array(rows)
                m, f = a[:, 0], a[:, 1]
                print(f'  {lab:<12} {len(a):>4} {np.median(m):>7.2f} {np.percentile(m,90):>7.2f} '
                      f'{np.median(f):>7.2f} {np.percentile(f,90):>7.2f} '
                      f'{np.median(f)/max(np.median(m),1e-9):>8.2f} {100*np.mean(m>2):>5.0f}%')

            for w in sorted(wk):
                row(w, wk[w])
            for s in ('SHORT', 'LONG'):
                if sides[s]:
                    row(s, sides[s])
            row('ALL', [x for v in wk.values() for x in v])

            # Joe's two: the 07-11 11:00 bad cross and the 14:30 good one
            for i, e in enumerate(ent):
                d = dt(e[0])
                if d.strftime('%m-%d') == '07-11' and 10 <= d.hour <= 15:
                    print(f'    >> {d:%m-%d %H:%M}  {"SHORT" if e[2]==-1 else "LONG":<5} '
                          f'MAE {float(q[i][4]):.2f}  MFE {float(q[i][5]):.2f}')
