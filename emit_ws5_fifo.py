"""emit_ws5_fifo.py - the ws5-fifo span mechanic, painted on TradingView as bgcolors. Joe 0907.

THE MECHANIC IS JOE'S. The spec lives in docs/ws5-fifo_spec.md; this file is the build. Where the two
disagree, the spec wins and this file gets rewritten.

    A span OPENS on the bar all three ws5 required lines hold the away-from-50 state AND ws5Mage is oob.
    A span CLOSES on the first bar all three ws2 required lines hold the towards-50 state.
    Required: the dr-side boundary (85 at dr +1, 15 at dr -1), Mage, m. The b line is optional.
    dr = ws5Mage oob 85/15, LATCHED. A dr flip clears every line state and cancels an open span.

THE OPEN POPULATION IS SET BY ws5 ALONE (Joe 0907: "I never asked to open the ws3 set. the ask was to
simply cross the lines that were already in play at the time of ws5 opening the span"). Every bar the
open condition NEWLY becomes true is a span. An open is never consumed, replaced or ignored by a live
span, so SPANS MAY OVERLAP and the open count does not move when the closing timeframe changes.

    THE BUG THIS REPLACES. The first build let a live span swallow later opens. Measured 08-05 -> 08-12:
    it dropped 174 of 311 opens, and which ones it dropped depended on the close timeframe - so the row
    count moved 379 / 429 / 483 for ws5 / ws3 / ws2 closing. Joe: "the latest pine (ws2 based) added a
    lot more signals, which should not have happened." He was right; the open side had no rule.

THE MAGE CROSS MUST HAPPEN NEAR OOB (Joe 0907: "what is the impact if I require the Mage to be crossed
while it's oob?" then "add a tolerance of 10"). The ws5Mage cross only puts ws5Mage into the away state
if ws5Mage was within MAGE_TOL of its dr-side boundary at the cross bar. ws5Mage must still be FULLY oob
at the open bar - the tolerance loosens the cross test, not the open gate.

THE PAINT: red = SHORT (dr +1), green = LONG (dr -1). The codebase's own mapping - the locked bgcolor
block at jig.py:789-792 pairs s_sig_short with red and s_sig_long with green. ONLY THE SPAN END IS
PAINTED, DOUBLED: the TF1 bar it ends on plus the one after it (Joe 0907: "I need the bgcolors to be
doubled for easy view - eg for 13:48, there should be a bgcolor at 13:48 and 13:49"). The span end is
the trade time, so it is the only bar carrying a decision; the leadup bars carried none.
"""
import os
import bisect
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.analysis.jig import _Score
from optimus9.compute.line_config import mech_lines, override
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key

TF_OPEN = 5                 # the timeframe whose lines OPEN the span
TF_CLOSE = 2                # the timeframe whose lines CLOSE the span. Joe 0907 "lock ws2 in"
XWOB = 6                    # bars a cross must hold before it confirms = 30 s at the 5 s grid. Joe 0907
MAGE_TOL = 10.0             # how far INSIDE the band the ws5Mage cross may sit and still count. Joe 0907
BUCKET_MS = 60_000          # TF1 - the pane Joe reads it on
FROM_UTC = '2026-08-05 00:00:00'
TO_UTC = '2026-08-19 11:59:55'      # the end of the line cache
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ws5_fifo_0805_0819.pine')


def _ms(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() * 1000)


def confirmed_crosses(x, target, lo, hi):
    """{bar: 'over'|'under'} - the repo's held() run rule with dr stripped.

    build_wsf_x_cross.held() takes dr to say which side is 'far'. This search wants crosses in BOTH
    directions, so the confirmed side is tracked instead: the side flips only once the new side has held
    XWOB consecutive bars, and the cross is stamped on the bar the run reaches XWOB - not on the bar it
    started. Same semantics otherwise. Note the repo's own XCROSS_XWOB is 5; ws5-fifo uses Joe's 6."""
    xs, tv = x.tolist(), target.tolist()
    out, conf, run, cur = {}, None, 0, None
    for k in range(lo, hi + 1):
        a, b = xs[k], tv[k]
        if a != a or b != b:                       # NaN on either line - no side to be on
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


def dr_series(mage, hi_b, lo_b, lo, hi, n):
    """ws5Mage oob 85/15, LATCHED: hold the last side touched until the other fires. Joe 0906."""
    mg = mage.tolist()
    out, cur = np.zeros(n, np.int8), 0
    for k in range(lo, hi + 1):
        v = mg[k]
        if v == v:
            if v >= hi_b:
                cur = +1
            elif v <= lo_b:
                cur = -1
        out[k] = cur
    return out


