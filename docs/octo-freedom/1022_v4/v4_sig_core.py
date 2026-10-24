"""v4core's WALK REQUESTS, and nothing else. Joe 1024.

ONE RESPONSIBILITY: find every bar where v4core's own qualifiers complete, and state it as a
request to the walk. It runs no walk, opens no trade, picks no direction and reads no open
position.

IT NO LONGER WALKS. Joe 1024: *"let's send a signal out from each mech to the walk, and those
signals will be born of the qualifiers... that allows the walk to discard any mech signal except
the one its holding, until rev-trade"*. `v4_walk_hold` owns the walk and its exclusivity; this file
owns the two arms. Before that each mech walked for itself, so three walks ran over the same bars.

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

THE ARM ITSELF IS NOT REIMPLEMENTED HERE. `v4_core_arm` owns STEP1's gate and both arms, and this
file calls it. Joe 1024 named them: **arm1** is the original cws2r/cws3r arm, **arm2** is his
cws1r-plus-two-of-cws4r-to-cws8r arm.
"""
import io
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_core_arm as CA
import v4_signal as SG
import v4_walk_req as WR
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


def requests(CL, R, A, B):
    """Every v4core walk request in [A, B], both sides. -> list, bar-ordered.

    THE START TF IS THE MECH'S OWN CHOICE and differs between the arms: arm1 hands the walk
    whichever of cws2r/cws3r triggered (ws3 on a tie, Joe 1023), arm2 hands it
    `CORE_LIN_ENTRY_TF` 4 - *"I've chosen ws4 specifically to align with the new 'ws4r to ws1Mage
    ib mech'"*.

    ARM2 CARRIES THE IMMEDIATE FLAG, his 1024 rule: *"if ws{V4_CORE_LIN_ENTRY_TF}r is not oob,
    then it is an immediate exhaust"*. It travels on the request so the rule stays v4core's while
    the holder executes it.
    """
    out = []
    for side in (-1, +1):
        for a, gate, which in _arm_episodes(CL, side, A, B):
            if which == 'arm2':
                stf = int(K.CORE_LIN_ENTRY_TF)
                out.append(WR.request(a, side, 'core arm2', stf, a, immediate=True,
                                      why='arm2 %s, ws%d' % (SG.why_time(a), stf)))
            else:
                stf = CA.start_tf(CL, a, side)
                out.append(WR.request(a, side, 'core arm1', stf, a,
                                      why='arm1 %s, ws%d' % (SG.why_time(a), stf)))
    out.sort(key=lambda q: (q['bar'], q['side']))
    return out
