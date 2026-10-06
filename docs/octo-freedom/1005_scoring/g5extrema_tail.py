"""THE `g5extrema_lookback` SWEEP, SECOND PASS — the TAIL columns. Joe 1006 asked the question that
exposed the first pass: *"are sweeps inherently flawed? how do they handle early reversals on a large
leg? that's our typical MAE killer"*.

THE FIRST PASS BANKED mean MAE, median MAE and a count over 0.70. None of those sees the tail:
  - the 34 rows at MAE >= 1.8 are 9 % of rows and carry 37 % of ALL the heat
  - and they come from only 15 DISTINCT ARMS. One arm, 09-25 18:01:25, produces SEVEN of them
So a per-row cell can show a gain that is one leg counted seven times, and mean/median both dilute
the top 9 % away. Median is the worst of the three - a 50th-percentile statistic on a top-decile
problem.

THIS PASS BANKS THE EFFECTIVE TAIL:
  rows_18   rows with MAE >= 1.8 on the traded side
  arms_18   DISTINCT arm bars behind them  <- the number a knob would actually be reducing
  mae_18    their total MAE
  worst     the single largest MAE in the cell
  top_arm   the arm contributing the most tail MAE, and how many rows it owns
1.8 is Joe's own filter, 1006: *"I've filtered on MAE >=1.8 so that we can focus on the biggest
problems first"*. It is his threshold, not a knee I measured.
"""
import os as _os, sys, io, contextlib, time
import numpy as np
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
sys.path.insert(0, '/home/joe/thecodes')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    with contextlib.redirect_stderr(io.StringIO()):
        import score39 as SC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TAIL = 1.8
ts = np.asarray(SC.ts, np.int64)
H, L = SC.pivots(0.70)
db = DatabaseManager(**get_db_config()); db.connect()
K = [r['k'] for r in db.execute("SELECT DISTINCT os_knob_key k FROM octosig_rulings", fetch=True)
     if 'flip-towards' in r['k']][0]
SIG = [(int(np.searchsorted(ts, int(r['ms']))), str(r['d']), r['a']) for r in db.execute(
    "SELECT os_bar_ms ms, os_day d, os_arm_ts a FROM octosig_rulings WHERE os_knob_key=%s "
    "ORDER BY os_bar_ms", (K,), fetch=True)]
db.disconnect()
print('# %d octo-sigs | tail threshold MAE >= %.1f (Joe\'s filter) | live value 48 bars' % (len(SIG), TAIL))
print('# arms_18 is the EFFECTIVE tail count. rows_18 counts one leg many times; arms_18 does not.')
print()
print('| g5extrema_lookback | = sec | scored | mean MAE | **rows_18** | **arms_18** | **mae_18** | '
      'tail share of MAE | worst | top arm (rows) | secs |')
print('|' + '---|' * 11, flush=True)
for v in range(6, 241, 6):
    t0 = time.time()
    SC.G5EXTREMA_LOOKBACK_BARS = v
    a = []; tail = []
    for k, day, arm in SIG:
        r = SC.classify(k)
        D_ = r.get('D') or {}
        flip = bool(r['status'] == 'CONFLUENCE' and not D_.get('away', True))
        d = int(r['d'])
        if d == 0: continue
        f2, a2, _ = SC.score(k, -d if flip else d, H, L)
        if a2 is None: continue
        a.append(a2)
        if a2 >= TAIL: tail.append((a2, day + ' ' + arm))
    tot = float(np.sum(a)); tm = float(np.sum([x for x, _ in tail])) if tail else 0.0
    arms = {}
    for x, key in tail: arms[key] = arms.get(key, [0, 0.0]); arms[key][0] += 1; arms[key][1] += x
    top = max(arms.items(), key=lambda kv: kv[1][1])[0] if arms else '—'
    topn = arms[top][0] if arms else 0
    star = '**' if v == 48 else ''
    print('| %s%d%s | %d | %d | %.4f | **%d** | **%d** | **%.3f** | **%.0f%%** | %.3f | %s (%d) | %.0f |'
          % (star, v, star, v * 5, len(a), float(np.mean(a)), len(tail), len(arms), tm,
             100.0 * tm / tot if tot else 0, max([x for x, _ in tail]) if tail else 0.0,
             top[6:] if top != '—' else '—', topn, time.time() - t0), flush=True)
