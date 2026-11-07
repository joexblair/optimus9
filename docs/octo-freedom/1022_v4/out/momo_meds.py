"""The three fdm2-momo medians re-measured for his 1106 maxTF 10, and every report-only read.

HIS 1106 RULINGS, verbatim:
  1  maxTF            *"set it at 10"*  - LIVE, on r-pred and on Mage-beyond-x
  2  the towards gate *"report-only on this: step1's own precedent calls towards() on closed-prev"*
  3  cross + count    *"either one firing is enough.  let's make this reporting-only"*
  4  a cross rev-trade*"report-only: subtracts one from the 3"*
  5  the cross count  *"report-only"*
  6  pinned's maxTF   *"unsure.  report on both ws10 and ws12"*
  and *"no need to recreate the 94.5 day data yet"* / *"go for A"* - re-measure Mage-beyond-x's
  median on the capped set and give r-pred a floor of 1 instead of a median.

WHY IT EXISTS. FDM2_MOMO_MED_MX 7 was measured on the 27-line set ws4..ws30. On his 7-line set
ws4..ws10 "the count is under 7 out of 7" is true for every count from 0 to 6, so the vote stops
discriminating. The median has to be re-measured on the carrier set it is applied to, and his
instruction rules out re-running the fdm2 leg chain.

SO IT READS THE CACHED CAD WALKS, NOT THE CHAIN. latch_cache.json holds every truncation's cad
walk first bar and its side from the 94.5-day harvest, so the counts can be recomputed with ONE
tape load and no leg walk. Nothing is re-derived and nothing is overwritten.

TWO POPULATIONS, BECAUSE THE RCA CHANGED WHICH BARS THE VOTE IS READ AT:

  walk0   the 417 cad-walk FIRST bars. THE CONTROL: the banked medians were measured here, so the
          emerging ws4..ws30 answer must come back 0 / 7 / 9 or this run is measuring the wrong
          bars and none of its numbers may be quoted. My first draft harvested the TRUNCATION bar
          instead and the mismatch is what caught it.
  span    every bar of every cad walk - walk0 to walk0 + FDM_XCAD_WALK_MIN, 121 bars each. This is
          the population his per-bar vote is actually read at, and it is what the live medians now
          owe their value to.

THE SPAN IS A SUPERSET OF WHAT THE CAD WALK REACHES. A cad walk stops at its first bar that both
passes the truncation test and is not vetoed, and which bar that is depends on the vote itself - so
measuring over the realised prefix would define the median in terms of its own answer. The full
121-bar span is the non-circular choice and the only one taken here.

THE REPORT-ONLY READS STAY ON walk0. Rulings 2 to 5 never vote, and the `towards` gate costs an
opposed-extremum scan per line per bar, which is 1.36M scans on the span.
"""
import io
import json
import os
import statistics as st
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.environ.setdefault('W_V4_EXPERIMENT', '1')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import ln
finally:
    sys.stderr = _e

CACHE = '/home/joe/.claude/jobs/7c82535c/tmp/latch_cache.json'
XW = max(1, int(os.environ.get('W_MEDS_XWIN', '12')))      # his "last minute" = 12 bars = 60 s
CAPS = [int(x) for x in os.environ.get('W_MEDS_CAPS', '10,12,30').split(',')]
BANKED = (int(K.FDM2_MOMO_FLOOR_RPRED), int(K.FDM2_MOMO_MED_MX), int(K.FDM2_MOMO_MED_PIN))

LN = F2.load()
NB = len(LN['close'])
M = F2._momo_lines(LN)
TFS = list(M['tfs'])
ROWS = [r for r in json.load(open(CACHE)) if 0 <= int(r['walk0']) < NB]
WALKB = int(round(float(K.FDM_XCAD_WALK_MIN) * 60.0 / 5.0))      # 10.0 min = 120 bars

#   the two populations, as parallel bar/side arrays
W_BAR = np.array([int(r['walk0']) for r in ROWS], int)
W_SID = np.array([int(r['side']) for r in ROWS], int)
sb, ss = [], []
for r in ROWS:
    b0, sd = int(r['walk0']), int(r['side'])
    hi = min(b0 + WALKB, NB - 1)
    sb.extend(range(b0, hi + 1))
    ss.extend([sd] * (hi - b0 + 1))
S_BAR, S_SID = np.array(sb, int), np.array(ss, int)

