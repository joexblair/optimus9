"""live_seam_report - the 4-hour run's report, built from what live_seam recorded. 1026.

ONE JOB: read out/{meta.json, seed.npz, bars.jsonl, events.jsonl}, rebuild the same 21 lines once over
the run from the tape (the backtest path), and write out/report.md. It decides nothing the run did
not already record, except the four post-hoc columns, which need bars after the firing.

THE REPLAY. One BiasWindow ending at the last live bar, o9-live's span (LOOKBACK_H + WARMUP_H),
emerging lines, then `v4_closed_prev.series(.., ts=W.ts)`. Each live read B is compared with the
replay's value at the same bar. `warmup_check.py` measured this span window-invariant: r lines at
<= 8.5e-14, b and Mage at <= 8.7e-09, px exact.

    python3 live_seam.py report <run_dir>
"""
import json
import os
from collections import Counter, defaultdict

import numpy as np

import live_seam as LS

TOL = 2.0e-07          # ac06c2 #6, anchored to 1001_rebuild_timing.md's largest bb-role diff (ws2x)
WOB12 = 12             # Joe 1026, his named value - "spitballing only". Printed, gates nothing
PAIRING = ('An A firing pairs with the first B firing of the same event, lines and side that comes after '
           'it and before the next A firing of that same event, lines and side. Otherwise it is "A only"; '
           'a B firing no A firing claims is "B only". (Mine, accepted by ac06c2 #6.)')


def load(rd):
    """One run folder's record. -> (meta, seed, bars, events)."""
    META, SEED, BARS, EVENTS = LS.paths(rd)
    meta = json.load(open(META))
    seed = np.load(SEED)
    bars = [json.loads(l) for l in open(BARS)]
    evs = [json.loads(l) for l in open(EVENTS)]
    for e in evs:                       # the first run predates `kind`, and every row it wrote was a firing
        e.setdefault('kind', 'fire')
    return meta, seed, bars, evs


def series(seed, bars):
    """The A and B series over seed + live, on one grid. -> ts, A, B, live mask."""
    ts = np.r_[np.asarray(seed['ts'], np.int64), np.asarray([b['ts'] for b in bars], np.int64)]
    A = {n: np.r_[np.asarray(seed[n], float), np.asarray([np.nan if b.get('a', {}).get(n) is None
                                                          else b['a'][n] for b in bars], float)]
         for n in LS.NAMES}
    B = {n: LS.CP.series(A[n], LS.tf_of(n) * 60, ts=ts) for n in LS.NAMES}
    live = np.r_[np.zeros(len(seed['ts']), bool), np.ones(len(bars), bool)]
    return ts, A, B, live


def record(rd, cache=None):
    """One run, with #2 DERIVED from its bar record. -> (meta, seed, bars, events, ts, A, B).

    #1, #3 and #4 are the rows the run wrote. #2 is derived at every live bar by `live_seam.passes`,
    the function the run itself calls, over the recorded series, for t in `live_seam.PASS_TFS`. Joe
    widened #2 to every adjacent pair (1026, ac06c2 #34) after the runs had started, and a bar's pass
    rows depend only on bars at or before it, so the derivation is the run's own answer.
    `cache` {bar ts: rows} lets a follow pass derive only the bars it has not seen.
    """
    meta, seed, bars, evs = load(rd)
    ts, A, B, _live = series(seed, bars)
    cache = {} if cache is None else cache
    idx = {int(t): i for i, t in enumerate(ts)}
    der = []
    for b in bars:
        t = int(b['ts'])
        if t not in cache:
            j = idx[t]
            cache[t] = [LS.decorate(e, read, j, ts, A, B) for read, X in (('A', A), ('B', B))
                        for e in LS.passes(X, j, A)]
        der += cache[t]
    return meta, seed, bars, [e for e in evs if e['ev'] != 2] + der, ts, A, B


def _state(ev, side):
    """The state an event's firing enters. #1 enters ib; #3 and #4 enter oob on `side`."""
    if ev == 1:
        return lambda v: LS.K.ib(v) if np.isfinite(v) else False
    return lambda v: bool(np.isfinite(v) and LS.K.oob(v, side))


