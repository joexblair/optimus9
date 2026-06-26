"""
alchemy_report.py (Joe 0622) — the beginning of the 'alchemy reporting': overlays the bias entry
signals onto the bl_review event timeline.

SRP: a PRODUCER that appends event rows to bl_review — it does NOT touch build_review's BL event
logic. Run AFTER build_review (which drops+rebuilds the table). Both signals print the same label
's30a+Mwobs' in the `event` column (Joe's call), gated by the breach-driven BIAS STATE (BiasState
over s22r's bls3 flips, #32), with `breach_dir` tagging the s30a side (+1 hi / -1 lo); other value
columns stay null ('just the event'):
  • s30a       — the s30 set (m, M, r) all OOB the same side: the entry STATE (onset marked).
  • s30a+Mwob  — the s30M wob firing while m, r OOB: the entry TRIGGER (the window's W.HT/W.LT).
Added separately (two row-sets), both labelled 's30a+Mwobs'. SHORT bias keeps HI s30a, LONG keeps LO.
`paint_bias_state()` writes bl_review.bias_state from the same BiasState direction (bny30 retired).

_CFG mirrors the canonical cascade config (as bias_pk_emit) — the s30 lines are config-invariant,
so it only serves to instantiate the window + resolve the s30 line refs from the DB.
"""
import datetime as dtm
import numpy as np
import bias_machine as bm
from optimus9.analysis.bias_state import BiasState, bls3_bias_events, pk_bias_events, bro_cross_bias_events, bro_cross_flips

_EVENT = 's30a+Mwobs'
_CFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m',
                     xm45=False, mae=0.4, target=0.9, floater_anchor='last', verdict='pk')


def build_bias_state(db, end_ms, lookback_hours=120):
    """Build the bias window + the merged BiasState (bls3 + pk + bro-cross producers) once, for both
    consumers. Producers stack most-recent-wins (#37 BRD: composite bias)."""
    W = bm.BiasWindow(db, end_ms, cfg=_CFG)
    bs = (BiasState()
          .feed(bls3_bias_events(db, ('s22r',), end_ms, lookback_hours))
          .feed(pk_bias_events(W))
          .feed(bro_cross_bias_events(db, W)))
    return W, bs


def add_pl_cascade_events(db, W, bs, end_ms, lookback_hours=120):
    """Insert the DECOUPLED lp-cascade overlay into bl_review (alchemy BRD 0626). Replaces the pk-walked
    s30a overlay: the cascade (s6m → xm45a → gcs15a → xm45min wob) now rides the COMPOSITE bias, not the
    pk producer (the 17:04 gate-gap fix). Two events: 'pl_cas_start' (s6m onset) + 'pl_cas_end' (the
    xm45min-wob entry — the trade). breach_dir tags the side. Returns the row count."""
    from optimus9.analysis.trade_gate import TradeGateWalker
    start = end_ms - lookback_hours * 3600 * 1000
    bias = bs.direction_array(W.ts)
    rows = [(dtm.datetime.utcfromtimestamp(t / 1000), kind, side)
            for t, kind, side in TradeGateWalker(W, db).cascade(bias) if start <= t < end_ms]
    if rows:
        db.executemany('INSERT INTO bl_review (bar_time, event, breach_dir) VALUES (%s, %s, %s)', rows)
    return len(rows)


def add_bro_cross_events(db, W, end_ms, lookback_hours=120):
    """Insert a `bro_x_bias` event row per bro-cross flip (#37 / alchemy BRD): the weave-cease bias
    change. `breach_dir` tags the side (+1 bull / -1 bear); `bb_mage`/`bb_min` = the triggering set's
    mage/min at the flip. SRP: appends event rows, mirrors add_s30a_events. Returns the row count."""
    start = end_ms - lookback_hours * 3600 * 1000
    rows = [(dtm.datetime.utcfromtimestamp(f['t'] / 1000), 'bro_x_bias', f['dir'], f['mage'], f['min'])
            for f in bro_cross_flips(db, W) if start <= f['t'] < end_ms]
    if rows:
        db.executemany('INSERT INTO bl_review (bar_time, event, breach_dir, bb_mage, bb_min) VALUES (%s, %s, %s, %s, %s)', rows)
    return len(rows)


def add_pk_bias_events(db, W, end_ms, lookback_hours=120):
    """Insert a `pk_bias` event row per bias-pk update (the pk producer's own bias signal — was invisible).
    breach_dir tags direction (+1 bull / -1 bear). Mirrors add_bro_cross_events. Returns the row count."""
    start = end_ms - lookback_hours * 3600 * 1000
    m = {'BULL': 1, 'BEAR': -1}
    rows = [(dtm.datetime.utcfromtimestamp(int(u['t']) / 1000), 'pk_bias', m[u['call']])
            for u in W.signals() if u['call'] in m and start <= int(u['t']) < end_ms]
    if rows:
        db.executemany('INSERT INTO bl_review (bar_time, event, breach_dir) VALUES (%s, %s, %s)', rows)
    return len(rows)


def paint_bias_state(db, bs, end_ms):
    """Write bl_review.bias_state from the merged BiasState direction (Joe 0623 #32; 0626 alchemy BRD):
    +1 long / -1 short, held between events (bls3 flips + pk updates + bro-cross flips). 0 before the
    first. bny30 is retired — bl_review reads the bias machine state. Returns the segment count."""
    tl = bs.timeline()                                                 # [(t_ms, direction), ...] merged
    db.execute('UPDATE bl_review SET bias_state = 0')                  # clear (incl. pre-first-event)
    for i, (t, d) in enumerate(tl):
        nxt = tl[i + 1][0] if i + 1 < len(tl) else end_ms
        db.execute('UPDATE bl_review SET bias_state = %s WHERE bar_time >= %s AND bar_time < %s',
                   (d, dtm.datetime.utcfromtimestamp(t / 1000), dtm.datetime.utcfromtimestamp(nxt / 1000)))
    return len(tl)
