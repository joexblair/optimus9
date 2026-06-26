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


def bro_cross_flips(db, W, sets=('hb16', 'hbhl16', 'hblo16', 'hbhi16'), cluster_min=30):
    """Bro-cross weave-cease flips → rich events (#37, docs/bias_mechanics_design.md). Returns a list of
    dicts {t, dir, set, mage, min} — the bias feed (`bro_cross_bias_events`) and the bl_review event-row
    overlay both derive from this (one computation, two views).

    Per set: confirm a flip once the EMERGING minion holds ONE side of the mage for `lp_bro_wob`
    consecutive 5s bars (the weave ceased), OOB-gated (both lines OOB the same side). lo-breach (both
    < lo, minion above mage) → +1 BULL; hi-breach (both > hi, mage above minion) → -1 BEAR. One flip per
    direction change per set. Aggregate the 4 sets, then CLUSTER: keep the FIRST flip per `cluster_min`-min
    cluster — an opposite direction = a new cluster (fires); a same direction within the window is
    suppressed (the 4 sets crossing in succession = one bias change). `set`/`mage`/`min` = the triggering
    set + its lines at the flip bar. Config-sourced: N from `lp_config.lp_bro_wob`, OOB from
    `optimus9_system` (no hardcode)."""
    N = int(db.execute("SELECT val FROM lp_config WHERE name='lp_bro_wob'", fetch=True)[0]['val'])
    sysr = db.execute('SELECT hi_boundary, lo_boundary FROM optimus9_system', fetch=True)[0]
    HI, LO = float(sysr['hi_boundary']), float(sysr['lo_boundary'])
    ts = W.ts; nb = len(ts)
    raw = []
    for st in sets:
        m = W._line_emerging(st + 'm'); M = W._line_emerging(st + 'M')
        fin = np.isfinite(m) & np.isfinite(M)
        sign = np.where(fin, np.sign(m - M), 0).astype(int)
        chg = np.concatenate([[True], sign[1:] != sign[:-1]])
        idx = np.arange(nb); last_start = np.maximum.accumulate(np.where(chg, idx, -1)); run_len = idx - last_start + 1
        last = 0
        for i in range(N, nb):
            if not fin[i]:
                continue
            held = run_len[i] >= N
            d = 1 if (held and sign[i] > 0 and m[i] < LO and M[i] < LO) else \
                (-1 if (held and sign[i] < 0 and m[i] > HI and M[i] > HI) else 0)
            if d and d != last:
                raw.append((int(ts[i]), d, st, float(M[i]), float(m[i]))); last = d
    raw.sort(key=lambda x: x[0])
    window = cluster_min * 60 * 1000
    out, le_t, le_d = [], None, 0
    for t, d, st, mage, minv in raw:
        if d != le_d or (le_t is not None and t - le_t >= window):
            out.append({'t': t, 'dir': d, 'set': st, 'mage': round(mage, 1), 'min': round(minv, 1)})
            le_t, le_d = t, d
    return out


def bro_cross_bias_events(db, W, **kw):
    """Bro-cross flips → direction events [(t_ms, dir)] for BiasState.feed (thin view of bro_cross_flips)."""
    return [(f['t'], f['dir']) for f in bro_cross_flips(db, W, **kw)]


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
