"""build_wsf_event_mark - the walk's events laid out for Joe to mark.

Joe 0829: "drop the current walk events in a db table for me. I'll mark the good trades for you to
model on".

ONE ROW PER BANKED EVENT of one walk run. Every column the walk produced is here so the row can be
judged without a join, plus two empty columns that are Joe's alone:

    wem_verdict   his call on the trade. NULL until he writes it.
    wem_words     his words. NULL until he writes it.

NOTHING IS DELETED and nothing is overwritten. Joe 0827: "no deletes - here's the reason why: if we
add a new ingredient to support a decision that overrides an existing verdict, there is always a
possibility that the new ingredient is malformed". A second run of this script at the same
(knobs, run) is refused rather than replaced, so a mark he has already written cannot be lost.

MINE, STATED, three:
  the source run defaults to the highest run at the walk's current knob signature. That is the walk
    as it stands; an older run is named explicitly with SRC_RUN.
  the knob signature and the source run are on every row, so a mark is always traceable to the walk
    that produced it. Joe's standing rule - every knob that changes rows is in the key.
  px at the trade bar comes from wes_pxs_signal, already banked by the walk. It is here because Joe
    is marking TRADES, and a trade without its price is not judgeable.
"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from build_wsf_walk_events import SIG

SRC_RUN = None      # RUN SCOPE. None = the highest run at SIG. An int names an older run.

DDL = '''CREATE TABLE IF NOT EXISTS wsf_event_mark (
    wem_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wem_knobs     VARCHAR(160) NOT NULL,  -- the walk's knob signature. In the unique key
    wem_run       INT      NOT NULL,      -- the walk run these rows came from. In the unique key
    wem_created   DATETIME NOT NULL,
    wem_seq       INT      NOT NULL,      -- the walk's own sequence number, gaps = gated events
    wem_utc       DATETIME NOT NULL,      -- the exhaust bar
    wem_dr        TINYINT  NOT NULL,      -- +1 = SHORT, -1 = LONG
    wem_test      VARCHAR(24) NOT NULL,   -- maxtf | plain | forced, or a pair
    wem_trigger_tf SMALLINT,              -- the designated line that declared it
    wem_watch_tf  SMALLINT,               -- the line the trade rides
    wem_route     VARCHAR(12),            -- weak-mage | rule-c | big-hammer
    wem_trade_utc DATETIME,               -- the bar the trade opened
    wem_lag_s     INT,                    -- exhaust bar -> trade bar, seconds
    wem_pxs       DOUBLE,                 -- px_smooth at the trade bar
    wem_slot1_utc DATETIME, wem_slot2_utc DATETIME,
    wem_pool_note VARCHAR(255) NOT NULL DEFAULT '',
    -- JOE'S COLUMNS. Empty on write, his alone.
    wem_verdict   VARCHAR(16),            -- his call on the trade
    wem_words     VARCHAR(500),           -- his words
    UNIQUE KEY uq_wem (wem_knobs, wem_run, wem_utc, wem_dr),
    KEY ix_wem_verdict (wem_verdict)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

COLS = ['wem_knobs','wem_run','wem_created','wem_seq','wem_utc','wem_dr','wem_test',
        'wem_trigger_tf','wem_watch_tf','wem_route','wem_trade_utc','wem_lag_s','wem_pxs',
        'wem_slot1_utc','wem_slot2_utc','wem_pool_note']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    run = SRC_RUN
    if run is None:
        got = db.execute('SELECT MAX(wee_run) r FROM wsf_exhaust_event WHERE wee_knobs=%s',
                         (SIG,), fetch=True)[0]['r']
        if got is None:
            print(f'  no walk runs banked at {SIG}'); db.disconnect(); return 1
        run = int(got)
    have = db.execute('SELECT COUNT(*) c FROM wsf_event_mark WHERE wem_knobs=%s AND wem_run=%s',
                      (SIG, run), fetch=True)[0]['c']
    if have:
        marked = db.execute('SELECT COUNT(*) c FROM wsf_event_mark WHERE wem_knobs=%s '
                            'AND wem_run=%s AND wem_verdict IS NOT NULL', (SIG, run),
                            fetch=True)[0]['c']
        print(f'  run {run} is already laid out here - {have} rows, {marked} of them marked.')
        print(f'  REFUSING to rewrite. Joe 0827: "no deletes". Point SRC_RUN at another run, or')
        print(f'  re-run the walk so a new run number is allocated.')
        db.disconnect(); return 1

    rows = db.execute("""SELECT e.wee_seq s, e.wee_utc u, e.wee_dr dr, e.wee_test t,
                                e.wee_trigger_tf g, e.wee_note n,
                                e.wee_trade1_utc t1, e.wee_trade2_utc t2,
                                s.wes_watch_tf w, s.wes_route rt, s.wes_utc x, s.wes_lag_s lg,
                                s.wes_pxs_signal px
                           FROM wsf_exhaust_event e
                           JOIN wsf_event_signal s ON s.wes_event_pk = e.wee_pk
                          WHERE e.wee_knobs=%s AND e.wee_run=%s
                       ORDER BY e.wee_utc, e.wee_seq""", (SIG, run), fetch=True)
    if not rows:
        print(f'  run {run} has no events at {SIG}'); db.disconnect(); return 1
    created = db.execute('SELECT NOW() n', fetch=True)[0]['n']
    vals = [(SIG, run, created, x['s'], x['u'], x['dr'], x['t'], x['g'], x['w'], x['rt'],
             x['x'], x['lg'], x['px'], x['t1'], x['t2'],
             (x['n'].split('. ', 1)[1] if '. ' in x['n'] else x['n'])[:255]) for x in rows]
    db.executemany(f'INSERT INTO wsf_event_mark ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', vals)
    print(f'\n  wsf_event_mark : {len(vals)} rows laid out from walk run {run}')
    print(f'  knobs {SIG}\n')
    # THE QUERIES PIN THE KNOB SIGNATURE, NOT JUST THE RUN. wem_run restarts at 1 for every
    # signature, exactly as wee_run does, so `WHERE wem_run=1` can straddle two different walks the
    # moment a second signature reaches run 1. This is the same defect that made report_wsf_bar.py
    # read a pre-bake walk's trade slots on 0829. Joe's standing rule: every knob that changes rows
    # is in the key AND in every query that reads it.
    print('  MARK A TRADE:')
    print("    UPDATE wsf_event_mark SET wem_verdict='good', wem_words='...'")
    print(f"     WHERE wem_knobs='{SIG}'")
    print(f"       AND wem_run={run} AND wem_utc='2026-08-04 01:49:35';\n")
    print('  SEE WHAT IS MARKED:')
    print("    SELECT wem_utc, wem_dr, wem_test, wem_trade_utc, wem_verdict, wem_words")
    print(f"      FROM wsf_event_mark WHERE wem_knobs='{SIG}'")
    print(f"       AND wem_run={run} ORDER BY wem_utc;\n")
    print('  THE LATEST WALK, WITHOUT NAMING THE SIGNATURE:')
    print("    SELECT wem_utc, wem_dr, wem_test, wem_trade_utc, wem_verdict, wem_words")
    print("      FROM wsf_event_mark")
    print("     WHERE (wem_knobs, wem_run) = (SELECT wem_knobs, wem_run FROM wsf_event_mark")
    print("                                    ORDER BY wem_created DESC LIMIT 1)")
    print("     ORDER BY wem_utc;\n")
    print(f"  {'seq':>4} {'bar':<10}{'dr':>3}  {'declared by':<12}{'line':<6}{'route':<11}"
          f"{'trade':<10}{'lag':>7}{'px at trade':>13}  verdict")
    for v in vals:
        lg = int(v[11]); px = v[12]
        print(f"  {v[3]:>4} {str(v[4])[11:]:<10}{v[5]:>+3}  {v[6]:<12}ws{v[8]:<4}{v[9]:<11}"
              f"{str(v[10])[11:]:<10}{f'{lg//60}m{lg%60:02d}s':>7}"
              f"{(f'{px:.6f}' if px is not None else '-'):>13}  -")
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
