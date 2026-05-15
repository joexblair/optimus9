"""
OptimizerRunner — see class docstring for purpose, Pine alignment, and design notes.
"""


"""
managers.py — PK Optimizer
All process classes. One responsibility per class.
Every class calls get_logger(self.__class__.__name__).

Terminology:
  OOB  = out of boundary (indicator has crossed high/low threshold)
  IB   = in boundary (indicator is within thresholds)
  OS/OB remain only in RSI/K oscillator context where they are technically correct.
"""

import asyncio
import itertools
import json
import math
import multiprocessing
import signal
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable, Optional

import mysql.connector
import numpy as np
import pandas as pd
import requests
import websockets

from logger import get_logger

# ── cross-package imports ─────────────────────────────────────────────────
from ..db.database_manager import DatabaseManager
from ..compute.pk_detector import PKDetector
from ..compute.swing_analyzer import SwingAnalyzer
from ..compute.indicator_computer import IndicatorComputer


class OptimizerRunner:
    """Drives the parameter grid. Per combo: compute, detect, analyze, persist."""

    def __init__(self, db: DatabaseManager, detector: PKDetector, analyzer: SwingAnalyzer) -> None:
        self._db       = db
        self._detector = detector
        self._analyzer = analyzer
        self._log      = get_logger(self.__class__.__name__)

    def run(self, or_pk: int,
            base_df:  pd.DataFrame,
            ind_df:   pd.DataFrame,
            dema:     np.ndarray,
            oob_side: np.ndarray,
            param_grid: list,
            config: dict,
            p_rev_enabled: bool = False) -> None:
        """
        Drive the parameter grid for one calibration target.

        Round 260514: when p_rev_enabled and the calibration line's TF > 5s,
        compute the indicator line via IndicatorComputer.f_bb_lookahead
        (Pine barmerge.lookahead_on equivalent) instead of the resample +
        forward-fill chain. Returns values that resolve at 5s precision
        against the developing higher-TF bar.

        For 5s-native targets (ind_seconds == 5) p_rev is a no-op — the
        flag is honoured by collapsing to the regular f_bb path since there
        is no higher TF to look ahead on.
        """
        
        close = base_df['close'].to_numpy(dtype=float)
        total = len(param_grid)

        ind_seconds = int(config['ic_itf_seconds'])
        use_lookahead = bool(p_rev_enabled and ind_seconds > 5)
        if use_lookahead:
            self._log.info(f'p_rev active: indicator line via f_bb_lookahead '
                           f'(TF={ind_seconds}s)')

        for idx, params in enumerate(param_grid, 1):
            self._log.info(f'[{idx}/{total}]  {params}')
            if use_lookahead:
                # Pine: request.security(..., barmerge.lookahead_on)
                line = IndicatorComputer.f_bb_lookahead(
                    base_df, ind_seconds,
                    int(params['len']), float(params['mult']), params['src'],
                    float(config['ic_high_boundary']),
                    float(config['ic_low_boundary']),
                )
            else:
                line_src = IndicatorComputer.build_source(ind_df, params['src'])
                line_raw = IndicatorComputer.f_bb(line_src, int(params['len']),
                                                   float(params['mult']))
                line     = IndicatorComputer.align_to_base(line_raw, ind_df, base_df)
            signals  = self._detector.detect(
                line, dema,
                int(params['pool_c']), int(params['pool_w']),
                int(params['pool_range']), int(params['multiplier']),
                float(params['slope_floor']), oob_side, params,
            )
            outcomes = self._analyzer.analyze(signals, close)
            self._persist(or_pk, base_df['timestamp'].to_numpy(), outcomes)

    @staticmethod
    def _db_val(v):
        """Convert NaN/inf to None so MySQL receives NULL rather than a literal string."""
        if isinstance(v, float) and not math.isfinite(v):
            return None
        return v

    def _persist(self, or_pk: int, timestamps: np.ndarray, outcomes: list) -> None:
        if not outcomes:
            return

        dv = self._db_val
        sig_sql = '''INSERT INTO pk_signals
            (pks_or_pk, pks_timestamp, pks_dir, pks_state, pks_line_value,
             pks_slope, pks_slope_diff, pks_dema_slope, pks_dema_value, pks_pool,
             pks_len, pks_mult, pks_src,
             pks_pool_c, pks_pool_w, pks_pool_range, pks_slope_floor, pks_multiplier)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        out_sql = '''INSERT INTO pk_outcomes
            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop,
             pko_bars_to_max_profit, pko_result, pko_stop_pct)
            VALUES (%s,%s,%s,%s,%s,%s)'''

        sig_rows = [
            (or_pk, int(timestamps[o['bar_index']]),
             o['direction'], dv(o['pk_state']), dv(o['line_value']),
             dv(o['slope']), dv(o['slope_diff']), dv(o['dema_slope']), dv(o['dema_value']), o['pool'],
             o['len'], o['mult'], o['src'],
             o['pool_c'], o['pool_w'], o['pool_range'], o['slope_floor'], o['multiplier'])
            for o in outcomes
        ]

        first_id = self._db.executemany(sig_sql, sig_rows)

        self._db.executemany(out_sql, [
            (first_id + i,
             dv(o['max_profit_pct']), o['bars_to_stop'],
             o['bars_to_max_profit'], o['result'], o['stop_pct'])
            for i, o in enumerate(outcomes)
        ])
