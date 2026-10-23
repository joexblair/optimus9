"""The backstop DEFERRED TO LINEAGE. Joe 1022: *"we need to defer to lineage before placing the
signal"* / *"these need lineage applied. eg 08-31 0335 would be lineage walked to 0401, then the
SHORT would open"*.

THE CHAIN. A backstop fire is a candidate, not a trade. Lineage walks from the ws5r reversal that
fired it, and the trade opens on the bar AFTER lineage prints EXHAUST.

MY CHOICES, all stated rather than defaulted:
  the anchor     the ws5r reversal the backstop fired on, NOT the fire bar. The fire can be later
                 than the reversal when the pool oob lands after it, and lineage walks the reversal.
  the start TF   BANKED 1023. The LOWEST rung of the contiguous same-side oob run holding ws5, read
                 at the FIRE bar. Joe: *"at v4-ws5rbackstop's signal, find the highest same-side
                 oob ws{1-maxTF}r and pass it to lineage"*, then *"swap `highest` with `lowest`"*,
                 and on a set of ws4/ws5/ws7: *"why is ws7 there?  the v4lineage spec only allows
                 jumps of +1"* - so the run must be CONSECUTIVE. It was always ws5 before.
                 CONFIRMED on the 2026-09-01 19:15:35 fire: run ws4-ws5, start ws4, EXHAUST
                 19:39:55, and Joe: *"19:39 is a good result"*.
  the open bar   max(EXHAUST, the fire) + 1. Measured 1023: 4 of 911 walks exhaust BEFORE their own
                 fire bar, by up to 5.9 min, because the walk anchors on the raw reversal while the
                 fire waits up to BSTOP_SYNC_MIN for its oob partner. The guard lives here so no
                 caller can forget it.
  the side       the backstop's, which is ws5r's own oob side. The walk follows it up the ladder.
  the bound      the forward search ends at the SCAN WINDOW's end. That is the data's edge, not a
                 cap on the mech - a walk that reaches it is reported UNRESOLVED, never guessed.
  no EXHAUST     a walk that returns NO IB CROSS or NO REVERSAL opens no trade. It is counted.
  one at a time  Joe #40: *"accept the first open signal"*. A later EXHAUST at or before the open
                 trade's entry is dropped; the next one after it flips the position, which is what
                 rev-trade means.
  the exit       the next accepted EXHAUST. There is still no exit mech - #17 is held back - so the
                 sequence is the backstop-plus-lineage chained to itself, not the machine.

usage: v4_deferred_trades.py '2026-08-30 00:00:00' '2026-09-06 23:59:55' window
"""
import sys
import io

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
import v4_backstop as BS
import v4_lineage_trace as LT
from v4_backstop_trades import prices


def start_tf(R, d, fallback=None):
    """The start TF for one fire: the BOTTOM of the walkable run holding ws5. -> tf or None.

    `fallback` is what to use when ws5r is not same-side oob at the fire bar, so no run exists.
    None means the fire produces no walk at all. NOT RULED by Joe - the caller passes it.
    """
    r = K.walkable_run(R, d['fire'], d['side'])
    return r[0] if r else fallback


def defer(fires, R, B, fallback=None):
    """Each fire -> its lineage verdict. -> rows, chronological by the fire."""
    out = []
    for d in fires:
        stf = start_tf(R, d, fallback)
        if stf is None:
            out.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'],
                        'side': d['side'], 'dir': d['dir'], 'verdict': 'NO WALKABLE RUN',
                        'exh': None, 'steps': 0, 'start_tf': None})
            continue
        v, bar, rows = LT.walk(R, stf, d['side'], d['rev'], B, log=lambda *a: None)
        unresolved = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
        out.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'],
                    'side': d['side'], 'dir': d['dir'],
                    'verdict': 'UNRESOLVED' if unresolved else v, 'exh': None if unresolved else bar,
                    'steps': len(rows), 'start_tf': stf})
    return out


def accept(rows):
    """One signal per EXHAUST bar. -> the accepted signals, chronological by EXHAUST.

    WHAT THIS ACTUALLY DOES, corrected 1023. The docstring used to promise *"a later EXHAUST at or
    before the open trade's entry is dropped"*, and the 1023 audit showed `r['exh'] <= last` can
    only ever fire on an exact TIE, because `ok` is already sorted ascending by `exh`. So this is
    a de-duplicator, not a one-at-a-time rule: 602 fires collapsed to 356 distinct EXHAUST bars
    across 151 tie groups.

    POSITIONS THEREFORE OVERLAP, AND JOE 1023 RULED THAT THEY MAY: *"let's see how that plays out.
    if hedging is profitable and causal, I'm not against it. it will need a safe max_pyramid
    setting that only the account (leverage) can provide"*. `max_pyramid` is his knob, default
    UNLIMITED, reported per level rather than chosen here.

    THE TIE-BREAK IS NOW EXPLICIT: (exh, fire), so the earliest-firing signal wins a tie. It used
    to rest on the sort being stable, and the audit found 151 tie groups - none mixed-direction on
    this data, but nothing here prevented it.
    """
    ok = sorted([r for r in rows if r['verdict'] == 'EXHAUST' and r['exh'] is not None],
                key=lambda r: (r['exh'], r['fire']))
    acc, last = [], -1
    for r in ok:
        if r['exh'] <= last:
            continue
        acc.append(r)
        last = r['exh']
    return acc


