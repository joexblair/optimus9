"""Grind the gcb5p breach EXIT MASK over the top-33 configs, 33 days — does varying which
exits complete the breach (and thus the bls3 timing) break the ~1.5 stop cluster?
Joe's discriminator: stops spread → exits are the lever; stops pinned → swing-geom / hb9b."""
import sys, time; sys.path.insert(0, '/home/joe/thecodes')
import multiprocessing as mp
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration import bl_grind_sweep as S
from logger import get_logger
log = get_logger('ExitMask')

MASKS = [1, 2, 3, 4, 5, 6, 7]                        # exit combos (bit1=exit1, bit2=exit2, bit4=exit3)

if __name__ == '__main__':
    db = DatabaseManager(**get_db_config()); db.connect()
    top = db.execute('SELECT k_len,rsi_len,stc_len,mn_len,mn_mult,mn_src FROM bl_grind_results '
                     'WHERE n>=20 ORDER BY avg_stop LIMIT 33', fetch=True)
    configs = [(r['k_len'], r['rsi_len'], r['stc_len'], r['mn_len'], float(r['mn_mult']), r['mn_src']) for r in top]
    db.disconnect()

    S.prepare(33 * 24, warmup_hours=12)
    items = [(c, m) for c in configs for m in MASKS]
    log.info(f'exit-mask grind: {len(configs)} configs x {len(MASKS)} masks = {len(items)} over 33d')
    out = []
    with mp.Pool(12, maxtasksperchild=50) as pool:
        for i, r in enumerate(pool.imap_unordered(S._eval_mask, items, chunksize=2), 1):
            out.append(r)
            if i % 30 == 0:
                log.info(f'  {i}/{len(items)} done')

    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute('DROP TABLE IF EXISTS bl_grind_exitmask')
    db.execute('''CREATE TABLE bl_grind_exitmask (pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        k_len INT, rsi_len INT, stc_len INT, mn_len INT, mn_mult DECIMAL(4,2), mn_src VARCHAR(8),
        gcb5p_mask INT, n INT, avg_stop FLOAT, median_stop FLOAT, max_stop FLOAT, avg_profit FLOAT)''')
    cols = ['k_len', 'rsi_len', 'stc_len', 'mn_len', 'mn_mult', 'mn_src', 'gcb5p_mask',
            'n', 'avg_stop', 'median_stop', 'max_stop', 'avg_profit']
    db.executemany(f"INSERT INTO bl_grind_exitmask ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})",
                   [[r.get(c) for c in cols] for r in out])
    db.disconnect()
    log.info('EXITMASK COMPLETE')
