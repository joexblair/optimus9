"""
ReportExporter — see class docstring for purpose, Pine alignment, and design notes.
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


class ReportExporter:
    """Exports a completed optimizer run to CSV."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def export(self, or_pk: int, output_dir: str = '.') -> str:
        rows = self._db.execute(
            '''SELECT s.pks_timestamp, s.pks_dir, s.pks_state, s.pks_pool,
                      s.pks_line_value, s.pks_slope, s.pks_slope_diff,
                      s.pks_dema_slope, s.pks_dema_value,
                      s.pks_len, s.pks_mult, s.pks_src,
                      s.pks_pool_c, s.pks_pool_w, s.pks_pool_range,
                      s.pks_slope_floor, s.pks_multiplier,
                      o.pko_max_profit_pct, o.pko_bars_to_stop,
                      o.pko_bars_to_max_profit
               FROM pk_signals s JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               WHERE s.pks_or_pk = %s ORDER BY s.pks_timestamp ASC''',
            (or_pk,), fetch=True,
        )
        path = f'{output_dir}/optimizer_run_{or_pk}.csv'
        pd.DataFrame(rows).to_csv(path, index=False)
        self._log.info(f'Exported {len(rows)} rows → {path}')
        return path
