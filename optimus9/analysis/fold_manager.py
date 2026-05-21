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
from ..db.kline_loader     import KlineLoader
from ..compute.indicator_computer import IndicatorComputer
from ..compute.pk5s_gate_computer import Pk5sGateComputer
from ..compute.swing_analyzer import SwingAnalyzer
from ..compute.outcome_walker import walk_outcome


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

    # r05 (260521): _MAX_BARS dropped — outcome_walker now uses no cap.
    # bars_to_stop=None ⇔ trade ran off the end of available klines.

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._kl  = KlineLoader(db)
        self._log = get_logger(self.__class__.__name__)

    # ─────────────────────────────────────────────────────────────────────
    # Public entry
    # ─────────────────────────────────────────────────────────────────────

    def run(self, tp_pk: int, lookback_days: int, centroids: dict,
            stops: list, gating_on: bool = True,
            gate_ic_pks: list = None,
            notes: str = None) -> int:
        """
        Fold all lines in centroids onto line_signals.

        centroids — {ic_pk: {len, mult/k/rsi/stc, src, pool_c, pool_w,
                             pool_range, slope_floor, multiplier,
                             weight_close, weight_wide}}
        stops     — list of stop_pct values; outcomes computed per stop
        gating_on — if True, compute bny30 gate mask and tag each fire's
                    ls_gated_in column (1 if gate agrees, 0 if filtered).
                    All fires are persisted regardless — gating is a tag,
                    not a filter. Analysis filters via WHERE ls_gated_in=1.
        gate_ic_pks — list of gate ic_pks; defaults to [2, 3] (bny30M/p).

        Returns the lsr_pk for the run.
        """
        if gate_ic_pks is None:
            gate_ic_pks = [2, 3]   # bny30M + bny30p

        end_ms   = int(datetime.now(timezone.utc).timestamp() * 1000)
        start_ms = int((datetime.now(timezone.utc)
                        - timedelta(days=lookback_days)).timestamp() * 1000)

        self._log.info(f'FoldManager: tp_pk={tp_pk}, lookback={lookback_days}d, '
                       f'lines={sorted(centroids.keys())}, stops={stops}, '
                       f'gating={"on" if gating_on else "off"}'
                       + (f' ic_pks={gate_ic_pks}' if gating_on else ''))

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

        # Compute the bny30 gate mask once if gating is on (used by all lines)
        if gating_on:
            gate_mask = IndicatorComputer.compute_gate_mask(
                db=self._db, ic_pks=gate_ic_pks,
                base_df=base_df, fold='AND',
            )
            kept = int((gate_mask != 0).sum())
            self._log.info(f'  gate: bny30 AND — {kept} bars OOB '
                           f'(L={int((gate_mask == 1).sum())}, '
                           f'S={int((gate_mask == -1).sum())})')
        else:
            gate_mask = np.zeros(len(base_df), dtype=np.int8)

        # Process each line
        for ic_pk in sorted(centroids.keys()):
            try:
                fires, gated = self._process_line(
                    lsr_pk, ic_pk, centroids[ic_pk],
                    base_df, gate_mask, gating_on, stops,
                )
                if gating_on:
                    pct = (100.0 * gated / fires) if fires else 0
                    self._log.info(f'  ic_pk={ic_pk}: {fires} fires, '
                                   f'{gated} gated-in ({pct:.1f}%)')
                else:
                    self._log.info(f'  ic_pk={ic_pk}: {fires} fires '
                                   '(gating off; all marked ls_gated_in=1)')
            except Exception as e:
                self._log.error(f'  ic_pk={ic_pk} failed: {e}')
                raise

        return lsr_pk

    # ─────────────────────────────────────────────────────────────────────
    # Per-line processing
    # ─────────────────────────────────────────────────────────────────────

    def _process_line(self, lsr_pk: int, ic_pk: int, params: dict,
                      base_df: pd.DataFrame, gate_mask: np.ndarray,
                      gating_on: bool, stops: list) -> tuple:
        """
        Run pk machine for one line at its centroid, extract fires,
        compute outcomes per stop, tag with gate agreement, bulk-insert.

        Returns (total_fires, gated_in_fires) — first is all fires
        persisted; second is the subset where gate agrees with direction.
        """
        line_cfg = self._load_line_config(ic_pk)

        # DEMA per line's source (matches inspector's setup)
        dema_src = IndicatorComputer.build_source(base_df, line_cfg['ic_dema_src'])
        dema     = IndicatorComputer.dema(dema_src, int(line_cfg['ic_dema_len']))

        # Build single-line vote dict for Pk5sGateComputer
        vote = self._build_single_line_vote(ic_pk, params, line_cfg)

        # Run the gate machine to produce PK fires
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
        gated_count = 0
        rows = []
        for i in fire_idx:
            i = int(i)
            direction = int(pk_arr[i])

            # ls_gated_in: 1 if bny30 gate agrees with this fire's direction.
            # When gating_on=False, mark all fires as 1 so consumer queries
            # using `WHERE ls_gated_in=1` behave consistently across runs.
            if gating_on:
                gated_in = 1 if int(gate_mask[i]) == direction else 0
            else:
                gated_in = 1
            gated_count += gated_in

            row = {
                'lsr_pk':    lsr_pk,
                'timestamp': int(timestamps[i]),
                'ic_pk':     ic_pk,
                'direction': direction,
                'gated_in':  gated_in,
                'line_value': None,           # Pk5sGateComputer doesn't expose per-bar
                'slope':       None,           # internals; populate later via separate
                'dema_value':  float(dema[i]),  # slope-instrumented compute pass.
            }

            # Compute outcomes per stop. All fires get outcomes, not just
            # gated-in ones — lets analysis compare "what gating filtered out
            # had it played out" against "what it kept."
            for stop in stops:
                outcome = self._evaluate_outcome(base_df, i, direction, stop)
                suf = f'{int(round(stop * 100)):02d}'
                row[f'max_profit_{suf}']   = outcome['max_profit_pct']
                row[f'bars_to_stop_{suf}'] = outcome['bars_to_stop']

            rows.append(row)

        self._bulk_insert_signals(rows)
        return len(rows), gated_count

    def _evaluate_outcome(self, base_df: pd.DataFrame, entry_idx: int,
                          direction: int, stop_pct: float) -> dict:
        """
        Walk forward from entry_idx via shared outcome_walker.walk_outcome.

        r05 (260521): per-bar walk moved to compute.outcome_walker, shared
        with SwingAnalyzer. _MAX_BARS cap dropped — bars_to_stop=None now
        strictly means the trade ran off the end of available klines.
        """
        close = base_df['close'].to_numpy()
        outcome = walk_outcome(close, entry_idx, direction, stop_pct)
        # FoldManager only consumes max_profit_pct and bars_to_stop;
        # drop bars_to_max_profit to keep the call-site stable.
        return {
            'max_profit_pct': outcome['max_profit_pct'],
            'bars_to_stop':   outcome['bars_to_stop'],
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
        """Delegates to shared KlineLoader (r05 260521 refactor)."""
        return self._kl.load_window(tp_pk, start_ms, end_ms)

    def _bulk_insert_signals(self, rows: list) -> None:
        if not rows:
            return
        cols = (
            'ls_lsr_pk', 'ls_timestamp', 'ls_ic_pk', 'ls_direction',
            'ls_gated_in',
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
                r['gated_in'],
                r['line_value'], r['slope'], r['dema_value'],
                r.get('max_profit_60'),   r.get('bars_to_stop_60'),
                r.get('max_profit_71'),   r.get('bars_to_stop_71'),
                r.get('max_profit_95'),   r.get('bars_to_stop_95'),
            ))
        sql = f'INSERT INTO line_signals ({",".join(cols)}) VALUES ' + \
              ','.join([placeholders] * len(values))
        flat = [v for row in values for v in row]
        self._db.execute(sql, tuple(flat))
