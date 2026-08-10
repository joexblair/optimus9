"""build_rsd — realtime swing detection (rsd). Joe 0802 named it.

THE IDEA (Joe 0802)
  MFE side detection is, stripped to mechanics, a SIDE-DISAGREEMENT test: build_exhv2._derive reads which
  side s4Mage breached (sd), which side the bias expected (wt), and flags `mf = int(sd != wt)`.
  rsd applies that same test across a faster set of Mages, with each rung tested against the NEXT SLOWER
  rung instead of against a bias. No r-pred, no bias, no exhaustion - completely standalone (Joe 0802).

  NOT the dominoes test. Dominoes scored the ORDERING of OOB->IB crossing bars across gcs15M/s30M/s1M and
  carried 1.01x against the live win flag. This scores SIDE DISAGREEMENT, which is the test that carried
  +0.905% median at 96.8% on 62 rows when run on the single s4Mage rung.

THE SET   Joe 0802: s2, s1, s30, gcs15, gcs5. mult 0.7 (Joe 0802), so the whole set shares s4Mage's flavour
  rsdM2  bb 37|0.7|close @ TF 2.0   min
  rsdM1  bb 37|0.7|close @ TF 1.0   min
  rsdM30 bb 37|0.7|close @ TF 0.5   min = 30 s
  rsdM15 bb 37|0.7|close @ TF 0.25  min = 15 s
  rsdM5  bb 37|0.7|close @ TF 5/60  min = 5 s   (the base grid - no resampling)
  every rung is FASTER than s4Mage (TF4 = 4 min), so every rung can register the disagreement earlier

THE SIGNAL   Joe 0802: "use s4M cross oob + 240s as the signal"
  s4Mage = rsdM4 = bb 37|0.7|close @ TF4, the same line exhv2 uses (build_exhv2.LINE_SPEC['M'])
  a crossing INTO OOB at bar z fires a signal at z + 48 bars = z + 240 s. Causal - no forward peek,
  unlike the `held` test which needs the 240 s to have already happened.
  DIRECTION  the side s4Mage breached. hi -> SHORT, lo -> LONG.
             Joe 0802: "the side s4M breaches on is the gauranteed bias direction"

THE READING   a rung's "side" when it is INSIDE the band is not defined by the mechanic, so BOTH are banked
  lastoob   the side of the most recent OOB breach at/before the signal bar. Mirrors `sd` semantics
  mid       sign(M - 50). Always defined, never stale

THE PAIRS   fastest vs next-slower, read AT the signal bar. Joe 0802 chose (a): the set tests against itself
  p0 5s vs 15s   p1 15s vs 30s   p2 30s vs 1m   p3 1m vs 2m
  Joe 0802 "try them all" - every pair individually AND thresholds >=1, >=2, >=3, =4

THE SCORE   Joe 0802: "swing detect 1"  -> swing_detect.find_pivots(pct=1.0).
  PRICE SERIES  pxs (event-tape px_smooth: DEMA of close over real-trade bars, forward-filled onto the 5 s
  grid). swing_detect's docstring says close-based, but the line cache does not carry close - JigCache
  exposes ts/lines/evt/pxs only - and pxs is what every return and MAE figure in this project is already
  scored on (build_dominoes_db uses R.L0['src'].pxs). Deviating from the docstring to stay consistent with
  the rest of the measurement stack. Structural choice, stated not inferred.
  TWO-STAGE (standing rule): the causal signal timestamps are banked FIRST, scored SECOND. The scorer never
  feeds back into generation.

TAPE   reuses rpl_walk's tape - no new geometry, no new cache key (Joe 0802: 07-30 to 07-31 is inside it).

    python3 build_rsd.py                 # bank rpl_rsd + print the readout
"""
import sys, os, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import bbline
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.compute.swing_detect import find_pivots
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

