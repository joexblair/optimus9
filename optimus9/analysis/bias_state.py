"""
bias_state.py (Joe 0623, #32) — breach-driven directional bias.

A thin collector over a COLLECTION of breach lines (currently just ['s22r']): it reads their bls3
flips from bl_states and holds a direction until the next flip —
    hi-breach → short (-1) · lo-breach → long (+1)   (bias = -breach_dir).

SRP: `flips()` collects the event stream from the line collection; `timeline()` / `direction_array()`
apply the verdict (the breach→direction rule lives ONLY here). Consumers (alchemy_report's s30a gate,
bl_review's bny30_bias) READ it — they never recompute. The line collection is the growth seam:
add lines to widen the bias source; the verdict and consumers don't change.
"""
from datetime import timezone
import numpy as np


class BiasState:
    def __init__(self, db, lines=('s22r',)):
        self._db = db
        self._lines = tuple(lines)

    def flips(self, end_ms, lookback_hours=120):
        """bls3-flip events across the line collection: sorted [(bar_time_ms, breach_dir), ...].
        A flip = the first bar of a state-3 run (state==3 and the line's previous state != 3)."""
        ph = ','.join(['%s'] * len(self._lines))
        rows = self._db.execute(
            f'''SELECT line_name, bar_time, state, breach_dir FROM bl_states
                WHERE line_name IN ({ph}) ORDER BY line_name, bar_time''',
            tuple(self._lines), fetch=True)
        start = end_ms - lookback_hours * 3600 * 1000
        out, prev = [], {}
        for r in rows:
            ln, st = r['line_name'], int(r['state'])
            t = int(r['bar_time'].replace(tzinfo=timezone.utc).timestamp() * 1000)
            if st == 3 and prev.get(ln) != 3 and start <= t < end_ms:
                out.append((t, int(r['breach_dir'])))
            prev[ln] = st
        out.sort()
        return out

    def timeline(self, end_ms, lookback_hours=120):
        """The held bias direction: [(t_ms, direction), ...], direction = -breach_dir, one per flip."""
        return [(t, -bd) for t, bd in self.flips(end_ms, lookback_hours)]

    def direction_array(self, ts, end_ms, lookback_hours=120):
        """Per-bar bias direction aligned to `ts` (forward-filled from the flips). 0 before the first."""
        tl = self.timeline(end_ms, lookback_hours)
        out = np.zeros(len(ts), np.int8)
        if not tl:
            return out
        ft = np.array([t for t, _ in tl]); fd = np.array([d for _, d in tl], np.int8)
        idx = np.searchsorted(ft, ts, 'right') - 1
        ok = idx >= 0
        out[ok] = fd[idx[ok]]
        return out
