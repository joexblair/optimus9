"""His 1104 arm table, cut the way he asked for it: one row per arm, summed over its configs.

HIS ASK: *"re-print the [each arm, summed over the 24 configs that hold it] table at the end of the
sweep for comparison"*. So this reads a finished sweep file and re-emits that table, with the same
three cuts he was given - his 4 days, the 4 random days, and the whole file - plus the rest of the
tape when the file carries all 94 days.

IT READS THE SWEEP FILE, never the mech. Every number here is a sum of rows already on disk, so a
re-print cannot disagree with the grid it came from.

THE CONTROL ROW IS CHECKED FIRST. Config 0 is the ruled machine and its four banked days are known;
a drift there voids the grid and the table is not worth reading.

usage: fdm2_arms.py <sweep file> [<sweep file> ...]
"""
import io
import sys

OURS = ['2026-08-03', '2026-09-15', '2026-09-16', '2026-09-17']
RANDOM = ['2026-07-29', '2026-08-14', '2026-08-20', '2026-09-25']
#   the banked machine's own per-day net, from the ruled single-day runs. Config 0 must match.
CONTROL = {'2026-08-03': -3.940, '2026-09-15': 13.256, '2026-09-16': -1.750, '2026-09-17': -5.902}
LABEL = {'FDM_RE_WS6_GATE': 'the ws6r gate', 'ws6r gate': 'the ws6r gate',
         'FDM_RE_REV_READ': 'the reversal read', 'reversal read': 'the reversal read',
         'FDM_RE_WS5_FNC': "ws5r's fence", 'ws5r fence': "ws5r's fence",
         'FDM_RE_SCAN_HI': 'the scan ceiling', 'scan hi': 'the scan ceiling',
         'FDM_RE_FIRE_IB': 'the ib close in the set', 'ib in the set': 'the ib close in the set',
         'R_TRIP': 'the r trip (rsi, stoch range, stoch len)', 'B_MULT': "ws1b's multiplier"}
ARM = {'closed_prev': 'chart-matched', 'emerging': 'live', 'ex2080': 'at 20/80', 'oob': 'oob'}
#   a fence knob holds the SMALLER end of its pair, his 1103 convention, so the arm is printed as
#   the pair it means. The ib slot is a yes/no and reads as one.
PAIR = ("ws5r's fence",)
YESNO = {'0': 'out of the set', '1': 'in the set'}


def arm_label(name, raw):
    lab = LABEL.get(name, name)
    v = str(raw)
    if lab in PAIR:
        try:
            f = float(v)
            return '%s %g/%g' % (lab, f, 100.0 - f)
        except ValueError:
            pass
    if lab == 'the ib close in the set':
        return 'the ib close ' + YESNO.get(v, v)
    return '%s %s' % (lab, ARM.get(v, v))


def read(p):
    """-> (the knob names, the data rows). The header row names the knobs."""
    names, rows = None, []
    for l in io.open(p, encoding='utf-8'):
        if l.startswith('| the day | the config |'):
            c = [x.strip() for x in l.split('|')]
            names = c[3:c.index('signals in the day')]
            continue
        if not l.startswith('| 2026-') or names is None:
            continue
        c = [x.strip() for x in l.split('|')]
        j = 3 + len(names)
        #   the row carries 9 fields after the config block: signals, legs, stopped, gross, drag,
        #   net, MAE, MFE and the first signal. net sits at j + 5.
        if len(c) < j + 9:
            continue
        cfg = dict(zip(names, c[3:j]))
        rows.append(dict(cfg, day=c[1], ci=int(c[2]), nsig=int(c[j]), legs=int(c[j + 1]),
                         stops=int(c[j + 2]), net=float(c[j + 5])))
    return names, rows


for path in sys.argv[1:]:
    names, rows = read(path)
    if not rows:
        print('## %s | no data rows' % path)
        continue
    days = []
    for r in rows:
        if r['day'] not in days:
            days.append(r['day'])
    cuts = [('your 4 days', OURS), ('the 4 random days', RANDOM)]
    rest = [d for d in days if d not in OURS and d not in RANDOM]
    if rest:
        cuts.append(('the other %d days' % len(rest), rest))
    cuts.append(('all %d' % len(days), days))
    print()
    print('## %s | %d configs x %d days' % (path, len({r['ci'] for r in rows}), len(days)))
    c0 = {r['day']: r for r in rows if r['ci'] == 0}
    bad = [(d, c0[d]['net'], v) for d, v in CONTROL.items()
           if d in c0 and abs(c0[d]['net'] - v) > 0.0015]
    print('# the control row, config 0 against the banked machine: %s'
          % ('HOLDS on %d of %d banked days'
             % (sum(1 for d in CONTROL if d in c0), len(CONTROL)) if not bad else
             'DRIFTED - ' + ', '.join('%s %+.3f against %+.3f' % x for x in bad)))
    if bad:
        print('# THIS GRID IS VOID until it is re-run')
    print('# every number is a sum of that cut\'s per-day nets over every config holding the arm')
    print()
    print('| the arm | ' + ' | '.join('%s net %%' % n for n, _ in cuts) + ' | configs | legs |')
    print('|' + '---|' * (len(cuts) + 3))
    for n in names:
        vals = {}
        for r in rows:
            vals.setdefault(r[n], []).append(r)
        for k in sorted(vals, key=lambda x: (len(str(x)), str(x))):
            rs = vals[k]
            print('| %s | %s | %d | %d |'
                  % (arm_label(n, k),
                     ' | '.join('%+.3f' % sum(r['net'] for r in rs if r['day'] in set(d))
                                for _, d in cuts),
                     len({r['ci'] for r in rs}), sum(r['legs'] for r in rs)))
