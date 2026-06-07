"""
bl_grind — the BL grind's walk engine (pure) + the gated-vs-ungated metric.

The walk IS the realtime trade logic, replayed over historical bars (the same
function the live engine will call bar-by-bar — "the grind is a literal replay"):

  bls3      a BL line completes  → combined transitions INTO 3 → the setup ARMS
  trigger   the first pk within `arm_timeout` bars, while bny30 is OPEN, fires a trade
  direction bny30's OPEN side sets it (gate, not a verdict): oob-hi → short, oob-lo → long
  score     req2 (stop) = adverse excursion to the next swing peak/trough in the trade
            direction; req3 (profit) = the following leg — the same risk/reward bl_review
            scores, anchored at the pk bar instead of the gate-open.

Pure functions: arrays in, trades out — no DB, no I/O. So the grind calls it per combo
in a worker, and the live engine calls it on the rolling window. Semantics that are
Joe's calls are isolated as args (`arm_timeout`) or one-liners flagged below.
"""
from __future__ import annotations


def _swing_fns(pivots):
    piv = sorted(pivots)
    def next_kind(i, kind): return next((x for x, k in piv if x > i and k == kind), None)
    def first_after(i0):    return next((x for x, k in piv if x > i0), None)
    return next_kind, first_after


def _score(j, d, px, next_kind, first_after):
    """req2/req3 for a trade opened at bar j, direction d (+1 long / -1 short).
    short → adverse is UP → next peak 'H'; long → adverse is DOWN → next trough 'L'."""
    pk = next_kind(j, 'H' if d == -1 else 'L')
    if pk is None:
        return None
    stop = round(abs(px[pk] - px[j]) / px[j] * 100, 3)
    tk   = first_after(pk)
    profit = round(abs(px[tk] - px[pk]) / px[pk] * 100, 3) if tk is not None else None
    return {'open_i': j, 'dir': d, 'stop_pct': stop, 'profit_pct': profit}


def _dir_from_bny30(oob):
    """bny30 OPEN side → trade direction. oob-hi (+1) → short (-1); oob-lo (-1) → long (+1).
    [confirm polarity — matches bl_review's hi-breach→short reversal.]"""
    return -1 if oob > 0 else 1


def walk(combined, pk_dir, px, bny30_oob, pivots, pk_lookback: int = 11) -> list:
    """One pass over the bars → the gated trades.
      combined[i]   BL combined state (min-nonzero fold); 3 = a line completed (bls3)
      pk_dir[i]     curated 5s pk this bar: 0 = none, +1 = long, -1 = short
      px[i]         px_smooth
      bny30_oob[i]  bny30 gate: 0 = closed (IB), +1 = open OOB-hi, -1 = open OOB-lo
      pivots        [(idx, 'H'|'L')] swing pivots on px
      pk_lookback   bars before bls3 to search for a confirming in-line pk

    At a bls3 (combined→3) with bny30 open, the bny30 side sets the direction (#3); if a
    curated pk IN THAT DIRECTION fired within the last `pk_lookback` bars (the confirmation —
    'in line with the 5s pk'), the trade opens at the bls3 bar."""
    n = len(px)
    next_kind, first_after = _swing_fns(pivots)
    trades = []
    for i in range(1, n):
        if combined[i] == 3 and combined[i - 1] != 3 and bny30_oob[i] != 0:   # bls3 + gate open
            d  = _dir_from_bny30(bny30_oob[i])
            lo = max(0, i - pk_lookback + 1)                                  # last pk_lookback bars incl. i
            if any(pk_dir[k] == d for k in range(lo, i + 1)):                 # an in-line pk
                t = _score(i, d, px, next_kind, first_after)
                if t is not None:
                    trades.append(t)
    return trades


def _summary(trades: list) -> dict:
    """#6 — the stop required to reach the profitable swing (req2). The gate earns its
    keep if it lowers this."""
    s = [t for t in trades if t['stop_pct'] is not None]
    if not s:
        return {'n': 0}
    stops = sorted(t['stop_pct'] for t in s)
    prof  = [t['profit_pct'] for t in s if t['profit_pct'] is not None]
    return {'n': len(stops),
            'avg_stop':    round(sum(stops) / len(stops), 3),
            'median_stop': stops[len(stops) // 2],
            'max_stop':    stops[-1],                                # worst-case stop needed
            'avg_profit':  round(sum(prof) / len(prof), 3) if prof else None}


def gated_vs_ungated(combined, pk_dir, px, bny30_oob, pivots, pk_lookback: int = 11) -> dict:
    """The headline: the BL gate's value-add on the required stop. 'gated' = walk() trades
    (a bls3 confirmed by an in-line pk). 'ungated' = every in-line pk while bny30 is open,
    the BL gate removed. If gated's stop is tighter, the gate is buying entry quality."""
    next_kind, first_after = _swing_fns(pivots)
    ungated = [t for t in (_score(i, _dir_from_bny30(bny30_oob[i]), px, next_kind, first_after)
                           for i in range(len(px))
                           if bny30_oob[i] != 0 and pk_dir[i] == _dir_from_bny30(bny30_oob[i]))
               if t is not None]
    return {'pk_lookback': pk_lookback,
            'gated':   _summary(walk(combined, pk_dir, px, bny30_oob, pivots, pk_lookback)),
            'ungated': _summary(ungated)}
