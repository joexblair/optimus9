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
  reconcile          5s pk signal reconciliation against Pine TradingView output.

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
from optimus9.config import get_db_config
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
    PKStateComputer,        # noqa: F401
    PKGateFilter,           # noqa: F401
    PKSignalDetector,       # noqa: F401
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
from optimus9.analysis.reconciler import Reconciler


_log = get_logger('run')


# ─── DB connection ─────────────────────────────────────────────────────────
def _db() -> DatabaseManager:
    db = DatabaseManager(**get_db_config())
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
    s.add_argument('--start_ms',      type=int, default=None,
                   help='Fixed kline window start, ms epoch (inclusive). '
                        'Use with --end_ms for reproducible validation grinds.')
    s.add_argument('--end_ms',        type=int, default=None,
                   help='Fixed kline window end, ms epoch (exclusive).')
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
    sv.add_argument('--lookback_days', type=int, default=35,
                    help='Ensure kline_collection has at least N days of 5s bars '
                         'before launching workers (default 35)')

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

    # reconcile ------------------------------------------------------------
    rc = sub.add_parser('reconcile',
                        help='5s pk signal reconciliation vs Pine TradingView output')
    rc.add_argument('--tp_pk',      type=int, default=1)
    rc.add_argument('--hours',      type=float, default=12.0,
                    help='Window size in hours (default 12)')
    rc.add_argument('--end_date',   type=str, default=None,
                    help='YYYY-MM-DD (end of day UTC). Default: now.')
    rc.add_argument('--output_dir', default='.')

    vg = sub.add_parser('validate_gate',
                        help='Goal-alignment report: per-PK win/stop + gate filter '
                             'blocks → gate_validation table + Pine overlay')
    vg.add_argument('--tp_pk',          type=int,   default=1)
    vg.add_argument('--lookback_hours', type=float, default=6.0)
    vg.add_argument('--stop_loss',      type=float, default=0.4)
    vg.add_argument('--profit_point',   type=float, default=0.9)
    vg.add_argument('--boundary_slip',  type=float, default=3.0,
                    help='loosen OOB boundaries inward by N (slip 3 → 18/82)')
    vg.add_argument('--end_ms',         type=int,   default=None,
                    help='time-machine end (ms); default = now (data max)')
    vg.add_argument('--pine',           default='gca5m_gate_validation.pine',
                    help='Pine overlay output path')

    cs = sub.add_parser('cluster_score',
                        help="Rank a grind's AM centroids by swing-catch profit "
                             '(near_swing/total_net) → cluster_scores table')
    cs.add_argument('--or_pk',       type=int,   required=True)
    cs.add_argument('--tp_pk',       type=int,   default=1)
    cs.add_argument('--top_n',       type=int,   default=20,
                    help='AM top-N centroids to score')
    cs.add_argument('--horizon',     type=int,   default=2160,
                    help='outcome-walk cap in 5s bars (default 3h)')
    cs.add_argument('--manual_stop', type=float, default=0.33,
                    help='trusted hand-traded stop; stop-sweep low anchor')

    bd = sub.add_parser('bl_detect',
                        help='BL 4-state detection for a line family (hb9) → '
                             'bl_states table + labelled Pine overlay')
    bd.add_argument('--lookback_hours', type=float, default=12.0)
    bd.add_argument('--curl_floor',     type=float, default=1.0)
    bd.add_argument('--curl_lookback',  type=int,   default=7,
                    help='curl slope window in bars (~bars before K reverses; default 7)')
    bd.add_argument('--flatten',        type=float, default=0.5)
    bd.add_argument('--pseudo_cross',   type=float, default=15.0)
    bd.add_argument('--grace',          type=int,   default=2,
                    help='bars to wait for a curl after an early exit3 (default 2)')
    bd.add_argument('--fence_pad',      type=float, default=5.0,
                    help='widen the no-prediction fence: hi += pad, lo -= pad '
                         '(default 5 → 25:75 engage band)')
    bd.add_argument('--end_ms',         type=int,   default=None,
                    help='time-machine end (ms); default = now (data max)')
    bd.add_argument('--pine',           default='bl_hb9_states.pine')

    tk = sub.add_parser('tape_check',
                        help='Scan kline_collection over a window for gaps, '
                             'continuity breaks (open != prev close) and OHLC sanity')
    tk.add_argument('--tp_pk', type=int,   default=1)
    tk.add_argument('--hours', type=float, default=12.0)

    dr = sub.add_parser('delete_run',
                        help='Cascade-delete an optimizer run (or_pk) + all related '
                             'rows; pk_signals/outcomes batched to dodge the lock table')
    dr.add_argument('--or_pk', type=int, required=True)
    dr.add_argument('--batch', type=int, default=100000,
                    help='pk_signals/outcomes rows per batch (lock-safe; default 100k)')

    return p


