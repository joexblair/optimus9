"""THE 2026-09-03 to 09-04 LEGS AS A PINE OVERLAY, built from the banked table.

Joe 1030: *"I need a pine emit that uses red/green bgcolors to show the profitable trades, and
blue/yellow to show the losing trades, for that 09-03 to 09-04 list"*, then *"can't you just read
the onscreen table?"*.

HE IS RIGHT - IT READS days_0903.md. The legs, their directions and their nets are already banked
there from the walk that produced the table. Re-walking the chain to paint it would be 14 minutes
to recompute numbers that are on disk.

THE EPOCH IS COMPUTED FROM THE TIMESTAMP, not from the tape's index: the grid is UTC at 5 s, so a
timestamp IS its epoch. The 1-minute bar is floor(ms / 60000) * 60000, the same arithmetic
l2_barrage_emit.py uses.

THE COLOURS ARE ALL HIS. He named the losing pair himself, 1030: *"losing SHORT is blue, losing
LONG is yellow"*. The profitable pair's direction split is still mine.
    profitable LONG   green        losing LONG   yellow
    profitable SHORT  red          losing SHORT  blue

ONLY THE OPEN BAR IS PAINTED, his 1030: *"I don't need every bar painted. print only 2 consecutive
bgcolors at the OPEN bar for each trade"*. Two 1-minute bars: the open's own and the next, which is
the doubling l2_barrage.pine uses so a one-bar event is visible at TF1.
"""
import datetime as dt
import io
import os
import re
import sys

sys.path.insert(0, '/home/joe/thecodes')
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever
#   happens. Without it a refusal from v4_knobs.check() - an off-ruled run with no
#   W_V4_EXPERIMENT=1 - goes into the StringIO and the process exits 1 with NOTHING on
#   either stream. That cost a diagnosis on 1101.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    from optimus9.analysis.jig import _Score
finally:
    sys.stderr = _e

HERE = os.path.dirname(os.path.abspath(__file__))
#   THE SOURCE TABLE IS SETTABLE so the stop-on and stop-off walks each get their own overlay.
SRC = os.path.join(HERE, os.environ.get('W_SRC', 'days_0903.md'))
OUT = os.path.join(HERE, os.environ.get('W_OUT', 'legs_0903_0904.pine'))
BUCKET_MS = 60_000
DRAG = 0.1975
TS = re.compile(r'^2026-\d\d-\d\d \d\d:\d\d:\d\d$')


