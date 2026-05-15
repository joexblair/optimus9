"""
OutlierReporter — see class docstring for purpose, Pine alignment, and design notes.
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


class OutlierReporter:
    """Queries pk_outcomes and logs param sets with unusual win-rate distributions."""

    _WIN_RATE_HI = 70.0
    _WIN_RATE_LO = 30.0
    _MIN_SAMPLES = 20

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self) -> None:
        self._log.info('Generating outlier report')
        stats = self._db.execute(
            '''SELECT pks_len, pks_mult, pks_src,
                      COUNT(*) AS total,
                      SUM(pko_result = 'won') AS won,
                      AVG(pko_max_profit_pct) AS avg_profit
               FROM pk_signals s JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               GROUP BY pks_len, pks_mult, pks_src
               HAVING COUNT(*) >= %s
               ORDER BY won / COUNT(*) DESC''',
            (self._MIN_SAMPLES,), fetch=True,
        )
        if not stats:
            self._log.info('No results to report')
            return
        for row in stats:
            win_rate = int(row['won']) / max(int(row['total']), 1) * 100
            if win_rate >= self._WIN_RATE_HI or win_rate <= self._WIN_RATE_LO:
                flag = 'HIGH' if win_rate >= self._WIN_RATE_HI else 'LOW'
                self._log.info(
                    f'OUTLIER [{flag}]  len={row["pks_len"]}  mult={row["pks_mult"]}'
                    f'  src={row["pks_src"]}  win={win_rate:.1f}%  n={row["total"]}'
                    f'  avg_profit={float(row["avg_profit"]):.4f}%'
                )
        self._log.info('Outlier report complete')
