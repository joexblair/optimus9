"""curl_pred3 — the real curl-pred: persistence + normalised arc + R2 floor, on s3r. Joe 0804.

Joe 0804: "build the real curl-pred with persistence, normalised arc and R2 floor on s3r, after it
has been delegated by s15r or s22r".

WHAT WAS WRONG BEFORE
  v1 (curl_pred.py)  fired on the FIRST bar of opposing curvature anywhere after momo activation.
                     7.0 s6 bars early. No persistence, no scale-free arc, no fit-quality gate.
  v2 (curl_pred2.py) ROC on s3r after an s15r handover. The HANDOVER did all the work (2.50 s6 bars);
                     ROC contributed −0.14 and its winning settings were the slowest/strictest with a
                     zero threshold, i.e. waiting for the turn rather than predicting it.

THE THREE FIXES
  1 PERSISTENCE   the condition must hold for WOB consecutive EVENT samples. Fires on the LAST bar
                  of the run, not the first — this is the wob idiom, matching cross_wob.
  2 NORMALISED    arc_n = |qa| * 0.25 / (max(y) - min(y)) over the window. momo()'s raw arc is in
    ARC           r-units per NORMALISED-window squared, so a 6-sample and a 48-sample window give
                  incomparable qa. Dividing by the window's own r-range makes one threshold mean the
                  same thing at every size. momo()'s own CURL_ARC_MIN = 4.0 is the un-normalised form.
  3 R2 FLOOR      on the QUADRATIC fit. momo() gates its LINEAR verdict on MOMO_R2_MIN = 0.50 but its
                  curl block has no equivalent, so a parabola describing nothing can still fire.

DELEGATION (Joe 0804: "after it has been delegated by s15r OR s22r" — v2 used s15r alone)
  handover = the first bar where EITHER s15r or s22r reaches the direction-matched level:
  dr -1 -> r <= HOFF | dr +1 -> r >= 100-HOFF. From that bar, s3r is watched on EVENT BARS ONLY.

VERTEX. The predictive test is vtx > 1.0 — the parabola's turning point is BEYOND the window end, so
the turn has not happened yet. VTX_MAX bounds how far beyond, separating "just ahead" from "far
ahead". momo()'s own curl test is 0.05 < vtx < 0.95, i.e. INSIDE — that fires at or after the turn.

Strictly causal: the window ending at event sample i reads samples i-NSAMP+1 .. i, all <= i.

    python3 curl_pred3.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

JD = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp'
S6 = 72.0                                  # 1 s6 bar = 6 min = 72 bars at the 5 s grid
HOFF = (15.0, 20.0, 25.0, 30.0)            # SWEEP: handover level on s15r OR s22r
NSAMP = (6, 12, 24, 48)                    # SWEEP: event samples in the quadratic window
ARCN = (0.02, 0.05, 0.10, 0.20)            # SWEEP: NORMALISED arc floor, dimensionless
R2MIN = (0.0, 0.5, 0.8)                    # SWEEP: quadratic R2 floor. momo's linear floor is 0.50
WOB = (1, 2, 3, 6)                         # SWEEP: consecutive event samples the condition holds
VTXMAX = (1.5, 3.0, 1e9)                   # SWEEP: upper bound on how far ahead the vertex sits
VAR = ('r3a', 'r3b')                       # SWEEP: R_SPEC[4] vs R_SPEC[15] at TF3


def fit_all(y, ns):
    """Vectorised quadratic over every causal window of ns samples. Returns qa, qb, r2, rng.
    The design matrix is constant, so all windows solve as one matmul."""
    if len(y) < ns:
        return None
    W = swv(y, ns)                                     # W[j] = y[j : j+ns], ENDS at j+ns-1
    x = np.linspace(0.0, 1.0, ns)
    X = np.vstack([x ** 2, x, np.ones(ns)]).T
    P = np.linalg.pinv(X)                              # 3 x ns
    C = W @ P.T                                        # (nwin, 3) -> qa, qb, qc
    pred = C @ X.T
    res = ((W - pred) ** 2).sum(1)
    tot = ((W - W.mean(1, keepdims=True)) ** 2).sum(1)
    r2 = np.where(tot > 1e-12, 1.0 - res / np.maximum(tot, 1e-12), 0.0)
    rng = W.max(1) - W.min(1)
    return C[:, 0], C[:, 1], r2, rng


def main():
    A = np.load(JD + '/lines_all.npz'); B = np.load(JD + '/r3.npz')
    ts_a = A['ts'].astype(np.int64)
    RA = {15: A['r15'].astype(float), 22: A['r22'].astype(float)}
    ts = B['ts'].astype(np.int64); evt = B['evt'].astype(bool)
    R3 = {v: B[v].astype(float) for v in VAR}

    db = DatabaseManager(**get_db_config()); db.connect()
    rows = db.execute('SELECT sw_n,sw_dr,sw_momo_activated_ms,sw_momo_r_ext_ms FROM s46_window '
                      'ORDER BY sw_n', fetch=True)
    db.disconnect()
    live = [r for r in rows if r['sw_momo_activated_ms'] and r['sw_momo_r_ext_ms']]

    def handover(r, h):
        """first bar where EITHER s15r or s22r reaches the direction-matched level (Joe 0804)."""
        dr = int(r['sw_dr'])
        a = int(np.searchsorted(ts_a, int(r['sw_momo_activated_ms'])))
        xe = int(np.searchsorted(ts_a, int(r['sw_momo_r_ext_ms'])))
        if xe <= a:
            return None
        best = None
        for tf in (15, 22):
            seg = RA[tf][a:xe + 1]
            hit = ((seg <= h) if dr < 0 else (seg >= 100.0 - h)) & np.isfinite(seg)
            w = np.flatnonzero(hit)
            if len(w):
                b_ = a + int(w[0])
                best = b_ if best is None else min(best, b_)
            del seg
        return int(ts_a[best]) if best is not None else None

    print('armed rows %d   (1 s6 bar = %d bars at the 5 s grid)' % (len(live), int(S6)))
    HO = {}
    for h in HOFF:
        HO[h] = [(r, handover(r, h)) for r in live]
        n = sum(1 for _, g in HO[h] if g is not None)
        print('  handover s15r OR s22r at %.0f : %2d of %d rows (%.0f%%)'
              % (h, n, len(live), 100.0 * n / len(live)))
    print()

    out = []
    for h in HOFF:
        pairs = [(r, g) for r, g in HO[h] if g is not None]
        if len(pairs) < 6:
            continue
        # NULL control: fire at the handover bar itself
        nl = [int((int(r['sw_momo_r_ext_ms']) - g) / 5000) for r, g in pairs]
        out.append(dict(tag='NULL handover', h=h, ns=0, arc=0, r2=0, wb=0, vx=0, var='-',
                        n=len(nl), cov=100.0 * len(nl) / len(live),
                        med=float(np.median(nl)), p25=float(np.percentile(nl, 25)),
                        p75=float(np.percentile(nl, 75)), late=0.0))
        for var in VAR:
            rr = R3[var]
            for ns in NSAMP:
                # precompute the fit ONCE per (row, ns), then reuse across arc/r2/wob/vtx
                pre = []
                for r, g in pairs:
                    dr = int(r['sw_dr']); xe_ms = int(r['sw_momo_r_ext_ms'])
                    i0 = int(np.searchsorted(ts, g)); i1 = int(np.searchsorted(ts, xe_ms))
                    if i1 <= i0 or i1 >= len(ts):
                        pre.append(None); continue
                    e = np.flatnonzero(evt[i0:i1 + 1]) + i0
                    y = rr[e]
                    if len(y) < ns or not np.isfinite(y).all():
                        pre.append(None); continue
                    f = fit_all(y, ns)
                    if f is None:
                        pre.append(None); continue
                    qa, qb, r2, rng = f
                    with np.errstate(divide='ignore', invalid='ignore'):
                        vtx = np.where(np.abs(qa) > 1e-12, -qb / (2 * qa), np.nan)
                        arcn = np.where(rng > 1e-9, np.abs(qa) * 0.25 / np.maximum(rng, 1e-9), np.nan)
                    opp = (qa > 0) if dr < 0 else (qa < 0)
                    pre.append((e, ns, opp, arcn, r2, vtx, xe_ms))
                for am in ARCN:
                    for rm in R2MIN:
                        for vx in VTXMAX:
                            for wb in WOB:
                                L = []
                                for p in pre:
                                    if p is None:
                                        continue
                                    e, ns_, opp, arcn, r2, vtx, xe_ms = p
                                    ok = opp & (arcn >= am) & (r2 >= rm) & (vtx > 1.0) & (vtx <= vx)
                                    ok = np.nan_to_num(ok, nan=False).astype(bool)
                                    if wb > 1:
                                        c = np.convolve(ok.astype(int), np.ones(wb, int), 'valid') == wb
                                        z = np.flatnonzero(c)
                                        k = (int(z[0]) + wb - 1) if len(z) else None
                                    else:
                                        z = np.flatnonzero(ok)
                                        k = int(z[0]) if len(z) else None
                                    if k is None:
                                        continue
                                    fb = int(e[k + ns_ - 1])       # window ENDS here: causal
                                    L.append(int((xe_ms - ts[fb]) / 5000))
                                if len(L) < 6:
                                    continue
                                a1 = np.array(L, float)
                                out.append(dict(tag='curl-pred', h=h, ns=ns, arc=am, r2=rm, wb=wb,
                                                vx=vx, var=var, n=len(L),
                                                cov=100.0 * len(L) / len(live),
                                                med=float(np.median(a1)),
                                                p25=float(np.percentile(a1, 25)),
                                                p75=float(np.percentile(a1, 75)),
                                                late=100.0 * float((a1 < 0).mean())))
    print('LEAD TO THE r EXTREME, in s6 bars (1 s6 = 72 x 5 s). POSITIVE = fired BEFORE it.')
    print('target: small positive, high coverage, low late%%.')
    print('  %-13s %5s %4s %5s %4s %4s %6s %4s %5s %6s %7s %7s %7s %6s'
          % ('what', 'hoff', 'nsmp', 'arc', 'r2', 'wob', 'vtx', 'var', 'n', 'cov%',
             'p25', 'MEDIAN', 'p75', 'late%'))
    nulls = [o for o in out if o['tag'] == 'NULL handover']
    for o in nulls:
        print('  %-13s %5.0f %4s %5s %4s %4s %6s %4s %5d %6.0f %7.2f %7.2f %7.2f %6.0f'
              % (o['tag'], o['h'], '-', '-', '-', '-', '-', '-', o['n'], o['cov'],
                 o['p25'] / S6, o['med'] / S6, o['p75'] / S6, o['late']))
    cp = [o for o in out if o['tag'] == 'curl-pred']
    for o in sorted(cp, key=lambda z: (z['late'] > 20, abs(z['med'] / S6 - 1.0)))[:20]:
        print('  %-13s %5.0f %4d %5.2f %4.1f %4d %6.1f %4s %5d %6.0f %7.2f %7.2f %7.2f %6.0f'
              % (o['tag'], o['h'], o['ns'], o['arc'], o['r2'], o['wb'],
                 (o['vx'] if o['vx'] < 1e8 else 99), o['var'], o['n'], o['cov'],
                 o['p25'] / S6, o['med'] / S6, o['p75'] / S6, o['late']))


if __name__ == '__main__':
    main()
