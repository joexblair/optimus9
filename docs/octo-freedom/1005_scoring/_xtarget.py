"""#61 — THE x-CROSS TARGET, SWEPT. 1008.

Joe 1008: *"B. I need to get to the best MAE/MFE quickly so that I can start working on the large
stops"* / *"we're sweeping, ie measuring - that nulls the block"*.

**#61 IS UNBLOCKED.** Its block read *"nothing measures ws{tf}x at all. The lines are cached for
timeframes 1 to 8 but `wsf_line_bar` holds only the r lines"*. Verified 1008: **all five roles - r,
x, m, Mage, b - are cached for ws1 to ws25** at score39's own window. And a sweep is the
measurement, so the block is void by Joe's ruling.

THE TARGET AS BUILT, in `_chain10.xcond`:
    t1, t2 = h + 1, h + 2
    xv = X[h][k]
    c = (xv < R[t1][k] and xv < R[t2][k]) if d > 0 else (xv > R[t1][k] and xv > R[t2][k])
    return c and bnd(t1, k, d) == '.' and bnd(t2, k, d) == '.'

THREE THINGS VARIED:

  the target ROLE  **r** (current) / **m** / **Mage** / **b** - #61's own menu. Plus **fence**,
                   which is MY reading of #61's *"boundary"*: the x crossing the ex-fence LEVEL
                   rather than a line. #61 leaves *"whether the cross must be of ALL of Mage, b and
                   the boundary, or ANY one of them"* open and unasked, so only SINGLE targets are
                   swept - the combined target is still Joe's to rule.

  the target TFs   **both** = h+1 AND h+2, what the lineage walk uses now.
                   **next** = h+1 only.
                   **self** = h itself - and this is #61's own structure, *"the fast partner crosses
                   ws{weak-mage-tf}r"*, same TF, different role. §14a measured `self` 0.16-0.17
                   BETTER than `both` on the 15:41 leg.

  the in-fence test on the target   on (current) / off.

THE IN-FENCE TEST IS APPLIED TO THE TARGET LINE, not to r, when the role changes - the current code
tests it on the same lines it crosses, so this preserves that. Stated because #61 does not say.

THE CROSS DIRECTION is left exactly as built. #61 records Joe 0818 *"x crosses over if dr==-1, and x
crosses under if dr==1"* as NOT YET CONFIRMED; `xcond` already implements that and it is not touched
here.

RANKED ON MFE/MAE, as asked. It IS comparable inside this sweep because `mae_stop_pct` is fixed at
2.5 on every arm - the ratio is only incomparable when the stop itself moves, because a stopped leg
scores the knob value.

Held at the 1.06 build's other settings: `reent_xwob` 18, everything else banked.
"""
import os, sys, json, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

ROLE = os.environ['X_ROLE']; TFS = os.environ['X_TFS']; FENCE = os.environ['X_FENCE'] == '1'
SC, PX = C.SC, C.PX
N = len(SC.ts); FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
C.MAE_STOP = 2.5
_idx = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_idx + 1) - np.maximum.accumulate(np.where(m, 0, _idx + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])

TGT = C.R if ROLE == 'r' else ({t: np.asarray(SC.LD(t * 60, ROLE), float)[:N]
                                for t in range(1, 26)} if ROLE in ('m', 'Mage', 'b') else None)
EXF_HI, EXF_LO = C.EXF_HI, C.EXF_LO
OFF = {'both': (1, 2), 'next': (1,), 'self': (0,)}[TFS]

def infence(t, k, d):
    v = float(TGT[t][k])
    return (v < EXF_HI) if d > 0 else (v > EXF_LO)

def xcond_line(h, k, d):
    ts = [h + o for o in OFF]
    if any(t not in TGT for t in ts): return False
    xv = float(C.X[h][k])
    if not all((xv < float(TGT[t][k])) if d > 0 else (xv > float(TGT[t][k])) for t in ts):
        return False
    return all(infence(t, k, d) for t in ts) if FENCE else True

def xcond_fence(h, k, d):
    xv = float(C.X[h][k])
    return (xv < EXF_LO) if d > 0 else (xv > EXF_HI)

C.xcond = xcond_fence if ROLE == 'fence' else xcond_line

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

legs = []; k, d = 1, +1; g = 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    legs.append(dict(day=DAYOF(k), why=why, open=k, exit=xk, dd=d,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

per = collections.defaultdict(lambda: [0.0, 0, 0, 0.0, 0.0]); whys = collections.Counter()
for r in legs:
    a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['dd'])
    e = per[r['day']]
    e[0] += r['real']; e[1] += 1; e[2] += 1 if r['why'] == 'mae breach' else 0
    e[3] += a_; e[4] += f_
    whys[r['why']] += 1
print(json.dumps(dict(role=ROLE, tfs=TFS, fence=int(FENCE), legs=len(legs), whys=dict(whys),
                      per={k_: [round(v[0], 4), v[1], v[2], round(v[3], 4), round(v[4], 4)]
                           for k_, v in sorted(per.items())})), flush=True)
