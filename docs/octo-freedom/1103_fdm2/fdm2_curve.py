"""His 1104 coverage report: one row per knob rung, the ruled rung marked.

WHY IT IS SEPARATE FROM fdm2_arms.py: that file sums an ARM over every config holding it, which is
the right cut for a cross grid. The coverage grid is not a cross - it moves ONE knob at a time with
every other knob at the bank - so its rows are (knob, rung) pairs and an arm sum over them means
nothing. This reads the same file and prints the curve.

GROSS PER LEG IS THE COLUMN THAT MATTERS: the 0.1975% round trip is what any rung has to clear.

usage: fdm2_curve.py <the curve sweep file>
"""
import io
import sys

OURS = ['2026-08-03', '2026-09-15', '2026-09-16', '2026-09-17']
RANDOM = ['2026-07-29', '2026-08-14', '2026-08-20', '2026-09-25']
DRAG = 0.1975

for path in sys.argv[1:]:
    rows, names = [], None
    for l in io.open(path, encoding='utf-8'):
        if l.startswith('| the day | the config |'):
            c = [x.strip() for x in l.split('|')]
            names = c[3:c.index('signals in the day')]
            continue
        if not l.startswith('| 2026-') or names is None:
            continue
        c = [x.strip() for x in l.split('|')]
        j = 3 + len(names)
        if len(c) < j + 9:
            continue
        rows.append(dict(zip(names, c[3:j]), day=c[1], ci=int(c[2]), legs=int(c[j + 1]),
                         stops=int(c[j + 2]), gross=float(c[j + 3]), net=float(c[j + 5])))
    if not rows:
        print('## %s | no data rows' % path)
        continue
    curves = []
    for r in rows:
        k = (r['KNOB'], r['RUNG'])
        if k not in [c[0] for c in curves]:
            curves.append((k, []))
    cur = dict((k, v) for k, v in curves)
    for r in rows:
        cur[(r['KNOB'], r['RUNG'])].append(r)
    print()
    print('## %s | the coverage curve, one knob at a time' % path)
    print('# every other knob sits at the bank for every row, so a row is that knob alone')
    print('# the first rung of each knob is the RULED value and carries the control numbers')
    print('# gross per leg is what the %.4f%% round trip has to be beaten by' % DRAG)
    #   EVERY CURVE'S OWN RULED RUNG IS A CONTROL ROW. Checking only the file's first config let
    #   the TRAJ_MIN_TRAVEL curve print 917 legs against the control row's 898 without a word.
    _base = None
    _drift = []
    for (kn, rg), rs in curves:
        nl = sum(r['legs'] for r in rs)
        nt = sum(r['net'] for r in rs)
        if _base is None:
            _base = (nl, nt)
        elif kn not in [c[0][0] for c in curves[:[c[0] for c in curves].index((kn, rg))]]:
            if abs(nl - _base[0]) or abs(nt - _base[1]) > 0.0015:
                _drift.append((kn, rg, nl, nt))
    print('# per-curve control check: %s'
          % ('every curve\'s ruled rung matches the grid\'s own baseline of %d legs / %+.3f net'
             % _base if not _drift else
             'DRIFTED on %d curve(s) - ' % len(_drift)
             + ', '.join('%s ruled rung %s gives %d legs / %+.3f against %d / %+.3f'
                         % (k, r, n, t, _base[0], _base[1]) for k, r, n, t in _drift)
             + '. THOSE CURVES ARE VOID'))
    print()
    print('| the knob | the rung | ruled | legs | stopped | gross % | net % | gross per leg % |'
          ' days net>0 | his 4 days net % | the 4 random net % |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    seen = set()
    for (kn, rg), rs in curves:
        nl = sum(r['legs'] for r in rs)
        first = kn not in seen
        seen.add(kn)
        print('| %s | %s | %s | %d | %d | %+.3f | %+.3f | %s | %d of %d | %+.3f |'
              ' %+.3f |'
              % (kn, rg, 'RULED' if first else '-', nl, sum(r['stops'] for r in rs),
                 sum(r['gross'] for r in rs), sum(r['net'] for r in rs),
                 ('%+.4f' % (sum(r['gross'] for r in rs) / nl)) if nl else '-',
                 sum(1 for r in rs if r['net'] > 0), len(rs),
                 sum(r['net'] for r in rs if r['day'] in OURS),
                 sum(r['net'] for r in rs if r['day'] in RANDOM)))
