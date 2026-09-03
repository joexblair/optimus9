#!/usr/bin/env python3
"""build_handoff — IO for the HTF-deference handoff. Joe 0810.

SRP: the walk is optimus9.analysis.jig.handoff (pure). This reads the cache, replays the
momo_landed walk to get the landings and the per-bar live set, calls the producer, writes the
table, and prints the 08-04 16:50 -> 19:50 trace Joe named.

    python3 build_handoff.py
"""
import sys, datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, KLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis.jig import momo_landed, handoff
from optimus9.compute.momo_gated import momo_g, momo_window
from optimus9.compute.momo_config import momo_bank, momo_config
import build_momo_landed as B

NEAR = 2                          # KNOB "near {fence-2:knob} the fence" -> [78,80) / (20,22]
XWOB = B.XWOB                     # 4 bars the HTF must hold in the near band to be WAITING
LEG_LO, LEG_HI = '2026-08-04 16:50:00', '2026-08-04 19:50:00'
ERRANT = ['2026-08-04 17:46:15', '2026-08-04 18:09:35', '2026-08-04 19:15:15',
          '2026-08-04 19:22:05']
TARGET = '2026-08-04 19:48:15'

DDL = '''CREATE TABLE IF NOT EXISTS handoff (
    hof_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    hof_fence    SMALLINT NOT NULL, hof_xwob SMALLINT NOT NULL, hof_kwindow SMALLINT NOT NULL,
    hof_near     SMALLINT NOT NULL,      -- KNOB 2 -> near band [78,80) hi / (20,22] lo
    hof_clear    VARCHAR(20) NOT NULL,   -- the momo_landed clear rule this sits on
    hof_ms       BIGINT NOT NULL, hof_utc VARCHAR(19),      -- the delegation. first knowable bar
    hof_tf       SMALLINT NOT NULL,      -- the line whose exit released it
    hof_dr       TINYINT NOT NULL,
    hof_origin_ms BIGINT, hof_origin_utc VARCHAR(19),       -- the landing that first tried
    hof_origin_tf SMALLINT,
    hof_deferred_s INT,                  -- origin -> delegation, seconds
    hof_depth    SMALLINT NOT NULL,      -- how many times it deferred
    hof_chain    VARCHAR(255),           -- tf>tf>tf, the deference chain
    hof_marker_ms BIGINT, hof_marker_utc VARCHAR(19),
    hof_r        DOUBLE,
    hof_released VARCHAR(28),            -- htf_left_the_near_band, or NULL for a normal exit
    UNIQUE KEY uq_hof (hof_fence, hof_xwob, hof_kwindow, hof_near, hof_clear, hof_ms, hof_tf),
    KEY (hof_ms), KEY (hof_tf), KEY (hof_dr))'''

BLK_DDL = '''CREATE TABLE IF NOT EXISTS handoff_blocked (
    hbk_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    hbk_fence    SMALLINT NOT NULL, hbk_xwob SMALLINT NOT NULL, hbk_kwindow SMALLINT NOT NULL,
    hbk_near     SMALLINT NOT NULL, hbk_clear VARCHAR(20) NOT NULL,
    hbk_ms       BIGINT NOT NULL, hbk_utc VARCHAR(19),   -- the landing that was suppressed
    hbk_tf       SMALLINT NOT NULL, hbk_dr TINYINT NOT NULL,
    hbk_defer_to SMALLINT NOT NULL,      -- the highest waiting HTF it submitted to
    hbk_htfs     VARCHAR(255),           -- every waiting HTF at that bar
    hbk_r        DOUBLE,
    UNIQUE KEY uq_hbk (hbk_fence, hbk_xwob, hbk_kwindow, hbk_near, hbk_clear, hbk_ms, hbk_tf),
    KEY (hbk_ms), KEY (hbk_tf))'''

BCOLS = ('hbk_fence,hbk_xwob,hbk_kwindow,hbk_near,hbk_clear,hbk_ms,hbk_utc,hbk_tf,hbk_dr,'
         'hbk_defer_to,hbk_htfs,hbk_r')

