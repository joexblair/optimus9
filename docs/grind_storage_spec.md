# Grind-result storage — spec + process

*DRAFT (Joe 0622). Tames the ~16-table sprawl (`bias_pk_cascade/_flosc/_foundation/_grind/…`,
`s30_grind_results`, `line_signals`, …) where every grind minted its own bespoke schema.*

## 1. Why
- **Comparability** — "which grind, which config, beat the KPI?" must be one query, across all grinds.
- **Provenance** — every result carries its window, engine_rev, and full config, so it's reproducible.
- **KPI-first** — the headline metric (per machine) is a first-class column, not buried in `correct/total`.
- It's the **single-source / no-hardcode** discipline applied to the storage layer.

## 2. The standard shape — two tables, JSON-flexible, KPI-typed

**`grind_run`** — one row per grind invocation (regeneratable):

| col | type | meaning |
|---|---|---|
| `gr_pk` | BIGINT PK | |
| `gr_kind` | VARCHAR(40) | grind type: `bias_cascade`, `s30_swing`, `bl_dialin`, … |
| `gr_config` | JSON | the grind's config/knobs (the BiasConfig / sweep grid def / …) |
| `gr_window_start`,`gr_window_end` | BIGINT | ms epoch (multi-window → list in `gr_config`) |
| `gr_engine_rev` | VARCHAR(40) | md5 of the engine module — pins reproducibility |
| `gr_kpi_name` | VARCHAR(40) | the KPI metric name, e.g. `cascade_placement_rate` |
| `gr_kpi_value` | FLOAT | the headline KPI (best cell, or aggregate) |
| `gr_is_live` | TINYINT | 1 = the current/live result for this `gr_kind` |
| `gr_created_dt` | DATETIME | |
| `gr_notes` | VARCHAR(255) | |

**`grind_result`** — one row per config-cell:

| col | type | meaning |
|---|---|---|
| `grr_pk` | BIGINT PK | |
| `grr_run_pk` | BIGINT | → `grind_run.gr_pk` |
| `grr_cell` | JSON | the cell's params, e.g. `{"ordering":"seq","s3_variant":"m","xm45":0}` |
| `grr_metrics` | JSON | all metrics, e.g. `{"correct":158,"total":367,"net_usd":1897}` |
| `grr_kpi` | FLOAT | the cell's KPI value — the **named, indexed** column for ranking |

The cell params and metrics stay **JSON** (per-grind freedom); only the **KPI is promoted to a column**
so leaderboards/comparisons are uniform. `gr_config` + `gr_engine_rev` + window = full provenance.

## 3. The KPI is per-machine
Each machine declares its KPI; the grind scores against it (the engine, not the storage, decides).
- **Bias machine** → the **cascade win** — first-trade-after-bias-update placement/profit
  (`project_bias_cascade_win`; `gr_kpi_name = cascade_placement_rate`).
- **BL machine** → its equivalent (the gate-open trade quality / net) — TBD.

## 4. Process
- Every grind uses **`GrindStore`** (`optimus9/db/grind_store.py`) — the only persistence seam:
  `register_run(kind, config, window, engine_rev, kpi_name) → run_pk`, then
  `write_results(run_pk, cells)` (cells carry `cell`/`metrics`/`kpi`), then
  `finalize(run_pk, kpi_value, mark_live=…)`.
- **No new bespoke table per grind.** A grind that needs extra detail puts it in `grr_metrics` JSON.
- `vw_grind_leaderboard` ranks live runs by KPI per kind — the discovery surface.

## 5. Retrofit (slow-burn, like the OOB refactor #28)
Migrate the existing tables one at a time, each verified: `bias_pk_cascade` first (it holds the
live KPI), then the rest. Keep the old table until its consumers move; log each in the sunset
register (#30). Goal: the bespoke grind tables empty out into `grind_run`/`grind_result`.
