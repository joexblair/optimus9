"""The maker-first fill model with a taker backup. 1016. Joe's three decisions, swept not chosen.

JOE 1016: *"maker/maker is highly unlikely. you have the 5s bars - tell me if you can build a
maker/maker solution. every trade signal that fires needs a resulting trade, so a taker "backup" is
needed if the maker is missed"*, then *"the three things all live in the data - the goal is the
config that produces the best overal pnl"*.

THE THREE, now knobs swept on net PnL rather than ruled:
    OFF_TICKS   how far inside the signal price the limit rests, in ticks
    WAIT_BARS   how long it rests before the taker backup crosses
    MAKER_EXIT  whether the exit also rests maker-first with the same backup

THE DATA. The 5 s highs and lows are in `kline_collection` (kc_high / kc_low), NOT in the scoring
tape - the tape cache holds only __ts__, __pxs__, __close__, __evt__. Measured over the 94 built
days: 1,624,320 rows, zero NULL highs or lows, the tick 0.000010 = 0.64 bps of the 0.155563 mean
close, the mean 5 s bar range 3.51 bps, and 33.11% of bars have zero range.

THE FILL RULE IS TRADE-THROUGH, NOT TOUCH. A resting bid fills at the first later bar whose LOW is
at or below it; an ask at the first whose HIGH is at or above it. AT OFF_TICKS 0 THAT IS THE TOUCH
PRICE AND THE NUMBER IS AN UPPER BOUND - the 5 s bars carry no depth and no queue position, so
"price reached my level" is not "I was filled". At 1 tick or more the price has traded THROUGH the
level, which is a defensible claim. The 0-tick arms are reported, and labelled.

ADVERSE SELECTION IS NOT ASSUMED, IT FALLS OUT. A bid fills when price is coming down to it, so the
trade is scored from the price it actually got, on the path that actually followed. The 0.040%
maker/maker row in docs/arm_delay_book.md is a FEE figure with no selection term; this model does
not need one because the selection is in the price path.

THE PER-LEG COSTS, decomposed from docs/arm_delay_book.md:117-128, which is internally consistent:
    maker leg   2.00 bps fee, 0.00 bps slippage      (maker/maker 0.040% = 2 x 2.00)
    taker leg   5.50 bps fee, 3.35 bps slippage      (taker/taker 0.177% = 0.110 + 0.067)
                                                      (taker/maker 0.108% = 0.075 + 0.034)
THE BANKED DRAG IS MORE CONSERVATIVE AND IS CARRIED AS AN ALTERNATIVE: 0.1975% round trip is
5.50 fee + 4.375 slippage per taker leg (8.75 bps slippage RT at 22,000 coins,
docs/octo-freedom/1005_knobs.md:39). W_FILL_TAKER_SLIP picks which.

WHAT THIS MODEL DOES NOT DO, and it matters: the signal list is banked FIRST and the fill model is
applied to it, so the standdown and the cap are computed on SIGNAL bars, not on fill bars. A maker
entry that fills late does not shift the next signal's standdown window. MINE AND STATED - it is
the first cut, and the alternative is re-walking octo2 per fill config, which the sweep cannot
afford. The effect is second order on entry and zero on exit.

SRP: this file turns a (signal bar, side) list into filled prices and a net. It decides no signal.
"""
import os
import numpy as np

TICK = float(os.environ.get('W_FILL_TICK', '0.00001'))
MAKER_FEE_BPS = float(os.environ.get('W_FILL_MAKER_FEE', '2.00'))
TAKER_FEE_BPS = float(os.environ.get('W_FILL_TAKER_FEE', '5.50'))
TAKER_SLIP_BPS = float(os.environ.get('W_FILL_TAKER_SLIP', '3.35'))   # 4.375 = the banked figure
MAKER_SLIP_BPS = float(os.environ.get('W_FILL_MAKER_SLIP', '0.00'))


def align(tape_ts, kl_ts, kl_hi, kl_lo):
    """Put the kline highs and lows on the TAPE's bar grid, by timestamp.

    The tape starts 2026-07-02 12:00 and the klines 2026-07-03, so index alignment would be wrong
    by 8,640 bars. Bars with no kline carry NaN and a fill test against them is a miss, never a
    silent pass. -> (hi, lo) both len(tape_ts).
    """
    t = np.asarray(tape_ts, np.int64)
    k = np.asarray(kl_ts, np.int64)
    hi = np.full(len(t), np.nan)
    lo = np.full(len(t), np.nan)
    pos = np.searchsorted(k, t)
    ok = (pos < len(k))
    pos_ok = pos[ok]
    same = k[pos_ok] == t[ok]
    idx = np.flatnonzero(ok)[same]
    hi[idx] = np.asarray(kl_hi, float)[pos_ok[same]]
    lo[idx] = np.asarray(kl_lo, float)[pos_ok[same]]
    return hi, lo


class Fill:
    """Maker-first with a taker backup, over one tape."""

    def __init__(self, px, hi, lo, off_ticks, wait_bars, tick=None):
        self.px = np.asarray(px, float)
        self.hi = np.asarray(hi, float)
        self.lo = np.asarray(lo, float)
        self.off = int(off_ticks)
        self.wait = int(wait_bars)
        self.tick = TICK if tick is None else float(tick)
        self.n = len(self.px)

    def leg(self, k, want):
        """One leg resting from bar k. `want` +1 BUY (rest a bid), -1 SELL (rest an ask).

        -> (the fill price, the fill bar, 'maker' or 'taker'). The backup crosses at k + wait and
        pays that bar's price, which is the cost of the miss and is measured, not assumed.
        CAUSAL: the fill test at bar j reads only bar j.
        """
        k = int(k)
        base = float(self.px[k])
        lim = base - self.off * self.tick if want > 0 else base + self.off * self.tick
        end = min(k + self.wait, self.n - 1)
        for j in range(k + 1, end + 1):
            if want > 0:
                v = self.lo[j]
                if np.isfinite(v) and v <= lim:
                    return lim, j, 'maker'
            else:
                v = self.hi[j]
                if np.isfinite(v) and v >= lim:
                    return lim, j, 'maker'
        return float(self.px[end]), end, 'taker'

    @staticmethod
    def leg_bps(how):
        return (MAKER_FEE_BPS + MAKER_SLIP_BPS) if how == 'maker' else \
               (TAKER_FEE_BPS + TAKER_SLIP_BPS)

    def trade(self, entry_bar, exit_bar, dr, maker_exit):
        """-> dict. dr +1 SHORT, -1 LONG - the banked frame.

        A SHORT enters by SELLING (rest an ask above) and exits by BUYING (rest a bid below).
        A LONG enters by BUYING and exits by SELLING. Resting is always on the favourable side,
        which is what earns the offset.
        """
        want_in = -1 if dr > 0 else +1
        ep, eb, eh = self.leg(entry_bar, want_in)
        if maker_exit:
            xp, xb, xh = self.leg(exit_bar, -want_in)
        else:
            xb = int(exit_bar); xp, xh = float(self.px[xb]), 'taker'
        gross = (100.0 * (ep - xp) / ep) if dr > 0 else (100.0 * (xp - ep) / ep)
        cost = (self.leg_bps(eh) + self.leg_bps(xh)) / 100.0
        return {'gross': gross, 'cost': cost, 'net': gross - cost,
                'entry_px': ep, 'exit_px': xp, 'entry_bar': eb, 'exit_bar': xb,
                'entry_how': eh, 'exit_how': xh}
