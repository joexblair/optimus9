"""
leave_n_out — under the gate-M (bny30M) regime, probe which BL lines are influencers
vs redundant with the gate. For a reference combo (best-balance M), measure:
  • LOO  — remove each line, re-fold the rest, re-walk → n/day, stop, profit.
  • overlap — fraction of a line's state==3 (completion) bars that coincide with a
              gated PK within lookback (high ⇒ the line completes when the gate is
              already admitting — redundant with bny30, Joe's "overlap" cue).
  • group drops — the 30s pair (s30r,s90b, same TF as the 30s gate) and the
                  highest-overlap pair, removed together.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration import bl_group_grind as G
from optimus9.orchestration.gate_signal_sweep import pine_aligned_signals
from optimus9.analysis.bl_detect import GCA5M_RAW
from optimus9.analysis.bl_grind import walk, _summary

REF = {'b6b': 4, 'hb15b': 3, 'hb9b': 5, 'hs15r': 2, 'hs9r': 2, 's18b': 12, 's30r': 4, 's90b': 17}
TF  = {'b6b': 360, 'hb15b': 900, 'hb9b': 540, 'hs15r': 900, 'hs9r': 540, 's18b': 360, 's30r': 30, 's90b': 30}
DAY = 9.0


def main():
    G.prepare(); G.precompute()
    db = DatabaseManager(**get_db_config()); db.connect()
    base, mask = G._CTX['base'], G._CTX['mask']
    idx, dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=False)
    full = np.zeros(len(mask), np.int8); full[idx] = dirs
    raw = full[mask]
    db.disconnect()
    names = G._CTX['names']; px = G._CTX['px']; piv = G._CTX['pivots']; lb = G._CTX['pk_lookback']

    def fw(subset):
        st = [G._STATES[(n, REF[n])] for n in subset]
        if not st:
            return {'n': 0}
        return _summary(walk(G._refold(st), raw, px, piv, lb))

    def overlap(n):
        st = G._STATES[(n, REF[n])]; done = np.where(st == 3)[0]
        if len(done) == 0:
            return 0.0, 0
        hit = sum(1 for i in done if np.any(raw[max(0, i - lb):i + 1] != 0))
        return hit / len(done), len(done)

    def row(tag, r, extra=''):
        if not r.get('n'):
            print(f'  {tag:<22} n0'); return
        print(f'  {tag:<22} n{r["n"]:>4} ({r["n"]/DAY:>5.1f}/d)  stop {r["avg_stop"]:.3f}  '
              f'prof {r["avg_profit"] if r["avg_profit"] else 0:.3f}{extra}')

    print('\n' + '=' * 80)
    print(f'LEAVE-N-OUT under gate-M · ref combo {",".join(str(REF[n]) for n in names)}')
    print('=' * 80)
    base_r = fw(names)
    row('FULL (8 lines)', base_r)

    print('\nleave-one-out (Δ vs full):')
    loo = []
    for n in names:
        r = fw([x for x in names if x != n]); ov, nd = overlap(n)
        d = (r.get('n', 0) - base_r['n']) / DAY
        loo.append((n, r, ov))
        row(f'−{n} (TF{TF[n]})', r, f'  Δ{d:+.1f}/d  overlap {ov:.2f} ({nd} done)')

    print('\ngroup drops:')
    row('−30s pair (s30r,s90b)', fw([x for x in names if x not in ('s30r', 's90b')]))
    hi = sorted(loo, key=lambda t: -t[2])[:2]
    pair = [t[0] for t in hi]
    row(f'−hi-overlap ({",".join(pair)})', fw([x for x in names if x not in pair]))
    # keep only the slow lines (drop all 3 of the fastest TFs: both 30s + the 360s)
    slow = [n for n in names if TF[n] >= 540]
    row(f'slow-only ({",".join(slow)})', fw(slow))
    db = None
    print('\n(reference-combo probe — promising subsets warrant their own re-grind)')


if __name__ == '__main__':
    main()
