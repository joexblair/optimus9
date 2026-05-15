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
    All heavy lifting stays in the DB — Python only sees ~3,150 combo summary rows.

    Outputs:
      - Console / info.log: full analysis report
      - CSV: combo summary with all metrics (for further exploration)
    """

    _NUMERIC_PARAMS = ['len', 'mult', 'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier']
    _CAT_PARAMS     = ['src']
    # Params that must be ints — no fractional grid points exist. Used by
    # _compute_centroid to round these to int rather than 4dp.
    _INT_PARAMS     = {'len', 'pool_c', 'pool_w', 'pool_range', 'multiplier'}

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def run(self, or_pk: int, min_signals: int = 30, top_n: int = 20,
            output_dir: str = '.') -> str:

        run_meta  = self._load_run_meta(or_pk)
        stop_pct  = float(run_meta['tc_stop_pct'])
        raw       = self._load_combo_summaries(or_pk)

        if not raw:
            self._log.error(f'No results found for or_pk={or_pk}')
            return ''

        df = pd.DataFrame(raw)
        df = self._enrich(df, stop_pct)

        # Filter to combos with enough decided trades
        filtered = df[df['decided'] >= min_signals].copy()

        self._report_overview(df, filtered, run_meta)
        self._report_sensitivity(filtered)
        self._report_top_n(filtered, top_n)
        self._report_centroid(filtered, top_n)

        path = f'{output_dir}/analysis_or{or_pk}.csv'
        df.to_csv(path, index=False)
        self._log.info(f'Full combo summary → {path}')
        return path

    # ── data loading ──────────────────────────────────────────────────────────

    def _load_run_meta(self, or_pk: int) -> dict:
        rows = self._db.execute(
            '''SELECT r.*, tc.tc_stop_pct, tc.tc_indicator_label,
                      tc.tc_dema_len, tc.tc_dema_src
               FROM optimizer_runs r
               JOIN test_configs tc ON tc.tc_pk = r.or_tc_pk
               WHERE r.or_pk = %s''',
            (or_pk,), fetch=True,
        )
        if not rows:
            raise ValueError(f'No optimizer_run for or_pk={or_pk}')
        return rows[0]

    def _load_combo_summaries(self, or_pk: int) -> list:
        return self._db.execute(
            '''SELECT
                   s.pks_len        AS len,
                   s.pks_mult       AS mult,
                   s.pks_src        AS src,
                   s.pks_pool_c     AS pool_c,
                   s.pks_pool_w     AS pool_w,
                   s.pks_pool_range AS pool_range,
                   s.pks_slope_floor AS slope_floor,
                   s.pks_multiplier  AS multiplier,
                   COUNT(*)                                                           AS total,
                   SUM(o.pko_result IN ('won','stopped'))                             AS decided,
                   SUM(o.pko_result = 'won')                                         AS won,
                   SUM(o.pko_result = 'stopped')                                     AS stopped_ct,
                   SUM(o.pko_result = 'inconclusive')                                AS inconclusive_ct,
                   AVG(CASE WHEN o.pko_result = 'won' THEN o.pko_max_profit_pct END) AS avg_win_pct,
                   AVG(o.pko_bars_to_stop)                                            AS avg_bars,
                   AVG(o.pko_bars_to_max_profit)                                      AS avg_bars_peak
               FROM pk_signals s
               JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               WHERE s.pks_or_pk = %s
               GROUP BY s.pks_len, s.pks_mult, s.pks_src,
                        s.pks_pool_c, s.pks_pool_w, s.pks_pool_range,
                        s.pks_slope_floor, s.pks_multiplier''',
            (or_pk,), fetch=True,
        )

    # ── enrichment ────────────────────────────────────────────────────────────

    def _enrich(self, df: pd.DataFrame, stop_pct: float) -> pd.DataFrame:
        df = df.copy()
        for col in ['total', 'decided', 'won', 'stopped_ct', 'inconclusive_ct']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        for col in ['avg_win_pct', 'avg_bars', 'avg_bars_peak']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # When a combo has zero wins, avg_win_pct is NaN (mean over empty subset).
        # Coerce to 0 so expectancy collapses to -stop_pct rather than NaN —
        # the correct value when every signal stops out. Without this, idxmax
        # downstream raises "Encountered all NA values" on a degenerate day.
        df['avg_win_pct'] = df['avg_win_pct'].fillna(0.0)
        
        df['win_rate']         = df['won'] / df['decided'].replace(0, float('nan'))
        df['inconclusive_rate'] = df['inconclusive_ct'] / df['total'].replace(0, float('nan'))
        # expectancy in % per trade: E = win_rate × avg_win - loss_rate × stop
        df['expectancy']       = (
            df['win_rate'] * df['avg_win_pct']
            - (1.0 - df['win_rate']) * stop_pct
        )
        return df

    # ── report sections ───────────────────────────────────────────────────────

    def _report_overview(self, df: pd.DataFrame, filtered: pd.DataFrame, meta: dict) -> None:
        total_signals = int(df['total'].sum())
        days_approx   = total_signals / (17_280 * len(df))  # rough: signals per 5s bar
        baseline_wr   = float(df['won'].sum() / max(df['decided'].sum(), 1) * 100)

        self._log.info(self._DIV_LINE)
        self._log.info(
            f'  PK GRINDER — ANALYSIS   or_pk={meta["or_pk"]}'
            f'   {meta["tc_indicator_label"]}'
        )
        # Round 260514: surface the two new run flags so output is self-
        # describing. Defaults to "?" if columns are absent (pre-260514 runs).
        p_rev = meta.get('or_p_rev_enabled')
        pk5s  = meta.get('or_pk5s_gate_enabled')
        if p_rev is not None or pk5s is not None:
            self._log.info(
                f'  Run config: p_rev={"on" if p_rev else "off"}'
                f'   pk5s_gate={"on" if pk5s else "off"}'
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

    def _report_sensitivity(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        self._log.info('PER-PARAM SENSITIVITY  (avg expectancy across combos per value)')
        self._log.info(self._SEC_LINE)

        for param in self._NUMERIC_PARAMS + self._CAT_PARAMS:
            if param not in df.columns:
                continue
            grp = (df.groupby(param)['expectancy']
                     .agg(['mean', 'count'])
                     .reset_index()
                     .sort_values(param))
            parts = '   '.join(
                f'{row[param]}={float(row["mean"]):+.4f}%'
                for _, row in grp.iterrows()
            )
            self._log.info(f'  {param:<12}  {parts}')

        self._log.info('')

    def _report_top_n(self, df: pd.DataFrame, n: int) -> None:
        if df.empty:
            return
        top = df.nlargest(n, 'expectancy')
        self._log.info(f'TOP {n} COMBOS BY EXPECTANCY')
        self._log.info(self._SEC_LINE)
        self._log.info(
            f'  {"#":>3}  {"len":>3}  {"mult":>5}  {"src":<6}'
            f'  {"pc":>3}  {"pw":>3}  {"pr":>3}'
            f'  {"exp%":>7}  {"win%":>6}  {"avg_win":>8}  {"sigs":>6}'
        )
        for rank, (_, row) in enumerate(top.iterrows(), 1):
            self._log.info(
                f'  {rank:>3}  {int(row["len"]):>3}  {float(row["mult"]):>5.2f}'
                f'  {str(row["src"]):<6}'
                f'  {int(row["pool_c"]):>3}  {int(row["pool_w"]):>3}  {int(row["pool_range"]):>3}'
                f'  {float(row["expectancy"]):>+7.4f}'
                f'  {float(row["win_rate"])*100:>5.1f}%'
                f'  {float(row["avg_win_pct"]) if pd.notna(row["avg_win_pct"]) else 0.0:>7.4f}%'
                f'  {int(row["total"]):>6}'
            )
        self._log.info('')

    def _compute_centroid(self, df: pd.DataFrame, n: int = 20) -> dict:
        """
        Top-N expectancy-weighted centroid of a combo dataframe.

        Numeric params in _INT_PARAMS round to int (a centroid value of
        18.25 for `len` is meaningless — no grid point exists there).
        Other numeric params round to 4dp. Categorical params resolve to
        the weighted mode.

        Returns {} for empty input. Falls back to uniform weights when all
        expectancies are non-positive (preserves the original guard).
        """
        if df.empty:
            return {}
        top = df.nlargest(n, 'expectancy').copy()
        weights = top['expectancy'].clip(lower=0)
        if weights.sum() == 0:
            weights = pd.Series(1.0, index=top.index)

        centroid = {}
        for param in self._NUMERIC_PARAMS:
            if param not in top.columns:
                continue
            vals = pd.to_numeric(top[param], errors='coerce')
            val  = float((vals * weights).sum() / weights.sum())
            centroid[param] = int(round(val)) if param in self._INT_PARAMS \
                              else round(val, 4)

        for param in self._CAT_PARAMS:
            if param not in top.columns:
                continue
            centroid[param] = (
                top.assign(w=weights)
                   .groupby(param)['w']
                   .sum()
                   .idxmax()
            )
        return centroid

    def _report_centroid(self, df: pd.DataFrame, n: int) -> None:
        """Single-run centroid log path. Math lives in _compute_centroid."""
        if df.empty:
            return
        centroid = self._compute_centroid(df, n)
        self._log.info(f'RECOMMENDED CENTROID  (top {n} combos, weighted by expectancy)')
        self._log.info(self._SEC_LINE)
        parts = '   '.join(f'{k}={v}' for k, v in centroid.items())
        self._log.info(f'  {parts}')
        self._log.info(self._DIV_LINE)

    # ──────────────────────────────────────────────────────────────────────
    # Compare — side-by-side reporting of 2-4 optimizer runs
    #
    # Added 260515. Portrait layout (vertical block per run), pivot-friendly
    # long-format CSV output. Reuses _load_run_meta / _load_combo_summaries /
    # _enrich / _compute_centroid so the per-run math is identical to a
    # single-run report. First or_pk is the baseline; last is the target.
    # Delta block computes target − baseline.
    # ──────────────────────────────────────────────────────────────────────

    # Auto-labels keyed on (p_rev, pk5s_gate) flag tuple
    _COMPARE_LABELS = {
        ('off', 'off'): 'baseline',
        ('on',  'off'): 'p_rev only',
        ('off', 'on'):  'gate only',
        ('on',  'on'):  'production',
    }

    def compare(self, or_pks: list, output_dir: str = '.') -> str:
        """
        Side-by-side comparison of 2-4 optimizer runs.

        Output: portrait console report + long-format CSV at
        {output_dir}/compare_<or_pks_joined>.csv.

        First or_pk in the list is the baseline; the last is the target.
        Centroid drift is reported target − baseline; intermediate runs
        appear in the per-run blocks but not in the delta calculation.
        """
        if not 2 <= len(or_pks) <= 4:
            raise ValueError(f'compare requires 2-4 or_pks, got {len(or_pks)}')

        runs = [self._build_run_summary(op) for op in or_pks]
        baseline, target = runs[0], runs[-1]

        # ── header ────────────────────────────────────────────────────────
        self._log.info(self._DIV_LINE)
        self._log.info(
            '  COMPARE — or_pk ' + ' / '.join(str(r['or_pk']) for r in runs)
        )
        self._log.info(self._DIV_LINE)

        # ── configs block ─────────────────────────────────────────────────
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

        # ── per-run blocks ────────────────────────────────────────────────
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
            num_parts = '  '.join(
                f'{p}={cent[p]}' for p in self._NUMERIC_PARAMS if p in cent
            )
            self._log.info(f'  centroid      {num_parts}')
            cat_parts = '  '.join(
                f'{p}={cent[p]}' for p in self._CAT_PARAMS if p in cent
            )
            if cat_parts:
                self._log.info(f'                {cat_parts}')

        self._log.info('')
        self._log.info(self._SEC_LINE)

        # ── delta block ───────────────────────────────────────────────────
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
        for p in self._NUMERIC_PARAMS:
            bv = baseline['centroid'].get(p)
            tv = target['centroid'].get(p)
            if bv is None or tv is None:
                continue
            delta = tv - bv
            if p in self._INT_PARAMS:
                tail = '(—)' if delta == 0 else f'({delta:+d})'
                self._log.info(f'    {p:<12} {int(bv):>5} → {int(tv):<5}  {tail}')
            else:
                tail = '(—)' if abs(delta) < 1e-9 else f'({delta:+.3f})'
                self._log.info(f'    {p:<12} {bv:>5.3f} → {tv:<5.3f}  {tail}')

        for p in self._CAT_PARAMS:
            bv = baseline['centroid'].get(p)
            tv = target['centroid'].get(p)
            if bv is None or tv is None:
                continue
            marker = '(—)' if bv == tv else '(changed)'
            self._log.info(f'    {p:<12} {str(bv):>5} → {str(tv):<5}  {marker}')

        self._log.info('')
        self._log.info(self._SEC_LINE)

        # ── warnings ──────────────────────────────────────────────────────
        warnings = self._comparison_warnings(runs)
        if warnings:
            self._log.info('')
            self._log.info('WARNINGS')
            for w in warnings:
                self._log.info(f'  • {w}')

        self._log.info('')
        self._log.info(self._DIV_LINE)

        # ── CSV ───────────────────────────────────────────────────────────
        csv_path = self._write_compare_csv(runs, output_dir)
        self._log.info(f'Compare CSV (long format) → {csv_path}')
        return csv_path

    def _build_run_summary(self, or_pk: int) -> dict:
        """
        Load + enrich a single run's combo data into the summary dict that
        compare() consumes. Lookback inferred from the pk_signals time span
        since we don't store lookback explicitly on optimizer_runs.
        """
        meta     = self._load_run_meta(or_pk)
        stop_pct = float(meta['tc_stop_pct'])
        raw      = self._load_combo_summaries(or_pk)
        if not raw:
            raise ValueError(f'No combos for or_pk={or_pk}')
        df       = self._enrich(pd.DataFrame(raw), stop_pct)
        filtered = df[df['decided'] >= 30].copy()

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
        }
        if not filtered.empty:
            summary['win_rate']   = float(
                filtered['won'].sum() / max(filtered['decided'].sum(), 1)
            )
            summary['expectancy'] = float(filtered['expectancy'].max())
            summary['centroid']   = self._compute_centroid(filtered, n=20)
        return summary

    def _comparison_warnings(self, runs: list) -> list:
        """Sanity checks: mismatched tc_pk, lookback drift, incomplete runs."""
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
        """
        Long-format CSV for pivoting downstream (Excel pivot / pandas
        pivot_table). Each row = one metric observation for one run.

        Columns:
            or_pk, label, p_rev, pk5s_gate, lookback_days,
            metric_class, metric_name, value

        metric_class:
            'summary'  → signals, combos, combos_filtered, win_rate, expectancy
            'centroid' → len, mult, pool_c, pool_w, pool_range,
                         slope_floor, multiplier, src

        value is mixed dtype (numeric for most, str for categorical `src`);
        consumers cast as needed.

        Pivot example in pandas:
            df_long = pd.read_csv('compare_1_3_5.csv')
            df_wide = df_long.pivot_table(
                index='metric_name', columns='or_pk',
                values='value', aggfunc='first',
            )
        """
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
