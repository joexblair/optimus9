"""
swing_detect — percentage ZigZag swing detection (gate sweep Stage 0, v2).

Joe's framing: "map the difference between each spike and trough, where the
difference is greater than 0.9%." Finds alternating High/Low pivots where each
leg (pivot-to-pivot move) is at least `pct`%. Replaces the forward-walk
profit_partition proxy, which fragmented ~7 real swings into ~140 tiny windows.
See gate_sweep_design.md.

Close-based (matches outcome_walker's convention). A leg is confirmed once price
reverses >= pct% from the running extreme; the final running extreme is appended
as a provisional (still-forming) pivot.
"""
import numpy as np


def find_pivots(price: np.ndarray, pct: float = 0.9) -> list:
    """
    Return alternating pivots as a list of (index, kind), kind in {'H','L'}.

    A High is confirmed when price falls >= pct% below the running high since the
    last pivot; a Low when it rises >= pct% above the running low. Index 0 is
    prepended (opposite kind to the first confirmed pivot) so the initial leg is
    represented; the final running extreme is appended as provisional.
    """
    price = np.asarray(price, dtype=float)
    n = len(price)
    if n < 2:
        return []
    thr = pct / 100.0
    pivots = []
    hi_i = lo_i = ext_i = 0
    trend = 0                                    # 0 undecided, +1 rising, -1 falling
    for i in range(1, n):
        p = price[i]
        if trend == 0:
            if p > price[hi_i]:
                hi_i = i
            if p < price[lo_i]:
                lo_i = i
            if (price[hi_i] - p) / price[hi_i] >= thr:
                pivots.append((int(hi_i), 'H')); trend = -1; ext_i = i
            elif (p - price[lo_i]) / price[lo_i] >= thr:
                pivots.append((int(lo_i), 'L')); trend = 1; ext_i = i
        elif trend == 1:
            if p >= price[ext_i]:
                ext_i = i
            elif (price[ext_i] - p) / price[ext_i] >= thr:
                pivots.append((int(ext_i), 'H')); trend = -1; ext_i = i
        else:
            if p <= price[ext_i]:
                ext_i = i
            elif (p - price[ext_i]) / price[ext_i] >= thr:
                pivots.append((int(ext_i), 'L')); trend = 1; ext_i = i

    if trend != 0:
        pivots.append((int(ext_i), 'H' if trend == 1 else 'L'))
    if pivots and pivots[0][0] != 0:
        pivots.insert(0, (0, 'L' if pivots[0][1] == 'H' else 'H'))
    return pivots


def legs(price: np.ndarray, pivots: list) -> list:
    """Consecutive pivots → legs. Each leg is a dict:
       {start, end, dir (+1 up / -1 down), amp_pct}."""
    price = np.asarray(price, dtype=float)
    out = []
    for (a, ka), (b, kb) in zip(pivots, pivots[1:]):
        amp = (price[b] - price[a]) / price[a] * 100.0
        out.append({'start': a, 'end': b, 'dir': 1 if kb == 'H' else -1,
                    'amp_pct': amp})
    return out


def swing_mask(n: int, legs_list: list, min_amp_pct: float = 0.9) -> np.ndarray:
    """Per-bar boolean: bar is inside a leg whose |amplitude| >= min_amp_pct.
    Provisional first/last legs that fall short of the threshold are excluded."""
    m = np.zeros(n, dtype=bool)
    for lg in legs_list:
        if abs(lg['amp_pct']) >= min_amp_pct:
            m[lg['start']: lg['end'] + 1] = True
    return m
