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
    def split(bar: dict) -> list:
        T = int(bar['timestamp'])
        O, H, L, C = float(bar['open']), float(bar['high']), float(bar['low']), float(bar['close'])
        V      = float(bar['volume'])
        n      = SyntheticBarBuilder._N
        unit_v = round(V / n, 8)
        prices = [O + i * (C - O) / n for i in range(n + 1)]
        h_bar  = n - 1 if C >= O else 0
        l_bar  = 0     if C >= O else n - 1

        bars = []
        for i in range(n):
            o_i = prices[i]
            c_i = prices[i + 1]
            h_i = max(o_i, c_i)
            l_i = min(o_i, c_i)
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
    def split_batch(bars_1m: list) -> list:
        out = []
        for bar in bars_1m:
            out.extend(SyntheticBarBuilder.split(bar))
        return out