MGA, XSA, DIF = {}, {}, {}
for rd in ('emerging', 'closed_prev'):
    mg = LN['CPM'] if rd == 'closed_prev' else LN['MGE']
    xs = M['XCP'] if rd == 'closed_prev' else M['XEM']
    for t in TFS:
        MGA[(rd, t)] = np.asarray(mg[t], float)
        XSA[(rd, t)] = np.asarray(xs[t], float)
        DIF[(rd, t)] = XSA[(rd, t)] - MGA[(rd, t)]


def counts(bars, sides, rd, cap):
    """The three live signal counts at each (bar, side), over ws4..ws{cap}. -> 3 int arrays.

    Vectorised over the bars: 50,457 span bars x 27 lines in pure python is 1.4M dict lookups per
    signal, and the answer is three boolean sums that numpy does in one pass per line.
    """
    n = len(bars)
    nr = np.zeros(n, int)
    nx = np.zeros(n, int)
    npn = np.zeros(n, int)
    for t in [t for t in TFS if t <= cap]:
        nr += (np.asarray(M[('RP', rd, t)], int)[bars] == sides).astype(int)
        d = MGA[(rd, t)][bars] - XSA[(rd, t)][bars]
        nx += (np.isfinite(d) & (d * sides > 0)).astype(int)
        #   pinned is read on EMERGING whatever FDM2_MOMO_READ says - a pin is a lift-off read
        for sd in (+1, -1):
            m = sides == sd
            if m.any():
                npn[m] += np.asarray(M[('PIN', t, sd)], bool)[bars[m]].astype(int)
    return nr, nx, npn


def med(v):
    return float(np.median(v)) if len(v) else float('nan')


def row(*c):
    print('| ' + ' | '.join(str(x) for x in c) + ' |')


def head(*c):
    row(*c)
    row(*(['---'] * len(c)))


#   ── THE CONTROL: the banked medians must reproduce on walk0, emerging, ws4..ws30 ──────────────
cr, cx, cp = counts(W_BAR, W_SID, 'emerging', 30)
CTRL = (med(cr), med(cx), med(cp))
CTRL_OK = tuple(int(x) for x in CTRL) == BANKED
#   and the counts themselves must BE momo_vote's answer, bar for bar
for j in range(len(ROWS)):
    v = F2.momo_vote(LN, int(W_BAR[j]), int(W_SID[j]))
    assert v['read'] == 'emerging', 'FDM2_MOMO_READ is not emerging, the control is void'
    assert (v['rpred'], v['mx'], v['pin']) == (int(cr[j]), int(cx[j]), int(cp[j])), \
        'the harvest and momo_vote disagree at %s' % ln.U(int(W_BAR[j]))

print('| the run | value |')
print('|---|---|')
row('the tape', '%d bars, %s .. %s' % (NB, ln.U(0), ln.U(NB - 1)))
row('the cad walks', '%d, from the 94.5-day harvest' % len(ROWS))
row('walk0, the control population', '%d cad-walk FIRST bars' % len(W_BAR))
row('span, the per-bar population', '%d bars - every bar of every cad walk, %d bars each'
    % (len(S_BAR), WALKB + 1))
row('the cad walk length', 'FDM_XCAD_WALK_MIN %.1f min = %d bars, so %d read bars'
    % (float(K.FDM_XCAD_WALK_MIN), WALKB, WALKB + 1))
row('the carriers', 'ws%d..ws%d, capped at ws%s' % (TFS[0], TFS[-1],
                                                    ', ws'.join(str(c) for c in CAPS)))
row('the cross window', '%d bars = %d s, his "last minute"' % (XW, XW * 5))
row('THE CONTROL', 'walk0 emerging ws4..ws30 medians are %g / %g / %g against the banked %d / %d'
                   ' / %d - %s' % (*CTRL, *BANKED,
                                   'REPRODUCED' if CTRL_OK else 'MISMATCH, nothing below is usable'))
row('the stop', 'every leg outcome in the cache carries FDM_MAE_CAP 1.10%')

print()
print('# the three LIVE counts on the span - the population his per-bar vote reads')
print()
head('the read', 'the carriers', 'the signal', 'bars', 'median', 'p25', 'p75', 'min', 'max',
     'the banked knob', 'against this median')
