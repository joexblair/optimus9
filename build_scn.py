"""build_scn — scenario models for the 1.3% / 0.65%-MAE signals, matched against the tape. Joe 0802 22:45.

    Joe: "for each of the 461 quorum 1 signals - at the beginning of the >=1.3% walk - build a scenario
    model - note the positioning of all rsd lines - note any recent crosses within each TF - lookback over
    the full line cache (05-18 to 08-01) - find matching models that return a loosely similar result
    (~1.3 with <~0.65 MAE) - note any variations in line position and crosses, so that the modelling is
    rich - all data must live in SRP based db tables"

JOE'S RULINGS 0802 23:05
  population  the 461 KEPT quorum-1 signals: established, reached 1.3%, needed <= 0.65% MAE to get there
  matching    score each historical bar 0-24 by how many of the 24 lines sit in the SAME BAND as the
              signal. Report the outcome distribution at EVERY level. No threshold is picked.
  crosses     raw sign change of (A - B). Immediate, no lag. Lookback 4 MINUTES = 48 bars at the 5 s grid.

THE LINE SET — 6 sets x 4 lines = 24
  gcs5 5 s | gcs15 15 s | s30 30 s | s1 1 min | s2 2 min | s4 4 min,  each with r, m, x, Mage
  Mage is bb 37 | 0.7 | close — the rsd mult Joe set 0802, NOT R.LN['M'] which is 0.83. This is the rsd
  exercise, so the rsd Mage is the right line. r/m/x are the generic R.LN specs at each TF, which is what
  build_rpl_jig already does for the small sets.
  s2 r/m/x do not exist in build_rpl_jig.LINES; they are built here from the same generic specs.

BANDS — Joe: "lo oob, lo boundary to 30, 30 to 60, 60 to hi boundary, hi oob", 30 and 60 sweepable
  0 = lo oob  (<= LO 15.0)      1 = (15, 30]      2 = (30, 60]      3 = (60, 85)      4 = hi oob (>= 85)
  The two mid edges are banked on the run row so a sweep is queryable rather than lost.

WHAT "LOOSELY SIMILAR RESULT" MEANS HERE — the same test the signals were selected by
  from a historical bar, in the signal's direction: does pxs reach 1.3% before needing more than 0.65%
  adverse on the way. One-sided, no horizon, no cap (handover §3.3 rule 1, Joe's no-caps rule).

SRP TABLES
  rpl_scn_run     one row per run — every parameter, so a result is reproducible from the table alone
  rpl_scn_signal  one row per source signal (461)
  rpl_scn_pos     one row per (owner, line) — line POSITIONING only. owner = signal pk or match pk
  rpl_scn_cross   one row per (owner, pair) with a cross inside the lookback — cross EVENTS only
  rpl_scn_agree   one row per (signal, agreement level 0-24) — COMPLETE, every tape bar counted, no
                  truncation. This is the distribution Joe asked for and it loses nothing.
  rpl_scn_match   individual bars at each signal's MAXIMUM agreement level — the nearest neighbours, kept
                  so the per-match variation in position and crosses is inspectable

CAUSALITY. Every scenario is read AT its own bar from history ending there. The forward outcome is
computed separately and is never an input to the match.

    python3 build_scn.py                       # full run
    python3 build_scn.py --lo-mid 30 --hi-mid 60 --cross-bars 48 --target 1.3 --mae 0.65
"""
import os, sys, time, datetime as dt, heapq
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from vmomo import vmomo

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

SETS = [('gcs5', 5.0 / 60), ('gcs15', 0.25), ('s30', 0.5), ('s1', 1.0), ('s2', 2.0), ('s4', 4.0)]
KINDS = ('r', 'm', 'x', 'M')
NAMES = ['%s_%s' % (s, k) for s, _ in SETS for k in KINDS]        # 24, stable order
PAIRS = [(a, b) for i, a in enumerate(KINDS) for b in KINDS[i + 1:]]   # 6 within-set pairs
CROSS = ['%s_%s%s' % (s, a, b) for s, _ in SETS for a, b in PAIRS]      # 36, stable order

