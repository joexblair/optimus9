"""mo_bb2.py — "two BB lines ahead of r" + the walk-forward verdict, at MID. (Joe 0714)

Joe: "we know that BB lines lead a K line, and at 11:00 both s45m and s45Mage are above s45r.
      how often does (2 BB lines closer to the target OOB than r + momo's walk forward verdict)
      at mid zone produce an r breach without being pushed back?"

BB2   both m AND Mage on the TARGET side of r   (target hi -> both above r · target lo -> both below r)
WF    the walk-forward verdict: accumulated BB pressure since the last curl is in the NEITHER band
      (net -0..+1) — no #1 push and no #2 push. Nothing is bending r.
      Run on TWO BB lines, separately: the set's own m, and the mo BB (7|0.64|close). No silent pick.

OUTCOME, both readings of "without being pushed back":
  REACH  r touches its TARGET OOB before the OPPOSITE one.
  CLEAN  same, AND it never away-curled on the way there.

ZONE: r's distance to its target boundary. Joe's question is MID; the other zones are context.
Lines: uniform s-set (the one that WON the hs30 cross A/B) — r k 7|5|7|ohlc4 · m bb 6|0.56|ohlc4
       · Mage bb 37|0.83|ohlc4.  mo BB: bb 7|0.64|close.
Base rate first, IS/OOS split, no fitted threshold. Causal/emerging; every read via the jig.

  python3 mo_bb2.py [days] [warmup_hours]        (default 32d, 600h)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline

TFS = [15, 25, 30, 45]
HI, LO = 85.0, 15.0
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
WARM = int(sys.argv[2]) if len(sys.argv) > 2 else 600

R    = dict(k_len=7, rsi=5,  stc=7,   src='ohlc4')
M    = dict(length=6,  mult=0.56, src='ohlc4')
MAGE = dict(length=37, mult=0.83, src='ohlc4')
MOBB = dict(length=7,  mult=0.64, src='close')
WF_LO, WF_HI = -1, 2                                   # the NEITHER band: net in [-1, +2)


def zone_of(d):
    return 'IN_OOB' if d < 0 else ('CLOSE' if d < 15 else ('APPROACH' if d < 35 else 'MID'))


def overrides():
    o = {}
    for tf in TFS:
        o.update(kline(f'z{tf}r', tf, **R))
        o.update(bbline(f'z{tf}m', tf, **M))
        o.update(bbline(f'z{tf}Mage', tf, **MAGE))
        o.update(bbline(f'z{tf}mo', tf, **MOBB))
    return o


end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
win0 = end_ms - DAYS * 24 * 3600_000
print(f'{DAYS}d · {WARM}h warmup · TFs {TFS}', flush=True)

rows = []                       # (tf, ms, zone, bb2, wf_m, wf_mo, reach, clean)
with Jig(end_ms, hours=DAYS * 24, warmup=WARM, overrides=overrides()) as j:
    C, ts = j.causal, np.asarray(j.ts, np.int64)
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)

    for tf in TFS:
        g = (ts % (tf * 60 * 1000)) == 0
        bts = ts[g]
        k    = C.line(f'z{tf}r')[g]
        m    = C.line(f'z{tf}m')[g]
        mage = C.line(f'z{tf}Mage')[g]
        mo   = C.line(f'z{tf}mo')[g]
        n = len(bts)

        side = np.where(k >= HI, 1, np.where(k <= LO, -1, 0))
        curl_dir = {}
        for dirn in (+1, -1):
            for t in C.curl(bts, k, dirn):
                curl_dir[int(np.searchsorted(bts, t))] = dirn

        nxt = np.zeros(n, np.int8); nx = 0             # the forward truth: next OOB side r touches
        for i in range(n - 1, -1, -1):
            nxt[i] = nx
            if side[i] != 0:
                nx = side[i]

        first = next((i for i in range(n) if side[i] != 0), None)
        if first is None:
            continue
        occ = home = side[first]
        net_m = net_mo = 0
        for i in range(first + 1, n):
            tgt = occ if occ != 0 else -home
            if side[i - 1] != 0 and side[i] == 0:
                home, occ = side[i - 1], 0
                net_m, net_mo = -net_m, -net_mo
                tgt = -home
            elif side[i] != 0:
                occ = home = side[i]

            net_m  += int(np.sign(m[i]  - m[i - 1]))  * tgt
            net_mo += int(np.sign(mo[i] - mo[i - 1])) * tgt

            if occ == 0 and bts[i] >= win0 and nxt[i] != 0:
                dist = float(HI - k[i]) if tgt == 1 else float(k[i] - LO)
                bb2 = (m[i] > k[i] and mage[i] > k[i]) if tgt == 1 else (m[i] < k[i] and mage[i] < k[i])
                reach = 1 if nxt[i] == tgt else 0
                # CLEAN: reaches the target having never away-curled on the way
                clean = 0
                if reach:
                    q = next(x for x in range(i + 1, n) if side[x] != 0)
                    clean = 0 if any(curl_dir.get(x, 0) * tgt == -1 for x in range(i + 1, q)) else 1
                rows.append((tf, int(bts[i]), zone_of(dist), int(bb2),
                             int(WF_LO <= net_m < WF_HI), int(WF_LO <= net_mo < WF_HI), reach, clean))

            if i in curl_dir:
                net_m = net_mo = 0                     # the curl IS the pressure being spent
        print(f'  z{tf} done', flush=True)

cut = win0 + int(0.6 * (end_ms - win0))
print(f'\n{len(rows)} travelling bars · IS/OOS cut {dt(cut):%Y-%m-%d}\n')

CONDS = [
    ('BASE (all bars)',            lambda r: True),
    ('BB2 alone',                  lambda r: r[3]),
    ('WF alone (set m)',           lambda r: r[4]),
    ('WF alone (mo BB)',           lambda r: r[5]),
    ('BB2 + WF (set m)',           lambda r: r[3] and r[4]),
    ('BB2 + WF (mo BB)',           lambda r: r[3] and r[5]),
    ('BB2 + WF both',              lambda r: r[3] and r[4] and r[5]),
]

for tf in TFS:
    for zone in ('MID', 'APPROACH', 'CLOSE'):
        S = [r for r in rows if r[0] == tf and r[2] == zone]
        oos = [r for r in S if r[1] >= cut]
        if len(oos) < 50:
            continue
        b_r = np.mean([r[6] for r in oos]); b_c = np.mean([r[7] for r in oos])
        print(f'--- s{tf}  ·  {zone}  ·  OOS base P(REACH) {b_r:.3f}  P(CLEAN) {b_c:.3f}  n={len(oos)} ---')
        print(f"  {'condition':<22} {'n_IS':>6} {'P_IS':>6} | {'n_OOS':>6} {'REACH':>6} {'lift':>5} "
              f"{'CLEAN':>6} {'lift':>5}")
        for name, f in CONDS:
            i_s = [r for r in S if r[1] < cut and f(r)]
            o_s = [r for r in S if r[1] >= cut and f(r)]
            if len(o_s) < 15:
                print(f'  {name:<22} {len(i_s):>6} {"":>6} | {len(o_s):>6}   (n<15)')
                continue
            pi = np.mean([r[6] for r in i_s]) if i_s else 0
            pr = np.mean([r[6] for r in o_s]); pc = np.mean([r[7] for r in o_s])
            print(f'  {name:<22} {len(i_s):>6} {pi:>6.3f} | {len(o_s):>6} {pr:>6.3f} {pr/b_r:>5.2f} '
                  f'{pc:>6.3f} {pc/max(b_c,1e-9):>5.2f}')
        print()
