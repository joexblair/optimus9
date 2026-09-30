"""standalone_actionable - `actionable` as a causal EVENT, with no wsf_dtf_v3 row anywhere.

Joe 0930: *"I'm trying to fix the gap rule issues so that we can decouple from a v3 row and use
causal calculations to create a standalone (no v3) `actionable` EVENT"*.

WHAT A v3 ROW ACTUALLY IS. Not a measurement - a de-duplication:

    q  = sideways & isfinite(r) & ((r < fence_lo) | (r > fence_hi))   # a PER-BAR mask, every bar
    rows.append((a_ + argmax(q[a_:b_+1]), tf, d))                     # the FIRST true bar only

Everything the row asserts is true at every bar the mask is true. The row picks the first.

THE QUALIFIED SUPPORT COUNT, per bar, row-free:

    Q[k] = how many timeframes have, AT BAR k:  sideways  AND  r outside the fence
                                                AND  the coil on the dr side

  The banked mech's support test counts only the coil sign, and applies it at ROW bars. This applies
  the row's own qualifier at EVERY bar. That is the piece that has never been measured - the earlier
  row-free run dropped the qualifier entirely and is not evidence about this.

THE EPISODE, row-free:
    opens  the bar Q reaches support_min          - knowable at that bar
    ends   the bar Q drops below support_min      - knowable at that bar
    dr     bounded by the dr run, as the banked mech does

THE EVENT:
    release()  unchanged, searching inside the episode
    actionable = release bar + confirm_lag_s      - knowable at that bar

  An episode whose coil never confirms a release gets NO actionable. The banked mech substitutes a
  mage-rev or a row on those; a standalone event has nothing to substitute, and that is Joe's call,
  not a gap to paper over.

NOTHING IS BANKED AND NO KNOB MOVES.

    python3 standalone_actionable.py
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


def runs(ok, off):
    """-> [(i0, i1, fail_bar)] for every run of True in `ok`, bar-indexed from `off`."""
    if not ok.any(): return []
    d = np.diff(np.concatenate(([0], ok.view(np.int8), [0])))
    st = np.flatnonzero(d == 1); en = np.flatnonzero(d == -1) - 1
    return [(off + int(a), off + int(b),
             (off + int(b) + 1) if (b + 1) < len(ok) else None) for a, b in zip(st, en)]


def main():
    rig = S.Rig((FROM_MS, TO_MS)); px = rig.px; A, B = rig.A, rig.B
    cfg = dict(S.BASE); segs = rig.segs_for(A, B)
    tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
    FL, FH = cfg['fence_lo'], cfg['fence_hi']
    smin = cfg['support_min']
    lag = cfg['confirm_lag_s'] // 5; look = cfg['lookback_s'] // 5
    LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])

    # ---- the qualifier, per bar, per timeframe -----------------------------------------
    Q = {}
    for tf in tfs:
        sw = rig.sideways(tf, cfg); r = rig.R[tf]
        Q[tf] = sw & np.isfinite(r) & ((r < FL) | (r > FH))
    QP = np.zeros(rig.n, np.int16); QM = np.zeros(rig.n, np.int16)
    for tf in tfs:
        QP += (Q[tf] & (rig.D[tf] > 0)).astype(np.int16)
        QM += (Q[tf] & (rig.D[tf] < 0)).astype(np.int16)
    print('B|window 2026-06-10 .. 2026-09-08 = 90 days|timeframes %d|support_min %d' % (len(tfs), smin))
    print('B|qualified support count, per bar:  max dr+1 %d   max dr-1 %d   bars at/above %d: %d'
          % (QP.max(), QM.max(), smin, int((QP >= smin).sum() + (QM >= smin).sum())))

    # ---- the banked mech, for the comparison -------------------------------------------
    SUP = np.zeros(rig.n, np.int16); SUPM = np.zeros(rig.n, np.int16)
    for tf in tfs:
        SUP += (rig.D[tf] > 0).astype(np.int16); SUPM += (rig.D[tf] < 0).astype(np.int16)
    rws = []
    for tf in tfs:
        for (a_, b_, d) in segs:
            if not d: continue
            seg = Q[tf][a_:b_ + 1]
            if seg.any(): rws.append((a_ + int(np.argmax(seg)), tf, d))
    rws.sort(key=lambda x: (x[0], x[1]))
    ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d > 0 else SUPM[i]) >= smin)) for (i, tf, d) in rws]
    base_sig = []
    for m in coil_moments(ann):
        d = m['dr']; cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        if ex['rev'] is None: continue
        s_ = int(ex['rev'])
        if A <= s_ <= B: base_sig.append(s_)
    BASE = sorted(set(base_sig))
    print('B|banked mech: %d sig bars' % len(BASE))
    print()

    # ---- the qualified count's own distribution ----------------------------------------
    print('D|qualified count|bars at exactly this count (dr+1)|bars at or above (dr+1)|'
          'bars at exactly (dr-1)|bars at or above (dr-1)')
    for c in range(0, int(max(QP.max(), QM.max())) + 1):
        print('D|%d|%d|%d|%d|%d' % (c, int((QP == c).sum()), int((QP >= c).sum()),
                                    int((QM == c).sum()), int((QM >= c).sum())))
    print()

    # ---- the standalone episodes, across every reachable threshold ---------------------
    print('T|support_min|episodes|len p50|len max|with a release|actionable events|'
          'rule#1 open|trades|net>0|stopped|net sum|per trade')
    for smin_ in range(1, int(max(QP.max(), QM.max())) + 1):
        eps = []
        for (a_, b_, d) in segs:
            if not d: continue
            c = (QP if d > 0 else QM)[a_:b_ + 1]
            for (i0, i1, fb) in runs(c >= smin_, a_):
                eps.append((i0, i1, fb, d))
        if not eps:
            print('T|%d|0|-|-|-|-|-|-|-|-|-|-' % smin_); sys.stdout.flush(); continue
        lens = np.array([e[1] - e[0] + 1 for e in eps])
        act = []
        for (i0, i1, fb, d) in eps:
            cc = (lambda i, _d=d: float(rig.CC[i] * _d))
            p_, conf = release(cc, i0, i1, lag, last_bar=rig.n - 1)
            if not conf: continue
            a_bar = int(p_) + lag
            if A <= a_bar <= B: act.append(a_bar)
        bars = sorted(set(act))
        opens = sorted(k for k in bars if rig.gate_open(k))
        row = 'T|%d|%d|%d|%d|%d|%d' % (smin_, len(eps), np.median(lens), lens.max(),
                                       len(act), len(bars))
        if opens:
            T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
            if T:
                n, w, ns, tot = score(px, T, CAP)
                row += '|%d|%d|%d (%.1f%%)|%d (%.1f%%)|%+.3f|%+.4f' % (
                    len(opens), n, w, 100.0*w/n, ns, 100.0*ns/n, tot, tot/n)
            else:
                row += '|%d|0|-|-|-|-' % len(opens)
        else:
            row += '|0|-|-|-|-|-'
        print(row); sys.stdout.flush()
    print()
    print('R|banked mech - wsl_sig_utc, for the comparison')
    opens = sorted(k for k in BASE if rig.gate_open(k))
    T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
    n, w, ns, tot = score(px, T, CAP)
    print('R|sig bars %d|rule#1 open %d|trades %d|net>0 %d (%.1f%%)|stopped %d|net sum %+.3f|'
          'per trade %+.4f' % (len(BASE), len(opens), n, w, 100.0*w/n, ns, tot, tot/n))
    print('R|LAG: standalone actionable is release+180s and reads no row -> 0 s, by construction')
    return 0


if __name__ == '__main__':
    sys.exit(main())
