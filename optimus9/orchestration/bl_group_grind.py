"""bl_group_grind — the 8-line group baseline grind.

Each active breach's k_len over a 3-value bounded bracket (×lo/mid/hi from bl_grind_config)
→ all 3^N combos, FOLDED from precomputed line-states (no per-combo recompute: each line has
only 3 possible states, so we compute N×3 once then fold). bny30 gate, brackets, window,
swing, lookback all read from bl_grind_config — nothing hardcoded.
"""
import itertools
import multiprocessing as mp
import numpy as np

from logger import get_logger
from ..config import get_db_config
from ..db.database_manager import DatabaseManager
from ..analysis.bl_detect import BLDetect, GCA5M_RAW
from ..analysis.bl_grind import walk, _summary
from ..compute.swing_detect import find_pivots
from .gate_signal_sweep import pine_aligned_signals

_CTX, _STATES = {}, {}
_log = get_logger('BLGroupGrind')


def active_config():
    db = DatabaseManager(**get_db_config()); db.connect()
    c = db.execute('SELECT * FROM bl_grind_config WHERE bgc_is_active=1', fetch=True)[0]
    db.disconnect()
    return c


def _refold(states):
    st = np.vstack(states); nz = np.where(st == 0, 99, st)
    return np.where((st == 0).all(axis=0), 0, nz.min(axis=0)).astype(np.int8)


def _bracket(seed, c):
    return sorted({max(2, int(round(seed * m))) for m in (c['bgc_len_lo'], c['bgc_len_mid'], c['bgc_len_hi'])})


def _precompute_one(item):
    name, L = item
    fam = _CTX['fams'][name]
    f2 = dict(fam); f2['k'] = {**fam['k'], 'k_len': int(L)}
    st = _CTX['det']._run_family(f2, _CTX['base'], _CTX['ts'])[3]['state']
    return (name, int(L)), st[_CTX['mask']].copy()


def prepare(end_ms=None):
    c = active_config()
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=float(c['bgc_window_days']) * 24, warmup_hours=float(c['bgc_warmup_h']))
    base, ts, win_start, _, px = det._setup(end_ms)
    pk_idx, pk_dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=bool(c['bgc_bny30_gate']))
    raw_pk = np.zeros(len(ts), np.int8); raw_pk[pk_idx] = pk_dirs
    db.disconnect()
    mask = ts >= win_start
    pxw = np.asarray(px, float)[mask]
    fams = {f['name']: f for f in det._families}
    lens = {nm: _bracket(f['k']['k_len'], c) for nm, f in fams.items()}
    _CTX.update(det=det, base=base, ts=ts, mask=mask, fams=fams, lens=lens, names=sorted(fams),
                raw_pk=raw_pk[mask], px=pxw, pivots=sorted(find_pivots(pxw, float(c['bgc_swing_pct']))),
                pk_lookback=int(c['bgc_pk_lookback']))
    _log.info(f"prepared {len(fams)} lines · bny30_gate={c['bgc_bny30_gate']} · "
              + ' '.join(f"{nm}{lens[nm]}" for nm in _CTX['names']))
    return c


def precompute(workers=12):
    items = [(nm, L) for nm in _CTX['names'] for L in _CTX['lens'][nm]]
    _log.info(f'precompute {len(items)} line-states')
    with mp.Pool(workers) as pool:
        for key, st in pool.imap_unordered(_precompute_one, items):
            _STATES[key] = st


def _eval(combo):
    names = _CTX['names']
    states = [_STATES[(names[i], combo[i])] for i in range(len(names))]
    s = _summary(walk(_refold(states), _CTX['raw_pk'], _CTX['px'], _CTX['pivots'], _CTX['pk_lookback']))
    return {'combo': ','.join(map(str, combo)), **s}


def run_round(workers=12):
    combos = list(itertools.product(*[_CTX['lens'][nm] for nm in _CTX['names']]))
    _log.info(f'round: {len(combos)} combos')
    out = []
    with mp.Pool(workers) as pool:
        for i, r in enumerate(pool.imap_unordered(_eval, combos, chunksize=50), 1):
            out.append(r)
            if i % 1000 == 0:
                _log.info(f'  {i}/{len(combos)}')
    return out


def persist(results, table='bl_group_results'):
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(f'''CREATE TABLE IF NOT EXISTS {table} (gpk BIGINT AUTO_INCREMENT PRIMARY KEY,
        names VARCHAR(200), combo VARCHAR(200), n INT, avg_stop FLOAT, median_stop FLOAT,
        max_stop FLOAT, avg_profit FLOAT, UNIQUE KEY uq (combo))''')
    names = ','.join(_CTX['names'])
    cols = ['names', 'combo', 'n', 'avg_stop', 'median_stop', 'max_stop', 'avg_profit']
    upd = ', '.join(f'{x}=VALUES({x})' for x in cols[2:])
    db.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))}) "
                   f"ON DUPLICATE KEY UPDATE {upd}",
                   [[names, r['combo']] + [r.get(x) for x in cols[2:]] for r in results])
    db.disconnect()
    _log.info(f'persisted {len(results)} → {table}')


def main():
    c = prepare()
    precompute()
    res = run_round()
    persist(res)
    ok = [r for r in res if r.get('n', 0) >= 1 and r.get('avg_stop')]
    if ok:
        nn = np.array([r['n'] for r in ok]); st = np.array([r['avg_stop'] for r in ok])
        best = min(ok, key=lambda r: (r['n'] < 4, r['avg_stop']))
        wd = float(c['bgc_window_days'])
        _log.info(f"ROUND-1: {len(res)} combos · n median {np.median(nn):.0f} (~{np.median(nn)/wd:.1f}/day) · "
                  f"stop median {np.median(st):.3f} · best [{best['combo']}] stop {best['avg_stop']:.3f} n{best['n']}")
    _log.info('GROUP ROUND-1 COMPLETE')


if __name__ == '__main__':
    main()
