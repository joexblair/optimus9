"""sweep_confirm_lag - confirm_lag_s scored on SIGNAL SURVIVAL, LAG and NET PER TRADE.

Joe 0930: *"180s was an arbitrary and non-proven value. now I'm interested in reducing it to a point
where we don't lose any existing siganls while improving the overall lag of `signal`"*.

WHY THIS RUN EXISTS. The 0917 sweep scored this knob on `hit` - whether the release landed on the
moment's maximum-coil bar - and on `coil %`, the share of the available coil captured. Both were
reproduced on 0930: the ceiling matches the spec's 7202.0 to the decimal, and `hit` tracks within
1-4 on every rung, so the metric is settled. NEITHER COLUMN MEASURES THE LAG AND NEITHER MEASURES
NET PER TRADE. This run scores the two things Joe is now optimising.

WHAT LOWERING IT DOES, from the code:
    if lag_bars > 0 and len(w) and w.max() > v[t]: continue
  a shorter window has FEWER chances to disconfirm, so MORE releases confirm and moments move OFF
  the lookback/gap/forward ladder onto CONFIRMED. No moment is lost - each one's BAR changes.
  At lag_bars = 0 the disconfirm test is skipped outright and every down-tick qualifies.

  It also moves `actionable_confirmed = release + lag_bars`, which is where first_forward() starts
  searching for the signal. So the knob is both a quality filter AND a dead zone before the search.

SURVIVAL is set inclusion against the banked 1,863 sig bars, not a count - a moment that changes
branch still emits a signal, just on a different bar.

    python3 sweep_confirm_lag.py
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


def main():
    rig = S.Rig((FROM_MS, TO_MS)); px = rig.px; A, B = rig.A, rig.B
    cfg = dict(S.BASE); segs = rig.segs_for(A, B)
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
    look = cfg['lookback_s'] // 5
    LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
    MS = list(coil_moments(ann))

    def arm(lag):
        res = []; via = {}
        for m in MS:
            d = m['dr']; cc = (lambda i, _d=d: float(rig.CC[i] * _d))
            p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
            ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
            if ex['rev'] is None: continue
            sig = int(ex['rev'])
            if not (A <= sig <= B): continue
            brk = int(m['brk']) if m['brk'] is not None else int(m['i1'])
            act = int(coil_exit.fired(ex)[1])
            res.append((sig, max(brk, sig, act), ex['via']))
            via[ex['via']] = via.get(ex['via'], 0) + 1
        return res, via

    base_res, _ = arm(cfg['confirm_lag_s'] // 5)
    BASE = set(s for s, _e, _v in base_res)
    print('B|banked confirm_lag_s %d|sig bars %d' % (cfg['confirm_lag_s'], len(BASE)))
    print()
    print('C|lag s|conf|lb|gap|fwd|sig bars|of the 1863 SURVIVING|survive %|new bars|'
          'lag at0|lag med|lag p90|lag max|rule#1 open|trades|net>0|stopped|net sum|per trade')
    for lag_s in [0] + list(range(5, 181, 5)):
        lag = lag_s // 5
        res, via = arm(lag)
        bars = set(s for s, _e, _v in res)
        la = np.array([(e - s) * 5 for s, e, _v in res])
        opens = sorted(k for k in bars if rig.gate_open(k))
        T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
        n, w, ns, tot = score(px, T, CAP)
        surv = len(BASE & bars)
        print('C|%d|%d|%d|%d|%d|%d|%d|%.1f%%|%d|%d (%.1f%%)|%d|%d|%d|%d|%d|%d (%.1f%%)|%d|%+.3f|%+.4f'
              % (lag_s, via.get('confirmed', 0), via.get('lookback', 0), via.get('gap', 0),
                 via.get('forward', 0), len(bars), surv, 100.0 * surv / len(BASE),
                 len(bars - BASE),
                 int((la == 0).sum()), 100.0 * (la == 0).sum() / la.size,
                 np.median(la), np.percentile(la, 90), la.max(),
                 len(opens), n, w, 100.0 * w / n, ns, tot, tot / n))
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
