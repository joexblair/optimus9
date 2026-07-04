"""monitor_closed_trades.py — emit one line per NEW closed trade in o9_live (the Monitor event stream).

Polls o9_ledger every 5s; prints CLOSED_TRADE for each newly-closed led_id (flushed). Each line becomes a
notification → react by running `python3 ops/recon_live_vs_walk.py <led_id>` to confirm live↔walk sync.
Seeds from the current max so only FUTURE closes fire. DB self-heals (DatabaseManager L1 reconnect).
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

cfg = get_db_config(); cfg['database'] = 'o9_live'
db = DatabaseManager(**cfg); db.connect()


def max_closed():
    try:
        r = db.execute("SELECT COALESCE(MAX(led_id),0) m FROM o9_ledger WHERE status='closed'", fetch=True)
        return int(r[0]['m'])
    except Exception:
        return None


last = max_closed() or 0
print('monitor: watching o9_ledger for closed trades (led_id > %d)' % last, flush=True)
while True:
    time.sleep(5)
    m = max_closed()
    if m is None or m <= last:
        continue
    rows = db.execute("SELECT led_id, side, entry_px, exit_px, net, reason FROM o9_ledger "
                      "WHERE status='closed' AND led_id > %s ORDER BY led_id", (last,), fetch=True)
    for r in rows:
        print('CLOSED_TRADE led_id=%d side=%s entry=%s exit=%s net=%.2f reason=%s'
              % (r['led_id'], r['side'], r['entry_px'], r['exit_px'], float(r['net'] or 0), r['reason']), flush=True)
    last = m
