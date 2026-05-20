"""
PKDetector — see class docstring for purpose, Pine alignment, and design notes.
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


class PKDetector:
    """
    Applies f_pk_state logic across a pre-computed indicator line + DEMA.
    Only emits signals when the combined gate oob_side is non-zero and
    the PK direction matches the gate direction.

    Pine alignment note (260514)
    ---------------------------
    This class's peak-search window is one bar wider than Pine's f_pk_state
    (uses pool_range+1 bars where Pine uses pool_range). Intentionally
    preserved for continuity with the 30-day grind dataset that produced
    the b6M centroid (or_pk=1).

    The newer Pk5sGateComputer matches Pine exactly — its f_pk_state covers
    line[i - upper + 1 : i - lower + 1]. The two classes coexist in this
    round; the discrepancy here will be patched once the next clean centroid
    is locked. See round spec 260514_pk5s_spec.md.

    r05 (260519): line_type parameter added so K-line targets can use this
    gated path. BB lines populate 'mult'; K lines populate 'len_rsi' and
    'len_stoch'. Default 'bb' preserves the prior calling contract for any
    code that didn't update with this change.
    """

    _PM_LONG  =  2.0
    _PM_SHORT = -2.0

    def __init__(self, high_b: float = 70.0, low_b: float = 30.0) -> None:
        self._midpoint = (high_b + low_b) / 2.0
        self._log      = get_logger(self.__class__.__name__)

    def detect(self, line: np.ndarray, dema: np.ndarray,
               pool_c: int, pool_w: int, pool_range: int,
               multiplier: int, slope_floor: float,
               oob_side: np.ndarray, params: dict,
               line_type: str = 'bb') -> list:

        # pool_range=0 means disabled — skip
        if pool_range == 0:
            return []

        signals = []
        half    = pool_range // 2

        for label, bars in (('close', pool_c), ('wide', pool_w)):
            lower  = (bars - half) * multiplier
            upper  = (bars + half) * multiplier
            center = bars * multiplier

            for i in range(upper + 1, len(line)):
                if np.isnan(line[i]) or np.isnan(dema[i]) or np.isnan(dema[i - center]):
                    continue
                side = int(oob_side[i])
                if side == 0:
                    continue

                window = line[i - upper : i - lower + 1]
                if not len(window):
                    continue
                peak = np.max(window) if line[i] > self._midpoint else np.min(window)

                line_slope  = float(line[i] - peak)
                price_slope = float(dema[i] - dema[i - center])
                slope_diff  = abs(line_slope - price_slope)

                if slope_diff <= slope_floor:
                    continue

                pk_state = (
                    (1.0 if line_slope > 0 else -1.0)
                    if np.sign(line_slope) != np.sign(price_slope)
                    else (self._PM_LONG if line_slope > 0 else self._PM_SHORT)
                )

                expected = -side
                if pk_state not in (float(expected), float(expected) * 2.0):
                    continue

                sig = {
                    'bar_index':   i,
                    'direction':   expected,
                    'pk_state':    pk_state,
                    'line_value':  float(line[i]),
                    'slope':       line_slope,
                    'slope_diff':  slope_diff,
                    'dema_slope':  price_slope,
                    'dema_value':  float(dema[i]),
                    'pool':        label,
                    'len':         params['len'],
                    'src':         params['src'],
                    'pool_c':      pool_c,
                    'pool_w':      pool_w,
                    'pool_range':  pool_range,
                    'slope_floor': slope_floor,
                    'multiplier':  multiplier,
                }
                # Line-type-specific params: BB carries mult; K carries the
                # two extra length params. _persist_gated reads these by
                # line_type, so they must be present on the side that needs
                # them and absent (or None) on the other.
                if line_type == 'bb':
                    sig['mult'] = params['mult']
                else:  # 'k'
                    sig['len_rsi']   = params['len_rsi']
                    sig['len_stoch'] = params['len_stoch']

                signals.append(sig)

        return signals
