"""The population census behind the momentum petri dish. IT PICKS NOTHING.

HIS 1105 ASK: *"honestly I wouldn't know the four spine values - can you build a jig that derives
them, or reverse-engineers them?"* and, while it was being written, *"you'll need a large sample to
create stable results"*.

THE SAMPLE IS THE WHOLE TAPE: 1,632,960 bars, 2026-07-02 12:00:00 to 2026-10-04 23:59:55, 94.5
days, 32,374 legs across the eight Mage lines. No cap, no day selection, no horizon.

THE FOUR VALUES, AND WHAT DERIVES EACH. Every one is answered by a base rate, never a preference -
his standing rule that a knob is anchored to a measurement:

  1  which Mage timeframes supply the legs   a Mage whose legs are so short that no r line can
                                             traverse to the fence carries no information, and one
                                             whose legs are so long that nearly every r line gets
                                             there carries none either. The base rate shows both.
  2  which r lines get scored                the same test per r line, with its positive COUNT
                                             beside it, so a 2% rate on 11 hits is not a finding.
  3  the label's fence                       both fences measured side by side. 15/85 is the
                                             indicator spec's OWN boundary (ic_high_boundary 85.00,
                                             ic_low_boundary 15.00); 20/80 is a knob we added.
  4  how many days                           the base rate is re-estimated after each day, so the
                                             day it stops moving is visible instead of argued.

THE POPULATION IS HIS OWN MECHANISM. v4_sweep_pivots.legs(name): a Mage oob->ib cross confirm opens
a leg and the next OPPOSITE-side cross confirm closes it. BOTH ENDS ARE MECHANISM-DEFINED, so no
horizon of mine enters the label. His 1024 reason: *"fixing a pct has never completley served us"*.

THE LEGS OVERLAP, AND THAT IS THE EFFECTIVE-n PROBLEM. legs()' own docstring: *"Consecutive
same-side crosses are a line re-entering oob and leaving again; each of them still opens a leg
that runs to the next opposite boundary, so the legs OVERLAP"*. Measured: each bar sits inside 3.11
legs at ws1Mage and 12.93 at ws30Mage. SO EVERY RATE IS REPORTED TWICE - once over all legs, and
once over a NON-OVERLAPPING subset taken greedily by earliest close. The greedy subset is the
standard de-overlap and has no value to choose; it is the honest episode count.

THE SIDE IS MEASURED, NOT ASSUMED. legs() says *"a leg opened by a LOW cross is a leg the price
rises through"*, so I read a LOW-side leg as one where r climbs toward the HIGH fence. RATHER THAN
TRUST THAT, the census scores BOTH fences on every leg and prints the pair, so the asymmetry in the
numbers settles it.

    W_SPINE_MAGES   a comma list to narrow the Mage lines, for a quick re-run. Default: all eight.
    W_SPINE_TFS     a comma list to narrow the r lines. Default: ws1 to ws{HI}, no cap.
"""
import io
import os
import sys
import time
from collections import defaultdict

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_sweep_pivots as SP
    import ln
finally:
    sys.stderr = _e

FENCES = (('20/80', 20.0, 80.0), ('15/85', 15.0, 85.0))
READS = ('closed-prev', 'emerging')
SIDES = ((True, 'HIGH'), (False, 'LOW'))
LN = F2.load()
HI = int(LN['HI'])
NB = len(LN['close'])
MAGES = ([s.strip() for s in os.environ['W_SPINE_MAGES'].split(',')]
         if os.environ.get('W_SPINE_MAGES') else list(SP.TFS_WIDE))
TFS = ([int(s) for s in os.environ['W_SPINE_TFS'].split(',')]
       if os.environ.get('W_SPINE_TFS') else list(range(1, HI + 1)))


def greedy_nonoverlap(lg):
    """A maximum set of legs no two of which share a bar. -> a bool mask over `lg`.

    Taken by earliest CLOSE, which is the standard interval-scheduling choice and yields a maximum
    set. No value is chosen here.
    """
    order = sorted(range(len(lg)), key=lambda i: (lg[i][1], lg[i][0]))
    keep = np.zeros(len(lg), bool)
    last = -1
    for i in order:
        if lg[i][0] > last:
            keep[i] = True
            last = lg[i][1]
    return keep


#   ── the legs, per Mage line ───────────────────────────────────────────────────────────────────
LEGS, KEEP, DAYS = {}, {}, {}
print('| the census | value |')
print('|---|---|')
print('| the tape | %d bars, %s to %s, %.1f days |' % (NB, ln.U(0), ln.U(NB - 1), NB * 5 / 86400.0))
print('| the Mage lines scanned | %s |' % ', '.join(MAGES))
print('| the r lines scored | %s |' % (('ws1r to ws%dr, no cap' % HI) if len(TFS) == HI
                                       else ', '.join('ws%dr' % t for t in TFS)))
