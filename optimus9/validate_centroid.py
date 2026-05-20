"""
validate_centroid — pick top-1 PROVEN combo for an or_pk, emit CSV +
Pine for visual sanity check on TradingView.

Why top-1 not centroid:
  The 'centroid' in analyze_manager is a weighted average of top-20 params;
  it may not be a grid point we actually tested. For Pine validation we
  need real signal timestamps, so we lift the BEST tested combo
  (highest expectancy with ≥30 decided signals) and inspect its fires.

CSV output (per-signal rows + footer aggregates):
  signal_id, datetime, direction, max_pct, won, max_at, stop_at,
  bars_to_max, bars_to_stop
  Datetime format: 'MMDD HH:MM:SS' UTC

Pine emit:
  Standalone overlay indicator with all signal timestamps as array.push
  calls. Drop into TV editor → attach to FARTCOINUSDT 5s → arrows should
  land on the recorded bars. Set chart TZ to UTC to match.

Usage (standalone):
  python3 validate_centroid.py --or_pk 20 --emit_pine

Usage (from run.py post-analyze hook):
  from validate_centroid import validate
  validate(db, or_pk, output_dir='.', emit_pine=True)
"""

import argparse
import csv
import os
from datetime import datetime, timezone
from typing import Optional

from logger import get_logger

from optimus9.db.database_manager import DatabaseManager

_log = get_logger('validate_centroid')

# 5s bar in milliseconds — for ts + bars_to_X * BAR_MS arithmetic
_BAR_MS = 5_000


def _fmt_dt(ts_ms: Optional[int]) -> str:
    """Format ms-epoch as 'MMDD HH:MM:SS' UTC. Empty if None."""
    if ts_ms is None:
        return ''
    return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime('%m%d %H:%M:%S')


def _load_run_context(db: DatabaseManager, or_pk: int) -> dict:
    """
    Resolve the stop_pct, profit_zone, tc_indicator_label, ic_line_type
    for this or_pk by joining through optimizer_runs → test_configs →
    indicator_configs.
    """
    rows = db.execute(
        '''SELECT
               r.or_pk,
               tc.tc_pk,
               tc.tc_indicator_label,
               tc.tc_stop_pct,
               tc.tc_profit_zone,
               ic.ic_pk,
               ic.ic_line_type
           FROM optimizer_runs r
           JOIN test_configs tc      ON tc.tc_pk = r.or_tc_pk
           JOIN indicator_configs ic ON ic.ic_pk = tc.tc_ic_pk
           WHERE r.or_pk = %s''',
        (or_pk,), fetch=True,
    )
    if not rows:
        raise ValueError(f'No optimizer_runs row for or_pk={or_pk}')
    r = rows[0]
    return {
        'or_pk':        int(r['or_pk']),
        'tc_pk':        int(r['tc_pk']),
        'tc_label':     r['tc_indicator_label'],
        'stop_pct':     float(r['tc_stop_pct']),
        'profit_zone':  float(r['tc_profit_zone']),
        'ic_pk':        int(r['ic_pk']),
        'line_type':    r['ic_line_type'],
    }


