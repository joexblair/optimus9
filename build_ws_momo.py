"""build_ws_momo — the momo-TF study, banked per 5 s bar. Joe 0806.

QUESTION (Joe): find the highest momo TF that matches our 1.11%-sized swings. Too high a TF and the
ws{TF}r line's momentum overshoots the swing, so the walk misses trades.

METHOD (Joe 0806), verbatim:
    -for each swing:
    --identify the r line(s) that cross oob just before the 1.11 pivot
    --then look back to see if momo produced a same-side `momo` or `curl`
    ---the lookback uses the ws1 events as markers - only test for momo/curl on a ws1 `cadence
       marker`. this matches how the walk will behave when it is testing for momentum

CONCRETIONS, as answered by Joe 0806:
    swing series      pxs (px_smooth), NOT close. close gives 20 pivots at 1.11%, pxs gives 18.
    "just before"     JOE'S REFERENCE: ws18r/ws17r qualify at the 08-04 19:44:20 pivot, ws16r is too
                      early. Measured leads: 11.2 / 14.4 min qualify, 57.0 min rejects, and NOTHING
                      lands between 15.2 and 40.3 min. JUST_BEFORE_MIN 30 sits inside that empty
                      band, so the verdict is invariant anywhere in 16..40 for that pivot. MY pick
                      from inside the gap, not a measured optimum.
    cadence marker    a ws1Mage OR ws1b OOB->IB crossing — "the things the current gate already
                      reads". Stamped at the CONFIRMATION bar (cross + XWOB-1), so a marker is only
                      used at the bar it becomes knowable.
    momo direction    dr = the SIDE of the r line's OOB cross (+1 at an H pivot, -1 at an L), from
                      Joe's "same-side momo or curl". NOT the trade's bias.
    lookback end      Joe: "if it's a bear bias, look back until the in-test r line is >60. inverse
                      for bull". Walking BACK from the pivot the r line descends off its OOB high, so
                      the lookback CONTINUES while r is beyond the level and STOPS once it is not:
                      bear (H pivot) stops when r <= 60, bull (L) stops when r >= 40. 40 is the
                      mirror of 60 about the 50 midline — MY reading of "inverse".
                      FIRST BUILD HAD THIS INVERTED (stop when r > 60), which fires on the very first
                      marker at an H pivot because r is already high there — 98 of 98 qualifying rows
                      tested exactly one marker and momo was never really evaluated.

TABLES, same per-5s mentality as ws_strat_bar:
    ws_momo_bar   one row per 5 s bar: pxs, pivot flag, cadence-marker flag, and all 57 r lines
    ws_momo       one row per (pivot, TF): the r's OOB crossing, and the momo/curl found in lookback

    python3 build_ws_momo.py [--rebuild]

--rebuild forces the line arrays to recompute. REQUIRED after any kline_collection repair: the
cache key is (end_ms, hours, warmup, line-spec) and does NOT include the kline content, so a
repaired tape silently reuses the old arrays without it.
"""
import datetime as dt
from datetime import timezone
import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, KLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.compute.swing_detect import find_pivots
from optimus9.analysis.jig import oob_ib_cross
from optimus9.compute.momo_gated import momo_g, CURL_R2_MIN

HI, LO = 85., 15.
TFS = list(range(4, 61))          # Joe: momo_tf = [4 to 60] minutes
R_SPEC = dict(k_len=7, rsi=5, stc=8, src='close')   # "same config as the current r lines"
SWING_PCT = 1.11
JUST_BEFORE_MIN = 30              # see the docstring — my pick from inside the 15.2..40.3 empty band
XWOB = 2                          # cadence-marker confirmation hold, in 5 s bars
STOP_HI, STOP_LO = 60.0, 40.0     # lookback ends when the in-test r passes these
START = dt.datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)   # -> cache end 08-09 12:00 = 5 days
RCOLS = [f'wmb_r{t}' for t in TFS]
u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

BAR_DDL = '''CREATE TABLE IF NOT EXISTS ws_momo_bar (
    wmb_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    wmb_ms       BIGINT NOT NULL, wmb_utc VARCHAR(19),
    wmb_evt      TINYINT NOT NULL,          -- a traded bar (volume > 0)
    wmb_pxs      DOUBLE,                    -- px_smooth, the series the pivots are found on
    wmb_pivot    TINYINT NOT NULL,          -- 1 = a 1.11% swing pivot sits on this bar
    wmb_pivot_kind CHAR(1),                 -- H | L
    wmb_marker   TINYINT NOT NULL,          -- 1 = a ws1 cadence marker confirms here
    wmb_marker_src VARCHAR(16),             -- which ws1 line(s) produced it
    ''' + ',\n    '.join(f'{c:<10} DOUBLE' for c in RCOLS) + ''',
    UNIQUE KEY uq_wmb (wmb_ms), KEY (wmb_pivot), KEY (wmb_marker))'''

