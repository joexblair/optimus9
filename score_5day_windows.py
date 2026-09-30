"""score_5day_windows - every 5-day window across all available data, scored individually.

Joe 0930: *"block to exclude: break the voliatile span into small 5 day windows and score them
individually - drop the ones that have a notable adversial deviataion"*.

WHY IT SCORES EVERYTHING, NOT JUST THE VOLATILE SPAN. An outlier cannot be identified without the
distribution it is an outlier in. The slide runs 05-10 high 0.27 -> 06-06 low 0.10, -63.1% over 27
days, but "notable" only means something against the other windows. So all 29 windows from 05-07 to
09-29 are scored and the price move is reported BESIDE the result, per window.

TWO CACHES, because the tape is a fixed 94.5-day width:
    A  END_MS 2026-08-09 12:00  covers 2026-05-07 00:00 -> 2026-08-09 11:59
    B  END_MS 2026-09-30 00:00  covers 2026-06-27 12:00 -> 2026-09-29 23:59
A serves every window that fits inside it; B serves the rest. The cache used is reported per window
so a window is never silently compared across two builds.

WARMUP IS MEASURED, not assumed: a window is only scored from the first bar at which every line the
chain reads is finite.

KNOBS AS BANKED - confirm_lag_s 180, release bounded at i1, MAE cap 0.70. Nothing is excluded here;
this run produces the evidence for WHICH windows Joe drops.

    python3 score_5day_windows.py
"""
import sys, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import optimus9.orchestration.build_ws_lines as BWL

MS = lambda *a: int(dt.datetime(*a, tzinfo=dt.timezone.utc).timestamp() * 1000)
DAY = 86400000
CAP = 0.70
CACHES = [('A', MS(2026, 8, 9, 12), MS(2026, 5, 7), MS(2026, 8, 9, 12)),
          ('B', MS(2026, 9, 30), MS(2026, 6, 27, 12), MS(2026, 9, 30))]


def chain(rig, cfg, A, B):
    from optimus9.compute.coil_moment import moments as coil_moments, release
    from optimus9.compute import coil_exit
    from optimus9.analysis.jig import ws1mage_rev
    tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
    FL, FH = cfg['fence_lo'], cfg['fence_hi']
    segs = []; s = A
    for k in range(A + 1, B + 1):
        if rig.DR[k] != rig.DR[k - 1]: segs.append((s, k - 1, int(rig.DR[s]))); s = k
    segs.append((s, B, int(rig.DR[s])))
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
    sig = set()
    for m in coil_moments(ann):
        d = m['dr']; cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
        if ex['rev'] is not None and A <= int(ex['rev']) <= B: sig.add(int(ex['rev']))
    return sorted(sig)


def finite_from(rig, cfg):
    fin = 0
    for tf in [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]:
        for r in ('m', 'Mage', 'r'):
            a = np.asarray(rig.lines['ws%d' % tf][r], float)
            fin = max(fin, int(np.argmax(np.isfinite(a))))
    for nm in ('ws1', rig.C['sig_line'].replace('Mage', '')):
        for r in ('m', 'Mage', 'r'):
            a = np.asarray(rig.lines[nm][r], float)
            fin = max(fin, int(np.argmax(np.isfinite(a))))
    return fin


