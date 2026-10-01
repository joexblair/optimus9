"""add_ws5mage_unclaimed_excursions - the ws5Mage ex-fence runs that carry no banked signal.

Joe 0930: *"if there are any ws5Mage ex-fence that don't carry a trade (ie they're missing from the
table), add that ws5Mage excursion to the db table."*

The table was one row per banked signal. It becomes one row per (signal OR unclaimed excursion),
distinguished by `wsb_kind`.

CLAIMED means a banked signal's containing run AT THAT FENCE starts on the same bar. Everything
else is unclaimed and gets a row.

NO DWELL THRESHOLD. Every excursion is stored, whatever its length, and `wsb_run{fence}_bars`
carries the bar count - filter by dwell in SQL. Joe set the arm dwell at 45 s for the mech; that is
not a reason to hide the shorter runs from the table.

THREE STRUCTURAL CHOICES, MINE, STATED
  1 `wsb_kind`  'signal' | 'excursion'. Without it the row unit is ambiguous.
  2 `wsb_fence` '15/85' | '25/75' on excursion rows, NULL on signal rows. An excursion exists AT a
    fence - the same span can be an excursion at 25/75 and not at 15/85.
  3 the unique key becomes (wsb_knobs, wsb_kind, wsb_fence, wsb_sig_ms). A 15/85 and a 25/75
    excursion can share a start bar and would collide on the old key.

AND ONE I COULD NOT MAKE CLEAN: on an excursion row `wsb_sig_utc` holds the excursion's FIRST bar,
not a signal. The column name is wrong for those rows. Joe was offered a rename and said build.

A run is split by a dr flip, same rule as the build - "oob on the dr side" has no single answer
otherwise. Span and knobs are inherited from the existing rows. Idempotent per knobs.

    python3 docs/22_go_20260921/add_ws5mage_unclaimed_excursions.py
"""
import sys, os, datetime as dt, logging
sys.path.insert(0, os.environ['CLAUDE_JOB_DIR'] + '/tmp'); sys.path.insert(0, '/home/joe/thecodes')
logging.disable(logging.CRITICAL)
import numpy as np, mechdev_rig
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE = 'ws5mage_sig_backing'
DW = 9; MID = 50.0
FENCES = (('15/85', (15.0, 85.0)), ('25/75', (25.0, 75.0)))
MS = lambda y, m, d, h=0: int(dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp() * 1000)
rig = mechdev_rig.load(expect_end_ms=MS(2026, 9, 8))
Mg = np.asarray(rig.lines['ws5']['Mage'], float)
tsa = np.asarray(rig.ts, np.int64)
U = lambda k: dt.datetime.fromtimestamp(int(rig.ts[k]) / 1000, dt.timezone.utc)
FLOOR = rig.bar('2026-08-31 00:00:00')

db = DatabaseManager(**get_db_config()); db.connect()
for col, typ in (('wsb_kind', "VARCHAR(10) NOT NULL DEFAULT 'signal'"),
                 ('wsb_fence', 'VARCHAR(8) NULL')):
    try: db.execute('ALTER TABLE %s ADD COLUMN %s %s' % (TABLE, col, typ))
    except Exception as e:
        if 'Duplicate' not in str(e): raise
try:
    db.execute('ALTER TABLE %s DROP INDEX uq_wsb' % TABLE)
    db.execute('ALTER TABLE %s ADD UNIQUE KEY uq_wsb '
               '(wsb_knobs, wsb_kind, wsb_fence, wsb_sig_ms)' % TABLE)
    print('U|unique key widened to (knobs, kind, fence, sig_ms)')
except Exception as e:
    print('U|unique key: %s' % str(e)[:80])

base = db.execute("SELECT DISTINCT wsb_knobs k FROM %s WHERE wsb_kind='signal'" % TABLE,
                  fetch=True)
KNOBS = base[0]['k']
span = db.execute("SELECT MIN(wsb_sig_ms) lo, MAX(wsb_sig_ms) hi FROM %s "
                  "WHERE wsb_kind='signal' AND wsb_knobs=%%s" % TABLE, (KNOBS,), fetch=True)[0]
D0, D1 = MS(2026, 9, 1), MS(2026, 9, 4)      # the span the signal rows were built on
k0 = int(np.searchsorted(tsa, D0)); k1 = int(np.searchsorted(tsa, D1))
print('U|knobs %s' % KNOBS)
print('U|span %s -> %s  %d bars' % (U(k0).strftime('%Y-%m-%d %H:%M'),
                                    U(k1 - 1).strftime('%Y-%m-%d %H:%M'), k1 - k0))


def runs(fen):
    """every oob run on the dr side in [k0,k1), split at a dr flip. -> [(start,end,dr)]"""
    lo_, hi_ = fen; out = []; st = None; sd = None
    for k in range(k0, k1):
        d = int(rig.DR[k])
        o = (Mg[k] >= hi_) if d > 0 else (Mg[k] <= lo_)
        if o and st is None: st, sd = k, d
        elif o and d != sd: out.append((st, k - 1, sd)); st, sd = k, d
        elif (not o) and st is not None: out.append((st, k - 1, sd)); st = None
    if st is not None: out.append((st, k1 - 1, sd))
    return out


