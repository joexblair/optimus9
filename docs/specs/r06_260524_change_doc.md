# r06 — gca5m PROVEN + Pine v6 Emit Pipeline

**Period**: 2026-05-22 → 2026-05-24
**Korero (Maori) marker**: 260524

---

## Project Context (durable preamble — preserve in every change doc)

Joe ("Sifu") builds **Optimus9** — parameter optimizer for the BBSTR Pine
strategy on FARTCOINUSDT 5s Bybit futures. WSL2 Ubuntu at
`/mnt/c/Users/Administrator/thecodes/optimus9`. GitHub:
https://github.com/joexblair/optimus9. 16-core. MySQL pk_optimizer DB.

**Goal**: hybrid pilot → full bot. Pine emits signals → webhook → Python places
orders via Bybit API.

**Current milestone**: 5s line calibration → solid foundation for HTF stack
(s18B trend anchor → trend machine verdict).

### Key concepts

- **p-rev**: 5s PK fires → freezes HTF line value as PK anchor. Unifies
  Frame A (5s PnL) and Frame B (HTF compatibility) — same target.
- **"Always a stop"**: trade stops, wins, or runs off dataset end.
  `bars_to_stop=NULL` ⇔ end-of-dataset. `tc_max_bars` deprecated.
- **Series-of-tests-stacked-on-known-good-ancestors**: each TF validated
  against predecessor before becoming the next.
- **5s-foundation-first**: HTF lines can't anchor without 5s PK firing.
- **Canonical output reuse**: AM v2's `analysis_or<N>.csv` is source of truth.
- **Apply-script pattern over diffs**: Python find-and-replace edits,
  idempotent, prints status. Hard-won r05 lesson — git apply diffs caused
  hours of format/transfer failures.

### PM mechanisms (refined this round)

- **PM Suppression** (existing): PM sentinels REDUCE the opposing
  directional bucket. `adj_long = max(0, long_pts − pm_short_wt ×
  pm_suppress_str)`. Default `pm_suppress_str=0.5`.

- **PM Additive** (new — Pine only as of r06; Python in r07 grind):
  per-pool tunable. When a PM sentinel (line + price slopes agree with
  significant magnitude → "trend continuation" state) is produced, the
  matching directional bucket gets `pool_weight × pm_additive_<pool>_str`
  added. Two inputs: `pm_additive_close_str`, `pm_additive_wide_str`.
  Default 0.0 (current behavior). Filed for grind dimensions in r07.

### Vote machine

- 3 buckets: long_pts, short_pts, neutral_pts.
- Ratios scale to 0-10. Threshold 7.5 (production) = 75% dominance required.
- **Dead zone** is the threshold gap: under pm_option_a, long_ratio +
  short_ratio = 10 exactly → neither fires when ratios are between 2.5 and 7.5.
- **Control voter** (Pine): synthetic third voter always votes neutral.
  Inflates `active_w` denominator under pm_option_b. Default weight 0
  (off). Dial up to enforce stronger consensus.
- **Boundaries** (Pine inputs, two distinct concepts):
  - **OOB boundary** (`ic_high_boundary` / `ic_low_boundary`, 85/15):
    the fence. Reserved for future gate emulation in Pine.
  - **RSI domain** (`rsi_ob` / `rsi_os`, 70/30): used by `f_bb` to rescale
    BB% into RSI numeric space; also forms `f_pk_state` midpoint (=50).

### Decision delay

Waits N bars to confirm reversing PK hasn't printed. Opposing PK during
window resets pending direction. Both abandoned (no fire) — Joe confirmed
this is intent ("if there's opposing forces then price is likely sideways").

**Pine note**: production logic always zeros `s5_pk_final` on new direction,
producing an inherent 1-bar lag even at `decision_delay=0`. Pine emitter
fixed in r06 by special-casing `t_decision_delay==0` to fire immediately.

**Passthrough toggle** (Pine, r06): bypasses state machine entirely.
`s5_pk_final = pk_raw`; `fire_long/short` require `pk_raw[1] == 0` for
rapid-flip suppression. Useful for diagnosis and as a baseline AB comparison.

---

## r06 COMPLETED Work

### Python / Grind

- ✅ MAE capture pipeline: `pko_max_adverse_pct` + `pko_bars_to_max_adverse`
  columns added to pk_outcomes. Both `_persist_self_gated` AND `_persist_gated`
  paths updated (the latter was missed initially → all of or_pk=30 had NULL
  MAE → re-grind to or_pk=32 with both paths fixed).

- ✅ gca5m grind (tc_pk=18) configuration:
  - Sweep: len ∈ [6..12], src ∈ {close, hl2, hlc3, hlcc4, ohlc4},
    pool_c ∈ [3..17] step 2, pool_w ∈ [19..35] step 2, pool_range ∈ {6, 8},
    slope_floor ∈ [1..41] step 4
  - Locked: mult=0.74, multiplier=1
  - 55,440 total combos.