def opens(ts, op, drl, hi_b, lo_b, lo, hi):
    """[(bar, dr), ...] - every bar the open condition NEWLY becomes true. ws5 alone; no close is
    consulted, so this list is identical whatever timeframe closes the span."""
    c_m = confirmed_crosses(op['x'], op['m'], lo, hi)
    c_g = confirmed_crosses(op['x'], op['Mage'], lo, hi)
    c_hi = confirmed_crosses(op['x'], np.full(len(ts), hi_b), lo, hi)
    c_lo = confirmed_crosses(op['x'], np.full(len(ts), lo_b), lo, hi)
    mg = op['Mage'].tolist()

    state = {'boundary': None, 'Mage': None, 'm': None}
    prev, out, pdr = False, [], drl[lo]
    for k in range(lo, hi + 1):
        d = drl[k]
        if d != pdr:                               # a dr flip clears every line state
            state = {t: None for t in state}
            prev = False
        pdr = d
        if d == 0:
            continue
        away = 'over' if d > 0 else 'under'        # away from 50, per dr
        bnd = c_hi if d > 0 else c_lo              # the dr-side boundary, Joe 0819
        for key, src in (('m', c_m), ('boundary', bnd)):
            if k in src:
                state[key] = 'away' if src[k] == away else 'towards'
        if k in c_g:                               # the Mage cross carries the tolerance test
            v = mg[k]
            near = (v == v) and ((v >= hi_b - MAGE_TOL) if d > 0 else (v <= lo_b + MAGE_TOL))
            state['Mage'] = 'away' if (c_g[k] == away and near) else 'towards'
        v = mg[k]
        oob = (v == v) and ((v >= hi_b) if d > 0 else (v <= lo_b))
        now = all(s == 'away' for s in state.values()) and oob
        if now and not prev:
            out.append((k, int(d)))
        prev = now
    return out


def close_bars(ts, cl, drl, hi_b, lo_b, lo, hi):
    """[bar, ...] - every bar the close condition NEWLY becomes true, sorted."""
    c_m = confirmed_crosses(cl['x'], cl['m'], lo, hi)
    c_g = confirmed_crosses(cl['x'], cl['Mage'], lo, hi)
    c_hi = confirmed_crosses(cl['x'], np.full(len(ts), hi_b), lo, hi)
    c_lo = confirmed_crosses(cl['x'], np.full(len(ts), lo_b), lo, hi)

    state = {'boundary': None, 'Mage': None, 'm': None}
    prev, out, pdr = False, [], drl[lo]
    for k in range(lo, hi + 1):
        d = drl[k]
        if d != pdr:
            state = {t: None for t in state}
            prev = False
        pdr = d
        if d == 0:
            continue
        away = 'over' if d > 0 else 'under'
        bnd = c_hi if d > 0 else c_lo
        for key, src in (('m', c_m), ('Mage', c_g), ('boundary', bnd)):
            if k in src:
                state[key] = 'away' if src[k] == away else 'towards'
        now = all(s == 'towards' for s in state.values())
        if now and not prev:
            out.append(k)
        prev = now
    return out


