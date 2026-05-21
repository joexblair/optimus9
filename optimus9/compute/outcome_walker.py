"""
OutcomeWalker — shared per-bar forward walk for trade outcomes.
"""


"""
managers.py — PK Optimizer
All process classes. One responsibility per class.
Every class calls get_logger(self.__class__.__name__).

Terminology:
  OOB  = out of boundary (indicator has crossed high/low threshold)
  IB   = in boundary (indicator is within thresholds)
  OS/OB remain only in RSI/K oscillator context where they are technically correct.
"""

from typing import Optional
import numpy as np


def walk_outcome(close:      np.ndarray,
                 entry_idx:  int,
                 direction:  int,
                 stop_pct:   float,
                 timestamps: Optional[np.ndarray] = None) -> dict:
    """
    Walk forward from `entry_idx` on `close`, tracking max favorable
    excursion and stop fire.

    No max_bars cap — under the "always a stop" design principle, the
    only legitimate reason a trade can be unresolved is that the
    available kline data ends before the stop fires. Loop runs until
    stop fires OR `close` is exhausted.

    Returned dict has three fields:
      max_profit_pct     : best favorable excursion as a positive %
                           (downward for SHORT, upward for LONG)
      bars_to_max_profit : bar offset when that max was last updated;
                           None if max_profit_pct stayed at 0.0
      bars_to_stop       : bar offset when stop fired; None ⇔ "trade
                           ran off the end of the dataset" — the only
                           interpretation, by design.

    Rounding: max_profit_pct rounded to 6 decimals (TV is 5; we hold
    one extra digit for downstream aggregation precision).

    `timestamps` is reserved for future debug instrumentation. When
    provided, callers can wire it into per-call logging. Currently
    unused inside this function — kept on the signature so adding a
    debug print here later doesn't require a signature change anywhere
    upstream.

    Parameters
    ----------
    close : np.ndarray of float close prices
    entry_idx : int index into close where the trade enters
    direction : +1 for LONG, -1 for SHORT
    stop_pct : float stop distance in percent (e.g. 0.71 for 0.71%)
    timestamps : optional ms-epoch array, same length as close

    Returns
    -------
    dict {max_profit_pct, bars_to_max_profit, bars_to_stop}
    """
    entry = float(close[entry_idx])
    end   = len(close) - 1

    if direction == 1:
        stop_level = entry * (1.0 - stop_pct / 100.0)
    else:
        stop_level = entry * (1.0 + stop_pct / 100.0)

    best_price         = entry
    max_profit_pct     = 0.0
    bars_to_max_profit = None
    bars_to_stop       = None

    for j in range(entry_idx + 1, end + 1):
        c = float(close[j])

        if direction == 1:
            if c > best_price:
                best_price         = c
                max_profit_pct     = (best_price / entry - 1.0) * 100.0
                bars_to_max_profit = j - entry_idx
            if c <= stop_level:
                bars_to_stop = j - entry_idx
                break
        else:
            if c < best_price:
                best_price         = c
                max_profit_pct     = (entry / best_price - 1.0) * 100.0
                bars_to_max_profit = j - entry_idx
            if c >= stop_level:
                bars_to_stop = j - entry_idx
                break

    return {
        'max_profit_pct':     round(max_profit_pct, 6),
        'bars_to_max_profit': bars_to_max_profit,
        'bars_to_stop':       bars_to_stop,
    }
