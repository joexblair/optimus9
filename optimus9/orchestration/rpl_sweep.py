"""rpl knob sweep — flip-to-flip leg MAE/MFE, minimax over windows, branching on centroids.

Metric (Joe 0721): the chain IS the trade — each flip closes and opens the opposite. A leg = flip_i -> flip_{i+1};
MFE = best favourable excursion in flip_i's direction, MAE = worst adverse (px_smooth). Objective = median(MFE-MAE)
per window, MINIMAX (worst window) over N windows spread across the tape — sweep to push the worst window's edge up.

Cheap knobs only (module globals read at call time; monkeypatched, no cache rebuild). Fence/tf_ceiling/line-configs
need an L0 rebuild -> separate phase. Branching: sweep each knob solo -> rank by delta -> refine the top-3 combined
-> adopt best as new baseline -> recurse. Logs to rpl_sweep.log. Run: python3 -m optimus9.orchestration.rpl_sweep
"""
import sys, time, itertools, numpy as np
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.breaching_line import predict_breach
from optimus9.compute.swing_detect import find_pivots   # canonical swing producer (jig.score.swings calls this)

SWING_PCT = 0.5   # metric yardstick (Joe 0721): covers the smallest rollercoaster. Measured RC-leg knee: [0.4,0.5) empty,
                  # [0.5,0.6) holds 8 RC legs, sub-0.4% = 11 degenerate micro-RCs (min 0.142%). 0.5% = covers down to the knee.

DAY = 24 * 3600 * 1000
WINDOWS = [(int(R.end_ms - off * DAY), int(R.end_ms - off * DAY + 1.5 * DAY)) for off in [2 + 1.5 * i for i in range(20)]]  # 20 x 1.5d tiling ~30 days
# --- Class A: cheap knobs (module globals read at call time; monkeypatch, no recompute) ---
KNOB_ATTR = {  # config-key -> rpl_walk module attribute
    'finisher_s1r_boundary_slip': 'FIN_S1R_SLIP', 'finisher_s30r_boundary_slip': 'FIN_S30R_SLIP',
    'finisher_s30r_near_dwell': 'FIN_NEAR_DWELL', 'latch_depth': 'LATCH_DEPTH', 'latch_dwell': 'LATCH_DWELL',
    'exit_tf_floor': 'EXIT_TF_FLOOR', 'delegate_offset': 'DELOFF', 'xcp_tf_floor': 'FLOOR',
    'xcp_bnd_offset': 'BND4',   # gcs5_r_tol DROPPED (dead knob: never read since gcs5 finisher went pure-latch)
}
KNOB_VALS = {
    'finisher_s1r_boundary_slip': [15, 20, 25, 30, 35], 'finisher_s30r_boundary_slip': [2, 3, 4, 6, 8],
    'finisher_s30r_near_dwell': [1, 2, 3, 4], 'latch_depth': [3, 4, 5, 6, 8], 'latch_dwell': [1, 2, 3],
    'exit_tf_floor': [3, 4, 5, 6, 8], 'delegate_offset': [3, 4, 5, 6, 7],
    'xcp_tf_floor': [12, 15, 19, 24, 30], 'xcp_bnd_offset': [2, 3, 4, 6, 8],   # x-cross-pred near-boundary threshold
}
# --- Class B: boundary/fence (feed predict_breach -> baked into L0['P']; recompute P, no jig rebuild) ---
BND_ATTR = {'hi_bound': 'HI', 'lo_bound': 'LO', 'fence_hi': 'FH', 'fence_lo': 'FL'}
BND_VALS = {'hi_bound': [83, 84, 85, 86, 87], 'lo_bound': [13, 14, 15, 16, 17],
            'fence_hi': [60, 62, 65, 68, 70], 'fence_lo': [30, 32, 35, 38, 40]}
ALL_ATTR = {**KNOB_ATTR, **BND_ATTR}
ALL_VALS = {**KNOB_VALS, **BND_VALS}
BASE = {k: getattr(R, a) for k, a in ALL_ATTR.items()}
ORIG_P, ORIG_PS30 = R.L0['P'], R.L0['Ps30']   # pristine baked P; restore after any Class-B recompute
EI = R.L0['ei']; ETS = R.L0['ts'][EI]; EPX = R.L0['pxs'][EI]   # event-bar px_smooth (Joe: EVERYTHING runs on px_smooth events, not the ffilled index tape)
LOG = open('/home/joe/thecodes/rpl_sweep.log', 'a', buffering=1)
def log(m): print(m); LOG.write(m + '\n')