def spans(ts, op, cl, drl, hi_b, lo_b, lo, hi):
    """[(open_bar, close_bar, dr), ...]. ONE CLOSE PER OPEN - the FIRST close bar after the open, inside
    the same dr run (Joe 0907: "there can only be the first ws3 close per ws5 open"). An open with no
    close before the dr flips is dropped."""
    fires = close_bars(ts, cl, drl, hi_b, lo_b, lo, hi)
    out = []
    for k, d in opens(ts, op, drl, hi_b, lo_b, lo, hi):
        j = bisect.bisect_right(fires, k)
        if j < len(fires) and drl[fires[j]] == d:
            out.append((k, fires[j], d))
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
    ln = lambda tf, r: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
                       override(tf * 60, *spec[r])) + '.npy'))
    op = {r: ln(TF_OPEN, r) for r in ('x', 'm', 'Mage')}
    cl = {r: ln(TF_CLOSE, r) for r in ('x', 'm', 'Mage')}

    # Walk from the first bar EVERY line is finite, so the cross state and the dr latch entering the
    # report range are established rather than seeded at an arbitrary midnight.
    lo = max(int(np.flatnonzero(np.isfinite(a))[0]) for a in list(op.values()) + list(cl.values()))
    hi = len(ts) - 1
    drl = dr_series(op['Mage'], hi_b, lo_b, lo, hi, len(ts)).tolist()
    all_opens = opens(ts, op, drl, hi_b, lo_b, lo, hi)
    found = spans(ts, op, cl, drl, hi_b, lo_b, lo, hi)

    a0, a1 = int(np.searchsorted(ts, _ms(FROM_UTC))), int(np.searchsorted(ts, _ms(TO_UTC)))
    # A span is IN RANGE when its CLOSE is - the close is the trade time. n_open counts opens whose
    # OPEN bar is in range, so the two are on different bases: a span can open before FROM_UTC and close
    # inside it. Reported separately; never subtracted.
    keep = [(b, e, d) for b, e, d in found if a0 <= e <= a1]
    n_open = sum(1 for k, _ in all_opens if a0 <= k <= a1)
    n_noclose = sum(1 for k, _ in all_opens if a0 <= k <= a1) - sum(1 for b, _, _ in found if a0 <= b <= a1)

    # THE SPAN END, DOUBLED. Floor the end stamp onto its TF1 bucket, then add the next bucket, so every
    # span paints exactly two adjacent chart bars.
    short_ts, long_ts = [], []
    for b, e, d in keep:
        bar = (int(ts[e]) // BUCKET_MS) * BUCKET_MS
        (short_ts if d > 0 else long_ts).extend((bar, bar + BUCKET_MS))

    streams = [                                    # ORDER IS PRIORITY - later paints over earlier
        {'name': 'fifo_short', 'ts': _Score.bucket_spans(short_ts, BUCKET_MS), 'color': 'color.red'},
        {'name': 'fifo_long', 'ts': _Score.bucket_spans(long_ts, BUCKET_MS), 'color': 'color.green'},
    ]
    notes = [
        'ws5-fifo spans. Joe 0907. spec: docs/ws5-fifo_spec.md',
        'span OPENS when the dr-side boundary, ws5Mage and ws5m all hold the AWAY-from-50 state',
        '   AND ws5Mage is oob at that bar. the ws5Mage cross only counts if ws5Mage was within',
        '   %.0f of its dr-side boundary when it crossed.' % MAGE_TOL,
        'span CLOSES on the FIRST bar the dr-side boundary, ws%dMage and ws%dm all hold the'
        % (TF_CLOSE, TF_CLOSE),
        '   TOWARDS-50 state. one close per open.',
        'the OPEN population is set by ws5 alone - an open is never consumed by a live span,',
        '   so spans may OVERLAP and the count does not move with the closing timeframe.',
        'dr = ws5Mage oob %.0f/%.0f, latched. a dr flip clears the state and cancels an open span.'
        % (hi_b, lo_b),
        'xwob %d bars = %d s, both sides. boundary is dr-side: %.0f at dr +1, %.0f at dr -1.'
        % (XWOB, XWOB * 5, hi_b, lo_b),
        'red = SHORT (dr +1)   green = LONG (dr -1)',
        'the SPAN END is painted, DOUBLED: the TF1 bar it ends on plus the one after it.',
        'range %s -> %s.' % (FROM_UTC, TO_UTC),
        '%d ws5 opens, %d closed into spans: %d short, %d long.'
        % (n_open, len(keep), sum(1 for r in keep if r[2] > 0), sum(1 for r in keep if r[2] < 0)),
    ]
    total = _Score(None).emit_bgcolor(streams, OUT, 'ws5-fifo spans 08-05 to 08-19', notes=notes)
    u = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc).strftime('%m-%d %H:%M:%S')
    print('  %s' % OUT)
    print('  open tf ws%d, close tf ws%d, xwob %d, Mage tolerance %.0f' % (TF_OPEN, TF_CLOSE, XWOB, MAGE_TOL))
    print('  %d ws5 opens with their OPEN in range; %d of those never closed before the dr flipped'
          % (n_open, n_noclose))
    print('  %d spans with their CLOSE in range: %d short, %d long'
          % (len(keep), sum(1 for r in keep if r[2] > 0), sum(1 for r in keep if r[2] < 0)))
    print('  %d TF1 stamps painted (%d short, %d long)'
          % (total, len(streams[0]['ts']), len(streams[1]['ts'])))
    print('  first span %s -> %s   last span %s -> %s'
          % (u(keep[0][0]), u(keep[0][1]), u(keep[-1][0]), u(keep[-1][1])))


if __name__ == '__main__':
    main()
