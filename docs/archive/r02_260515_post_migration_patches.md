# 260515 — optimus9 post-migration patches

Applied **after** `python3 migrate.py --commit` succeeds. These additions target the new package files (`optimus9/analysis/analyze_manager.py` and `optimus9/orchestration/report_manager.py`), which are much smaller than the original `managers.py` — each find-and-replace operates on a focused single-responsibility file.

Apply in order. After all three sections, run:

```bash
pytest                                                # all tests should pass
python3 run.py compare --or_pks 1 4                   # try the new command
python3 run.py smoke --tc_pk 1 --lookback_days 1      # full pipeline sanity
```

---

## 1. AnalyzeManager — int-aware centroid + _compute_centroid extraction

In `optimus9/analysis/analyze_manager.py`.

### 1a. Add `_INT_PARAMS` class attribute

**Find** the class attributes block:

```python
    _NUMERIC_PARAMS = ['len', 'mult', 'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier']
    _CAT_PARAMS     = ['src']
```

**Replace with:**

```python
    _NUMERIC_PARAMS = ['len', 'mult', 'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier']
    _CAT_PARAMS     = ['src']
    # Params that must be ints — no fractional grid points exist. Used by
    # _compute_centroid to round these to int rather than 4dp.
    _INT_PARAMS     = {'len', 'pool_c', 'pool_w', 'pool_range', 'multiplier'}
```

### 1b. Extract `_compute_centroid`, refactor `_report_centroid` to delegate

**Find** the existing `_report_centroid` method:

```python
    def _report_centroid(self, df: pd.DataFrame, n: int) -> None:
        if df.empty:
            return
        top = df.nlargest(n, 'expectancy').copy()

        # Guard: use uniform weights if all expectancy values are identical or negative
        weights = top['expectancy'].clip(lower=0)
        if weights.sum() == 0:
            weights = pd.Series(1.0, index=top.index)

        self._log.info(f'RECOMMENDED CENTROID  (top {n} combos, weighted by expectancy)')
        self._log.info(self._SEC_LINE)

        centroid = {}
        for param in self._NUMERIC_PARAMS:
            if param not in top.columns:
                continue
            vals = pd.to_numeric(top[param], errors='coerce')
            centroid[param] = round(float((vals * weights).sum() / weights.sum()), 4)

        # Categorical: weighted mode
        for param in self._CAT_PARAMS:
            if param not in top.columns:
                continue
            centroid[param] = (
                top.assign(w=weights)
                   .groupby(param)['w']
                   .sum()
                   .idxmax()
            )

        parts = '   '.join(f'{k}={v}' for k, v in centroid.items())
        self._log.info(f'  {parts}')
        self._log.info(self._DIV_LINE)
```

**Replace with:**

```python
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
```

### 1c. Add compare workflow

Append the following block as new methods on `AnalyzeManager`, before the class's closing line / module-level helpers.

```python
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
```

---

## 2. ReportManager — stamp `or_completed_at` on success

In `optimus9/orchestration/report_manager.py`.

The `or_completed_at` column has been in the schema since day one but nothing populates it. Compare's warnings block now surfaces NULL values as "run may be incomplete." Stamp completion at the end of `run()` so future runs are queryable as definitively-finished.

**Find** the end of `ReportManager.run()` — typically the last few lines look like:

```python
        OptimizerRunner(
            self._db,
            PKDetector(float(config['ic_high_boundary']), float(config['ic_low_boundary'])),
            SwingAnalyzer(float(config['tc_stop_pct']), int(config['tc_max_bars']),
                          float(config.get('tc_drag_pct', 0.0))),
        ).run(or_pk, base_df, ind_df, dema, oob_side, grid, config,
              p_rev_enabled=p_rev_enabled)

        if export_csv:
            ...
```

**Replace with** (add the UPDATE after `OptimizerRunner.run` returns, before any export):

```python
        OptimizerRunner(
            self._db,
            PKDetector(float(config['ic_high_boundary']), float(config['ic_low_boundary'])),
            SwingAnalyzer(float(config['tc_stop_pct']), int(config['tc_max_bars']),
                          float(config.get('tc_drag_pct', 0.0))),
        ).run(or_pk, base_df, ind_df, dema, oob_side, grid, config,
              p_rev_enabled=p_rev_enabled)

        # Stamp completion. Rows with NULL or_completed_at = aborted /
        # in-progress; compare's warnings block surfaces this so partial
        # results don't quietly contaminate side-by-side analysis.
        self._db.execute(
            'UPDATE optimizer_runs SET or_completed_at = NOW() WHERE or_pk = %s',
            (or_pk,),
        )

        if export_csv:
            ...
```

---

## 3. Verification

After applying both sections:

```bash
# All tests should pass now
pytest

# Quick smoke — pipeline + analyser
python3 run.py smoke --tc_pk 1 --lookback_days 1

# Compare two runs (use real or_pks from your DB)
python3 run.py compare --or_pks 1 5
```

The compare output should now show `or_completed_at` warnings flag any historically-incomplete rows. After running `optimus9_data_cleanup.sql` (separate file), or_pk=1 should be correctly labeled as `baseline` (off / off).

If `pytest` reports any failures, re-read the failing test's docstring — most likely cause is a typo during patch application. Tests are intentionally narrow so failures point cleanly at what's wrong.
