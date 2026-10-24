"""v4core's SIGNAL PRODUCER, and nothing else. Joe 1024.

ONE RESPONSIBILITY: find every bar where v4core's conditions are met and lineage resolves, and
state it as a signal. It opens no trade, picks no direction and reads no open position.

WHY IT IS A TAPE SCAN AND NOT A FORWARD SEARCH, which is the change Joe ruled:

    Does a mech's condition being met create a candidate regardless of what is open
    -yes.  then the pyramid checks are downstream of that

Before 1024 v4core was asked *"what will close the trade that is open?"* - `Machine.core` searched
forward from the open bar on that trade's target side and returned the FIRST arm's trade-open bar.
That made a signal's existence depend on what was already open, so a v4core arm on the counter side
was invisible rather than held. Joe found it twice: the 2026-09-01 16:07:05 LOW-side arm during an
open LONG, and the 04:26:00 HIGH-side arm he expected to see gated by max_pyramid.

AN ARM EPISODE, NOT AN ARM BAR. The conditions hold across a run of bars, so the signal is the
FIRST bar of each contiguous qualifying run per side. Without that collapse 09-01 produced 95 arm
bars for 5 real arms.

THE ARM ITSELF IS NOT REIMPLEMENTED HERE. `v4_core_arm.arm` owns STEP1's gate and both arms -
STEP2 and his 1024 second arm - and this file calls it. The lineage walk is `v4_fast.walk`.
"""
import io
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_core_arm as CA
import v4_fast as F
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


def _arm_episodes(CL, side, A, B):
    """Every arm EPISODE on one side. -> [(arm bar, gate bar, which)].

    An episode is the FIRST bar of a contiguous run where `CA.armed_at` holds; the run is then
    skipped. The conditions persist across many bars, so without the skip one arm reports as
    dozens - on 2026-09-01 the first version of this produced 95 rows for 5 arms, because the
    closed c-lines step every ~10 bars and an adjacent-bar test merged nothing.

    The GATE is read BACKWARDS from the arm with `CA.gate_at`. A forward search finds the gate
    first and then the arm; a tape scan has the arm and must find the gate that preceded it. The
    first version called `CA.arm` from each bar, which made the gate and the arm the same bar every
    time because the gate search restarted where the arm was.
    """
    out, k = [], int(A)
    while k <= int(B):
        w = CA.armed_at(CL, k, side)
        if w is None:
            k += 1
            continue
        g = CA.gate_at(CL, k, side)
        if g is not None:
            out.append((k, g, w))
        while k <= int(B) and CA.armed_at(CL, k, side) is not None:
            k += 1                                     # skip the rest of this run
    return out


def produce(CL, R, A, B):
    """Every v4core signal in [A, B], both sides. -> list of signals, bar-ordered.

    The signal bar is the LINEAGE EXHAUST, which is what v4core's STEP4/STEP5 resolve to. Joe's
    1024 immediate case - *"if ws{V4_CORE_LIN_ENTRY_TF}r is not oob, then it is an immediate
    exhaust"* - makes the arm bar itself the exhaust, and that is read here rather than inside the
    walk because it is v4core's rule and not lineage's.
    """
    out = []
    for side in (-1, +1):
        for a, gate, which in _arm_episodes(CL, side, A, B):
            stf = K.CORE_LIN_ENTRY_TF if which == 'arm2' else CA.start_tf(CL, a, side)
            if which == 'arm2' and not K.oob(R[stf][a], side):
                out.append(SG.signal(a, side, 'core', a,
                                     '%s arm %s, ws%d NOT oob - immediate exhaust'
                                     % (which, SG.why_time(a), stf)))
                continue
            v, exh = F.walk(R, stf, side, a, B)
            if v != 'EXHAUST' or exh is None:
                continue
            out.append(SG.signal(exh, side, 'core', a,
                                 '%s arm %s, ws%d' % (which, SG.why_time(a), stf)))
    out.sort(key=lambda s: (s['bar'], s['side']))
    return out
