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
    # Seed at the first FINITE bar, and skip non-finite bars in the walk. Seeding at index 0 when price[0] is
    # NaN made every comparison against the running extreme False, so `trend` never left 0 and the function
    # returned [] SILENTLY — a warmup prefix of 2 NaNs was enough (Joe 0709).
    fin = np.flatnonzero(np.isfinite(price) & (price > 0))
    if fin.size < 2:
        return []
    start = int(fin[0])
    hi_i = lo_i = ext_i = start
    trend = 0                                    # 0 undecided, +1 rising, -1 falling
    for i in range(start + 1, n):
        p = price[i]
        if not np.isfinite(p) or p <= 0:
            continue
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
    if pivots and pivots[0][0] != start:
        pivots.insert(0, (start, 'L' if pivots[0][1] == 'H' else 'H'))   # anchor at the first FINITE bar, not 0
    return pivots


def compare_pivots(a, b, pct: float = 0.9, tol: int = 12) -> list:
    """Run the 0.9% ZigZag on TWO aligned price series (a, b — same length/index) and align
    their pivots. Returns rows sorted by bar:
      {kind, a_bar, b_bar, a_px, b_px, lag, diff_pct, status}
    status: 'both' (matched same-kind pivot within `tol` bars), 'a_only', 'b_only'.
    lag = b_bar - a_bar (bars); diff_pct = (b_px - a_px)/a_px*100 at the matched pivots.
    Leading NaN is ffilled (so DEMA warmup doesn't stall the running extreme); the synthetic
    index-0 prepend pivot is dropped. Used to compare px_smooth vs close swing detection."""
    def prep(x):
        x = np.asarray(x, float).copy(); m = np.isfinite(x)
        if m.any() and not m.all():
            idx = np.where(m, np.arange(len(x)), 0); np.maximum.accumulate(idx, out=idx)
            x = x[idx]; x[:int(np.argmax(m))] = x[int(np.argmax(m))]
        return x
    a, b = prep(a), prep(b)
    pa = [p for p in find_pivots(a, pct) if p[0] != 0]
    pb = [p for p in find_pivots(b, pct) if p[0] != 0]
    used, rows = set(), []
    for ba, ka in pa:
        cand = [(j, bb) for j, (bb, kb) in enumerate(pb) if kb == ka and j not in used and abs(bb - ba) <= tol]
        if cand:
            j, bb = min(cand, key=lambda x: abs(x[1] - ba)); used.add(j)
            rows.append(dict(kind=ka, a_bar=int(ba), b_bar=int(bb), a_px=float(a[ba]), b_px=float(b[bb]),
                             lag=int(bb - ba), diff_pct=round((b[bb] - a[ba]) / a[ba] * 100, 4), status='both'))
        else:
            rows.append(dict(kind=ka, a_bar=int(ba), b_bar=None, a_px=float(a[ba]), b_px=None,
                             lag=None, diff_pct=None, status='a_only'))
    for j, (bb, kb) in enumerate(pb):
        if j not in used:
            rows.append(dict(kind=kb, a_bar=None, b_bar=int(bb), a_px=None, b_px=float(b[bb]),
                             lag=None, diff_pct=None, status='b_only'))
    rows.sort(key=lambda r: r['a_bar'] if r['a_bar'] is not None else r['b_bar'])
    return rows


def nearest(bars: np.ndarray, i: int):
    """The VALUE in sorted `bars` closest to `i` (back OR forth); None if empty.
    Returns the bar index itself (not its position in `bars`)."""
    if len(bars) == 0:
        return None
    k = int(np.searchsorted(bars, i))
    cands = [c for c in (k - 1, k) if 0 <= c < len(bars)]
    return int(bars[min(cands, key=lambda c: abs(int(bars[c]) - i))]) if cands else None


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
