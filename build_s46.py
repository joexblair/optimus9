"""build_s46 — the s4/s6 strategy's atoms, banked once, with no knob baked in. Joe 0803 01:20.

    Joe: "nothing about our strategy relies on rpl, so why is rpl_entry 'banking discrete wobs'?
    instead of the jig?"
    Joe: "fix it, thanks"

TWO FAULTS REPAIRED

  1. THE `rpl_` PREFIX WAS WRONG. This strategy touches no RPL machinery. Tables are `s46_` — s4Mage
     sets the entry, s6 sets the exit (docs/260802_s4_s6_strategy.md).

  2. THE WOB DIMENSION WAS WASTE. rpl_entry held 7 discrete entry wobs x every confirmed cross = 19,035
     rows. An OOB run of length L confirms at EVERY wob <= L and none above, so ONE ROW PER RUN carrying
     its length answers every wob at once - including the exact threshold, which the 7-point sample
     could only bracket. 13,622 run rows carry strictly more than the 19,035 they replaced.

WHAT IS EXPENSIVE IS THE LINES, NOT THE KNOB. Building L0 + the 0.70 Mages costs ~42 s; cross_wob on a
resident array is microseconds. So the lines are banked and the knobs are not:

    s46_px       the px_smooth series, one row per 5 s bar. The thing every outcome is arithmetic over.
    s46_run      one row per s4Mage OOB run - EVERY run, including 1-bar blips.
                 sr_alt    item 13 - ALT loosened (other side, or same side having crossed 50 between)
                 sr_s1hold item 14 - bars s1Mage held within 15 points of the breach boundary Its length is the wob
                 answer; the lines at its first bar are the setup.
                 sr_ib_bars is the RAW in-bounds stretch before the run, i.e. the wob-1 gap. The gap AT
                 WOB n is not a stored column and must not be: Joe 0803 ruled that a sub-wob blip does
                 NOT interrupt the in-bounds dwell, so at wob n the gap runs from the END of the last
                 run with sr_dwell_bars >= n, counting intervening blips as in-bounds. That is a walk
                 over rows filtered on sr_dwell_bars >= n - sr_prev_end_ms makes it a single pass.
    s46_exit     one row per SIGN-RUN of (crossing line - s6Mage), with sx_run_bars = its length, so
                 the exit wob is derivable: confirmation at wob n = sx_ms + (n-1) bars, run >= n.
                 sx_dir is the TRADE the cross closes (+1 long / -1 short), NOT the line's direction;
                 sx_lb_min is bars since the line was OOB on that TRADE's breach side.
    s46_revtrig  one row per reverse trigger.

Every entry/exit/outcome question is then arithmetic over these, with no jig and no rebuild:
    entry bar at wob n   = the run's first bar + n - 1, for runs with sr_dwell_bars >= n
    exit                 = the first s46_exit row after it on the breach side with sx_lb_min <= LB
    ret / MAE / MFE      = arithmetic over s46_px between the two

PRODUCERS ONLY. _Causal.cross_wob for every boundary and cross; _Causal.seen_within for the lookback.
No runs_of, no runlen, no rollany. Causal throughout - nothing reads past its own bar.

    s4Mage bb 37|0.70|close @TF4      s6Mage bb 37|0.90|close @TF6   (Joe 0803: 0.70 -> 0.90)
    s4m    bb 6|0.45|close  @TF4      s6m    bb 6|0.40|close  @TF6   (Joe 0803: 0.45 -> 0.40)
                                      s6x    bb 5|0.35|close  @TF6   (Joe 0803, new)
    ladder r / x / mini / Mage at 12 rungs, from L0.   HI/LO 85/15.
WINDOW 05-18 -> 07-31. Pre-05-18 is synthetic warmup, never analysis (rpl_walk.py:121, Joe 0729).

    python3 build_s46.py
"""
import os, sys, re, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline, _Causal
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
HI, LO = R.HI, R.LO
TAPE0 = int(dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc).timestamp() * 1000)
RUNGS = [1, 2, 4, 6, 10, 15, 22, 30, 45, 60, 90, 120]
LINES = [('r', 'r'), ('x', 'x'), ('mm', 'm'), ('mg', 'M')]
CEIL_A, CEIL_B = 120, 90
SUPERSEDED = ['rpl_entry', 'rpl_s4evt', 'rpl_exit2', 'rpl_s6exit', 'rpl_revtrig', 'rpl_s6exh',
              'rpl_s6exh2', 'rpl_trades']

