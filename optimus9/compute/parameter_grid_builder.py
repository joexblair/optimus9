"""
ParameterGridBuilder — see class docstring for purpose, Pine alignment, and design notes.
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


class ParameterGridBuilder:
    """Reads test_param_ranges for a tc_pk and expands all parameter combinations."""

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def build(self, tc_pk: int) -> list:
        rows = self._db.execute(
            '''SELECT tpr_param_name, tpr_current_value, tpr_step,
                      tpr_range, tpr_enum_values, tpr_param_type
               FROM test_param_ranges WHERE tpr_tc_pk = %s ORDER BY tpr_param_name''',
            (tc_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No param ranges for tc_pk={tc_pk}')

        param_lists = {}
        for row in rows:
            name  = row['tpr_param_name']
            ptype = row['tpr_param_type']

            if ptype == 'enum':
                param_lists[name] = [v.strip() for v in row['tpr_enum_values'].split(',')]
                continue

            current = float(row['tpr_current_value'])
            step    = float(row['tpr_step'])
            rng     = float(row['tpr_range'])
            n       = int(round(rng / step)) if step else 0
            half    = n // 2
            values  = [round(current - half * step + k * step, 8) for k in range(n + 1)]

            if ptype == 'int':
                values = sorted(set(int(round(v)) for v in values))
                if name == 'pool_range':
                    # pool_range=0 means disabled — exclude
                    values = [v for v in values if v > 0]
                elif name in ('len', 'len_rsi', 'len_stoch'):
                    # r04: length params must be positive (k_len=0, rsi_len=0
                    # etc. would crash IndicatorComputer). Center-symmetric
                    # sweeps around small baselines can land on zero or negative.
                    values = [v for v in values if v > 0]

            param_lists[name] = values

        keys   = list(param_lists.keys())
        combos = list(itertools.product(*[param_lists[k] for k in keys]))
        self._log.info(f'Grid: {len(combos)} combinations from {len(keys)} params')
        return [dict(zip(keys, combo)) for combo in combos]
