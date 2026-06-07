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


def walk(combined, raw_pk, px, bny30_oob, pivots, arm_timeout: int = 12) -> list:
    """One pass over the bars → the gated trades.
      combined[i]   BL combined state (min-nonzero fold); 3 = a line completed (bls3)
      raw_pk[i]     pk signal this bar (truthy = pk fires)
      px[i]         px_smooth
      bny30_oob[i]  bny30 gate: 0 = closed (IB), +1 = open OOB-hi, -1 = open OOB-lo
      pivots        [(idx, 'H'|'L')] swing pivots on px
      arm_timeout   bars the arm survives after bls3 before it lapses
    """
    n = len(px)
    next_kind, first_after = _swing_fns(pivots)
    trades, i = [], 1
    while i < n:
        if combined[i] == 3 and combined[i - 1] != 3:                 # bls3: a completion
            j = next((k for k in range(i, min(n, i + arm_timeout + 1))  # first armed pk, bny30 open
                      if raw_pk[k] and bny30_oob[k] != 0), None)
            if j is not None:
                t = _score(j, _dir_from_bny30(bny30_oob[j]), px, next_kind, first_after)
                if t is not None:
                    trades.append(t)
                i = j + 1                                             # one trade per setup
                continue
        i += 1
    return trades


def _summary(trades: list) -> dict:
    scored = [t for t in trades if t['profit_pct'] is not None and t['stop_pct']]
    if not scored:
        return {'n': 0}
    rr = [t['profit_pct'] / t['stop_pct'] for t in scored]
    wins = sum(1 for r in rr if r >= 1.0)                            # [placeholder win rule: RR>=1]
    return {'n': len(scored),
            'avg_stop':   round(sum(t['stop_pct']   for t in scored) / len(scored), 3),
            'avg_profit': round(sum(t['profit_pct'] for t in scored) / len(scored), 3),
            'avg_rr':     round(sum(rr) / len(rr), 3),
            'win_rate':   round(wins / len(rr), 3)}


def gated_vs_ungated(combined, raw_pk, px, bny30_oob, pivots, arm_timeout: int = 12) -> dict:
    """The headline: the BL gate's value-add. 'gated' = walk() trades (pk must follow a
    bls3 within the arm). 'ungated' = every pk while bny30 is open, scored identically —
    the same signal with the BL gate removed. The delta is what the gate buys."""
    next_kind, first_after = _swing_fns(pivots)
    ungated = [t for t in (_score(j, _dir_from_bny30(bny30_oob[j]), px, next_kind, first_after)
                           for j in range(len(px)) if raw_pk[j] and bny30_oob[j] != 0)
               if t is not None]
    return {'arm_timeout': arm_timeout,
            'gated':   _summary(walk(combined, raw_pk, px, bny30_oob, pivots, arm_timeout)),
            'ungated': _summary(ungated)}