DDL_PX = '''CREATE TABLE IF NOT EXISTS s46_px (
    px_ms BIGINT PRIMARY KEY, px_utc VARCHAR(20), px_v DOUBLE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

DDL_RUN = '''CREATE TABLE IF NOT EXISTS s46_run (
    sr_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    sr_ms BIGINT, sr_utc VARCHAR(20), sr_end_ms BIGINT, sr_end_utc VARCHAR(20),
    sr_side VARCHAR(2), sr_dr TINYINT, sr_dwell_bars INT,
    sr_ib_bars INT, sr_prev_ms BIGINT, sr_prev_end_ms BIGINT, sr_prev_dwell INT,
    sr_alt TINYINT, sr_s1hold INT,
    sr_m4 DOUBLE, sr_m4_min DOUBLE, sr_m4_max DOUBLE,
    sr_s4m DOUBLE, sr_s6mage DOUBLE, sr_s6m DOUBLE, sr_px DOUBLE,
    sr_init_bull INT, sr_init_bear INT, sr_init_bull90 INT, sr_init_bear90 INT,
    %s,
    UNIQUE KEY (sr_ms), KEY (sr_side), KEY (sr_dwell_bars), KEY (sr_ib_bars)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''' % ', '.join(
    'sr_%s%d DOUBLE' % (p, t) for t in RUNGS for p, _k in LINES)

DDL_EX = '''CREATE TABLE IF NOT EXISTS s46_exit (
    sx_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    sx_line VARCHAR(4), sx_ms BIGINT, sx_utc VARCHAR(20), sx_dir TINYINT,
    sx_cross DOUBLE, sx_s6mage DOUBLE, sx_lb_min INT, sx_px DOUBLE, sx_run_bars INT,
    UNIQUE KEY (sx_line, sx_ms, sx_dir), KEY (sx_dir), KEY (sx_lb_min), KEY (sx_line),
    KEY (sx_run_bars)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

DDL_RV = '''CREATE TABLE IF NOT EXISTS s46_revtrig (
    rv_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    rv_ms BIGINT, rv_utc VARCHAR(20), rv_cage VARCHAR(2), rv_dr TINYINT,
    rv_s4m DOUBLE, rv_s4mage DOUBLE, rv_s6mage DOUBLE, rv_px DOUBLE,
    rv_s4m_oob_bars INT, rv_s4mage_oob_bars INT,
    UNIQUE KEY (rv_ms, rv_cage), KEY (rv_cage)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

edge = lambda s: np.flatnonzero(s & ~np.r_[False, s[:-1]])


def heal(d, table, ddl):
    """CREATE TABLE IF NOT EXISTS does not ADD columns. Precedent build_rpl_jig.py:203-212.
    Matches the NAME TYPE shape so index clauses sliced by the comma split are skipped."""
    d.execute(ddl)
    have = {r['COLUMN_NAME'].lower() for r in d.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() "
        "AND TABLE_NAME=%s", (table,), fetch=True)}
    add = 0
    for part in ddl[ddl.index('(') + 1:ddl.rindex(')')].split(','):
        q = part.strip()
        m = re.match(r'^(\w+)\s+(BIGINT|INT|DOUBLE|TINYINT|VARCHAR\(\d+\))\b', q, re.I)
        if not m or m.group(1).lower() in have:
            continue
        d.execute('ALTER TABLE %s ADD COLUMN %s' % (table, q)); add += 1
    return add


def main(argv):
    t0 = time.time()
    L = R.L0; ts = np.asarray(L['ts'], np.int64); n = len(ts); E = L['E']; P = L['P']
    s6m, s4m = E[6]['m'], E[4]['m']
    ovr = {}
    ovr.update(bbline('p4', 4.0, length=37, mult=0.70, src='close'))       # s4Mage, unchanged
    ovr.update(bbline('m6', 6.0, length=37, mult=0.90, src='close'))       # s6Mage - Joe 0803: 37|0.9
    ovr.update(bbline('x6', 6.0, length=5, mult=0.35, src='close'))        # s6x    - Joe 0803: 5|0.35
    ovr.update(bbline('n6', 6.0, length=6, mult=0.40, src='close'))        # s6m    - Joe 0803: 6|0.4
    end_ms = int(ts[-1]) + 5000
    with Jig(end_ms, hours=int((end_ms - TAPE0) / 3600000) + 2, warmup=180, overrides=ovr) as j:
        t2 = np.asarray(j.ts, np.int64); base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        srcv = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
        p_ = np.full(len(srcv), np.nan); p_[ei] = IC.dema(srcv[ei], int(R.PXS_CFG['len']))
        f = np.isfinite(p_); ix = np.where(f, np.arange(len(p_)), 0); np.maximum.accumulate(ix, out=ix)
        p_ = p_[ix]; p_[:int(np.argmax(f))] = p_[int(np.argmax(f))]
        M4_ = np.asarray(j.W.line('p4'), float); M6_ = np.asarray(j.W.line('m6'), float)
        X6_ = np.asarray(j.W.line('x6'), float); N6_ = np.asarray(j.W.line('n6'), float)
    off = int(np.searchsorted(ts, int(t2[0]))); kk = min(len(t2), n - off)
    lift = lambda a: np.concatenate([np.full(off, np.nan), a[:kk], np.full(n - off - kk, np.nan)])
    px, M4, M6 = lift(p_), lift(M4_), lift(M6_)
    s6x, s6mm = lift(X6_), lift(N6_)          # s6x bb 5|0.35, s6m bb 6|0.40  (both @TF6, Joe 0803)
    C = _Causal(None)
    print('lines ready  %.0f s' % (time.time() - t0), flush=True)

    d = DatabaseManager(**get_db_config()); d.connect()
    for tb, ddl in (('s46_px', DDL_PX), ('s46_run', DDL_RUN), ('s46_exit', DDL_EX),
                    ('s46_revtrig', DDL_RV)):
        heal(d, tb, ddl); d.execute('DELETE FROM %s' % tb)

    # ---------- s46_px : the price series, the thing every outcome is arithmetic over ----------
    a0 = int(np.searchsorted(ts, TAPE0))
    pxr = [(int(ts[i]), u(ts[i]), float(px[i])) for i in range(a0, n) if np.isfinite(px[i])]
    d.executemany('INSERT INTO s46_px (px_ms,px_utc,px_v) VALUES (%s,%s,%s)', pxr, chunk=10000)
    print('s46_px %d rows   %.0f s' % (len(pxr), time.time() - t0), flush=True)

    idx = np.arange(n)
    # ---------- s46_exit : the cross against s6Mage, for BOTH candidate crossing lines ----------
    #   Joe 0803 ruled the exit is "(OOB s6m) crossing s6Mage", then specified an s6x too. Both are
    #   banked and tagged (sx_line) so which one is the exit stays a WHERE clause, not a rebuild.
    #   THE EXIT WOB IS DERIVABLE, NOT FIXED. One row per SIGN-RUN of (crossing line - s6Mage), with
    #   sx_run_bars = the run's length. cross_wob's rising edge at wob n is the n-th bar of the run, so
    #   the confirmation at any n is sx_ms + (n-1) bars, for runs with sx_run_bars >= n. Same structure
    #   as s46_run - Joe 0803 on the entry: banking discrete wobs is waste, the run length IS the answer.
    #   sx_lb_min is read at the CROSS bar (the run's first bar): the cross is the event, the wob only
    #   confirms it held.
    #
    #   sx_dir IS THE TRADE THE CROSS CLOSES, NOT THE DIRECTION THE LINE MOVED. Both were inverted in
    #   the previous build and the consumer read sx_dir as a trade side, so a long was being closed by
    #   an up-cross and gated on the wrong boundary. Restored from build_exit2.py, which was correct:
    #       EV = {1: XDN[OOBHI[XDN]], -1: XUP[OOBLO[XUP]]}
    #   trade +1 = hi breach = LONG  -> the line crosses DOWN through s6Mage, having been OOB HI
    #   trade -1 = lo breach = SHORT -> the line crosses UP   through s6Mage, having been OOB LO
    exr = []
    for tag, cl in (('s6m', s6mm), ('s6x', s6x)):
        dd = cl - M6
        lasthi = np.maximum.accumulate(np.where(np.nan_to_num(cl, nan=-1e9) >= HI, idx, -1))
        lastlo = np.maximum.accumulate(np.where(np.nan_to_num(cl, nan=1e9) <= LO, idx, -1))
        LBMIN = {1: idx - lasthi + 1, -1: idx - lastlo + 1}   # keyed by the BREACH side
        for trade_dr, cross_dr in ((1, -1), (-1, +1)):        # long closes on a DOWN cross, short on UP
            side = C.cross_wob(dd, 0.0, cross_dr, 1)          # n=1 = the raw side test
            for z in edge(side):
                z = int(z)
                if int(ts[z]) < TAPE0 or LBMIN[trade_dr][z] < 1:
                    continue
                nz = np.flatnonzero(~side[z:])
                rl = int(nz[0]) if len(nz) else (n - z)
                exr.append((tag, int(ts[z]), u(ts[z]), trade_dr, float(cl[z]), float(M6[z]),
                            int(LBMIN[trade_dr][z]), float(px[z]) if np.isfinite(px[z]) else None, rl))
    d.executemany('INSERT IGNORE INTO s46_exit (sx_line,sx_ms,sx_utc,sx_dir,sx_cross,sx_s6mage,'
                  'sx_lb_min,sx_px,sx_run_bars) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                  sorted(exr), chunk=5000)
    print('s46_exit %d rows (s6m %d / s6x %d)   %.0f s'
          % (len(exr), sum(1 for z in exr if z[0] == 's6m'), sum(1 for z in exr if z[0] == 's6x'),
             time.time() - t0), flush=True)

    # ---------- RPL init scan (kept pending the A+D re-score; drop with P if it fails) ----------
    INIT = {}
    for ceil in (CEIL_A, CEIL_B):
        for dr in (1, -1):
            best = np.zeros(n, np.int32)
            for tf in range(1, ceil + 1):
                r_ = E[tf]['r']
                hit = ((r_ >= HI) if dr > 0 else (r_ <= LO)) | (np.asarray(P[tf], np.int8) == dr)
                np.copyto(best, np.int32(tf), where=hit)
            INIT[(ceil, dr)] = best

    # ---------- s46_run : EVERY s4Mage OOB run. Its length IS the wob answer. ----------
    #   cross_wob(.., n=1) is the raw side test; the run boundaries are its edges. No hand-rolled runs.
    # item 14 - s1Mage hold. Joe 0802: "require s1Mage to have been loosely/fuzzy lo oob for
    # > 2 minutes". s1Mage = bb 37|0.83|close @TF1 = L0's M at TF1. "fuzzy" = within FUZZ board points
    # of the boundary, the 15-point slack carried from the original build.
    S1 = E[1]['M']
    FUZZ = 15
    S1H = {1: (idx + 1) - np.maximum.accumulate(
               np.where(np.nan_to_num(S1, nan=-1e9) >= HI - FUZZ, 0, idx + 1)),
           -1: (idx + 1) - np.maximum.accumulate(
               np.where(np.nan_to_num(S1, nan=1e9) <= LO + FUZZ, 0, idx + 1))}
    ST = {1: C.cross_wob(M4, HI, +1, 1), -1: C.cross_wob(M4, LO, -1, 1)}
    ANY = ST[1] | ST[-1]
    # run-length of IN-BOUNDS ending at i. cross_wob's own idiom (jig.py:261-263): reset is 0 where the
    # condition HOLDS. The condition here is ~ANY, so the mask must be ~ANY - inverting it counts OOB
    # bars instead and reads 0 at every bar before an OOB run.
    rst = np.where(~ANY, 0, idx + 1)
    ibrun = (idx + 1) - np.maximum.accumulate(rst)          # consecutive IB bars ending at i, causal
    runs = []
    for sgn, side in ((1, 'hi'), (-1, 'lo')):
        st = ST[sgn]
        for a in edge(st):
            a = int(a)
            nz = np.flatnonzero(~st[a:])
            b = a + (int(nz[0]) - 1 if len(nz) else len(st) - a - 1)
            runs.append((a, b, sgn, side))
    runs.sort()
    rows = []
    for k, (a, b, sgn, side) in enumerate(runs):
        if int(ts[a]) < TAPE0:
            continue
        seg = M4[a:b + 1]; seg = seg[np.isfinite(seg)]
        prev = runs[k - 1] if k else None
        # item 13 - ALT, loosened. Joe 0802: "allow same-side OOB double dipping if Mage has traversed
        # past 50 before returning to the egress OOB". 1 = the previous run was the OTHER side, or the
        # same side with s4Mage crossing 50 in between.
        if prev is None:
            alt = 0
        elif prev[2] != side:
            alt = 1
        else:
            sg = M4[prev[1]:a + 1]
            alt = int((sg < 50).any() if sgn > 0 else (sg > 50).any())
        lad = []
        for t_ in RUNGS:
            for _p, kk_ in LINES:
                v_ = E[t_][kk_][a]
                lad.append(float(v_) if np.isfinite(v_) else None)
        rows.append(tuple([int(ts[a]), u(ts[a]), int(ts[b]), u(ts[b]), side, sgn, int(b - a + 1),
                           int(ibrun[a - 1]) if a else -1,
                           int(ts[prev[0]]) if prev else None,
                           int(ts[prev[1]]) if prev else None,
                           int(prev[1] - prev[0] + 1) if prev else None,
                           alt, int(S1H[sgn][a - 1]) if a else 0,
                           float(M4[a]) if np.isfinite(M4[a]) else None,
                           float(seg.min()) if len(seg) else None,
                           float(seg.max()) if len(seg) else None,
                           float(s4m[a]) if np.isfinite(s4m[a]) else None,
                           float(M6[a]) if np.isfinite(M6[a]) else None,
                           float(s6mm[a]) if np.isfinite(s6mm[a]) else None,
                           float(px[a]) if np.isfinite(px[a]) else None,
                           int(INIT[(CEIL_A, 1)][a]), int(INIT[(CEIL_A, -1)][a]),
                           int(INIT[(CEIL_B, 1)][a]), int(INIT[(CEIL_B, -1)][a])] + lad))
    d.executemany('INSERT INTO s46_run (sr_ms,sr_utc,sr_end_ms,sr_end_utc,sr_side,sr_dr,sr_dwell_bars,'
                  'sr_ib_bars,sr_prev_ms,sr_prev_end_ms,sr_prev_dwell,sr_alt,sr_s1hold,sr_m4,sr_m4_min,sr_m4_max,sr_s4m,sr_s6mage,'
                  'sr_s6m,sr_px,sr_init_bull,sr_init_bear,sr_init_bull90,sr_init_bear90,%s) VALUES (%s)'
                  % (','.join('sr_%s%d' % (p, t) for t in RUNGS for p, _k in LINES),
                     ','.join(['%s'] * (24 + len(LINES) * len(RUNGS)))), rows, chunk=2000)
    print('s46_run %d rows   %.0f s' % (len(rows), time.time() - t0), flush=True)

    # ---------- s46_revtrig ----------
    M4O = {1: C.cross_wob(s4m, HI, +1, 1), -1: C.cross_wob(s4m, LO, -1, 1)}
    ib6 = (M6 > LO) & (M6 < HI) & np.isfinite(M6)
    rl = lambda m: (idx + 1) - np.maximum.accumulate(np.where(m, 0, idx + 1))
    rvr = []
    for cage in (1, -1):
        m = M4O[cage]; r1 = rl(m); r2 = rl(ST[cage])
        lv = np.flatnonzero((~m) & np.r_[False, m[:-1]])
        for z in lv[ST[cage][lv] & ib6[lv]]:
            z = int(z)
            if int(ts[z]) < TAPE0:
                continue
            rvr.append((int(ts[z]), u(ts[z]), 'hi' if cage > 0 else 'lo', cage,
                        float(s4m[z]), float(M4[z]), float(M6[z]),
                        float(px[z]) if np.isfinite(px[z]) else None,
                        int(r1[z - 1]) if z else 0, int(r2[z])))
    d.executemany('INSERT IGNORE INTO s46_revtrig (rv_ms,rv_utc,rv_cage,rv_dr,rv_s4m,rv_s4mage,'
                  'rv_s6mage,rv_px,rv_s4m_oob_bars,rv_s4mage_oob_bars) VALUES (%s)'
                  % ','.join(['%s'] * 10), sorted(rvr), chunk=3000)
    print('s46_revtrig %d rows   %.0f s' % (len(rvr), time.time() - t0), flush=True)

    d.execute('DELETE FROM s46_exit WHERE sx_line IS NULL')
    for tb in SUPERSEDED:
        if d.execute("SHOW TABLES LIKE %s", (tb,), fetch=True):
            d.execute('DROP TABLE %s' % tb); print('  dropped %s (superseded)' % tb, flush=True)
    print('total %.0f s' % (time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
