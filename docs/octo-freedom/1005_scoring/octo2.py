"""`octo2`. 1016. JOE'S NAME: *"this is a new machine that we're building now, named `octo2`"*.

WHAT IT IS. A side-event machine. A side-event both closes and opens, which is Joe's 1016 ruling:
*"the exits are the same as the entries in my eyes"* / *"I'm calling it"*.
    a LOW-side event   closes every open SHORT and opens a LONG
    a HIGH-side event  closes every open LONG  and opens a SHORT
HIS SIDE RULE, 1016, which is what forced the structure: *"because there was already an OPEN LONG
printing at 19:12, and 19:12 is low side, there is no action to take on the already opened LONG
trade. the only thing that interacts with a LONG is a high oob EXIT -this means your correction is
poisoned, because you weren't aware that the OPEN long can't be touched by a low-side signal. the
only thing the low-side signal can do is open a LONG trade"*.

THE MAIN-CHAIN MACHINE IS SEPARATE AND IS NOT TOUCHED. Joe 1016: *"when it's further developed,
we'll need to integrate the main-chain machine"*. Until then `octo2` wires only its own mechs and
`docs/octo-freedom/main_chain_handover.md` holds the main chain's pick-up state. Joe 1016 on that
integration: *"still benched for now"*.

THIS MACHINE'S SPEC IS `docs/octo-freedom/octo2_spec.md` - every in-use mech with Joe's verbatim
words, the banked knob table, and the open decisions. Read it before changing anything here.

SRP, AND WHAT EACH PART OWNS
    `_conj.py`          the conjunction - its role map, its span, the ws2/ws3 patch, the ws1Mage
                        gate and its slack, and the x-cross lookback that consumes it
    `_bouncepred.py`    the continuance / reverse verdict at a ws5Mage oob reversal
    `_lineage_conf.py`  lineage as a confluence verdict. It CANNOT return a bar
    `optimus9.analysis.jig`  every producer. Joe 1016: *"any producers need to be in the jig"*
    this file           the walk - the trigger order, the standdown, the cap, the side rule
It opens and closes trades and owns nothing else.

THE TRIGGERS, in the order they were built
    ws5Mage ENTERING oob, either side. On 2026-07-22 this beat every gated turn-predictor by
      6.24 hours, and its signal bar sat 0.75 min before the 19:13:15 L price pivot
    the GATED TURN-PREDICTOR - the conjunction with Joe's 1015 gate: *"the turn signal can only
      fire if ws1Mage is same-side oob"*

THE BANKED STATE, Joe 1016: *"g15 ws5/fwd/ex/xwob1/step1 +173.9969% / bank this as our state and
make the machine live. no mom-xfer"*.
    the hold's grid      g15ib - the g15Mage ib-cross grid, `_bp_g15.py`
    the sample side      ws5 - the side ws5Mage crossed to
    the pairing          fwd - this cross and the next
    the fence            ex - 83/17
    the cross hold       xwob 1 bar = 5 s
    the step             1 cross forward
    mom-xfer             OFF. His words: *"no mom-xfer"*
    net over 94 days     +173.9969% on the banked drag 0.1975% per trade: gross +399.7394%,
                         1143 trades, drag 225.7425% = 56.5% of gross
    it was 1st of 34 fill-model arms on net, against the superseded fixed grid's +125.7001%

`bounce-pred` HAS PRIORITY OVER THE TURN-PREDICTOR. Joe 1016: *"bounce-pred has prioirty over
turn-predictor"*. A `continuance` verdict means WAIT - the bouncing is still running and a higher
TF has not finished its journey; `reverse` means the pivot has happened and the entry is good.
    on the ws5Mage-oob path      always held by bounce-pred
    on the turn-predictor path   held WHENEVER ws5Mage is oob at the event bar
HIS EARLIER WORDING, SUPERSEDED BY THE LINE ABOVE AND KEPT SO THE CHANGE IS LEGIBLE: *"`bounce-pred`
is not applied to a `turn-detection` event"*. It let 2026-07-22 00:23:55 through unheld with ws5Mage
at 102.92 - HIGH oob - which is the event Joe then called out: *"when 00:23 prints `continuance`,
the 00:23 signal is held until `reverse` prints at ~01:08 (+ the additional 10 minutes need to
confirm the `reverse` signal). in this example, the SHORT opens at ~01:18"*.

THE HOLD STARTS AT THE EVENT BAR, not at the conjunction's fire bar. Joe named *"00:23"*, which is
the event bar 00:23:55 (the x-cross confirmation); the fire was 00:22:00. STRUCTURAL AND STATED: the
event bar is the bar the event exists at, so it is the only bar the hold can causally start from.

WHAT ENDS THE HOLD IS STILL JOE'S OPEN DECISION. `_bouncepred.walk` stops at the FIRST reverse. On
his own 00:02:10 to 01:10:30 episode the verdict flips 25 times (68 continuance, 60 reverse) and the
first reverse is a 1-of-30 flicker at 00:06:00, so the first-reverse rule lands 1 h 2 min before the
01:18:15 bar he named. REPORTED TO HIM, NOT DECIDED HERE.

THE STANDDOWN, Joe 1016: *"until we have a reason to change: require a 4 minute standdown after a
trade is printed. the logic (untested, possibly unsound): if the pivot is still pivoting after 4
minutes then there's a lot of trading activity happening, which might indicate the end of a larger
cycles momentum"*. 48 bars. MEASURED: on the 2026-07-22 22:10:35 leg it suppressed three ws5Mage
flicker triggers at 22:12:35, 22:13:30 and 22:13:55.

THE CAP, Joe 1015: *"for the second LONG, pyramid it. max 2 same-target trades at any given time"*.

LINEAGE IS CONFLUENCE ONLY, Joe 1015. It is read, never acted on, and `_lineage_conf.read()`
returns no bar so it cannot become an entry or an exit by accident.

THE NON-OOB BAND IS DISABLED, Joe 1016: *"disable it"*. The producer stays in the jig as
`mage_band_split` with its in-use costs recorded there.

CAUSAL. Every trigger bar is the bar its own event becomes knowable - a conjunction fires at the
k-th CONFIRMATION, an x-cross at its xwob completion, a bounce-pred verdict at its +10 min offset.
The x-cross lookback only ever reaches BACKWARD from a bar that has arrived.
"""
import os
import numpy as np

