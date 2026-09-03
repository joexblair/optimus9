"""build_wsf_event_sign_run - the Mage sign at each walk event, and how long it has held.

Joe 0831: "drop this report into a db table, for all of 08-04". The report is the one he read at
00:32:50 and 01:25:25 - the faster line ws{TF-1}Mage sitting above (+) or below (-) ws{TF}Mage.

THE SIGN. At the event bar, ws{TF-1}Mage minus ws{TF}Mage. Positive means the faster line sits
above this one. ws1's faster line is gcws30 (30 seconds); gcws30 itself has no faster line beneath
it and so has no sign and no row.

THE RUN. Count back at the 2-minute sample step until the sign changes. Joe 0831: "the `run
samples` and `minutes` columns are retained, and contained to the 48 minute sampling window" - so
the count stops at 24 samples even when the sign holds longer. That containment is HIS, from the
0829 window spec: "look back 48 minutes, step=2 minutes".

  WHAT A CAPPED RUN MEANS. 24 samples means "at least 24" - the sign had not changed by the edge of
  his window. Uncapped, the longest run on 08-04 was 92 samples (ws10 at 03:02:30). Joe 0831 ruled
  the `why it stopped` column out, so nothing on the row distinguishes a run that ended at a sign
  change from one that reached 24.

  AND NEAR THE START OF THE DAY the window is short. An event at 00:20:20 has only 11 samples of
  08-04 behind it, so its run is bounded by the data as well as by the containment. 62 of the
  day's rows were affected before the containment was applied; measured, not estimated.

DROPPED ON JOE 0831: `run started` (it is the event bar minus (run samples - 1) x the step, so it
carried no fact of its own) and `why it stopped`.

THE THREE COLUMNS FROM THE WALK come from wsf_event_mark - wem_dr, wem_route, and Joe's own
verdict, which load_wsf_validation.py loaded from 260830_0804_wsf_validation.csv and which was
proven this session to match all 210 events on timestamp, dr and verdict.

NOTHING IS DELETED beyond this table's own rows at this exact knob signature.
"""
import sys
import datetime as dt

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
GRID_S   = 5
STEP_S   = 120        # the sample step. Joe 0829: "step=2 minutes"
WINDOW_MIN = 48       # the containment. Joe 0829: "look back 48 minutes"
LINES = [('g30', 'gcws30'), ('ws1', 'ws1'), ('ws2', 'ws2'), ('ws3', 'ws3')]
# gcws30 is present only as ws1's faster line. It gets no row of its own.
WALK_RUN = 1
WALK_KNOBS = ('kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4_mt12_mg20'
              '_dl180_xw5_wl2_wh12_tr2_g10x4_xtr_hg15_dr9s+1_hrmedian_lhws1b:1')

DDL = '''CREATE TABLE IF NOT EXISTS wsf_event_sign_run (
    wesr_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wesr_knobs VARCHAR(160) NOT NULL,     -- the walk signature the events came from
    wesr_run   INT NOT NULL,              -- the walk run
    wesr_step_s     SMALLINT NOT NULL,    -- the sample step, 120 seconds
    wesr_window_min SMALLINT NOT NULL,    -- the containment, 48 minutes = 24 samples
    wesr_utc  DATETIME NOT NULL,          -- the event bar
    wesr_line VARCHAR(8) NOT NULL,        -- ws1, ws2, ws3
    wesr_sign TINYINT NOT NULL,           -- +1 the faster line sits above, -1 below, 0 equal
    wesr_run_samples SMALLINT NOT NULL,   -- samples the sign has held, counting back. Max 24
    wesr_minutes     SMALLINT NOT NULL,   -- run_samples x 2
    wesr_dr      TINYINT NOT NULL,        -- wem_dr
    wesr_route   VARCHAR(12),             -- wem_route
    wesr_verdict VARCHAR(8),              -- wem_verdict, Joe's own from the csv
    UNIQUE KEY uq_wesr (wesr_knobs, wesr_run, wesr_step_s, wesr_window_min, wesr_utc, wesr_line),
    KEY k_line (wesr_line), KEY k_verdict (wesr_verdict), KEY k_route (wesr_route))'''

