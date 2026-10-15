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
REN_WOB = int(os.environ.get('W_HTF_REN_WOB', 0))   # the re-enable's hold, 0 bars = none
ON = os.environ.get('W_HTF_GATE', '1') == '1'

# W_HTF_REN_WOB IS NOT RULED. Joe gave the release "a 48 wob" and gave the re-enable no hold at
# all, so 0 is the literal reading of his spec and the default stays there until he rules on it.


class HTFGate:
    """The gate over one tape. Build once, then `oob_side` and `release`."""

    def __init__(self, sc, wob=None, ren_wob=None, x_tf=None):
        self.wob = int(WOB if wob is None else wob)
        self.ren_wob = int(REN_WOB if ren_wob is None else ren_wob)
        self.x_tf = int(X_TF if x_tf is None else x_tf)
        n = len(sc.ts)
        self.n = n
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        self.r = {t: np.asarray(sc.LD(t * 60, 'r'), float)[:n] for t in TFS}
        self.x = np.asarray(sc.LD(self.x_tf * 60, 'x'), float)[:n]
        self.xr = np.asarray(sc.LD(self.x_tf * 60, 'r'), float)[:n]
        self.ib = self.r[IB_TF] if IB_TF in self.r else \
            np.asarray(sc.LD(IB_TF * 60, 'r'), float)[:n]

    # ---- the restriction
    def oob_side(self, k):
        """Is an HTF r line oob at bar `k`? -> (the cp side permitted, tf, which end, its value).

        The cp side is Joe's: HTF HIGH oob permits a LOW cp (-1), HTF LOW oob permits a HIGH cp
        (+1). -> (None, None, None, None) when no HTF line is oob and every cp is permitted.
        The third return value is the END, 'HIGH' or 'LOW', which `release` needs for its cross
        direction.
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

    def release(self, frm, htf_end):
        """-> (the release bar, the cross bar), or (None, None).

            htf_end  +1 the HTF line is HIGH oob, -1 it is LOW oob.

        Joe: *"the restriction ends when ws30r is IB after ws60x-crosses r with a 48 wob"*.

        THE CROSS DIRECTION MIRRORS THE oob END, Joe 1013: *"the 08:22 oob-hack ws60x-cross is
        inverted - if ws{oob-hack HTF}r is low oob, then the restriction can only be completed by a
        x-cross over. inverted for high-oob: the x crosses under"*, which extends his earlier
        *"it's always x-crossing under on a high oob"*.
            HTF HIGH oob  ->  ws{X_TF}x crosses UNDER r
            HTF LOW  oob  ->  ws{X_TF}x crosses OVER  r
        BUILT UNDER-ONLY FIRST, 1013, and that was wrong on every LOW-oob restriction. The 2026-07-19
        08:03:10 one released at 08:22:15 off an UNDER cross it should have ignored.

        The cross must hold WOB bars, then the first bar ws{IB_TF}r is inside the oob fence releases
        it. FORWARD LOOP, and the release bar is never earlier than the wob's own completion.
        """
        frm = int(frm)
        # the side the x must be on AFTER the cross: under r for a HIGH-oob HTF, over r for a LOW one
        want_under = int(htf_end) > 0
        under = (self.x < self.xr) if want_under else (self.x > self.xr)
        for k in range(frm + 1, self.n):
            if not (under[k] and not under[k - 1]):
                continue
            end = min(k + self.wob, self.n)
            if not bool(under[k:end].all()):
                continue
            wb = k + self.wob - 1
            for q in range(wb, self.n):
                if self.lo < float(self.ib[q]) < self.hi:
                    assert q >= k and q >= wb, 'the HTF release landed before its own wob completed'
                    return q, k
            return None, k
        return None, None

    def re_enable(self, frm, htf_end):
        """-> the bar the restriction comes back on, or None. Walked FORWARD from `frm`.

        Joe 1013: *"the missing mech is: the restriction is re-enabled if that ws{oob-hack}x
        reversed after the x-cross-over, and has crossed under r"*, then on the line and the test:
        *"we're designing causal code - we don't get to choose which cross. you know that BB%B lines
        lead K lines, therefore a cross under r when r is low oob is going to produce downward pxs.
        drop my 'pushing r deeper into oob' - it's confused the situation"*.

        So the test is two states on the SAME pair the release reads, ws{X_TF}x and ws{X_TF}r:
            the restriction was LOW  oob  ->  x crosses UNDER r, and r is LOW  oob at that bar
            the restriction was HIGH oob  ->  x crosses OVER  r, and r is HIGH oob at that bar
        the opposite cross to the release, with r oob on the restriction's own end.

        THE HOLD, `ren_wob`, is 0 bars by default = no hold, because Joe specified none. With a
        hold the cross must stay on its side `ren_wob` bars and the re-enable is stamped on the bar
        the hold completes, mirroring the release. The oob test is read AT THE CROSS BAR - his words
        are "a cross under r when r is low oob", which is a state at the cross.

        NO "DEEPER" TEST - he dropped it, and the oob test alone does the work. MEASURED on the
        2026-07-19 08:03:10 LOW-oob restriction released 08:15:50: seven UNDER crosses follow, and
        ws60r sits at 19.23 to 19.50 on the first six - not oob - while the seventh at 09:15:10 has
        it at 9.16, LOW oob. One of seven survives, and it is the ws1-cp bar of the LONG that lost
        0.7911%. Without the oob test the restriction would come back at 08:17:30 and never lift.
        """
        frm = int(frm)
        high = int(htf_end) > 0
        # the re-enable cross is the OPPOSITE of the release's
        side = (self.x > self.xr) if high else (self.x < self.xr)
        w = max(1, self.ren_wob)
        for k in range(frm + 1, self.n):
            if not (side[k] and not side[k - 1]):
                continue
            v = float(self.xr[k])            # the oob state AT THE CROSS, his "when r is low oob"
            if not ((v >= self.hi) if high else (v <= self.lo)):
                continue
            end = min(k + w, self.n)
            if not bool(side[k:end].all()):
                continue
            q = k + w - 1                    # the bar the hold completes - when it becomes knowable
            assert q >= k, 'the HTF re-enable landed before its own cross'
            return q
        return None

    def active_at(self, bar, frm, htf_end):
        """Is the restriction active at `bar`, having started at `frm`? -> bool.

        Alternates release / re-enable forward from `frm`. Every bar read is at or before the bar
        whose state it reports, so a caller asking about a cp's ib bar is asking causally.
        """
        bar, frm = int(bar), int(frm)
        k = frm
        on = True
        while k <= bar:
            if on:
                rel, _x = self.release(k, htf_end)
                if rel is None or rel > bar:
                    return True
                k = rel; on = False
            else:
                ren = self.re_enable(k, htf_end)
                if ren is None or ren > bar:
                    return False
                k = ren; on = True
        return on

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

    def permits_live(self, cp_side, allowed_cp_side, cp_ib_bar, frm, htf_end):
        """`permits` with the release/re-enable alternation applied - the form the walk uses once
        the re-enable exists. A cp is permitted when the restriction is not active at its ib bar, or
        when the cp is on the side the restriction allows."""
        if allowed_cp_side is None:
            return True
        if not self.active_at(cp_ib_bar, frm, htf_end):
            return True
        return int(cp_side) == int(allowed_cp_side)


def cp_side_for(dr):
    """The INVERSE of `trade_side`: which cp side places a trade of side `dr`? -> +1 HIGH, -1 LOW.

    A HIGH cp (+1) places a SHORT (dr +1); a LOW cp (-1) places a LONG (dr -1). So the cp side and
    the trade side carry the SAME sign, and this function is here because I have now got that sign
    backwards three times in one session - most recently in the chain report's gap column, which
    read 21:17:55 as permitted when it is blocked. One place, asserted.
    """
    dr = int(dr)
    assert dr in (-1, +1), 'a trade side is +1 (SHORT) or -1 (LONG), got %r' % (dr,)
    cp = dr
    assert trade_side(cp) == dr, (
        'cp_side_for and trade_side disagree: cp %+d maps to dr %+d, not %+d'
        % (cp, trade_side(cp), dr))
    return cp


def trade_side(cp_side):
    """`_ibmech`'s entry rule, restated here so a caller need not re-derive it.
    HIGH cp (+1) -> a SHORT, dr +1.   LOW cp (-1) -> a LONG, dr -1.
    """
    return +1 if int(cp_side) > 0 else -1
