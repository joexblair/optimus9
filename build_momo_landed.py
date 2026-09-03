"""build_momo_landed — IO for the momo_landed mechanic. Joe 0810.

SRP. The walk is optimus9.analysis.jig.momo_landed (pure). The momentum verdict is
optimus9.compute.momo_gated.momo_g under momo_window. This file: read the cache, compute the
verdicts at the markers, call the producer, write the tables.

Joe's spec, verbatim:
    1) decrease the range: TF8 to TF33
    2) create a `fence_momo_landed` fence built on 100-{knob:20}
    3) without using lookahead, walk the ws1 markers
    -at each marker, tag the TF{8 to 33}r lines that qualify for `momentum` (momo or curl)
    -keep walking the markers (causal)
    -IF a momentum tagged line has xwob {knob:4} crossed out of the fence_momo_landed fence
    --create a timestamped 'momo_landed' event

Joe's theory: "I'm using 30sec to 6min to accept a handoff from lines that are marked as
momo_landed=true. this is the first step towards learning how momentum will support the strategy."

    python3 build_momo_landed.py [--rebuild]
"""
import sys, datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, KLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis.jig import oob_ib_cross, momo_landed
from optimus9.compute.momo_gated import momo_g, momo_window
from optimus9.compute.momo_config import momo_bank, momo_config

# Joe 0810: "disable the current clear mechanism: instead of clearing on 'first momentum line
# exiting fence', now it will be 'highest TF momentum line curling against bias'".
# The old rule stays reachable as 'landed' so the banked 117 rows remain reproducible; it is off.
CLEAR_ON = 'hi_tf_counter_curl'

TFS = list(range(8, 34))          # Joe 0810: "decrease the range: TF8 to TF33"
R_SPEC = dict(k_len=7, rsi=5, stc=8, src='close')
# THE ws1 MARKERS. Joe 0810: "that's 160 gcws30b crossings, released by a test on ws1 — this is my
# definition of ws1 markers." They are read from ws_strat_walk, not recomputed here, so this file
# and the gate cannot drift apart.
#   WRONG UNTIL 0810: I used the ws1Mage/ws1b OOB->IB crossings themselves — 1,649 of them against
#   the 160, and not one shared a bar with a gcws30 signal. The whole first run was on that basis.
#   It also made `dr` look undefined (gcws30b had no side at 78.5% of those bars); with the correct
#   markers every one carries wsw_side by construction.
MARKER_LINES = ('ws1Mage', 'ws1b')   # read for the per-bar table only; not the marker source
MARKER_GATE_BY = 'ws1Mage+ws1b'      # the release path that defines a ws1 marker
FENCE = 20                        # fence_momo_landed = [20, 80]
XWOB = 4                          # 5 s pxs bars the tagged line must hold outside the fence
# BAKED IN 0903, Joe: "good work - bake it in". WAS 4 (Joe 0810). The window is K_WINDOW x the
# line's OWN timeframe, so this moves every timeframe, not just the ws20 the grid was scored on:
# ws8 32 -> 48 min, ws20 80 -> 120 min, ws33 132 -> 198 min.
# K_WINDOW LEFT THIS FILE 0903. It is a momentum knob, not a domTF one, and it now lives in
# momo_config as mmc_k_window - one value per bank, read per timeframe. Joe 0810 set the
# k_window x TF shape; Joe 0903 set it to 6 and moved it to the bank.
START = dt.datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

RCOLS = [f'mlb_r{t}' for t in TFS]