- ✅ or_pk=32 PROVEN combo:
  - `len=6 mult=0.74 src=hlcc4 pool_c=5 pool_w=23 pool_range=8 slope_floor=41.0 multiplier=1`
  - 695 signals, 39.0% win, $4,210 gross_banked, max_dd=14.80%
  - min_won_pct=0.6072

- ✅ DD-blocked combo review (CSV exported, 7 DD-OK + 20 DD-killed for
  Pine dial-in testing). Showed slope_floor=21 sweet spot in win%
  but DD-killed under sequential equity walk.

### Config / Infrastructure

- ✅ `optimus9/config.py` module: loads `optimus9_config.json` with env-var
  override. Replaces the hardcoded `'yourpassword'` fallback pattern.
- ✅ `optimus9_config.json.example` template. Added to `.gitignore`.

### Pine v6 Strategy Emit

- ✅ `optimus9/emit/pine_strategy_emitter.py`: `PineStrategyEmitter` class.
  Reads `analysis_or<N>.csv` for PROVEN combo, queries pk_signals +
  pk_outcomes for last 400 PROVEN signals, writes
  `bbstr_or<N>_strategy.pine`.

- ✅ `emit_pine_strategy.py`: standalone CLI.

- ✅ `--emit_pine` flag on `analyze_manager`: combined run.

- ✅ Pine v6 strategy features:
  - `pyramiding=10`, `margin_long=0`, `margin_short=0`,
    `process_orders_on_close=true`
  - Unique entry/exit IDs per signal (`L_N` / `LX_N`, `S_N` / `SX_N`)
  - Per-bar Python truth labels for last 400 signals (open trades only,
    direction-prefixed: `L open | win=X% | dd=Y%`)
  - Three-layer debug bgcolor toggles: line divergence / pk_raw / s5_pk_final
  - Debug table (live vote machine state, toggleable)
  - Manual `f_dema()` (Pine v6 has no native `ta.dema`)
  - Decision delay 0-bar fix (no inherent 1-bar lag)
  - Passthrough toggle (skip decision delay state machine)
  - Control voter input (default 0, off)
  - PM Additive Close/Wide inputs (default 0.0, off — not in grind yet)
  - Separate boundary inputs (OOB 85/15 vs RSI 70/30) — fixes the
    conflation that was causing Python/Pine signal mismatch

- ✅ Gate window export utility (`export_gate_windows.py`): merges
  contiguous gate-open bars into windows; outputs CSV with
  `gate_open_utc`, `gate_close_utc`, `duration_seconds` columns.

### Documentation

- ✅ r06_260523_combo_dial_in.csv — 27 combos sorted for Pine UI testing
- ✅ r06_260522_fib_design_note.md — FIB validation Phase 1+2 design
- ✅ r06_260524_change_doc.md — this document

---

## r06 DECISIONS

### Vote machine semantics

- **Threshold default = 7.5** (production), not 7.0.
- **pm_option_a default = false** in Pine strategy (uses pm_option_b so
  the control voter has effect when dialed up). Production grind used
  pm_option_a; this is an intentional Pine-only divergence with safe
  defaults.

### Pine strategy entry/exit

- Each fire gets a unique ID. Exit IDs prefixed `LX_` / `SX_` for visual
  matching with `L_` / `S_` entries in TradingView.

### Pine hedge mode

- Pine doesn't natively support true hedge mode. Strategy uses pyramiding
  + unique IDs which stacks same-direction entries; opposing entries
  net-close per Pine's standard model. Acceptable for AB testing. Real
  hybrid pilot deployment will use Python's Bybit integration for actual
  hedging — Pine emits alerts only.

### Pine TP/SL