print('| the reads | %s |' % ', '.join(READS))
print('| the fences | %s |' % ', '.join(f[0] for f in FENCES))
print('| the leg | a Mage oob->ib cross confirm to its next opposite-side cross confirm |')
print('| the cross hold | SP_XWOB %d bars = %d s |' % (int(SP.XWOB), int(SP.XWOB) * 5))
print('| the label | did ws{T}r reach the fence inside the leg |')
print()

print('| the Mage line | legs | non-overlapping legs | median length, min | bars covered | overlap factor |')
print('|---|---|---|---|---|---|')
for nm in MAGES:
    lg = SP.legs(nm)
    LEGS[nm] = lg
    KEEP[nm] = greedy_nonoverlap(lg)
    DAYS[nm] = [ln.U(o)[:10] for o, _, _ in lg]
    L = np.array([z - o for o, z, _ in lg], float)
    cov = np.zeros(NB, bool)
    for o, z, _ in lg:
        cov[o:z + 1] = True
    c = int(cov.sum())
    print('| %s | %d | %d | %.1f | %d | %.2f |'
          % (nm, len(lg), int(KEEP[nm].sum()), np.median(L) * 5 / 60.0, c, L.sum() / max(1, c)))
print()

#   ── ONE PASS PER (read, Mage, r line). The slice max and min answer all four fence-and-side
#   questions, so nothing is scanned twice, and nothing is held: the counters are updated in place.
C = defaultdict(lambda: [0, 0])                 # (read, nm, t, fence, want_hi, only_keep) -> [hits, n]
DAYHIT = defaultdict(lambda: [0, 0])            # (day,) -> [hits, n] for the running estimate
t0 = time.time()
done = 0
for read in READS:
    src = LN['CPR'] if read == 'closed-prev' else LN['EMR']
    for nm in MAGES:
        lg, keep, dys = LEGS[nm], KEEP[nm], DAYS[nm]
        for t in TFS:
            a = np.asarray(src[t], float)
            for i, (o, z, s) in enumerate(lg):
                seg = a[o:z + 1]
                if not seg.size or not np.isfinite(seg).any():
                    continue
                mx, mn = float(np.nanmax(seg)), float(np.nanmin(seg))
                for f in FENCES:
                    for want_hi, _lab in SIDES:
                        hit = (mx >= f[2]) if want_hi else (mn <= f[1])
                        for ok in (False, True):
                            if ok and not keep[i]:
                                continue
                            e = C[(read, nm, t, f[0], want_hi, ok, int(s))]
                            e[1] += 1
                            e[0] += 1 if hit else 0
                if read == 'closed-prev':
                    e = DAYHIT[dys[i]]
                    e[1] += 1
                    e[0] += 1 if mx >= 80.0 else 0
            done += 1
            if done % 40 == 0:
                sys.stderr.write('%d passes, %.0f s\n' % (done, time.time() - t0))
                sys.stderr.flush()


def agg(pred):
    h = n = 0
    for k, v in C.items():
        if pred(k):
            h += v[0]; n += v[1]
    return h, n


def pct(h, n):
    return ('%.1f%% of %d' % (100.0 * h / n, n)) if n else '-'


print('## spine 1 and 3 - the base rate per Mage line and fence, over every r line')
print()
print('| the Mage line | the read | the fence | side scored | all legs | non-overlapping legs |')
print('|---|---|---|---|---|---|')
for nm in MAGES:
    for read in READS:
        for f in FENCES:
            for want_hi, lab in SIDES:
                a = agg(lambda k, nm=nm, read=read, f=f, want_hi=want_hi:
                        k[0] == read and k[1] == nm and k[3] == f[0] and k[4] == want_hi and not k[5])
                b = agg(lambda k, nm=nm, read=read, f=f, want_hi=want_hi:
                        k[0] == read and k[1] == nm and k[3] == f[0] and k[4] == want_hi and k[5])
                print('| %s | %s | %s | %s | %s | %s |'
                      % (nm, read, f[0], lab, pct(*a), pct(*b)))
print()

print('## the side reading - the same legs split by the side their Mage cross opened on')
print()
print('| the Mage line | the read | the fence | opened LOW, HIGH fence | opened LOW, LOW fence | opened HIGH, HIGH fence | opened HIGH, LOW fence |')
print('|---|---|---|---|---|---|---|')
for nm in MAGES:
    for read in READS:
        for f in FENCES:
            row = []
            for sd in (-1, +1):
                for want_hi, _l in SIDES:
                    r = agg(lambda k, nm=nm, read=read, f=f, want_hi=want_hi, sd=sd:
                            k[0] == read and k[1] == nm and k[3] == f[0] and k[4] == want_hi
                            and not k[5] and k[6] == sd)
                    row.append(pct(*r))
            print('| %s | %s | %s | %s |' % (nm, read, f[0], ' | '.join(row)))