def chain(acc, close, hi, lo):
    """Each accepted EXHAUST closes the trade the previous one opened."""
    out = []
    for a, b in zip(acc, acc[1:]):
        en, ex = a['exh'] + 1, b['exh']
        if ex <= en:
            continue
        dd = 1 if a['dir'] == 'LONG' else -1
        p0, p1 = float(close[en]), float(close[ex])
        h = float(np.nanmax(hi[en:ex + 1])); l = float(np.nanmin(lo[en:ex + 1]))
        out.append({'en': en, 'ex': ex, 'dir': a['dir'], 'p0': p0, 'p1': p1,
                    'net': (p1 - p0) / p0 * 100.0 * dd,
                    'mfe': ((h - p0) if dd > 0 else (p0 - l)) / p0 * 100.0,
                    'mae': ((l - p0) if dd > 0 else (p0 - h)) / p0 * 100.0,
                    'bars': ex - en + 1, 'fire': a['fire'], 'rev': a['rev']})
    return out


if __name__ == '__main__':
    A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
    ow = sys.argv[3]
    R = {t: ln.line('ws%dr' % t) for t in range(1, K.TF_CEILING + 3)}
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    f = BS.scan(A, B, R, MG, ln.U, 'lift', ow)
    rows = defer(f, R, B)
    acc = accept(rows)
    tr = chain(acc, close, hi, lo)
    print('# control ws5r 2026-09-03 00:35:00 = %.2f (DB-ruled known-good 12.48; the BANKED k6 rsi8 stc6 line reads 6.77 there)'
          % R[5][ln.K('2026-09-03 00:35:00')])
    print('# RULED_OK %s. oob_when %r. %s .. %s' % (K.RULED_OK, ow, ln.U(A), ln.U(B)))
    print('# every fire deferred to lineage. the trade opens the bar AFTER EXHAUST.')
    print()
    print('| the backstop fire | its ws5r reversal | side | lineage | EXHAUST | the lag, reversal to EXHAUST | accepted |')
    print('|---|---|---|---|---|---|---|')
    accset = set(id(r) for r in acc)
    for r in rows:
        print('| %s | %s | %s | %s | %s | %s | %s |'
              % (ln.U(r['fire']), ln.U(r['rev']), 'high' if r['side'] > 0 else 'low', r['verdict'],
                 ln.U(r['exh']) if r['exh'] else '-',
                 '%d s' % ((r['exh'] - r['rev']) * 5) if r['exh'] else '-',
                 'YES' if id(r) in accset else 'no'))
    print()
    print('| the funnel | value |')
    print('|---|---|')
    print('| backstop fires | %d |' % len(rows))
    for v in ('EXHAUST', 'NO IB CROSS', 'NO REVERSAL', 'UNRESOLVED'):
        n = sum(1 for r in rows if r['verdict'] == v)
        if n: print('| lineage returned %s | %d |' % (v, n))
    print('| accepted, one trade at a time | %d |' % len(acc))
    print('| closed trades | %d |' % len(tr))
    if not tr:
        sys.exit(0)
    print()
    print('| the entry | dir | entry px | the exit | exit px | bars | net %% | MFE %% | MAE %% |')
    print('|---|---|---|---|---|---|---|---|---|')
    for t in tr:
        print('| %s | %s | %.5f | %s | %.5f | %d | %+.3f | %+.3f | %+.3f |'
              % (ln.U(t['en']), t['dir'], t['p0'], ln.U(t['ex']), t['p1'], t['bars'],
                 t['net'], t['mfe'], t['mae']))
    n = np.array([t['net'] for t in tr]); mf = np.array([t['mfe'] for t in tr])
    ma = np.array([t['mae'] for t in tr]); bb = np.array([t['bars'] for t in tr])
    print()
    print('| the summary | value |')
    print('|---|---|')
    print('| trades | %d |' % len(tr))
    print('| net, summed | %+.3f%% |' % n.sum())
    print('| net, mean | %+.4f%% |' % n.mean())
    print('| winners | %d of %d |' % (int((n > 0).sum()), len(n)))
    print('| the best | %+.3f%% |' % n.max())
    print('| the worst | %+.3f%% |' % n.min())
    print('| MFE, mean | %+.3f%% |' % mf.mean())
    print('| MAE, mean | %+.3f%% |' % ma.mean())
    print('| MFE over MAE, on the means | %.2f |' % (mf.mean() / abs(ma.mean())))
    print('| the hold, median | %d bars = %d s |' % (int(np.median(bb)), int(np.median(bb)) * 5))
    print('| LONG | %d, net %+.3f%% |' % (sum(1 for t in tr if t['dir'] == 'LONG'),
          sum(t['net'] for t in tr if t['dir'] == 'LONG')))
    print('| SHORT | %d, net %+.3f%% |' % (sum(1 for t in tr if t['dir'] == 'SHORT'),
          sum(t['net'] for t in tr if t['dir'] == 'SHORT')))
