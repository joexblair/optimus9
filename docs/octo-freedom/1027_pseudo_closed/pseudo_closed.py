"""THE PSEUDO-CLOSED LINE. Joe 1027, his words and his idea:

    "can we simply look back the width of the TF, at each emerging bar, and test the diff between
     the first value (one TF-width earlier) and the current bar's value? eg at 1432 testing ws13r,
     get the ws13r emerging value at 1419 and the ws13r emerging value at now, and create a psuedo
     ws13 closed bar?"

    "forge - lets make things easier for ourselves"

WHAT IT IS. At every 5 s bar t, the ws{T}r line is computed on the bar sequence that ENDS AT t -
closes at t, t-T, t-2T, ... So the value at t is the CLOSED value of a ws{T} grid phased to close
exactly at t. Every bar in that sequence is complete; none of them is a forming bucket.

WHY THAT IS LEGITIMATE, his own observation: *"if teadingview are using midnight as the offset for
non-standarad lines, it backs the concept of choosing any seam"*. TV re-anchors non-day-divisor TFs
to midnight rather than the epoch, so the seam is already a choice. This picks the seam that closes
at the bar being read.

IT IS CAUSAL BY CONSTRUCTION. Every input is a close at or before t. There is no forming bucket and
no forward read, which is asserted rather than claimed.

THE CHAIN IS THE PRODUCT'S OWN, read out of optimus9.compute.indicator_computer:
    k = _sma(_stoch(_rsi(close, rsi_len), stc_len), k_len)
    _rsi  = Wilder: delta, RMA of gains and losses at n, 100 - 100/(1+rs)
    _rma  = SMA-seeded, prev = (prev*(n-1) + x)/n
    _stoch= 100*(x-min)/(max-min) over n, 50 when the range is 0
and the ws{T}r config is ('k', rsi 5, stc 8, k_len 7, 'close') from mech_lines(db,'wsf').
TRANSPOSING rsi/stc/k_len IS SILENT AND WRONG - the jig says so - so the tuple order is read from
line_config, not retyped from memory.

THE BAR WARMUP. The chain needs ~19 bars before its first finite value and Wilder's RMA at n=5
needs more to converge. BARS is the count of TF bars held per read; it is a WARMUP, not a horizon
on anything Joe measures, and `converged()` reports what changes when it is doubled, so the value
is justified rather than chosen.
"""
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

RSI_N, STC_N, K_N = 5, 8, 7            # ('k', rsi 5, stc 8, k_len 7, 'close') - the wsf r config
BARS = 120                              # TF bars of history per read; see `converged()`


def _rma_axis0(X, n):
    """Wilder's RMA down axis 0 (oldest row first), vectorised across the other axis."""
    out = np.full_like(X, np.nan)
    if X.shape[0] < n:
        return out
    prev = np.nanmean(X[:n], axis=0)
    out[n - 1] = prev
    m = n - 1
    for i in range(n, X.shape[0]):
        x = X[i]
        prev = np.where(np.isnan(x), prev, (prev * m + np.where(np.isnan(x), 0.0, x)) / n)
        out[i] = prev
    return out


def _rsi_axis0(X, n):
    d = np.full_like(X, np.nan)
    d[1:] = X[1:] - X[:-1]
    g = _rma_axis0(np.where(d > 0, d, 0.0), n)
    l = _rma_axis0(np.where(d < 0, -d, 0.0), n)
    with np.errstate(invalid='ignore', divide='ignore'):
        rs = np.where(l != 0, g / l, np.inf)
    return 100.0 - (100.0 / (1.0 + rs))


def _stoch_axis0(X, n):
    w = sliding_window_view(X, n, axis=0)              # (rows-n+1, cols, n)
    lo = np.nanmin(w, axis=-1); hi = np.nanmax(w, axis=-1)
    rng = hi - lo
    cur = X[n - 1:]
    with np.errstate(invalid='ignore', divide='ignore'):
        o = np.where(rng != 0, 100.0 * (cur - lo) / rng, 50.0)
    o = np.where(np.isnan(rng), np.nan, o)
    out = np.full_like(X, np.nan)
    out[n - 1:] = o
    return out


def _sma_axis0(X, n):
    w = sliding_window_view(X, n, axis=0)
    out = np.full_like(X, np.nan)
    out[n - 1:] = np.nanmean(w, axis=-1)
    return out


def series(close, tf_minutes, idx, bars=BARS):
    """The pseudo-closed ws{tf}r at each bar in `idx`. -> an array the length of `idx`.

        close        the 5 s close series
        tf_minutes   the TF width
        idx          the 5 s bar indices to evaluate at

    THE SEQUENCE AT t IS t, t-T, t-2T, ... with T = tf_minutes of 5 s bars, so a bucket closes
    exactly at t and every bucket is complete.
    """
    close = np.asarray(close, float)
    T = int(tf_minutes) * 60 // 5
    idx = np.asarray(idx, np.int64)
    assert T > 0, 'the TF is shorter than one 5 s bar'
    #   X[i] is the OLDEST row first: i = 0 is t - bars*T, i = bars is t itself
    X = np.full((bars + 1, len(idx)), np.nan)
    for i in range(bars + 1):
        back = (bars - i) * T
        src = idx - back
        ok = src >= 0
        X[i, ok] = close[src[ok]]
    assert np.all((idx - 0) <= (len(close) - 1)), 'an index is past the end of the tape'
    k = _sma_axis0(_stoch_axis0(_rsi_axis0(X, RSI_N), STC_N), K_N)
    return k[-1]                                        # the row stamped at t itself


def converged(close, tf_minutes, idx, a=BARS, b=None):
    """What doubling the bar warmup changes. -> (max abs diff, the fraction of bars that move)."""
    b = int(a * 2) if b is None else int(b)
    u, v = series(close, tf_minutes, idx, a), series(close, tf_minutes, idx, b)
    d = np.abs(u - v)
    fin = np.isfinite(d)
    return (float(np.nanmax(d[fin])) if fin.any() else float('nan'),
            float(np.mean(d[fin] > 1e-9)) if fin.any() else float('nan'))