# --- GPU-batched P recompute (Class-B): resident f64 TF-stacks on the card; predict_breach batches over (90,N) ---
try:
    import cupy as _cp
    _GR  = _cp.asarray(np.stack([R.L0['E'][tf]['r'] for tf in R.TFS]))   # f64 -> bit-identical to CPU (no f32 boundary flips)
    _GM  = _cp.asarray(np.stack([R.L0['E'][tf]['m'] for tf in R.TFS]))
    _GMM = _cp.asarray(np.stack([R.L0['E'][tf]['M'] for tf in R.TFS]))
    _GS  = (_cp.asarray(R.L0['s30r_']), _cp.asarray(R.L0['s30m_']), _cp.asarray(R.L0['s30M_']))
    _GPU = True
except Exception:
    _GPU = False

def _recompute_P():
    """Rebuild L0['P'] + Ps30 from current R.HI/LO/FH/FL into a FRESH dict (never mutates ORIG_P).
    GPU-batched when available (f64, bit-identical); any cupy error falls back to the CPU loop so the campaign survives."""
    if _GPU:
        try:
            Ph = _cp.asnumpy(predict_breach(_GR, _GM, _GMM, R.HI, R.LO, R.FH, R.FL, 0.0))
            R.L0['P'] = {tf: Ph[i] for i, tf in enumerate(R.TFS)}
            R.L0['Ps30'] = _cp.asnumpy(predict_breach(*_GS, R.HI, R.LO, R.FH, R.FL, 0.0))
            return
        except Exception:
            _cp.get_default_memory_pool().free_all_blocks()
    E = R.L0['E']
    R.L0['P'] = {TF: predict_breach(E[TF]['r'], E[TF]['m'], E[TF]['M'], R.HI, R.LO, R.FH, R.FL, 0.0) for TF in R.TFS}
    R.L0['Ps30'] = predict_breach(R.L0['s30r_'], R.L0['s30m_'], R.L0['s30M_'], R.HI, R.LO, R.FH, R.FL, 0.0)

def _leg_net(flips, ts, pxs):
    """Per flip->flip leg: MFE/MAE via swing_detect (Joe 0721). find_pivots at SWING_PCT confirms only >=1.5%
    reversals and anchors at entry (ep is always a pivot -> mfe/mae >= 0). MFE = furthest favourable pivot in
    the leg's direction, MAE = furthest adverse. A leg with no >=1.5% swing yields no pivots -> scores 0 (noise)."""
    nets = []
    for a, b in zip(flips, flips[1:]):
        i = int(np.searchsorted(ts, a['ts'])); j = int(np.searchsorted(ts, b['ts'])); seg = pxs[i:j + 1]; ep = pxs[i]
        if len(seg) < 2 or ep <= 0 or not np.isfinite(ep): continue
        piv = find_pivots(seg, SWING_PCT)
        if not piv: nets.append(0.0); continue                      # no >=1.5% swing -> noise leg
        pv = np.array([seg[p[0]] for p in piv], float); hi = np.nanmax(pv); lo = np.nanmin(pv)
        if a['dir'] == 'bull': mfe = (hi - ep) / ep * 100; mae = (ep - lo) / ep * 100
        else: mfe = (ep - lo) / ep * 100; mae = (hi - ep) / ep * 100
        nets.append(mfe - mae)
    return nets

SCAN = WINDOWS[::2]   # 10-window subset (still spans 30d) for cheap solo-dial RANKING; adoption re-scores on full 20

def score(overrides, windows=WINDOWS):
    """Set knobs, run each window, return (minimax_net, per_window_nets). Restores knobs (+ P) after.
    Class-B knobs (boundary/fence) trigger an in-place P recompute; ORIG_P is restored in finally."""
    for k, v in overrides.items(): setattr(R, ALL_ATTR[k], v)
    touched_bnd = any(k in BND_ATTR for k in overrides)
    if touched_bnd: _recompute_P()
    wins = []
    try:
        for s, e in windows:
            flips = R.run_chain('bear', s, persist=False, end=e)
            nets = _leg_net(flips, ETS, EPX)          # event-bar px_smooth only
            wins.append(float(np.median(nets)) if len(nets) >= 4 else float('nan'))
    finally:
        for k, a in ALL_ATTR.items(): setattr(R, a, BASE[k])
        if touched_bnd: R.L0['P'], R.L0['Ps30'] = ORIG_P, ORIG_PS30
    valid = [w for w in wins if np.isfinite(w)]
    return (min(valid) if valid else float('-inf')), wins