def post_hoc(ts, X, j, name, ev, side):
    """The three columns that need bars after the firing, on the series `X` it came from.

    -> (dwell bars, dwell still open at the last bar held, survives close True/False/None, wob 12
    True/False/None). None = not decided by the bars held. The DB writer and the report both call this.
    """
    st = _state(ev, side)
    v = X[name]
    k = j
    while k < len(v) and st(v[k]):
        k += 1
    n = k - j
    open_end = k == len(v)
    w12 = True if n >= WOB12 else (None if open_end else False)
    tf_ms = LS.tf_of(name) * 60_000
    t = int(ts[j])
    day = (t // 86_400_000) * 86_400_000
    close_ts = day + ((t - day) // tf_ms) * tf_ms + tf_ms - LS.BAR_MS
    i = int(np.searchsorted(ts, close_ts))
    bc = bool(st(v[i])) if i < len(ts) and int(ts[i]) == close_ts else None
    return n, open_end, bc, w12


def _post_hoc(ts, X, j, name, ev, side):
    """post_hoc as report cells."""
    n, open_end, bc, w12 = post_hoc(ts, X, j, name, ev, side)
    yn = {True: 'yes', False: 'no', None: 'run ended'}
    return ('>= %d (run ended)' % (n * 5)) if open_end else str(n * 5), yn[bc], yn[w12]


def pair(evs):
    """Pair A and B firings by PAIRING. -> [(A firing or None, B firing or None)], chronological."""
    by = defaultdict(lambda: {'A': [], 'B': []})
    for e in evs:
        if e['kind'] == 'fire':
            by[(e['ev'], tuple(e['lines']), e['side'])][e['read']].append(e)
    out = []
    for key, d in by.items():
        As = sorted(d['A'], key=lambda e: e['ts'])
        Bs = sorted(d['B'], key=lambda e: e['ts'])
        used = set()
        for i, a in enumerate(As):
            nxt = As[i + 1]['ts'] if i + 1 < len(As) else None
            hit = None
            for k, b in enumerate(Bs):
                if k in used or b['ts'] <= a['ts']:
                    continue
                if nxt is not None and b['ts'] >= nxt:
                    break
                hit = k
                break
            if hit is None:
                out.append((a, None))
            else:
                used.add(hit)
                out.append((a, Bs[hit]))
        for k, b in enumerate(Bs):
            if k not in used:
                out.append((None, b))
    out.sort(key=lambda p: (p[0] or p[1])['ts'])
    return out


def _v(x):
    return '-' if x is None else '%.2f' % x


def main(rd):
    meta, seed, bars, evs, ts, A, B = record(rd)
    idx = {int(t): i for i, t in enumerate(ts)}
    L = []
    w = L.append
    t0, t1 = bars[0]['ts'], bars[-1]['ts']
    w('# live_seam - read A against read B on the live tape, %s to %s' % (LS.utc(t0), LS.utc(t1)))
    w('')
    w('## The run')
    w('')
    late = np.array([b['late_ms'] for b in bars]); comp = np.array([b['done_ms'] - b['recv_ms'] for b in bars])
    w('| item | value |')
    w('|---|---|')
    w('| live bars | %d |' % len(bars))
    w('| first live bar | %s |' % LS.utc(t0))
    w('| last live bar | %s |' % LS.utc(t1))
    w('| seeded bars before it | %d, %s to %s |' % (meta['seed_bars'], meta['seed_from'], meta['seed_to']))
    w('| window | lookback %s h + warmup %s h, o9-live\'s |' % (meta['lookback_h'], meta['warmup_h']))
    w('| filler_invisible | %s |' % meta['filler_invisible'])
    w('| bars read after close, ms: min / median / max | %d / %d / %d |' % (late.min(), np.median(late), late.max()))
    w('| compute per bar, ms: min / median / max | %d / %d / %d |' % (comp.min(), np.median(comp), comp.max()))
    w('| bars with a compute error | %d |' % sum('error' in b for b in bars))
    w('| missing bars on the tape | %d |' % sum(b['gap_bars'] for b in bars))
    w('')
    w('- pairing rule: %s' % PAIRING)
    w('- #3 and #4: the firing bar is the RAW cross bar. Joe 1026: *"take a wob, or the raw cross bar - capture both"*.')
    w('- dwell s = consecutive 5 s bars the state holds from the firing bar, x 5, on the series the firing came from.')
    w('- survives to bucket close = the state at that TF\'s next bucket close, the bar at next seam - 5 s.')
    w('  On the B series this is "yes" by construction: B is constant inside a bucket.')
    w('- wob 12 = held >= 12 bars = 60 s. Joe\'s named value, *"spitballing only"*. It gates nothing.')
    w('- #1 carries the same three columns; its state is ib. #2 carries none: a pass reads two lines and two')
    w('  conditions, so which state a dwell would measure is not defined. #2 stays on the raw pass bar.')
    w('')

    # ── the replay ──
    db = LS.DatabaseManager(**LS.get_db_config()); db.connect()
    ovr = LS.line_overrides(db, LS._Names())
    W = LS.window(db, ovr, t1)
    rts = np.asarray(W.ts, np.int64)
    rpos = {int(t): i for i, t in enumerate(rts)}
    w('## Read B, live against the replay')
    w('')
    w('The replay is one window ending %s, emerging lines, `v4_closed_prev.series`. Tolerance %.1e is'
      ' ac06c2\'s (#6). The max |diff| is reported pass or fail.' % (LS.utc(t1), TOL))
    w('')
    w('| line | bars compared | exactly equal | max abs diff | above %.1e | NaN mismatch | verdict |' % TOL)
    w('|---|---|---|---|---|---|---|')
    fails = []
    for n in LS.NAMES:
        Br = LS.CP.series(np.asarray(W._line_emerging(n), float), LS.tf_of(n) * 60, ts=rts)
        lv, rv, bt = [], [], []
        for b in bars:
            i = rpos.get(int(b['ts']))
            if i is None:
                continue
            lv.append(np.nan if b['b'][n] is None else b['b'][n]); rv.append(Br[i]); bt.append(b['ts'])
        lv, rv = np.asarray(lv), np.asarray(rv)
        both = np.isfinite(lv) & np.isfinite(rv)
        d = np.abs(lv - rv)
        nanm = int((np.isnan(lv) != np.isnan(rv)).sum())
        mx = float(d[both].max()) if both.any() else float('nan')
        above = int((d[both] > TOL).sum())
        for k in np.flatnonzero(both & (d > TOL)):
            fails.append((bt[k], n, lv[k], rv[k], d[k]))
        w('| %s | %d | %d | %.1e | %d | %d | %s |' % (n, len(lv), int((lv[both] == rv[both]).sum()), mx, above,
                                                      nanm, 'PASS' if above == 0 and nanm == 0 else 'FAIL'))
    w('')
    if fails:
        w('### every read B above tolerance, chronological')
        w('')
        w('| bar | line | live read B | replay | abs diff |')
        w('|---|---|---|---|---|')
        for t, n, a, r, d in sorted(fails):
            w('| %s | %s | %.10f | %.10f | %.1e |' % (LS.utc(t), n, a, r, d))
        w('')
    # bars the tape rewrote after the live read
    rw = []
    base = W.base
    for b in bars:
        i = rpos.get(int(b['ts']))
        if i is None or 'ohlcv' not in b:
            continue
        r = base.iloc[i]
        now = [float(r['open']), float(r['high']), float(r['low']), float(r['close']), float(r['volume'])]
        if now != b['ohlcv']:
            rw.append((b['ts'], b['ohlcv'], now))
    w('### bars whose OHLCV changed on the tape after the live read: %d' % len(rw))
    w('')
    if rw:
        w('| bar | live OHLCV | tape now |')
        w('|---|---|---|')
        for t, a, r in rw:
            w('| %s | %s | %s |' % (LS.utc(t), ' / '.join('%g' % x for x in a), ' / '.join('%g' % x for x in r)))
        w('')

    # ── the firings ──
    pairs = pair(evs)
    w('## The firings, one row per pair, chronological')
    w('')
    cnt = Counter()
    for a, b in pairs:
        e = a or b
        cnt[(e['ev'], 'both' if a and b else ('A only' if a else 'B only'))] += 1
    w('| event | pairs | both | A only | B only |')
    w('|---|---|---|---|---|')
    for ev in (1, 2, 3, 4):
        tot = sum(v for (e, _k), v in cnt.items() if e == ev)
        w('| %s | %d | %d | %d | %d |' % (LS.EV_NAME[ev], tot, cnt[(ev, 'both')], cnt[(ev, 'A only')], cnt[(ev, 'B only')]))
    w('')
    w('| event | lines | side | fired under | A bar | B bar | gap s | read A at A bar | read B at A bar |'
      ' A dwell s | A survives close | A wob 12 | B dwell s | B survives close | B wob 12 |')
    w('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for a, b in pairs:
        e = a or b
        kind = 'both' if a and b else ('A only' if a else 'B only')
        nm = e['lines'][0]
        cols = []
        for f, X in ((a, A), (b, B)):
            if f is None or e['ev'] == 2:
                cols += ['-', '-', '-']
            else:
                cols += list(_post_hoc(ts, X, idx[int(f['ts'])], nm, f['ev'], f['side']))
        av = '; '.join('%s %s' % (n, _v(e['a'][n])) for n in e['lines']) if a is None else \
            '; '.join('%s %s' % (n, _v(a['a'][n])) for n in a['lines'])
        bv = '; '.join('%s %s' % (n, _v(e['b'][n])) for n in e['lines']) if a is None else \
            '; '.join('%s %s' % (n, _v(a['b'][n])) for n in a['lines'])
        w('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            LS.EV_NAME[e['ev']] + (' (%s)' % e['why'] if e.get('why') else ''), ' -> '.join(e['lines']),
            LS.SIDE[e['side']], kind, a['utc'] if a else '-', b['utc'] if b else '-',
            ((b['ts'] - a['ts']) // 1000) if a and b else '-', av if a else '-', bv if a else '-',
            ' | '.join(cols)))
    w('')

    # ── #1 with the r ladder, Joe 1026: "at the ws1b oob to ib event, capture the r values of the ws1-12 lines"
    import live_seam_db as D
    brec = {b['ts']: b for b in bars}
    one = sorted([e for e in evs if e['ev'] == 1], key=lambda e: (e['ts'], e['read']))
    w('## Every #1 firing with the r ladder, chronological')
    w('')
    w('ws1r..ws12r at the firing bar, on the read that fired. H = at or above the high fence (80), L = at or below'
      ' the low fence (20), - = neither. Both sides are shown: this harness has no trade side.')
    w('')
    w('| bar | read | side left | ' + ' | '.join('ws%dr' % t for t in LS.R_TFS) + ' |')
    w('|---|---|---|' + '---|' * len(LS.R_TFS))
    for e in one:
        cells = [c.split(' ', 1)[1] for c in D.ladder_1(brec[e['ts']], e['read']).split('; ')]
        w('| %s | %s | %s | %s |' % (e['utc'], e['read'], LS.SIDE[e['side']], ' | '.join(cells)))
    w('')

    # ── every pass bar ──
    pr = sorted([e for e in evs if e['ev'] == 2], key=lambda e: (e['ts'], e['read']))
    w('## Every pass bar of ws1r..ws%dr, both reads, chronological' % LS.PASS_TFS[-1])
    w('')
    w('Rung scan: every rung above the handing line, as `line value ex-fence/towards` (y/n). The full scan is in'
      ' out/events.jsonl. Reversals are on the EMERGING series in both reads, raw bar and stamp kept apart.')
    w('')
    w('| bar | read | handing line | side | why | receiver | rung scan | handing rev raw | handing rev stamp |'
      ' receiver rev raw | receiver rev stamp |')
    w('|---|---|---|---|---|---|---|---|---|---|---|')
    for e in pr:
        sc = '; '.join('%s %s %s/%s' % (r['line'], _v(r['value']), 'y' if r['ex_fence'] else 'n',
                                         'y' if r['towards'] else 'n') for r in e.get('rungs', []))
        h, r = e.get('rev_hand'), e.get('rev_recv')
        w('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            e['utc'], e['read'], e['lines'][0], LS.SIDE[e['side']], e['why'],
            e['lines'][1] if e['kind'] == 'fire' else 'none', sc,
            h['raw_utc'] if h else '-', h['stamp_utc'] if h else '-',
            r['raw_utc'] if r else '-', r['stamp_utc'] if r else '-'))
    w('')
    path = os.path.join(rd, 'report.md')
    open(path, 'w').write('\n'.join(L) + '\n')
    print(path)


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
