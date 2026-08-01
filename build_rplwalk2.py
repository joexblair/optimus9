"""build_rplwalk2 — the RPL walk on the NEW spec (Joe 0728/0729). Research file; nothing gated is touched.

LADDER — the continuation rule, Joe 0728 (his restatement, which supersedes the earlier wording):
    "unless ANY TF above above current_tf is (not r predicted AND not oob), walk current_tf upwards"
  => walk up  IFF  every TF above current_tf is (r-predicted OR OOB).
     Stop as soon as ANY TF above is quiet (neither predicted nor OOB).
  Monotonic UP. There is no walk-down: the only downward move in the spec is the DELEGATE, a separate
  mechanic. So rpl_flow_spec.md:50 ("monotonic up - never looks back") is not contradicted (task #4).
  NOTE this differs from today's engine, which climbs to the HIGHEST r-pred TF regardless of what sits
  between. Both ladders are computed here so the difference is measured, not assumed.

EXHAUSTION — the marker, from rpl_exhaust (built by build_exhaust.py). Three-way race on current_tf:
    leg r  x crosses r     gated by r's continuous OOB dwell >= 1/4 seam (TF*15s)
    leg M  x crosses Mage  same gate
    leg b  x crosses the boundary, UNCONDITIONAL
  First to fire wins. Read at the RAW crossing bar; actionable at the CONFIRMED bar (+40s).

FLOOR   TF22 - RPL starts there; below is s4Mage + s15/s22 (Joe 0729).
WINDOW  05-18 onward only. Pre-05-18 bars are synthetic - warmup only, never analysis (Joe 0729).

    python3 build_rplwalk2.py [--ceiling 120]
"""
import sys, datetime as dt
import numpy as np
import build_exhaust as X
import build_rpl_6of9 as B
import build_past50 as BP
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import _latch_with_reset
import optimus9.compute.breaching_line as BL
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

utc = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')


def load_markers():
    """rpl_exhaust -> {(tf,bias): (raw_bar_idx[], leg[], conf_bar_idx[])}, sorted by bar. Race winners only."""
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute('''SELECT xh_tf,xh_bias,xh_leg,xh_raw_ms,xh_conf_ms FROM rpl_exhaust
                        WHERE xh_race_first=1 ORDER BY xh_tf,xh_bias,xh_raw_ms''', fetch=True)
    d.disconnect()
    ts = R.L0['ts']
    out = {}
    for w in rows:
        k = (w['xh_tf'], w['xh_bias'])
        out.setdefault(k, [[], [], []])
        out[k][0].append(int(np.searchsorted(ts, w['xh_raw_ms'])))
        out[k][1].append(w['xh_leg'])
        out[k][2].append(int(np.searchsorted(ts, w['xh_conf_ms'])))
    return {k: (np.array(v[0]), np.array(v[1]), np.array(v[2])) for k, v in out.items()}, len(rows)


def ladders(bias, ceiling):
    """CONTIGUOUS ladder — Joe 0729 confirmed the reading: "any TF you would have to climb through".
    current_tf = the highest T such that EVERY TF from the floor up to T is participating (r-pred OR OOB).
    The first quiet TF blocks everything above it: no leaping across a quiet TF to a distant r-pred one,
    which is the leap today's engine makes and the causality guard Joe wrote the rule for.
    Returns (contiguous, engine_highest, tfs). 0 in `contiguous` = no climb at all (TF22 itself quiet).

    The literal reading — "any TF ANYWHERE above" — was tried and cannot climb: with ~99 TFs above the
    floor something above is always quiet, so it pins current_tf at 22 forever. It produced a ladder stuck
    at 119, waits of 3.4 days, and leg r scoring zero.

    LEAPFROG is BENCHED (Joe 0729): "I've seen cases in older specs where I needed to also test TF+2
    (because TF+1 did not trigger), but that may have been a line config issue... the data will tell us."
    """
    E = R.L0['E']; P = R.L0['P']; p = R._polar(bias)
    n = R.L0['n']
    tfs = list(range(X.RPL_FLOOR, ceiling + 1))
    rp = np.zeros((len(tfs), n), dtype=bool)
    for i, t in enumerate(tfs):
        rp[i] = (P[t] == p['CS']) | p['oob_climb'](E[t]['r'])
    alive = rp[0].copy()
    cont = np.where(alive, tfs[0], 0).astype(np.int16)
    for i in range(1, len(tfs)):
        alive &= rp[i]
        cont = np.where(alive, tfs[i], cont)
    eng = np.zeros(n, dtype=np.int16)
    for i, t in enumerate(tfs):
        eng = np.where(rp[i], t, eng)
    return cont, eng, tfs


