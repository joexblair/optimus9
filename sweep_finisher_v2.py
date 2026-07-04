"""
sweep_finisher_v2.py (Joe 0704) — worst-window minimax sweep of the finisher_v2 knobs on the 6-baseline
(s2/3/4m len 6, s5m len 8; trigger gcs5M; correct DB r-lines). Engine functions only (no reimplementation).

Knobs: fin_mage_wob {0-3} · fin_s30M_oob {0,1} · s15r_lb · s30r_lb · fin_lb · fin_fwd.
Metric: net-of-cost per window (stop applied via the exit stack), ranked by WORST window (minimax). All combos
→ table finisher_v2_sweep. Opens (arm/gate) precomputed once per window; finisher+exit+walk per combo.

  python3 sweep_finisher_v2.py smoke   # 3 combos × 1 window, sanity
  python3 sweep_finisher_v2.py         # full grid × windows, multiprocessing
"""
import sys, itertools, time, os; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm; from datetime import timezone
from dataclasses import replace
import multiprocessing as mp
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis import lr_v2 as L
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
SMOKE = len(sys.argv) > 1 and sys.argv[1] == 'smoke'
WIN_ENDS = [ms('2026-06-15 00:00'), ms('2026-06-16 00:00'), ms('2026-06-18 00:00'),
            ms('2026-06-19 00:00'), ms('2026-06-21 00:00'), ms('2026-06-22 00:00')]
if SMOKE: WIN_ENDS = WIN_ENDS[:1]
SPEC = {'s2m': (6, 0.56, 'close'), 's2M': (37, 0.72, 'hlcc4'), 's3m': (6, 0.56, 'close'), 's3M': (37, 0.72, 'ohlc4'),
        's4m': (6, 0.56, 'close'), 's4M': (37, 0.72, 'ohlc4'), 's5m': (8, 0.40, 'ohlc4'), 's5M': (37, 0.83, 'ohlc4'),
        's7m': (10, 0.77, 'ohlc4'), 's7M': (37, 0.83, 'ohlc4'), 's15m': (7, 0.74, 'hlcc4'), 's15M': (37, 0.83, 'ohlc4'),
        's30m': (10, 0.60, 'hlc3'), 's30M': (37, 0.83, 'ohlc4')}
GRID = list(itertools.product((0, 1, 2, 3), (0, 1), (14, 19, 24, 29, 34, 39), (9, 14, 19, 24, 29), (30, 42, 54), (6, 12)))
if SMOKE: GRID = [(0, 1, 29, 19, 42, 12), (2, 1, 29, 19, 42, 12), (0, 0, 24, 14, 42, 12)]

_W = None; _lr = None

def worker_init():
    global _W, _lr
    db = DatabaseManager(**get_db_config()); db.connect(); ls = bm.LineStore(db); cfg = bm.BiasConfig(**BASE_BIAS); _lr = lr_config(db)
    ovr = {ln: (ls.resolve(ln)[0], ('bb', a, b, c), 'emerging') for ln, (a, b, c) in SPEC.items()}
    ovr['s2M'] = (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging')
    _W = []
    for end in WIN_ENDS:
        W = bm.BiasWindow(db, end, lookback=72, warmup=80, cfg=cfg, lean=True, line_overrides=ovr); W._line = W._line_emerging
        opens = L.gate_open(W, _lr, L.v2_arm(W, _lr), L.gate_signals(W, _lr))     # fixed (s5m=8) → once per window
        _W.append((W, opens))

def eval_combo(args):
    wob, oob, s15lb, s30lb, flb, ffwd = args
    cfg2 = replace(_lr, fin_mage_wob=wob, fin_s30M_oob=oob, s15r_lb=s15lb, s30r_lb=s30lb, fin_lb=flb, fin_fwd=ffwd)
    nets, maes, nn = [], [], 0
    for (W, opens) in _W:
        seen, ent = set(), []
        for e in L.finisher_v2(W, cfg2, opens, 'gcs5M'):
            if e[3] not in seen: seen.add(e[3]); ent.append(e)
        resc = L.strand_rescue(W, cfg2, ent, L.lr_exit_v2(W, cfg2, ent, predict=False))
        nets.append(sum(r - 0.20 for (*_, r, _rsn) in resc)); nn += len(resc)
        maes += [x[4] for x in lr_walk(W, ent, cfg2)]
    return (args, float(min(nets)), float(np.mean(nets)), nn, float(np.median(maes)) if maes else 0.0)

if __name__ == '__main__':
    nproc = max(1, (os.cpu_count() or 4) - 2)
    print('grid=%d combos x %d windows | %d workers%s' % (len(GRID), len(WIN_ENDS), nproc, ' [SMOKE]' if SMOKE else '')); sys.stdout.flush()
    t0 = time.time(); res = []
    if SMOKE:
        worker_init()
        for a in GRID:
            r = eval_combo(a); res.append(r)
            print('  wob%d oob%d s15lb%d s30lb%d lb%d fwd%d -> worst=%+.0f mean=%+.0f n=%d MAE=%.2f' % (
                r[0][0], r[0][1], r[0][2], r[0][3], r[0][4], r[0][5], r[1], r[2], r[3], r[4]))
        print('smoke ok (%.0fs)' % (time.time() - t0)); sys.exit(0)
    with mp.Pool(processes=nproc, initializer=worker_init) as pool:
        for i, r in enumerate(pool.imap_unordered(eval_combo, GRID, chunksize=4), 1):
            res.append(r)
            if i % 60 == 0: print('  %d/%d (%.0fs)' % (i, len(GRID), time.time() - t0)); sys.stdout.flush()
    res.sort(key=lambda x: -x[1])
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute('DROP TABLE IF EXISTS finisher_v2_sweep')
    db.execute('''CREATE TABLE finisher_v2_sweep (mage_wob INT, s30M_oob INT, s15r_lb INT, s30r_lb INT,
                  fin_lb INT, fin_fwd INT, worst DOUBLE, mean DOUBLE, n INT, mae DOUBLE)''')
    db.executemany('INSERT INTO finisher_v2_sweep VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                   [(c[0], c[1], c[2], c[3], c[4], c[5], w, mn, nn, mae) for (c, w, mn, nn, mae) in res])
    print('\ndone %d in %.0fs (%.1fh) -> finisher_v2_sweep. TOP 20 by WORST-window net-of-cost:' % (
        len(res), time.time() - t0, (time.time() - t0) / 3600))
    print('  wob oob s15lb s30lb finlb finfwd | worst  mean   n   MAE')
    for (c, w, mn, nn, mae) in res[:20]:
        print('  %d   %d   %-2d    %-2d    %-2d    %-2d     | %+5.0f %+5.0f %5d %.2f' % (
            c[0], c[1], c[2], c[3], c[4], c[5], w, mn, nn, mae))
    base = next(((w, mn, nn) for (c, w, mn, nn, mae) in res if c == (0, 1, 29, 19, 42, 12)), None)
    print('  baseline (wob0 oob1 s15r29 s30r19 lb42 fwd12):', base)
