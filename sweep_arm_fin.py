"""sweep_arm_fin.py (Joe 0704) — 2D sweep of the #53 finisher-lookback-on-arm-unlatch knobs:
  arm_wob  (s5Mage unlatch wobslay, 2..15)  ×  fin_fwd  (proximal forward tolerance, 2..15 in 30s-bars → ×6 base).
Uses v2_walk_ad (the shipping producer) + lr_exit_v2(predict=False) + strand_rescue, scored on the 7 canonical
sweep windows by WORST-window net-of-cost (minimax). Parallel, checkpointed/resumable → table sweep_arm_fin.
  python3 sweep_arm_fin.py
"""
import os
os.environ.update({k: '1' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')})
import sys, json, datetime as dtm
from datetime import timezone
sys.path.insert(0, '/home/joe/thecodes')
import multiprocessing as mp
import numpy as np
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS, RT_COST


def ms(s):
    return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


WINDOW_ENDS = [ms('2026-05-25 00:00') + i * 5 * 86400000 for i in range(7)]   # the 7 canonical sweep windows
GRID = [(aw, ff) for aw in range(2, 16) for ff in range(2, 16)]              # arm_wob × fin_fwd(30s-bars)

_DB = None; _LC = None; _CFG = None; _CACHE = {}


def _init():
    global _DB, _LC, _CFG
    _DB = DatabaseManager(**get_db_config()); _DB.connect()
    _LC = lr_config(_DB); _CFG = bm.BiasConfig(**BASE_BIAS)


def _win(end):
    if end not in _CACHE:                                # base tape loaded once per worker per window
        W = bm.BiasWindow(_DB, end, cfg=_CFG, lean=True); W._line = W._line_emerging
        _CACHE[end] = W
    return _CACHE[end]


def _work(cfg):
    aw, ff = cfg
    _LC.arm_wob = aw; _LC.fin_fwd = ff * 6               # fin_fwd 30s-bars → base(5s) bars
    nets = []
    try:
        for end in WINDOW_ENDS:
            W = _win(end)
            ent = v2_walk_ad(W, _LC)
            resc = strand_rescue(W, _LC, ent, lr_exit_v2(W, _LC, ent, predict=False))
            r = np.array([x[5] for x in resc]) if resc else np.array([])
            nets.append(float((r - RT_COST).sum()) if len(r) else 0.0)
        return aw, ff, min(nets), nets, None
    except Exception as e:
        return aw, ff, None, [], str(e)[:200]


if __name__ == '__main__':
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute("""CREATE TABLE IF NOT EXISTS sweep_arm_fin (arm_wob INT, fin_fwd_30s INT, worst FLOAT,
        nets TEXT, err TEXT, PRIMARY KEY (arm_wob, fin_fwd_30s))""")
    done = {(r['arm_wob'], r['fin_fwd_30s']) for r in
            db.execute('SELECT arm_wob, fin_fwd_30s FROM sweep_arm_fin WHERE err IS NULL', fetch=True)}
    todo = [c for c in GRID if c not in done]
    ncore = max(1, min(14, (os.cpu_count() or 4) - 2))
    print('sweep_arm_fin: %d configs (%d done) × %d windows · %d cores' % (len(GRID), len(done), len(WINDOW_ENDS), ncore), flush=True)
    with mp.Pool(ncore, initializer=_init) as pool:
        n = 0
        for aw, ff, worst, nets, err in pool.imap_unordered(_work, todo, chunksize=1):
            db.execute('INSERT INTO sweep_arm_fin VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE '
                       'worst=VALUES(worst), nets=VALUES(nets), err=VALUES(err)',
                       (aw, ff, worst, json.dumps(nets), err))
            n += 1
            if n % 20 == 0:
                print('  %d/%d done' % (n, len(todo)), flush=True)
    print('DONE. top 10 by worst-window net-of-cost:', flush=True)
    for r in db.execute('SELECT arm_wob, fin_fwd_30s, worst FROM sweep_arm_fin WHERE err IS NULL '
                        'ORDER BY worst DESC LIMIT 10', fetch=True):
        print('  arm_wob=%-2d fin_fwd=%-2d(×30s)  worst=%+.1f%%' % (r['arm_wob'], r['fin_fwd_30s'], r['worst']), flush=True)
    db.disconnect()
