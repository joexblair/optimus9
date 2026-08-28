"""build_wsf_ingredient — the master list of the walk's ingredients. One row per ingredient.

Joe 0827: "you should have every ingredient listed in single table. that table holds the dataset
that you refer to for each decision - when you have a confirmed ingredient list, you won't miss any
of them. the other tables will simply join to the ingredient's PKs. we are SRP all the way"

WHAT THIS TABLE IS. The catalogue: what each ingredient IS, where its value lives, and whether Joe
has confirmed it. It carries NO per-bar reading and NO per-event usage - those belong to
wsf_event_ingredient, which joins here by wig_pk.

WHAT IT IS NOT. It is not run-versioned. There is one list, and it is the list the walk refers to
for every decision. When an ingredient changes home, the row is UPDATED and wig_changed_utc moves.
When one is retired, wig_retired_utc is set. NOTHING IS DELETED - Joe 0827: "no deletes".

wig_confirmed DEFAULTS TO 1. Joe 0827, verbatim: "if we've just built a new ingredient and tested
it, then it will be added to the wig table as confirmed. we'll only set it to zero if it is
superseded -- taking this approach ensures that a new ingredient is always accepted, so that we
don't have to remember to set `confirmed`".

So a new row is live the moment it lands. Setting it to 0 is the deliberate act, and it means
SUPERSEDED - not "unproven". This script never writes a 0; only Joe does.

THE NUMBERS in wig_num are Joe's own, from the 0825 list of 36: "list all of your model ingredients.
for each ingredient, tell me how you applied it and how it contributed to your verdict." Ingredients
Joe added after that list carry NULL.

    python3 build_wsf_ingredient.py
"""
import sys
import datetime as dt

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DDL = '''CREATE TABLE IF NOT EXISTS wsf_ingredient (
    wig_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wig_num       SMALLINT,                 -- Joe's number from his 0825 list of 36. NULL if later
    wig_name      VARCHAR(48) NOT NULL,     -- the ingredient, in Joe's own words. THE NATURAL KEY
    wig_home      VARCHAR(40) NOT NULL,     -- the table or producer the value lives in
    wig_source    VARCHAR(64) NOT NULL,     -- the column or expression inside that home
    wig_read      TINYINT NOT NULL,         -- 1 = the recipe consumes it today. 0 = banked, unread
    wig_confirmed TINYINT NOT NULL DEFAULT 1,  -- 1 = live. 0 = SUPERSEDED, and only Joe sets it
    wig_note      VARCHAR(255) NOT NULL DEFAULT '',
    wig_added_utc   DATETIME NOT NULL,
    wig_changed_utc DATETIME,               -- set when home, source or read changes
    wig_retired_utc DATETIME,               -- set instead of deleting the row
    UNIQUE KEY uq_wig (wig_name),
    KEY k_wig_read (wig_read), KEY k_wig_conf (wig_confirmed)) ENGINE=InnoDB'''