EV_DDL = '''CREATE TABLE IF NOT EXISTS momo_landed (
    ml_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    ml_fence     SMALLINT NOT NULL,        -- KNOB: fence_momo_landed = [fence, 100-fence]
    ml_xwob      SMALLINT NOT NULL,        -- KNOB: 5 s bars held outside the fence
    ml_kwindow   SMALLINT NOT NULL,        -- KNOB: momo window = kwindow * TF minutes
    ml_clear     VARCHAR(20) NOT NULL,     -- KNOB: landed | hi_tf_counter_curl
    ml_tf        SMALLINT NOT NULL,        -- the ws{TF}r line that landed
    ml_dr        TINYINT NOT NULL,         -- +1 / -1, the ws1 marker's side it was tagged with
    ml_ms        BIGINT NOT NULL, ml_utc VARCHAR(19),   -- hold completes; first KNOWABLE bar
    ml_cross_ms  BIGINT NOT NULL, ml_cross_utc VARCHAR(19),  -- the bar it went outside the fence
    ml_marker_ms BIGINT NOT NULL, ml_marker_utc VARCHAR(19), -- the ws1 marker that tagged it
    ml_lag_min   DOUBLE,                   -- marker -> hold complete, minutes
    ml_r         DOUBLE,                   -- ws{TF}r at the hold bar
    ml_pxs       DOUBLE,
    ml_momo_state VARCHAR(8),              -- 'momo' | 'curl' at the tagging marker
    ml_momo_slope DOUBLE, ml_momo_r2 DOUBLE, ml_momo_r DOUBLE,
    UNIQUE KEY uq_ml (ml_fence, ml_xwob, ml_kwindow, ml_clear, ml_tf, ml_ms),
    KEY (ml_ms), KEY (ml_tf), KEY (ml_dr))'''

BAR_DDL = '''CREATE TABLE IF NOT EXISTS momo_landed_bar (
    mlb_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    mlb_fence    SMALLINT NOT NULL, mlb_xwob SMALLINT NOT NULL, mlb_kwindow SMALLINT NOT NULL,
    mlb_clear    VARCHAR(20) NOT NULL,
    mlb_ms       BIGINT NOT NULL, mlb_utc VARCHAR(19),
    mlb_evt      TINYINT NOT NULL,         -- a pxs event bar (volume > 0)
    mlb_pxs      DOUBLE,
    mlb_marker   TINYINT NOT NULL,         -- 1 = a ws1 marker confirms here
    mlb_marker_side TINYINT,               -- the marker's side = dr for the momentum test
    mlb_marker_src VARCHAR(16),            -- which ws1 line(s) produced it
    mlb_tagged   SMALLINT NOT NULL,        -- how many TFs qualified for momentum at this marker
    mlb_tag_tfs  VARCHAR(255),             -- which ones, and momo|curl
    mlb_landed   TINYINT NOT NULL,         -- 1 = a momo_landed event completes here
    mlb_landed_tf SMALLINT,
    mlb_live     SMALLINT NOT NULL,        -- tags LIVE on this bar, not just at markers
    mlb_live_tfs VARCHAR(255),
    mlb_cleared  TINYINT NOT NULL,         -- 1 = the clear fired here
    mlb_clear_tf SMALLINT,                 -- the highest-TF line that curled against its dr
    mlb_ws1Mage  DOUBLE, mlb_ws1b DOUBLE,
    ''' + ',\n    '.join(f'{c:<10} DOUBLE' for c in RCOLS) + ''',
    UNIQUE KEY uq_mlb (mlb_fence, mlb_xwob, mlb_kwindow, mlb_clear, mlb_ms),
    KEY (mlb_ms), KEY (mlb_marker), KEY (mlb_landed))'''


