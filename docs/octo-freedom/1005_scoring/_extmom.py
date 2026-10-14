"""THE MOMENTUM EXTENSION MECH. 1013. Joe's design, built from his rulings only.

SRP: this file owns the extension and nothing else. It does not open a trade, does not close one,
and holds no state across calls. It answers ONE question: given a close event that has fired, which
bar does the held close actually fire on. The lineage walk (`_chain10`) and the IB-cross mech
(`_ibmech`) are untouched.

JOE'S SPEC, VERBATIM, 1013:
  *"we're going to use this momentum to extend trades.
    the mech fires at the the close event:
    -the close event will be held
    -ongoing momentum is tested using n of 7 `toward this column's board`
    -if n >=4 then ride ws{mom_cont_tf}r until it is stalled
    --the ws{mom-cont-tf}r stall can fire infence
    -on stall, the held close will fire"*

THE BOARD IS THE CLOSE COLUMN'S BOARD - the FLIPPED dr, not the leg's own.
  Joe 1013: *"flip the dr on the close trade - we're not reversing, we're extending the leg using
  those mom-true lines"*. The leg's own board is -dr; the close column reads the board of -dr, i.e.
  +dr. For the 07-18 02:31 SHORT (dr +1) that is the HIGH board.

THE 7 LINES are the momentum report's rows: ws12, ws15, ws20, ws30, dws8r, dws10r, dws15r. They are
  passed IN, as (name, side-keyed mask) pairs - this file does not know how a mask is built, and the
  caller owns MOMT / MOMD. `n` is how many of them are mom-true toward the board at a bar.

THE RIDE LINE. Joe's notation is `ws{mom_cont_tf}r` and his example sets mom_cont_tf 10. MEASURED
  ON BOTH FAMILIES AT BOTH QUALIFYING CLOSES, gate off, 4-leg gross against the standing +6.4370%:
      dws15r  +7.6278%   one leg carries it: the LONG +1.2365%, the SHORT -0.0457%, 287.2 min ride
      dws10r  +7.1028%   both legs up, +0.3548% and +0.3110%
      dws8r   +7.0846%   both legs up, +0.3410% and +0.3066%
      ws20r   +6.6312%   both legs up, +0.1718% and +0.0225%
      ws12r   +6.4902%   the LONG loses
      ws8r    +6.4341%   stalls 5 s after the close: extends nothing
      ws10r   +6.4341%   stalls 5 s after the close: extends nothing
      ws15r   +6.4320%   the LONG loses
      ws30r   +6.0751%   both legs lose
  ws10r - the literal reading - is ALREADY stalled at both close bars, so the literal reading
  extends nothing at all. Joe banked dws10r: *"your proposal is good, let's bank it"*.

THE STALL. `jig.stall_mask` with stall_n 6 samples on the ride line's own momo lattice. The
  ex-fence gate is OFF, per Joe: *"the ws{mom-cont-tf}r stall can fire infence"*. `_chain10` gates
  its own stall to the same-side ex-fence 17/83 for the lineage walk; this mech does not, and
  `W_EXT_FENCE=1` is kept only to re-measure that difference.

THE STALL'S SIDE is the board being ridden - the close column's board. The ride goes toward the
  board that passed the n test, so the stall is asked on that side.

THE EXIT RULE IS W_EXT_EXIT, AND ITS THREE VALUES ARE THREE DIFFERENT NUMBERS:
      'stall'  the ride ends at the first ride-line stall.        4-leg gross +7.1028%
      'n'      the ride ends when n first falls below W_EXT_N.    4-leg gross +7.1898%
      'first'  whichever of the two comes first.                  4-leg gross +7.0684%
  DEFAULT 'stall' - Joe banked the proposal, which was the stall exit with mom_cont_tf 10. The 'n'
  reading is his own words *"ongoing momentum is tested"* taken literally and is the better of the
  three on this sample; he has not ruled between them, so it is a knob and not a silent choice.
  SAMPLE: 2 qualifying closes on one day. Not a basis for fixing anything.

n < W_EXT_N AT THE CLOSE BAR -> the close is not held. `exit_bar` returns the close bar itself.

NO BOUND ON THE RIDE. Joe has not specified one, so there is no cap, no horizon and no maximum
  hold. A ride that finds no stall on the tape returns None and the caller decides.

CAUSAL. Every read is at or before the bar being tested, the walk is forward, and the asserts below
enforce both. `stall_mask`'s lattice only ever looks back from its own bar.
"""
import os
import numpy as np

from optimus9.analysis.jig import stall_mask
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_config
from optimus9.compute.momo_gated import momo_window

N_MIN = int(os.environ.get('W_EXT_N', 4))            # n of 7 toward the board
TF = int(os.environ.get('W_EXT_TF', 10))             # mom_cont_tf, in minutes
FAMILY = os.environ.get('W_EXT_LINE', 'dws')         # 'dws' -> dws{TF}r, 'ws' -> ws{TF}r
EXIT = os.environ.get('W_EXT_EXIT', 'stall')         # 'stall' | 'n' | 'first'
# JOE 1013'S ws30 MODE. *"I think the `ws30 -> oob -> ws1cp-ib` flow is the best option for a
# surgical way to use a line as wide as ws30"* / *"let ws30 fire the hold and ride it"*.
# When ws30 is mom-true toward the TRADE'S OWN board at the close event, the close is HELD and fires
# at the first target-side ws1cp-ib after ws30r goes oob - NOT at the dws10r stall. The switch is per
# trade, taken at the close event and not re-tested, per *"dynamically means the switch is made for
# the current trade only"*.
# THE LARGE-LEG TESTS ARE NOT PART OF THIS. The sampling match and the cascade validation are
# measured in docs/octo-freedom/1013_large_leg_findings.md and shipped nowhere - this mode reaches
# the same 2026-07-18 21:17:45 bar on the 18:45 LONG without them.
WS30 = os.environ.get('W_EXT_WS30', '1') == '1'
FENCE = os.environ.get('W_EXT_FENCE', '0') == '1'    # the ex-fence gate, OFF per Joe
assert EXIT in ('stall', 'n', 'first'), 'W_EXT_EXIT must be stall, n or first'


