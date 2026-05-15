# optimus9

Parameter optimization engine for the BBSTR trading strategy. Calibrates indicator and gate settings against historical 5s OHLCV by sweeping parameter grids, applying multi-gate signal filtering, and scoring outcomes by expectancy. Long-term roadmap: this codebase replaces the TradingView Pine Script implementation and becomes the trading bot itself.

## Quick start

Requirements: Python 3.12+, MySQL 8+, pandas / numpy / mysql-connector-python / requests / websockets / pytest.

```bash
# Configure DB credentials (env vars; defaults to localhost / root / empty pw)
export PK_DB_HOST=localhost
export PK_DB_USER=root
export PK_DB_PASS=<your password>
export PK_DB_NAME=pk_optimizer

# Sanity check: package imports + tests
python3 -c "from optimus9 import DatabaseManager; print('ok')"
pytest

# Pull historical 5s OHLCV (Bybit 1m REST → synthetic 5s)
python3 run.py backfill_synthetic --symbol FARTCOINUSDT

# Fast pipeline check (5-combo smoke against 1 day)
python3 run.py smoke --tc_pk 1 --lookback_days 1

# Full parameter grind (with p_rev and pk5s_gate both on)
python3 run.py start --tc_pk 1 --lookback_days 30

# Compare two runs side-by-side (portrait report + pivot-friendly CSV)
python3 run.py compare --or_pks 1 5
```

## Layout

```
optimus9/             # the package — see docs/README.md for layer-by-layer breakdown
├── db/               # database connection and query layer
├── data/             # exchange clients (Binance, Bybit), bar builders, ingestion
├── compute/          # indicator math, PK detection, vote machines, swing analysis
├── orchestration/    # run drivers, process supervision
└── analysis/         # post-run reporting, run comparison, outlier detection

tests/                # pytest scaffold — see tests/conftest.py for shared fixtures
docs/                 # specs, archived patches, SQL migrations — see docs/README.md
run.py                # CLI entry point — see `python3 run.py --help`
logger.py             # shared singleton logger
schema.sql            # canonical database schema
pytest.ini            # test runner config
```

## CLI

```
python3 run.py start    --tc_pk N  [--p_rev {on,off}]      [--pk5s_gate {on,off}]
                                   [--lookback_days N]     [--skip_analyze]
python3 run.py analyze  --or_pk N  [--min_signals N]       [--top_n N]
python3 run.py smoke    --tc_pk N  [--lookback_days N]
python3 run.py compare  --or_pks A B [C D]
python3 run.py backfill_synthetic  [--symbol SYM]
python3 run.py backfill_binance    [--symbol SYM] [--once]
python3 run.py tick_collect        [--symbol SYM]
python3 run.py bar_build
python3 run.py indicator_monitor
```

`--p_rev` toggles Pine `barmerge.lookahead_on` semantics on higher-TF calibration lines. `--pk5s_gate` toggles the 5s PK vote-machine folded into the OOB gate stack. Both default `on` for production; toggle off to isolate their contribution in comparison runs.

## Round-driven development

Changes are organized into numbered rounds. Each round produces one spec file in `docs/specs/` with a changes log at the top that accumulates decisions and refinements as the work progresses. Implementation artifacts (patches docs, migration scripts, SQL diffs) are dated and archived per round. See `docs/README.md` for the pattern.

Current active spec: `docs/specs/r02_260514_pk5s.md`.

## License

Private. Not for distribution.
