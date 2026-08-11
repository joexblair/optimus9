#!/usr/bin/env python3
"""`eyes_on_pine` — Joe's chart reads, banked as results.

Joe 0810: "we're measuring using my eyes on pine."  His read is a measurement with an n and a
verdict; it belongs in the record beside the numbers the code produces.  Until now it existed only
in chat, so it could not be joined, swept, or carried across a rebuild.

ROW UNIT = ONE EVENT.  A read given as a batch ("everything else is well placed") expands to one
row per event it covers, with Joe's verbatim words repeated on each row.  The event is the only
unit that joins to `momo_landed_report` / `ws_strat_walk` and the only unit a sweep can score, so
the batch cannot be the row (see the s46 lesson: the row unit manufactures the result).

A read is NEVER overwritten.  When Joe revises one, the new read is appended with a fresh
`eop_seq` and the old row gets `eop_superseded_by` set.  The history is the audit trail for why a
knob or a clause exists.

NO READ TIMESTAMP.  The message time was not recorded, so there is no column for it — `eop_seq` is
the order Joe gave them in, and nothing is invented.
"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DDL = '''CREATE TABLE IF NOT EXISTS eyes_on_pine (
    eop_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    eop_seq       SMALLINT NOT NULL,       -- the order Joe gave the reads in. NOT a clock
    eop_session   VARCHAR(10) NOT NULL,    -- the working day the read was given
    eop_artefact  VARCHAR(40) NOT NULL,    -- the .pine he was looking at
    eop_mechanic  VARCHAR(20) NOT NULL,    -- ws_strat | momo_landed
    eop_event_utc VARCHAR(19) NOT NULL,    -- the event stamp. joins to the mechanic's table
    eop_line      VARCHAR(8),              -- ws{TF}r for momo_landed. NULL for a ws_strat signal
    eop_verdict   VARCHAR(4) NOT NULL,     -- pass | fail
    eop_words     VARCHAR(255) NOT NULL,   -- Joe verbatim. the batch sentence, repeated per event
    eop_note      VARCHAR(255),            -- Joe's reasoning, verbatim, where he gave one
    eop_superseded_by SMALLINT,            -- the eop_seq that overrode this read. NULL = current
    eop_resolved  TINYINT NOT NULL DEFAULT 0,  -- 1 = the verdict STOOD and the defect it found is
                                           --     fixed. distinct from superseded, which is Joe
                                           --     revising the verdict itself
    eop_resolved_note VARCHAR(255),
    UNIQUE KEY uq_eop (eop_seq, eop_mechanic, eop_event_utc, eop_line),
    KEY (eop_event_utc), KEY (eop_verdict), KEY (eop_mechanic))'''

R1_FIX = ("Joe 0810: 'this is resolved'. the read forced the gate from if/elif (OR) to AND; "
          "both signals now wsw_gated=1, wsw_gate_by=''")

COLS = ['eop_seq', 'eop_session', 'eop_artefact', 'eop_mechanic', 'eop_event_utc', 'eop_line',
        'eop_verdict', 'eop_words', 'eop_note', 'eop_superseded_by',
        'eop_resolved', 'eop_resolved_note']

SESSION = '2026-08-10'
GATED_PINE, MOMO_PINE = 'ws_strat_gated.pine', 'ws_strat_momo_landed.pine'

# --- the reads, verbatim. seq = the order Joe gave them.
W1 = 'I\'m still seeing signals 08-04 16:10 and 16:31 / in both cases, neither ws1MAge and ws1b are OOB'
W2 = 'the pine emit is showing me that the ws1 signals are correct'
W3 = 'did ws8r bounce on the fence boundary? ideally, 07:44:15 should have been nulled'
W4 = 'everything else is well placed for delegating to the LTFs (6min to 30sec)'
W5 = 're #3 - it has a pass. on inspection, the cost of delaying outweighed the mae costs'

# read 1: two signals on the pre-AND build. Joe's read forced the gate from if/elif (OR) to AND.
READ1 = ['2026-08-04 16:10:25', '2026-08-04 16:31:30']
# read 3 / read 5: the same event, failed then passed.
R3_EVENT, R3_LINE = '2026-08-05 07:44:15', 'ws8r'
# read 4 window: the 08-05 06:00 -> 15:00 table, everything except R3_EVENT
R4_LO, R4_HI = '2026-08-05 06:00:00', '2026-08-05 15:00:00'


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    rows = []

    # seq 1 — pre-AND build, 2 signals. Both are gated in the current build; the read is what
    # produced that. Kept so the reason the AND exists survives.
    for t in READ1:
        rows.append((1, SESSION, GATED_PINE, 'ws_strat', t, None, 'fail', W1, None, None, 1, R1_FIX))

    # seq 2 — the 160 signals the ws1 gate releases, after the AND fix.
    rel = db.execute("SELECT wsw_conf_utc FROM ws_strat_walk WHERE wsw_gate_by='ws1Mage+ws1b' "
                     'ORDER BY wsw_conf_ms', fetch=True)
    for r in rel:
        rows.append((2, SESSION, GATED_PINE, 'ws_strat', r['wsw_conf_utc'], None, 'pass', W2, None, None, 0, None))

    # seq 3 — one momo_landed event, failed. Superseded by seq 5.
    rows.append((3, SESSION, MOMO_PINE, 'momo_landed', R3_EVENT, R3_LINE, 'fail', W3, None, 5, 0, None))

    # seq 4 — the rest of the 08-05 06:00->15:00 table, passed.
    ev = db.execute('SELECT mlr_landed, mlr_line FROM momo_landed_report '
                    'WHERE mlr_landed BETWEEN %s AND %s ORDER BY mlr_landed',
                    (R4_LO, R4_HI), fetch=True)
    for e in ev:
        if e['mlr_landed'] == R3_EVENT and e['mlr_line'] == R3_LINE:
            continue
        rows.append((4, SESSION, MOMO_PINE, 'momo_landed', e['mlr_landed'], e['mlr_line'],
                     'pass', W4, None, None, 0, None))

    # seq 5 — Joe revises read 3 to a pass, with his reasoning.
    rows.append((5, SESSION, MOMO_PINE, 'momo_landed', R3_EVENT, R3_LINE, 'pass', W5,
                 'the cost of delaying outweighed the mae costs', None, 0, None))

    db.execute('DELETE FROM eyes_on_pine WHERE eop_session=%s', (SESSION,))
    db.executemany('INSERT INTO eyes_on_pine (%s) VALUES (%s)'
                   % (','.join(COLS), ','.join(['%s'] * len(COLS))), rows)
    print('eyes_on_pine : %d rows, %d reads' % (len(rows), len({r[0] for r in rows})))
    for s in sorted({r[0] for r in rows}):
        g = [r for r in rows if r[0] == s]
        print('  seq %d  %-12s %-4s  n=%-3d  %s%s'
              % (s, g[0][3], g[0][6], len(g), g[0][7][:64],
                 '   [superseded by %d]' % g[0][9] if g[0][9] else ''))
    db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
