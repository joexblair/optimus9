"""build_tf_walk - Joe's TF2-23 walk. Joe 0909.

THE MECHANIC HAS NO NAME. Joe has called it "the mech" and "the walk"; this filename is a
placeholder. Do not coin one - rename on his word.

THE SPEC IS docs/tf_walk_spec.md. It carries Joe's six steps verbatim, every rule with its
provenance, what is still MINE and unruled, and the superseded configurations whose numbers are
void. Read it before changing anything here.

WHAT IS MINE AND UNRULED, restated so it cannot decay into background:
  - STEP 1 IS A STATE, NOT AN EVENT. "walk forward until ws1r is oob" is true across many
    contiguous bars. This takes the RISING EDGE of a 6-bar hold, one walk per edge. The
    alternative is the first bar beyond the boundary with no hold. Every walk count and row
    count below depends on which Joe means.
  - THE CLEAN LATCH latches and never resets. Step 3 needs a tagged (clean) line to be OOB, and
    a line cannot be inside the fence and oob at once, so a live state test makes step 3
    unreachable. No dirtying event was specified, so the latch is monotonic - MEASURED: all 22
    timeframes are clean at 00:18 and still clean at 24:00, so the clean test filters nothing.
  - A MID-WALK DR FLIP has no rule. The walk continues; each row carries the dr at its own bar.
  - STRICT VS INCLUSIVE: ws1r's trigger uses cross_wob (strictly beyond the boundary); the
    tagged-line oob test uses at-or-above.

dr       ws1Mage AND ws13m both oob, SAME side. Previous dr holds until that happens.
         Joe 0909 replaced ws2Mage with ws1Mage.
fence    83 / 17  (MOMO_FENCE_R = 17)
clean    a dirty line goes clean when its r is INSIDE the fence and its verdict advances to momo
         or curl. NOT the 0731 rpl/exhv2 producer - Joe 0909: "we're not using the rpl logic".
exit     the highest CLEAN momentum-true TF has its x cross its m - dr -1 x crosses OVER m,
         dr +1 x crosses UNDER m - with Mage strictly closer to 50 than both x and m. Joe 0909
         withdrew his example values; the condition is built from his words, not the numbers.
advance  the next row needs a HIGHER tagged TF oob + sideways.
restart  the walk restarts after the x-cross-m event, so walks CHAIN and do not overlap.
xwob     6 bars = 30 s everywhere EXCEPT the x-cross-m test, which is 12 bars = 60 s.
window   the WALK is contained to 08-25. The verdict/clean warm-up starts 08-23 so both are warm
         at 00:18 - Joe contained the walk, not the warm-up.

THE VERDICT CACHE IS KEYED ON THE DR SOURCE. Verdicts are computed AT each bar's dr, so a
different dr rule is a different verdict set. Keying on the bar range alone silently reuses the
wrong verdicts with no error.

    python3 build_tf_walk.py
"""
import sys, os, time, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
from datetime import timezone
import numpy as np
from optimus9.compute.line_config import override, mech_lines
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_g_why, momo_window
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.analysis.jig import _Causal
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

TFS = list(range(2, 24))
FENCE = 17.0
FH, FL = 100.0 - FENCE, FENCE
XWOB = 6         # 6 bars = 30 s. every crossing test EXCEPT x-cross-m
XWOB_XM = 12     # 12 bars = 60 s. Joe 0909: "increase the x cross m wob to 12"
W0, W1 = '2026-08-23 00:00:00', '2026-08-26 00:00:00'
WALK0, WALK1 = '2026-08-25 00:00:00', '2026-08-26 00:00:00'
START = '2026-08-25 00:18:00'
SCR = os.environ.get('TF_WALK_CACHE', os.path.join(os.path.dirname(os.path.abspath(__file__)), '.tf_walk_cache'))
os.makedirs(SCR, exist_ok=True)
# THE DR SOURCE IS IN THE CACHE NAME. The verdicts are computed AT each bar's dr, so a
# different dr rule is a different verdict set. The old signature checked only the bar
# range, which would have silently reused ws2Mage-dr verdicts under a ws1Mage dr.
DR_SRC = 'ws1Mage+ws13m'
CACHE = os.path.join(SCR, f'st_0823_0826_{DR_SRC}.npz')

t0 = time.time()
db = DatabaseManager(**get_db_config()); db.connect()
sy = db.execute('SELECT pxsmooth_dema_src s,pxsmooth_dema_len l,hi_boundary hi,lo_boundary lo '
                'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
HI, LO = float(sy['hi']), float(sy['lo'])
SPEC = {}
for g in mech_lines(db, 'wsf'):
    if g['role'] not in SPEC:
        _t, s, m = g['override']; SPEC[g['role']] = (s, m)
BK = {tf: momo_bank(db, tf) for tf in range(1, 24)}
db.disconnect()

ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
             {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
u = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc).strftime('%H:%M:%S')
ms = lambda s: int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                   .replace(tzinfo=timezone.utc).timestamp() * 1000)
L = lambda tf, role: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
                     override(tf * 60, *SPEC[role])) + '.npy'))
