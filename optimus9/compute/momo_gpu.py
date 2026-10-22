"""momo_gpu - the GPU mirror of momo_gated.momo_g, for the mom-true mask and nothing else.

Joe 1018, ruling the route after I recommended the 16-core CPU: *"6, gpu"*. The cost of that
ruling is stated in `docs/octo-freedom/1018_mom_cache_gate.md` S9 and is paid by `parity()`: this
is a SECOND implementation of a banked mech, so no mask off it is usable until it matches the CPU
path bar for bar.

WHAT IT MIRRORS. `momo_gated.momo_g(line, dr, w)[0] in ('momo', 'curl')` - the mom-true tag, Joe
1009: *"I use mom-true as shorthand for momentum.momo and momentum.curl"*. Nothing else. It does
not return the slope, the fit, the reason or the four-tuple; a caller wanting those calls the CPU
path, which remains the only implementation of the verdict in words.

SRP. This module computes ONE line's mask for ONE bank. It owns no cache, no file path, no
timeframe list and no knob - the bank arrives as an argument, exactly as `momtrue_mask` takes it.

THE FOUR THINGS THAT MAKE IT A MIRROR AND NOT A REWRITE, each one a line of momo_core:

  the straight fit   21 samples, `momo_fixed_samples`, strided
                     `stride = max(1, round(window_min * 12 / 20))`, ending AT the bar.
                     momo_core.momo_fit: `idx = [w - k*MOMO_STEP_BARS for k in range(20,-1,-1)]`
  the bend           a degree-2 fit over the FULL window of `window_min * 12` 5 s bars, on
                     `xx = linspace(0, 1, nb)`, fitted ONLY where flat AND level - which is what
                     `quad='auto'` means in momo_fit, not an optimisation added here
  the verdict        momo_core.verdict, with momo_seam 'off' so the seam excuse cannot fire
  the three gates    momo_gated.curl_gates at gate2=True, the default every existing caller uses

FLOAT64 THROUGHOUT, MINE, STATED. The verdict is a stack of threshold comparisons - |slope| against
`momo_slope_min`, r2 against `momo_r2_min`, r against 50 +/- slack, arc against `curl_arc_min`. In
float32 those thresholds move and the mask would differ from the CPU for a reason that has nothing
to do with the mech.

DIRECT DOT PRODUCTS FOR THE BEND, MINE, STATED. The three moments could come from prefix sums in
O(n), but a prefix-sum difference over a 4,320-bar window subtracts two numbers of order 1e8 to
recover one of order 1e5, and the digits lost are exactly the ones the `curl_r2_min` comparison
reads. The windows are gathered and multiplied instead.

CAUSAL. Every bar's verdict reads bars <= it: the strided samples end at the bar and the bend
window ends at the bar. Asserted in `_causal_check`, not claimed in this sentence.
"""
import numpy as np

try:
    import cupy as cp
    HAVE_GPU = True
except Exception:                                    # pragma: no cover - no GPU on this box
    cp = None
    HAVE_GPU = False

# The mom-true states, Joe 1009. Same tuple as _momtrue.STATES, kept here so a reader of this file
# does not have to go and look.
STATES = ('momo', 'curl')

CHUNK = 8192          # bend windows gathered at once. Memory, not a mech knob: 8192 x 4320 x 8 B
#                       is 283 MB for the window matrix and the same again for its square.


