#!/usr/bin/env python3
"""
gate_validate — robustness of a gate config across windows x profit targets.

Scores raw (no gate) vs named gates by win-rate of admitted gca5m PKs, over
several lookback windows and ±thresholds. Built to catch overfitting: a gate
tuned on a short window often loses its edge over longer ones.

  python3 gate_validate.py --windows 7 14 28 --thresholds 0.6 0.9 1.2
"""
import argparse
import numpy as np

from optimus9.db.database_manager import DatabaseManager
from optimus9.db.kline_loader import KlineLoader
from optimus9.config import get_db_config
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.orchestration.gate_signal_sweep import (
    generate_gca5m_signals, label_winners, score_signals,
)


def _M(src, l, m):
    return dict(ic_itf_seconds=30, ic_line_type='bb', ic_src=src,
                ic_high_boundary=85, ic_low_boundary=15, ic_bb_len=l, ic_bb_mult=m)


def _P(src, k, r, s):
    return dict(ic_itf_seconds=30, ic_line_type='k', ic_src=src,
                ic_high_boundary=85, ic_low_boundary=15, ic_k_len=k, ic_rsi_len=r, ic_stc_len=s)


GATES = {
    'current':     (_M('hl2', 58, 1.24), _P('ohlc4', 21, 114, 105)),
    'cand-select': (_M('hl2', 58, 1.50), _P('ohlc4', 80, 50, 200)),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tp_pk', type=int, default=1)
    ap.add_argument('--windows', type=int, nargs='+', default=[7, 14, 28])
    ap.add_argument('--thresholds', type=float, nargs='+', default=[0.6, 0.9, 1.2])
    ap.add_argument('--horizon', type=int, default=720)
    a = ap.parse_args()

    db = DatabaseManager(**get_db_config()); db.connect()
    # generate signals once per window, score at each threshold
    per_win = {}
    for d in a.windows:
        base = KlineLoader(db).load_recent(a.tp_pk, d)
        close = base['close'].to_numpy(float)
        bars, dirs = generate_gca5m_signals(base, db)
        per_win[d] = (base, close, bars, dirs)

    for thr in a.thresholds:
        print(f'\n=== target +/-{thr}%  (edge = gate win-rate - raw) ===')
        print(f'{"win":>4} {"raw%":>6} | ' + ' | '.join(f'{n:>24}' for n in GATES))
        for d in a.windows:
            base, close, bars, dirs = per_win[d]
            win = label_winners(bars, dirs, close, thr, a.horizon)
            raw = win.mean() * 100
            row = f'{d:>3}d {raw:5.1f}% | '
            for n, (cM, cP) in GATES.items():
                g = IC._mask_from_configs([cM, cP], base, fold='OR')
                s = score_signals(g, bars, dirs, win)
                row += f'{s["win_rate"]*100:4.1f}% ({s["win_rate"]*100-raw:+4.1f}) adm{s["admitted"]:>5} | '
            print(row)


if __name__ == '__main__':
    main()
