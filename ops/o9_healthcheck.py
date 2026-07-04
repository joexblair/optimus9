"""o9_healthcheck.py — one-line o9-live system snapshot; flags anything wrong. Run hourly via a Monitor
(the safety net for what the closed-trade monitor misses: process death, stale tape, liquidation risk).
Emits 'o9-live HEALTH [OK|PROBLEM]: ...' — a PROBLEM line is the alarm to investigate.
"""
import sys, time, urllib.request
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

FAKEAPI = 'http://127.0.0.1:8098'
SYMBOL = 'FARTCOINUSDT'
now = int(time.time() * 1000)
probs = []


def age(ms):
    return None if ms is None else round((now - int(ms)) / 1000.0, 1)


try:
    dev = DatabaseManager(**get_db_config()); dev.connect()
    k = dev.execute("SELECT MAX(kc_timestamp) t FROM kline_collection WHERE kc_tp_pk="
                    "(SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s)", (SYMBOL,), fetch=True)
    tape = age(k[0]['t']) if k and k[0]['t'] else None
    try:
        tk = dev.execute("SELECT MAX(tk_timestamp) t FROM ticks", fetch=True)
        ticks = age(tk[0]['t']) if tk and tk[0]['t'] else None
    except Exception:
        ticks = None
    dev.disconnect()
    if tape is None or tape > 30:
        probs.append('TAPE STALE (%ss)' % tape)
    if ticks is not None and ticks > 90:
        probs.append('TICKS STALE (%ss)' % ticks)
except Exception as e:
    tape = ticks = None; probs.append('dev DB: %s' % e)

try:
    c = get_db_config(); c['database'] = 'o9_live'; o9 = DatabaseManager(**c); o9.connect()
    h = o9.execute("SELECT phase_label, loop_ms, updated_ms FROM o9_health WHERE health_id=1", fetch=True)
    hb = age(h[0]['updated_ms']) if h else None
    loop_ms = h[0]['loop_ms'] if h else None
    acct = o9.execute("SELECT equity, trade_count FROM o9_account WHERE acct_id=1", fetch=True)
    eq = float(acct[0]['equity']) if acct else None
    tc = acct[0]['trade_count'] if acct else 0
    pos = o9.execute("SELECT side, SUM(qty) q FROM o9_ledger WHERE status='open' GROUP BY side", fetch=True)
    posn = ('%s %.0f' % (pos[0]['side'], float(pos[0]['q']))) if pos else 'flat'
    cl1h = o9.execute("SELECT COUNT(*) n, COALESCE(SUM(net),0) p FROM o9_ledger WHERE status='closed' "
                      "AND closed_ms > %s", (now - 3600_000,), fetch=True)[0]
    o9.disconnect()
    if hb is None or hb > 60:
        probs.append('LOOP HEARTBEAT STALE (hb=%ss — loop dead?)' % hb)
    if eq is not None and eq < 50:
        probs.append('EQUITY LOW $%.0f (liquidation risk)' % eq)
except Exception as e:
    hb = loop_ms = eq = None; posn = '?'; tc = 0; cl1h = {'n': '?', 'p': 0}; probs.append('o9 DB: %s' % e)

try:
    with urllib.request.urlopen(FAKEAPI + '/health', timeout=5) as r:
        fake = 'up' if r.status == 200 else 'HTTP%d' % r.status
except Exception:
    fake = 'DOWN'; probs.append('fakeAPI DOWN')

status = 'PROBLEM' if probs else 'OK'
print('o9-live HEALTH [%s]: hb=%ss tape=%ss ticks=%ss fakeAPI=%s eq=$%s pos=%s trades(1h)=%s/$%+.2f loop=%sms%s'
      % (status, hb, tape, ticks, fake, ('%.0f' % eq) if eq is not None else '?', posn,
         cl1h['n'], float(cl1h['p']), loop_ms, ('' if not probs else '  ⚠ ' + ' · '.join(probs))), flush=True)
