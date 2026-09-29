"""What the 165 s emission latency costs THIS mech - the capped one.

Entry at the bar the signal NAMES (the spec) vs entry at the bar the chain can first EMIT it.
Same knobs, same cap, same walk, same 90 days. Nothing else changes.
"""
import sys, io, numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import sweep_v3_signal as S
from measure_live_stop import score, FROM_MS, TO_MS
from optimus9.compute.trade_walk import walk

CAP = 0.70


def build_pairs(rig):
    """-> [(named_bar, emit_bar)] for every resolved moment in the window."""
    cfg = dict(S.BASE); A, B = rig.A, rig.B
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
    from optimus9.compute.coil_moment import moments as coil_moments, release
    from optimus9.compute import coil_exit
    from optimus9.analysis.jig import ws1mage_rev
    lag = cfg['confirm_lag_s'] // 5; look = cfg['lookback_s'] // 5
    LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
    out = []
    for m in coil_moments(ann):
        d = m['dr']
        cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        if ex['rev'] is None: continue
        named = int(ex['rev'])
        if not (A <= named <= B): continue
        # THE EMIT BAR, verbatim from report_realtime_replay.emit_bar(): the moment is known-ended
        # at its BREAKING row, and `rev` and `actionable` must both have passed. `settled` waits
        # for the confirm window to be unclipped as well.
        brk = m['brk'] if m['brk'] is not None else m['i1']
        eager = max(brk, int(ex['rev']), int(ex['actionable']))
        settled = max(eager, int(m['i1']) + lag)
        out.append((named, eager, settled))
    return out


def main():
    rig = S.Rig((FROM_MS, TO_MS)); px = rig.px; B = rig.B
    pairs = build_pairs(rig)
    print('E|moments %d' % len(pairs))
    for lab, idx in (('eager', 1), ('settled', 2)):
        lags = np.array([(p[idx] - p[0]) * 5 for p in pairs])
        print('E|%s lag s  p25 %d|median %d|p75 %d|p90 %d|max %d|mean %.0f|at 0 s %d of %d'
              % (lab, np.percentile(lags,25), np.median(lags), np.percentile(lags,75),
                 np.percentile(lags,90), lags.max(), lags.mean(),
                 int((lags==0).sum()), lags.size))
    for lab, idx in (('NAMED bar - the spec', 0), ('EAGER emit bar', 1), ('SETTLED emit bar', 2)):
        opens = sorted({p[idx] for p in pairs if rig.gate_open(p[idx])})
        T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
        n, w, ns, tot = score(px, T, CAP)
        by = {}
        for t in T: by[t['closed_by']] = by.get(t['closed_by'], 0) + 1
        print('E|%s|rule#1 open %d|trades %d|net>0 %d (%.1f%%)|stopped %d (%.1f%%)|'
              'net sum %+.3f|per trade %+.4f'
              % (lab, len(opens), n, w, 100.0*w/n, ns, 100.0*ns/n, tot, tot/n))
        print('E|  closed by: %s' % '  '.join('%s %d' % kv for kv in sorted(by.items())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
