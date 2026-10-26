"""THE SIGNAL. Joe 1024 named it, and naming it is the whole point of this file.

Joe 1024, asked whether a signal and a fire are the same thing:

    a signal, or a fire (do you see these as the same thing?  I see "signal" as "here, I have
    actionable data for you", and fire as "I'm actioining based on that signal". the distinction
    allows for holding signals if other mechs need to qualify

MY CODE HAD NO SUCH OBJECT, and the naming shows it: `v4_fast.scan` returns `fires`, and what it
actually produces is a SIGNAL by his definition - `max(the ws5r reversal stamp, the first
qualifying oob bar)`, the bar the last condition landed, with nothing actioned. v4core had no
signal stage at all: `Machine.core` returned a trade-OPEN bar, so the signal existed only as a
number inside a routing decision. Holding was impossible because there was nothing to hold.

THIS FILE OWNS ONE THING: what a signal IS. It does not produce one, qualify one, or act on one.
    the producers   v4_sig_core, v4_sig_bstop, v4_sig_saviour - one mech each
    the consumer    v4_router - the fire bar, the direction, the pyramid test, the hold queue

A SIGNAL CARRIES NO TRADE-OPEN BAR AND NO DIRECTION. Both were computed inside the mechs before
1024 - the open bar in five places by four different rules, the direction in two places that could
disagree - and that conflation is what Joe named: *"without a single point producing rev-trade,
mechs conflate internally"*. A signal states a BAR and a SIDE; the router derives the rest.
"""
import v4_knobs as K

#   the mechs that may produce a signal. A new producer adds its name here and nowhere else.
MECHS = ('core', 'backstop', 'saviour', 'reentry')


def signal(bar, side, mech, src, why=''):
    """One signal. -> dict.

        bar    the bar the mech's last condition LANDED on - an exhaust, a fill, an arm. It is a
               stamp or a confirm bar, so it is knowable AT that bar and nothing after it is read.
        side   +1 the HIGH oob side, -1 the LOW. THE SIDE IS AN INPUT, never derived here.
        mech   which producer. One of MECHS
        src    the bar that started the mech's own walk - its arm, its fire, its open. Carried for
               the trace only; the router never reads it
        why    one line for the report

    NO 'open' FIELD AND NO 'dir' FIELD, on purpose. See the module docstring.
    """
    assert mech in MECHS, 'unknown signal mech %r' % (mech,)
    assert side in (-1, +1), 'a signal side must be -1 or +1, got %r' % (side,)
    assert int(bar) >= 0, 'a signal bar must be a real bar'
    assert int(src) <= int(bar), 'a signal cannot land before the walk that produced it started'
    return {'bar': int(bar), 'side': int(side), 'mech': mech, 'src': int(src), 'why': why}


def why_time(bar):
    """The time format used INSIDE a signal's `why`. -> 'HH:MM:SS'.

    Joe 1024: *"the detail column can be reduced to ` step2 arm 00:26:00, ws2`"*. The date is
    dropped because the `why` sits beside the signal's own full `YYYY-MM-DD HH:MM:SS` timestamp in
    every report that prints it, so the day is already on the row.

    IT IS BARE HH:MM:SS, which breaks his own *"every printed timestamp is YYYY-MM-DD HH:MM:SS"*
    rule for a window that spans days: an arm on the previous day reads as if it were today's.
    This is the format he asked for and the limitation is stated rather than worked around.
    """
    import ln
    return ln.U(int(bar))[11:]


def direction(side):
    """The trade a signal on `side` would OPEN. -> 'LONG' or 'SHORT'.

    THE ONE SOURCE. Joe's own backstop rule - *"a HIGH oob ws5r reversal spawns a SHORT, a LOW oob
    reversal spawns a LONG"* - and it now governs every mech rather than only that one.

    IT REPLACED `flip(the previous trade)`, which was the chain's rule and which could disagree
    with the signal's own side. On 2026-09-01 19:43 it did: a HIGH-oob backstop fire whose own dir
    was SHORT opened a LONG, because the previous trade had been a SHORT and the chain alternated.
    Joe caught the contradiction inside the row.
    """
    assert side in (-1, +1), side
    return 'SHORT' if side > 0 else 'LONG'


def closes(side):
    """The direction a signal on `side` CLOSES. -> 'LONG' or 'SHORT'.

    rev-trade is two opposing mechanisms and Joe stated the order: *"CLOSE the trade, then OPEN a
    **NEW** trade in the opposite direction"*. So a HIGH-side signal closes LONGs and opens a SHORT.
    """
    return 'LONG' if side > 0 else 'SHORT'


def target_side(dirn):
    """The target-side an open trade owns. -> +1 high, -1 low.

    Banked: a LONG hunts the HIGH oob, a SHORT the LOW, and the side is set once at the open.
    """
    assert dirn in ('LONG', 'SHORT'), dirn
    return +1 if dirn == 'LONG' else -1


def fire_bar(sig):
    """The bar a signal may be ACTIONED on. -> bar.

    ONE RULE, IN ONE PLACE. It replaced five computations by four rules - `exh + 1` in v4core,
    `a + 1` in v4core's immediate-exhaust case, `max(exh, fire) + 1` in the backstop, `fill + 1` in
    three separate v4saviour returns, and `max(exh, fire) + 1` again inside v4_equity.ledger.

    The signal bar is already the bar its last condition became knowable, so the fire is the next
    bar and nothing earlier. The assert carries that rather than a comment.
    """
    b = int(sig['bar']) + 1
    assert b > int(sig['bar']), 'the fire bar is not after the signal bar'
    return b
