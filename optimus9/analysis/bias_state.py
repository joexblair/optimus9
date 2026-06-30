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


def bl_state_bias_events(db, lines=('s22r',), end_ms=None, lookback_hours=120):
    """bl state-change → direction events [(t_ms, dir)] (#37 bl-state-change, alchemy BRD). Fires on a
    flip TO 1 AND a flip TO 3 of the specified breach line(s) — no LTF lines (they'd poison the bias):
      • flips to 1 (breach starts / prediction-captured) → bias = breach_dir   (MOMENTUM into the breach)
      • flips to 3 (breach completes)                    → bias = -breach_dir  (the REVERSAL)
    So a HI breach reads BULL→BEAR as it matures 1→3; a LO breach BEAR→BULL. The to-1 half overrides
    errant pk that fights the established trend; a 3→1 re-engage emits a fresh to-1 (momentum). Most-
    recent-wins in BiasState (no weighting yet — #40)."""
    ph = ','.join(['%s'] * len(lines))
    rows = db.execute(
        f'''SELECT line_name, bar_time, state, breach_dir FROM bl_states
            WHERE line_name IN ({ph}) ORDER BY line_name, bar_time''', tuple(lines), fetch=True)
    start = (end_ms - lookback_hours * 3600 * 1000) if end_ms else None
    out, prev = [], {}
    for r in rows:
        ln, st, bd = r['line_name'], int(r['state']), int(r['breach_dir'])
        t = int(r['bar_time'].replace(tzinfo=timezone.utc).timestamp() * 1000)
        if (end_ms is None or start <= t < end_ms) and bd != 0:
            if st == 1 and prev.get(ln) != 1:
                out.append((t, bd))                          # to-1: momentum (LO→bear, HI→bull)
            elif st == 3 and prev.get(ln) != 3:
                out.append((t, -bd))                         # to-3: reversal (LO→bull, HI→bear)
        prev[ln] = st
    return out


def pk_bias_events(W):
    """Bias machine pk updates → direction events [(t_ms, dir)]: BULL → +1, BEAR → -1."""
    m = {'BULL': 1, 'BEAR': -1}
    return [(int(u['t']), m[u['call']]) for u in W.signals() if u['call'] in m]


def bro_cross_events(db, W, sets):
    """Per-set cross SIGNAL streams (#37) — ONE computation, reused by every verdict. For each set:
    {set, ts, m, M, sign, run_len, fin} where sign=sign(m-M) and run_len = how many consecutive bars
    the current side has held. Pure event-construction (no hold/OOB verdict) — `bro_cross_flips` and
    debug probes both consume THIS instead of re-deriving the cross, so the cross lives in one place.
    value_mode-routed per line (#33)."""
    ts = W.ts; nb = len(ts)
    def line(name):
        r = db.execute("SELECT value_mode FROM vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
        return W._line(name) if (r and r[0]['value_mode'] == 'closed') else W._line_emerging(name)
    streams = []
    for st in sets:
        m = line(st + 'm'); M = line(st + 'M')
        fin = np.isfinite(m) & np.isfinite(M)
        sign = np.where(fin, np.sign(m - M), 0).astype(int)
        chg = np.concatenate([[True], sign[1:] != sign[:-1]])
        idx = np.arange(nb); last_start = np.maximum.accumulate(np.where(chg, idx, -1)); run_len = idx - last_start + 1
        streams.append({'set': st, 'ts': ts, 'm': m, 'M': M, 'sign': sign, 'run_len': run_len, 'fin': fin})
    return streams


def bro_cross_flips(db, W, sets=('hbhl16', 'hblo16', 'hbhi16'), cluster_min=30, N=None):
    """Bro-cross flips → rich events (#37, docs/bias_mechanics_design.md). The VERDICT over
    `bro_cross_events`. Returns {t, dir, set, mage, min} — the bias feed (`bro_cross_bias_events`)
    and the bl_review overlay both derive from this (one computation, two views).

    Requires an ACTUAL crossover (Joe 0626): `sign(m-M)` CHANGES — mage crosses UNDER minion
    (lo-breach → +1 BULL) or OVER it (hi-breach → -1 BEAR) — and the new side holds `N` consecutive 5s
    bars (the weave ceased), with both lines OOB on that side. Anchored to `run_len == N`, so a line
    merely DROPPING into OOB while the minion already sits one side does NOT fire. Aggregate the sets,
    then CLUSTER: first flip per `cluster_min`-min cluster (opposite dir = new cluster; same dir
    suppressed). `N` is the wobble/sustain tolerance — defaults to `lp_config.lp_bro_wob`; pass N to
    test (N=1 = fire on the cross itself). OOB from `optimus9_system` (no hardcode).
    [TODO: per-set active flag in DB; sets are still a default arg.]"""
    if N is None:
        N = int(db.execute("SELECT val FROM lp_config WHERE name='lp_bro_wob'", fetch=True)[0]['val'])
    sysr = db.execute('SELECT hi_boundary, lo_boundary FROM optimus9_system', fetch=True)[0]
    HI, LO = float(sysr['hi_boundary']), float(sysr['lo_boundary'])
    raw = []
    for s in bro_cross_events(db, W, sets):
        ts, m, M, sign, run_len, fin, st = s['ts'], s['m'], s['M'], s['sign'], s['run_len'], s['fin'], s['set']
        for i in range(N, len(ts)):
            if not fin[i] or run_len[i] != N:             # a cross that held EXACTLY N bars (weave ceased)
                continue
            sgn = sign[i]
            if sgn > 0 and m[i] < LO and M[i] < LO:         # mage crossed UNDER minion, both OOB-low → BULL
                raw.append((int(ts[i]), 1, st, float(M[i]), float(m[i])))
            elif sgn < 0 and m[i] > HI and M[i] > HI:       # mage crossed OVER minion, both OOB-high → BEAR
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
