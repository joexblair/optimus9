"""v3_collect - the octo-v3 test-point collector. Joe's rulings only, one per line of code.

Joe 1018, starting the greenfield build: *"you'll learn the mech by examples. I'll walk you through
the events of many trades, you'll store everything in a db table that you'll consolidate into the
spec"*.

THE KNOBS HE NAMED, 1018:
    v3_min_tf     1     the TF controlling the signal cadence. 60 s
    v3_rmom_fnc   80    the fence testing whether an r is close enough to oob to be predicted
    v3_mage_fnc   75    the fence testing whether a Mage is close enough to oob to be predicted

THE WOBS HE RULED, 1018, each anchored to a value he had already banked:
    oob dwell     3     bars ws{min_tf}b's oob run must reach. His ws1mage-rev WS1MR_DWELL
    tp xwob       4     bars ib must hold for the test-point. His ws1mage-rev WS1MR_HOLD
    step1 wob     3     bars ib must hold for the lineage step 1. Joe 1018: *"6 step1's wob: 3"*

THE FENCES ARE MIRRORED, Joe 1018 *"1 and 2: yes"*: v3_rmom_fnc 80 reads (20, 80) and v3_mage_fnc
75 reads (25, 75), the same shape as momo_fence_r 17 -> (17, 83). The TRADE SIDE picks the end -
Joe 1016: a LONG hunts the high oob, a SHORT the low - and the side is set once at the open.

THE CHAIN, as he walked it:
  1  the required leg    ws{min_tf}b reaches oob on the trade's side, dwell 3. Joe 1018: *"3:
                         required"*
  2  the test-point      ws{min_tf}Mage crosses to ib, xwob 4. His marker, verbatim
  3  the extrema         walk back to look forward, same side, for the ws{min_tf}Mage extrema.
                         `jig.mage_cascade_bar` mode 'extrema' - his own 1017 producer, 48-bar gap
  4  rider-tf            set AT THE FIRST test-point: the highest wsf r in oob; else the highest
                         mom-true wsf r; else defer to routing, which is not built
  5  mrider-tf           the highest wsf Mage BETWEEN the fence and oob. Joe 1018: *"mrider's are
                         not latched - they qualify only between ex-fence and oob"*
  6  the race            every r-oob line at the test-point races to its OWN ib, step1 wob 3. The
                         WINNER carries lineage - Joe 1018: *"#12, the race's winner"* - and a tie
                         goes to the higher TF - *"#13, the higherTF is the tie breaker"*
  7  step2               at the winner's step1 bar ONLY (Joe 1018: *"8, only on the step1 bar"*),
                         winner+1 or winner+2 must be ex-fence on the SAME side (*"7, same side"*).
                         Qualifies -> the baton passes. Disqualified -> EXHAUST is printed
  8  the mrider override EXHAUST does not end the leg while an mrider is qualified. Joe 1018: *"at
                         23:16, we have an mrider, so the EXHAUST print is not the end of the leg
                         ... when they are qualified, we predict continuance and walk to the next
                         testpoint"*
  9  the verdict         the next test-point same-side -> the prediction held. Not same-side -> exit,
                         and the exit races MAE: above 1.1 the leg's MFE is set to 0

WHAT IS NOT RULED AND SO IS NOT HERE: why ws12Mage cannot claim mrider (Joe 1018: *"I don't yet
have a well-formed definition"* - the weakness read he described is recorded in the spec, not coded);
what rider-tf does at the SECOND test-point; which anchor the leg's MAE/MFE runs from; and what
step2 does when winner+2 falls outside wsf. Each is a column that stays NULL until he rules it.

CAUSAL. Every bar read is at or before the bar under test, and each wob's confirmation bar is
banked beside its event bar so a consumer never acts earlier than the fact is knowable.
"""
import os
import sys
import io
import glob
import contextlib

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')

MIN_TF = int(os.environ.get('W_V3_MIN_TF', 1))
RMOM_FNC = float(os.environ.get('W_V3_RMOM_FNC', 80))
MAGE_FNC = float(os.environ.get('W_V3_MAGE_FNC', 75))
OOB_DWELL = int(os.environ.get('W_V3_OOB_DWELL', 3))
TP_XWOB = int(os.environ.get('W_V3_TP_XWOB', 4))
STEP1_WOB = int(os.environ.get('W_V3_STEP1_WOB', 3))
WSF_HI = int(os.environ.get('W_V3_WSF_HI', 12))
MAE_RACE = float(os.environ.get('W_V3_MAE_RACE', 1.1))

