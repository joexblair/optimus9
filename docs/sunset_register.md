# Sunset register

Code disabled and marked for removal after a review period. Review before deleting (task #30). Each entry: what, why, when disabled, what replaces it, removal criteria.

## SyntheticBackfiller — synthetic 1m→5s kline backfill
- **Disabled:** 2026-07-05 (Joe).
- **What:** `optimus9/data/synthetic_backfiller.py` `SyntheticBackfiller` — fetched Bybit 1m futures history and split each 1m bar into 12 identical 5s bars as placeholder kline history (overwritten later by live tick-derived bars).
- **Why:** the 1m→12×5s split manufactures phantom **flat filler bars** that drift oscillators into false reversals (o9-live 07-04 false short; see `project_filler_invisible` memory). No-trade gaps should be **invisible** to the lines (match Bybit/TV), not synthesised.
- **Replaced by:** (1) `optimus9_system.filler_invisible=1` — lines compute on the event tape (real-trade bars), no-trade gaps invisible; (2) real-history repopulation via **TV CSV → KlineSanitiser** (`kline_sanitise_service.py`) instead of synthetic fill.
- **Disabled where:**
  - `run.py` supervisor `_backfill()` auto-thread — **commented out** (the automatic manufacturer). This is the functional disable.
  - `run.py` `cmd_backfill_synthetic` (CLI) — kept, emits a SUNSET warning.
  - `recover_frozen_klines.py` — one-off recovery script, SUNSET note added.
- **Removal criteria:** confirm the TV-CSV → KlineSanitiser path has covered ≥1 real repopulation/freeze-recovery need, then delete the class + `cmd_backfill_synthetic` + `recover_frozen_klines.py`. Leave `binance_backfiller.py` (separate real-source path) untouched.

## RPL — the exhaustion tool and everything that imports it

- **Disabled:** 2026-09-03 (Joe: *"RPL is sunsetted"*).
- **What:** `build_exhv2.py` and the ~17 files that `import build_exhv2` — `build_rpl_jig.py`,
  `predict_walk.py`, `curl_pred.py`, `build_dominoes_db.py`, `build_scn.py`, `walk_long.py`,
  `exh_0731.py`, `scan_up.py`, `scan_up2.py`, `build_r3.py`, `build_r7512.py`,
  `emit_dominoes_pine.py`, `build_momo_slip.py`, `build_s46_lines.py`.
- **Why:** the momentum verdict left `build_exhv2` for `optimus9/compute/momo_core.py` on 0813
  (Joe: *"RPL is in sunset, so we need to salvage"* / *"RPL will only poison our ws spec"*). Nothing
  in the dtf or wsf path imports `build_exhv2` any more — checked 0903.
- **What replaces it:** nothing. The momentum verdict it used to host lives in `momo_core`, and its
  knobs live in the `momo_config` table.
- **How it is disabled:** not by a flag. The momentum knobs became `None` by default on 0903, so any
  of these files that reaches the verdict raises a plain error naming `momo_config`. Its five
  command-line knob flags (`--r2 --slope --window --arc`) write straight into `momo_core` and are
  not expected to be used.
- **Removal criteria:** Joe's word. Nothing has been deleted.

## the s46 path

- **Disabled:** 2026-09-03 (Joe: *"s46 is dead"*).
- **What:** `optimus9/analysis/s46_momo.py`, `optimus9/analysis/build_s46_event.py`,
  `optimus9/analysis/sweep_s46_momo.py`, and `build_s46_momo.py`.
- **Why:** Joe's call. They call the gated momentum verdict on the s15 / s22 boards, which belong to
  neither the `wsf` nor the `domtf` band.
- **What replaces it:** nothing.
- **How it is disabled:** they bind no momentum bank, so they raise on their first momentum call.
  They import only each other; nothing live imports them — checked 0903.
- **Removal criteria:** Joe's word. Nothing has been deleted.

## build_ws_momo — the momo-TF study

- **Disabled:** 2026-09-03 (Joe: *"sunset build_ws_momo"*).
- **What:** `build_ws_momo.py`, and its two tables `ws_momo_bar` and `ws_momo`.
- **Why:** it answered one question Joe set on 0806 — which r-line timeframe best announces a 1.11%
  price swing. It is a study output read by Joe, not a producer anything downstream queries.
- **What replaces it:** nothing.
- **How it is disabled:** it binds no momentum bank, so it raises on its first momentum call.
  Nothing imports it — checked 0903.
- **Removal criteria:** Joe's word. The two tables are untouched.
