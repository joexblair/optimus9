"""v4-ws5rbackstop's SIGNAL PRODUCER, and nothing else. Joe 1024.

ONE RESPONSIBILITY: state every backstop fire as a request to the walk. It runs no walk, and there
is no trade-open bar, no direction and no reading of what is open.

IT NO LONGER WALKS. Joe 1024 moved the walk's exclusivity into `v4_walk_hold`, so this file ends at
the fire. Its own spec is the qualifier set: *"IF ws5r is oob and reversing AND (ws1r or ws2r or
ws3r are same side oob) AND ws5Mage is past 50"*.

THE RENAME MATTERS. `v4_fast.scan` calls its output `fires` and `v4_backstop` says *"reports every
fire"*, but what they produce is a SIGNAL by Joe's 1024 definition - `max(the ws5r reversal stamp,
the first qualifying oob bar)` is the bar the last condition LANDED, with nothing actioned. His
distinction: *"'signal' as 'here, I have actionable data for you', and fire as 'I'm actioining based
on that signal'"*. `scan`'s field keeps its name because the array is cached and shared; what this
file emits is a signal, and the router owns the fire.

NO SIDE FILTER HERE. `Machine.backstop` filtered fires to the open trade's target-side, which was
right while a signal could only exist as a closure for the open position. Under his 1024 ruling a
condition being met is a candidate regardless of what is open, so both sides are produced and the
ROUTER decides. The 1024 side binding is not lost - it moves downstream to the pyramid test and
the close rule, which is where he put it.

THE SCAN AND THE WALK ARE NOT REIMPLEMENTED. `v4_fast.scan` owns the fire conditions, `v4_fast.walk`
the lineage, `K.walkable_run` the start TF.
"""
import io
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_fast as F
import v4_signal as SG
import v4_walk_req as WR
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


def requests(R, MG, A, B, fallback=None):
    """Every v4-ws5rbackstop walk request in [A, B], both sides. -> list, bar-ordered.

    THE REQUEST BAR IS THE FIRE and the walk's ANCHOR is the ws5r reversal, which is earlier. The
    fire waits on the oob partner, so the qualifiers complete after the reversal the walk must scan
    from - and Joe 1023's `max()` then keeps the emitted signal from predating the fire. The holder
    applies that max, once, for all three mechs.

    `fallback` is the start TF for a fire with no walkable same-side oob run holding ws5 - 134 of
    602 on the current bank. UNRULED by Joe, so None means no request rather than a rung chosen
    here.
    """
    out = []
    for d in F.scan(A, B, R, MG):
        r = K.walkable_run(R, d['fire'], d['side'])
        stf = r[0] if r else fallback
        if stf is None:
            continue
        out.append(WR.request(int(d['fire']), d['side'], 'ws5rbackstop', int(stf), int(d['rev']),
                              why='fire %s, ws%d' % (SG.why_time(d['fire']), stf)))
    out.sort(key=lambda q: (q['bar'], q['side']))
    return out
