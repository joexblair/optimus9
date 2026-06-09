"""
analyze_gate_experiments — merge the 4 gate datasets (bl_group_results_<mode>) with
their cluster_scores, and surface the objective: trades CLOSEST to swings with the
SMALLEST qty (fees/slippage). Persists gate_experiment_summary for later inspection.

Objective lenses:
  bl_stop        — avg adverse excursion to next swing (proximity; lower=closer).
  per_day        — qty (lower=cheaper fees/slippage).
  capture_per_1k — cluster swing-capture EFFICIENCY, volume stripped (higher=better).
  win_pct/net    — decided win rate / net %.
We want LOW per_day + LOW bl_stop + HIGH capture_per_1k — a balance, not all three.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.cluster_scoring import ClusterScoring

MODES = [('off', 9001), ('M', 9002), ('p', 9003), ('both', 9004)]
DAY = 9.0


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    cs = ClusterScoring(db, top_n=42)
    allrows = {}
    for name, pk in MODES:
        rows = cs.score(pk)                       # full ranked list (survives the table drop)
        bl = {r['combo']: r for r in db.execute(
            f'SELECT combo,n,avg_stop,avg_profit FROM bl_group_results_{name}', fetch=True)}
        for r in rows:
            b = bl.get(r['combo'], {})
            r['bl_n'] = b.get('n'); r['bl_stop'] = b.get('avg_stop'); r['bl_profit'] = b.get('avg_profit')
            r['per_day'] = (b.get('n') or 0) / DAY
        allrows[name] = rows

    # persist a tidy combined summary
    db.execute('''CREATE TABLE IF NOT EXISTS gate_experiment_summary (
        ges_pk BIGINT AUTO_INCREMENT PRIMARY KEY, mode VARCHAR(8), cs_rank INT, combo VARCHAR(160),
        bl_n INT, per_day FLOAT, bl_stop FLOAT, bl_profit FLOAT,
        swing_capture FLOAT, capture_per_1k FLOAT, win_pct FLOAT, total_net FLOAT)''')
    db.execute('DELETE FROM gate_experiment_summary')
    data = []
    for name, _ in MODES:
        for i, r in enumerate(allrows[name], 1):
            data.append((name, i, r['combo'], r['bl_n'], r['per_day'], r['bl_stop'], r['bl_profit'],
                         r['swing_capture'], r['capture_per_1k'], r['win_pct'], r['total_net']))
    db.executemany('''INSERT INTO gate_experiment_summary
        (mode,cs_rank,combo,bl_n,per_day,bl_stop,bl_profit,swing_capture,capture_per_1k,win_pct,total_net)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', data)

    W = 96
    print('\n' + '=' * W)
    print('GATE EXPERIMENTS — per-mode best by each lens  (candidates = top-42 by BL proximity/qty)')
    print('=' * W)
    for name, pk in MODES:
        rows = allrows[name]
        pds = np.array([r['per_day'] for r in rows], float)
        sts = np.array([r['bl_stop'] for r in rows if r['bl_stop'] is not None], float)
        print(f'\n── {name} (or_pk {pk}) — {len(rows)} candidates · '
              f'per_day {pds.min():.1f}–{pds.max():.1f} · bl_stop {sts.min():.3f}–{sts.max():.3f}')
        for lens, key, rev in [('closest to swing (min bl_stop)', 'bl_stop', False),
                               ('smallest qty (min per_day)', 'per_day', False),
                               ('most efficient (max capture_per_1k)', 'capture_per_1k', True),
                               ('best net (max total_net)', 'total_net', True)]:
            cand = [r for r in rows if r.get(key) is not None]
            b = sorted(cand, key=lambda r: r[key], reverse=rev)[0]
            print(f'   {lens:<38} combo {b["combo"]:<24} '
                  f'day{b["per_day"]:>5.1f} stop{b["bl_stop"]:>6.3f} '
                  f'cap/1k{b["capture_per_1k"]:>7.1f} win%{b["win_pct"]:>5.1f} net{b["total_net"]:>6.1f}')

    # cross-mode balance: rank all candidates by a simple balance of low qty + low stop + high efficiency
    print('\n' + '=' * W)
    print('BALANCE PICKS — normalized (low per_day + low bl_stop + high capture_per_1k), across all modes')
    print('=' * W)
    pool = [(name, r) for name, _ in MODES for r in allrows[name]
            if r['bl_stop'] is not None and r['per_day'] > 0]
    pd_a = np.array([r['per_day'] for _, r in pool]); st_a = np.array([r['bl_stop'] for _, r in pool])
    cp_a = np.array([r['capture_per_1k'] for _, r in pool])
    def z(a): return (a - a.mean()) / (a.std() + 1e-9)
    score = -z(pd_a) - z(st_a) + z(cp_a)          # higher = better balance
    order = np.argsort(-score)
    print(f'{"rk":>3} {"mode":>5} {"combo":<24} {"day":>6} {"stop":>6} {"cap/1k":>7} {"win%":>5} {"net":>6} {"bal":>6}')
    for rk, j in enumerate(order[:15], 1):
        name, r = pool[j]
        print(f'{rk:>3} {name:>5} {r["combo"]:<24} {r["per_day"]:>6.1f} {r["bl_stop"]:>6.3f} '
              f'{r["capture_per_1k"]:>7.1f} {r["win_pct"]:>5.1f} {r["total_net"]:>6.1f} {score[j]:>6.2f}')
    db.disconnect()
    print('\nsummary persisted → gate_experiment_summary')


if __name__ == '__main__':
    main()