def sweep_group(cur, base_mm, vals, tag):
    """One branching round over the knobs in `vals`: solo-dial each, rank by delta, lean-refine by stacking
    the top-1/2/3 best values, adopt the best combo. Returns (cur, base_mm, improved)."""
    log(f'\n--- {tag} (baseline minimax {base_mm:+.3f}%) ---')
    scan_base, _ = score(cur, SCAN)   # subset baseline to rank solo dials against (same window set)
    deltas = []
    for k in vals:
        best_v, best_mm = cur[k], scan_base
        for v in vals[k]:
            if v == cur[k]: continue
            mm, _ = score({**cur, k: v}, SCAN)
            log(f'  {k}={v}: scan {mm:+.3f}%')
            if mm > best_mm: best_mm, best_v = mm, v
        deltas.append((best_mm - scan_base, k, best_v, best_mm))
    deltas.sort(reverse=True)
    log(f'  top single-dial scan gains: {[(k,v,round(mm,3)) for d,k,v,mm in deltas[:5] if d>0]}')
    top_gain, top_knob = (deltas[0][0], deltas[0][1]) if deltas else (0.0, None)   # biggest solo scan mover
    top = [(k, v) for d, k, v, mm in deltas if d > 0]
    if not top:
        log('  no single-dial improvement'); return cur, base_mm, False, top_gain, top_knob
    best_combo, best_combo_mm = dict(cur), base_mm
    for n in (1, 2, 3):
        if n > len(top): break
        cand = {**cur, **dict(top[:n])}
        mm, _ = score(cand)
        log(f'  stack top-{n} {dict(top[:n])}: minimax {mm:+.3f}%')
        if mm > best_combo_mm: best_combo_mm, best_combo = mm, cand
    if best_combo_mm > base_mm + 1e-6:
        cur, base_mm = best_combo, best_combo_mm
        log(f'  ADOPT {tag}: { {k: cur[k] for k in ALL_VALS if cur[k] != BASE[k]} }  minimax {base_mm:+.3f}%')
        return cur, base_mm, True, top_gain, top_knob
    log('  refine gave no gain over baseline -> hold'); return cur, base_mm, False, top_gain, top_knob

def main():
    log('\n===== rpl sweep ' + time.strftime('%Y-%m-%d %H:%M') + ' =====')
    log('windows: ' + str([R.fmt(s) + '..' + R.fmt(e) for s, e in WINDOWS]))
    cur = dict(BASE)
    base_mm, base_w = score(cur)
    log(f'baseline knobs {cur}\n  minimax net {base_mm:+.3f}%  windows {[round(w,3) for w in base_w]}')
    # Campaign (Joe 0721): repeat macro-cycles until EVERY knob stops changing. Each cycle:
    #   (1) two generations of cheap-knob refinement,
    #   (2) a FRESH dedicated hi/lo+fence sweep merged back (big lever, re-swept vs the new baseline),
    #   (3) a FRESH dedicated pass for any DISCOVERED big mover (solo scan gain >= BIG_MOVER) - same treatment as hi/lo,
    #   (4) a combined next-level pass over all knobs.
    # Converges when a full cycle adopts nothing.
    BIG_MOVER = 0.15   # minimax %-points on a solo scan that promotes a knob to dedicated fresh re-sweeps
    movers = set()
    for cyc in range(1, 9):
        imp = False
        for g in (1, 2):
            cur, base_mm, i, gain, mk = sweep_group(cur, base_mm, KNOB_VALS, f'cyc{cyc} gen{g} [cheap knobs]'); imp |= i
            if gain >= BIG_MOVER and mk and mk not in movers and mk not in BND_VALS:
                movers.add(mk); log(f'  >> NEW big mover: {mk} (+{gain:.3f}% solo) -> dedicated fresh re-sweeps henceforth')
        cur, base_mm, ib, _, _ = sweep_group(cur, base_mm, BND_VALS, f'cyc{cyc} [FRESH hi/lo+fence]'); imp |= ib
        for mk in sorted(movers):
            cur, base_mm, im, _, _ = sweep_group(cur, base_mm, {mk: ALL_VALS[mk]}, f'cyc{cyc} [FRESH mover {mk}]'); imp |= im
        cur, base_mm, ic, gain, mk = sweep_group(cur, base_mm, ALL_VALS, f'cyc{cyc} [combined next-level]'); imp |= ic
        if gain >= BIG_MOVER and mk and mk not in movers and mk not in BND_VALS:
            movers.add(mk); log(f'  >> NEW big mover: {mk} (+{gain:.3f}% solo) -> dedicated fresh re-sweeps henceforth')
        log(f'\n== end macro-cycle {cyc}: minimax {base_mm:+.3f}%  movers={sorted(movers)}  drift { {k: cur[k] for k in ALL_VALS if cur[k] != BASE[k]} } ==')
        if not imp:
            log('  full macro-cycle, no knob changed -> CONVERGED'); break
    log(f'\n===== FINAL: minimax {base_mm:+.3f}%  knobs {cur} =====')

if __name__ == '__main__':
    main()
