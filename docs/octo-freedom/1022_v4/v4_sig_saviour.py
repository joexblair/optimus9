"""v4saviour's SIGNAL PRODUCER, and nothing else. Joe 1024.

ONE RESPONSIBILITY: state every v4saviour signal on the tape. It reads no open position, and it is
not called by the router.

IT IS ARMED ON A SIGNAL, NOT ON A POSITION. Joe 1024 ruled it after I had built it the other way:

    the saviour's hunt starts at the gated signal's bar
    -yes, exactly the same behaviour as a non-gated signal

    here's what makes this simple and easy - the 0429 signal doesn't know it's gated, that's
    routers decision.  router doesn't feedback, therefore ZERO action is needed to allow the 0459
    saviour qualification to fire

WHAT IT REPLACED. `route` used to call this file once per BLOCK, at the block's earliest open bar,
through a `saviour=` callback. That made the saviour the one producer whose existence depended on
what the router had opened - and a signal the router DROPPED armed nothing at all. On 2026-09-01
the 04:28:55 HIGH core signal was dropped against the 03:34:30 SHORT, and under the callback the
only hunt on that block ran from 03:34:30, where the arm walkback read ws5r 90.66 HIGH oob and
returned NOT ARMED. Run from the signal's own bar the same mech reads ws5r 41.91, arms, and fires
SAVIOUR REV at 04:41:45.

THE HUNT'S TARGET-SIDE IS THE COUNTER OF THE SIGNAL'S SIDE, because the saviour hunts the trade
that signal would OPEN: a HIGH signal opens a SHORT, and a SHORT's target-side is LOW. The signal
it emits carries that same side, so it closes the SHORT and opens a LONG - which is what
`SAVIOUR REV` has always meant, and what Joe asked for: *"saviour should pass timestamp/LOW/saviour
to router"*. `STAYS OPEN` and `NOT ARMED` produce no signal.

THE WALK IS NOT REIMPLEMENTED. `v4_saviour.walk` owns branch A, branch B, his route clause and the
verdicts.
"""
import io
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_saviour as SV
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e


def produce(sigs, R, MG):
    """Every v4saviour signal armed on `sigs`. -> list of signals, bar-ordered.

        sigs  the signals from the other producers. One hunt per signal, from ITS bar

    IT DOES NOT ARM ON ANOTHER SAVIOUR SIGNAL, so the caller passes the other producers' output and
    this makes one pass. A saviour arming on a saviour would chain without end, and whether it
    should is UNRULED - Joe has not been asked.
    """
    out = []
    for g in sigs:
        assert g['mech'] != 'saviour', 'a saviour may not arm on another saviour signal'
        s = -int(g['side'])
        res = SV.walk(int(g['bar']), s, R, MG, ln.U)
        if res['verdict'] != 'SAVIOUR REV':
            continue
        out.append(SG.signal(int(res['fill']), s, 'saviour', int(g['bar']),
                             'fill %s, armed on the %s %s signal %s'
                             % (ln.U(res['fill']), 'HIGH' if g['side'] > 0 else 'LOW',
                                g['mech'], ln.U(g['bar']))))
    out.sort(key=lambda z: (z['bar'], z['side']))
    return out
