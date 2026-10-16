"""`veto-on-momentum`. 1016. JOE NAMED IT: *"the ws3 ws4 ws5 lines that we've chosen for the
new `veto-on-momentum`"*. He first called the idea a *"lost-momentum check"*; `veto-on-momentum` is
the name he settled on and is the one in use.

JOE'S MECH, NOT MINE.

HIS SPEC, 1016 verbatim: *"I think we need a lost-momentum check to fire at `OPEN` or bounce-pred's
'verdict' - ie hold the open signal and test for lost momentum before allowing the open signal to
fire -lost momentum is signalled by {knob:ws3-6} leading AWAY from oob and carrying the ib tag, in a
matryoshka pattern"*, then refined across the same session:

    *"ride ws5r until lineage sees momentum and takes over the last mile"*
    *"the mech will simply keep the incoming trade OPEN and ride ws5r until lineage takes over"*
    *"the INCOMING trade (the LONG trade that was opened before 02:07's SHORT verdict) remains open"*
    *"your 'it is a veto on the close. The verdict's power to close the opposite side is suspended'
      is the correct view"*
    *"if there is no incoming trade (chain gap), then the OPEN would be at 02:07, towards the
      direction that the r lines are facing (LONG for this example)"*
    *"lineage will hand over to the bounce-pred mech when ws5Mage crosses to target-side oob"*

SO IT IS AN EXIT-SIDE MECH, NOT AN ENTRY GATE:
    1   the verdict's power to CLOSE the opposite side is suspended - the open trade rides
    1a  with nothing open, the OPEN fires at the verdict bar on the side the r lines FACE, which is
        the opposite of what the verdict would normally open
    2   the trade rides ws5r
    3   handover when ws5Mage reaches the riding trade's TARGET-SIDE OOB
    4   bounce-pred walks from the handover
    5   its REVERSE is the exit, at the verdict's knowable bar

LINEAGE DECIDES NOTHING HERE. Joe 1016: *"that was banning lineage as a decision route"*. It names
the state the trade is in while riding. `_lineage_conf.py` is untouched and still returns no bar.

TERMINOLOGY, Joe 1016: *"its "high oob" and "low oob". board refers to the full range (0 to 100 for
r, unlimited for MAge)"*.

THE PATTERN, measured over the 94 built days before this was written:
    at the event bar, ws3r AND ws4r AND ws5r have each left the oob on the side OPPOSITE the event,
    in ascending timeframe order, each within W_VOM_LOOKBACK, and all three still out.
    a departure only counts if the line stays out at least W_VOM_MIN_OUT - without that filter 71%
    of "departures" were fence jitter lasting 15 to 55 seconds.
  HIS CLAIM THAT MOTIVATED THE FILTER, 1016: *"it is very rare for a ws4r and ws5r line to leave its
  source oob and then reverse and return to source oob without passing 50 first"*. MEASURED: at a
  5-minute minimum it is 9.3% across four arms, and the filter never removes a single episode that
  DID pass 50 - every episode it drops is a no-50 return. His claim holds.

TWO VALUES ARE MINE AND ARE STATED. Joe named the filters, not the numbers.
    W_VOM_MIN_OUT    60 bars = 5 min. The measured knee: the no-50 rate goes 36.7% at 1 min, 23.4%
                    at 2 min, 9.3% at 5 min, 6.3% at 10 min. 5 min is where it halves and flattens.
    W_VOM_LOOKBACK   240 bars = 20 min. At 5 min only 1 event of 2799 matched and at 60 min the
                    pattern fires on 9.50% of events; 20 min gives 36 = 1.29%. TWEAKABLE.

SRP: this file answers two questions - does the pattern hold at a bar, and where does a ride exit.
It holds no trade state and moves no trade.
"""
import os

import numpy as np

from optimus9.analysis.jig import oob_ib_cross

ON = os.environ.get('W_VOM_ON', '1') == '1'
TFS = tuple(int(x) for x in os.environ.get('W_VOM_TFS', '3,4,5').split(','))
MIN_OUT = int(os.environ.get('W_VOM_MIN_OUT', 60))       # 5 min. MINE, the measured knee
LOOKBACK = int(os.environ.get('W_VOM_LOOKBACK', 240))    # 20 min. MINE
XWOB = int(os.environ.get('W_VOM_XWOB', 4))              # the cross hold, Joe 0911 "boundary:4"


class VetoOnMomentum:
    """The pattern and the ride, over one tape. Build once."""

    def __init__(self, sc, hold, m5):
        self.sc = sc
        self.hold = hold                 # the bounce-pred object that takes over at the handover
        self.m5 = np.asarray(m5, float)
        self.n = len(self.m5)
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        self.dep = {}
        for t in TFS:
            r = np.asarray(sc.LD(t * 60, 'r'), float)[:self.n]
            for side in (+1, -1):
                inoob = (r >= self.hi) if side > 0 else (r <= self.lo)
                back = np.flatnonzero(inoob)
                ds = []
                for k, c, sd in oob_ib_cross(r, self.hi, self.lo, XWOB):
                    if sd != side:
                        continue
                    nx = back[back > k]
                    out = (int(nx[0]) - k) if nx.size else (self.n - k)
                    if out >= MIN_OUT:
                        ds.append((int(k), int(k) + out))
                self.dep[(t, side)] = ds

    def holds(self, bar, event_side):
        """Does the pattern hold at `bar` for an event on `event_side`? -> the three departure
        bars, or None. The lines leave the oob OPPOSITE the event."""
        if not ON:
            return None
        src = -int(event_side)
        got = []
        for t in TFS:
            c = [k for k, e in self.dep[(t, src)] if bar - LOOKBACK <= k <= bar and e > bar]
            if not c:
                return None
            got.append(max(c))
        return got if all(got[i] <= got[i + 1] for i in range(len(got) - 1)) else None

    def ride_exit(self, bar, dr, until=None):
        """Where a riding trade of side `dr` exits. -> (the handover bar, the exit bar, why).

        The handover waits for ws5Mage to reach the riding trade's TARGET-SIDE OOB - low for a
        SHORT (dr +1), high for a LONG. Then bounce-pred walks and its REVERSE is the exit, at the
        verdict's knowable bar. NO CAP on either leg; Joe has set none.
        """
        import _bouncepred as BP
        end = (self.n - 1) if until is None else int(until)
        tside = -1 if int(dr) > 0 else +1           # a SHORT hunts the low oob
        seg = self.m5[int(bar):end + 1]
        want = (seg <= self.lo) if tside < 0 else (seg >= self.hi)
        hit = np.flatnonzero(want)
        if hit.size == 0:
            return None, None, 'no handover - ws5Mage never reached the target-side oob'
        h = int(bar) + int(hit[0])
        w = self.hold.walk(h, tside, until=end)
        if not w:
            return h, None, 'handed over at %s, bounce-pred produced no verdict' % self.sc.U(h)
        rb, v, ka, med, pos, why = w[-1]
        if v != BP.REVERSE:
            return h, None, 'handed over at %s, still continuance' % self.sc.U(h)
        return h, int(ka), ('handed over at %s, bounce-pred reverse at %s, %d of 30 positive, '
                            'median %+.2f' % (self.sc.U(h), self.sc.U(rb), pos, med))
