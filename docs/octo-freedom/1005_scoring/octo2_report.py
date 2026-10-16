"""THE OCTO2 CHAIN REPORT. 1016. Joe: *"we have an established chain report (eg the main-chain
report). please use that"*.

THE FORMAT IS `1013_report.py`'s, column for column where the column exists in octo2:
    the knob header       | knob | live value |
    the chain             | # | opens | side | how it opened | close event | why it ends |
                          | gap between legs reason | gross |  + a TOTAL row
    the gap column        Joe 1013: *"a new column that uses max 3 words to describe why a leg's
                          end is not the same timestamp as the next leg's OPEN"*
    the per-leg counts    | per leg | how it opened | ... | events | note |

ONE COLUMN THE MAIN CHAIN HAS THAT OCTO2 DOES NOT: `the chain ends`. In the main chain a leg has a
CLOSE event and then the walk continues to an END bar, so both are printed. In octo2 the side-event
that closes a trade IS its end - there is no second walk after it. The column is LEFT OUT rather
than filled with the close bar twice. STATED, not quietly dropped.

IT READS THE `dev-cache`, Joe's name: *"when I need this rebuilt for another window, I'll refer to
it as our `dev-cache`"*. No machine build - 0.24 s against ~250 s.

    python3 octo2_report.py <cache-key>
"""
import datetime as dt
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _win3 as W3

DRAG = 0.1975          # the banked drag per trade, docs/octo-freedom/1005_knobs.md:39

k = sys.argv[1] if len(sys.argv) > 1 else '5ef6b159153ee7341aab'
d = W3.load(k, log=lambda z: None)
if d is None:
    raise SystemExit('no dev-cache for key %s' % k)
ts = d['ts']
U = lambda i: dt.datetime.fromtimestamp(int(ts[int(i)]) / 1000, dt.UTC).strftime(
    '%Y-%m-%d %H:%M:%S')
PX = d['px']
rows = d.get('walk_rows')
ev = d['events']
tr = d['trades']

print()
print('| knob | live value |')
print('|---|---|')
print('| WINDOW | %s .. %s |' % (d['window_from'], d['window_to']))
print('| BARS | %d = %.1f days |' % (int(d['n']), int(d['n']) * 5 / 86400.0))
print('| the hold grid | g15ib, the g15Mage ib-cross grid |')
print('| the sample side / pairing | ws5 / fwd |')
print('| the cross fence / xwob / step | the ex-fence %.0f/%.0f / 1 bar = 5 s / 1 cross |'
      % (d['ex_lo'], d['ex_hi']))
print('| the oob fence | %.0f/%.0f |' % (d['lo_fence'], d['hi_fence']))
print('| mom-xfer | OFF |')
print('| the drag applied | %.4f%% per trade |' % DRAG)
print('| events emitted | %d |' % len(ev))
print('| rows the walk took | %s |' % ('%d' % len(rows) if rows else 'not in this cache'))
print('| the dev-cache key | %s |' % k)

# ---- the gap reason. Joe 1013: MAX THREE WORDS.
def why_gap(prev_exit, open_bar):
    if prev_exit is None:
        return 'first leg'
    if open_bar == prev_exit:
        return 'no gap'
    if open_bar < prev_exit:
        return 'pyramid overlap'
    blocked = sum(1 for b, s, src, nt in ev if prev_exit < b < open_bar)
    if blocked:
        return 'cap blocked %d' % blocked
    return 'no event'

print()
# MAE AND gross AT 2dp, Joe 1016: *"add an MAE column. 2dp. set gross to 2dp also"*.
# MAE is `max(0, adverse)` over entry -> exit, the banked definition
# (docs/octo-freedom/1005_knobs.md:37: *"Pre-entry adverse belongs to a different leg"*).
print('| # | opens | side | how it opened | close event | why it ends | gap between legs reason | '
      'MAE | gross |')
print('|---|---|---|---|---|---|---|---|---|')
tot = 0.0
prev_exit = None
for i, t in enumerate(sorted(tr, key=lambda z: z['entry']), 1):
    tot += t['gross']
    print('| %d | %s | %s | %s | %s | %s | %s | %.2f%% | %+.2f%% |'
          % (i, U(t['entry']), 'SHORT' if t['dr'] > 0 else 'LONG',
             t['source'].replace('|', '·'), U(t['exit']),
             t['exit_reason'].replace('|', '·'), why_gap(prev_exit, t['entry']),
             t['mae'], t['gross']))
    prev_exit = t['exit']
print('| **TOTAL** | — | — | — | %s | — | — | — | **%+.2f%%** |'
      % (U(max(t['exit'] for t in tr)), tot))

print()
print('| check | result |')
print('|---|---|')
print('| trades closed | %d |' % len(tr))
print('| positive | %d = %.1f%% |' % (sum(1 for t in tr if t['gross'] > 0),
                                      100.0 * sum(1 for t in tr if t['gross'] > 0) / len(tr)))
print('| gross | %+.2f%% |' % tot)
print('| drag | %.2f%% |' % (len(tr) * DRAG))
print('| **net** | **%+.2f%%** |' % (tot - len(tr) * DRAG))
print('| still open at the end | %d |' % len(d['open_at_end']))
print('| mom-xfer would have withheld | %d events |' % len(d['mx_blocked']))

print()
print('| per leg | how it opened | why it ends | held | MAE | MFE | MFE over MAE | gross |')
print('|---|---|---|---|---|---|---|---|')
for t in sorted(tr, key=lambda z: z['entry']):
    held = (t['exit'] - t['entry']) * 5
    r = (t['mfe'] / t['mae']) if t['mae'] > 0 else float('inf')
    print('| %s | %s | %s | %s | %.2f%% | %.2f%% | %s | %+.2f%% |'
          % (U(t['entry']), t['source'].replace('|', '·'), t['exit_reason'].replace('|', '·'),
             str(dt.timedelta(seconds=held)), t['mae'], t['mfe'],
             'inf' if t['mae'] == 0 else '%.2f' % r, t['gross']))

print()
print('| the day | events | rows | trades closed | gross | drag | net |')
print('|---|---|---|---|---|---|---|')
days = sorted({U(t['entry'])[:10] for t in tr} | {U(b)[:10] for b, s, sr, nt in ev})
for dy in days:
    de = [1 for b, s, sr, nt in ev if U(b).startswith(dy)]
    dr_ = [1 for r in (rows or []) if U(r['bar']).startswith(dy)]
    dt_ = [t for t in tr if U(t['entry']).startswith(dy)]
    g = sum(t['gross'] for t in dt_)
    print('| %s | %d | %s | %d | %+.2f%% | %.2f%% | %+.2f%% |'
          % (dy, len(de), '%d' % len(dr_) if rows else '—', len(dt_), g,
             len(dt_) * DRAG, g - len(dt_) * DRAG))
