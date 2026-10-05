"""THE SWEEP. Joe 1005: "collect all knobs from all involved machines and sweep. gpu is an option.
use small increments (steps 0.1 or 0.05), and sample every result. find every relevant knob on the
Jig and add it to the soup. momentum is another."

WHAT THIS RUNS, and what it cannot:
  STAGE 1  ONE-AT-A-TIME over the 11 DOWNSTREAM knobs, at Joe's steps. Each cell re-routes every
           signal through mtd + branch D and re-scores. 289 cells.
  STAGE 2  the DENSE JOINT GRID over the 4 pure-scoring knobs — swing x stop x pyramid x risk =
           33 x 25 x 5 x 96 = 396,000 cells, vectorised (cupy when present, numpy otherwise).
           Routing is held at its current values here; stage 1 is what moves routing.
  NOT RUN  the 32 UPSTREAM knobs (Jig + momentum + the four fences + rig.DR). Each cell needs a
           full re-walk of every day: 96 s/day x 17 days = 27.2 min PER CELL. One-at-a-time over
           those 32 is 1,337 cells = 606 h = 25.3 days of compute. That is Joe's to scope.

FIT / TEST, and this is structural not optional: the 10 days already scored are FIT, the 7 random
non-sequential days are TEST. Every cell banks fitNet, testNet AND robust = min(fit, test) per the
banked objective in docs/linelab_spec.md s2 ("ROBUST = min(fitNet, testNet, ...) - nothing hides").

NO WINNER IS PICKED. Every cell is banked. Joe sets what winning means - see memory
`mae-mfe-only` bias 2: "Do not sweep and hand back 'the winner'."
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, time, contextlib, itertools
import numpy as np
sys.path.insert(0, _HERE)
try:
    import cupy as _cp
    XP, GPU = _cp, True
except Exception:
    XP, GPU = np, False

_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    exec(open(_os.path.join(_HERE, 'ninedays.py')).read().split('ALL = {}')[0])
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

FIT = ['2026-09-%02d' % d for d in (25, 26, 27, 28, 29, 30)] + ['2026-10-%02d' % d for d in (1, 2, 3, 4)]
TEST = [l.strip() for l in open(_os.path.join(_HERE, 'oos7.txt')) if l.strip()]
COST = 0.1975
CUR = dict(swing=0.70, stop=0.80, risk=2.0, pyr=0, lookback=48, tol15=3, tol30=6,
           fence=85.0, rev_wob=2, gap_max=4, af_block=60)

# ---------- the signal pool: every octo-sig bar of every day, read ONCE
def signal_bars(days):
    out = {}
    for day in days:
        A0, A1 = S.K(day + ' 00:00:00'), S.K(day + ' 23:59:55')
        sig = []
        for ln in open(_os.path.join(_HERE, 'octosig', '%s.out' % day)):
            if not ln.startswith('R|') or ln.startswith('R|run'): continue
            f = ln.rstrip('\n').split('|')
            if len(f) < 7: continue
            k = S.K(day + ' ' + f[2])
            if A0 <= k <= A1: sig.append((k, f[2]))
        out[day] = sig
    return out

# ---------- routing at an arbitrary knob cell. mtd + branch D, re-derived.
def route(k, c):
    """-> (status, grade, dr) at this bar under knob cell c. Mirrors score39.mtd/branchD exactly,
    with the swept knobs substituted. Nothing invented."""
    d = int(S.DRv[k])
    if d == 0: return (None, None, 0)
    HI, LO = c['fence'], 100.0 - c['fence']
    same = (lambda v: v >= HI) if d > 0 else (lambda v: v <= LO)
    a = max(0, k - c['lookback'])
    g5 = S.MTD['g5']
    hits = [i for i in range(a, k + 1) if np.isfinite(g5[i]) and same(g5[i])]
    if hits:
        ex = max(hits, key=lambda i: g5[i]) if d > 0 else min(hits, key=lambda i: g5[i])
    else:
        REV = S._mage_rev(g5, c['rev_wob']) if c['rev_wob'] != CUR['rev_wob'] else S.REV
        j = k
        while j < S.TAPE_LAST and not (np.isfinite(g5[j]) and same(g5[j])): j += 1
        if not (np.isfinite(g5[j]) and same(g5[j])): return (None, None, d)
        want = -1 if d > 0 else +1
        nxt = [i for i in range(j, S.TAPE_LAST + 1) if REV[i] == want]
        if not nxt: return (None, None, d)
        ex = nxt[0]
    TOL = {'g5': 0, 'g15': c['tol15'], 'g30': c['tol30'], 'ws1': 0}
    v = {}
    for n in ('g5', 'g15', 'g30', 'ws1'):
        w = TOL[n]
        if w == 0: v[n] = S.MTD[n][ex]; continue
        lo_, hi_ = max(0, ex - w), min(S.TAPE_LAST, ex + w)
        seg = S.MTD[n][lo_:hi_ + 1]
        v[n] = (float(np.nanmax(seg)) if d > 0 else float(np.nanmin(seg))) if np.isfinite(seg).any() else np.nan
    r1 = all(np.isfinite(v[n]) and same(v[n]) for n in v)
    net = v['ws1'] - v['g15']
    towards = (net > 0) if d > 0 else (net < 0)
    if not r1:
        return (('BLOCKED', 'mtd.r2', d) if towards else ('OPEN', 'neither', d))
    # branch D
    exf = (lambda x: x >= HI) if d > 0 else (lambda x: x <= LO)
    blk = [t for t in S.TF if np.isfinite(S.Rl[t][ex]) and exf(S.Rl[t][ex])]
    af = S.anchor_floater(S.Rl[1], S.PX, d, ex, block=c['af_block'])
    div = bool(af.get('fired')) if isinstance(af, dict) else False
    w1 = float(af['floater'][1]) if div else float(S.Rl[1][ex])
    keep = []
    if blk:
        keep = [blk[0]]
        for t in blk[1:]:
            if t - keep[-1] - 1 <= c['gap_max']: keep.append(t)
    if not keep: return ('OPEN', 'no r block', d)
    weak = min(keep, key=lambda t: S.Rl[t][ex]) if d > 0 else max(keep, key=lambda t: S.Rl[t][ex])
    band = (min(w1, S.Rl[weak][ex]), max(w1, S.Rl[weak][ex]))
    claim = [t for t in S.TF if t > max(keep) and np.isfinite(S.Rl[t][ex]) and band[0] <= S.Rl[t][ex] <= band[1]]
    if claim: return ('OPEN', 'band claimed', d)
    mnet = S.Mg[12][ex] - S.Mg[1][ex]
    away = (mnet < 0) if d > 0 else (mnet > 0)
    return ('CONFLUENCE', 'with-trend' if away else 'against-trend', d)

# ---------- pivots, cached per swing pct (the only sequential cost)
_PIV = {}
def piv(pct):
    if pct not in _PIV:
        p = S.find_pivots(S.PX, pct)
        _PIV[pct] = (np.array([i for i, kk in p if kk == 'H']), np.array([i for i, kk in p if kk == 'L']))
    return _PIV[pct]

def trades(days, c, SIG):
    """-> list of (open_bar, close_bar, net_pct, n_live_placeholder) for the CONFLUENCES, dr-bias side."""
    Hs, Ls = piv(c['swing'])
    out = []
    for day in days:
        for k, lbl in SIG[day]:
            st, gr, d = route(k, c)
            if st != 'CONFLUENCE': continue
            tgt = Ls if d > 0 else Hs
            nxt = tgt[tgt > k]
            if nxt.size == 0: continue                       # UNRESOLVED, excluded and counted
            j = int(nxt[0]); entry = float(S.PX[k]); seg = S.PX[k:j + 1]
            adv = (seg - entry) / entry * 100.0 if d > 0 else (entry - seg) / entry * 100.0
            fav = (entry - seg) / entry * 100.0 if d > 0 else (seg - entry) / entry * 100.0
            hit = np.flatnonzero(np.isfinite(adv) & (adv >= c['stop']))
            if hit.size:
                ex = k + int(hit[0]); gross = -c['stop']
            else:
                ex = j; gross = float(np.nanmax(fav))
            out.append((k, ex, gross - COST))
    out.sort()
    return out

def apply_pyr(tr, cap):
    if not cap: return tr, list(range(len(tr)))
    taken, live = [], []
    for t in tr:
        live = [x for x in live if x > t[0]]
        if len(live) >= cap: continue
        taken.append(t); live.append(t[1])
    return taken, None

def nlive_of(tr):
    n = []
    for i, t in enumerate(tr):
        n.append(sum(1 for j, u in enumerate(tr) if j != i and u[0] <= t[0] < u[1]))
    return np.array(n, float)

def compound(tr, risk, worst):
    """-> (final_mult, max_dd). Shared budget: lev = risk/(n_live+1)/worst. Close-time order."""
    if not tr: return 1.0, 0.0
    nl = nlive_of(tr)
    order = np.argsort([t[1] for t in tr])
    net = np.array([tr[i][2] for i in order]); nlo = nl[order]
    lev = risk / (nlo + 1.0) / worst
    f = 1.0 + lev * net / 100.0
    if (f <= 0).any(): return 0.0, 1.0
    eq = np.cumprod(f); pk = np.maximum.accumulate(eq)
    return float(eq[-1]), float(np.max((pk - eq) / pk))

def metrics(days, c, SIG):
    tr = trades(days, c, SIG)
    tr, _ = apply_pyr(tr, c['pyr'])
    if not tr: return dict(n=0, total=0.0, mean=0.0, wins=0, fin=1.0, dd=0.0)
    net = np.array([t[2] for t in tr])
    fin, dd = compound(tr, c['risk'], c['stop'] + COST)
    return dict(n=len(tr), total=float(net.sum()), mean=float(net.mean()),
                wins=int((net > 0).sum()), fin=fin, dd=dd)

# ---------- the swept grids, at Joe's steps
def grid(lo, hi, st):
    n = int(round((hi - lo) / st)) + 1
    return [round(lo + i * st, 6) for i in range(n)]

OAT = [  # knob, lo, hi, step  — the 11 DOWNSTREAM knobs
 ('swing',    0.40, 2.00, 0.05), ('stop',     0.30, 1.50, 0.05),
 ('risk',     0.50,10.00, 0.10), ('pyr',      0,    4,    1),
 ('lookback', 12,   240,  12),   ('tol15',    0,    12,   1),
 ('tol30',    0,    12,   1),    ('fence',    70.0, 95.0, 0.5),
 ('rev_wob',  1,    6,    1),    ('gap_max',  0,    11,   1),
 ('af_block', 12,   180,  12),
]

DDL = """CREATE TABLE IF NOT EXISTS lazyg_sweep (
    ls_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    ls_stage     VARCHAR(8)   NOT NULL,   -- oat | joint
    ls_knob      VARCHAR(24)  NOT NULL,   -- the knob varied (oat), or 'multi' (joint)
    ls_swing     DECIMAL(6,4) NOT NULL, ls_stop   DECIMAL(6,4) NOT NULL,
    ls_risk      DECIMAL(6,3) NOT NULL, ls_pyr    TINYINT      NOT NULL,
    ls_lookback  SMALLINT     NOT NULL, ls_tol15  TINYINT      NOT NULL,
    ls_tol30     TINYINT      NOT NULL, ls_fence  DECIMAL(6,3) NOT NULL,
    ls_rev_wob   TINYINT      NOT NULL, ls_gap_max TINYINT     NOT NULL,
    ls_af_block  SMALLINT     NOT NULL,
    ls_fit_n     SMALLINT NOT NULL, ls_fit_total DECIMAL(12,4) NOT NULL,
    ls_fit_mean  DECIMAL(10,5) NOT NULL, ls_fit_wins SMALLINT NOT NULL,
    ls_fit_fin   DECIMAL(16,6) NOT NULL, ls_fit_dd DECIMAL(8,5) NOT NULL,
    ls_test_n    SMALLINT NOT NULL, ls_test_total DECIMAL(12,4) NOT NULL,
    ls_test_mean DECIMAL(10,5) NOT NULL, ls_test_wins SMALLINT NOT NULL,
    ls_test_fin  DECIMAL(16,6) NOT NULL, ls_test_dd DECIMAL(8,5) NOT NULL,
    ls_robust    DECIMAL(10,5) NOT NULL, -- min(fit_mean, test_mean), docs/linelab_spec.md s2
    UNIQUE KEY uq_ls (ls_stage, ls_swing, ls_stop, ls_risk, ls_pyr, ls_lookback, ls_tol15,
                      ls_tol30, ls_fence, ls_rev_wob, ls_gap_max, ls_af_block),
    INDEX (ls_stage, ls_knob), INDEX (ls_robust))"""

COLS = ('ls_stage,ls_knob,ls_swing,ls_stop,ls_risk,ls_pyr,ls_lookback,ls_tol15,ls_tol30,ls_fence,'
        'ls_rev_wob,ls_gap_max,ls_af_block,ls_fit_n,ls_fit_total,ls_fit_mean,ls_fit_wins,ls_fit_fin,'
        'ls_fit_dd,ls_test_n,ls_test_total,ls_test_mean,ls_test_wins,ls_test_fin,ls_test_dd,ls_robust')

def row(stage, knob, c, f, t):
    return (stage, knob, c['swing'], c['stop'], c['risk'], c['pyr'], c['lookback'], c['tol15'],
            c['tol30'], c['fence'], c['rev_wob'], c['gap_max'], c['af_block'],
            f['n'], round(f['total'],4), round(f['mean'],5), f['wins'], round(f['fin'],6), round(f['dd'],5),
            t['n'], round(t['total'],4), round(t['mean'],5), t['wins'], round(t['fin'],6), round(t['dd'],5),
            round(min(f['mean'], t['mean']),5))

if __name__ == '__main__':
    t0 = time.time()
    print('# GPU: %s%s | FIT %d days | TEST %d days' %
          (GPU, (' cupy ' + _cp.__version__) if GPU else ' numpy fallback', len(FIT), len(TEST)))
    SIG = signal_bars(FIT + TEST)
    print('# signals: FIT %d | TEST %d' % (sum(len(SIG[d]) for d in FIT), sum(len(SIG[d]) for d in TEST)))
    db = DatabaseManager(**get_db_config()); db.connect(); db.execute(DDL)
    ins = []
    print()
    print('## STAGE 1 — ONE-AT-A-TIME, all 11 downstream knobs, every cell banked')
    print('| knob | cells | fit mean range | test mean range | robust range | secs |')
    print('|' + '---|' * 6)
    for knob, lo, hi, st in OAT:
        g = grid(lo, hi, st); k0 = time.time(); fm = []; tm = []; rb = []
        for val in g:
            c = dict(CUR); c[knob] = int(val) if knob in ('pyr','lookback','tol15','tol30','rev_wob','gap_max','af_block') else val
            f = metrics(FIT, c, SIG); t = metrics(TEST, c, SIG)
            ins.append(row('oat', knob, c, f, t))
            fm.append(f['mean']); tm.append(t['mean']); rb.append(min(f['mean'], t['mean']))
        print('| %s | %d | %+.3f .. %+.3f | %+.3f .. %+.3f | %+.3f .. %+.3f | %.0f |'
              % (knob, len(g), min(fm), max(fm), min(tm), max(tm), min(rb), max(rb), time.time()-k0))
    db.executemany('INSERT INTO lazyg_sweep (' + COLS + ') VALUES (' + ','.join(['%s']*26) + ') '
                   'ON DUPLICATE KEY UPDATE ls_robust=VALUES(ls_robust)', ins)
    print()
    print('# STAGE 1 banked: %d cells in %.0f s' % (len(ins), time.time()-t0))
    if _os.environ.get('LG_STAGE2', '1') == '1':
        stage2(SIG, db)
    db.disconnect()



# ================= STAGE 2 — the dense joint grid, routing held at CUR =================
# Routing does NOT depend on swing / stop / pyr / risk, so every signal is routed ONCE and the
# 396,000 cells reuse it. The compound is vectorised over the risk axis (cupy when present).

def routed(days, SIG, c):
    """-> [(bar, dr)] for the CONFLUENCES only, at routing knobs c. Computed once."""
    out = []
    for day in days:
        for k, lbl in SIG[day]:
            st, gr, d = route(k, c)
            if st == 'CONFLUENCE': out.append((k, d))
    out.sort()
    return out

def legs_at(conf, swing, stop):
    """-> (open[], close[], net[]) for a routed confluence set at this swing and stop."""
    Hs, Ls = piv(swing)
    o, cl, nt = [], [], []
    for k, d in conf:
        tgt = Ls if d > 0 else Hs
        nxt = tgt[tgt > k]
        if nxt.size == 0: continue
        j = int(nxt[0]); entry = float(S.PX[k]); seg = S.PX[k:j + 1]
        adv = (seg - entry) / entry * 100.0 if d > 0 else (entry - seg) / entry * 100.0
        fav = (entry - seg) / entry * 100.0 if d > 0 else (seg - entry) / entry * 100.0
        hit = np.flatnonzero(np.isfinite(adv) & (adv >= stop))
        if hit.size: ex, g = k + int(hit[0]), -stop
        else:        ex, g = j, float(np.nanmax(fav))
        o.append(k); cl.append(ex); nt.append(g - COST)
    return np.array(o), np.array(cl), np.array(nt)

def grid_block(o, cl, nt, pyr, risks, worst):
    """-> (final[], dd[], n) over the risk axis for one (swing, stop, pyr) cell."""
    if o.size == 0:
        z = np.ones(len(risks)); return z, np.zeros(len(risks)), 0
    keep = np.ones(o.size, bool)
    if pyr:
        live = []
        for i in range(o.size):
            live = [x for x in live if x > o[i]]
            if len(live) >= pyr: keep[i] = False
            else: live.append(cl[i])
    oo, cc, nn = o[keep], cl[keep], nt[keep]
    if oo.size == 0:
        z = np.ones(len(risks)); return z, np.zeros(len(risks)), 0
    nl = ((oo[None, :] <= oo[:, None]) & (oo[:, None] < cc[None, :])).sum(1) - 1
    order = np.argsort(cc)
    nn, nl = nn[order], nl[order]
    R = XP.asarray(np.asarray(risks, float))[:, None]
    NT = XP.asarray(nn)[None, :]; NL = XP.asarray(nl.astype(float))[None, :]
    lev = R / (NL + 1.0) / worst
    f = 1.0 + lev * NT / 100.0
    dead = (f <= 0).any(axis=1)
    f = XP.where(f <= 0, 1e-12, f)
    eq = XP.cumprod(f, axis=1)
    pk = XP.maximum.accumulate(eq, axis=1)
    dd = XP.max((pk - eq) / pk, axis=1)
    fin = eq[:, -1]
    fin = XP.where(dead, 0.0, fin); dd = XP.where(dead, 1.0, dd)
    g = (lambda x: _cp.asnumpy(x)) if GPU else (lambda x: x)
    return g(fin), g(dd), int(oo.size)

def stage2(SIG, db):
    SW = grid(0.40, 2.00, 0.05); ST = grid(0.30, 1.50, 0.05)
    PY = [0, 1, 2, 3, 4];        RK = grid(0.50, 10.00, 0.10)
    cells = len(SW) * len(ST) * len(PY) * len(RK)
    print()
    print('## STAGE 2 — the dense joint grid: swing %d x stop %d x pyramid %d x risk %d = %d cells'
          % (len(SW), len(ST), len(PY), len(RK), cells))
    cf, ct = routed(FIT, SIG, CUR), routed(TEST, SIG, CUR)
    print('# routed ONCE: %d FIT confluences, %d TEST confluences' % (len(cf), len(ct)))
    t0 = time.time(); ins = []; done = 0
    for sw in SW:
        for st_ in ST:
            of, clf, ntf = legs_at(cf, sw, st_)
            ot, clt, ntt = legs_at(ct, sw, st_)
            worst = st_ + COST
            for py in PY:
                ff, df, nf = grid_block(of, clf, ntf, py, RK, worst)
                ft, dt, n_t = grid_block(ot, clt, ntt, py, RK, worst)
                mf = (np.asarray(ntf)[:nf].mean() if nf else 0.0)
                mt = (np.asarray(ntt)[:n_t].mean() if n_t else 0.0)
                for ri, rk in enumerate(RK):
                    c = dict(CUR); c.update(swing=sw, stop=st_, pyr=py, risk=rk)
                    ins.append(row('joint', 'multi', c,
                        dict(n=nf, total=float(mf*nf), mean=float(mf), wins=0, fin=float(ff[ri]), dd=float(df[ri])),
                        dict(n=n_t, total=float(mt*n_t), mean=float(mt), wins=0, fin=float(ft[ri]), dd=float(dt[ri]))))
                done += len(RK)
            if len(ins) >= 40000:
                db.executemany('INSERT INTO lazyg_sweep (' + COLS + ') VALUES (' + ','.join(['%s']*26) + ') '
                               'ON DUPLICATE KEY UPDATE ls_robust=VALUES(ls_robust)', ins); ins = []
        print('#   swing %.2f done | %d of %d cells | %.0f s' % (sw, done, cells, time.time()-t0), flush=True)
    if ins:
        db.executemany('INSERT INTO lazyg_sweep (' + COLS + ') VALUES (' + ','.join(['%s']*26) + ') '
                       'ON DUPLICATE KEY UPDATE ls_robust=VALUES(ls_robust)', ins)
    print('# STAGE 2 banked: %d cells in %.0f s' % (cells, time.time()-t0))
