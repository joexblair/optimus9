"""oos_confirm_lag - 180 vs 165 on data the 165 choice never saw.

Joe 0930: *"I'm proposing 165 - we need to OOS it"*.

THE WINDOWS. The tape is a fixed 94.5-day width ending at END_MS, so the OOS comes from two caches
and only the UNSEEN slice of each is scored:

    IS     END_MS 2026-09-08 00:00   score 2026-06-10 -> 2026-09-08   the window 165 was picked on
    OOS-A  END_MS 2026-08-09 12:00   score 2026-05-07 -> 2026-06-10   34 days, never seen
    OOS-B  END_MS 2026-09-30 00:00   score 2026-09-08 -> 2026-09-30   21 days, never seen

END_MS is set on the module BEFORE the downstream importers read it, so one process can walk all
three. WARMUP IS MEASURED, NOT ASSUMED: the analysis window starts at the first bar where every line
the chain reads is finite, computed from the arrays.

ARMS 1 AND 2 ONLY - confirm_lag_s 180 and 165, release search bounded at i1 as banked. Arms 3 and 4
(unbounded search) wait on Joe's ruling: is a release found after the moment has ended still that
moment's release? 129 of 937 land past the breaking row.

SURVIVAL is measured inside each window against THAT WINDOW'S OWN 180 set, so it answers "does 165
keep the signals 180 would have produced here" - not a comparison to the IS window's bars.

    python3 oos_confirm_lag.py
"""
import sys, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import optimus9.orchestration.build_ws_lines as BWL

MS = lambda y, m, d, h=0: int(dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp() * 1000)
WINDOWS = [
    ('IS    06-10..09-08', MS(2026, 9, 8), MS(2026, 6, 10), MS(2026, 9, 8)),
    ('OOS-A 05-07..06-10', MS(2026, 8, 9, 12), MS(2026, 5, 7), MS(2026, 6, 10)),
    ('OOS-B 09-08..09-30', MS(2026, 9, 30), MS(2026, 9, 8), MS(2026, 9, 30)),
]
CAP = 0.70


def run_window(lbl, end_ms, w0, w1):
    BWL.END_MS = end_ms
    BWL.TAPE_END = dt.datetime.fromtimestamp(end_ms / 1000, dt.timezone.utc)
    # build_wsf_trades MUST be here. It binds END_MS BY VALUE at its line 61
    # (`from ...build_ws_lines import END_MS, HOURS, WARMUP`), so mutating BWL.END_MS above does
    # NOT rebind it - it keeps whatever window imported it first. Rig.__init__ then reads the
    # rule#1 r lines and px from it while indexing them off report_coil_exit's tape. 0930: that
    # gated OOS-A 509,760 bars (29.5 d) and OOS-B 380,160 bars (22.0 d) out of register.
    for m in [k for k in list(sys.modules) if k in
              ('report_coil_exit', 'sweep_v3_signal', 'measure_live_stop',
               'build_wsf_trades')]:
        del sys.modules[m]
    import sweep_v3_signal as S
    from measure_live_stop import score
    from optimus9.compute.trade_walk import walk
    from optimus9.compute.coil_moment import moments as coil_moments, release
    from optimus9.compute import coil_exit
    from optimus9.analysis.jig import ws1mage_rev

    rig = S.Rig((w0, w1)); cfg = dict(S.BASE); ts = rig.ts; px = rig.px
    U = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M')
    tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
    # WARMUP, MEASURED: the first bar where every line the chain reads is finite
    fin = 0
    for tf in tfs:
        for r in ('m', 'Mage', 'r'):
            a = np.asarray(rig.lines['ws%d' % tf][r], float)
            fin = max(fin, int(np.argmax(np.isfinite(a))))
    for nm in ('ws1', rig.C['sig_line'].replace('Mage', '')):
        for r in ('m', 'Mage', 'r'):
            a = np.asarray(rig.lines[nm][r], float)
            fin = max(fin, int(np.argmax(np.isfinite(a))))
    A = max(rig.A, fin); B = rig.B
    print('W|%s|END_MS %s|tape %s -> %s|scored %s -> %s|first all-finite bar %s|bars %d (%.1f d)'
          % (lbl, dt.datetime.fromtimestamp(end_ms/1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M'),
             U(0), U(len(ts)-1), U(A), U(B), U(fin), B - A + 1, (B - A + 1) * 5 / 86400.0))
    sys.stdout.flush()

    segs = []; s = A
    for k in range(A + 1, B + 1):
        if rig.DR[k] != rig.DR[k - 1]: segs.append((s, k - 1, int(rig.DR[s]))); s = k
    segs.append((s, B, int(rig.DR[s])))
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
    MSM = list(coil_moments(ann))
    out = {}
    for lag_s in (180, 165):
        lag = lag_s // 5
        res = []; via = {}
        for m in MSM:
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
        bars = sorted({s_ for s_, _e, _v in res})
        la = np.array([(e - s_) * 5 for s_, e, _v in res])
        opens = sorted(k for k in bars if rig.gate_open(k))
        T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP) if opens else ([], None)
        n = w = ns = 0; tot = 0.0
        if T: n, w, ns, tot = score(px, T, CAP)
        out[lag_s] = dict(bars=set(bars), via=via, la=la, opens=len(opens), n=n, w=w, ns=ns, tot=tot,
                          moments=len(MSM))
    return out


def main():
    print('R|window|lag s|moments|conf|lb|gap|fwd|sig bars|survive vs its own 180|survive %|'
          'new bars|lag at0|lag med|lag p90|rule#1 open|trades|net>0|stopped|net sum|per trade')
    for (lbl, end_ms, w0, w1) in WINDOWS:
        o = run_window(lbl, end_ms, w0, w1)
        b180 = o[180]['bars']
        for lag_s in (180, 165):
            r = o[lag_s]; la = r['la']
            surv = len(b180 & r['bars'])
            print('R|%s|%d|%d|%d|%d|%d|%d|%d|%d|%.1f%%|%d|%d (%.1f%%)|%d|%d|%d|%d|%d (%.1f%%)|%d|'
                  '%+.3f|%s'
                  % (lbl, lag_s, r['moments'], r['via'].get('confirmed', 0),
                     r['via'].get('lookback', 0), r['via'].get('gap', 0), r['via'].get('forward', 0),
                     len(r['bars']), surv, 100.0 * surv / max(1, len(b180)),
                     len(r['bars'] - b180),
                     int((la == 0).sum()), 100.0 * (la == 0).sum() / max(1, la.size),
                     np.median(la) if la.size else 0, np.percentile(la, 90) if la.size else 0,
                     r['opens'], r['n'], r['w'], 100.0 * r['w'] / max(1, r['n']), r['ns'], r['tot'],
                     ('%+.4f' % (r['tot'] / r['n'])) if r['n'] else '-'))
            sys.stdout.flush()
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
