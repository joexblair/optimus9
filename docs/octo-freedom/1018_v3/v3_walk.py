"""v3_walk - walk the octo-v3 chain leg after leg, printing what each one does.

Every rule is Joe's, 1018. The ones this file implements, in the order a bar tests them:
  the arm        ws{min_tf}b reaches oob on the leg's side, dwell 3. Nothing fires before it
  the test-point ws{min_tf}Mage crosses to ib, xwob 4. Its SIDE is recorded, not assumed
  the extrema    walk back to look forward, same side - jig.mage_cascade_bar mode 'extrema'
  rider-tf       set at the FIRST test-point: highest wsf r in oob, else highest mom-true, else
                 routing (not built)
  mrider-tf      the highest wsf Mage past the fence but NOT oob, ws3-ws12 - Joe 1018 excluded
                 ws1 and ws2
  the race       every oob r to its OWN ib, step1 wob 3. Winner carries lineage; a tie goes to the
                 higher TF
  step2          at the winner's step1 bar only, winner+1 or winner+2 past the fence, same side
  the chain      a pass makes holder+n the new holder and lineage repeats from its step1 bar
  the exhaust    step2 disqualified. With an mrider the leg continues to the next test-point;
                 without one the leg ends and the OPPOSITE side opens

THE OPEN IS NOT THE ARM. Joe 1019, catching me conflating them: *"the last leg didn't end at
01:07 - why is it printed here as the OPEN?"*. A leg OPENS on the bar the previous leg ended - the
exhaust bar, or its knowable bar - and only ARMS later, when ws{min_tf}b next reaches oob on the
new side. On the 2026-09-03 00:41:30 LONG that gap is 1,530 s, and the leg's entire MAE of 0.7256
happens inside it at 01:01:30. Anchored on the arm instead, the same leg reads MAE 0.0068 and the
drawdown vanishes. `leg_open` and `arm` are separate fields and every MAE/MFE runs from the OPEN.

THE STUCK CASE IS DETECTED, NOT DECIDED. When a holder sits between the fence and oob, Joe's three
race conditions (a) (b) (c) apply; this file flags the case and reports which of them fires rather
than choosing one, because their precedence is not ruled.
"""
import os
import sys
import io
import glob
import contextlib

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')

MIN_TF = 1
RMOM_FNC, MAGE_FNC = 80.0, 75.0
OOB_DWELL, TP_XWOB, STEP1_WOB, R_XWOB_OOB = 6, 4, 3, 8   # dwell 6: Joe 1019 *"43: 6"*
WSF_HI, MRIDER_LO = 12, 3
TRAJ_K, AWAY_CONF = 12, 12
PRED1_GAPS = 2        # misses allowed in the pred1 run, non-consecutive. Joe 1019
XCROSS_MULT = 1.5


