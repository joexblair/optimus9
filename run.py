"""
run.py — Optimus9 CLI entry point

Subcommands:
  start              Drive a full grind for a test_config.
  analyze            Aggregate a completed run into a structured report + CSV.
  smoke              Tiny 5-combo grind against 1 day of data — integration test.
  compare            Side-by-side comparison of 2-4 optimizer runs.
  supervisor         Always-on data pipeline (TickCollector + BarBuilder).
  backfill_synthetic Build 5s OHLCV from Bybit 1m REST historicals.
  backfill_binance   Binance backfill loop.
  tick_collect       Live Bybit WS → ticks (single-process; supervisor preferred).
  bar_build          ticks → kline_collection (5s; supervisor preferred).
  indicator_monitor  Config drift sniffer.

Round 260514 (r02) — 5s PK gate + p-rev:
  • start gains --p_rev / --pk5s_gate flags (both default 'on')
  • start invokes analyze automatically unless --skip_analyze
  • smoke command added — small fixed grid for fast integration check
  • optimizer_runs columns or_p_rev_enabled / or_pk5s_gate_enabled
    recorded per run for queryable cross-run comparison

Round 260515 (r02 cont.) — compare:
  • compare command added — portrait console output + pivot-friendly CSV
  • int-aware centroid rounding (len/pool_c/pool_w/pool_range/multiplier)

Round 260516 (r03) — supervisor:
  • supervisor command added — TickCollector + BarBuilder under ProcessManager
  • intended deployment via systemd user service (see r03 spec)

═════════════════════════════════════════════════════════════════════════════
TODO — parked items, surface when relevant
═════════════════════════════════════════════════════════════════════════════
  • Per-config p_rev override on test_configs (currently CLI-only)
      → add tc_p_rev_default TINYINT(1), CLI flag becomes override
  • Persist mode flag: --persist {full,signals_only,outcomes_only,sample}
      → cuts DB write load on large grinds, lets us reduce data resolution
        on exploratory passes
  • Additional analyser visualisations
      → per-param 3D surface, direction-match-vs-win confusion matrix
  • Trend machine rebuild (xls 260511 spec, separate workstream)
  • Patch PKDetector's 1-bar window discrepancy once next clean centroid
    is locked in (see PKDetector docstring for current rationale)
  • Auto-backfill on supervisor startup (gap between last_kline and now)
  • IndicatorMonitor + BinanceBackfiller as supervised workers
  • Exponential restart backoff in ProcessManager
═════════════════════════════════════════════════════════════════════════════
"""

import argparse
import os
import sys

from logger import get_logger
from optimus9 import (
    AnalyzeManager,
    BarBuilder,
    BinanceBackfiller,
    BinanceClient,
    BybitKlineClient,
    BybitWebSocketClient,
    DatabaseManager,
    IndicatorMonitor,
    OptimizerRunner,
    Pk5sGateComputer,        # noqa: F401 — re-exported for import sanity-checks
    PKDetector,
    ParameterGridBuilder,
    ProcessManager,
    ReportManager,
    SwingAnalyzer,
    SyntheticBackfiller,
    TickCollector,
    WorkerSpec,
)
from optimus9.orchestration.workers import (
    tick_collector_worker,
    bar_builder_worker,
)


_log = get_logger('run')


# ─── DB connection ─────────────────────────────────────────────────────────
def _db() -> DatabaseManager:
    db = DatabaseManager(
        host     = os.environ.get('PK_DB_HOST',     'localhost'),
        user     = os.environ.get('PK_DB_USER',     'root'),
        password = os.environ.get('PK_DB_PASS',     'yourpassword'),
        database = os.environ.get('PK_DB_NAME',     'pk_optimizer'),
        port     = int(os.environ.get('PK_DB_PORT', 3306)),
    )
    db.connect()
    return db


