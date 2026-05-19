"""
FoldManager — generates line_signals from per-line centroid configs.

Foundation for r05's support/friction (SnF) work. After per-line grinds
produce centroid params, FoldManager runs each centroid through the PK
machine on a defined window, captures fires + per-fire diagnostics,
computes outcomes against the 3 candidate stops, and persists everything
to line_signals.

Output table is then queryable for affinity matrices:
  - Pairwise co-fire rates at multiple time windows
  - Solo-fire rates per line
  - Lead/lag relationships
  - Outcome-conditioned support patterns

Status: SKELETON. Tests pending against schema deployment + first centroid
set. Marked DRAFT until validated end-to-end on or_pk=6/7/8 centroids.
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone

from logger import get_logger

from ..db.database_manager import DatabaseManager
from ..compute.indicator_computer import IndicatorComputer
from ..compute.pk5s_gate_computer import Pk5sGateComputer
from ..compute.swing_analyzer import SwingAnalyzer


class FoldManager:
    """
    Generate line_signals for a set of per-line centroids on a given window.

    Usage:
      fm = FoldManager(db)
      lsr_pk = fm.run(
          tp_pk=1,
          lookback_days=3,
          centroids={
              4: {'len': 14, 'mult': 0.74, 'src': 'close', 'pool_c': 34,
                  'pool_w': 56, 'pool_range': 3, 'slope_floor': 5.4, 'multiplier': 1,
                  'weight_close': 5, 'weight_wide': 2},
              5: {...}, 6: {...}, 7: {...}, 8: {...}, 9: {...},
          },
          stops=[0.60, 0.71, 0.95],
          gating_on=False,
      )
      # Then query: SELECT * FROM line_signals WHERE ls_lsr_pk = lsr_pk
    """

    _MAX_BARS = 1080  # match production tc.tc_max_bars default

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    # ─────────────────────────────────────────────────────────────────────
    # Public entry
    # ─────────────────────────────────────────────────────────────────────

    def run(self, tp_pk: int, lookback_days: int, centroids: dict,
            stops: list, gating_on: bool = False,
            notes: str = None) -> int:
        """
        Fold all lines in centroids onto line_signals.

        centroids — {ic_pk: {len, mult/k/rsi/stc, src, pool_c, pool_w,
                             pool_range, slope_floor, multiplier,
                             weight_close, weight_wide}}
        stops     — list of stop_pct values; outcomes computed per stop
        Returns the lsr_pk (line_signal_runs row id) for the run.
        """
        end_ms   = int(datetime.now(timezone.utc).timestamp() * 1000)
        start_ms = int((datetime.now(timezone.utc)
                        - timedelta(days=lookback_days)).timestamp() * 1000)

        self._log.info(f'FoldManager: tp_pk={tp_pk}, lookback={lookback_days}d, '
                       f'lines={sorted(centroids.keys())}, stops={stops}, '
                       f'gating={"on" if gating_on else "off"}')

        # Create the run row
        lsr_pk = self._db.execute(
            '''INSERT INTO line_signal_runs
                 (lsr_tp_pk, lsr_window_start, lsr_window_end,
                  lsr_ic_pks, lsr_centroids, lsr_stops_json,
                  lsr_gating_on, lsr_notes)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
            (tp_pk, start_ms, end_ms,
             ','.join(str(p) for p in sorted(centroids.keys())),
             json.dumps({str(k): v for k, v in centroids.items()}),
             json.dumps([f'{s:.2f}' for s in stops]),
             1 if gating_on else 0,
             notes),
        )
        self._log.info(f'  lsr_pk={lsr_pk}')

        # Load klines once for the window
        base_df = self._load_klines(tp_pk, start_ms, end_ms)
        self._log.info(f'  base: {len(base_df)} × 5s bars')

        # Compute gate mask if requested. Otherwise zero array → all bars valid.
        if gating_on:
            oob_side = self._compute_bny30_gate(tp_pk, base_df)
            self._log.info(f'  gate: {int((oob_side != 0).sum())} OOB bars '
                           f'(L={int((oob_side == 1).sum())}, '
                           f'S={int((oob_side == -1).sum())})')
        else:
            oob_side = np.zeros(len(base_df), dtype=np.int8)

        # Process each line
        for ic_pk in sorted(centroids.keys()):
            try:
                fires = self._process_line(
                    lsr_pk, ic_pk, centroids[ic_pk],
                    base_df, oob_side, stops,
                )
                self._log.info(f'  ic_pk={ic_pk}: {fires} fires persisted')
            except Exception as e:
                self._log.error(f'  ic_pk={ic_pk} failed: {e}')
                raise  # don't half-fold; either all or none

        return lsr_pk

    # ─────────────────────────────────────────────────────────────────────
    # Per-line processing
    # ─────────────────────────────────────────────────────────────────────

    def _process_line(self, lsr_pk: int, ic_pk: int, params: dict,
                      base_df: pd.DataFrame, oob_side: np.ndarray,
                      stops: list) -> int:
        """
        Run pk machine for one line at its centroid, extract fires,
        compute outcomes per stop, bulk-insert into line_signals.
        """
        line_cfg = self._load_line_config(ic_pk)

        # DEMA per line's source (matches inspector's setup)
        dema_src = IndicatorComputer.build_source(base_df, line_cfg['ic_dema_src'])
        dema     = IndicatorComputer.dema(dema_src, int(line_cfg['ic_dema_len']))

        # Build single-line vote dict for Pk5sGateComputer
        vote = self._build_single_line_vote(ic_pk, params, line_cfg)

        # Run the gate machine
        pk_arr = Pk5sGateComputer(self._db).compute(
            tce_pk=f'fold-{lsr_pk}-{ic_pk}',
            base_df=base_df, dema=dema,
            params=vote,
            midpoint=(float(line_cfg['ic_high_boundary']) +
                      float(line_cfg['ic_low_boundary'])) / 2.0,
        )

        # Extract transition indices (PK fires)
        prev = np.concatenate([[0], pk_arr[:-1]])
        fire_idx = np.where((pk_arr != prev) & (pk_arr != 0))[0]

        timestamps = base_df['timestamp'].to_numpy()
        rows = []
        for i in fire_idx:
            i = int(i)
            direction = int(pk_arr[i])

            row = {
                'lsr_pk':    lsr_pk,
                'timestamp': int(timestamps[i]),
                'ic_pk':     ic_pk,
                'direction': direction,
                'line_value': None,           # Pk5sGateComputer doesn't expose per-bar
                'slope':       None,           # internals; populate later via separate
                'dema_value':  float(dema[i]),  # slope-instrumented compute pass.
            }

            # Compute outcomes per stop
            for stop in stops:
                outcome = self._evaluate_outcome(base_df, i, direction, stop)
                suf = f'{int(round(stop * 100)):02d}'
                row[f'max_profit_{suf}']   = outcome['max_profit_pct']
                row[f'bars_to_stop_{suf}'] = outcome['bars_to_stop']

            rows.append(row)

        self._bulk_insert_signals(rows)
        return len(rows)

    def _evaluate_outcome(self, base_df: pd.DataFrame, entry_idx: int,
                          direction: int, stop_pct: float) -> dict:
        """
        Walk forward from entry_idx, capture max_profit_pct and bars_to_stop
        against stop_pct. Returns dict with max_profit_pct and bars_to_stop
        (bars_to_stop = None if trade never stopped within MAX_BARS).
        """
        close = base_df['close'].to_numpy()
        entry = float(close[entry_idx])
        cap   = min(entry_idx + self._MAX_BARS, len(close) - 1)

        max_profit_pct = 0.0
        bars_to_stop   = None

        if direction == 1:
            stop_level = entry * (1.0 - stop_pct / 100.0)
            for j in range(entry_idx + 1, cap + 1):
                c = float(close[j])
                if c > entry:
                    profit = (c / entry - 1.0) * 100.0
                    if profit > max_profit_pct:
                        max_profit_pct = profit
                if c <= stop_level:
                    bars_to_stop = j - entry_idx
                    break
        else:
            stop_level = entry * (1.0 + stop_pct / 100.0)
            for j in range(entry_idx + 1, cap + 1):
                c = float(close[j])
                if c < entry:
                    profit = (1.0 - c / entry) * 100.0
                    if profit > max_profit_pct:
                        max_profit_pct = profit
                if c >= stop_level:
                    bars_to_stop = j - entry_idx
                    break

        return {
            'max_profit_pct': round(max_profit_pct, 4),
            'bars_to_stop':   bars_to_stop,
        }

    # ─────────────────────────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────────────────────────

    def _build_single_line_vote(self, ic_pk: int, params: dict,
                                line_cfg: dict) -> dict:
        """
        Build the Pk5sGateComputer params dict for single-line vote_overrides.
        Mirrors the structure used by Pk5sGateComputer.compute().
        """
        line_type = line_cfg['ic_line_type']
        base = {
            'pool_c':      int(params['pool_c']),
            'pool_w':      int(params['pool_w']),
            'pool_range':  int(params['pool_range']),
            'slope_floor': float(params['slope_floor']),
            'multiplier':  int(params['multiplier']),
            'vote_overrides': {
                str(ic_pk): {
                    'weight_close': int(params.get('weight_close', 5)),
                    'weight_wide':  int(params.get('weight_wide',  2)),
                }
            },
        }

        if line_type == 'bb':
            base.update({
                'ic_line_type': 'bb',
                'ic_src':       params['src'],
                'ic_bb_len':    int(params['len']),
                'ic_bb_mult':   float(params['mult']),
            })
        else:  # 'k'
            base.update({
                'ic_line_type': 'k',
                'ic_src':       params['src'],
                'ic_k_len':     int(params.get('len',       line_cfg['ic_k_len'])),
                'ic_rsi_len':   int(params.get('len_rsi',   line_cfg['ic_rsi_len'])),
                'ic_stc_len':   int(params.get('len_stoch', line_cfg['ic_stc_len'])),
            })

        return base

    def _load_line_config(self, ic_pk: int) -> dict:
        rows = self._db.execute(
            '''SELECT ic.*,
                      ic.ic_src AS ic_dema_src,
                      2         AS ic_dema_len   -- default; mirror tc.tc_dema_len if needed
               FROM indicator_configs ic
               WHERE ic.ic_pk = %s''',
            (ic_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No indicator_config for ic_pk={ic_pk}')
        return rows[0]

    def _load_klines(self, tp_pk: int, start_ms: int,
                     end_ms: int) -> pd.DataFrame:
        rows = self._db.execute(
            '''SELECT kc_timestamp AS timestamp, kc_open  AS open,
                      kc_high      AS high,      kc_low   AS low,
                      kc_close     AS close,     kc_volume AS volume
               FROM kline_collection
               WHERE kc_tp_pk    = %s
                 AND kc_timestamp >= %s
                 AND kc_timestamp <  %s
               ORDER BY kc_timestamp ASC''',
            (tp_pk, start_ms, end_ms), fetch=True,
        )
        if not rows:
            raise RuntimeError(f'No klines for tp_pk={tp_pk} in window')
        return pd.DataFrame(rows)

    def _compute_bny30_gate(self, tp_pk: int,
                            base_df: pd.DataFrame) -> np.ndarray:
        """
        Stub. To be implemented when bny30 integration lands.
        Returns the folded oob_side array (+1 HI, -1 LO, 0 IB) from
        bny30M and bny30p gates aligned to base_df.
        """
        raise NotImplementedError(
            'bny30 gating not yet integrated into FoldManager. '
            'Set gating_on=False until that lands.'
        )

    def _bulk_insert_signals(self, rows: list) -> None:
        if not rows:
            return
        cols = (
            'ls_lsr_pk', 'ls_timestamp', 'ls_ic_pk', 'ls_direction',
            'ls_line_value', 'ls_slope', 'ls_dema_value',
            'ls_max_profit_60', 'ls_bars_to_stop_60',
            'ls_max_profit_71', 'ls_bars_to_stop_71',
            'ls_max_profit_95', 'ls_bars_to_stop_95',
        )
        placeholders = '(' + ','.join(['%s'] * len(cols)) + ')'
        values = []
        for r in rows:
            values.append((
                r['lsr_pk'], r['timestamp'], r['ic_pk'], r['direction'],
                r['line_value'], r['slope'], r['dema_value'],
                r.get('max_profit_60'),   r.get('bars_to_stop_60'),
                r.get('max_profit_71'),   r.get('bars_to_stop_71'),
                r.get('max_profit_95'),   r.get('bars_to_stop_95'),
            ))
        sql = f'INSERT INTO line_signals ({",".join(cols)}) VALUES ' + \
              ','.join([placeholders] * len(values))
        flat = [v for row in values for v in row]
        self._db.execute(sql, tuple(flat))