# MOMO LINES — Joe 0802 23:20: "add the momo decisions to the modelling".
# BOTH sets, because they are different questions and different lines:
#   the rule-3 trio the momo DECISION is actually made on — jr4/jr15/jr22, exhv2's own R_SPEC
#   the six rsd r lines the MODELLING is over — gcs5_r .. s4_r, generic R.LN['r'] at each TF
# s4_r and jr4 are NOT the same line: R.LN['r'] has rsi 5, exhv2's R_SPEC[4] has rsi 6.
MOMO_LINES = [('s4r', 'jr4'), ('s15r', 'jr15'), ('s22r', 'jr22')] + \
             [('%s_r' % s, '%s_r' % s) for s, _ in SETS]
MOMO_STATE = {0: 'none', 1: 'sideways', 2: 'curl', 3: 'momo'}

TAPE0 = int(dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc).timestamp() * 1000)   # Joe: 05-18
TAPE1 = int(dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc).timestamp() * 1000)    # Joe: 08-01

DDL = ['''CREATE TABLE IF NOT EXISTS rpl_scn_run (
    rn_pk BIGINT AUTO_INCREMENT PRIMARY KEY, rn_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    rn_target_pct DOUBLE, rn_mae_max_pct DOUBLE,
    rn_band_lo DOUBLE, rn_band_lomid DOUBLE, rn_band_himid DOUBLE, rn_band_hi DOUBLE,
    rn_cross_bars INT, rn_cross_sec INT,
    rn_tape0_ms BIGINT, rn_tape1_ms BIGINT, rn_tape_bars BIGINT,
    rn_quorum TINYINT, rn_n_signal INT, rn_lines INT, rn_pairs INT, rn_note TEXT)''',
 '''CREATE TABLE IF NOT EXISTS rpl_scn_signal (
    sg_pk BIGINT AUTO_INCREMENT PRIMARY KEY, sg_run BIGINT,
    sg_ms BIGINT, sg_utc VARCHAR(20),
    sg_arm_ms BIGINT, sg_arm_utc VARCHAR(20), sg_arm_line VARCHAR(4), sg_arm_side VARCHAR(2),
    sg_dir VARCHAR(5), sg_dr TINYINT, sg_px DOUBLE,
    sg_momo_n TINYINT, sg_momo_which VARCHAR(24),
    sg_bars_to_target INT, sg_min_to_target DOUBLE, sg_mae_pct DOUBLE,
    sg_band_vec VARCHAR(48), sg_max_agree TINYINT,
    sg_momo_up TINYINT, sg_momo_dn TINYINT,
    KEY (sg_run), KEY (sg_ms))''',
 '''CREATE TABLE IF NOT EXISTS rpl_scn_pos (
    ps_pk BIGINT AUTO_INCREMENT PRIMARY KEY, ps_run BIGINT,
    ps_owner_kind VARCHAR(6), ps_owner BIGINT,
    ps_tf VARCHAR(6), ps_kind VARCHAR(2), ps_line VARCHAR(10),
    ps_value DOUBLE, ps_band TINYINT,
    KEY (ps_run), KEY (ps_owner_kind, ps_owner), KEY (ps_line))''',
 '''CREATE TABLE IF NOT EXISTS rpl_scn_cross (
    cx_pk BIGINT AUTO_INCREMENT PRIMARY KEY, cx_run BIGINT,
    cx_owner_kind VARCHAR(6), cx_owner BIGINT,
    cx_tf VARCHAR(6), cx_pair VARCHAR(4), cx_a VARCHAR(2), cx_b VARCHAR(2),
    cx_dir TINYINT, cx_bars_since INT, cx_sec_since INT,
    KEY (cx_run), KEY (cx_owner_kind, cx_owner), KEY (cx_tf, cx_pair))''',
 '''CREATE TABLE IF NOT EXISTS rpl_scn_agree (
    ag_pk BIGINT AUTO_INCREMENT PRIMARY KEY, ag_run BIGINT, ag_signal BIGINT,
    ag_level TINYINT, ag_n_bars BIGINT,
    ag_n_reached BIGINT, ag_n_clean BIGINT,
    ag_rate_clean DOUBLE, ag_med_min DOUBLE, ag_med_mae DOUBLE,
    KEY (ag_run), KEY (ag_signal), KEY (ag_level))''',
 '''CREATE TABLE IF NOT EXISTS rpl_scn_momo (
    mo_pk BIGINT AUTO_INCREMENT PRIMARY KEY, mo_run BIGINT,
    mo_owner_kind VARCHAR(6), mo_owner BIGINT,
    mo_line VARCHAR(10), mo_dr TINYINT,
    mo_state VARCHAR(8), mo_slope DOUBLE, mo_r2 DOUBLE, mo_r DOUBLE,
    KEY (mo_run), KEY (mo_owner_kind, mo_owner), KEY (mo_line, mo_dr), KEY (mo_state))''',
 '''CREATE TABLE IF NOT EXISTS rpl_scn_match (
    mt_pk BIGINT AUTO_INCREMENT PRIMARY KEY, mt_run BIGINT, mt_signal BIGINT,
    mt_ms BIGINT, mt_utc VARCHAR(20), mt_agree TINYINT,
    mt_px DOUBLE, mt_reached TINYINT, mt_clean TINYINT,
    mt_bars_to_target INT, mt_min_to_target DOUBLE, mt_mae_pct DOUBLE,
    mt_band_vec VARCHAR(48), mt_band_diff VARCHAR(255),
    KEY (mt_run), KEY (mt_signal), KEY (mt_agree))''']


