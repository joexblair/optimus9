#!/usr/bin/env python3
"""
gate_grind — Scout A gate sweep (bny30M lengths/mult/src × bny30p k_len/src).

Scores each combo's OR-folded gate against the forward-walk "≥0.9% reachable
from here" target mask (direction-agnostic IoU + recall/precision), ranks them,
prints baseline (current bny gate) vs top-N, writes a CSV. See
gate_sweep_design.md.

MVP grid is in-code (~10K). Resample is cached, so it runs in a couple of min.

  python3 gate_grind.py --tp_pk=1 --lookback_days=3 --horizon=720 --csv=gate_grindA.csv
"""
import argparse
import csv
import numpy as np

from optimus9.db.database_manager import DatabaseManager
from optimus9.db.kline_loader import KlineLoader
from optimus9.config import get_db_config
from optimus9.compute.profit_partition import compute_profit_partition
from optimus9.orchestration.gate_sweep_runner import run_sweep, score_combo, SCOUT_A_TEMPLATE

BASELINE = dict(M_src='hl2', M_bb_len=58, M_bb_mult=1.24, p_src='ohlc4', p_k_len=21)
SOURCES  = ['close', 'hl2', 'hlc3', 'hlcc4', 'ohlc4']
# Ranges extended after the first 1d grind pinned the optimum at the edges
# (wanted longer M_bb_len, lower mult, shorter p_k than the 58/1.24/21 centre).
M_LENS   = [40, 60, 80, 100, 130, 160, 200, 240]
M_MULTS  = [0.3, 0.5, 0.74, 1.0, 1.5]
P_KS     = [3, 5, 8, 13, 21, 34, 55, 80]


def _fmt(r, n):
    return (f"IoU {r['score']:.4f} | recall {r['recall']*100:5.1f}% | "
            f"precision {r['precision']*100:5.1f}% | open {r['open']/n*100:5.1f}% | "
            f"solo {'/'.join('%.3f' % x for x in r['solo_scores'])}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tp_pk',         type=int,   default=1)
    ap.add_argument('--lookback_days', type=int,   default=3)
    ap.add_argument('--threshold',     type=float, default=0.9)
    ap.add_argument('--horizon',       type=int,   default=720)
    ap.add_argument('--top',           type=int,   default=20)
    ap.add_argument('--csv',           default='gate_grindA.csv')
    a = ap.parse_args()

    db   = DatabaseManager(**get_db_config()); db.connect()
    base = KlineLoader(db).load_recent(a.tp_pk, a.lookback_days)
    n    = len(base)
    tgt  = compute_profit_partition(base['close'].to_numpy(float),
                                    threshold_pct=a.threshold, horizon=a.horizon)['cls'] != 0
    print(f'\nwindow {n:,} bars (~{a.lookback_days}d) | target ≥{a.threshold}% reachable: '
          f'{tgt.mean()*100:.1f}% of bars')

    bl = score_combo(BASELINE, SCOUT_A_TEMPLATE, base, tgt)
    print(f'\nBASELINE (current bny gate) {BASELINE}')
    print('  ' + _fmt(bl, n))

    combos = [dict(M_src=ms, M_bb_len=L, M_bb_mult=mu, p_src=ps, p_k_len=k)
              for L  in M_LENS for mu in M_MULTS for ms in SOURCES
              for k  in P_KS   for ps in SOURCES]
    print(f'\ngrinding {len(combos):,} combos (OR-folded, vs reachable mask)...')
    res = run_sweep(combos, SCOUT_A_TEMPLATE, base, tgt, progress=2000)

    n_beat = sum(1 for r in res if not np.isnan(r['score']) and r['score'] > bl['score'])
    print(f'\n{n_beat:,}/{len(combos):,} combos beat the baseline (IoU {bl["score"]:.4f}).')
    print(f'\nTOP {a.top} by IoU:')
    for r in res[:a.top]:
        c = r['combo']
        beat = '  <== beats baseline' if r['score'] > bl['score'] else ''
        print(f"  M_len={c['M_bb_len']:>3} mult={c['M_bb_mult']:.2f} M_src={c['M_src']:6} "
              f"p_k={c['p_k_len']:>3} p_src={c['p_src']:6} | {_fmt(r, n)}{beat}")

    with open(a.csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['M_bb_len', 'M_bb_mult', 'M_src', 'p_k_len', 'p_src',
                    'iou', 'recall', 'precision', 'open', 'solo_M', 'solo_p'])
        for r in res:
            c = r['combo']
            w.writerow([c['M_bb_len'], c['M_bb_mult'], c['M_src'], c['p_k_len'], c['p_src'],
                        f"{r['score']:.6f}", f"{r['recall']:.6f}", f"{r['precision']:.6f}",
                        r['open'], f"{r['solo_scores'][0]:.6f}", f"{r['solo_scores'][1]:.6f}"])
    print(f'\nwrote {len(res):,} rows -> {a.csv}')


if __name__ == '__main__':
    main()
