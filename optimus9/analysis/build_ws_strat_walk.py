"""build_ws_strat_walk — IO for the ws_strat_walk table + the red/green pine. Joe 0805.

SRP. The mechanic is optimus9/analysis/ws_strat.py (pure, no IO). This file: read the 21 lines from
the 08-05 line cache, call walk(), write ws_strat_walk, emit the pine.

THE TABLE is durable and knob-stamped: wsw_oobw / wsw_xwob are COLUMNS, unique on
(oobw, xwob, cross_ms), and a run DELETEs only its own knob pair before inserting. Two configs
coexist; neither overwrites the other. Same pattern as s46_event's (se_cfg, se_fence_s, se_xwob).

THE PINE (Joe 0805: "align the pine timestamps to fit on a 15second pane. if the timestamps are not
15sec seamed, print the bgcolors on the 15s bar prior to the timestamp"). jig.bucket_spans(ts,
15000) floors each 5 s timestamp onto its own 15 s seam — which IS the 15 s bar prior to it — and
dedupes. Colours follow the LOCKED _bgcolor_frag block (jig.py:567): red = the hi side, green = the
lo side.

    python3 -m optimus9.analysis.build_ws_strat_walk [--oobw 18] [--xwob 2] [--no-pine]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.jig import _Score
from optimus9.analysis.ws_strat import (walk, candidates, states, gate, LINES,
                                        GATE_FENCE, GATE_LB)
from optimus9.compute.line_config import LineStore
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP

START = dt.datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)   # Joe 0805: "starting at 08-04 12:00"
START_MS = int(START.timestamp() * 1000)
OOBW, XWOB = 16, 2               # Joe's two knobs. oobw in 5 s bars (>16 => >=17 = 85 s); xwob in 5 s bars.
#                                  0805: oobw 18 -> 8, from Joe's
#                                  8 estimated bgcolor times. 5 of the 8 sat on candidates of dwell 9..18;
#                                  two more (19:44:30, 05:27:30) need the dwell to survive a short IB poke.
FENCE, LB = GATE_FENCE, GATE_LB                    # gate knobs: fence 22 | lookback 19 bars (95 s)
BUCKET_MS = 60_000               # TF1 — Joe's pane. Was 15_000 from the 0805 15s request and
#                                  never moved; on a 1-min chart only 42 of 160 timestamps sat
#                                  on a minute open, so 118 never painted. array.binary_search
#                                  matches the BAR OPEN exactly, so the bucket must equal the
#                                  chart TF. 160 events -> 160 distinct minutes, 0 collisions.
PINE = 'ws_strat_gated.pine'   # Joe 0810 cats THIS file. Its meaning is fixed: the signals
#                                the current gate RELEASES. Do not repoint it, do not reuse
#                                the name for anything else.

# 21 line columns, named wsw_<line>. MySQL column names are case-insensitive, so wsw_ws1Mage and
# wsw_ws1m are distinct only because 'Mage' != 'm' — not because of the capital M.
COLS = ['wsw_' + n for n in LINES]

DDL = '''CREATE TABLE IF NOT EXISTS ws_strat_walk (
    wsw_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wsw_oobw      SMALLINT NOT NULL,          -- KNOB: OOB dwell floor, 5s bars, tested STRICTLY >
    wsw_xwob      SMALLINT NOT NULL,          -- KNOB: bars gcws30b must hold IB to confirm the cross
    wsw_cross_ms  BIGINT NOT NULL,            -- the FIRST IB bar = Joe's crossover timestamp
    wsw_cross_utc VARCHAR(19),
    wsw_conf_ms   BIGINT NOT NULL,            -- cross + (xwob-1): the first bar the event is KNOWABLE
    wsw_conf_utc  VARCHAR(19),
    wsw_bucket_ms BIGINT NOT NULL,            -- cross_ms floored onto its TF1 (60s) bar open (the pine bar)
    wsw_fence     SMALLINT NOT NULL,          -- KNOB: ws1b must sit outside [fence, 100-fence]
    wsw_lb        SMALLINT NOT NULL,          -- KNOB: ws1b lookback, 5s bars, ENDING at the conf bar
    wsw_blen      SMALLINT NOT NULL,          -- gcws30b + ws1b bb length, from vw_indicator_configs_live
    wsw_bmult     DECIMAL(8,4) NOT NULL,      -- ... and its mult. Banked because the line spec is NOT
    wsw_mlen      SMALLINT NOT NULL,          -- otherwise in the key: two runs on different lines would
    wsw_mmult     DECIMAL(8,4) NOT NULL,      -- collide on (oobw, xwob, ms) and silently overwrite.
    wsw_side      TINYINT NOT NULL,           -- +1 the OOB run was hi (>=85), -1 lo (<=15)
    wsw_oob_bars  INT NOT NULL,               -- the OOB run length, 5s bars, at the last OOB bar
    wsw_gated     TINYINT NOT NULL,           -- 1 = blocked by the gate, 0 = passes
    wsw_gate_by   VARCHAR(16) NOT NULL,       -- what RELEASED it: 'ws1Mage+ws1b' | 'lookback'.
    --                                           '' = nothing released it, so it stays blocked.
    wsw_ws1_exhausted TINYINT NOT NULL,       -- 1 = passed ONLY via the lookback (Joe's `ws1-exhausted`)
    wsw_lb_oob    TINYINT NOT NULL,           -- the lookback found ws1b OOB (>=85 / <=15)
    wsw_lb_fence  TINYINT NOT NULL,           -- the lookback found ws1b merely outside the fence
    wsw_ws1b_weaker_than_ws1Mage TINYINT NOT NULL,  -- Joe 0810: "if ws1b is outside of the fence and
    --                                           has not reached oob when gcws30 signals, then a flag
    --                                           is set to show that ws1b was weaker than s1Mage".
    --                                           = ws1Mage OOB AND ws1b outside the fence AND ws1b
    --                                           not OOB. Both sides of the comparison must hold.
    wsw_pxs       DOUBLE,                     -- px_smooth (DEMA close 2, event tape) at the conf bar
    ''' + ',\n    '.join(f'{c:<16} DOUBLE' for c in COLS) + ''',
    UNIQUE KEY uq_wsw (wsw_oobw, wsw_xwob, wsw_fence, wsw_lb, wsw_blen, wsw_bmult,
                       wsw_mlen, wsw_mmult, wsw_cross_ms),
    KEY (wsw_cross_ms), KEY (wsw_side), KEY (wsw_gated), KEY (wsw_ws1_exhausted))'''

BCOLS = ['wsb_' + n for n in LINES]

# ws_strat_bar — the DEBUG/ANALYSIS table (Joe 0805: "does your debug/analysis table (not my walk
# table) have all pxs events and the associated line values ... write on each bar"). ONE ROW PER 5 s
# BAR of the walk window, carrying px_smooth, the 21 line values, and the full walk state — so a
# question like "what prevented 23:30:30 from creating a pine emit" is a WHERE clause, not a script.
# wsb_evt marks the pxs EVENT bars (volume > 0); on a filler bar every line and pxs is the carried
# forward value, which is why the flag is banked rather than the filler bars dropped.
BAR_DDL = '''CREATE TABLE IF NOT EXISTS ws_strat_bar (
    wsb_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wsb_oobw      SMALLINT NOT NULL,          -- KNOB, as ws_strat_walk
    wsb_xwob      SMALLINT NOT NULL,
    wsb_blen      SMALLINT NOT NULL, wsb_bmult DECIMAL(8,4) NOT NULL,
    wsb_mlen      SMALLINT NOT NULL, wsb_mmult DECIMAL(8,4) NOT NULL,
    wsb_ms        BIGINT NOT NULL, wsb_utc VARCHAR(19),
    wsb_evt       TINYINT NOT NULL,           -- 1 = a pxs EVENT bar (volume > 0); 0 = carried-forward filler
    wsb_px        DOUBLE,                     -- kline_collection close at this bar
    wsb_pxs       DOUBLE,                     -- px_smooth: DEMA(close, 2) on the event tape
    wsb_state     TINYINT,                    -- gcws30b: +1 OOB-hi, -1 OOB-lo, 0 IB, NULL = NaN
    wsb_hi_run    INT NOT NULL,               -- consecutive bars ENDING HERE with gcws30b >= hi
    wsb_lo_run    INT NOT NULL,               -- ... <= lo
    wsb_ib_run    INT NOT NULL,               -- ... strictly IB
    wsb_dwell     INT NOT NULL,               -- the OOB dwell counter at this bar. SURVIVES an IB
    --                                           excursion shorter than xwob; reset by a confirmed
    --                                           cross, a side flip or NaN. This is what oobw gates.
    wsb_dwell_side TINYINT NOT NULL,          -- the side that counter belongs to; 0 = no session open
    wsb_cand      TINYINT NOT NULL,           -- 1 = this bar is the FIRST IB bar of an xwob-confirmed run
    wsb_gate_ok   TINYINT NOT NULL,           -- 1 = that candidate's prior OOB run passed > oobw
    wsb_conf      TINYINT NOT NULL,           -- 1 = this bar is a candidate's confirmation bar
    wsb_side      TINYINT,                    -- candidate bars only: +1 the prior OOB run was hi, -1 lo
    wsb_oob_bars  INT,                        -- candidate bars only: that prior OOB run length, 5s bars
    wsb_gated     TINYINT,                    -- signal bars only: 1 = blocked by the gate
    wsb_gate_by   VARCHAR(16),                -- what RELEASED it; '' = nothing did
    wsb_ws1_exhausted TINYINT,                -- 1 = passed ONLY via the ws1b lookback
    wsb_lb_oob    TINYINT, wsb_lb_fence TINYINT,
    wsb_ws1b_weaker_than_ws1Mage TINYINT,     -- Joe 0810, signal bars only
    ''' + ',\n    '.join(f'{c:<16} DOUBLE' for c in BCOLS) + ''',
    UNIQUE KEY uq_wsb (wsb_oobw, wsb_xwob, wsb_blen, wsb_bmult, wsb_mlen, wsb_mmult, wsb_ms),
    KEY (wsb_ms), KEY (wsb_evt), KEY (wsb_state), KEY (wsb_cand), KEY (wsb_gate_ok))'''

u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def _migrate(db):
    """Idempotent. Joe 0805: "sticky was never an option, so bake it in to the spec, delete any
    references to contiguous". The tables briefly carried a wsw_rule/wsb_rule column with two
    values; the dwell that survives a short IB excursion is now the ONLY rule, so the column and
    every row written under the other value are removed. wsb_dwell / wsb_dwell_side stay — they are
    the dwell counter itself, not the rule flag."""
    have = lambda t, c: bool(db.execute(
        "SELECT 1 FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
        "AND TABLE_NAME=%s AND COLUMN_NAME=%s", (t, c), fetch=True))
    tbl = lambda t: bool(db.execute("SHOW TABLES LIKE %s", (t,), fetch=True))
    # gate builds keep adding columns. A CREATE TABLE IF NOT
    # EXISTS cannot add them, and every banked row predates the gate, so the tables are rebuilt from
    # scratch rather than half-migrated. Nothing is lost — both are fully regenerated by this run.
    for t, c in (('ws_strat_walk', 'wsw_gated'), ('ws_strat_bar', 'wsb_gated')):
        if tbl(t) and not have(t, c):
            n = db.execute(f'SELECT COUNT(*) n FROM {t}', fetch=True)[0]['n']
            db.execute(f'DROP TABLE {t}')
            print(f'migrated {t}: dropped and rebuilt for the gate columns ({n} pre-gate rows)')
    for t, col, key, kcols in (('ws_strat_walk', 'wsw_rule', 'uq_wsw',
                                'wsw_oobw, wsw_xwob, wsw_cross_ms'),
                               ('ws_strat_bar', 'wsb_rule', 'uq_wsb',
                                'wsb_oobw, wsb_xwob, wsb_ms')):
        if not (tbl(t) and have(t, col)):
            continue
        n = db.execute(f"SELECT COUNT(*) n FROM {t} WHERE {col} <> 'sticky'", fetch=True)[0]['n']
        db.execute(f"DELETE FROM {t} WHERE {col} <> 'sticky'")
        db.execute(f"ALTER TABLE {t} DROP INDEX {key}, ADD UNIQUE KEY {key} ({kcols})")
        db.execute(f"ALTER TABLE {t} DROP COLUMN {col}")
        print(f"migrated {t}: dropped {n} rows written under the superseded dwell, DROP {col}, "
              f"{key} rebuilt on ({kcols})")


def write_bars(db, ts, V, pxs, evt, i0, i1, HI, LO, oobw, xwob, ev=(), spec=(48, 0.98, 37, 0.90)):
    """ws_strat_bar: one row per 5 s bar of the walk window. States come from ws_strat.states() —
    the SAME arrays walk() runs on, so the table cannot drift from the events."""
    S = states(V['gcws30b'], HI, LO, xwob)
    cand = {e['cross']: e for e in candidates(V['gcws30b'], HI, LO, xwob, S)}
    conf_at = {e['conf'] for e in cand.values()}
    G = {e['cross']: e for e in ev}                    # the GATED verdict, by cross bar

    px = np.full(len(ts), np.nan)
    rows = db.execute('SELECT kc_timestamp t, kc_close c FROM kline_collection WHERE kc_tp_pk=1 '
                      'AND kc_timestamp BETWEEN %s AND %s', (int(ts[i0]), int(ts[i1 - 1])), fetch=True)
    if rows:
        kt = np.array([r['t'] for r in rows], np.int64); kc = np.array([float(r['c']) for r in rows])
        o = np.argsort(kt); kt, kc = kt[o], kc[o]
        j = np.searchsorted(ts, kt)
        ok = (j < len(ts)) & (ts[np.clip(j, 0, len(ts) - 1)] == kt)
        px[j[ok]] = kc[ok]

    out = []
    for i in range(i0, i1):
        st = 1 if S['oob_hi'][i] else (-1 if S['oob_lo'][i] else (0 if S['ib'][i] else None))
        e = cand.get(i)
        out.append([oobw, xwob, *spec, int(ts[i]), u(ts[i]), int(evt[i]),
                    None if not np.isfinite(px[i]) else float(px[i]),
                    None if pxs is None or not np.isfinite(pxs[i]) else float(pxs[i]),
                    st, int(S['hi_run'][i]), int(S['lo_run'][i]), int(S['ib_run'][i]),
                    int(S['dwell'][i]), int(S['dwell_side'][i]),
                    1 if e else 0, 1 if (e and e['oob'] > oobw) else 0, 1 if i in conf_at else 0,
                    e['side'] if e else None, e['oob'] if e else None,
                    G[i]['gated'] if i in G else None, G[i]['by'] if i in G else None,
                    G[i]['exhausted'] if i in G else None,
                    G[i]['lb_oob'] if i in G else None, G[i]['lb_fence'] if i in G else None,
                    G[i]['ws1b_weaker'] if i in G else None]
                   + [None if not np.isfinite(V[n][i]) else float(V[n][i]) for n in LINES])

    _migrate(db)
    db.execute(BAR_DDL)
    db.execute('DELETE FROM ws_strat_bar WHERE wsb_oobw=%s AND wsb_xwob=%s', (oobw, xwob))
    cols = ('wsb_oobw,wsb_xwob,wsb_blen,wsb_bmult,wsb_mlen,wsb_mmult,wsb_ms,wsb_utc,wsb_evt,wsb_px,wsb_pxs,wsb_state,wsb_hi_run,'
            'wsb_lo_run,wsb_ib_run,wsb_dwell,wsb_dwell_side,wsb_cand,wsb_gate_ok,wsb_conf,wsb_side,'
            'wsb_oob_bars,wsb_gated,wsb_gate_by,wsb_ws1_exhausted,wsb_lb_oob,wsb_lb_fence,'
            'wsb_ws1b_weaker_than_ws1Mage,'
            + ','.join(BCOLS))
    nph = len(cols.split(','))
    db.executemany(f'INSERT INTO ws_strat_bar ({cols}) VALUES ({",".join(["%s"] * nph)})', out)
    return out, cand


def main(oobw=OOBW, xwob=XWOB, pine=True, bars=True):
    db = DatabaseManager(**get_db_config()); db.connect()
    row = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, lo_boundary lo '
                     'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(row['h']), float(row['lo'])
    pxs_cfg = {'src': row['s'], 'len': row['l']}
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in LINES}
    # the LIVE spec of the three lines that enter a decision, banked on every row (see the DDL note)
    BLEN, BMULT = ovr['gcws30b'][1][1], float(ovr['gcws30b'][1][2])
    MLEN, MMULT = ovr['ws1Mage'][1][1], float(ovr['ws1Mage'][1][2])
    assert ovr['ws1b'][1][1:3] == ovr['gcws30b'][1][1:3], 'ws1b and gcws30b must share the b spec'
    print(f'lines  gcws30b/ws1b bb {BLEN}|{BMULT}  ws1Mage bb {MLEN}|{MMULT}')

    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg=pxs_cfg)   # cache HIT — built 0805
    ts = np.asarray(J.ts)
    V = {n: np.asarray(J.W.line(n), float) for n in LINES}
    pxs = np.asarray(J.pxs, float) if J.pxs is not None else None
    evt = np.asarray(J.evt, bool) if J.evt is not None else np.ones(len(ts), bool)

    i0 = int(np.searchsorted(ts, START_MS, 'left'))
    print(f'boundaries hi {HI} / lo {LO}   knobs oobw {oobw} (>{oobw} bars = >={oobw + 1} = '
          f'{(oobw + 1) * 5}s)  xwob {xwob} ({xwob * 5}s)')
    print(f'tape {u(ts[0])} -> {u(ts[-1])}, {len(ts):,} bars')
    print(f'walk {u(ts[i0])} -> {u(ts[-1])}, bars {i0:,}..{len(ts) - 1:,} = {len(ts) - i0:,}')

    ev = walk(V['gcws30b'], HI, LO, oobw, xwob, i0=i0)
    gate(ev, V, HI, LO, FENCE, LB)
    print(f'\n{len(ev)} crossovers  (hi {sum(1 for e in ev if e["side"] > 0)} / '
          f'lo {sum(1 for e in ev if e["side"] < 0)})')

    rows = []
    for e in ev:
        c, k = e['conf'], e['cross']
        rows.append([oobw, xwob, int(ts[k]), u(ts[k]), int(ts[c]), u(ts[c]),
                     (int(ts[k]) // BUCKET_MS) * BUCKET_MS, FENCE, LB,
                     BLEN, BMULT, MLEN, MMULT, e['side'], e['oob'],
                     e['gated'], e['by'], e['exhausted'], e['lb_oob'], e['lb_fence'],
                     e['ws1b_weaker'],
                     float(pxs[c]) if pxs is not None else None]
                    + [float(V[n][c]) for n in LINES])

    _migrate(db)
    db.execute(DDL)
    db.execute('DELETE FROM ws_strat_walk WHERE wsw_oobw=%s AND wsw_xwob=%s', (oobw, xwob))
    if rows:
        cols = ('wsw_oobw,wsw_xwob,wsw_cross_ms,wsw_cross_utc,wsw_conf_ms,wsw_conf_utc,'
                'wsw_bucket_ms,wsw_fence,wsw_lb,wsw_blen,wsw_bmult,wsw_mlen,wsw_mmult,'
                'wsw_side,wsw_oob_bars,wsw_gated,'
                'wsw_gate_by,wsw_ws1_exhausted,wsw_lb_oob,wsw_lb_fence,'
                'wsw_ws1b_weaker_than_ws1Mage,wsw_pxs,' + ','.join(COLS))
        npw = len(cols.split(','))
        db.executemany(f'INSERT INTO ws_strat_walk ({cols}) VALUES ({",".join(["%s"] * npw)})', rows)
    n = db.execute('SELECT COUNT(*) n FROM ws_strat_walk WHERE wsw_oobw=%s AND wsw_xwob=%s',
                   (oobw, xwob), fetch=True)[0]['n']
    print(f'ws_strat_walk: {len(rows)} rows offered, {n} in table at oobw {oobw} / xwob {xwob}')
    ung = [e for e in ev if not e['gated']]
    from collections import Counter
    print(f'GATE fence {FENCE} (outside [{FENCE},{100-FENCE}]) | lb {LB} bars = {LB*5}s')
    print(f'  {len(ung)} ungated / {len(ev)} signals ({len(ung)/24:.2f}/hr), {len(ev)-len(ung)} gated')
    print('  by clause: ' + '  '.join(f'{k or "GATED"}={v}' for k, v in
          sorted(Counter(e['by'] for e in ev).items(), key=lambda x: -x[1])))
    print(f"  ws1b_weaker_than_ws1Mage {sum(e['ws1b_weaker'] for e in ev)}")
    print(f"  ws1-exhausted {sum(e['exhausted'] for e in ev)}   "
          f"lookback found OOB {sum(e['lb_oob'] for e in ev)} / fence-only "
          f"{sum(e['lb_fence'] and not e['lb_oob'] for e in ev)}")

    if bars:
        brows, cand = write_bars(db, ts, V, pxs, evt, i0, len(ts), HI, LO, oobw, xwob, ev,
                                 (BLEN, BMULT, MLEN, MMULT))
        nb = db.execute('SELECT COUNT(*) n FROM ws_strat_bar WHERE wsb_oobw=%s AND wsb_xwob=%s',
                        (oobw, xwob), fetch=True)[0]['n']
        rej = [c for c in cand.values() if c['oob'] <= oobw and c['cross'] >= i0]
        print(f'ws_strat_bar : {len(brows)} rows offered, {nb} in table   '
              f'evt {int(evt[i0:].sum()):,} / filler {int((~evt[i0:]).sum()):,}')
        print(f'               {len([c for c in cand.values() if c["cross"] >= i0])} crossover '
              f'candidates in window: {len(ev)} passed the >{oobw} dwell gate, {len(rej)} REJECTED')
        if rej:
            print(f"               rejected oob_bars: min {min(c['oob'] for c in rej)} / "
                  f"median {int(np.median([c['oob'] for c in rej]))} / "
                  f"max {max(c['oob'] for c in rej)}")
    db.disconnect()

    if not ev:
        return rows
    w = max(len(x) for x in LINES)
    print(f"\n{'#':>3} {'cross_utc':<19} {'conf':<8} {'side':>4} {'oob_bars':>8} {'15s bucket':<19} "
          f"{'pxs':>9}  {'gate':<7} {'by':<7} {'exh':<3}")
    for i, r in enumerate(rows, 1):
        px = f'{r[21]:>9.5f}' if r[21] is not None else f'{"-":>9}'
        print(f'{i:>3} {r[3]:<19} {r[5][11:]:<8} {r[13]:>4} {r[14]:>8} {u(r[6]):<19} {px}'
              f"  {'GATED' if r[15] else 'ungated':<7} {r[16]:<7} {'EXH' if r[17] else '':<3}")
    print(f"\nline values at the CONFIRMATION bar\n{'#':>3} " + ' '.join(f'{n:>9}' for n in LINES))
    for i, r in enumerate(rows, 1):
        print(f'{i:>3} ' + ' '.join(f'{v:>9.2f}' for v in r[22:]))

    if pine:
        bkt = _Score(None).bucket_spans
        # PINE PAINTS ONLY THE SIGNALS THE ws1Mage+ws1b AND RELEASED (Joe 0810).
        #   Not the 361 raw, and not the 256 released overall — the 96 that the 19-bar ws1b lookback
        #   released on its own are EXCLUDED, because the lookback is a separate mechanic Joe is
        #   holding still while this one is worked on. wsw_gate_by names the release path, so the
        #   filter is exact rather than inferred.
        U = [r for r in rows if r[16] == 'ws1Mage+ws1b']
        hi_ts = bkt([r[2] for r in U if r[13] > 0], BUCKET_MS)
        lo_ts = bkt([r[2] for r in U if r[13] < 0], BUCKET_MS)
        streams = [{'name': 'oob_hi_x_ib', 'ts': hi_ts, 'color': 'color.red'},
                   {'name': 'oob_lo_x_ib', 'ts': lo_ts, 'color': 'color.green'}]
        notes = (f'ws_strat_walk | red = gcws30b crossed OOB(hi >= {HI:.0f}) -> IB | '
                 f'green = OOB(lo <= {LO:.0f}) -> IB'
                 f' | gcws30b = bb {BLEN}|{BMULT}|close @ 30s, emerging'
                 f' | OOB dwell > {oobw} bars of 5s (>= {(oobw + 1) * 5}s), one side, SURVIVES an IB'
                 f' excursion shorter than XWOB'
                 f' | cross confirmed by IB held XWOB {xwob} bars ({xwob * 5}s); the bar painted is the'
                 f' FIRST IB bar, floored onto its {BUCKET_MS // 1000}s seam'
                 f' | walk {u(ts[i0])} -> {u(ts[-1])}'
                 f' | PAINTS THE {len(U)} SIGNALS RELEASED BY ws1Mage+ws1b, of {len(rows)} total'
                 f' | GATE (Joe 0810): a gcws30 signal is BLOCKED unless ws1Mage is OOB AND ws1b is'
                 f' outside the [{FENCE},{100-FENCE}] fence. Blocked is the resting state — the lines'
                 f' only RELEASE.'
                 f' | NOT PAINTED: {sum(1 for e in ev if e["by"] == "lookback")} released by the'
                 f' {LB}-bar ws1b lookback alone (a separate mechanic, held still), and'
                 f' {sum(1 for e in ev if e["gated"])} that nothing released'
                 f' | CAUSAL: the event is knowable at cross+{xwob - 1} bars = +{(xwob - 1) * 5}s')
        total = _Score(None).emit_bgcolor(streams, PINE, 'ws_strat_walk — gcws30b OOB x IB (15s)',
                                          notes=notes)
        print(f'\n{PINE}  ->  {total} painted {BUCKET_MS//1000}s bars')
        print(f'  red   oob_hi_x_ib  {sum(1 for r in U if r[13] > 0):>3} events -> {len(hi_ts):>3} '
              f'distinct {BUCKET_MS//1000}s bars')
        print(f'  green oob_lo_x_ib  {sum(1 for r in U if r[13] < 0):>3} events -> {len(lo_ts):>3} '
              f'distinct {BUCKET_MS//1000}s bars')
        seam = sum(1 for r in U if r[2] % BUCKET_MS == 0)
        print(f'  {seam} of {len(U)} crossovers already sat on a {BUCKET_MS//1000}s seam; '
              f'{len(U) - seam} were floored back to the prior {BUCKET_MS//1000}s bar')
    return rows


if __name__ == '__main__':
    a = sys.argv
    main(oobw=int(a[a.index('--oobw') + 1]) if '--oobw' in a else OOBW,
         xwob=int(a[a.index('--xwob') + 1]) if '--xwob' in a else XWOB,
         pine='--no-pine' not in a, bars='--no-bars' not in a)
