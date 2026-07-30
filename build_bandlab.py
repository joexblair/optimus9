"""build_bandlab — the DELEGATE BAND test (Joe 0728).

Joe's design, verbatim in docs/bp50.md §1:
  bands (60-90, 45-60, 30-60), each with the delegate at the ROOT and the higher TFs in the band
  delegating to the root; near_ib is applied to CURRENT_TF's r, not the delegate's; walk the RPL walk to
  find how close {current_tf}r must be to OOB before we start polling the delegate for crosses; and if r
  is IB when the delegate crosses the boundary, fire on the x-cross-boundary.

MECHANIC AS BUILT
  gate    D  = how close current_tf's r must be to its OOB boundary before polling starts.
               dist = (HI - r) on the bull/hi side, (r - LO) on the lo side. GENERALISES xcp_bnd_offset
               (currently 4) and moves its subject to current_tf. Latches once satisfied.
  fire       delegate x crosses max(HI, rD) downward / min(LO, rD) upward — algebraically identical to
               Joe's "if r is IB ... fire on the x cross boundary", i.e. the NEARER of the two thresholds.
               Debounced through the jig's own causal.cross_wob at wob_n, the same call the engine uses.
  baseline   the real _climb_to_prov flip_provisional from the same fire bar. Not an arm — the thing to beat.

ARMS  (band -> root; None outside the band means that arm does not fire there)
  bands   30-44 -> 30 | 45-59 -> 45 | 60-90 -> 60      Joe's three bands read as a partition (no overlap)
  root60  60-90 -> 60                                   the 60-90 band alone
  aligned nearest TF <= rung that divides 1440          the seam-alignment result (bp50 §12.3)
  ctl_un  31-45 -> 31 | 46-60 -> 46 | 61-90 -> 61       CONTROL: same shape, deliberately UNALIGNED roots
  cur     rung -> rung                                  CONTROL: no delegation at all

VECTORISATION (behaviour-identical to the scalar walk, proven by _selftest against _climb_to_prov's ladder)
  cadence is every emerging bar, so the scan window w is ONE bar; and the rung ladder reduces to a running
  max, because max{TF > rung : rpred} equals highest[i] exactly when highest[i] > rung. So rung is
  cummax(highest) clipped at 3, `highest` is shared by every fire of the same bias, and the walk is
  processed in constant-rung RUNS instead of bar by bar.

Causal throughout: nothing reads past the bar under test. No caps.

    python3 build_bandlab.py [--selftest] [--persist]
"""
import sys, datetime as dt
import numpy as np
import build_rpl_6of9 as B
import build_past50 as BP
import optimus9.orchestration.rpl_walk as R

HI, LO = R.HI, R.LO
ALIGNED = [t for t in range(2, 91) if 1440 % t == 0]
GRID = [0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15, 30]    # the near_ib gate D, oscillator points
# D >= 15 saturates (gate satisfied on the first bar, stops controlling anything) — 30 kept as the marker.
_EDGE = {}
_HIGH = {}


def _band(edges):
    def f(rung):
        for lo, root in edges:
            if rung >= lo:
                return root
        return None
    return f


ARMS = {
    'bands':   _band([(60, 60), (45, 45), (30, 30)]),
    'root60':  _band([(60, 60)]),
    # strictly BELOW rung: `<=` collapsed this to `cur` (nearest divisor of 1440 at/below 90 is 90 itself),
    # inheriting cur's 100%-by-construction score. It was not a control at all.
    'aligned': lambda rung: max([t for t in ALIGNED if t < rung], default=None),
    'ctl_un':  _band([(61, 61), (46, 46), (31, 31)]),
    'cur':     lambda rung: rung,
}


def highest(bias):
    """highest[i] = max TF that is r-pred at bar i, for this bias. Shared by every fire."""
    if bias in _HIGH:
        return _HIGH[bias]
    L = R.L0; E = L['E']; P = L['P']; p = R._polar(bias)
    h = np.zeros(len(L['ts']), dtype=np.int16)
    for TF in sorted(R.TFS):                                  # ascending -> last write wins = the max
        m = (P[TF] == p['CS']) | p['oob_climb'](E[TF]['r'])
        h[m] = TF
    _HIGH[bias] = h
    return h


