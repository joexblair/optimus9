"""lineage2's FOUR CADENCES, and nothing else. Joe 1025.

ONE RESPONSIBILITY: say which bars a lineage2 walk is allowed to make a decision on. It runs no
walk, picks no rider and passes no baton.

WHY CADENCES EXIST, his framing:

    the key difference for lineage2: v4lineage tests `r` mom states on every bar, lineage2 tests
    them on a determined cadence

    the point of cadences: they are where decisions are made. testing at set points (like 0723)
    provides the opportunity to override a poor signal (ws6r exhaust) if a better signal (ws7
    ex-fence) has presented itself

TARGET-SIDE THROUGHOUT. Joe 1025: *"all calcs and decisions are target-side"*.

NO DWELL ON ANY ib CROSS HERE, his ruling: *"no dwell. the way I see it: because we're on closed
bars, we have an automatic wob. it also means I have TV values that are precisely aligned with what
the code sees"*. So every `oob_ib_cross` call takes xwob 1 and the cross bar IS the actionable bar.

t1 AND t2 READ CLOSED LINES, t3 READS EMERGING. That is his 1025 split: the cws lines *"were
introduced for accuracy and specificity in the lower TFs"*, and *"I don't want slower TF's running
on closed bars because it spoils the line reversal times"*. Both t1cadence qualifiers are cws1r -
he corrected his own handover: *"this is my wrong: both should be cws1r"*.

t4 IS NOT DETECTED HERE. It is a consequence of the walk's own rider state - a non-oob rider that
reverses with no in-lin-hop candidate - so `v4_lineage2` raises it where the rider is known.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import v4_knobs as K
import v4_fast as F
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
from optimus9.analysis.jig import oob_ib_cross
sys.stderr = _e

HTF_LO = 7                                     # *"any of ws7r to ws12r (HTF lines)"* - Joe 1025


def _runs(a):
    """Contiguous True runs of `a`. -> [(start, end)] inclusive."""
    d = np.diff(np.r_[False, a, False].astype(np.int8))
    return list(zip(np.flatnonzero(d == 1).astype(int), (np.flatnonzero(d == -1) - 1).astype(int)))


def _oob(line, side):
    v = np.asarray(line, float)
    return (v <= K.OOB_LO) if int(side) < 0 else (v >= K.OOB_HI)


def t1(CL, side, A, B):
    """TYPE 1 - cws1b is oob. -> [(the cadence bar, why)].

        --if cws1b is oob
        ---walk to "%cws1b crossing from oob to ib%"
        ---IF (cws1r had "reversed on target-side of 50" while cws1b was oob) OR (cws1r reverses on
         target-side of 50 in the 2 minutes (CAUSALLY) following the cws1b oob to ib cross)
        ----fire a cadence event on the "%cws1b crossing from oob to ib%" bar or the "late cws1r
         reversing" bar, whichever is last

    THE REVERSAL IS lift_off ON cws1r, with the value's side of 50 tested at the stamp - the exact
    construct `v4_w4_handover._next_ws1r_rev` uses for his *"same-side of 50"* wording.

    THE RAW BAR IS WHAT THE WINDOWS BOUND, and the STAMP is only the fire bar. That is his standing
    rule, carried in `v4_fast.revs`: *"RAW, on purpose: the raw bar is the anchor and the identity
    of the reversal. Every caller that ACTS on one passes it through K.lift_stamp first"*.

    THE FIRST BUILD BOUNDED BOTH WINDOWS BY THE STAMP and so missed his 2026-08-29 07:48 example.
    His cws1b oob run is 07:46:00..07:46:55, its ib cross 07:47:00, and the 120 s grace reaches
    07:49:00. The cws1r reversal's raw bar is 07:49:00 - exactly on the edge, inside - and its
    stamp is 07:49:35, 35 s past. Bounding by the stamp threw the event away.

    *"WHICHEVER IS LAST"* is his standing race shape - `max(the ib cross bar, the reversal stamp)`.
    """
    b1 = np.asarray(CL['b'], float)
    r1 = np.asarray(CL['r'][1], float)
    oob = _oob(b1, side)
    raws = np.array(sorted(int(x) for x in F.revs(r1, 1, side)), dtype=int)
    grace = max(0, int(K.L2_T1_GRACE_S) // 5)
    out = []
    for c, _cf, s in oob_ib_cross(b1, K.OOB_HI, K.OOB_LO, 1):
        if s != int(side) or not (int(A) <= c <= int(B)):
            continue
        run = next((r for r in _runs(oob) if r[1] == c - 1), None)
        if run is None:
            continue
        s0, s1 = run
        #   the DURING branch: the RAW reversal inside the oob run, cws1r on the target side of 50
        during = [int(x) for x in raws
                  if s0 <= x <= s1 and K.side_of(r1[K.lift_stamp(int(x))]) == int(side)]
        if during:
            bar = max(int(c), K.lift_stamp(during[-1]))      # *"whichever is last"*
            assert bar >= int(c), 'the t1 cadence precedes its own cws1b ib cross'
            out.append((bar, 't1 cws1b oob %s..%s, cws1r reversed %s during, stamp %s'
                        % (ln.U(s0)[11:], ln.U(s1)[11:], ln.U(during[-1])[11:],
                           ln.U(K.lift_stamp(during[-1]))[11:])))
            continue
        #   the GRACE branch: the RAW reversal forward of the cross, inside L2_T1_GRACE_S
        late = [int(x) for x in raws
                if c < x <= c + grace and K.side_of(r1[K.lift_stamp(int(x))]) == int(side)]
        if late:
            bar = max(int(c), K.lift_stamp(late[0]))         # *"whichever is last"*
            assert bar >= int(c), 'the t1 cadence precedes its own cws1b ib cross'
            out.append((bar, 't1 cws1b ib %s, cws1r reversed %s inside the %ds grace, stamp %s'
                        % (ln.U(c)[11:], ln.U(late[0])[11:], K.L2_T1_GRACE_S,
                           ln.U(K.lift_stamp(late[0]))[11:])))
    return out


def t2(CL, side, A, B):
    """TYPE 2 - cws1r is oob and cws1b is NOT oob. -> [(the cadence bar, why)].

        --IF cws1r is oob and cws1b is NOT oob
        ---fire a cadence event when cws1r crosses to ib

    cws1b's oob state is read at the CROSS bar, which is the bar the event fires on.
    """
    b1 = np.asarray(CL['b'], float)
    r1 = np.asarray(CL['r'][1], float)
    out = []
    for c, _cf, s in oob_ib_cross(r1, K.OOB_HI, K.OOB_LO, 1):
        if s != int(side) or not (int(A) <= c <= int(B)):
            continue
        if K.oob(b1[c], side):
            continue                               # that is t1's case, not t2's
        out.append((int(c), 't2 cws1r ib %s, cws1b %.2f not oob' % (ln.U(c)[11:], b1[c])))
    return out


def t3(R, side, arm, B):
    """TYPE 3 - the HTF reversal. -> [(the cadence bar, why)].

        TYPE 3 v4cadence (the HTF reversal - when any of ws7r to ws12r (HTF lines) have been oob
        already in this trade, and now int(round(75%)) of the HTF lines are printing a reversal)

    THE POPULATION IS THE HTF LINES THAT HAVE BEEN OOB, not all of ws7..ws12. Joe 1025 confirmed
    it on his own 07:49 example, where ws9r is *"the only HTF line to oob"* and 75% qualifies on
    that one line: `int(round(0.75 x 1)) == 1`.

    *"ALREADY IN THIS TRADE"* is measured from the ARM bar - *"use the arm bar"*.

    *"PRINTING A REVERSAL"* is lift-off - *"lift-off. for t3cadence, precisely timed reversal(s)
    help us improve profit"*. The stamp is the actionable bar.

    THE EXTRA GATE IS HIS: *"the 75% qualification can only fire if there are no higher TFs
    exfence, ie there are no baton-pass candidates"*. That is tested at the candidate bar.
    """
    hi = int(K.L2_MOM_MAXTF)
    tfs = [t for t in range(HTF_LO, hi + 1) if t in R]
    oobm = {t: _oob(R[t], side) for t in tfs}
    stamp = {t: sorted(K.lift_stamp(int(x)) for x in F.revs(np.asarray(R[t], float), t, side))
             for t in tfs}
    out = []
    for k in range(int(arm), int(B) + 1):
        been = [t for t in tfs if oobm[t][int(arm):k + 1].any()]
        if not been:
            continue
        need = int(round(float(K.L2_T3_FRAC) * len(been)))
        if need < 1:
            continue
        rev = [t for t in been if any(int(arm) <= x <= k for x in stamp[t])]
        if len(rev) < need:
            continue
        #   his gate: no higher TF ex-fence, so no baton candidate exists above the top reverser
        top = max(rev)
        above = [t for t in range(top + 1, hi + 1) if t in R and K.ex_fence(R[t][k], side)]
        if above:
            continue
        out.append((int(k), 't3 %d of %d oob HTF lines reversed (ws%s), none above ws%d ex-fence'
                    % (len(rev), len(been), ','.join(str(t) for t in rev), top)))
        break                                      # the walk ends here; one t3 per walk
    return out
