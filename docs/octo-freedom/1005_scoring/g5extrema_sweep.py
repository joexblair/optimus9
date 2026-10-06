"""THE `g5extrema_lookback` SWEEP, scored on MAE/MFE. Joe 1006: *"go for sweep"*.

THE KNOB, renamed on his word the same turn: `g5extrema_lookback` — how far back mtd step 1 searches
for the g5Mage oob extrema. One job, used once (`score39.py:76`). It is NOT `rev_lookback`, which is
a different knob that happens to sit at the same 48 bars / 240 s.

WHY THIS RUN EXISTS. The knob was swept once before, stage 1: 19 cells, 12..240 bars stepped by 12,
scored on NET % under FIT/TEST. `lazyg_sweep` has NO MAE/MFE columns at all, 48 itself was never a
cell, and the run predates every bake from 1006 — the 2 min mtd walk, CLAIM_HOP 3, flip-towards and
the grade correction. Joe asked the question that run cannot answer: the MAE/MFE impact.

MY CHOSEN RANGE AND STEP, NAMED: 6 to 240 bars stepped by 6 = 30 s increments, 40 cells. The old
sweep's step of 12 skipped the live value; step 6 includes 48 and resolves the 36..72 region where
total net peaked. Joe set no range, so this is mine.

POPULATION: the 397 octo-sigs in `octosig_rulings` at the current knob key, 12 days, one set.
SCORING: score39.score at swing 0.70, swing-to-pivot, MAE = max(0, adverse), NO STOP, on the side
ACTUALLY TRADED — the flip is on `towards` per Joe 1006, so a with-trend row scores its flipped side.
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

ts = np.asarray(SC.ts, np.int64)
H, L = SC.pivots(0.70)
db = DatabaseManager(**get_db_config()); db.connect()
K = [r['k'] for r in db.execute("SELECT DISTINCT os_knob_key k FROM octosig_rulings", fetch=True)
     if 'flip-towards' in r['k']][0]
BARS = [int(np.searchsorted(ts, int(r['ms']))) for r in db.execute(
    "SELECT os_bar_ms ms FROM octosig_rulings WHERE os_knob_key=%s ORDER BY os_bar_ms",
    (K,), fetch=True)]
db.disconnect()
print('# %d octo-sigs | live value 48 bars = 240 s | step 6 bars = 30 s' % len(BARS), flush=True)
print()
print('| g5extrema_lookback | = sec | scored | r1 | r2 | neither | CONF | OPEN | BLOCKED | src fwd | '
      'mean MAE | median MAE | mean MFE | MAE>0.70 | secs |')
print('|' + '---|' * 15, flush=True)
for v in range(6, 241, 6):
    t0 = time.time()
    SC.G5EXTREMA_LOOKBACK_BARS = v
    a = []; f = []; rt = {}; st = {}; fwd = 0
    for k in BARS:
        r = SC.classify(k)
        rt[r['m']['route']] = rt.get(r['m']['route'], 0) + 1
        st[r['status']] = st.get(r['status'], 0) + 1
        if r['m'].get('src') == 'fwd': fwd += 1
        D_ = r.get('D') or {}
        flip = bool(r['status'] == 'CONFLUENCE' and not D_.get('away', True))
        d = int(r['d']); dt = -d if flip else d
        if d == 0: continue
        f2, a2, _ = SC.score(k, dt, H, L)
        if a2 is None: continue
        a.append(a2); f.append(f2)
    star = '**' if v == 48 else ''
    print('| %s%d%s | %d | **%d** | %d | %d | %d | **%d** | %d | %d | %d | **%.4f** | **%.4f** | **%.4f** | **%d** | %.0f |'
          % (star, v, star, v * 5, len(a), rt.get('mtd.r1', 0), rt.get('mtd.r2', 0),
             rt.get('neither', 0), st.get('CONFLUENCE', 0), st.get('OPEN', 0), st.get('BLOCKED', 0),
             fwd, float(np.mean(a)), float(np.median(a)), float(np.mean(f)),
             int((np.array(a) > 0.70).sum()), time.time() - t0), flush=True)
