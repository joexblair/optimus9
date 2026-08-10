"""build_s46_window — the working window's trades, banked to a table. Joe 0803 03:10.

    Joe: "drop our current window into a db table, using these columns
      #  entry utc  side  MAE  MFE  ret  exit utc"

GATES 5 + 14 ARE BAKED IN (Joe 0803: "bake 5+14 in"). They are conditions now, not columns:
    item 5   sr_ib_bars > 24 bars = 120 s   the in-bounds stretch before the excursion
             (`retest_min_ib_sec` = 120, rpl_config baseline)
    item 14  sr_s1hold > 24 bars = 120 s    s1Mage (bb 37|0.83|close @TF1) held within 15 board points
             of the breach boundary. Joe 0802: "require s1Mage to have been loosely/fuzzy lo oob for
             > 2 minutes"
    item 13 (ALT) is NOT applied - measured vacuous, passing 13,622 of 13,622 runs, because with every
    run entry-eligible the previous run is nearly always the other side or has s4Mage crossing 50
    between. It stays a column so the fact stays visible.

CONFIG - the sweep's only defensible setting (wob sweep, step 2, 1 -> 958):
    ENTRY   wob 1 = the boundary cross bar itself. Joe 0803 set the wob to zero; cross_wob clamps to
            max(1, n), so 0 and 1 are the same event - the run's FIRST out-of-bounds bar. Causal: with
            no dwell filter nothing about the run's future is read.
            Every second bar from 10 s to 17 min measured flat to negative; wob 1 is the only setting
            with a large population and a block-t positive in both halves (+1.24, IS +0.41 / OOS +1.44).
    EXIT    s6x (bb 5|0.35|close @TF6) crossing s6Mage (bb 37|0.90|close @TF6), gated by seen_within
            (s6x OOB on the breach side, 72 bars = 6 min). s6Mage's own level is NOT tested.
    EXITWOB 3 bars = 15 s (Joe 0803: "3 is good"). The cross must HOLD 3 consecutive bars; the exit is
            the 3rd. Undebounced (wob 1) fired on a single 5 s bar - on 07-29 trade #1 that exited at
            02:12:05 while s6x was still 8.5 points BELOW s6Mage. wob 3 moves it to 02:19:00, the first
            bar s6x is genuinely above the band.
            Derivable, not rebuilt: s46_exit stores sx_run_bars, so exit at wob n = sx_ms + (n-1) bars
            for runs with sx_run_bars >= n.
    GATES   items 5 and 14, applied. s2m (item 6) and ALT (item 13) stay columns, not applied.

COLUMNS - Joe's seven, plus the two gate flags so any subset is a WHERE clause:
    sw_n, sw_entry_utc, sw_side, sw_mae, sw_mfe, sw_ret, sw_exit_utc
    sw_s2m_ok   1 when s2m (bb 6|0.45|close @TF2) is on the trade's own side of 50
                Joe 0803: "if s4M is hi oob, s2m must be >50, inverse for a bearish s4M excursion"
    sw_ib_bars  in-bounds bars before this run, so "> 24 bars = 120 s" stays queryable

READS THE ATOMS, BUILDS NOTHING. s46_run + s46_exit + s46_px only - no jig, no line rebuild.

    python3 build_s46_window.py [--from 2026-07-29] [--to 2026-07-31]
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

U = lambda m: dt.datetime.fromtimestamp(m / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
LB, XLINE, XWOB = 72, 's6x', 3   # lookback 6 min | crossing line | exit wob 3 bars = 15 s
WIN_FROM, WIN_TO = '2026-07-29', '2026-07-31'

DDL = '''CREATE TABLE IF NOT EXISTS s46_window (
    sw_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    sw_n INT, sw_entry_ms BIGINT, sw_entry_utc VARCHAR(20), sw_side VARCHAR(2), sw_dr TINYINT,
    sw_mae DOUBLE, sw_mfe DOUBLE, sw_ret DOUBLE,
    sw_exit_ms BIGINT, sw_exit_utc VARCHAR(20), sw_hold_bars INT,
    sw_s2m DOUBLE, sw_s2m_ok TINYINT, sw_ib_bars INT, sw_dwell_bars INT,
    sw_alt TINYINT, sw_s1hold INT,
    UNIQUE KEY (sw_entry_ms), KEY (sw_side), KEY (sw_s2m_ok), KEY (sw_ib_bars)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def main(argv):
    g = lambda f, d: (argv[argv.index(f) + 1] if f in argv else d)
    d0, d1 = g('--from', WIN_FROM), g('--to', WIN_TO)
    _ms = lambda x: int(dt.datetime(*[int(z) for z in x.split('-')],
                                    tzinfo=dt.timezone.utc).timestamp() * 1000)
    A, B = _ms(d0), _ms(d1)

    d = DatabaseManager(**get_db_config()); d.connect()
    PX = d.execute('SELECT px_ms,px_v FROM s46_px ORDER BY px_ms', fetch=True)
    pm = np.array([r['px_ms'] for r in PX], np.int64)
    pv = np.array([r['px_v'] for r in PX], float)
    E = d.execute('''SELECT sx_ms,sx_dir FROM s46_exit WHERE sx_line=%s AND sx_lb_min<=%s
                     AND sx_run_bars>=%s ORDER BY sx_ms''', (XLINE, LB, XWOB), fetch=True)
    SHIFT = (XWOB - 1) * 5000                       # confirmation bar = cross bar + (wob-1) bars
    ex = {1: np.array([r['sx_ms'] + SHIFT for r in E if r['sx_dir'] == 1], np.int64),
          -1: np.array([r['sx_ms'] + SHIFT for r in E if r['sx_dir'] == -1], np.int64)}
    RUN = d.execute('''SELECT sr_ms,sr_end_ms,sr_side,sr_dr,sr_dwell_bars,sr_ib_bars,sr_mm2,
                       sr_alt,sr_s1hold FROM s46_run
                       WHERE sr_ms>=%s AND sr_ms<%s AND sr_ib_bars>24 AND sr_s1hold>24
                       ORDER BY sr_ms''', (A, B), fetch=True)
    rows = []
    for r in RUN:
        t = int(r['sr_ms']); sgn = int(r['sr_dr'])
        a = int(np.searchsorted(pm, t))
        if a >= len(pm) or pm[a] != t:
            continue
        nx = ex[sgn][ex[sgn] > t]
        if not len(nx):
            continue
        xm = int(nx[0]); b = int(np.searchsorted(pm, xm))
        if b >= len(pm) or pm[b] != xm:
            continue
        p0 = pv[a]; seg = pv[a + 1:b + 1]
        if not len(seg):
            continue
        s2 = r['sr_mm2']
        ok = None if s2 is None else int((s2 > 50) if sgn > 0 else (s2 < 50))
        rows.append((len(rows) + 1, t, U(t), r['sr_side'], sgn,
                     float(abs(min(0.0, sgn * ((seg.min() if sgn > 0 else seg.max()) - p0) / p0 * 100))),
                     float(max(0.0, sgn * ((seg.max() if sgn > 0 else seg.min()) - p0) / p0 * 100)),
                     float(sgn * (pv[b] - p0) / p0 * 100),
                     xm, U(xm), int(b - a),
                     float(s2) if s2 is not None else None, ok,
                     int(r['sr_ib_bars']), int(r['sr_dwell_bars']),
                     int(r['sr_alt']), int(r['sr_s1hold'])))
    d.execute(DDL); d.execute('DELETE FROM s46_window')
    d.executemany('INSERT INTO s46_window (sw_n,sw_entry_ms,sw_entry_utc,sw_side,sw_dr,sw_mae,sw_mfe,'
                  'sw_ret,sw_exit_ms,sw_exit_utc,sw_hold_bars,sw_s2m,sw_s2m_ok,sw_ib_bars,'
                  'sw_dwell_bars,sw_alt,sw_s1hold) VALUES (%s)'
                  % ','.join(['%s'] * 17), rows, chunk=2000)
    d.disconnect()
    ma = np.array([r[5] for r in rows]); xm = set(r[8] for r in rows)
    print('s46_window %d rows, %d exits, %.2f n/exit   %s -> %s   exit %s wob %d lb %d   gates 5+14'
          % (len(rows), len(xm), len(rows) / max(1, len(xm)), d0, d1, XLINE, XWOB, LB))
    print('  MAE mean %.3f  median %.3f  max %.3f' % (ma.mean(), np.median(ma), ma.max()))


if __name__ == '__main__':
    main(sys.argv[1:])
