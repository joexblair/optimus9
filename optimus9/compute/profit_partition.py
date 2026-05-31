"""
ProfitPartition — price-intrinsic ±threshold profit partition (gate sweep, Stage 0).

For every bar, forward-walk on CLOSE to the FIRST ±threshold cross within a
horizon. Classifies each bar as long-favorable / short-favorable / neither,
purely from price — no line, no signals, no probe centroid. This is the ground
truth the gate match score is scored against (see gate_sweep_design.md).

Design (2026-05-31):
  - Symmetric ±threshold (default 0.9%): the opposite-side threshold IS the
    implicit stop, so there is NO separate stop parameter. Self-correcting — a
    bar that only reaches +0.9% after first dropping 0.9% is classed short, not
    long. Consequence: every long-favorable bar's max adverse excursion is
    bounded under `threshold` by construction (and symmetrically for shorts).
  - CLOSE-based crossing, matching outcome_walker's convention. A scalar close
    can't cross both thresholds in one bar, so there is no intrabar ambiguity.
  - `horizon` (H) is the one residual knob — how long we wait for the move
    before calling a bar `neither` (chop). It is the scalp hold-time; pin it
    empirically (see the auto-derive-x note in gate_sweep_design.md).

The three classes (long / short / neither) map onto the gate's three states
(LO breach / HI breach / in-band).
"""

from typing import Optional
import numpy as np


# Class labels — natural trade polarity (+1 long, -1 short, 0 none), matching
# pks_dir. NOTE: this is INVERTED vs the gate's oob_side (LO breach=-1 enables
# longs). The gate match scorer owns that bridge (hit = gate == -P); see
# gate_match_score.py. Do NOT "align" these to oob_side — it would bury the
# inversion inside this general price primitive.
LONG, SHORT, NEITHER = 1, -1, 0


def compute_profit_partition(close: np.ndarray,
                             threshold_pct: float = 0.9,
                             horizon: int = 720) -> dict:
    """
    Partition every bar by which of ±threshold_pct its close reaches first,
    within `horizon` bars forward.

    Parameters
    ----------
    close : np.ndarray of float close prices
    threshold_pct : symmetric profit/stop threshold in percent (0.9 = 0.9%)
    horizon : max bars to look forward before labelling a bar `neither`

    Returns
    -------
    dict with arrays of length len(close):
      cls          : int8  per-bar class {+1 long, -1 short, 0 neither}
      mae_pct      : float winner's max adverse excursion (% magnitude) en
                     route to its win; NaN for `neither` bars. Bounded
                     < threshold_pct by construction.
      bars_to_win  : int32 bars from entry to the winning cross; -1 for neither
    """
    n   = len(close)
    cls = np.zeros(n, dtype=np.int8)
    mae = np.full(n, np.nan, dtype=np.float64)
    btw = np.full(n, -1, dtype=np.int32)

    up_mult = 1.0 + threshold_pct / 100.0
    dn_mult = 1.0 - threshold_pct / 100.0

    for i in range(n - 1):
        entry  = float(close[i])
        hi_lvl = entry * up_mult
        lo_lvl = entry * dn_mult

        j_end = min(i + horizon, n - 1)
        fut   = close[i + 1: j_end + 1]
        if fut.size == 0:
            continue

        up_hits = fut >= hi_lvl
        dn_hits = fut <= lo_lvl
        up_any  = bool(up_hits.any())
        dn_any  = bool(dn_hits.any())
        if not up_any and not dn_any:
            continue                                   # neither within horizon

        up_idx = int(up_hits.argmax()) if up_any else -1   # offset into `fut`
        dn_idx = int(dn_hits.argmax()) if dn_any else -1

        if   not dn_any:            first, direction = up_idx, LONG
        elif not up_any:            first, direction = dn_idx, SHORT
        elif up_idx < dn_idx:       first, direction = up_idx, LONG
        else:                       first, direction = dn_idx, SHORT
        # up_idx == dn_idx is impossible: a single close can't be >=hi and <=lo.

        cls[i] = direction
        btw[i] = first + 1                              # bars from entry (i)

        # Max adverse excursion en route to the win. By construction the
        # opposite threshold was NOT crossed before `first`, so this is
        # bounded under threshold_pct.
        seg = fut[: first + 1]
        if direction == LONG:
            worst = float(seg.min())
            mae[i] = (1.0 - worst / entry) * 100.0 if worst < entry else 0.0
        else:
            worst = float(seg.max())
            mae[i] = (worst / entry - 1.0) * 100.0 if worst > entry else 0.0

    return {'cls': cls, 'mae_pct': mae, 'bars_to_win': btw}


def summarize_partition(cls: np.ndarray, mae_pct: np.ndarray,
                        threshold_pct: float = 0.9) -> dict:
    """
    Coverage fractions (the saturation check) + winner-MAE percentiles
    (the empirical stop floor). See gate_sweep_design.md.
    """
    n = len(cls)
    long_n    = int((cls == LONG).sum())
    short_n   = int((cls == SHORT).sum())
    neither_n = int((cls == NEITHER).sum())

    winners = mae_pct[~np.isnan(mae_pct)]
    pcts = {}
    if winners.size:
        for p in (50, 75, 90, 95, 99):
            pcts[p] = float(np.percentile(winners, p))

    tradeable = long_n + short_n
    return {
        'n':              n,
        'long_frac':      long_n / n if n else 0.0,
        'short_frac':     short_n / n if n else 0.0,
        'neither_frac':   neither_n / n if n else 0.0,
        'tradeable_frac': tradeable / n if n else 0.0,
        'mae_pct':        pcts,
        'mae_mean':       float(winners.mean()) if winners.size else None,
        'threshold_pct':  threshold_pct,
    }
