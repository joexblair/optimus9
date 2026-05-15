# 260514 — managers.py patches

Small edits to existing classes in `managers.py`. The new code goes into `260514_managers_additions.py`; this doc covers everything else.

Apply in order. Each section is search-replace within the existing file.

---

## 1. PKDetector — docstring update

The 1-bar window discrepancy now has a sibling class (`Pk5sGateComputer`) that matches Pine exactly. Documenting the difference so future readers don't "fix" the discrepancy without understanding the continuity choice.

**Find** (around line 686):

```python
class PKDetector:
    """
    Applies f_pk_state logic across a pre-computed indicator line + DEMA.
    Only emits signals when the combined gate oob_side is non-zero and
    the PK direction matches the gate direction.
    """
```

**Replace with:**

```python
class PKDetector:
    """
    Applies f_pk_state logic across a pre-computed indicator line + DEMA.
    Only emits signals when the combined gate oob_side is non-zero and
    the PK direction matches the gate direction.

    Pine alignment note (260514)
    ---------------------------
    This class's peak-search window is one bar wider than Pine's f_pk_state
    (uses pool_range+1 bars where Pine uses pool_range). Intentionally
    preserved for continuity with the 30-day grind dataset that produced
    the b6M centroid (or_pk=1).

    The newer Pk5sGateComputer matches Pine exactly — its f_pk_state covers
    line[i - upper + 1 : i - lower + 1]. The two classes coexist in this
    round; the discrepancy here will be patched once the next clean centroid
    is locked. See round spec 260514_pk5s_spec.md.
    """
```

---

## 2. ReportManager — load pk_5s extensions

Add a new method alongside `_load_gate_configs`. Place after `_load_gate_configs` (around line 1127), before `_load_klines`.

**Add new method:**

```python
    def _load_pk5s_extensions(self, tc_pk: int) -> list:
        """
        Active pk_5s tce rows for this test_config, with tce_params parsed
        from JSON. Each row has a tce_pk and a tce_params dict ready to feed
        into Pk5sGateComputer.compute(...).

        Returns [] if no active pk_5s extensions exist (gate folding falls
        back to bny30M/p only — the existing OOB-gate-only behaviour).
        """
        rows = self._db.execute(
            '''SELECT tce_pk, tce_params
               FROM test_config_extensions
               WHERE tce_tc_pk     = %s
                 AND tce_type      = 'pk_5s'
                 AND tce_is_active = 1
               ORDER BY tce_sort_order''',
            (tc_pk,), fetch=True,
        )
        # JSON column comes back as str on most pymysql configs; parse if so.
        for r in rows:
            if isinstance(r['tce_params'], (str, bytes)):
                r['tce_params'] = json.loads(r['tce_params'])
        return rows
```

---

## 3. ReportManager.run — accept flags + fold pk_5s gate + record flags

**Find** the method signature (around line 1027):

```python
    def run(self, tc_pk: int, export_csv: bool = True, output_dir: str = '.',
            lookback_days: int = None) -> Optional[str]:
```

**Replace with:**

```python
    def run(self, tc_pk: int,
            export_csv: bool = True, output_dir: str = '.',
            lookback_days: int = None,
            p_rev_enabled: bool = True,
            pk5s_gate_enabled: bool = True) -> Optional[str]:
        """
        Drive a full optimizer run for a test_config.

        Round 260514 changes:
          • p_rev_enabled — when True and the calibration line's TF > 5s,
            OptimizerRunner uses f_bb_lookahead (Pine barmerge.lookahead_on
            equivalent) instead of resample-and-forward-fill. Recorded on
            the optimizer_runs row.
          • pk5s_gate_enabled — when True, active pk_5s test_config_extensions
            rows produce gate arrays via Pk5sGateComputer that fold with
            bny30M/p as a third OOB-equivalent gate. Recorded on the run.

        Both flags default True for production. Toggle for the comparison
        matrix in 260514_pk5s_spec.md.
        """
```

**Find** the optimizer_runs INSERT (around line 1033-1039):

```python
        or_pk = self._db.execute(
            '''INSERT INTO optimizer_runs (or_tc_pk, or_tp_pk, or_timestamp, or_dema_len, or_dema_src)
               VALUES (%s,%s,%s,%s,%s)''',
            (tc_pk, int(config['tc_tp_pk']),
             int(datetime.now(timezone.utc).timestamp() * 1000),
             int(config['tc_dema_len']), config['tc_dema_src']),
        )
```

**Replace with:**

