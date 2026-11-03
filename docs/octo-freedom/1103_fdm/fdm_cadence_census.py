"""THE fdm CADENCE CENSUS. His 1103 ask, verbatim:

    for each of these trades
    -find the cadence event(s), and the ensuing ws10x wob36 cross race(s).  (causal, first only)
    -report the percentage of towards (at the cadence event) against the percentage of reversals
     (at the ws10x-cadence)
    --report in TF ranges to curtail the data, ie ws3 to ws9, ws10 to ws16, ws17 to ws23,
      ws24 to ws30

HIS PREAMBLE, the cadence event:

    a cadence event prints on ws1b to ib, IF ws1,2Mage was more deeply oob (further away from 50)
    than ws1,2,3r during ws1b's oob excursion
    -ws1Mage, ws1b, ws1r are all oob at some time during ws1b's oob excursion
    -ws3Mage must be ex 25/75 fence while ws1b is oob
    --this cadence event can only be tested on target-side

HIS 1103 RULINGS, each one closing a hole I raised:

  the population       ws3 to ws30 for BOTH the cadence and the ws10x-cadence. 28 lines
  the Mage pairing     *"it can be any mage deeper than any r, as long as the ws1,2,3 candidates
                       are oob.  example, (ws2r is infence and printing a ws2Mage oob that is
                       deeper than ws1r oob) = qualify"*. So ONE pair suffices: an r among
                       ws1r/ws2r/ws3r that is oob, and a Mage among ws1Mage/ws2Mage deeper than it
  the side             the live trade's target side. There is no declined rev-trade - *"my 1841
                       short is conjecture.  if you pretend to be the LONG heading towards 1841,
                       and the cadence reports many `towards`, then the data is telling us to walk
                       to the next cadence"*
  ws3Mage's fence      25/75, confirmed
  the series           lift-off on EMERGING, every other read closed-prev. His standing rule
  "ex" on any fence    external of, INCLUDING oob. His standing rule

THE MECH THIS SERVES, his 1103 words and the piece that was missing:

    the mech will be walking from cadence event to cadence event, and at each event it will make a
    bimodal decision: walk or rev-trade
    --the walk option fires if the data infers that the lines are still climbing
    --rev-trade fires when the data is no longer telling us that the lines are trending with the
      trade's direction.  this is where the ws10x cross helps us - it fires outside of a normal
      cadence, and gives us a second chance at discovering if the lines are no longer strong enough
      to hold course

WOB 24 AND 36 ARE BOTH RUN. He wrote *"wob 24 or 36"* and used 36 in his example, so neither is
ruled and both are reported.

CAUSAL. Every read is at or before the bar it is reported on. The reversal census spans the cadence
event to the ws10x-cadence, both of which are confirm bars that are knowable at themselves.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import v4_l2_proxy as PX
    import v4_lineage2 as L2
    import v4_closed_prev as CP
    import ln
    from optimus9.analysis.jig import oob_ib_cross, lift_off
finally:
    sys.stderr = _e

E = RS.load((RS.K0, RS.R0, RS.S0))
HI = int(K.L2_MOM_MAXTF)
#   closed-prev for every value read, emerging kept only for lift-off
CPR = {t: np.asarray(CP.series(E[t], int(t) * 60), float) for t in range(1, HI + 1)}
EMR = {t: np.asarray(E[t], float) for t in range(1, HI + 1)}
MG = LL.mage()
CPM = {t: np.asarray(CP.series(MG[t], int(t) * 60), float) for t in MG}
BD = PX.Board(CPR, CPR, MG=CPM, MGE=CPM, PS=None)
B1 = np.asarray(CP.series(np.asarray(ln.line('ws1b'), float), 60), float)
X10 = np.asarray(ln.line('ws10x'), float)          # emerging - his fallback's own ruling
M10 = np.asarray(CP.series(MG[10], 600), float)
R10 = CPR[10]
RANGES = [(3, 9), (10, 16), (17, 23), (24, 30)]


def deeper(a, b, side):
    """Is `a` more deeply oob than `b` on `side` - further from 50. -> bool."""
    return (a > b) if int(side) > 0 else (a < b)


def cadence_events(side, A, B):
    """His cadence events on `side` in [A, B]. -> [(the event bar, the excursion start, why)].

    The event is ws1b's oob->ib cross. The three preamble tests are evaluated over the excursion
    that ENDS at that cross, so every read is at or before the event bar.
    """
    out = []
    oob = (B1 >= K.OOB_HI) if int(side) > 0 else (B1 <= K.OOB_LO)
    for c, cf, s in oob_ib_cross(B1, K.OOB_HI, K.OOB_LO, 1):
        if int(s) != int(side) or not (int(A) <= int(c) <= int(B)):
            continue
        j = int(c) - 1
        if j < 0 or not oob[j]:
            continue
        while j > 0 and oob[j - 1]:
            j -= 1
        s0, s1 = j, int(c) - 1
        assert s1 < int(c), 'an excursion ends at or after its own ib cross'
        #   test 1: a Mage among ws1,2Mage deeper than an oob r among ws1,2,3r, somewhere in it
        t1 = None
        for b in range(s0, s1 + 1):
            for rt in (1, 2, 3):
                rv = float(CPR[rt][b])
                rob = (rv >= K.OOB_HI) if side > 0 else (rv <= K.OOB_LO)
                if not rob:
                    continue
                for mt in (1, 2):
                    mv = float(CPM[mt][b])
                    if deeper(mv, rv, side):
                        t1 = (b, mt, mv, rt, rv)
                        break
                if t1:
                    break
            if t1:
                break
        if t1 is None:
            continue
        #   test 2: ws1Mage, ws1b and ws1r all oob at some time in it - each at its own bar
        def anyoob(a):
            seg = a[s0:s1 + 1]
            return bool(((seg >= K.OOB_HI) if side > 0 else (seg <= K.OOB_LO)).any())
        if not (anyoob(CPM[1]) and anyoob(B1) and anyoob(CPR[1])):
            continue
        #   test 3: ws3Mage ex-25/75 while ws1b is oob
        lo3, hi3 = 25.0, 75.0
        m3 = CPM[3][s0:s1 + 1]
        if not bool(((m3 >= hi3) if side > 0 else (m3 <= lo3)).any()):
            continue
        out.append((int(c), int(s0),
                    'ws1b excursion %s..%s, ws%dMage %.2f deeper than ws%dr %.2f at %s'
                    % (ln.U(s0)[11:], ln.U(s1)[11:], t1[1], t1[2], t1[3], t1[4],
                       ln.U(t1[0])[11:])))
    return out


def x10_race(side, frm, B, w):
    """The first ws10x race cross after `frm` on `side`, at hold `w`. -> (bar, which) or None.

    The three candidates are his: to ib, ws10r, ws10Mage. Cross OVER on the low side, UNDER on the
    high side - his fallback's own rule.
    """
    hits = []
    for c, cf, s in oob_ib_cross(X10, K.OOB_HI, K.OOB_LO, w):
        if int(s) == int(side) and int(c) > int(frm) and int(cf) <= int(B):
            hits.append((int(cf), 'to ib'))
            break
    for nm, other in (('ws10r', R10), ('ws10Mage', M10)):
        for i in range(int(frm) + 1, int(B) + 1):
            a, b = X10[i - 1], X10[i]
            oa, ob = other[i - 1], other[i]
            if not np.isfinite([a, b, oa, ob]).all():
                continue
            crossed = (a >= oa and b < ob) if side > 0 else (a <= oa and b > ob)
            if not crossed:
                continue
            end = i + w
            if end > len(X10):
                break
            seg = [(X10[j] < other[j]) if side > 0 else (X10[j] > other[j])
                   for j in range(i, end)]
            if all(seg):
                hits.append((i + w - 1, nm))
                break
    if not hits:
        return None
    return min(hits, key=lambda x: x[0])


def census(side, a, b, t0, t1):
    """-> {(lo,hi): (towards at `a`, reversed in (a, b], the ex-fence population)}.

    *** HIS 1103 POPULATION CHANGE. *** *"recreate the table using lines that have been
    ex-20/80-fence at least once during the trade"* / *"the n of 7 will need to change to n of
    {count of lines that went ex fence}"*. So the denominator is no longer the range's 7 lines - it
    is the lines in that range that printed ex-20/80 at least once in [t0, t1], the TRADE's span.
    "ex" INCLUDES oob, his standing rule, so the test is r <= 20 low / r >= 80 high.
    A line that never went ex-fence in the trade is out of both the numerator and the denominator.
    """
    fnc = float(K.FDM_RE_GATE_FNC) * 0 + 20.0      # fdm-20-80-fnc 20 -> (20.0, 80.0)
    edge = (100.0 - fnc) if int(side) > 0 else fnc
    out = {}
    for lo, hi in RANGES:
        tw = rv = n = 0
        for tf in range(lo, min(hi, HI) + 1):
            seg = CPR[tf][int(t0):int(t1) + 1]
            went = bool(((seg >= edge) if int(side) > 0 else (seg <= edge)).any())
            if not went:
                continue
            n += 1
            if L2.towards(BD, tf, int(a), int(side)):
                tw += 1
            r = next((int(x) for x in lift_off(EMR[tf], int(side), K.LIFT_PTS, K.gap_for(tf),
                                               K.LIFT_TOL, K.LIFT_WOB)
                      if int(a) < int(x) <= int(b)), None)
            if r is not None:
                rv += 1
        out[(lo, hi)] = (tw, rv, n)
    return out


TRADES = [('0702', '2026-08-03 07:02:00', 'LONG', None),
          ('1008', '2026-08-03 10:08:00', 'SHORT', +1),
          ('1315', '2026-08-03 13:15:00', 'LONG', -1),
          ('1406', '2026-08-03 14:06:00', 'SHORT', +1),
          ('1644', '2026-08-03 16:44:00', 'LONG', -1),
          ('1841', '2026-08-03 18:41:00', 'SHORT', +1)]
TEND = ln.K('2026-08-04 00:00:00')
W = [int(x) for x in os.environ.get('W_X10_WOB', '24,36').split(',')]

print('# THE fdm CADENCE CENSUS | 2026-08-03 | population ws3..ws30, his ruling')
print('# every value read is closed-prev; lift-off is emerging; ws10x is emerging, his fallback rule')
print('# the side at each event is the LIVE trade\'s target side - he is pretending to hold it')
print('# "ex" includes oob, his standing rule | ws3Mage fence 25/75')
print()
for i, (nm, t, d, psd) in enumerate(TRADES):
    k = ln.K(t)
    nxt = ln.K(TRADES[i + 1][1]) if i + 1 < len(TRADES) else TEND
    sides = ((psd,) if psd is not None else (-1, +1))
    for sd in sides:
        sn = 'HIGH' if sd > 0 else 'LOW'
        evs = cadence_events(sd, k, nxt)
        print('## %s %s | the live trade\'s target side %s | its span %s .. %s | %d cadence event%s'
              % (nm, d, sn, ln.U(k), ln.U(nxt), len(evs), '' if len(evs) == 1 else 's'))
        print()
        if not evs:
            print('| no cadence event on the %s side inside this trade\'s span |' % sn)
            print('|---|')
            print()
            continue
        print('| the cadence event | the ws10x hold | the ws10x-cadence | which candidate won |'
              ' the TF range | towards at the event | reversed by the ws10x-cadence | the'
              ' ex-fence population |')
        print('|---|---|---|---|---|---|---|---|')
        for ev, s0, why in evs:
            for w in W:
                rc = x10_race(sd, ev, TEND, w)
                if rc is None:
                    print('| %s | %d bars = %d s | none to %s | - | - | - | - | - |'
                          % (ln.U(ev), w, w * 5, ln.U(TEND)))
                    continue
                xb, which = rc
                cs = census(sd, ev, xb, k, nxt)
                for (lo, hi), (tw, rvn, n) in cs.items():
                    print('| %s | %d bars = %d s | %s | %s | ws%d to ws%d | %d of %d | %d of %d |'
                          ' %d |'
                          % (ln.U(ev), w, w * 5, ln.U(xb), which, lo, hi, tw, n, rvn, n, n))
        print()
        for ev, s0, why in evs:
            print('| the cadence event %s | %s |' % (ln.U(ev), why))
            print('|---|---|')
        print()
