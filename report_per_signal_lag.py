import sys, numpy as np, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
import sweep_v3_signal as S
from measure_live_stop import FROM_MS, TO_MS
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.compute import coil_exit
from optimus9.analysis.jig import ws1mage_rev

D0, D1 = 1788220800000, 1788307200000          # 09-01 00:00 .. 09-02 00:00 UTC
rig = S.Rig((FROM_MS, TO_MS)); A, B = rig.A, rig.B
cfg = dict(S.BASE); ts = rig.ts
T = lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000, dt.timezone.utc).strftime('%H:%M:%S')
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
lag = cfg['confirm_lag_s']//5; look = cfg['lookback_s']//5
LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                   rig.lines[rig.C['sig_line'].replace('Mage','')]['Mage'], rig.hi, rig.lo,
                   dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
out = []
for m in coil_moments(ann):
    d = m['dr']; cc = (lambda i,_d=d: float(rig.CC[i]*_d))
    p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n-1)
    ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
    if ex['rev'] is None: continue
    sig = int(ex['rev'])
    if not (A <= sig <= B) or not (D0 <= int(ts[sig]) < D1): continue
    i0, i1 = int(m['i0']), int(m['i1'])
    brk = int(m['brk']) if m['brk'] is not None else i1
    act = int(coil_exit.fired(ex)[1])
    emit = max(brk, sig, act)
    binds = []
    if brk == emit: binds.append('brk')
    if sig == emit: binds.append('sig')
    if act == emit: binds.append('act')
    hits = coil_exit._knowable(LEGS[d], i1 - look, i1, i1) if ex['via'] == 'lookback' else []
    rel = T(int(p)) if conf else '-'
    out.append((sig, d, ex['via'], rig.gate_open(sig), i0, i1, brk, act, emit, (emit-sig)*5,
                '+'.join(binds), len(hits), (T(hits[0][1]) if hits else '-'), rel, m['rows']))
out.sort()
print('P|#|sig|dr|branch|rule#1|moment i0|moment i1|rows|release bar|brk|actionable|emit|LAG s|'
      'emit bound by|lb cand|earliest cand')
for n_, r in enumerate(out, 1):
    print('P|%d|%s|%+d|%s|%s|%s|%s|%d|%s|%s|%s|%s|%d|%s|%d|%s'
          % (n_, T(r[0]), r[1], r[2], 'OPEN' if r[3] else 'gated', T(r[4]), T(r[5]), r[14],
             r[13], T(r[6]), T(r[7]), T(r[8]), r[9], r[10], r[11], r[12]))
L = np.array([r[9] for r in out])
print('P|--- 09-01: %d moments|lag at 0 s %d|median %d|p90 %.0f|max %d ---'
      % (len(out), int((L==0).sum()), np.median(L), np.percentile(L,90), L.max()))
bb = {}
for r in out: bb[r[10]] = bb.get(r[10], 0) + 1
print('P|--- emit bound by: %s ---' % '  '.join('%s %d' % kv for kv in sorted(bb.items())))
