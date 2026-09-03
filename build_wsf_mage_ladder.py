"""build_wsf_mage_ladder - the ws1..ws12 Mage ladder at every walk event.

Joe 0901 named the mechanic that reads this: `Mage-ladder-weakness`. His definition:
  "this calculation gathers the Mage values for all TFs, and reports a weak signal if the
   ws{1 to 12}Mage values are seen to be stepping away from the TF below it"
and, distinguishing it from the scan that already exists:
  "this is not the weak-mage-tf calculation, which captures the first Mage that is not oob"

THE DIRECTION RULE, Joe 0901, closing the last open definition:
  "this is a dr -1, therefore the weakness calulation will be true if the higher TFs are
   increasing in value. inverse for dr +1"
  dr -1 -> weakness when the ladder CLIMBS from ws1 up to ws12
  dr +1 -> weakness when it FALLS

WHAT THIS TABLE HOLDS, and what it deliberately does not.
  It holds the raw ladder: the Mage value per timeframe, and the step to the neighbour, stored
  BOTH ways round on Joe 0901's M2 "store both" - so neither reader has to flip a sign in their
  head. wml_step_up is Joe's ladder reading, wml_step_down is the sign the matryoshka report
  prints. They are the same subtraction with the operands swapped; PROVEN on 2,520 event rows
  that sgn(step_down) == -sgn(step_up), 0 exceptions.

  IT NOW HOLDS THE WEAKNESS VERDICT, and it carries NO KNOB. Joe 0901: "STEP 3 and STEP 2 need
  to return either yes or no: the lines show weakness, or not" and "anything beyond this is
  strangling the result", after correcting the step-counting reading: "this is levelling an unfair
  verdict, and highlights that you are not allowing for the voliatility that naturally exists in
  crypto".
    wml_spread = ws12Mage - ws1Mage
    wml_weak   = 1 when wml_spread is positive and dr is -1, or negative and dr is +1
  There is no tolerance, no count and no threshold in it. Nothing was chosen by looking at data.

  THE TWO CANDIDATE DIRECTION TESTS TURNED OUT TO BE ONE. ws12 minus ws1 equals the sum of the 11
  steps exactly - they telescope. MEASURED across all 210 events: largest difference 0.0000000000.
  The third candidate, the majority sign of the steps, is a count and Joe 0901 ruled counts out.

  THE ws1 QUALIFIER IS DROPPED. Joe 0901, quoting his own 0831 wording back and ruling on it:
    "the test needs ws1 to print a sign-consistent lead-up, that signals against dr (ie, the ws1
     sign pattern that you see at 03:25:45, is allowed to validate bullish mage-ladder-weakness)"
    "-drop this mech"
  It is no longer computed. wml_ws1_sign, wml_ws1_qual and wml_ws1_run are NOT written by this
  build any more; they are left in the table with the values they already carry, on Joe 0827's
  no-deletes rule - "if we have a history of its usage, we can 1) easily compare the facts needed
  to repair (or enhance) that ingredient and 2) be sure that we have not broken an earlier
  confirmed wsf-exhaust event".

  WHY THE ws1 KNOBS STAY IN THE UNIQUE KEY. wml_ws1_step_s (120 s) and wml_ws1_window_min (48 min)
  were added to the key when the run was banked. Taking them out is a second key migration for no
  gain - they are NOT NULL with defaults, so the key and the pinned DELETE both still work.

  CAUTION, STATED. This build still DELETEs at its signature before inserting. A re-run therefore
  replaces the existing 2,520 rows and the three dropped columns come back NULL. The values in
  them today are the only copy.

  ws1's STEP COMES FROM gcws30. Joe 0901: "how will we know what direction (`+` or `-`) ws1 is
  being pulled towards?" - ws1's sign only exists relative to the line below it, and gcws30 (30 s)
  is the only one. So wml_step_up and wml_step_down are populated on the ws1 row from
  ws1Mage - gcws30Mage, exactly as every other line's step is populated from the line below it.
  One sign mechanism, twelve lines, no special case and no separate column.

  THIS DOES NOT CHANGE `Mage-ladder-weakness`. wml_spread is ws12Mage - ws1Mage and wml_weak is its
  sign against dr. Both read VALUES, not steps, so gcws30 is not in either.

SEPARATE FROM wsf_event_sign_run, on Joe 0901's M1 "bank the ladder seperately". That table is the
matryoshka mech - three lines, read across time. This one is the ladder mech - twelve lines, read
at one bar. Same underlying subtraction, different axis.

NOTHING IS DELETED beyond this table's own rows at this exact knob signature.
"""
import sys

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
TFS      = list(range(1, 13))
WALK_RUN = 1
WALK_KNOBS = ('kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4_mt12_mg20'
              '_dl180_xw5_wl2_wh12_tr2_g10x4_xtr_hg15_dr9s+1_hrmedian_lhws1b:1')