```python
        or_pk = self._db.execute(
            '''INSERT INTO optimizer_runs
                 (or_tc_pk, or_tp_pk, or_timestamp, or_dema_len, or_dema_src,
                  or_p_rev_enabled, or_pk5s_gate_enabled)
               VALUES (%s,%s,%s,%s,%s,%s,%s)''',
            (tc_pk, int(config['tc_tp_pk']),
             int(datetime.now(timezone.utc).timestamp() * 1000),
             int(config['tc_dema_len']), config['tc_dema_src'],
             1 if p_rev_enabled else 0,
             1 if pk5s_gate_enabled else 0),
        )
        self._log.info(f'Run config: p_rev={"on" if p_rev_enabled else "off"}, '
                       f'pk5s_gate={"on" if pk5s_gate_enabled else "off"}')
```

**Find** the gate-loading section (around line 1049-1069):

```python
        # Gate: load active extensions, compute oob_side per gate, fold
        gate_cfgs = self._load_gate_configs(tc_pk)
        if gate_cfgs:
            gate_sides = []
            for gcfg in gate_cfgs:
                gate_df   = IndicatorComputer.resample(base_df, int(gcfg['ic_itf_seconds']))
                oob_raw   = IndicatorComputer.compute_oob_side(gcfg, gate_df)
                oob_align = IndicatorComputer.align_to_base(oob_raw, gate_df, base_df)
                gate_sides.append(oob_align)
                name = f'{gcfg["is_prefix"]}{gcfg["itf_label"]}{gcfg["il_suffix"]}'
                self._log.info(
                    f'Gate {name}: {int((oob_align != 0).sum())} OOB bars'
                    f' ({int((oob_align == 1).sum())} HI / {int((oob_align == -1).sum())} LO)'
                )
            oob_side = IndicatorComputer.fold_gates(gate_sides)
            self._log.info(
                f'Combined gate: {int((oob_side != 0).sum())} OOB bars of {len(base_df)}'
            )
        else:
            self._log.warning('No active gates — all bars valid (no direction constraint)')
            oob_side = np.zeros(len(base_df), dtype=np.int8)
```

**Replace with:**

```python
        # Gates: bny30M/p (existing OOB gates) + optional pk_5s vote machines.
        # All gates fold via OR semantics in IndicatorComputer.fold_gates.
        gate_cfgs = self._load_gate_configs(tc_pk)
        gate_sides = []

        for gcfg in gate_cfgs:
            gate_df   = IndicatorComputer.resample(base_df, int(gcfg['ic_itf_seconds']))
            oob_raw   = IndicatorComputer.compute_oob_side(gcfg, gate_df)
            oob_align = IndicatorComputer.align_to_base(oob_raw, gate_df, base_df)
            gate_sides.append(oob_align)
            name = f'{gcfg["is_prefix"]}{gcfg["itf_label"]}{gcfg["il_suffix"]}'
            self._log.info(
                f'Gate {name}: {int((oob_align != 0).sum())} OOB bars'
                f' ({int((oob_align == 1).sum())} HI / {int((oob_align == -1).sum())} LO)'
            )

        # pk_5s gate extensions
        if pk5s_gate_enabled:
            pk5s_cfgs = self._load_pk5s_extensions(tc_pk)
            for pcfg in pk5s_cfgs:
                pk5s_arr = Pk5sGateComputer(self._db).compute(
                    int(pcfg['tce_pk']), base_df, dema, pcfg['tce_params'],
                    midpoint=(float(config['ic_high_boundary']) +
                              float(config['ic_low_boundary'])) / 2.0,
                )
                gate_sides.append(pk5s_arr.astype(float))
        else:
            self._log.info('pk_5s gate disabled by flag')

        if gate_sides:
            oob_side = IndicatorComputer.fold_gates(gate_sides)
            self._log.info(
                f'Combined gate: {int((oob_side != 0).sum())} OOB bars of {len(base_df)}'
            )
        else:
            self._log.warning('No active gates — all bars valid (no direction constraint)')
            oob_side = np.zeros(len(base_df), dtype=np.int8)
```

**Find** the OptimizerRunner instantiation (around line 1078-1083):

```python
        OptimizerRunner(
            self._db,
            PKDetector(float(config['ic_high_boundary']), float(config['ic_low_boundary'])),
            SwingAnalyzer(float(config['tc_stop_pct']), int(config['tc_max_bars']),
                          float(config.get('tc_drag_pct', 0.0))),
        ).run(or_pk, base_df, ind_df, dema, oob_side, grid, config)
```

**Replace with:**

```python
        OptimizerRunner(
            self._db,
            PKDetector(float(config['ic_high_boundary']), float(config['ic_low_boundary'])),
            SwingAnalyzer(float(config['tc_stop_pct']), int(config['tc_max_bars']),
                          float(config.get('tc_drag_pct', 0.0))),
        ).run(or_pk, base_df, ind_df, dema, oob_side, grid, config,
              p_rev_enabled=p_rev_enabled)
```

---

## 4. OptimizerRunner.run — use f_bb_lookahead when p_rev_enabled

**Find** the method signature (around line 916-922):