def ms(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
               .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


_b = lambda m: (int(m) // BUCKET_MS) * BUCKET_MS
#   THE STOP STATE COMES OFF THE SOURCE TABLE'S OWN HEADER, never off what I remember running.
STOP = 'UNREADABLE - the source table did not state it'
for L in open(SRC):
    if not L.startswith('#'):
        break
    if 'the stop is ' in L:
        STOP = L.split('the stop is ', 1)[1].strip()
rows, skipped = [], []
for L in open(SRC):
    if not L.startswith('| 2026'):
        continue
    c = [x.strip() for x in L.strip().strip('|').split('|')]
    if len(c) < 12 or not TS.match(c[0]) or c[1] not in ('LONG', 'SHORT'):
        continue
    if c[0][:10] not in ('2026-09-03', '2026-09-04'):
        continue
    if not TS.match(c[2]):
        skipped.append((c[0], c[1], 'no exit in the window, so no net'))
        continue
    net = float(c[11])
    rows.append((c[0], c[1], c[2], c[3], net))

win_l, win_s, los_l, los_s = [], [], [], []
for opn, d, ex, ct, net in rows:
    #   TWO BARS AT THE OPEN - the open's own 1-minute bar and the next one. Nothing else.
    a = _b(ms(opn))
    span = [a, a + BUCKET_MS]
    tgt = (win_l if d == 'LONG' else win_s) if net >= 0 else (los_l if d == 'LONG' else los_s)
    tgt.extend(span)

#   ORDER IS PRIORITY - a later stream paints over an earlier one on a shared minute.
streams = [
    {'name': 'losing_long', 'ts': _Score.bucket_spans(los_l, BUCKET_MS), 'color': 'color.yellow'},
    {'name': 'losing_short', 'ts': _Score.bucket_spans(los_s, BUCKET_MS), 'color': 'color.blue'},
    {'name': 'profitable_long', 'ts': _Score.bucket_spans(win_l, BUCKET_MS),
     'color': 'color.green'},
    {'name': 'profitable_short', 'ts': _Score.bucket_spans(win_s, BUCKET_MS), 'color': 'color.red'},
]
nwl = sum(1 for r in rows if r[4] >= 0 and r[1] == 'LONG')
nws = sum(1 for r in rows if r[4] >= 0 and r[1] == 'SHORT')
nll = sum(1 for r in rows if r[4] < 0 and r[1] == 'LONG')
nls = sum(1 for r in rows if r[4] < 0 and r[1] == 'SHORT')
notes = [
    'THE lineage2 CHAIN LEGS, 2026-09-03 and 2026-09-04. one colour per outcome and direction.',
    'the legs are read from days_0903.md, which v4_chain.legs produced. this file only paints.',
    '',
    'green  = profitable LONG   (%d legs)' % nwl,
    'red    = profitable SHORT  (%d legs)' % nws,
    'yellow = losing LONG       (%d legs)' % nll,
    'blue   = losing SHORT      (%d legs)' % nls,
    'THE LOSING PAIR IS HIS: "losing SHORT is blue, losing LONG is yellow" - 1030. the profitable',
    '  pair\'s direction split is MINE; he named red/green without naming a direction.',
    '',
    'ONLY THE OPEN BAR IS PAINTED - two 1-minute bars, the open\'s own and the next. his "print',
    '  only 2 consecutive bgcolors at the OPEN bar for each trade". no exit and no span is drawn.',
    'STREAM ORDER IS PRIORITY: losing_long, losing_short, profitable_long, profitable_short.',
    '',
    'net = realised MINUS drag %.4f%% a round trip. a leg at exactly 0 counts as profitable.' % DRAG,
    'THE STOP: %s' % STOP,
    '',
    'the arm: RMOM_FNC 75.0 -> (25.0, 75.0), L2_MOM_MAXTF 20, LIN2_EXFNC_LATCH_REL \'lift\',',
    '  the ws1b counter-oob cadence OFF, LIN2_MATRY_WSF_TAKEOVER_ON 0, LIN2_CASC_REV_GATE_ON 0.',
    'THE CHAIN OPENS EARLIER THAN THE WINDOW: 2026-08-29 23:53:55 SHORT, handed in. only legs',
    '  whose OPEN falls on 09-03 or 09-04 are painted.',
    '',
    'the pair was picked on the mage cascade\'s own record over 2026-08-30..09-06: 09-03 is the',
    '  worst day at 75.0%% of its reversals opening a losing leg, 09-04 the second best at 34.8%%,',
    '  and together 18 won against 17 lost.',
    '',
    '%d legs, 2 bars each, on %d 1-minute bars. the legs are in days_0903.md with their MAE,'
    ' MFE and net.'
    % (len(rows), sum(len(s['ts']) for s in streams)),
]
total = _Score(None).emit_bgcolor(streams, OUT, 'lineage2 legs 09-03 to 09-04 (TF1)', notes=notes)
print('  %s' % OUT)
print('')
print('| the read | value |')
print('|---|---|')
print('| legs painted | %d |' % len(rows))
print('| profitable LONG - green | %d |' % nwl)
print('| profitable SHORT - red | %d |' % nws)
print('| losing LONG - yellow | %d |' % nll)
print('| losing SHORT - blue | %d |' % nls)
print('| 1-minute bars painted | %d |' % total)
print('| summed net %% of the painted legs | %+.4f |' % sum(r[4] for r in rows))
for o, d, why in skipped:
    print('| skipped %s %s | %s |' % (o, d, why))
print('| the stop | %s |' % STOP)
print('| the first painted minute | %s |' % min(min(s['ts']) for s in streams if s['ts']))
print('| its UTC | %s |' % dt.datetime.fromtimestamp(
    min(min(s['ts']) for s in streams if s['ts']) / 1000, dt.timezone.utc)
    .strftime('%Y-%m-%d %H:%M:%S'))