def _query_proven_combo(db: DatabaseManager, or_pk: int,
                        stop_pct: float, profit_zone: float,
                        min_decided: int = 30,
                        top_stage1: int = 100,
                        dd_threshold: float = 0.15) -> dict:
    """
    Pick PROVEN COMBO via the AM v2 two-stage ranker:
      Stage 1: top top_stage1 combos by expectancy with ≥min_decided decided
      Stage 2: walk equity per combo, sort by gross_banked, DD-filter

    Returns the dict-row of the Stage 2 rank #1 combo (with all param +
    metric columns populated).
    """
    # Stage 1: top N by expectancy
    stage1 = db.execute(
        f'''SELECT
                s.pks_len,
                s.pks_mult,
                s.pks_src,
                s.pks_len_rsi,
                s.pks_len_stoch,
                s.pks_pool_c,
                s.pks_pool_w,
                s.pks_pool_range,
                s.pks_slope_floor,
                s.pks_multiplier,
                COUNT(*) AS n_signals,
                SUM(CASE WHEN o.pko_max_profit_pct >= %s THEN 1 ELSE 0 END) AS won,
                SUM(CASE WHEN o.pko_bars_to_stop IS NOT NULL
                          AND (o.pko_max_profit_pct IS NULL
                               OR o.pko_max_profit_pct < %s) THEN 1 ELSE 0 END) AS stopped,
                AVG(CASE WHEN o.pko_max_profit_pct >= %s
                          THEN o.pko_max_profit_pct ELSE NULL END) AS avg_won_pct
            FROM pk_signals s
            LEFT JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
            WHERE s.pks_or_pk = %s
            GROUP BY s.pks_len, s.pks_mult, s.pks_src,
                     s.pks_len_rsi, s.pks_len_stoch,
                     s.pks_pool_c, s.pks_pool_w, s.pks_pool_range,
                     s.pks_slope_floor, s.pks_multiplier
            HAVING (won + stopped) >= %s
            ORDER BY
                (won * COALESCE(avg_won_pct, 0) - stopped * %s) / (won + stopped) DESC
            LIMIT %s''',
        (profit_zone, profit_zone, profit_zone, or_pk,
         min_decided, stop_pct, top_stage1),
        fetch=True,
    )
    if not stage1:
        raise RuntimeError(
            f'No combo with ≥{min_decided} decided signals for or_pk={or_pk}'
        )

    # Stage 2: walk equity per combo, pick best gross_banked under DD threshold
    best = None
    best_banked = -float('inf')
    for combo in stage1:
        signals = _query_combo_signals(db, or_pk, combo)
        metrics = _walk_equity(signals, profit_zone, stop_pct)
        if metrics['max_drawdown'] > dd_threshold:
            continue
        if metrics['gross_banked'] > best_banked:
            best_banked = metrics['gross_banked']
            best = {**combo, **metrics}

    if best is None:
        _log.warning(f'All {len(stage1)} Stage 1 combos exceeded DD threshold '
                     f'{dd_threshold*100:.0f}% — falling back to top expectancy')
        # Fallback: use top expectancy combo despite DD
        signals = _query_combo_signals(db, or_pk, stage1[0])
        metrics = _walk_equity(signals, profit_zone, stop_pct)
        best = {**stage1[0], **metrics}

    return best


def _walk_equity(signals: list, profit_zone: float, stop_pct: float,
                 seed: float = 1000.0) -> dict:
    """Mirror of AnalyzeManager._walk_equity for the validator's standalone use."""
    import numpy as np
    equity, peak, max_dd = seed, seed, 0.0
    won_pcts, stopped, inconc = [], 0, 0
    gross_wins, gross_losses = 0.0, 0.0
    pnls = []
    for s in signals:
        mp  = float(s['max_pct']) if s['max_pct'] is not None else None
        bts = s['bts'] if 'bts' in s else s.get('bars_to_stop')
        if mp is not None and mp >= profit_zone:
            pnl = mp
            won_pcts.append(mp)
            gross_wins += mp
        elif bts is not None:
            pnl = -stop_pct
            stopped += 1
            gross_losses += stop_pct
        else:
            pnl = 0.0
            inconc += 1
        pnls.append(pnl)
        equity *= (1.0 + pnl / 100.0)
        peak = max(peak, equity)
        if peak > 0:
            dd = (peak - equity) / peak
            if dd > max_dd:
                max_dd = dd
    n = len(pnls)
    n_won = len(won_pcts)
    arr = np.array(pnls)
    neg = arr[arr < 0]
    mean_pnl = float(arr.mean()) if n else 0.0
    std_pnl  = float(arr.std(ddof=0)) if n > 1 else 0.0
    std_neg  = float(neg.std(ddof=0)) if len(neg) > 1 else 0.0
    decided = n_won + stopped
    return {
        'gross_banked':  equity,
        'max_drawdown':  max_dd,
        'profit_factor': (gross_wins / gross_losses) if gross_losses > 0 else float('inf'),
        'sharpe':        (mean_pnl / std_pnl) if std_pnl > 0 else float('inf'),
        'sortino':       (mean_pnl / std_neg) if std_neg > 0 else float('inf'),
        'n_won':         n_won,
        'n_stopped':     stopped,
        'n_inconc':      inconc,
        'win_rate':      (n_won / decided) if decided else 0.0,
        'avg_won_pct':   (sum(won_pcts) / n_won) if n_won else 0.0,
        'min_won_pct':   min(won_pcts) if won_pcts else 0.0,
        'win95_flag':    1 if decided and (n_won / decided) > 0.95 else 0,
    }


def _query_combo_signals_for_combo(db, or_pk, combo):
    """Wrapper: dispatch to _query_combo_signals using DB-row dict keys."""
    return _query_combo_signals(db, or_pk, combo)


