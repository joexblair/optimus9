"""
IndicatorMonitor — see class docstring for purpose, Pine alignment, and design notes.
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


class IndicatorMonitor:
    """
    Runs once per invocation — computes and logs current indicator values
    for live validation against TradingView.
    Scheduled inline worker (interval_s=10) in ProcessManager.
    Shows each gate line independently plus combined OOB status.
    """

    _LOOKBACK = 2000

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, tp_pk: int, tc_pk: int) -> None:
        try:
            self._report(tp_pk, tc_pk)
        except Exception as exc:
            self._log.error(f'Monitor error: {exc}')

    def _report(self, tp_pk: int, tc_pk: int) -> None:
        cfg = self._load_cfg(tc_pk)
        if not cfg:
            return

        ind_name = f'{cfg["is_prefix"]}{cfg["itf_label"]}{cfg["il_suffix"]}'

        base_df = self._load_klines(tp_pk)
        if base_df.empty:
            self._log.info('── no klines yet — run backfill_synthetic ──')
            return

        # Indicator line
        ind_df  = IndicatorComputer.resample(base_df, int(cfg['ic_itf_seconds']))
        ind_src = IndicatorComputer.build_source(ind_df, cfg['ic_src'])
        bb      = IndicatorComputer.f_bb(
            ind_src, int(cfg['ic_bb_len']), float(cfg['ic_bb_mult']),
            float(cfg['ic_high_boundary']), float(cfg['ic_low_boundary']),
        )
        bb_val = float(bb[-1]) if len(bb) and not np.isnan(bb[-1]) else None

        # Gate lines
        gate_cfgs  = self._load_gate_cfgs(tc_pk)
        gate_lines = []
        gate_sides = []
        for gcfg in gate_cfgs:
            gname    = f'{gcfg["is_prefix"]}{gcfg["itf_label"]}{gcfg["il_suffix"]}'
            gate_df  = IndicatorComputer.resample(base_df, int(gcfg['ic_itf_seconds']))
            oob_raw  = IndicatorComputer.compute_oob_side(gcfg, gate_df)
            oob_aln  = IndicatorComputer.align_to_base(oob_raw, gate_df, base_df)
            gate_sides.append(oob_aln)

            # Latest value for display
            gsrc = IndicatorComputer.build_source(gate_df, gcfg['ic_src'])
            if gcfg['ic_line_type'] == 'bb':
                gvals = IndicatorComputer.f_bb(gsrc, int(gcfg['ic_bb_len']), float(gcfg['ic_bb_mult']))
            else:
                gvals = IndicatorComputer.f_k(gsrc, int(gcfg['ic_rsi_len']),
                                               int(gcfg['ic_stc_len']), int(gcfg['ic_k_len']))
            gval  = float(gvals[-1]) if len(gvals) and not np.isnan(gvals[-1]) else None
            side  = int(oob_aln[-1]) if len(oob_aln) else 0
            label = 'HI OOB' if side == 1 else ('LO OOB' if side == -1 else 'IB    ')
            gate_lines.append((gname, label, gval, gcfg['ic_line_type']))

        combined_side = int(IndicatorComputer.fold_gates(gate_sides)[-1]) if gate_sides else 0
        combined_str  = 'HI OOB' if combined_side == 1 else ('LO OOB' if combined_side == -1 else 'IB    ')

        # DEMA
        dema_src = IndicatorComputer.build_source(base_df, cfg['tc_dema_src'])
        dema     = IndicatorComputer.dema(dema_src, int(cfg['tc_dema_len']))
        dema_val = float(dema[-1]) if len(dema) and not np.isnan(dema[-1]) else None

        last_close = float(base_df['close'].iloc[-1])
        last_ts    = _ms_to_iso(int(base_df['timestamp'].iloc[-1]))

        sep = '─' * 64
        self._log.info(sep)
        self._log.info(
            f'  {last_ts}   close={last_close:.8f}'
            f'   5s bars={len(base_df)}   {int(ind_df.shape[0])} × {cfg["ic_itf_seconds"]}s bars'
        )
        self._log.info(
            f'  {ind_name:8s}  bb%b={ f"{bb_val:6.2f}" if bb_val is not None else "   --"}'
            f'   src({cfg["ic_src"]})={float(ind_src[-1]):.8f}'
        )
        for gname, label, gval, gtype in gate_lines:
            metric = 'bb%b' if gtype == 'bb' else 'k   '
            self._log.info(
                f'  {gname:8s}  {label}  {metric}={ f"{gval:6.2f}" if gval is not None else "   --"}'
            )
        self._log.info(f'  gate      {combined_str}  (combined)')
        self._log.info(
            f'  DEMA      { f"{dema_val:.8f}" if dema_val is not None else "--"}'
        )
        self._log.info(sep)

    def _load_cfg(self, tc_pk: int) -> Optional[dict]:
        rows = self._db.execute(
            '''SELECT tc.*,
                      ic.ic_line_type, ic.ic_src, ic.ic_high_boundary, ic.ic_low_boundary,
                      ic.ic_bb_len, ic.ic_bb_mult, ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix, itf.itf_label, il.il_suffix
               FROM test_configs tc
               JOIN indicator_configs    ic  ON ic.ic_pk   = tc.tc_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk    = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk   = ic.ic_il_pk
               WHERE tc.tc_pk = %s''',
            (tc_pk,), fetch=True,
        )
        return rows[0] if rows else None

    def _load_gate_cfgs(self, tc_pk: int) -> list:
        return self._db.execute(
            '''SELECT ic.*,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix, itf.itf_label, il.il_suffix
               FROM test_config_extensions tce
               JOIN indicator_configs    ic  ON ic.ic_pk      = tce.tce_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk    = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk       = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk      = ic.ic_il_pk
               WHERE tce.tce_tc_pk     = %s
                 AND tce.tce_type      = 'gate'
                 AND tce.tce_is_active = 1
               ORDER BY tce.tce_sort_order''',
            (tc_pk,), fetch=True,
        )

    def _load_klines(self, tp_pk: int) -> pd.DataFrame:
        rows = self._db.execute(
            '''SELECT kc_timestamp AS timestamp, kc_open AS open, kc_high AS high,
                      kc_low AS low, kc_close AS close, kc_volume AS volume
               FROM kline_collection WHERE kc_tp_pk = %s
               ORDER BY kc_timestamp DESC LIMIT %s''',
            (tp_pk, self._LOOKBACK), fetch=True,
        )
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame(rows).sort_values('timestamp').reset_index(drop=True)
