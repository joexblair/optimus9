"""The emission lag split by coil_exit class - CONFIRMED, LOOKBACK, GAP, FORWARD.

Joe 0929: "latency is ok for now. eventually we'll cherry-pick what we need from the classes and
optimise". This says which classes are free and which are expensive, over 90 days rather than the
121-row 09-01..09-06 sample.

Lag = (the bar the chain can first EMIT the answer) - (the bar the signal NAMES), in seconds.
The emit bar is report_realtime_replay.emit_bar() verbatim.
"""
import sys, numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import sweep_v3_signal as S
from measure_live_stop import score, FROM_MS, TO_MS
from optimus9.compute.trade_walk import walk

CAP = 0.70


def main():
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
    from optimus9.compute.coil_moment import moments as coil_moments, release
    from optimus9.compute import coil_exit
    from optimus9.analysis.jig import ws1mage_rev
    lag = cfg['confirm_lag_s'] // 5; look = cfg['lookback_s'] // 5
    LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
    by = {}
    named_all, emit_all = [], []
    for m in coil_moments(ann):
        d = m['dr']
        cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        if ex['rev'] is None: continue
        named = int(ex['rev'])
        if not (A <= named <= B): continue
        brk = m['brk'] if m['brk'] is not None else m['i1']
        emit = max(brk, int(ex['rev']), int(ex['actionable']))
        by.setdefault(ex['via'], []).append((named, emit))
        named_all.append(named); emit_all.append(emit)

    print('L|class|n|share|at 0 s|0 s %|p25 s|median s|p75 s|p90 s|max s|mean s')
    tot = sum(len(v) for v in by.values())
    for via in ('confirmed', 'lookback', 'gap', 'forward'):
        v = by.get(via, [])
        if not v:
            print('L|%s|0|-|-|-|-|-|-|-|-|-' % via); continue
        g = np.array([(e - n) * 5 for n, e in v])
        print('L|%s|%d|%.1f%%|%d|%.1f%%|%d|%d|%d|%d|%d|%.0f'
              % (via, len(v), 100.0*len(v)/tot, int((g==0).sum()), 100.0*(g==0).sum()/len(v),
                 np.percentile(g,25), np.median(g), np.percentile(g,75), np.percentile(g,90),
                 g.max(), g.mean()))
    g = np.array([(e - n) * 5 for n, e in zip(named_all, emit_all)])
    print('L|ALL|%d|100.0%%|%d|%.1f%%|%d|%d|%d|%d|%d|%.0f'
          % (tot, int((g==0).sum()), 100.0*(g==0).sum()/tot, np.percentile(g,25), np.median(g),
             np.percentile(g,75), np.percentile(g,90), g.max(), g.mean()))

    print()
    print('W|what each class is worth if you trade it at the EMIT bar')
    print('W|class|opens|trades|net>0|net>0 %|stopped|net sum|per trade')
    for via in ('confirmed', 'lookback', 'gap', 'forward'):
        v = by.get(via, [])
        if not v: continue
        opens = sorted({e for _n, e in v if rig.gate_open(e)})
        if not opens: continue
        T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
        if not T: continue
        n, w, ns, t_ = score(px, T, CAP)
        print('W|%s|%d|%d|%d|%.1f%%|%d|%+.3f|%+.4f'
              % (via, len(opens), n, w, 100.0*w/n, ns, t_, t_/n))
    return 0


if __name__ == '__main__':
    sys.exit(main())
