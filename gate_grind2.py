#!/usr/bin/env python3
"""
gate_grind2 — gate sweep v2: filter gca5m's 5s PK signals by profitability.

Generates gca5m's raw ungated PKs once, labels winners (flat ±0.9% via
profit_partition), then sweeps bny30M/bny30p (OR) as a sign-opposition filter on
them. Reports the raw ungated win-rate, the current-gate baseline, and TWO
rankings: balanced (F1 of precision+recall on winners) and selective (win-rate,
min-admit guarded). See gate_sweep_design.md.

  python3 gate_grind2.py --tp_pk=1 --lookback_days=3 --horizon=720
"""
import argparse
import csv
import numpy as np

from optimus9.db.database_manager import DatabaseManager
from optimus9.db.kline_loader import KlineLoader
from optimus9.config import get_db_config
from optimus9.orchestration.gate_signal_sweep import (
    generate_gca5m_signals, label_winners, run_signal_sweep, score_signals,
)
from optimus9.orchestration.gate_sweep_runner import (
    build_gate_configs, _build_resample_cache, _line_side, _fold, SCOUT_A_TEMPLATE,
)

BASELINE = dict(M_src='hl2', M_bb_len=58, M_bb_mult=1.24, p_src='ohlc4', p_k_len=21)
SOURCES  = ['close', 'hl2', 'hlc3', 'hlcc4', 'ohlc4']
M_LENS   = [40, 58, 80, 110, 150, 200]
M_MULTS  = [0.5, 0.74, 1.0, 1.24, 1.5]
P_KS     = [3, 5, 8, 13, 21, 34, 55, 80]


def _fmt(r):
    return (f"F1 {r['f1']:.3f} | win-rate {r['win_rate']*100:5.1f}% | "
            f"recall {r['recall']*100:5.1f}% | admitted {r['admitted']:4d}/{r['total']}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tp_pk',         type=int,   default=1)
    ap.add_argument('--lookback_days', type=int,   default=3)
    ap.add_argument('--threshold',     type=float, default=0.9)
    ap.add_argument('--horizon',       type=int,   default=720)
    ap.add_argument('--min_admit',     type=int,   default=50)
    ap.add_argument('--top',           type=int,   default=12)
    ap.add_argument('--csv',           default='gate_grind2.csv')
    a = ap.parse_args()

    db    = DatabaseManager(**get_db_config()); db.connect()
    base  = KlineLoader(db).load_recent(a.tp_pk, a.lookback_days)
    close = base['close'].to_numpy(float)
    bars, dirs = generate_gca5m_signals(base, db)
    win = label_winners(bars, dirs, close, a.threshold, a.horizon)
    raw_wr = win.mean()
    print(f'\ngca5m signals: {len(bars):,} | raw winners (ungated): {int(win.sum()):,} '
          f'= {raw_wr*100:.1f}% win-rate (this is the bar to beat)')

    cache = _build_resample_cache(SCOUT_A_TEMPLATE, base)
    def gate_for(combo):
        sides = [_line_side(cfg, base, cache) for cfg in build_gate_configs(combo, SCOUT_A_TEMPLATE)]
        return _fold(sides, 'OR')

    bl = score_signals(gate_for(BASELINE), bars, dirs, win)
    print(f'\nBASELINE (current bny gate) {BASELINE}\n  {_fmt(bl)}')

    combos = [dict(M_src=ms, M_bb_len=L, M_bb_mult=mu, p_src=ps, p_k_len=k)
              for L in M_LENS for mu in M_MULTS for ms in SOURCES
              for k in P_KS for ps in SOURCES]
    print(f'\ngrinding {len(combos):,} gate combos (sign-opposition filter, OR)...')
    res = run_signal_sweep(combos, SCOUT_A_TEMPLATE, base, bars, dirs, win)

    def key_desc(v):
        return (np.isnan(v), -(0 if np.isnan(v) else v))
    by_f1 = sorted(res, key=lambda r: key_desc(r['f1']))
    by_wr = sorted([r for r in res if r['admitted'] >= a.min_admit],
                   key=lambda r: key_desc(r['win_rate']))

    print(f'\n=== BALANCED — top {a.top} by F1 ===')
    for r in by_f1[:a.top]:
        c = r['combo']
        print(f"  M={c['M_bb_len']:>3}/{c['M_bb_mult']:.2f}/{c['M_src']:5} "
              f"p={c['p_k_len']:>2}/{c['p_src']:5} | {_fmt(r)}")
    print(f'\n=== SELECTIVE — top {a.top} by win-rate (≥{a.min_admit} admitted) ===')
    for r in by_wr[:a.top]:
        c = r['combo']
        print(f"  M={c['M_bb_len']:>3}/{c['M_bb_mult']:.2f}/{c['M_src']:5} "
              f"p={c['p_k_len']:>2}/{c['p_src']:5} | {_fmt(r)}")

    with open(a.csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['M_bb_len', 'M_bb_mult', 'M_src', 'p_k_len', 'p_src',
                    'f1', 'win_rate', 'recall', 'admitted', 'admitted_win', 'total', 'total_win'])
        for r in res:
            c = r['combo']
            w.writerow([c['M_bb_len'], c['M_bb_mult'], c['M_src'], c['p_k_len'], c['p_src'],
                        f"{r['f1']:.6f}", f"{r['win_rate']:.6f}", f"{r['recall']:.6f}",
                        r['admitted'], r['admitted_win'], r['total'], r['total_win']])
    print(f'\nwrote {len(res):,} rows -> {a.csv}')


if __name__ == '__main__':
    main()
