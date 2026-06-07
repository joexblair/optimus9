"""
bl_grind_sweep — module 3: the gcb5p parameter sweep over the BL walk.

Caches the shared compute ONCE (tape, raw 5s-pk, px_smooth, swings, and the FIXED breach
families' states — hb9b, mnm9m). Per gcb5p combo it recomputes ONLY gcb5p's line + state,
re-folds the combined gate (min-nonzero), walks, and records the gated stop metric (#6).

Parallel via mp.Pool with maxtasksperchild — workers recycle so memory stays bounded
(the grind's memory pin from the mindmap). fork shares the cached arrays copy-on-write;
the per-combo work (_run_family→_line) is pure compute, no DB, so it's fork-safe.
"""
import multiprocessing as mp
import numpy as np

from logger import get_logger
from ..config import get_db_config
from ..db.database_manager import DatabaseManager
from ..analysis.bl_detect import BLDetect
from ..analysis.bl_grind import walk, _summary
from ..compute.swing_detect import find_pivots

_LINE = 'gcb5p'
_CTX  = {}                       # shared context, populated in the parent before the pool forks
_log  = get_logger('BLGrindSweep')


def _refold(states):
    """combined = min over NON-ZERO states, 0 only when all idle (the gate fold)."""
    st = np.vstack(states)
    nz = np.where(st == 0, 99, st)
    return np.where((st == 0).all(axis=0), 0, nz.min(axis=0)).astype(np.int8)


def prepare(lookback_hours, end_ms=None, swing_pct=0.9, warmup_hours=12.0):
    """Parent-side: build the shared context once. Returns (loaded_bars, window_bars).
    warmup_hours only needs to cover the longest line lookback (rsi/stc ≤160 ≈ 27min), so
    12h is ample — a shorter total window = a faster per-combo state machine."""
    db  = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=lookback_hours, warmup_hours=warmup_hours)
    base, ts, win_start, raw_pk, px = det._setup(end_ms)
    mask  = ts >= win_start
    fixed = [det._run_family(f, base, ts)[3]['state']               # hb9b, mnm9m — computed once
             for f in det._families if f['name'] != _LINE]
    gcb5p = next(f for f in det._families if f['name'] == _LINE)
    pxw   = np.asarray(px, float)[mask]
    piv   = sorted(find_pivots(pxw, swing_pct))
    db.disconnect()                                                 # workers don't touch the DB
    _CTX.update(det=det, base=base, ts=ts, mask=mask, fixed=fixed, gcb5p=gcb5p,
                raw_pk=np.asarray(raw_pk)[mask], px=pxw, pivots=piv, pk_lookback=11)
    return len(ts), int(mask.sum())


def _eval_combo(combo):
    """combo = (k_len, rsi_len, stc_len). Recompute gcb5p, re-fold, walk → stop summary."""
    k_len, rsi_len, stc_len = combo
    fam = dict(_CTX['gcb5p'])
    fam['k'] = {**fam['k'], 'k_len': int(k_len), 'rsi_len': int(rsi_len), 'stc_len': int(stc_len)}
    try:
        state    = _CTX['det']._run_family(fam, _CTX['base'], _CTX['ts'])[3]['state']
        combined = _refold(_CTX['fixed'] + [state])[_CTX['mask']]
        s = _summary(walk(combined, _CTX['raw_pk'], _CTX['px'], _CTX['pivots'], _CTX['pk_lookback']))
    except Exception as e:                                          # never let one combo kill the grind
        s = {'n': -1, 'err': str(e)[:80]}
    return {'k_len': int(k_len), 'rsi_len': int(rsi_len), 'stc_len': int(stc_len), **s}


def make_grid(k_lens=range(5, 36), rsi_lens=range(10, 161, 5), stc_lens=range(10, 161, 5)):
    return [(k, r, s) for k in k_lens for r in rsi_lens for s in stc_lens]


def _rank(out):
    return sorted(out, key=lambda r: (r.get('n', 0) <= 0, r.get('avg_stop') or 9e9))  # most/tightest first


def run_sweep(combos, workers=None, maxtasks=200, chunksize=4, progress=1000, checkpoint=2500):
    workers = workers or max(1, mp.cpu_count() - 2)
    _log.info(f'sweep: {len(combos)} combos · {workers} workers · maxtasksperchild={maxtasks}')
    out = []
    with mp.Pool(workers, maxtasksperchild=maxtasks) as pool:
        for i, r in enumerate(pool.imap_unordered(_eval_combo, combos, chunksize=chunksize), 1):
            out.append(r)
            if i % progress == 0:
                _log.info(f'  {i}/{len(combos)} done')
            if checkpoint and i % checkpoint == 0:                  # survive a crash/overrun
                persist(_rank(out)); _log.info(f'  checkpoint persisted at {i}')
    return _rank(out)


def main():
    import argparse
    ap = argparse.ArgumentParser(description='BL grind — gcb5p sweep')
    ap.add_argument('--window_hours', type=float, default=26)
    ap.add_argument('--warmup_hours', type=float, default=12)
    ap.add_argument('--workers',      type=int,   default=12)       # leave cores for klinecollect/auditor
    args = ap.parse_args()
    nb, nw = prepare(args.window_hours, warmup_hours=args.warmup_hours)
    combos = make_grid()
    _log.info(f'BL grind start: {len(combos)} combos · window {args.window_hours}h ({nw} bars) · '
              f'warmup {args.warmup_hours}h · {args.workers} workers')
    res = run_sweep(combos, workers=args.workers)
    persist(res)
    _log.info(f'BL grind COMPLETE — best: {res[0] if res else None}')


if __name__ == '__main__':
    main()


def persist(results, table='bl_grind_results'):
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(f'DROP TABLE IF EXISTS {table}')
    db.execute(f'''CREATE TABLE {table} (
        bgr_pk BIGINT AUTO_INCREMENT PRIMARY KEY, k_len INT, rsi_len INT, stc_len INT,
        n INT, avg_stop FLOAT, median_stop FLOAT, max_stop FLOAT, avg_profit FLOAT)''')
    cols = ['k_len', 'rsi_len', 'stc_len', 'n', 'avg_stop', 'median_stop', 'max_stop', 'avg_profit']
    db.executemany(
        f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s'] * len(cols))})",
        [[r.get(c) for c in cols] for r in results])
    db.disconnect()
    _log.info(f'persisted {len(results)} rows → {table}')
