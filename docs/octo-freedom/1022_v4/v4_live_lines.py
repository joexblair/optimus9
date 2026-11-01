"""THE FOUR LINES THE WALK IS HANDED, ON THE LIVE READ. Joe 1029: *"completely drop prev-close"*.

WHAT THIS REPLACES. `v4_closed_prev.arm_lines` returned the same four things built from the
previous completed bar's close, held forward. That read is dropped: he asked whether a ws1r
crossing at 2026-08-30 00:19 would be reading a ws12r value set at 00:12, and measured at that bar
ws12r was 7.08 minutes stale and ws10r 9.08 minutes stale.

WHAT IT COST WHILE IT WAS STILL IN THE WALK'S PATH. His ws1b hold is meant to hold the
00:59:25..01:20:45 low excursion together as one event. On the live read ws1b's crossing back
inside at 01:04:50 holds only 4 bars, so at 12 bars it does not qualify and the excursion stands.
On the prev-close read the same moment is one clean crossing at 01:04:00 holding 24 bars, which
qualifies, so the hold had no effect and the exit fired at 01:04:55 either way.

THE SHAPE IS UNCHANGED, so every caller swaps one import and no mech is edited.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


_SUB = {}


def sub_line(name):
    """A sub-wsf line by name, live off disk. -> array. gcws30b, gcws30r, gcws15b ...

    WHY IT IS NOT `ln.line`. That parser is hard-coded for the ws{tf}{role} name and multiplies the
    digits by 60, so it cannot read a 30 s or 15 s line - `ln.line('gcws30b')` raises on the digit
    scan. The spec comes from `LineStore.resolve`, which is the production resolver every
    optimus9 builder uses, so the array here is the same one the live tree reads.

    MEASURED 1031: gcws30b resolves to (30 s, bb 49, 0.95, close, emerging), the same bb spec as
    ws1b at half the timeframe seconds - which is what optimus9/analysis/build_ws_strat_walk.py
    asserts about the pair.
    """
    name = str(name)
    if name in _SUB:
        return _SUB[name]
    _e2 = sys.stderr; sys.stderr = io.StringIO()
    from optimus9.compute.line_config import LineStore
    from optimus9.orchestration.rpl_cache import LINE_DIR, _line_key
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.config import get_db_config
    sys.stderr = _e2
    db = DatabaseManager(**get_db_config()); db.connect()
    try:
        ls = LineStore(db)
        ovr = (*ls.resolve(name), ls.value_mode(name))
    finally:
        db.disconnect()
    import os
    p = os.path.join(LINE_DIR, _line_key(ln.EM, HOURS, WARMUP, ovr) + '.npy')
    a = np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]
    _SUB[name] = a
    return a


def arm_lines(E):
    """The four lines the walk reads, every one live. -> {'b', 'r', 'M'}.

    `E` is the live r ladder keyed by timeframe in minutes, the same dict `v4_rcfg_sweep.load`
    returns. ws1b and the two Mage lines come straight off the tape.
    """
    #   'g30b' IS gcws30b, added 1031 for his t1 and arm updates. It is handed in beside ws1b
    #   rather than replacing it in this dict, because the two mechs that move to it each carry
    #   their own knob and a run may have one on the new line and one on the old.
    return {'b': np.asarray(ln.line('ws1b'), float),
            'g30b': sub_line('gcws30b'),
            'r': {int(t): np.asarray(v, float) for t, v in E.items()},
            'M': {t: np.asarray(ln.line('ws%dMage' % t), float) for t in (1, 2)}}


def mage(hi=None):
    """The Mage ladder ws1..ws{hi}, live. -> {tf: array}.

    `hi` DEFAULTS TO THE KNOB, not to a literal 12. L2_MOM_MAXTF is declared as the ladder's top
    rung, and a caller that restates 12 silently disagrees with it the moment the knob moves -
    which is exactly what his 1030 *"increase the TF from 12 to 20"* does. One source for one fact.
    """
    hi = int(K.L2_MOM_MAXTF) if hi is None else int(hi)
    return {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, hi + 1)}
