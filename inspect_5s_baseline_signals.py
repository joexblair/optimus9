"""
inspect_5s_baseline_signals.py — per-stop simulation for the baseline
signals StopCalibrator generates for a 5s singular tc.

Pure math model (no trading vocabulary):

  For each signal:
    start = dema[signal_bar]
    Record full forward DEMA trajectory (no horizon cap — walk until
    end of dataset)

  For each candidate stop S:
    For each signal:
      stop_level = start * (1 - S/100)  for LONG signals
                 = start * (1 + S/100)  for SHORT signals
      Walk trajectory:
        Track running_mfe (max favorable pct from start)
        First bar where DEMA crosses stop_level → halt, record stop bar
        End of dataset reached → halt, no stop bar (incomplete)
      Classify:
        stopped + running_mfe >= 0.6  → 'won'         banked = running_mfe
        stopped + running_mfe <  0.6  → 'stopped'     loss   = S
        not stopped (end-of-data)     → 'incomplete'  no bank, no loss

Per-stop aggregate:
  total / won / stopped / incomplete
  gross_profit = sum(running_mfe for won signals)
  gross_loss   = S * stopped_count
  net          = gross_profit - gross_loss

DEMA used throughout (not OHLC). Single-bar wicks don't trigger stops.

Usage:
    python3 inspect_5s_baseline_signals.py --tc_pk 2 --lookback_days 1
"""
import argparse
import json
import os
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from logger import get_logger
from optimus9.db.database_manager import DatabaseManager
from optimus9.compute.pk5s_gate_computer import Pk5sGateComputer
from optimus9.compute.indicator_computer import IndicatorComputer

_MIDPOINT = 50.0
_PROFIT_ZONE = 0.60   # win threshold (from tc.tc_profit_zone)
_CEILING = 1.0        # scalper exit ceiling — running_mfe >= 1% halts walk,
                      # banked = ceiling. Models the reality that scalpers
                      # take profit around 1%; the inspector should not
                      # credit signals for multi-day swings that no scalper
                      # would actually capture.
_LONG_WALK_BARS = 520 # flag for review when stop walk took longer than this


def _db():
    db = DatabaseManager(
        host     = os.environ.get('PK_DB_HOST', 'localhost'),
        user     = os.environ.get('PK_DB_USER', 'root'),
        password = os.environ.get('PK_DB_PASS', 'yourpassword'),
        database = os.environ.get('PK_DB_NAME', 'pk_optimizer'),
        port     = int(os.environ.get('PK_DB_PORT', 3306)),
    )
    db.connect()
    return db


def load_tc(db, tc_pk: int) -> dict:
    rows = db.execute(
        '''SELECT tc.*, ic.ic_line_type, ic.ic_src,
                  ic.ic_bb_len, ic.ic_bb_mult,
                  ic.ic_k_len, ic.ic_rsi_len, ic.ic_stc_len
           FROM test_configs tc
           JOIN indicator_configs ic ON ic.ic_pk = tc.tc_ic_pk
           WHERE tc.tc_pk = %s''',
        (tc_pk,), fetch=True,
    )
    if not rows:
        raise ValueError(f'No tc for tc_pk={tc_pk}')
    return rows[0]


def load_pool_params(db) -> dict:
    rows = db.execute(
        '''SELECT tce_params FROM test_config_extensions
           WHERE tce_type = 'pk_5s' AND tce_is_active = 1
           ORDER BY tce_pk DESC LIMIT 1''',
        (), fetch=True,
    )
    p = rows[0]['tce_params']
    if isinstance(p, (str, bytes)):
        p = json.loads(p)
    return p


def load_weights(db, ic_pk: int) -> tuple:
    rows = db.execute(
        '''SELECT tcev.tcev_weight_close, tcev.tcev_weight_wide
           FROM test_config_ext_votes tcev
           JOIN test_config_extensions tce ON tce.tce_pk = tcev.tcev_tce_pk
           WHERE tce.tce_type = 'pk_5s' AND tce.tce_is_active = 1
             AND tcev.tcev_ic_pk = %s AND tcev.tcev_is_active = 1
           ORDER BY tce.tce_pk DESC LIMIT 1''',
        (ic_pk,), fetch=True,
    )
    if not rows:
        return (5, 2)
    return (int(rows[0]['tcev_weight_close']),
            int(rows[0]['tcev_weight_wide']))