SPAN = {}
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        SPAN[(rd, cap)] = counts(S_BAR, S_SID, rd, cap)
        n = len([t for t in TFS if t <= cap])
        for sig, v, nm, bk in (('rpred', SPAN[(rd, cap)][0], 'FDM2_MOMO_FLOOR_RPRED', BANKED[0]),
                               ('mx', SPAN[(rd, cap)][1], 'FDM2_MOMO_MED_MX', BANKED[1]),
                               ('pin', SPAN[(rd, cap)][2], 'FDM2_MOMO_MED_PIN', BANKED[2])):
            row(rd, 'ws4..ws%d = %d lines' % (cap, n), sig, len(v), '%g' % med(v),
                '%g' % np.percentile(v, 25), '%g' % np.percentile(v, 75), int(v.min()),
                int(v.max()), '%s %d' % (nm, bk),
                'the same' if med(v) == bk else 'MOVES to %g' % med(v))

print()
print('# the same three counts on walk0 - the bars the banked medians came from')
print()
head('the read', 'the carriers', 'the signal', 'bars', 'median', 'p25', 'p75', 'min', 'max')
WLK = {}
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        WLK[(rd, cap)] = counts(W_BAR, W_SID, rd, cap)
        n = len([t for t in TFS if t <= cap])
        for sig, v in zip(('rpred', 'mx', 'pin'), WLK[(rd, cap)]):
            row(rd, 'ws4..ws%d = %d lines' % (cap, n), sig, len(v), '%g' % med(v),
                '%g' % np.percentile(v, 25), '%g' % np.percentile(v, 75), int(v.min()),
                int(v.max()))

print()
print('# HIS OPTION A on the span - r-pred floored at 1, Mage-beyond-x re-measured, pinned as is')
print()
head('the read', 'the carriers', 'r-pred test', 'r-pred fires', 'Mage-beyond-x test',
     'Mage-beyond-x fires', 'pinned test', 'pinned fires', 'any vote a constant')
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        n = len([t for t in TFS if t <= cap])
        nr, nx, npn = SPAN[(rd, cap)]
        mm = int(med(nx))
        mp = int(med(npn)) if cap != 30 else BANKED[2]
        f1 = int((nr >= 1).sum())
        f2 = int((nx < mm).sum())
        f3 = int((npn >= mp).sum())
        tot = len(nr)
        const = [lab for lab, f in (('r-pred', f1), ('Mage-beyond-x', f2), ('pinned', f3))
                 if f in (0, tot)]
        row(rd, 'ws4..ws%d = %d lines' % (cap, n), 'count >= 1',
            '%d of %d = %.1f%%' % (f1, tot, f1 / tot * 100.0),
            'count < %d (re-measured)' % mm, '%d of %d = %.1f%%' % (f2, tot, f2 / tot * 100.0),
            'count >= %d%s' % (mp, '' if cap != 30 else ' (banked)'),
            '%d of %d = %.1f%%' % (f3, tot, f3 / tot * 100.0),
            ', '.join(const) if const else 'none - all three discriminate')

print()
print('# HIS OPTION A - the vote tally on the span, against the banked medians')
print()
head('the read', 'the carriers', 'the medians used', '0 votes', '1 vote', '2 votes', '3 votes',
     'bars the vote fires on', 'the share')
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        n = len([t for t in TFS if t <= cap])
        nr, nx, npn = SPAN[(rd, cap)]
        mm = int(med(nx))
        mp = int(med(npn)) if cap != 30 else BANKED[2]
        for lab, (tr, tm, tp, ge) in (
                ('the banked 0 / 7 / 9', (BANKED[0], BANKED[1], BANKED[2], True)),
                ('HIS A - 1 / %d / %d' % (mm, mp), (1, mm, mp, True))):
            v = ((nr >= tr).astype(int) + (nx < tm).astype(int) + (npn >= tp).astype(int))
            tally = [int((v == i).sum()) for i in range(4)]
            fires = int((v >= int(K.FDM2_MOMO_VOTES)).sum())
            row(rd, 'ws4..ws%d = %d lines' % (cap, n), lab, *tally, fires,
                '%.1f%%' % (fires / len(v) * 100.0))