def main():
    w0 = MS(2026, 5, 7); wN = MS(2026, 9, 30)
    wins = [(w0 + i * 5 * DAY, w0 + (i + 1) * 5 * DAY)
            for i in range((wN - w0) // (5 * DAY))]
    print('B|5-day windows from %s to %s|%d windows'
          % (dt.datetime.fromtimestamp(w0/1000, dt.timezone.utc).strftime('%Y-%m-%d'),
             dt.datetime.fromtimestamp(wN/1000, dt.timezone.utc).strftime('%Y-%m-%d'), len(wins)))
    print('W|#|from|to|cache|px first|px last|px move %|px range %|sig bars|rule#1 open|trades|'
          'net>0|net>0 %|stopped|MAE sum|MFE sum|net sum|per trade')
    rows_out = []
    for (cl, end_ms, c0, c1) in CACHES:
        mine = [w for w in wins if w[0] >= c0 and w[1] <= c1
                and not any(r[0] == w[0] for r in rows_out)]
        if not mine: continue
        BWL.END_MS = end_ms
        BWL.TAPE_END = dt.datetime.fromtimestamp(end_ms / 1000, dt.timezone.utc)
        # build_wsf_trades MUST be here - see the note in oos_confirm_lag.run_window. It binds
        # END_MS by value at import, so without this the second cache reads rule#1's r lines off
        # the first cache's tape.
        for m in [k for k in list(sys.modules)
                  if k in ('report_coil_exit', 'sweep_v3_signal', 'measure_live_stop',
                           'build_wsf_trades')]:
            del sys.modules[m]
        import sweep_v3_signal as S
        from measure_live_stop import score
        from optimus9.compute.trade_walk import walk
        rig = S.Rig((c0, c1)); cfg = dict(S.BASE); ts = rig.ts; px = rig.px
        fin = finite_from(rig, cfg)
        for (a_ms, b_ms) in mine:
            A = max(int(np.searchsorted(ts, a_ms)), fin)
            B = min(int(np.searchsorted(ts, b_ms)), rig.n - 1)
            if B - A < 2000: continue
            sig = chain(rig, cfg, A, B)
            opens = sorted(k for k in sig if rig.gate_open(k))
            n = w = ns = 0; tot = 0.0; smae = smfe = 0.0
            if opens:
                T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
                if T:
                    n, w, ns, tot = score(px, T, CAP)
                    for t in T:
                        o, c, d = t['open'], t['close'], t['dr']
                        e = float(px[o])
                        adv = -((np.asarray(px[o:c+1], float) - e) / e * 100.0) * d
                        smae += float(-np.minimum.accumulate(adv)[-1]); smfe += float(adv.max())
            p0 = float(px[A]); p1 = float(px[B])
            pmin = float(np.min(px[A:B+1])); pmax = float(np.max(px[A:B+1]))
            rows_out.append((a_ms, cl, A, B, p0, p1, pmin, pmax, len(sig), len(opens),
                             n, w, ns, smae, smfe, tot))
            sys.stdout.flush()
    U = lambda ms: dt.datetime.fromtimestamp(ms/1000, dt.timezone.utc).strftime('%m-%d')
    rows_out.sort()
    per = []
    for i, (a_ms, cl, A, B, p0, p1, pmin, pmax, nsig, nop, n, w, ns, smae, smfe, tot) in \
            enumerate(rows_out, 1):
        pt = (tot / n) if n else None
        if pt is not None: per.append(pt)
        print('W|%d|%s|%s|%s|%.4f|%.4f|%+.2f%%|%.2f%%|%d|%d|%d|%d|%s|%d|%.3f|%.3f|%+.3f|%s'
              % (i, U(a_ms), U(a_ms + 5*DAY), cl, p0, p1, (p1-p0)/p0*100.0,
                 (pmax-pmin)/pmin*100.0, nsig, nop, n, w,
                 ('%.1f%%' % (100.0*w/n)) if n else '-', ns, smae, smfe, tot,
                 ('%+.4f' % pt) if pt is not None else '-'))
    if per:
        a = np.array(per)
        print('S|per-trade across %d scored windows|min %+.4f|p25 %+.4f|median %+.4f|p75 %+.4f|'
              'max %+.4f|mean %+.4f|sd %.4f' % (a.size, a.min(), np.percentile(a,25),
              np.median(a), np.percentile(a,75), a.max(), a.mean(), a.std()))
        med = np.median(a); mad = np.median(np.abs(a - med))
        print('S|median %+.4f   MAD %.4f   windows below median-3*MAD (%.4f): %s'
              % (med, mad, med - 3*mad,
                 ', '.join('#%d' % (i+1) for i, v in enumerate(per) if v < med - 3*mad) or 'none'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
