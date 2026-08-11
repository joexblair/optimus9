#!/usr/bin/env python3
"""momo_landed deliverables. Reads the banked `momo_landed` table, writes:

  1. `momo_landed_report` — one row per event, the onscreen table's 12 columns
  2. `ws_strat_momo_landed.pine` — blue/yellow bgcolor, TF1 pane

Both derive from the same SELECT, so the table and the chart cannot disagree.
No recompute: `build_momo_landed.py` owns the walk, this owns the presentation.
"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.jig import _Score

# the exact config the events were built at — build_momo_landed.py's constants
FENCE, XWOB, K_WINDOW = 20, 4, 4
BUCKET_MS = 60_000                    # TF1 pane, same as ws_strat_gated.pine
PINE = 'ws_strat_momo_landed.pine'

RPT_DDL = '''CREATE TABLE IF NOT EXISTS momo_landed_report (
    mlr_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    mlr_fence     SMALLINT NOT NULL,       -- KNOB fence_momo_landed = [20, 80]
    mlr_xwob      SMALLINT NOT NULL,       -- KNOB 4 * 5s bars held outside the fence
    mlr_kwindow   SMALLINT NOT NULL,       -- KNOB momo window = 4 * TF minutes
    mlr_landed    VARCHAR(19) NOT NULL,    -- col 1  the hold completes, first knowable bar
    mlr_line      VARCHAR(8)  NOT NULL,    -- col 2  ws{TF}r that created the event
    mlr_dr        TINYINT     NOT NULL,    -- col 3  +1 / -1, the ws1 marker's side
    mlr_cross_out VARCHAR(19) NOT NULL,    -- col 4  the bar it went outside the fence
    mlr_marker    VARCHAR(19) NOT NULL,    -- col 5  the ws1 marker that tagged it
    mlr_lag_min   DOUBLE,                  -- col 6  marker -> landed, minutes
    mlr_r_land    DOUBLE,                  -- col 7  ws{TF}r at the landed bar
    mlr_state     VARCHAR(8),              -- col 8  momo | curl at the tagging marker
    mlr_slope     DOUBLE,                  -- col 9
    mlr_r2        DOUBLE,                  -- col 10
    mlr_r_tag     DOUBLE,                  -- col 11 ws{TF}r at the tagging marker
    mlr_pxs       DOUBLE,                  -- col 12
    mlr_momentum_true   VARCHAR(19),       -- col 13 momo|curl fires: the FIRST marker of the
                                           --        unbroken same-side run in which this TF stayed
                                           --        qualified, up to and including the tagging marker
    mlr_momentum_set_by_tf VARCHAR(16),    -- col 14 'min-max' of the TFs qualifying at that marker
    UNIQUE KEY uq_mlr (mlr_fence, mlr_xwob, mlr_kwindow, mlr_line, mlr_landed),
    KEY (mlr_landed), KEY (mlr_line), KEY (mlr_dr))'''

COLS = ['mlr_fence', 'mlr_xwob', 'mlr_kwindow', 'mlr_landed', 'mlr_line', 'mlr_dr',
        'mlr_cross_out', 'mlr_marker', 'mlr_lag_min', 'mlr_r_land', 'mlr_state',
        'mlr_slope', 'mlr_r2', 'mlr_r_tag', 'mlr_pxs',
        'mlr_momentum_true', 'mlr_momentum_set_by_tf']


def momentum_true(db):
    """When momo|curl fired, per (marker, TF).

    RESOLUTION: momentum is evaluated ONLY at the ws1 markers — that is the spec ("at each marker,
    tag the TF{8 to 33}r lines that qualify"). So the finest grain available here is marker-grained,
    not 5 s. A 5 s momentum_true needs momo run on every bar for all 26 TFs; that is a new walk.

    A run breaks on a side flip: `dr` is an input to the momentum test, so the same TF qualifying
    under the other side is a different test, not a continuation.

    A run does NOT break on an intervening momo_landed. Clearing the tags is tag bookkeeping; the
    momo|curl condition on the line is unaffected by it.

    -> {(marker_ms, tf): (first_marker_utc, 'min-max')}
    """
    mk = db.execute('SELECT mlb_ms, mlb_utc, mlb_marker_side, mlb_tag_tfs FROM momo_landed_bar '
                    'WHERE mlb_marker=1 ORDER BY mlb_ms', fetch=True)
    seq = []
    for m in mk:
        tfs = set()
        if m['mlb_tag_tfs']:
            tfs = {int(p.split(':')[0]) for p in m['mlb_tag_tfs'].split(',')}
        seq.append((m['mlb_ms'], m['mlb_utc'], m['mlb_marker_side'], tfs))

    out = {}
    for i, (ms, _utc, side, tfs) in enumerate(seq):
        for tf in tfs:
            j = i
            while j - 1 >= 0 and seq[j - 1][2] == side and tf in seq[j - 1][3]:
                j -= 1
            span = seq[j][3]
            out[(ms, tf)] = (seq[j][1], '%d-%d' % (min(span), max(span)))
    return out


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(RPT_DDL)

    ev = db.execute(
        'SELECT ml_tf, ml_dr, ml_ms, ml_utc, ml_cross_utc, ml_marker_ms, ml_marker_utc, ml_lag_min, '
        '       ml_r, ml_momo_state, ml_momo_slope, ml_momo_r2, ml_momo_r, ml_pxs '
        'FROM momo_landed WHERE ml_fence=%s AND ml_xwob=%s AND ml_kwindow=%s ORDER BY ml_ms',
        (FENCE, XWOB, K_WINDOW), fetch=True)
    if not ev:
        print('no momo_landed rows at fence=%d xwob=%d kwindow=%d' % (FENCE, XWOB, K_WINDOW))
        return

    mt = momentum_true(db)
    rows = []
    for e in ev:
        t_utc, span = mt.get((e['ml_marker_ms'], e['ml_tf']), (None, None))
        if t_utc is None:
            raise RuntimeError('no tag for ws%dr at marker %s' % (e['ml_tf'], e['ml_marker_utc']))
        rows.append((FENCE, XWOB, K_WINDOW, e['ml_utc'], 'ws%dr' % e['ml_tf'], e['ml_dr'],
                     e['ml_cross_utc'], e['ml_marker_utc'], e['ml_lag_min'], e['ml_r'],
                     e['ml_momo_state'], e['ml_momo_slope'], e['ml_momo_r2'], e['ml_momo_r'],
                     e['ml_pxs'], t_utc, span))

    db.execute('DELETE FROM momo_landed_report WHERE mlr_fence=%s AND mlr_xwob=%s AND mlr_kwindow=%s',
               (FENCE, XWOB, K_WINDOW))
    db.executemany('INSERT INTO momo_landed_report (%s) VALUES (%s)'
                   % (','.join(COLS), ','.join(['%s'] * len(COLS))), rows)
    print('momo_landed_report : %d rows, %d columns' % (len(rows), len(COLS)))

    # --- pine. blue = dr +1 (hi side), yellow = dr -1 (lo side).
    # Precedent for blue-is-hi: emit_ws_strat_proposal.py, emit_exhv2_pine.py, bias_emit.py all
    # paint the hi-side stream blue. bgcolor never uses red/green — that channel is direction on
    # labels only (jig.emit_direction_overlay).
    bkt = _Score(None).bucket_spans
    hi = bkt([e['ml_ms'] for e in ev if e['ml_dr'] > 0], BUCKET_MS)
    lo = bkt([e['ml_ms'] for e in ev if e['ml_dr'] < 0], BUCKET_MS)
    nhi = sum(1 for e in ev if e['ml_dr'] > 0)
    nlo = len(ev) - nhi

    notes = [
        'ws_strat_momo_landed  —  momo_landed events, full window',
        '',
        '  BLUE    dr +1, hi side   %3d events -> %3d TF1 bars' % (nhi, len(hi)),
        '  YELLOW  dr -1, lo side   %3d events -> %3d TF1 bars' % (nlo, len(lo)),
        '',
        '  the painted bar is the LANDED bar: the xwob hold completes, first knowable bar',
        '  window %s -> %s' % (ev[0]['ml_utc'], ev[-1]['ml_utc']),
        '',
        '  mechanic: at each ws1 marker, tag the ws{8..33}r lines qualifying for momentum',
        '            (momo or curl). a tagged line that crosses OUT of fence_momo_landed and',
        '            holds xwob bars emits momo_landed. all tags clear on emit.',
        '',
        '  ws1 marker      = a gcws30b oob->ib crossing released by the ws1 gate',
        '                    (ws_strat_walk, wsw_gate_by = ws1Mage+ws1b), stamped at wsw_conf_ms',
        '  dr              = the ws1 marker side, wsw_side',
        '  lines           ws{TF}r  7|5|8|close,  TF = 8..33 minutes, emerging',
        '',
        '  KNOBS   fence_momo_landed %d      -> fence [%d, %d]' % (FENCE, FENCE, 100 - FENCE),
        '          xwob              %d      -> %ds held outside the fence' % (XWOB, XWOB * 5),
        '          kwindow           %d      -> momo window = %d * TF minutes' % (K_WINDOW, K_WINDOW),
        '          pxs grid          5s',
        '          BUCKET_MS         %d  -> TF1 pane' % BUCKET_MS,
        '',
        '  source  momo_landed / momo_landed_report,  fence=%d xwob=%d kwindow=%d'
        % (FENCE, XWOB, K_WINDOW),
    ]
    total = _Score(None).emit_bgcolor(
        [{'name': 'momo_landed_hi', 'ts': hi, 'color': 'color.blue'},
         {'name': 'momo_landed_lo', 'ts': lo, 'color': 'color.yellow'}],
        PINE, 'ws_strat_momo_landed — momo_landed (TF1)', opacity=0, notes=notes)
    print('%-28s : %d events -> %d painted TF1 bars (blue %d / yellow %d)'
          % (PINE, len(ev), total, len(hi), len(lo)))
    db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
