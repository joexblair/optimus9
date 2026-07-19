"""mo_walk.py — the PER-BAR verdict. (Joe 0714)

Joe: "if the logic is applying at every bar, then a verdict is created at each bar. no #1 or #2 means
walk forward, no?"  Correct — and mo_curl.py could not answer it, because it only ever recorded the
CURL bars (the positive class). With no non-curl bars there is no denominator and no walk-forward verdict.

THE VERDICT, at every travelling bar (K between OOBs — the 07-11 10:00 case, s45r at 36):
    accumulated pressure since the last curl, SIGNED BY THE TARGET
        strongly +ve  -> a #1 (toward) curl is due; K is being carried to its target
        strongly -ve  -> a #2 (away)  curl is due; the target may be flipping
        neither       -> WALK FORWARD. Nothing is bending it. It continues to its target.

THE LABEL (Joe's sentence, verbatim: "we can trust s45r to OOB at ~12:45"):
    from this bar, does K reach its TARGET OOB before the OPPOSITE one?   REACH / FAILED

So the test is: does the accumulated-pressure state, read at an arbitrary bar, separate the bars that
walk forward to the target from the bars that flip?  Base rate first. IS/OOS split. No fitted threshold.

  BB mo{tf}m: bb 7|0.64|close  ·  K mo{tf}b: k 5|74|29|hlc3  ·  K mo{tf}r: k 7|5|7|ohlc4
  python3 mo_walk.py [days] [warmup_hours]        (default 32d, 600h)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline

TFS = [15, 25, 30, 45]
HI, LO = 85.0, 15.0
BB = dict(length=7, mult=0.64, src='close')
KVARS = {'b': dict(k_len=5, rsi=74, stc=29, src='hlc3'),
         'r': dict(k_len=7, rsi=5, stc=7, src='ohlc4')}
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
WARM = int(sys.argv[2]) if len(sys.argv) > 2 else 600


def zone_of(d):
    return 'IN_OOB' if d < 0 else ('CLOSE' if d < 15 else ('APPROACH' if d < 35 else 'MID'))


def overrides():
    o = {}
    for tf in TFS:
        o.update(bbline(f'mo{tf}m', tf, **BB))
        for v, c in KVARS.items():
            o.update(kline(f'mo{tf}{v}', tf, **c))
    return o


end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
win0 = end_ms - DAYS * 24 * 3600_000
print(f'{DAYS}d · {WARM}h warmup · TFs {TFS}', flush=True)

bars = []          # (tf, kvar, ms, zone, net, mag, bars_since, reach)
with Jig(end_ms, hours=DAYS * 24, warmup=WARM, overrides=overrides()) as j:
    C = j.causal
    ts = np.asarray(j.ts, np.int64)
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)

    for tf in TFS:
        m = (ts % (tf * 60 * 1000)) == 0
        bts = ts[m]
        bb = C.line(f'mo{tf}m')[m]
        n = len(bts)

        for kvar in KVARS:
            k = C.line(f'mo{tf}{kvar}')[m]
            side = np.where(k >= HI, 1, np.where(k <= LO, -1, 0))
            curls = set()
            for dirn in (+1, -1):
                curls |= {int(np.searchsorted(bts, t)) for t in C.curl(bts, k, dirn)}

            # the forward truth: for every bar, the NEXT OOB side K touches
            nxt = np.zeros(n, np.int8)
            nx = 0
            for i in range(n - 1, -1, -1):
                nxt[i] = nx
                if side[i] != 0:
                    nx = side[i]

            first = next((i for i in range(n) if side[i] != 0), None)
            if first is None:
                continue
            occ = home = side[first]
            net = bsince = 0
            mag = 0.0
            for i in range(first + 1, n):
                tgt = occ if occ != 0 else -home
                if side[i - 1] != 0 and side[i] == 0:          # left an OOB: target flips, push inverts
                    home, occ = side[i - 1], 0
                    net, mag = -net, -mag
                    tgt = -home
                elif side[i] != 0:
                    occ = home = side[i]

                dv = float(bb[i] - bb[i - 1])
                net += int(np.sign(dv)) * tgt
                mag += dv * tgt
                bsince += 1

                # RECORD only TRAVELLING bars (K not sitting in an OOB) — Joe's 10:00 case
                if occ == 0 and bts[i] >= win0 and nxt[i] != 0:
                    dist = float(HI - k[i]) if tgt == 1 else float(k[i] - LO)
                    bars.append((tf, kvar, int(bts[i]), zone_of(dist), net, mag, bsince,
                                 1 if nxt[i] == tgt else 0))

                if i in curls:
                    net, bsince = 0, 0                          # the curl IS the pressure being spent
                    mag = 0.0
        print(f'  mo{tf} done', flush=True)

cut = win0 + int(0.6 * (end_ms - win0))
print(f'\n{len(bars)} travelling bars · IS/OOS cut {dt(cut):%Y-%m-%d}\n')

A = bars
base = np.mean([b[7] for b in A])
print(f'BASE RATE  P(K reaches its target OOB before the opposite) = {base:.3f}   n={len(A)}\n')

# ---- does accumulated pressure separate walk-forward from flip? --------------------------------
BUCKETS = [(-99, -6, 'net <= -6  (heavy AWAY)'), (-6, -3, 'net -5..-3'), (-3, -1, 'net -2..-1'),
           (-1, 2, 'net -0..+1  (NEITHER)'), (2, 4, 'net +2..+3'), (4, 7, 'net +4..+6'),
           (7, 99, 'net >= +7  (heavy TOWARD)')]

for kv, lab in (('r', '7|5|7'), ('b', '5|74|29')):
    print(f'--- K = {lab} ---')
    print(f"  {'bucket':<24} {'n_IS':>6} {'P_IS':>6} {'n_OOS':>6} {'P_OOS':>6} {'lift_OOS':>8}")
    S = [b for b in A if b[1] == kv]
    b_oos = np.mean([b[7] for b in S if b[2] >= cut])
    for lo, hi, name in BUCKETS:
        i_s = [b[7] for b in S if b[2] < cut and lo <= b[4] < hi]
        o_s = [b[7] for b in S if b[2] >= cut and lo <= b[4] < hi]
        if len(o_s) < 20:
            continue
        print(f'  {name:<24} {len(i_s):>6} {np.mean(i_s) if i_s else 0:>6.3f} '
              f'{len(o_s):>6} {np.mean(o_s):>6.3f} {np.mean(o_s)/b_oos:>8.2f}')
    print(f'  {"BASE (OOS)":<24} {"":>6} {"":>6} {len([b for b in S if b[2]>=cut]):>6} {b_oos:>6.3f}\n')

# ---- and per zone: is the walk-forward verdict usable MID-BOARD? --------------------------------
print('WALK-FORWARD cell (net -0..+1, i.e. "no #1 and no #2") — OOS only\n')
print(f"  {'K':<10} {'zone':<10} {'n':>6} {'P(reach)':>9} {'base':>7} {'lift':>6}")
for kv, lab in (('r', '7|5|7'), ('b', '5|74|29')):
    S = [b for b in A if b[1] == kv and b[2] >= cut]
    bz = np.mean([b[7] for b in S])
    for z in ('CLOSE', 'APPROACH', 'MID'):
        w = [b[7] for b in S if b[3] == z and -1 <= b[4] < 2]
        if len(w) < 20:
            continue
        print(f'  {lab:<10} {z:<10} {len(w):>6} {np.mean(w):>9.3f} {bz:>7.3f} {np.mean(w)/bz:>6.2f}')