def load_klines(db, tp_pk: int, lookback_days: float) -> pd.DataFrame:
    cutoff_ms = int(
        (datetime.now(timezone.utc) - timedelta(days=lookback_days))
        .timestamp() * 1000
    )
    rows = db.execute(
        '''SELECT kc_timestamp AS timestamp, kc_open AS open, kc_high AS high,
                  kc_low AS low, kc_close AS close, kc_volume AS volume
           FROM kline_collection
           WHERE kc_tp_pk = %s AND kc_timestamp >= %s
           ORDER BY kc_timestamp ASC''',
        (tp_pk, cutoff_ms), fetch=True,
    )
    return pd.DataFrame(rows)


def build_vote(tc, w_close, w_wide):
    v = {
        'tcev_weight_close':  w_close,
        'tcev_weight_wide':   w_wide,
        'tcev_trigger_mode':  'standard_pk',
        'tcev_roc_threshold': None,
        'ic_itf_seconds':     5,
        'ic_src':             tc['ic_src'],
    }
    if tc['ic_line_type'] == 'bb':
        v.update({'ic_line_type': 'bb',
                  'ic_bb_len':    int(tc['ic_bb_len']),
                  'ic_bb_mult':   float(tc['ic_bb_mult']),
                  'ic_k_len': None, 'ic_rsi_len': None, 'ic_stc_len': None})
    else:
        v.update({'ic_line_type': 'k',
                  'ic_bb_len': None, 'ic_bb_mult': None,
                  'ic_k_len':    int(tc['ic_k_len']),
                  'ic_rsi_len':  int(tc['ic_rsi_len']),
                  'ic_stc_len':  int(tc['ic_stc_len'])})
    return v


def build_trajectory(entry_idx: int, direction: int,
                     dema: np.ndarray) -> dict:
    """
    Walk forward from entry to end of dataset. Record DEMA values and
    running MFE at each bar. No horizon cap. No stop applied.
    Used as the input to per-stop simulation.

    Returns dict with:
      start         — DEMA[entry_idx]
      direction     — +1 LONG, -1 SHORT
      dema_path     — np.ndarray of DEMA values from entry+1 to end
      favorable     — np.ndarray of favorable% at each bar
      running_mfe   — np.ndarray of cumulative max favorable% at each bar
    """
    start = float(dema[entry_idx])
    end   = len(dema) - 1
    path  = dema[entry_idx+1 : end+1].astype(float)

    if direction == 1:
        favorable = (path - start) / start * 100.0
    else:
        favorable = (start - path) / start * 100.0

    running_mfe = np.maximum.accumulate(favorable)
    # Guard: first bar can be negative favorable; running_mfe should not go
    # below 0 (no profit yet). Equivalent to max(favorable, 0) accumulate.
    running_mfe = np.maximum(running_mfe, 0.0)

    return {
        'start':       start,
        'direction':   direction,
        'dema_path':   path,
        'favorable':   favorable,
        'running_mfe': running_mfe,
    }