print()
print('# HIS OPTION A AS RULED - r-pred and Mage-beyond-x at maxTF 10, pinned still on ws4..ws30')
print()
#   HIS RULING 6 LEFT PINNED LIVE ON THE FULL SET: *"unsure.  report on both ws10 and ws12"*. So
#   the live vote is a MIX of carrier sets, not one cap across all three, and the tally has to be
#   taken on that mix. Every all-three-capped row above is a different combination.
head('the read', 'r-pred, ws4..ws%d' % CAPS[0], 'Mage-beyond-x, ws4..ws%d' % CAPS[0],
     'pinned, ws4..ws30', '0 votes', '1 vote', '2 votes', '3 votes', 'the vote fires on',
     'the share')
MIX = {}
for rd in ('emerging', 'closed_prev'):
    for cap in [c for c in CAPS if c != 30]:
        nr = SPAN[(rd, cap)][0]
        nx = SPAN[(rd, cap)][1]
        npn = SPAN[(rd, 30)][2]
        mm = int(med(nx))
        v = ((nr >= 1).astype(int) + (nx < mm).astype(int)
             + (npn >= BANKED[2]).astype(int))
        tally = [int((v == i).sum()) for i in range(4)]
        fires = int((v >= int(K.FDM2_MOMO_VOTES)).sum())
        MIX[(rd, cap)] = (1, mm, BANKED[2], fires, len(v))
        row(rd, 'count >= 1 (%d of %d = %.1f%%)'
            % (int((nr >= 1).sum()), len(nr), (nr >= 1).sum() / len(nr) * 100.0),
            'count < %d (%d of %d = %.1f%%)'
            % (mm, int((nx < mm).sum()), len(nx), (nx < mm).sum() / len(nx) * 100.0),
            'count >= %d (%d of %d = %.1f%%)'
            % (BANKED[2], int((npn >= BANKED[2]).sum()), len(npn),
               (npn >= BANKED[2]).sum() / len(npn) * 100.0),
            *tally, fires, '%.1f%%' % (fires / len(v) * 100.0))

print()
print('# the knob values HIS OPTION A asks for, at maxTF %d' % CAPS[0])
print()
head('the knob', 'banked now', 'HIS A', 'the carrier set it is applied to', 'the test',
     'how it was set')
for rd in ('emerging',):
    cap = CAPS[0]
    fl, mm, mp, fires, tot = MIX[(rd, cap)]
    row('FDM2_MOMO_MAX_TF', 'does not exist', cap, 'r-pred and Mage-beyond-x',
        'lines ws4..ws%d' % cap, 'HIS 1106 *"set it at 10"*')
    row('FDM2_MOMO_FLOOR_RPRED', BANKED[0], '%d - A FLOOR, NOT A MEDIAN' % fl,
        'ws4..ws%d = %d lines' % (cap, len([t for t in TFS if t <= cap])), 'count >= %d' % fl,
        "HIS A - at least one carrier predicted. Its median is 0 on every set, so a median "
        "cannot be used")
    row('FDM2_MOMO_MED_MX', BANKED[1], mm,
        'ws4..ws%d = %d lines' % (cap, len([t for t in TFS if t <= cap])), 'count < %d' % mm,
        'the median over the %d span bars, %s' % (tot, 'UNCHANGED from the banked value'
                                                  if mm == BANKED[1] else 'moved'))
    row('FDM2_MOMO_MED_PIN', BANKED[2], mp, 'ws4..ws30 = 27 lines', 'count >= %d' % mp,
        'UNCHANGED - his ruling 6 left pinned on the full set')
    row('FDM2_MOMO_VOTES', int(K.FDM2_MOMO_VOTES), int(K.FDM2_MOMO_VOTES), 'the three signals',
        '%d of 3' % int(K.FDM2_MOMO_VOTES), 'unchanged, and now every vote discriminates')

#   ── the report-only reads, rulings 2 to 5, on walk0 ───────────────────────────────────────────
GATE, CROSS = {}, {}
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        GATE[(rd, cap)] = []
        CROSS[(rd, cap)] = ([], [], [])
    for j, r in enumerate(ROWS):
        b, sd = int(W_BAR[j]), int(W_SID[j])
        per = {}
        for t in TFS:
            hit = int(M[('RP', rd, t)][b]) == sd
            gated = hit and bool(F2.towards(LN['CPR'][t], t, b, sd))
            w = DIF[(rd, t)][max(0, b - XW): b + 1]
            dirn = 0
            for i in range(1, len(w)):
                a, c = w[i - 1], w[i]
                if np.isfinite(a) and np.isfinite(c) and a != 0.0 and (a > 0) != (c > 0):
                    dirn = -1 if a > 0 else +1          # -1 = x crossed UNDER Mage
            per[t] = (hit, gated, dirn)
        for cap in CAPS:
            sub = [t for t in TFS if t <= cap]
            GATE[(rd, cap)].append(sum(1 for t in sub if per[t][1]))
            cr_ = sum(1 for t in sub if per[t][2] != 0)
            wk = sum(1 for t in sub if per[t][2] != 0 and (per[t][2] < 0) == (sd < 0))
            CROSS[(rd, cap)][0].append(cr_)
            CROSS[(rd, cap)][1].append(wk)
            CROSS[(rd, cap)][2].append(cr_ - wk)