EV_DDL = '''CREATE TABLE IF NOT EXISTS ws_momo (
    wm_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wm_swing_pct DECIMAL(6,3) NOT NULL,     -- the swing_detect value the pivots came from
    wm_just_before SMALLINT NOT NULL,       -- minutes: how far before the pivot an OOB cross counts
    wm_tf        SMALLINT NOT NULL,         -- the ws{TF}r under test, minutes
    wm_pivot_ms  BIGINT NOT NULL, wm_pivot_utc VARCHAR(19),
    wm_pivot_kind CHAR(1) NOT NULL,         -- H = bear bias (dr -1) | L = bull (dr +1)
    wm_pivot_px  DOUBLE,
    wm_oob_ms    BIGINT, wm_oob_utc VARCHAR(19),   -- the r's IB->OOB cross, NULL if none in window
    wm_oob_lead_min DOUBLE,                 -- minutes it leads the pivot
    wm_r_at_oob  DOUBLE, wm_r_at_pivot DOUBLE,
    wm_qualifies TINYINT NOT NULL,          -- 1 = that cross is inside wm_just_before
    wm_momo_ms   BIGINT, wm_momo_utc VARCHAR(19),  -- the cadence marker momo/curl was found at
    wm_momo_state VARCHAR(8),               -- momo | curl | NULL
    wm_momo_lead_min DOUBLE,                -- minutes that marker leads the pivot
    wm_momo_slope DOUBLE, wm_momo_r2 DOUBLE, wm_momo_r DOUBLE,
    wm_markers_tested SMALLINT,             -- cadence markers walked before the lookback ended
    wm_stop_ms   BIGINT,                    -- where the lookback stopped (r past 60 / 40)
    wm_near_mk_ms BIGINT, wm_near_mk_utc VARCHAR(19),  -- the ws1 cadence marker CLOSEST to the pivot
    wm_near_mk_lead_min DOUBLE,             -- minutes that marker leads (+) or trails (-) the pivot
    wm_momo_to_mk_min DOUBLE,               -- |momo marker - nearest marker|, minutes. Joe 0808 ranks
    --                                         the TFs on this: the 2 smallest are the TFs whose
    --                                         momentum fires at the marker the walk would be testing
    --                                         at the pivot. A large value = that TF fired early and
    --                                         overshoots the swing.
    UNIQUE KEY uq_wm (wm_swing_pct, wm_just_before, wm_tf, wm_pivot_ms),
    KEY (wm_tf), KEY (wm_pivot_ms), KEY (wm_momo_state))'''


