"""
slow4_validate — materialise the gate-M · slow-4 subset's top candidates as centroids
(or_pk 9005) so cluster_scoring can confirm win%/net behind the 0.858 stop.
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

SLOW4 = ['hb15b', 'hb9b', 'hs15r', 'hs9r']
OR_PK = 9005
DAY = 9.0


def main():
    G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=False)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw = full[mask]
    px, piv, lb, lens = G._CTX['px'], G._CTX['pivots'], G._CTX['pk_lookback'], G._CTX['lens']
    ts_win = G._CTX['ts'][mask]

    rows = []
    for vals in itertools.product(*[lens[n] for n in SLOW4]):
        st = [G._STATES[(n, v)] for n, v in zip(SLOW4, vals)]
        comb = G._refold(st)
        trades = walk(comb, raw, px, piv, lb)
        s = _summary(trades)
        if s.get('n'):
            rows.append((vals, s['n'], s['avg_stop'], trades))
    rows.sort(key=lambda r: r[2])                    # by stop asc
    cands = rows[:30]

    for t in ('am_centroids', 'am_centroid_signals'):
        db.execute(f'''CREATE TABLE IF NOT EXISTS {t} ({"amc_pk BIGINT AUTO_INCREMENT PRIMARY KEY, amc_or_pk INT, amc_rank INT, amc_n_signals INT, amc_combo VARCHAR(160), amc_params TEXT, INDEX(amc_or_pk)" if t=="am_centroids" else "acs_pk BIGINT AUTO_INCREMENT PRIMARY KEY, acs_amc_pk BIGINT, acs_ts BIGINT, acs_dir TINYINT, INDEX(acs_amc_pk)"})''')
    old = db.execute('SELECT amc_pk FROM am_centroids WHERE amc_or_pk=%s', (OR_PK,), fetch=True)
    if old:
        ph = ','.join(['%s'] * len(old))
        db.execute(f'DELETE FROM am_centroid_signals WHERE acs_amc_pk IN ({ph})', tuple(r['amc_pk'] for r in old))
        db.execute('DELETE FROM am_centroids WHERE amc_or_pk=%s', (OR_PK,))
    for rank, (vals, n, stop, trades) in enumerate(cands, 1):
        sigs = [(int(ts_win[t['open_i']]), int(t['dir'])) for t in trades]
        params = {SLOW4[i]: vals[i] for i in range(len(SLOW4))}
        db.execute('INSERT INTO am_centroids (amc_or_pk,amc_rank,amc_n_signals,amc_combo,amc_params) VALUES (%s,%s,%s,%s,%s)',
                   (OR_PK, rank, len(sigs), ','.join(map(str, vals)), json.dumps(params)))
        amc = db.execute('SELECT LAST_INSERT_ID() i', fetch=True)[0]['i']
        if sigs:
            db.executemany('INSERT INTO am_centroid_signals (acs_amc_pk,acs_ts,acs_dir) VALUES (%s,%s,%s)',
                           [(amc, t, d) for t, d in sigs])
    db.disconnect()
    print(f'materialized {len(cands)} slow4 candidates → or_pk {OR_PK}  '
          f'(best stop {cands[0][2]:.3f} @ {cands[0][1]/DAY:.1f}/d, combo {",".join(map(str,cands[0][0]))})')


if __name__ == '__main__':
    main()