R = {tf: L(tf, 'r') for tf in range(1, 24)}
X = {tf: L(tf, 'x') for tf in TFS}
M = {tf: L(tf, 'm') for tf in TFS}
G = {tf: L(tf, 'Mage') for tf in TFS}
G1 = L(1, 'Mage')          # ws1Mage - the dr source, TF1, not in TFS (2..23)
i0, i1 = int(np.searchsorted(ts, ms(W0))), int(np.searchsorted(ts, ms(W1)))
KS = int(np.searchsorted(ts, ms(START)))
KW0 = int(np.searchsorted(ts, ms(WALK0)))
KW1 = int(np.searchsorted(ts, ms(WALK1)))
print(f'  warm-up {W0} -> {W1}   walk contained to 08-25   start {START}   xwob {XWOB} '
      f'= {XWOB*5} s (x-cross-m uses xwob {XWOB_XM} = {XWOB_XM*5} s)', flush=True)

g1, m13 = G1, M[13]        # Joe 0909: dr from ws1Mage + ws13m
DR = np.zeros(len(ts), np.int8); cur = 0
for k in range(i0 - 200000, i1 + 1):
    a, b = float(g1[k]), float(m13[k])
    if a == a and b == b:
        if a >= HI and b >= HI: cur = +1
        elif a <= LO and b <= LO: cur = -1
    DR[k] = cur
print(f'  dr at start {int(DR[KS]):+d}   dr flips on 08-25 '
      f'{int(np.count_nonzero(np.diff(DR[KW0:KW1+1])))}', flush=True)

CODE = {'none': 0, 'sideways': 1, 'curl': 2, 'momo': 3}
ST = None
if os.path.exists(CACHE):
    z = np.load(CACHE)
    if int(z['sig'][0]) == i0 and int(z['sig'][1]) == i1:
        ST = {tf: z[f'st{tf}'] for tf in TFS}
        print(f'  verdicts from cache  {time.time()-t0:.0f}s', flush=True)
if ST is None:
    ST = {tf: np.zeros(len(ts), np.int8) for tf in TFS}
    for tf in TFS:
        Bk = BK[tf]; arr = R[tf]; out = ST[tf]
        with momo_config(Bk), momo_window(Bk['k_window'] * tf):
            for k in range(i0, i1 + 1):
                d = int(DR[k])
                if d:
                    out[k] = CODE[momo_g_why(arr, d, k, quad=True)[0]]
        print(f'    ws{tf}r verdicts done  {time.time()-t0:.0f}s', flush=True)
    np.savez(CACHE, sig=np.array([i0, i1]), **{f'st{tf}': ST[tf] for tf in TFS})

# ---- clean: latches when r is INSIDE the fence and the verdict is momo or curl (Joe 0909) ----
CLEAN = {}
for tf in TFS:
    r = R[tf]
    ev = (r >= FL) & (r <= FH) & np.isfinite(r) & (ST[tf] >= 2)
    c = np.zeros(len(ts), bool); on = False
    for k in range(i0, i1 + 1):
        if ev[k]: on = True
        c[k] = on
    CLEAN[tf] = c
print(f'  clean at 00:18       {sorted(tf for tf in TFS if CLEAN[tf][KS])}', flush=True)
print(f'  clean at 08-26 00:00 {sorted(tf for tf in TFS if CLEAN[tf][KW1])}', flush=True)

C = _Causal(None)
edge = lambda c: c & ~np.r_[False, c[:-1]]
XM = {}
for tf in TFS:
    d = X[tf] - M[tf]
    XM[(tf, +1)] = edge(C.cross_wob(d, 0.0, -1, XWOB_XM))   # dr +1: x crosses UNDER m
    XM[(tf, -1)] = edge(C.cross_wob(d, 0.0, +1, XWOB_XM))   # dr -1: x crosses OVER  m

hi_mom = np.zeros(len(ts), np.int8)
exitb = []
for k in range(i0, i1 + 1):
    d = int(DR[k])
    if not d: continue
    h = 0
    for tf in reversed(TFS):
        if ST[tf][k] >= 2 and CLEAN[tf][k]:
            h = tf; break
    hi_mom[k] = h
    if not h or not XM[(h, d)][k]: continue
    xv, mv, gv = float(X[h][k]), float(M[h][k]), float(G[h][k])
    if not (xv == xv and mv == mv and gv == gv): continue
    if abs(gv - 50.0) < abs(xv - 50.0) and abs(gv - 50.0) < abs(mv - 50.0):
        exitb.append(k)
