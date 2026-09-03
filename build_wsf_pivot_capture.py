"""build_wsf_pivot_capture - the matrix and the report's derived readings, captured at price pivots.

Joe 0830: "do you think you would get value from capturing the wsf-model-report and the matrix at
the swings? there's a swing_detect(1%) tool that will show you the pivots - you could collect the
data at 1) each pivot, and 2) each pivot + 3 minutes".

WHY. Joe 0830, on what these rows are for: "we're not baking this as a self-validation-test - we're
using the pivots to learn what good looks like in our matrix and wsf-model-report. ie the pivots
are adding to our modelling data". They are NOT a scoring set. wsf_event_mark carries his verdict
on what the walk declared; this carries what the board looked like where price actually turned,
including the turns the walk said nothing about.

HIS RULINGS, 0830, one per concretion:
  C1 the threshold  "1.0 is fine. this pivot data collection isn't part of the wsf or dtf mechs -
                    it's an external modelling tool. I would say there's no need to have a knob"
  C2 the matrix     "yes - use the current matrix format that you built earlier" - 12 lines x 24
                    samples, 48 minutes back at a 2-minute step
  C3 both dr boards "agreed - it gives you an idea of what not-good looks like"
  C4 before too     "before and after is a good idea - agreed"
  C5 the dr         "use the pivot to set the dr in the model (eg high pivot = dr +1)"
  E2 the report     confirmed: bank heading, extrema r, extrema dwell and the bar state - the four
                    things report_wsf_bar.py DERIVES and nothing banks

AND HIS CAUTION, which is why nothing here matches timestamps between the two sets:
  "when you compare the real turns, you'll need to be kind to yourself - the timestamps won't
   exactly match"

MINE, STATED, four:
  the pivot price series is px_smooth, not raw price. linelab.py:182 runs find_pivots(epx, pct) on
    px_smooth event bars and its mae() already defaults pct=1.0. Any other basis would put these
    pivots on a different footing from every MAE measurement in the repo.
  the `before` offset is -3 minutes, symmetric with Joe's +3. Three captures per pivot.
  a capture whose 48-minute window runs off the front of the day is still written - the samples
    that exist are written and the missing ones are simply absent rows. Truncating the window
    silently would be a cap Joe never asked for.
  the knob signature of the LINE CACHE is on every row. The r values come from wsf_line_bar and a
    row is meaningless without knowing which build produced it.

NOTHING IS DELETED. A re-run at the same (knobs, day) is refused rather than replaced.
"""
import datetime as dt
import os
import sys
import numpy as np
from collections import defaultdict
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.swing_detect import find_pivots
from optimus9.orchestration.rpl_cache import TAPE_DIR, _tape_key
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from build_wsf_walk_events import KNOBS, MAX_TF
from report_wsf_bar import heading, MOMO_STALL_DELAY

DAYS = ['2026-08-01', '2026-08-02', '2026-08-03', '2026-08-04',
        '2026-08-05', '2026-08-06', '2026-08-07', '2026-08-08']
PIVOT_PCT = 1.0        # Joe 0830: "1.0 is fine ... no need to have a knob"
GRID = 5               # seconds per bar
WINDOW_MIN = 48        # the matrix lookback, Joe 0829
STEP_MIN = 2           # the matrix step, Joe 0829
OFFSETS = [(-180, 'before'), (0, 'pivot'), (180, 'after')]   # Joe 0830: before, at, after

