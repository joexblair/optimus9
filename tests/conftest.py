"""
Shared pytest fixtures for optimus9 tests.

Round 260515 — minimal scaffold establishing the testing pattern. Add
fixtures as needed when new tests require shared setup.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_5s_df():
    """
    Synthetic 5s OHLCV — 720 bars = 1 hour. Random-walk close with
    derived O/H/L. Useful for testing resample / lookahead / build_source.
    """
    np.random.seed(42)
    n = 720
    start_ms = 1_699_999_920_000  # 360s-aligned (also 30s, 5s) → bars 0-5
                                  # cleanly fall in the first full window
    ts = np.arange(n) * 5_000 + start_ms
    rw = np.cumsum(np.random.randn(n) * 0.01) + 100.0
    return pd.DataFrame({
        'timestamp': ts,
        'open':   rw,
        'high':   rw + 0.02,
        'low':    rw - 0.02,
        'close':  rw,
        'volume': np.random.uniform(100, 1000, n),
    })


@pytest.fixture
def decimal_5s_df(sample_5s_df):
    """
    5s OHLCV with Decimal OHLC columns (object dtype) — simulates what
    comes back from pymysql against DECIMAL(20,8) kline_collection columns.
    Regression coverage for the 260515 lookahead_resample dtype fix.
    """
    from decimal import Decimal
    df = sample_5s_df.copy()
    for col in ['open', 'high', 'low', 'close']:
        df[col] = df[col].apply(Decimal).astype(object)
    return df