LBL_1ST = 'r-pred'
LBL_2ND = '2nd x r-pred'      # Joe 0730: a HIGHER-TF exhaustion dirtied the line, x recovered AND went OOB
LBL_2ND_NOX = '2nd r-pred'    # same, but x did not return OOB between the clean and the episode


def line_state(tf, dr, exh_ms):
    """[PRODUCER] The clean/dirty flag on one r line (Joe 0730), plus the 2nd-x label.

    dirty <- an exhaustion prints ANYWHERE (matching bias) while this line is outside its fence.
             The spend signal is system-wide: 5069 of 5238 suppressions are cross-TF.
    clean <- EITHER of two line-local scenarios (Joe 0731, verbatim for RPL and exhv2):
             1. x crosses back through r. A higher TF spent the line early; price swung back and x
                travelled back out to OOB to collect the swing.
             2. r returns to the FH/FL fence.
             The recovery signal is line-local, so a line that re-armed on its own terms is not held to
             another timeframe's event.
    Lines start DIRTY: at bar 0 a line already outside the fence cannot be told from a retreat. The first
    recovery of either kind resolves it.
    Fence crossings are cross_wob-debounced at WOBN, like every other cross in the chain - raw r>=FH
    flickers exactly as predict_breach does.
    2nd x r-pred (Joe 0730): the label belongs ONLY where a HIGHER TF created the exhaustion and this
    line's x then returns to OOB. `pending` is armed only when the dirtying exhaustion's TF exceeds this
    line's TF - a same-TF or lower-TF exhaustion cleans normally but earns no label.
    exh_ms = [(conf_ms, cur_tf), ...] for this bias.
    Returns (clean[], dirtied_by[], second_x_pending[], x_oob[]) over the full tape."""
    ts = R.L0['ts']; E = R.L0['E'][tf]; n = R.L0['n']
    S = R.L0['src']
    fence = R.FH if dr > 0 else R.FL
    out = S.causal.cross_wob(E['r'] - fence, 0.0, 1 if dr > 0 else -1, R.WOBN)   # debounced "left the fence"
    rearm = np.asarray((R.L0['fx_bear'] if dr > 0 else R.L0['fx_bull'])[tf], bool)  # x back THROUGH r
    back = ~out & np.r_[False, out[:-1]]                                        # r re-entered the fence
    xo = (E['x'] >= R.HI) if dr > 0 else (E['x'] <= R.LO)               # x out of bounds
    ev = sorted([(int(np.searchsorted(ts, m)), 'X', int(etf)) for m, etf in exh_ms]
                + [(int(i), 'C', 0) for i in np.flatnonzero(rearm | back)])
    # THE FLAG comes from the jig producer (Joe 0731: "this should be a producer in the jig, not a method
    # in RPL"). mode='rpl' -> the spend is the GLOBAL applied-exhaustion set. The loop below no longer
    # computes the flag; it derives only the RPL-specific labels dby (which TF spent it) and pend (the
    # 2nd-x arming), which the producer has no business knowing about.
    clean = ~S.causal.clean_dirty(E['r'], E['x'], dr, R.HI, R.LO, R.FH, R.FL, R.WOBN, mode='rpl',
                                  spend_bars=[int(np.searchsorted(ts, m)) for m, _ in exh_ms])
    dby = np.zeros(n, np.int16); pend = np.zeros(n, bool)
    cur, src, pending, last = False, 0, False, 0
    for i, kind, etf in ev:
        dby[last:i] = src; pend[last:i] = pending; last = i
        if kind == 'X':
            if out[i] and cur:
                cur = False; src = etf; pending = False   # re-spent; src keeps WHICH TF spent it
        else:
            if not cur and src > tf:     # ONLY a HIGHER-TF exhaustion earns the 2nd x label (Joe 0730)
                pending = True
            cur = True
    dby[last:] = src; pend[last:] = pending
    return clean, dby, pend, xo


