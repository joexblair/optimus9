"""
SwingAnalyzer — see class docstring for purpose, Pine alignment, and design notes.
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


class SwingAnalyzer:
    """
    Walks forward from each PK signal using close prices.

    Exit logic (r04 simplified):
      - Stop is fixed at entry ± stop_pct% — never moves.
      - max_profit_pct tracks the best excursion in the trade direction
        across the whole walk (no profit-zone gating).
      - bars_to_stop is set when stop is breached; NULL otherwise (inconclusive).

    The won/stopped/inconclusive classification is no longer SwingAnalyzer's
    concern — AnalyzeManager re-derives it from max_profit_pct + bars_to_stop
    using tc.tc_profit_zone as the "what counts" threshold. This keeps the
    classification single-sourced and tunable without re-running grinds.
    """

    def __init__(self, stop_pct: float = 0.33, max_bars: int = 1080) -> None:
        # r04: dropped drag_pct, profit_long, profit_short — classification
        # moved to AnalyzeManager (max_profit_pct >= tc.tc_profit_zone).
        self._stop_long  = 1.0 - stop_pct / 100.0
        self._stop_short = 1.0 + stop_pct / 100.0
        self._stop_pct   = stop_pct
        self._max_bars   = max_bars
        self._log        = get_logger(self.__class__.__name__)

    def analyze(self, signals: list, close: np.ndarray) -> list:
        return [self._evaluate(sig, close) for sig in signals]

    def _evaluate(self, sig: dict, close: np.ndarray) -> dict:
        i, direction = sig['bar_index'], sig['direction']
        entry        = close[i]
        cap          = min(i + self._max_bars, len(close) - 1)

        stop_level = entry * (self._stop_long if direction == 1 else self._stop_short)

        best_price         = entry
        max_profit_pct     = 0.0
        bars_to_max_profit = None
        bars_to_stop       = None

        for j in range(i + 1, cap + 1):
            c = close[j]

            if direction == 1:
                if c > best_price:
                    best_price         = c
                    max_profit_pct     = (best_price / entry - 1.0) * 100.0
                    bars_to_max_profit = j - i
                if c <= stop_level:
                    bars_to_stop = j - i
                    break
            else:
                if c < best_price:
                    best_price         = c
                    max_profit_pct     = (entry / best_price - 1.0) * 100.0
                    bars_to_max_profit = j - i
                if c >= stop_level:
                    bars_to_stop = j - i
                    break

        return {
            **sig,
            'max_profit_pct':     round(max_profit_pct, 6),
            'bars_to_stop':       bars_to_stop,
            'bars_to_max_profit': bars_to_max_profit,
        }
