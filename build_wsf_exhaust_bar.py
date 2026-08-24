"""build_wsf_exhaust_bar — Joe's estimated exhaust times turned into proven bars. Joe 0821.

Joe gave 37 exhaust events by eye, timed to the MINUTE, in
transfer/0804_wsf-exhaust_timestamps.csv. A minute is 12 bars at the 5-second grid, so every
measurement taken at an estimate counted 12 bars as the event when only one of them is.

Joe 0821, the two methods, verbatim:

    let's turn my estimates into proven times. there's 2 methods
    --if x-cross_forced is yes, then the wsf-exhaust event happens when x crosses r
    --if there is no x-cross, walk the bars leading up to my estimated time (eg walk from a
      timestamp that is 8 minutes earlier than my estimate), and capture the moment when the
      momentum tagged line exits the fence

BOTH MOMENTS ARE BANKED, raw and held, because they answer different questions:
    wxb_raw_utc   the bar the crossing or the exit actually happened
    wxb_conf_utc  the bar it CONFIRMED, after its xwob hold - the first bar it is actionable
For an x-cross the hold is XCROSS_XWOB 5 (20 s); for a fence exit it is MOMO_XWOB 4 (15 s).

TWO DEFECTS FOUND 0822 AND FIXED HERE. Joe: "let's clean that up".

  DEFECT A, the fence-exit CONFIRMED bar. `wflb_mfr_xwob` is Jig.cross_wob's output shape -
  CONFIRMED-IN-EFFECT, true on every bar of the run, not just the first. jig._Causal.cross_wob says
  it in its own docstring: "the consumer takes the RISING EDGE for the confirmation moment". This
  script took the confirmed bar NEAREST Joe's estimate instead, so on a long run it landed deep
  inside it. 00:49 read 00:49:00 when ws8r confirms at 00:48:15 - 45 s late. Now selects on
  `wflb_mfr_run = MOMO_XWOB`, which is the rising edge: the run counter passes 4 on exactly one bar.

  DEFECT B, the x-cross RAW bar. The confirmed bar at XCROSS_XWOB 5 already IS a rising edge -
  build_wsf_x_cross's hold latches `fired` - so the conf side was right. The raw lookup was not: it
  took the latest xwob-0 crossing of ANY target at or before conf, not the target that actually won.
  At 16:55 the boundary cross confirmed at 16:59:15 while a Mage/b/r cross fired at the same bar at
  xwob 0, so raw == conf and the 20 s hold vanished. Now matched on `wxc_race_won`.

THE SEARCH WINDOW is 8 minutes, Joe's own number from method 2, applied to both methods. The search
runs from 8 minutes before the estimate to the end of the estimated minute, and takes the LAST
qualifying event in that window - the one closest to what Joe saw.

WHICH LINE. The CSV's TF column names the TRIGGER - the line that exited the fence or stalled. It
is NOT the line the cross happens on. Joe 0821: "your walk isn't applying the mechanisms: you should
be looking for the cross in weak-make-tf, not the 'highest TF carrying momentum' TF".

    the x-cross method   reads ws{weak-mage-tf}x, where weak-mage-tf is read AT THE CROSSING BAR.
                         A crossing only counts if the line that crossed IS the weak-mage-tf on that
                         bar, which is what the walk would be watching at that instant.
    the fence-exit method reads ws{TF}r against momo-fence-r - the trigger line, as Joe specified:
                         "capture the moment when the momentum tagged line exits the fence".

THE TOLERANCE is 7 minutes either side of the estimate. Joe 0821: "use a -7 / +7 (minutes) tolerance
when matching my estimates". The first cut searched 8 minutes BACK and 55 seconds forward, which is
how 03:22 was missed - its crossing is at +45 s.

WHEN SEVERAL QUALIFY, the one CLOSEST to the start of Joe's estimated minute is taken.
"""
import sys
import csv
import datetime as dt

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WIN_FROM   = '2026-08-04 00:00:00'
CSV        = '/home/joe/thecodes/transfer/0804_wsf-exhaust_timestamps.csv'
TOL_MIN    = 7          # Joe 0821: "use a -7 / +7 (minutes) tolerance when matching my estimates"
XCROSS_XWOB = 5         # the x-cross hold, build_wsf_x_cross.py
MOMO_XWOB   = 4         # the fence-exit hold, build_wsf_line_bar.py
WON_COL = {'Mage': 'wxc_x_mage', 'b': 'wxc_x_b', 'boundary': 'wxc_x_bound'}   # DEFECT B
KNOBS = 'kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4'