# ─── argument parsing ──────────────────────────────────────────────────────
def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='run', description='Optimus9 CLI')
    sub = p.add_subparsers(dest='cmd', required=True)

    # start ----------------------------------------------------------------
    s = sub.add_parser('start', help='Drive a full grind for a test_config')
    s.add_argument('--tc_pk',         type=int, required=True)
    s.add_argument('--p_rev',         choices=['on', 'off'], default='on',
                   help='Apply Pine barmerge.lookahead_on to higher-TF '
                        'calibration line (default on)')
    s.add_argument('--pk5s_gate',     choices=['on', 'off'], default='on',
                   help='Fold pk_5s vote machine output into oob_side '
                        '(default on)')
    s.add_argument('--lookback_days', type=int, default=None,
                   help='Restrict kline window to last N days')
    s.add_argument('--skip_analyze',  action='store_true',
                   help='Do not auto-run analyze after the grind')
    s.add_argument('--no_csv',        action='store_true',
                   help='Skip optimizer CSV export from ReportExporter')
    s.add_argument('--output_dir',    default='.', help='Where reports land')

    # analyze --------------------------------------------------------------
    a = sub.add_parser('analyze', help='Aggregate a completed run')
    a.add_argument('--or_pk',       type=int, required=True)
    a.add_argument('--min_signals', type=int, default=30)
    a.add_argument('--top_n',       type=int, default=20)
    a.add_argument('--output_dir',  default='.')

    # smoke ----------------------------------------------------------------
    k = sub.add_parser('smoke', help='Fast 5-combo integration test')
    k.add_argument('--tc_pk',         type=int, required=True)
    k.add_argument('--lookback_days', type=int, default=1)

    # compare --------------------------------------------------------------
    c = sub.add_parser('compare',
                       help='Side-by-side comparison of 2-4 optimizer runs')
    c.add_argument('--or_pks',     type=int, nargs='+', required=True,
                   help='Two to four or_pks. First = baseline, last = target.')
    c.add_argument('--output_dir', default='.')

    # supervisor -----------------------------------------------------------
    sv = sub.add_parser('supervisor',
                        help='Always-on data pipeline (TickCollector + BarBuilder)')
    sv.add_argument('--tp_pk',  type=int, default=1)
    sv.add_argument('--symbol', default='FARTCOINUSDT')

    # backfill_synthetic ---------------------------------------------------
    bs = sub.add_parser('backfill_synthetic',
                        help='Build 5s OHLCV from Bybit 1m historicals')
    bs.add_argument('--tp_pk',  type=int, default=1)
    bs.add_argument('--symbol', default='FARTCOINUSDT')

    # backfill_binance -----------------------------------------------------
    bb = sub.add_parser('backfill_binance', help='Binance backfill loop')
    bb.add_argument('--tp_pk',  type=int, default=1)
    bb.add_argument('--symbol', default='FARTCOINUSDT')
    bb.add_argument('--once',   action='store_true')

    # tick_collect ---------------------------------------------------------
    tc = sub.add_parser('tick_collect', help='Live Bybit WS → ticks table')
    tc.add_argument('--tp_pk',  type=int, default=1)
    tc.add_argument('--symbol', default='FARTCOINUSDT')

    # bar_build ------------------------------------------------------------
    bbd = sub.add_parser('bar_build', help='ticks → kline_collection (5s)')
    bbd.add_argument('--tp_pk', type=int, default=1)

    # indicator_monitor ----------------------------------------------------
    im = sub.add_parser('indicator_monitor', help='Config drift sniffer')
    im.add_argument('--tp_pk', type=int, default=1)
    im.add_argument('--tc_pk', type=int, default=1)

    return p


# ─── command handlers ──────────────────────────────────────────────────────

