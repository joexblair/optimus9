"""
bl_grind_sweep — module 3: BL grind over gcb5p (k/rsi/stc) AND mnm9m (bb len/mult/src).

Caches the shared compute once (tape, raw_pk, px, swings, the FIXED hb9b state). Per combo
recomputes gcb5p's line+state AND mnm9m's line+state, re-folds the combined gate
(hb9b + gcb5p + mnm9m), walks, records the gated stop metric (#6). Parallel via mp.Pool +
maxtasksperchild; fork-shared CTX; pure _run_family (no DB in the workers).
"""
import multiprocessing as mp
import numpy as np

from logger import get_logger
from ..config import get_db_config
from ..db.database_manager import DatabaseManager
from ..analysis.bl_detect import BLDetect
from ..analysis.bl_grind import walk, _summary
from ..compute.swing_detect import find_pivots

_SWEPT = {'gcb5p', 'mnm9m'}      # the two families that vary per combo (hb9b stays fixed)
_CTX   = {}
_log   = get_logger('BLGrindSweep')


def _refold(states):
    st = np.vstack(states); nz = np.where(st == 0, 99, st)
    return np.where((st == 0).all(axis=0), 0, nz.min(axis=0)).astype(np.int8)


def prepare(lookback_hours, end_ms=None, swing_pct=0.9, warmup_hours=12.0):
    db  = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=lookback_hours, warmup_hours=warmup_hours)
    base, ts, win_start, raw_pk, px = det._setup(end_ms)
    mask  = ts >= win_start
    fixed = [det._run_family(f, base, ts)[3]['state']              # hb9b only — computed once
             for f in det._families if f['name'] not in _SWEPT]
    pxw   = np.asarray(px, float)[mask]
    _CTX.update(det=det, base=base, ts=ts, mask=mask, fixed=fixed,
                gcb5p=next(f for f in det._families if f['name'] == 'gcb5p'),
                mnm9m=next(f for f in det._families if f['name'] == 'mnm9m'),
                raw_pk=np.asarray(raw_pk)[mask], px=pxw,
                pivots=sorted(find_pivots(pxw, swing_pct)), pk_lookback=11)
    db.disconnect()
    return len(ts), int(mask.sum())


def _eval_combo(combo):
    """combo = (gk, gr, gs, ml, mm, msrc): gcb5p k/rsi/stc + mnm9m bb len/mult/src."""
    gk, gr, gs, ml, mm, msrc = combo
    gfam = dict(_CTX['gcb5p']); gfam['k'] = {**gfam['k'], 'k_len': int(gk), 'rsi_len': int(gr), 'stc_len': int(gs)}
    mfam = dict(_CTX['mnm9m']); mfam['k'] = {**mfam['k'], 'bb_len': int(ml), 'bb_mult': float(mm), 'src': msrc}
    try:
        gst = _CTX['det']._run_family(gfam, _CTX['base'], _CTX['ts'])[3]['state']
        mst = _CTX['det']._run_family(mfam, _CTX['base'], _CTX['ts'])[3]['state']
        combined = _refold(_CTX['fixed'] + [gst, mst])[_CTX['mask']]
        s = _summary(walk(combined, _CTX['raw_pk'], _CTX['px'], _CTX['pivots'], _CTX['pk_lookback']))
    except Exception as e:
        s = {'n': -1, 'err': str(e)[:80]}
    return {'k_len': int(gk), 'rsi_len': int(gr), 'stc_len': int(gs),
            'mn_len': int(ml), 'mn_mult': float(mm), 'mn_src': msrc, **s}


def make_grid(gk, gr, gs, ml, mm, ms):
    return [(k, r, s, l, m, src) for k in gk for r in gr for s in gs for l in ml for m in mm for src in ms]


def _eval_mask(item):
    """item = (combo6, gcb5p_exit_mask) — re-score a fixed gcb5p×mnm9m config with the
    gcb5p breach EXIT MASK overridden (which exits complete the breach → the bls3 timing)."""
    (gk, gr, gs, ml, mm, msrc), mask = item
    gfam = dict(_CTX['gcb5p']); gfam['k'] = {**gfam['k'], 'k_len': int(gk), 'rsi_len': int(gr), 'stc_len': int(gs)}
    gfam['exit_mask'] = int(mask)
    mfam = dict(_CTX['mnm9m']); mfam['k'] = {**mfam['k'], 'bb_len': int(ml), 'bb_mult': float(mm), 'src': msrc}
    try:
        gst = _CTX['det']._run_family(gfam, _CTX['base'], _CTX['ts'])[3]['state']
        mst = _CTX['det']._run_family(mfam, _CTX['base'], _CTX['ts'])[3]['state']
        combined = _refold(_CTX['fixed'] + [gst, mst])[_CTX['mask']]
        s = _summary(walk(combined, _CTX['raw_pk'], _CTX['px'], _CTX['pivots'], _CTX['pk_lookback']))
    except Exception as e:
        s = {'n': -1, 'err': str(e)[:60]}
    return {'k_len': int(gk), 'rsi_len': int(gr), 'stc_len': int(gs), 'mn_len': int(ml),
            'mn_mult': float(mm), 'mn_src': msrc, 'gcb5p_mask': int(mask), **s}


