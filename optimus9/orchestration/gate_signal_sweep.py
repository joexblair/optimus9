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
from ..compute.pk5s_gate_computer import Pk5sGateComputer
from ..compute.profit_partition import compute_profit_partition
from .gate_sweep_runner import (
    build_gate_configs, _build_resample_cache, _line_side, _fold,
)

# gca5m dialed centroid (2026-05-31): BB line close/len8/mult0.74; dema close/len2;
# pools c=7 w=33 range=6 slope_floor=17; vote weights 5/2; threshold 7.5; pm_supp 0.4.
GCA5M = dict(src='close', length=8, mult=0.74, dema_len=2, dema_src='close',
             pool_c=7, pool_w=33, pool_range=6, pool_slope=17,
             weight_close=5, weight_wide=2,
             pm_suppression=0.4, pm_additive=0.0,
             threshold_long=7.5, threshold_short=7.5)


def generate_gca5m_signals(base_df, db, cfg: dict = GCA5M):
    """gca5m's VOTE-AGGREGATED 5s PK fires (ungated) via Pk5sGateComputer — the
    proper signal stream (close+wide probes vote-folded + thresholded), not the
    per-pool firehose. dir = sign(s5_pk_final): +1 long, -1 short.

    Returns (bars, dirs) int arrays. The gate then admits a signal where
    gate[bar] == -dir (sign-opposition), exactly as the live grind gates.
    """
    dema = IC.dema(IC.build_source(base_df, cfg['dema_src']), int(cfg['dema_len']))
    vote = dict(tcev_pk=0, tcev_weight_close=int(cfg['weight_close']),
                tcev_weight_wide=int(cfg['weight_wide']), tcev_trigger_mode='standard_pk',
                tcev_roc_threshold=None, ic_itf_seconds=5, ic_line_type='bb',
                ic_src=cfg['src'], ic_bb_len=int(cfg['length']), ic_bb_mult=float(cfg['mult']),
                ic_k_len=None, ic_rsi_len=None, ic_stc_len=None)
    pp = dict(pool_c=int(cfg['pool_c']), pool_w=int(cfg['pool_w']),
              pool_range=int(cfg['pool_range']), pool_slope=float(cfg['pool_slope']),
              pm_additive=float(cfg['pm_additive']), pm_suppression=float(cfg['pm_suppression']),
              threshold_long=float(cfg['threshold_long']), threshold_short=float(cfg['threshold_short']))
    oob   = Pk5sGateComputer(db).compute('gca5m-signals', base_df, dema, pp,
                                         midpoint=50.0, vote_overrides=[vote])
    s5    = (-np.asarray(oob)).astype(np.int8)            # +1 long, -1 short
    clean = s5.astype(float)
    prev  = np.concatenate([[0.0], clean[:-1]])
    idx   = np.where((clean != 0.0) & (clean != prev))[0]  # fire transitions
    return idx.astype(int), s5[idx].astype(int)


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
