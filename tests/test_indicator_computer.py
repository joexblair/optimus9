"""Tests for optimus9.compute.indicator_computer."""

import numpy as np
import pandas as pd
import pytest

from optimus9 import IndicatorComputer


def test_lookahead_resample_developing_high_is_cummax(sample_5s_df):
    """
    Developing high at each 5s bar should equal the running max of 5s
    highs within its containing higher-TF window. 30s windows = 6 × 5s.
    """
    result = IndicatorComputer.lookahead_resample(sample_5s_df, target_seconds=30)

    # First 6 bars are in window 0 — developing high should be cummax of the
    # first 6 5s highs.
    first_window_highs = sample_5s_df['high'].iloc[:6].astype(float).cummax().to_numpy()
    np.testing.assert_array_almost_equal(result['high'].iloc[:6].to_numpy(),
                                          first_window_highs)


def test_lookahead_resample_developing_open_is_window_first(sample_5s_df):
    """Every 5s bar in a developing window shares the window's first open."""
    result = IndicatorComputer.lookahead_resample(sample_5s_df, target_seconds=30)
    # All 6 bars of window 0 should have the same open value
    first_open = float(sample_5s_df['open'].iloc[0])
    assert all(result['open'].iloc[:6] == first_open)


def test_lookahead_resample_accepts_decimal_dtype(decimal_5s_df):
    """
    Regression test for 260515 fix: kline_collection's DECIMAL columns
    come through pymysql as object dtype. lookahead_resample must cast
    before groupby cython ops.
    """
    # Should not raise NotImplementedError ("cummax is not supported
    # for object dtype")
    result = IndicatorComputer.lookahead_resample(decimal_5s_df, target_seconds=30)
    assert len(result) == len(decimal_5s_df)
    assert result['high'].dtype == float


def test_lookahead_resample_resets_at_window_boundary(sample_5s_df):
    """
    Pine barmerge.lookahead_on aligns to absolute clock boundaries.
    With 30s windows and 5s bars, bar 6 starts a new window — its
    developing open should differ from bar 5's (which is the close of
    the prior window) unless the underlying values happen to coincide.
    Tests the boundary-reset invariant, not just same-window cumulative.
    """
    result = IndicatorComputer.lookahead_resample(sample_5s_df, target_seconds=30)
    # Bar 6 opens a new 30s window; its developing 'open' should be
    # sample_5s_df['open'].iloc[6], regardless of what bars 0-5 did.
    expected_w1_open = float(sample_5s_df['open'].iloc[6])
    assert float(result['open'].iloc[6]) == expected_w1_open
    # And bars 6-11 should all share that open (they're in the same window)
    assert all(result['open'].iloc[6:12] == expected_w1_open)