"""
gate_signal_sweep — gate sweep v2: the gate as a CLASSIFIER on 5s PK signals.

The bny30 gate (bnyM OR bnyP) admits a 5s PK signal where the signal's sign
opposes the filter's breach sign (sign-opposition, per pk_signal_detector). We
score how well a gate keeps the WINNING signals and sheds the losers — winner =
flat ±threshold% (profit_partition: the signal's dir is the partition class at
its bar). See gate_sweep_design.md.

Two rank metrics (both produced):
  - F1 of precision+recall on winners  → balanced gate
  - win-rate (= precision) of admitted  → selective gate (guard with min count)
"""
import numpy as np

from ..compute.indicator_computer import IndicatorComputer as IC
from ..compute.pk_state_computer import PKStateComputer
from ..compute.profit_partition import compute_profit_partition
from .gate_sweep_runner import (
    build_gate_configs, _build_resample_cache, _line_side, _fold,
)

# gca5m dialed centroid (2026-05-31): BB line close/len8/mult0.74; dema close/len2;
# pools c=7 w=33 range=6 slope_floor=17 multiplier=1.
GCA5M = dict(src='close', length=8, mult=0.74, dema_len=2, dema_src='close',
             pool_c=7, pool_w=33, pool_range=6, slope_floor=17, multiplier=1)


def generate_line_signals(base_df, cfg: dict = GCA5M):
    """Raw ungated PK transitions for a BB line across the close + wide pools.
    Returns (bars, dirs) int arrays; dir = sign(state) ∈ {±1} (PM ±2 → ±1)."""
    src  = IC.build_source(base_df, cfg['src'])
    line = IC.f_bb(src, int(cfg['length']), float(cfg['mult']))
    dema = IC.dema(IC.build_source(base_df, cfg['dema_src']), int(cfg['dema_len']))
    sc = PKStateComputer()
    bars, dirs = [], []
    for pool_bars in (int(cfg['pool_c']), int(cfg['pool_w'])):
        st    = sc.compute(line, dema, pool_bars, int(cfg['pool_range']),
                           int(cfg['multiplier']), float(cfg['slope_floor']))
        clean = np.where(np.isnan(st), 0.0, st)
        prev  = np.concatenate([[0.0], clean[:-1]])
        trans = (clean != 0.0) & ~np.isnan(st) & (clean != prev)   # transitions
        idx   = np.where(trans)[0]
        bars.extend(idx.tolist())
        dirs.extend(np.sign(st[idx]).astype(int).tolist())
    return np.array(bars, dtype=int), np.array(dirs, dtype=int)


def label_winners(bars, dirs, close, threshold: float = 0.9, horizon: int = 720):
    """Winner = the signal's dir equals the ±threshold% partition class at its
    bar (price reaches threshold in the signal's direction first)."""
    P = compute_profit_partition(np.asarray(close, dtype=float), threshold, horizon)['cls']
    return P[bars] == dirs


def score_signals(gate_mask, bars, dirs, win) -> dict:
    """Score a gate's filtering. Admitted = sign-opposition (gate[bar] == -dir).
    precision = admitted that win; recall = winners admitted; win_rate==precision."""
    admitted = gate_mask[bars] == -dirs
    pt = int(admitted.sum())
    pw = int((admitted & win).sum())
    tw = int(win.sum())
    prec = pw / pt if pt else float('nan')
    rec  = pw / tw if tw else 0.0
    if not pt:
        f1 = float('nan')
    elif (prec + rec) > 0:
        f1 = 2 * prec * rec / (prec + rec)
    else:
        f1 = 0.0
    return dict(precision=prec, recall=rec, f1=f1, win_rate=prec,
                admitted=pt, admitted_win=pw, total=int(len(bars)), total_win=tw)


def run_signal_sweep(combos, template, base_df, bars, dirs, win, fold='OR'):
    """Score every gate combo's filtering of the (bars, dirs) signals."""
    cache = _build_resample_cache(template, base_df)
    out = []
    for combo in combos:
        cfgs  = build_gate_configs(combo, template)
        sides = [_line_side(cfg, base_df, cache) for cfg in cfgs]
        gate  = _fold(sides, fold)
        r = score_signals(gate, bars, dirs, win)
        r['combo'] = combo
        out.append(r)
    return out