def _query_combo_signals(db: DatabaseManager, or_pk: int, combo: dict) -> list:
    """
    Pull every signal for the chosen combo. Build WHERE clause with IS NULL
    handling for K-vs-BB param distinctions.

    `combo` is a row from Stage 1 SQL — keys are `pks_*`. Map them to
    column names directly.
    """
    where, vals = ['s.pks_or_pk = %s'], [or_pk]
    for col in (
        'pks_len', 'pks_mult', 'pks_src',
        'pks_len_rsi', 'pks_len_stoch',
        'pks_pool_c', 'pks_pool_w', 'pks_pool_range',
        'pks_slope_floor', 'pks_multiplier',
    ):
        val = combo.get(col)
        if val is None:
            where.append(f's.{col} IS NULL')
        else:
            where.append(f's.{col} = %s')
            vals.append(val)

    sql = f'''
        SELECT
            s.pks_pk            AS signal_id,
            s.pks_timestamp     AS ts,
            s.pks_dir           AS direction,
            o.pko_max_profit_pct        AS max_pct,
            o.pko_bars_to_max_profit    AS bars_to_max,
            o.pko_bars_to_stop          AS bars_to_stop
        FROM pk_signals s
        LEFT JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
        WHERE {' AND '.join(where)}
        ORDER BY s.pks_timestamp
    '''
    rows = db.execute(sql, tuple(vals), fetch=True)
    # Normalize key names so _walk_equity and the CSV writer both work
    for r in rows:
        r['bts'] = r.get('bars_to_stop')
    return rows


def _format_params(combo: dict) -> str:
    """Render the combo's params as a one-line summary. Accepts pks_* keys."""
    parts = []
    if combo.get('pks_len') is not None:
        parts.append(f'len={combo["pks_len"]}')
    if combo.get('pks_mult') is not None:
        parts.append(f'mult={float(combo["pks_mult"]):.2f}')
    if combo.get('pks_len_rsi') is not None:
        parts.append(f'len_rsi={combo["pks_len_rsi"]}')
    if combo.get('pks_len_stoch') is not None:
        parts.append(f'len_stoch={combo["pks_len_stoch"]}')
    parts.append(f'src={combo["pks_src"]}')
    parts.append(f'pool_c={combo["pks_pool_c"]}')
    parts.append(f'pool_w={combo["pks_pool_w"]}')
    parts.append(f'pool_range={combo["pks_pool_range"]}')
    parts.append(f'slope_floor={float(combo["pks_slope_floor"])}')
    parts.append(f'multiplier={combo["pks_multiplier"]}')
    return ', '.join(parts)


