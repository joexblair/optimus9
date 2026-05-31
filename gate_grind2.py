#!/usr/bin/env python3
"""
gate_grind2 — gate sweep v2: filter gca5m's 5s PK signals by profitability.

Scout A (--scout A): sweep bnyM {len,mult,src} + bnyp {k_len,src}.
Scout B (--scout B): bnyM anchored 58/1.50; sweep bnyp osc {k_len,rsi_len,stc_len}.

gca5m PKs are vote-aggregated (Pk5sGateComputer), winner = flat ±threshold%
(profit_partition), gate admits via sign-opposition. Reports raw ungated
win-rate (the bar), the current-gate baseline, and TWO rankings (F1 / win-rate).
See gate_sweep_design.md.

  python3 gate_grind2.py --scout=A --lookback_days=3 --threshold=0.6
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
    build_gate_configs, _build_resample_cache, _line_side, _fold,
    SCOUT_A_TEMPLATE, SCOUT_B_TEMPLATE,
)

# True current gate (for the reference baseline, always scored via Scout A template).
CURRENT = dict(M_src='hl2', M_bb_len=58, M_bb_mult=1.24, p_src='ohlc4', p_k_len=21)
SOURCES = ['close', 'hl2', 'hlc3', 'hlcc4', 'ohlc4']

# Scout A grid
A_M_LENS  = [40, 58, 80, 110, 150, 200]
A_M_MULTS = [0.3, 0.5, 0.74, 1.0, 1.5, 2.0]
A_P_KS    = [2, 3, 5, 8, 13, 21, 34, 55, 80, 110]
# Scout B grid (bnyp oscillator; M anchored in the template)
B_P_KS    = [2, 3, 5, 8, 13, 21, 34, 55, 80, 110]
B_P_RSI   = [30, 50, 70, 90, 114, 140, 170, 200]
B_P_STC   = [30, 50, 70, 90, 105, 130, 160, 200]


def scout_a_combos():
    return [dict(M_src=ms, M_bb_len=L, M_bb_mult=mu, p_src=ps, p_k_len=k)
            for L in A_M_LENS for mu in A_M_MULTS for ms in SOURCES
            for k in A_P_KS for ps in SOURCES]


def scout_b_combos():
    return [dict(p_k_len=k, p_rsi_len=r, p_stc_len=s)
            for k in B_P_KS for r in B_P_RSI for s in B_P_STC]


def _fmt(r):
    return (f"F1 {r['f1']:.3f} | win-rate {r['win_rate']*100:5.1f}% | "
            f"recall {r['recall']*100:5.1f}% | admitted {r['admitted']:4d}/{r['total']}")


def _label(c):
    return ' '.join(f'{k}={v}' for k, v in c.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--scout',         choices=['A', 'B'], default='A')
    ap.add_argument('--tp_pk',         type=int,   default=1)
    ap.add_argument('--lookback_days', type=int,   default=3)
    ap.add_argument('--threshold',     type=float, default=0.6)
    ap.add_argument('--horizon',       type=int,   default=720)
    ap.add_argument('--min_admit',     type=int,   default=50)
    ap.add_argument('--top',           type=int,   default=10)
    ap.add_argument('--csv',           default=None)
    a = ap.parse_args()

    template = SCOUT_A_TEMPLATE if a.scout == 'A' else SCOUT_B_TEMPLATE
    combos   = scout_a_combos() if a.scout == 'A' else scout_b_combos()
    csv_path = a.csv or f'gate_grind2_scout{a.scout}.csv'

    db    = DatabaseManager(**get_db_config()); db.connect()
    base  = KlineLoader(db).load_recent(a.tp_pk, a.lookback_days)
    close = base['close'].to_numpy(float)
    bars, dirs = generate_gca5m_signals(base, db)
    win = label_winners(bars, dirs, close, a.threshold, a.horizon)
    print(f'\n=== SCOUT {a.scout} | target ±{a.threshold}% | {a.lookback_days}d ===')
    print(f'gca5m signals: {len(bars):,} | raw winners (ungated): {int(win.sum()):,} '
          f'= {win.mean()*100:.1f}% win-rate (bar to beat)')

    cache = _build_resample_cache(SCOUT_A_TEMPLATE, base)
    bl_sides = [_line_side(cfg, base, cache) for cfg in build_gate_configs(CURRENT, SCOUT_A_TEMPLATE)]
    bl = score_signals(_fold(bl_sides, 'OR'), bars, dirs, win)
    print(f'\nBASELINE (current bny gate)\n  {_fmt(bl)}')

    print(f'\ngrinding {len(combos):,} combos (Scout {a.scout}, OR, sign-opposition)...')
    res = run_signal_sweep(combos, template, base, bars, dirs, win)

    def key_desc(v):
        return (np.isnan(v), -(0 if np.isnan(v) else v))
    by_f1 = sorted(res, key=lambda r: key_desc(r['f1']))
    by_wr = sorted([r for r in res if r['admitted'] >= a.min_admit], key=lambda r: key_desc(r['win_rate']))

    print(f'\n=== BALANCED — top {a.top} by F1 ===')
    for r in by_f1[:a.top]:
        print(f"  {_label(r['combo']):42} | {_fmt(r)}")
    print(f'\n=== SELECTIVE — top {a.top} by win-rate (≥{a.min_admit} admitted) ===')
    for r in by_wr[:a.top]:
        print(f"  {_label(r['combo']):42} | {_fmt(r)}")

    ckeys = list(res[0]['combo'].keys())
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(ckeys + ['f1', 'win_rate', 'recall', 'admitted', 'admitted_win', 'total', 'total_win'])
        for r in res:
            c = r['combo']
            w.writerow([c[k] for k in ckeys] +
                       [f"{r['f1']:.6f}", f"{r['win_rate']:.6f}", f"{r['recall']:.6f}",
                        r['admitted'], r['admitted_win'], r['total'], r['total_win']])
    print(f'\nwrote {len(res):,} rows -> {csv_path}')


if __name__ == '__main__':
    main()