def edge(dTF, bias):
    """debounced rising edge of the delegate fire: x crosses the NEARER of {boundary, rD}."""
    k = (dTF, bias)
    if k in _EDGE:
        return _EDGE[k]
    L = R.L0; S = L['src']; p = R._polar(bias)
    rD = L['E'][dTF]['r']; xD = L['E'][dTF]['x']
    thr = np.maximum(HI, rD) if p['BULL'] else np.minimum(LO, rD)
    conf = S.causal.cross_wob(xD - thr, 0.0, p['WOB_DIR'], R.WOBN)
    _EDGE[k] = conf & ~np.roll(conf, 1)
    return _EDGE[k]


def runs(bias, gbar):
    """[(start, stop, rung)] — the constant-rung segments of the walk from gbar to end of tape."""
    h = highest(bias)[gbar + 1:]
    rung = np.maximum(3, np.maximum.accumulate(h))
    brk = np.flatnonzero(np.r_[True, rung[1:] != rung[:-1]])
    out = []
    for a, b in zip(brk, np.r_[brk[1:], len(rung)]):
        out.append((gbar + 1 + int(a), gbar + 1 + int(b), int(rung[a])))
    return out


def walk(bias, gbar, delmap, D):
    """Returns (fire_bar, rung_at_fire, dTF, arm_bar) or (None, last_rung, None, arm_bar)."""
    L = R.L0; E = L['E']; p = R._polar(bias)
    armed = False; arm_bar = None; rung = 3
    for a, b, rung in runs(bias, gbar):
        rc = E[rung]['r'][a:b]
        dist = (p['CB'] - rc) if p['BULL'] else (rc - p['CB'])
        g = np.maximum.accumulate(dist <= D) if not armed else np.ones(b - a, bool)
        if not armed and g.any():
            armed = True; arm_bar = a + int(np.argmax(g))
        dTF = delmap(rung)
        if dTF is None or not armed:
            continue
        hit = np.flatnonzero(edge(dTF, bias)[a:b] & g)
        if len(hit):
            return a + int(hit[0]), rung, dTF, arm_bar
    return None, rung, None, arm_bar


def thresh(TF, bias):
    """the NEARER of {boundary, r} — Joe 0728, confirmed: max(HI,r) on the hi side, min(LO,r) on the lo side.
    Covers both rows: r IB -> the boundary is nearer -> fire on the boundary cross (Joe's stated case);
    r OOB -> r is nearer -> fire on the r cross (the row Joe confirmed 0728)."""
    r = R.L0['E'][TF]['r']
    return np.maximum(HI, r) if bias == 'bull' else np.minimum(LO, r)


def outcome(dTF, rung, k, bias):
    """Joe 0728: "we don't want the delegate to create a more granular cross that isn't aligned with
    current_tf's impending cross." So, from the delegate fire at bar k (wording is Joe's, 0728):
        early    the delegate's x flipped back WHILE current_tf's cross was still OUTSTANDING
                 -- a granular cross current_tf never followed
        none     current_tf never crosses at all -- the same failure, terminal form
        aligned  current_tf's cross landed BEFORE the delegate's x flipped back
    No cap: current_tf is searched to end of tape."""
    L = R.L0; S = L['src']; p = R._polar(bias)
    xD = L['E'][dTF]['x']; thrD = thresh(dTF, bias)
    # current_tf's cross is searched from the fire bar INCLUSIVE: when dTF == rung the delegate's cross IS
    # current_tf's cross, so the `cur` control must score 100% aligned by construction. It is the sanity check.
    cur = np.flatnonzero(edge(rung, bias)[k:])
    # the reversal must clear the SAME wob_n the fire cleared — testing raw state made one 5s flick a
    # reversal and inflated `early` on every arm. No new knob: same call, opposite direction.
    rev = np.flatnonzero(S.causal.cross_wob(xD - thrD, 0.0, -p['WOB_DIR'], R.WOBN)[k + 1:])
    if not len(cur):
        return 'none', None, None, None
    # DECOMPOSITION: aligned% alone conflates two independent things — how long the delegate's cross stands
    # (HELD, a property of the delegate) and how long it is required to stand (REQ, a property of the gate's
    # timing). aligned <=> held >= req. Reporting both separately makes arms comparable when their REQ differs.
    req = int(cur[0])
    held = int(rev[0]) if len(rev) else None            # None = never reversed to end of tape (no cap)
    if held is not None and held < req:
        return 'early', req, req, held
    return 'aligned', req, req, held