def main(rebuild=False):
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, lo_boundary lo '
                      'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sysr['h']), float(sysr['lo'])
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in MARKER_LINES}
    for tf in TFS:
        ovr[f'r{tf}'] = override(tf * 60, KLine(**R_SPEC), 'emerging')
    print(f'building/loading {len(ovr)} lines ...', flush=True)
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg={'src': sysr['s'], 'len': sysr['l']},
                          rebuild=rebuild)
    ts = np.asarray(J.ts); pxs = np.asarray(J.pxs, float); evt = np.asarray(J.evt, bool)
    V = {n: np.asarray(J.W.line(n), float) for n in ovr}
    R = {tf: V[f'r{tf}'] for tf in TFS}
    i0 = int(np.searchsorted(ts, int(START.timestamp() * 1000)))

    # --- the ws1 markers = the gcws30 signals the ws1 gate released. dr = the signal's own side.
    #     Stamped at the CONFIRMATION bar, which is where the gate read its inputs and the first bar
    #     the signal is knowable. Causal.
    sig = db.execute("SELECT wsw_conf_ms m, wsw_side s, wsw_cross_utc c FROM ws_strat_walk "
                     "WHERE wsw_gate_by=%s ORDER BY wsw_conf_ms", (MARKER_GATE_BY,), fetch=True)
    MK, SRC = {}, {}
    for x in sig:
        c = int(np.searchsorted(ts, int(x['m'])))
        if c >= i0 and ts[c] == int(x['m']):
            MK[c] = int(x['s']); SRC[c] = [MARKER_GATE_BY]
    mk = sorted(MK)
    print(f'{len(mk):,} ws1 markers (gcws30 signals released by ws1Mage+ws1b)   window {u(ts[i0])} -> {u(ts[-1])}   '
          f'fence [{FENCE},{100-FENCE}]  xwob {XWOB} ({XWOB*5}s)  momo window {KW} x TF', flush=True)

    # THE BANKS, ONE PER TIMEFRAME. This file runs TFS 8 to 33, which crosses the wsf band (1..12)
    # into the domtf band (13..60), so there is no single bank for the run - each line takes the
    # bank that owns its own timeframe. Read once here; binding inside the loop is cheap.
    BANKS = {tf: momo_bank(db, tf) for tf in TFS}
    for _tf, _b in sorted(BANKS.items()):
        print(f"  TF{_tf} momentum bank: {_b['mech']} v{_b['version']} "
              f"k_window {_b['k_window']}", flush=True)

    # ONE k_window IN THE ROW KEY. This table keys on a single k_window per run, but the run now
    # spans two banks. They agree today; if they ever stop agreeing, one value would stand for two
    # different knob sets, so this fails instead of writing it.
    _kws = {b['k_window'] for b in BANKS.values()}
    if len(_kws) != 1:
        raise SystemExit(f'the banks in this run hold different k_window values: {sorted(_kws)}. '
                         'This table records one k_window per run, so it cannot span them.')
    KW = _kws.pop()

    # --- momentum at each marker. momo_window rebinds MOMO_WINDOW_MIN per TF (Joe 0810, option A).
    tagged, detail = {}, {}
    for tf in TFS:
        with momo_config(BANKS[tf]), momo_window(BANKS[tf]['k_window'] * tf):
            for c in mk:
                st, sl, r2, rw = momo_g(R[tf], MK[c], c)
                if st in ('momo', 'curl'):
                    tagged.setdefault(c, {})[tf] = MK[c]
                    detail[(c, tf)] = (st, float(sl), float(r2), float(rw))
        print(f'  TF{tf} tagged on {sum(1 for c in mk if tf in tagged.get(c, {})):>5} markers', flush=True)
    ntag = sum(len(v) for v in tagged.values())
    print(f'{ntag:,} (marker x TF) tags on {len(tagged):,} of {len(mk):,} markers', flush=True)

    # THE CLEAR. Joe: "highest TF momentum line curling against bias". MY READING: the same gated
    # curl test Joe defined on 0805 (momo_gated.momo_g), run with the OPPOSITE dr. Lives here, not
    # in the jig, for the same SRP reason `tagged` does: momo_g imports build_exhv2.
    def counter_curl(tf, dr, bar):
        with momo_config(BANKS[tf]), momo_window(BANKS[tf]['k_window'] * tf):
            st, _sl, _r2, _rw = momo_g(R[tf], -int(dr), bar)
        return st == 'curl'

    ev, clears, live_log = momo_landed(R, tagged, HI, LO, FENCE, XWOB, i0=i0,
                                       clear_on=CLEAR_ON, counter_curl=counter_curl)
    print(f'{len(ev):,} momo_landed events   {len(clears):,} clears   '
          f'clear_on={CLEAR_ON}', flush=True)

    rows = []
    for e in ev:
        st, sl, r2, rw = detail[(e['marker'], e['tf'])]
        rows.append((FENCE, XWOB, KW, CLEAR_ON, e['tf'], e['dr'],
                     int(ts[e['bar']]), u(ts[e['bar']]), int(ts[e['cross']]), u(ts[e['cross']]),
                     int(ts[e['marker']]), u(ts[e['marker']]),
                     (int(ts[e['bar']]) - int(ts[e['marker']])) / 60000.0,
                     e['val'], float(pxs[e['bar']]), st, sl, r2, rw))
    db.execute(EV_DDL)
    db.execute('DELETE FROM momo_landed WHERE ml_fence=%s AND ml_xwob=%s AND ml_kwindow=%s '
               'AND ml_clear=%s', (FENCE, XWOB, KW, CLEAR_ON))
    if rows:
        cols = ('ml_fence,ml_xwob,ml_kwindow,ml_clear,ml_tf,ml_dr,ml_ms,ml_utc,ml_cross_ms,ml_cross_utc,'
                'ml_marker_ms,ml_marker_utc,ml_lag_min,ml_r,ml_pxs,ml_momo_state,ml_momo_slope,'
                'ml_momo_r2,ml_momo_r')
        db.executemany(f'INSERT INTO momo_landed ({cols}) VALUES '
                       f'({",".join(["%s"] * len(cols.split(",")))})', rows)

    land = {e['bar']: e['tf'] for e in ev}
    CLR = {c['bar']: c for c in clears}
    brows = []
    for i in range(i0, len(ts)):
        tg = tagged.get(i, {})
        tgs = ','.join(f"{tf}:{detail[(i, tf)][0][0]}" for tf in sorted(tg)) if tg else None
        lv = live_log.get(i, {})
        brows.append([FENCE, XWOB, KW, CLEAR_ON, int(ts[i]), u(ts[i]), int(evt[i]),
                      None if not np.isfinite(pxs[i]) else float(pxs[i]),
                      1 if i in MK else 0, MK.get(i), '+'.join(SRC[i]) if i in SRC else None,
                      len(tg), (tgs[:255] if tgs else None),
                      1 if i in land else 0, land.get(i),
                      len(lv), (','.join(str(t) for t in sorted(lv))[:255] or None),
                      1 if i in CLR else 0, CLR[i]['tf'] if i in CLR else None,
                      float(V['ws1Mage'][i]), float(V['ws1b'][i])]
                     + [None if not np.isfinite(R[t][i]) else float(R[t][i]) for t in TFS])
    db.execute(BAR_DDL)
    db.execute('DELETE FROM momo_landed_bar WHERE mlb_fence=%s AND mlb_xwob=%s AND mlb_kwindow=%s '
               'AND mlb_clear=%s',
               (FENCE, XWOB, KW, CLEAR_ON))
    bc = ('mlb_fence,mlb_xwob,mlb_kwindow,mlb_clear,mlb_ms,mlb_utc,mlb_evt,mlb_pxs,mlb_marker,'
          'mlb_marker_side,mlb_marker_src,mlb_tagged,mlb_tag_tfs,mlb_landed,mlb_landed_tf,'
          'mlb_live,mlb_live_tfs,mlb_cleared,mlb_clear_tf,'
          'mlb_ws1Mage,mlb_ws1b,' + ','.join(RCOLS))
    db.executemany(f'INSERT INTO momo_landed_bar ({bc}) VALUES '
                   f'({",".join(["%s"] * len(bc.split(",")))})', brows)
    print(f'momo_landed     : {len(rows):,} rows')
    print(f'momo_landed_bar : {len(brows):,} rows, {len(RCOLS)} r-line columns')
    db.disconnect()


if __name__ == '__main__':
    main(rebuild='--rebuild' in sys.argv)