def cmd_start(args, db: DatabaseManager) -> int:
    p_rev_enabled     = (args.p_rev     == 'on')
    pk5s_gate_enabled = (args.pk5s_gate == 'on')

    _log.info(
        f'Starting grind tc_pk={args.tc_pk}  '
        f'p_rev={"on" if p_rev_enabled else "off"}  '
        f'pk5s_gate={"on" if pk5s_gate_enabled else "off"}'
    )

    csv_path = ReportManager(db).run(
        args.tc_pk,
        export_csv        = (not args.no_csv),
        output_dir        = args.output_dir,
        lookback_days     = args.lookback_days,
        p_rev_enabled     = p_rev_enabled,
        pk5s_gate_enabled = pk5s_gate_enabled,
    )
    if csv_path:
        _log.info(f'Optimizer CSV → {csv_path}')

    if not args.skip_analyze:
        rows = db.execute(
            '''SELECT or_pk FROM optimizer_runs
               WHERE or_tc_pk = %s
               ORDER BY or_pk DESC LIMIT 1''',
            (args.tc_pk,), fetch=True,
        )
        if rows:
            or_pk = int(rows[0]['or_pk'])
            _log.info(f'Auto-analyzing or_pk={or_pk}')
            AnalyzeManager(db).run(or_pk, output_dir=args.output_dir)

    return 0


def cmd_analyze(args, db: DatabaseManager) -> int:
    _log.info(f'Analyzing or_pk={args.or_pk}')
    AnalyzeManager(db).run(
        args.or_pk,
        min_signals = args.min_signals,
        top_n       = args.top_n,
        output_dir  = args.output_dir,
    )
    return 0


# Hardcoded 5-combo grid for smoke runs. Covers all 5 srcs, both pool_ranges,
# and spreads len/mult/pool_c/pool_w to both ends. See r02 spec for rationale.
_SMOKE_GRID = [
    # len mult  pc  pw  pr  src      slope multiplier
    (19, 0.69,  8, 55,  2, 'close',  2.5, 3),  # known-good centroid baseline
    (22, 0.41, 12, 49,  4, 'hl2',    2.5, 3),  # param edges + range=4
    (16, 0.55, 10, 51,  2, 'hlc3',   2.5, 3),  # low len + diff src
    (20, 0.62,  8, 53,  2, 'hlcc4',  2.5, 3),  # mid params + diff src
    (18, 0.48, 12, 55,  4, 'ohlc4',  2.5, 3),  # range=4 + last src
]


def cmd_smoke(args, db: DatabaseManager) -> int:
    """
    Fast integration test: full pipeline (compute + gate + detect + analyse)
    against 1 day of data with 5 combos. Both --p_rev and --pk5s_gate
    default 'on'. To exercise off paths, use `start --lookback_days 1` with
    explicit flags.
    """
    _log.info(f'Smoke test tc_pk={args.tc_pk}  lookback_days={args.lookback_days}  '
              f'5-combo grid, both flags on')

    grid = [
        {
            'len':         L,
            'mult':        M,
            'pool_c':      PC,
            'pool_w':      PW,
            'pool_range':  PR,
            'src':         SRC,
            'slope_floor': SF,
            'multiplier':  MUL,
        }
        for (L, M, PC, PW, PR, SRC, SF, MUL) in _SMOKE_GRID
    ]

    # Monkey-patch the grid builder transiently. Sole call site is inside
    # ReportManager.run via ParameterGridBuilder(db).build(tc_pk).
    original_build = ParameterGridBuilder.build
    def _smoke_build(self, tc_pk: int) -> list:
        return grid
    ParameterGridBuilder.build = _smoke_build

    try:
        ReportManager(db).run(
            args.tc_pk,
            export_csv        = False,
            output_dir        = '.',
            lookback_days     = args.lookback_days,
            p_rev_enabled     = True,
            pk5s_gate_enabled = True,
        )
        rows = db.execute(
            '''SELECT or_pk FROM optimizer_runs
               WHERE or_tc_pk = %s ORDER BY or_pk DESC LIMIT 1''',
            (args.tc_pk,), fetch=True,
        )
        if rows:
            or_pk = int(rows[0]['or_pk'])
            _log.info(f'Smoke analyzing or_pk={or_pk}')
            AnalyzeManager(db).run(or_pk, min_signals=1, top_n=5)
    finally:
        ParameterGridBuilder.build = original_build

    return 0


