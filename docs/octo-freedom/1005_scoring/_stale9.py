"""THE 8 TIES WITH A TRUTH COLUMN, MY VIEW PER CLAUSE, THE ANCHORED DIVERGENCE, AND THE LADDERS.

Joe 1009:
  TRUTH    *"C3: 7 out of 8 are predicting the next move correctly (08-25 18:30 is the only miss),
           so much so that I'm considering it as the leading view that we create confluences
           around"*. So the truth column IS C3's ws5-ws11 majority with 08-25 18:30 flipped. It is
           Joe's read of the charts, not a measured outcome, and it is the only truth on the table.
  MY VIEW  *"update your tables with a column that shows your view of `UP`, `DOWN`, or `-`"*.
  DIV      *"add divergence tests: ws1r and ws2r. the signal might be later than when the
           divergence printed - lookback to the last extrema for an anchor (low extrema for -dr,
           high extrema for +dr)"*.
  LADDER   *"unless the signal has landed where ws1Mage is oob, lookback to the last dr-side
           ws1Mage cross to IB and test for a mage ladder. do the same for an r ladder"*, and
           *"both r and mage ladders can print in clusters. when that happens, a cluster that
           creates a ladder direction in the lower wsf is usually the best one to follow -
           lower-cluster wsf ladders are a prediction of right now, higher-clusters are a
           prediction of the overarching trend"*.

WHAT A LADDER IS, IS MINE AND IS STATED SO IT CAN BE OVERTURNED. Joe has named a DIRECTION and
CLUSTERS but not the test. The reading built here: a ladder cluster is a maximal run of CONSECUTIVE
TFs whose line values are strictly monotonic in the TF index. UP means the value rises with the TF,
DOWN means it falls. A run of length 1 is not a cluster. "lower" vs "higher" is split at the run's
own midpoint TF against the ws1-ws23 span.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _trajmech import traj, sample_series
from optimus9.analysis.jig import anchor_floater

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts); HI, LO = SC.HI, SC.LO; TF = C.TRIG_TF
R12 = np.asarray(C.R[TF], float)[:N]
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
TFS = list(C.ALL_TF)
R = {t: np.asarray(C.R[t], float)[:N] for t in TFS}
X = {t: np.asarray(C.X[t], float)[:N] for t in TFS}
MG = {t: np.asarray(SC.LD(t * 60, 'Mage'), float)[:N] for t in TFS}
M1 = MG[1]
BL = C.TRAJ_BLOCK * 5 / 60.0; LOOK = 3 * TF; ND = int(round(40.0 / BL))
sg = lambda z: 0 if z == 0 else (1 if z > 0 else -1)
NM = {0: '-', 1: 'UP', -1: 'DOWN'}
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                timezone=datetime.timezone.utc).strftime('%Y-%m-%d') \
    if False else datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
TIES = [('2026-08-25 00:42:05', +1), ('2026-08-25 02:06:05', -1), ('2026-08-25 06:54:05', -1),
        ('2026-08-25 18:30:05', +1), ('2026-08-25 22:57:35', +1), ('2026-08-26 00:30:05', -1),
        ('2026-08-26 02:55:50', +1), ('2026-08-26 04:06:05', -1)]
MISS = '2026-08-25 18:30:05'

def c3dir(k, d, lo_=5, hi_=11):
    u = dn = 0
    for t in range(lo_, hi_ + 1):
        r = traj(R[t], k, C.TRAJ_BLOCK, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_KIND, d)
        u += r['dir'] > 0; dn += r['dir'] < 0
    return sg(u - dn), dn, u
def c1dir(k, cut=8):
    sel = [t for t in TFS if t > cut]
    g = [float(MG[t][k]) - float(R[t][k]) for t in sel]
    bel = sum(1 for z in g if z < 0); ab = len(sel) - bel
    return (-1 if bel > ab else (1 if ab > bel else 0)), bel, len(sel)
def c4dir(k, w=20):
    nb = int(round(w * 60 / 5.0)); a = max(1, k - nb + 1); bel = ab = 0
    for t in TFS:
        xn, rn = float(X[t][k]), float(R[t][k])
        if not (np.isfinite(xn) and np.isfinite(rn)): continue
        bel += xn < rn; ab += xn >= rn
    return (-1 if bel > ab else (1 if ab > bel else 0)), bel, bel + ab
def tbdir(k, d):
    s = sample_series(R60, k, C.TRAJ_BLOCK, LOOK, C.TRAJ_KIND, d)
    if len(s) < 2: return 0, float('nan')
    df = s[0][1] - s[-1][1]
    return sg(df), df

def ladders(line, k, lo_tf=None):
    """every maximal run of consecutive TFs whose values are strictly monotonic in the TF index.
    MINE - see the module docstring."""
    tfs = [t for t in TFS if np.isfinite(line[t][k])]
    out = []; i = 0
    while i < len(tfs) - 1:
        v0, v1 = float(line[tfs[i]][k]), float(line[tfs[i + 1]][k])
        if v0 == v1: i += 1; continue
        dirn = 1 if v1 > v0 else -1
        j = i + 1
        while j < len(tfs) - 1:
            a, b = float(line[tfs[j]][k]), float(line[tfs[j + 1]][k])
            if a == b or (1 if b > a else -1) != dirn: break
            j += 1
        if j - i + 1 >= 3:
            out.append(dict(lo=tfs[i], hi=tfs[j], n=j - i + 1, dirn=dirn,
                            mid=(tfs[i] + tfs[j]) / 2.0))
        i = j
    return out

def m1_anchor(k, d):
    """ws1Mage oob at the bar? else the last dr-side ws1Mage cross INTO in-bounds."""
    v = float(M1[k])
    if v >= HI or v <= LO:
        return k, 'ws1Mage is oob at the bar (%.2f) — no lookback needed' % v
    oob = (M1 >= HI) if d > 0 else (M1 <= LO)
    # a cross to IB: oob at j-1, in-bounds at j
    cr = np.flatnonzero((~oob[1:k + 1]) & oob[0:k])
    if not len(cr):
        return None, 'no dr-side ws1Mage cross to IB before the bar'
    b = int(cr[-1]) + 1
    return b, 'the last %s-side ws1Mage cross to IB' % ('HIGH' if d > 0 else 'LOW')

def extremum(line, k, d, w):
    """the last extremum anchor: the LOW for d<0, the HIGH for d>0, inside w minutes."""
    nb = int(round(w * 60 / 5.0)); a = max(1, k - nb + 1)
    seg = line[a:k + 1]; ok = np.isfinite(seg)
    if not ok.any(): return None
    z = np.where(ok, seg, np.inf if d < 0 else -np.inf)
    return a + int(np.argmin(z) if d < 0 else np.argmax(z))

print('# THE 8 TIES. truth = Joe\'s C3 read, with %s flipped as the miss he named\n' % MISS,
      flush=True)
rows = []; sc = collections.Counter()
for ts, d in TIES:
    k = SC.K(ts)
    v3, dn3, u3 = c3dir(k, d)
    truth = -v3 if ts == MISS else v3
    v1, b1, n1 = c1dir(k); v4, b4, n4 = c4dir(k); vt, df = tbdir(k, d)
    for nm, v in (('C1 Mage below r, TF>8', v1), ('C3 traj ws5-ws11', v3),
                  ('C4 x below r', v4), ('the 36-sample tie-breaker', vt)):
        sc[(nm, 'correct' if v == truth else ('wrong' if v != 0 else 'no call'))] += 1
    rows.append((DAY(k), U(k), '%+d' % d, NM[truth], '%dD %dU' % (dn3, u3), NM[v3],
                 '%d/%d' % (b1, n1), NM[v1], '%d/%d' % (b4, n4), NM[v4],
                 '%+.2f' % df, NM[vt], 'the miss' if ts == MISS else ''))
box(('day', 'the dwell-ending', 'dr', 'TRUTH — Joe', 'C3 count', 'MY VIEW C3',
     'C1 below/total', 'MY VIEW C1', 'C4 below/total', 'MY VIEW C4',
     'tie-breaker diff', 'MY VIEW TB', 'note'), rows)
box(('the clause', 'correct of 8', 'wrong', 'no call'),
    [(nm, str(sc[(nm, 'correct')]), str(sc[(nm, 'wrong')]), str(sc[(nm, 'no call')]))
     for nm in ('C3 traj ws5-ws11', 'C1 Mage below r, TF>8', 'C4 x below r',
                'the 36-sample tie-breaker')])

print('\n\n# THE ANCHORED DIVERGENCE — ws1r and ws2r, anchored at the last extremum')
for w in (20, 60, 180):
    rows = []
    for ts, d in TIES:
        k = SC.K(ts)
        for t in (1, 2):
            e = extremum(R[t], k, d, w)
            if e is None: continue
            afk = anchor_floater(R[t], C.PX, d, k)
            afe = anchor_floater(R[t], C.PX, d, e)
            rows.append((DAY(k), U(k), '%+d' % d, 'ws%dr' % t, U(e),
                         '%.1f' % ((k - e) * 5 / 60.0), '%.2f' % float(R[t][e]),
                         '%.2f' % float(R[t][k]),
                         ('%d' % int(afk['fired'])) if afk else '—',
                         ('%+.2f' % afk['d_osc']) if afk else '—',
                         ('%d' % int(afe['fired'])) if afe else '—',
                         ('%+.2f' % afe['d_osc']) if afe else '—'))
    print('\n# the extremum searched over the last %d min' % w)
    box(('day', 'the dwell-ending', 'dr', 'the line', 'the extremum bar', 'min back',
         'r at the extremum', 'r at the bar', 'fired AT the bar', 'd_osc there',
         'fired AT the extremum', 'd_osc there'), rows)

print('\n\n# THE LADDERS — my reading of a ladder, see the docstring')
rows = []
for ts, d in TIES:
    k = SC.K(ts)
    ab, why = m1_anchor(k, d)
    for nm, line in (('Mage', MG), ('r', R)):
        for lbl, bar in (('at the bar', k), ('at the anchor', ab)):
            if bar is None: continue
            L = ladders(line, bar)
            if not L:
                rows.append((DAY(k), U(k), '%+d' % d, nm, lbl, U(bar), 'none', '—', '—', '—', why
                             if lbl == 'at the anchor' else ''))
                continue
            lowest = min(L, key=lambda z: z['mid'])
            rows.append((DAY(k), U(k), '%+d' % d, nm, lbl, U(bar), str(len(L)),
                         '; '.join('ws%d-ws%d %s' % (z['lo'], z['hi'], NM[z['dirn']]) for z in L),
                         'ws%d-ws%d' % (lowest['lo'], lowest['hi']), NM[lowest['dirn']],
                         why if lbl == 'at the anchor' else ''))
box(('day', 'the dwell-ending', 'dr', 'the line', 'read', 'the bar read', 'clusters',
     'every cluster', 'the LOWEST cluster', 'its direction', 'the anchor'), rows)
