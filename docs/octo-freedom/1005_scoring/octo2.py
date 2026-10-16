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
        self.conj = CJ.Conj(sc)
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
                how = 'the fire was %s, the cross ran %s; %s' % (self.sc.U(j), dirn,
                                                                 ', '.join(mem))
                # BOUNCE-PRED HAS PRIORITY. Joe 1016. The hold applies whenever ws5Mage is oob at
                # the event bar - the mech's own firing condition, Joe 1016: *"it will only fire
                # when ws5Mage is oob"*. When ws5Mage is in-fence there is nothing to hold and the
                # event stands on its own bar.
                if USE_BP and BP_PRIORITY and self.bp.trig_oob(cf, side):
                    w = self.hold.walk(cf, side, until=until)
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
                                   % (how, self.sc.U(cf), self.sc.U(rb), why)))
                    continue
                ev.append((cf, side, 'the turn-predictor', how))
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
        rows, live, last_print = [], [], None
        for bar, side, src, note in self.events(frm, until):
            if last_print is not None and bar - last_print < STANDDOWN:
                continue
            closing = +1 if side < 0 else -1
            opening = -1 if side < 0 else +1
            closed = []
            for t in list(live):
                if t['dr'] == closing:
                    t['exit'] = bar
                    t['exit_reason'] = src
                    closed.append(t)
                    live.remove(t)
            opened = None
            if sum(1 for t in live if t['dr'] == opening) < CAP:
                opened = {'dr': opening, 'entry': bar, 'exit': None, 'source': src,
                          'exit_reason': None}
                live.append(opened)
                last_print = bar
            rows.append((bar, side, src, note, closed, opened, len(live)))
        return rows, live

    def gross(self, t):
        """A closed trade's gross, in percent. -> float."""
        e, x, dr = int(t['entry']), int(t['exit']), int(t['dr'])
        return (100.0 * (self.px[e] - self.px[x]) / self.px[e]) if dr > 0 else \
               (100.0 * (self.px[x] - self.px[e]) / self.px[e])
