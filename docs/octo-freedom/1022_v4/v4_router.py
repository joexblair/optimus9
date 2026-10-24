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

    router only holds the LONG signal for milliseconds: it's job is to accept the signal, check
    count(exisitng open same-side trade) <= max_pyramid, and drop the signal if false

    [which open position does a signal close, when two or more are open on that side]
    -close all of them together

    [does each open position get its own saviour] -no.  a single saviour will open on qualification
    and defer to the router if `saviour-rev` prints.  the router will close them all together

    rev-trade is 2 opposing mechanisms: CLOSE the trade, then OPEN a **NEW** trade in the opposite
    direction

THE ORDER IS HIS AND IT MATTERS. The close runs first, then the open is tested against the cap. So
closing a block never frees the slot the open is tested against - a HIGH signal closes LONGs and
then counts SHORTS, and the LONGs it just closed were never in that count.

THE PYRAMID TEST IS NOT IN THIS FILE. Joe 1024: *"SRP the max_pyramid routing. my gut says it
should be a class"*. `v4_pyramid.Pyramid` owns the open trades, the count, the cap boundary and the
close-all. This file owns the signal loop and nothing about positions - it asks `admits` and it
does not know what the answer was counted from.

A REFUSED SIGNAL IS DROPPED. There is no queue and no retry. Joe 1024 ruled it after reading the
decision journal: *"router only holds the LONG signal for milliseconds"*.

WHAT THE QUEUE DID, which is why he removed it. His earlier *"[does a held signal expire] -no"* was
built here as a queue retried at every later signal bar. On 2026-09-01 that turned 108 decisions
into 76 refusals, and a signal whose lineage exhausted at 11:52:45 opened a trade at 17:33:30 -
340m45s later, as the entry for a leg it had not detected. The queue is gone, so a signal is acted
on once, at its own fire bar, or not at all.

ONE SAVIOUR. The caller supplies it through `saviour`, called once per block when the block opens,
and its signal is routed like any other.

CAUSAL. Every fire is `signal bar + 1`, and the asserts carry that rather than comments. With the
queue gone there is no second fire bar to reason about: a signal acts on the bar after it landed.
"""
import v4_knobs as K
import v4_pyramid as PY
import v4_signal as SG


def route(sigs, A, B, saviour=None, max_pyramid=None, journal=None):
    """Signals in, trades out. -> (the trades, the signals dropped).

        sigs         every signal from every producer, in any order
        saviour      an optional callable (block_open_bar, block_dir) -> a signal or None, called
                     ONCE per block, when the block opens. His one-saviour ruling
        max_pyramid  the cap on same-direction opens. Defaults to K.MAX_PYRAMID
        journal      an optional list. EVERY decision this router makes appends one row: what it
                     was handed, what it did, and the count it compared to the cap. It changes no
                     behaviour. Joe 1024 set its shape: *"besides the timestamp 1) the data that
                     was passed into router and 2) what the router did with it and 3) why it did
                     what it did"*.
                     IT DOES NOT RECORD THE OPEN SET. Joe 1024: *"why is `open before` important?
                     the router doesn't need that data"*. The decision reads ONE number - the
                     same-direction count after the close - so the journal carries that number and
                     not the state it was counted from

    A trade row carries `open`, `dir`, `sig`, and once closed `close` and `close_why`. A dropped
    signal carries `dropped_at`, the bar its open was refused.

    SIGNALS ARE ACTED ON IN FIRE ORDER, which is signal-bar order since every fire is its own bar
    plus one. Within a bar the order is the mech's NAME, which is alphabetical and therefore
    arbitrary - UNRULED, and it decides which of several signals sharing a bar becomes the trade.
    """
    pyr = PY.Pyramid(K.MAX_PYRAMID if max_pyramid is None else max_pyramid)
    pend = sorted([dict(s) for s in sigs if A <= s['bar'] <= B],
                  key=lambda s: (s['bar'], s['mech']))
    dropped, sav_seen = [], set()

    def _offer_to_saviour(dirn):
        """A block has just opened. Offer it to the single saviour, once."""
        if saviour is None:
            return
        first = pyr.earliest_open(dirn)
        if first is None or first in sav_seen:
            return
        sav_seen.add(first)
        sv = saviour(first, dirn)
        if sv is not None and A <= sv['bar'] <= B:
            pend.append(sv)
            pend.sort(key=lambda z: (z['bar'], z['mech']))

    def _act(s, bar):
        """The close, then the open - his order. -> the trade, or None when the open is DROPPED.

        EVERY DECISION IS RECORDED, not inferred. One `journal` row per signal acted on, carrying
        what it was handed, what it did, and the count it compared against the cap.
        """
        dirn = SG.direction(s['side'])
        shuts = SG.closes(s['side'])
        row = {'bar': int(bar), 'sig': int(s['bar']), 'mech': s['mech'], 'side': int(s['side']),
               'wants': dirn, 'shuts': shuts}
        shut = pyr.close_all(shuts, bar, '%s %s' % (s['mech'], dirn))
        row['closed'] = tuple(int(x['open']) for x in shut)
        row['count'] = pyr.count(dirn)
        row['cap'] = pyr.cap
        if not pyr.admits(dirn):
            row['verdict'] = 'DROPPED'
            row['blocked_by'] = pyr.blocking(dirn)
            if journal is not None:
                journal.append(row)
            return None
        row['verdict'] = 'OPENED'
        row['blocked_by'] = ()
        if journal is not None:
            journal.append(row)
        t = pyr.open(bar, dirn, s)
        _offer_to_saviour(dirn)
        return t

    seen = 0
    while seen < len(pend):
        s = pend[seen]; seen += 1
        fire = SG.fire_bar(s)
        assert fire > int(s['bar']), 'a fire cannot land on or before its own signal'
        if fire > B:
            dropped.append(dict(s, dropped_at=None))
            continue
        if _act(s, fire) is None:
            dropped.append(dict(s, dropped_at=fire))
    return pyr.trades(), dropped
