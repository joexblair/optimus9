"""THE CHAIN RESTART ON THE LOOP LINE'S oob. 1013. Joe's mech, his name:
'restart-chain-on-loop-tf-oob'.

HIS SPEC, VERBATIM:

    -IF there is no open trade
    --IF ws{loop-tf}r has crossed to IB
    ---IF ws1Mage has been IB for >24 bars AND ws1-3r are printing 'away'
    ----open a TRADE that goes away from the ws{loop-tf}r's oob side

AND HIS THREE CLARIFICATIONS, 1013:

  THE ARM: *"use the ws{loop-tf}r crossing to oob as an arm, then walk and test on each bar. no
    cap"*. So the arm is ws{loop-tf}r crossing INTO oob, and the three tests then run every bar.
  'AWAY': *"`away` is in an established mech. `towards` is the other side of the coin. it tells us
    if the line has momentum (toward) and lost momentum (away)"*, and he confirmed reading A - the
    lines must have lost momentum toward the side the loop line went oob on. Reading B, away from
    the other end, fires 7 min 50 s later at 2026-07-19 12:08:00 against A's 12:00:10.
  THE DIRECTION: *"don't use oob hack as a reference. the standard for trades is '-dr, low oob, LONG
    trade' or '+dr, high oob, SHORT trade'"*. So a LOW-oob loop line gives dr -1, a HIGH-oob one
    gives dr +1.

SRP: this file finds the bar and the side. It opens nothing, closes nothing and scores nothing. The
caller asks it where the next restart is, exactly as it asks `_ibmech` where the next cross-back is.

CAUSAL: `arm` walks forward and `fire` walks forward from the arm. Every value either reads sits at
or before the bar it returns - the ws1Mage dwell counts BACKWARD from the bar, the momentum masks
are read AT the bar, and the loop line's in-fence state is read AT the bar.
"""
import os

# THE KNOB NAME IS MINE; the 24 is his *"IB for >24 bars"*, and the lines ws1-ws3 are his too.
MAGE_DWELL = int(os.environ.get('W_RESTART_MAGE_DWELL', 24))   # bars; the test is STRICTLY greater
AWAY_TFS = tuple(int(z) for z in os.environ.get('W_RESTART_AWAY_TFS', '1,2,3').split(','))
ON = os.environ.get('W_RESTART', '1') == '1'


class Restart:
    """Build once per tape, then `arm` and `fire`.

        r      {tf: r array}        the r lines
        mom    {tf: {board: mask}}  the mom-true masks
        mg1    the ws1Mage array
        oobf   the oob test, oobf(tf, bar, board)
        loop_tf, hi, lo, n
    """

    def __init__(self, r, mom, mg1, oobf, loop_tf, hi, lo, n):
        self.r, self.mom, self.mg1, self.oobf = r, mom, mg1, oobf
        self.loop_tf, self.hi, self.lo, self.n = int(loop_tf), float(hi), float(lo), int(n)

    # ---- the arm
    def arm(self, frm):
        """-> (the arm bar, the board the loop line went oob on) or (None, None).

        The FIRST bar after `frm` on which ws{loop_tf}r crosses INTO oob, either end.
        """
        t = self.loop_tf
        for k in range(int(frm) + 1, self.n):
            for d in (-1, +1):
                if (not self.oobf(t, k - 1, d)) and self.oobf(t, k, d):
                    return k, d
        return None, None

    # ---- the three tests, per bar
    def mage_dwell(self, k):
        """How many consecutive bars up to and including `k` has ws1Mage been in-fence? BACKWARD."""
        n = 0
        while k - n >= 0 and self.lo < float(self.mg1[k - n]) < self.hi:
            n += 1
        return n

    def away(self, k, oob_board):
        """Are ALL of ws1-ws3 'away' at bar `k`? 'away' is NOT mom-true toward `oob_board`."""
        for t in AWAY_TFS:
            if t in self.mom and bool(self.mom[t][oob_board][k]):
                return False
        return True

    def fire(self, arm_bar, oob_board):
        """-> (the bar the trade opens, dr) or (None, None). Walked FORWARD from the arm, no cap.

        A trade opens on the first bar where all three hold:
            ws{loop_tf}r is in-fence - it has crossed back from the oob side
            ws1Mage has been in-fence for MORE than MAGE_DWELL bars
            ws1, ws2 and ws3 are all away from `oob_board`
        dr is Joe's standard: a LOW-oob loop line gives dr -1 (a LONG), a HIGH-oob one dr +1.
        """
        t = self.loop_tf
        arm_bar = int(arm_bar)
        for k in range(arm_bar, self.n):
            if self.oobf(t, k, oob_board):
                continue                       # still oob on that side, it has not crossed back
            if self.mage_dwell(k) <= MAGE_DWELL:
                continue
            if not self.away(k, oob_board):
                continue
            dr = -1 if oob_board < 0 else +1   # low oob -> LONG, high oob -> SHORT
            assert k >= arm_bar, 'the restart fired before its own arm'
            return k, dr
        return None, None

    def next(self, frm):
        """The whole mech from a bar with no open trade. -> (bar, dr, arm bar, the oob board)."""
        a, d = self.arm(frm)
        if a is None:
            return None, None, None, None
        k, dr = self.fire(a, d)
        if k is None:
            return None, None, a, d
        return k, dr, a, d
