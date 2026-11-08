"""One synthetic 5 s base frame, built from a fixed seed, so a refactor of the developing-line
builders can be proved numerically without a DB or a Jig. -> pandas.DataFrame."""
import numpy as np
import pandas as pd


def frame(n=51840, seed=20261108):
    rng = np.random.default_rng(seed)
    ts = 1788000000000 + np.arange(n) * 5000
    c = 0.18 + np.cumsum(rng.normal(0, 2e-5, n))
    h = c + np.abs(rng.normal(0, 1e-5, n))
    l = c - np.abs(rng.normal(0, 1e-5, n))
    o = np.concatenate([[c[0]], c[:-1]])
    return pd.DataFrame({'timestamp': ts, 'open': o, 'high': h, 'low': l, 'close': c,
                         'volume': np.full(n, 1000.0)})