def main(rebuild=False):
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',
                      fetch=True)[0]
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in ('ws1Mage', 'ws1b')}
    for tf in TFS:
        ovr[f'r{tf}'] = override(tf * 60, KLine(**R_SPEC), 'emerging')
    print(f'building/loading {len(ovr)} lines ...', flush=True)
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg={'src': sysr['s'], 'len': sysr['l']},
                          rebuild=rebuild)
    ts = np.asarray(J.ts); pxs = np.asarray(J.pxs, float); evt = np.asarray(J.evt, bool)
    V = {n: np.asarray(J.W.line(n), float) for n in ovr}
    i0 = int(np.searchsorted(ts, int(START.timestamp() * 1000)))

    PV = [(i, k) for i, k in find_pivots(pxs, SWING_PCT) if i >= i0]
    MK = {}
    for nm in ('ws1Mage', 'ws1b'):
        for (_, c, _) in oob_ib_cross(V[nm], HI, LO, XWOB):      # stamp at the CONFIRMATION bar
            if c >= i0:
                MK.setdefault(c, []).append(nm)
    mk = np.array(sorted(MK))
    print(f'{len(PV)} pivots at {SWING_PCT}%   {len(mk)} ws1 cadence markers   window {u(ts[i0])} -> {u(ts[-1])}')

    def ib_to_oob(v, side):
        o = (v >= HI) if side > 0 else (v <= LO)
        return np.flatnonzero(o & ~np.r_[False, o[:-1]])

    rows = []
    for pi, kind in PV:
        side = 1 if kind == 'H' else -1              # H = price topped: r goes hi. L = r goes lo.
        dr = side                                    # SAME SIDE as the OOB cross (Joe: "same-side
        #                                              momo or curl"). At an H pivot the r line went
        #                                              OOB-hi, so dr +1. Joe's "bear bias" names the
        #                                              LOOKBACK TERMINUS, not momo's direction.
        #                                              FIRST FIX USED dr = -side: momo's level gate at
        #                                              dr -1 wants r <= 50+slack (<=63.9 at most),
        #                                              while the lookback holds r > 60 — near
        #                                              mutually exclusive, so 0 hits in 98 pairs.
        stop = (lambda x: x <= STOP_HI) if kind == 'H' else (lambda x: x >= STOP_LO)
        pms = int(ts[pi])
        # the ws1 cadence marker CLOSEST to the pivot, either side (Joe 0808). This is the marker the
        # walk would be testing momentum at when the swing turns; the TFs whose momo fires nearest it
        # are the ones matched to the swing's size.
        nmk = int(mk[np.abs(mk - pi).argmin()]) if len(mk) else None
        nmk_ms = int(ts[nmk]) if nmk is not None else None
        nmk_lead = (pms - nmk_ms) / 60000 if nmk_ms is not None else None
        for tf in TFS:
            v = V[f'r{tf}']
            c = ib_to_oob(v, side); c = c[c <= pi]
            oob = int(c[-1]) if len(c) else None
            lead = (pms - int(ts[oob])) / 60000 if oob is not None else None
            qual = 1 if (lead is not None and lead <= JUST_BEFORE_MIN) else 0
            m_ms = m_st = m_sl = m_r2 = m_rv = m_lead = None; tested = 0; stop_ms = None
            if qual:
                for w in mk[mk <= pi][::-1]:          # cadence markers, walking BACK from the pivot
                    tested += 1
                    if stop(v[w]):
                        stop_ms = int(ts[w]); break
                    st, sl, r2, rw = momo_g(v, dr, int(w))
                    if st in ('momo', 'curl'):
                        m_ms, m_st, m_sl, m_r2, m_rv = int(ts[w]), st, float(sl), float(r2), float(rw)
                        m_lead = (pms - m_ms) / 60000
                        break
            m2mk = abs(m_ms - nmk_ms) / 60000 if (m_ms is not None and nmk_ms is not None) else None
            rows.append((SWING_PCT, JUST_BEFORE_MIN, tf, pms, u(pms), kind, float(pxs[pi]),
                         int(ts[oob]) if oob is not None else None,
                         u(ts[oob]) if oob is not None else None, lead,
                         float(v[oob]) if oob is not None else None, float(v[pi]), qual,
                         m_ms, u(m_ms) if m_ms else None, m_st, m_lead, m_sl, m_r2, m_rv,
                         tested, stop_ms, nmk_ms, u(nmk_ms) if nmk_ms else None, nmk_lead, m2mk))
        print(f"  pivot {u(pms)} {kind} done", flush=True)

    db.execute(EV_DDL)
    db.execute('DELETE FROM ws_momo WHERE wm_swing_pct=%s AND wm_just_before=%s',
               (SWING_PCT, JUST_BEFORE_MIN))
    cols = ('wm_swing_pct,wm_just_before,wm_tf,wm_pivot_ms,wm_pivot_utc,wm_pivot_kind,wm_pivot_px,'
            'wm_oob_ms,wm_oob_utc,wm_oob_lead_min,wm_r_at_oob,wm_r_at_pivot,wm_qualifies,'
            'wm_momo_ms,wm_momo_utc,wm_momo_state,wm_momo_lead_min,wm_momo_slope,wm_momo_r2,'
            'wm_momo_r,wm_markers_tested,wm_stop_ms,wm_near_mk_ms,wm_near_mk_utc,'
            'wm_near_mk_lead_min,wm_momo_to_mk_min')
    db.executemany(f'INSERT INTO ws_momo ({cols}) VALUES '
                   f'({",".join(["%s"] * len(cols.split(",")))})', rows)
    print(f'ws_momo: {len(rows)} rows')

    pk = {i: k for i, k in PV}
    brows = []
    for i in range(i0, len(ts)):
        brows.append([int(ts[i]), u(ts[i]), int(evt[i]),
                      None if not np.isfinite(pxs[i]) else float(pxs[i]),
                      1 if i in pk else 0, pk.get(i),
                      1 if i in MK else 0, '+'.join(MK[i]) if i in MK else None]
                     + [None if not np.isfinite(V[f'r{t}'][i]) else float(V[f'r{t}'][i]) for t in TFS])
    db.execute(BAR_DDL)
    db.execute('DELETE FROM ws_momo_bar')
    bc = ('wmb_ms,wmb_utc,wmb_evt,wmb_pxs,wmb_pivot,wmb_pivot_kind,wmb_marker,wmb_marker_src,'
          + ','.join(RCOLS))
    db.executemany(f'INSERT INTO ws_momo_bar ({bc}) VALUES '
                   f'({",".join(["%s"] * len(bc.split(",")))})', brows)
    print(f'ws_momo_bar: {len(brows)} rows, {len(RCOLS)} r-line columns')
    db.disconnect()


if __name__ == '__main__':
    import sys
    main(rebuild='--rebuild' in sys.argv)
