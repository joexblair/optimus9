"""
OptimizerRunner — see class docstring for purpose, Pine alignment, and design notes.
"""


"""
managers.py — PK Optimizer
All process classes. One responsibility per class.
Every class calls get_logger(self.__class__.__name__).

Terminology:
  OOB  = out of boundary (indicator has crossed high/low threshold)
  IB   = in boundary (indicator is within thresholds)
  OS/OB reserved for RSI/K oscillator context only.
"""

import json
import math

import numpy as np
import pandas as pd

from logger import get_logger

from ..db.database_manager import DatabaseManager
from ..compute.pk_signal_detector import PKSignalDetector
from ..compute.pk5s_gate_computer import Pk5sGateComputer
from ..compute.swing_analyzer import SwingAnalyzer
from ..compute.indicator_computer import IndicatorComputer


class OptimizerRunner:
    """
    Drives the parameter grid. Two execution paths:

      Self-gated (5s singular grind):
        No external gate. Builds single-line vote_overrides per combo and
        calls Pk5sGateComputer to produce a Pine-equivalent s5_pk_final
        signal. Transitions to ±1 become signals. Same machinery the
        reconciler uses, just with one voter (target line carries xlsx
        weights, others absent). True Pine mimic.

      Gated (b6m grind, r05 6-line grinds under bny30):
        External gate (bny30M/p) provides oob_side. Builds the calibration
        line per combo, calls PKSignalDetector to find PK transitions within the
        OOB region. K-line support added r04 (line via f_k); detect()
        now also accepts line_type so K-line params (len_rsi/len_stoch)
        emit correctly without expecting 'mult'.

    r04: K-line support added on the gated path (line via f_k instead of
    f_bb when ic_line_type='k'). Self-gated path supports K too via
    vote_overrides shape — Pk5sGateComputer already handles both line types.

    Mode selection is automatic: oob_side all-zeros → self-gated, otherwise
    gated. ReportManager's gate-folding logic produces all-zeros when there
    are no active gate extensions.

    r05: parked — should b6m converge on Pk5sGateComputer too? Or are
    they fundamentally different mechanisms suited to different timeframes?
    """

    _MIDPOINT = 50.0  # Pine f_pk_state midpoint switch

    def __init__(self, db: DatabaseManager, detector: PKSignalDetector,
                 analyzer: SwingAnalyzer) -> None:
        self._db       = db
        self._detector = detector
        self._analyzer = analyzer
        self._pk5s     = Pk5sGateComputer(db)
        self._log      = get_logger(self.__class__.__name__)

    def run(self, or_pk: int,
            base_df:  pd.DataFrame,
            ind_df:   pd.DataFrame,
            dema:     np.ndarray,
            oob_side: np.ndarray,
            param_grid: list,
            config: dict,
            p_rev_enabled: bool = False) -> None:

        is_self_gated = not oob_side.any()

        if is_self_gated:
            self._log.info(
                'Self-gated mode — Pk5sGateComputer with single-line vote_overrides per combo'
            )
            self._run_self_gated(or_pk, base_df, dema, param_grid, config)
        else:
            self._run_gated(
                or_pk, base_df, ind_df, dema, oob_side,
                param_grid, config, p_rev_enabled,
            )

    # ── Self-gated path (5s singular grind) ──────────────────────────────────

    def _run_self_gated(self, or_pk: int,
                        base_df: pd.DataFrame,
                        dema: np.ndarray,
                        param_grid: list,
                        config: dict) -> None:
        close      = base_df['close'].to_numpy(dtype=float)
        timestamps = base_df['timestamp'].to_numpy()
        line_type  = config.get('ic_line_type', 'bb')
        total      = len(param_grid)

        # Load fixed pool/threshold/decision params from production pk_5s tce.
        # These are the xlsx-truth values not swept this round (threshold,
        # decision_delay, pm_suppression). Pool dimensions (c/w/range/slope)
        # come from the combo dict.
        tce_params = self._load_tce_params()

        for idx, params in enumerate(param_grid, 1):
            self._log.info(f'[{idx}/{total}]')

            target_vote = self._build_target_vote(line_type, params)
            pool_params = self._build_pool_params(params, tce_params)

            oob_arr = self._pk5s.compute(
                tce_pk=f'grind-or{or_pk}-{idx}',
                base_df=base_df,
                dema=dema,
                params=pool_params,
                midpoint=self._MIDPOINT,
                vote_overrides=[target_vote],
            )
            s5_pk_final = -oob_arr  # invert to Pine convention

            signals = self._extract_transitions(s5_pk_final)
            outcomes = self._analyzer.analyze(signals, close)
            self._persist_self_gated(or_pk, timestamps, outcomes, params, line_type)

    @staticmethod
    def _build_target_vote(line_type: str, params: dict) -> dict:
        v = {
            'tcev_weight_close':  int(params['tcev_weight_close']),
            'tcev_weight_wide':   int(params['tcev_weight_wide']),
            'tcev_trigger_mode':  'standard_pk',
            'tcev_roc_threshold': None,
            'ic_itf_seconds':     5,
        }
        if line_type == 'bb':
            v.update({
                'ic_line_type': 'bb',
                'ic_src':       params['src'],
                'ic_bb_len':    int(params['len']),
                'ic_bb_mult':   float(params['mult']),
                'ic_k_len':     None,
                'ic_rsi_len':   None,
                'ic_stc_len':   None,
            })
        else:  # 'k'
            v.update({
                'ic_line_type': 'k',
                'ic_src':       params['src'],
                'ic_bb_len':    None,
                'ic_bb_mult':   None,
                'ic_k_len':     int(params['len']),
                'ic_rsi_len':   int(params['len_rsi']),
                'ic_stc_len':   int(params['len_stoch']),
            })
        return v

    @staticmethod
    def _build_pool_params(params: dict, tce_params: dict) -> dict:
        return {
            # Swept dimensions from the grid
            'pool_c':          int(params['pool_c']),
            'pool_w':          int(params['pool_w']),
            'pool_range':      int(params['pool_range']),
            'pool_slope':      float(params['slope_floor']),
            'multiplier':      int(params['multiplier']),
            # r07 Step 4: pm_additive — swept from the grid, fixed via tce, or 0.0.
            'pm_additive':     float(params.get('pm_additive',
                                                tce_params.get('pm_additive', 0.0))),
            # Fixed xlsx-truth values (not swept this round)
            'threshold_long':  tce_params.get('threshold_long',  7.5),
            'threshold_short': tce_params.get('threshold_short', 7.5),
            'pm_suppression':  tce_params.get('pm_suppression',  0.5),
        }

    def _load_tce_params(self) -> dict:
        rows = self._db.execute(
            '''SELECT tce_params FROM test_config_extensions
               WHERE tce_type = 'pk_5s' AND tce_is_active = 1
               ORDER BY tce_pk DESC LIMIT 1''',
            (), fetch=True,
        )
        if not rows:
            raise RuntimeError('No active pk_5s tce — cannot load fixed params')
        p = rows[0]['tce_params']
        if isinstance(p, (str, bytes)):
            p = json.loads(p)
        return p

    @staticmethod
    def _extract_transitions(s5_pk_final: np.ndarray) -> list:
        """
        Bars where signal changes from 0 (or opposite) to ±1. Each
        transition becomes a signal entry with bar_index + direction.
        """
        prev = np.concatenate([[0], s5_pk_final[:-1]])
        idx  = np.where((s5_pk_final != prev) & (s5_pk_final != 0))[0]
        return [
            {'bar_index': int(i), 'direction': int(s5_pk_final[i])}
            for i in idx
        ]

    def _persist_self_gated(self, or_pk: int, timestamps: np.ndarray,
                            outcomes: list, params: dict,
                            line_type: str) -> None:
        if not outcomes:
            return

        dv = self._db_val
        sig_sql = '''INSERT INTO pk_signals
            (pks_or_pk, pks_timestamp, pks_dir, pks_state, pks_line_value,
             pks_slope, pks_slope_diff, pks_dema_slope, pks_dema_value, pks_pool,
             pks_len, pks_mult, pks_src,
             pks_len_rsi, pks_len_stoch,
             pks_pool_c, pks_pool_w, pks_pool_range,
             pks_slope_floor, pks_multiplier)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

        out_sql = '''INSERT INTO pk_outcomes
            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit,
             pko_max_adverse_pct, pko_bars_to_max_adverse)
            VALUES (%s,%s,%s,%s,%s,%s)'''

        # Column distribution: BB has mult populated, K-only cols NULL.
        # K has len_rsi/len_stoch populated, mult NULL.
        pks_mult      = float(params['mult'])      if line_type == 'bb' else None
        pks_len_rsi   = int(params['len_rsi'])     if line_type == 'k'  else None
        pks_len_stoch = int(params['len_stoch'])   if line_type == 'k'  else None

        sig_rows = []
        for o in outcomes:
            sig_rows.append((
                or_pk, int(timestamps[o['bar_index']]),
                o['direction'],
                # pks_state NOT NULL — set to Pine PM convention sentinel
                float(o['direction']) * 2.0,
                # Per-bar internals not exposed by Pk5sGateComputer — NULL
                None, None, None, None, None,
                # pks_pool ENUM NOT NULL — placeholder (meaningless for vote-machine
                # rows, which aggregate close+wide pools internally)
                'close',
                int(params['len']), pks_mult, params['src'],
                pks_len_rsi, pks_len_stoch,
                int(params['pool_c']), int(params['pool_w']),
                int(params['pool_range']),
                float(params['slope_floor']),
                int(params['multiplier']),
            ))

        first_id = self._db.executemany(sig_sql, sig_rows)

        self._db.executemany(out_sql, [
            (first_id + i,
             dv(o['max_profit_pct']),
             o['bars_to_stop'],
             o['bars_to_max_profit'],
             dv(o.get('max_adverse_pct')),
             o.get('bars_to_max_adverse'))
            for i, o in enumerate(outcomes)
        ])

    # ── Gated path (b6m grind — existing PKDetector flow) ────────────────────

    def _run_gated(self, or_pk: int,
                   base_df: pd.DataFrame,
                   ind_df: pd.DataFrame,
                   dema: np.ndarray,
                   oob_side: np.ndarray,
                   param_grid: list,
                   config: dict,
                   p_rev_enabled: bool) -> None:
        close       = base_df['close'].to_numpy(dtype=float)
        total       = len(param_grid)
        ind_seconds = int(config['ic_itf_seconds'])
        line_type   = config.get('ic_line_type', 'bb')
        self._log.info(f'Gated mode — PKSignalDetector ({line_type} line) with externally-folded oob_side')
        
        use_lookahead = bool(p_rev_enabled and ind_seconds > 5 and line_type == 'bb')
        if use_lookahead:
            self._log.info(
                f'p_rev active: indicator line via f_bb_lookahead (TF={ind_seconds}s)'
            )
        elif line_type == 'k':
            self._log.info(f'K-line target — using f_k path (TF={ind_seconds}s)')

        for idx, params in enumerate(param_grid, 1):
            self._log.info(f'[{idx}/{total}]')

            line = self._build_line(
                base_df, ind_df, line_type, ind_seconds,
                use_lookahead, params, config,
            )
            signals = self._detector.detect(
                line, dema,
                int(params['pool_c']), int(params['pool_w']),
                int(params['pool_range']), int(params['multiplier']),
                float(params['slope_floor']), oob_side, params,
                line_type=line_type,
            )
            outcomes = self._analyzer.analyze(signals, close)
            self._persist_gated(or_pk, base_df['timestamp'].to_numpy(), outcomes, line_type)

    @staticmethod
    def _build_line(base_df: pd.DataFrame, ind_df: pd.DataFrame,
                    line_type: str, ind_seconds: int,
                    use_lookahead: bool, params: dict, config: dict) -> np.ndarray:
        if line_type == 'k':
            src_series = IndicatorComputer.build_source(ind_df, params['src'])
            line_raw   = IndicatorComputer.f_k(
                src_series,
                int(params['len_rsi']),
                int(params['len_stoch']),
                int(params['len']),
            )
            if ind_seconds == 5:
                return np.asarray(line_raw, dtype=float)
            return IndicatorComputer.align_to_base(line_raw, ind_df, base_df)

        if use_lookahead:
            return IndicatorComputer.f_bb_lookahead(
                base_df, ind_seconds,
                int(params['len']), float(params['mult']), params['src'],
                float(config['ic_high_boundary']),
                float(config['ic_low_boundary']),
            )

        src_series = IndicatorComputer.build_source(ind_df, params['src'])
        line_raw   = IndicatorComputer.f_bb(
            src_series, int(params['len']), float(params['mult']),
        )
        if ind_seconds == 5:
            return np.asarray(line_raw, dtype=float)
        return IndicatorComputer.align_to_base(line_raw, ind_df, base_df)

    def _persist_gated(self, or_pk: int, timestamps: np.ndarray,
                       outcomes: list, line_type: str) -> None:
        if not outcomes:
            return

        dv = self._db_val
        sig_sql = '''INSERT INTO pk_signals
            (pks_or_pk, pks_timestamp, pks_dir, pks_state, pks_line_value,
             pks_slope, pks_slope_diff, pks_dema_slope, pks_dema_value, pks_pool,
             pks_len, pks_mult, pks_src,
             pks_len_rsi, pks_len_stoch,
             pks_pool_c, pks_pool_w, pks_pool_range,
             pks_slope_floor, pks_multiplier)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''

        out_sql = '''INSERT INTO pk_outcomes
            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit,
             pko_max_adverse_pct, pko_bars_to_max_adverse)
            VALUES (%s,%s,%s,%s,%s,%s)'''

        sig_rows = []
        for o in outcomes:
            if line_type == 'k':
                pks_mult      = None
                pks_len_rsi   = int(o['len_rsi'])
                pks_len_stoch = int(o['len_stoch'])
            else:
                pks_mult      = o['mult']
                pks_len_rsi   = None
                pks_len_stoch = None

            sig_rows.append((
                or_pk, int(timestamps[o['bar_index']]),
                o['direction'], dv(o['pk_state']), dv(o['line_value']),
                dv(o['slope']), dv(o['slope_diff']), dv(o['dema_slope']),
                dv(o['dema_value']), o['pool'],
                int(o['len']), pks_mult, o['src'],
                pks_len_rsi, pks_len_stoch,
                int(o['pool_c']), int(o['pool_w']), int(o['pool_range']),
                float(o['slope_floor']), int(o['multiplier']),
            ))

        first_id = self._db.executemany(sig_sql, sig_rows)

        self._db.executemany(out_sql, [
            (first_id + i,
             dv(o['max_profit_pct']),
             o['bars_to_stop'],
             o['bars_to_max_profit'],
             dv(o.get('max_adverse_pct')),
             o.get('bars_to_max_adverse'))
            for i, o in enumerate(outcomes)
        ])

    # ── shared helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _db_val(v):
        """NaN/inf → None so MySQL gets NULL rather than a literal string."""
        if isinstance(v, float) and not math.isfinite(v):
            return None
        return v