exitb = np.array(exitb, int)
inw = exitb[(exitb >= KW0) & (exitb <= KW1)]
print(f'  exit events on 08-25: {len(inw)}', flush=True)
for k in inw:
    h = int(hi_mom[k])
    print(f'    {u(k)}  dr {int(DR[k]):+d}  tf {h}  x {float(X[h][k]):.2f}  m {float(M[h][k]):.2f}'
          f'  Mage {float(G[h][k]):.2f}', flush=True)

oob = lambda v, d: v == v and ((v >= HI) if d > 0 else (v <= LO))
infence = lambda v: v == v and (FL <= v <= FH)
r1 = R[1]
O1 = {+1: C.cross_wob(r1 - HI, 0.0, +1, XWOB), -1: C.cross_wob(r1 - LO, 0.0, -1, XWOB)}
# Joe 0909: "the walk re-starts after the x-cross-m event". So the walks CHAIN and do not
# overlap: step 1 looks forward from the previous walk's exit, not from every ws1r oob edge.
edges = [k for k in range(KS, KW1 + 1)
         if int(DR[k]) and O1[int(DR[k])][k] and not O1[int(DR[k])][k - 1]]
trig = []
pos = KS
while pos <= KW1:
    nxt = [k for k in edges if k >= pos]
    if not nxt:
        break
    kt = nxt[0]
    trig.append(kt)
    e = exitb[(exitb >= kt) & (exitb <= KW1)]
    pos = (int(e[0]) + 1) if len(e) else (KW1 + 1)
print(f'\n  ws1r oob confirming edges on 08-25 from {START[11:16]}: {len(edges)}', flush=True)
print(f'  walks after chaining (each starts at the previous exit): {len(trig)}', flush=True)
print(f'  {[u(k) for k in trig]}', flush=True)

print('\n=== THE WALK ===', flush=True)
rows = 0
for wi, kt in enumerate(trig, 1):
    d = int(DR[kt])
    tagged = sorted(tf for tf in TFS if ST[tf][kt] >= 2 and CLEAN[tf][kt])
    e = exitb[(exitb >= kt) & (exitb <= KW1)]
    kend = int(e[0]) if len(e) else KW1
    ex = (f'{u(kend)} tf {int(hi_mom[kend])}' if len(e) else 'none on 08-25 - runs to 24:00')
    print(f'\nwalk {wi}   ws1r oob {u(kt)}   dr {d:+d}   exit {ex}', flush=True)
    print(f'  tagged at trigger: {tagged if tagged else "none"}', flush=True)
    if not tagged: continue
    print(f'  {"row utc":<10}{"dr":>3}{"oob tf":>7}{"r":>8}{"sw bars":>8}{"sw start":>10}'
          f'  {"wk-tf-1":<11}{"wk-tf-2":<11}{"hi clean mom tf":>16}'
          f'  {"step4 clean momentum TFs (23 -> oobtf+1)":<44}', flush=True)
    cur = 0; k = kt; n = 0
    while k <= kend:
        hit = None
        for kk in range(k, kend + 1):
            dd = int(DR[kk])
            for tf in tagged:
                if tf > cur and ST[tf][kk] == 1 and oob(float(R[tf][kk]), dd):
                    hit = (kk, tf); break
            if hit: break
        if not hit: break
        kk, tf = hit
        s = kk
        while s - 1 >= i0 and ST[tf][s - 1] == 1: s -= 1
        up = [t for t in TFS if t > tf and infence(float(R[t][kk]))]
        w1 = f'{up[0]}:{float(R[up[0]][kk]):.2f}' if up else '-'
        w2 = f'{up[1]}:{float(R[up[1]][kk]):.2f}' if len(up) > 1 else '-'
        rev = [t for t in reversed(TFS) if t >= tf + 1 and ST[t][kk] >= 2 and CLEAN[t][kk]]
        print(f'  {u(kk):<10}{int(DR[kk]):>+3d}{tf:>7}{float(R[tf][kk]):>8.2f}{kk-s+1:>8}{u(s):>10}'
              f'  {w1:<11}{w2:<11}{int(hi_mom[kk]):>16}  {(str(rev) if rev else "none"):<44}',
              flush=True)
        n += 1; rows += 1; cur = tf; k = kk + 1
    if n == 0:
        print('  no tagged line reached oob + sideways before the exit', flush=True)
print(f'\n  walks {len(trig)}   rows {rows}   {time.time()-t0:.0f}s', flush=True)
