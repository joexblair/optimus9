"""
strat_review.py — SKELETON (Joe 0627). The module-agnostic strategy report.

bl_review was bl-CENTRIC (a report over bl_states; bl = the spine, everything else bolted on). strat_review
inverts that: it's a chronological event timeline assembled from ACTIVE MODULES, NONE privileged. Each
module emits rows into ONE common schema (IDENTICAL to bl_review — so Power Query just swaps the table
name); the aggregator merges + persists + paints the composite bias. Toggle a module = a flag in its
existing table (bias_producer / bl_lines / trade_gate) — "everything in one place", no new hierarchy.

  MODULES (each = name → active-flag → emit-rows):
    bl        — breach lifecycle (state/exit/context) + gate-open trades.  active = bias_producer.bl_state
    cascade   — the lp-cascade entries (pl_cas_start/end).                 active = always (the trade machine)
    pk        — pk-bias events.                                           active = bias_producer.pk
    bro_cross — bro-cross flips (bro_x_bias).                             active = bias_producer.bro_cross
  bias_state column = composite of the ACTIVE bias producers (paint_bias_state).

Same row-GENERATION as bl_review (reused, proven); BESPOKE module ORCHESTRATION (this file). When every
module is active, strat_review === bl_review row-for-row. Disable bl → bl simply isn't in the flow.
SKELETON: bl/cascade/pk/bro wired; the value columns reuse bl_review's builders. Full port is incremental.
"""
import datetime as dtm
from datetime import timezone
from logger import get_logger
from optimus9.analysis.bl_detect import BLDetect
from optimus9.analysis.bl_review import build_review, _persist
from alchemy_report import build_bias_state, paint_bias_state
from optimus9.analysis.bias_state import pk_bias_events, bro_cross_flips
from optimus9.analysis.trade_gate import TradeGateWalker

_TABLE = 'strat_review'
_LOOKBACK_MS = 120 * 3600 * 1000

# the common schema (IDENTICAL to bl_review) — every module's rows are dicts keyed by these
_COLS = ['bls_pk', 'bar_time', 'bl_line', 'event', 'state', 'c_bls', 'breach_dir', 'predicted', 'raw_pk',
         'bias_state', 'lookback_trade', 'thrown_out', 'px_smooth', 'breach_line', 'bb_mage', 'bb_min',
         'exit_bits', 'stop_px', 'stop_at', 'profit_px', 'profit_at', 'swing_closest_dt', 'entry_dt',
         'swing_adverse_dt']


def _row(**kw):
    return {c: kw.get(c) for c in _COLS}


def _utc(t_ms):
    return dtm.datetime.utcfromtimestamp(int(t_ms) / 1000)


# ── module emitters (each returns rows in the common schema) ───────────────────────────────────────
def _cascade_rows(ctx):
    """lp-cascade entries (pl_cas_start/end) — the trade machine, rides the composite bias."""
    start = ctx['end_ms'] - _LOOKBACK_MS
    bias = ctx['bs'].direction_array(ctx['W'].ts)
    return [_row(bar_time=_utc(t), event=kind, breach_dir=side)
            for t, kind, side in TradeGateWalker(ctx['W'], ctx['db']).cascade(bias)
            if start <= t < ctx['end_ms']]


def _pk_rows(ctx):
    start = ctx['end_ms'] - _LOOKBACK_MS
    m = {'BULL': 1, 'BEAR': -1}
    return [_row(bar_time=_utc(u['t']), event='pk_bias', breach_dir=m[u['call']])
            for u in ctx['W'].signals() if u['call'] in m and start <= int(u['t']) < ctx['end_ms']]


def _bro_rows(ctx):
    start = ctx['end_ms'] - _LOOKBACK_MS
    return [_row(bar_time=_utc(f['t']), event='bro_x_bias', breach_dir=f['dir'], bb_mage=f['mage'], bb_min=f['min'])
            for f in bro_cross_flips(ctx['db'], ctx['W']) if start <= f['t'] < ctx['end_ms']]


def build_strat_review(db, end_ms):
    log = get_logger('StratReview')
    bp = {r['bp_name']: bool(r['bp_active']) for r in db.execute('SELECT bp_name, bp_active FROM bias_producer', fetch=True)}

    # breach detection (bl_states) — shared by the bl-lifecycle + trades modules; run if EITHER is active.
    # SRP split: build_review's rows separate by bl_line — the breach lifecycle (bl_line=the line:
    # state/exit/context) vs the gate-open trades (bl_line='gate': gate_open/context). One compute, two
    # modules, clean attribution.
    bl_all = []
    if bp.get('bl_state') or bp.get('trades'):
        BLDetect(db, lookback_hours=120, warmup_hours=48).report(end_ms=end_ms)
        bl_all = build_review(db, persist=False)
    W, bs = build_bias_state(db, end_ms)                              # composite bias from ACTIVE producers
    ctx = dict(db=db, W=W, bs=bs, end_ms=end_ms, bp=bp)

    # the module registry — each emits rows; NONE is the foundation. Toggle = its flag in bias_producer.
    modules = [
        ('bl',        lambda: [r for r in bl_all if r['bl_line'] != 'gate'] if bp.get('bl_state') else []),
        ('trades',    lambda: [r for r in bl_all if r['bl_line'] == 'gate'] if bp.get('trades') else []),
        ('cascade',   lambda: _cascade_rows(ctx) if bp.get('cascade') else []),
        ('pk',        lambda: _pk_rows(ctx) if bp.get('pk') else []),
        ('bro_cross', lambda: _bro_rows(ctx) if bp.get('bro_cross') else []),
    ]
    rows, counts = [], {}
    for name, emit in modules:
        r = emit(); counts[name] = len(r); rows += r
    rows.sort(key=lambda o: (o['bar_time'], o.get('bl_line') or ''))

    _persist(db, rows, table=_TABLE)                                 # same schema as bl_review
    nseg = paint_bias_state(db, bs, end_ms, table=_TABLE)            # composite bias_state column
    log.info(f'{_TABLE}: {len(rows)} rows · modules {counts} · {nseg} bias segments')
    return rows, counts


if __name__ == '__main__':
    import sys; sys.path.insert(0, '/home/joe/thecodes')
    from optimus9.config import get_db_config
    from optimus9 import DatabaseManager
    db = DatabaseManager(**get_db_config()); db.connect()
    END = int(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc).timestamp() * 1000)   # real-tape window [0615,0622)
    rows, counts = build_strat_review(db, END)
    print(f'strat_review: {len(rows)} rows · modules {counts}')
    db.disconnect()
