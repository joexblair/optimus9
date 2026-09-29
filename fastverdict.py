"""A vectorised `sideways` detector, and the proof it matches Joe's momo_g_why bit for bit.

WHY. build_wsf_dtf_v3 calls momo_g_why once per (bar, TF) - about 5.6M calls per config over the
warm-up-to-window span at 23 timeframes. A granular sweep of momo_span_min x momo_slope_min at that
cost is hours per grid point. This computes the same verdict with numpy over whole arrays.

IT IS NOT A SECOND IMPLEMENTATION UNTIL IT IS PROVEN IDENTICAL. verify() replays Joe's own path and
compares every bar. If the mismatch count is anything but zero, nothing here may be used.

THE VERDICT PATH, read from momo_core.momo_fit + momo_core.verdict:
    idx      21 points ending at w, stride MOMO_STEP_BARS (6 bars at span 10)
    sl, r2   straight-line fit over those points, x = 0..20
    trk      clip(r2 * min(1, |sl| / MOMO_SLACK_REF), 0, 1)
    slack    LEVEL_SLACK * trk
    level    r[w] >= 50 - slack   (dr +1)   |   r[w] <= 50 + slack   (dr -1)
    flat     |sl| < MOMO_SLOPE_MIN
    quad     deg-2 fit over the last MOMO_WINDOW_MIN*12 bars, x = linspace(0,1,nb)
    vtx arc  -qb/(2qa), |qa|*0.25
  sideways = ok AND flat AND level AND NOT(quad fitted AND CURL_VTX_LO < vtx < CURL_VTX_HI
                                           AND arc >= CURL_ARC_MIN)
"""
import numpy as np


def lattice_fit(r, samples, step):
    """Straight-line fit over `samples` points ending at each bar, stride `step`. -> (slope, r2, ok)."""
    r = np.asarray(r, float); n = len(r)
    span = (samples - 1) * step
    Y = np.full((samples, n), np.nan)
    for j in range(samples):                       # point j sits (samples-1-j)*step bars back
        back = (samples - 1 - j) * step
        Y[j, back:] = r[:n - back] if back else r
    ok = np.isfinite(Y).all(axis=0)
    ok[:span] = False
    x = np.arange(samples, dtype=float)
    xm = x.mean(); xc = x - xm; sxx = (xc ** 2).sum()
    Y = np.where(np.isfinite(Y), Y, 0.0)            # ok already excludes these bars
    ym = Y.mean(axis=0)
    sl = (xc[:, None] * (Y - ym)).sum(axis=0) / sxx
    pred = sl * xc[:, None] + ym
    res = ((Y - pred) ** 2).sum(axis=0)
    tot = ((Y - ym) ** 2).sum(axis=0)
    r2 = np.where(tot > 1e-12, 1.0 - res / np.where(tot > 1e-12, tot, 1.0), 0.0)
    return np.nan_to_num(sl), np.nan_to_num(r2), ok


def rolling_quad(r, nb):
    """deg-2 fit over the last `nb` bars at each bar, x = linspace(0,1,nb). -> (qa, qb, ok).

    The design matrix is identical at every bar, so each normal-equation term is a fixed-weight
    rolling sum - one convolution each.
    """
    r = np.asarray(r, float); n = len(r)
    x = np.linspace(0.0, 1.0, nb)
    V = np.vstack([x ** 2, x, np.ones(nb)])        # 3 x nb
    G = V @ V.T                                     # 3 x 3, constant
    Gi = np.linalg.inv(G)
    fin = np.isfinite(r)
    y = np.where(fin, r, 0.0)
    rhs = np.empty((3, n))
    for i in range(3):
        w = V[i][::-1]                              # np.convolve(y,w)[b] == sum_t y[b-nb+1+t]*V[i][t]
        rhs[i] = np.convolve(y, w, mode='full')[:n]
    co = Gi @ rhs                                   # qa, qb, qc per bar
    good = np.convolve((~fin).astype(float), np.ones(nb), mode='full')[:n] == 0
    good[:nb - 1] = False
    return co[0], co[1], good


def sideways_mask(r, dr, samples, step, nb, slope_min, slack_ref, level_slack,
                  curl_vtx_lo, curl_vtx_hi, curl_arc_min):
    """Per-bar `sideways` for one line against a per-bar dr array. -> bool array."""
    r = np.asarray(r, float); dr = np.asarray(dr, np.int8)
    sl, r2, ok = lattice_fit(r, samples, step)
    trk = np.clip(r2 * np.minimum(1.0, np.abs(sl) / max(1e-9, slack_ref)), 0.0, 1.0)
    slack = level_slack * trk
    rw = r
    level = np.where(dr > 0, rw >= 50.0 - slack, rw <= 50.0 + slack)
    flat = np.abs(sl) < slope_min
    qa, qb, qok = rolling_quad(r, nb)
    with np.errstate(divide='ignore', invalid='ignore'):
        vtx = np.where(np.abs(qa) > 1e-12, -qb / (2.0 * qa), np.nan)
    arc = np.abs(qa) * 0.25
    curl = qok & (np.abs(qa) > 1e-12) & (vtx > curl_vtx_lo) & (vtx < curl_vtx_hi) & (arc >= curl_arc_min)
    return ok & (dr != 0) & flat & level & ~curl
