"""Read fdm3-oracle's rows and collate his x/e-cross and AW-flip gates. A PROBE, not either scenario's code.

GOAL: answer his 1114 xe-exhaust and aw-exhaust specs from THE ORACLE'S OWN ROWS - *"all references
are based on oracle's rows"* - without rebuilding anything the oracle already holds.

IT READS THE LIVE SERVICE, NOT THE TAPE. fdm3-oracle takes ~18 minutes to start and holds its matrix
in memory with no disk cache, so a probe that rebuilt the matrix would pay that every run. The
running service serves /meta and /rows, so this reads those. ws1b and gcws30b are not in those rows,
so they come off the cached lines in the oracle's own row frame.

HIS 1114 RULINGS, all four built in here:
  #1 the N rows belong to the SCENARIO, not to the Nof15 - *"'are contained within no more than
     {knob:4,'fdm3-4-ltf-aws-rows'} consecutive rows' describes the N rows for the 4-ltf-aws
     scenario"*. His "13of15" inside 4-ltf-aws is shorthand for his own longer sentence.
  #2 N IS A MINIMUM - *"14 or 15 collective x/e crosses will qualify 13of15 and 14of15"*.
  #3 THE N ROWS ARE A WINDOW - *"if all of the gates are present inside the window, then the mech
     (the scenario) qualifies"*. So the window ends on the row it qualifies on: every gate is
     already inside it, and nothing later than that row is read.
  #4 the oracle holds no trades, only data, read from either target-side by the flip-pivots mode -
     *"the incoming trade, the one that is curated, will be using the appropriately curated data"*.

THE ROW LAYOUT comes from fdm3_oracle.build()'s own `cols` order, not from a guess:

    offset                      width      what
    0                           17         r-pred per line, gcws15 gcws30 ws1..ws15
    17                          2          the two sums, ws16-22 and ws23-30
    19                          17         the TO/AW code per line
    36                          4          the TO/AW counts, 2 per sum
    40                          17         THE CROSS CODE per line  <- what this probe reads
    57                          2          the TO(exf) counts per sum
    59                          4          M-no-rev TF, value lo, value hi, THE ROW'S TARGET-SIDE

THE CROSS CODE's bits, his 1110 and 1113: 1 an x-cross, 2 an e-cross, 3 both, on the row's
target-side; +4 the line reads AW on this row and TO on the row before - HIS TO -> AW FLIP; +8 ws1
only, TO(exf) on this row where the row before was not.

usage: oracle_rows.py                 # the rates over the whole tape, both pivot directions
       oracle_rows.py '<from>' '<to>'  # one row per minute in a span, with the window counts
"""
import datetime as dt
import io
import json
import os
import sys
import urllib.request

import numpy as np

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.chdir(V4)                                    # the tape is cwd-sensitive - every run prints its bar count
_err = sys.stderr
sys.stderr = io.StringIO()
try:
    import ln
    import v4_live_lines as LL
    import v4_closed_prev as CP
    import v4_knobs as K
finally:
    sys.stderr = _err

BASE = 'http://127.0.0.1:8788'
META = json.load(urllib.request.urlopen(BASE + '/meta'))
LINES, SUMS = META['lines'], META['sums']
STRIDE, NROWS = int(META['stride']), int(META['rows'])
T0, STEP = int(META['t0']), int(META['step'])
DAYS = dict((d, k) for d, k in META['days'])
O_CROSS = len(LINES) + len(SUMS) + len(LINES) + 2 * len(SUMS)
O_SIDE = STRIDE - 1
#   HIS 1114: *"derived from ws1 to ws15"*. gcws15 and gcws30 are in the oracle's LINES and are NOT part of
#   either scenario's count.
WS = [(i, int(n[2:])) for i, n in enumerate(LINES) if n.startswith('ws') and int(n[2:]) <= 15]
assert [tf for _i, tf in WS] == list(range(1, 16)), WS

