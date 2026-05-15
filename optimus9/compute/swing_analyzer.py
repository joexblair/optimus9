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

    Exit logic:
      - Stop is fixed at entry ± stop_pct% — never moves.
      - Profit zone starts when price travels at least (stop_pct + drag_pct)%
        in the trade direction. Below that threshold the position hasn't covered
        its risk + drag and max_profit is not tracked.
      - won        = stop breached after entering profit zone.
      - stopped    = stop breached before entering profit zone.
      - inconclusive = max_bars cap reached without stop breach.
    """

    def __init__(self, stop_pct: float = 0.33, max_bars: int = 1080,
                 drag_pct: float = 0.0) -> None:
        self._stop_long    = 1.0 - stop_pct / 100.0
        self._stop_short   = 1.0 + stop_pct / 100.0
        self._profit_long  = 1.0 + (stop_pct + drag_pct) / 100.0
        self._profit_short = 1.0 - (stop_pct + drag_pct) / 100.0
        self._stop_pct     = stop_pct
        self._drag_pct     = drag_pct
        self._max_bars     = max_bars
        self._log          = get_logger(self.__class__.__name__)

    def analyze(self, signals: list, close: np.ndarray) -> list:
        return [self._evaluate(sig, close) for sig in signals]

    def _evaluate(self, sig: dict, close: np.ndarray) -> dict:
        i, direction = sig['bar_index'], sig['direction']
        entry        = close[i]
        cap          = min(i + self._max_bars, len(close) - 1)

        stop_level       = entry * (self._stop_long  if direction == 1 else self._stop_short)
        profit_threshold = entry * (self._profit_long if direction == 1 else self._profit_short)

        best_price         = entry
        in_profit_zone     = False
        max_profit_pct     = 0.0
        bars_to_max_profit = None
        bars_to_stop       = None
        result             = 'inconclusive'

        for j in range(i + 1, cap + 1):
            c = close[j]

            if direction == 1:
                if not in_profit_zone and c >= profit_threshold:
                    in_profit_zone = True
                if in_profit_zone and c > best_price:
                    best_price         = c
                    max_profit_pct     = (best_price / entry - 1.0) * 100.0
                    bars_to_max_profit = j - i
                if c <= stop_level:
                    bars_to_stop = j - i
                    result       = 'won' if in_profit_zone else 'stopped'
                    break
            else:
                if not in_profit_zone and c <= profit_threshold:
                    in_profit_zone = True
                if in_profit_zone and c < best_price:
                    best_price         = c
                    max_profit_pct     = (entry / best_price - 1.0) * 100.0
                    bars_to_max_profit = j - i
                if c >= stop_level:
                    bars_to_stop = j - i
                    result       = 'won' if in_profit_zone else 'stopped'
                    break

        return {
            **sig,
            'max_profit_pct':     round(max_profit_pct, 6),
            'bars_to_stop':       bars_to_stop,
            'bars_to_max_profit': bars_to_max_profit,
            'result':             result,
            'stop_pct':           self._stop_pct,
        }