print()
print('# REPORT-ONLY, ruling 2 - the closed-prev `towards` gate on r-pred, at walk0')
print()
head('the read', 'the carriers', 'r-pred median', 'gated median', 'bars the gate removes a line',
     'of bars', 'the share', 'lines removed, total')
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        n = len([t for t in TFS if t <= cap])
        raw = WLK[(rd, cap)][0]
        g = np.array(GATE[(rd, cap)], int)
        cut = raw - g
        row(rd, 'ws4..ws%d = %d lines' % (cap, n), '%g' % med(raw), '%g' % med(g),
            int((cut > 0).sum()), len(cut), '%.1f%%' % ((cut > 0).sum() / len(cut) * 100.0),
            int(cut.sum()))

print()
print('# REPORT-ONLY, rulings 3, 4 and 5 - the x-crosses-Mage read, at walk0')
print()
head('the read', 'the carriers', 'bars with at least one cross', 'of bars', 'the share',
     'cross lines, median', 'cross lines, max', '`walk` votes, median',
     '`rev-trade` votes, median', 'bars with a `rev-trade` vote', 'bars with both vote kinds')
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        n = len([t for t in TFS if t <= cap])
        c, w, rv = (np.array(x, int) for x in CROSS[(rd, cap)])
        row(rd, 'ws4..ws%d = %d lines' % (cap, n), int((c > 0).sum()), len(c),
            '%.1f%%' % ((c > 0).sum() / len(c) * 100.0), '%g' % med(c), int(c.max()),
            '%g' % med(w), '%g' % med(rv), int((rv > 0).sum()),
            int(((w > 0) & (rv > 0)).sum()))

print()
print('# REPORT-ONLY, ruling 4 - a cross `rev-trade` vote subtracting one from the 3, at walk0')
print()
head('the read', 'the carriers', 'bars firing at 3 of 3', 'bars a subtraction removes',
     'bars firing after it', 'the share before', 'the share after')
for rd in ('emerging', 'closed_prev'):
    for cap in CAPS:
        n = len([t for t in TFS if t <= cap])
        nr, nx, npn = WLK[(rd, cap)]
        rv = np.array(CROSS[(rd, cap)][2], int)
        mm = int(med(SPAN[(rd, cap)][1]))
        mp = int(med(SPAN[(rd, cap)][2])) if cap != 30 else BANKED[2]
        v = ((nr >= 1).astype(int) + (nx < mm).astype(int) + (npn >= mp).astype(int))
        a = v >= int(K.FDM2_MOMO_VOTES)
        b2 = (v - (rv > 0).astype(int)) >= int(K.FDM2_MOMO_VOTES)
        row(rd, 'ws4..ws%d = %d lines' % (cap, n), int(a.sum()), int((a & ~b2).sum()),
            int(b2.sum()), '%.1f%%' % (a.sum() / len(v) * 100.0),
            '%.1f%%' % (b2.sum() / len(v) * 100.0))

print()
print('# REPORT-ONLY, ruling 6 - pinned on ws4..ws10 and ws4..ws12 beside the live ws4..ws30')
print()
head('the population', 'the carriers', 'pinned median', 'p25', 'p75', 'min', 'max',
     'bars at or above the banked 9', 'of bars', 'the share')
for lab, D in (('span', SPAN), ('walk0', WLK)):
    for cap in CAPS:
        n = len([t for t in TFS if t <= cap])
        v = D[('emerging', cap)][2]
        f = int((v >= BANKED[2]).sum())
        row(lab, 'ws4..ws%d = %d lines' % (cap, n), '%g' % med(v),
            '%g' % np.percentile(v, 25), '%g' % np.percentile(v, 75), int(v.min()), int(v.max()),
            f, len(v), '%.1f%%' % (f / len(v) * 100.0))