# ─── command handlers ──────────────────────────────────────────────────────

def cmd_start(args, db: DatabaseManager) -> int:
    p_rev_enabled     = (args.p_rev     == 'on')
    pk5s_gate_enabled = (args.pk5s_gate == 'on')

    if (args.start_ms is None) != (args.end_ms is None):
        _log.error('--start_ms and --end_ms must be supplied together')
        return 1

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
        start_ms          = args.start_ms,
        end_ms            = args.end_ms,
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
    # r07: read creds from optimus9_config.json via get_db_config (was a
    # hardcoded PK_DB_* env-fallback with a 'yourpassword' default that
    # systemd wouldn't have — it doesn't inherit the interactive shell env).
    # Children pickle this plain dict into their own processes.
    db_kwargs = get_db_config()

    # Backfill the last N days into kline_collection before launching
    # workers — ensures the table holds a guaranteed minimum coverage
    # window. SyntheticBackfiller's window mode always fetches the full
    # span; INSERT IGNORE dedupes against existing rows downstream.
    _log.info(f'Ensuring kline_collection holds last {args.lookback_days} days before launching workers')
    SyntheticBackfiller(db, BybitKlineClient()).backfill(
        args.tp_pk, args.symbol, lookback_days=args.lookback_days,
    )

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


def cmd_reconcile(args, db: DatabaseManager) -> int:
    Reconciler(db).reconcile(
        tp_pk      = args.tp_pk,
        end_date   = args.end_date,
        hours      = args.hours,
        output_dir = args.output_dir,
    )
    return 0


def cmd_validate_gate(args, db: DatabaseManager) -> int:
    from optimus9.analysis.goal_alignment import GoalAlignment
    ga = GoalAlignment(db, lookback_hours=args.lookback_hours, stop_loss=args.stop_loss,
                       profit_point=args.profit_point, tp_pk=args.tp_pk,
                       boundary_slip=args.boundary_slip)
    rows  = ga.report(end_ms=args.end_ms)
    won   = sum(r['win_ms'] is not None for r in rows)
    gated = sum(r['gated'] for r in rows)
    _log.info(f'gate_validation: {len(rows)} PKs | won {won} | gated {gated} → table gate_validation')
    ga.emit_pine(rows, args.pine)
    _log.info(f'Pine overlay → {args.pine}')
    return 0


def cmd_cluster_score(args, db: DatabaseManager) -> int:
    from optimus9.analysis.cluster_scoring import ClusterScoring
    cs   = ClusterScoring(db, tp_pk=args.tp_pk, top_n=args.top_n,
                          horizon=args.horizon, manual_stop=args.manual_stop)
    rows = cs.score(args.or_pk)
    top  = rows[0]
    _log.info(f'cluster_scores: {len(rows)} centroids → table cluster_scores | '
              f'#1 {top["combo"]} near_swing={top["near_swing"]:.2f} '
              f'total_net={top["total_net"]:.2f}')
    return 0