import _conj as CJ
import _bouncepred as BP
import _ibmech as IBM
from optimus9.analysis.jig import next_oob_divergence

STANDDOWN = int(os.environ.get('W_CONJ_STANDDOWN', 48))   # 4 min, Joe 1016
CAP = int(os.environ.get('W_CONJ_CAP', 2))                # Joe 1015
USE_BP = os.environ.get('W_OCTO2_BP', '1') == '1'
USE_TURN = os.environ.get('W_OCTO2_TURN', '1') == '1'
USE_OOB = os.environ.get('W_OCTO2_OOB', '1') == '1'
# BANKED DEFAULT 1 = Joe's 1016 ruling *"bounce-pred has prioirty over turn-predictor"*. 0 restores
# the superseded exemption, for an A/B only.
BP_PRIORITY = os.environ.get('W_OCTO2_BP_PRIORITY', '1') == '1'
# W_OCTO2_GRID - which grid the hold is measured on. BANKED 'g15ib', Joe 1016:
# *"g15 ws5/fwd/ex/xwob1/step1 +173.9969% / bank this as our state and make the machine live.
# no mom-xfer"*. His own idea: *"instead of a fixed width, collect samples on each g15Mage crossing
# back to ib (on the target side). the logic: we're sampling at locations that are consistent
# within the market's cycles"*. 'fixed' is the superseded two-fixed-offset mech, kept for A/B only.
#
# WHAT THE BANK RETIRES. Under 'g15ib' the two fixed offsets W_BP_OFF_A and W_BP_OFF_B ARE NOT
# READ - `_bp_g15` takes its two sample bars from the g15Mage ib-crosses, not from an offset. So
# the +7.5/+9.5 pair I proposed on 94-day fidelity is MOOT and that decision is closed. The offsets
# stay ruled in `_ruled.py` because the 'fixed' A/B path still reads them.
GRID = os.environ.get('W_OCTO2_GRID', 'g15ib')
# ── THE ENTRY TIMING. BANKED 1017 as Joe's "A". ───────────────────────────────────────────────
# WHAT IT REPLACES: until 1017 a verdict opened AT its own bar. That cost real net once an MAE cap
# was applied - his own words: *"now is a good time to fix the net value - without an MAE cap, the
# numbers don't mean a lot when we start gating"*. At his 1.60 cap, firing at the verdict bar earns
# +1.4405% over the 40 trades of 2026-08-22 to 2026-08-24 against this mech's +14.5689% over 34.
#
# HIS SPEC, 1017 verbatim: *"wait for the next high-side g30Mage oob, and use that bar as the
# anchor for a divergence test / --if the divergence test is bearish, then open the SHORT"*.
# And the shape, ruled after I put the two causal readings to him: *"bank A"*, A being *"wait for
# option 2, no fallback"*. He confirmed the fallback is NOT causal - picking which signals to not
# wait for needs the exit bar, which is in the future at the verdict.
#   SO A VERDICT THAT NEVER FIRES PRODUCES NO TRADE. 6 of the 40 fire at or after their own exit
#   and are simply given up, worth +8.2009% at the cap. That is the cost of the bank and it is his.
#
# THE SIDE IS THE TRADE'S, from his own words *"because this a SHORT ... the next high-side"*. The
# EVENT-side variant measured +12.2153% over 30 trades and is NOT banked; W_OCTO2_FIRE_SIDE='event'
# runs it for an A/B.
FIRE = os.environ.get('W_OCTO2_FIRE', 'oobdiv')   # 'oobdiv' = Joe's A. 'verdict' = the old bar.
FIRE_TF = int(os.environ.get('W_OCTO2_FIRE_TF', 30))      # SECONDS. g30Mage, his own line
# THE EVENT-SIDE A/B IS NOT OFFERED HERE. It measured +12.2153% over 30 trades against the trade
# side's +14.5689% over 34, but it keys off the ws1cp's oob side and octo2 does not track that -
# the diagnostic read it from `_ibmech.cps`. Offering a knob that reads the VERDICT's side instead
# would be a different mech wearing the measured arm's name, so there is no knob.
# ── THE MAE CAP. Joe 1017: *"apply a 1.6 MAE cap. if the cap is hit, the MFE for that row is set
# to zero"*, and asked whether that means the row realises the cap loss: *"-yes"*. So a stopped row
# realises -MAE_CAP, and drag is added on top of it by the report, never in here.
#   WHY 1.60 AND NOT LOWER, his reason, not a fit: *"MAE is intentionally higher (1.6) because our
#   window is a high MFE zzone"*. Measured beside it: 0.70 is `trade_config`'s own `mae_cap` and
#   1.10 is lineage's `stop`; both earn LESS on this window because more trades are stopped before
#   they resolve. 1.60 is also the peak of the swept range for every arm, on 40 trades.
#   IT STOPS 17 of the 40 at the old entry timing and 13 of the 34 at this one.
MAE_CAP = float(os.environ.get('W_OCTO2_MAE_CAP', 1.60))
# STOP WINS A TIE. INHERITED, not mine: `trade_config`'s `stop_same_bar_priority` is 'stop',
# Joe 0929 *"use stop"*.
MAE_CAP_ON = os.environ.get('W_OCTO2_MAE_CAP_ON', '1') == '1'
# ── THE TRADE FLIP. Joe 1018: *"ok, wire it in and resweep"*, the mech being the one he named the
# *"trade flip mech"* / *"the printed SHORT is more likely to flip to a LONG"*.
#   WHAT IT DOES: at a verdict that would open, the 4-voters-against suite is asked whether the
#   OPPOSITE side is validated. If the suite ALLOWS it - fewer than W_VOTE_MIN objections - the
#   open FLIPS to that side. If the suite kills it, the printed side stands untouched.
#   SO IT IS A FLIP, NOT A BLOCK. MINE BY HIS NAMING, STATED: he has called it the flip mech twice
#   and never asked for a block. A block variant would be a different knob.
#   NO SECOND VOTE ON THE FLIPPED SIDE. The against-vote has already tested that exact side and
#   allowed it; asking again is the same call. STRUCTURAL AND STATED.
#   THE CAP IS CHECKED ON THE FINAL SIDE, after any flip, so a flip cannot break the pyramid rule.
#   THE VETO'S no-open PATH IS UNTOUCHED - the flip test only runs where something would open.
FLIP = os.environ.get('W_OCTO2_FLIP', '0') == '1'    # DEFAULT OFF until the sweep rules it


