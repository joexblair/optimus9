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
