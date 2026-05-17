"""
StopCalibrator — see class docstring for purpose, design notes.
"""

import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from logger import get_logger

from ..db.database_manager import DatabaseManager
from ..compute.pk5s_gate_computer import Pk5sGateComputer
from ..compute.swing_analyzer import SwingAnalyzer


class StopCalibrator:
    """
    Per-line stop_pct calibration for 5s singular grinds.

    Generates baseline signals via Pk5sGateComputer with single-line
    vote_overrides — the target line carries its xlsx weights, no other
    lines participate. This mirrors the reconciler's mechanism exactly:
    same f_pk_state, same threshold + decision_delay aggregation Pine uses.

    Then sweeps stop_pct across a 12-value range, picks the value that
    maximizes net banked profit, adds tc_stop_buffer, writes back to
    tc.tc_stop_pct. Per-stop diagnostics persisted to stop_calibration.

    Round: r04_260517 (revised mid-round after Joe's "how does Pine
    handle 5s?" question — answer: vote machine via Pk5sGateComputer,
    not PKDetector. r05 captures the bigger "which machine for what
    timeframe" architectural question.)
    """

    # 12 stop values: [0.11, 0.15, 0.19, ..., 0.55]
    _STOP_RANGE_DEFAULT = (0.11, 0.55, 0.04)

    # Midpoint for f_pk_state's peak-selector switch. Same value Pine
    # uses for s5_pk computation. Hardcoded here — r05 will read from
    # indicator_configs once ob/os are promoted to per-line config.
    _MIDPOINT = 50.0

    def __init__(self, db: DatabaseManager,
                 stop_range: tuple = _STOP_RANGE_DEFAULT) -> None:
        self._db    = db
        self._pk5s  = Pk5sGateComputer(db)
        self._stops = self._build_stop_values(stop_range)
        self._log   = get_logger(self.__class__.__name__)

    def calibrate(self, tc_pk: int,
                  base_df: pd.DataFrame,
                  dema: np.ndarray,
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
            f'lookback={lookback_days:.1f}d, profit_zone={profit_zone:.2f}%, '
            f'buffer={buffer_pct:.2f}%'
        )

        signals = self._generate_signals(tc, base_df, dema)
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

        self._persist_calibration(
            tc_pk, run_ts, int(round(lookback_days)),
            results, peak['stop_pct'],
        )

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
                      ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len
               FROM test_configs tc
               JOIN indicator_configs ic ON ic.ic_pk = tc.tc_ic_pk
               WHERE tc.tc_pk = %s''',
            (tc_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No test_config for tc_pk={tc_pk}')
        return rows[0]

    def _load_baseline_pool_params(self) -> dict:
        """
        Read pool/threshold/decision params from the production pk_5s tce.
        Same source the reconciler uses (xlsx-truth in DB form).
        """
        rows = self._db.execute(
            '''SELECT tce_params FROM test_config_extensions
               WHERE tce_type = 'pk_5s' AND tce_is_active = 1
               ORDER BY tce_pk DESC LIMIT 1''',
            (), fetch=True,
        )
        if not rows:
            raise RuntimeError(
                'No active pk_5s tce found — cannot determine baseline pool params'
            )
        p = rows[0]['tce_params']
        if isinstance(p, (str, bytes)):
            p = json.loads(p)
        return p

    def _load_baseline_weights(self, ic_pk: int) -> tuple:
        """
        Read this line's xlsx weights from the production pk_5s tcev.
        Used as fixed weights for single-line vote during calibration.
        Returns (weight_close, weight_wide). Falls back to (5, 2) if no
        active row found — better to calibrate against something than
        fail outright.
        """
        rows = self._db.execute(
            '''SELECT tcev.tcev_weight_close, tcev.tcev_weight_wide
               FROM test_config_ext_votes tcev
               JOIN test_config_extensions tce ON tce.tce_pk = tcev.tcev_tce_pk
               WHERE tce.tce_type = 'pk_5s'
                 AND tce.tce_is_active = 1
                 AND tcev.tcev_ic_pk = %s
                 AND tcev.tcev_is_active = 1
               ORDER BY tce.tce_pk DESC LIMIT 1''',
            (ic_pk,), fetch=True,
        )
        if not rows:
            self._log.warning(
                f'No tcev row for ic_pk={ic_pk} — using default weights (5, 2)'
            )
            return (5, 2)
        return (
            int(rows[0]['tcev_weight_close']),
            int(rows[0]['tcev_weight_wide']),
        )

    def _generate_signals(self, tc: dict,
                          base_df: pd.DataFrame,
                          dema: np.ndarray) -> list:
        """
        Build single-line vote_overrides at this line's indicator_configs
        baseline values + xlsx weights. Call Pk5sGateComputer. Extract
        transition signals (bars where Pine s5_pk_final changes to ±1)
        as the baseline signal set.
        """
        pool_params  = self._load_baseline_pool_params()
        w_close, w_wide = self._load_baseline_weights(int(tc['tc_ic_pk']))

        target_vote = self._build_vote(tc, w_close, w_wide)
        self._log.info(
            f'Baseline vote: line_type={target_vote["ic_line_type"]}, '
            f'weights=({w_close}, {w_wide}), '
            f'pool=(c={pool_params.get("pool_c")}, w={pool_params.get("pool_w")}, '
            f'range={pool_params.get("pool_range")}, slope={pool_params.get("pool_slope")})'
        )

        oob_arr = self._pk5s.compute(
            tce_pk=f'calibrate-tc{tc["tc_pk"]}',
            base_df=base_df,
            dema=dema,
            params=pool_params,
            midpoint=self._MIDPOINT,
            vote_overrides=[target_vote],
        )
        # Pk5sGateComputer returns OOB-equivalent (sign-inverted from Pine).
        # Flip to Pine s5_pk_final convention for transition extraction.
        s5_pk_final = -oob_arr

        # Transitions: bars where signal changes from 0 (or opposite) to ±1
        prev = np.concatenate([[0], s5_pk_final[:-1]])
        transitions_idx = np.where((s5_pk_final != prev) & (s5_pk_final != 0))[0]
        return [
            {'bar_index': int(i), 'direction': int(s5_pk_final[i])}
            for i in transitions_idx
        ]

    @staticmethod
    def _build_vote(tc: dict, weight_close: int, weight_wide: int) -> dict:
        v = {
            'tcev_weight_close':  weight_close,
            'tcev_weight_wide':   weight_wide,
            'tcev_trigger_mode':  'standard_pk',
            'tcev_roc_threshold': None,
            'ic_itf_seconds':     5,
        }
        if tc['ic_line_type'] == 'bb':
            v.update({
                'ic_line_type': 'bb',
                'ic_src':       tc['ic_src'],
                'ic_bb_len':    int(tc['ic_bb_len']),
                'ic_bb_mult':   float(tc['ic_bb_mult']),
                'ic_k_len':     None,
                'ic_rsi_len':   None,
                'ic_stc_len':   None,
            })
        else:  # 'k'
            v.update({
                'ic_line_type': 'k',
                'ic_src':       tc['ic_src'],
                'ic_bb_len':    None,
                'ic_bb_mult':   None,
                'ic_k_len':     int(tc['ic_k_len']),
                'ic_rsi_len':   int(tc['ic_rsi_len']),
                'ic_stc_len':   int(tc['ic_stc_len']),
            })
        return v

    def _evaluate_stop(self, signals: list, close: np.ndarray,
                       stop_pct: float, profit_zone: float) -> dict:
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
