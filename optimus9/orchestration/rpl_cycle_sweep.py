"""Cycle-group line-config sweep (Joe 0721). Splits the shared r/m/M/x line configs into three bands — s2-cycle
{s1,s2}, s8-cycle {s3-s8}, HTF {s9+} — and dials each out independently, plus the band edges (s2_top, s8_top).

Built on the per-line cache (cache_jig_perline): each config combo changes only some lines' specs, so a rebuild
touches only the changed lines. Scoring reuses the pooled flip-leg metric via an L0 swap — the tape (ts/evt/pxs)
is line-config-invariant, so PS.ETS/EPX stay valid and only R.L0's lines/P/fx change.

Iterative (Joe): sweep the per-group configs, then the band edges; if an edge moves, resweep the configs.
Run AFTER the pooled sweep frees the CPU (first call populates the full per-line cache, ~4.6 min).
"""
import time, numpy as np
import optimus9.orchestration.rpl_walk as R
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration import rpl_sweep as PS   # reuse WINDOWS / SCAN / score / _leg_net / log

GROUPS = ('s2', 's8', 'htf')
# baseline per-group configs = the current shared LN (all three bands identical => reproduces the default _ovr)
BASE_CFG = {g: {k: dict(R.LN[k]) for k in ('r', 'x', 'm', 'M')} for g in GROUPS}
BASE_EDGE = {'s2_top': 2, 's8_top': 8}
# per-param small-step ranges (branch one param at a time, per band)
RANGE = {
    'r': {'k_len': [5, 7, 9], 'rsi': [4, 5, 6], 'stc': [9, 11, 13]},
    'x': {'length': [4, 5, 6], 'mult': [0.30, 0.37, 0.44]},
    'm': {'length': [5, 6, 8], 'mult': [0.38, 0.45, 0.52]},
    'M': {'length': [30, 37, 44], 'mult': [0.75, 0.83, 0.91]},
}
EDGE_RANGE = {'s2_top': [1, 2, 3], 's8_top': [6, 8, 10, 12]}

def _band(TF, s2_top, s8_top):
    return 's2' if TF <= s2_top else ('s8' if TF <= s8_top else 'htf')

def group_ovr(cfg, s2_top, s8_top):
    """Full _ovr with per-band r/m/M/x configs; non-TF lines (s1x/s1m/s30/gcs5) stay at their defaults."""
    ovr = {}
    for TF in R.TFS:
        g = _band(TF, s2_top, s8_top)
        for k in ('r', 'x', 'm', 'M'): ovr.update(R._mk(f'{k}{TF}', TF, cfg[g][k]))
    for nm in ('s1x', 's1m'): ovr.update(R._mk(nm, 1.0, R.LN[nm]))
    for nm in ('s30r', 's30M'): ovr.update(R._mk(nm, 0.5, R.LN[nm]))
    ovr.update(R._mk('s30x', 0.5, R.LN['x'])); ovr.update(R._mk('s30m', 0.5, R.LN['m']))
    g5 = 5.0 / 60.0
    ovr.update(R._mk('gcs5r', g5, R.LN['r'])); ovr.update(R._mk('gcs5m', g5, R.LN['m'])); ovr.update(R._mk('gcs5x', g5, R.LN['x']))
    return ovr

def score_cfg(cfg, s2_top, s8_top, windows=None):
    """Build L0 for this per-group config (per-line cache), swap it into R.L0, score with the pooled metric, restore."""
    ovr = group_ovr(cfg, s2_top, s8_top)
    jc = cache_jig_perline(R.end_ms, 40, 600, ovr, pxs_cfg=R.PXS_CFG)
    L0_old = R.L0
    R.L0 = R.build_lines(jc)
    try:
        return PS.score({}, windows if windows is not None else PS.WINDOWS)
    finally:
        R.L0 = L0_old

def _clone(cfg):
    return {g: {k: dict(cfg[g][k]) for k in cfg[g]} for g in cfg}

def sweep():
    PS.log('\n===== cycle-group line sweep ' + time.strftime('%Y-%m-%d %H:%M') + ' =====')
    cfg = _clone(BASE_CFG); edge = dict(BASE_EDGE)
    base_mm, base_w = score_cfg(cfg, edge['s2_top'], edge['s8_top'])
    PS.log(f'baseline (all bands = default LN, edges {edge}) minimax {base_mm:+.3f}%  windows {[round(w,3) for w in base_w]}')
    for macro in range(1, 4):
        improved = False
        # 1) per-band, per-line, per-param branch (scan on subset, confirm on full)
        for g in GROUPS:
            for k in ('r', 'x', 'm', 'M'):
                for param, vals in RANGE[k].items():
                    cur = cfg[g][k].get(param); best_v, best_mm = cur, base_mm
                    for v in vals:
                        if v == cur: continue
                        trial = _clone(cfg); trial[g][k][param] = v
                        mm, _ = score_cfg(trial, edge['s2_top'], edge['s8_top'], PS.SCAN)
                        PS.log(f'  m{macro} {g}.{k}.{param}={v}: scan {mm:+.3f}%')
                        if mm > best_mm: best_mm, best_v = mm, v
                    if best_v != cur:
                        trial = _clone(cfg); trial[g][k][param] = best_v
                        mm, _ = score_cfg(trial, edge['s2_top'], edge['s8_top'])   # confirm on full
                        if mm > base_mm + 1e-6:
                            cfg, base_mm, improved = trial, mm, True
                            PS.log(f'  ADOPT {g}.{k}.{param}={best_v}  minimax {base_mm:+.3f}%')
        # 2) band edges — if one moves, the loop re-enters and resweeps configs against the new perimeter
        for e, vals in EDGE_RANGE.items():
            cur = edge[e]; best_v, best_mm = cur, base_mm
            for v in vals:
                if v == cur: continue
                te = dict(edge); te[e] = v
                if te['s2_top'] >= te['s8_top']: continue
                mm, _ = score_cfg(cfg, te['s2_top'], te['s8_top'], PS.SCAN)
                PS.log(f'  m{macro} edge {e}={v}: scan {mm:+.3f}%')
                if mm > best_mm: best_mm, best_v = mm, v
            if best_v != cur:
                te = dict(edge); te[e] = best_v
                mm, _ = score_cfg(cfg, te['s2_top'], te['s8_top'])
                if mm > base_mm + 1e-6:
                    edge, base_mm, improved = te, mm, True
                    PS.log(f'  ADOPT edge {e}={best_v} (resweep configs next macro)  minimax {base_mm:+.3f}%')
        PS.log(f'\n== end macro {macro}: minimax {base_mm:+.3f}%  edges {edge} ==')
        if not improved:
            PS.log('  no change -> converged'); break
    PS.log(f'\n===== CYCLE-GROUP FINAL minimax {base_mm:+.3f}%  edges {edge} =====')
    PS.log('  drift: ' + str({g: {k: {p: cfg[g][k][p] for p in RANGE[k] if cfg[g][k].get(p) != BASE_CFG[g][k].get(p)} for k in ('r', 'x', 'm', 'M') if any(cfg[g][k].get(p) != BASE_CFG[g][k].get(p) for p in RANGE[k])} for g in GROUPS}))

if __name__ == '__main__':
    sweep()
