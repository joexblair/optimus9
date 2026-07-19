"""hs30_veto.py — the mo engine as a VETO on the hs30 cross. (Joe 0714)

Joe: "my gut says that if mo is not creating a #1 or #2 outcome by 11:00, then we walk forward until we
      get a signal and block the s30m crosses"

This INVERTS what mo_walk.py asked. That asked "does the NEITHER band FORECAST a breach" (null at MID).
This asks "does the NEITHER band mean DON'T TRADE YET" — a veto, not a forecast. Different claim.

THE EVENT (hs30 = the 30-MINUTE set; `h` nulls the DB s30 = 30-SECOND collision):
    SHORT   hs30r OOB-high  AND  hs30m crosses BELOW hs30r     (30-min bar grid — it won the A/B)
    LONG    hs30r OOB-low   AND  hs30m crosses ABOVE hs30r
    hs30r = k 7|5|7|ohlc4   ·   hs30m = bb 6|0.45|ohlc4   (Joe 0714 — corrects the 0.56 I used)

THE VETO STATE, read on s45 at the cross moment (the mo engine owns its own BB — Joe: "yes, this belongs
to the momo engine"):
    K  = s45r  k 7|5|7|ohlc4        BB = s45mo  bb 7|0.64|close        TF 45
    net = accumulated sign(bb[t]-bb[t-1]) * target, since the last s45r curl. Reset at each curl.
    NEITHER  net in [-1,+2)   -> no #1, no #2. BLOCK, walk forward.
    #1       net >= +2        -> toward-target push
    #2       net <= -1        -> away-from-target push

"until we get a signal" is ambiguous between #1, #2, and either — so all three are reported, not picked.

SCORE  jig.score.entry_quality — MAE/MFE to the next favourable swing, exit-independent. No net, no PnL.
Causal/emerging; every read via the jig.

  python3 hs30_veto.py [days] [warmup_hours] [swing_pct]        (default 32d, 600h, 2%)
"""
import sys, datetime as dtm
from datetime import timezone
import collections
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
WARM = int(sys.argv[2]) if len(sys.argv) > 2 else 600
SWING = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
HI, LO = 85.0, 15.0
GRID = 1800_000                                   # the 30-min bar grid

OV = {**kline('hs30r', 30, k_len=7, rsi=5, stc=7, src='ohlc4'),
      **bbline('hs30m', 30, length=6, mult=0.45, src='ohlc4'),
      **kline('s45r',   45, k_len=7, rsi=5, stc=7, src='ohlc4'),
      **bbline('s45mo', 45, length=7, mult=0.64, src='close')}


def zone_of(d):
    return 'IN_OOB' if d < 0 else ('CLOSE' if d < 15 else ('APPROACH' if d < 35 else 'MID'))


end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
win0 = end_ms - DAYS * 24 * 3600_000
print(f'{DAYS}d · {WARM}h warmup · swing {SWING}%', flush=True)

