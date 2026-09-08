"""emit_ws5_fifo_137.py - the SUPERSEDED ws5-fifo build, painted for Joe to read. Joe 0907.

THIS IS NOT THE MECH. The mech is emit_ws5_fifo.py, spec docs/ws5-fifo_spec.md. This file reproduces the
137-row build exactly as it stood when Joe read the MFE/MAE table and gave his 15-of-17 verdict
(eyes_on_pine seq 12), so those 17 rows can be put back on the chart against the same span set.

WHAT MAKES IT THE 137 AND NOT THE MECH:
  - A LIVE SPAN CONSUMES LATER OPENS. When a second ws5 open arrives while a span is still open, the
    earlier open is replaced. That destroyed 174 of 311 opens over 08-05 -> 08-10. Joe 0907: "I never
    asked to open the ws3 set. the ask was to simply cross the lines that were already in play at the
    time of ws5 opening the span." The mech does not do this; this file does, on purpose.
  - ws5 CLOSES THE SPAN, not ws2.
  - NO Mage-cross-oob requirement and NO tolerance. Both came later.

Everything else matches the mech: xwob 6, dr from ws5Mage oob 85/15 latched, the dr-side boundary,
ws5b optional, red = SHORT / green = LONG, the span end painted doubled onto TF1 buckets.
"""
import os
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.analysis.jig import _Score
from optimus9.compute.line_config import mech_lines, override
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key

TF = 5                      # ws5 both opens AND closes the span in this build
XWOB = 6                    # bars a cross must hold before it confirms = 30 s at the 5 s grid
BUCKET_MS = 60_000          # TF1 - the pane Joe reads it on
FROM_UTC = '2026-08-05 00:00:00'
TO_UTC = '2026-08-10 00:00:00'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ws5_fifo_137_0805_0810.pine')


def _ms(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() * 1000)


def confirmed_crosses(x, target, lo, hi):
    """{bar: 'over'|'under'} - the repo's held() run rule with dr stripped. The confirmed side flips only
    once the new side has held XWOB consecutive bars; the cross is stamped on the bar the run reaches
    XWOB, not the bar it started."""
    xs, tv = x.tolist(), target.tolist()
    out, conf, run, cur = {}, None, 0, None
    for k in range(lo, hi + 1):
        a, b = xs[k], tv[k]
        if a != a or b != b:
            run = 0
            continue
        s = a > b
        if conf is None:
            conf, run = s, 0
            continue
        if s == conf:
            run, cur = 0, None
            continue
        cur, run = (s, 1) if (cur is None or s != cur) else (cur, run + 1)
        if run >= XWOB:
            out[k] = 'over' if s else 'under'
            conf, run, cur = s, 0, None
    return out


def spans(ts, ln, hi_b, lo_b, lo, hi):
    """[(open_bar, close_bar, dr), ...] - the CONSUMING build. `opened = k` on every new all-away
    transition, which replaces a live open. That is the behaviour this file exists to reproduce."""
    c_m = confirmed_crosses(ln['x'], ln['m'], lo, hi)
    c_g = confirmed_crosses(ln['x'], ln['Mage'], lo, hi)
    c_hi = confirmed_crosses(ln['x'], np.full(len(ts), hi_b), lo, hi)
    c_lo = confirmed_crosses(ln['x'], np.full(len(ts), lo_b), lo, hi)

    mg = ln['Mage'].tolist()
    dr, cur = np.zeros(len(ts), np.int8), 0
    for k in range(lo, hi + 1):                    # ws5Mage oob, latched
        v = mg[k]
        if v == v:
            if v >= hi_b:
                cur = +1
            elif v <= lo_b:
                cur = -1
        dr[k] = cur
    drl = dr.tolist()

    state = {'boundary': None, 'Mage': None, 'm': None}
    prev_away = prev_tow = False
    opened, out, pdr = None, [], drl[lo]
    for k in range(lo, hi + 1):
        d = drl[k]
        if d != pdr:
            state = {t: None for t in state}
            prev_away = prev_tow = False
            opened = None
        pdr = d
        if d == 0:
            continue
        away = 'over' if d > 0 else 'under'
        bnd = c_hi if d > 0 else c_lo
        for key, src in (('m', c_m), ('Mage', c_g), ('boundary', bnd)):
            if k in src:
                state[key] = 'away' if src[k] == away else 'towards'
        v = mg[k]
        oob = (v == v) and ((v >= hi_b) if d > 0 else (v <= lo_b))
        all_away = all(s == 'away' for s in state.values()) and oob
        all_tow = all(s == 'towards' for s in state.values())
        if all_away and not prev_away:
            opened = k                             # <== CONSUMES any live open. the superseded rule
        if all_tow and not prev_tow and opened is not None:
            out.append((opened, k, int(d)))
            opened = None
        prev_away, prev_tow = all_away, all_tow
    return out