class V3(object):
    def __init__(self, sc, cache):
        self.sc = sc
        self.R = {t: np.asarray(sc.LD(t * 60, 'r'), float) for t in range(1, WSF_HI + 3)}
        self.M = {t: np.asarray(sc.LD(t * 60, 'Mage'), float) for t in range(1, WSF_HI + 1)}
        self.X = {t: np.asarray(sc.LD(t * 60, 'x'), float) for t in range(1, WSF_HI + 2)}
        self.B = np.asarray(sc.LD(MIN_TF * 60, 'b'), float)
        self.MT = {}
        for t in range(1, WSF_HI + 1):
            g = glob.glob(os.path.join(cache, 'momt_ws%d_*.npz' % t))
            if g:
                z = np.load(g[0])
                self.MT[t] = {+1: z['p'], -1: z['m']}
        self.n = len(self.B)

    # ---- the readings, all side-aware. The side is the leg's, set once at its open.
    def oob(self, v, s):
        return (v >= self.sc.HI) if s > 0 else (v <= self.sc.LO)

    def ib(self, v):
        return self.sc.LO < v < self.sc.HI

    def exf(self, v, s, fnc):
        return (v >= fnc) if s > 0 else (v <= 100.0 - fnc)

    def qual(self, v, s):
        """the mrider band: past the Mage fence but NOT oob. Not latched."""
        return self.exf(v, s, MAGE_FNC) and not self.oob(v, s)

    def between(self, v, s):
        """the STUCK case: an r past its fence but not oob."""
        return self.exf(v, s, RMOM_FNC) and not self.oob(v, s)

    # ---- the legs of the walk
    def leg_open(self, prev_end_bar, knowable=None):
        """THE OPEN. The bar the previous leg ended, NOT the arm. See the header note.

        `knowable` is that end's own confirmation bar; a fill cannot precede it, so a caller that
        prices the open passes it. Which of the two the open takes is Joe's ruling, open as #31.
        """
        return int(prev_end_bar), (None if knowable is None else int(knowable))

    def mae_mfe(self, px, frm, to, side):
        """(MAE, MFE) in %, anchored on `frm` - which is THE OPEN, never the arm."""
        px = np.asarray(px, float)
        seg = (px[int(frm):int(to) + 1] - px[int(frm)]) / px[int(frm)] * 100.0
        fav = seg if side < 0 else seg          # a LONG gains on a rise; side flips the sign below
        if side > 0:
            fav = -seg
        return float(np.nanmax(-fav)), float(np.nanmax(fav))

    def testpoint(self, frm, side=None, prev_cross=None):
        """The first ws{min_tf}Mage oob->ib cross after `frm`, xwob 4. -> a dict or None.

        `prev_cross` is the bar the arm window opens at - the PREVIOUS ws{min_tf}Mage ib cross. Pass
        it and the result carries the arm and a `valid` flag; a cross with no ws1b run inside its own
        window IS NOT A TEST-POINT and comes back valid False so a caller reports the rejection.
        """
        line = self.M[MIN_TF]
        run, was = 0, None
        for j in range(int(frm) + 1, self.n):
            v = line[j]
            if v >= self.sc.HI:
                run, was = 0, +1
            elif v <= self.sc.LO:
                run, was = 0, -1
            else:
                run += 1
                if run >= TP_XWOB and was is not None:
                    k = j - TP_XWOB + 1
                    out = {'bar': k, 'known': j, 'side': int(was), 'valid': True,
                           'arm': None, 'why': 'no arm test asked for'}
                    if prev_cross is not None:
                        a, why = self.arm_for(k, int(was if side is None else side), prev_cross)
                        out['arm'], out['why'] = a, why
                        out['valid'] = a is not None
                    return out
        return None

    def step1(self, t, frm):
        """the line's own return to ib, held STEP1_WOB bars. -> (the cross bar, knowable)."""
        run = 0
        for j in range(int(frm), self.n):
            run = run + 1 if self.ib(self.R[t][j]) else 0
            if run >= STEP1_WOB:
                return j - STEP1_WOB + 1, j
        return None, None

    def oob_lines(self, bar, s):
        """the wsf r lines whose oob run at `bar` reached the r xwob. Joe 1018's xwob 8."""
        out = []
        for t in range(1, WSF_HI + 1):
            if not self.oob(self.R[t][bar], s):
                continue
            a = bar
            while a > 0 and self.oob(self.R[t][a - 1], s):
                a -= 1
            e = bar
            while e < self.n - 1 and self.oob(self.R[t][e + 1], s):
                e += 1
            if e - a + 1 >= R_XWOB_OOB:
                out.append(t)
        return out

    def mrider(self, bar, s):
        q = [t for t in range(MRIDER_LO, WSF_HI + 1) if self.qual(float(self.M[t][bar]), s)]
        return (max(q) if q else None), q

    def race(self, bar, s):
        """-> (the winner, {tf: (its ib bar, knowable)}). Earliest bar; a tie to the HIGHER TF."""
        arr = {}
        for t in self.oob_lines(bar, s):
            a, c = self.step1(t, bar)
            if a is not None:
                arr[t] = (a, c)
        if not arr:
            return None, arr
        return sorted(arr, key=lambda t: (arr[t][0], -t))[0], arr

    def step2(self, holder, bar, s):
        """-> (holder+n or None, the two readings). Read on `bar` only."""
        out = []
        for p in (holder + 1, holder + 2):
            v = float(self.R[p][bar]) if p <= WSF_HI else float('nan')
            out.append((p, v, p <= WSF_HI and self.exf(v, s, RMOM_FNC)))
        nxt = next((p for p, v, ok in out if ok), None)
        return nxt, out

    # ---- v3-class-pred1, Joe 1019 named the mech
    def pred1_sign(self, bar, s):
        """Per TF: does the line carry a momentum sign. -> [(tf, mrider_qual, mom_true, carries)].

        Joe 1019: *"mrider qual and r mom-true are all signs of predicted momentum"*. A line carries
        one if its Mage sits in the mrider band OR its r is mom-true. The two are complementary, not
        redundant - at 2026-09-03 02:19:00 ws2-ws4 carried on mom-true alone and ws1/ws6-ws9 on the
        Mage band alone, and neither set spans the run by itself.
        """
        out = []
        for t in range(1, WSF_HI + 1):
            q = self.qual(float(self.M[t][bar]), s)
            mt = bool(self.MT[t][s][bar]) if t in self.MT else False
            out.append((t, q, mt, bool(q or mt)))
        return out

    def pred1_reach(self, bar, s, gaps=PRED1_GAPS):
        """The contiguous run of carriers anchored at ws1. -> the highest TF the run reaches, or 0.

        `gaps` misses are allowed inside the run and they may NOT BE CONSECUTIVE. Joe 1019: *"2, but
        they can't be consecutive TFs"*. Two misses in a row ends the run whatever the budget.

        NOT A PEAK DETECTOR. Tested over 1,727 swing highs at 0.9 pct: mean reach 2.86 AT the highs
        against 1.79 on a baseline sample, so the reach is HIGHER at a peak, not collapsed. Recorded
        in the spec S17 because the hypothesis was Joe's and the measurement killed it.

        THE THRESHOLD IS NOT IN HERE. It is a value and Joe has not set it; a caller passes its own.
        """
        last, used, prev_miss = 0, 0, False
        for t, q, mt, carries in self.pred1_sign(bar, s):
            if carries:
                last, prev_miss = t, False
                continue
            if prev_miss:
                break
            used += 1
            if used > int(gaps):
                break
            prev_miss = True
        return last

    def away_toward(self, tf, bar, prev=None):
        """The tag for one TF. ws{min_tf}Mage sets the perspective for the WHOLE ladder, Joe 1019.

        The TF supplies only its own Mage direction. Delegates the rule to the jig.
        """
        from optimus9.analysis.jig import away_toward as _at
        return _at(self.mage_dir(tf, bar), float(self.M[MIN_TF][bar]), prev)

    def mage_dir(self, tf, bar):
        """The Mage's trajectory direction at the scaled width. Joe 1019: the Mage, not the r."""
        from _trajmech import traj
        blk = max(1, TRAJ_K * int(tf))
        return int(traj(self.M[tf], int(bar) + 1, blk, 2, 24, 'close', 0)['dir'])

    def arm_for(self, tp, s, prev_cross):
        """The test-point's gate. -> ((start, end, bars), why) or (None, why).

        THE GATE IS SAME-SIDE ws2r OOB. Joe 1019: *"the testpoint is now gated by same-side ws2r
        oob"*. This REPLACES the ws1b arm, which he had queried - *"why do we need an arm? every
        testpoint is a cross to ib, so the line must go oob regardless of an arm"* - and which the
        tape showed was a formality: 8,132 of 8,136 HIGH ws1Mage crosses had a ws1b run behind them
        somewhere, so as a yes/no gate it rejected 4 in 8,136.

        THE RUN MUST REACH THE r xwob AND SIT IN THE TEST-POINT'S OWN WINDOW, which opens at the
        previous ws{min_tf}Mage ib cross. The window is Joe's 1019 bound, carried over unchanged
        from the ws1b arm it replaces.
        """
        r2 = self.R[2]
        o = np.array([self.oob(v, s) for v in r2])
        d = np.diff(np.r_[False, o, False].astype(np.int8))
        best = None
        lo = int(prev_cross)
        for a, e in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1):
            if a > lo and a <= tp and (e - a + 1) >= R_XWOB_OOB:
                if best is None or a > best[0]:
                    best = (int(a), int(e), int(e - a + 1))
        if best is None:
            at = float(r2[int(tp)])
            return None, ('no same-side ws2r oob run of %d+ bars between %s and this cross; '
                          'ws2r is %.2f at it' % (R_XWOB_OOB, ('the tape start' if lo < 0 else str(lo)), at))
        assert best[0] > lo and best[0] <= tp, 'the ws2r gate fell outside its own window'
        return best, 'ok'

    def xcross(self, tf, frm, s):
        """Joe's (c): the TF+1 x cutting BOTH ws{TF}r while oob and ws{TF+1}r while not oob.

        A HIGH-oob excursion is cut UNDER, a LOW-oob one OVER - the oob side decides, never dr.
        -> the first bar all three hold together for the xwob, or None.
        """
        xt = tf + 1
        if xt > WSF_HI + 1:
            return None
        w = int(round(xt * XCROSS_MULT))
        x = self.X[xt]
        cut = (lambda a, b: a < b) if s > 0 else (lambda a, b: a > b)
        run = 0
        for j in range(int(frm), self.n):
            both = cut(x[j], self.R[tf][j]) and cut(x[j], self.R[xt][j])
            run = run + 1 if both else 0
            if run >= w and self.oob(self.R[tf][j], s) and self.between(self.R[xt][j], s):
                return j
        return None

    # ---- the mage cascade, and what it says about the target side
    def cascade(self, bar, side):
        """(verdict, toward_target, the dict). jig.mage_cascade; this adds no rule of its own.

        `toward_target` is the verdict pointing at the leg's target end: 'up' for a LONG, 'down'
        for a SHORT. Joe 1019 uses it twice - to validate an END that landed on the wrong side, and
        to suppress a counter-side test-point.
        """
        from optimus9.analysis.jig import mage_cascade, MC_ZOOM, MC_MIN
        c = mage_cascade(self.M, int(bar), 1, WSF_HI, MC_ZOOM, MC_MIN, None)
        v = str(c.get('verdict'))
        want = 'up' if side > 0 else 'down'
        return v, (v == want), c

    def extrema(self, bar, side):
        """The ws{min_tf}Mage extrema by walk-back-to-look-forward. His 1017 producer, unchanged."""
        from optimus9.analysis.jig import mage_cascade_bar
        k, why = mage_cascade_bar(self.M[MIN_TF], int(bar), int(side), mode='extrema')
        return (None if k is None else int(k)), why

    # ---- the ws1r / ws2r walk-forward, and its disarm
    def walk_forward(self, tp, side):
        """Joe 1019's mech for a test-point with no oob r line. -> a dict.

        THE GATE: ws1r AND ws2r must both read trajectory towards the test-point side.
        THE EVENTS: either line reaching oob is the good outcome; ws2r reaching oob DISARMS the mech
        and hands the leg to lineage. ws2r leaving its fence and returning to in-fence is the only
        exhaustion - ws1r's own fence return was DROPPED, Joe 1019: *"drop ws1 from the infence
        rule"*, because it did not give ws2 a fighting chance.
        """
        d1, d2 = self.r_dir(1, tp), self.r_dir(2, tp)
        want = +1 if side > 0 else -1
        out = {'gate': bool(d1 == want and d2 == want), 'ws1_dir': d1, 'ws2_dir': d2,
               'ws1_oob': None, 'ws2_oob': None, 'ws2_fence_return': None,
               'disarm': None, 'exhaust': None}
        if not out['gate']:
            out['why'] = 'the gate is shut - ws1r %+d, ws2r %+d, both must face %+d' % (d1, d2, want)
            return out
        out['ws1_oob'] = self._first_oob(1, tp, side)
        out['ws2_oob'] = self._first_oob(2, tp, side)
        out['ws2_fence_return'] = self._fence_return(2, tp, side)
        out['disarm'] = out['ws2_oob']
        if out['disarm'] is not None and (out['ws2_fence_return'] is None
                                          or out['disarm'] < out['ws2_fence_return']):
            out['why'] = 'ws2r reached oob first - the mech disarms and lineage takes over'
            out['exhaust'] = None
        else:
            out['exhaust'] = out['ws2_fence_return']
            out['why'] = 'ws2r returned in-fence before reaching oob - exhaustion'
        return out

    def r_dir(self, tf, bar):
        """ws{tf}r's trajectory direction at the scaled width."""
        from _trajmech import traj
        return int(traj(self.R[tf], int(bar) + 1, max(1, TRAJ_K * int(tf)), 2, 24, 'close', 0)['dir'])

    def _first_oob(self, tf, frm, side):
        run = 0
        for j in range(int(frm), self.n):
            run = run + 1 if self.oob(self.R[tf][j], side) else 0
            if run >= R_XWOB_OOB:
                return j - R_XWOB_OOB + 1
        return None

    def _fence_return(self, tf, frm, side):
        """left its fence, then held STEP1_WOB bars back inside it."""
        seen, run = False, 0
        for j in range(int(frm), self.n):
            if self.exf(self.R[tf][j], side, RMOM_FNC):
                seen, run = True, 0
                continue
            if seen:
                run += 1
                if run >= STEP1_WOB:
                    return j - STEP1_WOB + 1
            else:
                run = 0
        return None

    # ---- the END validation, when the exhaust lands on the wrong side
    def end_gate(self, bar, side):
        """Joe 1019's gate. ws{min_tf}Mage on the COUNTER-target side of 50 and ex-fence on it."""
        v = float(self.M[MIN_TF][bar])
        counter = -int(side)
        on_side = (v < 50.0) if side > 0 else (v > 50.0)
        ex = self.exf(v, counter, MAGE_FNC)
        return bool(on_side and ex), {'ws1Mage': v, 'counter_side': 'LOW' if side > 0 else 'HIGH',
                                      'past_50': on_side, 'ex_fence': ex}

    def spend_walk(self, frm, side):
        """Walk ws{min_tf}r until its momentum is spent. -> (the bar, which end) or (None, None).

        Joe 1019: *"we walk the bar forward until it crosses to ib or crosses to infence"*, and
        *"walk ws1r forward until it crosses to infence or to ib (if it makes it to oob)"*. The
        counter side is the one it is travelling into, so the tests are read there.
        """
        counter = -int(side)
        oob_hit = None
        run_ib, run_if, seen_ex = 0, 0, False
        for j in range(int(frm), self.n):
            v = float(self.R[MIN_TF][j])
            if self.oob(v, counter):
                oob_hit = j if oob_hit is None else oob_hit
                run_ib, run_if = 0, 0
                continue
            if self.exf(v, counter, RMOM_FNC):
                seen_ex = True
                run_if = 0
            else:
                run_if = run_if + 1 if seen_ex else 0
            if oob_hit is not None:
                run_ib += 1
                if run_ib >= STEP1_WOB:
                    return j - STEP1_WOB + 1, 'it reached oob, so the ib return'
            elif run_if >= STEP1_WOB:
                return j - STEP1_WOB + 1, 'it never reached oob, so the in-fence return'
        return None, None


