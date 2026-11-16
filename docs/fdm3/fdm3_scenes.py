"""An fdm3 xe-aw scenario, loaded from the database and evaluated against fdm3-oracle's rows.

HIS 1116: *"instead of using a paragraph to describe a scenario, I'll now be explaining scenarios as
table data. this new method will allows us to drop the many 'knobs as envs' and move the xe-aw
scenarios into relational db tables. the tables are yours to build; my only requirement is that the
tables show a logical heirachy - be an SRP evangelist"*.

WHAT THIS MODULE OWNS, and nothing else: turning those rows into a verdict per oracle row.
  - the TABLES own what a scenario IS. No threshold, band or window is written here.
  - oracle_rows owns the oracle's row arrays and the control on their layout.
  - this module resolves a band against the scenario's pivot, a window against its range, and a
    measure against the arrays, then applies the bound.

THE FIVE TABLES, outermost first: fdm3_measure (what can be counted), fdm3_band (which timeframes),
fdm3_row_window (which rows), fdm3_scenario (one scenario's frame), fdm3_scenario_gate (its gates).
See optimus9/sql/migrations/261116_01_fdm3_scene_tables.sql.

usage: fdm3_scenes.py <scenario>                        # its gates, as the tables hold them
       fdm3_scenes.py <scenario> at '<row>'             # every gate read at one row
       fdm3_scenes.py <scenario> count '<from>' '<to>'  # how many rows it fires on
       fdm3_scenes.py <scenario> rows '<from>' '<to>'   # the rows it fires on, one per line
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, '/home/joe/thecodes')
import oracle_rows as OR
from optimus9.config import get_db_config
from optimus9.db.database_manager import DatabaseManager

TFS = 15                        # the timeframes the oracle prints a cell for, ws1..ws15


def _db():
    d = DatabaseManager(**get_db_config())
    d.connect()
    return d


def load_scene(scenario, db=None):
    """-> (frame dict, [gate dict]) for one scenario, straight from the tables.

    A gate arrives with its measure, band and window already joined, so this module never has to
    know what `aw` means or where `ltf` ends - the vocabulary tables carry that.
    """
    d = db or _db()
    fr = d.execute('SELECT * FROM fdm3_scenario WHERE scenario = %s', (scenario,), fetch=True)
    if not fr:
        raise SystemExit('no scenario %r in fdm3_scenario' % scenario)
    gates = d.execute(
        'SELECT g.knob, g.seq, g.bound, g.threshold, '
        '       g.measure, m.oracle_read, m.counted_as, '
        '       g.band, b.lo_tf, b.hi_tf, b.lo_pivot_off, b.hi_pivot_off, '
        '       g.row_window, w.n_rows '
        '  FROM fdm3_scenario_gate g '
        '  JOIN fdm3_measure    m ON m.measure    = g.measure '
        '  JOIN fdm3_band       b ON b.band       = g.band '
        '  JOIN fdm3_row_window w ON w.row_window = g.row_window '
        ' WHERE g.scenario = %s ORDER BY g.seq', (scenario,), fetch=True)
    return fr[0], list(gates)


def band_of(gate, pivot):
    """A band's timeframes, resolved by the scenario's pivot. -> (lo, hi) inclusive.

    HIS ltf-to-htf-pivot is *"the highest ltf TF"*, so `ltf` ends ON the pivot and `htf` starts one
    above it. The table holds the offsets; this only adds them.
    """
    lo = int(gate['lo_tf']) if gate['lo_tf'] is not None else pivot + int(gate['lo_pivot_off'])
    hi = int(gate['hi_tf']) if gate['hi_tf'] is not None else pivot + int(gate['hi_pivot_off'])
    assert 1 <= lo <= hi <= TFS, (gate['band'], lo, hi)
    return lo, hi


def read(R, gate, pivot, rows):
    """A gate's measure over its band and its window, at every oracle row. -> int array.

    The window ALWAYS ends on the row - HIS 1114 *"treat N rows as a window. if all of the gates are
    present inside the window, then the mech (the scenario) qualifies"*. Nothing later than the row
    is read, so a verdict at a row is causal at that row.
    """
    n = int(gate['n_rows']) if gate['n_rows'] is not None else rows
    lo, hi = band_of(gate, pivot)
    a = R[{'aw': 'aw', 'aw_flip': 'newaw', 'toexf': 'toexf', 'cross': 'cross'}[gate['measure']]]
    if gate['counted_as'] == 'timeframes':
        return OR.window(a, n)[:, lo:hi + 1].sum(1)
    #   prints: every cell inside the window, so the same timeframe can contribute more than once
    c = a[:, lo:hi + 1].astype(np.int32)
    t = c.copy()
    for d in range(1, n):
        s = np.zeros_like(t)
        s[d:] = c[:-d]
        t = t + s
    return t.sum(1)


def evaluate(R, frame, gates):
    """-> (fires bool array, {knob: int array}) - the verdict per oracle row and each gate's reading."""
    rows, pivot = int(frame['max_consecutive_rows']), int(frame['ltf_to_htf_pivot'])
    vals, ok = {}, np.ones(OR.NROWS, bool)
    for g in gates:
        v = read(R, g, pivot, rows)
        vals[g['knob']] = v
        ok &= (v >= int(g['threshold'])) if g['bound'] == 'min' else (v <= int(g['threshold']))
    ok[:rows - 1] = False       # a window short of the range is not a window
    return ok, vals