COLS = ('hof_fence,hof_xwob,hof_kwindow,hof_near,hof_clear,hof_ms,hof_utc,hof_tf,hof_dr,'
        'hof_origin_ms,hof_origin_utc,hof_origin_tf,hof_deferred_s,hof_depth,hof_chain,'
        'hof_marker_ms,hof_marker_utc,hof_r,hof_released')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, '
                      'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sysr['h']), float(sysr['lo'])
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in B.MARKER_LINES}
    for tf in B.TFS:
        ovr[f'r{tf}'] = override(tf * 60, KLine(**B.R_SPEC), 'emerging')
    print(f'loading {len(ovr)} lines ...', flush=True)
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sysr['s'], 'len': sysr['l']}, rebuild=False)
    ts = np.asarray(J.ts)
    R = {tf: np.asarray(J.W.line(f'r{tf}'), float) for tf in B.TFS}
    u = B.u
    i0 = int(np.searchsorted(ts, int(B.START.timestamp() * 1000)))

    sig = db.execute('SELECT wsw_conf_ms m, wsw_side s FROM ws_strat_walk WHERE wsw_gate_by=%s '
                     'ORDER BY wsw_conf_ms', (B.MARKER_GATE_BY,), fetch=True)
    MK = {}
    for x in sig:
        c = int(np.searchsorted(ts, int(x['m'])))
        if c >= i0 and ts[c] == int(x['m']):
            MK[c] = int(x['s'])
    mk = sorted(MK)

    # THE BANKS, ONE PER TIMEFRAME. This file runs B.TFS 8 to 33, which crosses the wsf band (1..12)
    # into the domtf band (13..60), so there is no single bank for the run - each line takes the
    # bank that owns its own timeframe. Read once here; binding inside the loop is cheap.
    BANKS = {tf: momo_bank(db, tf) for tf in B.TFS}
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

    tagged = {}
    for tf in B.TFS:
        with momo_config(BANKS[tf]), momo_window(BANKS[tf]['k_window'] * tf):
            for c in mk:
                st, _s, _r2, _r = momo_g(R[tf], MK[c], c)
                if st in ('momo', 'curl'):
                    tagged.setdefault(c, {})[tf] = MK[c]

    def counter_curl(tf, dr, bar):
        with momo_config(BANKS[tf]), momo_window(BANKS[tf]['k_window'] * tf):
            st, _s, _r2, _r = momo_g(R[tf], -int(dr), bar)
        return st == 'curl'

    ev, clears, live_log = momo_landed(R, tagged, HI, LO, B.FENCE, B.XWOB, i0=i0,
                                       clear_on=B.CLEAR_ON, counter_curl=counter_curl)
    print(f'{len(ev):,} momo_landed   {len(clears)} clears', flush=True)

    hofs, blocked = handoff(R, ev, live_log, B.FENCE, XWOB, NEAR, i0=i0)
    print(f'{len(hofs):,} handoffs   {len(blocked):,} landings suppressed   '
          f'near band [{100-B.FENCE-NEAR},{100-B.FENCE}) / ({B.FENCE},{B.FENCE+NEAR}]', flush=True)

    rows = []
    for h in hofs:
        chain = '>'.join(str(c['tf']) for c in h['chain']) + ('>' if h['chain'] else '') + str(h['tf'])
        rows.append((B.FENCE, B.XWOB, KW, NEAR, B.CLEAR_ON,
                     int(ts[h['bar']]), u(ts[h['bar']]), h['tf'], h['dr'],
                     int(ts[h['origin_bar']]), u(ts[h['origin_bar']]), h['origin_tf'],
                     h['deferred_s'], len(h['chain']), chain[:255],
                     int(ts[h['marker']]), u(ts[h['marker']]), h['val'], h.get('released')))
    db.execute(DDL)
    db.execute('DELETE FROM handoff WHERE hof_fence=%s AND hof_xwob=%s AND hof_kwindow=%s '
               'AND hof_near=%s AND hof_clear=%s',
               (B.FENCE, B.XWOB, KW, NEAR, B.CLEAR_ON))
    if rows:
        db.executemany(f'INSERT INTO handoff ({COLS}) VALUES '
                       f'({",".join(["%s"] * len(COLS.split(",")))})', rows)
    print(f'handoff : {len(rows):,} rows', flush=True)

    brows = [(B.FENCE, B.XWOB, KW, NEAR, B.CLEAR_ON, int(ts[b['bar']]), u(ts[b['bar']]),
              b['tf'], b['dr'], b['defer_to'], ','.join(str(z) for z in b['htfs'])[:255],
              float(R[b['tf']][b['bar']])) for b in blocked]
    db.execute(BLK_DDL)
    db.execute('DELETE FROM handoff_blocked WHERE hbk_fence=%s AND hbk_xwob=%s AND hbk_kwindow=%s '
               'AND hbk_near=%s AND hbk_clear=%s',
               (B.FENCE, B.XWOB, KW, NEAR, B.CLEAR_ON))
    if brows:
        db.executemany(f'INSERT INTO handoff_blocked ({BCOLS}) VALUES '
                       f'({",".join(["%s"] * len(BCOLS.split(",")))})', brows)
    print(f'handoff_blocked : {len(brows):,} rows', flush=True)

    print(f'\n=== the leg Joe named, {LEG_LO} -> {LEG_HI} ===', flush=True)
    print(f"  {'when':<20}{'':4}{'line':>7}{'r':>8}   detail")
    tl = []
    for b in blocked:
        tl.append((b['bar'], 'BLOCK', b))
    for h in hofs:
        tl.append((h['bar'], 'HANDOFF', h))
    for bar, kind, x in sorted(tl, key=lambda z: (z[0], z[1])):
        t = u(ts[bar])
        if not (LEG_LO <= t <= LEG_HI):
            continue
        if kind == 'BLOCK':
            print(f"  {t:<20}{'':4}{'ws%dr'%x['tf']:>7}{R[x['tf']][bar]:>8.2f}   deferred to ws{x['defer_to']}r"
                  f"   (waiting HTFs: {', '.join('ws%dr'%z for z in x['htfs'])})")
        else:
            ch = '>'.join('ws%dr' % c['tf'] for c in x['chain'])
            print(f"  {t:<20}{'>>>>':4}{'ws%dr'%x['tf']:>7}{x['val']:>8.2f}   HANDOFF"
                  f"   origin ws{x['origin_tf']}r @ {u(ts[x['origin_bar']])}"
                  f"   deferred {x['deferred_s']/60:.1f} min   depth {len(x['chain'])}"
                  f"{'   chain ' + ch if ch else ''}"
                  f"{'   [' + x['released'] + ']' if x.get('released') else ''}")

    print('\n=== Joe\'s errant stamps ===', flush=True)
    hset = {u(ts[h['bar']]) for h in hofs}
    bset = {}
    for b in blocked:
        bset.setdefault(u(ts[b['bar']]), []).append(b)
    for t in ERRANT + [TARGET]:
        tag = 'TARGET' if t == TARGET else 'errant'
        if t in hset:
            print(f"  {t}  {tag:<7} -> still a HANDOFF")
        elif t in bset:
            b = bset[t][0]
            print(f"  {t}  {tag:<7} -> SUPPRESSED, deferred to ws{b['defer_to']}r")
        else:
            print(f"  {t}  {tag:<7} -> not a landing under these knobs")
    db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
