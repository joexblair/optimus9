"""build_past50_pine — emit the RAW past-50 signals as a TF1-pane Pine (Joe 0726). SAVED.
Double-print red/green bgcolors, transp=0 (opaque): green = LONG entry bar, red = SHORT. RAW mechanic (no finisher,
no gate) — the pure triggers. Signals are 5s event-tape.
DEFAULT (Joe 0726): each signal paints 2 bars wide (its bar + the next), so it's visible on a TF1 pane.
Usage: build_past50_pine.py [YYYY-MM-DD ...]   (default 2026-06-12; multiple days -> one combined file).
"""
import sys
import datetime as dt
import build_past50 as P

DAY = 86400 * 1000
argdays = [a for a in sys.argv[1:] if a[:4].isdigit()]
days = [dt.datetime.strptime(a, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc) for a in argdays] or [
    dt.datetime(2026, 6, 12, tzinfo=dt.timezone.utc)]
days = sorted(days)

longs, shorts, rows = set(), set(), []
for d0 in days:
    S = int(d0.timestamp() * 1000); E = S + DAY
    for oi, de, trig in P.setups(S, E):                      # RAW: a_variant 'both', no finisher, no gate
        for ti, tf, br in trig:
            t = int(P.te[ti]); d = -de
            (longs if d > 0 else shorts).add(t)
            rows.append((t, d, tf, br))
longs, shorts = sorted(longs), sorted(shorts)
fT = lambda t: dt.datetime.utcfromtimestamp(t / 1000).strftime('%m-%d %H:%M:%S')
span = days[0].strftime('%Y-%m-%d') + ('..' + days[-1].strftime('%m-%d') if len(days) > 1 else '')
print('past-50 RAW signals %s | LONG %d (green) / SHORT %d (red)' % (span, len(longs), len(shorts)))
for t, d, tf, br in sorted(rows):
    print('  %s  %-5s s%d  Branch %s' % (fT(t), 'LONG' if d > 0 else 'SHORT', tf, br))


def arr(v):
    return ('array.from(' + ', '.join(str(x) for x in v) + ')') if v else 'array.new_int(0)'


# 2-bars-wide (Joe 0726): a bar paints if a signal falls in [time - w, time_close), w = bar duration -> the
# signal's bar AND the following bar. Constant w on a fixed TF, so this is exactly 2 bars per signal.
body = f'''//@version=5
indicator("past-50 RAW {span} · green=long red=short (TF1 pane, 2-bar)", overlay = true)
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
bgcolor(is_long  ? color.new(color.green, 0) : na, title = "past50_long")
bgcolor(is_short ? color.new(color.red,   0) : na, title = "past50_short")
'''
tag = days[0].strftime('%m%d') + ('_' + days[-1].strftime('%m%d') if len(days) > 1 else '')
path = f'/home/joe/thecodes/past50_raw_{tag}.pine'
open(path, 'w').write(body)
print('-> %s' % path)
