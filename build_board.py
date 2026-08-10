"""build_board — the LIVE BOARD writer. One job: bank every line value, every 5 s, to `rpl_board`.

WHY THIS EXISTS (Joe 0803):
  build_rpl_jig.py was doing two unrelated jobs in one process — banking the board AND running exhv2's
  chain as a causality test. Every one of the 65 realtime trading predictions selected its board out of
  rpl_jig heartbeat rows, so the trading work could not proceed without the causal test running. Joe:
  "the rpl_jig table doesn't belong in the realtime trading". He chose OPTION A — a separate process.

WHAT IT DOES NOT DO — deliberately, SRP:
  - no delegate / walk / hop / anchor / confirm / exit. That is the jig's job
  - no OOB flags, no momo, no GATHER, no r-pred. All DERIVED, all belong to the reader. A board writer
    that interprets is a board writer with an opinion.
  - one exception: bd_close, the raw close, because pxs is a DEMA of it.

WHY THE SPECS ARE DUPLICATED HERE AND NOT IMPORTED (measured 0803, not assumed):
  `import build_rpl_jig` to reach its LINES dict drags in build_exhv2 -> build_exhaust -> build_rpl_6of9
  -> build_past50. Measured: ~3 min startup and 12.4 GB transient RSS on a 23 GB box, alongside a jig
  already holding 400 MB. That defeats the isolation Joe asked for. The 33 specs are restated below,
  copied verbatim from build_rpl_jig.py:61-117, WHICH REMAINS THE SOURCE OF TRUTH.
    python3 build_board.py --verify     <- does the expensive import ONCE and asserts the sets match.
                                           Run it after any change to the jig's line set. Not per start.

COLUMN NAMING — the collision that bit on the first launch:
  A naive 'bd_' + name.lower() maps jm15 (s15m, bb 6|0.45) and jM15 (s15M, bb 37|0.7) to the same
  column, and MySQL column names are CASE-INSENSITIVE, so the DDL failed with 1060 Duplicate column.
  COL below is EXPLICIT for that reason, and _assert_cols() fails loudly if it ever stops covering
  LINE_SPECS or starts producing duplicates.

    python3 build_board.py [--hours 24] [--verify]
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline, kline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

BAR_MS = 5000
WIN_HOURS, WIN_WARMUP = 24, 24                 # rolling window: 3 days. Same as build_rpl_jig.

# --- THE 33 LINE SPECS. Verbatim from build_rpl_jig.py:61-117. That file is the source of truth. ---
LINES = {}
LINES.update(bbline('jM4',   4,        length=37, mult=0.7,  src='close'))   # s4Mage
LINES.update(bbline('jx15',  15,       length=4,  mult=0.37, src='close'))   # s15x
LINES.update(bbline('jm15',  15,       length=6,  mult=0.45, src='close'))   # s15m
LINES.update(bbline('jg15x', 0.25,     length=5,  mult=0.37, src='close'))   # gcs15x
LINES.update(bbline('jg15m', 0.25,     length=6,  mult=0.45, src='close'))   # gcs15m
LINES.update(kline ('jr15',  15, k_len=10, rsi=4, stc=11,    src='close'))   # s15r
LINES.update(kline ('jr22',  22, k_len=10, rsi=4, stc=11,    src='close'))   # s22r
LINES.update(kline ('jr4',   4,  k_len=7,  rsi=6, stc=11,    src='close'))   # s4r
LINES.update(bbline('jm4',   4,        length=6,  mult=0.45, src='close'))   # s4m
LINES.update(bbline('jx4',   4,        length=4,  mult=0.37, src='close'))   # s4x
LINES.update(bbline('jM15',  15,       length=37, mult=0.7,  src='close'))   # s15M
LINES.update(bbline('jx22',  22,       length=4,  mult=0.37, src='close'))   # s22x
LINES.update(bbline('jm22',  22,       length=6,  mult=0.45, src='close'))   # s22m
LINES.update(bbline('jM22',  22,       length=37, mult=0.7,  src='close'))   # s22M
LINES.update(R._mk('js1r',  1.0, R.LN['r']))                                 # s1r
LINES.update(R._mk('js30r', 0.5, R.LN['r']))                                 # s30r
SMALL_TF = [('g5', 5.0 / 60), ('g15', 0.25), ('s30', 0.5), ('s1', 1.0)]      # Joe's GATHER set: r/m/x each
for _n, _t in SMALL_TF:
    for _k in ('r', 'm', 'x'):
        LINES.update(R._mk('j%s%s' % (_n, _k), _t, R.LN[_k]))
HTF_MAGE = [('jH30', 30.0), ('jH45', 45.0), ('jH60', 60.0), ('jH90', 90.0)]  # Joe's HTF diagnostic set
for _n, _t in HTF_MAGE:
    LINES.update(bbline(_n, _t, length=37, mult=0.7, src='close'))
MAGES = [('jMg5', 5.0 / 60), ('jMg15', 0.25), ('jMg30', 0.5), ('jMg1', 1.0), ('jMg2', 2.0)]
for _n, _t in MAGES:                                                          # the rsd set, mult 0.7
    LINES.update(bbline(_n, _t, length=37, mult=0.7, src='close'))

# --- EXPLICIT column names. Uppercase M = Mage, so it becomes 'mage' to avoid the case-insensitive
#     collision with the lowercase m (the bb 6|0.45 line). ---
COL = {
    'jM4': 'bd_mage4',   'jm4': 'bd_m4',    'jx4': 'bd_x4',    'jr4': 'bd_r4',
    'jM15': 'bd_mage15', 'jm15': 'bd_m15',  'jx15': 'bd_x15',  'jr15': 'bd_r15',
    'jM22': 'bd_mage22', 'jm22': 'bd_m22',  'jx22': 'bd_x22',  'jr22': 'bd_r22',
    'jg15x': 'bd_g15x',  'jg15m': 'bd_g15m',
    'js1r': 'bd_s1r',    'js30r': 'bd_s30r',
    'jg5r': 'bd_g5r',    'jg5m': 'bd_g5m',    'jg5x': 'bd_g5x',
    'jg15r': 'bd_g15r',  'jg15m2': 'bd_g15m2', 'jg15x2': 'bd_g15x2',
    'js30r2': 'bd_s30r2','js30m': 'bd_s30m',  'js30x': 'bd_s30x',
    'js1r2': 'bd_s1r2',  'js1m': 'bd_s1m',    'js1x': 'bd_s1x',
    'jH30': 'bd_h30',    'jH45': 'bd_h45',    'jH60': 'bd_h60',  'jH90': 'bd_h90',
    'jMg5': 'bd_mg5',    'jMg15': 'bd_mg15',  'jMg30': 'bd_mg30','jMg1': 'bd_mg1', 'jMg2': 'bd_mg2',
}


def _assert_cols():
    """Fail loudly, at startup, on any gap or case-insensitive duplicate."""
    miss = sorted(set(LINES) - set(COL))
    if miss:
        raise SystemExit('build_board: no column mapped for %s. Add it to COL.' % miss)
    lower = {}
    for n in LINES:
        c = COL[n].lower()
        if c in lower:
            raise SystemExit('build_board: %s and %s both map to %s (MySQL is case-insensitive).'
                             % (lower[c], n, COL[n]))
        lower[c] = n
    return sorted(COL[n] for n in LINES)


def verify():
    """One-off: does the expensive import and asserts our spec set equals the jig's."""
    import build_rpl_jig as J
    a, b = set(LINES), set(J.LINES)
    print('build_board %d specs   build_rpl_jig %d specs' % (len(a), len(b)))
    if a != b:
        print('  ONLY HERE : %s' % sorted(a - b)); print('  ONLY JIG  : %s' % sorted(b - a))
        raise SystemExit('MISMATCH - resync build_board.LINES from build_rpl_jig.py:61-117')
    diff = [n for n in a if LINES[n] != J.LINES[n]]
    if diff:
        for n in diff: print('  SPEC DIFFERS %s\n    here %r\n    jig  %r' % (n, LINES[n], J.LINES[n]))
        raise SystemExit('MISMATCH - specs differ')
    print('  MATCH - %d specs identical' % len(a))