DDL_TP = """
CREATE TABLE IF NOT EXISTS v3_testpoint (
  v3tp_id            INT AUTO_INCREMENT PRIMARY KEY,
  v3tp_trade_open    DATETIME     NOT NULL,
  v3tp_side          VARCHAR(5)   NOT NULL,
  v3tp_seq           INT          NOT NULL,
  v3tp_oob_leg_bar   DATETIME     NULL,
  v3tp_oob_leg_bars  INT          NULL,
  v3tp_tp_bar        DATETIME     NOT NULL,
  v3tp_tp_known      DATETIME     NOT NULL,
  v3tp_tp_mage       DOUBLE       NULL,
  v3tp_tp_b          DOUBLE       NULL,
  v3tp_extrema_bar   DATETIME     NULL,
  v3tp_extrema_val   DOUBLE       NULL,
  v3tp_extrema_back  INT          NULL,
  v3tp_rider_tf      INT          NULL,
  v3tp_rider_src     VARCHAR(16)  NULL,
  v3tp_mrider_tf     INT          NULL,
  v3tp_r_oob         VARCHAR(64)  NULL,
  v3tp_r_exfnc       VARCHAR(64)  NULL,
  v3tp_mage_oob      VARCHAR(64)  NULL,
  v3tp_mage_exfnc    VARCHAR(64)  NULL,
  v3tp_mrider_qual   VARCHAR(64)  NULL,
  v3tp_momtrue       VARCHAR(64)  NULL,
  v3tp_race_winner   INT          NULL,
  v3tp_race_order    VARCHAR(128) NULL,
  v3tp_step1_bar     DATETIME     NULL,
  v3tp_step1_known   DATETIME     NULL,
  v3tp_step2_p1_tf   INT          NULL,
  v3tp_step2_p1_r    DOUBLE       NULL,
  v3tp_step2_p2_tf   INT          NULL,
  v3tp_step2_p2_r    DOUBLE       NULL,
  v3tp_step2_ok      TINYINT      NULL,
  v3tp_print         VARCHAR(32)  NULL,
  v3tp_mrider_at_s1  INT          NULL,
  v3tp_predict       VARCHAR(32)  NULL,
  v3tp_next_tp       DATETIME     NULL,
  v3tp_next_side     INT          NULL,
  v3tp_held          TINYINT      NULL,
  v3tp_mae_open      DOUBLE       NULL,
  v3tp_mfe_open      DOUBLE       NULL,
  v3tp_mae_tp        DOUBLE       NULL,
  v3tp_mfe_tp        DOUBLE       NULL,
  v3tp_min_tf        INT          NOT NULL,
  v3tp_rmom_fnc      DOUBLE       NOT NULL,
  v3tp_mage_fnc      DOUBLE       NOT NULL,
  v3tp_oob_dwell     INT          NOT NULL,
  v3tp_tp_xwob       INT          NOT NULL,
  v3tp_step1_wob     INT          NOT NULL,
  v3tp_wsf_hi        INT          NOT NULL,
  UNIQUE KEY uq_v3tp (v3tp_trade_open, v3tp_seq, v3tp_min_tf, v3tp_rmom_fnc, v3tp_mage_fnc,
                      v3tp_oob_dwell, v3tp_tp_xwob, v3tp_step1_wob, v3tp_wsf_hi)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

DDL_LINE = """
CREATE TABLE IF NOT EXISTS v3_testpoint_line (
  v3tpl_id        INT AUTO_INCREMENT PRIMARY KEY,
  v3tpl_tp_id     INT          NOT NULL,
  v3tpl_at        VARCHAR(16)  NOT NULL,
  v3tpl_bar       DATETIME     NOT NULL,
  v3tpl_tf        INT          NOT NULL,
  v3tpl_r         DOUBLE       NULL,
  v3tpl_r_oob     TINYINT      NULL,
  v3tpl_r_exfnc   TINYINT      NULL,
  v3tpl_mage      DOUBLE       NULL,
  v3tpl_mage_oob  TINYINT      NULL,
  v3tpl_mage_exf  TINYINT      NULL,
  v3tpl_mrider_q  TINYINT      NULL,
  v3tpl_momtrue   TINYINT      NULL,
  UNIQUE KEY uq_v3tpl (v3tpl_tp_id, v3tpl_at, v3tpl_tf),
  KEY ix_v3tpl_tp (v3tpl_tp_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


class Tape(object):
    """The lines, the fences and the mom-true masks for one side. Reads; decides nothing."""

    def __init__(self, sc, cache):
        self.sc = sc
        self.R = {t: np.asarray(sc.LD(t * 60, 'r'), float) for t in range(1, WSF_HI + 3)}
        self.M = {t: np.asarray(sc.LD(t * 60, 'Mage'), float) for t in range(1, WSF_HI + 1)}
        self.B = np.asarray(sc.LD(MIN_TF * 60, 'b'), float)
        self.PX = np.asarray(sc.PX, float)
        self.MT = {}
        for t in range(1, WSF_HI + 1):
            g = glob.glob(os.path.join(cache, 'momt_ws%d_*.npz' % t))
            if g:
                z = np.load(g[0])
                self.MT[t] = {+1: z['p'], -1: z['m']}

    def oob(self, v, side):
        return (v >= self.sc.HI) if side > 0 else (v <= self.sc.LO)

    def ib(self, v):
        return (v > self.sc.LO) & (v < self.sc.HI)

    def exf(self, v, side, fnc):
        return (v >= fnc) if side > 0 else (v <= 100.0 - fnc)

    def qual(self, v, side, fnc):
        """mrider's band: past the fence but NOT oob. Joe 1018, and not latched."""
        return self.exf(v, side, fnc) and not self.oob(v, side)


def dwell_bar(line, side, tp, dwell, tape, back_from):
    """The most recent oob run, on `side`, that REACHES `dwell` bars, at or before `back_from`."""
    o = tape.oob(line, side)
    j = int(back_from)
    while j >= 0:
        if o[j]:
            e = j
            while e >= 0 and o[e]:
                e -= 1
            e += 1
            if (j - e + 1) >= int(dwell):
                return e, j - e + 1
            j = e - 1
        else:
            j -= 1
    return None, None


def ib_cross(line, side, frm, xwob, tape, until=None):
    """The first oob->ib cross strictly after `frm` whose ib run holds `xwob` bars.

    -> (the first ib bar, the bar it is knowable, the side the run was on) or (None, None, None).
    """
    n = len(line) if until is None else int(until)
    run, was = 0, None
    for j in range(int(frm) + 1, n):
        v = line[j]
        if tape.oob(v, +1):
            run, was = 0, +1
        elif tape.oob(v, -1):
            run, was = 0, -1
        elif tape.ib(v):
            run += 1
            if run >= int(xwob) and was is not None:
                return j - int(xwob) + 1, j, was
        else:
            run = 0
    return None, None, None


def step1_bar(line, frm, wob, tape):
    """The line's own ib bar - ib held `wob` bars, at or after `frm`. -> (bar, knowable)."""
    run = 0
    for j in range(int(frm), len(line)):
        run = run + 1 if tape.ib(line[j]) else 0
        if run >= int(wob):
            return j - int(wob) + 1, j
    return None, None


def collect(tape, trade_open, side, seq, tp, tp_known, oob_leg, oob_bars):
    """One test-point's row and its two ladders. Every field is a reading, no verdict is invented."""
    from optimus9.analysis.jig import mage_cascade_bar, MC_GAP
    sc = tape.sc
    m1 = tape.M[MIN_TF]
    ex, why = mage_cascade_bar(m1, tp, side, mode='extrema')
    row = {'trade_open': trade_open, 'side': side, 'seq': seq,
           'oob_leg_bar': oob_leg, 'oob_leg_bars': oob_bars,
           'tp_bar': tp, 'tp_known': tp_known,
           'tp_mage': float(m1[tp]), 'tp_b': float(tape.B[tp]),
           'extrema_bar': None if ex is None else int(ex),
           'extrema_val': None if ex is None else float(m1[int(ex)]),
           'extrema_back': None if ex is None else int(tp - int(ex))}
    lad = {}
    for lab, bar in (('extrema', row['extrema_bar']), ('testpoint', tp)):
        if bar is None:
            continue
        rows = []
        for t in range(1, WSF_HI + 1):
            r = float(tape.R[t][bar]); mg = float(tape.M[t][bar])
            rows.append({'tf': t, 'r': r, 'mage': mg,
                         'r_oob': bool(tape.oob(r, side)),
                         'r_exfnc': bool(tape.exf(r, side, RMOM_FNC)),
                         'mage_oob': bool(tape.oob(mg, side)),
                         'mage_exf': bool(tape.exf(mg, side, MAGE_FNC)),
                         'mrider_q': bool(tape.qual(mg, side, MAGE_FNC)),
                         'momtrue': bool(tape.MT[t][side][bar]) if t in tape.MT else None})
        lad[lab] = (int(bar), rows)
    tprows = lad['testpoint'][1]
    csv = lambda key: ','.join('ws%d' % q['tf'] for q in tprows if q[key])
    row['r_oob'] = csv('r_oob'); row['r_exfnc'] = csv('r_exfnc')
    row['mage_oob'] = csv('mage_oob'); row['mage_exfnc'] = csv('mage_exf')
    row['mrider_qual'] = csv('mrider_q')
    row['momtrue'] = ','.join('ws%d' % q['tf'] for q in tprows if q['momtrue'])
    # rider-tf, Joe's 5a. SET AT THE FIRST TEST-POINT, so seq > 1 leaves it NULL until he rules it.
    if seq == 1:
        oobs = [q['tf'] for q in tprows if q['r_oob']]
        mts = [q['tf'] for q in tprows if q['momtrue']]
        if oobs:
            row['rider_tf'], row['rider_src'] = max(oobs), 'oob'
        elif mts:
            row['rider_tf'], row['rider_src'] = max(mts), 'mom-true'
        else:
            row['rider_tf'], row['rider_src'] = None, 'routing'
    else:
        row['rider_tf'], row['rider_src'] = None, None
    mq = [q['tf'] for q in tprows if q['mrider_q']]
    row['mrider_tf'] = max(mq) if mq else None
    # THE RACE. Joe 1018: the winner carries lineage, and a tie goes to the HIGHER TF.
    oobs = [q['tf'] for q in tprows if q['r_oob']]
    arr = {}
    for t in oobs:
        k, c = step1_bar(tape.R[t], tp, STEP1_WOB, tape)
        if k is not None:
            arr[t] = (k, c)
    if arr:
        order = sorted(arr, key=lambda t: (arr[t][0], -t))
        row['race_order'] = ','.join('ws%d@%s' % (t, sc.U(arr[t][0])) for t in order)
        w = order[0]
        row['race_winner'] = w
        row['step1_bar'], row['step1_known'] = arr[w]
        s1 = row['step1_bar']
        p1, p2 = w + 1, w + 2
        row['step2_p1_tf'] = p1 if p1 <= WSF_HI else None
        row['step2_p1_r'] = float(tape.R[p1][s1]) if p1 in tape.R else None
        row['step2_p2_tf'] = p2 if p2 <= WSF_HI else None
        row['step2_p2_r'] = float(tape.R[p2][s1]) if p2 in tape.R else None
        ok1 = p1 <= WSF_HI and tape.exf(tape.R[p1][s1], side, RMOM_FNC)
        ok2 = p2 <= WSF_HI and tape.exf(tape.R[p2][s1], side, RMOM_FNC)
        row['step2_ok'] = int(bool(ok1 or ok2))
        row['print'] = 'BATON PASSES' if row['step2_ok'] else 'EXHAUST'
        mq1 = [t for t in range(1, WSF_HI + 1) if tape.qual(float(tape.M[t][s1]), side, MAGE_FNC)]
        row['mrider_at_s1'] = max(mq1) if mq1 else None
        row['predict'] = ('CONTINUANCE' if (not row['step2_ok'] and row['mrider_at_s1'])
                          else ('BATON' if row['step2_ok'] else 'LEG ENDS'))
    else:
        for q in ('race_order', 'race_winner', 'step1_bar', 'step1_known', 'step2_p1_tf',
                  'step2_p1_r', 'step2_p2_tf', 'step2_p2_r', 'step2_ok', 'print',
                  'mrider_at_s1', 'predict'):
            row[q] = None
    return row, lad
