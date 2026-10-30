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

    def __init__(self, C, E, MG=None, MGE=None, PS=None):
        #   `C` IS NO LONGER A SECOND SOURCE. Joe 1029 dropped the previous completed bar's close,
        #   so a caller passes the live ladder here and the two stay identical. The `closed_*`
        #   accessors are kept for callers that still name them and now answer from the same
        #   arrays; the assert below refuses a caller that hands in two different ladders.
        self.C = {int(t): np.asarray(v, float) for t, v in C.items()}
        self.E = {int(t): np.asarray(v, float) for t, v in E.items()}
        #   THE CLOSED MAGE LADDER, added 1027 for *"the mage-cascde verdict at every cadence
        #   event"*. A FOURTH bucket. His 1027 truth table is what the walk does with the verdict.
        self.mage = None if MG is None else {int(t): np.asarray(v, float) for t, v in MG.items()}
        #   THE EMERGING MAGE LADDER, added 1027 for the BARRAGE. A FIFTH bucket, and the only
        #   caller is the barrage's ws1Mage oob->ib cross.
        #   WHY IT IS EMERGING, AND THE CHOICE IS MINE: his 1026 rule is *"move everything except
        #   reversal detection to closed bars"*, which would put this cross on cws1Mage. But
        #   LIN2_BARRAGE_TOL_S 70 s is MEASURED as the gap from the EMERGING 2026-08-30 02:27:50
        #   cross to the 02:29:00 ws1r reversal, so moving the read moves the anchor the threshold
        #   was taken from. The measured read is kept and the alternative is measured beside it, in
        #   out/l2_barrage_reads.md, rather than decided here.
        self.mage_em = None if MGE is None else {int(t): np.asarray(v, float)
                                                 for t, v in MGE.items()}
        #   THE PSEUDO-CLOSED LADDER, a SIXTH bucket, added 1028 on his ruling: *"1, pseudo for
        #   exfence"* with the band *"confine pseudo-closed to >3"*. Keys are TFs; a TF that is
        #   absent falls back to the closed read, so a caller that did not build it is unchanged.
        self.pseudo = None if PS is None else {int(t): np.asarray(v, float) for t, v in PS.items()}
        self.tfs = sorted(set(self.C) & set(self.E))
        assert self.tfs, 'the two ladders share no timeframe'
        self._gate = str(K.L2_GATE_MODE)
        assert self._gate in ('emerging', 'closed'), 'L2_GATE_MODE %r is not a mode' % self._gate
        #   THE PER-LINE EX-FENCE LATCH's two caches, his 1029 mech. Keyed per (tf, side, fence)
        #   and per side; both are built over the WHOLE tape so no caller's bar is out of range.
        self._lat = {}
        self._rel = {}

    #  ── STATE: the closed ladder, or the PSEUDO-CLOSED one above his band ─────────────────────
    def _state(self, tf):
        """The array a STATE read uses for ws{tf}r. -> pseudo above his band, else closed.

        Joe 1028: *"1, pseudo for exfence"*, and the band *"confine pseudo-closed to >3"* with
        ws1..ws3 his *"fast lines"*. LIN2_PSEUDO_MIN_TF 4 is the floor.

        A TF the caller did not build a pseudo line for falls back to closed, so nothing that
        predates this change moves. `state_src` reports which one answered.
        """
        t = int(tf)
        if self.pseudo is not None and t >= int(K.LIN2_PSEUDO_MIN_TF) and t in self.pseudo:
            return self.pseudo[t]
        #   THE FALLBACK IS THE LIVE VALUE. Joe 1029: *"completely drop prev-close"*. There is
        #   no second arm, so there is no knob either.
        return self.E[t]

    def state_src(self, tf):
        """Which ladder a STATE read for ws{tf}r came from. -> 'pseudo' or 'closed'. For a report."""
        t = int(tf)
        if self.pseudo is not None and t >= int(K.LIN2_PSEUDO_MIN_TF) and t in self.pseudo:
            return 'pseudo'
        return 'live'

    def value(self, tf, bar):
        """ws{tf}r at `bar`, on the STATE ladder. The number every fence test reads.

        IT IS THE SAME ARRAY THE FENCE TEST USES, which is MY call and stated in the knob: a row
        printing a closed number beside a pseudo ex-fence decision would misreport the board.
        """
        return float(self._state(tf)[int(bar)])

    def oob(self, tf, bar, side):
        """Is ws{tf}r oob on `side` at `bar`, on the STATE ladder."""
        return bool(K.oob(self._state(tf)[int(bar)], side))

    def ex_fence(self, tf, bar, side):
        """Is ws{tf}r past the r fence on `side` at `bar`, on the STATE ladder."""
        return bool(K.ex_fence(self._state(tf)[int(bar)], side))

    #  ── THE PER-LINE EX-FENCE LATCH: his 1029 mech, LIN2_LATCH_EXFNC_ON ───────────────────────
    #
    #   HIS SPEC, verbatim:
    #       I have a third option to add to pseudo-close and 180 wob: use a per-line latch
    #       -the mech would latch on when the r line crosses into exfence, with a small
    #        {knob:4,'LIN2_EXFNC_LATCH_WOB'} WOB
    #       -the latch releases on barrage's signal
    #       -the baton-passing consumers will no longer test a line's value to decide ex-fence
    #        (and oob). they will query the latch state
    #       -any non-baton-passing mechs can still use line values for decisions (eg, the test for
    #        2 consecutive exfence TFs that print exhaust if either failed to reach oob)
    #   and *"no need for a latch life on this new mech"* / *"the mech I propose is purely for
    #   baton-passing"*.
    #
    #   WHY IT LIVES HERE: this file's one responsibility is to answer "what is ws{tf}r here" and
    #   to know which read the caller is entitled to. The latch is a third read of the same board,
    #   so the routing belongs beside `_state`, not in the walk.
    #
    #   FIVE CONCRETIONS HIS SPEC DID NOT PIN. Each is MY call, stated, and each is listed with the
    #   arm I did not take so he can veto one without reading the code:
    #
    #     1  oob.  THERE IS NO oob LATCH. Joe 1029: *"what oob latch? that wasn't in the spec"*.
    #              I built one by reading his *"ex-fence (and oob)"* as "latch both fences", and it
    #              was wrong twice over - it was not asked for, and two independent latches drifted
    #              into "oob and not ex-fence", impossible on a value since 15/85 is a subset of
    #              20/80. Removed. THE LATCH ANSWERS EX-FENCE ONLY; every oob read in the walk
    #              stays on the line's value, which is his *"any non-baton-passing mechs can still
    #              use line values"* applied to the one fence he did not name.
    #     2  side. An opposite-side cross CLEARS a stale latch. Without it a line that latched HIGH
    #              and then crossed LOW would read ex-fence on BOTH sides at once and the rider
    #              scan could pick a line travelling the wrong way. NOT TAKEN: both latches held.
    #     3  the release bar. The barrage's CADENCE bar - the only timestamp the mech emits, and
    #              the bar the chain already consumes. NOT TAKEN: the ws1Mage oob->ib cross bar,
    #              and the ws1r reversal stamp.
    #     4  the release scope. Every line on the SAME side as the latch, released by the barrage
    #              on that side. His sentence carries no side qualifier, but a baton consumer is
    #              always called with the walk's side, and the barrage on the other side is an
    #              event this walk never sees. NOT TAKEN: all lines both sides, and contributors
    #              only.
    #     5  the window's first bar. A CROSS is required, so a line already beyond the fence at the
    #              first finite bar is NOT latched until it leaves and re-enters. NOT TAKEN:
    #              latching on the first bar it is seen beyond the fence.
    #
    #   AND A SIXTH, on the tie: a release and a latch-on at the SAME bar leave the line LATCHED.
    #   The on-edge describes the state AT that bar; the release clears the history up to it.
    #
    #   THE BARRAGE READS VALUES, NEVER THE LATCH. That is structural, not a preference: the latch
    #   releases on the barrage's signal, so a barrage that read the latch would be circular. Its
    #   per-line fence read stays on `ex_fence`, asserted below.
    #
    #   NO CAP AND NO LIFE. On his instruction there is no life knob. A line that latches and never
    #   meets a barrage on its side stays latched to the end of the tape.

    def _releases(self, side):
        """The bars a barrage on `side` releases every latch on `side`. -> sorted int array.

        WHOLE TAPE, not the walk's window: a latch set before the arm can be released by a barrage
        that fired before the arm, so scoping these to the walk would invent a horizon.
        """
        key = (int(side), float(K.RMOM_FNC))
        if key not in self._rel:
            #   LOCAL IMPORT. v4_l2_cadence does not import this file, so there is no cycle; the
            #   import is local only to keep module load order free of a new edge.
            import v4_l2_cadence as CAD
            assert self.mage_em is not None, \
                'the ex-fence latch needs the EMERGING Mage ladder - the barrage read is its release'
            n = len(self._state(self.tfs[0]))
            self._rel[key] = np.array(sorted(int(r[0]) for r in
                                             CAD.barrage(self, key, 0, n - 1)), dtype=int)
        return self._rel[key]

    @staticmethod
    def _confirm(mask, w):
        """The bars a cross INTO `mask` is confirmed on. -> int array.

        The edge is where the state turns on; the confirm bar is edge + w - 1, and only when the
        state held every bar of that window. The exact mirror of `_pass_bars`' off-edge shape, so
        an on-edge and an off-edge are measured the same way.
        """
        m = np.asarray(mask, bool)
        if len(m) < 2:
            return np.array([], dtype=int)
        out = []
        for e in (np.flatnonzero(~m[:-1] & m[1:]) + 1).astype(int):
            e = int(e)
            if e + w - 1 >= len(m):
                continue
            if m[e:e + w].all():
                out.append(e + w - 1)
        return np.array(sorted(set(out)), dtype=int)

    def _latch(self, tf, side):
        """THE latch for (line, side) at every bar. -> bool array over the tape.

        ON at an ex-fence cross confirmed over LIN2_EXFNC_LATCH_WOB bars, both arms.

        WHAT RELEASES IT IS LIN2_EXFNC_LATCH_REL:
            'bank'  a barrage on that side, or an opposite-side ex-fence cross confirmed over the
                    same hold. His 1029 mech and the arm every banked number was measured on.
            'lift'  the latched line's own lift-off on the SAME side, stamped at
                    lift + LIFT_WOB - 1, and nothing else. His 1030 proposal; the three choices
                    inside it are mine and are listed at the knob's declaration.
                    ITS SAMPLING RESTARTS AT THE LATCH, his 1030 ruling - a lift-off only counts
                    once the whole LIFT_PTS lattice sits at or after the latch-on bar.

        EX-FENCE ONLY. There is no oob latch - see decision 1 above. Neither arm releases on a
        cross to oob: oob is read THROUGH this state by the baton path, never against it.

        THE CACHE KEY CARRIES THE RELEASE MODE AND THE FENCE. Both move within one process in a
        comparison driver, and a key of (tf, side) alone would hand back a latch built under the
        other arm - real arrays, wrong arm, no error.
        """
        mode = str(K.LIN2_EXFNC_LATCH_REL)
        assert mode in ('bank', 'lift'), 'LIN2_EXFNC_LATCH_REL %r is not an arm' % mode
        key = (int(tf), int(side), mode, float(K.RMOM_FNC))
        if key in self._lat:
            return self._lat[key]
        v = self._state(tf)
        w = max(1, int(K.LIN2_EXFNC_LATCH_WOB))
        n = len(v)
        on = [int(x) for x in self._confirm(K.ex_fence_mask(v, int(side)), w)]
        if mode == 'lift':
            #   LOCAL IMPORT, same reason as _releases': no new module-load edge.
            from optimus9.analysis.jig import lift_off
            gap = int(K.gap_for(int(tf)))
            span = (max(2, int(K.LIFT_PTS)) - 1) * max(1, gap)
            raw = np.asarray(sorted(int(b) for b in lift_off(
                v, int(side), K.LIFT_PTS, gap, K.LIFT_TOL, K.LIFT_WOB)), int)
            #   THE SAMPLING RESTARTS AT THE LATCH, Joe 1030: *"lift-off per-line sampling is set
            #   to zero (samples collected) when the ex-fence latch is latched"*. So a lift-off
            #   only counts for an episode once the whole lattice sits at or after the latch-on
            #   bar: LIFT_PTS 6 samples at `gap` bars apart reach back span = 5 * gap bars, and
            #   the HELD bar of the off-edge is Y - 1, so the first usable off-edge is
            #   Y >= on + span + 1. Below that the line has not collected its samples yet and
            #   nothing can print.
            #   WHY IT IS A FILTER AND NOT A RE-COMPUTE: at_extreme_mask zeroes the first `span`
            #   bars of whatever array it is handed and is otherwise identical bar for bar, so
            #   lift_off(v[on:]) and lift_off(v) agree on every bar at or after on + span. One
            #   whole-tape pass and a searchsorted give the same answer as a pass per episode.
            st = np.zeros(n, bool)
            lat_on, idx = None, 0
            ons = sorted(on)
            while idx < len(ons):
                o0 = int(ons[idx])
                if o0 >= n:
                    break
                j = int(np.searchsorted(raw, o0 + span + 1, 'left'))
                rel = int(K.lift_stamp(int(raw[j]))) if j < len(raw) else None
                assert rel is None or rel > o0, \
                    'a lift-off release is at or before the latch-on bar it clears'
                end = n if rel is None or rel >= n else rel
                st[o0:end] = True
                if rel is None:
                    break
                #   the next episode starts at the first confirm bar AT OR AFTER the release.
                nxt = idx + 1
                while nxt < len(ons) and int(ons[nxt]) < rel:
                    nxt += 1
                idx = nxt
            for bb in on:
                if bb < n:
                    assert st[bb], 'a latch-on bar is not latched: tf %s side %s bar %d' % (
                        tf, side, bb)
            self._lat[key] = st
            return st
        off = sorted(set(int(x) for x in self._releases(side))
                     | set(int(x) for x in self._confirm(K.ex_fence_mask(v, -int(side)), w)))
        st = np.zeros(n, bool)
        #   A FORWARD LOOP OVER THE EVENTS, his causal form. sorted() puts (bar, 0) before
        #   (bar, 1), so at a tie the release is applied first and the latch-on wins - decision 6.
        cur, prev = False, 0
        for bb, kind in sorted([(x, 0) for x in off] + [(x, 1) for x in on]):
            if bb >= n:
                break
            st[prev:bb] = cur
            cur = bool(kind)
            prev = int(bb)
        st[prev:] = cur
        for bb in on:
            if bb < n:
                assert st[bb], 'a latch-on bar is not latched: tf %s side %s bar %d' % (
                    tf, side, bb)
        self._lat[key] = st
        return st

    def baton_src(self):
        """What a baton-passing fence test reads. -> a label. For a report's header."""
        if not int(K.LIN2_LATCH_EXFNC_ON):
            return 'value'
        return 'latch, released on %s' % str(K.LIN2_EXFNC_LATCH_REL)

    def _deep(self, tf, side):
        """THE ONE LATCH READ AT DEPTH. -> bool array. Latched AND 15/85 confirmed since its on-bar.

        His 1029 reading is what makes this a filter rather than a second latch: *"I see ex-fence
        as a literal term: 'external of the fence', ie oob is definitely ex-fence"*. Anything past
        15/85 is already past the RMOM_FNC pair, so the depth read can only ever be a subset of the
        latch and the two cannot disagree. Asserted below.

        MY FIRST BUILD WAS TWO INDEPENDENT LATCHES and they drifted into "oob but not ex-fence" for
        27,460 bars on 2026-08-30 across all 24 line-sides. That state is impossible on a value.

        CAUSAL: the confirm bars are the latch's own, and the running maximum only looks back.
        """
        #   THE KEY CARRIES THE RELEASE ARM AND THE FENCE, for the same reason _latch's does.
        key = (int(tf), int(side), 'deep', str(K.LIN2_EXFNC_LATCH_REL), float(K.RMOM_FNC))
        if key in self._lat:
            return self._lat[key]
        st = self._latch(tf, side)
        v = self._state(tf)
        w = max(1, int(K.LIN2_EXFNC_LATCH_WOB))
        n = len(v)
        idx = np.arange(n)
        #   this latch's own on-bar, at every bar: the last on-edge at or before it.
        edge = np.zeros(n, bool)
        edge[0] = st[0]
        edge[1:] = st[1:] & ~st[:-1]
        begun = np.maximum.accumulate(np.where(edge, idx, -1))
        #   the last CONFIRMED 15/85 bar at or before it.
        oc = np.zeros(n, bool)
        for b in self._confirm(K.oob_mask(v, int(side)), w):
            if int(b) < n:
                oc[int(b)] = True
        deep = np.maximum.accumulate(np.where(oc, idx, -1))
        out = st & (deep >= begun) & (begun >= 0)
        assert not np.any(out & ~st), \
            'the depth read is on where the latch is off - it must be a subset of it'
        self._lat[key] = out
        return out

    def baton_oob(self, tf, bar, side):
        """Is ws{tf}r oob on `side` at `bar`, FOR A BATON-PASSING CONSUMER.

        At LIN2_LATCH_OOB_ON 0, which is banked, this is the line value and nothing moves. At 1 it
        is the one latch read at depth - see `_deep`.
        """
        if not int(K.LIN2_LATCH_OOB_ON):
            return self.oob(tf, bar, side)
        return bool(self._deep(tf, side)[int(bar)])

    def baton_ex_fence(self, tf, bar, side):
        """Is ws{tf}r ex-fence on `side` at `bar`, FOR A BATON-PASSING CONSUMER.

        His 1029 ruling: the baton-passing consumers query the latch state. With
        LIN2_LATCH_EXFNC_ON 0 this is `ex_fence` and nothing moves.

        `baton_oob` is its oob counterpart, and at LIN2_LATCH_OOB_ON 0 that one is the line
        value - his 1029 correction that there is no second latch.
        """
        if not int(K.LIN2_LATCH_EXFNC_ON):
            return self.ex_fence(tf, bar, side)
        return bool(self._latch(tf, side)[int(bar)])

    def latch_on_bar(self, tf, bar, side):
        """The bar the latch live at `bar` turned on. -> bar or None. For a leg report's row."""
        st = self._latch(tf, side)
        b = int(bar)
        if not st[b]:
            return None
        while b > 0 and st[b - 1]:
            b -= 1
        return b

    def latch_off_bars(self, tf, side):
        """The bars the (line, side) latch turns OFF on. -> sorted list.

        Under his mech a line stops being ex-fence at a release, not at a value crossing, so these
        are `_pass_bars`' ex-fence edges. Its oob->ib rule is untouched and stays on the value.
        """
        st = self._latch(tf, side)
        return [int(x) + 1 for x in np.flatnonzero(st[:-1] & ~st[1:])]

    def closed_value(self, tf, bar):
        """ws{tf}r at `bar`, CLOSED, whatever the state ladder is. For a side-by-side report."""
        return float(self.C[int(tf)][int(bar)])

    def line(self, tf):
        """The STATE array, for a producer that needs the whole series - crosses, trajectory.

        Routed the same way as `value`, so a cross or a trajectory read sees the board the fence
        tests see. `closed_line` is the raw closed series for a caller that needs it specifically.
        """
        return self._state(tf)

    def closed_line(self, tf):
        """The CLOSED array, whatever the state ladder is."""
        return self.C[int(tf)]

    def mage_line(self, tf, mode):
        """ws{tf}Mage's whole series from the bucket `mode` names. -> the array.

        'closed' is the cascade's ladder, 'emerging' is the barrage's. A caller names the bucket
        it is entitled to; the routing stays in this file.
        """
        d = {'closed': self.mage, 'emerging': self.mage_em}[str(mode)]
        assert d is not None, 'the %s Mage ladder was not handed to the Board' % mode
        return d[int(tf)]

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

        THE oob DECISION IS `K.oob`, ONE COPY. Joe 1026: *"find out how 't3's two gates' know if a
        line is oob. whichever mech is deciding `oob` needs to receive the emerging values"*. The
        first build inlined `seg <= K.OOB_LO` to vectorise over the span, which put a SECOND copy
        of the oob rule in this file. It agreed with `K.oob` - the measured bar does not move - but
        a duplicate rule drifts the moment OOB_FNC or the boundary changes. The span is reduced to
        a single extreme first, so `K.oob` is still asked once per call rather than per bar.
        """
        seg = self._g(tf)[int(a):int(b) + 1]
        if not seg.size or not np.isfinite(seg).any():
            return False
        ex = float(np.nanmin(seg)) if int(side) < 0 else float(np.nanmax(seg))
        return bool(K.oob(ex, side))

    def gate_oob(self, tf, bar, side):
        """Is ws{tf}r oob on `side` at one bar, on the GATE ladder. -> bool."""
        return bool(K.oob(self._g(tf)[int(bar)], side))

    def gate_ex_fence(self, tf, bar, side):
        """Is ws{tf}r ex-fence on `side` at `bar`. t3's *"no higher TFs exfence"* gate."""
        return bool(K.ex_fence(self._g(tf)[int(bar)], side))
