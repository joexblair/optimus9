"""ONE COLLECTOR for every sweep arm. The stop state comes off the file, never off memory.

Joe 1030: *"in the summaries, note if the numbers are mae1.1"*, after asking *"with or without
mae1.1?"* about a net% I had given him twice without ever saying.

EVERY ROW CARRIES ITS STOP STATE, read from the arm's own header line. The driver prints either
'the 1.1% stop is OFF' or 'the stop is ON at LIN2_MAE_CAP 1.10%...', so the file says what it was
measured under and this reader does not have to trust what I remember launching.

usage: collect.py <label>=<file.md> [...]
"""
import os
import re
import sys

DATE = re.compile(r'^2026-\d\d-\d\d$')


def head(p):
    """the arm's stop state and its window, off its own header. -> (stop, window)."""
    stop, win = 'UNREADABLE', 'UNREADABLE'
    with open(p) as f:
        for L in f:
            if not L.startswith('#'):
                break
            if 'stop is OFF' in L:
                stop = 'OFF'
            elif 'the stop is ON at LIN2_MAE_CAP' in L:
                m = re.search(r'ON at LIN2_MAE_CAP ([\d.]+)%', L)
                stop = 'ON at %s%%' % (m.group(1) if m else '?')
            if L.startswith('# WINDOW '):
                m = re.search(r'WINDOW (\S+ \S+) \.\. (\S+ \S+)', L)
                if m:
                    win = '%s .. %s' % (m.group(1), m.group(2))
    return stop, win


def total(p):
    for L in open(p):
        if L.startswith('| TOTAL'):
            return [x.strip() for x in L.strip().strip('|').split('|')]
    return None


def legs(p):
    out = {}
    for L in open(p):
        if not L.startswith('| 2026'):
            continue
        c = [x.strip() for x in L.strip().strip('|').split('|')]
        if len(c) < 9 or not DATE.match(c[0]) or not c[1].isdigit():
            continue
        while len(c) < 14:
            c.append('-')
        out[c[3]] = c
    return out


if __name__ == '__main__':
    pairs = [a.split('=', 1) for a in sys.argv[1:]]
    print('| the arm | the stop | legs | MAE % | MFE % | realised % | drag % | net % |')
    print('|---|---|---|---|---|---|---|---|')
    wins = set()
    for lab, f in pairs:
        if not os.path.exists(f):
            print('| %s | - | FILE MISSING | | | | | |' % lab)
            continue
        st, w = head(f)
        wins.add(w)
        t = total(f)
        if t is None:
            print('| %s | %s | NO TOTAL ROW - the arm produced no scored legs | | | | | |'
                  % (lab, st))
            continue
        print('| %s | %s | %s | %s | %s | %s | %s | %s |'
              % (lab, st, t[2].replace(' scored legs', ''), t[9], t[10], t[11], t[12], t[13]))
    print('')
    print('| the read | value |')
    print('|---|---|')
    print('| the window on every row above | %s |' % (
        list(wins)[0] if len(wins) == 1 else 'MIXED - ' + ' / '.join(sorted(wins))))
    print('| arms with no TOTAL row | %d |' % sum(
        1 for _, f in pairs if not os.path.exists(f) or total(f) is None))