def run_at(k, d, fen):
    lo_, hi_ = fen
    o = lambda i: ((Mg[i] >= hi_) if int(rig.DR[i]) > 0 else (Mg[i] <= lo_))
    if not o(k): return None
    a = k
    while a > k0 and o(a - 1) and int(rig.DR[a - 1]) == d: a -= 1
    b = k
    while b < k1 - 1 and o(b + 1) and int(rig.DR[b + 1]) == d: b += 1
    return a, b


def latch(k, fen):
    lo_, hi_ = fen
    j = k
    while j > FLOOR:
        if (Mg[j] - MID) * (Mg[j - 1] - MID) < 0: break
        j -= 1
    arm = None; run = 0
    for i in range(j, k + 1):
        d = int(rig.DR[i])
        o = (Mg[i] >= hi_) if d > 0 else (Mg[i] <= lo_)
        if o and (run == 0 or int(rig.DR[i - 1]) == d): run += 1
        else: run = 0
        if run >= DW: arm = i
    return (arm, int((int(rig.ts[k]) - int(rig.ts[arm])) / 1000)) if arm is not None else None


# which run-starts are already CLAIMED by a signal row, per fence
claimed = {}
for fl, _ in FENCES:
    col = 'wsb_run%s_start' % fl.replace('/', '')
    rs = db.execute("SELECT %s s FROM %s WHERE wsb_kind='signal' AND wsb_knobs=%%s AND %s IS NOT NULL"
                    % (col, TABLE, col), (KNOBS,), fetch=True)
    claimed[fl] = {int(r['s'].replace(tzinfo=dt.timezone.utc).timestamp() * 1000) for r in rs}
    print('U|fence %s|run-starts claimed by a signal row: %d' % (fl, len(claimed[fl])))

COLS = ['wsb_knobs', 'wsb_kind', 'wsb_fence', 'wsb_sig_utc', 'wsb_sig_ms', 'wsb_dr', 'wsb_via',
        'wsb_ws5mage',
        'wsb_oob_1585', 'wsb_run1585_start', 'wsb_run1585_end', 'wsb_run1585_bars',
        'wsb_run1585_secs', 'wsb_bars_before1585', 'wsb_bars_after1585',
        'wsb_oob_2575', 'wsb_run2575_start', 'wsb_run2575_end', 'wsb_run2575_bars',
        'wsb_run2575_secs', 'wsb_bars_before2575', 'wsb_bars_after2575',
        'wsb_latch1585', 'wsb_latch1585_arm', 'wsb_latch1585_secs',
        'wsb_latch2575', 'wsb_latch2575_arm', 'wsb_latch2575_secs']
pay = []; stat = {}
for fl, fen in FENCES:
    allr = runs(fen)
    unc = [r for r in allr if int(rig.ts[r[0]]) not in claimed[fl]]
    stat[fl] = (len(allr), len(unc))
    for (a, b, d) in unc:
        rec = [KNOBS, 'excursion', fl, U(a), int(rig.ts[a]), d, 'none',
               float(Mg[a]) if np.isfinite(Mg[a]) else None]
        for f2 in ((15.0, 85.0), (25.0, 75.0)):
            r = run_at(a, d, f2)
            if r is None: rec += [0, None, None, None, None, None, None]
            else:
                x, y = r
                rec += [1, U(x), U(y), y - x + 1, (y - x + 1) * 5, a - x, y - a]
        for f2 in ((15.0, 85.0), (25.0, 75.0)):
            L = latch(a, f2)
            rec += [0, None, None] if L is None else [1, U(L[0]), L[1]]
        pay.append(tuple(rec))
for fl, _ in FENCES:
    print('U|fence %s|oob runs in the span %d|UNCLAIMED %d' % (fl, stat[fl][0], stat[fl][1]))
have = db.execute("SELECT COUNT(*) c FROM %s WHERE wsb_kind='excursion' AND wsb_knobs=%%s"
                  % TABLE, (KNOBS,), fetch=True)[0]['c']
if have:
    print('U|%d excursion rows already present at these knobs - nothing written' % have)
else:
    db.executemany('INSERT INTO %s (%s) VALUES (%s)'
                   % (TABLE, ','.join(COLS), ','.join(['%s'] * len(COLS))), pay)
    print('U|inserted %d excursion rows' % len(pay))
t = db.execute("SELECT wsb_kind k, wsb_fence f, COUNT(*) n FROM %s WHERE wsb_knobs=%%s "
               "GROUP BY 1,2 ORDER BY 1,2" % TABLE, (KNOBS,), fetch=True)
for r in t: print('U|table now|kind %-9s fence %-6s rows %s' % (r['k'], r['f'] or '-', r['n']))
db.disconnect()
