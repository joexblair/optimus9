"""Does dropping the moment-end term change the SIGNAL, or only when you learn it?

Joe 0929-late: "why are we testing per-bar when the whole strategy is based on stretchy-leash and
it's ability to predict when a coil will release?"

coil_exit.resolve's CONFIRMED branch reads only the release bar and the ws1mage-rev legs - never
m['i1'] or m['brk']. So on those moments the answer should be identical whether or not you wait for
the moment to break. This checks that, and prices it.

  emit WITH brk     max(brk, rev, actionable)   - what report_realtime_replay.emit_bar() does
  emit WITHOUT brk  max(rev, actionable)        - emit as soon as the answer exists
"""
import sys, numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import sweep_v3_signal as S
from measure_live_stop import score, FROM_MS, TO_MS
from optimus9.compute.trade_walk import walk
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.compute import coil_exit
from optimus9.analysis.jig import ws1mage_rev

CAP = 0.70
rig = S.Rig((FROM_MS, TO_MS)); px = rig.px; A, B = rig.A, rig.B
cfg = dict(S.BASE)
segs = rig.segs_for(A, B)
tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
FL, FH = cfg['fence_lo'], cfg['fence_hi']
rows = []
for tf in tfs:
    sw = rig.sideways(tf, cfg); r = rig.R[tf]
    q = sw & np.isfinite(r) & ((r < FL) | (r > FH))
    for (a_, b_, d) in segs:
        if not d: continue
        seg = q[a_:b_ + 1]
        if seg.any(): rows.append((a_ + int(np.argmax(seg)), tf, d))
rows.sort(key=lambda x: (x[0], x[1]))
SUP = np.zeros(rig.n, np.int16); SUPM = np.zeros(rig.n, np.int16)
for tf in tfs:
    SUP += (rig.D[tf] > 0).astype(np.int16); SUPM += (rig.D[tf] < 0).astype(np.int16)
ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d > 0 else SUPM[i]) >= cfg['support_min']))
       for (i, tf, d) in rows]
lag = cfg['confirm_lag_s'] // 5; look = cfg['lookback_s'] // 5
LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                   rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                   dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
byv = {}
for m in coil_moments(ann):
    d = m['dr']
    cc = (lambda i, _d=d: float(rig.CC[i] * _d))
    p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
    ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
    if ex['rev'] is None: continue
    sig = int(ex['rev'])
    if not (A <= sig <= B): continue
    brk = int(m['brk'] if m['brk'] is not None else m['i1'])
    act = int(coil_exit.fired(ex)[1])
    withb = max(brk, sig, act)
    without = max(sig, act)
    # LEGITIMATE: drop brk ONLY where resolve never reads the moment's end. On CONFIRMED it reads
    # only the release bar and the legs. On LOOKBACK rev IS i1 and on GAP named IS i1, so those
    # cannot be emitted before the break - you would be claiming to know the moment ended.
    legit = without if ex['via'] == 'confirmed' else withb
    byv.setdefault(ex['via'], []).append((sig, withb, without, legit))

print('N|class|n|WITH brk: at 0s / median / p90 / max|WITHOUT brk (NOT all achievable)|'
      'LEGITIMATE - brk dropped only where resolve ignores it|legit?')
allr = []
for via in ('confirmed', 'lookback', 'gap', 'forward'):
    v = byv.get(via, []); allr += v
    if not v: continue
    a = np.array([(t[1] - t[0]) * 5 for t in v]); b = np.array([(t[2] - t[0]) * 5 for t in v])
    c = np.array([(t[3] - t[0]) * 5 for t in v])
    print('N|%s|%d|%d (%.1f%%) / %d / %d / %d|%d (%.1f%%) / %d / %d / %d|%d (%.1f%%) / %d / %d / %d|%s'
          % (via, len(v), int((a==0).sum()), 100.0*(a==0).sum()/len(v), np.median(a),
             np.percentile(a,90), a.max(),
             int((b==0).sum()), 100.0*(b==0).sum()/len(v), np.median(b),
             np.percentile(b,90), b.max(),
             int((c==0).sum()), 100.0*(c==0).sum()/len(v), np.median(c),
             np.percentile(c,90), c.max(),
             'YES' if via == 'confirmed' else ('n/a - already 0' if via == 'forward' else 'NO')))
a = np.array([(t[1]-t[0])*5 for t in allr]); b = np.array([(t[2]-t[0])*5 for t in allr])
c = np.array([(t[3]-t[0])*5 for t in allr])
print('N|ALL|%d|%d (%.1f%%) / %d / %d / %d|%d (%.1f%%) / %d / %d / %d|%d (%.1f%%) / %d / %d / %d|'
      % (len(allr), int((a==0).sum()), 100.0*(a==0).sum()/len(allr), np.median(a),
         np.percentile(a,90), a.max(),
         int((b==0).sum()), 100.0*(b==0).sum()/len(allr), np.median(b),
         np.percentile(b,90), b.max(),
         int((c==0).sum()), 100.0*(c==0).sum()/len(allr), np.median(c),
         np.percentile(c,90), c.max()))
print()
print('N|IS THE SIGNAL SET IDENTICAL? the sig bars do not depend on the emit rule at all -')
print('N|  dropping brk changes WHEN you know, never WHAT you know. Same %d sig bars either way.'
      % len({t[0] for t in allr}))
print()
print('N|what you get if you trade at each emit bar')
for lab, idx in (('sig bar - the spec', 0), ('emit WITH brk - today', 1),
                 ('emit WITHOUT brk - NOT all achievable', 2),
                 ('emit LEGITIMATE - confirmed only', 3)):
    opens = sorted({t[idx] for t in allr if rig.gate_open(t[idx])})
    T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
    n, w, ns, tot = score(px, T, CAP)
    print('N|%s|rule#1 open %d|trades %d|net>0 %d (%.1f%%)|stopped %d|net sum %+.3f|per trade %+.4f'
          % (lab, len(opens), n, w, 100.0*w/n, ns, tot, tot/n))