def _rank(out):
    return sorted(out, key=lambda r: (r.get('n', 0) < 10, r.get('avg_stop') or 9e9))  # meaningful n, then tightest


def run_sweep(combos, workers=None, maxtasks=200, chunksize=4, progress=500, checkpoint=500):
    workers = workers or max(1, mp.cpu_count() - 2)
    _log.info(f'sweep: {len(combos)} combos · {workers} workers · maxtasksperchild={maxtasks}')
    out = []
    with mp.Pool(workers, maxtasksperchild=maxtasks) as pool:
        for i, r in enumerate(pool.imap_unordered(_eval_combo, combos, chunksize=chunksize), 1):
            out.append(r)
            if i % progress == 0:
                _log.info(f'  {i}/{len(combos)} done')
            if checkpoint and i % checkpoint == 0:
                persist(_rank(out)); _log.info(f'  checkpoint at {i}')
    return _rank(out)


def persist(results, table='bl_grind_results'):
    """Upsert keyed on the combo (CREATE IF NOT EXISTS, never drops) so results accumulate
    across restarts — the basis for resume-from-checkpoint."""
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(f'''CREATE TABLE IF NOT EXISTS {table} (
        bgr_pk BIGINT AUTO_INCREMENT PRIMARY KEY, k_len INT, rsi_len INT, stc_len INT,
        mn_len INT, mn_mult DECIMAL(4,2), mn_src VARCHAR(8),
        n INT, avg_stop FLOAT, median_stop FLOAT, max_stop FLOAT, avg_profit FLOAT,
        UNIQUE KEY uq_combo (k_len, rsi_len, stc_len, mn_len, mn_mult, mn_src))''')
    cols = ['k_len', 'rsi_len', 'stc_len', 'mn_len', 'mn_mult', 'mn_src',
            'n', 'avg_stop', 'median_stop', 'max_stop', 'avg_profit']
    upd  = ', '.join(f'{c}=VALUES({c})' for c in cols[6:])         # refresh metrics on re-score
    db.executemany(
        f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s'] * len(cols))}) "
        f"ON DUPLICATE KEY UPDATE {upd}",
        [[r.get(c) for c in cols] for r in results])
    db.disconnect()
    _log.info(f'persisted {len(results)} rows → {table} (upsert)')


def done_combos(table='bl_grind_results'):
    """The set of combos already scored in `table` (empty if it doesn't exist) — for resume."""
    db = DatabaseManager(**get_db_config()); db.connect()
    if not db.execute(f"SHOW TABLES LIKE '{table}'", fetch=True):
        db.disconnect(); return set()
    rows = db.execute(f'SELECT k_len, rsi_len, stc_len, mn_len, mn_mult, mn_src FROM {table}', fetch=True)
    db.disconnect()
    return {(r['k_len'], r['rsi_len'], r['stc_len'], r['mn_len'], round(float(r['mn_mult']), 2), r['mn_src'])
            for r in rows}


# gcb5p grid (coarser than the 3K — its shape is mapped; budget goes to mnm9m × window)
GK = range(8, 29, 4)             # k_len:  8,12,16,20,24,28              (6)
GR = range(30, 161, 30)          # rsi:    30,60,90,120,150              (5)
GS = range(30, 161, 30)          # stc:    30,60,90,120,150              (5)
ML = [16, 17, 18, 19, 20, 21, 22]            # mnm9m len                 (7)
MM = [0.53, 0.63, 0.73, 0.83]                # mnm9m mult                (4)
MS = ['close', 'hl2', 'hl3', 'ohlc4', 'hlcc4']   # mnm9m src             (5)


def main():
    import argparse
    ap = argparse.ArgumentParser(description='BL grind — gcb5p × mnm9m sweep')
    ap.add_argument('--window_hours', type=float, default=90)
    ap.add_argument('--warmup_hours', type=float, default=12)
    ap.add_argument('--workers',      type=int,   default=12)
    ap.add_argument('--fresh', action='store_true', help='drop the table + score all (default: resume — skip done)')
    args = ap.parse_args()
    nb, nw = prepare(args.window_hours, warmup_hours=args.warmup_hours)
    all_combos = make_grid(GK, GR, GS, ML, MM, MS)
    if args.fresh:
        db = DatabaseManager(**get_db_config()); db.connect()
        db.execute('DROP TABLE IF EXISTS bl_grind_results'); db.disconnect()
        done = set()
    else:
        done = done_combos()
    combos = [c for c in all_combos
              if (c[0], c[1], c[2], c[3], round(c[4], 2), c[5]) not in done]   # skip already-scored
    _log.info(f'BL grind: {len(combos)}/{len(all_combos)} to score ({len(done)} done) · '
              f'window {args.window_hours}h ({nw} bars) · {args.workers} workers')
    if combos:
        persist(run_sweep(combos, workers=args.workers))
    _log.info('BL grind COMPLETE')


if __name__ == '__main__':
    main()
