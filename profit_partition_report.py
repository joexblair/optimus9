#!/usr/bin/env python3
"""
profit_partition_report — Stage 0 saturation check + MAE histogram.

Loads klines for a tp_pk over a window, runs the ±threshold profit partition
(compute/profit_partition.py), and prints:
  - class fractions (long / short / neither)   ← the saturation check
  - winner-MAE percentiles                      ← the empirical stop floor
  - a text histogram of winner MAEs

See gate_sweep_design.md. Pure read; no DB writes.

  python3 profit_partition_report.py --tp_pk=1 --lookback_days=4 --horizon=720
"""
import argparse
import numpy as np

from optimus9.db.database_manager import DatabaseManager
from optimus9.db.kline_loader import KlineLoader
from optimus9.config import get_db_config
from optimus9.compute.profit_partition import (
    compute_profit_partition, summarize_partition,
)


def _text_hist(winners: np.ndarray, threshold: float, bins: int = 18,
               width: int = 50) -> str:
    if winners.size == 0:
        return '  (no winners)'
    counts, edges = np.histogram(winners, bins=bins, range=(0.0, threshold))
    peak = counts.max() or 1
    out = []
    for k in range(bins):
        bar = '#' * int(round(width * counts[k] / peak))
        out.append(f'  {edges[k]:5.2f}-{edges[k+1]:5.2f}% | {counts[k]:8,} {bar}')
    return '\n'.join(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--tp_pk',         type=int,   default=1)
    ap.add_argument('--lookback_days', type=int,   default=4)
    ap.add_argument('--threshold',     type=float, default=0.9)
    ap.add_argument('--horizon',       type=int,   default=720,
                    help='bars (5s) to wait for the move; 720 = 1h')
    ap.add_argument('--csv', default=None, help='optional path to dump winner MAEs')
    a = ap.parse_args()

    db = DatabaseManager(**get_db_config()); db.connect()
    df    = KlineLoader(db).load_recent(a.tp_pk, a.lookback_days)
    close = df['close'].to_numpy(dtype=float)
    n     = len(close)
    t0, t1 = int(df['timestamp'].iloc[0]), int(df['timestamp'].iloc[-1])

    r = compute_profit_partition(close, threshold_pct=a.threshold, horizon=a.horizon)
    s = summarize_partition(r['cls'], r['mae_pct'], threshold_pct=a.threshold)

    print(f'\n=== profit partition  tp_pk={a.tp_pk}  +/-{a.threshold}%  '
          f'horizon={a.horizon} bars ({a.horizon*5/60:.0f} min) ===')
    print(f'window: {n:,} bars  ({(t1 - t0) / 86_400_000:.1f} days)')

    print('\nSATURATION CHECK (can the gate discriminate?)')
    print(f'  long-P    : {s["long_frac"]*100:6.2f}%')
    print(f'  short-P   : {s["short_frac"]*100:6.2f}%')
    print(f'  neither   : {s["neither_frac"]*100:6.2f}%')
    print(f'  tradeable : {s["tradeable_frac"]*100:6.2f}%   '
          f'<- want a discriminating band, not ~5% or ~95%')

    print(f'\nWINNER-MAE (empirical stop floor, bounded <{a.threshold}%)')
    if s['mae_pct']:
        for p in (50, 75, 90, 95, 99):
            print(f'  p{p:<2}: {s["mae_pct"][p]:.3f}%')
        print(f'  mean: {s["mae_mean"]:.3f}%')

    print('\nMAE histogram (winners):')
    winners = r['mae_pct'][~np.isnan(r['mae_pct'])]
    print(_text_hist(winners, a.threshold))

    if a.csv:
        np.savetxt(a.csv, winners, fmt='%.6f', header='winner_mae_pct')
        print(f'\nwrote {winners.size:,} winner MAEs -> {a.csv}')


if __name__ == '__main__':
    main()
