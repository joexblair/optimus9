"""migrate_decision_action.py — add 'close_leg' and 'reduce' to o9_decision.action. (Joe 0709)

`app.py:76` writes `act = "close_leg"` on every option-B per-leg SL close, and `app.py:67` branches on
`"reduce"`. Neither is in the enum, so MySQL raises:

    1265 (01000): Data truncated for column 'action' at row 1

The exception propagates out of `_execute`, so any REMAINING intents on that bar are skipped — with hedge
legs, a stop on one side can silently drop an open on the other. The position itself does close
(`record_close_leg` runs before `log_decision`), so the trade is real and only the audit row is lost.

Pre-existing; surfaced 0709 when the arm probe (`O9_PRODUCER=arm`) started opening far more positions and the
per-leg SLs fired constantly. The recon monitor caught it within 20 minutes of going up.

Additive and idempotent: no existing value changes, no rows are rewritten, and it is safe with the loop
running — the statement it repairs is already failing. Run:  python3 migrate_decision_action.py [db]
"""
import sys

from optimus9 import DatabaseManager
from optimus9.config import get_db_config

WANT = "ENUM('open_long','open_short','add','close','close_leg','reduce','hold')"


def main(dbname='o9_live'):
    c = get_db_config(); c['database'] = dbname
    d = DatabaseManager(**c); d.connect()
    cur = [r['Type'] for r in d.execute('SHOW COLUMNS FROM o9_decision', fetch=True) if r['Field'] == 'action'][0]
    print('before: %s' % cur)
    if 'close_leg' in cur and 'reduce' in cur:
        print('already migrated — no-op')
    else:
        d.execute('ALTER TABLE o9_decision MODIFY COLUMN action %s NOT NULL' % WANT)
        cur = [r['Type'] for r in d.execute('SHOW COLUMNS FROM o9_decision', fetch=True) if r['Field'] == 'action'][0]
        print('after : %s' % cur)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'o9_live')
