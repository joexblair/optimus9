"""build_s46_momo — the momo mechanic inserted before the s6 exit. Joe 0804.

JOE'S SPEC, verbatim
    "the next thing to test is: 07-29 03:03:15  07-29 03:08:45  insert momo mechanic before exit.
     @ 0320, s15 and s22 have down momo. exit on s15x boundary,mage (race) @ 04:00"
    "curl is as important as momo, so yes include it in the calcs"
    "s15x and s22x as an exiting line can cross r, boundary or Mage"
  and from the four locked answers 0804:
    gate    EITHER s15 or s22   (at the s6 exit bar 03:08:45, s15 reads momo but s22 does not)
    timing  "Read every bar from entry; s6 exit suppressed while momo is down"
    lines   exhv2's own: x bb 4|0.37, M bb 37|0.70, r kline 10|4|11|close @TF15/TF22
    04:00   "approximate - take whichever leg fires first"

THE MECHANIC
  GATE      open at a bar when EITHER s15 or s22 returns 'momo' or 'curl' from build_exhv2.momo()
            called at dr = THE TRADE'S OWN direction. Both states are direction-aware: 'momo' needs
            the slope aligned with dr, and 'curl' returns from the |slope| < MOMO_SLOPE_MIN branch
            only after the dr-built level gate passes. 'sideways' and 'none' are not.
  SUPPRESS  while the gate is open the s6 exit cannot fire. It re-arms the moment the gate closes.
  RACE      while the gate is open the exit is the first of SIX legs - s15x and s22x, each crossing
            r, the boundary (HI 85 / LO 15), or Mage. A leg only counts at or after the bar the gate
            FIRST opened; a cross that happened before the mechanic engaged cannot close the trade.
  DIRECTION mirrors the s6 exit's own rule (build_s46.py: long closes on a DOWN cross, short on UP).
            SHORT -> all six legs are UP crosses.   LONG -> all six are DOWN crosses.

EVERY LEG IS BANKED SEPARATELY, so the race over any subset is a query and not a rebuild:
    s46_momo      one row per trade  - the gate bar, the gate source, and the two s6 exits
    s46_momo_leg  one row per (trade, candidate exit) - fire bar + MAE/MFE/ret scored to it
                    s6raw    the current strategy's exit, ungated. THE BASELINE.
                    s6gated  first s6 exit at a bar where the gate is CLOSED
                    x15r x15b x15M x22r x22b x22M    the six race legs
    the mechanic's exit = min(s6gated, chosen race subset). Pick the subset in SQL.

KNOBS
    GWOB    GATE wobble, bars. The momo/curl verdict must hold GWOB consecutive bars before the gate
            counts as open. Joe 0804: "I'm assuming you debounced the s15 and s22 lines" - it was not
            debounced at all, so this knob exists from that question. GWOB 1 = undebounced, the
            original behaviour. Swept.
    RWOB    race-leg wobble, bars. Joe left it unset; the s6 exit uses 3. Swept, default 1.
            WARNING, from the first run: MAE gets monotonically WORSE as RWOB rises (0.134 / 0.142 /
            0.149 / 0.155 at 1 / 2 / 3 / 5), i.e. the best MAE belongs to the least-confirmed cross.
            Under Joe's named trade the winning leg fires 2 bars = 10 s after entry against a 66-bar
            baseline hold. A near-instant exit has near-zero adverse excursion by construction, so an
            MAE-only ranking cannot separate a good exit from a fast one. Read hold_bars alongside.
    the momo knobs stay build_exhv2's: MOMO_WINDOW_MIN 60 min, MOMO_SAMPLES 12 @ 5 min,
    MOMO_SLOPE_MIN 1.0, MOMO_R2_MIN 0.50, CURL_ARC_MIN 4.0, LEVEL_SLACK 13.9.
    build_exhv2.momo() is CALLED, never copied - a second copy would fork those constants, which is
    exactly how MOMO_WINDOW_MIN went 5-vs-60 and CURL_ARC_MIN 0-vs-4.0 earlier in this work.

SCOPE  TF22 over the full 75-day tape does not fit in memory - the 96 h recon held 5.2 GB. --from /
       --to drive one jig pass; the default is the current working window plus margin either side.

    python3 build_s46_momo.py [--from 2026-07-29] [--to 2026-07-31] [--rwob 1,2,3,5]
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('RPL_TF_CEILING', '22')
import numpy as np
import build_exhv2 as X
from optimus9.analysis.jig import Jig, bbline, kline, _Causal
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

U = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
_ms = lambda x: int(dt.datetime(*[int(z) for z in x.split('-')], tzinfo=dt.timezone.utc).timestamp() * 1000)
HI, LO = 85.0, 15.0
TFS = (15, 22)
OPEN_STATES = ('momo', 'curl')            # Joe 0804: "curl is as important as momo"
EXIT_LB, EXIT_LINE, EXIT_WOB = 72, 's6x', 3      # the live s6 exit, unchanged
MARGIN_D = 2                              # days of jig either side of the window, for lines + resolution

DDL_T = '''CREATE TABLE IF NOT EXISTS s46_momo (
    mo_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    mo_entry_ms BIGINT, mo_entry_utc VARCHAR(20), mo_dr TINYINT, mo_side VARCHAR(2),
    mo_gate_ms BIGINT, mo_gate_utc VARCHAR(20), mo_gate_src VARCHAR(8), mo_gate_bars INT,
    mo_s6raw_ms BIGINT, mo_s6gated_ms BIGINT, mo_rwob SMALLINT, mo_gwob SMALLINT,
    UNIQUE KEY (mo_entry_ms, mo_rwob, mo_gwob), KEY (mo_dr)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

DDL_L = '''CREATE TABLE IF NOT EXISTS s46_momo_leg (
    ml_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    ml_entry_ms BIGINT, ml_entry_utc VARCHAR(20), ml_dr TINYINT, ml_rwob SMALLINT, ml_gwob SMALLINT,
    ml_leg VARCHAR(8), ml_fire_ms BIGINT, ml_fire_utc VARCHAR(20), ml_hold_bars INT,
    ml_mae DOUBLE, ml_mfe DOUBLE, ml_ret DOUBLE,
    UNIQUE KEY (ml_entry_ms, ml_rwob, ml_gwob, ml_leg), KEY (ml_leg), KEY (ml_rwob), KEY (ml_gwob)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def edge(b):
    b = np.asarray(b, bool)
    return b & ~np.r_[False, b[:-1]]


def score(pv, a, b, sgn):
    p0 = pv[a]; seg = pv[a + 1:b + 1]
    if not len(seg) or not np.isfinite(p0) or p0 == 0:
        return None
    worst = seg.min() if sgn > 0 else seg.max()
    best = seg.max() if sgn > 0 else seg.min()
    return (float(abs(min(0.0, sgn * (worst - p0) / p0 * 100))),
            float(max(0.0, sgn * (best - p0) / p0 * 100)),
            float(sgn * (pv[b] - p0) / p0 * 100))


def main(argv):
    g = lambda f, d: (argv[argv.index(f) + 1] if f in argv else d)
    d0, d1 = g('--from', '2026-07-29'), g('--to', '2026-07-31')
    rwobs = tuple(int(x) for x in g('--rwob', '1,2,3,5').split(','))
    gwobs = tuple(int(x) for x in g('--gwob', '1,3,6,12,24').split(','))
    A, B = _ms(d0), _ms(d1)
    J0 = A - MARGIN_D * 86400000
    J1 = B + MARGIN_D * 86400000

    d = DatabaseManager(**get_db_config()); d.connect()
    PX = d.execute('SELECT px_ms,px_v FROM s46_px ORDER BY px_ms', fetch=True)
    pm = np.array([r['px_ms'] for r in PX], np.int64)
    pv = np.array([r['px_v'] for r in PX], float)
    EX = d.execute('''SELECT sx_ms,sx_dir FROM s46_exit WHERE sx_line=%s AND sx_lb_min<=%s
                      AND sx_run_bars>=%s ORDER BY sx_ms''', (EXIT_LINE, EXIT_LB, EXIT_WOB), fetch=True)
    SH = (EXIT_WOB - 1) * 5000
    s6 = {1: np.array(sorted(r['sx_ms'] + SH for r in EX if r['sx_dir'] == 1), np.int64),
          -1: np.array(sorted(r['sx_ms'] + SH for r in EX if r['sx_dir'] == -1), np.int64)}
    RUN = d.execute('''SELECT sr_ms,sr_side,sr_dr FROM s46_run
                       WHERE sr_ms>=%s AND sr_ms<%s AND sr_ib_bars>24 AND sr_s1hold>24
                       ORDER BY sr_ms''', (A, B), fetch=True)
    print('population %d gated runs in %s -> %s' % (len(RUN), d0, d1))

    # --- one jig pass, exhv2's own TF15/TF22 line set -------------------------------------------
    ovr = {}
    for tf in TFS:
        for k, (_kind, sp) in X.LINE_SPEC.items():
            ovr.update(bbline('e%s%d' % (k, tf), float(tf), **sp))
        ovr.update(kline('er%d' % tf, float(tf), **X.R_SPEC[tf]))
    hrs = int((J1 - J0) / 3600000) + 2
    print('jig %s -> %s  (%d h, margin %d d)   momo win %d min, %d samples, slope_min %s, '
          'r2_min %s, curl_arc %s'
          % (U(J0), U(J1), hrs, MARGIN_D, X.MOMO_WINDOW_MIN, X.MOMO_SAMPLES, X.MOMO_SLOPE_MIN,
             X.MOMO_R2_MIN, X.CURL_ARC_MIN))
    with Jig(J1, hours=hrs, warmup=180, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        Lx = {tf: np.asarray(j.W.line('ex%d' % tf), float) for tf in TFS}
        LM = {tf: np.asarray(j.W.line('eM%d' % tf), float) for tf in TFS}
        Lr = {tf: np.asarray(j.W.line('er%d' % tf), float) for tf in TFS}
    n = len(ts)
    C = _Causal(None)

    # --- the six race legs, per direction, per wobble --------------------------------------------
    # SHORT (dr -1) closes on an UP cross; LONG (dr +1) on a DOWN cross - build_s46.py's own rule.
    LEGS = {}
    for w in rwobs:
        for tf in TFS:
            for nm, tgt in (('r', Lr[tf]), ('b', None), ('M', LM[tf])):
                for dr in (1, -1):
                    cd = -1 if dr > 0 else +1                     # cross direction
                    if nm == 'b':
                        lvl = HI if dr > 0 else LO
                        fired = C.cross_wob(Lx[tf], lvl, cd, w)
                    else:
                        fired = C.cross_wob(Lx[tf] - tgt, 0.0, cd, w)
                    LEGS[(w, 'x%d%s' % (tf, nm), dr)] = np.flatnonzero(edge(fired))

    # --- the gate, per bar, per direction. build_exhv2.momo() is CALLED, not copied. -------------
    lo_b = int(np.searchsorted(ts, A)); hi_b = n
    gate = {1: np.zeros(n, bool), -1: np.zeros(n, bool)}
    src = {1: np.zeros(n, np.int8), -1: np.zeros(n, np.int8)}     # bit 1 = s15, bit 2 = s22
    for dr in (1, -1):
        for b in range(lo_b, hi_b):
            s = 0
            for bit, tf in ((1, 15), (2, 22)):
                if X.momo(Lr[tf], dr, b)[0] in OPEN_STATES:
                    s |= bit
            if s:
                gate[dr][b] = True; src[dr][b] = s
    # GATE WOBBLE (Joe 0804: "I'm assuming you debounced the s15 and s22 lines" - it was not).
    # The raw per-bar verdict must hold GWOB consecutive bars. cross_wob on the bool at level 0.5 is
    # the jig's own run-length idiom, so this is the same producer the exits use, not a second copy.
    GATE = {(dr, w): C.cross_wob(gate[dr].astype(float), 0.5, +1, w)
            for dr in (1, -1) for w in gwobs}
    print('gate open bars (either s15 or s22 in %s):' % '/'.join(OPEN_STATES))
    for w in gwobs:
        print('   gwob %-3d = %4d s   LONG %6d of %d   SHORT %6d of %d'
              % (w, w * 5, GATE[(1, w)][lo_b:hi_b].sum(), hi_b - lo_b,
                 GATE[(-1, w)][lo_b:hi_b].sum(), hi_b - lo_b))

    SRC = {0: '-', 1: 's15', 2: 's22', 3: 'both'}
    trows, lrows = [], []
    for r in RUN:
        t = int(r['sr_ms']); dr = int(r['sr_dr'])
        a = int(np.searchsorted(ts, t)); apx = int(np.searchsorted(pm, t))
        if a >= n or ts[a] != t or apx >= len(pm) or pm[apx] != t:
            continue
        nx = s6[dr][s6[dr] > t]
        s6raw = int(nx[0]) if len(nx) else None      # the current strategy's exit. THE BASELINE.
        for gw in gwobs:
            gt = GATE[(dr, gw)]
            gi = np.flatnonzero(gt[a:])
            g0 = int(a + gi[0]) if len(gi) else None  # gate's FIRST confirmed-open bar after entry
            s6g = None                               # first s6 exit on a gate-CLOSED bar
            for m in nx:
                k = int(np.searchsorted(ts, int(m)))
                if k < n and ts[k] == int(m) and not gt[k]:
                    s6g = int(m); break
            for w in rwobs:
                cand = {'s6raw': s6raw, 's6gated': s6g}
                for tf in TFS:
                    for nm in ('r', 'b', 'M'):
                        key = 'x%d%s' % (tf, nm)
                        f = LEGS[(w, key, dr)]
                        f = f[f >= (g0 if g0 is not None else n)]
                        cand[key] = int(ts[f[0]]) if len(f) else None
                trows.append((t, U(t), dr, r['sr_side'],
                              int(ts[g0]) if g0 is not None else None,
                              U(ts[g0]) if g0 is not None else None,
                              SRC[int(src[dr][g0])] if g0 is not None else '-',
                              int(g0 - a) if g0 is not None else None,
                              s6raw, s6g, w, gw))
                for leg, m in cand.items():
                    if m is None:
                        continue
                    b = int(np.searchsorted(pm, m))
                    if b >= len(pm) or pm[b] != m:
                        continue
                    sc = score(pv, apx, b, dr)
                    if sc is None:
                        continue
                    lrows.append((t, U(t), dr, w, gw, leg, m, U(m), int(b - apx)) + sc)

    d.execute(DDL_T); d.execute(DDL_L)
    d.execute('DELETE FROM s46_momo WHERE mo_entry_ms>=%s AND mo_entry_ms<%s', (A, B))
    d.execute('DELETE FROM s46_momo_leg WHERE ml_entry_ms>=%s AND ml_entry_ms<%s', (A, B))
    d.executemany('INSERT INTO s46_momo (mo_entry_ms,mo_entry_utc,mo_dr,mo_side,mo_gate_ms,'
                  'mo_gate_utc,mo_gate_src,mo_gate_bars,mo_s6raw_ms,mo_s6gated_ms,mo_rwob,mo_gwob) '
                  'VALUES (%s)' % ','.join(['%s'] * 12), trows, chunk=2000)
    d.executemany('INSERT INTO s46_momo_leg (ml_entry_ms,ml_entry_utc,ml_dr,ml_rwob,ml_gwob,ml_leg,'
                  'ml_fire_ms,ml_fire_utc,ml_hold_bars,ml_mae,ml_mfe,ml_ret) VALUES (%s)'
                  % ','.join(['%s'] * 12), lrows, chunk=2000)
    d.disconnect()
    print('s46_momo %d rows (%d trades x %d rwob x %d gwob)   s46_momo_leg %d rows'
          % (len(trows), len(RUN), len(rwobs), len(gwobs), len(lrows)))
    base = [z for z in lrows if z[5] == 's6raw' and z[3] == rwobs[0] and z[4] == gwobs[0]]
    if base:
        m = np.array([z[9] for z in base]); h = np.array([z[8] for z in base])
        print('  baseline s6raw: %d trades, MAE mean %.3f  median %.3f  max %.3f   '
              'hold mean %.0f median %.0f bars' % (len(m), m.mean(), np.median(m), m.max(),
                                                   h.mean(), np.median(h)))


if __name__ == '__main__':
    main(sys.argv[1:])