```python
    def run(self, or_pk: int,
            base_df:  pd.DataFrame,
            ind_df:   pd.DataFrame,
            dema:     np.ndarray,
            oob_side: np.ndarray,
            param_grid: list,
            config: dict) -> None:
```

**Replace with:**

```python
    def run(self, or_pk: int,
            base_df:  pd.DataFrame,
            ind_df:   pd.DataFrame,
            dema:     np.ndarray,
            oob_side: np.ndarray,
            param_grid: list,
            config: dict,
            p_rev_enabled: bool = False) -> None:
        """
        Drive the parameter grid for one calibration target.

        Round 260514: when p_rev_enabled and the calibration line's TF > 5s,
        compute the indicator line via IndicatorComputer.f_bb_lookahead
        (Pine barmerge.lookahead_on equivalent) instead of the resample +
        forward-fill chain. Returns values that resolve at 5s precision
        against the developing higher-TF bar.

        For 5s-native targets (ind_seconds == 5) p_rev is a no-op — the
        flag is honoured by collapsing to the regular f_bb path since there
        is no higher TF to look ahead on.
        """
```

**Find** the per-combo line-compute (around line 927-931):

```python
        for idx, params in enumerate(param_grid, 1):
            self._log.info(f'[{idx}/{total}]  {params}')
            line_src = IndicatorComputer.build_source(ind_df, params['src'])
            line_raw = IndicatorComputer.f_bb(line_src, int(params['len']), float(params['mult']))
            line     = IndicatorComputer.align_to_base(line_raw, ind_df, base_df)
```

**Replace with:**

```python
        ind_seconds = int(config['ic_itf_seconds'])
        use_lookahead = bool(p_rev_enabled and ind_seconds > 5)
        if use_lookahead:
            self._log.info(f'p_rev active: indicator line via f_bb_lookahead '
                           f'(TF={ind_seconds}s)')

        for idx, params in enumerate(param_grid, 1):
            self._log.info(f'[{idx}/{total}]  {params}')
            if use_lookahead:
                # Pine: request.security(..., barmerge.lookahead_on)
                line = IndicatorComputer.f_bb_lookahead(
                    base_df, ind_seconds,
                    int(params['len']), float(params['mult']), params['src'],
                    float(config['ic_high_boundary']),
                    float(config['ic_low_boundary']),
                )
            else:
                line_src = IndicatorComputer.build_source(ind_df, params['src'])
                line_raw = IndicatorComputer.f_bb(line_src, int(params['len']),
                                                   float(params['mult']))
                line     = IndicatorComputer.align_to_base(line_raw, ind_df, base_df)
```

---

## 5. AnalyzeManager._report_overview — print flag state

**Find** (around line 1554, the overview header block):

```python
        self._log.info(self._DIV_LINE)
        self._log.info(
            f'  PK GRINDER — ANALYSIS   or_pk={meta["or_pk"]}'
            f'   {meta["tc_indicator_label"]}'
        )
        self._log.info(self._DIV_LINE)
```

**Replace with:**

```python
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
```

The `_load_run_meta` SELECT uses `r.*` so the new columns flow through automatically — no change needed there.

---

## 6. AnalyzeManager._enrich — guard avg_win_pct against all-stopped combos

Surfaced from the 260515 smoke (or_pk=4): on a degenerate day where every signal stops out, `avg_win_pct` is NaN (mean over empty subset). NaN propagates through `expectancy = win_rate × avg_win_pct - (1 - win_rate) × stop_pct`, and `_report_overview` crashes on `filtered['expectancy'].idxmax()` with "Encountered all NA values".

**Find** (in `_enrich`, around line 1540-1543):

```python
        for col in ['avg_win_pct', 'avg_bars', 'avg_bars_peak']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        df['win_rate']         = df['won'] / df['decided'].replace(0, float('nan'))
```

**Replace with:**

```python
        for col in ['avg_win_pct', 'avg_bars', 'avg_bars_peak']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # When a combo has zero wins, avg_win_pct is NaN (mean over empty subset).
        # Coerce to 0 so expectancy collapses to -stop_pct rather than NaN — the
        # correct value when every signal stops out. Without this, idxmax in
        # _report_overview raises "Encountered all NA values" on a degenerate
        # day (e.g. small smoke run on adverse market action).
        df['avg_win_pct'] = df['avg_win_pct'].fillna(0.0)

        df['win_rate']         = df['won'] / df['decided'].replace(0, float('nan'))
```

`_report_centroid` already has an all-negative-expectancy guard (uniform weights fallback at line 1640), so no further changes needed downstream.

---

## 7. AnalyzeManager — int-aware centroid rounding

Surfaced 260515. The centroid math rounded everything to 4 decimals, so int params came out fractional (`len=18.25` from `(19+16+20+18)/4`). Meaningless — no grid point at 18.25, and it masks the fact that an all-tied / uniform-weight fallback produced the value.