with Jig(end_ms, hours=DAYS * 24, warmup=WARM, overrides=OV) as j:
    C, ts = j.causal, np.asarray(j.ts, np.int64)
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)

    # ---- the mo state on s45, per 45-min bar, then broadcast to every 5s bar ----------------------
    g45 = np.flatnonzero((ts % (45 * 60 * 1000)) == 0)
    k45 = C.line('s45r')[g45]
    bb45 = C.line('s45mo')[g45]
    side45 = np.where(k45 >= HI, 1, np.where(k45 <= LO, -1, 0))
    curl45 = {}
    for dirn in (+1, -1):
        for t in C.curl(ts[g45], C.line('s45r')[g45], dirn):
            curl45[int(np.searchsorted(ts[g45], t))] = dirn

    n45 = len(g45)
    st_net = np.zeros(n45, int)                   # accumulated pressure, signed by target
    st_zone = np.array(['?'] * n45, object)
    first = next((i for i in range(n45) if side45[i] != 0), 0)
    occ = home = side45[first] if side45[first] != 0 else 1
    net = 0
    for i in range(first + 1, n45):
        tgt = occ if occ != 0 else -home
        if side45[i - 1] != 0 and side45[i] == 0:
            home, occ = side45[i - 1], 0
            net = -net
            tgt = -home
        elif side45[i] != 0:
            occ = home = side45[i]
        net += int(np.sign(bb45[i] - bb45[i - 1])) * tgt
        dist = float(HI - k45[i]) if tgt == 1 else float(k45[i] - LO)
        st_net[i], st_zone[i] = net, zone_of(dist)
        if i in curl45:
            net = 0                               # the curl IS the pressure being spent

    # broadcast: at any 5s bar, the mo state is the LAST COMPLETED 45-min bar's (causal)
    slot = np.searchsorted(ts[g45], ts, side='right') - 1
    slot = np.clip(slot, 0, n45 - 1)
    bar_net, bar_zone = st_net[slot], st_zone[slot]

    # ---- the crosses --------------------------------------------------------------------------------
    rs = C.sign('hs30r')
    x = C.cross('hs30m', 'hs30r', GRID)
    hit = np.flatnonzero(((rs == 1) & (x == -1)) | ((rs == -1) & (x == 1)))
    hit = hit[ts[hit] >= win0]
    ent = [(int(ts[i]), int(rs[i]), -int(rs[i]), int(i)) for i in hit]
    q = j.score.entry_quality(ent, swing_pct=SWING)
    print(f'{len(ent)} crosses  ·  hs30m bb 6|0.45|ohlc4\n')

    R = []                                        # (ms, bd, mae, mfe, mo_net, mo_zone)
    for i, e in enumerate(ent):
        b = e[3]
        R.append((e[0], e[2], float(q[i][4]), float(q[i][5]), int(bar_net[b]), str(bar_zone[b])))


def tab(title, rows):
    if len(rows) < 5:
        print(f'  {title:<26} n={len(rows)}   (too few)')
        return
    m = np.array([r[2] for r in rows]); f = np.array([r[3] for r in rows])
    print(f'  {title:<26} {len(rows):>4} {np.median(m):>7.2f} {np.percentile(m,90):>7.2f} '
          f'{np.median(f):>7.2f} {np.percentile(f,90):>7.2f} '
          f'{np.median(f)/max(np.median(m),1e-9):>8.2f} {100*np.mean(m>2):>5.0f}%')


NEITHER = lambda r: -1 <= r[4] < 2
P1 = lambda r: r[4] >= 2                          # toward-target push
P2 = lambda r: r[4] < -1                          # away-from-target push

print(f"  {'':<26} {'n':>4} {'MAEmed':>7} {'MAEp90':>7} {'MFEmed':>7} {'MFEp90':>7} {'MFE/MAE':>8} {'MAE>2':>6}")
tab('ALL (no veto)', R)
print()
tab('BLOCKED  (NEITHER)', [r for r in R if NEITHER(r)])
tab('ALLOWED  (#1 or #2)', [r for r in R if not NEITHER(r)])
print()
tab('  ALLOWED by #1 only', [r for r in R if P1(r)])
tab('  ALLOWED by #2 only', [r for r in R if P2(r)])
print()
print('  --- by the s45r zone at the cross ---')
for z in ('IN_OOB', 'CLOSE', 'APPROACH', 'MID'):
    tab(f'  {z}  BLOCKED', [r for r in R if NEITHER(r) and r[5] == z])
    tab(f'  {z}  ALLOWED', [r for r in R if not NEITHER(r) and r[5] == z])
print()
print('  --- per week, ALLOWED only ---')
wk = collections.defaultdict(list)
for r in R:
    if not NEITHER(r):
        w = dt(r[0]).isocalendar()
        wk[f'{w[0]}-W{w[1]:02d}'].append(r)
for w in sorted(wk):
    tab(f'  {w}', wk[w])
print()
print('  --- 07-11 ---')
for r in R:
    d = dt(r[0])
    if d.strftime('%m-%d') == '07-11':
        v = 'BLOCK ' if NEITHER(r) else ('ALLOW#1' if P1(r) else 'ALLOW#2')
        print(f'    {d:%H:%M}  {"SHORT" if r[1]==-1 else "LONG":<5}  {v:<8} '
              f'mo_net {r[4]:>3}  s45r {r[5]:<9} MAE {r[2]:>5.2f}  MFE {r[3]:>5.2f}')