def cmd_tape_check(args, db: DatabaseManager) -> int:
    """Loud data-quality gate over kline_collection: missing bars, non-gapless
    seams (open != prior close), and OHLC sanity. PASS/FAIL verdict."""
    import datetime as _dt
    tp, hours, bar = args.tp_pk, args.hours, 5000
    mx = db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=%s',
                    (tp,), fetch=True)[0]['m']
    if mx is None:
        _log.error(f'tape_check tp={tp}: no klines'); return 1
    end   = int(mx)
    start = end - int(hours * 3600 * 1000)
    rows  = db.execute(
        '''SELECT kc_timestamp ts, kc_open o, kc_high h, kc_low l, kc_close c
           FROM kline_collection WHERE kc_tp_pk=%s AND kc_timestamp BETWEEN %s AND %s
           ORDER BY kc_timestamp''', (tp, start, end), fetch=True)

    def _u(ms): return _dt.datetime.fromtimestamp(ms / 1000, tz=_dt.timezone.utc).strftime('%m-%d %H:%M:%S')
    gaps, seams = [], []
    for i in range(1, len(rows)):
        dt = int(rows[i]['ts']) - int(rows[i - 1]['ts'])
        if dt != bar:
            gaps.append((rows[i - 1]['ts'], rows[i]['ts'], (dt - bar) // bar))
        elif abs(float(rows[i]['o']) - float(rows[i - 1]['c'])) > 1e-9:
            seams.append((rows[i]['ts'], float(rows[i - 1]['c']), float(rows[i]['o'])))
    bad = [r['ts'] for r in rows
           if not (float(r['h']) >= max(float(r['o']), float(r['c']))
                   and float(r['l']) <= min(float(r['o']), float(r['c']))
                   and float(r['h']) >= float(r['l']))]

    expected = (end - start) // bar + 1
    _log.info(f'tape_check tp={tp} last {hours}h: {len(rows):,} bars (expect ~{expected:,}) '
              f'| missing-bar gaps={len(gaps)}  non-gapless seams={len(seams)}  bad-OHLC={len(bad)}')
    for ts0, ts1, miss in gaps[:5]:
        _log.info(f'  GAP {miss} bar(s): {_u(int(ts0))} -> {_u(int(ts1))}')
    for ts, pc, o in seams[:5]:
        _log.info(f'  SEAM @ {_u(int(ts))}: open {o} != prev close {pc} '
                  f'({(o - pc) / pc * 1e4:+.2f} bps)')
    for ts in bad[:5]:
        _log.info(f'  BAD-OHLC @ {_u(int(ts))}')
    verdict = 'PASS' if not (gaps or seams or bad) else 'FAIL'
    _log.info(f'tape_check: {verdict}')
    return 0 if verdict == 'PASS' else 1


def cmd_delete_run(args, db: DatabaseManager) -> int:
    """Cascade-delete one optimizer run. The big children (pk_signals + their
    pk_outcomes) are deleted in pks_pk ranges so each statement stays under the
    InnoDB lock table (the 1206 error on full-table deletes)."""
    orp, batch = args.or_pk, args.batch
    r = db.execute(
        'SELECT MIN(pks_pk) lo, MAX(pks_pk) hi, COUNT(*) n FROM pk_signals WHERE pks_or_pk=%s',
        (orp,), fetch=True)[0]
    if r['lo'] is not None:
        lo, hi, n = int(r['lo']), int(r['hi']), int(r['n'])
        _log.info(f'delete_run or_pk={orp}: {n:,} pk_signals (+outcomes) in '
                  f'pks_pk [{lo:,}..{hi:,}], batch={batch:,}')
        cur, i = lo, 0
        while cur <= hi:
            top = cur + batch
            db.execute('''DELETE o FROM pk_outcomes o JOIN pk_signals s
                          ON o.pko_pks_pk = s.pks_pk
                          WHERE s.pks_or_pk=%s AND s.pks_pk>=%s AND s.pks_pk<%s''',
                       (orp, cur, top))
            db.execute('DELETE FROM pk_signals WHERE pks_or_pk=%s AND pks_pk>=%s AND pks_pk<%s',
                       (orp, cur, top))
            i += 1
            if i % 10 == 0 or top > hi:
                _log.info(f'  cleared to pks_pk {min(top,hi):,}  '
                          f'(~{min(100,(cur-lo)*100//max(hi-lo,1))}%)')
            cur = top
    else:
        _log.info(f'delete_run or_pk={orp}: no pk_signals')

    for sql, label in (
        ('DELETE FROM pk_combo_summary WHERE pcs_or_pk=%s', 'pk_combo_summary'),
        ('''DELETE acs FROM am_centroid_signals acs JOIN am_centroids amc
            ON acs.acs_amc_pk = amc.amc_pk WHERE amc.amc_or_pk=%s''', 'am_centroid_signals'),
        ('DELETE FROM am_centroids WHERE amc_or_pk=%s', 'am_centroids'),
        ('DELETE FROM cluster_scores WHERE cs_or_pk=%s', 'cluster_scores'),
        ('DELETE FROM optimizer_runs WHERE or_pk=%s', 'optimizer_runs'),
    ):
        try:
            db.execute(sql, (orp,)); _log.info(f'  deleted {label}')
        except Exception as e:                       # table may not exist for every run
            _log.warning(f'  skip {label}: {str(e)[:70]}')
    _log.info(f'delete_run or_pk={orp}: done')
    return 0


def cmd_bl_detect(args, db: DatabaseManager) -> int:
    import collections
    from optimus9.analysis.bl_detect import BLDetect
    d    = BLDetect(db, lookback_hours=args.lookback_hours, curl_floor=args.curl_floor,
                    curl_lookback=args.curl_lookback, flatten=args.flatten,
                    pseudo_cross=args.pseudo_cross, grace=args.grace,
                    fence_pad=args.fence_pad)
    rows = d.report(end_ms=args.end_ms)
    d.emit_pine(rows, args.pine)
    dist = dict(sorted(collections.Counter(
        r['state'] for r in rows if r['hb9b'] is not None).items()))
    _log.info(f'bl_states: {len(rows)} bars → table bl_states | states {dist} | '
              f'Pine → {args.pine}')
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
    'reconcile':          cmd_reconcile,
    'validate_gate':      cmd_validate_gate,
    'cluster_score':      cmd_cluster_score,
    'bl_detect':          cmd_bl_detect,
    'delete_run':         cmd_delete_run,
    'tape_check':         cmd_tape_check,
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
