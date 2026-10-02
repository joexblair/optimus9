"""octo_loop — the decide layer o9-live's app calls each bar, for `octo-freedom`.

`O9LiveApp.on_bar` (`app.py:94-119`) calls `window(now_ms)`, the health hooks, then
`intents(W, positions, legs)`, and executes what comes back. This class is that interface - the role
`StrategyLoop` plays for the v2 producer. It is not a `StrategyLoop` producer: `StrategyLoop.intents`
runs two independent books with pyramids and v2's exits (`strategy.py:69-109`); octo-freedom's book is
`trade_walk.TradeBook`.

ONE JOB: turn `OctoFreedom`'s per-bar records into `TradeIntent`s and trade-signal dump lines, under
Joe's rulings. It builds no line (`OctoFreedom` / `Inputs` do), sizes nothing (`PositionSizer`) and
places nothing (`O9LiveApp` / the adapter).

JOE'S RULINGS IT APPLIES
    sides           dr +1 = SHORT = 'Sell', dr -1 = LONG = 'Buy' (Joe 0925). The book's trades carry
                    the arm's dr (Joe 1001)
    startup         Joe 1002: *"stay flat"* - the book starts empty at the first live bar
    no pyramid      Joe 1002: *"no pyramid trades. note the signal for recon and keep walking"* - a
                    same-dr octo-sig is written to the dump as `non-trading octo-sig`, no order
    a feed gap      Joe 1002: *"if the gap is less than 5 minutes, yes - place the trade"*, reading (a):
                    the whole gap under 5 min -> the opens inside it are placed, late; 5 min or more ->
                    none are placed, each is written as `non-trading octo-sig`. *"if a close event fires
                    in the gap, it needs to fire as soon as the event is known (after the gap)"* - closes
                    are placed whatever the gap
    the dump        five ruled fields, `trade_signal_dump.py`

THE BOOK FOLLOWS THE MECH; THE EXCHANGE FOLLOWS WHAT WAS PLACED. An open that is not placed still opens
in `TradeBook`, because the book is what the recon holds against the backtest. Its later close then
finds no position on the exchange and places nothing - the `non-trading octo-sig` line already told the
recon there will be no close.

A POSITION THE BOOK DID NOT OPEN STOPS THE LOOP AT STARTUP. If the exchange already holds a position
at the first live bar, `intents` raises: adopting it into the book, flattening it, or ignoring it is
Joe's ruling, not this class's.
"""
import time

from optimus9.live.octo_freedom import BAR_MS, OctoFreedom
from optimus9.live.octo_inputs import OctoConfig
from optimus9.live.sizing import TradeIntent
from optimus9.live.trade_signal_dump import TradeSignalDump

LATE_OPEN_MS = 5 * 60 * 1000        # Joe 1002: "if the gap is less than 5 minutes, yes - place the trade"


def side_of(dr):
    """dr +1 = SHORT = Sell, dr -1 = LONG = Buy - Joe 0925."""
    if int(dr) == 0:
        raise ValueError('a trade cannot carry dr 0')
    return 'Sell' if int(dr) > 0 else 'Buy'


def closing_side(pos_side):
    return 'Buy' if pos_side == 'Sell' else 'Sell'


class OctoLoop:
    def __init__(self, db, bias_cfg, dump=None, cfg=None, log=print):
        self.cfg = cfg or OctoConfig(db)
        self.prod = OctoFreedom(db, self.cfg, bias_cfg)
        self.dump = dump or TradeSignalDump()
        self.log = log
        self._W = None
        self._inp = None
        self._live_from = None
        self._last_T = None

    # --- the interface O9LiveApp calls ------------------------------------------------------------
    def window(self, now_ms):
        """Build this bar's window. -> the BiasWindow (the app's health hooks read `.ts` / `.line`)."""
        W, inp = self.prod.window(now_ms)
        if int(inp.ts[-1]) > int(now_ms) - BAR_MS:
            raise RuntimeError('octo_loop: the window ends at %d, a bar that has not closed by %d'
                               % (int(inp.ts[-1]), int(now_ms)))
        self._W, self._inp = W, inp
        return W

    def intents(self, W, positions, legs=None):
        """Step every new bar and return this bar's intents, in the order they must execute."""
        if W is not self._W:
            raise RuntimeError('octo_loop: intents() was handed a window this loop did not build')
        inp = self._inp
        T = int(inp.ts[-1])
        positions = positions or {}
        if self._live_from is None:
            if positions:
                raise RuntimeError('octo_loop: the exchange holds %r at startup and the book is empty. '
                                   'Adopt, flatten or ignore is Joe\'s ruling - not started'
                                   % (sorted(positions),))
            self._live_from = T                            # Joe 1002: stay flat; the book starts here
        recs = self.prod.advance(inp, self._live_from)
        gap_ms = 0 if self._last_T is None else T - self._last_T
        self._last_T = T
        now = int(time.time() * 1000)
        out = []
        for r in recs:
            for ev in r['events']:
                if ev[0] == 'open':
                    side = side_of(ev[1]['dr'])
                    if r['ts'] < T and gap_ms >= LATE_OPEN_MS:
                        self.dump.write('open', side, 'non-trading octo-sig', r['ts'], now)
                        self.log('octo_loop: octo-sig at %d not placed - feed gap %d ms >= %d'
                                 % (r['ts'], gap_ms, LATE_OPEN_MS))
                        continue
                    if side in positions:
                        self.log('octo_loop: octo-sig at %d not placed - the exchange already holds %s '
                                 'and the book was flat; no pyramid' % (r['ts'], side))
                        continue
                    out.append(TradeIntent('open', side=side, reason='octo-sig', ts=r['ts']))
                    self.dump.write('open', side, 'octo-sig', r['ts'], now)
                elif ev[0] == 'close':
                    tr = ev[1]
                    side = side_of(tr['dr'])
                    pos = positions.get(side)
                    if pos is None:
                        continue                           # the open was not placed; nothing to close
                    out.append(TradeIntent('close', side=closing_side(side), qty=float(pos['size']),
                                           reason=tr['closed_by'], ts=r['ts']))
                    self.dump.write('close', side, tr['closed_by'], r['ts'], now)
                elif ev[0] == 'inert':
                    self.dump.write('open', side_of(ev[2]), 'non-trading octo-sig', ev[1] * BAR_MS, now)
        return out

    # --- health hooks: O9LiveApp._write_phase calls these; they only report ------------------------
    def phase(self, W, positions):
        arm = self.prod.walk.arm
        book = self.prod.book.pos if self.prod.book else None
        if book is not None:
            label, tone = 'in trade %s' % side_of(book['dr']), 'go'
        elif arm.live:
            label, tone = 'armed dr %+d' % arm.arm_dr, 'wait'
        else:
            label, tone = 'flat', 'idle'
        return {'label': 'octo-freedom · ' + label, 'tone': tone,
                'arm': ('dr %+d' % arm.arm_dr) if arm.live else None,
                'gate': 'open' if self.prod._prev_emitted else None, 'gate_reason': None,
                'in_position': book is not None,
                'exit': None}                              # o9_health.exit_line is varchar(8), v2's exit line;
        #                                                    octo-freedom's exits are trade_walk's three - not one line

    def state_mask(self, W, since_ms=0):
        return 0, 0, False                                 # the v2 cascade grid has no octo-freedom cells

    def substrate(self, W):
        return {}

    def mech_events(self, W):
        return []
