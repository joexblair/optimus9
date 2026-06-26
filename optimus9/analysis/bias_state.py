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


def bro_cross_flips(db, W, sets=('hbhl16', 'hblo16', 'hbhi16'), cluster_min=30):
    """Bro-cross flips → rich events (#37, docs/bias_mechanics_design.md). Returns dicts
    {t, dir, set, mage, min} — the bias feed (`bro_cross_bias_events`) and the bl_review event overlay
    both derive from this (one computation, two views).

    Requires an ACTUAL crossover (Joe 0626): `sign(m-M)` must CHANGE — the mage crosses UNDER the minion
    (lo-breach → +1 BULL) or OVER it (hi-breach → -1 BEAR) — and the new side then holds `lp_bro_wob`
    consecutive 5s bars (the weave ceased), with both lines OOB on that side. Anchored to the cross
    (`run_len == N`), so the lines merely DROPPING into OOB while the minion already sits on one side
    does NOT fire (the prior bug: it triggered on the OOB-onset without a cross). Aggregate the sets,
    then CLUSTER: keep the FIRST flip per `cluster_min`-min cluster (opposite dir = new cluster fires;
    same dir within the window suppressed). hb16 dropped — too twitchy (Joe 0626). N from
    `lp_config.lp_bro_wob`, OOB from `optimus9_system` (no hardcode). [TODO: per-set active flag in DB.]"""
    N = int(db.execute("SELECT val FROM lp_config WHERE name='lp_bro_wob'", fetch=True)[0]['val'])
    sysr = db.execute('SELECT hi_boundary, lo_boundary FROM optimus9_system', fetch=True)[0]
    HI, LO = float(sysr['hi_boundary']), float(sysr['lo_boundary'])
    ts = W.ts; nb = len(ts)
    def line(name):                                          # route by the line's value_mode (#33)
        r = db.execute("SELECT value_mode FROM vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
        return W._line(name) if (r and r[0]['value_mode'] == 'closed') else W._line_emerging(name)
    raw = []
    for st in sets:
        m = line(st + 'm'); M = line(st + 'M')
        fin = np.isfinite(m) & np.isfinite(M)
        sign = np.where(fin, np.sign(m - M), 0).astype(int)
        chg = np.concatenate([[True], sign[1:] != sign[:-1]])
        idx = np.arange(nb); last_start = np.maximum.accumulate(np.where(chg, idx, -1)); run_len = idx - last_start + 1
        for i in range(N, nb):
            if not fin[i] or run_len[i] != N:             # a cross that held EXACTLY N bars (weave ceased)
                continue
            s = sign[i]
            if s > 0 and m[i] < LO and M[i] < LO:          # mage crossed UNDER minion, both OOB-low → BULL
                raw.append((int(ts[i]), 1, st, float(M[i]), float(m[i])))
            elif s < 0 and m[i] > HI and M[i] > HI:        # mage crossed OVER minion, both OOB-high → BEAR
                raw.append((int(ts[i]), -1, st, float(M[i]), float(m[i])))
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
