"""THE BOARD PROXY. Joe 1026: *"build a proxy that sends the emerging values to the gate decision"*.

ONE RESPONSIBILITY: hold both ladders and route each read to the right one. It decides nothing
about trades, riders or cadences - it answers "what is ws{tf}r here" and knows which line set the
caller is entitled to for that question.

WHY IT EXISTS. Before this the routing was implicit in which dict a caller was handed, so the
closed/emerging split lived in six call sites and a reader had to trace each one. The split is now
ONE TABLE in this file, and every rule of his that set it is quoted beside the method it governs.

HIS THREE RULINGS, in the order he gave them:

    1025  the rider-scan has all lines emerging for intra-mech continuity
          I don't want slower TF's running on closed bars because it spoils the line reversal times

    1026  add all lines to csw1-12. these closed lines will give us more accurate fence/exfence
          baton decisions
          with ws1-12, emerg: time the reversals
          best of both worlds

    1026  build a proxy that sends the emerging values to the gate decision

SO THREE BUCKETS, not two:

    STATE    the CLOSED ladder. oob, ex-fence, the raw value - the rider scan, the baton
             candidates and the baton-pass crosses. His *"fence/exfence baton decisions"*.
    TIMING   the EMERGING ladder. Reversal stamps only. His *"emerg: time the reversals"*.
    GATE     the EMERGING ladder, on his 1026 instruction. t3cadence's two gates - the
             *"have been oob already in this trade"* population and the *"no higher TFs exfence"*
             test.

WHAT THE GATE SWITCH IS WORTH, measured on his 2026-08-30 18:37 LOW walk, arm 19:16:00: ws7r is
the only HTF line to reach LOW oob on either ladder, and it reaches it at 19:57:00 closed against
19:50:00 emerging. Its reversal stamp is 19:20:10 on both. So the gate on emerging moves t3 from
19:57:00 to 19:50:00 - it does NOT reach the 19:20 he eyeballed, because on both ladders the oob
lands 30 minutes AFTER the reversal.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_fast as F
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


class Board:
    """Both r ladders, and which read is entitled to which.

        C  the CLOSED cws1r..cws12r set
        E  the EMERGING ws1r..ws12r set
    """

    def __init__(self, C, E):
        self.C = {int(t): np.asarray(v, float) for t, v in C.items()}
        self.E = {int(t): np.asarray(v, float) for t, v in E.items()}
        self.tfs = sorted(set(self.C) & set(self.E))
        assert self.tfs, 'the two ladders share no timeframe'
        self._gate = str(K.L2_GATE_MODE)
        assert self._gate in ('emerging', 'closed'), 'L2_GATE_MODE %r is not a mode' % self._gate

    #  ── STATE: the closed ladder ──────────────────────────────────────────────────────────────
    def value(self, tf, bar):
        """ws{tf}r at `bar`, CLOSED. The number every fence test reads."""
        return float(self.C[int(tf)][int(bar)])

    def oob(self, tf, bar, side):
        """Is ws{tf}r oob on `side` at `bar`, CLOSED."""
        return bool(K.oob(self.C[int(tf)][int(bar)], side))

    def ex_fence(self, tf, bar, side):
        """Is ws{tf}r past the r fence on `side` at `bar`, CLOSED."""
        return bool(K.ex_fence(self.C[int(tf)][int(bar)], side))

    def line(self, tf):
        """The CLOSED array, for a producer that needs the whole series - crosses, trajectory."""
        return self.C[int(tf)]

    #  ── TIMING: the emerging ladder ───────────────────────────────────────────────────────────
    def rev_stamps(self, tf, side):
        """ws{tf}r's reversal stamps on `side`, EMERGING. -> a sorted list.

        His 1025 reason for keeping these emerging: closed bars *"spoils the line reversal times"*.
        """
        return sorted(K.lift_stamp(int(x)) for x in F.revs(self.E[int(tf)], int(tf), int(side)))

    def reversed_in(self, tf, side, a, b):
        """Did ws{tf}r print a reversal with its stamp in [a, b], EMERGING."""
        return any(int(a) <= x <= int(b) for x in self.rev_stamps(tf, side))

    #  ── GATE: the emerging ladder, his 1026 instruction ───────────────────────────────────────
    def _g(self, tf):
        return self.E[int(tf)] if self._gate == 'emerging' else self.C[int(tf)]

    def gate_mode(self):
        """Which ladder the gates read. -> 'emerging' or 'closed'. For the report's header."""
        return self._gate

    def gate_been_oob(self, tf, a, b, side):
        """Was ws{tf}r oob on `side` at ANY bar in [a, b]. t3's population gate.

        *"when any of ws7r to ws12r (HTF lines) have been oob already in this trade"*, and
        *"already in this trade"* is measured from the arm bar - his 1025 ruling.
        """
        seg = self._g(tf)[int(a):int(b) + 1]
        return bool((seg <= K.OOB_LO).any() if int(side) < 0 else (seg >= K.OOB_HI).any())

    def gate_ex_fence(self, tf, bar, side):
        """Is ws{tf}r ex-fence on `side` at `bar`. t3's *"no higher TFs exfence"* gate."""
        return bool(K.ex_fence(self._g(tf)[int(bar)], side))