- TP = 0.95 × min_won_pct (was 0.99; Joe's call: "at 99% the TP value is
  practically the same")
- SL = tc_stop_pct from test_configs (0.4% for tc_pk=18)

---

## r06 OPEN ITEMS (parked for r07)

### Architectural

- **Consolidate `_persist_self_gated` and `_persist_gated`** into single
  shared persistence method. Duplication was what allowed the MAE-miss
  bug to slip through.

- **ParameterGridBuilder yield-per-combo**: current `build()` materializes
  the full combo list in memory. OOM-killed during or_pk=32 grind at
  combo 47520/47520. Convert to generator.

- **Sortino fix**: 1e-10 denominator threshold to prevent the
  `Sortino=7987390474373178` blow-up when very few losing trades.

- **DD model under HTF-gated execution**: AM v2's `_walk_equity`
  sequentially compounds; over-penalizes high-frequency combos that
  may be excellent HTF confirmation sources. Filed for redesign.

- **Two-stage vote evaluation**: separate "loudness" (stage 1, denominator
  includes control) from "dominance" (stage 2, directional split only).
  Two thresholds. Grind-test whether two-stage produces cleaner PROVEN
  combos than single-stage. Worth exploring given Joe's note that the
  OG Pine grind never dialed in cleanly — single-stage may be the
  structural limitation.

### Data Management

- **Archive util to slower SSD** (Option D from r06 disk discussion):
  After each grind completes and analyze runs, export pk_signals +
  pk_outcomes for that or_pk to compressed CSV on `/mnt/archive/optimus9/`,
  then DELETE from MySQL. Keep `analysis_or<N>.csv` online. Disk audit
  showed pk_signals + pk_outcomes = 99.8% of DB volume.

- **Per-or_pk table sharding** (longer-term): if archive util becomes
  insufficient, split pk_signals into `pk_signals_or<N>` tables per
  optimizer run. Easier archiving (file-level moves), still queryable.

### Grind Dimensions

- **PM additive grind**: sweep `pm_additive_close_str` and
  `pm_additive_wide_str` (0.0 to 1.0). Probably option-C compromise:
  close sweep [0.0, 0.25, 0.5, 0.75, 1.0], wide locked at 0.5 (or
  symmetric inverse) → 5x combo multiplier (~280K combos at current
  grind size). Done as separate grind, NOT folded into the main one.

- **🆕 bny30 gate tuning as precursor (r07/r08 milestone)**: 
  
  The gates shape the dataset before line-pattern recognition runs.
  Today the gate config is fixed in the tce and every combo evaluates
  against the same gate. Tuning the gate AFTER finding a PROVEN line
  combo would optimize pattern recognition against a possibly-wrong
  dataset. Tuning the gate AS A PRECURSOR sanitizes the dataset for
  everything downstream.
  
  **Design sketch**:
  - New milestone: tc_pk for bny30M/p gate tuning
  - Sweep bny30M and bny30p indicator parameters (len, mult, src,
    high_boundary, low_boundary) to find gate configs that produce
    cleaner regime separation
  - Quality metric: post-gate regime metrics (consistency of price
    behavior during gate-open windows; gate-open windows that correlate
    with measurable directional movement; ratio of in-gate to out-of-gate
    volatility, etc.)
  - Output: a "good gate" set of bny30M/p indicator params
  - Then: the gca5m line grinds run against this validated gate
  
  **Why precursor not post-op**:
  - If gates are right, raw gc{x}5{x} data going into line-pattern
    recognition is more sanitized → cleaner combos
  - Post-op optimization would let the line combo "shop for fit" with
    a particular gate — overfitting risk
  - Separates two distinct optimization domains: regime detection
    (gate) and pattern detection (line)
  
  **Open design questions**:
  - What's the gate quality metric? Without a downstream signal to
    optimize against, gate tuning needs its own success measure
  - Walk-forward / OOS validation should be built in from day 1
  - Whether to grind gate params per-line-type or once globally

### Pine

- **OOB gate emulation**: replicate bny30M/bny30p gating in Pine itself
  for hybrid pilot deployment (currently gates are applied at Python
  grind time only). Pine inputs `ic_high_boundary` / `ic_low_boundary`
  already exposed but not consumed.

- **dotenv migration**: existing scripts (`run.py`, `analyze_manager.py`,
  `validate_centroid.py`) still use the hardcoded-fallback env-var
  pattern. Migrate to `optimus9.config` so the password isn't
  duplicated in source.

### Hybrid Pilot

- **Pine strategy webhook → Python → Bybit**: deployment path after
  Pine AB testing concludes. Pine emits alerts; Python places real
  orders with native Bybit hedge mode.

- **DEMA cycle measurement util**: replaces hardcoded 0.4% SL with
  dynamic SL derived from local volatility/cycle.

- **FIB validation**: Phase 1 (lagging) + Phase 2 (predictive). Design
  note already in repo.

---

## Tomorrow's First Actions

1. ✅ Pine emitted with all r06 fixes (boundary separation, PM additive,
   step values, passthrough toggle, decision delay 0-bar fix)
2. Verify Pine ↔ Python signal alignment with the new boundary inputs
3. If aligned → build PM additive into Python:
   - Read `Pk5sGateComputer.compute()` to find vote-folding code
   - Apply script: add per-pool PM additive to compute path
   - DDL: add `pm_additive_close_str`, `pm_additive_wide_str` to
     `test_param_ranges`
4. Clear old pk_signals + pk_outcomes (DELETE WHERE
   `pks_or_pk IN (...)`) — disk relief + cleanup of pre-additive data
5. Re-grind tc_pk=18 → new or_pk → analyze → emit Pine → AB validation

---

## File Manifest (r06 deliverables)

In `/optimus9/`:
- `config.py` — new
- `emit/__init__.py` — new
- `emit/pine_strategy_emitter.py` — new
- `analysis/analyze_manager.py` — modified (--emit_pine flag)
- `orchestration/optimizer_runner.py` — modified (MAE on both paths)
- `compute/outcome_walker.py` — modified (MAE tracking)

At repo root:
- `emit_pine_strategy.py` — new
- `export_gate_windows.py` — new
- `optimus9_config.json.example` — new
- `optimus9_config.json` — gitignored, contains real password

Generated outputs:
- `bbstr_or<N>_strategy.pine` — Pine v6 strategy file
- `analysis_or<N>.csv` — combo rankings
- `gate_windows_or<N>.csv` — merged gate-open intervals
- `r06_260523_combo_dial_in.csv` — 27 combos for Pine UI testing

---

🤙 End of r06.
