"""build_s46_div — the divergence polarity flip, banked as raw slopes so every soft knob is a
read-time filter. Joe 0803/0804.

    ############################################################################
    #  DISABLED — Joe 0804: "disable, but don't remove, the divergence code"   #
    #  Runs only with --enable. NOT in the trade path: build_s46_window.py and #
    #  emit_ad_pine.py reference neither s46_div nor s46_flip. Tables retained.#
    #  WHY: the flip lost at every setting. 191,275 knob settings, MAE rises   #
    #  monotonically with flip count; per-line vote rates on the 517 trades a  #
    #  flip damages are within 7 points of the 332 it helps. The one combo     #
    #  beating baseline on both halves of a 50/50 chronological split moves    #
    #  MAE 0.269->0.267 IS and 0.237->0.236 OOS on 7 flips out of 849.         #
    ############################################################################

WHAT JOE SPECIFIED (verbatim, so nothing is lost in translation)
    "@07-29 06:26, a long position is taken at the top of a swing - instant MAE with no way out"
    "I think we can reverse the polarity before the trigger fires, if we use divergence: s{3,4,5}Mage
     and s{3,4,5}r and possibly m, showing bearish divergence votes (6 votes in total)"
    "the anchor needs to be captured when s6x crosses, the floater is derived by calcs in the jig
     (for a bear div, calcs will look for the max value prior to the last min pxs value prior to the
     floater)"
    "swap s3 with s6"                      -> the voting family is s4 / s5 / s6
    "use s4Mage"                           -> Mage votes are bb 37|0.70|close, s4Mage's own config
    "trade the opposite side. ie hi breach becomes SHORT"
    "instruct the divergence mechanic to lookback {sweep 25} x TF minutes, where TF is the highest TF
     in the voting group (eg 25 x 6 = 150 minutes) / inside of the 150 minutes, mechanic will (for
     bear) find the lowest pxs value before the highest line value (excluding the anchor value)"
    "it's important that the highest line value is before the lowest pxs"

THE ORDER, WHICH IS THE WHOLE MECHANIC
    [line extreme]  ->  [pxs extreme]  ->  [anchor]
    bear (LONG entry):  line MAX   then pxs MIN after it,  then the anchor bar
    bull (SHORT entry): line MIN   then pxs MAX after it,  then the anchor bar
    The anchor bar itself is excluded from both searches (Joe: "excluding the anchor value").
    Verified on Joe's case: 07-29 anchor 06:30, s6r floater 05:00 value 100.00 at MULT 15, pxs min
    after it, pk_state -1.0 BEAR. Joe's own reading: "anchor: 42 / prior min pxs: 06:06 / prior max
    of s6r: 05:00 (value 100) - this is a clear bearish divergence".

RAW SLOPES ARE BANKED, NOT STATES. `pk_state` is re-applied at read time from dv_line_slope /
dv_price_slope, so SLOPE_FLOOR and the Price-Match policy cost nothing to sweep and there is still a
single source of truth for the decision (jig `_Causal.pk_state` -> Pk5sGateComputer).

KNOBS
    GRID (changes the argmax, so it must be banked)
      MULT    lookback = MULT x TF_MAX(6) minutes
      GUARD   bars immediately before the anchor excluded from the FLOATER search. The pxs search is
              NOT guarded - guard exists to stop the line extreme landing inside the entry's own
              move (at MULT 25 s5Mage/s6Mage both put their floater 4 min before the anchor).
    ANCHOR IS NOT A KNOB. The anchor is the ENTRY BAR - the s4Mage boundary cross - and nothing else.
    Joe's literal spec was "captured when s6x crosses", and his verification anchor 06:30 sits 4 min
    AFTER the 06:26 entry. Joe 0804: "06:30 was my poor eyes ... build only the causal. our codebase
    is not at all lookahead-friendly". An s6x-cross anchor variant was written and deleted unbuilt.
    READ-TIME KNOBS (see sweep_s46_div.py) - VOTESET, VOTE_MIN, SLOPE_FLOOR, PM_VOTE.

TWO TABLES
    s46_div    one row per (entry, anchor, mult, guard, line) - the raw divergence geometry
    s46_flip   one row per entry - the as-is trade AND the flipped trade, both scored off s46_px with
               the same s6 exit rule (a flipped side takes the next OPPOSITE-direction s6 exit)

READS THE ATOMS + ONE JIG PASS. s46_run / s46_exit / s46_px supply the population, the exits and the
price; the jig supplies the 3 Mage vote lines, s6x and the exit s6Mage. r and m come from the rpl
ladder (L0). Nothing about entry or exit logic is re-derived here.

    python3 build_s46_div.py [--mult 5,10,...] [--guard 0,12,24,48] [--from 2026-05-18]
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

U = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

TF_MAX   = 6                              # highest TF in the voting group, minutes - Joe: "eg 25 x 6"
BAR_S    = 5                              # the 5 s grid
BPM      = 60 // BAR_S                    # 12 bars per minute
MULTS    = (5, 10, 15, 20, 25, 30, 40, 50, 75, 100)
GUARDS   = (0, 12, 24, 48)                # bars = 0 / 60 / 120 / 240 s
MAGE_MULT = 0.70                          # Joe: "use s4Mage" -> the vote Mage family is s4Mage's config
EXIT_LB, EXIT_LINE, EXIT_WOB = 72, 's6x', 3      # the live s6 exit: 6 min look-back, cross held 3 bars

DDL_DIV = '''CREATE TABLE IF NOT EXISTS s46_div (
    dv_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    dv_entry_ms BIGINT, dv_entry_utc VARCHAR(20), dv_dr TINYINT,
    dv_mult SMALLINT, dv_guard SMALLINT, dv_line VARCHAR(8),
    dv_float_ms BIGINT, dv_float_val DOUBLE, dv_pxs_ms BIGINT, dv_pxs_val DOUBLE,
    dv_anchor_val DOUBLE, dv_anchor_px DOUBLE,
    dv_line_slope DOUBLE, dv_price_slope DOUBLE,
    UNIQUE KEY (dv_entry_ms, dv_mult, dv_guard, dv_line),
    KEY (dv_mult), KEY (dv_guard), KEY (dv_line)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

DDL_FLIP = '''CREATE TABLE IF NOT EXISTS s46_flip (
    fl_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    fl_entry_ms BIGINT, fl_entry_utc VARCHAR(20), fl_dr TINYINT, fl_side VARCHAR(2),
    fl_mae DOUBLE, fl_mfe DOUBLE, fl_ret DOUBLE, fl_exit_ms BIGINT, fl_exit_utc VARCHAR(20),
    fl_f_mae DOUBLE, fl_f_mfe DOUBLE, fl_f_ret DOUBLE, fl_f_exit_ms BIGINT, fl_f_exit_utc VARCHAR(20),
    fl_ib_bars INT, fl_s1hold INT, fl_s2m_ok TINYINT,
    UNIQUE KEY (fl_entry_ms), KEY (fl_dr)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def derive(arr, px, a_i, bars, guard, bear):
    """floater = the line extreme; the pxs extreme sits AFTER it and before the anchor.
    Joe: "it's important that the highest line value is before the lowest pxs".
    Returns (floater_idx, pxs_idx) or None when the window cannot hold the geometry."""
    s = max(0, a_i - bars)
    e = a_i - guard                                    # anchor bar excluded, plus the guard band
    if e - s < 3:
        return None
    seg = arr[s:e]
    if not np.isfinite(seg).any():
        return None
    f_i = s + (int(np.nanargmax(seg)) if bear else int(np.nanargmin(seg)))
    if f_i >= a_i - 1:                                 # need at least one bar AFTER the floater
        return None
    ps = px[f_i + 1:a_i]                               # pxs search is NOT guarded - see module docstring
    if not np.isfinite(ps).any():
        return None
    p_i = f_i + 1 + (int(np.nanargmin(ps)) if bear else int(np.nanargmax(ps)))
    return f_i, p_i


def score(pv, a, b, sgn):
    """MAE / MFE / ret in %, signed by the trade direction. a = entry idx, b = exit idx."""
    p0 = pv[a]; seg = pv[a + 1:b + 1]
    if not len(seg) or not np.isfinite(p0) or p0 == 0:
        return None
    worst = seg.min() if sgn > 0 else seg.max()
    best = seg.max() if sgn > 0 else seg.min()
    return (float(abs(min(0.0, sgn * (worst - p0) / p0 * 100))),
            float(max(0.0, sgn * (best - p0) / p0 * 100)),
            float(sgn * (pv[b] - p0) / p0 * 100))


DISABLED = ('build_s46_div is DISABLED (Joe 0804: "disable, but don\'t remove, the divergence code").\n'
            'The mechanic is falsified - see the banner in the module docstring. s46_div and s46_flip\n'
            'are retained and readable. Pass --enable to rebuild them anyway.')


def main(argv):
    if '--enable' not in argv:
        raise SystemExit(DISABLED)
    g = lambda f, d: (argv[argv.index(f) + 1] if f in argv else d)
    mults = tuple(int(x) for x in g('--mult', ','.join(str(m) for m in MULTS)).split(','))
    guards = tuple(int(x) for x in g('--guard', ','.join(str(m) for m in GUARDS)).split(','))

    import optimus9.orchestration.rpl_walk as R
    from optimus9.analysis.jig import Jig, bbline, _Causal
    from optimus9.compute.indicator_computer import IndicatorComputer as IC

    L = R.L0; ts = np.asarray(L['ts'], np.int64); n = len(ts); E = L['E']

    d = DatabaseManager(**get_db_config()); d.connect()
    PX = d.execute('SELECT px_ms,px_v FROM s46_px ORDER BY px_ms', fetch=True)
    pm = np.array([r['px_ms'] for r in PX], np.int64)
    pv = np.array([r['px_v'] for r in PX], float)
    EX = d.execute('''SELECT sx_ms,sx_dir FROM s46_exit WHERE sx_line=%s AND sx_lb_min<=%s
                      AND sx_run_bars>=%s ORDER BY sx_ms''', (EXIT_LINE, EXIT_LB, EXIT_WOB), fetch=True)
    SHIFT = (EXIT_WOB - 1) * 5000
    ex = {1: np.array(sorted(r['sx_ms'] + SHIFT for r in EX if r['sx_dir'] == 1), np.int64),
          -1: np.array(sorted(r['sx_ms'] + SHIFT for r in EX if r['sx_dir'] == -1), np.int64)}
    RUN = d.execute('''SELECT sr_ms,sr_side,sr_dr,sr_ib_bars,sr_s1hold,sr_mm2 FROM s46_run
                       WHERE sr_ib_bars>24 AND sr_s1hold>24 ORDER BY sr_ms''', fetch=True)
    print('population %d gated runs (item 5 ib>24 bars, item 14 s1hold>24 bars)' % len(RUN))

    # --- one jig pass: the 3 Mage vote lines, s6x and the exit s6Mage -----------------------------
    T0 = int(dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc).timestamp() * 1000)
    ovr = {}
    ovr.update(bbline('x6', 6.0, length=5, mult=0.35, src='close'))       # s6x
    ovr.update(bbline('m6', 6.0, length=37, mult=0.90, src='close'))      # s6Mage, the EXIT config
    for tf in (4, 5, 6):
        ovr.update(bbline('MV%d' % tf, float(tf), length=37, mult=MAGE_MULT, src='close'))
    hrs = int((int(ts[-1]) + 5000 - T0) / 3600000) + 2
    with Jig(int(ts[-1]) + 5000, hours=hrs, warmup=180, overrides=ovr) as j:
        t2 = np.asarray(j.ts, np.int64); base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        srcv = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
        p_ = np.full(len(srcv), np.nan); p_[ei] = IC.dema(srcv[ei], int(R.PXS_CFG['len']))
        f = np.isfinite(p_); ixf = np.where(f, np.arange(len(p_)), 0); np.maximum.accumulate(ixf, out=ixf)
        p_ = p_[ixf]; p_[:int(np.argmax(f))] = p_[int(np.argmax(f))]
        X6_ = np.asarray(j.W.line('x6'), float); M6_ = np.asarray(j.W.line('m6'), float)
        MG_ = {tf: np.asarray(j.W.line('MV%d' % tf), float) for tf in (4, 5, 6)}
    off = int(np.searchsorted(ts, int(t2[0]))); kk = min(len(t2), n - off)
    lift = lambda a: np.concatenate([np.full(off, np.nan), a[:kk], np.full(n - off - kk, np.nan)])
    px = lift(p_); s6x = lift(X6_); s6M = lift(M6_)
    MG = {tf: lift(MG_[tf]) for tf in (4, 5, 6)}

    LINES = [('s4Mage', MG[4]), ('s5Mage', MG[5]), ('s6Mage', MG[6]),
             ('s4r', np.asarray(E[4]['r'], float)), ('s5r', np.asarray(E[5]['r'], float)),
             ('s6r', np.asarray(E[6]['r'], float)),
             ('s4m', np.asarray(E[4]['m'], float)), ('s5m', np.asarray(E[5]['m'], float)),
             ('s6m', np.asarray(E[6]['m'], float))]

    # --- diagnostic only: Joe 0803 asked "s6x x s6Mage crosses fire roughly every 2 minutes / are
    # they debounced?". Not used as an anchor - the anchor is the entry bar. ------------------------
    C = _Causal(None); dd = s6x - s6M
    xb = np.flatnonzero(_edge(C.cross_wob(dd, 0.0, 1, 1)) | _edge(C.cross_wob(dd, 0.0, -1, 1)))
    gaps = np.diff(ts[xb]) / 1000.0
    print('s6x x s6Mage crosses %d over the tape   gap median %.0f s  mean %.0f s  min %.0f s'
          % (len(xb), np.median(gaps), gaps.mean(), gaps.min()))

    # --- per entry: score the as-is trade and the flipped trade -----------------------------------
    fl_rows = []; ent = []
    for r in RUN:
        t = int(r['sr_ms']); sgn = int(r['sr_dr'])
        a_px = int(np.searchsorted(pm, t)); a_i = int(np.searchsorted(ts, t))
        if a_px >= len(pm) or pm[a_px] != t or a_i >= n or ts[a_i] != t:
            continue
        out = {}
        for s in (sgn, -sgn):
            nx = ex[s][ex[s] > t]
            if not len(nx):
                out[s] = None; continue
            b = int(np.searchsorted(pm, int(nx[0])))
            out[s] = None if (b >= len(pm) or pm[b] != int(nx[0])) else (score(pv, a_px, b, s), int(nx[0]))
        if out[sgn] is None or out[sgn][0] is None or out[-sgn] is None or out[-sgn][0] is None:
            continue
        (ma, mf, rt), xm = out[sgn]; (fa, ff, ft), fx = out[-sgn]
        s2 = r['sr_mm2']
        ok = None if s2 is None else int((s2 > 50) if sgn > 0 else (s2 < 50))
        fl_rows.append((t, U(t), sgn, r['sr_side'], ma, mf, rt, xm, U(xm),
                        fa, ff, ft, fx, U(fx), int(r['sr_ib_bars']), int(r['sr_s1hold']), ok))
        ent.append((t, a_i, sgn))
    print('scored %d entries both ways (as-is + flipped, same s6 exit rule)' % len(ent))

    # --- the divergence grid ----------------------------------------------------------------------
    dv_rows = []
    for t, a_i, sgn in ent:
        bear = sgn > 0                                  # LONG entry is contradicted by a BEAR divergence
        for M in mults:
            bars = int(M * TF_MAX * BPM)
            for G in guards:
                for nm, arr in LINES:
                    got = derive(arr, px, a_i, bars, G, bear)
                    if not got:
                        continue
                    f_i, p_i = got
                    ls = arr[a_i] - arr[f_i]; ps = px[a_i] - px[f_i]
                    if not (np.isfinite(ls) and np.isfinite(ps)):
                        continue
                    dv_rows.append((t, U(t), sgn, M, G, nm,
                                    int(ts[f_i]), float(arr[f_i]), int(ts[p_i]), float(px[p_i]),
                                    float(arr[a_i]), float(px[a_i]), float(ls), float(ps)))

    d.execute(DDL_FLIP); d.execute('DELETE FROM s46_flip')
    d.executemany('INSERT INTO s46_flip (fl_entry_ms,fl_entry_utc,fl_dr,fl_side,fl_mae,fl_mfe,fl_ret,'
                  'fl_exit_ms,fl_exit_utc,fl_f_mae,fl_f_mfe,fl_f_ret,fl_f_exit_ms,fl_f_exit_utc,'
                  'fl_ib_bars,fl_s1hold,fl_s2m_ok) VALUES (%s)' % ','.join(['%s'] * 17),
                  fl_rows, chunk=2000)
    d.execute(DDL_DIV); d.execute('DELETE FROM s46_div')
    d.executemany('INSERT INTO s46_div (dv_entry_ms,dv_entry_utc,dv_dr,dv_mult,dv_guard,dv_line,'
                  'dv_float_ms,dv_float_val,dv_pxs_ms,dv_pxs_val,dv_anchor_val,dv_anchor_px,'
                  'dv_line_slope,dv_price_slope) VALUES (%s)'
                  % ','.join(['%s'] * 14), dv_rows, chunk=4000)
    d.disconnect()
    ma = np.array([r[4] for r in fl_rows]); fa = np.array([r[9] for r in fl_rows])
    print('s46_flip %d rows   MAE as-is mean %.3f median %.3f max %.3f'
          % (len(fl_rows), ma.mean(), np.median(ma), ma.max()))
    print('                   MAE flip  mean %.3f median %.3f max %.3f'
          % (fa.mean(), np.median(fa), fa.max()))
    print('s46_div  %d rows   mult %s  guard %s  lines %d   anchor = the ENTRY BAR (causal)'
          % (len(dv_rows), mults, guards, len(LINES)))


def _edge(b):
    b = np.asarray(b, bool)
    return b & ~np.r_[False, b[:-1]]


if __name__ == '__main__':
    main(sys.argv[1:])
