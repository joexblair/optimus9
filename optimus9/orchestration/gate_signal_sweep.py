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


def gca5m_pk_raw(base_df, db, cfg: dict = GCA5M) -> np.ndarray:
    """The per-bar pk_raw = the gca5m vote-aggregated, thresholded 5s signal
    (+1 long / -1 short / 0). This is the Pine's `pk_raw` BEFORE the decision-delay
    state machine and the bny30 gate. (close+wide probes vote-folded + thresholded.)"""
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
    oob = Pk5sGateComputer(db).compute('gca5m-signals', base_df, dema, pp,
                                       midpoint=50.0, vote_overrides=[vote])
    return (-np.asarray(oob)).astype(np.int8)            # +1 long, -1 short


def apply_decision_delay(pk_raw, delay: int = 1) -> np.ndarray:
    """Port of the Pine PROVEN production decision-delay state machine (passthrough
    OFF). A new direction must HOLD `delay` bars (confirmation) before s5_pk_final
    takes it; an opposing pk restarts the countdown; a neutral bar resets. Returns
    the SUSTAINED s5_pk_final per bar (+1/-1/0) — the Pine's actual fire driver."""
    pk_raw = np.asarray(pk_raw, dtype=np.int8)
    n = len(pk_raw)
    out = np.zeros(n, np.int8)
    countdown = pending = final = 0
    for i in range(n):
        r = int(pk_raw[i])
        if r != 0:
            if r == pending:
                countdown = max(0, countdown - 1)
                if countdown == 0:
                    final = r
            else:
                pending = r
                if delay == 0:
                    countdown, final = 0, r
                else:
                    countdown, final = delay, 0
        else:
            pending = countdown = final = 0
        out[i] = final
    return out


# the bny30 production gate (Joe 2026-06-06): bny30M (BB hl2 68/1.24) OR
# bny30m (K ohlc4 21/114/105), 30s, 85/15.
BNY30 = [
    dict(ic_itf_seconds=30, ic_line_type='bb', ic_src='hl2', ic_bb_len=68, ic_bb_mult=1.24,
         ic_high_boundary=85, ic_low_boundary=15),
    dict(ic_itf_seconds=30, ic_line_type='k', ic_src='ohlc4', ic_k_len=21, ic_rsi_len=114,
         ic_stc_len=105, ic_high_boundary=85, ic_low_boundary=15),
]


def bny30_oob_side(base_df) -> np.ndarray:
    """The bny30 gate's per-5s oob_side (+1 HI / -1 LO / 0 in-band), OR-folded over
    bny30M (BB hl2 68/1.24) + bny30m (K ohlc4 21/114/105) — the production gate."""
    gate_df = IC.resample(base_df, 30)
    sides   = [IC.align_to_base(IC.compute_oob_side(cfg, gate_df), gate_df, base_df)
               for cfg in BNY30]
    return IC.fold_gates(sides)


def generate_gca5m_signals(base_df, db, cfg: dict = GCA5M):
    """gca5m's UNGATED, UN-delayed pk_raw fire transitions (+1 long / -1 short).
    Returns (bars, dirs). For the Pine-aligned realtime signal use pine_aligned_signals()."""
    s5    = gca5m_pk_raw(base_df, db, cfg)
    clean = s5.astype(float)
    prev  = np.concatenate([[0.0], clean[:-1]])
    idx   = np.where((clean != 0.0) & (clean != prev))[0]  # fire transitions
    return idx.astype(int), s5[idx].astype(int)


def pine_aligned_signals(base_df, db, cfg: dict = GCA5M, delay: int = 1, gate: bool = True):
    """The full Pine PROVEN realtime entry signal — what the strategy actually trades:
      pk_raw → decision-delay(delay) state machine → fire edges → bny30 gate
    The gate is mean-reversion: a fire survives only where dir == -oob_side (fire_long
    needs the gate OOB-low, fire_short OOB-high). Returns (bars, dirs)."""
    fin   = apply_decision_delay(gca5m_pk_raw(base_df, db, cfg), delay)
    clean = fin.astype(float)
    prev  = np.concatenate([[0.0], clean[:-1]])
    idx   = np.where((clean != 0.0) & (clean != prev))[0]  # confirmed fire edges
    dirs  = fin[idx].astype(int)
    if gate:
        oob  = bny30_oob_side(base_df)
        keep = dirs == -oob[idx].astype(int)               # mean-reversion gate
        idx, dirs = idx[keep], dirs[keep]
    return idx.astype(int), dirs


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
