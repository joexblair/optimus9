"""lin2-reentry's SIGNAL, and nothing else. His label, 1029: *"label it lin2-reentry"*.

ONE RESPONSIBILITY: state every lin2-reentry signal on the tape. It reads no open position and it
is not called by the router - the same rule v4_sig_saviour states for itself.

THE MECH, his words, 1029:

    -there is no trade open  (either because of a STOP, or because the machine is cold-starting)
    -walk
    -if ws1b crosses from oob to ib (candidate-side)
    --if ws5Mage is oob or has been oob in the last 5 minutes on the candidate-side
    ---anchor on the ws5Mage extremum.  the anchor is for the next step to align with
    ---if at least 2 ws{>5}Mage wsf lines are printing a value that is away from the candidate
       side, at the anchor bar
    ----open the trade, direction: away from candidate-side

HIS FIRST LINE IS THE ROUTER'S, NOT THIS FILE'S. *"the mech ends after the 23:53:50 bar, where it
delegates to the router to open the SHORT"*, and the layer's own rule is that a signal source reads
no open position. So this states EVERY firing and the router drops the ones it cannot take. On
2026-08-29 both 23:53:50 and 23:56:00 are stated; the router opens on the first and drops the
second because a trade is open.

THE SIGNAL CARRIES A BAR AND A SIDE. The anchor bar is NOT a field on it - his 1029 ruling:
*"that breaks SRP - router doesn't need it, and the duplication is a cost"*. It appears in the
report line and nowhere else. `src` is the signal's own bar, because this mech runs no walk and so
has no earlier starting bar to name.

THE SIDE IS THE SIDE ws1b CAME IN FROM. A HIGH crossing-in states side +1, and the router turns
that into a SHORT - the same convention every other signal in this layer uses.

EVERY READ IS LIVE. The last-completed-bar read is dropped, his 1029 ruling.

CAUSAL BY CONSTRUCTION: the anchor is the furthest point ws5Mage reached between its own run's
start and the crossing bar. No bar after the crossing is read, and the assert carries it.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_signal as SG
from optimus9.analysis.jig import oob_ib_cross
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e

MECH = 'lin2-reentry'


def anchor_at(M5, side, fire, lookback_bars):
    """The furthest point ws5Mage reached in its run, up to `fire`. -> (bar, value) or None.

    The run is the unbroken stretch beyond the line on `side` that contains `fire`, or the most
    recent such stretch inside the look-back. Only bars at or before `fire` are read.
    """
    m = K.oob_mask(M5, int(side))
    f = int(fire)
    j = f if m[f] else None
    if j is None:
        for i in range(f, max(0, f - int(lookback_bars)) - 1, -1):
            if m[i]:
                j = i
                break
    if j is None:
        return None
    i = j
    while i > 0 and m[i - 1]:
        i -= 1
    seg = np.asarray(M5[i:j + 1], float)
    if not np.isfinite(seg).any():
        return None
    k = i + (int(np.nanargmax(seg)) if side > 0 else int(np.nanargmin(seg)))
    assert k <= f, 'the anchor is later than the crossing bar - that read is not causal'
    return (k, float(M5[k]))


def signals(B1, MG, tf=None, lines=None, hi=None, lookback_s=None, xwob=None):
    """Every lin2-reentry signal on the tape, bar-ordered. -> list of signals.

    `B1` is ws1b and `MG` the Mage ladder keyed by timeframe, both the live read, handed in by the
    caller so this file holds no opinion about where they came from.
    """
    tf = int(K.LIN2_CHAIN_OPEN_TF) if tf is None else int(tf)
    need = int(K.LIN2_CHAIN_OPEN_LINES) if lines is None else int(lines)
    hi = int(K.L2_MOM_MAXTF) if hi is None else int(hi)
    lb = (int(K.LIN2_CHAIN_OPEN_LOOKBACK_S) if lookback_s is None else int(lookback_s)) // 5
    w = max(1, int(K.LIN2_CHAIN_OPEN_XWOB) if xwob is None else int(xwob))
    band = [t for t in range(tf + 1, hi + 1) if t in MG]
    assert band, 'no timeframe above ws%d in the Mage ladder - the count can never be met' % tf
    b1 = np.asarray(B1, float)
    m5 = np.asarray(MG[tf], float)
    gate = {+1: K.oob_mask(m5, +1), -1: K.oob_mask(m5, -1)}
    out = []
    for c, cf, sd in oob_ib_cross(b1, K.OOB_HI, K.OOB_LO, w):
        sd = int(sd)
        f = int(cf) if w > 1 else int(c)
        g = gate[sd]
        if not (bool(g[f]) or bool(g[max(0, f - lb):f + 1].any())):
            continue
        an = anchor_at(m5, sd, f, lb)
        if an is None:
            continue
        k, v0 = an
        got = [t for t in band
               if np.isfinite(MG[t][k])
               and ((float(MG[t][k]) < v0) if sd > 0 else (float(MG[t][k]) > v0))]
        if len(got) < need:
            continue
        out.append(SG.signal(f, sd, MECH, f,
                             'ws1b crosses in from the %s side %s, ws%dMage anchor %s at %.2f,'
                             ' %d of %d lines beyond it'
                             % ('HIGH' if sd > 0 else 'LOW', SG.why_time(f), tf, ln.U(k), v0,
                                len(got), len(band))))
    return sorted(out, key=lambda x: x['bar'])
