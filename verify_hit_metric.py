"""Reproduce the 0917 sweep's `hit` column to find out what it measured.

HYPOTHESIS: hit = the release pick bar IS the moment's maximum-coil bar, over the 61 moments that
have a span (i1 > i0). If right, lag 180 s gives 31/61 and lag 0 gives 13/61.
"""
import sys, numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import sweep_v3_signal as S
from measure_live_stop import FROM_MS, TO_MS
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.analysis.jig import ws1mage_rev
W5 = (1788220800000, 1788652800000)      # 09-01 .. 09-06, the window the 0917 sweep used
rig = S.Rig((FROM_MS, TO_MS)); A, B = rig.A, rig.B
cfg = dict(S.BASE); ts = rig.ts
segs = rig.segs_for(A, B)
tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
FL, FH = cfg['fence_lo'], cfg['fence_hi']
rows = []
for tf in tfs:
    sw = rig.sideways(tf, cfg); r = rig.R[tf]
    q = sw & np.isfinite(r) & ((r < FL) | (r > FH))
    for (a_, b_, d) in segs:
        if not d: continue
        seg = q[a_:b_+1]
        if seg.any(): rows.append((a_ + int(np.argmax(seg)), tf, d))
rows.sort(key=lambda x: (x[0], x[1]))
SUP = np.zeros(rig.n, np.int16); SUPM = np.zeros(rig.n, np.int16)
for tf in tfs:
    SUP += (rig.D[tf] > 0).astype(np.int16); SUPM += (rig.D[tf] < 0).astype(np.int16)
ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d>0 else SUPM[i]) >= cfg['support_min']))
       for (i, tf, d) in rows]
MS = [m for m in coil_moments(ann) if W5[0] <= int(ts[int(m['i0'])]) < W5[1]]
span = [m for m in MS if int(m['i1']) > int(m['i0'])]
print('H|moments in 09-01..09-06|%d|with a span|%d|single-bar|%d'
      % (len(MS), len(span), len(MS)-len(span)))
ceil = 0.0
for m in span:
    d = m['dr']; v = (np.asarray(rig.CC, float)*d)[int(m['i0']):int(m['i1'])+1]
    ceil += float(v.max())
print('H|ceiling = sum of each spanned moment max coil|%.1f   (spec says 7202.0)' % ceil)
print()
print('L|lag s|bars|hit|coil|coil %|unconfirm|mean off s|neg')
for lag_s in (0, 60, 120, 180, 240, 300, 600):
    lag = lag_s // 5
    hit = 0; tot = 0.0; unc = 0; offs = []; neg = 0
    for m in span:
        d = m['dr']; cc = (lambda i,_d=d: float(rig.CC[i]*_d))
        i0, i1 = int(m['i0']), int(m['i1'])
        p, conf = release(cc, i0, i1, lag, last_bar=rig.n-1)
        if not conf: unc += 1; continue
        v = (np.asarray(rig.CC, float)*d)[i0:i1+1]
        best = i0 + int(np.argmax(v))
        cv = float((np.asarray(rig.CC, float)*d)[int(p)])
        tot += cv
        if int(p) == best: hit += 1
        else: offs.append(abs(int(p) - best) * 5)
        if cv < 0: neg += 1
    print('L|%d|%d|%d/%d|%.1f|%.1f%%|%d|%.0f|%d'
          % (lag_s, lag, hit, len(span), tot, 100.0*tot/ceil, unc,
             (np.mean(offs) if offs else 0), neg))
