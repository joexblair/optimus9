"""
PKVoteMachine — pure vote-folding math.

Aggregates per-probe state arrays into long/short/neutral vote buckets,
applies PM suppression, computes ratios, and emits pk_raw direction.

SRP boundaries:
  - No knowledge of "lines", DB-loaded vote configs, or trigger modes.
    Caller (Pk5sGateComputer or future SnF aggregator) is responsible
    for building probe_states from line+state computation.
  - No knowledge of gates or oob_side. Output is pk_raw direction;
    caller decides what to do with it.
  - No knowledge of decision delay. Deleted in r07 — pk_raw IS the
    final signal direction.

r07 Step 2 signature: pm_additive args NOT YET PRESENT. They arrive
in Step 4. Implement this class to the Step-2 shape only — do not
pre-add pm_additive fields, the design doc has both signatures
documented for clarity.

Architecture context:
  - "Pool" = full settings group for ONE line (one votes-table row).
  - "Probe" = close or wide measurement WITHIN a pool. Two probes per
    pool, distinct distances and weights.
  - probe_states / probe_weights dicts use (pool_id, probe_label) tuple
    keys. pool_id is the tcev_pk of the votes table row; probe_label
    is 'close' or 'wide'. Same shape supports single-line gca5m
    (one pool_id) and multi-line SnF r08 (N pool_ids).

PM mechanics:
  - State ±1 (divergence) contributes weight to long_pts / short_pts
  - State 0 (neutral) and PM sentinels (±2) contribute weight to
    neutral_pts at full weight
  - PM sentinels ADDITIONALLY contribute to pm_long_wt / pm_short_wt
    tracking buckets, used for PM suppression below
  - PM suppression: adj_long = max(0, long_pts - pm_short_wt × pm_suppress_str)
    Conceptually: PM_SHORT evidence ("price and bearish lines aligned")
    suppresses long votes by pm_suppress_str × its weight, without
    voting short itself.
  - Symmetric for adj_short.

Ratio + threshold:
  - active_w = adj_long + adj_short + neutral_pts (pm_option_a=false)
  - long_ratio = (adj_long / active_w) × 10
  - pk_raw = +1 if long_ratio > threshold_long
            -1 if short_ratio > threshold_short
             0 otherwise
"""

import numpy as np

from logger import get_logger


class PKVoteMachine:
    """Pure vote-folding math. See module docstring."""

    _PM_LONG  =  2.0
    _PM_SHORT = -2.0

    def __init__(self,
                 pm_suppress_str: float = 0.5,
                 control_voter_weight: int = 0,
                 pm_option_a: bool = False) -> None:
        """
        Parameters
        ----------
        pm_suppress_str : float
            Strength of PM-sentinel suppression on opposing direction.
            adj_long = max(0, long_pts - pm_short_wt * pm_suppress_str).
            Pine default 0.4; Python config-driven.
        control_voter_weight : int
            Weight of a "control voter" — a phantom contributor that
            adds to active_w (the ratio denominator) without contributing
            to any directional bucket. Dampens ratio swings on bars with
            few active probes. Default 0 (off). Inherited from Pine; may
            be dropped in Python production (r08 decision).
        pm_option_a : bool
            False (default, Python current): active_w = adj_long + adj_short
                + neutral_pts (post-suppression denominators)
            True (Pine variant): active_w = long_pts + short_pts + neutral_pts
                (raw pre-suppression denominators)
            Resolve before Step 5 production wiring.
        """
        self._pm_suppress_str       = float(pm_suppress_str)
        self._control_voter_weight  = int(control_voter_weight)
        self._pm_option_a           = bool(pm_option_a)
        self._log                   = get_logger(self.__class__.__name__)

    def aggregate(self,
                  probe_states:  dict,
                  probe_weights: dict,
                  threshold_long:  float,
                  threshold_short: float) -> dict:
        """
        Fold per-probe states into vote buckets, compute ratios + pk_raw.

        Parameters
        ----------
        probe_states : dict
            { (pool_id, 'close'): np.ndarray, (pool_id, 'wide'): np.ndarray, ... }
            Each array has identical length n. Values per bar:
              NaN — not yet computable
              0    — neutral
              ±1   — divergence (long/short)
              ±2   — PM sentinel (PM_LONG / PM_SHORT, trend continuation)
        probe_weights : dict
            { (pool_id, 'close'): int, (pool_id, 'wide'): int, ... }
            Same keys as probe_states. Zero-weight probes can be omitted
            by the caller or passed as 0 — either is handled.
        threshold_long : float
            Ratio threshold for long fires (typical 5.0-7.5 on 0-10 scale).
        threshold_short : float
            Ratio threshold for short fires.

        Returns
        -------
        dict with keys:
            long_pts, short_pts, neutral_pts : raw accumulation buckets
            long_ratio, short_ratio          : 0-10 scaled ratios
            pk_raw                           : int8 array, -1/0/+1
        """
        if not probe_states:
            raise ValueError('probe_states must be non-empty')

        # Infer bar count from any probe state array
        n = len(next(iter(probe_states.values())))

        long_pts    = np.zeros(n, dtype=np.float64)
        short_pts   = np.zeros(n, dtype=np.float64)
        neutral_pts = np.zeros(n, dtype=np.float64)
        pm_long_wt  = np.zeros(n, dtype=np.float64)
        pm_short_wt = np.zeros(n, dtype=np.float64)

        for key, states in probe_states.items():
            weight = int(probe_weights.get(key, 0))
            if weight == 0:
                continue

            # Match Pine's f_vote — PM sentinels route to neutral at full weight
            long_pts    += np.where(states ==  1.0, weight, 0.0)
            short_pts   += np.where(states == -1.0, weight, 0.0)
            neutral_pts += np.where(
                (states == 0.0) | (states == self._PM_LONG) | (states == self._PM_SHORT),
                weight, 0.0,
            )
            pm_long_wt  += np.where(states == self._PM_LONG,  weight, 0.0)
            pm_short_wt += np.where(states == self._PM_SHORT, weight, 0.0)

        # PM suppression: PM evidence on one side dampens votes on the other
        adj_long  = np.maximum(0.0, long_pts  - pm_short_wt * self._pm_suppress_str)
        adj_short = np.maximum(0.0, short_pts - pm_long_wt  * self._pm_suppress_str)

        # Ratio denominator. Control voter adds to denominator only.
        if self._pm_option_a:
            active_w = long_pts + short_pts + neutral_pts + self._control_voter_weight
        else:
            active_w = adj_long + adj_short + neutral_pts + self._control_voter_weight

        with np.errstate(invalid='ignore', divide='ignore'):
            long_ratio  = np.where(active_w > 0, (adj_long  / active_w) * 10.0, 0.0)
            short_ratio = np.where(active_w > 0, (adj_short / active_w) * 10.0, 0.0)

        pk_raw = np.where(long_ratio  > threshold_long,   1,
                 np.where(short_ratio > threshold_short, -1, 0)).astype(np.int8)

        return {
            'long_pts':    long_pts,
            'short_pts':   short_pts,
            'neutral_pts': neutral_pts,
            'long_ratio':  long_ratio,
            'short_ratio': short_ratio,
            'pk_raw':      pk_raw,
        }