def _print_gates(frame, gates):
    print('| the scenario | its range | its ltf-to-htf pivot | confirmed | his example |')
    print('|---|---|---|---|---|')
    print('| %s | %d rows | ws%d | %s | %s |'
          % (frame['scenario'], frame['max_consecutive_rows'], frame['ltf_to_htf_pivot'],
             'yes' if frame['confirmed'] else 'no', frame['his_example'] or '-'))
    print()
    print('| his knob | what it counts | how | the timeframes | the rows | bound | threshold |')
    print('|' + '---|' * 7)
    for g in gates:
        lo, hi = band_of(g, int(frame['ltf_to_htf_pivot']))
        print('| %s | %s | %s | ws%d..ws%d | %s | %s | %d |'
              % (g['knob'], g['measure'], g['counted_as'], lo, hi,
                 '%d' % g['n_rows'] if g['n_rows'] is not None
                 else '%d, the range' % frame['max_consecutive_rows'],
                 g['bound'], g['threshold']))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    scenario = sys.argv[1]
    frame, gates = load_scene(scenario)
    mode = sys.argv[2] if len(sys.argv) > 2 else 'gates'
    if mode == 'gates':
        _print_gates(frame, gates)
        return
    R, _SD = OR.load(alo=0, ahi=0)
    print(OR.control(R))
    fires, vals = evaluate(R, frame, gates)
    rows = int(frame['max_consecutive_rows'])
    if mode == 'at':
        k = OR.K_OF(sys.argv[3])
        print('%s at %s, its window %s .. %s'
              % (scenario, sys.argv[3], OR.U(k - rows + 1), OR.U(k)))
        print()
        print('| his knob | its reading | bound | threshold | passes |')
        print('|---|---|---|---|---|')
        for g in gates:
            v = int(vals[g['knob']][k])
            hit = v >= int(g['threshold']) if g['bound'] == 'min' else v <= int(g['threshold'])
            print('| %s | %d | %s | %d | %s |'
                  % (g['knob'], v, g['bound'], g['threshold'], 'yes' if hit else 'NO'))
        print()
        print('| %s fires at %s | %s |' % (scenario, sys.argv[3], 'yes' if fires[k] else 'no'))
        return
    a, z = OR.K_OF(sys.argv[3]), OR.K_OF(sys.argv[4])
    hit = [i for i in range(a, z + 1) if fires[i]]
    if mode == 'count':
        print('| %s, %s to %s | rows |' % (scenario, sys.argv[3], sys.argv[4]))
        print('|---|---|')
        print('| it fires on | %d |' % len(hit))
        return
    print('| the window | its last row | the incoming pseudo trade | %s |'
          % ' | '.join(g['knob'] for g in gates))
    print('|' + '---|' * (3 + len(gates)))
    for i in hit:
        print('| %s | %s | %s | %s |'
              % (OR.U(i - rows + 1), OR.U(i)[11:19], OR.direction(_SD, i - rows + 1, i + 1),
                 ' | '.join(str(int(vals[g['knob']][i])) for g in gates)))


if __name__ == '__main__':
    main()