def main():
    db = DatabaseManager(**get_db_config())
    db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary hi, lo_boundary lo '
                      'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    hi_b, lo_b = float(sysr['hi']), float(sysr['lo'])
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _tf, sp, mo = g['override']
            spec[g['role']] = (sp, mo)
    db.disconnect()

    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sysr['s'], 'len': sysr['l']}) + '.npz'))['__ts__']
    ln = {r: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
          override(TF * 60, *spec[r])) + '.npy')) for r in ('x', 'm', 'Mage')}

    lo = max(int(np.flatnonzero(np.isfinite(a))[0]) for a in ln.values())
    hi = len(ts) - 1
    found = spans(ts, ln, hi_b, lo_b, lo, hi)

    a0, a1 = int(np.searchsorted(ts, _ms(FROM_UTC))), int(np.searchsorted(ts, _ms(TO_UTC)))
    keep = [(b, e, d) for b, e, d in found if a0 <= e <= a1]

    short_ts, long_ts = [], []
    for b, e, d in keep:                           # THE SPAN END, DOUBLED
        bar = (int(ts[e]) // BUCKET_MS) * BUCKET_MS
        (short_ts if d > 0 else long_ts).extend((bar, bar + BUCKET_MS))

    streams = [
        {'name': 'fifo137_short', 'ts': _Score.bucket_spans(short_ts, BUCKET_MS), 'color': 'color.red'},
        {'name': 'fifo137_long', 'ts': _Score.bucket_spans(long_ts, BUCKET_MS), 'color': 'color.green'},
    ]
    notes = [
        'ws5-fifo, THE SUPERSEDED 137-ROW BUILD. Joe 0907. NOT the mech.',
        'the mech is emit_ws5_fifo.py / docs/ws5-fifo_spec.md.',
        'this build differs in three ways, on purpose:',
        '  1. a LIVE SPAN CONSUMES LATER OPENS - 174 of 311 opens destroyed over this window.',
        '  2. ws5 closes the span, not ws2.',
        '  3. no Mage-cross-oob requirement and no tolerance.',
        'span OPENS when the dr-side boundary, ws5Mage and ws5m all hold the AWAY-from-50 state',
        '   AND ws5Mage is oob at that bar. ws5b optional.',
        'span CLOSES when all three hold the TOWARDS-50 state.',
        'dr = ws5Mage oob %.0f/%.0f, latched. a dr flip clears the state and cancels an open span.'
        % (hi_b, lo_b),
        'xwob %d bars = %d s. boundary is dr-side: %.0f at dr +1, %.0f at dr -1.'
        % (XWOB, XWOB * 5, hi_b, lo_b),
        'red = SHORT (dr +1)   green = LONG (dr -1)',
        'the SPAN END is painted, DOUBLED: the TF1 bar it ends on plus the one after it.',
        'range %s -> %s.' % (FROM_UTC, TO_UTC),
        '%d spans: %d short, %d long.' % (len(keep), sum(1 for r in keep if r[2] > 0),
                                          sum(1 for r in keep if r[2] < 0)),
    ]
    total = _Score(None).emit_bgcolor(streams, OUT, 'ws5-fifo 137 (superseded) 08-05 to 08-10',
                                      notes=notes)
    u = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc).strftime('%m-%d %H:%M:%S')
    print('  %s' % OUT)
    print('  %d spans: %d short (red), %d long (green)'
          % (len(keep), sum(1 for r in keep if r[2] > 0), sum(1 for r in keep if r[2] < 0)))
    print('  %d TF1 stamps painted (%d short, %d long)'
          % (total, len(streams[0]['ts']), len(streams[1]['ts'])))
    print('  first span end %s   last span end %s' % (u(keep[0][1]), u(keep[-1][1])))


if __name__ == '__main__':
    main()
