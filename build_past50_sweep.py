"""build_past50_sweep — ALL-DIALS step=1 branch-descent sweep of the past-50 mechanic (Joe 0726). SAVED.
Every dial swept step=1 (no number left behind), one dial at a time from a centre, adopt-on-improve — the RPL-sweep
method (NOT sampling, NOT full-factorial). Deduped, 21 random days, swing 2%. Two reports: A-trigger x×Mage vs m×Mage.

DIALS (all step=1):
  wob         4..12     (cross debounce)
  oob_hi      82..90    (OOB level; LO = 100-hi — s4M/hs60x qualify + Branch-B x-gate)
  develop     46..54    (the r-vs-N fork; A if r>develop else B)
  dwell_seams 1..4      (× 240s TF-seam = sustained-OOB floor)
Objective = median(MFE-MAE) over deduped trades across the 21 days, trade-floor >= MINTR (else rejected).
Vectorised qualify + searchsorted trigger + memoised scoring so the full step=1 descent finishes.
Usage: build_past50_sweep.py [seed] [ndays]   (default seed 21, 21 days)
"""
import sys
import numpy as np
import datetime as dt
import build_past50 as P

te = P.te; L = P.L; s4M = P.s4M; hs = P.hs; cache = P.cache; lab = P.lab; HTFS = P.HTFS
n = len(te); _tef = te.astype(float)
DAY = 86400 * 1000
MINTR = 15
SEED = int(sys.argv[1]) if len(sys.argv) > 1 else 21
KDAYS = int(sys.argv[2]) if len(sys.argv) > 2 else 21
WOBS = list(range(4, 13)); OOBS = list(range(82, 91)); DEVS = list(range(46, 55)); SEAMS = [1, 2, 3, 4]
CENTER = dict(wob=6, oob=85, dev=50, seam=1)
_scache = {}


def random_days(seed, k):
    lo, hi = int(te[0]), int(te[-1]) - DAY
    nd = int((hi - lo) / DAY)
    offs = np.random.default_rng(seed).choice(np.arange(nd), min(k, nd), replace=False)
    return [(int(lo + o * DAY), int(lo + o * DAY + DAY)) for o in sorted(offs)]


def _sustained(line, side, hi, lo, secs):
    oob = (line >= hi) if side > 0 else (line <= lo)
    starts = oob & ~np.roll(oob, 1); starts[0] = oob[0]
    rs = np.maximum.accumulate(np.where(starts, _tef, -np.inf))
    return oob & ((_tef - rs) >= secs * 1000)


def qualify(oob, seam):
    hi, lo = oob, 100 - oob; secs = seam * 240
    out = []
    for de in (+1, -1):
        q = _sustained(s4M, de, hi, lo, secs) & ((hs >= hi) if de > 0 else (hs <= lo))
        out += [(int(i), de) for i in np.flatnonzero(q & ~np.roll(q, 1))]
    return sorted(out)


def _wc(a, b, d, wob):
    wc = cache.causal.cross_wob(a - b, 0.0, d, wob); return wc & ~np.roll(wc, 1)


def fires(wob, dev, oob, a_variant):
    hi, lo = oob, 100 - oob; F = {}
    for tf in HTFS:
        x, m, Mg, r = L[tf]['x'], L[tf]['m'], L[tf]['M'], L[tf]['r']
        d_ = r > dev
        for d in (+1, -1):
            A = _wc(x, Mg, d, wob) if a_variant == 'x' else _wc(m, Mg, d, wob)
            B = _wc(x, m, d, wob) & ((x >= hi) | (x <= lo))
            F[(tf, d)] = np.flatnonzero((d_ & A) | (~d_ & B))
    return F


def deduped(onsets, F):
    tr = {}
    for i0, de in onsets:
        d = -de; endt = te[i0] + 5 * 3600 * 1000
        for tf in HTFS:
            idx = F[(tf, d)]; j = np.searchsorted(idx, i0)
            if j < len(idx) and te[idx[j]] < endt:
                ti = int(idx[j]); tr[(int(te[ti]), tf)] = d
    return tr