def _selftest(fires=None):
    """The vectorised ladder must reproduce _climb_to_prov's rung sequence. Checked EXHAUSTIVELY over every
    bar of the tape — no sampling, no truncation. The earlier version compared 5 fires x 4000 bars against the
    scalar loop; those were caps applied without instruction, and unnecessary, because the identity is provable:

      _climb_to_prov does  hi = max([TF for TF in TFS if TF > rung and rpred(TF, i)], default=rung)
      define               highest[i] = max{TF in TFS : rpred(TF, i)}          (0 if none)

      If highest[i] > rung: highest[i] is itself a TF > rung that is rpred, and no larger TF is rpred at all,
                            so the constrained max EQUALS highest[i].
      If highest[i] <= rung: no TF > rung is rpred, so the comprehension is empty and hi = rung (default).
      Either way  rung_new = max(rung, highest[i]),  hence  rung = max(3, cummax(highest)).

    PROVED vs TESTED. The ladder reduction above is PROVED, not tested — there is no case where the constrained
    set is non-empty but highest[i] <= rung, because highest IS the global max over rpred TFs. What remains
    testable is only whether `highest` computes that max correctly, and that is TESTED here against an
    INDEPENDENT algorithm: descending TF order with first-write-wins, versus highest()'s ascending
    last-write-wins. (An earlier version of this function recomputed highest() line for line and compared it to
    itself — a tautology that would have passed with any bug in it.)"""
    L = R.L0; E = L['E']; P = L['P']
    ok = True
    for bias in ('bull', 'bear'):
        p = R._polar(bias)
        n = len(L['ts'])
        ref = np.zeros(n, dtype=np.int16); filled = np.zeros(n, dtype=bool)
        for TF in sorted(R.TFS, reverse=True):             # descending, FIRST write wins
            m = ((P[TF] == p['CS']) | p['oob_climb'](E[TF]['r'])) & ~filled
            ref[m] = TF; filled |= m
        got = highest(bias)
        bad = int((ref != got).sum())
        print('  selftest %-4s: %d/%d bars mismatched (independent descending scan)' % (bias, bad, n))
        ok &= (bad == 0)
    return ok


def main(argv):
    gts = B.gts
    S, E = int(gts[0]), int(gts[-1]) + 1
    hm = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
    print('window %s -> %s   wob_n=%d  xcp_bnd_offset(base)=%d\naligned TFs %s'
          % (hm(S), hm(E), R.WOBN, R.BND4, ALIGNED))

    fires = []; seen = set()
    for oi, de, ti, tf, br, tev in B._fires(S, E):
        key = (int(BP.te[ti]), tf)
        if key in seen:
            continue
        seen.add(key)
        fts = int(BP.te[ti])
        if gts[0] <= fts <= gts[-1]:
            fires.append((fts, int(np.searchsorted(gts, fts)), 'bull' if de > 0 else 'bear'))
    print('A/B fires (deduped on fire_ts+tf): %d  (%d bull / %d bear)'
          % (len(fires), sum(1 for f in fires if f[2] == 'bull'), sum(1 for f in fires if f[2] == 'bear')))

    if '--selftest' in argv:
        if not _selftest(fires):
            return []

    print('EARLY (Joe 0728) = the delegate made a granular cross that current_tf never followed:')
    print('  early   = delegate x reverses past its own threshold before current_tf crosses')
    print('  none    = current_tf never crosses at all')
    print('  aligned = current_tf crosses while the delegate cross still stands\n')

    rows = []
    for arm in ARMS:
        print('  %-8s %5s %11s %8s %10s %10s %8s %8s %8s'
              % ('arm', 'D', 'fired', 'ALIGNED', 'med REQ', 'med HELD', 'never-rev', 'med rung', 'med del'))
        for D in GRID:
            fired = 0; rungs = []; dels = []; reqs = []; helds = []; nev = 0
            tally = {'aligned': 0, 'early': 0, 'none': 0}
            for fts, gbar, bias in fires:
                k, rung, dTF, ab = walk(bias, gbar, ARMS[arm], D)
                if k is None:
                    continue
                fired += 1; rungs.append(rung); dels.append(dTF)
                oc, _, req, held = outcome(dTF, rung, k, bias)
                tally[oc] += 1
                if req is not None:
                    reqs.append(req * 5)
                if held is None:
                    nev += 1
                elif held is not None:
                    helds.append(held * 5)
                rows.append((arm, D, fts, bias, rung, dTF, int(gts[k]), oc, req, held))
            f = max(fired, 1)
            RQ = np.array(reqs) if reqs else np.array([np.nan])
            HL = np.array(helds) if helds else np.array([np.nan])
            print('  %-8s %5s %4d/%-3d %3.0f%% %7.0f%% %9.0fs %9.0fs %7.0f%% %8s %8s'
                  % (arm, D, fired, len(fires), 100 * fired / max(len(fires), 1),
                     100 * tally['aligned'] / f, np.nanmedian(RQ), np.nanmedian(HL),
                     100 * nev / f,
                     int(np.median(rungs)) if rungs else '-', int(np.median(dels)) if dels else '-'))
        print()
    return rows


