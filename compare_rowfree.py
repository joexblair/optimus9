"""compare_rowfree - the row-free moment definition, measured beside the banked one.

Joe 0929-late chose option C: measure it, change nothing.

TODAY a `wsf_dtf_v3` ROW prints only where a timeframe's sideways run is long enough AND its r-line
is outside the fence. A moment is a run of consecutive same-dr ROWS carrying support_min 23. The
moment's end is only knowable when the NEXT row prints - that wait is 100% of the emission lag.

ROW-FREE the support count is `(m + Mage)/2 - r` per timeframe, counted at EVERY 5 s bar. A moment
is a run of consecutive BARS at or above support_min 23 inside one dr run. The end is the bar the
count drops below 23 - knowable at that bar.

  IT DROPS THE SIDEWAYS + FENCE QUALIFIER FROM THE MOMENT DEFINITION. That test is what makes a
  ROW; support is what makes a MOMENT. Row-free keeps the second and loses the first. That is the
  whole reason the signal set can move, and it is the thing Joe has to price.

Three variants, same downstream (release -> coil_exit.resolve -> rule#1 gate -> walk with the stop):

  ROWS               the banked mech
  BARS bounded       row-free moments, release still searching [i0, i1]
  BARS unbounded     row-free moments, release scanning forward from i0 with no i1 bound

NOTHING IS BANKED AND NO KNOB MOVES.

    python3 compare_rowfree.py
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


def support(rig, cfg):
    """SUP[k] / SUPM[k] - how many timeframes carry a positive / negative coil at bar k.
    Pure per-bar arithmetic on three lines. No rows, no DB."""
    tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
    SUP = np.zeros(rig.n, np.int16); SUPM = np.zeros(rig.n, np.int16)
    for tf in tfs:
        SUP += (rig.D[tf] > 0).astype(np.int16); SUPM += (rig.D[tf] < 0).astype(np.int16)
    return tfs, SUP, SUPM


def ann_rows(rig, cfg, segs, tfs, SUP, SUPM):
    """The banked shape: one entry per wsf_dtf_v3 row."""
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
    return [dict(i=i, dr=d, ok=bool((SUP[i] if d > 0 else SUPM[i]) >= cfg['support_min']))
            for (i, tf, d) in rows]


def ann_bars(rig, cfg, segs, SUP, SUPM):
    """The row-free shape: one entry per BAR, inside each dr run."""
    smin = cfg['support_min']; out = []
    for (a_, b_, d) in segs:
        if not d: continue
        c = SUP[a_:b_ + 1] if d > 0 else SUPM[a_:b_ + 1]
        ok = c >= smin
        for j in range(len(ok)):
            out.append(dict(i=a_ + j, dr=d, ok=bool(ok[j])))
    return out


def run(rig, cfg, ann, LEGS, lag, look, unbounded):
    """-> (n_moments, [(sig_bar, emit_bar, via)])"""
    A, B = rig.A, rig.B
    ms = coil_moments(ann)
    out = []
    for m in ms:
        d = m['dr']
        cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        hi = (rig.n - 1) if unbounded else m['i1']
        p, conf = release(cc, m['i0'], hi, lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        if ex['rev'] is None: continue
        sig = int(ex['rev'])
        if not (A <= sig <= B): continue
        brk = m['brk'] if m['brk'] is not None else m['i1']
        emit = max(int(brk), sig, int(coil_exit.fired(ex)[1]))
        out.append((sig, emit, ex['via']))
    return len(ms), out


def report(rig, lab, nm, res, base=None):
    px = rig.px; B = rig.B
    sigs = sorted({s for s, _e, _v in res})
    lags = np.array([(e - s) * 5 for s, e, _v in res]) if res else np.array([0])
    via = {}
    for _s, _e, v in res: via[v] = via.get(v, 0) + 1
    print('S|%s|moments %d|resolved %d|distinct sig bars %d' % (lab, nm, len(res), len(sigs)))
    print('S|  via: %s' % '  '.join('%s %d' % kv for kv in sorted(via.items())))
    print('S|  emit lag s: at 0 %d (%.1f%%)|median %d|p75 %d|p90 %d|max %d'
          % (int((lags == 0).sum()), 100.0 * (lags == 0).sum() / lags.size,
             np.median(lags), np.percentile(lags, 75), np.percentile(lags, 90), lags.max()))
    opens = sorted(k for k in sigs if rig.gate_open(k))
    if opens:
        T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
        if T:
            n, w, ns, tot = score(px, T, CAP)
            print('S|  rule#1 open %d|trades %d|net>0 %d (%.1f%%)|stopped %d (%.1f%%)|'
                  'net sum %+.3f|per trade %+.4f'
                  % (len(opens), n, w, 100.0*w/n, ns, 100.0*ns/n, tot, tot/n))
    if base is not None:
        bs = np.array(sorted(base))
        ss = np.array(sigs)
        exact = len(set(sigs) & set(base))
        if ss.size and bs.size:
            j = np.searchsorted(bs, ss)
            j = np.clip(j, 1, len(bs) - 1) if len(bs) > 1 else np.zeros(len(ss), int)
            d = np.minimum(np.abs(ss - bs[j]), np.abs(ss - bs[j - 1])) if len(bs) > 1 \
                else np.abs(ss - bs[0])
            print('S|  vs ROWS: exact match %d of %d|within 1 min %d|within 5 min %d|'
                  'median distance to nearest %d s'
                  % (exact, len(sigs), int((d <= 12).sum()), int((d <= 60).sum()),
                     int(np.median(d) * 5)))
    print()
    return sigs


def main():
    rig = S.Rig((FROM_MS, TO_MS))
    cfg = dict(S.BASE)
    segs = rig.segs_for(rig.A, rig.B)
    tfs, SUP, SUPM = support(rig, cfg)
    lag = cfg['confirm_lag_s'] // 5; look = cfg['lookback_s'] // 5
    LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
    print('B|window 2026-06-10 .. 2026-09-08 = 90 days|support_min %d' % cfg['support_min'])
    print()
    aR = ann_rows(rig, cfg, segs, tfs, SUP, SUPM)
    nm, res = run(rig, cfg, aR, LEGS, lag, look, False)
    base = report(rig, 'ROWS - the banked mech', nm, res)
    sys.stdout.flush()

    aB = ann_bars(rig, cfg, segs, SUP, SUPM)
    print('B|row-free entries %d bars vs %d rows' % (len(aB), len(aR)))
    print()
    for unb in (False, True):
        nm, res = run(rig, cfg, aB, LEGS, lag, look, unb)
        report(rig, 'BARS - release %s' % ('UNBOUNDED' if unb else 'bounded [i0,i1]'),
               nm, res, base)
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    sys.exit(main())