def rp_matrix(bias, ceiling, exh_ms=None):
    """participating[i] = TF tfs[i] is r-pred OR OOB, per bar.

    exh_ms (Joe 0730) = the applied exhaustion bars for this bias. When given, the predict term is gated
    by the line's clean/dirty flag (see line_state) so a line whose breach is spent and not re-formed
    cannot predict it again on the way back down through the FH..HI band. oob_climb is never gated.

    r-pred is CANCELLED by the x/r cross on the same line (Joe 0730). predict_breach is a per-bar state
    that can stay true after x has crossed through r, which kept a spent TF participating and carried it
    into the seed and the contiguous climb (s69: an 8.2-min r-pred at 0518 20:42 still holding at the
    0520 10:26 exhaustion, 37.75 h later). The predict term is now a latch: set on the predict rising
    edge, reset by the polarity-matched debounced cross already built in rpl_walk.build_lines
    (fx_bull = x crosses UNDER r, fx_bear = x crosses OVER r). Set wins on ties. oob_climb is NOT
    cancelled - r sitting out of bounds is a fact, not a prediction."""
    E = R.L0['E']; P = R.L0['P']; p = R._polar(bias)
    fx = R.L0['fx_bull'] if p['BULL'] else R.L0['fx_bear']
    dr = p['CS']
    tfs = list(range(X.RPL_FLOOR, ceiling + 1))
    rp = np.zeros((len(tfs), R.L0['n']), dtype=bool)
    for i, t in enumerate(tfs):
        pr = (P[t] == p['CS'])
        edge = pr & ~np.r_[False, pr[:-1]]
        live = _latch_with_reset(edge, np.asarray(fx[t], bool))
        if exh_ms is not None:
            live &= line_state(t, dr, exh_ms)[0]
        rp[i] = live | p['oob_climb'](E[t]['r'])
    return rp, tfs


_EP = {}


def rpred_episodes(tf, dr, exh_ms=None):
    """[PRODUCER] r-pred episodes on one line, cached. An episode is set by the predict_breach rising edge
    and reset by the x/r cross on the same line (Joe 0730) - the same definition rp_matrix participates on.
    Returns (starts, ends_exclusive) as bar indices."""
    if (tf, dr) not in _EP:
        E = R.L0['E'][tf]
        P = BL.predict_breach(E['r'], E['m'], E['M'], R.HI, R.LO, R.FH, R.FL, 0.0)
        pr = (P == dr)
        fx = np.asarray((R.L0['fx_bull'] if dr > 0 else R.L0['fx_bear'])[tf], bool)
        s = _latch_with_reset(pr & ~np.r_[False, pr[:-1]], fx)
        if exh_ms is not None:
            s &= line_state(tf, dr, exh_ms)[0]          # a dirty line cannot open an episode
        ch = np.flatnonzero(s[1:] != s[:-1]) + 1
        st = np.r_[0, ch]; en = np.r_[ch, len(s)]
        k = s[st]; st, en = st[k], en[k]
        lbl = [LBL_1ST] * len(st)
        if exh_ms is not None and len(st):
            _, _, pend, xo = line_state(tf, dr, exh_ms)   # armed ONLY by a HIGHER-TF exhaustion
            trans = np.flatnonzero(pend[1:] & ~pend[:-1]) + 1
            for t0 in trans.tolist():
                nxt = np.flatnonzero(st >= t0)
                if len(nxt):
                    j = int(nxt[0])
                    lbl[j] = LBL_2ND if xo[t0:int(st[j]) + 1].any() else LBL_2ND_NOX
        _EP[(tf, dr)] = (st, en, lbl)
    return _EP[(tf, dr)]


def rpred_at(tf, dr, i, exh_ms=None):
    """The r-pred episode live at, or most recently before, bar i.
    Returns (start_idx, end_idx_exclusive, label) or None. label = LBL_1ST | LBL_2ND (Joe 0730)."""
    st, en, lbl = rpred_episodes(tf, dr, exh_ms)
    h = np.flatnonzero(st <= i)
    if not len(h):
        return None
    j = int(h[-1])
    return int(st[j]), int(en[j]), lbl[j]