DDL_CAP = '''CREATE TABLE IF NOT EXISTS wsf_pivot_capture (
    wpc_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wpc_knobs     VARCHAR(160) NOT NULL,  -- the LINE CACHE signature the r values came from
    wpc_day       DATE     NOT NULL,
    wpc_created   DATETIME NOT NULL,
    wpc_pivot_utc DATETIME NOT NULL,      -- the bar find_pivots named, on px_smooth at 1.0%
    wpc_kind      CHAR(1)  NOT NULL,      -- H = a high pivot, L = a low
    wpc_pivot_dr  TINYINT  NOT NULL,      -- Joe 0830 C5: high pivot = dr +1
    wpc_pivot_pxs DOUBLE,                 -- px_smooth at the pivot bar
    wpc_offset_s  INT      NOT NULL,      -- -180, 0, +180
    wpc_offset    VARCHAR(8) NOT NULL,    -- before | pivot | after
    wpc_utc       DATETIME NOT NULL,      -- the capture bar = pivot + offset
    UNIQUE KEY uq_wpc (wpc_knobs, wpc_pivot_utc, wpc_offset_s),
    KEY ix_wpc_day (wpc_day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

DDL_CELL = '''CREATE TABLE IF NOT EXISTS wsf_pivot_matrix (
    wpm_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wpm_cap_pk    BIGINT   NOT NULL,      -- FK -> wsf_pivot_capture.wpc_pk
    wpm_dr        TINYINT  NOT NULL,      -- BOTH boards are stored, Joe 0830 C3
    wpm_tf        SMALLINT NOT NULL,      -- ws1 to ws12
    wpm_sample    SMALLINT NOT NULL,      -- 0 = the capture bar, 1..23 = further back
    wpm_utc       DATETIME NOT NULL,
    wpm_r         DOUBLE,
    wpm_verdict   VARCHAR(10),
    UNIQUE KEY uq_wpm (wpm_cap_pk, wpm_dr, wpm_tf, wpm_sample),
    KEY ix_wpm_cap (wpm_cap_pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

DDL_READ = '''CREATE TABLE IF NOT EXISTS wsf_pivot_read (
    wpr_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wpr_cap_pk    BIGINT   NOT NULL,      -- FK -> wsf_pivot_capture.wpc_pk
    wpr_dr        TINYINT  NOT NULL,      -- the pivot's own dr, Joe 0830 C5
    wpr_tf        SMALLINT NOT NULL,
    wpr_r         DOUBLE,
    wpr_verdict   VARCHAR(10),
    wpr_heading   VARCHAR(8),             -- toward | away, Joe 0829's definition
    wpr_extrema_r DOUBLE,                 -- the true extreme of the current cycle
    wpr_extrema_dwell_s INT,              -- seconds since that extreme
    wpr_stalled   TINYINT,
    wpr_mfr_out   TINYINT,                -- outside momo-fence-r
    wpr_state     VARCHAR(24),            -- the bar state the report prints
    UNIQUE KEY uq_wpr (wpr_cap_pk, wpr_tf),
    KEY ix_wpr_cap (wpr_cap_pk)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    for d in (DDL_CAP, DDL_CELL, DDL_READ):
        db.execute(d)

    s = db.execute('SELECT pxsmooth_dema_src src, pxsmooth_dema_len len FROM optimus9_system '
                   'WHERE sys_pk=1', fetch=True)[0]
    tape = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                                                    {'src': s['src'], 'len': s['len']}) + '.npz'))
    ts, pxs = tape['__ts__'], tape['__pxs__']
    print(f'  tape {len(ts):,} bars   pivots on px_smooth at {PIVOT_PCT}%\n', flush=True)

    nsamp = WINDOW_MIN // STEP_MIN                 # 24
    step_bars = STEP_MIN * 60 // GRID              # 24 bars = 2 minutes
    tot_cap = tot_cell = tot_read = 0
    for day in DAYS:
        d0 = int(dt.datetime.fromisoformat(day + ' 00:00:00').timestamp() * 1000)
        d1 = d0 + 86400 * 1000
        i0, i1 = int(np.searchsorted(ts, d0)), int(np.searchsorted(ts, d1))
        if i1 <= i0:
            print(f'  {day}   no tape bars, skipped', flush=True); continue

        # THE LINE CACHE for this day, at the live signature. No cache, no captures.
        L = defaultdict(dict)
        for x in db.execute('SELECT wflb_utc t, wflb_tf tf, wflb_dr dr, wflb_r r, wflb_verdict v, '
                            'wflb_stalled st, wflb_mfr_out m FROM wsf_line_bar '
                            'WHERE wflb_knobs=%s AND wflb_tf<=%s AND wflb_utc >= %s AND wflb_utc < %s',
                            (KNOBS, MAX_TF, day + ' 00:00:00',
                             (dt.date.fromisoformat(day) + dt.timedelta(days=1)).isoformat()
                             + ' 00:00:00'), fetch=True):
            L[str(x['t'])][(int(x['dr']), int(x['tf']))] = x
        if not L:
            print(f'  {day}   NO LINE CACHE at these knobs, skipped', flush=True); continue
        have = db.execute('SELECT COUNT(*) c FROM wsf_pivot_capture WHERE wpc_knobs=%s AND wpc_day=%s',
                          (KNOBS, day), fetch=True)[0]['c']
        if have:
            print(f'  {day}   {have} captures already banked - REFUSING to rewrite. '
                  f'Joe 0827: "no deletes"', flush=True); continue

        piv = find_pivots(pxs[i0:i1], PIVOT_PCT)
        created = db.execute('SELECT NOW() n', fetch=True)[0]['n']
        nc = ncell = nread = 0
        for idx, kind in piv:
            g = i0 + int(idx)
            if not (i0 <= g < i1):
                continue
            ptime = dt.datetime.utcfromtimestamp(int(ts[g]) / 1000)
            pdr = 1 if kind == 'H' else -1        # Joe 0830 C5
            for off_s, off_name in OFFSETS:
                b = g + off_s // GRID
                if b < 0 or b >= len(ts):
                    continue
                btime = dt.datetime.utcfromtimestamp(int(ts[b]) / 1000)
                bkey = btime.strftime('%Y-%m-%d %H:%M:%S')
                if bkey not in L:
                    continue
                db.execute('INSERT INTO wsf_pivot_capture (wpc_knobs,wpc_day,wpc_created,'
                           'wpc_pivot_utc,wpc_kind,wpc_pivot_dr,wpc_pivot_pxs,wpc_offset_s,'
                           'wpc_offset,wpc_utc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                           (KNOBS, day, created, ptime, kind, pdr,
                            float(pxs[g]) if np.isfinite(pxs[g]) else None,
                            off_s, off_name, btime))
                cap = db.execute('SELECT wpc_pk p FROM wsf_pivot_capture WHERE wpc_knobs=%s '
                                 'AND wpc_pivot_utc=%s AND wpc_offset_s=%s',
                                 (KNOBS, ptime, off_s), fetch=True)[0]['p']
                nc += 1
                # THE MATRIX - both dr boards, 12 lines, 24 samples back at a 2-minute step
                cells = []
                for k in range(nsamp):
                    sb = b - k * step_bars
                    if sb < 0:
                        break
                    skey = dt.datetime.utcfromtimestamp(int(ts[sb]) / 1000
                                                        ).strftime('%Y-%m-%d %H:%M:%S')
                    row = L.get(skey)
                    if not row:
                        continue
                    for dr in (1, -1):
                        for tf in range(1, MAX_TF + 1):
                            z = row.get((dr, tf))
                            if z is None:
                                continue
                            cells.append((cap, dr, tf, k, skey, float(z['r']), z['v']))
                if cells:
                    db.executemany('INSERT INTO wsf_pivot_matrix (wpm_cap_pk,wpm_dr,wpm_tf,'
                                   'wpm_sample,wpm_utc,wpm_r,wpm_verdict) '
                                   'VALUES (%s,%s,%s,%s,%s,%s,%s)', cells)
                    ncell += len(cells)
                # THE REPORT'S DERIVED READINGS at the pivot's own dr, E2
                reads = _reads(L, ts, b, bkey, pdr, cap)
                if reads:
                    db.executemany('INSERT INTO wsf_pivot_read (wpr_cap_pk,wpr_dr,wpr_tf,wpr_r,'
                                   'wpr_verdict,wpr_heading,wpr_extrema_r,wpr_extrema_dwell_s,'
                                   'wpr_stalled,wpr_mfr_out,wpr_state) '
                                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', reads)
                    nread += len(reads)
        print(f'  {day}   {len(piv):>3} pivots   {nc:>4} captures   {ncell:>7,} matrix cells   '
              f'{nread:>4} report reads', flush=True)
        tot_cap += nc; tot_cell += ncell; tot_read += nread
    print(f'\n  wsf_pivot_capture : {tot_cap:,} rows')
    print(f'  wsf_pivot_matrix  : {tot_cell:,} rows')
    print(f'  wsf_pivot_read    : {tot_read:,} rows')
    db.disconnect()
    return 0


def _reads(L, ts, b, bkey, dr, cap):
    """heading, extrema r, extrema dwell and the bar state - the four the report derives.

    The extrema cycle runs from the line's last momentum-true bar to this bar, exactly as
    report_wsf_bar.extrema() does, and the hold is counted ELAPSE per Joe 0829."""
    board = {tf: L[bkey].get((dr, tf)) for tf in range(1, MAX_TF + 1)}
    if not any(board.values()):
        return []
    mom = {tf for tf, z in board.items() if z is not None and z['v'] in ('momo', 'curl')}
    hi = sorted(t for t in mom if t >= 4); lo = sorted(t for t in mom if t <= 3)
    state = 'wsf-momoc' if (hi or lo) else 'wsf-exhaust'
    keys = sorted(L)
    j = keys.index(bkey)
    out = []
    for tf in range(1, MAX_TF + 1):
        z = board.get(tf)
        if z is None:
            continue
        start = 0
        for k in range(j, -1, -1):
            zz = L[keys[k]].get((dr, tf))
            if zz is not None and zz['v'] in ('momo', 'curl'):
                start = k; break
        seg = [(keys[k], L[keys[k]].get((dr, tf))) for k in range(start, j + 1)]
        seg = [(t, z2) for t, z2 in seg if z2 is not None]
        if not seg:
            continue
        pick = min(seg, key=lambda q: float(q[1]['r'])) if dr < 0 \
            else max(seg, key=lambda q: float(q[1]['r']))
        dwell = int((dt.datetime.fromisoformat(bkey)
                     - dt.datetime.fromisoformat(pick[0])).total_seconds())
        ex, held, turned = None, 0, False
        for _t, z2 in seg:
            r = float(z2['r'])
            if ex is None or (r < ex if dr < 0 else r > ex):
                ex, held, turned = r, 0, False; continue
            if turned or ((r > ex) if dr < 0 else (r < ex)):
                turned = True; held += 1
        h = heading(dr, held, float(pick[1]['r']), z['v'] in ('momo', 'curl'))
        out.append((cap, dr, tf, float(z['r']), z['v'], h, float(pick[1]['r']), dwell,
                    int(z['st'] or 0), int(z['m'] or 0), state))
    return out


if __name__ == '__main__':
    sys.exit(main())