def bands_of(V, lo, lomid, himid, hi):
    """(bars, 24) int8 band index. NaN -> -1, which can never equal a signal band, so a warming line
    simply fails to agree rather than agreeing by accident."""
    out = np.full(V.shape, -1, np.int8)
    f = np.isfinite(V)
    out[f & (V <= lo)] = 0
    out[f & (V > lo) & (V <= lomid)] = 1
    out[f & (V > lomid) & (V <= himid)] = 2
    out[f & (V > himid) & (V < hi)] = 3
    out[f & (V >= hi)] = 4
    return out


def cross_features(V, nb):
    """For each of the 36 within-set pairs: (dir, bars_since) at every bar, for the most recent raw sign
    change of (A - B). bars_since = nb+1 when no cross inside the lookback. Raw sign change per Joe."""
    n = V.shape[0]
    DIRS = np.zeros((n, len(CROSS)), np.int8)
    SINCE = np.full((n, len(CROSS)), nb + 1, np.int32)
    ci = 0
    for si, (s, _) in enumerate(SETS):
        base = si * 4
        for a, b in PAIRS:
            ia, ib = base + KINDS.index(a), base + KINDS.index(b)
            d = V[:, ia] - V[:, ib]
            sg = np.sign(np.nan_to_num(d, nan=0.0)).astype(np.int8)
            flip = np.r_[False, (sg[1:] != sg[:-1]) & (sg[1:] != 0) & (sg[:-1] != 0)]
            idx = np.arange(n)
            last = np.maximum.accumulate(np.where(flip, idx, -1))
            has = last >= 0
            SINCE[has, ci] = (idx - last)[has]
            DIRS[has, ci] = sg[last[has]]              # +1 = A now above B, -1 = A now below
            ci += 1
    SINCE[SINCE > nb] = nb + 1
    return DIRS, SINCE