def main(argv):
    if '--verify' in argv:
        verify(); return
    hours = float(argv[argv.index('--hours') + 1]) if '--hours' in argv else 24.0
    run_id = dt.datetime.now(dt.timezone.utc).strftime('%m%d_%H%M%S')
    PXS = R.PXS_CFG
    u = lambda ms: dt.datetime.fromtimestamp(int(ms) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
    line_cols = _assert_cols()

    ddl = ('CREATE TABLE IF NOT EXISTS rpl_board (\n'
           '  bd_pk BIGINT AUTO_INCREMENT PRIMARY KEY, bd_created DATETIME DEFAULT CURRENT_TIMESTAMP,\n'
           '  bd_run VARCHAR(20), bd_ms BIGINT, bd_utc VARCHAR(20),\n'
           '  bd_pxs DOUBLE, bd_close DOUBLE,\n'
           + ''.join('  %s DOUBLE,\n' % c for c in line_cols) +
           '  KEY (bd_run), KEY (bd_ms), UNIQUE KEY uq_bar (bd_run, bd_ms))')

    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(ddl)
    # SELF-HEALING COLUMNS: CREATE TABLE IF NOT EXISTS does not add columns to an existing table, so a
    # new line would silently 1054 every INSERT. Precedent: build_rpl_jig.py:202.
    have = {c['Field'].lower() for c in d.execute('SHOW COLUMNS FROM rpl_board', fetch=True)}
    for c in line_cols:
        if c.lower() not in have:
            d.execute('ALTER TABLE rpl_board ADD COLUMN %s DOUBLE' % c); print('  added column %s' % c)
    d.disconnect()

    cols = ['bd_run', 'bd_ms', 'bd_utc', 'bd_pxs', 'bd_close'] + line_cols
    SQL = 'INSERT IGNORE INTO rpl_board (%s) VALUES (%s)' % (','.join(cols), ','.join(['%s'] * len(cols)))
    print('%s  board run %s   %d lines   tick %ds   window %d+%dh   hours %.1f'
          % (u(time.time() * 1000), run_id, len(LINES), BAR_MS // 1000, WIN_HOURS, WIN_WARMUP, hours),
          flush=True)

    def san(v):
        # NaN SANITISER AT THE ROW BOUNDARY. The connector renders float('nan') as the bare literal
        # `nan`, which MySQL parses as a column name and kills the run. Precedent: build_rpl_jig.py.
        if v is None: return None
        v = float(v)
        return None if not np.isfinite(v) else v

    t_end = time.time() + hours * 3600.0
    d = DatabaseManager(**get_db_config()); d.connect()
    last, nrow = None, 0
    while time.time() < t_end:
        bar = (int(time.time() * 1000) // BAR_MS) * BAR_MS
        if bar == last:
            time.sleep(0.5); continue
        last = bar
        try:
            with Jig(bar, hours=WIN_HOURS, warmup=WIN_WARMUP, overrides=LINES) as j:
                ts = np.asarray(j.ts, np.int64)
                base = j.W.base
                evt = base['volume'].to_numpy(dtype=float) > 0
                src = IC.build_source(base, PXS['src'])
                ei = np.flatnonzero(evt)
                pxs = np.full(len(src), np.nan)
                pxs[ei] = IC.dema(src[ei], int(PXS['len']))
                fin = np.isfinite(pxs)
                if fin.any():                          # forward-fill onto the 5 s grid, as rpl_cache does
                    ix = np.where(fin, np.arange(len(pxs)), 0)
                    np.maximum.accumulate(ix, out=ix)
                    pxs = pxs[ix]
                    pxs[:int(np.argmax(fin))] = pxs[int(np.argmax(fin))]
                L = {n: np.asarray(j.W.line(n), float) for n in LINES}
                cl = base['close'].to_numpy(float)

            i = len(ts) - 1                            # THE CURRENT BAR. Nothing may read past it.
            if ts[i] != bar:
                i = min(int(np.searchsorted(ts, bar)), len(ts) - 1)

            row = {'bd_run': run_id, 'bd_ms': int(ts[i]), 'bd_utc': u(ts[i]),
                   'bd_pxs': san(pxs[i]), 'bd_close': san(cl[i])}
            for n in LINES:
                row[COL[n]] = san(L[n][i])
            d.execute(SQL, tuple(row[c] for c in cols))
            nrow += 1
            if nrow % 120 == 0:
                print('%s  %d rows' % (u(ts[i]), nrow), flush=True)
        except Exception as e:                         # never let one bad tick end the run
            print('%s  TICK ERROR %s: %s' % (u(bar), type(e).__name__, e), flush=True)
            try: d.disconnect()
            except Exception: pass
            d = DatabaseManager(**get_db_config()); d.connect()
        time.sleep(0.5)
    d.disconnect()
    print('%s  board run %s ended, %d rows' % (u(time.time() * 1000), run_id, nrow), flush=True)


if __name__ == '__main__':
    main(sys.argv[1:])