DDL = '''CREATE TABLE IF NOT EXISTS wsf_exhaust_bar (
    wxb_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wxb_win_from   DATETIME NOT NULL,
    wxb_tol_min    SMALLINT NOT NULL,   -- KNOB. minutes either side of the estimate. 7
    wxb_wm_tf      SMALLINT,            -- the weak-mage-tf AT THE LOCATED BAR. Filled on EVERY row,
    --   both methods. The x-cross method SEARCHES by it; the fence-exit method locates the bar by
    --   the trigger line and then reads it. It is a property of the board at that bar either way,
    --   and the trade signal that follows needs it regardless of how the exhaust was found.
    wxb_est        VARCHAR(8) NOT NULL, -- Joe's estimate, as he wrote it. HH:MM
    wxb_tf         VARCHAR(8) NOT NULL, -- the timeframe he named. "1or2" on one row
    wxb_dr         TINYINT NOT NULL,    -- the direction he named
    wxb_method     VARCHAR(12) NOT NULL,-- which of Joe's two methods was used
    wxb_raw_utc    DATETIME,            -- the bar the crossing or the exit HAPPENED
    wxb_conf_utc   DATETIME,            -- the bar it CONFIRMED, after its xwob hold
    wxb_offset_s   INT,                 -- seconds from the start of Joe's estimated minute to raw
    wxb_found      TINYINT NOT NULL,    -- 0 = nothing qualifying inside the search window
    wxb_elif       TINYINT NOT NULL,    -- 1 = the estimate came from Joe's ELIF_time column
    wxb_note       VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE KEY uq_wxb (wxb_win_from, wxb_tol_min, wxb_est, wxb_tf, wxb_dr),
    KEY k_raw (wxb_raw_utc), KEY k_found (wxb_found))'''

