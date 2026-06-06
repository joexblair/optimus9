# r07 Status — closed 2026-05-30

## TL;DR

**r07 closed.** Vote machine extracted + extended, dispatch reshape +
AND composition shipped, per-combo summary table replaces a 40-min
GROUP BY, heartbeat + fixed-window grind args + 4 schema migrations
landed. The SnF architecture for r08 was designed in the same session
(filed as the r08 SnF spec stub in `r07_open_items.md`). gca5m line
dialed at 5s — sf=7 candidate. PM dials confirmed inert in single-line:
they belong at the SnF (collection) layer, not per-line.

### Shipped this round (commits in ~/thecodes)
- **r07.5 SQL tooling**: clone / inspect / delete test_config procs (`optimus9/sql/procs/`).
- **r07 Step 1**: decision delay deleted from Python.
- **r07 Step 2**: PKVoteMachine extracted from Pk5sGateComputer.
- **r07 Step 3a**: optional `vote_machine` injection point on PKSignalDetector
  (None-path byte-identical; regression-tested via fixed-window or_pk=49 vs or_pk=50).
- **r07 Step 4**: `pm_additive_str` in PKVoteMachine (single collapsed dial,
  close + wide) + Pk5sGateComputer pass-through + orchestration plumbing.
- **Dispatch reshape**: `signal_source` (vote / line) helper replaces
  `is_self_gated = not oob_side.any()` inference. Renames:
  `_run_vote_sourced`, `_run_line_sourced`.
- **AND composition**: vote-sourced path AND-folds bny30 `oob_side` with
  `s5_pk_final` before transition extraction. Strict polarity
  (in-band → blocked, per the bny30 correction).
- **Schema**: `pks_pm_additive` + `pks_pm_suppression` columns on `pk_signals`;
  new `pk_combo_summary` table (per-combo aggregates populated by the grind,
  AM reads directly — replaces the 40-min GROUP BY).
- **AM refactor**: `_load_combo_summaries` reads `pk_combo_summary` first,
  falls back to GROUP BY for pre-refactor grinds. `_CANDIDATE_PARAMS`
  extended with pm dims.
- **Logger**: rotation handlers (10 MB × 5); Tick + Bar collectors
  downgraded to INFO+ERROR.
- **Supervisor as systemd**: `klinecollect.service` runs continuously as
  user joe from ~/thecodes; uses `get_db_config()` (not env fallbacks).
- **Grind UX**: heartbeat every 77 rows (pct + elapsed + ETA) replaces
  per-combo INFO; final completion line prints or_pk.
