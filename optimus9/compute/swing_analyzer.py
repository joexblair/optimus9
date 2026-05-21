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

# ── cross-package imports ─────────────────────────────────────────────────
from .outcome_walker import walk_outcome


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

    def __init__(self, stop_pct: float = 0.33, max_bars: int = None) -> None:
        """
        max_bars is deprecated as of r05 260521. Accepted for back-compat
        with callers that still pass tc_max_bars, but ignored. A trade
        either stops or runs off the dataset — no time cap.
        """
        self._stop_pct = stop_pct
        self._log      = get_logger(self.__class__.__name__)
        if max_bars is not None:
            self._log.debug(f'max_bars={max_bars} ignored (deprecated)')

    def analyze(self, signals: list, close: np.ndarray,
                timestamps: np.ndarray = None) -> list:
        """
        Walk each signal's outcome via outcome_walker.walk_outcome.

        timestamps is optional — when provided, threaded through to
        outcome_walker for future per-call debug instrumentation.
        """
        return [
            {**sig, **walk_outcome(
                close, sig['bar_index'], sig['direction'],
                self._stop_pct, timestamps,
            )}
            for sig in signals
        ]