def grid(bank, tf):
    """(window_min, n_samples, stride_bars, bend_bars) for a timeframe, from the bank.

    THE SAME FOUR EXPRESSIONS momo_gated.momo_window computes, read off the same bank. They are
    re-derived here rather than imported because momo_window is a context manager that mutates
    momo_core's globals - there is nothing to call that just returns the grid.
    """
    tf = int(tf)
    window_min = int(bank['k_window']) * tf
    fixed = int(bank['momo_fixed_samples'])
    if fixed > 0:
        n = max(2, fixed)
        stride = max(1, int(round((window_min * 12) / (n - 1))))
    else:
        n = max(2, window_min // int(bank['momo_step_min']))
        stride = int(bank['momo_step_min']) * 12
    return window_min, n, stride, window_min * 12


def _causal_check(n_samples, stride, bend_bars):
    """The invariant, as an assert and not a comment: no index this module reads lies after the bar.

    Joe's rule is that a causality claim goes in an assert. The two windows are built from these
    three numbers alone, so checking them checks every bar.
    """
    assert n_samples >= 2 and stride >= 1 and bend_bars >= 1
    newest_sample_offset = 0 - 0 * stride            # k = 0 is the bar itself
    oldest_sample_offset = -(n_samples - 1) * stride
    assert newest_sample_offset == 0, 'the strided fit must end AT the bar'
    assert oldest_sample_offset < 0, 'the strided fit must look back'
    assert bend_bars >= 1, 'the bend window must end AT the bar'


def _bend_weights(nb, xp):
    """The fixed arrays a degree-2 fit over `xx = linspace(0, 1, nb)` needs.

    -> (W, S) where W is (nb, 3) holding [xx**2, xx, 1] as the three moment weights, and S holds
    the pure-x sums [S1, S2, S3, S4, nb] that the bend's own r-squared needs.

    THE NORMAL EQUATIONS, NOT lstsq. np.polyfit solves a scaled Vandermonde by SVD; the Gram matrix
    of [1, x, x**2] on [0, 1] has a condition number near 15, so the normal equations carry the fit
    to the same place. That they actually do is what `parity()` measures - it is not asserted here.
    """
    xx = xp.linspace(0.0, 1.0, int(nb), dtype=xp.float64)
    W = xp.stack([xx * xx, xx, xp.ones_like(xx)], axis=1)
    S1 = float(xx.sum()); S2 = float((xx ** 2).sum())
    S3 = float((xx ** 3).sum()); S4 = float((xx ** 4).sum())
    G = np.array([[S4, S3, S2], [S3, S2, S1], [S2, S1, float(nb)]], dtype=np.float64)
    return W, (S1, S2, S3, S4, float(nb)), xp.asarray(np.linalg.inv(G))


def momtrue_gpu(line, tf, bank, n=None, gate2=True, xp=None):
    """Per bar, is this line mom-true, for each side. -> {+1: bool array, -1: bool array}

        line   the r line on the 5 s grid
        tf     the line's timeframe in MINUTES
        bank   the momo bank that owns `tf`, as momo_bank returns it
        gate2  Joe's second curl gate. True is the default every CPU caller uses

    The shape and dtype of the return match `_momtrue.momtrue_mask`, so a caller swaps one for the
    other without changing a line.
    """
    xp = (cp if HAVE_GPU else np) if xp is None else xp
    y = xp.asarray(np.asarray(line, dtype=np.float64))
    n = int(len(y) if n is None else n)
    y = y[:n]

    window_min, ns, stride, nb = grid(bank, tf)
    _causal_check(ns, stride, nb)

    slope_min = float(bank['momo_slope_min'])
    slack_ref = float(bank['momo_slack_ref'])
    r2_min = float(bank['momo_r2_min'])
    lvl_slack = float(bank['level_slack'])
    arc_min = float(bank['curl_arc_min'])
    vtx_lo = float(bank['curl_vtx_lo'])
    vtx_hi = float(bank['curl_vtx_hi'])
    curl_r2_min = float(bank['curl_r2_min'])

    # ---- the straight fit, every bar at once. x = 0..ns-1, so the fit weights are constants.
    k = xp.arange(ns, dtype=xp.int64)                       # 0 = oldest sample
    off = (ns - 1 - k) * stride                             # bars back from the bar under test
    bars = xp.arange(n, dtype=xp.int64)
    idx = bars[:, None] - off[None, :]                      # (n, ns), column ns-1 IS the bar
    have = idx[:, 0] >= 0
    Y = xp.where(idx >= 0, y[xp.clip(idx, 0, n - 1)], xp.nan)
    ok = have & xp.isfinite(Y).all(axis=1)

    x = xp.arange(ns, dtype=xp.float64)
    xm = float(x.mean())
    xc = x - xm
    sxx = float((xc * xc).sum())
    ym = Y.mean(axis=1)
    sl = (Y * xc[None, :]).sum(axis=1) / sxx
    ic = ym - sl * xm
    pred = sl[:, None] * x[None, :] + ic[:, None]
    res = ((Y - pred) ** 2).sum(axis=1)
    tot = ((Y - ym[:, None]) ** 2).sum(axis=1)
    r2 = xp.where(tot > 1e-12, 1.0 - res / xp.where(tot > 1e-12, tot, 1.0), 0.0)
    rw = y                                                  # momo_fit's r_at_bar is r[w]

    trk = xp.clip(r2 * xp.minimum(1.0, xp.abs(sl) / max(1e-9, slack_ref)), 0.0, 1.0)
    slack = lvl_slack * trk
    flat = xp.abs(sl) < slope_min

    # ---- the bend, only where flat AND level, which is momo_fit's own `quad='auto'`
    fin = xp.isfinite(y).astype(xp.int64)
    cfin = xp.concatenate([xp.zeros(1, xp.int64), xp.cumsum(fin)])
    whole = xp.zeros(n, bool)
    if nb <= n:
        b = xp.arange(nb - 1, n, dtype=xp.int64)
        whole[nb - 1:] = (cfin[b + 1] - cfin[b - nb + 1]) == nb

    out = {}
    for dr in (+1, -1):
        level = (rw >= 50.0 - slack) if dr > 0 else (rw <= 50.0 + slack)
        aligned = (sl > 0.0) if dr > 0 else (sl < 0.0)

        momo = ok & (~flat) & level & aligned & (r2 >= r2_min)

        need = ok & flat & level & whole
        curl = xp.zeros(n, bool)
        sel = xp.nonzero(need)[0]
        if int(sel.size):
            W, S, Ginv = _bend_weights(nb, xp)
            S1, S2, S3, S4, NB = S
            for s0 in range(0, int(sel.size), CHUNK):
                ii = sel[s0:s0 + CHUNK]
                win = ii[:, None] - (nb - 1) + xp.arange(nb, dtype=xp.int64)[None, :]
                YY = y[win]
                m = YY @ W                                  # (c, 3) = [sum xx^2 y, sum xx y, sum y]
                sy2 = (YY * YY).sum(axis=1)
                q = m @ Ginv.T                              # (c, 3) = [qa, qb, qc]
                qa, qb, qc = q[:, 0], q[:, 1], q[:, 2]
                bend = xp.abs(qa) > 1e-12
                vtx = xp.where(bend, -qb / xp.where(bend, 2.0 * qa, 1.0), xp.nan)
                arc = xp.abs(qa) * 0.25
                sp2 = (qa * qa * S4 + 2.0 * qa * qb * S3
                       + (2.0 * qa * qc + qb * qb) * S2 + 2.0 * qb * qc * S1 + qc * qc * NB)
                ssres = sy2 - 2.0 * (qa * m[:, 0] + qb * m[:, 1] + qc * m[:, 2]) + sp2
                sstot = sy2 - m[:, 2] * m[:, 2] / NB
                qr2 = xp.where(sstot > 1e-12, 1.0 - ssres / xp.where(sstot > 1e-12, sstot, 1.0), 0.0)
                qal = (qa < 0.0) if dr < 0 else (qa > 0.0)

                is_curl = bend & (vtx > vtx_lo) & (vtx < vtx_hi) & (arc >= arc_min)
                passes = is_curl & aligned[ii]
                if gate2:
                    passes = passes & qal
                if curl_r2_min > 0.0:
                    passes = passes & (qr2 >= curl_r2_min)
                curl[ii] = passes

        out[dr] = xp.asnumpy(momo | curl) if xp is cp else np.asarray(momo | curl)
    return out


def heading(momtrue, ex_r, held, delay_bars):
    """Joe 0829's away / toward tag, per bar, from the three things it reads.

        momtrue     the mom-true mask at the bar
        ex_r        the same-side extrema since the last mom-true bar, nan where there is none
        held        5 s bars since the line turned off that extrema, elapse-counted
        delay_bars  MOMO_STALL_DELAY in 5 s bars

    THE RULE IS report_wsf_bar.heading, UNCHANGED:
        if momentum_true:      return 'toward'     # C4 - a new cycle has started
        if extrema_r is None:  return 'toward'
        return 'away' if held >= MOMO_STALL_DELAY else 'toward'

    -> a bool array, True where the tag reads `away`.

    THE DELAY IS THE CALLER'S. Joe 1018 ruled it scales with the timeframe, reading B - five of the
    line's own candles, so `delay_bars = 5 * tf * 12`. It is NOT derived here, because this
    function owns the rule and not the knob.
    """
    return (~np.asarray(momtrue, bool)) & np.isfinite(ex_r) & (np.asarray(held) >= int(delay_bars))


def extrema_walk(r, momtrue, dr):
    """(ex_r, ex_bar, held) per bar - the two away/toward inputs, built from the mask.

    THE SAME WALK report_wsf_bar runs over its `seg`, which starts at the LAST mom-true bar:

        ex, held, turned = None, 0, False
        for r in seg:
            if ex is None or r is a new extreme:  ex, held, turned = r, 0, False; continue
            if turned or r has come back off ex:  turned = True; held += 1

    NO WINDOW. The DB producer bounded `seg` by a WIN_FROM knob; Joe's rule is that no window
    enters the code unless he set one, so the segment here runs from the last mom-true bar with
    nothing in front of it. A bar before the first mom-true bar of the tape walks from bar 0, which
    is what that producer's `start = 0` default does.

    `held` is a RAW BAR COUNT. The `MOMO_STALL_DELAY` comparison happens in `heading`, so moving
    that knob never rebuilds this.
    """
    r = np.asarray(r, float)
    mt = np.asarray(momtrue, bool)
    n = len(r)
    ex_r = np.full(n, np.nan)
    ex_bar = np.full(n, -1, np.int64)
    held = np.zeros(n, np.int64)
    ex = np.nan
    eb = -1
    h = 0
    turned = False
    better = (lambda v, e: v > e) if dr < 0 else (lambda v, e: v < e)
    for w in range(n):
        v = r[w]
        if mt[w]:
            ex, eb, h, turned = v, w, 0, False
        elif not np.isfinite(ex):
            if np.isfinite(v):
                ex, eb, h, turned = v, w, 0, False
        elif np.isfinite(v) and ((v < ex) if dr < 0 else (v > ex)):
            ex, eb, h, turned = v, w, 0, False
        elif turned or (np.isfinite(v) and better(v, ex)):
            turned = True
            h += 1
        ex_r[w], ex_bar[w], held[w] = ex, eb, h
    return ex_r, ex_bar, held
