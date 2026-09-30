"""race_latch - the latch releases on a race between the next v3 row and the next ws1mage-rev.

Joe 0930: *"the latch will realease on a race condition between the next v3 row and the next
ws1mage-rev"* / *"I'm just moving the lookback ws1mage-rev detection forward, so the same conditions
apply"*.

A RACE HAS NO WINDOW. First of the two events wins. There is no length, no cap and no horizon in
this - an earlier version of this file bounded the race at 180 s, which Joe never asked for and which
imported confirm_lag_s from a mech that had not fired.

1  THE LATCH.  coil_moment.moments() holds `cur` until a v3 row breaks the run. It now opens on
   whichever comes FIRST: the next v3 row that breaks the run, or the next ws1mage-rev `sig_conf`
   strictly after the newest row in `cur`. `brk` is whichever won.

2  THE LOOKBACK WINDOW.  coil_exit.resolve step 1 is

       _knowable(legs, named - lookback_bars, named, named)
   ->  _knowable(legs, named - lookback_bars, base,  base)     # base = the bar the latch opened

   Same legs, same dr keying, same `sig` in the window, same `sig_conf <= by` causality test. The
   forward edge is the latch's own release bar, so it carries no number of its own.

   When the latch was opened BY a sig_conf, that sig_conf is inside the window by construction - so
   the row flows as a LOOKBACK hit, which is what Joe asked for: "immediately flow like the walk had
   qualified lookback".

CAUSAL. `sig_conf` is the bar the cross's 4-bar hold completes - the first bar the event is standing
evidence. Nothing here reads `rev` or `sig` raw, and nothing reads a bar above the bar being tested.

NOTHING IS BANKED AND NO KNOB MOVES.

    python3 race_latch.py
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
LOOKBACK, GAP, FORWARD, CONFIRMED = 'lookback', 'gap', 'forward', 'confirmed'


def knowable(legs, lo, hi, by):
    """coil_exit._knowable, verbatim."""
    return [(int(a), int(b)) for a, b in zip(legs['sig'], legs['sig_conf'])
            if lo <= a <= hi and int(b) <= by]


def moments_raced(rows, SC):
    """coil_moment.moments with the latch racing a ws1mage-rev `sig_conf`. No window.

    SC[d] is the sorted array of sig_conf bars for dr d.
    -> the same dicts, plus `by` = 'row' or 'rev' for which won the race.
    """
    out, cur = [], []
    n = len(rows)
    for j, a in enumerate(rows):
        if a['ok']:
            if cur and a['dr'] != cur[-1]['dr']:
                out.append((cur, rows[j]['i'], 'row')); cur = []
            cur.append(a)
        else:
            if cur:
                out.append((cur, rows[j]['i'], 'row')); cur = []
                continue
        if not cur:
            continue
        # the race: a sig_conf strictly after the newest row, inside 180 s, before the next row
        i = int(cur[-1]['i']); d = int(cur[-1]['dr'])
        sc = SC.get(d)
        if sc is None or not sc.size:
            continue
        k = int(np.searchsorted(sc, i + 1, 'left'))
        if k >= sc.size:
            continue
        c = int(sc[k])
        nxt = int(rows[j + 1]['i']) if (j + 1) < n else None
        if nxt is not None and nxt <= c:
            continue                                  # the row wins the race
        out.append((cur, c, 'rev')); cur = []
    if cur:
        out.append((cur, None, 'end'))
    return [dict(i0=m[0]['i'], i1=m[-1]['i'], dr=m[0]['dr'], rows=len(m), brk=b, by=w)
            for m, b, w in out]


def resolve_fwd(moment, pick, confirmed, legs, lag_bars, lookback_bars, gap_fill, fwd):
    """coil_exit.resolve with the LOOKBACK window's forward edge at the latch's release bar.

    fwd=True moves the edge to `base`; fwd=False is the banked rule, edge at `named`.
    """
    if confirmed:
        named = pick; base = pick + lag_bars
        return dict(coil_exit._blank(), named=named, base=base, actionable_confirmed=base,
                    rev=coil_exit.first_forward(legs, base), via=CONFIRMED)
    named = moment['i1']
    base = moment['brk'] if moment['brk'] is not None else moment['i1']
    edge = base if fwd else named
    hit = knowable(legs, named - lookback_bars, edge, edge)
    if hit:
        return dict(coil_exit._blank(), named=named, base=base, actionable_lookback=named,
                    rev=named, via=LOOKBACK)
    if gap_fill:
        inside = knowable(legs, named + 1, base, base)
        if inside:
            first = inside[0][1]
            return dict(coil_exit._blank(), named=named, base=base, actionable_gap=first,
                        rev=first, via=GAP)
    return dict(coil_exit._blank(), named=named, base=base, actionable_forward=base,
                rev=coil_exit.first_forward(legs, base), via=FORWARD)


def report(rig, lab, ms, LEGS, lag, look, gf, fwd, base=None):
    px = rig.px; A, B = rig.A, rig.B
    res = []; via = {}; won = {}
    for m in ms:
        d = m['dr']; cc = (lambda i, _d=d: float(rig.CC[i] * _d))
        p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
        ex = resolve_fwd(m, p, conf, LEGS[d], lag, look, bool(gf), fwd)
        if ex['rev'] is None: continue
        sig = int(ex['rev'])
        if not (A <= sig <= B): continue
        brk = int(m['brk']) if m['brk'] is not None else int(m['i1'])
        # the emit bar: everything the answer depends on must have passed
        act = int(coil_exit.fired(ex)[1])
        emit = max(brk, sig, act) if ex['via'] != CONFIRMED else max(sig, act)
        res.append((sig, emit, ex['via']))
        via[ex['via']] = via.get(ex['via'], 0) + 1
        won[m.get('by', 'row')] = won.get(m.get('by', 'row'), 0) + 1
    lags = np.array([(e - s) * 5 for s, e, _v in res]) if res else np.array([0])
    sigs = sorted({s for s, _e, _v in res})
    print('S|%s' % lab)
    print('S|  moments %d|resolved %d|sig bars %d' % (len(ms), len(res), len(sigs)))
    print('S|  via: %s' % '  '.join('%s %d' % kv for kv in sorted(via.items())))
    print('S|  latch opened by: %s' % '  '.join('%s %d' % kv for kv in sorted(won.items())))
    print('S|  emit lag s: at 0 %d (%.1f%%)|median %d|p75 %d|p90 %d|max %d'
          % (int((lags == 0).sum()), 100.0*(lags == 0).sum()/lags.size, np.median(lags),
             np.percentile(lags, 75), np.percentile(lags, 90), lags.max()))
    opens = sorted(k for k in sigs if rig.gate_open(k))
    if opens:
        T, _ = walk(opens, rig.DRW, px, min(opens), B, CAP)
        if T:
            n, w, ns, tot = score(px, T, CAP)
            print('S|  rule#1 open %d|trades %d|net>0 %d (%.1f%%)|stopped %d (%.1f%%)|'
                  'net sum %+.3f|per trade %+.4f'
                  % (len(opens), n, w, 100.0*w/n, ns, 100.0*ns/n, tot, tot/n))
    if base is not None and sigs:
        BA = np.array(base); SA = np.array(sigs)
        j = np.clip(np.searchsorted(BA, SA), 1, len(BA)-1)
        dd = np.minimum(np.abs(SA - BA[j]), np.abs(SA - BA[j-1]))
        print('S|  vs banked: exact-bar match %d of %d|within 1 min %d|median distance %d s'
              % (len(set(sigs) & set(base)), len(sigs), int((dd <= 12).sum()), int(np.median(dd)*5)))
    print()
    sys.stdout.flush()
    return sigs


def main():
    rig = S.Rig((FROM_MS, TO_MS)); cfg = dict(S.BASE)
    segs = rig.segs_for(rig.A, rig.B)
    tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
    FL, FH = cfg['fence_lo'], cfg['fence_hi']
    lag = cfg['confirm_lag_s'] // 5; look = cfg['lookback_s'] // 5
    rws = []
    for tf in tfs:
        sw = rig.sideways(tf, cfg); r = rig.R[tf]
        q = sw & np.isfinite(r) & ((r < FL) | (r > FH))
        for (a_, b_, d) in segs:
            if not d: continue
            seg = q[a_:b_ + 1]
            if seg.any(): rws.append((a_ + int(np.argmax(seg)), tf, d))
    rws.sort(key=lambda x: (x[0], x[1]))
    SUP = np.zeros(rig.n, np.int16); SUPM = np.zeros(rig.n, np.int16)
    for tf in tfs:
        SUP += (rig.D[tf] > 0).astype(np.int16); SUPM += (rig.D[tf] < 0).astype(np.int16)
    ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d > 0 else SUPM[i]) >= cfg['support_min']))
           for (i, tf, d) in rws]
    LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                       rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                       dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
    SC = {d: np.sort(np.asarray(LEGS[d]['sig_conf'], dtype=np.int64)) for d in LEGS}
    print('B|window 2026-06-10 .. 2026-09-08 = 90 days|v3 rows %d|lookback_s %d|'
          'no cap on the race' % (len(ann), cfg['lookback_s']))
    print()
    banked = report(rig, 'BANKED - latch on rows only, lookback ends at `named`',
                    coil_moments(ann), LEGS, lag, look, cfg['gap_fill'], False)
    report(rig, 'RACED - latch opens on the FIRST of (next row, next sig_conf). No window.',
           moments_raced(ann, SC), LEGS, lag, look, cfg['gap_fill'], True, banked)
    return 0


if __name__ == '__main__':
    sys.exit(main())