def _write_csv(path: str, ctx: dict, combo: dict, signals: list,
               profit_zone: float) -> None:
    """
    Write per-signal rows + footer with aggregates. The walked metrics
    (gross_banked, max_drawdown, PF, Sharpe, Sortino) are already on the
    combo dict from _query_proven_combo.

    Per-signal columns include `win_pct` (the trade's actual P&L) and
    `endoftrade_timestamp` (when the trade closed — at max if won, at
    stop if stopped, blank if inconclusive). These enable side-by-side
    comparison with TV's strategy trade log.
    """
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)

        # Header block
        w.writerow(['# validate_centroid output'])
        w.writerow([f'# or_pk={ctx["or_pk"]}  tc={ctx["tc_label"]}  '
                    f'line_type={ctx["line_type"]}'])
        w.writerow([f'# stop_pct={ctx["stop_pct"]:.4f}  '
                    f'profit_zone={profit_zone:.4f}'])
        w.writerow([f'# combo (PROVEN, Stage 2 rank #1): {_format_params(combo)}'])
        w.writerow([])

        # Per-signal rows
        w.writerow(['signal_id', 'datetime', 'direction',
                    'win_pct', 'won', 'max_pct',
                    'max_at', 'endoftrade_timestamp',
                    'bars_to_max', 'bars_to_stop'])
        for s in signals:
            ts = int(s['ts'])
            d  = int(s['direction'])
            mp = float(s['max_pct']) if s['max_pct'] is not None else None
            btm = s.get('bars_to_max')
            bts = s.get('bars_to_stop')

            # Determine trade outcome and P&L
            if mp is not None and mp >= profit_zone:
                win_pct       = mp
                won           = '1'
                eot_ms        = ts + int(btm) * _BAR_MS if btm is not None else None
            elif bts is not None:
                win_pct       = -ctx['stop_pct']
                won           = '0'
                eot_ms        = ts + int(bts) * _BAR_MS
            else:
                win_pct       = None
                won           = ''     # inconclusive — no resolution
                eot_ms        = None

            max_at_ms = ts + int(btm) * _BAR_MS if btm is not None else None

            w.writerow([
                s['signal_id'],
                _fmt_dt(ts),
                'LONG' if d == 1 else ('SHORT' if d == -1 else str(d)),
                f'{win_pct:+.4f}' if win_pct is not None else '',
                won,
                f'{mp:.4f}' if mp is not None else '',
                _fmt_dt(max_at_ms),
                _fmt_dt(eot_ms),
                btm if btm is not None else '',
                bts if bts is not None else '',
            ])

        # Footer aggregates (already computed by _walk_equity on combo)
        w.writerow([])
        w.writerow(['# AGGREGATES (Stage 2 metrics for this combo)'])
        w.writerow(['n_signals',     len(signals)])
        w.writerow(['n_won',         combo.get('n_won', '')])
        w.writerow(['n_stopped',     combo.get('n_stopped', '')])
        w.writerow(['n_inconclusive', combo.get('n_inconc', '')])
        w.writerow(['win_rate',      f'{combo["win_rate"]:.4f}'])
        w.writerow(['expectancy_pct', f'{(combo["win_rate"] * combo["avg_won_pct"] - (1-combo["win_rate"]) * ctx["stop_pct"]):.4f}'])
        w.writerow(['avg_won_pct',   f'{combo["avg_won_pct"]:.4f}'])
        w.writerow(['min_won_pct',   f'{combo["min_won_pct"]:.4f}'])
        w.writerow(['gross_banked',  f'{combo["gross_banked"]:.2f}'])
        w.writerow(['max_drawdown',  f'{combo["max_drawdown"]:.4f}'])
        w.writerow(['profit_factor', _fmt_inf(combo['profit_factor'])])
        w.writerow(['sharpe',        _fmt_inf(combo['sharpe'])])
        w.writerow(['sortino',       _fmt_inf(combo['sortino'])])
        w.writerow(['win95_flag',    combo['win95_flag']])


def _fmt_inf(v) -> str:
    import math
    if v is None:
        return ''
    try:
        f = float(v)
        if not math.isfinite(f):
            return 'inf'
        return f'{f:.4f}'
    except (TypeError, ValueError):
        return ''


def _emit_pine(path: str, ctx: dict, combo: dict, signals: list,
               profit_zone: float) -> None:
    """
    Write a self-contained Pine v5 overlay indicator with all signal
    timestamps + directions baked in as array.push calls.

    Drop into TV editor, attach to FARTCOINUSDT 5s, set chart timezone to
    UTC. Arrows should fire on the exact bars we recorded.
    """
    title = f'O9 r05 validate or_pk={ctx["or_pk"]} ({ctx["tc_label"]})'
    win_rate_str = f'{combo["win_rate"]*100:.1f}%'
    expectancy = combo['win_rate'] * combo['avg_won_pct'] - (1 - combo['win_rate']) * ctx['stop_pct']
    flag = ' ⚠ win95' if combo.get('win95_flag') else ''

    header = [
        '//@version=5',
        f'indicator("{title}", overlay=true, max_labels_count=500)',
        '',
        '// ── Validation snapshot (PROVEN COMBO, Stage 2 rank #1) ──',
        f'//   or_pk:     {ctx["or_pk"]}',
        f'//   tc:        {ctx["tc_label"]}  (ic_pk={ctx["ic_pk"]}, line_type={ctx["line_type"]})',
        f'//   stop_pct:  {ctx["stop_pct"]:.4f}    profit_zone: {profit_zone:.4f}',
        f'//   params:    {_format_params(combo)}',
        f'//   stats:     n={len(signals)}  win={win_rate_str}  '
        f'exp={expectancy:+.4f}%  gross_banked=${combo["gross_banked"]:,.0f}  '
        f'max_dd={combo["max_drawdown"]*100:.2f}%  '
        f'min_won={combo["min_won_pct"]:.4f}%{flag}',
        '',
        '// Recorded signals — bake timestamps + directions into arrays',
        'var int[] sig_ts  = array.new<int>(0)',
        'var int[] sig_dir = array.new<int>(0)',
        '',
        'if barstate.isfirst',
    ]

    push_lines = []
    for s in signals:
        ts = int(s['ts'])
        d  = int(s['direction'])
        push_lines.append(f'    array.push(sig_ts, {ts})  ; array.push(sig_dir, {d:>2})')

    footer = [
        '',
        '// Match the current bar timestamp against every recorded signal',
        'isLong  = false',
        'isShort = false',
        'n = array.size(sig_ts)',
        'for i = 0 to n - 1',
        '    if array.get(sig_ts, i) == time',
        '        d = array.get(sig_dir, i)',
        '        if d == 1',
        '            isLong  := true',
        '        else',
        '            isShort := true',
        '',
        'plotshape(isLong,  style=shape.triangleup,   location=location.belowbar, '
        'color=color.lime, size=size.small, title="LONG")',
        'plotshape(isShort, style=shape.triangledown, location=location.abovebar, '
        'color=color.red,  size=size.small, title="SHORT")',
    ]

    with open(path, 'w') as f:
        f.write('\n'.join(header + push_lines + footer) + '\n')


