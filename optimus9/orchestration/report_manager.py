"""
ReportManager — see class docstring for purpose, Pine alignment, and design notes.
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
from ..compute.indicator_computer import IndicatorComputer
from ..compute.pk_detector import PKDetector
from ..compute.pk5s_gate_computer import Pk5sGateComputer
from ..compute.swing_analyzer import SwingAnalyzer
from ..compute.stop_calibrator import StopCalibrator
from ..orchestration.optimizer_runner import OptimizerRunner
from ..compute.parameter_grid_builder import ParameterGridBuilder
from ..orchestration.report_exporter import ReportExporter


class ReportManager:
    """Top-level grind coordinator. Entry point: run(tc_pk)."""

    _LOOKBACK_WEEKS = 5

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, tc_pk: int,
            export_csv: bool = True, output_dir: str = '.',
            lookback_days: int = None,
            p_rev_enabled: bool = True,
            pk5s_gate_enabled: bool = True) -> Optional[str]:
        """
        Drive a full optimizer run for a test_config.

        Round 260514 changes:
          • p_rev_enabled — when True and the calibration line's TF > 5s,
            OptimizerRunner uses f_bb_lookahead (Pine barmerge.lookahead_on
            equivalent) instead of resample-and-forward-fill. Recorded on
            the optimizer_runs row.
          • pk5s_gate_enabled — when True, active pk_5s test_config_extensions
            rows produce gate arrays via Pk5sGateComputer that fold with
            bny30M/p as a third OOB-equivalent gate. Recorded on the run.

        Both flags default True for production. Toggle for the comparison
        matrix in 260514_pk5s_spec.md.
        """
        
        config = self._load_config(tc_pk)
        self._log.info(f'Config: {config["tc_indicator_label"]}')

        or_pk = self._db.execute(
            '''INSERT INTO optimizer_runs
                 (or_tc_pk, or_tp_pk, or_timestamp, or_dema_len, or_dema_src,
                  or_p_rev_enabled, or_pk5s_gate_enabled)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            (tc_pk, int(config['tc_tp_pk']),
             int(datetime.now(timezone.utc).timestamp() * 1000),
             int(config['tc_dema_len']), config['tc_dema_src'],
             1 if p_rev_enabled else 0,
             1 if pk5s_gate_enabled else 0),
        )
        self._log.info(f'Run config: p_rev={"on" if p_rev_enabled else "off"}, '
                       f'pk5s_gate={"on" if pk5s_gate_enabled else "off"}')
        self._log.info(f'Run created: or_pk={or_pk}')

        base_df = self._load_klines(int(config['tc_tp_pk']), lookback_days)
        self._log.info(f'Base: {len(base_df)} × 5s bars')

        # DEMA on native 5s
        dema_src = IndicatorComputer.build_source(base_df, config['tc_dema_src'])
        dema     = IndicatorComputer.dema(dema_src, int(config['tc_dema_len']))

        # Gate: load active extensions, compute oob_side per gate, fold
        # Gates: bny30M/p (existing OOB gates) + optional pk_5s vote machines.
        # All gates fold via OR semantics in IndicatorComputer.fold_gates.
        gate_cfgs = self._load_gate_configs(tc_pk)
        gate_sides = []

        for gcfg in gate_cfgs:
            gate_df   = IndicatorComputer.resample(base_df, int(gcfg['ic_itf_seconds']))
            oob_raw   = IndicatorComputer.compute_oob_side(gcfg, gate_df)
            oob_align = IndicatorComputer.align_to_base(oob_raw, gate_df, base_df)
            gate_sides.append(oob_align)
            name = f'{gcfg["is_prefix"]}{gcfg["itf_label"]}{gcfg["il_suffix"]}'
            self._log.info(
                f'Gate {name}: {int((oob_align != 0).sum())} OOB bars'
                f' ({int((oob_align == 1).sum())} HI / {int((oob_align == -1).sum())} LO)'
            )

        # pk_5s gate extensions
        if pk5s_gate_enabled:
            pk5s_cfgs = self._load_pk5s_extensions(tc_pk)
            for pcfg in pk5s_cfgs:
                pk5s_arr = Pk5sGateComputer(self._db).compute(
                    int(pcfg['tce_pk']), base_df, dema, pcfg['tce_params'],
                    midpoint=(float(config['ic_high_boundary']) +
                              float(config['ic_low_boundary'])) / 2.0,
                )
                gate_sides.append(pk5s_arr.astype(float))
        else:
            self._log.info('pk_5s gate disabled by flag')

        if gate_sides:
            oob_side = IndicatorComputer.fold_gates(gate_sides)
            self._log.info(
                f'Combined gate: {int((oob_side != 0).sum())} OOB bars of {len(base_df)}'
            )
        else:
            self._log.warning('No active gates — all bars valid (no direction constraint)')
            oob_side = np.zeros(len(base_df), dtype=np.int8)

        # Indicator resampled to its TF (b6M → 5s → 360s)
        ind_seconds = int(config['ic_itf_seconds'])
        ind_df      = IndicatorComputer.resample(base_df, ind_seconds)
        self._log.info(f'Indicator: {len(ind_df)} × {ind_seconds}s bars')

        grid = ParameterGridBuilder(self._db).build(tc_pk)

        # r04: Per-line stop_pct calibration before the grind.
        # 5s-native targets only — b6m calibration requires resample/align
        # the calibrator doesn't currently do (future round).
        # Skipped silently if tc_dynamic_stoploss is FALSE or absent.
        if config.get('tc_dynamic_stoploss') and int(config['ic_itf_seconds']) == 5:
            self._log.info('Stop calibration enabled (5s target) — running before grid grind')
            cal_lookback = (
                float(lookback_days) if lookback_days is not None
                else (base_df['timestamp'].iloc[-1] - base_df['timestamp'].iloc[0]) / 86_400_000.0
            )
            StopCalibrator(
                self._db,
                PKDetector(float(config['ic_high_boundary']),
                           float(config['ic_low_boundary'])),
            ).calibrate(tc_pk, base_df, dema, oob_side, cal_lookback)
            # Reload — calibrator just updated tc.tc_stop_pct
            config = self._load_config(tc_pk)

        OptimizerRunner(
            self._db,
            PKDetector(float(config['ic_high_boundary']), float(config['ic_low_boundary'])),
            # r04: SwingAnalyzer dropped drag_pct — classification moved to AnalyzeManager
            SwingAnalyzer(float(config['tc_stop_pct']), int(config['tc_max_bars'])),
        ).run(or_pk, base_df, ind_df, dema, oob_side, grid, config,
              p_rev_enabled=p_rev_enabled)
        
        # Stamp completion. Rows with NULL or_completed_at = aborted /
        # in-progress; compare's warnings block surfaces this so partial
        # results don't quietly contaminate side-by-side analysis.
        self._db.execute(
            'UPDATE optimizer_runs SET or_completed_at = NOW() WHERE or_pk = %s',
            (or_pk,),
        )

        return ReportExporter(self._db).export(or_pk, output_dir) if export_csv else None

    def _load_config(self, tc_pk: int) -> dict:
        """Load test_config joined with its calibration indicator_config."""
        rows = self._db.execute(
            '''SELECT tc.*,
                      ic.ic_line_type, ic.ic_src, ic.ic_high_boundary, ic.ic_low_boundary,
                      ic.ic_bb_len, ic.ic_bb_mult, ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len,
                      itf.itf_seconds  AS ic_itf_seconds,
                      s.is_prefix,
                      itf.itf_label,
                      il.il_suffix
               FROM test_configs tc
               JOIN indicator_configs    ic  ON ic.ic_pk      = tc.tc_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk    = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk       = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk      = ic.ic_il_pk
               WHERE tc.tc_pk = %s''',
            (tc_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No test_config for tc_pk={tc_pk}')
        return rows[0]

    def _load_gate_configs(self, tc_pk: int) -> list:
        """Load active gate extension configs, ordered by sort_order."""
        return self._db.execute(
            '''SELECT ic.*,
                      itf.itf_seconds AS ic_itf_seconds,
                      s.is_prefix,
                      itf.itf_label,
                      il.il_suffix
               FROM test_config_extensions tce
               JOIN indicator_configs    ic  ON ic.ic_pk      = tce.tce_ic_pk
               JOIN indicator_timeframes itf ON itf.itf_pk    = ic.ic_itf_pk
               JOIN indicator_series     s   ON s.is_pk       = ic.ic_is_pk
               JOIN indicator_lines      il  ON il.il_pk      = ic.ic_il_pk
               WHERE tce.tce_tc_pk    = %s
                 AND tce.tce_type     = 'gate'
                 AND tce.tce_is_active = 1
               ORDER BY tce.tce_sort_order''',
            (tc_pk,), fetch=True,
        )
    
    def _load_pk5s_extensions(self, tc_pk: int) -> list:
        """
        Active pk_5s tce rows for this test_config, with tce_params parsed
        from JSON. Each row has a tce_pk and a tce_params dict ready to feed
        into Pk5sGateComputer.compute(...).

        Returns [] if no active pk_5s extensions exist (gate folding falls
        back to bny30M/p only — the existing OOB-gate-only behaviour).
        """
        rows = self._db.execute(
            '''SELECT tce_pk, tce_params
               FROM test_config_extensions
               WHERE tce_tc_pk     = %s
                 AND tce_type      = 'pk_5s'
                 AND tce_is_active = 1
               ORDER BY tce_sort_order''',
            (tc_pk,), fetch=True,
        )
        # JSON column comes back as str on most pymysql configs; parse if so.
        for r in rows:
            if isinstance(r['tce_params'], (str, bytes)):
                r['tce_params'] = json.loads(r['tce_params'])
        return rows
        
        
    def _load_klines(self, tp_pk: int, lookback_days: int = None) -> pd.DataFrame:
        if lookback_days:
            cutoff = int((datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp() * 1000)
            where, params = 'kc_tp_pk = %s AND kc_timestamp >= %s', (tp_pk, cutoff)
        else:
            where, params = 'kc_tp_pk = %s', (tp_pk,)
        rows = self._db.execute(
            f'''SELECT kc_timestamp AS timestamp, kc_open AS open, kc_high AS high,
                       kc_low AS low, kc_close AS close, kc_volume AS volume
                FROM kline_collection WHERE {where} ORDER BY kc_timestamp ASC''',
            params, fetch=True,
        )
        if not rows:
            raise RuntimeError(f'No klines for tp_pk={tp_pk}')
        return pd.DataFrame(rows)
