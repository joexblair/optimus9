"""
AnalyzeManager — see class docstring for purpose, Pine alignment, and design notes.
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


class AnalyzeManager:
    """
    Aggregates grind results from MySQL and produces a structured analysis report.
    All heavy lifting stays in the DB — Python only sees the per-combo summary rows.

    Outputs:
      - Console / info.log: full analysis report
      - CSV: combo summary with all metrics (for further exploration)

    Round 04 changes:
      - 'won' / 'stopped' / 'inconclusive' classification re-derived from
        max_profit_pct + bars_to_stop using tc.tc_profit_zone, not the
        deleted pko_result column.
      - Sweep params discovered dynamically from pk_signals columns (which
        are populated) and test_param_ranges.tpr_param_type (for int/float/enum).
      - K-line target support: pks_len_rsi, pks_len_stoch surface as sweep
        params in K grinds, are NULL/absent in BB grinds.
    """

    # Columns in the combo summary query that are NOT sweep params — these
    # are the aggregate metrics. Everything else returned by the query is
    # treated as a sweep dimension.
    _META_COLS = {
        'total', 'won', 'stopped_ct', 'inconclusive_ct',
        'avg_win_pct', 'avg_bars', 'avg_bars_peak',
    }

    # Sweep dimensions that can appear in pk_signals / pk_combo_summary.
    # Order matters only for report presentation; missing/NULL columns are
    # filtered downstream.
    _CANDIDATE_PARAMS = [
        'len', 'mult', 'len_rsi', 'len_stoch', 'src',
        'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier',
        # r07 (2026-05-30): PM dials surface as sweep dims in vote-sourced
        # grinds. Tagged on signals + pk_combo_summary; NULL for line-sourced.
        'pm_additive', 'pm_suppression',
    ]

    # Auto-labels keyed on (p_rev, pk5s_gate) flag tuple (compare reports)
    _COMPARE_LABELS = {
        ('off', 'off'): 'baseline',
        ('on',  'off'): 'p_rev only',
        ('off', 'on'):  'gate only',
        ('on',  'on'):  'production',
    }

    _DIV_LINE = '═' * 72
    _SEC_LINE = '─' * 72

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, or_pk: int, min_signals: int = 30, top_n: int = 20,
            top_stage1: int = 100, dd_threshold: float = 0.15,
            output_dir: str = '.') -> str:
        """
        Two-stage analysis pipeline:
          Stage 1: top `top_stage1` combos by expectancy (statistical edge filter)
          Stage 2: walk each Stage 1 combo's signal sequence to get real
                   gross_banked, max_drawdown, profit_factor, sharpe, sortino
          DD filter: combos with max_drawdown > dd_threshold are listed
                     separately (not silently dropped).
          PROVEN COMBO: Stage 2 rank #1 by gross_banked (excluding DD-killed).
          Centroid: still computed for directional hint; no longer the
                    deployment recommendation.

        Console: top 20 by gross_banked + PROVEN COMBO + DD audit if any.
        CSV: full top 100 sorted by gross_banked with all metrics.
        """
        run_meta    = self._load_run_meta(or_pk)
        self._log.info(
            f'Loading combo summaries for or_pk={or_pk} '
            f'({run_meta["tc_indicator_label"]}) — this is the expensive '
            'step (GROUP BY across all signals), may take 10-20 min for '
            'large grinds'
        )
        stop_pct    = float(run_meta['tc_stop_pct'])
        profit_zone = float(run_meta['tc_profit_zone'])
        raw         = self._load_combo_summaries(or_pk, profit_zone)

        if not raw:
            self._log.error(f'No results found for or_pk={or_pk}')
            return ''

        df = pd.DataFrame(raw)
        df = self._enrich(df, stop_pct)

        # Discover which sweep params are populated for this run.
        params_present = self._discover_params(df)
        param_types    = self._load_param_types(int(run_meta['or_tc_pk']))

        # Filter to combos with enough decided trades
        filtered = df[df['decided'] >= min_signals].copy()

        # ── Stage 1: shortlist by expectancy ───────────────────────────────
        stage1 = self._compute_stage1(filtered, top_stage1)

        # ── Stage 2: walk equity per combo, compute real metrics ───────────
        stage2 = self._compute_stage2(
            or_pk, stage1, profit_zone, stop_pct, params_present,
        )

        # ── DD filter: kept (for ranking) vs killed (for audit) ────────────
        stage2_kept, stage2_killed = self._apply_dd_filter(stage2, dd_threshold)

        # Reports
        self._report_overview(df, filtered, run_meta)
        self._report_sensitivity(filtered, params_present)
        self._report_top_n_v2(stage2_kept, top_n, params_present, run_meta, df)
        self._report_baseline(run_meta, params_present)
        self._report_proven_combo(stage2_kept, params_present, profit_zone)
        self._report_centroid(filtered, top_n, params_present, param_types)
        if not stage2_killed.empty:
            self._report_dd_audit(stage2_killed, dd_threshold)

        # CSV — full top 100 by gross_banked, with all Stage 2 metrics
        path = f'{output_dir}/analysis_or{or_pk}.csv'
        self._write_stage2_csv(stage2, path)
        self._log.info(f'Full top {top_stage1} with metrics → {path}')
        self._log.info(self._DIV_LINE)
        return path

    def analyze_many(self, or_pks: list, parallel: int = 1, **kwargs) -> list:
        """
        Batch process multiple or_pks. Same kwargs as run().

        parallel=1 (default): sequential, single DB connection.
        parallel=N (N>1):     N worker processes, each opens its own DB.
                              Use N ≤ min(len(or_pks), available_cores).
                              Each or_pk takes 10-20 min for large grinds
                              so parallelism pays off heavily.

        Note: worker log lines may interleave across or_pks; CSVs are
        per-or_pk so they don't conflict.
        """
        if parallel > 1:
            import multiprocessing as mp
            self._log.info(
                f'Batch analyze: {len(or_pks)} or_pks across '
                f'{parallel} parallel workers'
            )
            with mp.Pool(parallel) as pool:
                return pool.map(
                    _analyze_one_worker,
                    [(op, kwargs) for op in or_pks],
                )

        out = []
        for or_pk in or_pks:
            self._log.info('')
            self._log.info('')
            try:
                out.append(self.run(or_pk, **kwargs))
            except Exception as e:
                self._log.error(f'or_pk={or_pk} failed: {e}')
                out.append(None)
        return out

    # ── data loading ──────────────────────────────────────────────────────────

    def top_combo_signals(self, or_pk: int, top_n: int = 20, min_signals: int = 30,
                          top_stage1: int = 100, dd_threshold: float = None) -> list:
        """The two-stage top-N combos (the 'centroids'), each with its signal
        timestamps. Reuses the run() ranking pipeline but returns data instead of
        writing reports — for downstream scorers like ClusterScoring.

        Ranked by gross_banked. `dd_threshold` is OFF by default: max-drawdown is a
        portfolio-level concern, not a signal-grind gate (r07), and at 5s it would
        cull every combo. Pass a value to re-enable the kept/killed split.

        Returns [{'rank': int, 'params': {name: value, ...},
                  'signals': [(ts_ms, dir), ...]}, ...].
        """
        meta        = self._load_run_meta(or_pk)
        stop_pct    = float(meta['tc_stop_pct'])
        profit_zone = float(meta['tc_profit_zone'])
        raw = self._load_combo_summaries(or_pk, profit_zone)
        if not raw:
            self._log.error(f'No results for or_pk={or_pk}')
            return []

        df       = self._enrich(pd.DataFrame(raw), stop_pct)
        params   = self._discover_params(df)
        filtered = df[df['decided'] >= min_signals].copy()
        stage1   = self._compute_stage1(filtered, top_stage1)
        stage2   = self._compute_stage2(or_pk, stage1, profit_zone, stop_pct, params)
        ranked   = (self._apply_dd_filter(stage2, dd_threshold)[0]
                    if dd_threshold is not None else stage2)

        out = []
        for _, combo in ranked.head(top_n).iterrows():
            sigs = self._query_combo_signals(or_pk, combo)
            out.append({
                'rank':    int(combo['stage2_rank']),
                'params':  {p: combo[p] for p in params},
                'signals': [(int(s['ts']), int(s['direction'])) for s in sigs],
            })
        self._log.info(f'top_combo_signals: or_pk={or_pk} → {len(out)} combos '
                       f'({sum(len(c["signals"]) for c in out)} signals)')
        return out

    def materialize_centroids(self, or_pk: int, top_n: int = 20, **kw) -> list:
        """top_combo_signals + persist to the reusable am_centroids /
        am_centroid_signals tables. Returns the list."""
        top = self.top_combo_signals(or_pk, top_n=top_n, **kw)
        if top:
            self._persist_centroids(or_pk, top)
        return top

    def centroids(self, or_pk: int) -> list:
        """Read materialised centroids for an or_pk (same shape as
        top_combo_signals, plus a 'combo' fingerprint). [] if none materialised."""
        try:
            heads = self._db.execute(
                '''SELECT amc_pk, amc_rank, amc_combo, amc_params
                   FROM am_centroids WHERE amc_or_pk=%s ORDER BY amc_rank''',
                (or_pk,), fetch=True)
        except mysql.connector.Error:
            return []
        out = []
        for h in heads or []:
            sigs = self._db.execute(
                '''SELECT acs_ts, acs_dir FROM am_centroid_signals
                   WHERE acs_amc_pk=%s ORDER BY acs_ts''', (h['amc_pk'],), fetch=True)
            out.append({
                'rank':    int(h['amc_rank']),
                'combo':   h['amc_combo'],
                'params':  json.loads(h['amc_params']) if h['amc_params'] else {},
                'signals': [(int(s['acs_ts']), int(s['acs_dir'])) for s in sigs],
            })
        return out

    def _persist_centroids(self, or_pk: int, top: list) -> None:
        """Materialise top-N centroids + their (ts,dir) into am_centroids /
        am_centroid_signals (replacing any prior rows for this or_pk), so
        cluster_scoring / SnF read centroids without re-touching the firehose."""
        self._db.execute('''CREATE TABLE IF NOT EXISTS am_centroids (
            amc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            amc_or_pk INT, amc_rank INT, amc_n_signals INT,
            amc_combo VARCHAR(160), amc_params TEXT, INDEX(amc_or_pk))''')
        self._db.execute('''CREATE TABLE IF NOT EXISTS am_centroid_signals (
            acs_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
            acs_amc_pk BIGINT, acs_ts BIGINT, acs_dir TINYINT, INDEX(acs_amc_pk))''')

        prior = self._db.execute(
            'SELECT amc_pk FROM am_centroids WHERE amc_or_pk=%s', (or_pk,), fetch=True)
        if prior:
            ph = ','.join(['%s'] * len(prior))
            ids = tuple(r['amc_pk'] for r in prior)
            self._db.execute(
                f'DELETE FROM am_centroid_signals WHERE acs_amc_pk IN ({ph})', ids)
            self._db.execute('DELETE FROM am_centroids WHERE amc_or_pk=%s', (or_pk,))

        for c in top:
            combo = '|'.join(str(c['params'][p]) for p in c['params'])
            self._db.execute(
                '''INSERT INTO am_centroids
                   (amc_or_pk, amc_rank, amc_n_signals, amc_combo, amc_params)
                   VALUES (%s,%s,%s,%s,%s)''',
                (or_pk, c['rank'], len(c['signals']), combo,
                 json.dumps({k: str(v) for k, v in c['params'].items()})))
            amc_pk = self._db.execute(
                'SELECT LAST_INSERT_ID() AS id', fetch=True)[0]['id']
            if c['signals']:
                self._db.executemany(
                    '''INSERT INTO am_centroid_signals (acs_amc_pk, acs_ts, acs_dir)
                       VALUES (%s,%s,%s)''',
                    [(amc_pk, ts, d) for ts, d in c['signals']])
        self._log.info(f'materialised {len(top)} centroids → am_centroids (or_pk={or_pk})')

    def _load_run_meta(self, or_pk: int) -> dict:
        rows = self._db.execute(
            '''SELECT r.*, tc.tc_pk AS or_tc_pk,
                      tc.tc_stop_pct, tc.tc_profit_zone, tc.tc_stop_buffer,
                      tc.tc_dynamic_stoploss, tc.tc_indicator_label,
                      tc.tc_dema_len, tc.tc_dema_src,
                      ic.ic_line_type AS og_line_type,
                      ic.ic_src       AS og_src,
                      ic.ic_bb_len    AS og_bb_len,
                      ic.ic_bb_mult   AS og_bb_mult,
                      ic.ic_k_len     AS og_k_len,
                      ic.ic_rsi_len   AS og_rsi_len,
                      ic.ic_stc_len   AS og_stc_len
               FROM optimizer_runs r
               JOIN test_configs tc ON tc.tc_pk = r.or_tc_pk
               JOIN indicator_configs ic ON ic.ic_pk = tc.tc_ic_pk
               WHERE r.or_pk = %s''',
            (or_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No optimizer_run for or_pk={or_pk}')
        return rows[0]

    def _load_combo_summaries(self, or_pk: int, profit_zone: float) -> list:
        # r07 (2026-05-30): prefer pre-aggregated rows from pk_combo_summary
        # (OptimizerRunner populates one row per combo as the grind runs).
        # AM's prior GROUP BY did 40 min on or_pk=54's 76.5M signal rows;
        # reading the summary table is O(combos) instead.
        #
        # Fallback to the original GROUP BY when no summary rows exist for
        # this or_pk — preserves backward-compat for grinds that ran before
        # the pk_combo_summary refactor. The fallback's GROUP BY now also
        # includes pks_pm_additive / pks_pm_suppression so vote-sourced
        # combos resolve correctly even via the slow path.
        #
        # r05 semantics preserved: 'won' counts any trade that reached
        # profit_zone regardless of whether stop later fired (in real
        # trading the position closes at profit). 'stopped_ct' excludes
        # those wins. 'inconclusive_ct' excludes them too. The three are
        # mutually exclusive and sum to total. 'decided' = won + stopped_ct
        # is computed in _enrich.
        rows = self._db.execute(
            '''SELECT pcs_len             AS len,
                      pcs_mult            AS mult,
                      pcs_len_rsi         AS len_rsi,
                      pcs_len_stoch       AS len_stoch,
                      pcs_src             AS src,
                      pcs_pool_c          AS pool_c,
                      pcs_pool_w          AS pool_w,
                      pcs_pool_range      AS pool_range,
                      pcs_slope_floor     AS slope_floor,
                      pcs_multiplier      AS multiplier,
                      pcs_pm_additive     AS pm_additive,
                      pcs_pm_suppression  AS pm_suppression,
                      pcs_total           AS total,
                      pcs_won             AS won,
                      pcs_stopped_ct      AS stopped_ct,
                      pcs_inconclusive_ct AS inconclusive_ct,
                      pcs_avg_win_pct     AS avg_win_pct,
                      pcs_avg_bars        AS avg_bars,
                      pcs_avg_bars_peak   AS avg_bars_peak
               FROM pk_combo_summary
               WHERE pcs_or_pk = %s''',
            (or_pk,), fetch=True,
        )
        if rows:
            return rows

        # Fallback: original GROUP BY over pk_signals + pk_outcomes.
        self._log.info(
            f'pk_combo_summary empty for or_pk={or_pk} — falling back to '
            'GROUP BY (this is the slow path; pre-refactor grind)'
        )
        return self._db.execute(
            '''SELECT
                   s.pks_len             AS len,
                   s.pks_mult            AS mult,
                   s.pks_len_rsi         AS len_rsi,
                   s.pks_len_stoch       AS len_stoch,
                   s.pks_src             AS src,
                   s.pks_pool_c          AS pool_c,
                   s.pks_pool_w          AS pool_w,
                   s.pks_pool_range      AS pool_range,
                   s.pks_slope_floor     AS slope_floor,
                   s.pks_multiplier      AS multiplier,
                   s.pks_pm_additive     AS pm_additive,
                   s.pks_pm_suppression  AS pm_suppression,
                   COUNT(*)                                                AS total,
                   SUM(o.pko_max_profit_pct >= %s)                         AS won,
                   SUM(o.pko_bars_to_stop IS NOT NULL
                       AND o.pko_max_profit_pct < %s)                      AS stopped_ct,
                   SUM(o.pko_bars_to_stop IS NULL
                       AND o.pko_max_profit_pct < %s)                      AS inconclusive_ct,
                   AVG(CASE WHEN o.pko_max_profit_pct >= %s
                            THEN o.pko_max_profit_pct END)                 AS avg_win_pct,
                   AVG(o.pko_bars_to_stop)                                 AS avg_bars,
                   AVG(o.pko_bars_to_max_profit)                           AS avg_bars_peak
               FROM pk_signals s
               JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               WHERE s.pks_or_pk = %s
               GROUP BY s.pks_len, s.pks_mult, s.pks_len_rsi, s.pks_len_stoch,
                        s.pks_src, s.pks_pool_c, s.pks_pool_w, s.pks_pool_range,
                        s.pks_slope_floor, s.pks_multiplier,
                        s.pks_pm_additive, s.pks_pm_suppression''',
            (profit_zone, profit_zone, profit_zone, profit_zone, or_pk), fetch=True,
        )

    def _load_param_types(self, tc_pk: int) -> dict:
        """
        Returns {param_name: 'int'|'float'|'enum'} from test_param_ranges.
        Used by centroid math to round int params to int (no fractional
        grid points exist for them).
        """
        rows = self._db.execute(
            '''SELECT tpr_param_name AS name, tpr_param_type AS ptype
               FROM test_param_ranges WHERE tpr_tc_pk = %s''',
            (tc_pk,), fetch=True,
        )
        return {r['name']: r['ptype'] for r in rows}

    # ── enrichment + param discovery ──────────────────────────────────────────

    def _enrich(self, df: pd.DataFrame, stop_pct: float) -> pd.DataFrame:
        df = df.copy()
        for col in ['total', 'won', 'stopped_ct', 'inconclusive_ct']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        for col in ['avg_win_pct', 'avg_bars', 'avg_bars_peak']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # All-stops combo → avg_win_pct is NaN. Coerce to 0 so expectancy
        # collapses to −stop_pct rather than NaN (preserves r02 idxmax fix).
        df['avg_win_pct'] = df['avg_win_pct'].fillna(0.0)

        # r05: decided = won + stopped_ct (computed in Python, not SQL).
        # The three SQL buckets (won/stopped_ct/inconclusive_ct) are
        # mutually exclusive and sum to total. 'decided' excludes
        # inconclusive trades from the win-rate denominator since they
        # never resolved into a clear outcome. This bounds win_rate ≤ 1.
        df['decided'] = df['won'] + df['stopped_ct']
        df['win_rate']         = df['won'] / df['decided'].replace(0, float('nan'))
        df['inconclusive_rate'] = df['inconclusive_ct'] / df['total'].replace(0, float('nan'))
        df['expectancy']       = (
            df['win_rate'] * df['avg_win_pct']
            - (1.0 - df['win_rate']) * stop_pct
        )
        return df

    def _discover_params(self, df: pd.DataFrame) -> list:
        """
        Return the candidate params that have at least one non-NULL value
        in this combo set. BB grinds drop len_rsi/len_stoch; K grinds drop
        mult. Order preserved from _CANDIDATE_PARAMS for presentation.
        """
        return [
            p for p in self._CANDIDATE_PARAMS
            if p in df.columns and df[p].notna().any()
        ]

    # ── report sections ───────────────────────────────────────────────────────

    def _report_overview(self, df: pd.DataFrame, filtered: pd.DataFrame, meta: dict) -> None:
        total_signals = int(df['total'].sum())
        baseline_wr   = float(df['won'].sum() / max(df['decided'].sum(), 1) * 100)

        self._log.info(self._DIV_LINE)
        self._log.info(
            f'  PK GRINDER — ANALYSIS   or_pk={meta["or_pk"]}'
            f'   {meta["tc_indicator_label"]}'
        )
        p_rev = meta.get('or_p_rev_enabled')
        pk5s  = meta.get('or_pk5s_gate_enabled')
        if p_rev is not None or pk5s is not None:
            self._log.info(
                f'  Run config: p_rev={"on" if p_rev else "off"}'
                f'   pk5s_gate={"on" if pk5s else "off"}'
            )
        self._log.info(
            f'  Calibration: stop_pct={float(meta["tc_stop_pct"]):.4f}%   '
            f'profit_zone={float(meta["tc_profit_zone"]):.4f}%   '
            f'dynamic_stoploss={"on" if meta["tc_dynamic_stoploss"] else "off"}'
        )
        self._log.info(self._DIV_LINE)

        if df['decided'].sum() < 5000:
            self._log.info('  ⚠  Low data volume — results are preliminary')
        self._log.info('')
        self._log.info('OVERVIEW')
        self._log.info(f'  Total signals        : {total_signals:>10,}')
        self._log.info(f'  Combos (all)         : {len(df):>10,}')
        self._log.info(f'  Combos (≥{meta.get("min_signals",30)} decided) : {len(filtered):>10,}')
        self._log.info(f'  Avg gated win rate   : {baseline_wr:>9.1f}%')

        if not filtered.empty:
            best  = filtered.loc[filtered['expectancy'].idxmax()]
            worst = filtered.loc[filtered['expectancy'].idxmin()]
            self._log.info(
                f'  Best expectancy      : {float(best["expectancy"]):>9.4f}%'
                f'   win={float(best["win_rate"])*100:.1f}%'
                f'   signals={int(best["total"])}'
            )
            self._log.info(
                f'  Worst expectancy     : {float(worst["expectancy"]):>9.4f}%'
                f'   win={float(worst["win_rate"])*100:.1f}%'
                f'   signals={int(worst["total"])}'
            )
        self._log.info('')

    def _report_sensitivity(self, df: pd.DataFrame, params: list) -> None:
        if df.empty:
            return
        self._log.info('PER-PARAM SENSITIVITY  (avg expectancy across combos per value)')
        self._log.info(self._SEC_LINE)

        for param in params:
            grp = (df.groupby(param, dropna=True)['expectancy']
                     .agg(['mean', 'count'])
                     .reset_index()
                     .sort_values(param))
            parts = '   '.join(
                f'{row[param]}={float(row["mean"]):+.4f}%'
                for _, row in grp.iterrows()
            )
            self._log.info(f'  {param:<12}  {parts}')

        self._log.info('')

    # ── Stage 1: shortlist by expectancy ─────────────────────────────────

    def _compute_stage1(self, df: pd.DataFrame, top_n: int) -> pd.DataFrame:
        """
        Stage 1: take top N combos by expectancy. Returns a slice of df
        with `stage1_rank` column added.
        """
        if df.empty:
            return df.iloc[0:0].copy()
        out = df.nlargest(top_n, 'expectancy').copy()
        out['stage1_rank'] = range(1, len(out) + 1)
        return out

    # ── Stage 2: walk equity per combo, compute real metrics ─────────────

    _PARAM_COL_MAP = (
        ('pks_len',         'len'),
        ('pks_mult',        'mult'),
        ('pks_src',         'src'),
        ('pks_len_rsi',     'len_rsi'),
        ('pks_len_stoch',   'len_stoch'),
        ('pks_pool_c',      'pool_c'),
        ('pks_pool_w',      'pool_w'),
        ('pks_pool_range',  'pool_range'),
        ('pks_slope_floor', 'slope_floor'),
        ('pks_multiplier',  'multiplier'),
    )

    def _query_combo_signals(self, or_pk: int, combo_row) -> list:
        """
        Pull all signals + outcomes for a specific combo, ordered by time.
        BB combos have NULL len_rsi/stoch; K combos have NULL mult.
        WHERE clause uses IS NULL for NULL values to match correctly.
        """
        where_parts = ['s.pks_or_pk = %s']
        vals = [or_pk]
        for col, key in self._PARAM_COL_MAP:
            v = combo_row.get(key)
            if v is None or (isinstance(v, float) and pd.isna(v)):
                where_parts.append(f's.{col} IS NULL')
            else:
                where_parts.append(f's.{col} = %s')
                vals.append(v)

        sql = f'''
            SELECT s.pks_timestamp        AS ts,
                   s.pks_dir              AS direction,
                   o.pko_max_profit_pct   AS max_pct,
                   o.pko_bars_to_stop     AS bts,
                   o.pko_bars_to_max_profit AS btm
            FROM pk_signals s
            LEFT JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
            WHERE {' AND '.join(where_parts)}
            ORDER BY s.pks_pk
        '''
        return self._db.execute(sql, tuple(vals), fetch=True)

    @staticmethod
    def _walk_equity(signals: list, profit_zone: float, stop_pct: float,
                     seed: float = 1000.0) -> dict:
        """
        Walk a signal sequence on a $seed-equity curve. Returns:
          gross_banked, max_drawdown, profit_factor, sharpe, sortino,
          mean_pnl, n_won, n_stopped, n_inconc, avg_won_pct,
          min_won_pct, win95_flag

        signal_pnl logic:
          max_pct >= profit_zone           → +max_pct (win at profit_zone exit)
          else if bars_to_stop NOT NULL    → -stop_pct (loss)
          else                             → 0 (inconclusive, no trade close)

        Inconclusive trades count toward 'total' but not 'decided'. They
        contribute 0 to equity (assumes the strategy holds them flat).

        Returns inf for sharpe/sortino/PF when stdev or denominator is 0;
        the CSV writer converts inf → blank for cleanliness.
        """
        # RESOLVED equity walk
        equity = seed
        peak   = seed
        max_dd = 0.0

        won_pcts     = []
        stopped      = 0
        unrealized   = 0     # was 'inconc'; renamed locally for clarity
        gross_wins   = 0.0
        gross_losses = 0.0
        pnls         = []

        # UNREALIZED parallel equity walk (r05 260521)
        u_equity     = seed
        u_peak       = seed
        u_max_dd     = 0.0
        u_pnls       = []
        u_max_pcts   = []

        for s in signals:
            mp  = float(s['max_pct']) if s['max_pct'] is not None else None
            bts = s['bts']

            if bts is not None:
                # RESOLVED — stop fired at some point during the trade
                if mp is not None and mp >= profit_zone:
                    pnl = mp
                    won_pcts.append(mp)
                    gross_wins += mp
                else:
                    pnl = -stop_pct
                    stopped += 1
                    gross_losses += stop_pct

                pnls.append(pnl)
                equity *= (1.0 + pnl / 100.0)
                peak    = max(peak, equity)
                if peak > 0:
                    dd = (peak - equity) / peak
                    if dd > max_dd:
                        max_dd = dd
            else:
                # UNREALIZED — trade ran off the end of available klines.
                u_pnl = mp if mp is not None else 0.0
                unrealized += 1
                u_pnls.append(u_pnl)
                if mp is not None and mp > 0:
                    u_max_pcts.append(mp)
                u_equity *= (1.0 + u_pnl / 100.0)
                u_peak    = max(u_peak, u_equity)
                if u_peak > 0:
                    u_dd = (u_peak - u_equity) / u_peak
                    if u_dd > u_max_dd:
                        u_max_dd = u_dd

        n     = len(pnls)
        n_won = len(won_pcts)
        arr   = np.array(pnls)
        neg   = arr[arr < 0]

        mean_pnl    = float(arr.mean())             if n   else 0.0
        std_pnl     = float(arr.std(ddof=0))        if n > 1 else 0.0
        std_neg     = float(neg.std(ddof=0))        if len(neg) > 1 else 0.0
        avg_won_pct = float(np.mean(won_pcts))      if won_pcts else 0.0
        min_won_pct = float(np.min(won_pcts))       if won_pcts else 0.0

        decided = n_won + stopped
        win_rate = (n_won / decided) if decided else 0.0

        return {
            'gross_banked':  equity,
            'max_drawdown':  max_dd,
            'profit_factor': (gross_wins / gross_losses) if gross_losses > 0 else float('inf'),
            'sharpe':        (mean_pnl / std_pnl) if std_pnl > 0 else float('inf'),
            'sortino':       (mean_pnl / std_neg) if std_neg > 0 else float('inf'),
            'mean_pnl':      mean_pnl,
            'n_won':         n_won,
            'n_stopped':     stopped,
            'n_inconc':      unrealized,    # alias for n_unrealized (back-compat)
            'n_unrealized':  unrealized,
            'win_rate_walked': win_rate,
            'avg_won_pct_walked': avg_won_pct,
            'min_won_pct':   min_won_pct,
            'win95_flag':    1 if win_rate > 0.95 else 0,
            # UNREALIZED shadow metrics (trades still open at dataset end)
            'unrealized_gross_banked': u_equity,
            'unrealized_max_drawdown': u_max_dd,
            'unrealized_mean_pnl':     float(np.mean(u_pnls)) if u_pnls else 0.0,
            'unrealized_avg_max_pct':  float(np.mean(u_max_pcts)) if u_max_pcts else 0.0,
        }

    def _compute_stage2(self, or_pk: int, stage1: pd.DataFrame,
                        profit_zone: float, stop_pct: float,
                        params: list) -> pd.DataFrame:
        """
        For each Stage 1 combo: pull its signals, walk equity, attach
        metrics. Returns df sorted by gross_banked DESC.
        """
        if stage1.empty:
            return stage1.copy()

        rows = []
        for _, combo in stage1.iterrows():
            signals = self._query_combo_signals(or_pk, combo)
            metrics = self._walk_equity(signals, profit_zone, stop_pct)
            row = {
                'stage1_rank': int(combo['stage1_rank']),
                'expectancy':  float(combo['expectancy']),
                'total':       int(combo['total']),
            }
            for p in params:
                row[p] = combo[p]
            row.update(metrics)
            rows.append(row)

        out = pd.DataFrame(rows)
        out = out.sort_values('gross_banked', ascending=False).reset_index(drop=True)
        out['stage2_rank'] = range(1, len(out) + 1)
        return out

    @staticmethod
    def _apply_dd_filter(stage2: pd.DataFrame, dd_threshold: float):
        """Split stage2 into kept (DD ≤ threshold) and killed (DD > threshold)."""
        if stage2.empty:
            return stage2.copy(), stage2.copy()
        kept   = stage2[stage2['max_drawdown'] <= dd_threshold].copy()
        killed = stage2[stage2['max_drawdown']  > dd_threshold].copy()
        kept   = kept.sort_values('gross_banked', ascending=False).reset_index(drop=True)
        killed = killed.sort_values('gross_banked', ascending=False).reset_index(drop=True)
        return kept, killed

    # ── Stage 2 reports ──────────────────────────────────────────────────

    def _report_top_n_v2(self, stage2_kept: pd.DataFrame, n: int,
                         params: list, meta: dict,
                         full_df: pd.DataFrame) -> None:
        """
        Top N by gross_banked from Stage 2 (DD-filtered). Console keeps
        the simple 9-col layout — full picture lives in the CSV.
        """
        self._log.info(f'TOP {n} COMBOS BY gross_banked   (Stage 2, DD ≤ kill switch)')
        self._log.info(self._SEC_LINE)

        line_type = meta.get('og_line_type', 'bb')
        if line_type == 'bb':
            header = (f'  {"#":>3}  {"len":>4} {"mult":>5} {"src":>6}  '
                      f'{"exp%":>7} {"win%":>5} {"avg_won":>7} {"sigs":>5}  '
                      f'{"gross_bank":>11}')
        else:
            header = (f'  {"#":>3}  {"len":>4} {"rsi":>4} {"stc":>4} {"src":>6}  '
                      f'{"exp%":>7} {"win%":>5} {"avg_won":>7} {"sigs":>5}  '
                      f'{"gross_bank":>11}')
        self._log.info(header)

        if stage2_kept.empty:
            self._log.info('  (no combos survived DD filter — see DD audit below)')
            return

        for _, row in stage2_kept.head(n).iterrows():
            flag = ' ⚠' if int(row.get('win95_flag', 0)) == 1 else ''
            if line_type == 'bb':
                core = (
                    f'  {int(row["stage2_rank"]):>3}  '
                    f'{int(row["len"]):>4} '
                    f'{float(row["mult"]):>5.2f} '
                    f'{str(row["src"]):>6}  '
                )
            else:
                core = (
                    f'  {int(row["stage2_rank"]):>3}  '
                    f'{int(row["len"]):>4} '
                    f'{int(row["len_rsi"]):>4} '
                    f'{int(row["len_stoch"]):>4} '
                    f'{str(row["src"]):>6}  '
                )
            metrics = (
                f'{float(row["expectancy"]):>+7.4f} '
                f'{float(row["win_rate_walked"])*100:>5.1f} '
                f'{float(row["avg_won_pct_walked"]):>7.4f} '
                f'{int(row["total"]):>5}  '
                f'${row["gross_banked"]:>9,.0f}{flag}'
            )
            self._log.info(core + metrics)

        # OG line row (existing logic, but compute from full_df since OG
        # might not be in Stage 1/2)
        if meta is not None:
            self._log.info('')
            self._render_og_row_v2(full_df, meta, line_type)
        self._log.info('')

    def _render_og_row_v2(self, df: pd.DataFrame, meta: dict, line_type: str) -> None:
        """Render OG row in the new column format."""
        if line_type == 'bb':
            og_len  = meta.get('og_bb_len')
            og_mult = meta.get('og_bb_mult')
            og_src  = meta.get('og_src')
            if any(v is None for v in (og_len, og_mult, og_src)):
                return
            mask = (
                (df['len'].astype(int) == int(og_len)) &
                ((df['mult'].astype(float) - float(og_mult)).abs() < 0.01) &
                (df['src'] == og_src)
            )
        else:
            og_k   = meta.get('og_k_len')
            og_rsi = meta.get('og_rsi_len')
            og_stc = meta.get('og_stc_len')
            og_src = meta.get('og_src')
            if any(v is None for v in (og_k, og_rsi, og_stc, og_src)):
                return
            mask = (
                (df['len'].astype(int) == int(og_k)) &
                (df['len_rsi'].astype(int) == int(og_rsi)) &
                (df['len_stoch'].astype(int) == int(og_stc)) &
                (df['src'] == og_src)
            )

        og_rows = df[mask]
        if og_rows.empty:
            self._log.info('   og   (no rows match OG line params)')
            return
        best = og_rows.loc[og_rows['expectancy'].idxmax()]

        if line_type == 'bb':
            core = (
                f'  {"og":>3}  '
                f'{int(best["len"]):>4} '
                f'{float(best["mult"]):>5.2f} '
                f'{str(best["src"]):>6}  '
            )
        else:
            core = (
                f'  {"og":>3}  '
                f'{int(best["len"]):>4} '
                f'{int(best["len_rsi"]):>4} '
                f'{int(best["len_stoch"]):>4} '
                f'{str(best["src"]):>6}  '
            )
        # OG row uses expectancy-based metrics (it's from full_df, not Stage 2)
        win = float(best['win_rate']) * 100 if pd.notna(best['win_rate']) else 0
        avg = float(best['avg_win_pct']) if pd.notna(best['avg_win_pct']) else 0
        self._log.info(
            core +
            f'{float(best["expectancy"]):>+7.4f} '
            f'{win:>5.1f} '
            f'{avg:>7.4f} '
            f'{int(best["total"]):>5}  '
            f'{"—":>11}'
        )

    def _report_proven_combo(self, stage2_kept: pd.DataFrame,
                             params: list, profit_zone: float) -> None:
        """PROVEN COMBO = Stage 2 rank #1 after DD filter. Goes before centroid."""
        self._log.info('PROVEN COMBO  (Stage 2 rank #1, DD-qualified)')
        self._log.info(self._SEC_LINE)
        if stage2_kept.empty:
            self._log.info('  No combo passed DD filter.')
            self._log.info('')
            return

        best = stage2_kept.iloc[0]
        # Render all params with their value
        parts = []
        for p in params:
            v = best[p]
            if pd.isna(v):
                continue
            if p == 'mult':
                parts.append(f'{p}={float(v):.2f}')
            elif p == 'slope_floor':
                parts.append(f'{p}={float(v):.1f}')
            elif isinstance(v, (int, np.integer)) or (isinstance(v, float) and v.is_integer()):
                parts.append(f'{p}={int(v)}')
            else:
                parts.append(f'{p}={v}')
        self._log.info(f'  {"   ".join(parts)}')

        flag = ' ⚠ win95'  if int(best.get('win95_flag', 0)) == 1 else ''
        sharpe = best['sharpe']
        sortino = best['sortino']
        pf = best['profit_factor']
        self._log.info(
            f'  expectancy={float(best["expectancy"]):+.4f}%  '
            f'win={float(best["win_rate_walked"])*100:.1f}%  '
            f'signals={int(best["total"])}  '
            f'gross_banked=${best["gross_banked"]:,.0f}'
        )
        self._log.info(
            f'  max_dd={float(best["max_drawdown"])*100:.2f}%  '
            f'PF={self._fmt_inf(pf, "{:.2f}")}  '
            f'Sharpe={self._fmt_inf(sharpe, "{:.3f}")}  '
            f'Sortino={self._fmt_inf(sortino, "{:.3f}")}  '
            f'min_won={float(best["min_won_pct"]):.4f}%'
            f'{flag}'
        )
        self._log.info('')

    def _report_dd_audit(self, stage2_killed: pd.DataFrame,
                         dd_threshold: float) -> None:
        """DD audit: combos that exceeded DD threshold but had top-100 expectancy."""
        self._log.info('DD KILLED  (top-100 expectancy but DD > '
                       f'{dd_threshold*100:.0f}%)')
        self._log.info(self._SEC_LINE)
        self._log.info(
            f'  {"s1_rank":>7}  {"exp%":>7}  {"gross_bank":>11}  '
            f'{"max_dd":>6}  {"sigs":>5}'
        )
        for _, row in stage2_killed.head(20).iterrows():
            self._log.info(
                f'  {int(row["stage1_rank"]):>7}  '
                f'{float(row["expectancy"]):>+7.4f}  '
                f'${row["gross_banked"]:>9,.0f}  '
                f'{float(row["max_drawdown"])*100:>5.2f}%  '
                f'{int(row["total"]):>5}'
            )
        if len(stage2_killed) > 20:
            self._log.info(f'  ... +{len(stage2_killed)-20} more in CSV')
        self._log.info('')

    def _write_stage2_csv(self, stage2: pd.DataFrame, path: str) -> None:
        """Write top 100 Stage 2 results with full metrics to CSV."""
        if stage2.empty:
            stage2.to_csv(path, index=False)
            return
        # Convert inf to NaN for cleaner CSV
        df = stage2.copy()
        for col in ('sharpe', 'sortino', 'profit_factor'):
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        df.to_csv(path, index=False)

    @staticmethod
    def _fmt_inf(v, fmt: str) -> str:
        """Format with handling for inf (returns '∞')."""
        try:
            v = float(v)
            if not np.isfinite(v):
                return '∞'
            return fmt.format(v)
        except (TypeError, ValueError):
            return '—'

    # ── Existing reports below (unchanged from r05) ──────────────────────

    def _report_top_n(self, df: pd.DataFrame, n: int, params: list,
                      meta: dict = None) -> None:
        if df.empty:
            return
        top = df.nlargest(n, 'expectancy')
        self._log.info(f'TOP {n} COMBOS BY EXPECTANCY')
        self._log.info(self._SEC_LINE)
        # Dynamic header — show first 4 params + metrics for column budget
        head_params = params[:4]
        head_cols = '  '.join(f'{p:>8}' for p in head_params)
        self._log.info(
            f'  {"#":>3}  {head_cols}  '
            f'{"exp%":>7}  {"win%":>6}  {"avg_win":>8}  {"sigs":>6}'
        )
        for rank, (_, row) in enumerate(top.iterrows(), 1):
            param_vals = '  '.join(
                f'{self._fmt_param_val(row[p]):>8}' for p in head_params
            )
            self._log.info(
                f'  {rank:>3}  {param_vals}  '
                f'{float(row["expectancy"]):>+7.4f}'
                f'  {float(row["win_rate"])*100:>5.1f}%'
                f'  {float(row["avg_win_pct"]) if pd.notna(row["avg_win_pct"]) else 0.0:>7.4f}%'
                f'  {int(row["total"]):>6}'
            )

        # r05: append a row for the OG line settings, so the report shows
        # how the original line stacks up against the top 20. Pool params
        # drift to whatever optimum exists in the grid — this answers
        # "the OG line at its best, regardless of pool".
        if meta is not None:
            self._render_og_row(df, meta, head_params)

        self._log.info('')

    def _render_og_row(self, df: pd.DataFrame, meta: dict,
                       head_params: list) -> None:
        """
        Find the best combo where line params match indicator_configs
        OG values and render as a labeled row after the top N.
        """
        line_type = meta.get('og_line_type', 'bb')

        if line_type == 'bb':
            og_len  = meta.get('og_bb_len')
            og_mult = meta.get('og_bb_mult')
            og_src  = meta.get('og_src')
            if og_len is None or og_mult is None or og_src is None:
                return
            og_len  = int(og_len)
            og_mult = float(og_mult)
            mask = (
                (df['len'].astype(int) == og_len) &
                ((df['mult'].astype(float) - og_mult).abs() < 0.01) &
                (df['src'] == og_src)
            )
        else:
            og_k   = meta.get('og_k_len')
            og_rsi = meta.get('og_rsi_len')
            og_stc = meta.get('og_stc_len')
            og_src = meta.get('og_src')
            if any(v is None for v in (og_k, og_rsi, og_stc, og_src)):
                return
            mask = (
                (df['len'].astype(int) == int(og_k)) &
                (df['len_rsi'].astype(int) == int(og_rsi)) &
                (df['len_stoch'].astype(int) == int(og_stc)) &
                (df['src'] == og_src)
            )

        og_rows = df[mask]
        if og_rows.empty:
            self._log.info('   og   (no rows match OG line params — '
                           'verify indicator_configs values are in the grid)')
            return

        best = og_rows.loc[og_rows['expectancy'].idxmax()]
        param_vals = '  '.join(
            f'{self._fmt_param_val(best[p]):>8}' for p in head_params
        )
        self._log.info(
            f'   og  {param_vals}  '
            f'{float(best["expectancy"]):>+7.4f}'
            f'  {float(best["win_rate"])*100:>5.1f}%'
            f'  {float(best["avg_win_pct"]) if pd.notna(best["avg_win_pct"]) else 0.0:>7.4f}%'
            f'  {int(best["total"]):>6}'
        )

    @staticmethod
    def _fmt_param_val(v) -> str:
        if pd.isna(v):
            return '-'
        if isinstance(v, float):
            return f'{v:.2f}'
        return str(v)

    def _report_baseline(self, meta: dict, params: list) -> None:
        """
        Surface the line's original indicator_configs values for visual
        comparison against the recommended centroid that follows.
        """
        line_label = meta.get('tc_indicator_label', 'unknown')
        self._log.info(f'ORIGINAL LINE ({line_label})')
        self._log.info(self._SEC_LINE)
        line_type = meta.get('og_line_type', 'bb')

        # Build a dict of baseline values keyed the same way as centroid
        baseline = {'src': meta.get('og_src')}
        if line_type == 'bb':
            baseline['len']  = meta.get('og_bb_len')
            baseline['mult'] = float(meta['og_bb_mult']) if meta.get('og_bb_mult') is not None else None
        else:  # 'k'
            baseline['len']       = meta.get('og_k_len')
            baseline['len_rsi']   = meta.get('og_rsi_len')
            baseline['len_stoch'] = meta.get('og_stc_len')

        # Render only the params that are also in this grind's discovered set
        # (so the line aligns with the centroid line below)
        parts = []
        for p in params:
            v = baseline.get(p)
            if v is None:
                parts.append(f'{p}=—')   # not in indicator_configs (e.g., pool_c)
            elif isinstance(v, float):
                parts.append(f'{p}={v:g}')
            else:
                parts.append(f'{p}={v}')
        self._log.info(f'  {"   ".join(parts)}')
        self._log.info('')

    def _compute_centroid(self, df: pd.DataFrame, n: int, params: list,
                          param_types: dict) -> dict:
        """
        Top-N expectancy-weighted centroid of a combo dataframe.

        Numeric int params round to int; float params round to 4dp.
        Categorical params resolve to the weighted mode.
        """
        if df.empty:
            return {}
        top = df.nlargest(n, 'expectancy').copy()
        weights = top['expectancy'].clip(lower=0)
        if weights.sum() == 0:
            weights = pd.Series(1.0, index=top.index)

        centroid = {}
        for param in params:
            ptype = param_types.get(param, 'float')

            if ptype == 'enum':
                centroid[param] = (
                    top.assign(w=weights)
                       .groupby(param)['w']
                       .sum()
                       .idxmax()
                )
            else:
                vals = pd.to_numeric(top[param], errors='coerce')
                # Skip params with all-NaN (shouldn't happen post-discover,
                # but defensive)
                if not vals.notna().any():
                    continue
                val = float((vals * weights).sum() / weights.sum())
                centroid[param] = int(round(val)) if ptype == 'int' else round(val, 4)
        return centroid

    def _report_centroid(self, df: pd.DataFrame, n: int,
                         params: list, param_types: dict) -> None:
        if df.empty:
            return
        centroid = self._compute_centroid(df, n, params, param_types)
        self._log.info(f'RECOMMENDED CENTROID  (top {n} combos, weighted by expectancy)')
        self._log.info(self._SEC_LINE)
        parts = '   '.join(f'{k}={v}' for k, v in centroid.items())
        self._log.info(f'  {parts}')
        self._log.info(self._DIV_LINE)

    # ──────────────────────────────────────────────────────────────────────
    # Compare — side-by-side reporting of 2-4 optimizer runs
    # ──────────────────────────────────────────────────────────────────────

    def compare(self, or_pks: list, output_dir: str = '.') -> str:
        if not 2 <= len(or_pks) <= 4:
            raise ValueError(f'compare requires 2-4 or_pks, got {len(or_pks)}')

        runs = [self._build_run_summary(op) for op in or_pks]
        baseline, target = runs[0], runs[-1]

        self._log.info(self._DIV_LINE)
        self._log.info('  COMPARE — or_pk ' + ' / '.join(str(r['or_pk']) for r in runs))
        self._log.info(self._DIV_LINE)

        self._log.info('')
        self._log.info('CONFIGS')
        for i, r in enumerate(runs):
            marker = ''
            if   i == 0:                marker = '   ← baseline'
            elif i == len(runs) - 1:    marker = '   ← target'
            self._log.info(
                f'  or_pk={r["or_pk"]:<4}   p_rev={r["p_rev"]:<3}  '
                f'pk5s_gate={r["pk5s_gate"]:<3}{marker}'
            )
        self._log.info('')
        self._log.info(self._SEC_LINE)

        # Union of params present across all runs (so the report aligns)
        all_params = []
        seen = set()
        for r in runs:
            for p in r['params']:
                if p not in seen:
                    all_params.append(p)
                    seen.add(p)

        for r in runs:
            self._log.info('')
            self._log.info(
                f'or_pk={r["or_pk"]}  {r["label"]:<14}'
                f'lookback≈{r["lookback_days"]}d'
            )
            self._log.info(f'  signals       {r["signals"]:>12,}')
            self._log.info(
                f'  combos        {r["combos_filtered"]:>12} / {r["combos"]}'
            )
            self._log.info(f'  win_rate      {r["win_rate"]*100:>11.1f}%')
            self._log.info(f'  expectancy    {r["expectancy"]:>+11.3f}%')
            cent = r['centroid']
            cent_parts = '  '.join(
                f'{p}={cent[p]}' for p in all_params if p in cent
            )
            self._log.info(f'  centroid      {cent_parts}')

        self._log.info('')
        self._log.info(self._SEC_LINE)

        self._log.info('')
        self._log.info(f'DELTA — or_pk={target["or_pk"]} vs or_pk={baseline["or_pk"]}')
        self._log.info('')

        if baseline['signals'] > 0:
            ratio = target['signals'] / baseline['signals']
            pct   = (ratio - 1.0) * 100
            self._log.info(f'  signals      ×{ratio:.3f}     ({pct:+.0f}%)')
        wr_delta = (target['win_rate'] - baseline['win_rate']) * 100
        self._log.info(f'  win_rate     {wr_delta:+.2f}pp')
        exp_delta = target['expectancy'] - baseline['expectancy']
        self._log.info(f'  expectancy   {exp_delta:+.3f}%')

        self._log.info('')
        self._log.info('  centroid drift')
        for p in all_params:
            bv = baseline['centroid'].get(p)
            tv = target['centroid'].get(p)
            if bv is None or tv is None:
                continue
            btype = baseline['param_types'].get(p, 'float')
            if btype == 'int':
                delta = int(tv) - int(bv)
                tail = '(—)' if delta == 0 else f'({delta:+d})'
                self._log.info(f'    {p:<12} {int(bv):>5} → {int(tv):<5}  {tail}')
            elif btype == 'enum':
                marker = '(—)' if bv == tv else '(changed)'
                self._log.info(f'    {p:<12} {str(bv):>5} → {str(tv):<5}  {marker}')
            else:
                delta = float(tv) - float(bv)
                tail = '(—)' if abs(delta) < 1e-9 else f'({delta:+.3f})'
                self._log.info(f'    {p:<12} {float(bv):>5.3f} → {float(tv):<5.3f}  {tail}')

        self._log.info('')
        self._log.info(self._SEC_LINE)

        warnings = self._comparison_warnings(runs)
        if warnings:
            self._log.info('')
            self._log.info('WARNINGS')
            for w in warnings:
                self._log.info(f'  • {w}')

        self._log.info('')
        self._log.info(self._DIV_LINE)

        csv_path = self._write_compare_csv(runs, output_dir)
        self._log.info(f'Compare CSV (long format) → {csv_path}')
        return csv_path

    def _build_run_summary(self, or_pk: int) -> dict:
        meta        = self._load_run_meta(or_pk)
        stop_pct    = float(meta['tc_stop_pct'])
        profit_zone = float(meta['tc_profit_zone'])
        raw         = self._load_combo_summaries(or_pk, profit_zone)
        if not raw:
            raise ValueError(f'No combos for or_pk={or_pk}')
        df          = self._enrich(pd.DataFrame(raw), stop_pct)
        params      = self._discover_params(df)
        param_types = self._load_param_types(int(meta['or_tc_pk']))
        filtered    = df[df['decided'] >= 30].copy()

        span_rows = self._db.execute(
            '''SELECT MIN(pks_timestamp) AS mn, MAX(pks_timestamp) AS mx
               FROM pk_signals WHERE pks_or_pk = %s''',
            (or_pk,), fetch=True,
        )
        lookback_days = 0.0
        if span_rows and span_rows[0]['mn'] and span_rows[0]['mx']:
            lookback_days = round(
                (span_rows[0]['mx'] - span_rows[0]['mn']) / 86_400_000.0, 1
            )

        p_rev = 'on' if meta.get('or_p_rev_enabled')     else 'off'
        pk5s  = 'on' if meta.get('or_pk5s_gate_enabled') else 'off'
        label = self._COMPARE_LABELS.get((p_rev, pk5s), '')

        summary = {
            'or_pk':           or_pk,
            'tc_pk':           int(meta['or_tc_pk']),
            'completed_at':    meta.get('or_completed_at'),
            'label':           label,
            'p_rev':           p_rev,
            'pk5s_gate':       pk5s,
            'lookback_days':   lookback_days,
            'signals':         int(df['total'].sum()),
            'combos':          len(df),
            'combos_filtered': len(filtered),
            'win_rate':        0.0,
            'expectancy':      0.0,
            'centroid':        {},
            'params':          params,
            'param_types':     param_types,
        }
        if not filtered.empty:
            summary['win_rate']   = float(
                filtered['won'].sum() / max(filtered['decided'].sum(), 1)
            )
            summary['expectancy'] = float(filtered['expectancy'].max())
            summary['centroid']   = self._compute_centroid(
                filtered, 20, params, param_types,
            )
        return summary

    def _comparison_warnings(self, runs: list) -> list:
        out = []
        tc_pks = {r['tc_pk'] for r in runs}
        if len(tc_pks) > 1:
            out.append(
                f'tc_pk mismatch across runs: {sorted(tc_pks)} — '
                f'comparing different calibration targets'
            )
        lookbacks = [r['lookback_days'] for r in runs]
        if lookbacks and (max(lookbacks) - min(lookbacks)) > 0.5:
            out.append(
                f'lookback window varies: {lookbacks} days — '
                f'data volume differs across runs'
            )
        for r in runs:
            if r['combos_filtered'] == 0:
                out.append(
                    f'or_pk={r["or_pk"]}: no combos met min_signals=30 — '
                    f'centroid and win rate not meaningful'
                )
            if r.get('completed_at') is None:
                out.append(
                    f'or_pk={r["or_pk"]}: or_completed_at is NULL — '
                    f'run may be incomplete; results may be partial'
                )
        return out

    def _write_compare_csv(self, runs: list, output_dir: str) -> str:
        rows = []
        for r in runs:
            common = {
                'or_pk':         r['or_pk'],
                'label':         r['label'],
                'p_rev':         r['p_rev'],
                'pk5s_gate':     r['pk5s_gate'],
                'lookback_days': r['lookback_days'],
            }
            for k in ('signals', 'combos', 'combos_filtered',
                      'win_rate', 'expectancy'):
                rows.append({**common,
                             'metric_class': 'summary',
                             'metric_name':  k,
                             'value':        r[k]})
            for k, v in r['centroid'].items():
                rows.append({**common,
                             'metric_class': 'centroid',
                             'metric_name':  k,
                             'value':        v})

        or_pks_str = '_'.join(str(r['or_pk']) for r in runs)
        path = f'{output_dir}/compare_{or_pks_str}.csv'
        pd.DataFrame(rows).to_csv(path, index=False)
        return path


