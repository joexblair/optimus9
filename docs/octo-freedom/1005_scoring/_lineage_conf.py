"""LINEAGE AS CONFLUENCE ONLY. 1016. Joe's ruling, enforced structurally.

HIS WORDS, 1015: *"lineage is confluence only"*, and it corrected a real error - I had used
`run_leg`'s own end bar as a trade's exit, which cost 1.56 points on the 2026-07-22 22:09:55 SHORT
pair before he caught it.

WHY THIS FILE EXISTS. `_chain10.run_leg` returns an end bar, and an end bar in a caller's hand is
an exit waiting to be taken. This wrapper exists so there is ONE way to ask lineage a question and
it CANNOT answer with a bar: `read()` returns a verdict and a reason, never a timestamp a caller
could act on. The rule is in the return type, not in a comment.

SRP: this file converts a lineage walk into a confluence read. It opens no trade, closes none, and
owns no threshold.
"""
import os

CARRY_MIN = int(os.environ.get('W_LINEAGE_CARRY_MIN', 12))
# W_LINEAGE_CARRY_MIN - how many bars the walk must be carried for the read to be 'carrying'.
# 12 bars = 60 s. MINE, and STATED: Joe ruled the ROLE, not a threshold. 2026-07-22 measured the
# walk closing in 2 bars when nothing above the rider has turned, and carrying 90 to 392 bars when
# something has; 12 is above the former and far below the latter. TWEAKABLE.

VERDICTS = ('carrying', 'exhausted', 'blocked')


def read(run_leg, bar, trade_side):
    """Lineage's confluence read at `bar` for a trade of side `trade_side`. -> (verdict, reason).

    NO BAR IS RETURNED, EVER. Joe 1015: *"lineage is confluence only"*. A caller gets one of
    VERDICTS and a sentence, so a lineage walk cannot become an entry or an exit by accident.

        carrying   the walk was carried at least CARRY_MIN bars - something above the rider is
                   momentum-true toward the oob side the trade is heading to
        exhausted  the walk ended on the exhaustion test
        blocked    the walk ended on anything else - the max jumpstart gap, the MAE stop, a
                   backstop. Named separately because "the walk stopped" is not "the move is over"
    """
    end, why, _mae, _ceil, _hand, _tr = run_leg(int(bar), int(trade_side))
    carried = int(end) - int(bar)
    w = str(why)
    if carried >= CARRY_MIN:
        return 'carrying', 'the walk carried %d bars = %.2f min, ending on %s' % (
            carried, carried * 5 / 60.0, w)
    if 'exhaust' in w.lower():
        return 'exhausted', 'the walk closed in %d bars on %s' % (carried, w)
    return 'blocked', 'the walk closed in %d bars on %s' % (carried, w)


def agrees(verdict):
    """Does the read support acting? -> bool. 'carrying' only.

    STATED: this is a convenience for a caller that wants one boolean, and it still returns no bar.
    """
    return verdict == 'carrying'
