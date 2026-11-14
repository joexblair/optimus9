"""Read fdm3-oracle's rows over HTTP and collate his x/e-cross and AW-flip events. A PROBE.

GOAL: answer his 1114 xe-exhaust and aw-exhaust specs from THE ORACLE'S OWN ROWS - *"all references
are based on oracle's rows"* - without rebuilding anything the oracle already holds.

IT READS THE LIVE SERVICE, NOT THE TAPE. fdm3-oracle takes ~18 minutes to start and holds its matrix
in memory with no disk cache, so a probe that rebuilt the matrix would pay that every run. The
running service serves /meta and /rows, so this reads those.

THE ROW LAYOUT comes from fdm3_oracle.build()'s own `cols` order, not from a guess:

    offset                      width      what
    0                           17         r-pred per line, gcws15 gcws30 ws1..ws15
    17                          2          the two sums, ws16-22 and ws23-30
    19                          17         the TO/AW code per line
    36                          4          the TO/AW counts, 2 per sum
    40                          17         THE CROSS CODE per line  <- what this probe reads
    57                          2          the TO(exf) counts per sum
    59                          4          M-no-rev's TF, its value lo and hi, and the row's side

THE CROSS CODE's bits, his 1110 and 1113: 1 an x-cross, 2 an e-cross, 3 both, on the row's
target-side; +4 the line reads AW on this row and TO on the row before - HIS TO -> AW FLIP; +8 ws1
only, TO(exf) on this row where the row before was not.

usage: oracle_rows.py                 # the rates over the whole tape
       oracle_rows.py '<from>' '<to>'  # one row per minute in a span, with the collated counts
"""
import datetime as dt
import json
import sys
import urllib.request

import numpy as np

BASE = 'http://127.0.0.1:8788'
META = json.load(urllib.request.urlopen(BASE + '/meta'))
LINES, SUMS = META['lines'], META['sums']
STRIDE, NROWS = int(META['stride']), int(META['rows'])
T0, STEP = int(META['t0']), int(META['step'])
O_CROSS = len(LINES) + len(SUMS) + len(LINES) + 2 * len(SUMS)
#   HIS 1114: *"derived from ws1 to ws15"*. gcws15 and gcws30 are in the oracle's LINES and are NOT
#   part of either event.
WS = [(i, int(n[2:])) for i, n in enumerate(LINES) if n.startswith('ws') and int(n[2:]) <= 15]
TFS = [tf for _i, tf in WS]
assert TFS == list(range(1, 16)), TFS


def U(k):
    return dt.datetime.fromtimestamp((T0 + int(k) * STEP) / 1000,
                                     dt.timezone.utc).strftime('%Y-%m-%d %H:%M')


def K(s):
    return (int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                .replace(tzinfo=dt.timezone.utc).timestamp() * 1000) - T0) // STEP


def load(off=0, flip=0, fnc=20, chunk=20000):
    """The cross bit and the AW-flip bit per row per ws TF. -> (cross [n,16] bool, flip [n,16])."""
    x = np.zeros((NROWS, 16), bool)
    aw = np.zeros((NROWS, 16), bool)
    for a in range(0, NROWS, chunk):
        n = min(chunk, NROWS - a)
        u = '%s/rows?start=%d&count=%d&off=%d&flip=%d&fnc=%d' % (BASE, a, n, off, flip, fnc)
        b = np.frombuffer(urllib.request.urlopen(u).read(), np.int8).reshape(-1, STRIDE)
        for j, tf in WS:
            c = b[:, O_CROSS + j].astype(int)
            x[a:a + n, tf] = (c & 3) > 0
            aw[a:a + n, tf] = (c & 4) > 0
    return x, aw


def collate(x, rows, forward=False):
    """HIS 1114 *"collectively"*: how many of ws1..ws15 printed an x OR an e cross anywhere in a
    window of `rows` consecutive oracle rows. -> count per row.

    THE WINDOW'S DIRECTION IS NOT THE SAME IN HIS TWO SPECS and both are offered here rather than
    picked: his xe example reads BACK from the event row (*"09-23 0028 ... over 0027 and 0028"*),
    his 4-ltf-aws example reads FORWARD from the flip row (*"0157 to 0200: the 4 AW flips print at
    0157, and 13 of the 15 TFs have printed an x or e cross in the fields of 0157, 0158, 0159,
    0200"*). Forward is LOOKAHEAD at the flip row - raised with him.
    """
    cum = x.copy()
    for d in range(1, rows):
        sh = np.zeros_like(x)
        if forward:
            sh[:-d] = x[d:]
        else:
            sh[d:] = x[:-d]
        cum = cum | sh
    return cum[:, 1:16].sum(1)


def main():
    x, aw = load()
    days = NROWS / 1440.0
    c2 = collate(x, 2)
    print('| the collated event, a 2 row window ending on the row | rows | per day |')
    print('|---|---|---|')
    for lab, m in (('exactly 13 of 15', c2 == 13), ('exactly 14 of 15', c2 == 14),
                   ('exactly 15 of 15 - his xe-all-in', c2 == 15), ('13 or more of 15', c2 >= 13)):
        print('| %s | %d | %.1f |' % (lab, int(m.sum()), m.sum() / days))
    nf = aw[:, 1:7].sum(1)          # HIS fdm3-4-ltf-aws-maxTF ws6
    f4 = collate(x, 4, forward=True)        # HIS 4-ltf-aws-rows 4, his example's direction
    b4 = collate(x, 4)
    print()
    print('| the 4-ltf-aws parts | rows | per day |')
    print('|---|---|---|')
    print('| 4+ AW flips on one row within ws1..ws6 | %d | %.1f |'
          % (int((nf >= 4).sum()), (nf >= 4).sum() / days))
    print('| 13+ of 15 over the flip row and the 3 AFTER it | %d | %.1f |'
          % (int((f4 >= 13).sum()), (f4 >= 13).sum() / days))
    print('| BOTH - the scenario as written, forward | %d | %.1f |'
          % (int(((nf >= 4) & (f4 >= 13)).sum()), ((nf >= 4) & (f4 >= 13)).sum() / days))
    print('| BOTH, if the 4 rows ran BACKWARD instead | %d | %.1f |'
          % (int(((nf >= 4) & (b4 >= 13)).sum()), ((nf >= 4) & (b4 >= 13)).sum() / days))
    if len(sys.argv) >= 3:
        a, z = K(sys.argv[1]), K(sys.argv[2])
        print()
        print('| the row | the TFs that crossed | 2 row back-count | 4 row fwd-count '
              '| AW flips ws1..ws6 |')
        print('|' + '---|' * 5)
        for k in range(a, z + 1):
            tfs = [str(tf) for tf in TFS if x[k, tf]]
            fl = [str(tf) for tf in range(1, 7) if aw[k, tf]]
            print('| %s | %d: %s | %d | %d | %d: %s |'
                  % (U(k), len(tfs), ','.join(tfs), c2[k], f4[k], len(fl), ','.join(fl) or '-'))


main()
