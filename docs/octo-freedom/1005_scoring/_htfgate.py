"""THE HTF oob GATE. 1013. Joe's hack, banked from his words only.

Joe 1013: *"I'm going to use a hack to get us past the 21:17 short, because right now I don't know
how to build the countering LONG trade without breaking the rest of our machine / here's the mech /
-if a trade closes when ws{>=30}r is oob, only open trades that are towards the oob HTF line / -the
restriction ends when ws30r is IB after ws60x-crosses r with a 48 wob"*.

AND HIS CLARIFICATION, which is the form built here: *"if the HTF line is high OOB, then only long
trades sourced from low oob ws1cp's are allowed. the inverse is true for an HTF low oob: only high
oob ws1cp's are allowed to place a SHORT trade"*. The rule is stated in cp terms, so it is coded in
cp terms - no derived trade side.

    HTF HIGH oob  ->  only a LOW-oob ws1cp may open, and it makes a LONG
    HTF LOW  oob  ->  only a HIGH-oob ws1cp may open, and it makes a SHORT

That direction matches `_ibmech`'s entry rule - a cp's trade heads AWAY from the board its own cp
fired on - so the gate never contradicts the mech it gates.

THE RELEASE, his: *"it's always x-crossing under on a high oob"*, so the ws60x cross is the UNDER
direction only. Measured from the 2026-07-18 21:17:55 exit, 57 ws60x/ws60r crosses occur before
03:09 and only 8 hold the 48-bar wob; the rest are 5-to-45-second flickers. With UNDER-only the
first qualifying one is 2026-07-19 01:00:00, its wob completes 01:03:55, and ws30r is IB at
01:05:45 - the row Joe banked.

SRP: this file owns the gate and nothing else. It opens no trade, closes none, and holds no state
across calls. `_ibmech` stamps the cps, `_extmom` holds the close, `_chain10` walks - none of them
know this exists; the caller asks the gate before it opens.

CAUSAL. `oob_side` reads one bar. `release` walks FORWARD from the bar it is given and the wob is a
hold, so the release bar is the bar on which the release becomes knowable - not earlier.
"""
import os
import numpy as np

# THE KNOB NAMES ARE MINE; the values are Joe's.
TFS = tuple(int(z) for z in os.environ.get('W_HTF_TFS', '30,45,60,90').split(','))
X_TF = int(os.environ.get('W_HTF_X_TF', 60))        # the x/r pair the release reads, ws60
IB_TF = int(os.environ.get('W_HTF_IB_TF', 30))      # the line that must be IB, ws30
WOB = int(os.environ.get('W_HTF_X_WOB', 48))        # Joe: "a 48 wob", 48 bars = 4.0 min
ON = os.environ.get('W_HTF_GATE', '1') == '1'


class HTFGate:
    """The gate over one tape. Build once, then `oob_side` and `release`."""

    def __init__(self, sc):
        n = len(sc.ts)
        self.n = n
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        self.r = {t: np.asarray(sc.LD(t * 60, 'r'), float)[:n] for t in TFS}
        self.x = np.asarray(sc.LD(X_TF * 60, 'x'), float)[:n]
        self.xr = np.asarray(sc.LD(X_TF * 60, 'r'), float)[:n]
        self.ib = self.r[IB_TF] if IB_TF in self.r else \
            np.asarray(sc.LD(IB_TF * 60, 'r'), float)[:n]

    # ---- the restriction
    def oob_side(self, k):
        """Is an HTF r line oob at bar `k`? -> (the cp side permitted, tf, which end, its value).

        The cp side is Joe's: HTF HIGH oob permits a LOW cp (-1), HTF LOW oob permits a HIGH cp
        (+1). -> (None, None, None, None) when no HTF line is oob and every cp is permitted.
        THE FIRST oob LINE IN TF ORDER WINS. Joe named no tie-break and the lines have not been seen
        oob on opposite ends at the same bar; if that ever happens this picks the lowest TF and the
        caller should be told. STATED.
        """
        k = int(k)
        for t in TFS:
            if t not in self.r:
                continue
            v = float(self.r[t][k])
            if v >= self.hi:
                return -1, t, 'HIGH', v
            if v <= self.lo:
                return +1, t, 'LOW', v
        return None, None, None, None

    def release(self, frm):
        """-> (the release bar, the cross bar), or (None, None).

        Joe: *"the restriction ends when ws30r is IB after ws60x-crosses r with a 48 wob"*, and
        *"it's always x-crossing under on a high oob"* - so UNDER only. The cross must hold WOB
        bars, then the first bar ws{IB_TF}r is inside the oob fence releases it.
        FORWARD LOOP, and the release bar is never earlier than the wob's own completion.
        """
        frm = int(frm)
        under = self.x < self.xr
        for k in range(frm + 1, self.n):
            if not (under[k] and not under[k - 1]):
                continue
            end = min(k + WOB, self.n)
            if not bool(under[k:end].all()):
                continue
            wb = k + WOB - 1
            for q in range(wb, self.n):
                if self.lo < float(self.ib[q]) < self.hi:
                    assert q >= k and q >= wb, 'the HTF release landed before its own wob completed'
                    return q, k
            return None, k
        return None, None

    def permits(self, cp_side, allowed_cp_side, cp_ib_bar, release_bar):
        """May a cp open a trade? -> bool.

        Permitted when there is no restriction, when the cp's ib bar is at or after the release, or
        when the cp is on the side the restriction allows.
        """
        if allowed_cp_side is None:
            return True
        if release_bar is not None and int(cp_ib_bar) >= int(release_bar):
            return True
        return int(cp_side) == int(allowed_cp_side)


def trade_side(cp_side):
    """`_ibmech`'s entry rule, restated here so a caller need not re-derive it.
    HIGH cp (+1) -> a SHORT, dr +1.   LOW cp (-1) -> a LONG, dr -1.
    """
    return +1 if int(cp_side) > 0 else -1
