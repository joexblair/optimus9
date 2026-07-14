"""cs_ladder.py — does the cs ladder see the cs120 bias flip coming? (Joe 0714)

Joe: "because it is so slow, we can't catch the reversal without more dimensions. cs30/45/60 turning while
cs120 is still pinned is the pressure building."  The cs series IS a ladder — read it DOWNWARD.

  BIAS      cs120b OOB (>=85 hi / <=15 lo) = the slow gravity.
  FLIP      cs120b coarse-CURLS off that OOB side, toward the middle.   (coarse curl, no wob — the same
            producer every s-line uses: jig.coarse + jig.curl -> lr_v2._curl_detect.)
  QUESTION  before each flip, how far DOWN the ladder does agreement run, and how many minutes early?
  CONTROL   and how often does a fast rung curl WITHOUT cs120 following?  Without this the whole thing is
            a hindsight story.

Every read via the jig. Causal. No caps.
  python3 cs_ladder.py [days]        (default 7)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
import bias_emit as BE
import arm_walk as AW

# Joe 0714:  b = 11|21|77|close  ->  k_len 11 | rsi 21 | stc 77   ->  DB ('k', rsi, stc, k_len, src)
#            m =  7|0.45|close
B_CFG = ('k', 21, 77, 11, 'close')
M_CFG = ('bb', 7, 0.45, 'close')
FAST = [8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 30, 45, 60]   # the leaders
SLOW = 120                                                                       # the bias line
HI, LO = 85.0, 15.0
FOLLOW_MIN = 120        # a fast curl "led" a flip if cs120 curls the same way within this many minutes


def overrides():
    o = {}
    for tf in FAST + [SLOW]:
        o[f'cs{tf}b'] = (tf * 60, B_CFG, 'emerging')
        o[f'cs{tf}m'] = (tf * 60, M_CFG, 'emerging')
    return o


def curls(C, ts, name, tf, direction):
    """Coarse curl of a cs rung — same seam rule as every other ladder (arm_walk.curl_div)."""
    seam = tf * 60 // AW.curl_div(tf, AW.parse_bands(AW.DEFAULT_BANDS))
    return sorted(int(np.searchsorted(ts, t)) for t in C.curl(*C.coarse(name, seam * 1000), direction))


days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
end = dtm.datetime.now(timezone.utc)
end_ms = int(end.timestamp() * 1000)

with Jig(end_ms, hours=days * 24, warmup=600, overrides=overrides()) as j:
    C = j.causal
    ts, px = np.asarray(j.ts, np.int64), np.asarray(j.px, float)
    n = len(ts)
    win0 = end_ms - days * 24 * 3600_000
    dt = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M')
    mins = lambda a, b: (ts[b] - ts[a]) / 60000.0

    slow = C.line(f'cs{SLOW}b')
    slow_side = np.where(slow >= HI, 1, np.where(slow <= LO, -1, 0))

    print(f'cs{SLOW}b = k_len 11 | rsi 21 | stc 77 | close     {days} days')
    print(f'  OOB-LOW  {100 * np.mean(slow_side[ts >= win0] == -1):.0f}% of bars   '
          f'OOB-HIGH {100 * np.mean(slow_side[ts >= win0] == 1):.0f}%   '
          f'in-band {100 * np.mean(slow_side[ts >= win0] == 0):.0f}%')
    print()

    # ---- the FLIP events: cs120b curls off its OOB side, toward the middle -----------------------
    flips = []
    for es, lab in ((-1, 'LO->up'), (1, 'HI->down')):
        for k in curls(C, ts, f'cs{SLOW}b', SLOW, -es):        # curl toward the middle
            if ts[k] >= win0 and slow_side[k] == es:
                flips.append((k, es))
    flips.sort()
    print(f'cs{SLOW} FLIPS (coarse curl while OOB): {len(flips)}')
    for k, es in flips:
        print(f'   {dt(k)}   from {"LOW" if es == -1 else "HIGH"}   cs{SLOW}b {slow[k]:.1f}   px {px[k]:.5f}')
    print()

    # ---- per-rung: lead time into each flip, and the CONTROL (how often it cries wolf) -----------
    print(f'{"rung":>5} | {"curls":>6} {"led a flip":>10} {"hit rate":>8} | {"lead (min)":>10} | '
          f'{"P(flip|this rung curled)":>24}')
    print('-' * 84)
    stats = {}
    for tf in FAST:
        led, leads, tot = 0, [], 0
        for es in (-1, 1):
            fl = [k for k, e in flips if e == es]
            for c in curls(C, ts, f'cs{tf}b', tf, -es):        # same direction as the flip
                if ts[c] < win0 or slow_side[c] != es:         # only while the bias is pinned that way
                    continue
                tot += 1
                nxt = [f for f in fl if 0 <= mins(c, f) <= FOLLOW_MIN]
                if nxt:
                    led += 1
                    leads.append(mins(c, nxt[0]))
        hit = led / tot if tot else 0.0
        stats[tf] = (tot, led, hit, np.median(leads) if leads else np.nan)
        print(f'{tf:>5} | {tot:>6} {led:>10} {hit:>7.0%} | '
              f'{(f"{np.median(leads):.0f}" if leads else "-"):>10} | {hit:>23.0%}')

    # ---- CONFLUENCE: does agreement DEPTH raise the hit rate? ------------------------------------
    print()
    print('CONFLUENCE — at each fast-rung curl, how many OTHER rungs curled the same way within 30 min?')
    print(f'{"rungs agreeing":>15} | {"n":>5} {"led a flip":>10} {"hit rate":>8}')
    print('-' * 46)
    allc = {tf: {es: set(c for c in curls(C, ts, f'cs{tf}b', tf, -es) if ts[c] >= win0) for es in (-1, 1)}
            for tf in FAST}
    buckets = {}
    for tf in FAST:
        for es in (-1, 1):
            fl = [k for k, e in flips if e == es]
            for c in allc[tf][es]:
                if slow_side[c] != es:
                    continue
                agree = sum(1 for t2 in FAST if t2 != tf
                            and any(abs(mins(c2, c)) <= 30 for c2 in allc[t2][es]))
                hit = any(0 <= mins(c, f) <= FOLLOW_MIN for f in fl)
                b = min(agree, 12)
                buckets.setdefault(b, [0, 0])
                buckets[b][0] += 1
                buckets[b][1] += int(hit)
    for b in sorted(buckets):
        nn, hh = buckets[b]
        print(f'{b:>15} | {nn:>5} {hh:>10} {hh / nn:>7.0%}')
