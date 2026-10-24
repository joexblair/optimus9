"""THE ROUTER. Joe 1024: *"the code should be asking 'where is my rev-trade event?', but we haven't
(SRP) built a routing mech. without a single point producing rev-trade, mechs conflate internally"*.

ONE RESPONSIBILITY: turn signals into trades. It owns the fire bar, the direction, the qualifier
and the close rule. It does not know how any signal was produced and never reads a line.

WHAT IT REPLACED, measured in the code it removes:
    the rev-trade BAR   computed in FIVE places by FOUR rules - `exh + 1` in v4core, `a + 1` in
                        v4core's immediate case, `max(exh, fire) + 1` in the backstop, `fill + 1`
                        in three v4saviour returns, and `max(exh, fire) + 1` again in
                        v4_equity.ledger. Now `v4_signal.fire_bar`, once.
    the DIRECTION       computed in TWO places that could disagree - `flip(the previous trade)` in
                        the chain and `'SHORT' if side > 0` in the scan. On 2026-09-01 19:43 they
                        did disagree and the row printed LONG beside a SHORT fire. Now
                        `v4_signal.direction`, once, from the signal's own side.

HIS RULINGS, 1024, each one a line of this file:

    a mech's condition being met creates a candidate regardless of what is open
    -yes.  then the pyramid checks are downstream of that

    [does a held signal expire] -no.  the mechs that carry a held signal will always print a verdict

    [which open position does a signal close, when two or more are open on that side]
    -close all of them together

    [does each open position get its own saviour] -no.  a single saviour will open on qualification
    and defer to the router if `saviour-rev` prints.  the router will close them all together

    rev-trade is 2 opposing mechanisms: CLOSE the trade, then OPEN a **NEW** trade in the opposite
    direction

THE ORDER IS HIS AND IT MATTERS. The close runs first, then the open is tested against the cap. So
closing a block never frees the slot the open is tested against - a HIGH signal closes LONGs and
then counts SHORTS, and the LONGs it just closed were never in that count.

THE PYRAMID TEST IS HIS, restated after I had made it a side-search question: *"it is simply: I'm
about to open a SHORT (or a long), is there a SHORT (or long) already open"*.

A HELD SIGNAL NEVER EXPIRES. It sits in the queue and is retried at every later signal bar, because
his answer was *"no"* and his reason was that the mech will always print a verdict. There is NO
horizon on the hold - adding one would be a cap he has not specified.

ONE SAVIOUR. The caller supplies it through `saviour`, called once per block when the block opens,
and its signal is routed like any other.

CAUSAL. Every fire is `signal bar + 1`, and the asserts carry that rather than comments. The router
walks signal bars forward and never reads one that has not landed.
"""
import v4_knobs as K
import v4_signal as SG


def _open_count(opens, dirn):
    """How many trades in `dirn` are open. -> int. The pyramid test's whole input."""
    return sum(1 for t in opens if t['dir'] == dirn)


def _close_all(opens, dirn, bar, why):
    """Close EVERY open trade in `dirn`. -> (the trades that stay open, the closed rows).

    Joe 1024: *"close all of them together"*, corrected from my "two" to *"two **or more**"*.
    """
    stay, shut = [], []
    for t in opens:
        if t['dir'] == dirn:
            shut.append(dict(t, close=int(bar), close_why=why))
        else:
            stay.append(t)
    return stay, shut


def route(sigs, A, B, saviour=None, max_pyramid=None):
    """Signals in, trades out. -> (the trades, the signals still held).

        sigs         every signal from every producer, in any order
        saviour      an optional callable (block_open_bar, block_dir) -> a signal or None, called
                     ONCE per block, when the block opens. His one-saviour ruling
        max_pyramid  the cap on same-direction opens. Defaults to K.MAX_PYRAMID

    A trade row carries `open`, `dir`, `sig`, and once closed `close` and `close_why`. A held
    signal carries `held_at`, the bar its open was first refused.

    A HELD SIGNAL'S FIRE BAR IS NOT ITS OWN. MY STRUCTURAL READ, STATED. A signal that lands at
    04:29 and is refused cannot later fire at 04:30 - that bar has passed, and acting on it would
    be a trade opened in the past. So a held signal fires at the bar its hold CLEARS:
        fire = max(the signal bar + 1, the bar the block freed)
    Joe ruled that a held signal never expires and that its mech will always print a verdict; he
    did not say which bar it fires on, and nothing else in his rulings forces one.
    """
    mx = K.MAX_PYRAMID if max_pyramid is None else max_pyramid
    assert mx >= 1, 'max_pyramid below 1 can never open a trade'
    pend = sorted([dict(s) for s in sigs if A <= s['bar'] <= B],
                  key=lambda s: (s['bar'], s['mech']))
    opens, done, held, sav_seen = [], [], [], set()

    def _offer_to_saviour(dirn):
        """A block has just opened. Offer it to the single saviour, once."""
        if saviour is None:
            return
        blk = [x for x in opens if x['dir'] == dirn]
        if not blk:
            return
        first = min(int(x['open']) for x in blk)
        if first in sav_seen:
            return
        sav_seen.add(first)
        sv = saviour(first, dirn)
        if sv is not None and A <= sv['bar'] <= B:
            pend.append(sv)
            pend.sort(key=lambda z: (z['bar'], z['mech']))

    def _act(s, bar):
        """The close, then the open - his order. -> the trade, or None when the open is HELD.

        A REFUSAL IS RECORDED, not inferred. `s['refused']` gains one row per bar this signal was
        turned away: the bar, the direction it wanted, and the OPEN BARS of the trades that filled
        the cap. Without it the hold's cause has to be reasoned about from the trade list.
        """
        nonlocal opens
        opens, shut = _close_all(opens, SG.closes(s['side']), bar,
                                 '%s %s' % (s['mech'], SG.direction(s['side'])))
        done.extend(shut)
        dirn = SG.direction(s['side'])
        if _open_count(opens, dirn) >= mx:
            s.setdefault('refused', []).append(
                (int(bar), dirn, tuple(int(x['open']) for x in opens if x['dir'] == dirn)))
            return None
        t = {'open': int(bar), 'dir': dirn, 'sig': s}
        opens.append(t)
        _offer_to_saviour(dirn)
        return t

    seen = 0
    while seen < len(pend):
        bar = pend[seen]['bar']
        batch = []
        while seen < len(pend) and pend[seen]['bar'] == bar:
            batch.append(pend[seen]); seen += 1
        #   HELD FIRST. They landed earlier, so they are older, and nothing in his rulings lets a
        #   newer signal overtake one that is waiting.
        queue, held = sorted(held, key=lambda z: z['bar']) + batch, []
        for s in queue:
            fire = max(SG.fire_bar(s), int(bar))
            assert fire > int(s['bar']), 'a fire cannot land on or before its own signal'
            if fire > B:
                held.append(s)
                continue
            t = _act(s, fire)
            if t is None:
                s['held_at'] = fire
                held.append(s)                         # the SAME dict, so `refused` accumulates
    return done + opens, held