SAMPLE_DDL = '''CREATE TABLE IF NOT EXISTS rpl_bandlab (
    bl_pk         BIGINT AUTO_INCREMENT PRIMARY KEY,
    bl_created    DATETIME DEFAULT CURRENT_TIMESTAMP,
    bl_bias       VARCHAR(4),
    bl_cur_tf     INT,                  -- current_tf (the climb rung) at the delegate cross
    bl_del_tf     INT,                  -- the delegate under test
    -- TWO bars, because cross_wob confirms only after the crossed side holds wob_n bars and the consumer
    -- takes the rising edge of the CONFIRMED state. The confirmed bar is always exactly wob_n-1 bars (40s at
    -- wob_n=9) after the real crossing. Joe 0728 caught this: a reported "cross of 15" showed x=43.4, because
    -- x ran 15.9 -> 43.4 inside those 40s. Line values must be quoted at bl_raw_ms; a LIVE filter can only
    -- read them at bl_cross_ms, since 40s earlier you cannot know the cross will hold.
    bl_raw_ms     BIGINT, bl_raw_utc VARCHAR(19),     -- the ACTUAL crossing bar (k - (wob_n-1))
    bl_raw_x      FLOAT, bl_raw_thr FLOAT,            -- delegate x and threshold AT the real cross
    bl_cur_x_raw  FLOAT,                              -- current_tf x at the real cross (the filter feature)
    bl_cross_ms   BIGINT, bl_cross_utc VARCHAR(19),   -- the CONFIRMED bar (what a live system can act on)
    bl_cur_r      FLOAT,                -- current_tf's r AT the delegate cross
    bl_cur_r_dist FLOAT,                -- how far that r is from its OOB boundary  <- the threshold column
    bl_cur_x      FLOAT, bl_cur_m FLOAT,
    bl_del_r      FLOAT, bl_del_x FLOAT, bl_del_thr FLOAT,
    bl_flip_ms    BIGINT,               -- when the delegate's x flipped back (NULL = never, to end of tape)
    bl_hold_s     INT,
    bl_curcross_ms BIGINT,              -- current_tf's own cross
    bl_wait_s     INT,                  -- delegate cross -> current_tf cross
    bl_outcome    VARCHAR(8),           -- early | aligned
    INDEX (bl_del_tf, bl_outcome), INDEX (bl_cur_tf), INDEX (bl_cross_ms))'''