def simulate_signal_at_stop(traj: dict, stop_pct: float,
                            profit_zone: float = _PROFIT_ZONE,
                            ceiling: float = _CEILING) -> dict:
    """
    For one signal trajectory at one candidate stop, find the FIRST halt
    event among: ceiling-hit, stop-cross, end-of-dataset.

    Halt order matters: a trade that hits ceiling before stop is exited
    at ceiling regardless of any subsequent stop crossing — scalper
    semantics (take profit at +1%, don't sit through the round-trip back
    to stop). Joe's clarification this round.

    Returns:
      stop_bar       — bar where DEMA crossed stop_level (or None if not the halt)
      ceiling_bar    — bar where running_mfe reached ceiling (or None)
      halt_bar       — actual halt bar (whichever event won the race)
      bars_walked    — total bars walked before halt
      running_mfe    — favorable% captured up to halt
      outcome        — 'won_ceiling' | 'won_stopped' | 'stopped' | 'incomplete'
      banked         — ceiling (1.0) for won_ceiling; mfe for won_stopped; 0 else
      lost           — stop_pct if 'stopped'; 0 else
      walked_past    — True if bars_walked > _LONG_WALK_BARS (review flag)
    """
    start     = traj['start']
    direction = traj['direction']
    path      = traj['dema_path']
    mfe_curve = traj['running_mfe']

    # Stop crossings
    if direction == 1:
        stop_level = start * (1.0 - stop_pct / 100.0)
        stop_crossings = np.where(path <= stop_level)[0]
    else:
        stop_level = start * (1.0 + stop_pct / 100.0)
        stop_crossings = np.where(path >= stop_level)[0]
    first_stop = int(stop_crossings[0]) if len(stop_crossings) else None

    # Ceiling crossings (running_mfe >= ceiling)
    ceiling_crossings = np.where(mfe_curve >= ceiling)[0]
    first_ceiling = int(ceiling_crossings[0]) if len(ceiling_crossings) else None

    # Pick the earlier of the two; ceiling wins ties (Joe: halt-at-ceiling
    # is the scalper exit, takes priority over a same-bar stop)
    if first_ceiling is not None and (first_stop is None or first_ceiling <= first_stop):
        halt_idx    = first_ceiling
        mfe_at_halt = float(mfe_curve[halt_idx])
        bars_walked = halt_idx + 1
        return {
            'stop_bar':    None,
            'ceiling_bar': bars_walked,
            'halt_bar':    bars_walked,
            'bars_walked': bars_walked,
            'running_mfe': round(mfe_at_halt, 4),
            'outcome':     'won_ceiling',
            'banked':      ceiling,
            'lost':        0.0,
            'walked_past': bars_walked > _LONG_WALK_BARS,
        }

    if first_stop is not None:
        halt_idx    = first_stop
        mfe_at_halt = float(mfe_curve[halt_idx])
        bars_walked = halt_idx + 1
        won_at_stop = mfe_at_halt >= profit_zone
        return {
            'stop_bar':    bars_walked,
            'ceiling_bar': None,
            'halt_bar':    bars_walked,
            'bars_walked': bars_walked,
            'running_mfe': round(mfe_at_halt, 4),
            'outcome':     'won_stopped' if won_at_stop else 'stopped',
            'banked':      round(mfe_at_halt, 4) if won_at_stop else 0.0,
            'lost':        stop_pct if not won_at_stop else 0.0,
            'walked_past': bars_walked > _LONG_WALK_BARS,
        }

    # Neither ceiling nor stop fired — incomplete
    bars_walked = len(path)
    mfe_at_halt = float(mfe_curve[-1]) if len(mfe_curve) > 0 else 0.0
    return {
        'stop_bar':    None,
        'ceiling_bar': None,
        'halt_bar':    None,
        'bars_walked': bars_walked,
        'running_mfe': round(mfe_at_halt, 4),
        'outcome':     'incomplete',
        'banked':      0.0,
        'lost':        0.0,
        'walked_past': bars_walked > _LONG_WALK_BARS,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tc_pk', type=int, required=True)
    parser.add_argument('--lookback_days', type=float, default=1.0)
    parser.add_argument('--stop_min',  type=float, default=0.07)
    parser.add_argument('--stop_max',  type=float, default=1.51)
    parser.add_argument('--stop_step', type=float, default=0.04)
    parser.add_argument('--no_detail', action='store_true',
                        help='Skip per-signal-per-stop detail CSV (saves memory on large runs)')
    parser.add_argument('--emit_pine', action='store_true',
                        help='Write a TV Pine v6 strategy file alongside the CSVs, '
                             'with the timestamp+direction arrays baked in for A/B '
                             'comparison against a known-good Pine source.')
    parser.add_argument('--max_signals', type=int, default=150,
                        help='Cap on signals emitted to the Pine file. TV enforces '
                             'a ~1200 local-variable limit at script main scope; '
                             'each pushed signal costs ~6 locals, so ~150 signals '
                             'leaves headroom. Python sim always uses the full set.')
    parser.add_argument('--output', type=str, default=None)
    args = parser.parse_args()

    log = get_logger('inspect')
    db  = _db()

    tc = load_tc(db, args.tc_pk)
    log.info(f'tc_pk={args.tc_pk} ({tc["tc_indicator_label"]})')
    log.info(f'dema params: src={tc["tc_dema_src"]}, len={tc["tc_dema_len"]}  '
             f'profit_zone={_PROFIT_ZONE}%')

    pool   = load_pool_params(db)
    w_close, w_wide = load_weights(db, int(tc['tc_ic_pk']))
    log.info(f'weights=({w_close}, {w_wide})')

    df = load_klines(db, int(tc['tc_tp_pk']), args.lookback_days)
    log.info(f'Loaded {len(df)} 5s bars')

    dema_src = IndicatorComputer.build_source(df, tc['tc_dema_src'])
    dema     = IndicatorComputer.dema(dema_src, int(tc['tc_dema_len']))
    dema_arr = np.asarray(dema, dtype=float)

    vote = build_vote(tc, w_close, w_wide)
    pk5s = Pk5sGateComputer(db)
    oob_arr = pk5s.compute(
        tce_pk=f'inspect-tc{args.tc_pk}',
        base_df=df, dema=dema,
        params=pool, midpoint=_MIDPOINT,
        vote_overrides=[vote],
    )
    s5_pk_final = -oob_arr

    prev = np.concatenate([[0], s5_pk_final[:-1]])
    transitions_idx = np.where((s5_pk_final != prev) & (s5_pk_final != 0))[0]
    timestamps = df['timestamp'].to_numpy()

    n_long  = int((s5_pk_final[transitions_idx] == 1).sum())
    n_short = int((s5_pk_final[transitions_idx] == -1).sum())

    print()
    print(f'Total: {len(transitions_idx)} signals  ({n_long} LONG, {n_short} SHORT)')
    print(f'Dataset: {len(df)} bars  ({len(df)*5/60:.1f} min)')
    print(f'Profit zone (win threshold): {_PROFIT_ZONE}%')

    # ── build stop list ───────────────────────────────────────────────────
    stops = []
    s = args.stop_min
    while s <= args.stop_max + 1e-9:
        stops.append(round(s, 4))
        s += args.stop_step

    print(f'Sweep: {len(stops)} stops from {stops[0]:.2f}% to {stops[-1]:.2f}% '
          f'(step {args.stop_step:.2f}%)')
    print()

    # ── streaming sim: build one trajectory at a time ────────────────────
    # Aggregates keyed by stop_pct. Win is split into won_ceiling (mfe hit
    # 1% before stop) and won_stopped (stop fired with mfe>=profit_zone).
    agg = {sp: {'won_ceiling': 0, 'won_stopped': 0,
                'stopped': 0, 'incomplete': 0,
                'gross_profit': 0.0, 'gross_loss': 0.0}
           for sp in stops}

    detail_rows = [] if not args.no_detail else None
    progress_every = max(1, len(transitions_idx) // 20)

    # Also collect signal-level data for Pine emission (timestamp_ms, direction)
    signal_records = []

    for n, i in enumerate(transitions_idx, 1):
        if n % progress_every == 0 or n == len(transitions_idx):
            log.info(f'  processed {n}/{len(transitions_idx)} signals')

        i = int(i)
        direction = int(s5_pk_final[i])
        ts_ms = int(timestamps[i])
        utc = datetime.fromtimestamp(ts_ms/1000, tz=timezone.utc)\
                       .strftime('%Y-%m-%d %H:%M:%S')
        dir_str = 'LONG' if direction == 1 else 'SHORT'

        signal_records.append({'ts_ms': ts_ms, 'direction': direction,
                               'utc': utc, 'bar_idx': i})

        traj = build_trajectory(i, direction, dema_arr)

        for stop_pct in stops:
            r = simulate_signal_at_stop(traj, stop_pct, _PROFIT_ZONE, _CEILING)
            a = agg[stop_pct]
            outcome = r['outcome']
            if   outcome == 'won_ceiling': a['won_ceiling'] += 1
            elif outcome == 'won_stopped': a['won_stopped'] += 1
            elif outcome == 'stopped':     a['stopped']     += 1
            else:                          a['incomplete']  += 1
            a['gross_profit'] += r['banked']
            a['gross_loss']   += r['lost']

            if detail_rows is not None:
                detail_rows.append({
                    'signal_n':    n,
                    'utc':         utc,
                    'direction':   dir_str,
                    'bar_idx':     i,
                    'entry_dema':  round(traj['start'], 6),
                    'stop_pct':    stop_pct,
                    'halt_bar':    r['halt_bar'],
                    'stop_bar':    r['stop_bar'],
                    'ceiling_bar': r['ceiling_bar'],
                    'bars_walked': r['bars_walked'],
                    'running_mfe': r['running_mfe'],
                    'outcome':     r['outcome'],
                    'banked':      r['banked'],
                    'lost':        r['lost'],
                    'walked_past_520': r['walked_past'],
                })

        del traj

    # ── print per-stop aggregate table ───────────────────────────────────
    print()
    print(f'Per-stop aggregate (ceiling={_CEILING}%, profit_zone={_PROFIT_ZONE}%):')
    print(f'  {"stop%":>6}  {"w_ceil":>6}  {"w_stop":>6}  {"stopped":>7}  '
          f'{"inc":>5}  {"win%":>5}  {"avg_bank":>8}  {"gross_p":>9}  '
          f'{"gross_l":>9}  {"net":>10}')
    print(f'  {"-"*6}  {"-"*6}  {"-"*6}  {"-"*7}  {"-"*5}  {"-"*5}  '
          f'{"-"*8}  {"-"*9}  {"-"*9}  {"-"*10}')

    aggregate_rows = []
    for stop_pct in stops:
        a = agg[stop_pct]
        won = a['won_ceiling'] + a['won_stopped']
        total = won + a['stopped'] + a['incomplete']
        avg_bank = a['gross_profit'] / won if won > 0 else 0.0
        net      = a['gross_profit'] - a['gross_loss']
        win_pct  = won / total * 100 if total > 0 else 0.0

        print(f'  {stop_pct:>6.2f}  {a["won_ceiling"]:>6}  {a["won_stopped"]:>6}  '
              f'{a["stopped"]:>7}  {a["incomplete"]:>5}  {win_pct:>4.1f}%  '
              f'{avg_bank:>8.4f}  {a["gross_profit"]:>+9.2f}  '
              f'{-a["gross_loss"]:>+9.2f}  {net:>+10.2f}')

        aggregate_rows.append({
            'stop_pct':     stop_pct,
            'total':        total,
            'won_ceiling':  a['won_ceiling'],
            'won_stopped':  a['won_stopped'],
            'stopped':      a['stopped'],
            'incomplete':   a['incomplete'],
            'win_pct':      round(win_pct, 2),
            'avg_bank_pct': round(avg_bank, 4),
            'gross_profit': round(a['gross_profit'], 4),
            'gross_loss':   round(a['gross_loss'], 4),
            'net':          round(net, 4),
        })

    # ── write CSVs ───────────────────────────────────────────────────────
    base = args.output or f'baseline_signals_tc{args.tc_pk}'
    prefix = f'{int(args.lookback_days)}days_'
    agg_path = f'{prefix}{base}_aggregate.csv'
    pd.DataFrame(aggregate_rows).to_csv(agg_path, index=False)
    print()
    print(f'Aggregate CSV: {agg_path}')

    if detail_rows is not None:
        det_path = f'{prefix}{base}_detail.csv'
        pd.DataFrame(detail_rows).to_csv(det_path, index=False)
        print(f'Detail CSV:    {det_path}  '
              f'({len(detail_rows)} rows = {len(transitions_idx)} signals × {len(stops)} stops)')
    else:
        print('Detail CSV:    skipped (--no_detail)')

    # ── emit Pine strategy file ──────────────────────────────────────────
    if args.emit_pine:
        pine_path = f'{prefix}bbstr_engine_tc{args.tc_pk}.pine'
        n_total = len(signal_records)
        if n_total > args.max_signals:
            # Take the most-recent N — keeps signals near the right edge of
            # the TV chart, less scrolling to validate them.
            pine_signals = signal_records[-args.max_signals:]
            log.info(f'Pine emit: truncating {n_total} signals → {len(pine_signals)} '
                     f'most-recent (--max_signals={args.max_signals}; TV local-var limit)')
        else:
            pine_signals = signal_records
        emit_pine_file(pine_path, pine_signals, args.tc_pk,
                       tc['tc_indicator_label'],
                       total_python_signals=n_total)
        truncated_note = ('' if len(pine_signals) == n_total
                          else f', most-recent {len(pine_signals)} of {n_total}')
        print(f'Pine file:     {pine_path}  '
              f'({len(pine_signals)} signals{truncated_note})')


# ──────────────────────────────────────────────────────────────────────────
# Pine emitter
# ──────────────────────────────────────────────────────────────────────────

_PINE_HEADER = '''//@version=6
strategy('BBSTR_AB',
     overlay                 = false,
     precision               = 1,
     initial_capital         = 500,
     currency                = currency.USDT,
     default_qty_type        = strategy.fixed,
     default_qty_value       = 33300,
     pyramiding              = 10,
     commission_type         = strategy.commission.percent,
     commission_value        = 0.205,
     slippage                = 3,
     calc_on_order_fills     = true,
     process_orders_on_close = true,
     margin_long             = 1.82,
     margin_short            = 1.82,
     max_labels_count        = 500,
     max_lines_count         = 500)
'''


def emit_pine_file(path: str, signal_records: list,
                   tc_pk: int, tc_label: str,
                   total_python_signals: int = None) -> None:
    """
    Write a Pine v6 strategy file that replays the Python-generated
    signal timestamps as entries, with configurable SL/TP UI for A/B
    testing against a known-good Pine source.

    Signals are stored in two parallel arrays (timestamp_ms, direction).
    Population is chunked into batch helper functions to dodge Pine's
    per-`if`-block length cap (CE10205). A sequential cursor matches
    signals to bars as the chart progresses, tolerating TV data gaps.

    total_python_signals — when set and larger than len(signal_records),
    annotates the file header to make truncation visible.
    """
    lines = []
    lines.append(_PINE_HEADER)
    lines.append('')
    lines.append(f'// Generated from optimus9 inspector')
    lines.append(f'// tc_pk={tc_pk} ({tc_label})')
    if total_python_signals is not None and total_python_signals > len(signal_records):
        lines.append(f'// {len(signal_records)} signals  '
                     f'(truncated from {total_python_signals} python signals — '
                     f'TV local-var limit)')
    else:
        lines.append(f'// {len(signal_records)} signals')
    lines.append(f'// Generated at {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")}')
    lines.append('')

    # ── UI inputs ────────────────────────────────────────────────────────
    lines.append('// ─── UI inputs ──────────────────────────────────────────')
    lines.append('sl_pct      = input.float(0.7, "Stop loss %",   minval=0.1, step=0.04)')
    lines.append('tp_pct      = input.float(1.1, "Take profit %", minval=0.1, step=0.04)')
    lines.append('exit_method = input.string("current tp value", "Exit method",')
    lines.append('                           options=["current tp value", "no tp"])')
    lines.append('')
    lines.append('_sl_mult = sl_pct / 100.0')
    lines.append('_tp_mult = tp_pct / 100.0')
    lines.append('')

    # ── Signal arrays ────────────────────────────────────────────────────
    lines.append('// ─── Signal arrays — populated once on first bar ────────')
    lines.append('var int[] SIG_TS  = array.new<int>(0)')
    lines.append('var int[] SIG_DIR = array.new<int>(0)  // +1=LONG, -1=SHORT')
    lines.append('')

    # Batch the array.push calls into helper functions. Pine v6 caps the
    # body length of any single `if` block (CE10205) at around ~500 lines.
    # We chunk the pushes into _load_batch_N() functions of BATCH_SIZE
    # signals each (200 push statements per function), then call each
    # batch from a tiny `if barstate.isfirst` block. Functions can mutate
    # script-level var arrays via push since arrays are reference types.
    BATCH_SIZE = 100
    n_batches = (len(signal_records) + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_idx in range(n_batches):
        s = batch_idx * BATCH_SIZE
        e = min(s + BATCH_SIZE, len(signal_records))
        lines.append(f'// Batch {batch_idx + 1}/{n_batches} — signals {s+1}-{e}')
        lines.append(f'_load_batch_{batch_idx}() =>')
        for rec in signal_records[s:e]:
            lines.append(f'    array.push(SIG_TS, {rec["ts_ms"]})')
            lines.append(f'    array.push(SIG_DIR, {rec["direction"]})')
        # Explicit return so the function is a valid expression
        lines.append('    true')
        lines.append('')

    lines.append('if barstate.isfirst')
    for batch_idx in range(n_batches):
        lines.append(f'    _load_batch_{batch_idx}()')
    lines.append('')

    # ── Cursor-based matcher ─────────────────────────────────────────────
    lines.append('// ─── Sequential cursor matcher ──────────────────────────')
    lines.append('// Signals are time-ordered. Advance cursor past any timestamp')
    lines.append('// the current bar has already passed (handles TV data gaps).')
    lines.append('var int next_sig_idx = 0')
    lines.append('bool _sig_long  = false')
    lines.append('bool _sig_short = false')
    lines.append('')
    lines.append('while next_sig_idx < array.size(SIG_TS) and array.get(SIG_TS, next_sig_idx) < time')
    lines.append('    next_sig_idx := next_sig_idx + 1')
    lines.append('')
    lines.append('if next_sig_idx < array.size(SIG_TS) and array.get(SIG_TS, next_sig_idx) == time')
    lines.append('    int _dir = array.get(SIG_DIR, next_sig_idx)')
    lines.append('    if _dir == 1')
    lines.append('        _sig_long := true')
    lines.append('    else')
    lines.append('        _sig_short := true')
    lines.append('    next_sig_idx := next_sig_idx + 1')
    lines.append('')
    lines.append('bool _can_long  = _sig_long')
    lines.append('bool _can_short = _sig_short')
    lines.append('')

    # ── Exit + Entry block ───────────────────────────────────────────────
    lines.append('// ─── Exit + Entry block ─────────────────────────────────')
    lines.append('bool   use_fixed_tp = exit_method == "current tp value"')
    lines.append('float  tp_long      = use_fixed_tp and strategy.position_size > 0 ? strategy.position_avg_price * (1 + _tp_mult) : na')
    lines.append('float  tp_short     = use_fixed_tp and strategy.position_size < 0 ? strategy.position_avg_price * (1 - _tp_mult) : na')
    lines.append('')
    lines.append('// SL always active. TP is conditional')
    lines.append('if strategy.position_size > 0')
    lines.append("    strategy.exit('XL', from_entry='L',")
    lines.append('         stop  = strategy.position_avg_price * (1 - _sl_mult),')
    lines.append('         limit = tp_long)')
    lines.append('if strategy.position_size < 0')
    lines.append("    strategy.exit('XS', from_entry='S',")
    lines.append('         stop  = strategy.position_avg_price * (1 + _sl_mult),')
    lines.append('         limit = tp_short)')
    lines.append('')
    lines.append('// Entries')
    lines.append('if _sig_long and _can_long')
    lines.append("    strategy.entry('L', strategy.long)")
    lines.append('if _sig_short and _can_short')
    lines.append("    strategy.entry('S', strategy.short)")
    lines.append('')

    with open(path, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == '__main__':
    main()
