"""
Reconciler — 5s pk signal verification against Pine TradingView output.

Calls Pk5sGateComputer with xlsx-sourced config (overriding the DB-driven
default) and prints timestamps where s5_pk_final fires. Output matches
the green/red bgcolor markers TradingView paints on Pine's
S5_PK_FINAL_ONLY indicator.

Short-term reconciliation tool. When the Optimus9 trading bot supersedes
the TV Pine strategy, delete this file, remove `cmd_reconcile` and the
'reconcile' wiring from run.py, and remove the vote_overrides parameter
from Pk5sGateComputer.compute().

Round: r03_260516 reconciliation sub-round
Source of truth for parameters: 2605145s_pk_config.xlsx (260514) +
TV input overrides confirmed 260516.
"""

from datetime import datetime, timezone

import numpy as np
import pandas as pd

from logger import get_logger

from ..db.database_manager import DatabaseManager
from ..compute.pk5s_gate_computer import Pk5sGateComputer
from ..compute.indicator_computer import IndicatorComputer
from .._helpers import _ms_to_iso


# ─── Parameters ────────────────────────────────────────────────────────────
# Source: 2605145s_pk_config.xlsx (260514) + TV input panel overrides.
# Edit when Joe changes TV inputs; this is the only source of truth for
# the reconciler.

_OB = 70.0
_OS = 30.0

_DEMA_SRC = 'close'      # TV override; Pine default was hlcc4
_DEMA_LEN = 2

_POOL_PARAMS = {
    'pool_c':          30,
    'pool_w':          70,
    'pool_slope':      5.0,
    'pool_range':      4,
    'threshold_long':  7.5,     # TV override; Pine default was 7.0
    'threshold_short': 7.5,     # TV override; Pine default was 7.0
    'pm_suppression':  0.5,
    'decision_delay':  1,       # TV override; Pine default was 3
}

# (xlsx_name, type, params, weight_close, weight_wide)
#   type 'bb' params: dict(src, bb_len, bb_mult)
#   type 'k'  params: dict(src, k_len, rsi_len, stc_len)
#   type None: disabled (weights zero anyway, kept for documentation)
_LINES = [
    ('gcs5m', 'bb', dict(src='hlcc4', bb_len=12, bb_mult=0.74),       5, 2),
    ('gcs5r', 'k',  dict(src='hl2',   k_len=6, rsi_len=40, stc_len=96), 0, 0),
    ('gcs5b', None, None,                                              0, 0),
    ('gcb5M', 'bb', dict(src='hl2',   bb_len=40, bb_mult=1.0),        1, 2),
    ('gcb5p', 'k',  dict(src='hlc3',  k_len=5, rsi_len=38, stc_len=29), 0, 4),
    ('gca5o', 'k',  dict(src='ohlc4', k_len=4, rsi_len=9,  stc_len=50), 2, 2),
    ('gca5m', 'bb', dict(src='close', bb_len=6, bb_mult=0.74),         0, 6),
    ('gca5M', None, None,                                              0, 0),
]


