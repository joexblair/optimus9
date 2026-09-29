"""measure_live_stop - what changes when the 0.70% stop becomes a LIVE exit instead of a score rewrite.

Joe 0929-late: *"research how a stop is applied in trading - you'll learn that it's both: (at its
signal or flip bar) OR (at the stop bar)"*.

A stop does not REPLACE the other exits. It RACES them. Three exits are live on an open trade -
an opposing-dr sig_utc, the dr-flip backstop, and the 0.70% stop - and the trade ends at whichever
fires first. The others are cancelled. Today `sweep_mae_cap.py` applies the cap AFTER the walk, so
the trade still runs to its signal/flip bar and only the SCORE is rewritten.

WHAT THIS MEASURES
  1. the freed window - for each stopped trade, how many bars earlier it ends, and how many ungated
     sig_utc bars fall inside the window that frees up
  2. the full re-walk with the stop live, so the new trades those windows create are counted
  3. the same-bar collisions, which are unruled tie-breaks

TWO VARIANTS, because one concretion is UNSPECIFIED: may an ungated sig_utc open a trade on the
stop bar ITSELF? The dr-flip bar is closed to opens (`continue` in the walk). Whether the stop bar
is too has not been ruled. Both are run.

    python3 measure_live_stop.py
"""
import sys, io, numpy as np, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
import sweep_v3_signal as S
sys.stderr = _e

FROM_MS, TO_MS = 1781049600000, 1788825600000          # 2026-06-10 .. 2026-09-08, ~90 days
CAP = 0.70                                              # Joe ruled it


def adv_at(px, o, k, d):
    """The adverse excursion at bar k for a trade opened at o with dr d, as a % of entry.
    Negative is against the trade. -adv >= CAP is the stop."""
    e = float(px[o])
    return -((float(px[k]) - e) / e * 100.0) * d


def walk(opens, dr, px, start, end, cap=None, open_on_stop_bar=False):
    """The banked walk, optionally with the stop as a LIVE exit racing the other two.

    cap=None reproduces sweep_mae_cap.py exactly. cap=0.70 makes the stop a third exit.
    Returns (trades, still_open, collisions).
    """
    O = set(int(x) for x in opens); start = max(1, int(start)); out = []; pos = None
    coll = dict(stop_and_flip=0, stop_and_sig=0)
    for k in range(start, int(end) + 1):
        if pos is not None:
            d = int(dr[k])
            flip = pos['left'] and d == pos['dr'] and d != int(dr[k - 1])
            stop = cap is not None and -adv_at(px, pos['open'], k, pos['dr']) >= cap
            if stop and flip:
                coll['stop_and_flip'] += 1
            if stop and k in O:
                coll['stop_and_sig'] += 1
            if stop:                                     # Joe: the stop wins a same-bar tie
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='stop'))
                pos = None
                if not open_on_stop_bar:
                    continue
            else:
                if d == -pos['dr'] and d != 0:
                    pos['left'] = True
                if flip:
                    out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                    opened_by=pos['opened_by'], closed_by='dr-flip'))
                    pos = None; continue
        if k in O:
            d = int(dr[k])
            if pos is not None and not (d == -pos['dr'] and d != 0):
                continue
            if pos is not None:
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='sig_utc'))
            pos = dict(open=k, dr=d, opened_by='sig_utc', left=False)
    return out, pos, coll


def score(px, T, cap):
    """-cap for a stopped trade, else mfe - mae over its span. Joe's rule."""
    tot = 0.0; w = 0; ns = 0
    for t in T:
        o, c, d = t['open'], t['close'], t['dr']
        e = float(px[o])
        mv = (np.asarray(px[o:c + 1], float) - e) / e * 100.0
        adv = -mv * d
        if (-np.minimum.accumulate(adv) >= cap).any():
            ns += 1; tot += -cap
        else:
            v = float(adv.max()) - float(-adv.min())
            tot += v
            if v > 0: w += 1
    return len(T), w, ns, tot


def build(rig):
    """The signal chain at the banked knobs - lifted verbatim from sweep_mae_cap.main()."""
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
    sig = set()
    for m in coil_moments(ann):
        d = m['dr']
        cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        if ex['rev'] is not None and A <= int(ex['rev']) <= B:
            sig.add(int(ex['rev']))
    return sig, sorted(k for k in sig if rig.gate_open(k))


def main():
    rig = S.Rig((FROM_MS, TO_MS)); px = rig.px; B = rig.B
    sig, opens = build(rig)
    O = set(opens)
    print('B|sig bars %d|rule#1 open %d' % (len(sig), len(opens)))

    # --- the mech as handed over: cap in SCORING only -------------------------------------
    T0, _, _ = walk(opens, rig.DRW, px, min(opens), B, cap=None)
    n0, w0, ns0, tot0 = score(px, T0, CAP)
    print('R|scoring-only|trades %d|net>0 %d (%.1f%%)|stopped %d (%.1f%%)|net sum %+.3f|per trade %+.4f'
          % (n0, w0, 100.0*w0/n0, ns0, 100.0*ns0/n0, tot0, tot0/n0))

    # --- the freed window, per stopped trade ----------------------------------------------
    freed = []; sig_in_gap = 0; gaps_with_sig = 0
    for t in T0:
        o, c, d = t['open'], t['close'], t['dr']
        e = float(px[o])
        adv = -((np.asarray(px[o:c+1], float) - e) / e * 100.0) * d
        hit = np.flatnonzero(-np.minimum.accumulate(adv) >= CAP)
        if not hit.size: continue
        sbar = o + int(hit[0])
        freed.append(c - sbar)
        g = sum(1 for k in range(sbar + 1, c + 1) if k in O)
        sig_in_gap += g
        if g: gaps_with_sig += 1
    f = np.array(freed)
    print('F|stopped trades %d' % f.size)
    print('F|bars freed  p25 %d|median %d|p75 %d|max %d|mean %.1f'
          % (np.percentile(f,25), np.median(f), np.percentile(f,75), f.max(), f.mean()))
    print('F|seconds freed  median %d|max %d' % (np.median(f)*5, f.max()*5))
    print('F|ungated sig_utc bars inside the freed windows: %d, across %d of %d freed windows'
          % (sig_in_gap, gaps_with_sig, f.size))

    # --- the stop as a LIVE exit, both variants -------------------------------------------
    for oosb in (False, True):
        T, _, coll = walk(opens, rig.DRW, px, min(opens), B, cap=CAP, open_on_stop_bar=oosb)
        n, w, ns, tot = score(px, T, CAP)
        by = {}
        for t in T: by[t['closed_by']] = by.get(t['closed_by'], 0) + 1
        lab = 'open allowed on the stop bar' if oosb else 'stop bar CLOSED to opens'
        print('L|%s|trades %d|net>0 %d (%.1f%%)|stopped %d (%.1f%%)|net sum %+.3f|per trade %+.4f'
              % (lab, n, w, 100.0*w/n, ns, 100.0*ns/n, tot, tot/n))
        print('L|  closed by: %s' % '  '.join('%s %d' % kv for kv in sorted(by.items())))
        print('L|  same-bar collisions: stop+flip %d   stop+sig_utc %d'
              % (coll['stop_and_flip'], coll['stop_and_sig']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