def validate(db: DatabaseManager, or_pk: int,
             output_dir: str = '.',
             emit_pine: bool = False,
             min_decided: int = 30,
             top_stage1: int = 100,
             dd_threshold: float = 0.15) -> dict:
    """
    Run the full validation flow for or_pk using AM v2 ranker:
      Stage 1: top top_stage1 combos by expectancy
      Stage 2: walk equity, pick best gross_banked among DD-qualifying

    Picks the PROVEN COMBO and writes CSV (always) + Pine (if requested).
    Returns the combo dict (with walked metrics attached).
    """
    ctx   = _load_run_context(db, or_pk)
    combo = _query_proven_combo(
        db, or_pk,
        ctx['stop_pct'], ctx['profit_zone'],
        min_decided=min_decided,
        top_stage1=top_stage1,
        dd_threshold=dd_threshold,
    )
    signals = _query_combo_signals(db, or_pk, combo)

    _log.info(f'validate or_pk={or_pk}  tc={ctx["tc_label"]}')
    _log.info(f'  combo: {_format_params(combo)}')
    _log.info(
        f'  signals={len(signals)}  '
        f'won={combo["n_won"]}  '
        f'stopped={combo["n_stopped"]}  '
        f'inconclusive={combo["n_inconc"]}'
    )
    expectancy = combo['win_rate'] * combo['avg_won_pct'] - (1 - combo['win_rate']) * ctx['stop_pct']
    _log.info(
        f'  expectancy={expectancy:+.4f}%  '
        f'win={combo["win_rate"]*100:.1f}%  '
        f'gross_banked=${combo["gross_banked"]:,.0f}  '
        f'max_dd={combo["max_drawdown"]*100:.2f}%  '
        f'min_won={combo["min_won_pct"]:.4f}%'
        + (' ⚠ win95' if combo.get('win95_flag') else '')
    )

    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, f'validate_or{or_pk}.csv')
    _write_csv(csv_path, ctx, combo, signals, ctx['profit_zone'])
    _log.info(f'  csv → {csv_path}')

    if emit_pine:
        pine_path = os.path.join(output_dir, f'validate_or{or_pk}.pine')
        _emit_pine(pine_path, ctx, combo, signals, ctx['profit_zone'])
        _log.info(f'  pine → {pine_path}')

    return combo


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument('--or_pk',  type=int, help='single or_pk to validate')
    grp.add_argument('--or_pks', type=str,
                     help='comma-separated or_pks for batch validation, '
                          'e.g. --or_pks=20,21,22,17,18,19')
    parser.add_argument('--output_dir',    type=str, default='.')
    parser.add_argument('--emit_pine',     action='store_true')
    parser.add_argument('--min_decided',   type=int,   default=30)
    parser.add_argument('--top_stage1',    type=int,   default=100)
    parser.add_argument('--dd_threshold',  type=float, default=0.15)
    args = parser.parse_args()

    or_pks = ([args.or_pk] if args.or_pk is not None
              else [int(p) for p in args.or_pks.split(',')])

    db = DatabaseManager()
    try:
        db.connect()
        for op in or_pks:
            try:
                validate(db, op, args.output_dir, args.emit_pine,
                         args.min_decided, args.top_stage1, args.dd_threshold)
            except Exception as e:
                _log.error(f'or_pk={op} failed: {e}')
    finally:
        db.disconnect()
