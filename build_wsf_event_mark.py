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
import os
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import KLine, override
from optimus9.compute.momo_gated import momo_g_why, momo_window
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
import build_momo_landed as B
from build_wsf_walk_events import SIG

MOMO_TFS = (30, 45, 60)   # the three dtf lines the momentum column reports, in this order
MOMO_SHORT = {'momo': 'mo', 'none': 'no', 'curl': 'cu', 'sideways': 'side'}
# KNOB-FREE LABEL MAP, Joe 0902: "please use the same mo|no|cu|side outputs". The same four short
# forms the printed reports use, so a value read from the table and a value read from a report are
# the same string.

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
    -- THE dtf MOMENTUM READ AT THE EXHAUST BAR. Joe 0902: "add a 30|45|60 momentum column to
    -- wsf_event_mark ... to show the momentum states for each wem_utc rows".
    wem_momo_30_45_60 VARCHAR(40),        -- ws30r / ws45r / ws60r, read at wem_utc, at wem_dr
    --                                   values mo | no | cu | side, Joe 0902 "please use the same
    --                                   mo|no|cu|side outputs". Longest is 'side / side / side'
    -- JOE'S COLUMNS. Empty on write, his alone.
    wem_verdict   VARCHAR(16),            -- his call on the trade
    wem_words     VARCHAR(500),           -- his words
    UNIQUE KEY uq_wem (wem_knobs, wem_run, wem_utc, wem_dr),
    KEY ix_wem_verdict (wem_verdict)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

COLS = ['wem_knobs','wem_run','wem_created','wem_seq','wem_utc','wem_dr','wem_test',
        'wem_trigger_tf','wem_watch_tf','wem_route','wem_trade_utc','wem_lag_s','wem_pxs',
        'wem_slot1_utc','wem_slot2_utc','wem_pool_note']


def fill_momo(db):
    """The 30|45|60 momentum column, for every row that has not got one yet.

    Joe 0902: "add a 30|45|60 momentum column to wsf_event_mark. tp show the momentum states for
    each wem_utc rows. this request is contained only to the existing wsf_event_mark data".

    ONE PRODUCER, THE dtf MODE. momo_g_why(..., quad=True)[0] is the GATED verdict - gate 2 throws
    away a curl that bends against dr. Joe 0901: "be sure to use the dtf mode of 'curl' - there is
    a version that wsf consumes which allows for agnostic curls, which we don't want to deploy in
    dtf".

    THE dr IS THE ROW'S OWN, wem_dr. Joe 0902: "all data in a row will consume the dr that was
    present when 30/45 flipped to momentum-true". Here the row's anchor is wem_utc and its dr is
    already banked beside it, so the row's dr is what the three lines are read against.

    ADDS ONLY. Never updates a row that already carries a value, never touches another column,
    never deletes. Safe to run against rows the walk's refuse-guard protects.
    """
    have = {r['Field'] for r in db.execute('SHOW COLUMNS FROM wsf_event_mark', fetch=True)}
    if 'wem_momo_30_45_60' not in have:
        db.execute('ALTER TABLE wsf_event_mark ADD COLUMN wem_momo_30_45_60 VARCHAR(40)')
        print('  wsf_event_mark : added column wem_momo_30_45_60', flush=True)
    todo = db.execute('SELECT wem_pk pk, wem_utc u, wem_dr dr FROM wsf_event_mark '
                      'WHERE wem_momo_30_45_60 IS NULL ORDER BY wem_utc', fetch=True)
    if not todo:
        print('  wem_momo_30_45_60 : every row already carries a value', flush=True)
        return
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                    'WHERE sys_pk=1', fetch=True)[0]
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    R = {tf: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
         override(tf * 60, KLine(**B.R_SPEC), 'emerging')) + '.npy')) for tf in MOMO_TFS}
    # THE BAR INDEX COMES FROM THE TAPE'S OWN ts. Not len(npy)-len(rows), which put a read 77,759
    # bars adrift on 0901. searchsorted on the cached ts is the only alignment used here.
    ms = lambda d: int(d.replace(tzinfo=timezone.utc).timestamp() * 1000)
    idx, miss = {}, []
    for r in todo:
        j = int(np.searchsorted(ts, ms(r['u'])))
        if j >= len(ts) or int(ts[j]) != ms(r['u']):
            miss.append(str(r['u']))
        else:
            idx[r['pk']] = j
    if miss:
        print(f'  {len(miss)} rows have no bar in the line cache and are left NULL: '
              f'{miss[:5]}{" ..." if len(miss) > 5 else ""}', flush=True)
    # THE BANK. MOMO_TFS 30, 45 and 60 all fall in one band, so one bank covers the run - checked, not assumed.
    _bk = {tf: momo_bank(db, tf) for tf in MOMO_TFS}
    _ids = {(b['mech'], b['tf_lo'], b['tf_hi'], b['version']) for b in _bk.values()}
    if len(_ids) != 1:
        raise SystemExit(f'MOMO_TFS spans {len(_ids)} momentum banks: {sorted(_ids)}. '
                         'One run must sit inside one bank.')
    BANK = _bk[MOMO_TFS[0]]
    print(f"  momentum bank: {BANK['mech']} tf{BANK['tf_lo']}..{BANK['tf_hi']} "
          f"v{BANK['version']}", flush=True)
    st = {}
    for tf in MOMO_TFS:
        with momo_config(BANK), momo_window(BANK['k_window'] * tf):
            for r in todo:
                if r['pk'] not in idx: continue
                st.setdefault(r['pk'], {})[tf] = momo_g_why(
                    R[tf], int(r['dr']), idx[r['pk']], quad=True)[0]
    upd = [(' / '.join(MOMO_SHORT[st[pk][tf]] for tf in MOMO_TFS), pk) for pk in st]
    db.executemany('UPDATE wsf_event_mark SET wem_momo_30_45_60=%s WHERE wem_pk=%s', upd)
    print(f'  wem_momo_30_45_60 : filled {len(upd)} of {len(todo)} rows', flush=True)


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    fill_momo(db)          # BEFORE the refuse guard - it adds a column, it never rewrites a row
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