COLS = ['wesr_knobs', 'wesr_run', 'wesr_step_s', 'wesr_window_min', 'wesr_utc', 'wesr_line',
        'wesr_sign', 'wesr_run_samples', 'wesr_minutes', 'wesr_dr', 'wesr_route', 'wesr_verdict']


def sgn(v):
    return 1 if v > 0 else -1 if v < 0 else 0


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    stepb = STEP_S // GRID_S                      # 24 bars = 2 minutes
    nsamp = WINDOW_MIN * 60 // STEP_S             # 24 samples = 48 minutes
    cols = ','.join(f'wlb_{c}Mage {c}' for c, _ in LINES)
    bars = db.execute(f'SELECT wlb_utc t,{cols} FROM ws_line_bar '
                      'WHERE wlb_utc >= %s AND wlb_utc < %s ORDER BY wlb_utc',
                      (WIN_FROM, WIN_TO), fetch=True)
    IDX = {str(b['t']): i for i, b in enumerate(bars)}
    M = {c: [b[c] for b in bars] for c, _ in LINES}
    ev = db.execute('SELECT wem_utc t, wem_dr d, wem_route r, wem_verdict v FROM wsf_event_mark '
                    'WHERE wem_run=%s AND wem_knobs=%s ORDER BY wem_utc',
                    (WALK_RUN, WALK_KNOBS), fetch=True)
    print(f'  ws_line_bar : {len(bars):,} bars   wsf_event_mark : {len(ev)} events', flush=True)
    print(f'  step {STEP_S} s = {stepb} bars   containment {WINDOW_MIN} min = {nsamp} samples',
          flush=True)

    db.execute(DDL)
    where = ('wesr_knobs=%s AND wesr_run=%s AND wesr_step_s=%s AND wesr_window_min=%s '
             'AND wesr_utc >= %s AND wesr_utc < %s')
    kv = (WALK_KNOBS, WALK_RUN, STEP_S, WINDOW_MIN, WIN_FROM, WIN_TO)
    n = db.execute('SELECT COUNT(*) c FROM wsf_event_sign_run WHERE ' + where, kv,
                   fetch=True)[0]['c']
    if n:
        print(f'  deleting {n:,} rows already stored at this signature', flush=True)
        db.execute('DELETE FROM wsf_event_sign_run WHERE ' + where, kv)

    rows, capped, short = [], 0, 0
    for e in ev:
        m = str(e['t']); i = IDX.get(m)
        if i is None:
            print(f'  {m} has no ws_line_bar row - skipped', flush=True); continue
        for k, (c, lab) in enumerate(LINES):
            if k == 0:
                continue                       # gcws30 is the faster line for ws1, not a row
            f = LINES[k - 1][0]

            def sg(j):
                a, b = M[c][j], M[f][j]
                return sgn(float(b) - float(a)) if (a is not None and b is not None) else 0

            s0 = sg(i)
            run, j = 0, i
            while j >= 0 and run < nsamp and s0 != 0 and sg(j) == s0:
                run += 1; j -= stepb
            if run >= nsamp:
                capped += 1
            elif j < 0:
                short += 1
            rows.append((WALK_KNOBS, WALK_RUN, STEP_S, WINDOW_MIN, m, lab,
                         s0, run, run * 2, int(e['d']), e['r'], e['v']))
    db.executemany(f'INSERT INTO wsf_event_sign_run ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', rows)
    print(f'  wsf_event_sign_run : {len(rows):,} rows', flush=True)
    print(f'    runs that reached the {nsamp}-sample containment : {capped}', flush=True)
    print(f"    runs that ran out of the day's data before it  : {short}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
