"""
PKGateFilter — gate predicate, swappable.

The default filter implements mean-reversion semantic: a PK signal passes
only when oob_side != 0 AND the signal direction is OPPOSITE the gate's
OOB side. Line went too high (oob_side=+1) → only SHORT signals (state -1
or -2) pass. Line went too low (oob_side=-1) → only LONG signals (+1, +2).

Future filters (HTF gates, regime gates, etc.) can subclass or replace
this class without touching the signal detector.
"""

from logger import get_logger


class PKGateFilter:
    """Mean-reversion gate filter. Signal direction must oppose oob_side."""

    def __init__(self) -> None:
        self._log = get_logger(self.__class__.__name__)

    def passes(self, pk_state: float, oob_side: int) -> bool:
        """
        Return True if pk_state should produce a signal given the gate state.

        pk_state ∈ {NaN, 0, ±1, ±2}
        oob_side ∈ {-1, 0, +1}
        """
        if oob_side == 0:
            return False
        # Mean reversion: signal direction is the OPPOSITE of oob_side.
        # If line is in OOB high (oob_side=+1), fire SHORT (-1 or -2).
        # If line is in OOB low (oob_side=-1), fire LONG (+1 or +2).
        expected = -oob_side
        return pk_state == float(expected) or pk_state == float(expected) * 2.0

    def direction(self, oob_side: int) -> int:
        """Return the trade direction expected for an OOB side."""
        return -oob_side
