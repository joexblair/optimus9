"""THE TRUNCATION TEST - bound a walk at its own verdict bar and demand the same answer.

WHAT IT CAUGHT. On 1031 it found v4_l2_cadence.t1 firing on the ws1b ib CROSS bar while its own
filter and its own comment both used the wob-12 CONFIRM bar. 16 of the 17 t1 cadences on the
2026-08-14 0659 walk were acting 25 to 55 s before the hold that qualifies them was complete. No
assert caught it, no docstring caught it, and the walk's own rows looked right.

THE PRINCIPLE. A decision taken at bar V may read bar V and no bar after it. So a walk bounded at V
must produce the identical verdict and the identical rows. If bounding it changes anything, some
read reached past V - and the usual culprit is a producer that FILTERS on a confirm bar it does not
FIRE on, because the entry then needs a window wider than the bar it claims.

IT IS A STANDING CHECK, his 1031 instruction, not a one-off. Run it on every walk before reporting
one, and name its result in the report.

usage: v4_truncation_test.py <driver.py> <arm 'YYYY-MM-DD HH:MM:SS'> <high|low> <verdict bar>
       - the verdict bar may be the literal `auto`, which takes it from the unbounded run's own
         first verdict. Use `auto` whenever a mech change may have MOVED the verdict, which is
         most of the time - passing a stale bar tests the wrong bound and can pass vacuously.
       - the driver must honour W_B_END as its forward bound
       - every W_V4_* knob in the caller's environment is passed through untouched

exit 0 = the verdict and every row survive the bound. exit 1 = they do not, and the diff is printed.
"""
import os
import re
import subprocess
import sys
import tempfile

VERDICT = re.compile(r'^\|\s*the verdict\s*\|\s*(.+?)\s*\|\s*$')
VBAR = re.compile(r'^\|\s*the verdict bar\s*\|\s*(.+?)\s*\|\s*$')
MODE = re.compile(r"^## MODE (.+?) - every row")


def run(driver, arm, side, bend=None):
    env = dict(os.environ)
    if bend:
        env['W_B_END'] = bend
    else:
        env.pop('W_B_END', None)
    with tempfile.NamedTemporaryFile('w+', suffix='.md', delete=False) as f:
        out = f.name
    with open(out, 'w') as fo, open(os.devnull, 'w') as fe:
        r = subprocess.run([sys.executable, driver, arm, side], stdout=fo, stderr=fe, env=env)
    if r.returncode != 0:
        print('the driver exited %d with B_END=%r' % (r.returncode, bend))
        return None
    return open(out).read()


def rows(text):
    """-> {mode: [the row lines]} from the 'every row' sections."""
    out, cur = {}, None
    for ln in text.splitlines():
        m = MODE.match(ln)
        if m:
            cur = m.group(1)
            out[cur] = []
            continue
        if ln.startswith('## '):
            cur = None
            continue
        if cur is not None and ln.startswith('|'):
            out[cur].append(ln)
    return out


def verdicts(text):
    v = [m.group(1) for ln in text.splitlines() for m in [VERDICT.match(ln)] if m]
    b = [m.group(1) for ln in text.splitlines() for m in [VBAR.match(ln)] if m]
    return list(zip(v, b))


def main():
    if len(sys.argv) != 5:
        print(__doc__)
        return 2
    driver, arm, side, vbar = sys.argv[1:5]
    print('# THE TRUNCATION TEST')
    print('# driver %s | arm %s | side %s | the bound %s' % (driver, arm, side, vbar))
    print('# every W_V4_* knob comes from this environment, untouched')
    print()
    full = run(driver, arm, side, None)
    if full is None:
        return 1
    if str(vbar) == 'auto':
        fv0 = verdicts(full)
        if not fv0 or not fv0[0][1] or fv0[0][1] == '-':
            print('| the read | value |')
            print('|---|---|')
            print('| the unbounded run gives no verdict bar | nothing to bound at |')
            return 1
        vbar = fv0[0][1]
        print('# the bound was taken from the unbounded run: %s' % vbar)
        print()
    cut = run(driver, arm, side, vbar)
    if cut is None:
        return 1
    fv, cv = verdicts(full), verdicts(cut)
    fr, cr = rows(full), rows(cut)
    print('| the read | no end bound | bounded at %s | same? |' % vbar)
    print('|---|---|---|---|')
    ok = True
    for i, (a, b) in enumerate(zip(fv, cv), 1):
        same = a == b
        ok &= same
        print('| the verdict, block %d | %s %s | %s %s | %s |'
              % (i, a[0], a[1], b[0], b[1], 'YES' if same else 'NO'))
    if len(fv) != len(cv):
        ok = False
        print('| verdict blocks | %d | %d | NO |' % (len(fv), len(cv)))
    for m in sorted(set(fr) | set(cr)):
        a, b = fr.get(m, []), cr.get(m, [])
        same = a == b
        ok &= same
        print('| every row of mode %s | %d rows | %d rows | %s |'
              % (m, len(a), len(b), 'IDENTICAL' if same else 'DIFFERS'))
        if not same:
            for j in range(max(len(a), len(b))):
                x = a[j] if j < len(a) else '<missing>'
                y = b[j] if j < len(b) else '<missing>'
                if x != y:
                    print()
                    print('the first differing row of mode %s, row %d:' % (m, j + 1))
                    print('  unbounded: %s' % x)
                    print('  bounded:   %s' % y)
                    break
    print()
    print('| the read | value |')
    print('|---|---|')
    print('| THE TEST | %s |' % ('PASSES - no decision read past the bound'
                                 if ok else 'FAILS - a read reached past the bound'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