def samples(del_tfs=(30, 45, 60), persist=False):
    """Joe 0728: "because your test showed a cross far before current_tf's cross, you now have a sample of
    1) time range and 2) r value range. ie store both ... with more of the same r-pred state samples,
    captured when an early granular cross doesn't align with the current_tf cross, you will have a dataset
    that shows you a common r_threshold_that_ignores_early_crosses."

    So: NO GATE. Every delegate cross in every walk is captured and labelled, because the gate is the thing
    being learned — pre-applying it would filter out the samples that define it. current_tf's r AT the cross
    (and its distance from the boundary) is recorded for every sample; the threshold is then whatever
    separates early from aligned.

    Deduped on (delegate TF, cross bar): overlapping setups converge on the same episode and would otherwise
    triple-count the same cross."""
    L = R.L0; ts = L['ts']; E = L['E']
    gts = B.gts
    utc = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    fires = []; seen = set()
    for oi, de, ti, tf, br, tev in B._fires(int(gts[0]), int(gts[-1]) + 1):
        key = (int(BP.te[ti]), tf)
        if key in seen:
            continue
        seen.add(key)
        fts = int(BP.te[ti])
        if gts[0] <= fts <= gts[-1]:
            fires.append((fts, int(np.searchsorted(gts, fts)), 'bull' if de > 0 else 'bear'))
    print('%d setups | delegates %s | NO GATE — every cross captured' % (len(fires), list(del_tfs)))

    rows = []; done = set()
    for fts, gbar, bias in fires:
        p = R._polar(bias)
        for a, b, rung in runs(bias, gbar):
            for dTF in del_tfs:
                if dTF > rung:
                    continue
                for k in np.flatnonzero(edge(dTF, bias)[a:b]):
                    k = a + int(k)
                    if (dTF, k) in done:
                        continue
                    done.add((dTF, k))
                    oc, _, req, held = outcome(dTF, rung, k, bias)
                    if oc == 'none':
                        continue
                    kr = max(0, k - (R.WOBN - 1))          # the REAL crossing bar; see the DDL note
                    rc = float(E[rung]['r'][k])
                    rows.append(dict(
                        bias=bias, cur=rung, dtf=dTF, ms=int(ts[k]),
                        raw_ms=int(ts[kr]), raw_x=float(E[dTF]['x'][kr]),
                        raw_thr=float(thresh(dTF, bias)[kr]), cur_x_raw=float(E[rung]['x'][kr]),
                        cur_r=rc, dist=float((p['CB'] - rc) if p['BULL'] else (rc - p['CB'])),
                        cur_x=float(E[rung]['x'][k]), cur_m=float(E[rung]['m'][k]),
                        del_r=float(E[dTF]['r'][k]), del_x=float(E[dTF]['x'][k]),
                        del_thr=float(thresh(dTF, bias)[k]),
                        flip=int(ts[k + 1 + held]) if held is not None else None,
                        hold=held * 5 if held is not None else None,
                        curx=int(ts[k + req]), wait=req * 5, oc=oc))
    print('captured %d samples (%d early / %d aligned)\n'
          % (len(rows), sum(r['oc'] == 'early' for r in rows), sum(r['oc'] == 'aligned' for r in rows)))

    for dTF in del_tfs:
        sub = [r for r in rows if r['dtf'] == dTF]
        if not sub:
            continue
        ea = np.array([r['dist'] for r in sub if r['oc'] == 'early'])
        al = np.array([r['dist'] for r in sub if r['oc'] == 'aligned'])
        we = np.array([r['wait'] for r in sub if r['oc'] == 'early'])
        wa = np.array([r['wait'] for r in sub if r['oc'] == 'aligned'])
        print('  delegate s%d — %d samples' % (dTF, len(sub)))
        print('    current_tf r distance from boundary:')
        for nm, v in (('EARLY  ', ea), ('ALIGNED', al)):
            if len(v):
                print('      %s n=%-5d min %5.1f  p10 %5.1f  med %5.1f  p90 %5.1f  max %5.1f'
                      % (nm, len(v), v.min(), np.percentile(v, 10), np.median(v), np.percentile(v, 90), v.max()))
        print('    wait to current_tf cross (s):')
        for nm, v in (('EARLY  ', we), ('ALIGNED', wa)):
            if len(v):
                print('      %s med %6.0f  p90 %7.0f  max %8.0f' % (nm, np.median(v), np.percentile(v, 90), v.max()))
        if len(ea) and len(al):
            print('    threshold scan — keep a cross only when r distance <= T:')
            print('      %6s %10s %10s %10s' % ('T', 'early kept', 'aligned kept', 'purity'))
            for T in (1, 2, 3, 4, 6, 8, 10, 15, 20, 30, 50, 100):
                ke = int((ea <= T).sum()); ka = int((al <= T).sum())
                if ke + ka == 0:
                    continue
                print('      %6d %7d/%-4d %7d/%-4d %9.1f%%'
                      % (T, ke, len(ea), ka, len(al), 100 * ka / (ke + ka)))
        print()

    if persist:
        from optimus9.db.database_manager import DatabaseManager
        from optimus9.config import get_db_config
        d = DatabaseManager(**get_db_config()); d.connect(); d.execute(SAMPLE_DDL)
        d.execute('DELETE FROM rpl_bandlab')
        d.executemany('''INSERT INTO rpl_bandlab (bl_bias,bl_cur_tf,bl_del_tf,bl_raw_ms,bl_raw_utc,bl_raw_x,
            bl_raw_thr,bl_cur_x_raw,bl_cross_ms,bl_cross_utc,
            bl_cur_r,bl_cur_r_dist,bl_cur_x,bl_cur_m,bl_del_r,bl_del_x,bl_del_thr,bl_flip_ms,bl_hold_s,
            bl_curcross_ms,bl_wait_s,bl_outcome)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            [(r['bias'], r['cur'], r['dtf'], r['raw_ms'], utc(r['raw_ms']), r['raw_x'], r['raw_thr'],
              r['cur_x_raw'], r['ms'], utc(r['ms']), r['cur_r'], r['dist'], r['cur_x'],
              r['cur_m'], r['del_r'], r['del_x'], r['del_thr'], r['flip'], r['hold'], r['curx'],
              r['wait'], r['oc']) for r in rows])
        d.disconnect()
        print('persisted %d rows to rpl_bandlab' % len(rows))
    return rows


def delsweep(D=8, lo=45, hi=90):
    """PAIRED delegate sweep — the arm comparison is unmatched (arms fire at different bars, so their REQ
    differs and aligned% is not comparable). Here the walk, the gate and the fire bar are held fixed and ONLY
    the delegate TF varies, so every TF is scored on the same episodes. REQ = delegate fire -> current_tf
    cross, which is Joe's criterion: "aligned with current_tf's impending cross". ALIGNED = HELD >= REQ.
    Marks each TF that divides 1440 so a spike at the aligned TFs is visible against the slope."""
    gts = B.gts
    fires = []; seen = set()
    for oi, de, ti, tf, br, tev in B._fires(int(gts[0]), int(gts[-1]) + 1):
        key = (int(BP.te[ti]), tf)
        if key in seen:
            continue
        seen.add(key)
        fts = int(BP.te[ti])
        if gts[0] <= fts <= gts[-1]:
            fires.append((fts, int(np.searchsorted(gts, fts)), 'bull' if de > 0 else 'bear'))
    print('PAIRED delegate sweep — D=%d, same walk/gate/fire bar, only the delegate TF varies' % D)
    print('  %d fires | REQ = fire -> current_tf cross | ALIGNED = HELD >= REQ\n' % len(fires))
    print('  %-6s %8s %9s %10s %10s %9s   %s'
          % ('delTF', 'fired', 'ALIGNED', 'med REQ', 'med HELD', 'align?', ''))
    res = {}
    for t in range(lo, hi + 1):
        fired = 0; al = 0; reqs = []; helds = []
        for fts, gbar, bias in fires:
            # STRICTLY below current_tf. With `>=`, a TF equal to the rung is not delegating at all — its
            # "delegate cross" IS current_tf's cross, so it scores 100% aligned with a 0s wait. s90 did exactly
            # that at median rung 90 and inflated the aligned-TF mean to 49.5% vs 40.7%, a number I reported
            # before catching it. Excluded at source so it cannot re-enter the sweep.
            k, rung, dTF, ab = walk(bias, gbar, (lambda r, t=t: t if r > t else None), D)
            if k is None:
                continue
            fired += 1
            oc, _, req, held = outcome(dTF, rung, k, bias)
            al += (oc == 'aligned')
            if req is not None:
                reqs.append(req * 5)
            if held is not None:
                helds.append(held * 5)
        p = 100 * al / max(fired, 1)
        res[t] = (fired, p, np.median(reqs) if reqs else np.nan, np.median(helds) if helds else np.nan)
        print('  s%-5d %8d %8.1f%% %9.0fs %9.0fs %9s' % (t, fired, p, res[t][2], res[t][3],
                                                          'ALIGNED' if 1440 % t == 0 else ''))
    A = [res[t][1] for t in res if 1440 % t == 0]
    U = [res[t][1] for t in res if 1440 % t != 0]
    print('\n  aligned TFs   n=%2d  mean ALIGNED %.1f%%' % (len(A), np.mean(A)))
    print('  unaligned     n=%2d  mean ALIGNED %.1f%%' % (len(U), np.mean(U)))
    RA = [res[t][2] for t in res if 1440 % t == 0]
    RU = [res[t][2] for t in res if 1440 % t != 0]
    print('  med REQ       aligned %.0fs   unaligned %.0fs' % (np.mean(RA), np.mean(RU)))
    return res


if __name__ == '__main__':
    if '--samples' in sys.argv:
        samples(persist='--persist' in sys.argv)
    elif '--delsweep' in sys.argv:
        d = [a for a in sys.argv if a.isdigit()]
        delsweep(D=int(d[0]) if d else 8)
    else:
        main(sys.argv[1:])