def cmd_compare(args, db: DatabaseManager) -> int:
    """Side-by-side comparison of 2-4 optimizer runs. Output: console + CSV."""
    if not 2 <= len(args.or_pks) <= 4:
        _log.error(f'compare requires 2-4 or_pks (got {len(args.or_pks)})')
        return 1
    _log.info(f'Comparing or_pks={args.or_pks}')
    AnalyzeManager(db).compare(args.or_pks, output_dir=args.output_dir)
    return 0


def cmd_supervisor(args, db: DatabaseManager) -> int:
    """
    Drive the always-on data pipeline. Registers TickCollector and BarBuilder
    as continuous supervised workers, then blocks until SIGTERM / SIGINT.

    Workers receive db_kwargs (not the parent's DB connection) and construct
    their own connection inside the child process — multiprocessing.Process
    can't pickle live MySQL connections.

    The parent `db` connection is released before supervise() starts so we're
    not holding a connection while just supervising children.
    """
    db_kwargs = {
        'host':     os.environ.get('PK_DB_HOST',     'localhost'),
        'user':     os.environ.get('PK_DB_USER',     'root'),
        'password': os.environ.get('PK_DB_PASS',     'yourpassword'),
        'database': os.environ.get('PK_DB_NAME',     'pk_optimizer'),
        'port':     int(os.environ.get('PK_DB_PORT', 3306)),
    }

    # Backfill any gap between last stored 5s bar and now before
    # launching workers. Cold start fills the full 5-week lookback;
    # warm start fills whatever gap exists. SyntheticBackfiller
    # short-circuits on gaps under 30s, so this is cheap when the
    # supervisor has been running recently.
    _log.info('Checking kline_collection for backfill needs before launching workers')
    SyntheticBackfiller(db, BybitKlineClient()).backfill(args.tp_pk, args.symbol)

    # Parent doesn't need its DB while supervising — release it
    db.disconnect()

    pm = ProcessManager()
    pm.register(WorkerSpec(
        name              = 'tick_collector',
        target_fn         = tick_collector_worker,
        args              = (args.tp_pk, args.symbol, db_kwargs),
        restart_on_failure= True,
        interval_s        = None,        # continuous
        restart_delay_s   = 5.0,
    ))
    pm.register(WorkerSpec(
        name              = 'bar_builder',
        target_fn         = bar_builder_worker,
        args              = (args.tp_pk, db_kwargs),
        restart_on_failure= True,
        interval_s        = None,
        restart_delay_s   = 5.0,
    ))
    pm.start()  # blocks until SIGTERM/SIGINT
    return 0


def cmd_backfill_synthetic(args, db: DatabaseManager) -> int:
    client = BybitKlineClient()
    return SyntheticBackfiller(db, client).backfill(args.tp_pk, args.symbol) or 0


def cmd_backfill_binance(args, db: DatabaseManager) -> int:
    client = BinanceClient()
    bf     = BinanceBackfiller(db, client)
    if args.once:
        bf.backfill(args.tp_pk, args.symbol)
    else:
        bf.run_loop(args.tp_pk, args.symbol)
    return 0


def cmd_tick_collect(args, db: DatabaseManager) -> int:
    TickCollector(db).run(args.tp_pk, args.symbol)
    return 0


def cmd_bar_build(args, db: DatabaseManager) -> int:
    BarBuilder(db).run(args.tp_pk)
    return 0


def cmd_indicator_monitor(args, db: DatabaseManager) -> int:
    IndicatorMonitor(db).run(args.tp_pk, args.tc_pk)
    return 0


_DISPATCH = {
    'start':              cmd_start,
    'analyze':            cmd_analyze,
    'smoke':              cmd_smoke,
    'compare':            cmd_compare,
    'supervisor':         cmd_supervisor,
    'backfill_synthetic': cmd_backfill_synthetic,
    'backfill_binance':   cmd_backfill_binance,
    'tick_collect':       cmd_tick_collect,
    'bar_build':          cmd_bar_build,
    'indicator_monitor':  cmd_indicator_monitor,
}


# ─── entry ─────────────────────────────────────────────────────────────────
def main(argv: list = None) -> int:
    args = _build_parser().parse_args(argv)
    db   = _db()
    try:
        return _DISPATCH[args.cmd](args, db)
    finally:
        db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
