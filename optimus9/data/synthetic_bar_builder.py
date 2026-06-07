"""
SyntheticBarBuilder — see class docstring for purpose, Pine alignment, and design notes.
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


class SyntheticBarBuilder:
    """
    Splits 1m OHLCV bars into 12 × 5s bars using linear price interpolation.
    Assigns the 1m H to the bar where the path peaks, L to where it troughs.
    Bullish (C >= O): low in first bar, high in last bar.
    Bearish (C < O):  high in first bar, low in last bar.
    """

    _N       = 12
    _STEP_MS = 5_000

    @staticmethod
    def split(bar: dict, wiggle: float = 0.0) -> list:
        """Split a 1m bar into 12 × 5s. wiggle=0 → linear close path (default; live gap-fill).
        wiggle>0 → a per-minute-seeded random-walk BRIDGE on the closes, pinned to the faithful
        close and clipped to [L,H], scaled to wiggle·(H-L). The 5s oscillators (pk, gcb5p) then
        see realistic intra-minute churn instead of a ruler line, while 1m O/H/L/C/V stay exact.
        Seeded by the bar timestamp → deterministic (re-runs reproduce the tape)."""
        T = int(bar['timestamp'])
        O, H, L, C = float(bar['open']), float(bar['high']), float(bar['low']), float(bar['close'])
        V      = float(bar['volume'])
        n      = SyntheticBarBuilder._N
        unit_v = round(V / n, 8)

        if wiggle > 0.0 and H > L:
            rng    = np.random.default_rng(T)                         # deterministic per minute
            trend  = O + np.arange(1, n + 1) * (C - O) / n            # linear closes, trend[-1]=C
            w      = rng.standard_normal(n).cumsum()
            w      = w - w[-1] * np.arange(1, n + 1) / n              # bridge: pin the close end to 0
            w      = w / (np.abs(w).max() + 1e-12) * wiggle * (H - L)
            closes = np.clip(trend + w, L, H)
            closes[-1] = C                                            # exact faithful close
            prices = [O] + closes.tolist()
        else:
            prices = [O + i * (C - O) / n for i in range(n + 1)]

        h_bar = int(np.argmax(prices[1:]))                           # H at the peak-close bar
        l_bar = int(np.argmin(prices[1:]))                           # L at the trough-close bar

        bars = []
        for i in range(n):
            o_i, c_i = prices[i], prices[i + 1]
            h_i, l_i = max(o_i, c_i), min(o_i, c_i)
            if i == h_bar:
                h_i = max(h_i, H)
            if i == l_bar:
                l_i = min(l_i, L)
            bars.append(dict(
                timestamp = T + i * SyntheticBarBuilder._STEP_MS,
                open=round(o_i, 8), high=round(h_i, 8),
                low=round(l_i, 8),  close=round(c_i, 8), volume=unit_v,
            ))
        return bars

    @staticmethod
    def split_batch(bars_1m: list, wiggle: float = 0.0) -> list:
        out = []
        for bar in bars_1m:
            out.extend(SyntheticBarBuilder.split(bar, wiggle=wiggle))
        return out