# ── the leg driver ────────────────────────────────────────────────────────────────────────────
UNRULED = {
    9:  'the MAE/MFE anchor - the open or the test-point that started the leg',
    10: 'rider-tf at the SECOND test-point - re-seed or carry',
    11: 'step2 when winner+2 falls outside wsf',
    31: 'the open bar - the exhaust bar or its knowable bar',
    24: 'a test-point with no oob r AND the ws1r/ws2r gate shut - nothing drives the chain',
    40: 'the v3-class-pred1 reach threshold',
    45: 'how STALE an unclaimed arm may be - the consumption rule only stops a REUSED one',
}


def walk_leg(v, open_bar, side, claimed=None, log=print, pred1_thr=None):
    """ONE LEG, from its open to its end, printing every step. -> a dict.

    THE ORDER A LEG IS WALKED, every step Joe's:
      the open        the bar the PREVIOUS leg ended. Not the arm
      the test-point  ws{min_tf}Mage to ib, xwob 4, claiming its own unclaimed arm
      the extrema     walk back to look forward
      the readings    rider, mrider, the pred1 ladder, the away/toward tags
      the race        the oob r lines to their own ib; the winner carries lineage
      the chain       step2 on the winner's step1 bar, then holder+n, repeating
      no oob r        the ws1r/ws2r walk-forward, which DISARMS on ws2r reaching oob
      the exhaust     the mrider override, else the END validation when it landed counter-side
      the verdict     the next test-point - same side held, counter side exits, suppressed while
                      the cascade points at the target

    IT HALTS ON AN UNRULED CONCRETION rather than choosing one. `pred1_thr` None means Joe has not
    set the threshold, so the reach is REPORTED and never gates.
    """
    claimed = set() if claimed is None else claimed
    sd = 'LONG' if side > 0 else 'SHORT'
    rec = {'open': int(open_bar), 'side': int(side), 'steps': [], 'end': None, 'why': None,
           'unruled': []}
    say = lambda t: (log(t), rec['steps'].append(t))

    say('| the leg | %s, opened %s |' % (sd, v.sc.U(int(open_bar))))
    say('|---|---|')
    prev = int(open_bar)
    tp = v.testpoint(open_bar, side, prev)
    while tp is not None and not tp['valid']:
        say('| a ws1Mage ib cross at %s | REJECTED - %s |' % (v.sc.U(tp['bar']), tp['why']))
        prev = tp['bar']
        tp = v.testpoint(tp['bar'], side, prev)
    if tp is None:
        rec['why'] = 'no valid test-point before the tape ends'
        say('| the leg | %s |' % rec['why'])
        return rec
    claimed.add(tp['arm'][0])
    say('| the gate, same-side ws2r oob xwob %d | %s, %d bars |' % (R_XWOB_OOB, v.sc.U(tp['arm'][0]), tp['arm'][2]))
    say('| the test-point, xwob %d | %s, knowable %s |' % (TP_XWOB, v.sc.U(tp['bar']), v.sc.U(tp['known'])))
    say('| its side | %s%s |' % ('HIGH +1' if tp['side'] > 0 else 'LOW -1',
                                 '' if tp['side'] == side else '  ** counter-side **'))
    ex, why = v.extrema(tp['bar'], side)
    if ex is not None:
        say('| the ws1Mage extrema | %s, %.4f, %d s back |'
            % (v.sc.U(ex), v.M[MIN_TF][ex], (tp['bar'] - ex) * 5))
    oob = v.oob_lines(tp['bar'], side)
    mr, mq = v.mrider(tp['bar'], side)
    reach = v.pred1_reach(tp['bar'], side)
    say('| wsf r oob, xwob %d | %s |' % (R_XWOB_OOB, ', '.join('ws%d' % t for t in oob) or 'NONE'))
    say('| mrider-tf, ws%d-ws%d | %s |' % (MRIDER_LO, WSF_HI, ('ws%d' % mr) if mr else 'NONE'))
    say('| pred1_reach, gaps %d non-consecutive | ws%d%s |'
        % (PRED1_GAPS, reach, '' if pred1_thr is None else
           (' - %s thr ws%d' % ('HOLDS' if reach >= pred1_thr else 'RELEASES', pred1_thr))))
    if pred1_thr is None:
        rec['unruled'].append(40)

    if not oob:
        wf = v.walk_forward(tp['bar'], side)
        say('| the ws1r/ws2r gate | %s - ws1r %+d, ws2r %+d |'
            % ('OPEN' if wf['gate'] else 'SHUT', wf['ws1_dir'], wf['ws2_dir']))
        if not wf['gate']:
            rec['why'] = 'no oob r and the ws1r/ws2r gate is shut - nothing drives the chain'
            rec['unruled'].append(24)
            say('| the leg | %s |' % rec['why'])
            return rec
        for lab, k in (('ws1r reaches oob', wf['ws1_oob']), ('ws2r reaches oob - THE DISARM', wf['ws2_oob']),
                       ('ws2r fence return - the only exhaustion', wf['ws2_fence_return'])):
            say('| %s | %s |' % (lab, v.sc.U(k) if k is not None else 'never'))
        if wf['disarm'] is None:
            rec['end'], rec['why'] = wf['exhaust'], wf['why']
            say('| the leg | %s at %s |' % (wf['why'], v.sc.U(wf['exhaust'])))
            return rec
        say('| lineage takes over at | %s |' % v.sc.U(wf['disarm']))
        holder = 2
        bar, _ = v.step1(2, wf['disarm'])
    else:
        w, arr = v.race(tp['bar'], side)
        if w is None:
            rec['why'] = 'no oob r line returns to ib before the tape ends'
            say('| the race | %s |' % rec['why'])
            return rec
        order = sorted(arr, key=lambda t: (arr[t][0], -t))
        say('| the race | %s |' % ', '.join('ws%d@%s' % (t, v.sc.U(arr[t][0])) for t in order))
        say('| the winner carries lineage | ws%d |' % w)
        holder, bar = w, arr[w][0]

    say('')
    say('| the holder | its step1 bar | holder+1 | r | ok | holder+2 | r | ok | the print |')
    say('|---|---|---|---|---|---|---|---|---|')
    while True:
        nxt, two = v.step2(holder, bar, side)
        (p1, v1, o1), (p2, v2, o2) = two
        if p2 > WSF_HI and not o1:
            rec['unruled'].append(11)
        say('| ws%d | %s | %s | %s | %s | %s | %s | %s | %s |'
            % (holder, v.sc.U(bar),
               'ws%d' % p1 if p1 <= WSF_HI else 'out of band', ('%.2f' % v1) if p1 <= WSF_HI else '-',
               'YES' if o1 else 'no',
               'ws%d' % p2 if p2 <= WSF_HI else 'out of band', ('%.2f' % v2) if p2 <= WSF_HI else '-',
               'YES' if o2 else 'no',
               ('BATON PASSES to ws%d' % nxt) if nxt else 'EXHAUST'))
        if nxt is None:
            break
        nb, _ = v.step1(nxt, bar)
        if nb is None:
            break
        holder, bar = nxt, nb

    say('')
    mr2, _ = v.mrider(bar, side)
    say('| the exhaust | %s on ws%d |' % (v.sc.U(bar), holder))
    say('| mrider there | %s |' % (('ws%d' % mr2) if mr2 else 'NONE'))
    if mr2:
        say('| the mrider override | the leg continues to the next test-point |')
        rec['end'], rec['why'] = bar, 'exhaust held open by mrider ws%d' % mr2
        return rec

    gate, g = v.end_gate(bar, side)
    say('| the END gate - ws1Mage counter-side ex-fence | %s - %.4f, past 50 %s, ex-fence %s |'
        % ('QUALIFIES' if gate else 'no', g['ws1Mage'], g['past_50'], g['ex_fence']))
    if not gate:
        rec['end'], rec['why'] = bar, 'EXHAUST prints - the END gate does not qualify'
        say('| the leg | ENDS at %s, %s opens |' % (v.sc.U(bar), 'SHORT' if side > 0 else 'LONG'))
        return rec
    verd, toward, _ = v.cascade(bar, side)
    say('| the cascade at the exhaust | %s%s |' % (verd, ' - toward the target' if toward else ''))
    if not toward:
        rec['end'], rec['why'] = bar, 'the cascade is not toward the target - the END prints'
        say('| the leg | ENDS at %s |' % v.sc.U(bar))
        return rec
    sb, swhy = v.spend_walk(bar, side)
    if sb is None:
        rec['end'], rec['why'] = bar, 'ws1r never spent its momentum before the tape ends'
        return rec
    say('| ws1r momentum spent | %s - %s, %d s after the exhaust |' % (v.sc.U(sb), swhy, (sb - bar) * 5))
    verd2, toward2, _ = v.cascade(sb, side)
    say('| the cascade RETESTED there | %s |' % verd2)
    if toward2:
        rec['end'], rec['why'] = None, 'the cascade still points at the target - the trade STAYS OPEN'
        say('| the trade | STAYS OPEN past %s |' % v.sc.U(sb))
        rec['stays_open_from'] = sb
        return rec
    rec['end'], rec['why'] = sb, 'the cascade turned - the END prints at the spend bar'
    say('| the leg | ENDS at %s |' % v.sc.U(sb))
    return rec
