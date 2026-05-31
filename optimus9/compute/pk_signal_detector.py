"""
PKSignalDetector — orchestrates state computation + gating + transition
detection to produce per-pool signals.

REPLACES the per-bar PKDetector. Key semantic change:

  OLD (PKDetector, per-bar):
    Every bar where (state != 0) AND (gate matches) emits a signal.
    Trends produce N consecutive signals over N bars.

  NEW (PKSignalDetector, transition):
    A signal fires only when state TRANSITIONS into a new directional
    value (non-zero and different from previous bar's state).
    Trends produce ONE signal at the trend's start.

Rationale: 5s signals are anchor points for HTF p-rev logic, not per-bar
re-evaluations of the same trend.

VECTORIZED implementation (r07): transition detection and gate filtering
done in numpy. Per-bar Python loops eliminated except for the small loop
over signal indices to build per-signal dicts (small N, no benefit from
vectorizing that step).

Same interface as PKDetector.detect() for downstream compatibility:
returns list of signal dicts with the same keys.
"""

from typing import Optional

import numpy as np

from logger import get_logger
from .pk_state_computer import PKStateComputer
from .pk_gate_filter   import PKGateFilter
from .pk_vote_machine   import PKVoteMachine


class PKSignalDetector:
    """Detect PK transition signals across close and wide pools, gate-aware."""

    def __init__(self,
                 state_computer: Optional[PKStateComputer] = None,
                 gate_filter:    Optional[PKGateFilter]    = None,
                 vote_machine:   Optional[PKVoteMachine]   = None) -> None:
        self._state_computer = state_computer or PKStateComputer()
        self._gate_filter    = gate_filter    or PKGateFilter()
        # r07 Step 3a: optional vote-machine injection point. When None
        # (default; the gated grind path supplies nothing) behaviour is
        # unchanged. The vote-engaged flow is Step 3b — see detect().
        self._vote_machine   = vote_machine
        self._log            = get_logger(self.__class__.__name__)

    def detect(self, line: np.ndarray, dema: np.ndarray,
               pool_c: int, pool_w: int, pool_range: int,
               multiplier: int, slope_floor: float,
               oob_side: np.ndarray, params: dict,
               line_type: str = 'bb') -> list:
        """
        Return list of signal dicts. Compatible with PKDetector.detect()'s
        contract.

        Length-mismatch handling (r07): line, dema, and oob_side can differ
        in length when ind_seconds == 5 (see PKStateComputer.compute docstring).
        We truncate all three to the minimum length, matching the original
        PKDetector loop's implicit behavior.
        """
        if self._vote_machine is not None:
            # r07 Step 3b (vote-engaged flow) — pending design decisions on
            # aggregate-signal persistence + gate-on-pk_raw sign convention.
            raise NotImplementedError(
                'PKSignalDetector vote-engaged flow is Step 3b (not yet '
                'implemented). Use vote_machine=None for the per-probe path.'
            )

        if pool_range == 0:
            return []

        # Truncate to common length. See class/method docstrings.
        n = min(len(line), len(dema), len(oob_side))
        line     = line[:n]
        dema     = dema[:n]
        oob_side = oob_side[:n]

        signals = []
        for label, bars in (('close', pool_c), ('wide', pool_w)):
            state_series = self._state_computer.compute(
                line, dema, bars, pool_range, multiplier, slope_floor,
            )
            pool_signals = self._extract_per_pool(
                line, dema, state_series, label, bars,
                pool_c, pool_w, pool_range, multiplier, slope_floor,
                oob_side, params, line_type,
            )
            signals.extend(pool_signals)

        return signals

    # ── Per-pool vectorized signal extraction ────────────────────────────────

    def _extract_per_pool(self, line, dema, state_series, label, bars,
                          pool_c, pool_w, pool_range, multiplier, slope_floor,
                          oob_side, params, line_type) -> list:
        """
        Vectorized transition detection + gate filtering for one pool.

        Transition rule:
          A signal fires at bar i where state_series[i] is non-zero AND
          differs from state_series[i-1] (treating NaN-prev as zero).

        Gate rule (sign-opposition):
          oob_side[i] != 0 AND state_series[i] matches -oob_side[i] — a signal
          is admitted only where its sign is the negation of the filter's
          breach sign.
        """
        n = len(state_series)
        if n == 0:
            return []

        # ── Transition mask ────────────────────────────────────────────────
        # Treat NaN states as 0 for the "previous" comparison. This matches
        # the loop's prev_state=0 reset on NaN.
        states_clean = np.where(np.isnan(state_series), 0.0, state_series)
        # prev_state[0] = 0 implicitly (the loop initialises prev_state = 0)
        prev_states  = np.concatenate([[0.0], states_clean[:-1]])

        # A transition is: current is non-zero AND differs from previous.
        # (NaN current is excluded because NaN != anything is True but we
        #  filter NaN separately.)
        is_directional = (states_clean != 0.0) & ~np.isnan(state_series)
        is_change      = (states_clean != prev_states)
        is_transition  = is_directional & is_change

        # ── Gate mask ───────────────────────────────────────────────────────
        # Sign-opposition: a signal is admitted only where its sign is the
        # negation of the filter's breach sign. oob_side ∈ {-1, 0, +1};
        # expected signal sign = -oob_side. Match on state ∈ {±1, ±2}.
        oob = oob_side.astype(np.int8)
        expected = -oob.astype(np.float64)  # what the state should oppose to
        gate_passes = (oob != 0) & (
            (state_series == expected) | (state_series == expected * 2.0)
        )

        # Final signal indices
        signal_mask = is_transition & gate_passes
        signal_indices = np.where(signal_mask)[0]

        if len(signal_indices) == 0:
            return []

        # ── Build signal dicts (small N, looping is fine) ──────────────────
        # Recompute peak/slopes at signal bars for the dict — same as before.
        half  = pool_range // 2
        upper = (bars + half) * multiplier
        lower = (bars - half) * multiplier
        center = bars * multiplier
        midpoint = self._state_computer._midpoint

        out = []
        for i in signal_indices:
            window = line[i - upper + 1 : i - lower + 1]
            peak   = np.max(window) if line[i] > midpoint else np.min(window)
            line_slope  = float(line[i] - peak)
            price_slope = float(dema[i] - dema[i - center])
            slope_diff  = abs(line_slope - price_slope)
            cur_state   = float(state_series[i])
            oob_at_i    = int(oob_side[i])
            expected    = self._gate_filter.direction(oob_at_i)

            sig = {
                'bar_index':   int(i),
                'direction':   expected,
                'pk_state':    cur_state,
                'line_value':  float(line[i]),
                'slope':       line_slope,
                'slope_diff':  slope_diff,
                'dema_slope':  price_slope,
                'dema_value':  float(dema[i]),
                'pool':        label,
                'len':         params['len'],
                'src':         params['src'],
                'pool_c':      pool_c,
                'pool_w':      pool_w,
                'pool_range':  pool_range,
                'slope_floor': slope_floor,
                'multiplier':  multiplier,
            }

            if line_type == 'bb':
                sig['mult'] = params['mult']
            else:  # 'k'
                sig['len_rsi']   = params['len_rsi']
                sig['len_stoch'] = params['len_stoch']

            out.append(sig)

        return out