def seeded_ladder(rp, tfs, g, stop):
    """Joe 0729: "on s15/s22 handoff scan from the max TF downwards for an r-pred".
    SEED = the highest participating TF at the handoff bar g - a ONE-BAR top-down scan, so no causality is
    broken: nothing is read past bar g, and no quiet TF is skipped DURING a climb. It replaces walking up
    from TF22, which required an unbroken 84-TF chain to reach the TFs where the exhaustions actually are
    (applied current_tf maxed at 81 / median 28 while rpl_micro's exhaustions sat at 88-119).
    Above the seed the CONTIGUOUS rule still governs: climb to T only if every TF in (seed, T] participates.
    Returns per-bar current_tf over [g, stop), monotonic up. 0 = nothing participating at the handoff."""
    col = rp[:, g]
    if not col.any():
        return None, 0
    si = int(np.flatnonzero(col)[-1])                 # top-down scan: highest participating TF at handoff
    w = rp[si:, g:stop]
    alive = np.logical_and.accumulate(w, axis=0)      # contiguous run upward FROM the seed
    idx = alive.shape[0] - 1 - np.argmax(alive[::-1], axis=0)
    reach = np.where(alive.any(0), np.array(tfs[si:])[idx], tfs[si])
    return np.maximum.accumulate(reach.astype(np.int16)), tfs[si]


def main(argv):
    ceiling = 120
    for i, a in enumerate(argv):
        if a == '--ceiling' and i + 1 < len(argv):
            ceiling = int(argv[i + 1])
    X.rebuild_cache(ceiling)
    mk, nrows = load_markers()
    print('rpl_exhaust: %d race-winning markers loaded' % nrows)

    gts = R.L0['ts']
    S = X.ANALYSIS_START
    fires = []; seen = set()
    for oi, de, ti, tf, br, tev in B._fires(S, int(gts[-1]) + 1):
        key = (int(BP.te[ti]), tf)
        if key in seen:
            continue
        seen.add(key)
        fts = int(BP.te[ti])
        if S <= fts <= gts[-1]:
            fires.append((fts, int(np.searchsorted(gts, fts)), 'bull' if de > 0 else 'bear'))
    print('A/B setups on the REAL window (%s onward): %d' % (utc(S)[:5], len(fires)))

    res = {}
    for bias in ('bull', 'bear'):
        res[bias] = ladders(bias, ceiling)
    print('\nLADDER COMPARISON (per bar, whole real window)')
    print('  %-6s %10s %10s %10s %10s' % ('bias', 'new med', 'old med', 'new max', 'old max'))
    for bias in ('bull', 'bear'):
        nw, od, _ = res[bias]
        sl = slice(int(np.searchsorted(gts, S)), None)
        print('  %-6s %10d %10d %10d %10d'
              % (bias, np.median(nw[sl]), np.median(od[sl]), nw[sl].max(), od[sl].max()))
        eq = (nw[sl] == od[sl]).mean()
        print('         ladders agree on %.1f%% of bars; new is lower on %.1f%%'
              % (100 * eq, 100 * (nw[sl] < od[sl]).mean()))
    return res




APPLIED_DDL = '''CREATE TABLE IF NOT EXISTS rpl_exh_applied (
    ea_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    ea_created   DATETIME DEFAULT CURRENT_TIMESTAMP,
    ea_setup_ms  BIGINT, ea_setup_utc VARCHAR(19), ea_bias VARCHAR(4),
    ea_start_tf  INT,                  -- current_tf at the setup bar (floor 22)
    ea_cur_tf    INT,                  -- current_tf AT the exhaustion = the TF the marker is on
    ea_climbs    INT,                  -- rung changes between setup and exhaustion
    ea_leg       VARCHAR(1),           -- r | M | b
    ea_raw_ms    BIGINT, ea_raw_utc VARCHAR(19),      -- the real crossing bar
    ea_conf_ms   BIGINT, ea_conf_utc VARCHAR(19),     -- actionable (+40s)
    ea_wait_s    INT,                  -- setup -> exhaustion
    ea_x FLOAT, ea_r FLOAT, ea_mage FLOAT, ea_thr FLOAT,
    ea_dwell_s   INT, ea_seam_q_s INT, ea_established TINYINT,
    ea_origin_bars INT, ea_jump FLOAT,
    ea_rpred_ms  BIGINT, ea_rpred_utc VARCHAR(19),  -- the r-pred episode on cur_tf that made it participate
    ea_rpred_end_ms BIGINT, ea_rpred_bars INT,      -- episode end / length; end < ea_conf_ms = it had lapsed
    ea_rpred_label VARCHAR(16),                    -- 'r-pred' | '2nd x r-pred' (after an x re-breach)
    INDEX (ea_bias, ea_cur_tf), INDEX (ea_leg), INDEX (ea_raw_ms))'''


