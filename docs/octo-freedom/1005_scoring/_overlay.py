"""FUZZY OVERLAY — the 3 reviewed trades as templates, against the other 9. 1008.

Joe 1008: *"fuzzy overlay the 2 reviewed trades + 21:27 against the others, and print any
near-matches"*.

THE TEMPLATES
  10:56:40  SHORT, dr +1. Joe: all TFs >7 upward, ws11/ws12 weak, x and m a clean upward ladder
            from ws3 -> flip to LONG. Its low-three recency gradient CLIFFS at ws3.
  12:27:05  LONG, dr -1. Joe: a -60 non-monotonic r ladder flipping at ws7, the higher wsf and dtf
            Mages de-pegging off the hi ex-fence -> pseudo +dr, walk up, then SHORT.
  21:27:40  LONG, dr -1. Found as 12:27's twin: same front, same trough, band within one rung.

SIX FEATURES, all fuzzy - signs, orderings and TF proximity, never absolute levels:
  F1  sign of the ws1r -> ws12r ladder
  F2  sign of the ws3x -> ws12x ladder
  F3  sign of the ws3m -> ws12m ladder
  F4  the arrival front TF, matched within +/- 3 rungs
  F5  is the arrived band contiguous
  F6  the low-three counter-visit recency gradient: SMOOTH when the two TF-steps are within 3x of
      each other, CLIFF otherwise. 10:56 is 48.1 / 40.5 / 195.2 -> 20.4x, a cliff. 12:27 is
      51.2 / 45.8 / 39.8 -> 1.11x, smooth.

THE MATCH COUNT IS PRINTED FEATURE BY FEATURE, not as a score. "Near-match" is called at 4 of 6 and
that 4 is MINE - the grid is there so the threshold can be moved or ignored.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX = C.SC, C.PX
box = C.box
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
LN = {}
for role in ('r', 'm', 'x', 'Mage'):
    for t in range(1, 31):
        LN[(t, role)] = SC.LD(t * 60, role)[:N]
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')
K = lambda s: SC.K(s)

STOPS = [('2026-09-25 10:56:40', 'SHORT'), ('2026-09-25 12:27:05', 'LONG'),
         ('2026-09-25 15:41:00', 'LONG'), ('2026-09-25 18:59:10', 'SHORT'),
         ('2026-09-25 21:27:40', 'LONG'), ('2026-09-25 22:28:25', 'SHORT'),
         ('2026-09-26 04:30:55', 'LONG'), ('2026-09-26 09:06:00', 'LONG'),
         ('2026-09-26 11:46:35', 'LONG'), ('2026-09-26 14:17:35', 'SHORT'),
         ('2026-09-26 16:25:40', 'LONG'), ('2026-09-26 18:37:00', 'LONG')]
TEMPLATES = ['10:56:40', '12:27:05', '21:27:40']

def sig(ts):
    k = K(ts); dr = int(DRv[k])
    at = lambda v: (v >= EXF_HI) if dr > 0 else (v <= EXF_LO)
    arr = [t for t in range(1, 31) if np.isfinite(LN[(t, 'r')][k]) and at(float(LN[(t, 'r')][k]))]
    front = arr[-1] if arr else None
    contig = bool(arr) and arr == list(range(arr[0], arr[-1] + 1))
    d_r = float(LN[(12, 'r')][k]) - float(LN[(1, 'r')][k])
    d_x = float(LN[(12, 'x')][k]) - float(LN[(3, 'x')][k])
    d_m = float(LN[(12, 'm')][k]) - float(LN[(3, 'm')][k])
    ctf = (lambda v: v <= EXF_LO) if dr > 0 else (lambda v: v >= EXF_HI)
    rec = []
    for t in (1, 2, 3):
        lc = None
        for j in range(k, max(0, k - 34560) - 1, -1):
            v = float(LN[(t, 'Mage')][j])
            if np.isfinite(v) and ctf(v): lc = j; break
        rec.append(((int(SC.ts[k]) - int(SC.ts[lc])) / 60000.0) if lc else float('nan'))
    st = [rec[1] - rec[0], rec[2] - rec[1]]
    # THE TIE RULE, added 1008. Identical recency values mean all three TFs last touched the
    # counter fence on the SAME bar - the tightest matryoshka there is, not a missing value. The
    # first coding returned 'n/a' for it and that discarded 4 of the 12 legs, including 21:27.
    if any(not np.isfinite(s) for s in st):
        grad, ratio = 'no data', float('nan')
    elif all(abs(s) < 1e-9 for s in st):
        grad, ratio = 'all three equal', 0.0
    elif min(abs(s) for s in st) < 1e-9:
        grad, ratio = 'one big step', float('inf')
    else:
        ratio = max(abs(s) for s in st) / min(abs(s) for s in st)
        grad = 'even steps' if ratio < 3.0 else 'one big step'
    return dict(ts=ts, k=k, dr=dr, front=front, contig=contig, d_r=d_r, d_x=d_x, d_m=d_m,
                rec=rec, ratio=ratio, grad=grad, nband=len(arr),
                band=('ws%d-ws%d' % (arr[0], arr[-1])) if arr else 'none')

S = {ts: sig(ts) for ts, side in STOPS}
sgn = lambda v: '+' if v > 0 else ('-' if v < 0 else '0')

print('# THE SIGNATURE OF ALL 12')
box(('day', 'side', 'open', 'dr', 'arrived band', 'front', 'contig', 'ws1r->ws12r',
     'ws3x->ws12x', 'ws3m->ws12m', 'ws1/ws2/ws3 min since the counter fence', 'step ratio', 'recency shape'),
    [(DAYOF(S[ts]['k'])[5:], side, ts[-8:] if len(ts) > 8 else ts, '%+d' % S[ts]['dr'],
      S[ts]['band'], ('ws%d' % S[ts]['front']) if S[ts]['front'] else '—',
      'Y' if S[ts]['contig'] else 'no',
      '%+.1f' % S[ts]['d_r'], '%+.1f' % S[ts]['d_x'], '%+.1f' % S[ts]['d_m'],
      ' / '.join('%.1f' % v for v in S[ts]['rec']),
      '%.2f' % S[ts]['ratio'] if np.isfinite(S[ts]['ratio']) else '—', S[ts]['grad'])
     for ts, side in STOPS])

TESTS = ['ws1r->ws12r direction', 'ws3x->ws12x direction', 'ws3m->ws12m direction',
         'arrival front within 3 TFs', 'arrived band unbroken', 'ws1/ws2/ws3 recency shape']

def agree(a, b):
    return [(TESTS[0], sgn(a['d_r']) == sgn(b['d_r'])),
            (TESTS[1], sgn(a['d_x']) == sgn(b['d_x'])),
            (TESTS[2], sgn(a['d_m']) == sgn(b['d_m'])),
            (TESTS[3], a['front'] is not None and b['front'] is not None
             and abs(a['front'] - b['front']) <= 3),
            (TESTS[4], a['contig'] == b['contig']),
            (TESTS[5], a['grad'] == b['grad'] and a['grad'] != 'no data')]

print('# WHAT THE SIX TESTS ARE')
box(('the test', 'what it reads', 'why it is fuzzy'),
    [('ws1r->ws12r direction', 'does the r ladder rise or fall from ws1 to ws12',
      'only the SIGN is compared, never the size'),
     ('ws3x->ws12x direction', 'does the x ladder rise or fall from ws3 to ws12',
      'only the sign - Joe read this as "a clean upward ladder from ws3"'),
     ('ws3m->ws12m direction', 'does the m ladder rise or fall from ws3 to ws12',
      'only the sign, same read as the x ladder'),
     ('arrival front within 3 TFs', 'the highest TF whose r has reached oob or the ex-fence',
      'matched within 3 rungs, so ws9 and ws8 count as the same front'),
     ('arrived band unbroken', 'are the arrived TFs one continuous run, or scattered',
      'yes/no only, the band\'s position and width are not compared'),
     ('ws1/ws2/ws3 recency shape', 'minutes since each of ws1/ws2/ws3 Mage last touched the '
      'counter-dr ex-fence', 'the SHAPE: all three equal / even steps / one big step')])
print()

for tmpl in TEMPLATES:
    T = S[[ts for ts, s in STOPS if ts.endswith(tmpl)][0]]
    print('\n# AGAINST THE %s TEMPLATE  (dr %+d, front %s, %s, gradient %s)'
          % (tmpl, T['dr'], 'ws%d' % T['front'] if T['front'] else '—', T['band'], T['grad']))
    rows = []
    for ts, side in STOPS:
        if ts.endswith(tmpl): continue
        a = S[ts]; fs = agree(a, T)
        nm = sum(1 for _, ok in fs if ok)
        rows.append((DAYOF(a['k'])[5:], side, ts[-8:], '%+d' % a['dr'],
                     *['Y' if ok else '-' for _, ok in fs],
                     '%d of 6' % nm, 'NEAR-MATCH' if nm >= 4 else ''))
    rows.sort(key=lambda z: -int(z[10].split()[0]))
    box(('day', 'side', 'open', 'dr', 'r ladder dir', 'x ladder dir', 'm ladder dir',
         'front within 3', 'band unbroken', 'recency shape', 'matched', 'verdict'), rows)

print('\n# EVERY NEAR-MATCH, COLLECTED')
rows = []
for tmpl in TEMPLATES:
    T = S[[ts for ts, s in STOPS if ts.endswith(tmpl)][0]]
    for ts, side in STOPS:
        if ts.endswith(tmpl): continue
        fs = agree(S[ts], T); nm = sum(1 for _, ok in fs if ok)
        if nm >= 4:
            rows.append((tmpl, ts[-8:], side, '%+d' % S[ts]['dr'], '%d of 6' % nm,
                         ', '.join(n for n, ok in fs if not ok) or 'all six'))
box(('template', 'near-match', 'side', 'dr', 'matched', 'the features that did NOT match'),
    rows or [('—', '—', '—', '—', '—', '—')])
print('\n- "near-match" is called at 4 of the 6 tests. That 4 is MINE; the grid above it is the evidence.')