# ─── Multiprocessing worker (module-level for pickle compatibility) ─────────
def _analyze_one_worker(args: tuple) -> str:
    """
    Worker process for analyze_many(parallel=N). Each process opens its
    own DB connection, runs analyze for one or_pk, then disconnects.
    Module-level (not method) because multiprocessing.Pool requires
    picklable callables.
    """
    import os
    or_pk, kwargs = args
    db = DatabaseManager(
        host     = os.environ.get('PK_DB_HOST', 'localhost'),
        user     = os.environ.get('PK_DB_USER', 'root'),
        password = os.environ.get('PK_DB_PASS', 'yourpassword'),
        database = os.environ.get('PK_DB_NAME', 'pk_optimizer'),
        port     = int(os.environ.get('PK_DB_PORT', 3306)),
    )
    db.connect()
    try:
        return AnalyzeManager(db).run(or_pk, **kwargs)
    except Exception:
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.disconnect()


# ─── CLI entry point ────────────────────────────────────────────────────────
if __name__ == '__main__':
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description='Re-analyze existing optimizer_runs through the AM v2 '
                    'two-stage ranker. Reads pk_signals/pk_outcomes only — '
                    'no re-grinding.'
    )
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument('--or_pk',  type=int, help='single or_pk to analyze')
    grp.add_argument('--or_pks', type=str,
                     help='comma-separated or_pks for batch, '
                          'e.g. --or_pks=20,21,22,17,18,19')
    parser.add_argument('--output_dir',   type=str,   default='.')
    parser.add_argument('--min_signals',  type=int,   default=30)
    parser.add_argument('--top_n',        type=int,   default=20)
    parser.add_argument('--top_stage1',   type=int,   default=100)
    parser.add_argument('--dd_threshold', type=float, default=0.15)
    parser.add_argument('--parallel',     type=int,   default=1,
                        help='Number of parallel worker processes '
                             '(default 1). Use 6 for the standard 6-or_pk '
                             'batch on a 16-core machine.')
    parser.add_argument('--emit_pine',    action='store_true',
                        help='After analysis completes, emit Pine v6 '
                             'strategy for the PROVEN combo of each or_pk.')
    args = parser.parse_args()

    or_pks = ([args.or_pk] if args.or_pk is not None
              else [int(p) for p in args.or_pks.split(',')])

    db = DatabaseManager(
        host     = os.environ.get('PK_DB_HOST', 'localhost'),
        user     = os.environ.get('PK_DB_USER', 'root'),
        password = os.environ.get('PK_DB_PASS', 'yourpassword'),
        database = os.environ.get('PK_DB_NAME', 'pk_optimizer'),
        port     = int(os.environ.get('PK_DB_PORT', 3306)),
    )
    db.connect()
    try:
        AnalyzeManager(db).analyze_many(
            or_pks,
            parallel=args.parallel,
            min_signals=args.min_signals,
            top_n=args.top_n,
            top_stage1=args.top_stage1,
            dd_threshold=args.dd_threshold,
            output_dir=args.output_dir,
        )

        if args.emit_pine:
            from ..emit.pine_strategy_emitter import PineStrategyEmitter
            emitter = PineStrategyEmitter(db)
            for or_pk in or_pks:
                emitter.emit(or_pk, output_dir=args.output_dir)
    finally:
        db.disconnect()