AWS_MAXTF = 6                   # HIS knob fdm3-4-ltf-aws-maxTF: the AW flips count on ws1..ws6
AWS_FLIPS = 4                   # HIS 4-ltf-aws: *">=4 AW flips on the same row"*
AWS_ROWS = 4                    # HIS knob fdm3-4-ltf-aws-rows: the window the gates sit inside
AWS_NOF15 = 13                  # HIS 4-ltf-aws: *">=13 of the ws1 to ws15 TFs"*, a MINIMUM
ALLIN_ROWS = 2                  # HIS xe-all-in: *"15of15 prints collectively in 2 rows"*
ALLIN_NOF15 = 15
#   HIS #5 gate, asked of the xe-all-in rows: ws1b oob, or gcws30b external of a 7/93 fence
OOB = float(K.FDM_FNC_OOB) if hasattr(K, 'FDM_FNC_OOB') else 15.0
G30_FNC = 7.0

#   THE ORACLE'S OWN ROW FRAME, rebuilt here so a line can be read where a row reads it. fdm3_oracle.build():
#   row i is the ws1 bar opening at t0 + 60 s * i, and its print bar is 12 five-second bars on - *"the cell is
#   the value where closed-prev shows it"*.
TS = np.asarray(ln.ts, np.int64)
FIRST = np.flatnonzero((TS % 60000) == 0)
FIRST = FIRST[FIRST + 12 < ln.N]
PRT = FIRST + 12
assert len(PRT) == NROWS, (len(PRT), NROWS)
assert TS[FIRST[0]] == T0, 'the row frame does not start where the oracle says it does'
assert (TS[PRT] - TS[FIRST] == 60000).all(), 'a print bar is not one ws1 bar on from its row'


def closed(emerging, tf_seconds):
    """The chart-matched value of an emerging line - closed-prev, the banked read for everything but lift-off."""
    return np.asarray(CP.series(np.asarray(emerging, float), tf_seconds), float)


W1B = closed(ln.line('ws1b'), 60)
G30B = closed(LL.sub_line('gcws30b'), 30)


def U(k):
    return dt.datetime.fromtimestamp((T0 + int(k) * STEP) / 1000,
                                     dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def K_OF(s):
    return (int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                .replace(tzinfo=dt.timezone.utc).timestamp() * 1000) - T0) // STEP


def load(off=0, flip=0, fnc=20, chunk=20000):
    """-> (crossed [n,16] bool, aw flip [n,16] bool, the row's target-side [n]) per ws TF, 1..15."""
    x = np.zeros((NROWS, 16), bool)
    aw = np.zeros((NROWS, 16), bool)
    sd = np.zeros(NROWS, np.int8)
    for a in range(0, NROWS, chunk):
        n = min(chunk, NROWS - a)
        u = '%s/rows?start=%d&count=%d&off=%d&flip=%d&fnc=%d' % (BASE, a, n, off, flip, fnc)
        b = np.frombuffer(urllib.request.urlopen(u).read(), np.int8).reshape(-1, STRIDE)
        for j, tf in WS:
            c = b[:, O_CROSS + j].astype(int)
            x[a:a + n, tf] = (c & 3) > 0
            aw[a:a + n, tf] = (c & 4) > 0
        sd[a:a + n] = b[:, O_SIDE]
    return x, aw, sd


def window(a, rows):
    """HIS #3: a window of `rows` oracle rows ENDING on the row, so nothing later than the row is read.
    -> the OR of `a` over the window, per row."""
    c = a.copy()
    for d in range(1, rows):
        s = np.zeros_like(a)
        s[d:] = a[:-d]
        c = c | s
    return c


def nof15(x, rows):
    """How many of ws1..ws15 printed an x OR an e cross anywhere in the window. HIS *"collectively"*."""
    return window(x, rows)[:, 1:16].sum(1)


