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

    # Sweep dimensions that can appear in pk_signals. Order matters only
    # for report presentation; missing/NULL columns are filtered downstream.
    _CANDIDATE_PARAMS = [
        'len', 'mult', 'len_rsi', 'len_stoch', 'src',
        'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier',
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
            output_dir: str = '.') -> str:

        run_meta    = self._load_run_meta(or_pk)
        stop_pct    = float(run_meta['tc_stop_pct'])
        profit_zone = float(run_meta['tc_profit_zone'])
        raw         = self._load_combo_summaries(or_pk, profit_zone)

        if not raw:
            self._log.error(f'No results found for or_pk={or_pk}')
            return ''

        df = pd.DataFrame(raw)
        df = self._enrich(df, stop_pct)

        # Discover which sweep params are populated for this run.
        # Any candidate column that's all-NULL gets pruned.
        params_present = self._discover_params(df)

        # Load int/float/enum classification from test_param_ranges for centroid math
        param_types = self._load_param_types(int(run_meta['or_tc_pk']))

        # Filter to combos with enough decided trades
        filtered = df[df['decided'] >= min_signals].copy()

        self._report_overview(df, filtered, run_meta)
        self._report_sensitivity(filtered, params_present)
        self._report_top_n(filtered, top_n, params_present, run_meta)
        self._report_baseline(run_meta, params_present)
        self._report_centroid(filtered, top_n, params_present, param_types)

        path = f'{output_dir}/analysis_or{or_pk}.csv'
        df.to_csv(path, index=False)
        self._log.info(f'Full combo summary → {path}')
        return path

    # ── data loading ──────────────────────────────────────────────────────────

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
        # r05: 'won' counts any trade that reached profit_zone regardless
        # of whether stop later fired (in real trading the position closes
        # at profit). 'stopped_ct' excludes those wins. 'inconclusive_ct'
        # excludes them too. The three are mutually exclusive and sum to
        # total. 'decided' = won + stopped_ct is computed in _enrich.
        # Bug fix from r04 where SQL's `decided` undercounted won-but-not-
        # stopped trades, producing win_rate > 100%.
        return self._db.execute(
            '''SELECT
                   s.pks_len        AS len,
                   s.pks_mult       AS mult,
                   s.pks_len_rsi    AS len_rsi,
                   s.pks_len_stoch  AS len_stoch,
                   s.pks_src        AS src,
                   s.pks_pool_c     AS pool_c,
                   s.pks_pool_w     AS pool_w,
                   s.pks_pool_range AS pool_range,
                   s.pks_slope_floor AS slope_floor,
                   s.pks_multiplier  AS multiplier,
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
                        s.pks_slope_floor, s.pks_multiplier''',
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
        self._log.info(f'  Overall win rate     : {baseline_wr:>9.1f}%  ← baseline to beat')

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
