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
    """
    Drives the parameter grid. Per combo: compute line, detect PKs, analyze, persist.

    Round 04 changes:
      - K-line target support. When config['ic_line_type']=='k', the line is
        computed via IndicatorComputer.f_k with len_rsi/len_stoch/len from
        the grid combo. BB targets use f_bb (existing path).
      - Persists pks_len_rsi and pks_len_stoch alongside existing per-row
        params. NULL for BB combos.
      - pko_result and pko_stop_pct dropped from pk_outcomes — schema reflects.
      - p_rev (lookahead) is a no-op for 5s targets (ind_seconds==5).
        Existing branch handles this.
    """

    def __init__(self, db: DatabaseManager, detector: PKDetector,
                 analyzer: SwingAnalyzer) -> None:
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
        close       = base_df['close'].to_numpy(dtype=float)
        total       = len(param_grid)
        ind_seconds = int(config['ic_itf_seconds'])
        line_type   = config.get('ic_line_type', 'bb')

        use_lookahead = bool(p_rev_enabled and ind_seconds > 5 and line_type == 'bb')
        if use_lookahead:
            self._log.info(
                f'p_rev active: indicator line via f_bb_lookahead (TF={ind_seconds}s)'
            )
        elif line_type == 'k':
            self._log.info(f'K-line target — using f_k path (TF={ind_seconds}s)')

        for idx, params in enumerate(param_grid, 1):
            self._log.info(f'[{idx}/{total}]  {params}')

            line = self._build_line(
                base_df, ind_df, line_type, ind_seconds,
                use_lookahead, params, config,
            )
            signals = self._detector.detect(
                line, dema,
                int(params['pool_c']), int(params['pool_w']),
                int(params['pool_range']), int(params['multiplier']),
                float(params['slope_floor']), oob_side, params,
            )
            outcomes = self._analyzer.analyze(signals, close)
            self._persist(or_pk, base_df['timestamp'].to_numpy(), outcomes, line_type)

    @staticmethod
    def _build_line(base_df: pd.DataFrame, ind_df: pd.DataFrame,
                    line_type: str, ind_seconds: int,
                    use_lookahead: bool, params: dict, config: dict) -> np.ndarray:
        """
        Compute the indicator line for one grid combo. Branches on line_type
        and the lookahead flag (BB-only). 5s native paths skip resampling.
        """
        if line_type == 'k':
            # K-line: rsi → stoch → sma chain, no lookahead concept.
            src_series = IndicatorComputer.build_source(ind_df, params['src'])
            line_raw   = IndicatorComputer.f_k(
                src_series,
                int(params['len_rsi']),
                int(params['len_stoch']),
                int(params['len']),
            )
            if ind_seconds == 5:
                return np.asarray(line_raw, dtype=float)
            return IndicatorComputer.align_to_base(line_raw, ind_df, base_df)

        # BB path
        if use_lookahead:
            return IndicatorComputer.f_bb_lookahead(
                base_df, ind_seconds,
                int(params['len']), float(params['mult']), params['src'],
                float(config['ic_high_boundary']),
                float(config['ic_low_boundary']),
            )

        src_series = IndicatorComputer.build_source(ind_df, params['src'])
        line_raw   = IndicatorComputer.f_bb(
            src_series, int(params['len']), float(params['mult']),
        )
        if ind_seconds == 5:
            return np.asarray(line_raw, dtype=float)
        return IndicatorComputer.align_to_base(line_raw, ind_df, base_df)

    @staticmethod
    def _db_val(v):
        """NaN/inf → None so MySQL gets NULL rather than a literal string."""
        if isinstance(v, float) and not math.isfinite(v):
            return None
        return v

    def _persist(self, or_pk: int, timestamps: np.ndarray,
                 outcomes: list, line_type: str) -> None:
        if not outcomes:
            return

        dv = self._db_val
        sig_sql = '''INSERT INTO pk_signals
            (pks_or_pk, pks_timestamp, pks_dir, pks_state, pks_line_value,
             pks_slope, pks_slope_diff, pks_dema_slope, pks_dema_value, pks_pool,
             pks_len, pks_mult, pks_src,
             pks_len_rsi, pks_len_stoch,
             pks_pool_c, pks_pool_w, pks_pool_range,
             pks_slope_floor, pks_multiplier)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

        # r04: pko_outcomes loses pko_result and pko_stop_pct
        out_sql = '''INSERT INTO pk_outcomes
            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit)
            VALUES (%s,%s,%s,%s)'''

        sig_rows = []
        for o in outcomes:
            # BB: pks_len from params['len']; pks_mult populated; K cols NULL
            # K:  pks_len from params['len'] (k_len); pks_mult NULL;
            #     pks_len_rsi, pks_len_stoch populated
            if line_type == 'k':
                pks_mult      = None
                pks_len_rsi   = int(o['len_rsi'])
                pks_len_stoch = int(o['len_stoch'])
            else:
                pks_mult      = o['mult']
                pks_len_rsi   = None
                pks_len_stoch = None

            sig_rows.append((
                or_pk, int(timestamps[o['bar_index']]),
                o['direction'], dv(o['pk_state']), dv(o['line_value']),
                dv(o['slope']), dv(o['slope_diff']), dv(o['dema_slope']),
                dv(o['dema_value']), o['pool'],
                int(o['len']), pks_mult, o['src'],
                pks_len_rsi, pks_len_stoch,
                int(o['pool_c']), int(o['pool_w']), int(o['pool_range']),
                float(o['slope_floor']), int(o['multiplier']),
            ))

        first_id = self._db.executemany(sig_sql, sig_rows)

        self._db.executemany(out_sql, [
            (first_id + i,
             dv(o['max_profit_pct']),
             o['bars_to_stop'],
             o['bars_to_max_profit'])
            for i, o in enumerate(outcomes)
        ])