def applied(ceiling=120, persist=False, exh_ms=None, _pass=1):
    """THE ACTUAL EXHAUSTION EVENTS. rpl_exhaust is a per-TF candidate pool; an event only APPLIES when its
    TF is current_tf at that moment, and current_tf exists only relative to a setup (cummax of the
    continuation rule's reachable top, from the fire bar, floored at TF22). Also requires current_tf to be
    UNCHANGED across the 40s confirmation lag - acting on s22's cross once the ladder has moved to s60 would
    read a signal the machine no longer believes."""
    X.rebuild_cache(ceiling)
    gts = R.L0['ts']; S = X.ANALYSIS_START
    mk, _ = load_markers()
    RPM = {b: rp_matrix(b, ceiling, (exh_ms or {}).get(b)) for b in ('bull', 'bear')}
    _EP.clear()                       # episode cache is flag-dependent

    fires = []; seen = set()
    for oi, de, ti, tf, br, tev in B._fires(S, int(gts[-1]) + 1):
        key = (int(BP.te[ti]), tf)
        if key in seen:
            continue
        seen.add(key)
        fts = int(BP.te[ti])
        if S <= fts <= gts[-1]:
            fires.append((fts, int(np.searchsorted(gts, fts)), 'bull' if de > 0 else 'bear'))

    d = DatabaseManager(**get_db_config()); d.connect()
    det = {(w['xh_tf'], w['xh_bias'], w['xh_raw_ms']): w for w in d.execute(
        '''SELECT * FROM rpl_exhaust WHERE xh_race_first=1''', fetch=True)}
    rows = []
    for fts, g, bias in fires:
        # SPEC'D TERMINATOR, not a cap: "the setup stays latched until it fires branch a/b, or s60x
        # breaches on opposing oob" (Joe 0727). Without it a setup matched an exhaustion 3.4 days later.
        stop = B.cap_of(g, 1 if bias == 'bull' else -1)
        cur, seed = seeded_ladder(RPM[bias][0], RPM[bias][1], g, stop)
        if cur is None:
            continue
        best = None
        for (tf, bs), (raw, leg, conf) in mk.items():
            if bs != bias:
                continue
            for ix in np.flatnonzero((raw >= g) & (raw < stop)):
                k = int(raw[ix]); j = k - g
                if cur[j] != tf:
                    continue
                jc = min(int(conf[ix]) - g, len(cur) - 1)
                if cur[jc] != tf:               # ladder moved inside the 40s lag -> not actionable
                    continue
                if best is None or k < best[0]:
                    best = (k, tf, leg[ix], int(conf[ix]))
                break
        if best is None:
            continue
        k, tf, leg, kc = best
        w = det.get((tf, bias, int(gts[k])))
        if w is None:
            continue
        ep = rpred_at(tf, 1 if bias == 'bull' else -1, kc,
                      (exh_ms or {}).get(bias))          # the r-pred episode live at the CONFIRMED bar
        rows.append(dict(rp=int(gts[ep[0]]) if ep else None,
                         rpe=int(gts[ep[1] - 1]) if ep else None,
                         rpb=(ep[1] - ep[0]) if ep else None,
                         rpl=ep[2] if ep else None,
                         setup=fts, bias=bias, start=int(cur[0]), cur=tf,
                         climbs=int((np.diff(cur[:k - g + 1]) != 0).sum()), leg=leg,
                         raw=int(gts[k]), conf=int(gts[kc]), wait=int((gts[k] - fts) / 1000),
                         x=w['xh_x'], r=w['xh_r'], mage=w['xh_mage'], thr=w['xh_thr'],
                         dw=w['xh_dwell_s'], qs=w['xh_seam_q_s'], est=w['xh_established'],
                         ob=w['xh_origin_bars'], jump=w['xh_jump']))
    print('\n%d setups -> %d APPLIED exhaustion events' % (len(fires), len(rows)))
    if rows:
        import collections
        print('  by leg   :', dict(collections.Counter(r['leg'] for r in rows)))
        print('  current_tf at exhaustion: med %d  min %d  max %d'
              % (np.median([r['cur'] for r in rows]), min(r['cur'] for r in rows), max(r['cur'] for r in rows)))
        print('  climbs before exhaustion: med %d  max %d'
              % (np.median([r['climbs'] for r in rows]), max(r['climbs'] for r in rows)))
        print('  setup -> exhaustion (s) : med %d  p90 %d'
              % (np.median([r['wait'] for r in rows]), np.percentile([r['wait'] for r in rows], 90)))
        print('  distinct exhaustion bars:', len(set(r['raw'] for r in rows)))
    if persist and rows:
        d.execute(APPLIED_DDL)
        have = {c['Field'] for c in d.execute('DESCRIBE rpl_exh_applied', fetch=True)}
        for col, spec in (('ea_rpred_ms', 'BIGINT'), ('ea_rpred_utc', 'VARCHAR(19)'),
                          ('ea_rpred_end_ms', 'BIGINT'), ('ea_rpred_bars', 'INT'),
                          ('ea_rpred_label', 'VARCHAR(16)')):
            if col not in have:
                d.execute('ALTER TABLE rpl_exh_applied ADD COLUMN %s %s' % (col, spec))
        d.execute('DELETE FROM rpl_exh_applied')
        _n = lambda v: None if (isinstance(v, float) and not np.isfinite(v)) else v
        d.executemany('''INSERT INTO rpl_exh_applied (ea_setup_ms,ea_setup_utc,ea_bias,ea_start_tf,ea_cur_tf,
            ea_climbs,ea_leg,ea_raw_ms,ea_raw_utc,ea_conf_ms,ea_conf_utc,ea_wait_s,ea_x,ea_r,ea_mage,ea_thr,
            ea_dwell_s,ea_seam_q_s,ea_established,ea_origin_bars,ea_jump,
            ea_rpred_ms,ea_rpred_utc,ea_rpred_end_ms,ea_rpred_bars,ea_rpred_label)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            [tuple(_n(v) for v in (r['setup'], X.utc_(r['setup']), r['bias'], r['start'], r['cur'],
             r['climbs'], r['leg'], r['raw'], X.utc_(r['raw']), r['conf'], X.utc_(r['conf']), r['wait'],
             r['x'], r['r'], r['mage'], r['thr'], r['dw'], r['qs'], r['est'], r['ob'], r['jump'],
             r['rp'], X.utc_(r['rp']) if r['rp'] else None, r['rpe'], r['rpb'], r['rpl']))
             for r in rows])
        print('persisted %d rows to rpl_exh_applied' % len(rows))
    d.disconnect()
    return rows


def applied_2pass(ceiling=120, persist=False, passes=3):
    """Joe 0730. rp_matrix needs the clean/dirty flag; the flag needs the exhaustion bars; the exhaustion
    bars come from applied(). Circular. Resolved by iterating: pass 1 runs unflagged, each later pass feeds
    the previous pass's confirmed bars into the flag. Reports the delta per pass so convergence is visible
    rather than assumed. Only the final pass persists."""
    prev = None; rows = None
    for k in range(1, passes + 1):
        rows = applied(ceiling=ceiling, persist=False, exh_ms=prev, _pass=k)
        cur = {}
        for r in rows:
            cur.setdefault(r['bias'], []).append((int(r['conf']), int(r['cur'])))
        for b in cur:
            cur[b] = sorted(set(cur[b]))
        keys = {(r['conf'], r['cur'], r['bias']) for r in rows}
        if k == 1:
            print('\npass %d: %d rows, %d distinct events  (no flag)' % (k, len(rows), len(keys)))
        else:
            print('pass %d: %d rows, %d distinct events | vs prev: -%d +%d'
                  % (k, len(rows), len(keys), len(pk - keys), len(keys - pk)))
            if keys == pk:
                print('  converged at pass %d' % k)
                prev = cur
                break
        pk = keys; prev = cur
    if persist:
        applied(ceiling=ceiling, persist=True, exh_ms=prev, _pass=99)
    return rows


if __name__ == '__main__':
    if '--applied' in sys.argv:
        applied_2pass(persist='--persist' in sys.argv)
    else:
        main(sys.argv[1:])
