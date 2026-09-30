import sys, numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import sweep_v3_signal as S
from measure_live_stop import FROM_MS, TO_MS
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.compute import coil_exit
from optimus9.analysis.jig import ws1mage_rev
rig = S.Rig((FROM_MS, TO_MS)); A, B = rig.A, rig.B
cfg = dict(S.BASE); segs = rig.segs_for(A, B)
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
lag = cfg['confirm_lag_s']//5; look = cfg['lookback_s']//5
LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                   rig.lines[rig.C['sig_line'].replace('Mage','')]['Mage'], rig.hi, rig.lo,
                   dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
ROWB = sorted({int(a['i']) for a in ann})
nc = 0; fits = 0; clipped = 0; flip = 0; details = []
for m in coil_moments(ann):
    d = m['dr']; cc = (lambda i,_d=d: float(rig.CC[i]*_d))
    i0, i1 = int(m['i0']), int(m['i1'])
    p, conf = release(cc, i0, i1, lag, last_bar=rig.n-1)
    if not conf: continue
    nc += 1
    if int(p) + lag <= i1:
        fits += 1                       # the 180 s confirm window lies inside the moment
        continue
    clipped += 1
    # PROVISIONAL TEST: truncate the moment at the first row at/after p + lag and re-run release.
    # If the verdict or the bar differs from the full-moment answer, a provisional emit is revisable.
    cand = [b for b in ROWB if i0 <= b <= i1 and b >= int(p)]
    changed = False
    for b in cand:
        p2, c2 = release(cc, i0, b, lag, last_bar=rig.n-1)
        if (not c2) or int(p2) != int(p):
            changed = True; break
    if changed:
        flip += 1; details.append((i0, i1, int(p)))
print('C|CONFIRMED moments|%d' % nc)
print('C|  release + 180 s fits INSIDE the moment - no clip possible|%d (%.1f%%)' % (fits, 100.0*fits/nc))
print('C|  release + 180 s runs PAST the moment end - a provisional window could clip|%d (%.1f%%)'
      % (clipped, 100.0*clipped/nc))
print('C|  of those, a truncated re-run CHANGES the verdict or the bar|%d' % flip)
print('C|  -> provisional emit on the confirmed branch is revisable on %d of %d moments (%.2f%%)'
      % (flip, nc, 100.0*flip/nc))
for (a_, b_, p_) in details[:10]:
    print('C|    changed: moment bars %d..%d  release %d' % (a_, b_, p_))
