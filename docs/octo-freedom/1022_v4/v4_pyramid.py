"""THE OPEN TRADES AND THE ADMISSION RULE. Joe 1024: *"SRP the max_pyramid routing. my gut says it
should be a class"*.

ONE RESPONSIBILITY: hold the open trades, answer whether one more may open in a direction, and
close every trade in a direction. It knows nothing about signals, bars-as-fires, mechs or lines.

WHY IT IS NOT IN v4_router. `route` was holding the position list, the close rule, the count, the
cap comparison AND the signal loop. The cap comparison is the only thing that decides whether a
signal becomes a trade, so it is the thing that must be readable on its own - and while it lived
inside the loop the open set leaked into the report, which Joe cut: *"why is `open before`
important? the router doesn't need that data"*.

HIS RULE, which is the whole class:

    router only holds the LONG signal for milliseconds: it's job is to accept the signal, check
    count(exisitng open same-side trade) <= max_pyramid, and drop the signal if false

and the test itself, restated by him after I had made it a side-search question:

    it is simply: I'm about to open a SHORT (or a long), is there a SHORT (or long) already open

THE CLOSE RUNS BEFORE THE TEST, and that is his order for rev-trade - *"CLOSE the trade, then OPEN
a **NEW** trade in the opposite direction"*. The caller sequences it; this class only provides the
two operations. Because a signal closes the OPPOSITE direction and is tested on its OWN, closing
never frees the slot it is then tested against.
"""


class Pyramid:
    """The open trades, and whether another may join them. `cap` is max_pyramid."""

    def __init__(self, cap):
        assert int(cap) >= 1, 'a cap below 1 can never open a trade'
        self.cap = int(cap)
        self._open = []
        self.closed = []

    def count(self, dirn):
        """How many trades are open in `dirn`. -> int. The admission rule's only input."""
        return sum(1 for t in self._open if t['dir'] == dirn)

    def admits(self, dirn):
        """May one more trade open in `dirn`. -> bool.

        THE BOUNDARY IS `count < cap`, so cap 1 means AT MOST ONE open in a direction. That is his
        *"is there a SHORT (or a long) already open"* - one open answers yes and refuses.

        HIS LATER WORDING READS THE OTHER WAY and is NOT applied here: *"check count(exisitng open
        same-side trade) <= max_pyramid"* admits at count == cap, so cap 1 would allow two open.
        The two statements differ by one trade and the difference is his to settle, so the code
        keeps the behaviour it already had rather than moving on the looser reading.
        """
        return self.count(dirn) < self.cap

    def blocking(self, dirn):
        """The OPEN BARS of the trades that fill the cap in `dirn`. -> tuple. For the report."""
        return tuple(int(t['open']) for t in self._open if t['dir'] == dirn)

    def earliest_open(self, dirn):
        """The first open bar of the block in `dirn`. -> bar or None.

        The block's own start, which is what a per-block mech is armed on.
        """
        b = [int(t['open']) for t in self._open if t['dir'] == dirn]
        return min(b) if b else None

    def close_all(self, dirn, bar, why):
        """Close EVERY open trade in `dirn`. -> the rows closed.

        Joe 1024: *"close all of them together"*, corrected from my "two" to *"two **or more**"*.
        """
        stay, shut = [], []
        for t in self._open:
            (shut if t['dir'] == dirn else stay).append(t)
        self._open = stay
        shut = [dict(t, close=int(bar), close_why=why) for t in shut]
        self.closed.extend(shut)
        return shut

    def open(self, bar, dirn, sig):
        """Open one trade. -> the trade row. The caller must have asked `admits` first."""
        assert self.admits(dirn), 'opened a trade the cap does not admit'
        t = {'open': int(bar), 'dir': dirn, 'sig': sig}
        self._open.append(t)
        return t

    def trades(self):
        """Every trade, closed and still open. -> list."""
        return self.closed + list(self._open)