def ride_name(tf=None, family=None):
    """The ride line's registered name. `dws{tf}r` reads through score39.LDN, `ws{tf}r` through LD."""
    tf = TF if tf is None else int(tf)
    family = FAMILY if family is None else family
    return '%s%dr' % (family, tf)


class ExtMom:
    """The extension, for one tape.

        rows      [(name, {+1: bool array, -1: bool array})] - the 7 momentum report lines
        ride      the ride line's values, one per grid bar
        bank      the momo bank for the ride line's timeframe, for its stall lattice
        exf_hi/lo the ex-fence 83 / 17, read only when W_EXT_FENCE is on
        n         bars on the tape
    """

    def __init__(self, rows, ride, bank, tf, exf_hi, exf_lo, n, stall_n):
        self.rows = [(str(k), v) for k, v in rows]
        self.ride = np.asarray(ride, float)[:int(n)]
        self.n = int(n)
        self.hi, self.lo = float(exf_hi), float(exf_lo)
        with momo_config(bank):
            with momo_window(int(bank['k_window']) * int(tf)):
                step, samples = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
        self.step, self.samples = step, samples
        self._st = {}
        for d in (+1, -1):
            m = stall_mask(self.ride, d, int(stall_n), step, samples)[:self.n]
            if FENCE:
                m = m & ((self.ride >= self.hi) if d > 0 else (self.ride <= self.lo))
            self._st[d] = m

    # ---- the n-of-7 test, at ONE bar
    def n_at(self, j, board):
        """How many of the 7 are mom-true toward `board` at bar `j`. Reads bar j only."""
        j = int(j)
        assert 0 <= j < self.n, 'the n test was asked outside the tape'
        return sum(1 for _, m in self.rows if bool(m[int(board)][j]))

    def holds(self, close_bar, board):
        """Is the close held? Joe: *"if n >=4 then ride"*."""
        return self.n_at(close_bar, board) >= N_MIN

    def stalled(self, j, board):
        """Is the ride line stalled at bar `j`, on the board being ridden."""
        return bool(self._st[int(board)][int(j)])

    # ---- JOE 1013'S ws30 MODE
    def ws30_aligned(self, close_bar, own_board, tf=30):
        """Does ws{tf} print in the voting table AND align with the TRADE's own direction?

        Joe 1013: *"if ws30 prints in the momentum voting table and aligns with the trade's
        direction / dynamically set ws30 as the 'hold and ride it' line. dynamically means the
        switch is made for the current trade only"*.

        `own_board` is the end the TRADE is heading to, which is NOT link 3's usual board - link 3
        normally reads the flipped dr. Joe 1013: *"we can only use the trades side for link 3"*.
        """
        key = 'ws%d' % int(tf)
        for k, mask in self.rows:
            if k == key:
                return bool(mask[int(own_board)][int(close_bar)])
        return False

    def ws30_oob(self, close_bar, own_board, r30, hi, lo):
        """Walk forward to the bar ws30r is oob at the trade's own end. -> bar, or None.
        Joe 1013: *"-walk to ws30r oob"*. FORWARD LOOP, causal.
        """
        a = np.asarray(r30, float)
        for k in range(int(close_bar) + 1, self.n):
            if (a[k] >= float(hi)) if int(own_board) > 0 else (a[k] <= float(lo)):
                return k
        return None

    # ---- the ride
    def exit_bar(self, close_bar, board, exit_rule=None):
        """-> (bar, why). The bar the held close actually fires on.

        FORWARD LOOP, Joe's causal form: IF this bar has the condition THEN fire. No search
        backward, no window, no cap.
        """
        c, b = int(close_bar), int(board)
        rule = EXIT if exit_rule is None else exit_rule
        if not self.holds(c, b):
            return c, 'n %d of %d under %d - the close fires unheld' % (
                self.n_at(c, b), len(self.rows), N_MIN)
        for k in range(c + 1, self.n):
            st = self.stalled(k, b)
            nn = self.n_at(k, b)
            if rule in ('stall', 'first') and st:
                assert k > c, 'the extension fired at or before its own close bar'
                return k, '%s stalled, %s %.2f' % (ride_name(), ride_name(), self.ride[k])
            if rule in ('n', 'first') and nn < N_MIN:
                assert k > c, 'the extension fired at or before its own close bar'
                return k, 'n %d of %d fell under %d' % (nn, len(self.rows), N_MIN)
        return None, 'no %s on the tape after the close' % (
            'stall' if rule == 'stall' else 'exit')

    def trace(self, close_bar, board, step=24):
        """Every `step` bars from the close to the exit: the n, the ride line, its stall state.
        REPORTING ONLY - no branch reads it.
        """
        c, b = int(close_bar), int(board)
        k_end, _ = self.exit_bar(c, b)
        k_end = self.n - 1 if k_end is None else k_end
        out = []
        for k in list(range(c, k_end, int(step))) + [k_end]:
            out.append({'bar': k, 'n': self.n_at(k, b), 'ride': float(self.ride[k]),
                        'stalled': self.stalled(k, b)})
        return out
