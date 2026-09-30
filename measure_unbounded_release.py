"""Unbound the release SEARCH past i1. Joe 0930: "eventually, it has to fall for longer than
3 minutes - the ws1Mage doesn't like to stay outside of the fence".

release() searches [i0, i1] only. This computes, for the whole 90-day coil series, every bar that
WOULD confirm a release, then asks: for each moment that found none inside its own span, where is
the first one after i0 with no upper bound, and how far past i1 does it sit?

Vectorised: ok[t] = (cc[t+1] < cc[t]) AND max(cc[t+1 .. t+lag]) <= cc[t]   - exactly release()'s test
"""
import sys, numpy as np, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
import sweep_v3_signal as S
from measure_live_stop import FROM_MS, TO_MS
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.compute import coil_exit
from optimus9.analysis.jig import ws1mage_rev
rig = S.Rig((FROM_MS, TO_MS)); A, B = rig.A, rig.B
cfg = dict(S.BASE); ts = rig.ts; n = rig.n
U = lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
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
SUP = np.zeros(n, np.int16); SUPM = np.zeros(n, np.int16)
for tf in tfs:
    SUP += (rig.D[tf] > 0).astype(np.int16); SUPM += (rig.D[tf] < 0).astype(np.int16)
ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d>0 else SUPM[i]) >= cfg['support_min']))
       for (i, tf, d) in rows]
lag = cfg['confirm_lag_s']//5; look = cfg['lookback_s']//5
LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                   rig.lines[rig.C['sig_line'].replace('Mage','')]['Mage'], rig.hi, rig.lo,
                   dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])

OKBAR = {}
for d in (1, -1):
    cc = np.asarray(rig.CC, float) * d
    w = np.full(n, -np.inf)                      # w[t] = max(cc[t+1 .. t+lag]), clipped at the end
    for s in range(1, lag+1):
        w[:n-s] = np.maximum(w[:n-s], cc[s:])
    turn = np.zeros(n, bool); turn[:n-1] = cc[1:] < cc[:-1]
    ok = turn & (w <= cc)
    OKBAR[d] = np.flatnonzero(ok)
    print('K|dr %+d|bars that would confirm a release, anywhere in 90 days|%d of %d (%.2f%%)'
          % (d, OKBAR[d].size, n, 100.0*OKBAR[d].size/n))
print()

modeA = []; modeB = []; none = 0
for m in coil_moments(ann):
    d = m['dr']; cc_f = (lambda i,_d=d: float(rig.CC[i]*_d))
    i0, i1 = int(m['i0']), int(m['i1'])
    p, conf = release(cc_f, i0, i1, lag, last_bar=n-1)
    if conf: continue
    # which mode: did the coil ever tick down inside the moment?
    v = (np.asarray(rig.CC, float)*d)
    ticked = bool((v[i0+1:i1+2] < v[i0:i1+1]).any()) if i1 >= i0 else False
    arr = OKBAR[d]
    k = int(np.searchsorted(arr, i0, 'left'))
    if k >= arr.size:
        none += 1; continue
    first = int(arr[k])
    rec = (first, i0, i1, int(m['brk']) if m['brk'] is not None else i1, (first - i1)*5)
    (modeB if ticked else modeA).append(rec)

for lbl, sel in (('mode B - ticked down, every turn undone', modeB),
                 ('mode A - never ticked down inside the moment', modeA)):
    if not sel: continue
    g = np.array([r[4] for r in sel])
    print('R|%s|n %d' % (lbl, len(sel)))
    print('R|  first unbounded release, seconds PAST i1: p25 %d|median %d|p75 %d|p90 %d|max %d'
          % (np.percentile(g,25), np.median(g), np.percentile(g,75), np.percentile(g,90), g.max()))
    print('R|  lands at or before i1 (inside the moment after all): %d' % int((g<=0).sum()))
    print('R|  lands at or before the breaking row: %d of %d (%.1f%%)'
          % (sum(1 for r in sel if r[0] <= r[3]), len(sel),
             100.0*sum(1 for r in sel if r[0] <= r[3])/len(sel)))
    print()
print('R|moments with NO confirming bar anywhere after i0, to the end of the tape|%d' % none)
