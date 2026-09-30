"""ab_lookback_value - what the LOOKBACK branch's timestamp should be. A/B, nothing banked.

Joe 0930: *"do we need to AB this before we apply?"* - yes, because 438 of 1,973 moments change
signal bar for a median 140 s gain, and rule#1 is re-evaluated at the new bar.

THE BRANCH. `resolve` enters LOOKBACK when a ws1mage-rev's cross sits in the 4 min before the
moment's last row AND its `sig_conf` is at or before that row. `_knowable` returns a LIST of them.
The rule then discards the list and uses the ROW - Joe 0917: *"'named bar''s timestamp become the
actionable time"*.

THREE ARMS. `rev` is what the walk opens on, so it is `rev` that decides the trades; the
`actionable_lookback` field moves with it for coherence.

    row        the banked rule - rev = actionable_lookback = the moment's last row
    earliest   rev = the EARLIEST qualifying sig_conf in the window
    latest     rev = the LATEST qualifying sig_conf in the window

  Joe's GAP rule says "use the first timestamp". He has never ruled it for LOOKBACK, so both ends
  of the window are defensible and both are measured.

CAUSAL on all three. `_knowable` already requires `sig_conf <= the row`, so every candidate's
confirmation has happened by the bar the banked rule uses. Moving the value earlier cannot read a
bar that has not printed.

    python3 ab_lookback_value.py
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
W5 = (1788220800000, 1788652800000)


def main():
    rig = S.Rig((FROM_MS, TO_MS)); px = rig.px; A, B = rig.A, rig.B
    cfg = dict(S.BASE); ts = rig.ts; segs = rig.segs_for(A, B)
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
    MS = list(coil_moments(ann))
    base = []
    for m in MS:
        d = m['dr']; cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        i1 = int(m['i1'])
        hits = coil_exit._knowable(LEGS[d], i1 - look, i1, i1) if ex['via'] == 'lookback' else []
        base.append((m, p, conf, ex, hits))

    print('R|arm|sig bars|lookback rows that MOVE|median move s|max move s|rule#1 open|trades|'
          'net>0|stopped|net sum|per trade|lag at0|lag median|lag p90')
    for arm in ('row', 'earliest', 'latest'):
        sigs = []; moved = []; lags = []
        for (m, p, conf, ex, hits) in base:
            i1 = int(m['i1']); brk = int(m['brk']) if m['brk'] is not None else i1
            if ex['via'] == 'lookback' and hits and arm != 'row':
                sig = int(hits[0][1] if arm == 'earliest' else hits[-1][1])
                act = sig
                if sig != int(ex['rev']): moved.append((int(ex['rev']) - sig) * 5)
            else:
                sig = int(ex['rev']); act = int(coil_exit.fired(ex)[1])
            if not (A <= sig <= B): continue
            sigs.append(sig)
            lags.append((max(brk, sig, act) - sig) * 5)
        bars = sorted(set(sigs)); la = np.array(lags)
        opens = sorted(k for k in bars if rig.gate_open(k))
        T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
        n, w, ns, tot = score(px, T, CAP)
        mv = np.array(moved) if moved else np.array([0])
        print('R|%s|%d|%d|%d|%d|%d|%d|%d (%.1f%%)|%d (%.1f%%)|%+.3f|%+.4f|%d (%.1f%%)|%d|%d'
              % (arm, len(bars), len(moved), np.median(mv), mv.max(), len(opens), n, w,
                 100.0*w/n, ns, 100.0*ns/n, tot, tot/n,
                 int((la == 0).sum()), 100.0*(la == 0).sum()/la.size,
                 np.median(la), np.percentile(la, 90)))
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
