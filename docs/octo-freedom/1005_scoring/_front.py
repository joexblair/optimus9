"""THE FENCE-ARRIVAL FRONT, fuzzy. 09-25 + 09-26, the 12 stopped trades. 1008.

Joe 1008: *"ws10/11/12 belonged to a specific example. it could be ws14/15/16, or ws9/10, or so-on.
use a more fuzzy approach once you've visualised the example and thought about what the overall
picture is telling you"*.

WHAT THE 12:27 EXAMPLE SHOWS. The r ladder on the tape's dr runs
  ws1 97.81, ws2 53.97, ws3 48.02, ws4 24.98, ws5 21.20, ws6 15.32, ws7 3.32, ws8 4.96,
  ws9 14.46, ws10 30.11, ws11 35.12, ws12 37.94, ws13 65.34 ...
It DIVES to a trough at ws7 and climbs back out. The lines at a fence are ws6 (ex-fence) and
ws7, ws8, ws9 (oob) - a CONTIGUOUS BAND IN THE MIDDLE OF THE LADDER, not a tide rising from ws1.
ws10/11/12 are simply the three rungs ABOVE that band, and Joe's prediction is that they arrive
next. On another leg the band sits elsewhere, so the band - not the TF numbers - is the object.

MEASURED PER LEG, on the TAPE's dr:
  arrived set     every TF in ws1..ws30 whose r is at oob or ex-fence
  band low/high   the edges of the arrived set
  contiguous      is the arrived set one unbroken run of TFs?
  rooted at ws1   does the band start at ws1, or is it mid-ladder?
  the front       the band's high edge - the TF the cascade has reached
  next 3 above    their r, and their distance to the dr-side ex-fence, in r-points
  trough TF       where the r ladder is furthest into the dr side, which is the band's centre

NOTHING IS SCORED. The band and its front are printed; which of them the mech reads is Joe's.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
RL = {t: SC.LD(t * 60, 'r')[:N] for t in range(1, 31)}
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
HI, LO = SC.HI, SC.LO
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')
K = lambda s: SC.K(s)

STOPS = [('2026-09-25 10:56:40', 'SHORT'), ('2026-09-25 12:27:05', 'LONG'),
         ('2026-09-25 15:41:00', 'LONG'), ('2026-09-25 18:59:10', 'SHORT'),
         ('2026-09-25 21:27:40', 'LONG'), ('2026-09-25 22:28:25', 'SHORT'),
         ('2026-09-26 04:30:55', 'LONG'), ('2026-09-26 09:06:00', 'LONG'),
         ('2026-09-26 11:46:35', 'LONG'), ('2026-09-26 14:17:35', 'SHORT'),
         ('2026-09-26 16:25:40', 'LONG'), ('2026-09-26 18:37:00', 'LONG')]

def arrived(k, dr):
    at = lambda v: (v >= EXF_HI) if dr > 0 else (v <= EXF_LO)
    return [t for t in range(1, 31) if np.isfinite(RL[t][k]) and at(float(RL[t][k]))]

def dist_to_fence(t, k, dr):
    v = float(RL[t][k])
    return (EXF_HI - v) if dr > 0 else (v - EXF_LO)

def trough(k, dr):
    vals = [(t, float(RL[t][k])) for t in range(1, 31) if np.isfinite(RL[t][k])]
    return (max(vals, key=lambda z: z[1]) if dr > 0 else min(vals, key=lambda z: z[1]))[0]

print('# THE ARRIVAL BAND AND ITS FRONT — the 12 stopped trades, on the tape dr')
rows = []
for ts, side in STOPS:
    k = K(ts); dr = int(DRv[k])
    a = arrived(k, dr)
    if not a:
        rows.append((DAYOF(k)[5:], side, SC.U(k), '%+d' % dr, 'none', '—', '—', '—', '—',
                     'ws%d' % trough(k, dr), '—', '—', '—')); continue
    lo, hi = a[0], a[-1]
    contig = (a == list(range(lo, hi + 1)))
    nxt = [t for t in range(hi + 1, min(31, hi + 4))]
    rows.append((DAYOF(k)[5:], side, SC.U(k), '%+d' % dr,
                 'ws%d-ws%d' % (lo, hi) if lo != hi else 'ws%d' % lo,
                 str(len(a)), 'Y' if contig else 'no', 'Y' if lo == 1 else 'no',
                 'ws%d' % hi, 'ws%d' % trough(k, dr),
                 ', '.join('ws%d' % t for t in nxt) or '— at the top',
                 ', '.join('%.1f' % float(RL[t][k]) for t in nxt) or '—',
                 ', '.join('%.1f' % dist_to_fence(t, k, dr) for t in nxt) or '—'))
box(('day', 'side', 'open', 'dr', 'arrived band', 'count', 'contiguous', 'rooted at ws1',
     'the front', 'ladder trough at', 'next 3 above the front', 'their r',
     'their distance to the ex-fence'), rows)

print('\n# THE TWO TWINS, LADDER BY LADDER — 12:27:05 and 21:27:40, both dr -1')
k1, k2 = K('2026-09-25 12:27:05'), K('2026-09-25 21:27:40')
box(('TF', '12:27 r', '12:27 at a fence', '12:27 dist to 17', '21:27 r', '21:27 at a fence',
     '21:27 dist to 17'),
    [('ws%d' % t, '%.2f' % float(RL[t][k1]),
      'oob' if float(RL[t][k1]) <= LO else ('ex-f' if float(RL[t][k1]) <= EXF_LO else '-'),
      '%+.1f' % dist_to_fence(t, k1, -1),
      '%.2f' % float(RL[t][k2]),
      'oob' if float(RL[t][k2]) <= LO else ('ex-f' if float(RL[t][k2]) <= EXF_LO else '-'),
      '%+.1f' % dist_to_fence(t, k2, -1)) for t in range(1, 31)])

print('\n# THE FRONT ACROSS THE 12, SORTED BY WHERE IT SITS')
srt = []
for ts, side in STOPS:
    k = K(ts); dr = int(DRv[k])
    a = arrived(k, dr)
    srt.append((a[-1] if a else 0, DAYOF(k)[5:], side, SC.U(k), '%+d' % dr,
                ('ws%d-ws%d' % (a[0], a[-1]) if a else 'none'), str(len(a)),
                ('Y' if a and a == list(range(a[0], a[-1] + 1)) else 'no')))
srt.sort()
box(('front TF', 'day', 'side', 'open', 'dr', 'arrived band', 'count', 'contiguous'),
    [(('ws%d' % f) if f else 'none', d, s, o, dr, b, c, ct) for f, d, s, o, dr, b, c, ct in srt])
