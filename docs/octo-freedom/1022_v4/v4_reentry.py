"""v4_reentry's SIGNAL PRODUCER, and nothing else. Joe 1025, inside the lineage2 handover:

    **v4_reentry mech:**
    -ws5Mage oob to IB AND ws{any TF >5}Mage failed to reach oob while ws5Mage was oob
    --examples: 08-28 1125, 1500, 08-29 0010, 0235

    build it now. the described reentry will be the only reentry mech in lineage2

ONE RESPONSIBILITY: state every v4_reentry signal on the tape. It runs no walk and reads no open
position - the router opens the trade, and lineage2's walk then runs on from there.

THE SIDE. ws5Mage leaves an oob run on one side; the signal carries THAT side, so the router opens
the direction that side implies. His 08-29 02:35 example is *"a LONG open at 0235 on reentry's
signal"* with *"target-side is high for the LONG"*, which is `v4_signal.direction(-1) == 'LONG'` -
a LOW-oob ws5Mage run. So the signal side is the side of the run ws5Mage just left.

THE LADDER ABOVE ws5 IS EMERGING, his 1025 ruling for the whole rider band: *"I don't want slower
TF's running on closed bars because it spoils the line reversal times"*. Its top rung is
`L2_MOM_MAXTF` 12 - *"ws{any TF >5}Mage"* needs a top and 12 is the one he set for this fork.

NO DWELL ON THE ib CROSS. Joe 1025: *"no dwell... because we're on closed bars, we have an
automatic wob"*. ws5Mage is EMERGING here, so that reasoning is his for the cws lines rather than
this one - stated, and the cross is taken at `xwob` 1, its own bar.

CAUSAL. The oob run and the partner test both read bars at or before the cross, and the assert
carries it.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import v4_knobs as K
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
from optimus9.analysis.jig import oob_ib_cross
sys.stderr = _e

BASE_TF = 5                                   # *"ws5Mage oob to IB"*


def _runs(a):
    """Contiguous True runs of `a`. -> [(start, end)] inclusive."""
    d = np.diff(np.r_[False, a, False].astype(np.int8))
    return list(zip(np.flatnonzero(d == 1).astype(int), (np.flatnonzero(d == -1) - 1).astype(int)))


def produce(MG, A, B, trace=None):
    """Every v4_reentry signal in [A, B], both sides. -> list of signals, bar-ordered.

        MG  {tf: the EMERGING ws{tf}Mage line}, covering BASE_TF .. L2_MOM_MAXTF

    One signal per ws5Mage oob run whose ib cross lands in the window and during which NO higher
    Mage reached oob. The run's own side is the signal's side.
    """
    hi = int(K.L2_MOM_MAXTF)
    above = [t for t in range(BASE_TF + 1, hi + 1) if t in MG]
    assert above, 'no Mage rung above ws%d to test' % BASE_TF
    m5 = np.asarray(MG[BASE_TF], float)
    out = []
    #   the ib crosses give the run's END and its side; the run's START comes from the oob mask.
    for side in (-1, +1):
        oob = (m5 <= K.OOB_LO) if side < 0 else (m5 >= K.OOB_HI)
        starts = {e: s for s, e in _runs(oob)}
        for c, cf, s in oob_ib_cross(m5, K.OOB_HI, K.OOB_LO, 1):
            if s != side or not (int(A) <= c <= int(B)):
                continue
            s0 = starts.get(c - 1)                 # the cross's first ib bar, so the run ends at c-1
            if s0 is None:
                continue
            row = {'bar': int(c), 'side': side, 'run_from': int(s0), 'run_to': int(c) - 1}
            assert row['run_to'] < row['bar'], 'the oob run does not end before its ib cross'
            reached = [t for t in above
                       if (np.nanmin(MG[t][s0:c]) <= K.OOB_LO if side < 0
                           else np.nanmax(MG[t][s0:c]) >= K.OOB_HI)]
            row['reached'] = tuple(reached)
            if reached:
                row['stage'] = 'ws%s reached oob during the run' % ','.join(str(t) for t in reached)
                _keep(trace, row)
                continue
            row['stage'] = 'reentry'
            _keep(trace, row)
            out.append(SG.signal(int(c), side, 'reentry', int(s0),
                                 'ws%dMage %s oob %s..%s, no higher Mage reached oob'
                                 % (BASE_TF, 'LOW' if side < 0 else 'HIGH',
                                    SG.why_time(s0), SG.why_time(int(c) - 1))))
    out.sort(key=lambda z: (z['bar'], z['side']))
    return out


def _keep(trace, row):
    if trace is not None:
        trace.append(row)
