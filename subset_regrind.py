"""
subset_regrind — pick-and-mix: under gate-M, re-grind several BL line SUBSETS over
their own len brackets, and map each subset's (qty, proximity) Pareto frontier. A
subset deserves its own best combo (the leave-N-out used the full-8's combo), so this
re-optimises per subset and asks: which pick gives the tightest stop nearest ~10/day?
"""
import sys, itertools
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration import bl_group_grind as G
from optimus9.orchestration.gate_signal_sweep import pine_aligned_signals
from optimus9.analysis.bl_detect import GCA5M_RAW
from optimus9.analysis.bl_grind import walk, _summary

DAY = 9.0
SUBSETS = {
    'full8':      ['b6b', 'hb15b', 'hb9b', 'hs15r', 'hs9r', 's18b', 's30r', 's90b'],
    'drop_b6b':   ['hb15b', 'hb9b', 'hs15r', 'hs9r', 's18b', 's30r', 's90b'],
    'drop_s90b':  ['b6b', 'hb15b', 'hb9b', 'hs15r', 'hs9r', 's18b', 's30r'],
    'slow4':      ['hb15b', 'hb9b', 'hs15r', 'hs9r'],
    'slow4+s30r': ['hb15b', 'hb9b', 'hs15r', 'hs9r', 's30r'],
    'prox_core':  ['hb9b', 'hs15r', 's18b', 's30r'],
}


def main():
    G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=False)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw = full[mask]; db.disconnect()
    px, piv, lb, lens = G._CTX['px'], G._CTX['pivots'], G._CTX['pk_lookback'], G._CTX['lens']

    def evalc(subset, vals):
        st = [G._STATES[(n, v)] for n, v in zip(subset, vals)]
        s = _summary(walk(G._refold(st), raw, px, piv, lb))
        return s

    print('\n' + '=' * 84)
    print('PICK-AND-MIX — per-subset (qty, proximity) frontier under gate-M')
    print('=' * 84)
    print(f'{"subset":<12}{"combos":>7}{"  best-stop combo":<26}{"day":>6}{"stop":>7}{"prof":>7}'
          f'   |  ~10/d pick: stop / day')
    for name, subset in SUBSETS.items():
        grids = [lens[n] for n in subset]
        rows = []
        for vals in itertools.product(*grids):
            s = evalc(subset, vals)
            if s.get('n'):
                rows.append((vals, s['n'] / DAY, s['avg_stop'], s.get('avg_profit') or 0))
        if not rows:
            print(f'{name:<12} no trades'); continue
        best_stop = min(rows, key=lambda r: r[2])
        # ~10/day pick: lowest stop among combos with per_day in [8,13]
        band = [r for r in rows if 8 <= r[1] <= 13]
        pick = min(band, key=lambda r: r[2]) if band else min(rows, key=lambda r: abs(r[1] - 10))
        bc = ','.join(map(str, best_stop[0]))
        print(f'{name:<12}{len(rows):>7}  {bc:<24}{best_stop[1]:>6.1f}{best_stop[2]:>7.3f}{best_stop[3]:>7.3f}'
              f'   |  {pick[2]:.3f} / {pick[1]:.1f}/d  [{",".join(map(str,pick[0]))}]')
    print('\n(stop = avg adverse-excursion to next swing; lower+fewer = the objective)')


if __name__ == '__main__':
    main()
