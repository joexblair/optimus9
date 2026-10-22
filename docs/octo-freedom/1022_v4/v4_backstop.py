"""`v4-ws5rbackstop`, Joe 1022. His spec, unedited:

    IF ws5r is oob and reversing AND (ws1r or ws2r or ws3r are same side oob) AND ws5Mage is past
    50 (<50 if ws5r is high, >50 if ws5r is low) AND a mage cascade verdict is the opposite of
    ws5r's oob side (ie a high oob ws5r needs a DOWN mage cascade verdict to rev-trade, low oob
    ws5r needs UP cascade) THEN rev-trade on the ws5r reversal
    -the ws1r,ws2r,ws3r oob condition has a +/-8.8 minute window to sync with ws5r reversing.  this
     needs to be causal

ONE MECH. No trade open, no v4saviour, no v4-lineage. It scans a span and reports every fire.

THE SIDE IS ws5r's OWN OOB SIDE, not a trade's. Nothing here takes a target-side: the mech reads
where ws5r is and what it does. The rev-trade's direction follows - a HIGH oob reversal spawns a
SHORT, a LOW oob reversal spawns a LONG - which is what his three examples are, all S.

HOW THE +/-8.8 WINDOW IS MADE CAUSAL, and this is MY STRUCTURAL READ, stated not decided quietly.
His window is symmetric but he required causality, and the two only reconcile one way: the oob may
land before OR after the reversal, and the FIRE BAR is the later of the two. So
    fill = max(the ws5r reversal stamp, the first qualifying oob bar in the window)
Nothing is read past the bar it fires on. His *"rev-trade on the ws5r reversal"* then means the
reversal is the EVENT; the fill waits for the last condition to land. Asserted, not commented.

TWO THINGS HE HAS NOT RULED, both parameters here and neither defaulted:
    cascade_at   the bar the mage cascade is read at. 'lift' takes the ws5r lift-off stamp, which is
                 his #25 r-driven read; 'fire' takes the fire bar itself.
    oob_when     'window' lets the oob land anywhere in the +/-8.8 min; 'at_fire' requires it to
                 still be oob on the fire bar.
"""
import sys
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
import v4_knobs as K
from optimus9.analysis.jig import mage_cascade, lift_off


def scan(A, B, R, MG, U, cascade_at, oob_when):
    """Every v4-ws5rbackstop fire with its reversal bar inside [A, B]. -> list of dicts."""
    assert cascade_at in ('lift', 'fire'), 'cascade_at is not ruled; pass it explicitly'
    assert oob_when in ('window', 'at_fire'), 'oob_when is not ruled; pass it explicitly'
    r5, m5 = R[5], MG[5]
    win = K.bstop_sync_bars()
    pool = list(range(1, K.BSTOP_POOL_HI + 1))
    out = []
    for side in (+1, -1):
        want = 'down' if side > 0 else 'up'          # opposite ws5r's oob side
        oob = {t: ((R[t] >= K.OOB_HI) if side > 0 else (R[t] <= K.OOB_LO)) for t in pool}
        for b in lift_off(r5, side, K.LIFT_PTS, K.gap_for(5), K.LIFT_TOL, K.LIFT_WOB):
            b = int(b)
            st = b + K.LIFT_WOB - 1                  # the usable event
            if st < A or st > B:
                continue
            if not K.oob(r5[b], side):               # ws5r must be oob AS IT REVERSES
                continue
            mg5 = float(m5[b])
            if not K.past_mid(mg5, -side):
                continue                             # ws5Mage must be past the middle fence the
                                                     # OTHER way to ws5r's oob side
            lo, hi = max(0, b - win), min(len(r5) - 1, b + win)
            hit = None
            for t in pool:
                w = np.flatnonzero(oob[t][lo:hi + 1])
                if len(w):
                    k = int(lo + w[0])
                    if hit is None or k < hit[1]:
                        hit = (t, k)
            if hit is None:
                continue
            fire = max(st, hit[1])
            if oob_when == 'at_fire' and not any(oob[t][fire] for t in pool):
                continue
            cb = st if cascade_at == 'lift' else fire
            assert cb <= fire, 'the cascade bar is past the fire bar'
            c = mage_cascade(MG, cb, zoom=K.SAV_CASCADE_ZOOM, min_lines=K.SAV_CASCADE_MIN)
            vd = None if c is None else c['verdict']
            if vd != want:
                continue
            out.append({'side': side, 'rev': b, 'stamp': st, 'fire': fire, 'oob_tf': hit[0],
                        'oob_bar': hit[1], 'ws5r': float(r5[b]), 'ws5Mage': mg5,
                        'cascade_bar': cb, 'verdict': vd,
                        'dir': 'SHORT' if side > 0 else 'LONG', 'why': c['why'] if c else '-'})
    out.sort(key=lambda d: d['fire'])
    return out