W0 = int(dt.datetime(2026, 7, 30, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)   # Joe 0802
W1 = int(dt.datetime(2026, 8,  1, 0, 0, tzinfo=dt.timezone.utc).timestamp() * 1000)   # exclusive
DWELL = 48                                  # bars = 240 s. Joe 0802: "s4M cross oob + 240s"
PCT = 1.0                                   # Joe 0802: "swing detect 1"
RUNGS = [('rsdM5', 5.0 / 60), ('rsdM15', 0.25), ('rsdM30', 0.5), ('rsdM1', 1.0), ('rsdM2', 2.0)]  # fastest first
PAIRS = [(0, 1), (1, 2), (2, 3), (3, 4)]    # faster vs next-slower

DDL = '''CREATE TABLE IF NOT EXISTS rpl_rsd (
    rs_pk BIGINT AUTO_INCREMENT PRIMARY KEY, rs_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    rs_cross_ms BIGINT, rs_cross_utc VARCHAR(20),      -- the s4Mage crossing INTO OOB
    rs_sig_ms   BIGINT, rs_sig_utc   VARCHAR(20),      -- crossing + 48 bars = 240 s. THE SIGNAL
    rs_side VARCHAR(2), rs_dir VARCHAR(5),             -- s4Mage breach side; hi->SHORT, lo->LONG
    rs_sig_px DOUBLE,
    rs_still_oob TINYINT,                              -- s4Mage still OOB at the signal bar
    rs_lastoob_p0 TINYINT, rs_lastoob_p1 TINYINT, rs_lastoob_p2 TINYINT, rs_lastoob_p3 TINYINT,
    rs_lastoob_n  TINYINT,                             -- how many of the 4 pairs disagree
    rs_mid_p0 TINYINT, rs_mid_p1 TINYINT, rs_mid_p2 TINYINT, rs_mid_p3 TINYINT,
    rs_mid_n  TINYINT,
    rs_piv_ms BIGINT, rs_piv_utc VARCHAR(20), rs_piv_kind VARCHAR(1),   -- next swing_detect pivot after sig
    rs_piv_bars INT, rs_piv_min DOUBLE,
    rs_move_pct DOUBLE,                                -- signed by rs_dir, signal px -> pivot px
    rs_mae_pct DOUBLE,                                 -- worst excursion against rs_dir, signal -> pivot
    KEY (rs_sig_ms), KEY (rs_side), KEY (rs_lastoob_n), KEY (rs_mid_n), KEY (rs_still_oob))'''


def _side_lastoob(v, hi, lo):
    """+1 / -1 / 0 per bar: the side of the most recent OOB breach at or before this bar. Causal."""
    s = np.where(v >= hi, 1, np.where(v <= lo, -1, 0)).astype(np.int8)
    idx = np.arange(len(s))
    last = np.maximum.accumulate(np.where(s != 0, idx, -1))
    out = np.zeros(len(s), np.int8)
    m = last >= 0
    out[m] = s[last[m]]
    return out


def main(argv):
    d = DatabaseManager(**get_db_config()); d.connect()
    HI, LO = R.HI, R.LO
    u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

    ovr = {}
    ovr.update(bbline('rsdM4', 4, length=37, mult=0.7, src='close'))       # the signal producer
    for nm, tf in RUNGS:
        ovr.update(bbline(nm, tf, length=37, mult=0.7, src='close'))
    J = cache_jig_perline(R.end_ms, R.HOURS, R.WARMUP, ovr, pxs_cfg=R.PXS_CFG)
    ts = np.asarray(J.ts, np.int64)
    n = len(ts)
    px = np.asarray(J.pxs, float)         # see the PRICE SERIES note in the docstring
    M4 = np.asarray(J.W.line('rsdM4'), float)
    LAST = {nm: _side_lastoob(np.asarray(J.W.line(nm), float), HI, LO) for nm, _ in RUNGS}
    MID = {nm: np.sign(np.asarray(J.W.line(nm), float) - 50.0).astype(np.int8) for nm, _ in RUNGS}
    print('tape   %s -> %s   n=%d' % (u(ts[0]), u(ts[-1]), n))
    print('window %s -> %s   (Joe 0802: 07-30 to 07-31)' % (u(W0), u(W1)))

    # --- swing_detect, run over the WHOLE tape then filtered: a pivot may sit outside the window ------
    piv = find_pivots(px, pct=PCT)
    pv_i = np.array([p[0] for p in piv], int)
    pv_k = [p[1] for p in piv]
    print('swing_detect pct=%.1f  ->  %d pivots over the tape, %d inside the window'
          % (PCT, len(piv), int(((ts[pv_i] >= W0) & (ts[pv_i] < W1)).sum())))

    # --- the signal: every s4Mage crossing INTO OOB, +48 bars -----------------------------------------
    o = (M4 >= HI) | (M4 <= LO)
    rise = np.flatnonzero(o & ~np.r_[False, o[:-1]])
    ROWS = []
    for z in rise:
        z = int(z)
        sb = z + DWELL
        if sb >= n or not (W0 <= ts[sb] < W1):
            continue
        side = 'hi' if M4[z] >= HI else 'lo'
        sgn = -1.0 if side == 'hi' else 1.0                      # hi breach -> SHORT
        lo_ = [int(LAST[RUNGS[a][0]][sb] != LAST[RUNGS[b][0]][sb]) for a, b in PAIRS]
        mi_ = [int(MID[RUNGS[a][0]][sb] != MID[RUNGS[b][0]][sb]) for a, b in PAIRS]
        nx = pv_i[pv_i > sb]
        if len(nx):
            pb = int(nx[0]); kind = pv_k[int(np.flatnonzero(pv_i == pb)[0])]
            seg = px[sb:pb + 1]
            move = float(sgn * (px[pb] - px[sb]) / px[sb] * 100.0)
            mae = float(((np.nanmax(seg) - px[sb]) if sgn < 0 else (px[sb] - np.nanmin(seg))) / px[sb] * 100.0)
            pvc = (int(ts[pb]), u(ts[pb]), kind, pb - sb, (int(ts[pb]) - int(ts[sb])) / 60000.0, move, mae)
        else:
            pvc = (None, None, None, None, None, None, None)
        ROWS.append((int(ts[z]), u(ts[z]), int(ts[sb]), u(ts[sb]), side,
                     'SHORT' if side == 'hi' else 'LONG', float(px[sb]), int(bool(o[sb])),
                     lo_[0], lo_[1], lo_[2], lo_[3], int(sum(lo_)),
                     mi_[0], mi_[1], mi_[2], mi_[3], int(sum(mi_))) + pvc)

    d.execute('DROP TABLE IF EXISTS rpl_rsd'); d.execute(DDL)
    d.executemany('INSERT INTO rpl_rsd (rs_cross_ms,rs_cross_utc,rs_sig_ms,rs_sig_utc,rs_side,rs_dir,'
                  'rs_sig_px,rs_still_oob,rs_lastoob_p0,rs_lastoob_p1,rs_lastoob_p2,rs_lastoob_p3,'
                  'rs_lastoob_n,rs_mid_p0,rs_mid_p1,rs_mid_p2,rs_mid_p3,rs_mid_n,rs_piv_ms,rs_piv_utc,'
                  'rs_piv_kind,rs_piv_bars,rs_piv_min,rs_move_pct,rs_mae_pct) VALUES ('
                  + ','.join(['%s'] * 25) + ')', ROWS)
    d.disconnect()
    report(ROWS)
    return ROWS


def med(v):
    v = [x for x in v if x is not None]
    return float(np.median(v)) if v else float('nan')


def report(ROWS):
    I = dict(side=4, still=7, lo=12, mi=17, bars=21, mins=22, move=23, mae=24)
    print('')
    print('SIGNALS  %d  (s4Mage crossing into OOB, +48 bars = 240 s, inside the window)' % len(ROWS))
    if not ROWS:
        return
    print('  SHORT %d / LONG %d   still OOB at the signal bar: %d'
          % (sum(1 for r in ROWS if r[I['side']] == 'hi'), sum(1 for r in ROWS if r[I['side']] == 'lo'),
             sum(r[I['still']] for r in ROWS)))

    def block(title, rows):
        m = [r[I['move']] for r in rows if r[I['move']] is not None]
        if not m:
            print('  %-26s %4d      (no pivot after the signal)' % (title, len(rows))); return
        a = [r[I['mae']] for r in rows if r[I['mae']] is not None]
        b = [r[I['mins']] for r in rows if r[I['mins']] is not None]
        print('  %-26s %4d %7.1f%% %+9.3f %+9.2f %8.3f %9.1f'
              % (title, len(rows), 100.0 * sum(1 for v in m if v > 0) / len(m),
                 med(m), sum(m), med(a), med(b)))

    for tag, base in (('lastoob', I['lo']), ('mid', I['mi'])):
        print('')
        print('READING: %s   (a rung disagrees with the NEXT SLOWER rung, read at the signal bar)' % tag)
        H = '  %-26s %4s %7s %9s %9s %8s %9s' % ('split', 'n', 'move>0', 'move med', 'move sum', 'mae med', 'min med')
        print(H); print('  ' + '-' * (len(H) - 2))
        block('ALL signals', ROWS)
        for p, nm in enumerate(('p0 5s vs 15s', 'p1 15s vs 30s', 'p2 30s vs 1m', 'p3 1m vs 2m')):
            block('%s  disagree' % nm, [r for r in ROWS if r[base - 4 + p]])
            block('%s  agree' % nm, [r for r in ROWS if not r[base - 4 + p]])
        for k in (1, 2, 3, 4):
            block('>= %d pairs disagree' % k, [r for r in ROWS if r[base] >= k])
        block('= 0 pairs disagree', [r for r in ROWS if r[base] == 0])


if __name__ == '__main__':
    main(sys.argv[1:])