print()

print('## spine 2 - the base rate per r line, over every Mage line')
print()
print('| the r line | the read | the fence | side scored | all legs | non-overlapping legs |')
print('|---|---|---|---|---|---|')
for t in TFS:
    for read in READS:
        for f in FENCES:
            for want_hi, lab in SIDES:
                a = agg(lambda k, t=t, read=read, f=f, want_hi=want_hi:
                        k[0] == read and k[2] == t and k[3] == f[0] and k[4] == want_hi and not k[5])
                b = agg(lambda k, t=t, read=read, f=f, want_hi=want_hi:
                        k[0] == read and k[2] == t and k[3] == f[0] and k[4] == want_hi and k[5])
                print('| ws%dr | %s | %s | %s | %s | %s |'
                      % (t, read, f[0], lab, pct(*a), pct(*b)))
print()

print('## spine 1 AND 2 TOGETHER - the full cross, and the r line nearest a coin flip per Mage line')
print()
print('THE TWO ARE NOT INDEPENDENT. The base rate rises with the Mage leg\'s length and falls with')
print('the r line\'s own bar width, so it is driven by ONE ratio - how far a line has to travel')
print('against how long it is given. That makes a FAMILY of (Mage, r) pairs sit near 50%, not a')
print('single point, and a pair has to be read off together. 50% is where a feature has the most')
print('room to move the answer; it is not a preference.')
print()
for read in READS:
    for f in FENCES:
        for want_hi, lab in SIDES:
            print()
            print('| the Mage line | %s, %s, %s - the r line nearest 50%% | its rate, non-overlapping legs | its rate, all legs |'
                  % (read, f[0], lab))
            print('|---|---|---|---|')
            for nm in MAGES:
                best, bd = None, None
                for t in TFS:
                    e = C.get((read, nm, t, f[0], want_hi, True, -1))
                    g = C.get((read, nm, t, f[0], want_hi, True, +1))
                    h = (e[0] if e else 0) + (g[0] if g else 0)
                    n = (e[1] if e else 0) + (g[1] if g else 0)
                    if not n:
                        continue
                    r = 100.0 * h / n
                    d = abs(r - 50.0)
                    if bd is None or d < bd:
                        best, bd = (t, r, n), d
                if best is None:
                    print('| %s | - | - | - |' % nm)
                    continue
                e = C.get((read, nm, best[0], f[0], want_hi, False, -1))
                g = C.get((read, nm, best[0], f[0], want_hi, False, +1))
                ah = (e[0] if e else 0) + (g[0] if g else 0)
                an = (e[1] if e else 0) + (g[1] if g else 0)
                print('| %s | ws%dr | %.1f%% of %d | %s |'
                      % (nm, best[0], best[1], best[2], pct(ah, an)))
print()

print('## the full cross - every Mage line against every r line, closed-prev, non-overlapping legs')
print()
print('| the Mage line | the r line | the fence | side scored | hits | legs | base rate | distance from 50 |')
print('|---|---|---|---|---|---|---|---|')
for nm in MAGES:
    for t in TFS:
        for f in FENCES:
            for want_hi, lab in SIDES:
                e = C.get(('closed-prev', nm, t, f[0], want_hi, True, -1))
                g = C.get(('closed-prev', nm, t, f[0], want_hi, True, +1))
                h = (e[0] if e else 0) + (g[0] if g else 0)
                n = (e[1] if e else 0) + (g[1] if g else 0)
                if not n:
                    continue
                r = 100.0 * h / n
                print('| %s | ws%dr | %s | %s | %d | %d | %.1f%% | %.1f |'
                      % (nm, t, f[0], lab, h, n, r, abs(r - 50.0)))
print()

print('## spine 4 - the running base rate as days accumulate, closed-prev, the 20/80 HIGH fence')
print()
print('| the day | legs opened x r lines | cumulative | cumulative hits | running base rate | move from the day before |')
print('|---|---|---|---|---|---|')
ch = cn = 0
prev = None
for d in sorted(DAYHIT):
    dh, dn = DAYHIT[d]
    ch += dh; cn += dn
    r = 100.0 * ch / cn if cn else float('nan')
    print('| %s | %d | %d | %d | %.3f%% | %s |'
          % (d, dn, cn, ch, r, ('%+.3f' % (r - prev)) if prev is not None else '-'))
    prev = r
