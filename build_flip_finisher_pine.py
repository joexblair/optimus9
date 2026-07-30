"""build_flip_finisher_pine — emit rpl_micro's flip_finisher events as a TF1-pane Pine (Joe 0727).

Double-print red/green bgcolors, transp=0 (opaque): green = LONG entry bar, red = SHORT — the same
convention and 2-bar-wide paint as build_past50_pine.py, so the two panes read alike.

Source = rpl_micro rows with m_mechanic='flip_finisher' (the 6-of-9 fire = the trade). Read straight
from the table, no re-walk. Direction: trade dir d = -m_de (m_de = the s4Mage breach side; the trade is
its reversal, so a lo-breach de=-1 is a LONG).

Usage: build_flip_finisher_pine.py [YYYY-MM-DD ...]     (default 2026-06-13; many days -> one file)
"""
import sys
import datetime as dt
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

days = [a for a in sys.argv[1:] if a[:4].isdigit()] or ['2026-06-13']
days = sorted(days)

d = DatabaseManager(**get_db_config()); d.connect()
rows = d.execute(
    'SELECT m_day,m_tid,m_tf,m_de,m_time,m_decision FROM rpl_micro '
    'WHERE m_mechanic=%s AND m_day IN (' + ','.join(['%s'] * len(days)) + ') ORDER BY m_day,m_time',
    tuple(['flip_finisher'] + days), fetch=True)
d.disconnect()
if not rows:
    print('no flip_finisher rows for %s — run build_rpl_6of9.py --persist first' % ', '.join(days)); sys.exit(1)

longs, shorts, seen = set(), set(), []
for r in rows:
    # m_time is "mmdd hh:mm:ss" UTC; pair it with m_day's year to get epoch ms
    t = int(dt.datetime.strptime(r['m_day'][:4] + r['m_time'], '%Y%m%d %H:%M:%S')
            .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
    (longs if r['m_de'] < 0 else shorts).add(t)
    seen.append((t, r['m_tid'], r['m_tf'], -r['m_de']))
longs, shorts = sorted(longs), sorted(shorts)

fT = lambda t: dt.datetime.fromtimestamp(t / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
span = days[0] + ('..' + days[-1][5:] if len(days) > 1 else '')
print('flip_finisher %s | %d events -> LONG %d (green) / SHORT %d (red)'
      % (span, len(seen), len(longs), len(shorts)))
for t, tid, tf, dd in seen:
    print('  %s  %-5s  %-8s s%d' % (fT(t), 'LONG' if dd > 0 else 'SHORT', tid, tf))


def arr(v):
    return ('array.from(' + ', '.join(str(x) for x in v) + ')') if v else 'array.new_int(0)'


# 2-bars-wide: a bar paints if an event falls in [time - w, time_close), w = bar duration -> the event's
# bar AND the following bar. Constant w on a fixed TF, so exactly 2 bars per event (build_past50_pine.py:37).
body = f'''//@version=5
indicator("flip_finisher {span} · green=long red=short (TF1 pane, 2-bar)", overlay = true)
long_t  = {arr(longs)}
short_t = {arr(shorts)}
w = time_close - time
is_long  = false
is_short = false
for i = 0 to array.size(long_t) - 1
    t = array.get(long_t, i)
    if t >= time - w and t < time_close
        is_long := true
for i = 0 to array.size(short_t) - 1
    t = array.get(short_t, i)
    if t >= time - w and t < time_close
        is_short := true
bgcolor(is_long  ? color.new(color.green, 0) : na, title = "flip_finisher_long")
bgcolor(is_short ? color.new(color.red,   0) : na, title = "flip_finisher_short")
'''
tag = days[0].replace('-', '')[4:] + ('_' + days[-1].replace('-', '')[4:] if len(days) > 1 else '')
path = f'/home/joe/thecodes/flip_finisher_{tag}.pine'
open(path, 'w').write(body)
print('-> %s' % path)
