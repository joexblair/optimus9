"""THE WALK REQUEST. Joe 1024: *"let's send a signal out from each mech to the walk, and those
signals will be born of the qualifiers... that allows the walk to discard any mech signal except
the one its holding, until rev-trade"*.

ONE RESPONSIBILITY: what a mech hands the walk. It produces none and runs no walk.

WHY A SECOND SIGNAL LAYER EXISTS. Until 1024 each mech called `v4_fast.walk` itself, so three
independent walks ran over the same bars and each emitted its own router signal. Nothing was
meddling - `walk` is pure - but the walks DUPLICATED: on 2026-09-01, 14 of 37 qualifier events
share a signal bar, and the router then dropped the losers by mech NAME. Joe's rule moves the
exclusivity to where the walk is:

    no other mech can meddle with the walk once walk has "started working with a mech"

THE RACE IS NOT THE ARM BAR IN ISOLATION. Joe corrected that: *"both core mechs arm on ws1b oob.
the distinction is found only when the certain lines qualify"*. So the bar that claims the walk is
the bar a mech's OWN qualifiers complete - which is what `bar` is here.

    mech            the qualifiers that birth the request
    core arm1       cws1b oob, then cws2r/cws3r qualify and a Mage is past 5/95
    core arm2       cws1b oob, then cws1r oob 18 bars, cws1Mage oob, two of cws4r-cws8r oob
    ws5rbackstop    a ws5r reversal, an oob partner among ws1-ws3r, ws5Mage past 50

TWO LAYERS, TWO OBJECTS. This is the mech -> walk layer; `v4_signal` is the walk -> router layer.
A request is NOT a trade signal: it names no direction and the router never sees one.
"""

#   the mechs that may request the walk. v4saviour is NOT here: it runs no lineage walk, it has its
#   own branch A / branch B / route, so it has nothing to hand this layer.
MECHS = ('core arm1', 'core arm2', 'ws5rbackstop')


def request(bar, side, mech, start_tf, anchor, immediate=False, why=''):
    """One mech -> walk request. -> dict.

        bar        the bar this mech's OWN qualifiers completed. THE RACE BAR
        side       +1 the HIGH oob side, -1 the LOW. An input, never derived
        mech       one of MECHS
        start_tf   the rung the walk starts on, chosen by the mech
        anchor     the bar the walk scans reversals FROM. For core it is `bar`; for the backstop it
                   is the ws5r reversal, which is EARLIER than the fire that qualified it
        immediate  v4core arm2's rule, carried here rather than reimplemented in the holder:
                   *"if ws{V4_CORE_LIN_ENTRY_TF}r is not oob, then it is an immediate exhaust"*
        why        one line for the report

    THE ANCHOR MAY PRECEDE THE BAR, and only the backstop uses that: its fire waits on the oob
    partner, so the walk starts from the reversal while the request is born at the fire.
    """
    assert mech in MECHS, 'unknown walk-request mech %r' % (mech,)
    assert side in (-1, +1), 'a request side must be -1 or +1, got %r' % (side,)
    assert int(bar) >= 0, 'a request bar must be a real bar'
    assert int(anchor) <= int(bar), 'the walk anchor is after the bar that requested it'
    assert int(start_tf) >= 1, 'a start TF must be a real rung'
    return {'bar': int(bar), 'side': int(side), 'mech': mech, 'start_tf': int(start_tf),
            'anchor': int(anchor), 'immediate': bool(immediate), 'why': why}
