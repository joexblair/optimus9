"""
PineStrategyEmitter — generates a Pine v6 strategy file from a PROVEN combo.

Reads analysis_or<N>.csv to find the highest-gross-banked DD-qualified combo,
queries pk_signals + pk_outcomes for last 400 PROVEN signals, and writes the
strategy as bbstr_or<N>_strategy.pine.

Pine output:
  - Mirrors production f_pk_state + f_bb + f_vote + decision delay logic
  - Single-line voter (close + wide pool only, no other TFs)
  - PROVEN params as defaults; all inputs exposed for dial-in testing
  - Bracket exits: TP = 0.95 × min_won_pct, SL from grind (0.4%)
  - process_orders_on_close=true to match Python's per-bar semantics
  - margin_long=0 / margin_short=0 (v6 default of 100% disabled for AB test)
  - pyramiding=10 + unique entry IDs per fire (each signal gets own bracket)
  - Last 400 PROVEN signals' outcomes baked as label arrays
"""

import csv
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional

from logger import get_logger

# ── cross-package imports ─────────────────────────────────────────────────
from ..db.database_manager import DatabaseManager


class PineStrategyEmitter:
    """Emit a Pine v6 strategy artifact for the PROVEN combo of an or_pk."""

    _DD_KILL_SWITCH = 0.15        # max_drawdown ≤ 15% to be PROVEN
    _LABEL_LAST_N_SIGNALS = 400   # last N PROVEN signals shown as labels
    _TP_FRACTION_OF_MIN_WON = 0.95  # Joe's call — 99% was practically same value

    def __init__(self, db: DatabaseManager) -> None:
        self._db  = db
        self._log = get_logger(self.__class__.__name__)

    def emit(self, or_pk: int, output_dir: str = '.') -> Optional[str]:
        """Emit Pine strategy for the PROVEN combo of or_pk. Returns output path."""
        csv_path = Path(output_dir) / f'analysis_or{or_pk}.csv'
        if not csv_path.exists():
            self._log.error(f'analysis_or{or_pk}.csv not found in {output_dir}')
            self._log.error(f'Run AnalyzeManager first: python3 -m optimus9.analysis.analyze_manager --or_pk={or_pk}')
            return None

        proven = self._find_proven(csv_path)
        if proven is None:
            self._log.warning(f'No DD-qualified combos in analysis_or{or_pk}.csv (all max_drawdown > {self._DD_KILL_SWITCH:.0%})')
            self._log.warning('Cannot emit a PROVEN-anchored Pine strategy. Re-run grind with tighter stop or relaxed DD policy.')
            return None

        self._log.info(f'PROVEN combo selected:')
        self._log.info(f'  len={proven["len"]} mult={proven["mult"]} src={proven["src"]}')
        self._log.info(f'  pool_c={proven["pool_c"]} pool_w={proven["pool_w"]} pool_range={proven["pool_range"]}')
        self._log.info(f'  slope_floor={proven["slope_floor"]} multiplier={proven["multiplier"]}')
        self._log.info(f'  signals={proven["total"]}  win={proven["win_pct"]:.1f}%  gross=${proven["gross_banked"]:.0f}  dd={proven["max_dd_pct"]:.1f}%')

        signals = self._query_last_window_signals(or_pk, proven)
        n_open = sum(1 for s in signals if s['bars_to_stop'] is None)
        self._log.info(
            f'Loaded {len(signals)} signals (last {self._LABEL_LAST_N_SIGNALS}); '
            f'{n_open} are open (will render as labels)'
        )

        stop_pct = self._tc_stop_pct(or_pk)
        tp_pct   = round(self._TP_FRACTION_OF_MIN_WON * proven['min_won'], 4)

        pine_src = self._render_pine(or_pk, proven, signals, stop_pct, tp_pct)

        output_path = Path(output_dir) / f'bbstr_or{or_pk}_strategy.pine'
        output_path.write_text(pine_src, encoding='utf-8')
        self._log.info(f'Pine strategy → {output_path}')
        return str(output_path)

    # ── PROVEN combo selection ───────────────────────────────────────────────

    def _find_proven(self, csv_path: Path) -> Optional[dict]:
        """Return the highest-gross-banked combo with max_drawdown ≤ kill switch."""
        with csv_path.open(encoding='utf-8-sig') as f:
            rows = list(csv.DictReader(f))

        qualifying = [
            r for r in rows
            if float(r['max_drawdown']) <= self._DD_KILL_SWITCH
        ]
        if not qualifying:
            return None

        qualifying.sort(key=lambda r: -float(r['gross_banked']))
        winner = qualifying[0]

        return {
            'len':           int(winner['len']),
            'mult':          float(winner['mult']),
            'src':           winner['src'].strip(),
            'pool_c':        int(winner['pool_c']),
            'pool_w':        int(winner['pool_w']),
            'pool_range':    int(winner['pool_range']),
            'slope_floor':   float(winner['slope_floor']),
            'multiplier':    int(winner['multiplier']),
            'total':         int(winner['total']),
            'win_pct':       float(winner['win_rate_walked']) * 100,
            'gross_banked':  float(winner['gross_banked']),
            'max_dd_pct':    float(winner['max_drawdown']) * 100,
            'min_won':       float(winner['min_won_pct']),
            'stage1_rank':   int(winner['stage1_rank']),
        }

    # ── Signal label data ────────────────────────────────────────────────────

    def _query_last_window_signals(self, or_pk: int, proven: dict) -> list:
        """Fetch last N PROVEN signals (by timestamp desc, then re-sort asc) with MAE."""
        rows = self._db.execute(
            '''SELECT s.pks_timestamp                AS ts_ms,
                      s.pks_dir                     AS direction,
                      o.pko_max_profit_pct          AS max_profit_pct,
                      o.pko_max_adverse_pct         AS max_adverse_pct,
                      o.pko_bars_to_stop            AS bars_to_stop
               FROM pk_signals  s
               JOIN pk_outcomes o ON o.pko_pks_pk = s.pks_pk
               WHERE s.pks_or_pk    = %s
                 AND s.pks_len      = %s
                 AND s.pks_mult     = %s
                 AND s.pks_src      = %s
                 AND s.pks_pool_c   = %s
                 AND s.pks_pool_w   = %s
                 AND s.pks_pool_range = %s
                 AND s.pks_slope_floor = %s
                 AND s.pks_multiplier  = %s
               ORDER BY s.pks_timestamp DESC
               LIMIT %s''',
            (or_pk, proven['len'], proven['mult'], proven['src'],
             proven['pool_c'], proven['pool_w'], proven['pool_range'],
             proven['slope_floor'], proven['multiplier'],
             self._LABEL_LAST_N_SIGNALS),
            fetch=True,
        )
        # DB returned newest-first (for LIMIT); re-sort ascending so Pine
        # arrays scan chronologically and label coloring matches order.
        return sorted(rows or [], key=lambda r: r['ts_ms'])

    def _tc_stop_pct(self, or_pk: int) -> float:
        """Pull tc_stop_pct from test_configs via optimizer_runs."""
        rows = self._db.execute(
            '''SELECT tc.tc_stop_pct
               FROM optimizer_runs o
               JOIN test_configs tc ON tc.tc_pk = o.or_tc_pk
               WHERE o.or_pk = %s''',
            (or_pk,), fetch=True,
        )
        return float(rows[0]['tc_stop_pct']) if rows else 0.4

    # ── Pine v6 source rendering ─────────────────────────────────────────────

    def _render_pine(self, or_pk: int, proven: dict, signals: list,
                     stop_pct: float, tp_pct: float) -> str:
        # Profit zone threshold used by AM v2 to classify won-vs-stopped
        PROFIT_ZONE = 0.6

        # Label all signals — won, stopped, or open. Direction-prefixed text.
        ts_csv     = ', '.join(str(int(s['ts_ms']))            for s in signals)
        dir_csv    = ', '.join(str(int(s['direction']))        for s in signals)
        status_csv = ', '.join(
            '"' + self._classify(s, PROFIT_ZONE) + '"' for s in signals
        )
        winpct_csv = ', '.join(
            f"{float(s['max_profit_pct'] or 0):.4f}" for s in signals
        )
        ddpct_csv  = ', '.join(
            f"{float(s['max_adverse_pct'] or 0):.4f}" for s in signals
        )
        n_labels = len(signals)

        # Defaults from PROVEN
        d_len    = proven['len']
        d_mult   = proven['mult']
        d_src    = proven['src']
        d_pc     = proven['pool_c']
        d_pw     = proven['pool_w']
        d_pr     = proven['pool_range']
        d_sf     = proven['slope_floor']
        d_mul    = proven['multiplier']

        # Source enum mapping for Pine input.source()
        src_pine = self._src_to_pine_default(d_src)

        # ── Pine source ──
        return f"""//@version=6
// ═══════════════════════════════════════════════════════════════════════════
// Optimus9 — gca5m PROVEN strategy
// or_pk={or_pk}  |  stage1_rank={proven['stage1_rank']}  |  generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
//
// PROVEN combo:  len={d_len}  mult={d_mult}  src={d_src}
//                pool_c={d_pc}  pool_w={d_pw}  pool_range={d_pr}  slope_floor={d_sf}
//                signals={proven['total']}  win={proven['win_pct']:.1f}%
//                gross_banked=${proven['gross_banked']:.0f}  max_dd={proven['max_dd_pct']:.1f}%
//                min_won_pct={proven['min_won']:.4f}%
//
// CALIBRATION:  SL={stop_pct}%   TP={tp_pct}% (95% of min_won_pct)
//
// NOTES:
//   - Pine v6 hedge mode is approximate. Pyramiding=10 stacks same-direction
//     entries; opposing entries net-close the existing position per Pine's
//     standard model. Real hybrid pilot deployment routes through Python
//     which handles hedging natively on Bybit.
//   - Labels showing Python truth (won/stopped/open) span last 400 PROVEN signals.
// ═══════════════════════════════════════════════════════════════════════════

strategy("Optimus9 gca5m PROVEN (or_pk={or_pk})",
         overlay              = true,
         pyramiding           = 10,
         margin_long          = 0,
         margin_short         = 0,
         process_orders_on_close = true,
         initial_capital      = 1000,
         default_qty_type     = strategy.percent_of_equity,
         default_qty_value    = 10,
         commission_type      = strategy.commission.percent,
         commission_value     = 0.06)

// ═══════════════════════════════════════════════════════════════════════════
// CONSTANTS
// ═══════════════════════════════════════════════════════════════════════════

PK_PM_LONG  = 2.0
PK_PM_SHORT = -2.0

// ═══════════════════════════════════════════════════════════════════════════
// BOUNDARY SETTINGS — two distinct concepts
//
// "OOB" boundary (ic_high_boundary / ic_low_boundary, 85/15):
//    The fence. Line crosses these → out of boundary (OOB) → eligible for
//    gating logic. NOT currently consumed by Pine strategy (gate was applied
//    upstream at Python grind time). Exposed for future OOB gate emulation.
//
// "RSI domain" rescale (rsi_ob / rsi_os, 70/30):
//    Used by f_bb to rescale BB% into the 0-100 RSI numeric space so BB and
//    K lines share a common range and slope_floor / threshold values are
//    comparable. Also forms f_pk_state midpoint via (ob+os)/2 = 50.
// ═══════════════════════════════════════════════════════════════════════════

ic_high_boundary = input.float(85.0, 'OOB High Boundary', group='Boundaries', step=1,
     tooltip='Fence: line above 85 = OOB high. Reserved for future gate emulation.')
ic_low_boundary  = input.float(15.0, 'OOB Low Boundary',  group='Boundaries', step=1,
     tooltip='Fence: line below 15 = OOB low.')
rsi_ob           = input.float(70.0, 'RSI OB (BB rescale)', group='Boundaries', step=1,
     tooltip='RSI overbought (70). Used by f_bb to rescale BB% into RSI domain. Also used in f_pk_state midpoint = (ob+os)/2 = 50.')
rsi_os           = input.float(30.0, 'RSI OS (BB rescale)', group='Boundaries', step=1,
     tooltip='RSI oversold (30). Pairs with rsi_ob.')

// Aliases for f_bb / f_pk_state internals
ob = rsi_ob
os = rsi_os

// ═══════════════════════════════════════════════════════════════════════════
// LINE SETTINGS  (matches CSV column order: len, mult, src)
// ═══════════════════════════════════════════════════════════════════════════

gca5m_len  = input.int({d_len},   'BB Length',     group='gca5m line', minval=2)
gca5m_mult = input.float({d_mult},'BB Multiplier', group='gca5m line', step=0.01)
gca5m_src  = input.source({src_pine}, 'BB Source', group='gca5m line')

// ═══════════════════════════════════════════════════════════════════════════
// POOL SETTINGS  (matches CSV: pool_c, pool_w, pool_range, slope_floor, multiplier)
// ═══════════════════════════════════════════════════════════════════════════

pool_c      = input.int({d_pc},  'Pool Close (bars back)', group='Pool', step=1)
pool_w      = input.int({d_pw},  'Pool Wide  (bars back)', group='Pool', step=1)
pool_range  = input.int({d_pr},  'Pool Range',             group='Pool', step=2)
slope_floor = input.float({d_sf},'Slope Floor',            group='Pool', step=5.0)
multiplier  = input.int({d_mul}, 'TF Multiplier',          group='Pool', minval=1)

// ═══════════════════════════════════════════════════════════════════════════
// VOTE WEIGHTS
// ═══════════════════════════════════════════════════════════════════════════

tcev_weight_close   = input.int(5, 'Vote Weight (Close)',   group='Vote Machine')
tcev_weight_wide    = input.int(2, 'Vote Weight (Wide)',    group='Vote Machine')
tcev_weight_control = input.int(0, 'Vote Weight (Control)', group='Vote Machine',
     tooltip='Dead-zone voter. Always votes neutral; inflates the denominator under pm_option_b. Higher values require stronger directional consensus to fire. Default 0 = off (matches production grind).')

// ═══════════════════════════════════════════════════════════════════════════
// PM SUPPRESSION
// ═══════════════════════════════════════════════════════════════════════════

pm_suppress_str = input.float(0.5, 'PM Suppression Strength', group='PM Suppression',
     step=0.05, minval=0.0, maxval=1.0,
     tooltip='Scalar applied to opposing-bucket PM weight. 0=no suppression, 1=full.')
pm_option_a     = input.bool(false, 'PM Option A (exclude neutral from active_w)',
     group='PM Suppression',
     tooltip='Off (pm_option_b) = include neutral in denominator. Required for control voter to have effect. On = exclude neutral (production grind default; control voter has no effect).')

pm_additive_close_str = input.float(0.0, 'PM Additive Close (per-pool)', group='PM Additive',
     step=0.05, minval=0.0, maxval=1.0,
     tooltip='When close pool produces a PM sentinel (line+price both same direction = trend continuation), add (close_weight * this) to the matching directional bucket. 0 = current behavior (PM contributes nothing directional). 1 = PM contributes equally to its matching direction. Currently NOT in the Python grind — set above 0 for experimentation only until next grind.')
pm_additive_wide_str  = input.float(0.0, 'PM Additive Wide (per-pool)',  group='PM Additive',
     step=0.05, minval=0.0, maxval=1.0,
     tooltip='Same as PM Additive Close but for the wide pool.')

// ═══════════════════════════════════════════════════════════════════════════
// DECISION LOGIC
// ═══════════════════════════════════════════════════════════════════════════

t_long_thresh    = input.float(7.5, 'Long Threshold',    group='Decision', step=0.5,
     tooltip='long_ratio must exceed this to fire. Production default = 7.5 (75% dominance).')
t_short_thresh   = input.float(7.5, 'Short Threshold',   group='Decision', step=0.5)
t_decision_delay = input.int(1,     'Decision Delay (bars)', group='Decision', minval=0,
     tooltip='Wait N bars after PK fires; opposing PK during window cancels both')
use_passthrough  = input.bool(false, 'Passthrough mode (skip decision delay state machine)',
     group='Decision',
     tooltip='When ON: s5_pk_final = pk_raw directly. fire_long/short require pk_raw[1] == 0 (rapid-flip suppression). When OFF: production state machine with countdown + opposing-PK cancellation.')

// ═══════════════════════════════════════════════════════════════════════════
// GATING — bny30M (BB) + bny30p (K), both 30S TF
//
// Python's PKDetector fires per-pool signals only when oob_side != 0 AND
// the signal direction is OPPOSITE the gate's OOB side (mean-reversion).
// In Pine we apply the gate as a HARD STOP after the vote machine: pk_raw
// must align with -oob_side. Keeps gate semantics distinct from voting.
// ═══════════════════════════════════════════════════════════════════════════

use_gate = input.bool(true, 'Gate fires by bny30 OOB', group='Gating',
     tooltip='When ON: fire_long requires oob_side==-1 (gate OOB low); fire_short requires oob_side==1 (gate OOB high). Mean-reversion logic. When OFF: signals fire regardless of bny30 state.')

// bny30M — BB line, hl2, len=58, mult=1.24, boundary 85/15
bny30M_len  = input.int(58,    'bny30M BB Length',     group='Gating: bny30M', minval=2)
bny30M_mult = input.float(1.24,'bny30M BB Multiplier', group='Gating: bny30M', step=0.01)
bny30M_src  = input.source(hl2, 'bny30M BB Source',    group='Gating: bny30M')

// bny30p — K line, ohlc4, k_len=21, rsi_len=114, stc_len=105
bny30p_k_len   = input.int(21,    'bny30p K Length',    group='Gating: bny30p', minval=2)
bny30p_rsi_len = input.int(114,   'bny30p RSI Length',  group='Gating: bny30p', minval=2)
bny30p_stc_len = input.int(105,   'bny30p Stoch Length', group='Gating: bny30p', minval=2)
bny30p_src     = input.source(ohlc4, 'bny30p K Source', group='Gating: bny30p')

// Gate boundaries hardcoded to 85/15 — these are global system constants
// (r08 TODO: move to a system_settings table, expose via global UI).
// Per indicator_configs row, both bny30M and bny30p use 85/15.
GATE_OOB_HI = 85.0
GATE_OOB_LO = 15.0

show_dbg_gate = input.bool(false, 'Debug: gate open (orange)', group='Debug')

// ═══════════════════════════════════════════════════════════════════════════
// CALIBRATION  (stop/profit)
// ═══════════════════════════════════════════════════════════════════════════

sl_pct = input.float({stop_pct},  'Stop %',       group='Calibration', step=0.05)
tp_pct = input.float({tp_pct}, 'Take Profit %',group='Calibration', step=0.05,
     tooltip='95% of min_won_pct from PROVEN combo')

// ═══════════════════════════════════════════════════════════════════════════
// DEMA  (5s native)
// ═══════════════════════════════════════════════════════════════════════════

dema_len    = input.int(2,     'DEMA Length', group='DEMA', minval=2)
dema_src_in = input.source(close, 'DEMA Source', group='DEMA')

// Pine v6 has no built-in ta.dema — compute manually
// DEMA = 2 × EMA(src, len) − EMA(EMA(src, len), len)
f_dema(src, len) =>
    e1 = ta.ema(src, len)
    e2 = ta.ema(e1, len)
    2.0 * e1 - e2

dema_price = f_dema(dema_src_in, dema_len)

// ═══════════════════════════════════════════════════════════════════════════
// DISPLAY
// ═══════════════════════════════════════════════════════════════════════════

show_labels     = input.bool(true, 'Show Python truth labels', group='Display',
     tooltip='Last 400 PROVEN signals as won/stopped/open labels')
show_arrows     = input.bool(true, 'Show signal arrows',       group='Display')

// ═══════════════════════════════════════════════════════════════════════════
// HELPERS — mirror production Pine
// ═══════════════════════════════════════════════════════════════════════════

f_bb(src, len, mult) =>
    basis = ta.sma(src, len)
    dev   = mult * ta.stdev(src, len)
    upper = basis + dev
    lower = basis - dev
    pct   = (src - lower) / (upper - lower)
    (ob - os) * pct + os

f_k(src, rsi_len, stc_len, k_len) =>
    r   = ta.rsi(src, rsi_len)
    raw = ta.stoch(r, r, r, stc_len)
    ta.sma(raw, k_len)

// Two-gate fold matching Python IndicatorComputer.fold_gates:
//   both zero  -> 0     |  one non-zero + one zero  -> non-zero
//   both same  -> same  |  both opposing             -> 0
f_fold_two(a, b) =>
    if a == 0 and b == 0
        0
    else if a == 0
        b
    else if b == 0
        a
    else if a == b
        a
    else
        0

f_pk_state(line_val, price_val, bars, range_size, mult_p, slope_fl) =>
    _half      = range_size / 2
    _lower_5s  = (bars - _half) * mult_p
    _upper_5s  = (bars + _half) * mult_p
    _window_5s = _upper_5s - _lower_5s
    _center_5s = bars * mult_p
    _midpoint  = (ob + os) / 2.0
    _hi_peak   = ta.highest(line_val[_lower_5s], _window_5s)
    _lo_peak   = ta.lowest( line_val[_lower_5s], _window_5s)
    _peak_val  = line_val > _midpoint ? _hi_peak : _lo_peak
    _line_slope  = line_val  - _peak_val
    _price_slope = price_val - price_val[_center_5s]
    if na(_line_slope) or na(_price_slope)
        float(na)
    else
        _slope_diff = math.abs(_line_slope - _price_slope)
        if _slope_diff <= slope_fl
            0.0
        else if math.sign(_line_slope) != math.sign(_price_slope)
            _line_slope > 0 ? 1.0 : -1.0
        else
            _line_slope > 0 ? PK_PM_LONG : PK_PM_SHORT

f_vote(state, weight) =>
    if na(state)
        [0.0, 0.0, 0.0]
    else if state == PK_PM_LONG or state == PK_PM_SHORT
        [0.0, 0.0, float(weight)]
    else if state > 0
        [float(weight), 0.0, 0.0]
    else if state < 0
        [0.0, float(weight), 0.0]
    else
        [0.0, 0.0, float(weight)]

// ═══════════════════════════════════════════════════════════════════════════
// LINE + PK STATES
// ═══════════════════════════════════════════════════════════════════════════

gca5m_line = f_bb(gca5m_src, gca5m_len, gca5m_mult)

state_gca5m_c = f_pk_state(gca5m_line, dema_price, pool_c, pool_range, multiplier, slope_floor)
state_gca5m_w = f_pk_state(gca5m_line, dema_price, pool_w, pool_range, multiplier, slope_floor)

// ═══════════════════════════════════════════════════════════════════════════
// GATE LINES — bny30M (BB) + bny30p (K), 30S TF, lookahead_on
//
// Match Python IndicatorComputer: f_bb uses rsi_ob=70/rsi_os=30 internally
// for the BB rescale (the 'ob'/'os' aliases above). The 85/15 boundaries
// here are the gate's own OOB fence applied to the rescaled line values.
// ═══════════════════════════════════════════════════════════════════════════

// Single request.security call computing BOTH bny30 lines — halves the cross-TF
// request overhead vs two separate calls. Pine v6 supports tuple returns.
f_bny30_both() =>
    bb = f_bb(bny30M_src, bny30M_len, bny30M_mult)
    k  = f_k(bny30p_src, bny30p_rsi_len, bny30p_stc_len, bny30p_k_len)
    [bb, k]

[bny30M_line, bny30p_line] = request.security(syminfo.tickerid, "30S", f_bny30_both(), barmerge.gaps_off, barmerge.lookahead_on)

bny30M_side = na(bny30M_line) ? 0 : (bny30M_line > GATE_OOB_HI ?  1 : bny30M_line < GATE_OOB_LO ? -1 : 0)
bny30p_side = na(bny30p_line) ? 0 : (bny30p_line > GATE_OOB_HI ?  1 : bny30p_line < GATE_OOB_LO ? -1 : 0)

oob_side = f_fold_two(bny30M_side, bny30p_side)

// Single orange bgcolor when gate is open (either direction)
bgcolor(show_dbg_gate and oob_side != 0 ? color.new(color.orange, 80) : na, title='dbg_gate_open')

// ═══════════════════════════════════════════════════════════════════════════
// VOTE MACHINE
// ═══════════════════════════════════════════════════════════════════════════

[l_c, s_c, n_c] = f_vote(state_gca5m_c, tcev_weight_close)
[l_w, s_w, n_w] = f_vote(state_gca5m_w, tcev_weight_wide)

// PM additive contributions (per-pool tunable). PM sentinels are "trend
// continuation" states (line and price move in same direction with significant
// slope). They route to neutral by default; adding them to their matching
// directional bucket weights the continuation signal accordingly.
pm_add_long_c  = (state_gca5m_c == PK_PM_LONG)  ? tcev_weight_close * pm_additive_close_str : 0.0
pm_add_short_c = (state_gca5m_c == PK_PM_SHORT) ? tcev_weight_close * pm_additive_close_str : 0.0
pm_add_long_w  = (state_gca5m_w == PK_PM_LONG)  ? tcev_weight_wide  * pm_additive_wide_str  : 0.0
pm_add_short_w = (state_gca5m_w == PK_PM_SHORT) ? tcev_weight_wide  * pm_additive_wide_str  : 0.0

long_pts    = l_c + l_w + pm_add_long_c  + pm_add_long_w
short_pts   = s_c + s_w + pm_add_short_c + pm_add_short_w
// Control voter always contributes to neutral. Inflates denominator under
// pm_option_b to suppress single-pool dominance (the "dead zone" mechanic).
neutral_pts = n_c + n_w + tcev_weight_control

// PM suppression — sentinel-based per-line weight aggregation
pm_long_wt  = (state_gca5m_c == PK_PM_LONG  ? tcev_weight_close : 0) +
              (state_gca5m_w == PK_PM_LONG  ? tcev_weight_wide  : 0)
pm_short_wt = (state_gca5m_c == PK_PM_SHORT ? tcev_weight_close : 0) +
              (state_gca5m_w == PK_PM_SHORT ? tcev_weight_wide  : 0)

adj_long_pts  = math.max(0.0, long_pts  - pm_short_wt * pm_suppress_str)
adj_short_pts = math.max(0.0, short_pts - pm_long_wt  * pm_suppress_str)
adj_neutral   = neutral_pts

active_w    = pm_option_a ? adj_long_pts + adj_short_pts : adj_long_pts + adj_short_pts + adj_neutral
long_ratio  = active_w > 0 ? (adj_long_pts  / active_w) * 10.0 : 0.0
short_ratio = active_w > 0 ? (adj_short_pts / active_w) * 10.0 : 0.0

// Dead zone under pm_option_b is two layers:
//   1. Threshold gap — ratios between 3.0 and 7.5 don't fire either direction
//   2. Control voter — inflates denominator, suppressing single-pool dominance
// Default control_weight=0 reproduces grind exactly. Dial up to enforce
// stronger consensus requirements.
pk_raw = long_ratio > t_long_thresh ? 1 : short_ratio > t_short_thresh ? -1 : 0

// ═══════════════════════════════════════════════════════════════════════════
// DECISION DELAY — same logic as production Pine
// ═══════════════════════════════════════════════════════════════════════════

var int pk_countdown   = 0
var int pk_pending_dir = 0
var int s5_pk_final    = 0

if pk_raw != 0
    if pk_raw == pk_pending_dir
        pk_countdown := math.max(0, pk_countdown - 1)
        if pk_countdown == 0
            s5_pk_final := pk_raw
    else
        // New direction (or first signal after neutral period).
        // If delay=0, fire immediately on same bar as pk_raw (no inherent lag).
        // If delay>0, zero s5_pk_final and start countdown for confirmation.
        pk_pending_dir := pk_raw
        if t_decision_delay == 0
            pk_countdown := 0
            s5_pk_final  := pk_raw
        else
            pk_countdown := t_decision_delay
            s5_pk_final  := 0
else
    pk_pending_dir := 0
    pk_countdown   := 0
    s5_pk_final    := 0

// ═══════════════════════════════════════════════════════════════════════════
// DEBUG VISUALIZATION — bgcolor layers showing where signals get filtered
//
// LAYER 1 (faintest):  Line-level divergence — any non-PM state on close OR wide pool
// LAYER 2 (medium):    pk_raw — vote machine cleared the threshold
// LAYER 3 (strongest): s5_pk_final_effective — what actually drives fires.
//                      Reflects use_passthrough toggle: ON → equals pk_raw; OFF → state machine output.
//
// If LAYER 1 fires but LAYER 2 doesn't  → vote machine threshold too tight
// If LAYER 2 fires but LAYER 3 doesn't  → decision delay cancelled by opposing PK (only relevant when passthrough OFF)
// If LAYER 3 fires but no entry arrow   → fire_long/fire_short edge detection issue (check pk_raw[1] under passthrough)
// ═══════════════════════════════════════════════════════════════════════════

show_dbg_line_state = input.bool(false, 'Debug: line divergence (faint)', group='Debug')
show_dbg_pk_raw     = input.bool(false, 'Debug: pk_raw (medium)',         group='Debug')
show_dbg_s5_final   = input.bool(false, 'Debug: s5_pk_final (strongest)', group='Debug')

// Layer 1: any line state is divergence (state ±1, not PM ±2)
dbg_line_long  = (not na(state_gca5m_c) and state_gca5m_c ==  1.0) or (not na(state_gca5m_w) and state_gca5m_w ==  1.0)
dbg_line_short = (not na(state_gca5m_c) and state_gca5m_c == -1.0) or (not na(state_gca5m_w) and state_gca5m_w == -1.0)

// Effective s5_pk_final value — respects passthrough toggle so the debug
// layer tells the truth about what's driving fire_long/fire_short.
s5_pk_final_effective = use_passthrough ? pk_raw : s5_pk_final

bgcolor(show_dbg_line_state and dbg_line_long  ? color.new(color.green, 92) : na, title='dbg_line_long')
bgcolor(show_dbg_line_state and dbg_line_short ? color.new(color.red,   92) : na, title='dbg_line_short')
bgcolor(show_dbg_pk_raw     and pk_raw ==  1   ? color.new(color.lime,  78) : na, title='dbg_pk_raw_long')
bgcolor(show_dbg_pk_raw     and pk_raw == -1   ? color.new(color.red,   78) : na, title='dbg_pk_raw_short')
bgcolor(show_dbg_s5_final   and s5_pk_final_effective ==  1 ? color.new(color.lime, 60) : na, title='dbg_s5_final_long')
bgcolor(show_dbg_s5_final   and s5_pk_final_effective == -1 ? color.new(color.red,  60) : na, title='dbg_s5_final_short')

// ═══════════════════════════════════════════════════════════════════════════
// STRATEGY ENTRIES + BRACKET EXITS
// ═══════════════════════════════════════════════════════════════════════════

var int signal_counter = 0

// Choose firing model based on passthrough toggle.
//   OFF (default): edge-detect transitions in s5_pk_final (post-state-machine).
//   ON:            edge-detect transitions in pk_raw, gated by pk_raw[1] == 0
//                  (only fire when entering directional from neutral; rapid
//                  flips between directions are suppressed because neither
//                  side has a neutral predecessor).
fire_long_pre  = use_passthrough ? (pk_raw ==  1 and pk_raw[1] == 0) : (s5_pk_final ==  1 and s5_pk_final[1] !=  1)
fire_short_pre = use_passthrough ? (pk_raw == -1 and pk_raw[1] == 0) : (s5_pk_final == -1 and s5_pk_final[1] != -1)

// Gate as global hard stop (mean-reversion semantic):
//   fire_long  requires oob_side == -1 (gate OOB low, line went too low → fire long)
//   fire_short requires oob_side ==  1 (gate OOB high, line went too high → fire short)
// When use_gate is OFF, the gate condition is bypassed.
fire_long  = fire_long_pre  and (use_gate ? oob_side == -1 : true)
fire_short = fire_short_pre and (use_gate ? oob_side ==  1 : true)

if fire_long
    signal_counter += 1
    entry_id = "L_"  + str.tostring(signal_counter)
    exit_id  = "LX_" + str.tostring(signal_counter)
    tp_price = close * (1.0 + tp_pct / 100.0)
    sl_price = close * (1.0 - sl_pct / 100.0)
    strategy.entry(entry_id, strategy.long)
    strategy.exit(exit_id, from_entry = entry_id, limit = tp_price, stop = sl_price)

if fire_short
    signal_counter += 1
    entry_id = "S_"  + str.tostring(signal_counter)
    exit_id  = "SX_" + str.tostring(signal_counter)
    tp_price = close * (1.0 - tp_pct / 100.0)
    sl_price = close * (1.0 + sl_pct / 100.0)
    strategy.entry(entry_id, strategy.short)
    strategy.exit(exit_id, from_entry = entry_id, limit = tp_price, stop = sl_price)

// ═══════════════════════════════════════════════════════════════════════════
// VISUAL ARROWS
// ═══════════════════════════════════════════════════════════════════════════

plotshape(show_arrows and fire_long,  title='LONG',  style=shape.triangleup,
          location=location.belowbar, color=color.new(color.green, 0), size=size.tiny)
plotshape(show_arrows and fire_short, title='SHORT', style=shape.triangledown,
          location=location.abovebar, color=color.new(color.red, 0),   size=size.tiny)

// ═══════════════════════════════════════════════════════════════════════════
// PYTHON TRUTH LABELS — last 400 PROVEN signals from pk_signals + pk_outcomes
// Format: status (won/stopped/open) | win=X% | dd=Y%
// ═══════════════════════════════════════════════════════════════════════════

var int[]    py_sig_times  = array.from({ts_csv if n_labels > 0 else '0'})
var int[]    py_sig_dirs   = array.from({dir_csv if n_labels > 0 else '0'})
var string[] py_sig_status = array.from({status_csv if n_labels > 0 else '""'})
var float[]  py_sig_win    = array.from({winpct_csv if n_labels > 0 else '0.0'})
var float[]  py_sig_dd     = array.from({ddpct_csv if n_labels > 0 else '0.0'})

if show_labels and {str(n_labels > 0).lower()}
    for i = 0 to array.size(py_sig_times) - 1
        if array.get(py_sig_times, i) == time
            sig_dir    = array.get(py_sig_dirs,   i)
            sig_status = array.get(py_sig_status, i)
            sig_win    = array.get(py_sig_win,    i)
            sig_dd     = array.get(py_sig_dd,     i)
            label_text = (sig_dir == 1 ? "L " : "S ") + sig_status + " | win=" + str.tostring(sig_win, "#.##") + "% | dd=" + str.tostring(sig_dd, "#.##") + "%"
            label_color = sig_status == "won" ? color.new(color.green, 20) : sig_status == "stopped" ? color.new(color.red, 20) : color.new(color.gray, 20)
            label_y_offset = sig_dir == 1 ? low * 0.999 : high * 1.001
            label_style = sig_dir == 1 ? label.style_label_up : label.style_label_down
            label.new(bar_index, label_y_offset, label_text,
                      color = label_color, style = label_style,
                      textcolor = color.white, size = size.small)
            break

// ═══════════════════════════════════════════════════════════════════════════
// DEBUG TABLE (top-right) — live vote state
// ═══════════════════════════════════════════════════════════════════════════

show_debug = input.bool(false, 'Show debug table', group='Display')
if show_debug
    var table dbg = table.new(position.top_right, 2, 8, bgcolor=color.new(color.black, 70))
    if barstate.islast
        table.cell(dbg, 0, 0, 'long_pts',    text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 0, str.tostring(long_pts,    '#.##'), text_color=color.lime, text_size=size.small)
        table.cell(dbg, 0, 1, 'short_pts',   text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 1, str.tostring(short_pts,   '#.##'), text_color=color.red,  text_size=size.small)
        table.cell(dbg, 0, 2, 'long_ratio',  text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 2, str.tostring(long_ratio,  '#.##'), text_color=color.lime, text_size=size.small)
        table.cell(dbg, 0, 3, 'short_ratio', text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 3, str.tostring(short_ratio, '#.##'), text_color=color.red,  text_size=size.small)
        table.cell(dbg, 0, 4, 'pk_raw',      text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 4, str.tostring(pk_raw),            text_color=color.yellow, text_size=size.small)
        table.cell(dbg, 0, 5, 'countdown',   text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 5, str.tostring(pk_countdown),      text_color=color.yellow, text_size=size.small)
        table.cell(dbg, 0, 6, 's5_pk_final', text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 6, str.tostring(s5_pk_final),       text_color=color.aqua,   text_size=size.small)
        table.cell(dbg, 0, 7, 'signal #',    text_color=color.white, text_size=size.small)
        table.cell(dbg, 1, 7, str.tostring(signal_counter),    text_color=color.aqua,   text_size=size.small)
"""

    # ── Classification helper ────────────────────────────────────────────────

    @staticmethod
    def _classify(s: dict, profit_zone: float) -> str:
        """Per-signal status for label: won / stopped / open."""
        bts = s['bars_to_stop']
        mp  = s['max_profit_pct']
        if bts is None:
            return 'open'  # ran off dataset end ≡ trade still open
        if mp is not None and float(mp) >= profit_zone:
            return 'won'
        return 'stopped'

    @staticmethod
    def _src_to_pine_default(src: str) -> str:
        """Map Python src name to Pine input.source default value."""
        return {
            'close':  'close',
            'hl2':    'hl2',
            'hlc3':   'hlc3',
            'hlcc4':  'hlcc4',
            'ohlc4':  'ohlc4',
        }.get(src, 'close')
