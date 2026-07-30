"""rc_window — RC-vs-climb config router off the NATIVE s2-cycle flip tag (Joe 0725). SAVED.

CORRECTION (0725): the RC window is NOT something to nowcast from features — it is already a first-class,
causal engine event. "s2-cycle" is a cycle-GROUP {s1,s2} (rpl_sweep_spec:334; s8-cycle {s3–s8}, HTF {s9+}),
and every `run_chain` flip is tagged `rc` (rpl_walk.py:250 `dict(...,rc=rc,...)`):
  rc=True  -> ROLLERCOASTER flip = s2-cycle counter-trend reversal (gcs5-timed, no pyramid)  == RC window
  rc=False -> CLIMB flip         = s8-cycle trend (s30-timed, pyramid ok)
Lifecycle (rpl_flow_spec:29, Joe's no-timeout rule): the s2-cycle runs until either
  OPEN  = s1/s2 EXHAUSTION (x-cross-pred against dir, r AT boundary -> delegate x×r wob -> gcs5 finisher), or
  CLOSE = an s8-cycle TF (s3–s8) r-preds -> s8 climb takes over (dir_confirm) == ">s2 cycle walked past the
          s2-cycle limit" (exit_tf_floor=4, so takeover effectively starts at s4).
So the router is NATIVE: run the chain, route each flip to its config by `rc`. The s2->s8 baton IS the router —
causal, on-the-fly, zero-leak. No stretch/OOB nowcaster ([[rc-window-realtime]]); that finding is demoted to at
most a downstream FILTER on WHICH rc flips to take (see `filter_hook`), never the routing spine.

Two-config plan (RC r15 + climb r18): run both, RC config governs rc=True flips, climb config governs rc=False.
Deep integration = swap the per-band config mid-chain on the rr_rollercoaster state (held for the engine rework);
this module gives the causal partition + spans so the config sweep can be MEASURED on each flip-subset today.
"""
import optimus9.orchestration.rpl_walk as R


def flip_stream(seed_bias='bear', seed_start=None, end=None, **kw):
    """The native tagged flip chain. -> list of dicts {ts, dir, rc(bool), walk, ev}. Causal (emerging-only)."""
    return R.run_chain(seed_bias=seed_bias, seed_start=seed_start, end=end, persist=False, **kw)


def route(flips):
    """The router: one decision per flip, straight off the s2-cycle tag. -> [(ts, dir, tag)] tag in {'rc','climb'}.
    This is the whole routing spine — the engine already classified the regime; we just read it."""
    return [(f['ts'], f['dir'], 'rc' if f['rc'] else 'climb') for f in flips]


def rc_windows(flips):
    """RC-window SPANS: each rollercoaster flip open -> the NEXT flip's open (when the s2-cycle hands off).
    -> [(start_ts, end_ts, dir)]. The last rc flip runs open-ended (end=None)."""
    out = []
    for k, f in enumerate(flips):
        if f['rc']:
            end = flips[k + 1]['ts'] if k + 1 < len(flips) else None
            out.append((f['ts'], end, f['dir']))
    return out


def partition(flips):
    """Split the chain into the two config-subsets the sweep dials separately. -> (rc_flips, climb_flips)."""
    rc = [f for f in flips if f['rc']]
    cl = [f for f in flips if not f['rc']]
    return rc, cl


def window_density(windows, seed_bias='bear'):
    """Per-window RC-leg FRACTION from the native chain — the selector for split/regime-dense cornering (Joe 0725).
    A leg is a flip-pair (a,b); its regime is a['rc']. -> [(s, e, rc_frac, rc_legs, cl_legs)]. Causal per window."""
    out = []
    for s, e in windows:
        flips = flip_stream(seed_bias, s, e)
        opens = flips[:-1]                                   # each leg is tagged by its opening flip
        rc_legs = sum(1 for a in opens if a['rc']); cl_legs = len(opens) - rc_legs
        legs = max(1, len(opens))
        out.append((s, e, rc_legs / legs, rc_legs, cl_legs))
    return out


def draw_regime_windows(pool, k, seed_bias='bear'):
    """Split a candidate window pool into the RC-objective set (most rc-dense) and climb set (least rc-dense).
    -> (rc_windows, climb_windows), each a list of (s,e). Selection is on TRAINING windows (our choice; not a leak —
    OOS stays disjoint + the live router is the causal native tag). Requires >=2 legs of the target regime to qualify."""
    dens = window_density(pool, seed_bias)
    rc_ok = sorted([d for d in dens if d[3] >= 2], key=lambda d: -d[2])   # most rc-dense first
    cl_ok = sorted([d for d in dens if d[4] >= 2], key=lambda d: d[2])    # least rc-dense (climb-dense) first
    rc_w = [(s, e) for (s, e, f, r, c) in rc_ok[:k]]
    cl_w = [(s, e) for (s, e, f, r, c) in cl_ok[:k]]
    return rc_w, cl_w


def filter_hook(flips, keep=None):
    """OPTIONAL downstream confluence (NOT routing): rank/keep a subset of rc flips. `keep(f)->bool` decides.
    This is the only place the demoted htf_stretch/OOB features could earn a role — grading WHICH rc flips to
    take, per-flip and causal (features read at f['ts']). Default keep=all. Off the routing critical path."""
    if keep is None:
        return flips
    return [f for f in flips if (not f['rc']) or keep(f)]


if __name__ == '__main__':
    # smoke: pull one seeded chain, report the RC/climb split + a few spans. run_chain is heavy (full walk);
    # keep the window small via `end` if needed.
    flips = flip_stream()
    n = len(flips); rc = sum(f['rc'] for f in flips)
    print('flips %d | RC(rollercoaster) %d (%.0f%%) | climb %d' % (n, rc, 100 * rc / max(1, n), n - rc))
    for (s, e, d) in rc_windows(flips)[:5]:
        import datetime as dt
        fs = dt.datetime.utcfromtimestamp(s / 1000).strftime('%m-%d %H:%M')
        fe = dt.datetime.utcfromtimestamp(e / 1000).strftime('%H:%M') if e else 'open'
        print('  RC-window %s -> %s  dir=%s' % (fs, fe, d))
    print('router = native rc tag; RC-config trades rc=True flips, climb-config trades rc=False. Zero-leak.')
