"""
gate_top300 — real-gate (both) candidate narrowing, done right: select the top ~300
combos by PROXIMITY (avg_stop) only — NO qty pre-filter — then cluster_score them and
persist an Excel-ready table + view. Qty stays a downstream trade-off, never a pre-filter.
"""
import sys, json, itertools
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration import bl_group_grind as G
from optimus9.orchestration.gate_signal_sweep import pine_aligned_signals
from optimus9.analysis.bl_detect import GCA5M_RAW
from optimus9.analysis.bl_grind import walk, _summary
from optimus9.analysis.cluster_scoring import ClusterScoring

OR_PK = 9010
TOPN  = 300
NAMES = ['b6b', 'hb15b', 'hb9b', 'hs15r', 'hs9r', 's18b', 's30r', 's90b']   # combo order
TABLE = 'gate_both_top300'


def main():
    G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=True)  # REAL gate
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw = full[mask]
    px, piv, lb = G._CTX['px'], G._CTX['pivots'], G._CTX['pk_lookback']
    ts_win = G._CTX['ts'][mask]
    day = float(G.active_config()['bgc_window_days'])

    # top-300 by avg_stop (proximity) from the real-gate grind — NO qty filter
    rows = db.execute('SELECT combo,n,avg_stop,avg_profit FROM bl_group_results_both '
                      'WHERE n>=2 AND avg_stop IS NOT NULL ORDER BY avg_stop ASC LIMIT %s', (TOPN,), fetch=True)
    bl = {r['combo']: r for r in rows}

    # materialize their signals as centroids
    for t in ('am_centroids', 'am_centroid_signals'):
        db.execute(f'''CREATE TABLE IF NOT EXISTS {t} ({"amc_pk BIGINT AUTO_INCREMENT PRIMARY KEY, amc_or_pk INT, amc_rank INT, amc_n_signals INT, amc_combo VARCHAR(160), amc_params TEXT, INDEX(amc_or_pk)" if t=="am_centroids" else "acs_pk BIGINT AUTO_INCREMENT PRIMARY KEY, acs_amc_pk BIGINT, acs_ts BIGINT, acs_dir TINYINT, INDEX(acs_amc_pk)"})''')
    old = db.execute('SELECT amc_pk FROM am_centroids WHERE amc_or_pk=%s', (OR_PK,), fetch=True)
    if old:
        ph = ','.join(['%s']*len(old))
        db.execute(f'DELETE FROM am_centroid_signals WHERE acs_amc_pk IN ({ph})', tuple(r['amc_pk'] for r in old))
        db.execute('DELETE FROM am_centroids WHERE amc_or_pk=%s', (OR_PK,))
    for rank, r in enumerate(sorted(rows, key=lambda r: r['avg_stop']), 1):
        vals = [int(x) for x in r['combo'].split(',')]
        states = [G._STATES[(NAMES[i], vals[i])] for i in range(len(NAMES))]
        trades = walk(G._refold(states), raw, px, piv, lb)
        sigs = [(int(ts_win[t['open_i']]), int(t['dir'])) for t in trades]
        db.execute('INSERT INTO am_centroids (amc_or_pk,amc_rank,amc_n_signals,amc_combo,amc_params) VALUES (%s,%s,%s,%s,%s)',
                   (OR_PK, rank, len(sigs), r['combo'], json.dumps({NAMES[i]: vals[i] for i in range(len(NAMES))})))
        amc = db.execute('SELECT LAST_INSERT_ID() i', fetch=True)[0]['i']
        if sigs:
            db.executemany('INSERT INTO am_centroid_signals (acs_amc_pk,acs_ts,acs_dir) VALUES (%s,%s,%s)',
                           [(amc, t, d) for t, d in sigs])

    # cluster score the 300
    scored = ClusterScoring(db, top_n=TOPN).score(OR_PK)     # in-memory rows survive the table drop

    # persist Excel-ready table: per-line cols + BL aggregates + cluster metrics
    db.execute(f'DROP TABLE IF EXISTS {TABLE}')
    db.execute(f'''CREATE TABLE {TABLE} (
        cs_rank INT, {', '.join(f'{n} INT' for n in NAMES)}, combo VARCHAR(160),
        n_signals INT, per_day FLOAT, avg_stop FLOAT, avg_profit FLOAT,
        swing_capture FLOAT, capture_per_1k FLOAT, win_pct FLOAT, total_net FLOAT)''')
    data = []
    for i, r in enumerate(scored, 1):
        vals = [int(x) for x in r['combo'].split(',')]
        b = bl.get(r['combo'], {})
        data.append([i, *vals, r['combo'], r['n_signals'],
                     round((b.get('n') or 0)/day, 2), b.get('avg_stop'), b.get('avg_profit'),
                     r['swing_capture'], r['capture_per_1k'], r['win_pct'], r['total_net']])
    cols = ['cs_rank', *NAMES, 'combo', 'n_signals', 'per_day', 'avg_stop', 'avg_profit',
            'swing_capture', 'capture_per_1k', 'win_pct', 'total_net']
    db.executemany(f"INSERT INTO {TABLE} ({','.join(cols)}) VALUES ({','.join(['%s']*len(cols))})", data)
    db.execute(f'DROP VIEW IF EXISTS v_{TABLE}')
    db.execute(f'CREATE VIEW v_{TABLE} AS SELECT * FROM {TABLE} ORDER BY total_net DESC')
    db.disconnect()
    print(f'{len(scored)} scored → table {TABLE} / view v_{TABLE}')
    print(f'  open in Excel: SELECT * FROM v_{TABLE};')
    print('  top 5 by net:')
    for r in sorted(scored, key=lambda r: -r['total_net'])[:5]:
        b = bl.get(r['combo'], {})
        print(f"    {r['combo']:<22} day{(b.get('n') or 0)/day:>5.1f} stop{b.get('avg_stop'):.3f} "
              f"win{r['win_pct']:>5.1f} net{r['total_net']:>6.1f} cap/1k{r['capture_per_1k']:>6.1f}")


if __name__ == '__main__':
    main()
