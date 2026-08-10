"""rsd_s4_24h — run rsd against the s4 swings over the LAST 24 HOURS. Joe 0802 21:17.

    Joe: "let's test the history theory: use rsd to predict the s4 swings, for the last 24 hours"

WHY A SECOND SCRIPT AND NOT build_rsd.py
  build_rsd.py cannot reach the last 24 h, and running it with a moved window would destroy Joe's result.
  1. rpl_walk's tape ENDS 08-01 00:00:00 (R.end_ms). The last 24 h is 08-01 21:20 -> 08-02 21:20 — no overlap.
  2. build_rsd.py:104 sources lines through cache_jig_perline -> .rpl_cache, the path task #42 flags as
     contaminated: cached lines covering 04-28 -> 05-07 were built on klines deleted 0802, and _line_key
     carries no fingerprint of the underlying data.
  3. build_rsd.py:148 does DROP TABLE IF EXISTS rpl_rsd. Its window (07-30 -> 08-01) is Joe's.
  So: lines come from Jig -> bias_machine.BiasWindow -> BLDetect._setup(end), a DIRECT kline_collection
  read with no disk cache (verified, rpl_learn ln_pk 29). Output goes to rpl_rsd_24h, a NEW table.

WHAT IS COPIED VERBATIM FROM build_rsd.py — every rsd knob is Joe's, none are re-derived here
  RUNGS   rsdM5 / rsdM15 / rsdM30 / rsdM1 / rsdM2 = bb 37|0.7|close at TF 5/60, 0.25, 0.5, 1.0, 2.0 min
  SIGNAL  s4Mage (rsdM4 = bb 37|0.7|close @ TF 4 min) crossing INTO OOB at bar z, fires at z + 48 bars
          = z + 240 s. DWELL = 48. Causal — the signal bar is 240 s AFTER the cross, never before.
  DIR     the side s4Mage breached. hi -> SHORT, lo -> LONG (Joe: "the side s4M breaches on is the
          gauranteed bias direction")
  PAIRS   fastest vs next-slower, read AT the signal bar: p0 5s|15s, p1 15s|30s, p2 30s|1m, p3 1m|2m
  READING both banked — `lastoob` (side of the most recent OOB breach at/before the bar) and
          `mid` (sign(M - 50)). A rung inside its band has no side under the mechanic, so neither is assumed
  SCORE   swing_detect.find_pivots(pxs, pct=1.0). Joe: "swing detect 1"

"THE s4 SWINGS" — the reading taken, stated not inferred
  The swing being predicted is the swing_detect 1% pivot in pxs, which is the scorer Joe named for rsd.
  Not s4Mage's own OOB->IB oscillation. Each signal is scored to the NEXT confirmed pivot after it.

WINDOW. The last 24 h ending at the latest kline. Signals are filtered to that window; the LINES and the
pivot walk are built over 24 h + 24 h warmup so nothing at the window's start is reading a warming line.

CAVEAT, INHERENT. find_pivots appends the final running extreme as PROVISIONAL. Signals close to the
right edge resolve against a pivot that is not yet confirmed, or against none at all. Both are reported
as their own row count rather than dropped.

    python3 rsd_s4_24h.py              # bank rpl_rsd_24h + print the readout
    python3 rsd_s4_24h.py --hours 48   # widen the measurement window
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

DWELL = 48                                  # bars = 240 s. Joe 0802: "s4M cross oob + 240s"
PCT = 1.0                                   # Joe 0802: "swing detect 1"
RUNGS = [('rsdM5', 5.0 / 60), ('rsdM15', 0.25), ('rsdM30', 0.5), ('rsdM1', 1.0), ('rsdM2', 2.0)]
PAIRS = [(0, 1), (1, 2), (2, 3), (3, 4)]    # faster vs next-slower
WARMUP_H = 24

DDL = '''CREATE TABLE IF NOT EXISTS rpl_rsd_24h (
    rs_pk BIGINT AUTO_INCREMENT PRIMARY KEY, rs_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    rs_cross_ms BIGINT, rs_cross_utc VARCHAR(20),
    rs_sig_ms   BIGINT, rs_sig_utc   VARCHAR(20),
    rs_side VARCHAR(2), rs_dir VARCHAR(5),
    rs_sig_px DOUBLE,
    rs_still_oob TINYINT,
    rs_lastoob_p0 TINYINT, rs_lastoob_p1 TINYINT, rs_lastoob_p2 TINYINT, rs_lastoob_p3 TINYINT,
    rs_lastoob_n  TINYINT,
    rs_mid_p0 TINYINT, rs_mid_p1 TINYINT, rs_mid_p2 TINYINT, rs_mid_p3 TINYINT,
    rs_mid_n  TINYINT,
    rs_piv_ms BIGINT, rs_piv_utc VARCHAR(20), rs_piv_kind VARCHAR(1),
    rs_piv_bars INT, rs_piv_min DOUBLE,
    rs_move_pct DOUBLE, rs_mae_pct DOUBLE,
    rs_provisional TINYINT,                            -- pivot is find_pivots' unconfirmed final extreme
    KEY (rs_sig_ms), KEY (rs_side), KEY (rs_lastoob_n), KEY (rs_mid_n), KEY (rs_still_oob))'''


def _side_lastoob(v, hi, lo):
    """+1 / -1 / 0 per bar: the side of the most recent OOB breach at or before this bar. Causal.
    Verbatim from build_rsd.py:84-92."""
    s = np.where(v >= hi, 1, np.where(v <= lo, -1, 0)).astype(np.int8)
    idx = np.arange(len(s))
    last = np.maximum.accumulate(np.where(s != 0, idx, -1))
    out = np.zeros(len(s), np.int8)
    m = last >= 0
    out[m] = s[last[m]]
    return out


def med(v):
    v = [x for x in v if x is not None and np.isfinite(x)]
    return float(np.median(v)) if v else float('nan')


def main(argv):
    hours = int(argv[argv.index('--hours') + 1]) if '--hours' in argv else 24
    u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    W0 = end_ms - hours * 3600000
    HI, LO = R.HI, R.LO

    ovr = {}
    ovr.update(bbline('rsdM4', 4, length=37, mult=0.7, src='close'))       # the signal producer
    for nm, tf in RUNGS:
        ovr.update(bbline(nm, tf, length=37, mult=0.7, src='close'))

    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=WARMUP_H, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan)
        px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        if fin.any():
            ix = np.where(fin, np.arange(len(px)), 0)
            np.maximum.accumulate(ix, out=ix)
            px = px[ix]
            px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        M4 = np.asarray(j.W.line('rsdM4'), float)
        LAST = {nm: _side_lastoob(np.asarray(j.W.line(nm), float), HI, LO) for nm, _ in RUNGS}
        MID = {nm: np.sign(np.asarray(j.W.line(nm), float) - 50.0).astype(np.int8) for nm, _ in RUNGS}
    n = len(ts)
    print('jig build %.1f s   bars %d   HI/LO %g/%g   DWELL %d bars = %d s   swing_detect pct %.1f'
          % (time.time() - t0, n, HI, LO, DWELL, DWELL * 5, PCT), flush=True)
    print('built  %s -> %s  (%d h + %d h warmup)' % (u(ts[0]), u(ts[-1]), hours, WARMUP_H))
    print('window %s -> %s  (the last %d h)' % (u(W0), u(end_ms), hours))

    piv = find_pivots(px, pct=PCT)
    pv_i = np.array([p[0] for p in piv], int)
    pv_k = [p[1] for p in piv]
    in_win = int(((ts[pv_i] >= W0) & (ts[pv_i] <= end_ms)).sum()) if len(pv_i) else 0
    last_pv = int(pv_i[-1]) if len(pv_i) else -1          # find_pivots' provisional final extreme
    print('swing_detect pct=%.1f -> %d pivots over the built span, %d inside the window'
          % (PCT, len(piv), in_win))

    o = (M4 >= HI) | (M4 <= LO)
    rise = np.flatnonzero(o & ~np.r_[False, o[:-1]])
    ROWS = []
    for z in rise:
        z = int(z)
        sb = z + DWELL
        if sb >= n or not (W0 <= ts[sb] <= end_ms):
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
            pvc = (int(ts[pb]), u(ts[pb]), kind, pb - sb, (int(ts[pb]) - int(ts[sb])) / 60000.0,
                   move, mae, int(pb == last_pv))
        else:
            pvc = (None, None, None, None, None, None, None, None)
        ROWS.append((int(ts[z]), u(ts[z]), int(ts[sb]), u(ts[sb]), side,
                     'SHORT' if side == 'hi' else 'LONG', float(px[sb]), int(bool(o[sb])),
                     lo_[0], lo_[1], lo_[2], lo_[3], int(sum(lo_)),
                     mi_[0], mi_[1], mi_[2], mi_[3], int(sum(mi_))) + pvc)

    d.execute(DDL)
    d.execute('DELETE FROM rpl_rsd_24h')                 # this table is THIS script's only; rpl_rsd untouched
    if ROWS:
        d.executemany('INSERT INTO rpl_rsd_24h (rs_cross_ms,rs_cross_utc,rs_sig_ms,rs_sig_utc,rs_side,rs_dir,'
                      'rs_sig_px,rs_still_oob,rs_lastoob_p0,rs_lastoob_p1,rs_lastoob_p2,rs_lastoob_p3,'
                      'rs_lastoob_n,rs_mid_p0,rs_mid_p1,rs_mid_p2,rs_mid_p3,rs_mid_n,rs_piv_ms,rs_piv_utc,'
                      'rs_piv_kind,rs_piv_bars,rs_piv_min,rs_move_pct,rs_mae_pct,rs_provisional) VALUES ('
                      + ','.join(['%s'] * 26) + ')', ROWS)
    d.disconnect()
    report(ROWS)
    return ROWS


def report(ROWS):
    I = dict(side=4, still=7, lo=12, mi=17, bars=21, mins=22, move=23, mae=24, prov=25)
    print('')
    print('SIGNALS  %d  (s4Mage crossing into OOB, +%d bars = %d s, inside the window)'
          % (len(ROWS), DWELL, DWELL * 5))
    if not ROWS:
        print('  none — no s4Mage OOB crossing produced a signal bar inside the window')
        return
    print('  SHORT %d / LONG %d   still OOB at the signal bar: %d   no pivot after: %d   provisional pivot: %d'
          % (sum(1 for r in ROWS if r[I['side']] == 'hi'), sum(1 for r in ROWS if r[I['side']] == 'lo'),
             sum(r[I['still']] for r in ROWS),
             sum(1 for r in ROWS if r[I['move']] is None),
             sum(1 for r in ROWS if r[I['prov']])))

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