DDL = '''CREATE TABLE IF NOT EXISTS wsf_mage_ladder (
    wml_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wml_knobs VARCHAR(160) NOT NULL,   -- the walk signature the events came from
    wml_run   INT NOT NULL,            -- the walk run
    wml_utc   DATETIME NOT NULL,       -- the event bar
    wml_tf    SMALLINT NOT NULL,       -- 1 to 12
    wml_mage  DOUBLE,                  -- ws{TF}Mage at the bar. %B, 0 to 100, unbounded outside
    wml_step_up   DOUBLE,              -- ws{TF}Mage - ws{TF-1}Mage. Joe's ladder reading
    wml_step_down DOUBLE,              -- ws{TF-1}Mage - ws{TF}Mage. the matryoshka report's sign
    --  the two are the same subtraction, operands swapped. Both stored on Joe 0901 "M2 store both"
    wml_spread    DOUBLE,              -- ws12Mage - ws1Mage. the number the binary reads
    wml_weak      TINYINT,             -- Mage-ladder-weakness. 1 = yes, 0 = no. NO KNOB
    wml_ws1_sign  TINYINT,             -- DROPPED Joe 0901. was sgn(gcws30Mage - ws1Mage) at the bar
    wml_ws1_qual  TINYINT,             -- DROPPED Joe 0901. was 1 when that sign opposed dr
    wml_ws1_run   SMALLINT,            -- DROPPED Joe 0901. was how long that sign had held
    wml_ws1_step_s     SMALLINT NOT NULL DEFAULT 120,  -- the sample step the run counts at
    wml_ws1_window_min SMALLINT NOT NULL DEFAULT 48,   -- the containment on the run
    wml_dr      TINYINT NOT NULL,      -- wem_dr
    wml_route   VARCHAR(12),           -- wem_route
    wml_verdict VARCHAR(8),            -- wem_verdict, Joe's own from the csv
    UNIQUE KEY uq_wml (wml_knobs, wml_run, wml_ws1_step_s, wml_ws1_window_min,
                       wml_utc, wml_tf),
    KEY k_tf (wml_tf), KEY k_verdict (wml_verdict), KEY k_dr (wml_dr))'''

COLS = ['wml_knobs', 'wml_run', 'wml_utc', 'wml_tf', 'wml_mage', 'wml_step_up', 'wml_step_down',
        'wml_spread', 'wml_weak', 'wml_ws1_step_s', 'wml_ws1_window_min',
        'wml_dr', 'wml_route', 'wml_verdict']

WS1_STEP_S     = 120   # STAYS IN THE UNIQUE KEY, no longer used to compute anything. It was the
WS1_WINDOW_MIN = 48    # sample step and containment for the dropped ws1 run - Joe 0829 "look back
#                        48 minutes, step=2 minutes"


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    cols = ','.join(['wlb_g30Mage g30'] + [f'wlb_ws{t}Mage m{t}' for t in TFS])
    bars = db.execute(f'SELECT wlb_utc t,{cols} FROM ws_line_bar '
                      'WHERE wlb_utc >= %s AND wlb_utc < %s ORDER BY wlb_utc',
                      (WIN_FROM, WIN_TO), fetch=True)
    B = {str(b['t']): b for b in bars}
    ev = db.execute('SELECT wem_utc t, wem_dr d, wem_route r, wem_verdict v FROM wsf_event_mark '
                    'WHERE wem_run=%s AND wem_knobs=%s ORDER BY wem_utc',
                    (WALK_RUN, WALK_KNOBS), fetch=True)
    print(f'  ws_line_bar : {len(bars):,} bars   wsf_event_mark : {len(ev)} events', flush=True)

    db.execute(DDL)
    have = {r['Field'] for r in db.execute('SHOW COLUMNS FROM wsf_mage_ladder', fetch=True)}
    add = [('wml_spread', 'DOUBLE'), ('wml_weak', 'TINYINT'), ('wml_ws1_sign', 'TINYINT'),
           ('wml_ws1_qual', 'TINYINT'), ('wml_ws1_run', 'SMALLINT'),
           ('wml_ws1_step_s', 'SMALLINT NOT NULL DEFAULT 120'),
           ('wml_ws1_window_min', 'SMALLINT NOT NULL DEFAULT 48')]
    for c, ty in add:
        if c not in have:
            db.execute(f'ALTER TABLE wsf_mage_ladder ADD COLUMN {c} {ty}')
            print(f'  added {c}', flush=True)
    if 'wml_ws1_step_s' not in have:
        db.execute('ALTER TABLE wsf_mage_ladder DROP INDEX uq_wml, ADD UNIQUE KEY uq_wml '
                   '(wml_knobs, wml_run, wml_ws1_step_s, wml_ws1_window_min, wml_utc, wml_tf)')
        print('  rebuilt the unique key with the ws1 run knobs in it', flush=True)
    where = ('wml_knobs=%s AND wml_run=%s AND wml_ws1_step_s=%s AND wml_ws1_window_min=%s '
             'AND wml_utc >= %s AND wml_utc < %s')
    kv = (WALK_KNOBS, WALK_RUN, WS1_STEP_S, WS1_WINDOW_MIN, WIN_FROM, WIN_TO)
    n = db.execute('SELECT COUNT(*) c FROM wsf_mage_ladder WHERE ' + where, kv, fetch=True)[0]['c']
    if n:
        print(f'  deleting {n:,} rows already stored at this signature', flush=True)
        db.execute('DELETE FROM wsf_mage_ladder WHERE ' + where, kv)

    rows, miss = [], 0
    for e in ev:
        m = str(e['t']); b = B.get(m)
        if b is None:
            miss += 1; continue
        dr = int(e['d'])
        m1, m12 = b['m1'], b['m12']
        spread = None if (m1 is None or m12 is None) else float(m12) - float(m1)
        weak = None if spread is None else int((spread > 0 and dr < 0) or (spread < 0 and dr > 0))
        for t in TFS:
            v = b[f'm{t}']
            v = None if v is None else float(v)
            below = b['g30'] if t == 1 else b[f'm{t-1}']   # ws1's line below is gcws30
            if v is None or below is None:
                up = dn = None
            else:
                up = v - float(below); dn = -up
            rows.append((WALK_KNOBS, WALK_RUN, m, t, v, up, dn,
                         spread, weak, WS1_STEP_S, WS1_WINDOW_MIN, dr, e['r'], e['v']))
    db.executemany(f'INSERT INTO wsf_mage_ladder ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', rows)
    if miss:
        print(f'  {miss} events had no ws_line_bar row and were skipped', flush=True)
    print(f'  wsf_mage_ladder : {len(rows):,} rows', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