# (num, name, home, source, read, note)
# HOME is where the value actually lives. Four ingredients have no banked home at all and that is
# recorded rather than hidden - Joe 0827 asked for the list so that none goes missing.
INGREDIENTS = [
    (1,   'am I in trade',             'the walk',        'the pyramid slots',           0, 'Joe 0823, question 1 of three. Ported out of the sunsetted build_wsf_walk.py 0828 on Joe word; the pool now lives in the walk and lands on wee_slot1/2'),
    (2,   'three-mage dr',             'jig',             'wsf_facing_dr + wsf_dr_lookback', 1, 'Joe 0823, question 2. gcws30Mage/ws1Mage/ws2Mage vs the 80/20 fence'),
    (4,   'r value',                   'wsf_line_bar',    'wflb_r',                      1, ''),
    (5,   'heading',                   'report_wsf_bar',  'derived at print',            0, 'away / toward / flat against momo-fence-r. NOT BANKED'),
    (6,   'r IB',                      'wsf_line_bar',    'wflb_oob',                    0, ''),
    (7,   'verdict',                   'wsf_line_bar',    'wflb_verdict',                1, 'momo | curl | sideways | none, after the momentum-kill'),
    (8,   'curl_dr',                   'wsf_line_bar',    'wflb_curl_ends',              0, ''),
    (9,   'wsf-curl-mode',             'momo_gated',      'curl_gates(gate2=False)',     0, 'Joe 0824. NOT BANKED - computed at the bar'),
    (10,  'stalled',                   'wsf_line_bar',    'wflb_stalled',                0, 'STALL_N 6 lattice samples with no new extreme'),
    (11,  '50 gate',                   'wsf_line_bar',    'wflb_level',                  0, ''),
    (12,  'blocked by 50',             'wsf_line_bar',    'wflb_level',                  0, ''),
    (13,  'last-verdict',              'wsf_line_bar',    'wflb_last_verdict',           0, ''),
    (14,  'last-verdict-dwell',        'wsf_line_bar',    'wflb_verdict_dwell',          0, 'seconds since the verdict changed. Joe 0820'),
    (15,  'Mage value',                'wsf_bar_tf',      'wbt_mage',                    0, ''),
    (16,  'lb-mage-oob',               'wsf_bar_tf',      'wbt_mage_oob_tol',            0, 'out of bounds inside the 120 s tolerance'),
    (17,  'weak-mage-tf',              'wsf_bar_tf',      'wbt_weak_mage_tf',            1, 'Joe 0817. scan ws2Mage upward to ws12Mage. FIXED AT THE EXHAUST BAR, Joe 0828: "reads weak-mage-tf at the exhaust bar and watches that line forward -- this is the correct option". Not re-read on the walk forward'),
    (18,  'stoch now',                 'wsf_bar_tf',      'wbt_stoch_now',               0, ''),
    (19,  'stoch out',                 'wsf_bar_tf',      'wbt_stoch_out',               0, 'the reading leaving r window at the next close'),
    (20,  'sat clock',                 'wsf_bar_tf',      'wbt_sat_bars',                0, ''),
    (21,  'sat left',                  'wsf_bar_tf',      'wbt_sat_left',                0, ''),
    (22,  'RSI',                       'wsf_bar_tf',      'wbt_rsi, wbt_rsi_lo, wbt_rsi_hi', 0, ''),
    (25,  'away / toward counts',      'report_wsf_bar',  'footer, derived at print',    0, 'NOT BANKED'),
    (26,  'r IB count',                'report_wsf_bar',  'footer, derived at print',    0, 'NOT BANKED'),
    (27,  'LTF away / HTF toward',     'report_wsf_bar',  'footer, derived at print',    0, 'Joe 0824. LTF is ws1-ws4, HTF is ws5-ws8. NOT BANKED'),
    (28,  'maxTF distance from fence', 'wsf_line_bar',    'wflb_r at the ceiling line',  0, ''),
    (29,  'Mage lines out of bounds',  'wsf_bar_tf',      'wbt_mage_oob_tol',            0, ''),
    (30,  'stoch_out_extreme',         'jig',             'stoch_out_extreme vs dr',     0, 'stoch out 0 = r cannot fall, 100 = r cannot rise. Joe 0828: dr is baked in, so the reading names which lines are committed to the dr trade rather than which way they cannot go'),
    (32,  'blast radius',              'nowhere',         'no machine reading',          0, 'Joe 0825: "each r line has a small blast radius". NO HOME'),
    (33,  'mid-board',                 'nowhere',         'no machine reading',          0, 'Joe 0825: "mid-board is the space where momentum is the lowest". Its 65/35 fence was retired by Joe 0825. NO HOME'),
    (34,  'depth',                     'wsf_bar_tf',      'wbt_sat_left, wbt_sat_bars',  0, 'Joe 0825, msg 843. Report followed at 03:53:00'),
    (35,  'limits',                    'wsf_line_bar',    'wflb_r at 100.00 or 0.00',    0, 'a limit is a turning point. MINE, from my own 0825 banking, not Joe words'),
    (None,'the dr latch',              'the walk',        'last known dr, held',         1, 'Joe 0826: "the walk will retain the last known dr"'),
    (None,'the maxTF declaration',     'wsf_line_bar',    'wflb_verdict at the ceiling line', 1, 'Joe 0819: "when ws8r stalls or crosses to oob, wsf-exhaustion is declared"'),
    (None,'the plain wsf-exhaust',     'wsf_line_bar',    'wflb_verdict, ws1 to the ceiling', 1, 'no line reads momo or curl'),
    (None,'the x-cross forced exhaust','wsf_x_cross',     'wxc_x_r',                     1, 'Joe 0825. OPEN O1 - the confirmer question is unresolved, and the watched x was label-selected'),
    (None,'the x-cross race',          'wsf_x_cross',     'wxc_race_won',                1, 'Joe 0818: "x X [MAge,b,boundary]", first to cross wins'),
    (None,'x-cross direction',         'wsf_x_cross',     'wxc_dr',                      1, 'dr +1 crosses UNDER, dr -1 crosses OVER. Joe: "you have nailed it"'),
    (None,'rule C',                    'wsf_bar_tf',      'wbt_weak_mage_tf IS NULL',    1, 'Joe 0817 as corrected 0826: fire on the next ws2x-cross'),
    (None,'the momentum-kill',         'wsf_line_bar',    'wflb_ungated vs wflb_verdict', 1, 'Joe 0821: a momentum-true r line leaving momo-fence-r or stalling reads none'),
    (None,'the baton',                 'wsf_line_bar',    'wflb_ungated vs wflb_verdict', 1, 'Joe 0825, msg 884. It IS the momentum-kill under Joe name for it. Report followed at 01:58:00'),
    (None,'momo-fence-r',              'wsf_line_bar',    'wflb_mfr_out',                1, 'Joe 0820: 100-{knob:17}, so 83 / 17'),
    (None,'the 85/15 boundary',        'optimus9_system', 'hi_boundary, lo_boundary',    1, 'the system fence. Not wsf own'),
    (None,'the ladder ceiling',        'the walk',        'MAX_TF',                      1, 'Joe 0826: "wsf is limited to TF12"'),
    (None,'the matryoshka',            'wsf_line_bar',    'the LTF/HTF split of holders', 0, 'Joe 0824, msg 720. Also banked as wsf_setup ltf_away_n / htf_toward_n'),
]

