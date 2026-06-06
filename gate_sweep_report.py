#!/usr/bin/env python3
"""
gate_sweep_report — Scout A MVP.

Scores the CURRENT bny gate as a baseline, sweeps a modest grid against the
±threshold price partition, and prints the top combos by gate match score.
See gate_sweep_design.md.

MVP: in-code grid (itertools). TODO: wire ParameterGridBuilder + a gate-sweep tc
for the full ~10K Scout A.

  python3 gate_sweep_report.py --tp_pk=1 --lookback_days=1 --horizon=720
"""
import argparse
import numpy as np

from optimus9.db.database_manager import DatabaseManager
from optimus9.db.kline_loader import KlineLoader
from optimus9.config import get_db_config
from optimus9.compute.profit_partition import compute_profit_partition, summarize_partition
from optimus9.orchestration.gate_sweep_runner import run_sweep, score_combo, SCOUT_A_TEMPLATE

# Current bnyM/bnyp params (ic_pks 2,3) — the hand-tuned gate, our baseline.
BASELINE = dict(M_src='hl2', M_bb_len=58, M_bb_mult=1.24, p_src='ohlc4', p_k_len=21)
SOURCES  = ['close', 'hl2', 'hlc3', 'hlcc4', 'ohlc4']


def _fmt(r, n):
    go = r['gate_open'] / n * 100
    solo = '/'.join('%.3f' % x for x in r['solo_scores'])
    return (f"score {r['score']:.4f} | open {go:4.1f}% | hits {r['hits']:5d} "
            f"false {r['false_open']:5d} missed {r['missed']:6d} wrong {r['wrong_side']:4d} "
            f"| solo {solo}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tp_pk',         type=int,   default=1)
    ap.add_argument('--lookback_days', type=int,   default=1)
    ap.add_argument('--threshold',     type=float, default=0.9)
    ap.add_argument('--horizon',       type=int,   default=720)
    ap.add_argument('--top',           type=int,   default=12)
    a = ap.parse_args()

    db   = DatabaseManager(**get_db_config()); db.connect()
    base = KlineLoader(db).load_recent(a.tp_pk, a.lookback_days)
    n    = len(base)
    part = compute_profit_partition(base['close'].to_numpy(float),
                                    threshold_pct=a.threshold, horizon=a.horizon)
    P    = part['cls']
    s    = summarize_partition(P, part['mae_pct'], a.threshold)
    print(f'\nwindow {n:,} bars | tradeable {s["tradeable_frac"]*100:.1f}% '
          f'(long {s["long_frac"]*100:.1f} / short {s["short_frac"]*100:.1f} '
          f'/ neither {s["neither_frac"]*100:.1f})')

    bl = score_combo(BASELINE, SCOUT_A_TEMPLATE, base, P)
    print(f'\nBASELINE (current bny gate) {BASELINE}')
    print('  ' + _fmt(bl, n))

    combos = [dict(M_src=ms, M_bb_len=L, M_bb_mult=1.24, p_src=ps, p_k_len=k)
              for L  in (40, 50, 58, 70, 90)
              for k  in (13, 21, 34, 50)
              for ms in SOURCES
              for ps in SOURCES]
    print(f'\nsweeping {len(combos)} combos (M_bb_len × p_k_len × M_src × p_src; mult fixed 1.24)...')
    res = run_sweep(combos, SCOUT_A_TEMPLATE, base, P, progress=200)

    n_beat = sum(1 for r in res if not np.isnan(r['score']) and r['score'] > bl['score'])
    print(f'\n{n_beat}/{len(combos)} combos beat the baseline (score {bl["score"]:.4f}).')
    print(f'\nTOP {a.top} by gate match score:')
    for r in res[:a.top]:
        c = r['combo']
        beat = '  <== beats baseline' if (not np.isnan(r['score']) and r['score'] > bl['score']) else ''
        print(f"  M_len={c['M_bb_len']:>3} M_src={c['M_src']:6} p_k={c['p_k_len']:>2} "
              f"p_src={c['p_src']:6} | {_fmt(r, n)}{beat}")


if __name__ == '__main__':
    main()
