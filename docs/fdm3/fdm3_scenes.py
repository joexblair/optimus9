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
       fdm3_scenes.py <scenario> rows '<from>' '<to>' [<file>]   # the rows it fires on, one per
                                                        # line, written to <file> if given
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
        'SELECT g.knob, g.seq, g.bound, g.threshold, g.window_rows, '
        '       g.measure, m.oracle_read, m.counted_as, '
        '       g.band, b.lo_tf, b.hi_tf, b.lo_pivot_off, b.hi_pivot_off, '
        '       g.row_window, w.n_rows, w.size_from, w.placement '
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


FIELD = {'aw': 'aw', 'aw_flip': 'newaw', 'toexf': 'toexf', 'cross': 'x', 'nof15': 'cross'}
#   HIS 1116: *"my cross is x only. Nof15 covers x or e"* - so `cross` reads the oracle's x bit and
#   `nof15` reads the x-or-e bit. The two were the other way round before he said it.


def rows_of(gate, rows):
    """How many oracle rows a gate's window covers, and whether it may float. -> (n, anywhere).

    The scenario's range always ENDS on the qualifying row - HIS 1114 *"treat N rows as a window. if
    all of the gates are present inside the window, then the mech (the scenario) qualifies"*. A
    window that may sit anywhere inside the range still never reaches past that row, so a verdict is
    causal at the row either way.
    """
    n = {'range': rows,
         'fixed': gate['n_rows'],
         'gate': gate['window_rows']}[gate['size_from']]
    assert n is not None, (gate['knob'], gate['row_window'])
    n = int(n)
    assert 1 <= n <= rows, (gate['knob'], n, rows)
    return n, gate['placement'] == 'anywhere'


def _tally(a, lo, hi, n, counted_as):
    """A measure over ws`lo`..ws`hi` in the `n` rows ending on each row. -> int array."""
    if counted_as == 'timeframes':
        return OR.window(a, n)[:, lo:hi + 1].sum(1)
    #   prints: every cell inside the window, so the same timeframe can contribute more than once
    c = a[:, lo:hi + 1].astype(np.int32)
    t = c.copy()
    for d in range(1, n):
        s = np.zeros_like(t)
        s[d:] = c[:-d]
        t = t + s
    return t.sum(1)


def read(R, gate, pivot, rows):
    """A gate's measure over its band and its window, at every oracle row. -> int array.

    A floating window is read at every placement that fits inside the range, and the one that serves
    the gate is taken - the largest tally for a minimum, the smallest for a maximum - because the
    gate asks whether SOME placement satisfies it.
    """
    n, anywhere = rows_of(gate, rows)
    lo, hi = band_of(gate, pivot)
    a = R[FIELD[gate['measure']]]
    v = _tally(a, lo, hi, n, gate['counted_as'])
    if not anywhere:
        return v
    best = v.copy()
    pick = np.maximum if gate['bound'] == 'min' else np.minimum
    for d in range(1, rows - n + 1):
        best = pick(best, np.roll(v, d))
    return best


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
    print('| his knob | what it counts | how | the timeframes | rows | where those rows sit '
          '| bound | threshold |')
    print('|' + '---|' * 8)
    for g in gates:
        lo, hi = band_of(g, int(frame['ltf_to_htf_pivot']))
        n, anywhere = rows_of(g, int(frame['max_consecutive_rows']))
        print('| %s | %s | %s | ws%d..ws%d | %d | %s | %s | %d |'
              % (g['knob'], g['measure'], g['counted_as'], lo, hi, n,
                 'anywhere in the range' if anywhere else 'ending on the row',
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
    #   HIS 1116: the oracle A state is fdm3-wide infrastructure and banked in fdm3_knobs, so this
    #   takes the live state rather than naming one.
    R, _SD = OR.load()
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
    hd = ['the window', 'its last row', 'the incoming pseudo trade'] + [g['knob'] for g in gates]
    body = [[OR.U(i - rows + 1), OR.U(i)[11:19], OR.direction(_SD, i - rows + 1, i + 1)]
            + [str(int(vals[g['knob']][i])) for g in gates] for i in hit]
    if len(sys.argv) < 6:
        print('| %s |' % ' | '.join(hd))
        print('|' + '---|' * len(hd))
        for r in body:
            print('| %s |' % ' | '.join(r))
        return
    wd = [max(len(hd[c]), *(len(r[c]) for r in body)) if body else len(hd[c])
          for c in range(len(hd))]
    with open(sys.argv[5], 'w') as f:
        f.write('# %s, every row it fires on from %s to %s\n' % (scenario, sys.argv[3], sys.argv[4]))
        f.write('# read off fdm3-oracle\'s rows, %d bars on the tape, the oracle fence %g/%g,\n'
                '# the pivots as found, A %s %s and A %s %s\n'
                % (OR.ln.N, OR.META['fence'], 100 - OR.META['fence'],
                   OR.META['abands'][0], 'ON' if int(OR.FK.A_WS1_WS6) else 'off',
                   OR.META['abands'][1], 'ON' if int(OR.FK.A_WS7_WS15) else 'off'))
        f.write('# %s\n#\n' % OR.control(R))
        f.write('# the scenario, as the fdm3_* tables hold it:\n')
        f.write('#   max-consecutive-rows %d, ltf-to-htf-pivot ws%d, confirmed %s\n'
                % (rows, int(frame['ltf_to_htf_pivot']), 'yes' if frame['confirmed'] else 'NO'))
        for g in gates:
            lo, hi = band_of(g, int(frame['ltf_to_htf_pivot']))
            n, anywhere = rows_of(g, rows)
            f.write('#   %-36s %s %-3d  %-7s ws%d..ws%d over %d row%s %s\n'
                    % (g['knob'], g['bound'], g['threshold'], g['measure'], lo, hi, n,
                       '' if n == 1 else 's',
                       'anywhere in the range' if anywhere else 'ending on the row'))
        f.write('#\n# a window is named by its FIRST row. Every window ends on the row the\n'
                '# scenario qualifies on, so nothing later than that row is read.\n'
                '#\n# %d rows\n\n' % len(body))
        f.write(' | '.join(h.ljust(w) for h, w in zip(hd, wd)).rstrip() + '\n')
        f.write('-+-'.join('-' * w for w in wd) + '\n')
        for r in body:
            f.write(' | '.join(v.ljust(w) for v, w in zip(r, wd)).rstrip() + '\n')
    print('wrote %d rows to %s' % (len(body), sys.argv[5]))


if __name__ == '__main__':
    main()