**Find** the class attributes (around line 1455-1456):

```python
    _NUMERIC_PARAMS = ['len', 'mult', 'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier']
    _CAT_PARAMS     = ['src']
```

**Replace with:**

```python
    _NUMERIC_PARAMS = ['len', 'mult', 'pool_c', 'pool_w', 'pool_range', 'slope_floor', 'multiplier']
    _CAT_PARAMS     = ['src']
    # Params that must be ints (no fractional grid points exist). Used by
    # _compute_centroid to round these to int rather than 4dp.
    _INT_PARAMS     = {'len', 'pool_c', 'pool_w', 'pool_range', 'multiplier'}
```

---

## 8. AnalyzeManager — _compute_centroid + compare()

Adds the compare workflow. The existing `_report_centroid` is refactored to delegate to a new `_compute_centroid` so the math is shared between single-run reports and compare blocks. Then four new methods support `compare`.

### 8a. Replace _report_centroid

**Find** the current `_report_centroid` method (around line 1632-1666):

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

        Numeric params in _INT_PARAMS round to int (a centroid value of 18.25
        for `len` is meaningless — no grid point exists there). Other numeric
        params round to 4dp. Categorical params resolve to the weighted mode.

        Returns {} for empty input. Falls back to uniform weights when all
        expectancies are non-positive (preserves original guard semantics).
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
        """Single-run centroid log path. Delegates math to _compute_centroid."""
        if df.empty:
            return
        centroid = self._compute_centroid(df, n)
        self._log.info(f'RECOMMENDED CENTROID  (top {n} combos, weighted by expectancy)')
        self._log.info(self._SEC_LINE)
        parts = '   '.join(f'{k}={v}' for k, v in centroid.items())
        self._log.info(f'  {parts}')
        self._log.info(self._DIV_LINE)
```

### 8b. Add compare workflow

Add the following block as new methods on `AnalyzeManager`, after `_report_centroid` and before the closing of the class. Suggest right above the final blank lines / `# ─── Helpers ───` divider.

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

    # Auto-labels keyed on (p_rev, pk5s_gate) flag tuple. Falls back to '' if
    # the tuple is unrecognised (defensive, should never hit).
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

        # ── header ───────────────────────────────────────────────────────
        self._log.info(self._DIV_LINE)
        self._log.info(
            '  COMPARE — or_pk ' + ' / '.join(str(r['or_pk']) for r in runs)
        )
        self._log.info(self._DIV_LINE)

        # ── configs block ────────────────────────────────────────────────
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

        # ── per-run blocks ───────────────────────────────────────────────
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

        # ── delta block ──────────────────────────────────────────────────
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

        # ── warnings ─────────────────────────────────────────────────────
        warnings = self._comparison_warnings(runs)
        if warnings:
            self._log.info('')
            self._log.info('WARNINGS')
            for w in warnings:
                self._log.info(f'  • {w}')

        self._log.info('')
        self._log.info(self._DIV_LINE)

        # ── CSV ──────────────────────────────────────────────────────────
        csv_path = self._write_compare_csv(runs, output_dir)
        self._log.info(f'Compare CSV (long format) → {csv_path}')
        return csv_path

    def _build_run_summary(self, or_pk: int) -> dict:
        """
        Load + enrich a single run's combo data into the summary dict that
        compare() consumes. Lookback is inferred from the pk_signals time
        span (we don't store lookback explicitly on optimizer_runs).
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
        """Sanity checks: mismatched tc_pk, mismatched lookback, empty combos."""
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
        consumers cast as needed. Pivot example in pandas:
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

## 9. Data integrity — backfill historical flags

The schema ALTER added `or_p_rev_enabled` / `or_pk5s_gate_enabled` with `DEFAULT 1`. Existing pre-260514 rows now show as `(on, on)` even though those runs predated both features. One-time correction for or_pk=1 (the 30-day grind):

```sql
UPDATE optimizer_runs SET or_p_rev_enabled = 0, or_pk5s_gate_enabled = 0 WHERE or_pk = 1;
```

If you ran any post-schema smokes that should be re-labeled, adjust per row. The patched `ReportManager.run` writes flags explicitly going forward, so the `DEFAULT` value is only relevant for pre-existing rows.

---

## Verification after applying

1. `python3 -c "from managers import Pk5sGateComputer; print(Pk5sGateComputer.__doc__[:200])"` — class imports cleanly.
2. `python3 -c "from managers import IndicatorComputer; print(IndicatorComputer.f_bb_lookahead.__doc__[:200])"` — method present.
3. `python3 run.py smoke --tc_pk 1 --lookback_days 1` — full pipeline against 1 day, 5-combo grid, finishes in seconds, analyser prints `Run config: p_rev=on pk5s_gate=on` in the header.
