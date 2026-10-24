"""v4-ws5rbackstop's SIGNAL PRODUCER, and nothing else. Joe 1024.

ONE RESPONSIBILITY: state every backstop fire whose lineage resolves, as a signal. No trade-open
bar, no direction, no reading of what is open.

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
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


def produce(R, MG, A, B, fallback=None):
    """Every v4-ws5rbackstop signal in [A, B], both sides. -> list of signals, bar-ordered.

    The signal bar is the LATER of the lineage exhaust and the fire itself. Joe 1023 ruled the
    max(): the fire waits for the oob pool, so it can land after the reversal the walk started
    from, and a signal may not predate the condition that produced it.

    `fallback` is the start TF for a fire with no walkable same-side oob run holding ws5 - 175 of
    1086 on the 1023 measurement. UNRULED by Joe, so None means the signal is not produced rather
    than a rung being chosen here.
    """
    out = []
    for d in F.scan(A, B, R, MG):
        r = K.walkable_run(R, d['fire'], d['side'])
        stf = r[0] if r else fallback
        if stf is None:
            continue
        v, exh = F.walk(R, stf, d['side'], d['rev'], B)
        if v != 'EXHAUST' or exh is None:
            continue
        bar = max(int(exh), int(d['fire']))
        out.append(SG.signal(bar, d['side'], 'backstop', int(d['rev']),
                             'fire %s, ws%d' % (SG.why_time(d['fire']), stf)))
    out.sort(key=lambda s: (s['bar'], s['side']))
    return out