def excursion():
    """HIS #5: ws1b oob, or gcws30b external of 7/93, at the row's print bar."""
    return ((np.abs(W1B[PRT] - 50.0) >= (50.0 - OOB))
            | (np.abs(G30B[PRT] - 50.0) >= (50.0 - G30_FNC)))


def main():
    days = NROWS / 1440.0
    exc = excursion()
    print('tape bars: %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
    print('legend: Nof15 = N or more of ws1..ws15 crossed inside the window (HIS #2, a minimum). '
          'the window ENDS on the row (HIS #3). ws1b oob = %.0f/%.0f, gcws30b fence = %.0f/%.0f.'
          % (OOB, 100 - OOB, G30_FNC, 100 - G30_FNC))
    for flip in (0, 1):
        x, aw, sd = load(flip=flip)
        lab = 'pivots as found' + (', flipped' if flip else '')
        c = nof15(x, ALLIN_ROWS)
        f4 = nof15(x, AWS_ROWS)
        nf = window((aw[:, 1:AWS_MAXTF + 1].sum(1) >= AWS_FLIPS)[:, None], AWS_ROWS)[:, 0]
        print()
        print('| %s | rows | per day |' % lab)
        print('|---|---|---|')
        print('| rows with no target-side, so no cross can print | %d | %.1f |'
              % (int((sd == 0).sum()), (sd == 0).sum() / days))
        for n in (13, 14, 15):
            m = c >= n
            print('| %dof15 in a %d row window | %d | %.1f |' % (n, ALLIN_ROWS, int(m.sum()), m.sum() / days))
        m = c >= ALLIN_NOF15
        print('| xe-all-in - %dof15 in %d rows | %d | %.1f |'
              % (ALLIN_NOF15, ALLIN_ROWS, int(m.sum()), m.sum() / days))
        print('| xe-all-in + ws1b oob or gcws30b ex-%.0f/%.0f | %d | %.1f |'
              % (G30_FNC, 100 - G30_FNC, int((m & exc).sum()), (m & exc).sum() / days))
        print('| %d+ AW flips on one row within ws1..ws%d | %d | %.1f |'
              % (AWS_FLIPS, AWS_MAXTF, int(nf.sum()), nf.sum() / days))
        print('| %dof15 in a %d row window | %d | %.1f |'
              % (AWS_NOF15, AWS_ROWS, int((f4 >= AWS_NOF15).sum()), (f4 >= AWS_NOF15).sum() / days))
        a4 = nf & (f4 >= AWS_NOF15)
        print('| 4-ltf-aws - both gates inside the %d row window | %d | %.1f |'
              % (AWS_ROWS, int(a4.sum()), a4.sum() / days))
        print('| 4-ltf-aws + ws1b oob or gcws30b ex-%.0f/%.0f | %d | %.1f |'
              % (G30_FNC, 100 - G30_FNC, int((a4 & exc).sum()), (a4 & exc).sum() / days))
    if len(sys.argv) >= 3:
        x, aw, sd = load()
        c, f4 = nof15(x, ALLIN_ROWS), nof15(x, AWS_ROWS)
        a, z = K_OF(sys.argv[1]), K_OF(sys.argv[2])
        print()
        print('| the row | its target-side | the TFs that crossed | %d row Nof15 | %d row Nof15 '
              '| AW flips ws1..ws%d | ws1b | gcws30b |' % (ALLIN_ROWS, AWS_ROWS, AWS_MAXTF))
        print('|' + '---|' * 8)
        for k in range(a, z + 1):
            tfs = [str(tf) for tf in range(1, 16) if x[k, tf]]
            fl = [str(tf) for tf in range(1, AWS_MAXTF + 1) if aw[k, tf]]
            print('| %s | %+d | %d: %s | %d | %d | %d: %s | %.2f | %.2f |'
                  % (U(k), sd[k], len(tfs), ','.join(tfs), c[k], f4[k], len(fl),
                     ','.join(fl) or '-', W1B[PRT[k]], G30B[PRT[k]]))


main()