class Octo2:
    """The machine over one tape. Build once, then `events` and `walk`."""

    def __init__(self, sc, mxgate=None):
        """`mxgate` is an optional `_momxfer.MomXfer`. Joe 1016: *"test its application as a gate
        on bounce-pred"*. INJECTED, not imported here, so this file keeps no dependency on the
        racer lines or their banks. None means no gate, which is the banked behaviour.

        WHAT THE GATE DOES: it WITHHOLDS a `reverse` that bounce-pred already produced, so no event
        is emitted at that bar. The walk does NOT then continue hunting a later reverse -
        `_bouncepred.walk` has already stopped. MINE AND STATED; Joe said *"a gate"*, and
        withholding is the minimal reading. Carrying on to a later reverse is a different mech.
        """
        n = len(sc.ts)
        self.n = n
        self.sc = sc
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        self.px = np.asarray(sc.PX, float)[:n]
        # the entry-timing mech's own lines. CLOSE is RAW - `jig.divergence` requires it.
        self.fire_line = np.asarray(sc.LD(FIRE_TF, 'Mage'), float)[:n]
        self.fire_r = np.asarray(sc.LD(60, 'r'), float)[:n]
        self.fire_px = (np.asarray(sc.CLOSE, float)[:n] if sc.CLOSE is not None else self.px)
        self.conj = CJ.Conj(sc)
        # THE ws1cp SIDE. The flip test's vote needs the EVENT's oob side - Joe 1017: *"extrema
        # must be same-side as the event's side (not the events' SHORT or LONG verdict)"* - and
        # octo2 did not track it. Built here from `_ibmech`, the ws1cp mech, which is the same
        # producer the diagnostics read it from. Lazy: only built when the flip is on.
        self._cps = None
        self.vote = None
        self.bp = BP.BouncePred(sc)
        # THE HOLD'S GRID. Both objects expose the same walk(frm, side, until) contract and both
        # stop on the first REVERSE, so the paths below do not branch on the grid.
        if GRID == 'g15ib':
            import _bp_g15 as G15
            self.hold = G15.BouncePredG15(sc, bp=self.bp)
        else:
            self.hold = self.bp
        self.x5 = np.asarray(sc.LD(BP.TRIG_TF * 60, 'x'), float)[:n]
        self.m5 = self.bp.trig
        self.oob = (self.m5 >= self.hi) | (self.m5 <= self.lo)
        # `veto-on-momentum`, Joe 1016. BUILT AFTER m5, which it reads - it needs both the hold object
        # that takes over at the handover and the ws5Mage line. It vetoes a CLOSE; it never gates
        # an entry.
        import _vetomom as VOM
        self.vom = VOM.VetoOnMomentum(sc, self.hold, self.m5) if VOM.ON else None
        self.vom_rows = []                 # every bar the veto fired, for the report
        self.mxgate = mxgate
        self.mx_blocked = []                  # every (bar, side, src, why) the gate withheld

    # ---- the triggers
    def oob_entries(self, frm, until):
        """ws5Mage ENTERING oob, either side. -> [(bar, side)]. An entry, not a state: being in
        oob cannot re-trigger, which is what let a 40-second flicker become a second SHORT on
        2026-07-22 before Joe accepted it explicitly."""
        out = []
        for j in range(int(frm) + 1, int(until) + 1):
            if self.oob[j] and not self.oob[j - 1]:
                out.append((j, +1 if self.m5[j] >= self.hi else -1))
        return out

    def turn_fires(self, frm, until):
        """The gated turn-predictor, both sides. -> [(bar, side, members, patched)]."""
        out = []
        for side in (+1, -1):
            for j, mem, p in self.conj.fires(frm, side, until=until):
                out.append((j, side, mem, p))
        return sorted(out)

    def events(self, frm, until):
        """Every side-event, in bar order. -> [(bar, side, source, note)].

        A ws5Mage-oob trigger is passed through `bounce-pred`, which may DELAY it to the verdict's
        knowable bar or hold it entirely on a `continuance`. A turn-predictor fire is exempt.
        """
        ev = []
        if USE_OOB:
            for j, side in self.oob_entries(frm, until):
                if not USE_BP:
                    ev.append((j, side, 'ws5Mage oob', 'bounce-pred off'))
                    continue
                w = self.hold.walk(j, side, until=until)
                if not w:
                    continue
                rb, v, ka, med, pos, why = w[-1]
                if v != BP.REVERSE:
                    continue        # continuance - the bouncing is still running, WAIT
                if self.mxgate is not None:
                    ok = self.mxgate.read(rb, ka, side)[0]
                    if not ok:
                        self.mx_blocked.append((ka, side, 'ws5Mage oob',
                                                self.mxgate.why(rb, ka, side)))
                        continue
                if ka <= until:
                    ev.append((ka, side, 'ws5Mage oob + bounce-pred reverse',
                               'the reversal was %s; %s' % (self.sc.U(rb), why)))
        if USE_TURN:
            for j, side, mem, p in self.turn_fires(frm, until):
                c, cf, dirn = self.conj.cross_for(j, side, self.x5, self.m5)
                if cf is None or cf > until:
                    continue
                # NOTHING MAY BE STAMPED BEFORE THE INFORMATION THAT PRODUCED IT. The x-cross is
                # found by looking BACKWARD from the fire, so its confirmation bar can sit EARLIER
                # than the fire - and the event used to be stamped there. Measured on
                # 2026-08-24 10:28:05: the event was recorded 26 bars = 130 s before its own fire
                # at 10:30:15, which in a live run would be placing a trade two minutes ago.
                # THE STAMP TAKES THE LATER BAR, which is the banked stamp rule: additive, max(),
                # never swap. Joe 1016: *"repair the lookahead as needed"*.
                # The HOLD's start bar takes it too - a hold that begins before the fire could
                # sample a bar the machine had not yet earned.
                know = max(int(cf), int(j))
                if know > until:
                    continue
                how = ('the fire was %s, the cross ran %s, confirmed %s, knowable %s; %s'
                       % (self.sc.U(j), dirn, self.sc.U(cf), self.sc.U(know), ', '.join(mem)))
                # BOUNCE-PRED HAS PRIORITY. Joe 1016. The hold applies whenever ws5Mage is oob at
                # the event bar - the mech's own firing condition, Joe 1016: *"it will only fire
                # when ws5Mage is oob"*. When ws5Mage is in-fence there is nothing to hold and the
                # event stands on its own bar.
                if USE_BP and BP_PRIORITY and self.bp.trig_oob(know, side):
                    w = self.hold.walk(know, side, until=until)
                    if not w:
                        continue
                    rb, v, ka, med, pos, why = w[-1]
                    if v != BP.REVERSE:
                        continue    # continuance - the bouncing is still running, WAIT
                    if self.mxgate is not None:
                        if not self.mxgate.read(rb, ka, side)[0]:
                            self.mx_blocked.append((ka, side, 'the turn-predictor',
                                                    self.mxgate.why(rb, ka, side)))
                            continue
                    if ka <= until:
                        ev.append((ka, side, 'the turn-predictor + bounce-pred reverse',
                                   '%s | held from %s, the reversal was %s; %s'
                                   % (how, self.sc.U(know), self.sc.U(rb), why)))
                    continue
                ev.append((know, side, 'the turn-predictor', how))
        # THE CAUSALITY INVARIANT, ASSERTED. Every turn-predictor event bar must be at or after
        # its own fire bar. A comment would not have caught the 2026-08-24 10:28:05 fault; this
        # does, on every run.
        for _b, _s, _src, _nt in ev:
            if 'turn-predictor' in _src:
                _m = _nt.split('the fire was ')
                if len(_m) > 1:
                    _fb = self.sc.K(_m[1][:19])
                    assert _b >= _fb, ('event %s is stamped before its own fire %s'
                                       % (self.sc.U(_b), self.sc.U(_fb)))
        # DEDUPE ON (bar, side). A bar is one side-event however many triggers landed on it.
        #   found 1016, run 1: several ws5Mage oob entries inside one bounce-pred walk resolve to
        #     the SAME knowable bar - 2026-07-22 01:04:05 printed four times
        #   found 1016, run 2 (the priority ruling): the oob path and the turn-predictor path now
        #     resolve to the same bar through the same bounce-pred reverse - 2026-07-22 00:47:30
        #     printed twice, once per path
        # THE KEY DROPS THE SOURCE. STRUCTURAL AND STATED: with the source in the key, the same
        # reverse at the same bar on the same side counts twice purely because two paths found it,
        # which is the double-count the first dedupe was written to stop. The earliest source in
        # bar order owns the row and the other path's name is recorded on it.
        seen, out = {}, []
        for bar, side, src, note in sorted(ev):
            key = (bar, side)
            if key in seen:
                i = seen[key]
                if src != out[i][2] and src not in out[i][3]:
                    out[i] = (out[i][0], out[i][1], out[i][2],
                              out[i][3] + ' || also found by: %s' % src)
                continue
            seen[key] = len(out)
            out.append((bar, side, src, note))
        return out

    # ---- the flip
    def cp_side(self, bar):
        """The oob side of the most recent ws1cp at or before `bar`. -> +1 high / -1 low / None."""
        if self._cps is None:
            self._cps = IBM.IBMech(self.sc).cps(0, self.n - 1)
        pr = [d for j, d in self._cps if j <= int(bar)]
        return int(pr[-1]) if pr else None

    def flip_dr(self, bar, open_dr):
        """Does the 4-voters-against suite validate the OPPOSITE side at `bar`. -> (dr, why).

        Returns the side to open and the trace. The returned dr is the FLIPPED one when the suite
        allows it, else `open_dr` unchanged.
        """
        if not FLIP:
            return int(open_dr), ''
        if self.vote is None:
            import _openvote as OVM
            self.vote = OVM.OpenVote(self.sc)
        es = self.cp_side(bar)
        if es is None:
            return int(open_dr), 'no ws1cp before this bar, so no flip test'
        ag = -int(open_dr)
        kills, n, vrows, _vb, _vw = self.vote.vote(int(bar), ag, es)
        if kills:
            return int(open_dr), ('the flip to %s was KILLED %d of 4'
                                  % ('SHORT' if ag > 0 else 'LONG', n))
        return ag, ('FLIPPED to %s, the against-vote ALLOWED it %d of 4'
                    % ('SHORT' if ag > 0 else 'LONG', n))

    # ---- the entry timing and the stop
    def fire_bar(self, bar, dr, until):
        """The bar a verdict at `bar` physically enters on. -> (bar, why) or None.

        Joe 1017's A: the next g30Mage oob on the TRADE's side that anchors a divergence firing the
        trade's direction. No fallback - None means no trade. The producer is the jig's.
        """
        if FIRE == 'verdict':
            return int(bar), 'the verdict bar'
        return next_oob_divergence(self.fire_line, self.fire_r, self.fire_px,
                                   int(bar), int(dr), int(dr), self.hi, self.lo, until=int(until))

    def stop_bar(self, t, upto):
        """The first bar `t`'s adverse excursion reaches MAE_CAP, at or before `upto`. -> bar/None.

        Joe 1017: *"apply a 1.6 MAE cap. if the cap is hit, the MFE for that row is set to zero"*
        and, asked whether the row then realises the cap loss, *"-yes"*. The LOSS is the report's
        to compute - this method only says where the trade ends. NO PnL IN HERE.
        """
        if not MAE_CAP_ON:
            return None
        e, dr = int(t['entry']), int(t['dr'])
        upto = int(upto)
        if e > upto:
            return None
        seg = self.px[e:upto + 1]
        adv = (seg - self.px[e]) / self.px[e] * 100.0 * (1 if dr > 0 else -1)
        w = np.flatnonzero(adv >= MAE_CAP)
        return (e + int(w[0])) if len(w) else None

    def _settle(self, upto, live, pending):
        """Promote pending trades whose entry has arrived, then stop anything that has hit the cap.

        -> the trades closed by the stop, in exit order.
        ORDER IS DELIBERATE: a trade promoted at `upto` is stop-checked in the same call, because
        its own entry bar can already be the bar the cap is reached on.
        """
        for t in list(pending):
            if int(t['entry']) <= int(upto):
                pending.remove(t)
                live.append(t)
        out = []
        for t in list(live):
            sb = self.stop_bar(t, upto)
            if sb is not None:
                t['exit'] = sb
                t['exit_reason'] = 'the %.2f MAE cap' % MAE_CAP
                live.remove(t)
                out.append(t)
        out.sort(key=lambda z: z['exit'])
        return out

    # ---- the walk
    def walk(self, frm, until):
        """-> (the rows, the still-open trades).

        rows   [(bar, side, source, note, [closed], the opened trade or None, open count)]
        A trade is {'dr', 'entry', 'exit', 'source', 'exit_reason'}. dr +1 SHORT, -1 LONG.
        `source` is the event that OPENED it. `exit_reason` is the event that CLOSED it, stamped
        at the close. Joe 1016: *"I just saw that the colum is `the source`. that's counter
        intuitive when you place it next to the exit. instead of `the source` coumn, create a
        `exit reason` column"*. A report prints `exit reason` beside the exit, never `source`.
        """
        rows, live, pending, last_print = [], [], [], None
        self.stop_rows = []
        # THE MECH OWNS NO EXIT. Joe 1017: *"I think it's better that the spec's edge is contained
        # to the actual activities of the mech, and let the machine handle everything that is not
        # involved in creating the veto, redirecting, pyramid flow, etc at the time of the verdict's
        # bar(s)"*. So `veto-on-momentum` acts only AT the verdict bar and the protected trade is
        # closed by whatever the machine's next closing event is, like every other trade. The ride
        # to ws5Mage's target-side oob, the handover to bounce-pred and the
        # `veto-on-momentum ride` exit reason are all gone with it.
        for bar, side, src, note in self.events(frm, until):
            # PENDING -> LIVE, AND THE STOP, up to and including this bar. A stop is not an event,
            # so a trade it closes is recorded on THIS row's `closed` list with its own true exit
            # bar, and in `self.stop_rows` at that bar so the stop is traceable where it happened.
            stopped = self._settle(bar, live, pending)
            for t in stopped:
                self.stop_rows.append((int(t['exit']), int(t['dr']), t['exit_reason'],
                                       'armed %s, entered %s'
                                       % (self.sc.U(t['armed']), self.sc.U(t['entry']))))
            if last_print is not None and bar - last_print < STANDDOWN:
                if stopped:
                    rows.append((bar, side, 'the MAE cap closed a trade', '', stopped, None,
                                 len(live) + len(pending)))
                continue
            closing = +1 if side < 0 else -1
            opening = -1 if side < 0 else +1
            # THE VETO, Joe 1016. When the r lines are travelling against this verdict, the
            # verdict's power to close the opposite side is suspended and that trade stays open.
            veto = None if self.vom is None else self.vom.holds(int(bar), int(side))
            closed = []
            if veto is not None:
                self.vom_rows.append((int(bar), int(side), 'veto: the close is suspended',
                                     'the departures were %s'
                                     % ', '.join(self.sc.U(z) for z in veto)))
            else:
                for t in list(live):
                    if t['dr'] == closing:
                        t['exit'] = bar
                        t['exit_reason'] = src
                        closed.append(t)
                        live.remove(t)
                        # A NORMAL EVENT MAY CLOSE A VETO-PROTECTED TRADE, Joe 1017: *"a normal
                        # event may close a trade that is riding"*. With the mech owning no exit
                        # there is nothing further to cancel here - this IS the close.
                        #   THE FAULT THIS REPLACES, kept because it cost real net: while the mech
                        #   owned an exit, a trade closed here was dropped from `live` but LEFT IN
                        #   `riding`, so the ride-exit block closed it a SECOND time at its own bar
                        #   and overwrote `exit` with the later, better bar. 6 trades over the 94
                        #   days, 5 days, worth +11.3375 pp of net the machine had not earned.
            # THE OPEN. Normally the verdict's own side. Under the veto with NOTHING open, Joe
            # 1016: *"the OPEN would be at 02:07, towards the direction that the r lines are
            # facing"* - which is the side the verdict would have CLOSED.
            #   AND UNDER THE VETO WITH SOMETHING OPEN THE VERDICT OPENS NOTHING, Joe 1017 on
            #   the 2026-08-22 02:15:00 event: *"creating a short is against the premise of the
            #   mech, and 3 LONG trades would break the pyramid rule"*. So the event closes
            #   nothing and opens nothing; the trade already open simply stays open. Until 1017
            #   this fell through to the verdict's own side and opened AGAINST the r lines the
            #   veto had just found travelling the other way.
            #   HE CALLED IT `END` AND THEN WITHDREW THE WORD, 1017: *""END" is confusing me.
            #   it's the opposite of "keeps riding""*. So the behaviour is named by what it does -
            #   no open - and no label is coined for it.
            #   LITERAL ON HIS WORDS: his 1a is conditioned on *"no incoming trade (chain gap)"*,
            #   so ANY live trade makes the verdict open nothing, not only one on the side
            #   being closed.
            open_dr = opening
            no_open = False
            if veto is not None:
                if live:
                    no_open = True
                else:
                    open_dr = closing
            opened = None
            # NO OPEN MEANS NO STAND-DOWN STAMP. `last_print` is set inside the open branch only,
            # which a no-open verdict inherits; MINE AND STATED, Joe has set no rule for it.
            # THE PYRAMID COUNTS LIVE TRADES ONLY. A pending trade - armed at a verdict and
            # still waiting for its fire bar - does NOT occupy a CAP slot, because the existing
            # test has always counted `live` and a pending trade is not live.
            #   MINE AND STATED, AND IT IS THE ONE RULE OF THIS BANK JOE HAS NOT SET. He has ruled
            #   on the pyramid before - 1017: *"3 LONG trades would break the pyramid rule"* - so
            #   if a pending trade should hold a slot, this is the line to change and the run to
            #   repeat. Flagged to him at the bank.
            # THE FLIP TEST runs BEFORE the pyramid check, so the cap is tested on the side that
            # will actually open.
            flip_why = ''
            if not no_open:
                open_dr, flip_why = self.flip_dr(bar, open_dr)
            if not no_open and sum(1 for t in live if t['dr'] == open_dr) < CAP:
                got = self.fire_bar(bar, open_dr, until)
                if got is not None:
                    fb, fwhy = got
                    # `armed` is the VERDICT bar - Joe's OPEN, and the trade's identity.
                    # `entry` is the PHYSICAL fill bar - his `trade-fires` column. `gross` prices
                    # off `entry`, which is why the fill bar keeps that name.
                    opened = {'dr': open_dr, 'armed': bar, 'entry': fb, 'exit': None,
                              'source': src, 'exit_reason': None, 'fire_why': fwhy,
                              'flip_why': flip_why,
                              'flipped': bool(flip_why.startswith('FLIPPED'))}
                    if veto is not None and open_dr == closing:
                        opened['source'] = 'veto-on-momentum open, ' + src
                    (live if fb <= bar else pending).append(opened)
                    # THE STAND-DOWN IS STAMPED AT THE VERDICT, not at the fill. MINE AND STATED:
                    # `last_print` has always been stamped where the decision was taken, and the
                    # stand-down exists to space DECISIONS, not fills.
                    last_print = bar
            # THE STOP'S CLOSES RIDE THIS ROW'S `closed` LIST. THE FAULT THIS REPLACES, kept
            # because it inverted a whole run: `stopped` was recorded only in `self.stop_rows` and
            # in the stand-down branch, so a scorer collecting rows' `closed` lists never saw a
            # stop-closed trade - it DELETED the row instead of charging it. Turning the cap ON
            # then RAISED 94-day gross from +251.0116% to +985.2081% across 119 vanished trades,
            # which a stop can never do. Caught by the control arm, not by reading the code.
            rows.append((bar, side, src, note, stopped + closed, opened,
                         len(live) + len(pending)))
        # THE TAIL. Anything still pending or live at `until` is settled there, so a trade that
        # was armed inside the window but never fired is dropped rather than counted.
        tail = self._settle(until, live, pending)
        for t in tail:
            self.stop_rows.append((int(t['exit']), int(t['dr']), t['exit_reason'],
                                   'armed %s, entered %s'
                                   % (self.sc.U(t['armed']), self.sc.U(t['entry']))))
        if tail:
            rows.append((int(until), 0, 'the MAE cap closed a trade', '', tail, None, len(live)))
        self.never_fired = list(pending)
        rows.sort(key=lambda z: z[0])
        # A TRADE IS CLOSED EXACTLY ONCE. The 1017 fault was exactly this invariant breaking, so it
        # is an assert and not a comment: `riding` outliving a normal close let the ride-exit block
        # append the same trade a second time and overwrite its exit bar.
        _cl = [id(t) for _b, _s, _sr, _nt, _c, _o, _n in rows for t in _c]
        assert len(_cl) == len(set(_cl)), 'a trade appears in two `closed` lists'
        return rows, live

    def gross(self, t):
        """A closed trade's gross, in percent. -> float."""
        e, x, dr = int(t['entry']), int(t['exit']), int(t['dr'])
        return (100.0 * (self.px[e] - self.px[x]) / self.px[e]) if dr > 0 else \
               (100.0 * (self.px[x] - self.px[e]) / self.px[e])
