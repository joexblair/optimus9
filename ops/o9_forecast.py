"""o9_forecast.py — the hourly PREDICTION JOURNAL (Joe 0704): each wake, look back at the last forecast,
grade it against what actually happened, THEN record the new one. Builds intimacy with the mechanic + a
queryable accuracy record over time. Table o9_forecast in o9_live (self-creates).

  python3 ops/o9_forecast.py last                 # show the latest forecast (to grade it)
  python3 ops/o9_forecast.py grade "<outcome>" <hit|partial|miss>   # grade the latest UNGRADED one
  python3 ops/o9_forecast.py record "<prediction>"                  # store a new forecast (snapshots price+cascade)
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

c = get_db_config(); c['database'] = 'o9_live'
db = DatabaseManager(**c); db.connect()
db.execute("""CREATE TABLE IF NOT EXISTS o9_forecast (
  fc_id BIGINT AUTO_INCREMENT PRIMARY KEY, made_ms BIGINT NOT NULL, price_at DECIMAL(14,8),
  casc VARCHAR(80), prediction TEXT NOT NULL, horizon VARCHAR(20) DEFAULT '~1h',
  graded_ms BIGINT, outcome TEXT, score VARCHAR(12)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")


def dt(ms):
    return time.strftime('%m-%d %H:%M:%S', time.gmtime(int(ms) / 1000)) if ms else '—'


def snapshot():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    k = dev.execute("SELECT kc_close c FROM kline_collection WHERE kc_tp_pk=(SELECT tp_pk FROM trading_pairs "
                    "WHERE tp_symbol_bybit='FARTCOINUSDT') ORDER BY kc_timestamp DESC LIMIT 1", fetch=True)
    dev.disconnect()
    px = float(k[0]['c']) if k else None
    h = db.execute("SELECT phase_label FROM o9_health WHERE health_id=1", fetch=True)
    return px, (h[0]['phase_label'] if h else None)


cmd = sys.argv[1] if len(sys.argv) > 1 else 'last'

if cmd == 'last':
    r = db.execute("SELECT * FROM o9_forecast ORDER BY fc_id DESC LIMIT 1", fetch=True)
    if not r:
        print('o9_forecast: no prior forecast (first wake — nothing to grade).')
    else:
        r = r[0]
        print('LAST FORECAST #%d  made %s  px=%s  casc=%s' % (r['fc_id'], dt(r['made_ms']), r['price_at'], r['casc']))
        print('  prediction: %s' % r['prediction'])
        print('  graded: %s' % ('NOT YET — grade it now' if not r['graded_ms']
                                 else '[%s] %s' % (r['score'], r['outcome'])))

elif cmd == 'grade':
    outcome = sys.argv[2]; score = sys.argv[3] if len(sys.argv) > 3 else 'partial'
    r = db.execute("SELECT fc_id FROM o9_forecast WHERE graded_ms IS NULL ORDER BY fc_id DESC LIMIT 1", fetch=True)
    if not r:
        print('o9_forecast: no ungraded forecast to grade.')
    else:
        db.execute("UPDATE o9_forecast SET graded_ms=%s, outcome=%s, score=%s WHERE fc_id=%s",
                   (int(time.time() * 1000), outcome, score, r[0]['fc_id']))
        print('graded #%d [%s]' % (r[0]['fc_id'], score))

elif cmd == 'record':
    pred = sys.argv[2]
    px, casc = snapshot()
    db.execute("INSERT INTO o9_forecast (made_ms, price_at, casc, prediction) VALUES (%s,%s,%s,%s)",
               (int(time.time() * 1000), px, casc, pred))
    fid = db.execute("SELECT LAST_INSERT_ID() i", fetch=True)[0]['i']
    print('recorded forecast #%d (px=%s, casc=%s)' % (fid, px, casc))

db.disconnect()