COLS = ['wig_num','wig_name','wig_home','wig_source','wig_read','wig_note',
        'wig_added_utc','wig_changed_utc']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    now = dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    have = {r['wig_name']: r for r in db.execute(
        'SELECT wig_name, wig_num, wig_home, wig_source, wig_read, wig_note FROM wsf_ingredient',
        fetch=True)}
    added = changed = same = 0
    for num, name, home, source, read, note in INGREDIENTS:
        if name not in have:
            db.execute(f'INSERT INTO wsf_ingredient ({",".join(COLS)}) VALUES (%s,%s,%s,%s,%s,%s,%s,NULL)',
                       (num, name, home, source, read, note, now))
            added += 1
            continue
        h = have[name]
        # THE NOTE COUNTS AS A CHANGE. It carries Joe's rulings, so a note edit that did not
        # land would be a rule silently absent from the table.
        moved = (h['wig_home'] != home or h['wig_source'] != source
                 or int(h['wig_read']) != read or (h['wig_num'] or None) != num
                 or (h['wig_note'] or '') != note)
        if moved:
            # UPDATE, never DELETE. wig_confirmed is untouched - a 0 there is Joe's supersede
            # ruling and a re-run must not undo it.
            db.execute('UPDATE wsf_ingredient SET wig_num=%s, wig_home=%s, wig_source=%s, '
                       'wig_read=%s, wig_note=%s, wig_changed_utc=%s WHERE wig_name=%s',
                       (num, home, source, read, note, now, name))
            changed += 1
        else:
            same += 1

    live = {n for _, n, _, _, _, _ in INGREDIENTS}
    for name in have:
        if name not in live:
            db.execute('UPDATE wsf_ingredient SET wig_retired_utc=%s WHERE wig_name=%s '
                       'AND wig_retired_utc IS NULL', (now, name))

    n = db.execute('SELECT COUNT(*) c FROM wsf_ingredient', fetch=True)[0]['c']
    print(f'\n  wsf_ingredient : {n} ingredients   '
          f'{added} added, {changed} updated, {same} unchanged\n', flush=True)
    print(f"  {'#':>4}  {'ingredient':<28}{'home':<18}{'source':<36}{'read':<6}{'Joe':<5}", flush=True)
    for r in db.execute('SELECT * FROM wsf_ingredient ORDER BY wig_home, wig_num IS NULL, wig_num',
                        fetch=True):
        print(f"  {(('#' + str(r['wig_num'])) if r['wig_num'] else '-'):>4}  {r['wig_name']:<28}"
              f"{r['wig_home']:<18}{r['wig_source']:<36}"
              f"{('yes' if r['wig_read'] else ''):<6}{('yes' if r['wig_confirmed'] else ''):<5}",
              flush=True)
    live = db.execute('SELECT COUNT(*) c FROM wsf_ingredient WHERE wig_confirmed=1', fetch=True)[0]['c']
    sup = db.execute('SELECT COUNT(*) c FROM wsf_ingredient WHERE wig_confirmed=0', fetch=True)[0]['c']
    print(f'\n  {live} live, {sup} superseded. A new ingredient lands live; only Joe sets a 0.',
          flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
