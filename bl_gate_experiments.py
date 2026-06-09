"""
bl_gate_experiments — run the 8-line fold under 4 bny30 gate modes, persist each,
and materialise each mode's top candidates as am_centroids so cluster_scoring can
score them (run.py cluster_score --or_pk 900X).

Line-states are gate-INDEPENDENT (the gate only filters the 5s PK fed to walk()), so
we precompute the 24 states ONCE, then re-eval per mode by swapping _CTX['raw_pk'].

  mode   gate  components      or_pk  table
  off    no    -              9001   bl_group_results_off
  M      yes   bny30M (BB)    9002   bl_group_results_M
  p      yes   bny30p (K)     9003   bl_group_results_p
  both   yes   bny30M+bny30p  9004   bl_group_results_both
"""
import sys, json
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration import bl_group_grind as G
from optimus9.orchestration.gate_signal_sweep import pine_aligned_signals
from optimus9.analysis.bl_detect import GCA5M_RAW
from optimus9.analysis.bl_grind import walk

MODES = [   # name, or_pk, gate, gate_bb, gate_k
    ('off',  9001, False, False, False),
    ('M',    9002, True,  True,  False),
    ('p',    9003, True,  False, True),
    ('both', 9004, True,  True,  True),
]
CAND_BY_STOP = 30      # top-N by lowest avg_stop (proximity)
CAND_BY_N    = 12      # plus top-N by lowest qty (smallest n) — cover both objective axes


def raw_pk_for(base, db, gate, gate_bb, gate_k, mask):
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=gate,
                                     gate_bb=gate_bb, gate_k=gate_k)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    return full[mask]


def candidates(res):
    ok = [r for r in res if r['n'] and r['n'] >= 2 and r['avg_stop'] is not None]
    by_stop = sorted(ok, key=lambda r: r['avg_stop'])[:CAND_BY_STOP]
    by_n    = sorted(ok, key=lambda r: r['n'])[:CAND_BY_N]
    seen, out = set(), []
    for r in by_stop + by_n:
        if r['combo'] not in seen:
            seen.add(r['combo']); out.append(r)
    return out


def materialize(db, or_pk, cands, raw_pk):
    names = G._CTX['names']; ts_win = G._CTX['ts'][G._CTX['mask']]
    px, piv, lb = G._CTX['px'], G._CTX['pivots'], G._CTX['pk_lookback']
    db.execute('''CREATE TABLE IF NOT EXISTS am_centroids (amc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        amc_or_pk INT, amc_rank INT, amc_n_signals INT, amc_combo VARCHAR(160), amc_params TEXT, INDEX(amc_or_pk))''')
    db.execute('''CREATE TABLE IF NOT EXISTS am_centroid_signals (acs_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        acs_amc_pk BIGINT, acs_ts BIGINT, acs_dir TINYINT, INDEX(acs_amc_pk))''')
    old = db.execute('SELECT amc_pk FROM am_centroids WHERE amc_or_pk=%s', (or_pk,), fetch=True)
    if old:
        ph = ','.join(['%s']*len(old))
        db.execute(f'DELETE FROM am_centroid_signals WHERE acs_amc_pk IN ({ph})', tuple(r['amc_pk'] for r in old))
        db.execute('DELETE FROM am_centroids WHERE amc_or_pk=%s', (or_pk,))
    n_sig_total = 0
    for rank, r in enumerate(cands, 1):
        vals = [int(x) for x in r['combo'].split(',')]
        states = [G._STATES[(names[i], vals[i])] for i in range(len(names))]
        trades = walk(G._refold(states), raw_pk, px, piv, lb)
        sigs = [(int(ts_win[t['open_i']]), int(t['dir'])) for t in trades]
        params = {names[i]: vals[i] for i in range(len(names))}
        db.execute('''INSERT INTO am_centroids (amc_or_pk,amc_rank,amc_n_signals,amc_combo,amc_params)
                      VALUES (%s,%s,%s,%s,%s)''', (or_pk, rank, len(sigs), r['combo'], json.dumps(params)))
        amc = db.execute('SELECT LAST_INSERT_ID() i', fetch=True)[0]['i']
        if sigs:
            db.executemany('INSERT INTO am_centroid_signals (acs_amc_pk,acs_ts,acs_dir) VALUES (%s,%s,%s)',
                           [(amc, t, d) for t, d in sigs])
        n_sig_total += len(sigs)
    return len(cands), n_sig_total


def main():
    G.prepare()
    G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    wd = float(G.active_config()['bgc_window_days'])
    print(f"\n{'mode':<6}{'or_pk':>6}{'combos':>8}{'n_med':>8}{'~/day':>7}{'stop_med':>9}{'best_stop':>10}{'cands':>7}{'sigs':>7}")
    for name, or_pk, gate, gbb, gk in MODES:
        G._CTX['raw_pk'] = raw_pk_for(base, db, gate, gbb, gk, mask)
        res = G.run_round()
        G.persist(res, table=f'bl_group_results_{name}')
        ok = [r for r in res if r['n'] and r['avg_stop'] is not None]
        nn = np.array([r['n'] for r in ok]); st = np.array([r['avg_stop'] for r in ok])
        nmed = np.median(nn); best = min(ok, key=lambda r: (r['n'] < 4, r['avg_stop']))
        cands = candidates(res)
        nc, ns = materialize(db, or_pk, cands, G._CTX['raw_pk'])
        print(f"{name:<6}{or_pk:>6}{len(res):>8}{nmed:>8.0f}{nmed/wd:>7.1f}"
              f"{np.median(st):>9.3f}{best['avg_stop']:>10.3f}{nc:>7}{ns:>7}")
    db.disconnect()
    print("\nmaterialized → run.py cluster_score --or_pk 9001/9002/9003/9004")


if __name__ == '__main__':
    main()