class Reconciler:
    """
    See module docstring. Single-purpose, short-lived reconciliation tool.

    Public:
      reconcile(tp_pk, end_date, hours, output_dir) -> csv_path
    """

    _DIV = '═' * 72

    def __init__(self, db: DatabaseManager) -> None:
        self._db   = db
        self._pk5s = Pk5sGateComputer(db)
        self._log  = get_logger(self.__class__.__name__)

    # ── public ──────────────────────────────────────────────────────────────
    def reconcile(self, tp_pk: int, end_date, hours: float,
                  output_dir: str = '.') -> str:
        end_ms   = self._parse_end_date(end_date)
        start_ms = end_ms - int(hours * 3600 * 1000)
        end_iso  = _ms_to_iso(end_ms)

        self._log.info(self._DIV)
        self._log.info(f'Reconciling tp_pk={tp_pk} — last {hours}h ending {end_iso}')
        self._log.info(self._DIV)

        df = self._load_klines(tp_pk, start_ms, end_ms)
        if df.empty:
            self._log.error(f'No klines for tp_pk={tp_pk} in window')
            return ''
        self._log.info(f'{len(df)} 5s bars loaded')

        dema = self._compute_dema(df, _DEMA_SRC, _DEMA_LEN)

        all_votes = self._build_votes()
        active = [v for v in all_votes
                  if v['tcev_weight_close'] > 0 or v['tcev_weight_wide'] > 0]
        self._log.info(
            f'{len(active)}/{len(all_votes)} vote lines active (xlsx weights)'
        )

        # OOB-equivalent signal — Pk5sGateComputer returns sign-inverted from Pine
        oob_signal = self._pk5s.compute(
            tce_pk='reconciler-xlsx-260514',
            base_df=df,
            dema=dema,
            params=_POOL_PARAMS,
            vote_overrides=active,
        )
        s5_pk_final = -oob_signal

        transitions = self._extract_transitions(df, s5_pk_final)
        self._log.info(f'{len(transitions)} signal transitions found')

        self._print_transitions(transitions)
        csv_path = self._write_csv(transitions, end_ms, hours, output_dir)
        self._log.info(f'CSV: {csv_path}')
        self._log.info(self._DIV)
        return csv_path

    # ── private ─────────────────────────────────────────────────────────────
    @staticmethod
    def _parse_end_date(end_date) -> int:
        if end_date is None:
            return int(datetime.now(timezone.utc).timestamp() * 1000)
        dt = datetime.strptime(end_date, '%Y-%m-%d').replace(
            hour=23, minute=59, second=59, tzinfo=timezone.utc,
        )
        return int(dt.timestamp() * 1000)

    def _load_klines(self, tp_pk: int, start_ms: int, end_ms: int) -> pd.DataFrame:
        rows = self._db.execute(
            '''SELECT kc_timestamp AS timestamp,
                      kc_open      AS open,
                      kc_high      AS high,
                      kc_low       AS low,
                      kc_close     AS close,
                      kc_volume    AS volume
               FROM kline_collection
               WHERE kc_tp_pk = %s
                 AND kc_timestamp >= %s
                 AND kc_timestamp <= %s
               ORDER BY kc_timestamp ASC''',
            (tp_pk, start_ms, end_ms), fetch=True,
        )
        if not rows:
            return pd.DataFrame()
        df = pd.DataFrame(rows)
        for col in ('open', 'high', 'low', 'close', 'volume'):
            df[col] = df[col].astype(float)
        return df

    @staticmethod
    def _compute_dema(df: pd.DataFrame, src: str, length: int) -> np.ndarray:
        src_series = pd.Series(IndicatorComputer.build_source(df, src))
        ema1 = src_series.ewm(span=length, adjust=False).mean()
        ema2 = ema1.ewm(span=length, adjust=False).mean()
        return (2 * ema1 - ema2).to_numpy()

    @staticmethod
    def _build_votes() -> list:
        votes = []
        for (_, line_type, params, weight_c, weight_w) in _LINES:
            v = {
                'tcev_weight_close':  weight_c,
                'tcev_weight_wide':   weight_w,
                'tcev_trigger_mode':  'standard_pk',
                'tcev_roc_threshold': None,
                'ic_itf_seconds':     5,
            }
            if line_type == 'bb':
                v.update({
                    'ic_line_type': 'bb',
                    'ic_src':       params['src'],
                    'ic_bb_len':    params['bb_len'],
                    'ic_bb_mult':   params['bb_mult'],
                    'ic_k_len':     None,
                    'ic_rsi_len':   None,
                    'ic_stc_len':   None,
                })
            elif line_type == 'k':
                v.update({
                    'ic_line_type': 'k',
                    'ic_src':       params['src'],
                    'ic_bb_len':    None,
                    'ic_bb_mult':   None,
                    'ic_k_len':     params['k_len'],
                    'ic_rsi_len':   params['rsi_len'],
                    'ic_stc_len':   params['stc_len'],
                })
            else:
                v.update({
                    'ic_line_type': 'bb',
                    'ic_src':       'close',
                    'ic_bb_len':    1, 'ic_bb_mult': 1.0,
                    'ic_k_len':     None, 'ic_rsi_len': None, 'ic_stc_len': None,
                })
            votes.append(v)
        return votes

    @staticmethod
    def _extract_transitions(df: pd.DataFrame, signal: np.ndarray) -> list:
        timestamps = df['timestamp'].to_numpy()
        prev = np.concatenate([[0], signal[:-1]])
        transitions_idx = np.where((signal != prev) & (signal != 0))[0]

        out = []
        for i in transitions_idx:
            direction = int(signal[i])
            j = i
            while j < len(signal) and signal[j] == direction:
                j += 1
            out.append({
                'timestamp_ms':  int(timestamps[i]),
                'timestamp':     _ms_to_iso(int(timestamps[i])),
                'direction':     'LONG' if direction == 1 else 'SHORT',
                'duration_bars': j - i,
            })
        return out

    def _print_transitions(self, transitions: list) -> None:
        if not transitions:
            self._log.info('No signal transitions in window')
            return
        long_count  = sum(1 for t in transitions if t['direction'] == 'LONG')
        short_count = sum(1 for t in transitions if t['direction'] == 'SHORT')
        self._log.info(self._DIV)
        for t in transitions:
            self._log.info(
                f"  {t['timestamp']}  {t['direction']:<6}  "
                f"({t['duration_bars']} bars)"
            )
        self._log.info(self._DIV)
        self._log.info(
            f"Total: {len(transitions)} signal transitions "
            f"({long_count} long, {short_count} short)"
        )

    @staticmethod
    def _write_csv(transitions: list, end_ms: int, hours: float,
                   output_dir: str) -> str:
        tag = _ms_to_iso(end_ms).replace(':', '-').replace('+00-00', 'Z')
        path = f'{output_dir}/reconcile_{tag}_{int(hours)}h.csv'
        pd.DataFrame([
            {
                'timestamp_utc': t['timestamp'],
                'direction':     t['direction'],
                'duration_bars': t['duration_bars'],
                'timestamp_ms':  t['timestamp_ms'],
            }
            for t in transitions
        ]).to_csv(path, index=False)
        return path
