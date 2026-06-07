"""
bl_grind — the BL grind's walk engine (pure) + the gated-vs-ungated metric.

The walk IS the realtime trade logic, replayed over historical bars (the same function
the live engine calls bar-by-bar — "the grind is a literal replay"):

  bls3      a BL line completes  → combined transitions INTO 3 → the trigger moment
  pk        a curated 5s pk within the last `pk_lookback` bars confirms the entry
  direction in line with that pk. The curated pk (= bl_states.raw_pk) is already
            bny30-gated upstream (PKGateFilter: it only exists when bny30 was open AND the
            signal opposed it — mean reversion), so its sign IS the trade direction:
            +1 long / -1 short (OOB-hi→short, #3). No separate bny30 input.
  entry     at the bls3 bar
  score     req2 (stop) = adverse excursion to the next swing in the trade direction;
            req3 (profit) = the following leg — recycled from bl_review

Pure: arrays in, trades out. The grind calls it per combo; the live engine on the window.
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


def walk(combined, pk_dir, px, pivots, pk_lookback: int = 11) -> list:
    """One pass over the bars → the gated trades.
      combined[i]   BL combined state (min-nonzero fold); 3 = a completion (bls3)
      pk_dir[i]     curated 5s pk (bl_states.raw_pk, already bny30-gated): 0 none, +1 long, -1 short
      px[i]         px_smooth
      pivots        [(idx, 'H'|'L')] swing pivots on px
      pk_lookback   bars before bls3 (inclusive) to search for a confirming curated pk

    At a bls3, the most recent curated pk within the last pk_lookback bars sets the
    direction ('in line with the 5s pk'); the trade opens at the bls3 bar."""
    n = len(px)
    next_kind, first_after = _swing_fns(pivots)
    trades = []
    for i in range(1, n):
        if combined[i] == 3 and combined[i - 1] != 3:                 # bls3: a completion
            lo = max(0, i - pk_lookback + 1)                          # last pk_lookback bars incl. i
            j  = next((k for k in range(i, lo - 1, -1) if pk_dir[k] != 0), None)  # most recent pk
            if j is not None:
                t = _score(i, pk_dir[j], px, next_kind, first_after)
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


def gated_vs_ungated(combined, pk_dir, px, pivots, pk_lookback: int = 11) -> dict:
    """The headline: the BL gate's value-add on the required stop. 'gated' = walk() trades
    (a bls3 confirmed by a curated pk in the lookback). 'ungated' = every curated pk, the
    BL gate removed, scored from its own bar. If gated's stop is tighter, the gate buys
    entry quality (the 0.68→0.33 stop thread)."""
    next_kind, first_after = _swing_fns(pivots)
    ungated = [t for t in (_score(i, pk_dir[i], px, next_kind, first_after)
                           for i in range(len(px)) if pk_dir[i] != 0)
               if t is not None]
    return {'pk_lookback': pk_lookback,
            'gated':   _summary(walk(combined, pk_dir, px, pivots, pk_lookback)),
            'ungated': _summary(ungated)}
