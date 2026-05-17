"""
StopCalibrator — see class docstring for purpose, design notes.
"""

import time
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from logger import get_logger

from ..db.database_manager import DatabaseManager
from ..compute.pk_detector import PKDetector
from ..compute.swing_analyzer import SwingAnalyzer
from ..compute.indicator_computer import IndicatorComputer


class StopCalibrator:
    """
    Per-line stop_pct calibration. Generates PK signals via PKDetector on
    the target line alone (using indicator_configs baseline values), sweeps
    stop_pct across a 12-value range, picks the value that maximizes net
    banked profit, adds tc_stop_buffer, writes back to tc.tc_stop_pct.

    The "what counts as a win" threshold is tc.tc_profit_zone. A signal is
    qualifying when its max_profit_pct >= tc_profit_zone, regardless of
    whether the stop was hit.

    Per-stop diagnostics are persisted to stop_calibration so calibration
    drift over time can be queried (e.g., "is gcs5m's optimal stop stable
    or wandering?").

    Round: r04_260517 5s singular grind
    """

    # 12 stop values: [0.11, 0.15, 0.19, ..., 0.55]
    _STOP_RANGE_DEFAULT = (0.11, 0.55, 0.04)

    def __init__(self, db: DatabaseManager,
                 detector: PKDetector,
                 stop_range: tuple = _STOP_RANGE_DEFAULT) -> None:
        self._db       = db
        self._detector = detector
        self._stops    = self._build_stop_values(stop_range)
        self._log      = get_logger(self.__class__.__name__)

    def calibrate(self, tc_pk: int,
                  base_df: pd.DataFrame,
                  dema: np.ndarray,
                  oob_side: np.ndarray,
                  lookback_days: float) -> float:
        """
        Sweep stop_pct, find best by net_banked, write to tc.tc_stop_pct.
        Returns the calibrated stop_pct value.
        """
        tc = self._load_tc(tc_pk)
        profit_zone = float(tc['tc_profit_zone'])
        buffer_pct  = float(tc['tc_stop_buffer'])

        self._log.info('═' * 72)
        self._log.info(
            f'Calibrating tc_pk={tc_pk} ({tc["tc_indicator_label"]}) — '
            f'lookback={lookback_days}d, profit_zone={profit_zone:.2f}%, '
            f'buffer={buffer_pct:.2f}%'
        )

        signals = self._generate_signals(tc, base_df, dema, oob_side)
        if not signals:
            self._log.warning(
                'No signals generated at baseline — cannot calibrate. '
                'Leaving tc_stop_pct unchanged.'
            )
            return float(tc['tc_stop_pct'])

        self._log.info(
            f'Generated {len(signals)} baseline signals. '
            f'Sweeping {len(self._stops)} stop values...'
        )

        close   = base_df['close'].to_numpy(dtype=float)
        run_ts  = int(datetime.now(timezone.utc).timestamp() * 1000)
        results = []

        # Header row for console table
        self._log.info(
            f'  {"stop":>5}  {"signals":>7}  {"qual":>5}  {"lost":>5}  '
            f'{"inc%":>5}  {"gross_p":>8}  {"gross_l":>8}  {"net":>8}'
        )

        for stop_pct in self._stops:
            row = self._evaluate_stop(signals, close, stop_pct, profit_zone)
            results.append(row)
            self._log.info(
                f'  {stop_pct:>5.2f}  {row["signals"]:>7}  '
                f'{row["qualifying"]:>5}  {row["lost"]:>5}  '
                f'{(row["inconclusive"]/max(row["signals"],1))*100:>5.1f}  '
                f'{row["gross_profit"]:>+8.2f}  {row["gross_loss"]:>+8.2f}  '
                f'{row["net_banked"]:>+8.2f}'
            )

        # Pick stop_pct that maximizes net_banked; on tie, prefer smaller stop
        results.sort(key=lambda r: (-r['net_banked'], r['stop_pct']))
        peak = results[0]
        chosen = round(peak['stop_pct'] + buffer_pct, 4)

        self._log.info(
            f'Peak net_banked = {peak["net_banked"]:+.2f}% at stop={peak["stop_pct"]:.2f}%. '
            f'Chosen stop_pct = {chosen:.2f}% (peak + buffer {buffer_pct:.2f}%)'
        )

        # Persist all rows; mark peak as chosen
        self._persist_calibration(
            tc_pk, run_ts, int(round(lookback_days)),
            results, peak['stop_pct'],
        )

        # Write chosen back to tc
        self._db.execute(
            'UPDATE test_configs SET tc_stop_pct = %s WHERE tc_pk = %s',
            (chosen, tc_pk),
        )
        self._log.info(f'Updated test_configs.tc_stop_pct = {chosen:.4f}')
        self._log.info('═' * 72)

        return chosen

    # ── private ─────────────────────────────────────────────────────────────

    @staticmethod
    def _build_stop_values(stop_range: tuple) -> list:
        start, end, step = stop_range
        n = int(round((end - start) / step)) + 1
        return [round(start + i * step, 4) for i in range(n)]

    def _load_tc(self, tc_pk: int) -> dict:
        rows = self._db.execute(
            '''SELECT tc.*, ic.ic_line_type, ic.ic_src,
                      ic.ic_bb_len, ic.ic_bb_mult,
                      ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len,
                      ic.ic_high_boundary, ic.ic_low_boundary
               FROM test_configs tc
               JOIN indicator_configs ic ON ic.ic_pk = tc.tc_ic_pk
               WHERE tc.tc_pk = %s''',
            (tc_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No test_config for tc_pk={tc_pk}')
        return rows[0]

    def _generate_signals(self, tc: dict,
                          base_df: pd.DataFrame,
                          dema: np.ndarray,
                          oob_side: np.ndarray) -> list:
        """
        Build the line at indicator_configs baseline values, run PKDetector,
        return raw signals. No grid sweep — just THIS line at ITS baseline.
        """
        line = self._build_line(tc, base_df)

        # Use Pine's documented default pool params for the calibration pass.
        # The grind that follows will sweep these — calibration here is just
        # "what stop fits this line's baseline signal characteristic."
        baseline_params = {
            'len':         int(tc.get('ic_bb_len') or tc.get('ic_k_len') or 0),
            'mult':        float(tc.get('ic_bb_mult') or 0),
            'src':         tc['ic_src'],
            'pool_c':      30,
            'pool_w':      70,
            'pool_range':  4,
            'slope_floor': 5.0,
            'multiplier':  1,
        }
        signals = self._detector.detect(
            line, dema,
            baseline_params['pool_c'], baseline_params['pool_w'],
            baseline_params['pool_range'], baseline_params['multiplier'],
            baseline_params['slope_floor'], oob_side, baseline_params,
        )
        return signals

    @staticmethod
    def _build_line(tc: dict, base_df: pd.DataFrame) -> np.ndarray:
        """
        Compute the indicator line at indicator_configs baseline values.
        BB or K based on ic_line_type.
        """
        src = IndicatorComputer.build_source(base_df, tc['ic_src'])
        if tc['ic_line_type'] == 'bb':
            line = IndicatorComputer.f_bb(
                src, int(tc['ic_bb_len']), float(tc['ic_bb_mult']),
            )
        else:  # 'k'
            line = IndicatorComputer.f_k(
                src,
                int(tc['ic_rsi_len']),
                int(tc['ic_stc_len']),
                int(tc['ic_k_len']),
            )
        return line

    def _evaluate_stop(self, signals: list, close: np.ndarray,
                       stop_pct: float, profit_zone: float) -> dict:
        """
        Run SwingAnalyzer at this stop_pct; compute per-stop aggregates
        against the profit_zone threshold.
        """
        analyzer = SwingAnalyzer(stop_pct=stop_pct)
        outcomes = analyzer.analyze(signals, close)

        signals_n     = len(outcomes)
        qualifying    = sum(1 for o in outcomes if o['max_profit_pct'] >= profit_zone)
        inconclusive  = sum(1 for o in outcomes if o['bars_to_stop'] is None)
        lost          = sum(
            1 for o in outcomes
            if o['bars_to_stop'] is not None and o['max_profit_pct'] < profit_zone
        )
        gross_profit  = sum(o['max_profit_pct'] for o in outcomes
                            if o['max_profit_pct'] >= profit_zone)
        gross_loss    = stop_pct * lost
        net_banked    = gross_profit - gross_loss

        return {
            'stop_pct':     stop_pct,
            'signals':      signals_n,
            'qualifying':   qualifying,
            'lost':         lost,
            'inconclusive': inconclusive,
            'gross_profit': round(gross_profit, 4),
            'gross_loss':   round(gross_loss, 4),
            'net_banked':   round(net_banked, 4),
        }

    def _persist_calibration(self, tc_pk: int, run_ts: int,
                             lookback_days: int, results: list,
                             chosen_stop: float) -> None:
        sql = '''INSERT INTO stop_calibration
            (sc_tc_pk, sc_run_ts, sc_lookback_days, sc_stop_pct,
             sc_signals, sc_qualifying, sc_lost, sc_inconclusive,
             sc_gross_profit, sc_gross_loss, sc_net_banked, sc_is_chosen)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
        rows = [
            (tc_pk, run_ts, lookback_days, r['stop_pct'],
             r['signals'], r['qualifying'], r['lost'], r['inconclusive'],
             r['gross_profit'], r['gross_loss'], r['net_banked'],
             1 if abs(r['stop_pct'] - chosen_stop) < 1e-9 else 0)
            for r in results
        ]
        self._db.executemany(sql, rows)