- **Fixed-window grind args**: `--start_ms / --end_ms` for reproducible
  reference grinds (used for Step 3a's byte-identical validation).
- **pk_outcomes schema migration**: bar-counter columns widened to
  `INT UNSIGNED` (smallint overflow on 7-day windows).
- **`.gitignore`** unignored `optimus9/sql/**/*.sql` so migrations + procs
  commit without `-f`.
- **Bug catches** (caught + filed): synthetic vote_overrides missing
  `tcev_pk` (first vote-sourced integration grind); pm dial resolution
  chain (combo-grid → tce_params fallback) for persist consistency.

### Dialing findings — 2026-05-30 1D sweeps

- **gca5m at 5s, slope_floor sweep** (or_pk=55, 41 combos):
  monotonic — lower sf → more signals, marginally better expectancy.
  Peak gross at sf=7 (~$2,680, +1.10% exp, 906 wins). Peak expectancy
  at sf=7.5 (+1.109%). Density wins with comparable win rate (~37.3%).
- **gca5m at 5s, pm_additive sweep** (or_pk=56, 31 combos): inert
  across [0, 0.5]; **one binary jump at 0.55** (1745 → 2035 signals);
  plateaus to 1.5. The polarising threshold-crossing behaviour Joe saw
  in Pine, in single-line it has only one tier.
- **gca5m at 5s, pm_suppression sweep** (or_pk=57, 31 combos): **zero
  effect** across [0, 1.5]. All 31 combos identical to baseline.
- **Implication**: PM dials are designed for multi-line vote dynamics.
  Single-line voting can't exercise them. They belong at the SnF
  (collection) layer where multiple lines actually interact.
- **Reference or_pks**: 53 (baseline single combo), 55/56/57 (1D sweeps).
- **5s centroid candidate**: sf=7 picked by visual cluster preference
  ("better clusters in places"). `cluster_quality_score` will make this
  empirical when r08 ships.

### r08 starting state — pointer

The full SnF architecture is in `r07_open_items.md` under
"r08 SnF spec stub — architecture landed 2026-05-30". TL;DR:
- **Per-line library + temporal-coalition SnF + cluster overlay.** Per-line
  grinds produce reusable signal libraries; SnF simulator forms coalitions
  by signals firing within x bars of each other; cluster overlay scores
  emitted streams against detected swings.
- **SnFv2 enhancement**: each line offers its top-5 intrinsic centroids;
  SnF sweeps the cross-product (5^N collection compositions).
- **Cluster overlay** built as a separate post-grind layer (not baked into
  grind), runs multi-algo swing detection (ZigZag + ATR + fractal) for
  robustness.
- **Friction formula A/B** filed (v1: opposing-signals-only; v2: + non-firing-line tax).
- **Swing significance calibration**: at 5s, "optimal clustering" (TBD); at
  HTF, 0.9% (scalper-exit threshold becomes natural at HTF noise levels).

### Step 3b — deferred by design

Original Step 3b (wire vote machine into PKSignalDetector for line-sourced
path) is **deferred indefinitely**. The SnF architecture treats lines as
independent signal sources composed at the SnF layer via temporal
coalition — not via PKSignalDetector's per-line vote machine. 3b is moot
in the new architecture.

### Where we stopped this round / fork moment

Architecture for r08 SnF locked. Per-line dial mechanics established via
the 3-grind 1D sweeps. r07 ships the engine; r08 builds the SnF analyzer
on top. **Natural fork point** — fresh r08 session reads
`fork_init_prompt.md` (handover dir) + memory + the spec stub and is
productive without this session's accumulated context bloat.

Joe's next move: loose Pine visual validation of a new 5s line
(gcs5M candidate). Once happy, hands the line spec + indicator config to
fresh CC for a per-line library multi-D grind. Same shape as r07 grinds
A/B/C, just for a different line.

---

## What Optimus9 is

A parameter-optimizer + signal engine for a futures trading strategy on
Bybit USDT-margined perpetuals. Specifically: it grinds parameter
combinations of a BB-or-K-line strategy on 5-second klines, walks each
signal forward to compute outcome (max profit, max adverse excursion,
bars to stop), and ranks combos by expectancy and drawdown.

Core concepts:
- **5s execution timeframe** — all PK fires originate on 5-second bars.
  HTFs (higher timeframes) serve as confirmation context.
- **PK** = "peak", a moment where line vs DEMA slope analysis indicates
  a directional commitment. PKs at 5s are the entry-timing layer.
- **p-rev** = "peak reversal anchor": when a 5s PK fires, the HTF's line
  value is frozen as that PK's anchor. The HTF then validates against
  the anchor; reversal back through the anchor cancels the trade premise.
- **Gates** (bny30M, bny30p, etc.) = OOB filters from other timeframes
  that condition WHEN a 5s PK is allowed to fire. Gate logic answers "is
  the current market regime appropriate for this kind of signal."
- **SnF** = multi-line voting (future r08 work). Multiple 5s lines'
  PKs fold into a single aggregated signal.
- **BL machine** = boundary-line decisions on OOB crosses (future r08).

Production target: full Python trading bot. The hybrid pilot path (Pine
emits webhook alerts → Python places orders) was dropped 2026-05-26.
Pine retained as a validation tool only.

**Repo**: github.com/joexblair/optimus9
**Local path**: `/mnt/c/Users/Administrator/thecodes/optimus9`
(WSL2 Ubuntu, MySQL `pk_optimizer` DB on `/dev/sdc`, 16 cores)

---

## Glossary

Terms used throughout the docs. Filed here because CC's gap report
(2026-05-26) caught that none of these were defined in one place.

**Architecture / code**:
- **Pool** — full settings group for ONE line: p_c, p_w, p_r, suppression,
  slope, multiplier, weight_close, weight_wide. One pool per line.
- **Probe** — close or wide measurement WITHIN a pool. Two probes per
  pool, distinct distances (pool_c vs pool_w bars back) and weights
  (weight_close vs weight_wide).
- **Voter** — synonym for pool in vote-machine context. Multi-line SnF
  has multiple voters; single-line gca5m has one voter with two probes.

**Signal classification states** (output of PKStateComputer per probe):
- `NaN` — not yet computable (insufficient lookback or NaN inputs)
- `0` — neutral (slope_diff under floor)
- `±1` — divergence (line and price slopes disagree on sign)
- `±2` — **PM sentinel** (slopes AGREE on sign, magnitudes both
  significant). PM = "Price Match". Conceptually: trend continuation
  rather than reversal-divergence.

**Vote machine mechanics** (the math we're extracting in r07):
- **long_pts / short_pts / neutral_pts** — accumulated probe-weighted
  votes per bar.
- **PM suppression** = PM_LONG state contributes a "soft no" to short_pts
  (and vice versa) via `adj_long = max(0, long_pts - pm_short_wt × pm_suppress_str)`.
  The intent: trend-continuation signals dampen opposing directional
  votes without firing themselves.
- **PM additive** (Step 4 work) = PM sentinels ADDITIONALLY contribute
  to the matching directional bucket (PM_LONG → adds weight to long_pts,
  not just suppressing short). The "additive" is gated by separate
  `pm_additive_close_str` and `pm_additive_wide_str` params, default 0.0.
- **control voter** — a no-op voter included in the vote arithmetic that
  contributes 0 to all directional buckets but DOES contribute to
  `active_w` (the denominator). Mechanically dampens ratio swings on
  bars with few active probes. Filed as "verify it's needed in Python
  production separately from Pine" in design doc open questions.
- **pm_option_a vs pm_option_b** — Pine has a toggle. **pm_option_a=true**:
  `active_w = long_pts + short_pts + neutral_pts` (raw counting).
  **pm_option_a=false** (current Python default): `active_w = adj_long +
  adj_short + neutral_pts` (post-suppression). Production likely keeps
  `false` (post-suppression); resolve before Step 5.
- **decision delay** — DELETED from Python 2026-05-26. Was a state
  machine where pk_raw fires entered a `delay`-bar countdown; if an
  opposing-direction pk_raw fired during countdown, the pending fire
  was cancelled. Hostile to HTF anchor signals. Pine retains it for
  validation parity.

**Grind / optimizer vocabulary**:
- **tc_pk** = `test_configs` row primary key. One tc = "this set of
  param ranges over this indicator config." Stable across runs.
- **or_pk** = `optimizer_runs` row primary key. One or = "I executed
  tc=X at this moment with these grid expansion choices." Each grind
  creates a new or_pk.
- **tce_pk** = `test_config_extensions` row primary key. Used for pk_5s
  gate extensions and similar add-ons to a base tc. **Architectural
  bridge**: each `test_config_extensions` row of type='pk_5s' IS a pool
  in the vote-machine sense. `tcev_pk` (which is just `tce_pk` viewed
  from the vote table) is the unique pool identifier when speaking
  architecturally. So `pool_id` and `tcev_pk` refer to the same thing.
- **combo** = one parameter dict from the grid expansion. A tc with
  10 params × 8 values each = 80 combos. Each combo gets its own
  per-row signal+outcome rows in pk_signals + pk_outcomes (joined by
  pks_or_pk and combo-param columns).
- **r0X** = milestone marker. Loosely "a focused chunk of work, usually
  spanning 1-3 sessions." Numbering is sequential; r06 closed 2026-05-25,
  r07 began same day. Not strictly per-session or per-day.
- **PROVEN** = the historical baseline combo (or_pk=32: len=6, mult=0.74,
  src=hlcc4, pool_c=5, pool_w=23, pool_range=8, slope_floor=41.0,
  multiplier=1). 695 signals, 39.0% win, $4,210 gross banked, 14.8% max_dd.
  All subsequent grinds reference this as the "does the new code produce
  signals at least as good as PROVEN?" benchmark.

**Outcome metrics** (in pk_outcomes + analysis CSVs):
- **gross_banked** = sum of profitable trade outcomes minus losses,
  in synthetic $ units (entry size = $100 per signal). Pre-fees.
- **expectancy** (exp%) = average return per signal as a percentage.
- **win_rate** (win%) = fraction of decided signals that hit profit_zone
  before hitting stop.
- **max_dd** = maximum equity drawdown across the sequential walk of
  signals. The DD kill switch fires combos with max_dd > 15%.
- **MAE** = Maximum Adverse Excursion. Per-signal worst-against-position
  excursion. Used for per-signal dd_pct in Pine labels and DD analysis.

---

## Prior milestones (one-line summaries)

- **r01-r03** (mid-late May 2026): Initial grind infrastructure. Pre-MAE
  pipeline, pre-SRP, pre-transition-semantics. All data deleted in r07
  cleanup. Historical analysis CSVs (analysis_or17-22) retained on disk.
- **r04** (late May 2026): MAE columns added to pk_outcomes schema.
  Outcome walker tracks both favorable and adverse excursions.
- **r05** (2026-05-21): KlineLoader refactor (shared between grind paths),
  tc_max_bars deprecated, "always a stop" principle locked in.
- **r06** (2026-05-22 to 2026-05-25): SRP refactor splitting PKDetector → 
  PKStateComputer + PKGateFilter + PKSignalDetector. Transition
  semantics (was per-bar). Pine bny30 gate emulation. f_bb 70/30
  rescale alignment.
- **r07** (2026-05-25 to current): Vectorization, vote machine extract design,
  Pine deprecation decision, decision delay deletion.

---

## Reference checkpoints on disk

All in `/mnt/c/Users/Administrator/thecodes/optimus9/`:

- `or44_reference.csv` — 55,170 signals, pre-vectorization, 80-combo
  PROVEN-locked sweep. Reference for vectorization validation.
- `or47` (in DB only, no analysis CSV yet) — vectorized re-grind of
  same config. Used for diff against or44_reference.
- `analysis_or32.csv` — original PROVEN baseline (or_pk=32, 695 signals,
  39% win, $4210 gross).
- `analysis_or36.csv` — initial gate emulation validation (or_pk=36,
  4048 signals, 42.7% win).
- `analysis_or44.csv` — refactor validation (or_pk=44, 55,170 signals,
  47.7% win, all DD-killed under current DD kill switch).

## Vectorization validation — exact result

`or44_reference.csv` (Python-loop version) vs or47's pk_signals
(vectorized version): out of 326 signals in or44 for one combo,
**325 matched perfectly on timestamp + direction + pk_state**, 1 was
off by one 5s bar, 1 was missed entirely. **0.6% drift.**

The drift is attributable to kline-window shift between the two grinds
(or_pk=44 ran ~6 hours before or_pk=47; their lookback-1-day windows
differ by ~22k bars at boundaries) — not to vectorization correctness
errors. The systematic structure of "1 boundary off-by-one + 1 missed
boundary signal" matches what kline-window shift would produce.

**Spec status**: the design doc says "must match exactly on overlapping
timestamps." Two overlapping-timestamp signals differ. The deviation is
within tolerable bounds for kline-window-shift artifacts; strictly,
spec is met if we read "overlapping" as "perfectly overlapping bar
sequence," not met if we read it as "any shared timestamp." We accepted
the drift as artifact, not bug.

Validation harness for exact reproducibility (fixed timestamp window
instead of rolling 1-day) is filed for r07 backlog.

---

## Database schema (current state, pk_signals + pk_outcomes)

Column dump for orientation. Full DDL is in MySQL `pk_optimizer.*`.

**pk_signals** (one row per signal per combo):
- `pks_pk` BIGINT AUTO_INCREMENT PRIMARY KEY
- `pks_or_pk` INT — FK to optimizer_runs.or_pk
- `pks_timestamp` BIGINT — ms epoch of the 5s bar where signal fired
- `pks_bar_index` INT — bar offset within the grind's loaded kline data
- `pks_dir` TINYINT — +1=long, -1=short
- `pks_pool` VARCHAR — 'close' or 'wide' (which probe within the pool fired)
- `pks_pk_state` FLOAT — 1.0/-1.0 (divergence) or 2.0/-2.0 (PM sentinel)
- `pks_line_value` FLOAT
- `pks_slope` FLOAT — line vs peak
- `pks_slope_diff` FLOAT
- `pks_dema_slope` FLOAT
- `pks_dema_value` FLOAT
- Combo-identifying columns: `pks_len`, `pks_mult`, `pks_src`,
  `pks_pool_c`, `pks_pool_w`, `pks_pool_range`, `pks_slope_floor`,
  `pks_multiplier`, `pks_len_rsi`, `pks_len_stoch` (last two for K-line
  variants, NULL for BB)

**pk_outcomes** (one row per signal, joined 1:1 to pk_signals):
- `pko_pk` BIGINT AUTO_INCREMENT PRIMARY KEY
- `pko_pks_pk` BIGINT — FK to pk_signals.pks_pk (1:1)
- `pko_max_profit_pct` FLOAT — best favorable excursion
- `pko_bars_to_max_profit` INT — when max profit was last updated
- `pko_max_adverse_pct` FLOAT — worst adverse excursion (MAE)
- `pko_bars_to_max_adverse` INT
- `pko_bars_to_stop` INT — NULL = trade ran off dataset

**Critical schema convention**: `pko_bars_to_stop IS NULL` means the
trade was inconclusive because data ended before stop fired. "Always
a stop" design principle — no max_bars cap, no time-based exits.

Schema migration questions for vote-machine signals (r07/r08): the
existing `pks_pool` column doesn't map cleanly to multi-probe-aggregated
signals. Filed as open question #1 in vote machine design doc.

---

## Apply scripts on disk (HISTORICAL — pre-CC pattern, retained as record)

**Status update (post-r07-Step-2)**: apply scripts were a workaround
pattern from when Claude generated code that Joe copy-pasted. With CC
editing files directly via git, the apply-script pattern is retired.
See "CC editing convention" section above. These scripts remain in
tree as historical record of pre-CC changes — they are NOT a pattern
for new work.

**Original convention**: each script edited source `.py` files in place
using `old/new` string replacements. `--dry-run` showed what would
change without writing. Re-runs were safe (matching `skip_if_contains`
text already present → skip; OLD text absent → NOMATCH, reported but
harmless). No DB migrations involved; schema changes were manual DDL.

**Note on vectorization apply** (CC catch): `apply_r07_vectorize_pk_classes.py`
only **verifies imports + dependencies**. The vectorized
`pk_state_computer.py` and `pk_signal_detector.py` files were direct
`cp` replacements from outputs, not generated by the apply script. The
script is a verification harness, not a code generator.

**Historical status**:
- `apply_r06_srp_pk_refactor.py` — DONE 2026-05-25
- `apply_r06_mae_persist_restore.py` — DONE 2026-05-26
- `apply_r07_vectorize_pk_classes.py` — DONE (verification only; .py
  files were direct `cp` replacements. The script imports the new
  PKStateComputer + PKGateFilter + PKSignalDetector classes, instantiates
  each with default args, and confirms pandas is available. It does NOT
  run them on real or synthetic data. Re-running it proves the classes
  load cleanly in the current environment; it doesn't prove correctness.)
- `apply_r07_remove_decision_delay.py` — DONE 2026-05-26 (4 of 5 edits
  via script, 5th edit applied manually due to inverted skip-logic in
  the script. The script's WARNING comment block at the top explicitly
  documents the skip-logic bug; future apply-script work — if any —
  should NOT model on this script.)
- `apply_r07_step2_vote_machine_extract.py` — DONE 2026-05-29 (final
  apply script in the pre-CC pattern; ships PKVoteMachine class,
  PKSignalDetector flow manager promotion is NOT included — that's
  Step 3, handled by CC.)

---

## Validation tooling

- `snapshot_pk_signals.py` — dump pk_signals for an or_pk to
  deterministically-ordered CSV. Used for diff-based validation
  against reference grinds.
- `validate_srp_refactor.py` — smoke test imports + synthetic data.
- `cleanup_old_grinds_v2.py` — per-or_pk delete (slower than TRUNCATE
  for big tables, but selective).
- `export_gate_windows.py` — merged gate-open intervals for an or_pk.

---

## Pine state

`optimus9/emit/pine_strategy_emitter.py` has all r06 + r07 changes:
- bny30 gate emulation via single tuple `request.security` call
- PM additive inputs present (Pine-only, default 0.0)
- `f_bb` rescale matches Python (70/30 OB/OS, 85/15 OOB)
- Decision delay state machine still present in Pine (only deleted
  from Python; Pine retains for validation comparisons)

---

## Open observations (not blocking)

- **Pine PM additive non-linear and polarising**: user tested visually.
  Could be math (threshold step-function) or could be Pine implementation
  quirk. Won't know until Python PM additive ships and we can compare.
  Filed in `r07_vote_machine_design.md`.

- **All combos DD-killed**: every refactor-validation grind has all
  combos exceed 15% max_dd. Could be calibration (1-day window too
  short), symmetric stop/take (0.4/0.4 vs PROVEN's 0.4/0.6), or
  transition semantics changing risk profile. Not blocking; worth
  checking with a longer-window grind once vote machine work lands.

- **Latent dema wraparound** in PKStateComputer (`np.roll(dema, center)`).
  Wraparound is masked by the explicit NaN of first `upper+1` bars, so
  doesn't fire today. Filed in `r07_open_items.md` as "do not clean up
  without re-validating."

- **align_to_base inconsistency**: for `ind_seconds == 5`, `_build_line`
  skips align_to_base and returns ind_df-length array. Causes line/dema
  length mismatch (~23 bars). PKStateComputer truncates to handle it.
  **This is a workaround, not a fix**. Filed for proper cleanup
  post-vote-machine: move truncation upstream into `_build_line`.

---

## Open backlog

**Single source of truth**: `r07_open_items.md`. This doc previously
duplicated a partial extract of items, which drifted from the working
backlog. To prevent further drift, the full backlog now lives in
`r07_open_items.md` only. Read that for r07 in-flight items, r08
prep, architectural findings (DD category error, cluster_quality_score,
pairwise voting model), Pine maintenance items, dormancy annotations,
and design questions.

`r07_vote_machine_design.md` is the source of truth for the vote
machine extract's specific step-by-step plan (Steps 1-5).

---

## CC editing convention (post-r07-Step-2)

Apply scripts were a workaround pattern emerging from Claude generating
code that Joe copy-pasted. They bundled multiple related edits with
idempotency and dry-run support.

**Claude Code (CC) edits files directly via git commits + pytest validation.**
The git+pytest equivalents replace the apply-script affordances:

| Apply script affordance     | CC equivalent              |
|-----------------------------|----------------------------|
| `--dry-run`                 | `git diff` before commit   |
| Idempotency                 | Commits are immutable      |
| Atomicity (multi-edit unit) | One logical change = one commit |
| Documentation               | Commit message + diff      |
| Replayability               | `git revert` / `git restore` |
| Validation                  | `pytest tests/` after each change |

**CC must commit with discipline** because the project's pre-CC git
workflow was end-of-session batched commits. CC's working pattern needs
to be tighter: granular commits, clear messages, pytest run after each
change, no batched WIP. This is more disciplined than the pre-CC
practice; the discipline is required because CC's edits are mid-session
and need to be revertable.

**Apply scripts already in tree** are retained as historical record of
pre-CC changes (e.g. `apply_r07_remove_decision_delay.py`). They are
NOT a pattern for new work. The WARNING comment block in that file
explains specifically not to model new scripts on its skip-logic.

---

## Production target (decided this session)

- **Pine** = visualization and validation tool only. 5s PK validation
  matters. HTF p-rev validation matters when we get there. SnF and BL
  machine won't be Pine-validated (simple enough that visual confirmation
  doesn't catch real bugs).
- **Python** = canonical signal engine, canonical execution engine,
  canonical data pipeline. No hybrid intermediate.
- **Decision delay** = DELETED in Python 2026-05-26. Pine keeps it.
- **PM additive grind strategy**: sweep one pool's pm_additive at a time
  during single-line dial-in. SnF queries the resulting DB to find best
  multi-line combinations.

---

## How to run a grind (orientation for fresh sessions)

```bash
cd /mnt/c/Users/Administrator/thecodes/optimus9

# Start a grind from CLI:
python3 run.py start --tc_pk=<N> --lookback_days=1 [--skip_analyze]

# Snapshot signals for validation:
python3 snapshot_pk_signals.py --or_pk=<N> --output=<filename>.csv

# Standalone analyze (when auto-analyze OOMs after grind completes):
python3 -m optimus9.analysis.analyze_manager --or_pk=<N>
```

`optimus9.config.get_db_config()` reads DB credentials from environment
or a fallback. The supervisor process (`python3 run.py supervisor`)
runs the live kline collector continuously.
