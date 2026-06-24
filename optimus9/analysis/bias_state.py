"""
bias_state.py (Joe 0623-24, #32) — the directional bias state, split for SRP.

  • PRODUCERS own the verdict — each turns a source into direction events:
      bls3_bias_events(db, lines, …) — s22r bls3 flip → -breach_dir (hi-breach short / lo-breach long)
      pk_bias_events(W)              — bias pk update: BULL → +1, BEAR → -1  (NEUT/VOID skipped)
  • BiasState is the AGNOSTIC HOLDER — it RECEIVES direction events from any producer, merges them
    (most-recent-wins over time), and serves a -1/0/+1 timeline. It has NO idea how the bias was set;
    the sources are interchangeable.

Consumers (alchemy_report's s30a gate, bl_review's bny30_bias) read BiasState only.
"""
from datetime import timezone
import numpy as np


def bls3_bias_events(db, lines=('s22r',), end_ms=None, lookback_hours=120):
    """bls3 flips across the line collection → direction events [(t_ms, -breach_dir)]."""
    ph = ','.join(['%s'] * len(lines))
    rows = db.execute(
        f'''SELECT line_name, bar_time, state, breach_dir FROM bl_states
            WHERE line_name IN ({ph}) ORDER BY line_name, bar_time''', tuple(lines), fetch=True)
    start = (end_ms - lookback_hours * 3600 * 1000) if end_ms else None
    out, prev = [], {}
    for r in rows:
        ln, st = r['line_name'], int(r['state'])
        t = int(r['bar_time'].replace(tzinfo=timezone.utc).timestamp() * 1000)
        if st == 3 and prev.get(ln) != 3 and (end_ms is None or start <= t < end_ms):
            out.append((t, -int(r['breach_dir'])))
        prev[ln] = st
    return out


def pk_bias_events(W):
    """Bias machine pk updates → direction events [(t_ms, dir)]: BULL → +1, BEAR → -1."""
    m = {'BULL': 1, 'BEAR': -1}
    return [(int(u['t']), m[u['call']]) for u in W.signals() if u['call'] in m]


class BiasState:
    """Agnostic holder of a -1/0/+1 bias timeline. Fed direction events by any producer; merges
    most-recent-wins. Knows nothing of the source."""

    def __init__(self):
        self._events = []                                    # [(t_ms, direction)]

    def feed(self, events):
        self._events.extend(events)
        return self                                          # chainable: BiasState().feed(a).feed(b)

    def timeline(self):
        return sorted(self._events)                          # merged, time-ordered (most-recent-wins)

    def direction_array(self, ts):
        """Per-bar direction aligned to `ts` (forward-filled from the merged events). 0 before the first."""
        tl = self.timeline()
        out = np.zeros(len(ts), np.int8)
        if not tl:
            return out
        ft = np.array([t for t, _ in tl]); fd = np.array([d for _, d in tl], np.int8)
        idx = np.searchsorted(ft, ts, 'right') - 1
        ok = idx >= 0
        out[ok] = fd[idx[ok]]
        return out
