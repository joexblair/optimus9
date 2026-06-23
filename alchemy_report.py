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
`paint_bny30_bias()` overrides bl_review.bny30_bias with the same BiasState direction (replaces bny30).

_CFG mirrors the canonical cascade config (as bias_pk_emit) — the s30 lines are config-invariant,
so it only serves to instantiate the window + resolve the s30 line refs from the DB.
"""
import datetime as dtm
import numpy as np
from optimus9.compute.indicator_computer import IndicatorComputer as IC
import bias_machine as bm
from bias_machine import OOB_HI, OOB_LO
from optimus9.analysis.bias_state import BiasState

_EVENT = 's30a+Mwobs'
_CFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m',
                     xm45=False, mae=0.4, target=0.9, floater_anchor='last', verdict='pk')


def add_s30a_events(db, end_ms, lookback_hours=120):
    """Insert s30a-state onsets + s30a+Mwob fires into bl_review as event rows, gated by the
    breach-driven BIAS STATE (BiasState over s22r's bls3 flips): SHORT bias keeps HI s30a, LONG bias
    keeps LO (side == -bias). breach_dir tags the s30a side (+1 hi / -1 lo). Other value columns
    null. Replaces the prior s14M side-of-50 gate (Joe 0623, #32). Returns count."""
    start = end_ms - lookback_hours * 3600 * 1000
    W = bm.BiasWindow(db, end_ms, cfg=_CFG)
    c = W.cfg
    (s30, cM), (_, cm), (_, cr) = (W._ls.resolve(c.s30_M), W._ls.resolve(c.s30_m), W._ls.resolve(c.s30_r))
    f30 = IC.resample(W.base, s30); t30 = f30['timestamp'].to_numpy() + s30 * 1000
    M = IC.f_bb(IC.build_source(f30, cM[3]), cM[1], cM[2])
    m = IC.f_bb(IC.build_source(f30, cm[3]), cm[1], cm[2])
    r = IC.f_k(IC.build_source(f30, cr[4]), cr[1], cr[2], cr[3])
    hi = (M >= OOB_HI) & (m >= OOB_HI) & (r >= OOB_HI)
    lo = (M <= OOB_LO) & (m <= OOB_LO) & (r <= OOB_LO)
    events = []                                            # (time_ms, side): +1 hi / -1 lo
    events += [(int(t30[i]),  1) for i in range(1, len(hi)) if hi[i] and not hi[i - 1]]   # s30a-hi onset
    events += [(int(t30[i]), -1) for i in range(1, len(lo)) if lo[i] and not lo[i - 1]]   # s30a-lo onset
    events += [(int(t),  1) for t in W.HT]                 # s30a+Mwob hi trigger
    events += [(int(t), -1) for t in W.LT]                 # s30a+Mwob lo trigger
    ts = W.ts
    bias = BiasState(db, ('s22r',)).direction_array(ts, end_ms, lookback_hours)   # +1 long / -1 short (s22r bls3)
    rows = []
    for t, side in sorted(events):
        if not (start <= t < end_ms):
            continue
        j = int(np.searchsorted(ts, t, 'right')) - 1       # most recent base bar at/before the event
        if j < 0 or bias[j] == 0:                          # no bias yet (before the first bls3 flip)
            continue
        if side == -bias[j]:                               # SHORT bias keeps HI s30a, LONG keeps LO (Joe 0623)
            rows.append((dtm.datetime.utcfromtimestamp(t / 1000), _EVENT, side))
    if rows:
        db.executemany('INSERT INTO bl_review (bar_time, event, breach_dir) VALUES (%s, %s, %s)', rows)
    return len(rows)


def paint_bny30_bias(db, end_ms, lookback_hours=120):
    """Override bl_review.bny30_bias with the breach-driven BiasState direction (Joe 0623, #32):
    +1 long / -1 short, held between s22r bls3 flips. 0 before the first flip. Replaces the old
    bny30-gate passthrough — bl_review now reads the bias machine state. Returns the segment count."""
    tl = BiasState(db, ('s22r',)).timeline(end_ms, lookback_hours)     # [(t_ms, direction), ...]
    db.execute('UPDATE bl_review SET bny30_bias = 0')                  # clear (incl. pre-first-flip)
    for i, (t, d) in enumerate(tl):
        nxt = tl[i + 1][0] if i + 1 < len(tl) else end_ms
        db.execute('UPDATE bl_review SET bny30_bias = %s WHERE bar_time >= %s AND bar_time < %s',
                   (d, dtm.datetime.utcfromtimestamp(t / 1000), dtm.datetime.utcfromtimestamp(nxt / 1000)))
    return len(tl)
