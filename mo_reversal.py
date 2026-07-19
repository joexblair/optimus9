"""mo_reversal.py — the reversal CALL, scored on price. (Joe 0714)

THE SIGNAL (Joe's model, now measured):
  A K line will not easily bend away from its target. Measured cost to bend it, in bars since the last curl:
      TOWARD the target (#1)   1 bar          <- cheap
      AWAY  from it    (#2)   3-6 bars        <- dear, and it scales with proximity:
                                                 IN_OOB 6 · CLOSE 5 · APPROACH 3 · MID 2
  So: an AWAY-curl that only cost a #1-sized push means the target has FLIPPED. The market shifted.
  That is the reversal call, and it is what this scores.

ENTRY   at the cheap away-curl.  Direction = where K just turned:  bd = -target
        (target hi -> K turns down -> SHORT · target lo -> K turns up -> LONG)
THRESHOLD  "cheap" = cost_bars <= the median TOWARD-cost for that (K-variant, zone), learned IN-SAMPLE only.
SCORE   jig.score.entry_quality -> MAE/MFE to the next favourable swing, EXIT-INDEPENDENT.
        Swept over 4% / 3% / 2% swing scales (Joe).  Reported PER WEEK.
        MAE/MFE only — no net, no PnL (Joe 0711).

  python3 mo_reversal.py [days] [warmup_hours]      (default 32d, 600h)
"""
import sys, datetime as dtm
from datetime import timezone
import collections
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline

TFS = [15, 25, 30, 45]
HI, LO = 85.0, 15.0
BB = dict(length=7, mult=0.64, src='close')
KVARS = {'b': dict(k_len=5, rsi=74, stc=29, src='hlc3'),
         'r': dict(k_len=7, rsi=5, stc=7, src='ohlc4')}
SWINGS = [4.0, 3.0, 2.0]
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

with Jig(end_ms, hours=DAYS * 24, warmup=WARM, overrides=overrides()) as j:
    C = j.causal
    ts = np.asarray(j.ts, np.int64)
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)

    # ---- collect every curl, with its cost, zone, direction ---------------------------------------
    curls = []                                     # (tf, kvar, bar_5s, ms, cdir, zone, cost_bars, tgt)
    for tf in TFS:
        m = (ts % (tf * 60 * 1000)) == 0
        bts, idx5 = ts[m], np.flatnonzero(m)
        bb = C.line(f'mo{tf}m')[m]
        n = len(bts)
        for kvar in KVARS:
            k = C.line(f'mo{tf}{kvar}')[m]
            side = np.where(k >= HI, 1, np.where(k <= LO, -1, 0))
            cd = {}
            for dirn in (+1, -1):
                for t in C.curl(bts, k, dirn):
                    cd[int(np.searchsorted(bts, t))] = dirn
            first = next((i for i in range(n) if side[i] != 0), None)
            if first is None:
                continue
            occ = home = side[first]
            cost = 0
            for i in range(first + 1, n):
                tgt = occ if occ != 0 else -home
                if side[i - 1] != 0 and side[i] == 0:
                    home, occ = side[i - 1], 0
                    tgt = -home
                elif side[i] != 0:
                    occ = home = side[i]
                cost += 1
                if i in cd:
                    dist = float(HI - k[i]) if tgt == 1 else float(k[i] - LO)
                    curls.append((tf, kvar, int(idx5[i]), int(bts[i]), int(cd[i] * tgt),
                                  zone_of(dist), cost, int(tgt)))
                    cost = 0

    cut = win0 + int(0.6 * (end_ms - win0))        # 60% in-sample
    print(f'{len(curls)} curls · {DAYS}d · IS/OOS cut {dt(cut):%Y-%m-%d}')

    # ---- THRESHOLD: the median TOWARD cost per (kvar, zone) — IN-SAMPLE ONLY ----------------------
    thr = {}
    for kv in KVARS:
        for z in ('IN_OOB', 'CLOSE', 'APPROACH', 'MID'):
            t = [c[6] for c in curls if c[1] == kv and c[5] == z and c[4] == 1 and c[3] < cut]
            thr[(kv, z)] = np.median(t) if len(t) >= 10 else 1.0
    print('  "cheap" threshold (IS median TOWARD-cost, bars):', {f'{a}/{b}': v for (a, b), v in thr.items()})

    # ---- the SIGNAL: an away-curl that cost no more than a toward-curl ----------------------------
    sig = [c for c in curls if c[4] == -1 and c[6] <= thr[(c[1], c[5])] and c[3] >= win0]
    print(f'  reversal calls: {len(sig)}   (of {len([c for c in curls if c[4]==-1])} away-curls)')
    print()

    for pct in SWINGS:
        for kv, lab in (('r', '7|5|7'), ('b', '5|74|29')):
            ent, meta = [], []
            for (tf, kvar, bar, ms, cdir, z, cost, tgt) in sig:
                if kvar != kv:
                    continue
                bd = -tgt                                  # K just turned this way
                ent.append((ms, -bd, bd, bar))
                meta.append((tf, z, ms))
            if not ent:
                continue
            q = j.score.entry_quality(ent, swing_pct=pct)
            wk = collections.defaultdict(list)
            for i, r in enumerate(q):
                w = dt(meta[i][2]).isocalendar()
                wk[f'{w[0]}-W{w[1]:02d}'].append((float(r[4]), float(r[5])))
            print(f'=== swing {pct:.0f}%  ·  K {lab}  ·  {len(q)} calls ===')
            print(f"  {'week':<10} {'n':>4} {'MAEmed':>7} {'MAEp90':>7} {'MFEmed':>7} {'MFEp90':>7} "
                  f"{'MFE/MAE':>8} {'MAE>2':>6}")
            allm, allf = [], []
            for w in sorted(wk):
                a = np.array(wk[w])
                m, f = a[:, 0], a[:, 1]
                allm += list(m)
                allf += list(f)
                print(f'  {w:<10} {len(a):>4} {np.median(m):>7.2f} {np.percentile(m, 90):>7.2f} '
                      f'{np.median(f):>7.2f} {np.percentile(f, 90):>7.2f} '
                      f'{np.median(f) / max(np.median(m), 1e-9):>8.2f} {100 * np.mean(m > 2):>5.0f}%')
            m, f = np.array(allm), np.array(allf)
            print(f'  {"ALL":<10} {len(m):>4} {np.median(m):>7.2f} {np.percentile(m, 90):>7.2f} '
                  f'{np.median(f):>7.2f} {np.percentile(f, 90):>7.2f} '
                  f'{np.median(f) / max(np.median(m), 1e-9):>8.2f} {100 * np.mean(m > 2):>5.0f}%')
            print()