def forward_leg(px, dr, target_pct, ):
    """For EVERY bar i: (bars to the first bar where pxs has moved target_pct in direction dr, and the
    worst adverse excursion on the way). bars = -1 when never reached.

    O(n log n) via a min-heap on the per-bar threshold, plus a sparse table for the range extreme. No
    horizon and no cap — a bar that never reaches its target is recorded as never, not truncated."""
    n = len(px)
    tgt = px * (1 + target_pct / 100.0) if dr > 0 else px * (1 - target_pct / 100.0)
    hit = np.full(n, -1, np.int64)
    h = []
    for j in range(n):
        p = px[j]
        if dr > 0:
            while h and h[0][0] <= p:
                _, i = heapq.heappop(h); hit[i] = j
            heapq.heappush(h, (tgt[j], j))
        else:
            while h and -h[0][0] >= p:
                _, i = heapq.heappop(h); hit[i] = j
            heapq.heappush(h, (-tgt[j], j))
    # range extreme against the direction, over [i, hit[i]]
    K = int(np.ceil(np.log2(max(n, 2)))) + 1
    sp = np.empty((K, n), np.float64)   # float32 lost ~3e-6 on the MAE; the gate is 0.65 so keep full precision
    sp[0] = px if dr > 0 else -px                      # we need the MIN for a LONG, MAX for a SHORT
    for k in range(1, K):
        L = 1 << k
        if L > n:
            sp[k] = sp[k - 1]; continue
        sp[k, :n - L + 1] = np.minimum(sp[k - 1, :n - L + 1], sp[k - 1, L // 2:n - L // 2 + 1])
        sp[k, n - L + 1:] = sp[k - 1, n - L + 1:]
    mae = np.full(n, np.nan, np.float64)
    ok = hit >= 0
    ii = np.flatnonzero(ok); jj = hit[ii]
    ln = (jj - ii + 1).astype(np.int64)
    kk = np.floor(np.log2(np.maximum(ln, 1))).astype(np.int64)
    ext = np.minimum(sp[kk, ii], sp[kk, jj - (1 << kk) + 1])
    ext = ext if dr > 0 else -ext
    mae[ii] = ((px[ii] - ext) / px[ii] * 100.0) if dr > 0 else ((ext - px[ii]) / px[ii] * 100.0)
    return hit, mae


def main(argv):
    g = lambda k, d: (type(d)(argv[argv.index(k) + 1]) if k in argv else d)
    TARGET = g('--target', 1.3)
    MAEMAX = g('--mae', 0.65)
    LOMID = g('--lo-mid', 30.0)
    HIMID = g('--hi-mid', 60.0)
    NB = g('--cross-bars', 48)
    QUORUM = g('--quorum', 1)
    HI, LO = R.HI, R.LO

    ovr = {}
    for s, tf in SETS:
        for k in KINDS:
            nm = '%s_%s' % (s, k)
            ovr.update(bbline(nm, tf, length=37, mult=0.7, src='close') if k == 'M'
                       else R._mk(nm, tf, R.LN[k]))
    ovr.update(J.LINES)                                 # jMg1/jMg2 for the arming, jr4/jr15/jr22 for momo

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    hours = int((end_ms - TAPE0) / 3600000) + 1
    print('tape %s -> %s  (build to now, matched only inside the span)  hours=%d' % (u(TAPE0), u(TAPE1), hours),
          flush=True)

    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        ix = np.where(fin, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        V = np.vstack([np.asarray(j.W.line(nm), float) for nm in NAMES]).T      # (n, 24)
        G1 = np.asarray(j.W.line('jMg1'), float); G2 = np.asarray(j.W.line('jMg2'), float)
        RL = {k: np.asarray(j.W.line(v), float) for k, v in
              (('s4r', 'jr4'), ('s15r', 'jr15'), ('s22r', 'jr22'))}
        RLALL = {v: np.asarray(j.W.line(v), float) for _, v in MOMO_LINES}
    n = len(ts)
    print('jig build %.1f s   bars %d   lines %d   pairs %d' % (time.time() - t0, n, len(NAMES), len(CROSS)),
          flush=True)

    BND = bands_of(V, LO, LOMID, HIMID, HI)
    DIRS, SINCE = cross_features(V, NB)
    print('bands + crosses %.1f s' % (time.time() - t0), flush=True)

    t1 = time.time()
    HITL, MAEL = forward_leg(px, 1, TARGET)
    HITS, MAES = forward_leg(px, -1, TARGET)
    print('forward legs %.1f s   LONG reached %d/%d   SHORT reached %d/%d'
          % (time.time() - t1, int((HITL >= 0).sum()), n, int((HITS >= 0).sum()), n), flush=True)

    # ---- momo decisions, every bar, every line, BOTH directions -------------------------------------
    t3 = time.time()
    MO = {}
    for tag, src_ in MOMO_LINES:
        arr = RLALL[src_]
        for dr in (1, -1):
            MO[(tag, dr)] = vmomo(arr, dr)
    cnt = {}
    for dr in (1, -1):
        cnt[dr] = sum((MO[(t_, dr)][0] == 3).astype(np.int8) for t_, _ in MOMO_LINES[:3])   # rule-3 trio
    print('momo %d lines x 2 dirs  %.1f s   momo-state bars: up %d  dn %d'
          % (len(MOMO_LINES), time.time() - t3,
             int(sum((MO[(t_, 1)][0] == 3).sum() for t_, _ in MOMO_LINES)),
             int(sum((MO[(t_, -1)][0] == 3).sum() for t_, _ in MOMO_LINES))), flush=True)

    # ---- regenerate the quorum-1 KEPT signals over the same 168 h window predict_walk used -------------
    from predict_walk import walk, resolve
    W = walk(ts, px, {'jMg1': G1, 'jMg2': G2, 'jr4': RL['s4r'], 'jr15': RL['s15r'], 'jr22': RL['s22r']},
             HI, LO, end_ms - 168 * 3600000)
    SIG = []
    for w in W:
        r = resolve(w, ts, px, QUORUM)
        if r is None:
            continue
        i, mn, which = r
        hit, mae = (HITL[i], MAEL[i]) if w['dr'] > 0 else (HITS[i], MAES[i])
        if hit < 0 or not np.isfinite(mae) or mae > MAEMAX:
            continue
        SIG.append(dict(i=i, w=w, momo_n=mn, which=which, hit=int(hit), mae=float(mae)))
    print('KEPT quorum-%d signals: %d' % (QUORUM, len(SIG)), flush=True)

    # ---- the matchable tape: inside 05-18 -> 08-01, finite bands, and a resolved forward leg -----------
    inspan = (ts >= TAPE0) & (ts <= TAPE1)
    print('tape bars inside the span: %d' % int(inspan.sum()), flush=True)

    for q in DDL:
        d.execute(q)
    # SELF-HEALING COLUMNS. CREATE TABLE IF NOT EXISTS does NOT add a column to a table that already
    # exists, so a field added mid-development fails every INSERT with 1054 until someone ALTERs by hand.
    # It bit this script when sg_momo_up/sg_momo_dn were added after a first run had already created
    # rpl_scn_signal. Precedent: build_rpl_jig.py:203-212, build_exhv2.py:409.
    for _t, _c, _ty in (('rpl_scn_signal', 'sg_momo_up', 'TINYINT'),
                        ('rpl_scn_signal', 'sg_momo_dn', 'TINYINT')):
        try:
            d.execute('ALTER TABLE %s ADD COLUMN %s %s' % (_t, _c, _ty))
        except Exception:
            pass                                     # already present
    run = d.execute(
        'INSERT INTO rpl_scn_run (rn_target_pct,rn_mae_max_pct,rn_band_lo,rn_band_lomid,rn_band_himid,'
        'rn_band_hi,rn_cross_bars,rn_cross_sec,rn_tape0_ms,rn_tape1_ms,rn_tape_bars,rn_quorum,rn_n_signal,'
        'rn_lines,rn_pairs,rn_note) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
        (TARGET, MAEMAX, LO, LOMID, HIMID, HI, NB, NB * 5, TAPE0, TAPE1, int(inspan.sum()), QUORUM,
         len(SIG), len(NAMES), len(CROSS),
         'Mage bb 37|0.7 (rsd mult, Joe 0802). r/m/x = generic R.LN at each TF. Raw sign-change crosses, '
         'lookback %d bars = %d s (Joe 0802 23:05). Agreement = count of the %d lines in the same band; '
         'every level 0-%d banked, nothing truncated.' % (NB, NB * 5, len(NAMES), len(NAMES))))
    print('run pk %d' % run, flush=True)

    LNAME = [(s, k, '%s_%s' % (s, k)) for s, _ in SETS for k in KINDS]
    CNAME = [(s, a, b, '%s%s' % (a, b)) for s, _ in SETS for a, b in PAIRS]

    def bank_pos(kind, owner, bar):
        rows = [(run, kind, owner, s, k, nm, (None if not np.isfinite(V[bar, c]) else float(V[bar, c])),
                 int(BND[bar, c])) for c, (s, k, nm) in enumerate(LNAME)]
        d.executemany('INSERT INTO rpl_scn_pos (ps_run,ps_owner_kind,ps_owner,ps_tf,ps_kind,ps_line,'
                      'ps_value,ps_band) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', rows)

    def bank_cross(kind, owner, bar):
        rows = [(run, kind, owner, s, p, a, b, int(DIRS[bar, c]), int(SINCE[bar, c]), int(SINCE[bar, c]) * 5)
                for c, (s, a, b, p) in enumerate(CNAME) if SINCE[bar, c] <= NB]
        if rows:
            d.executemany('INSERT INTO rpl_scn_cross (cx_run,cx_owner_kind,cx_owner,cx_tf,cx_pair,cx_a,'
                          'cx_b,cx_dir,cx_bars_since,cx_sec_since) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                          rows)

    def bank_momo(kind, owner, bar):
        rows = []
        for tag, _ in MOMO_LINES:
            for dr in (1, -1):
                st_, sl_, r2_, rw_ = MO[(tag, dr)]
                f = lambda v: (None if not np.isfinite(v) else float(v))
                rows.append((run, kind, owner, tag, dr, MOMO_STATE[int(st_[bar])],
                             f(sl_[bar]), f(r2_[bar]), f(rw_[bar])))
        d.executemany('INSERT INTO rpl_scn_momo (mo_run,mo_owner_kind,mo_owner,mo_line,mo_dr,mo_state,'
                      'mo_slope,mo_r2,mo_r) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)

    vec = lambda b: ''.join(str(x) if x >= 0 else '-' for x in BND[b])
    t2 = time.time()
    for si, s in enumerate(SIG):
        i, w = s['i'], s['w']
        sg = d.execute(
            'INSERT INTO rpl_scn_signal (sg_run,sg_ms,sg_utc,sg_arm_ms,sg_arm_utc,sg_arm_line,sg_arm_side,'
            'sg_dir,sg_dr,sg_px,sg_momo_n,sg_momo_which,sg_bars_to_target,sg_min_to_target,sg_mae_pct,'
            'sg_band_vec,sg_max_agree,sg_momo_up,sg_momo_dn) VALUES ('+','.join(['%s']*19)+')',
            (run, int(ts[i]), u(ts[i]), int(ts[w['arm']]), u(ts[w['arm']]), w['line'], w['side'],
             'LONG' if w['dr'] > 0 else 'SHORT', w['dr'], float(px[i]), s['momo_n'], s['which'],
             s['hit'] - i, (s['hit'] - i) * 5 / 60.0, s['mae'], vec(i), None,
             int(cnt[1][i]), int(cnt[-1][i])))
        bank_pos('signal', sg, i); bank_cross('signal', sg, i); bank_momo('signal', sg, i)

        # agreement over every in-span tape bar
        agree = (BND == BND[i]).sum(axis=1).astype(np.int8)
        HIT, MAE = (HITL, MAEL) if w['dr'] > 0 else (HITS, MAES)
        reached = (HIT >= 0)
        clean = reached & (MAE <= MAEMAX)
        arows = []
        for lv in range(len(NAMES) + 1):
            m = inspan & (agree == lv)
            nb_ = int(m.sum())
            if not nb_:
                continue
            mr = m & reached; mc = m & clean
            nr, nc = int(mr.sum()), int(mc.sum())
            mm = ((HIT[mc] - np.flatnonzero(mc)) * 5 / 60.0) if nc else np.array([])
            arows.append((run, sg, lv, nb_, nr, nc, (nc / nb_ * 100.0),
                          float(np.median(mm)) if nc else None,
                          float(np.median(MAE[mc])) if nc else None))
        d.executemany('INSERT INTO rpl_scn_agree (ag_run,ag_signal,ag_level,ag_n_bars,ag_n_reached,'
                      'ag_n_clean,ag_rate_clean,ag_med_min,ag_med_mae) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                      arows)

        mx = int(agree[inspan].max())
        d.execute('UPDATE rpl_scn_signal SET sg_max_agree=%s WHERE sg_pk=%s', (mx, sg))
        near = np.flatnonzero(inspan & (agree == mx))
        for b in near:
            b = int(b)
            diff = ','.join('%s:%d>%d' % (NAMES[c], BND[i, c], BND[b, c])
                            for c in range(len(NAMES)) if BND[b, c] != BND[i, c])
            mt = d.execute(
                'INSERT INTO rpl_scn_match (mt_run,mt_signal,mt_ms,mt_utc,mt_agree,mt_px,mt_reached,'
                'mt_clean,mt_bars_to_target,mt_min_to_target,mt_mae_pct,mt_band_vec,mt_band_diff) '
                'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (run, sg, int(ts[b]), u(ts[b]), mx, float(px[b]), int(HIT[b] >= 0),
                 int(HIT[b] >= 0 and np.isfinite(MAE[b]) and MAE[b] <= MAEMAX),
                 int(HIT[b] - b) if HIT[b] >= 0 else None,
                 float((HIT[b] - b) * 5 / 60.0) if HIT[b] >= 0 else None,
                 float(MAE[b]) if np.isfinite(MAE[b]) else None, vec(b), diff[:255]))
            bank_pos('match', mt, b); bank_cross('match', mt, b); bank_momo('match', mt, b)
        if (si + 1) % 25 == 0:
            print('  %d/%d signals  %.0f s' % (si + 1, len(SIG), time.time() - t2), flush=True)
    print('done  %.0f s total' % (time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