def score(cfg, days, a_variant):
    ons = [(i, de) for i, de in qualify(cfg['oob'], cfg['seam']) if any(S <= te[i] < E for S, E in days)]
    F = fires(cfg['wob'], cfg['dev'], cfg['oob'], a_variant)
    tr = deduped(ons, F)
    nets = {-1: [], 1: []}; mfes = []; maes = []
    for (ts, tf), d in tr.items():
        key = (ts, d)
        if key not in _scache:
            _, mf, ma = lab.score(ts, d); _scache[key] = (mf, ma)
        mf, ma = _scache[key]; nets[d].append(mf - ma); mfes.append(mf); maes.append(ma)
    alln = nets[-1] + nets[1]
    if len(alln) < MINTR:
        return dict(n=len(alln), net=-9.0, win=0, mfe=0, mae=0, ns=len(nets[-1]), nl=len(nets[1]))
    return dict(n=len(alln), net=float(np.median(alln)), win=100 * np.mean([x > 0 for x in alln]),
                mfe=float(np.median(mfes)), mae=float(np.median(maes)), ns=len(nets[-1]), nl=len(nets[1]))


def descend(days, a_variant):
    """step=1 branch-descent over all dials from CENTER, adopt-on-improve, iterate until stable."""
    cur = dict(CENTER); best = score(cur, days, a_variant)
    grids = {'wob': WOBS, 'oob': OOBS, 'dev': DEVS, 'seam': SEAMS}
    print('\n=== A-trigger %s×Mage | %d random days | dedup | swing 2%% | step=1 branch-descent ===' % (a_variant, len(days)))
    for sweep in range(1, 4):                              # up to 3 full passes over the dials
        moved = False
        for dial, grid in grids.items():
            trace = []
            for v in grid:                                # EVERY step=1 value of this dial
                if v == cur[dial]:
                    s = best; trace.append((v, s['net'], s['n'], True)); continue
                s = score({**cur, dial: v}, days, a_variant)
                trace.append((v, s['net'], s['n'], False))
                if s['net'] > best['net'] + 1e-9 and s['n'] >= MINTR:
                    best = s; cur[dial] = v; moved = True
            tr = ' '.join('%d:%+.2f%s' % (v, nt if nt > -8 else float('nan'), '*' if cur[dial] == v else '') for v, nt, nn, _ in trace)
            print('  pass%d %-5s -> %d | %s' % (sweep, dial, cur[dial], tr))
        if not moved:
            break
    print('  BEST %s: wob=%d oob=%d dev=%d seam=%d(=%ds) | net %+.3f win %.0f%% MFE %+.3f MAE %+.3f | %d tr (S%d/L%d)' % (
        a_variant, cur['wob'], cur['oob'], cur['dev'], cur['seam'], cur['seam'] * 240,
        best['net'], best['win'], best['mfe'], best['mae'], best['n'], best['ns'], best['nl']))
    return cur, best


if __name__ == '__main__':
    days = random_days(SEED, KDAYS)
    span = ', '.join(dt.datetime.utcfromtimestamp(S / 1000).strftime('%m-%d') for S, E in days)
    print('past-50 ALL-DIALS step=1 sweep | seed %d | %d random days: %s' % (SEED, len(days), span))
    print('dials: wob %s | oob %s | dev %s | seam %s (all step=1)' % (WOBS, OOBS, DEVS, SEAMS))
    cx, bx = descend(days, 'x')
    cm, bm = descend(days, 'm')
    print('\n=== VERDICT: x×Mage vs m×Mage (best config each) ===')
    print('  x×Mage: %s | net %+.3f win %.0f%% (%d tr)' % (cx, bx['net'], bx['win'], bx['n']))
    print('  m×Mage: %s | net %+.3f win %.0f%% (%d tr)' % (cm, bm['net'], bm['win'], bm['n']))