COLS = ['wxb_win_from', 'wxb_tol_min', 'wxb_wm_tf', 'wxb_est', 'wxb_tf', 'wxb_dr', 'wxb_method',
        'wxb_raw_utc', 'wxb_conf_utc', 'wxb_offset_s', 'wxb_found', 'wxb_elif', 'wxb_note']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    ev = []
    with open(CSV, encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            t = (r['ELIF_time_estimated'] or '').strip()
            elif_used = t not in ('', 'null')
            est = t if elif_used else r['ESTIMATED'].strip()
            ev.append(dict(est=est, tf=r['TF'].strip(), dr=int(r['dr']),
                           forced=(r['x-cross_forced_wsf-exhaust'] or '').strip().lower() == 'yes',
                           elif_used=elif_used, note=(r['notes'] or '').strip()[:255]))
    print(f'  {len(ev)} events from the CSV', flush=True)

    db.execute(DDL)
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_exhaust_bar', fetch=True)}
    if 'wxb_tol_min' not in have:
        db.execute('ALTER TABLE wsf_exhaust_bar ADD COLUMN wxb_tol_min SMALLINT NOT NULL DEFAULT 0')
        db.execute('ALTER TABLE wsf_exhaust_bar ADD COLUMN wxb_wm_tf SMALLINT')
        db.execute('ALTER TABLE wsf_exhaust_bar DROP INDEX uq_wxb, ADD UNIQUE KEY uq_wxb '
                   '(wxb_win_from, wxb_tol_min, wxb_est, wxb_tf, wxb_dr)')
        print('  added wxb_tol_min and wxb_wm_tf, rebuilt the unique key', flush=True)
    where = 'wxb_win_from=%s AND wxb_tol_min=%s'
    kv = (WIN_FROM, TOL_MIN)
    n = db.execute('SELECT COUNT(*) c FROM wsf_exhaust_bar WHERE ' + where, kv, fetch=True)[0]['c']
    if n:
        print(f'  deleting {n} rows already stored at this search window', flush=True)
        db.execute('DELETE FROM wsf_exhaust_bar WHERE ' + where, kv)

    rows = []
    for e in ev:
        h, m = e['est'].split(':')[:2]
        anchor = dt.datetime(2026, 8, 4, int(h), int(m), 0)
        s0 = (anchor - dt.timedelta(minutes=TOL_MIN)).strftime('%Y-%m-%d %H:%M:%S')
        t0 = (anchor + dt.timedelta(minutes=TOL_MIN)).strftime('%Y-%m-%d %H:%M:%S')
        raw = conf = wm = None
        method = 'x-cross' if e['forced'] else 'fence exit'
        if not e['tf'].isdigit():
            rows.append((WIN_FROM, TOL_MIN, None, e['est'], e['tf'], e['dr'], method,
                         None, None, None, 0, int(e['elif_used']),
                         'TF is not a single number - no trigger line to read'))
            continue
        tf = int(e['tf'])
        if e['forced']:
            # THE CROSS IS ON ws{weak-mage-tf}x, and the weak-mage-tf is read AT THE CROSSING BAR.
            c = db.execute("""SELECT x.wxc_utc u, x.wxc_tf tf, x.wxc_race_won won,
                     ABS(TIMESTAMPDIFF(SECOND, %s, x.wxc_utc)) gap
                   FROM wsf_x_cross x
                   JOIN wsf_bar_tf b ON b.wbt_win_from=%s AND b.wbt_wmt_tf_lo=2
                        AND b.wbt_utc=x.wxc_utc AND b.wbt_dr=x.wxc_dr AND b.wbt_tf=2
                  WHERE x.wxc_win_from=%s AND x.wxc_xwob=%s AND x.wxc_dr=%s AND x.wxc_race=1
                    AND x.wxc_utc BETWEEN %s AND %s
                    AND b.wbt_weak_mage_tf = x.wxc_tf
                  ORDER BY gap LIMIT 1""",
                (anchor.strftime('%Y-%m-%d %H:%M:%S'), WIN_FROM, WIN_FROM,
                 XCROSS_XWOB, e['dr'], s0, t0), fetch=True)
            if c:
                conf = c[0]['u']; wm = int(c[0]['tf'])
                # DEFECT B. The raw crossing must be the SAME TARGET that won at the confirmed bar.
                # wxc_race_won names it; each target has its own flag column at xwob 0.
                col = WON_COL[c[0]['won']]
                r0 = db.execute(f"""SELECT wxc_utc u FROM wsf_x_cross WHERE wxc_win_from=%s
                       AND wxc_xwob=0 AND wxc_tf=%s AND wxc_dr=%s AND {col}=1
                       AND wxc_utc <= %s ORDER BY wxc_utc DESC LIMIT 1""",
                    (WIN_FROM, wm, e['dr'], conf), fetch=True)
                raw = r0[0]['u'] if r0 else conf
        else:
            # DEFECT A. THE RISING EDGE, not any confirmed bar. wflb_mfr_run counts consecutive
            # bars outside momo-fence-r, so it equals MOMO_XWOB on exactly ONE bar per run - the
            # bar the hold completes. wflb_mfr_xwob stays 1 for the whole rest of the run.
            c = db.execute("""SELECT wflb_utc u, ABS(TIMESTAMPDIFF(SECOND, %s, wflb_utc)) gap
                   FROM wsf_line_bar WHERE wflb_win_from=%s AND wflb_knobs=%s AND wflb_tf=%s
                     AND wflb_dr=%s AND wflb_mfr_run=%s AND wflb_utc BETWEEN %s AND %s
                   ORDER BY gap LIMIT 1""",
                (anchor.strftime('%Y-%m-%d %H:%M:%S'), WIN_FROM, KNOBS, tf, e['dr'],
                 MOMO_XWOB, s0, t0), fetch=True)
            if c:
                conf = c[0]['u']
                # the run's own first bar, read off the counter rather than derived by subtraction
                r0 = db.execute("""SELECT wflb_utc u FROM wsf_line_bar WHERE wflb_win_from=%s
                       AND wflb_knobs=%s AND wflb_tf=%s AND wflb_dr=%s AND wflb_mfr_run=1
                       AND wflb_utc <= %s ORDER BY wflb_utc DESC LIMIT 1""",
                    (WIN_FROM, KNOBS, tf, e['dr'], conf), fetch=True)
                raw = r0[0]['u'] if r0 else conf
        # the weak-mage-tf at the located bar, for BOTH methods. Joe 0821: "why is the weak-mage
        # ignored when its a fence exit?" - it is not; the column was only being filled on the path
        # that searched by it.
        if conf is not None and wm is None:
            g = db.execute("""SELECT wbt_weak_mage_tf w FROM wsf_bar_tf WHERE wbt_win_from=%s
                   AND wbt_wmt_tf_lo=2 AND wbt_utc=%s AND wbt_dr=%s AND wbt_tf=2""",
                (WIN_FROM, conf, e['dr']), fetch=True)
            wm = int(g[0]['w']) if g and g[0]['w'] else None
        off = int((raw - anchor).total_seconds()) if raw else None
        rows.append((WIN_FROM, TOL_MIN, wm, e['est'], e['tf'], e['dr'], method,
                     raw, conf, off, int(raw is not None), int(e['elif_used']), e['note']))
    db.executemany(f'INSERT INTO wsf_exhaust_bar ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', rows)
    f = sum(r[10] for r in rows)
    print(f'  wsf_exhaust_bar : {len(rows)} rows   proven {f}   not found {len(rows) - f}', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
