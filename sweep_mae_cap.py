"""Sweep the MAE cap in 0.05 steps over the last 90 days of the line cache. Joe 0929.

The trades are computed ONCE - the cap changes only the scoring, not the walk - then scored at
every cap value. Both of Joe's 0929 rulings are in the walk: a sig_utc closes only on an opposing
dr, and the dr-flip backstop closes but never opens.

ENTRY IS THE sig BAR, matching the 47-trade 09-01..09-06 table. The emit-bar variant is a separate
axis and is not mixed in here.

THE CAP IS A STOP. The trade ends at the first bar its adverse excursion reaches the cap; MFE-MAE
is then -cap, per Joe: "if the cap is exceeded, print -0.9 in MFE-MAE".

    python3 sweep_mae_cap.py
"""
import sys, io, numpy as np, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
import sweep_v3_signal as S
from optimus9.compute.trade_walk import walk as twalk
sys.stderr = _e

FROM_MS, TO_MS = 1781049600000, 1788825600000          # 2026-06-10 .. 2026-09-08, ~90 days


def walk_no_flip_open(opens, dr, start, end):
    O = set(int(x) for x in opens); start = max(1, int(start)); out = []; pos = None
    for k in range(start, int(end) + 1):
        if pos is not None:
            d = int(dr[k])
            if d == -pos['dr'] and d != 0:
                pos['left'] = True
            if pos['left'] and d == pos['dr'] and d != int(dr[k - 1]):
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
    return out, pos


def trace(px, t):
    """The running adverse and favourable excursion, bar by bar, as percentages of entry."""
    o, c, d = t['open'], t['close'], t['dr']
    e = float(px[o])
    mv = (np.asarray(px[o:c + 1], float) - e) / e * 100.0
    adv = -mv * d
    return np.maximum.accumulate(adv), np.minimum.accumulate(adv)   # best-so-far, worst-so-far


def main():
    rig = S.Rig((FROM_MS, TO_MS))
    cfg = dict(S.BASE)
    # regenerate the signal chain at the banked knobs, then walk with both rulings
    A, B = rig.A, rig.B
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
    opens = sorted(k for k in sig if rig.gate_open(k))
    T, _ = walk_no_flip_open(opens, rig.DRW, min(opens), B)
    px = rig.px
    TR = [trace(px, t) for t in T]
    days = (TO_MS - FROM_MS) / 86400000.0
    print('B|window %s .. %s = %.0f days' % (
        dt.datetime.fromtimestamp(FROM_MS/1000, dt.timezone.utc).strftime('%Y-%m-%d'),
        dt.datetime.fromtimestamp(TO_MS/1000, dt.timezone.utc).strftime('%Y-%m-%d'), days))
    print('B|sig bars %d|rule#1 open %d|trades %d' % (len(sig), len(opens), len(T)))
    print()
    print('C|cap %|trades|net>0|net>0 %|stopped|stopped %|MAE sum|net sum|NET PER TRADE')
    best = None
    caps = [round(0.05 * i, 2) for i in range(1, 81)]          # 0.05 .. 4.00
    for cap in caps + [None]:
        tot = 0.0; smae = 0.0; ns = 0; w = 0
        for (best_so, worst_so) in TR:
            hit = np.flatnonzero(-worst_so >= cap) if cap is not None else np.array([], int)
            if cap is not None and hit.size:
                ns += 1; tot += -cap; smae += cap
            else:
                mae = float(-worst_so[-1]); mfe = float(best_so[-1])
                tot += mfe - mae; smae += mae
                if mfe - mae > 0: w += 1
        n = len(TR); per = tot / n
        lab = ('%.2f' % cap) if cap is not None else 'no cap'
        print('C|%s|%d|%d|%.1f%%|%d|%.1f%%|%.3f|%+.3f|%+.4f'
              % (lab, n, w, 100.0 * w / n, ns, 100.0 * ns / n, smae, tot, per))
        if cap is not None and (best is None or per > best[1]): best = (cap, per, w, ns, tot)
    print()
    print('C|BEST per trade|cap %.2f|net per trade %+.4f|net>0 %d|stopped %d|net sum %+.3f'
          % (best[0], best[1], best[2], best[3], best[4]))


if __name__ == '__main__':
    sys.exit(main())
