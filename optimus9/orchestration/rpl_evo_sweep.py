"""Evolutionary parallel sweep (Joe 0721). Honing the harness toward:
  - windows are UNIVERSAL: each sweep round randomly draws 11 x 24h windows from the last 2 months.
  - knob-SUBSETS (tight ranges, e.g. [3,4,5]) are the parallel unit; grouped in 3s, each group swept concurrently.
  - each group runs a branch-descent (perturb one param at a time from the seeded centroids) on the round's windows,
    keeps its TOP-3 configs by fitness ("centroids").
  - all groups' top-3 -> re-seeded into fresh groups; repeat until EVERY knob is unchanged for 2 more rounds.
  - the last 2 rounds (after knobs stop moving) re-score the semi-final configs on 30-day windows.
  - every group's top-3 centroids + their MFE/MAE evidence are written to the `rpl_evo` DB table (Joe's verification lens).

CPU-only + fork-based Pool: CUDA contexts don't survive fork, and workers inherit L0 copy-on-write. Config = flat
dict of knob keys (call-time, cheap) + optional line keys 'band.line.param' (L0 rebuild via the per-line cache).
Fitness = median(MFE-MAE) per window, MINIMAX over the round's windows; MFE/MAE stored as the selection evidence.
"""
import os, json, time, itertools
import numpy as np
from multiprocessing import get_context
import optimus9.orchestration.rpl_walk as R
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.compute.swing_detect import find_pivots
from optimus9.compute.breaching_line import predict_breach
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

DAY = 24 * 3600 * 1000
SWING_PCT = 0.5
OBJECTIVE = 'rc'    # 'rc' = corner the config for ROLLERCOASTER mechanics (score RC legs); 'climb' = RPL/climb mechanics.
                    # Joe 0722: corner TWO config sets, one per mechanic family. Set by run(); inherited by forked workers.
N_WINDOWS = 11                              # universal per round
WIN_HOURS = 24
POOL_DAYS = 48                              # draw from the last ~2 months (capped to the 51.7-day tape + warmup room)
FINAL_DAYS = 30                             # semi-final validation window length
KNOB_ATTR = {  # call-time knobs
    'finisher_s1r_boundary_slip': 'FIN_S1R_SLIP', 'finisher_s30r_boundary_slip': 'FIN_S30R_SLIP',
    'finisher_s30r_near_dwell': 'FIN_NEAR_DWELL', 'latch_depth': 'LATCH_DEPTH', 'latch_dwell': 'LATCH_DWELL',
    'exit_tf_floor': 'EXIT_TF_FLOOR', 'delegate_offset': 'DELOFF', 'xcp_tf_floor': 'FLOOR', 'xcp_bnd_offset': 'BND4',
    'hi_bound': 'HI', 'lo_bound': 'LO', 'fence_hi': 'FH', 'fence_lo': 'FL',
    'wob_n': 'WOBN', 'anti': 'ANTI', 'delegate_tf_floor': 'DELFLOOR',   # wired chain knobs (0721: all-in)
}
BND_KEYS = {'hi_bound', 'lo_bound', 'fence_hi', 'fence_lo'}   # need a P recompute
# tight per-knob ranges = the "subsets"
SUBSETS = {
    'finisher_s1r_boundary_slip': [20, 25, 30], 'finisher_s30r_boundary_slip': [3, 4, 5],
    'finisher_s30r_near_dwell': [1, 2, 3], 'latch_depth': [4, 5, 6], 'latch_dwell': [1, 2, 3],
    'exit_tf_floor': [3, 4, 5], 'delegate_offset': [4, 5, 6], 'xcp_tf_floor': [10, 12, 14],
    'xcp_bnd_offset': [3, 4, 5], 'lo_bound': [14, 15, 16],     # HI derived = 100-LO (symmetric boundary pair, Joe 0722)
    'fence_lo': [33, 35, 37],                                  # FH derived = 100-FL (symmetric fence pair)
    'wob_n': [7, 9, 11], 'anti': [45, 50, 55], 'delegate_tf_floor': [1, 2, 3],
}
BASE_CONFIG = {k: getattr(R, a) for k, a in KNOB_ATTR.items()}
# Warm-start seed (Joe 0722): the r7 config from the prior run — a decent starting point for the elitist hill-climb.
# BASE_CONFIG stays the drift reference; every value here is inside its subset range so the val-gate can revert it.
SEED_OVERRIDES = {'lo_bound': 14, 'exit_tf_floor': 3, 'xcp_bnd_offset': 3,
                  's2.r.stc': 9, 'htf.r.k_len': 9, 's2.x.length': 4, 'htf.x.length': 4}
DEFAULT_SUBSETS = SUBSETS                     # seed source; the live subset ranges are READ FROM THE DB (rpl_knob_subset)
# per-band line params (config key 'band.line.param'); each triggers an L0 rebuild via the per-line cache.
# TIGHT ranges (Joe 0722): step=1 for lengths/counts, 0.02 for multipliers, each CENTERED on the current best value
# (the r7 seed value where one exists, else the baseline) — fine local search, not a wide grid.
_LNTOK = {'r': 'r', 'x': 'x', 'm': 'mn', 'M': 'mj'}   # config-key token per line (mn/mj avoid the m/M case collision
_LNMAP = {v: k for k, v in _LNTOK.items()}             # MySQL ks_knob is case-insensitive); mapped back in _build_line_L0
_BASE_LINE = {'r': {'k_len': 7, 'rsi': 5, 'stc': 11}, 'x': {'length': 5, 'mult': 0.37},   # baseline centers (rpl_seed_baseline)
              'm': {'length': 6, 'mult': 0.45}, 'M': {'length': 37, 'mult': 0.83}}
def _tight(center, param):
    if param == 'mult': return [round(center - 0.02, 2), round(center, 2), round(center + 0.02, 2)]  # step 0.02
    return [center - 1, center, center + 1]                                                          # step 1 (counts)
for _b in ('s2', 's8', 'htf'):
    for _ln in ('r', 'x', 'm', 'M'):
        for _p, _base in _BASE_LINE[_ln].items():
            _key = f'{_b}.{_LNTOK[_ln]}.{_p}'
            DEFAULT_SUBSETS[_key] = _tight(SEED_OVERRIDES.get(_key, _base), _p)   # center on r7 seed value if present
DEFAULT_SUBSETS['s2_top'] = [1, 2, 3]; DEFAULT_SUBSETS['s8_top'] = [6, 8, 10]   # band-edge perimeters
SUBSETS = {}                                  # populated from DB in run(), inherited by forked workers

# ---------- windows ----------
# FIXED low-variance panel (Joe 0722): deterministic + spans the tape, so fitness is comparable across rounds and
# elitism can guarantee monotonic improvement. Random 11-window draws had net-variance ~0.5 on a FIXED config
# (measured) which swamped the config signal — the search was chasing draws. 32 windows drops that noise floor.
N_PANEL = 32
PANEL = [(int(R.end_ms - off * DAY), int(R.end_ms - off * DAY + WIN_HOURS * 3600 * 1000)) for off in [2 + 1.4 * i for i in range(N_PANEL)]]
# COARSE-TO-FINE (Joe 0722): early rounds sweep a small STATIC 12-window subset (spans the tape) for fast, reliable coarse
# tuning; then widen to the full 32-window PANEL for precise refinement. Both are fixed/deterministic — elitism stays valid
# WITHIN each phase, and the elite is re-baselined on the new panel at the switch (monotonicity is per-phase, logged).
COARSE_IDX = sorted({int(round(i * (N_PANEL - 1) / 11)) for i in range(12)})   # 12 windows evenly spanning the tape
COARSE = [PANEL[i] for i in COARSE_IDX]

# ---------- §5.3 AUTO-MANAGING LOOP (Joe 0723): hunt the agnostic IS/OOS config ----------
# Each CYCLE draws a FRESH random-day training window and FREEZES it for the whole cycle (elitism stays valid — the
# original design broke because it re-drew EVERY ROUND, making fitness non-comparable). Between cycles the ground
# changes, so the search cannot overfit any single window; it must find the config whose IS and OOS nets are IN SYNC.
IS_DAYS = 14                 # fresh random 24h days per training window. 8 -> 14 (Joe 0723): at 8 days HALF the IS/OOS gap
#                              was already present AT BASELINE (0.419 before any cornering) and half was cornering-induced
#                              (0.830 by r3). A bigger sample attacks both. Also a DIAGNOSTIC: if 14 still gaps ~0.8 the
#                              divergence is STRUCTURAL (missing confluences), not overfit — which is the more useful finding.
SYNC_TOL = 0.15              # MANUAL, tune freely (Joe: "I picked the number from nowhere"). |IS-OOS| net <= this = IN SYNC
MIN_OOS_NET = 0.0            # Joe 0723: "the 0.15 tolerance can't be applied to a negative net". A config at IS -0.50 /
#                              OOS -0.50 has gap 0.00 and would otherwise be called IN SYNC — even AGNOSTIC — while being
#                              consistently LOSING. In-sync and worth-having are orthogonal, so OOS net must clear this
#                              floor before the gap test means anything. Tunable (raise it to demand real edge, not just >0).
MAX_CYCLES = 12              # safety bound on fresh-window cycles
OOS_REGRESS_FLOOR = 0.02     # Joe 0724: 2-ADOPTION OOS-regression bail. OOS moves only on adoption (IS-net advance); two
#                              consecutive adoptions that each drop OOS by more than this floor = the over-corner turning toxic
#                              (a config that WAS good giving OOS back). Bank the peak-OOS config, draw a fresh window. Floor keeps
#                              two noise-sized down-ticks on the jittery 10-day block from firing; armed only when the peak was
#                              PROFITABLE (a never-good config regressing is the imbalanced/mined-out path, not this one).
MAX_OOS_STALL = 3            # Joe 0726: OOS-STALL bail — 3 rounds with NO OOS·10d change is the ABSOLUTE MAX. The 'oos_unprofitable'
#                              checkpoint verdict was LOG-ONLY (no branch action even with AUTO_BRANCH on), so an over-fit whose OOS
#                              flatlines while TRAIN corners was structurally un-exitable except by grinding out PATIENCE. This is its
#                              ACTION: when OOS·10d holds the same value (within OOS_STALL_EPS) for MAX_OOS_STALL rounds AND the config
#                              is NOT in-sync (OOS<=MIN_OOS_NET or gap>SYNC_TOL), the window is mined out — bank peak-OOS (if profitable),
#                              draw fresh. Realtime-honest: don't keep trading a config whose flat wide gap says it won't generalise.
OOS_STALL_EPS = 0.02         # "no change" tolerance on OOS·10d (matches OOS_REGRESS_FLOOR — a noise-sized tick is not a change)
# ROTATING-DRIVER + PARETO VETO (Joe 0726): the train-only descent over-fit deterministically (5 cycles, one keeper). Replace
# it with a 3-read round-robin: round-N dials one of {oos10, train, oos7}; a candidate is ADOPTED only if it improves the
# driver AND regresses NO read past VETO_EPS (Pareto gate). A veto-failed knob is TABU'd for TABU_K rounds so the descent
# can't re-propose the same over-fit corner. A full rotation with no adoption = mined out (bail). Bank on MAXIMIN (best
# worst-read), never the peak of one read — that's what banked the VAL-overfit r12 over the wide-good r5.
ROT = ('o10', 'train', 'o7')  # round-robin adoption driver, one per round
VETO_EPS = 0.02              # a move may not regress any OTHER read by more than this
TABU_K = 3                   # rounds a knob is fenced after a veto-fail
OOS7_DAYS = 7               # oos7 = 7 random days, disjoint from train + oos10 — a CLEAN confirm read (replaces contaminated oos32)
FAILSCAN_RAM_GB = 8.0        # Joe 0723/0724: refresh the full-tape failscan, RAM-GATED (avail>=this). The failscan needs ~3GB and
#                              the cheap phase peaks ~15-18GB with 5 concurrent L0s, so a measured `avail` gate beats a round/phase
#                              proxy. Asymmetry keeps it strict: a stale snapshot is minor, an OOM loses the run.
#                              ⚠ 0724 CORRECTION: the original rule fired the gated check ONLY at phase-convergence and skipped-till-
#                              next-convergence on failure. That assumed "convergence = low-RAM (no pool up)" — but empirically it's
#                              the OPPOSITE: the dying cycle's pool + the fresh cycle spinning up keep RAM tight at EVERY convergence,
#                              so the gate never passed and the snapshot froze for 3 cycles. TRIGGER (staleness) is now DECOUPLED from
#                              EXECUTION (RAM-clear): convergence sets a PENDING flag (_fs_dirty) and the top of every round retries it
#                              until RAM clears (see _try_failscan). Still only meaningful on a ~cornered elite -> pending is set at
#                              convergence and runs at the next pool-idle round-top, snapshotting the carried-forward elite.

def _ram_avail_gb():
    """MemAvailable in GB, read from /proc/meminfo (no psutil dep). 999.0 if unreadable -> gate passes."""
    try:
        for ln in open('/proc/meminfo'):
            if ln.startswith('MemAvailable:'):
                return int(ln.split()[1]) / 1048576.0
    except Exception:
        pass
    return 999.0
AUTO_BRANCH = False          # Joe 0723: DELETE RESTRICTIONS. We do NOT yet know whether an IS/OOS-friendly config rises
#                              fast or slow-burns, so bailing a cycle at the first imbalance (round 3) would prune the
#                              slow-burner class before we can characterise it. With False the checkpoint still BANKS every
#                              decision (imbalanced/regression/in_sync) but does NOT terminate the cycle — cycles run to
#                              natural stagnation and we get the FULL IS/OOS trajectory per window. Flip to True to re-arm
#                              the §5.3 branch actions once the data says what to select for.
# OOS = a FIXED disjoint block (recent tape). Fixed so bank-to-bank comparison is meaningful; disjoint from every IS
# draw so the in-sync test can never be self-confirming.
OOS_BLOCK = [(int(R.end_ms - off * DAY), int(R.end_ms - off * DAY + WIN_HOURS * 3600 * 1000)) for off in [2 + 1.3 * i for i in range(10)]]
IS_LO_OFF, IS_HI_OFF = 16.0, float(POOL_DAYS)   # IS days drawn from the OLDER tape (>=16d back) — never overlaps OOS_BLOCK

def draw_is_window(cycle):
    """Fresh random IS days for this cycle, FROZEN for its duration. Deterministic per cycle (reproducible/resumable).
    DISTINCT day-offsets (no duplicates) so all IS_DAYS windows carry independent tape."""
    rng = np.random.default_rng(5000 + cycle)
    offs = rng.choice(np.arange(int(IS_LO_OFF), int(IS_HI_OFF)), IS_DAYS, replace=False)
    return [(int(R.end_ms - float(o) * DAY), int(R.end_ms - float(o) * DAY + WIN_HOURS * 3600 * 1000)) for o in sorted(offs)]

def draw_is_pool(cycle):
    """SPLIT-CORNERING (Joe 0725): a LARGER candidate IS-window pool so each objective can select its regime-dense subset
    (rc_window.draw_regime_windows -> RC gets the rc-leg-dense windows, climb the climb-dense). Deterministic per cycle.
    Fixes RC's data starvation (measured 6.8x rc-leg concentration). Selection is on TRAIN windows only — OOS stays disjoint."""
    rng = np.random.default_rng(5000 + cycle)
    avail = np.arange(int(IS_LO_OFF), int(IS_HI_OFF))
    npool = min(len(avail), 3 * IS_DAYS)                                 # ~3x IS_DAYS candidates (capped to the available tape)
    offs = rng.choice(avail, npool, replace=False)
    return [(int(R.end_ms - float(o) * DAY), int(R.end_ms - float(o) * DAY + WIN_HOURS * 3600 * 1000)) for o in sorted(offs)]

def draw_oos7(cycle):
    """CLEAN confirm read (Joe 0726): OOS7_DAYS random days from the IS-era tape, disjoint from OOS_BLOCK (the recent 2-14d
    block) and — via the caller excluding these offsets from the train pool — from train too. Deterministic per cycle.
    A small, independent held-out: used as a Pareto veto/agreement read, not a peak to chase (7 days is noisy)."""
    rng = np.random.default_rng(7000 + cycle)
    offs = rng.choice(np.arange(int(IS_LO_OFF), int(IS_HI_OFF)), min(OOS7_DAYS, int(IS_HI_OFF - IS_LO_OFF)), replace=False)
    return sorted(int(o) for o in offs), [(int(R.end_ms - float(o) * DAY), int(R.end_ms - float(o) * DAY + WIN_HOURS * 3600 * 1000)) for o in sorted(offs)]
# OVERFITTING SAFEGUARD (Joe 0722): TRAIN explores/selects; VAL gates adoption. A knob change is adopted ONLY if it
# improves TRAIN *and* does NOT regress VAL — so a change that helps the train windows but hurts held-out ones is
# REJECTED as overfitting. Interleaved split (both span the tape). The 30-day finals is a THIRD held-out test set.
TRAIN = PANEL[0::2]
VAL = PANEL[1::2]                 # = oos10 (the disjoint 10-day block, once a cycle sets OOS_BLOCK); "VAL" name kept for refs
OOS7 = list(OOS_BLOCK)           # the 3rd read; overwritten per-cycle by draw_oos7 (default = oos10 so pre-cycle refs are safe)
VAL_EPS = 1e-6

def sample_windows(seed):   # kept for the variance diagnostic; the evo uses the fixed PANEL
    rng = np.random.default_rng(seed)
    lo = int(R.end_ms - POOL_DAYS * DAY); hi = int(R.end_ms - WIN_HOURS * 3600 * 1000)
    starts = rng.integers(lo, hi, size=N_WINDOWS)
    return [(int(s), int(s + WIN_HOURS * 3600 * 1000)) for s in starts]

# ---------- fitness (CPU) ----------
def _leg_net(flips, ets, epx):
    nets = []
    for a, b in zip(flips, flips[1:]):
        i = int(np.searchsorted(ets, a['ts'])); j = int(np.searchsorted(ets, b['ts'])); seg = epx[i:j + 1]; ep = epx[i]
        if len(seg) < 2 or ep <= 0 or not np.isfinite(ep): continue
        piv = find_pivots(seg, SWING_PCT)
        if not piv: nets.append((0.0, 0.0, int(a['rc']))); continue
        pv = np.array([seg[p[0]] for p in piv], float); hi = np.nanmax(pv); lo = np.nanmin(pv)
        if a['dir'] == 'bull': mfe = (hi - ep) / ep * 100; mae = (ep - lo) / ep * 100
        else: mfe = (ep - lo) / ep * 100; mae = (hi - ep) / ep * 100
        nets.append((mfe, mae, int(a['rc'])))     # rc flag: 1=rollercoaster leg, 0=climb
    return nets

def _apply_knobs(cfg):
    for k, a in KNOB_ATTR.items():
        if k in cfg: setattr(R, a, cfg[k])
    if 'lo_bound' in cfg: R.HI = 100 - cfg['lo_bound']    # symmetric boundary pair (Joe 0722): HI mirrors LO in 0-100
    if 'fence_lo' in cfg: R.FH = 100 - cfg['fence_lo']    # symmetric fence pair: FH mirrors FL

def _recompute_P_cpu():
    E = R.L0['E']
    R.L0['P'] = {TF: predict_breach(E[TF]['r'], E[TF]['m'], E[TF]['M'], R.HI, R.LO, R.FH, R.FL, 0.0) for TF in R.TFS}
    R.L0['Ps30'] = predict_breach(R.L0['s30r_'], R.L0['s30m_'], R.L0['s30M_'], R.HI, R.LO, R.FH, R.FL, 0.0)

def _build_line_L0(cfg):
    """Build an L0 for the per-band line config in cfg (keys 'band.line.param', + s2_top/s8_top edges).
    Unspecified lines default to R.LN. Uses the per-line cache (rebuilds only the bands whose config changed)."""
    s2t = int(cfg.get('s2_top', 2)); s8t = int(cfg.get('s8_top', 8))
    bands = {g: {k: dict(R.LN[k]) for k in ('r', 'x', 'm', 'M')} for g in ('s2', 's8', 'htf')}
    for key, val in cfg.items():
        p = key.split('.')
        if len(p) == 3 and p[0] in bands and p[1] in _LNMAP: bands[p[0]][_LNMAP[p[1]]][p[2]] = val
    ovr = {}
    for TF in R.TFS:
        g = 's2' if TF <= s2t else ('s8' if TF <= s8t else 'htf')
        for k in ('r', 'x', 'm', 'M'): ovr.update(R._mk(f'{k}{TF}', TF, bands[g][k]))
    for nm in ('s1x', 's1m'): ovr.update(R._mk(nm, 1.0, R.LN[nm]))
    for nm in ('s30r', 's30M'): ovr.update(R._mk(nm, 0.5, R.LN[nm]))
    ovr.update(R._mk('s30x', 0.5, R.LN['x'])); ovr.update(R._mk('s30m', 0.5, R.LN['m']))
    g5 = 5.0 / 60.0
    ovr.update(R._mk('gcs5r', g5, R.LN['r'])); ovr.update(R._mk('gcs5m', g5, R.LN['m'])); ovr.update(R._mk('gcs5x', g5, R.LN['x']))
    return R.build_lines(cache_jig_perline(R.end_ms, R.HOURS, R.WARMUP, ovr, pxs_cfg=R.PXS_CFG))

def _has_lines(cfg):
    return any(('.' in k) or k in ('s2_top', 's8_top') for k in cfg)

def _enter(cfg):
    """Apply cfg (knobs + optional line-L0 rebuild / boundary P-recompute) ONCE. Returns (restore_fn, ets, epx).
    The L0 build is the expensive part and is INDEPENDENT of the windows scored — so build once, score many."""
    save = {a: getattr(R, a) for a in KNOB_ATTR.values()}
    P0, Ps0 = R.L0['P'], R.L0['Ps30']; L0_old = R.L0
    _apply_knobs(cfg)                              # knobs first, so a line rebuild uses the config's boundary for P
    swap = _has_lines(cfg); touched_bnd = any(k in cfg for k in BND_KEYS)
    if swap: R.L0 = _build_line_L0(cfg)            # build_lines computes P at the applied boundary already
    elif touched_bnd: _recompute_P_cpu()
    ets = R.L0['ts'][R.L0['ei']]; epx = R.L0['pxs'][R.L0['ei']]
    def restore():
        for a, v in save.items(): setattr(R, a, v)
        if swap: R.L0 = L0_old
        elif touched_bnd: R.L0['P'], R.L0['Ps30'] = P0, Ps0
    return restore, ets, epx

def _score(windows, ets, epx):
    """Run the flip engine over the windows on the ALREADY-APPLIED config; return the fit tuple."""
    pw_rc = []; pw_cl = []; mfe = []; mae = []; rc_mfe = []; rc_mae = []; cl_mfe = []; cl_mae = []
    for s, e in windows:
        legs = _leg_net(R.run_chain('bear', s, persist=False, end=e), ets, epx)
        rcn = [m - a for m, a, rc in legs if rc]; cln = [m - a for m, a, rc in legs if not rc]
        if len(rcn) >= 2: pw_rc.append(float(np.median(rcn)))         # per-window RC net (RC legs are sparser -> >=2)
        if len(cln) >= 2: pw_cl.append(float(np.median(cln)))         # per-window climb net
        for m, a, rc in legs:
            mfe.append(m); mae.append(a)
            (rc_mfe if rc else cl_mfe).append(m); (rc_mae if rc else cl_mae).append(a)
    med = lambda x: float(np.median(x)) if x else 0.0
    need = max(2, len(windows) // 3)                                  # need this many windows-with-legs for a real score
    rob = lambda pw: float(np.percentile(pw, 20)) if len(pw) >= need else float('-inf')
    rc_mm = rob(pw_rc)   # ROBUST worst-case (Joe 0722): 20th-pct net, NOT pure min -> the messiest ~20% of windows can't
    cl_mm = rob(pw_cl)   # drag a good config down (no reference-config bootstrap). Deterministic. BOTH objs from one eval.
    return (rc_mm, cl_mm, med(mfe), med(mae), med(rc_mfe), med(rc_mae), med(cl_mfe), med(cl_mae))

def fitness(cfg, windows):
    """Single window-set score. Restores knobs (+ L0/P) after."""
    restore, ets, epx = _enter(cfg)
    try: return _score(windows, ets, epx)
    finally: restore()

def fitness_tv(cfg, train, val):
    """Score TRAIN and VAL from ONE L0 build (Joe 0722: kills the 2x line-rebuild waste — the hot path). -> (tr_fit, va_fit)."""
    restore, ets, epx = _enter(cfg)
    try: return _score(train, ets, epx), _score(val, ets, epx)
    finally: restore()

def fitness_multi(cfg, wins_list):
    """Score SEVERAL window-sets from ONE L0 build (Joe 0726: the 3-read rotation reads train+oos10+oos7 per candidate
    without paying 3 line rebuilds). -> [fit, ...] aligned to wins_list."""
    restore, ets, epx = _enter(cfg)
    try: return [_score(w, ets, epx) for w in wins_list]
    finally: restore()

def _score_knobs(cfg, windows, ets, epx):
    """Score a CHEAP/boundary-knob overlay on the ALREADY-BUILT line L0 (NO line rebuild). Applies only the call-time
    knobs (+ recomputes P if a boundary knob), scores, restores knobs/P. Joe 0722: cheap groups don't touch the lines,
    so the L0 is built ONCE per group by the caller and reused across every cheap candidate (was rebuilt each time)."""
    save = {a: getattr(R, a) for a in KNOB_ATTR.values()}; P0, Ps0 = R.L0['P'], R.L0['Ps30']
    for k, a in KNOB_ATTR.items():
        if k in cfg: setattr(R, a, cfg[k])
    if 'lo_bound' in cfg: R.HI = 100 - cfg['lo_bound']            # symmetric boundary pair
    if 'fence_lo' in cfg: R.FH = 100 - cfg['fence_lo']
    tb = any(k in cfg for k in BND_KEYS)
    if tb: _recompute_P_cpu()                                     # boundary changed P (cheap) — lines untouched
    try: return _score(windows, ets, epx)
    finally:
        for a, v in save.items(): setattr(R, a, v)
        if tb: R.L0['P'], R.L0['Ps30'] = P0, Ps0

def _net(fit, objective):
    """TRAIN/VAL MAE/MFE net (MFE - MAE) for the objective's legs — the adoption metric (Joe 0723). fit indices:
    4=rc_mfe 5=rc_mae 6=cl_mfe 7=cl_mae."""
    return (fit[4] - fit[5]) if objective == 'rc' else (fit[6] - fit[7])

# ---------- per-group branch-descent (runs in a worker) ----------
def sweep_group(args):
    """objective, group, seed. AGGRESSIVE train-only branch-descent, adopting a knob value only when it improves the TRAIN
    MAE/MFE NET (Joe 0723: NET, not minimax — a config that lifts the worst window but worsens the net is NOT progress and
    must not advance). Then validate the cornered config on VAL once (VAL = DIAGNOSTIC, not a gate — "dial train into a
    corner, then show where it doesn't stand up"). CHEAP groups build the line L0 ONCE and vary knobs on top; LINE groups
    rebuild per candidate. Returns (cfg, train_fit, val_fit)."""
    objective, group, seed, drv, tabu = args                     # Joe 0726: descent scores on the ROUND'S DRIVER window (drv),
    cur = dict(seed)                                             #   not always TRAIN; tabu = knobs fenced after a veto-fail (skip them)
    knobs = [k for k in group if k not in tabu]
    is_line = any(('.' in k) or k in ('s2_top', 's8_top') for k in knobs)
    if is_line:                                                  # each candidate changes a LINE param -> rebuild L0 per cand
        btr = fitness(cur, drv)
        for knob in knobs:
            for v in SUBSETS[knob]:
                if v == cur.get(knob): continue
                tr = fitness({**cur, knob: v}, drv)
                if _net(tr, objective) > _net(btr, objective) + 1e-9: cur = {**cur, knob: v}; btr = tr
        ftr, fo10, fo7 = fitness_multi(cur, [TRAIN, VAL, OOS7])   # Joe 0726: all 3 reads for the WINNER from ONE build (was a lone
    else:                                                        #   VAL read + a redundant parent rebuild in the veto). L0 already built.
        restore, ets, epx = _enter(cur)                          # single line-L0 build for the whole group
        try:
            btr = _score_knobs(cur, drv, ets, epx)
            for knob in knobs:
                for v in SUBSETS[knob]:
                    if v == cur.get(knob): continue
                    tr = _score_knobs({**cur, knob: v}, drv, ets, epx)   # no line rebuild — just knob + optional P
                    if _net(tr, objective) > _net(btr, objective) + 1e-9: cur = {**cur, knob: v}; btr = tr
            ftr = _score_knobs(cur, TRAIN, ets, epx)             # all 3 reads on the ALREADY-OPEN L0 — no rebuild
            fo10 = _score_knobs(cur, VAL, ets, epx)
            fo7 = _score_knobs(cur, OOS7, ets, epx)
        finally:
            restore()
    return (cur, tuple(ftr), tuple(fo10), tuple(fo7))            # (cfg, train_fit, oos10_fit, oos7_fit) — parent vetoes with ZERO rebuild

# ---------- DB ----------
def _db():
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute('''CREATE TABLE IF NOT EXISTS rpl_knob_subset (
        ks_id INT AUTO_INCREMENT PRIMARY KEY, ks_knob VARCHAR(64) UNIQUE, ks_values JSON,
        ks_kind VARCHAR(16), ks_active TINYINT DEFAULT 1)''')
    d.execute('''CREATE TABLE IF NOT EXISTS rpl_evo_group (
        eg_id INT AUTO_INCREMENT PRIMARY KEY, eg_subsets JSON, eg_active TINYINT DEFAULT 1)''')
    d.execute('''CREATE TABLE IF NOT EXISTS rpl_evo (
        re_id INT AUTO_INCREMENT PRIMARY KEY, re_objective VARCHAR(8), re_round INT, re_group INT, re_rank INT,
        re_minimax DOUBLE, re_mfe DOUBLE, re_mae DOUBLE,
        re_mfe_rc DOUBLE, re_mae_rc DOUBLE, re_mfe_cl DOUBLE, re_mae_cl DOUBLE,
        re_config JSON, re_scope VARCHAR(16), re_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    # CANDIDATE POOL (Joe 0723): every group's candidate each round — the menu §5.2 branches from. Banked so the branch
    # DIVERSITY threshold ("top-3 centroids sharing no less than N config differences") is MEASURED from data, not guessed.
    d.execute('''CREATE TABLE IF NOT EXISTS rpl_centroid (
        cp_id INT AUTO_INCREMENT PRIMARY KEY, cp_run VARCHAR(24), cp_iswin VARCHAR(255),
        cp_cycle INT, cp_round INT, cp_objective VARCHAR(8),
        cp_group VARCHAR(160), cp_rank INT, cp_tnet DOUBLE, cp_onet DOUBLE,
        cp_drift JSON, cp_config JSON, cp_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    for _c, _t in (('cp_run', 'VARCHAR(24)'), ('cp_iswin', 'VARCHAR(255)')):   # additive migration for pre-existing table
        try: d.execute(f'ALTER TABLE rpl_centroid ADD COLUMN {_c} {_t}')
        except Exception: pass
    # DURABLE OOS DECISION LOG (Joe 0723) — EVERY checkpoint decision, APPEND-ONLY across runs (never in the self-clean).
    # This is the dataset for "give me the config most alike for IS and OOS" -> ORDER BY ck_gap ASC. Invaluable for
    # deciding which confluences to build, so it must outlive any single run.
    d.execute('''CREATE TABLE IF NOT EXISTS rpl_oos_ckpt (
        ck_id INT AUTO_INCREMENT PRIMARY KEY, ck_run VARCHAR(24), ck_iswin VARCHAR(255), ck_isdays INT,
        ck_cycle INT, ck_round INT, ck_objective VARCHAR(8), ck_trigger VARCHAR(12),
        ck_is_net DOUBLE, ck_oos_net DOUBLE, ck_gap DOUBLE,
        ck_is_mfe DOUBLE, ck_is_mae DOUBLE, ck_oos_mfe DOUBLE, ck_oos_mae DOUBLE,
        ck_decision VARCHAR(16), ck_config JSON, ck_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    return d

def _kind(knob):
    if knob in ('s2_top', 's8_top') or '.' in knob: return 'line'
    return 'boundary' if knob in BND_KEYS else 'knob'

def ensure_defs(db):
    """Seed rpl_knob_subset + rpl_evo_group from DEFAULT_SUBSETS if empty (grouped in 3s). Idempotent."""
    have = db.execute('SELECT COUNT(*) c FROM rpl_knob_subset', fetch=True)[0]['c']
    if not have:
        for knob, vals in DEFAULT_SUBSETS.items():
            db.execute('INSERT INTO rpl_knob_subset (ks_knob,ks_values,ks_kind) VALUES (%s,%s,%s)',
                       (knob, json.dumps(vals), _kind(knob)))
        ids = {r['ks_knob']: r['ks_id'] for r in db.execute('SELECT ks_id,ks_knob FROM rpl_knob_subset', fetch=True)}
        cheap = [k for k in DEFAULT_SUBSETS if _kind(k) != 'line']    # cheap groups: arbitrary 3s (COW-parallel)
        for i in range(0, len(cheap), 3):
            db.execute('INSERT INTO rpl_evo_group (eg_subsets) VALUES (%s)', (json.dumps([ids[k] for k in cheap[i:i + 3]]),))
        # LINE groups PARAM-CENTRIC (Joe 0722): the 3 bands of each param grouped together, so the per-round random drop
        # keeps/drops a whole PARAM across all bands (r.k_len for s2+s8+htf, or none) -> matches Joe's "drop 2/3 of params".
        params = {}
        for k in DEFAULT_SUBSETS:
            if _kind(k) != 'line' or k in ('s2_top', 's8_top'): continue
            _, ln, p = k.split('.'); params.setdefault(f'{ln}.{p}', []).append(k)
        for pk in sorted(params):
            db.execute('INSERT INTO rpl_evo_group (eg_subsets) VALUES (%s)', (json.dumps([ids[k] for k in sorted(params[pk])]),))
        db.execute('INSERT INTO rpl_evo_group (eg_subsets) VALUES (%s)', (json.dumps([ids['s2_top'], ids['s8_top']]),))  # edges

def load_subsets(db):
    return {r['ks_knob']: (json.loads(r['ks_values']) if isinstance(r['ks_values'], str) else r['ks_values'])
            for r in db.execute('SELECT ks_knob,ks_values FROM rpl_knob_subset WHERE ks_active=1', fetch=True)}

def load_groups(db):
    id2knob = {r['ks_id']: r['ks_knob'] for r in db.execute('SELECT ks_id,ks_knob FROM rpl_knob_subset', fetch=True)}
    out = []
    for r in db.execute('SELECT eg_id,eg_subsets FROM rpl_evo_group WHERE eg_active=1 ORDER BY eg_id', fetch=True):
        subs = json.loads(r['eg_subsets']) if isinstance(r['eg_subsets'], str) else r['eg_subsets']
        out.append((r['eg_id'], [id2knob[s] for s in subs]))
    return out

def coverage(db):
    """Which subset-values made it into an elite config (proxy for the config space the search reached)."""
    subs = load_subsets(db)
    configs = [json.loads(r['re_config']) if isinstance(r['re_config'], str) else r['re_config']
               for r in db.execute('SELECT re_config FROM rpl_evo', fetch=True)]
    tested = {k: set() for k in subs}
    for c in configs:
        for k in subs:
            if k in c: tested[k].add(c[k])
    explored = sum(len(tested[k]) for k in subs); total = sum(len(subs[k]) for k in subs)
    log(f'  COVERAGE: {explored}/{total} subset-values reached an elite config')

def store_oos_ckpt(db, run_id, iswin, cyc, rnd, o, trig, is_net, oos_net, gap, tr, va, decision, cfg):
    """DURABLE record of EVERY OOS decision (Joe 0723): imbalanced / regression / in_sync alike. Append-only across runs.
    Answers "the config most alike for IS and OOS" via `ORDER BY ck_gap ASC` — the seed list for confluence building."""
    i_mfe, i_mae = (4, 5) if o == 'rc' else (6, 7)
    jz = json.dumps({k: (float(v) if isinstance(v, float) else v) for k, v in cfg.items()})
    db.execute('INSERT INTO rpl_oos_ckpt (ck_run,ck_iswin,ck_isdays,ck_cycle,ck_round,ck_objective,ck_trigger,'
               'ck_is_net,ck_oos_net,ck_gap,ck_is_mfe,ck_is_mae,ck_oos_mfe,ck_oos_mae,ck_decision,ck_config) '
               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
               (run_id, iswin, IS_DAYS, cyc, rnd, o, trig, float(is_net), float(oos_net), float(gap),
                float(tr[i_mfe]), float(tr[i_mae]), float(va[i_mfe]), float(va[i_mae]), decision, jz))

def store_oos32(db, cyc, rnd, o, is_net, oos32, gap32):
    """Joe 0724: end-of-cycle OOS·32 — the cornered elite scored over the 32 tape-spanning PANEL windows (which OVERLAP the IS
    window, so this is the CONTAMINATED wide OOS, distinct from the clean disjoint 10-day OOS·10d). Feeds the KPI dashboard's
    OOS·32/gap·32 columns. Append-only; the pulse reads the latest row per objective for the current cycle."""
    db.execute('''CREATE TABLE IF NOT EXISTS rpl_oos32 (o32_id INT AUTO_INCREMENT PRIMARY KEY, o32_cycle INT, o32_round INT,
        o32_objective VARCHAR(8), o32_is_net DOUBLE, o32_oos32 DOUBLE, o32_gap32 DOUBLE, o32_ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    db.execute('INSERT INTO rpl_oos32 (o32_cycle,o32_round,o32_objective,o32_is_net,o32_oos32,o32_gap32) VALUES (%s,%s,%s,%s,%s,%s)',
               (cyc, rnd, o, float(is_net), float(oos32), float(gap32)))

def win_sig(windows):
    """Readable signature of a training-window combo (the axis Joe analyses across ~40 combos): the UTC days it covers."""
    return ','.join(time.strftime('%m-%d', time.gmtime(s / 1000)) for s, _ in sorted(windows))[:255]

def store_centroids(db, cyc, rnd, o, groups, cands, seed_cfg, run_id='', iswin=''):
    """Bank this round's CANDIDATE POOL (Joe 0723) — one row per group's cornered candidate, with its drift vs the round's
    seed elite, its rank by train-net, and both nets. This is the menu §5.2 branches from; banking it lets the branch
    DIVERSITY threshold be read from the DB (pairwise drift distance) instead of guessed."""
    rows = []
    idx = [i for i, c in enumerate(cands) if c is not None]
    order = sorted(idx, key=lambda i: -_net(cands[i][1], o))
    rank = {i: k + 1 for k, i in enumerate(order)}
    for i in idx:
        cfg, tr, va = cands[i][0], cands[i][1], cands[i][2]                     # (cfg, train_fit, oos10_fit, oos7_fit) -> tnet=train, onet=oos10
        drift = {k: v for k, v in cfg.items() if seed_cfg.get(k) != v}          # what THIS group's move actually changed
        glabel = ','.join(groups[i]) if i < len(groups) else '?'
        jz = lambda dd: json.dumps({k: (float(v) if isinstance(v, float) else v) for k, v in dd.items()})
        rows.append((run_id, iswin, cyc, rnd, o, glabel[:160], rank[i], _net(tr, o), _net(va, o), jz(drift), jz(cfg)))
    if rows:
        db.executemany('INSERT INTO rpl_centroid (cp_run,cp_iswin,cp_cycle,cp_round,cp_objective,cp_group,cp_rank,cp_tnet,cp_onet,cp_drift,cp_config) '
                       'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)

def store_elite(db, rnd, elite, scope='panel'):
    """Frontier row per objective. Joe 0723: MFE/MAE columns carry the ADOPTED TRAIN metrics (monotonic net — never
    regress); re_minimax carries the VAL minimax (the DIAGNOSTIC — allowed to move, 'where it doesn't stand up').
    elite = {o: (cfg, train_fit, val_fit)}; each fit = (rc_mm,cl_mm,mfe,mae,rc_mfe,rc_mae,cl_mfe,cl_mae)."""
    rows = []
    for o, (cfg, tr, va) in elite.items():
        oi = 0 if o == 'rc' else 1
        rows.append((o, rnd, 0, 1, va[oi], tr[2], tr[3], tr[4], tr[5], tr[6], tr[7],   # re_minimax=VAL mm (diag); MFE/MAE=TRAIN
                     json.dumps({k: (float(v) if isinstance(v, float) else v) for k, v in cfg.items()}), scope))
    db.executemany('INSERT INTO rpl_evo (re_objective,re_round,re_group,re_rank,re_minimax,re_mfe,re_mae,re_mfe_rc,re_mae_rc,re_mfe_cl,re_mae_cl,re_config,re_scope) '
                   'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)

# ---------- evo loop ----------
def log(m):
    print(m); open('/home/joe/thecodes/rpl_evo.log', 'a', buffering=1).write(m + '\n')

def _is_line_group(g):
    return any(('.' in k) or k in ('s2_top', 's8_top') for k in g)

def _round(ctx, dbgroups, objective, seed, drv, tabu):
    """Every group branch-descends from the SINGLE elite seed on the round's DRIVER window `drv` (cheap 8-way, line 3-way),
    skipping any `tabu` knob. Each returns (cfg, driver_fit, oos10_fit) -> the caller re-reads all 3 for the Pareto veto."""
    cheap = [g for _, g in dbgroups if not _is_line_group(g)]
    line = [g for _, g in dbgroups if _is_line_group(g)]
    cands = []
    if cheap:
        with ctx.Pool(min(len(cheap), 8)) as pool:
            cands += pool.map(sweep_group, [(objective, g, seed, drv, tabu) for g in cheap])
    if line:
        with ctx.Pool(min(len(line), 3)) as pool:   # 3-way = one wave (keep_line=3). Safe on the 24GB ceiling (Joe 0723):
            cands += pool.map(sweep_group, [(objective, g, seed, drv, tabu) for g in line])
    return cands

def prepopulate_lines(subs):
    """Serially build the per-line cache for every single line-param value BEFORE the parallel phase, so parallel
    line-workers hit the cache (build_lines only, no in-worker Jig build) -> bounded peak memory for the 20h run."""
    keys = [k for k in subs if '.' in k]
    log(f'  pre-populating line cache: {sum(len(subs[k]) for k in keys)} single-line builds ...')
    t0 = time.time()
    for k in keys:
        for v in subs[k]:
            try: _build_line_L0({k: v})
            except Exception as e: log(f'    WARN prepop {k}={v}: {type(e).__name__}')
    log(f'  pre-populate done [{time.time()-t0:.0f}s]')

OI = {'rc': 0, 'climb': 1}   # index into a fit tuple's (rc_mm, cl_mm, ...) for each objective's minimax
RUN_ID = time.strftime('%m-%d %H:%M')   # tags candidate-pool rows so the append-only cross-run dataset stays separable

def _win_nets(cfg, windows):
    """Per-window mean(rc_net, cl_net) for a config — the raw material for messy-window detection."""
    save = {a: getattr(R, a) for a in KNOB_ATTR.values()}; P0, Ps0 = R.L0['P'], R.L0['Ps30']; L0_old = R.L0
    _apply_knobs(cfg); swap = _has_lines(cfg); tb = any(k in cfg for k in BND_KEYS)
    if swap: R.L0 = _build_line_L0(cfg)
    elif tb: _recompute_P_cpu()
    ets = R.L0['ts'][R.L0['ei']]; epx = R.L0['pxs'][R.L0['ei']]; out = []
    try:
        for s, e in windows:
            legs = _leg_net(R.run_chain('bear', s, persist=False, end=e), ets, epx)
            rcn = [m - a for m, a, rc in legs if rc]; cln = [m - a for m, a, rc in legs if not rc]
            vals = ([np.median(rcn)] if len(rcn) >= 2 else []) + ([np.median(cln)] if len(cln) >= 2 else [])
            out.append(float(np.mean(vals)) if vals else -9.0)
    finally:
        for a, v in save.items(): setattr(R, a, v)
        if swap: R.L0 = L0_old
        elif tb: R.L0['P'], R.L0['Ps30'] = P0, Ps0
    return np.array(out)

def run(max_rounds=200, smoke=False):
    """Elitist, interleaved co-evolution on the FIXED panel (Joe 0722). Each round, EACH objective branch-descends from
    ITS elite; a candidate replaces the elite ONLY if it strictly beats it on the same panel (elitism => monotonic, no
    regression). RC and climb both progress every round (neither starves). Converge when a full round improves neither.
    smoke=True: tiny fail-fast pilot (few cheap knobs, small panel, 4 rounds) to validate mechanics before the full run."""
    global SUBSETS, TRAIN, VAL, OOS7
    db = _db(); ensure_defs(db)
    SUBSETS = load_subsets(db)
    if smoke:
        cheap = [k for k in SUBSETS if _kind(k) != 'line'][:6]           # cheap knobs only -> no L0 rebuild, seconds/round
        SUBSETS = {k: SUBSETS[k] for k in cheap}
        TRAIN, VAL = PANEL[0:12:2], PANEL[1:12:2]; OOS7 = PANEL[13:19:2]; max_rounds = 6   # 6 train / 6 val / 3 oos7; +rounds to exercise the rotation
        dbgroups = [(i, cheap[i:i + 3]) for i in range(0, len(cheap), 3)]
    else:
        db.execute('DELETE FROM rpl_evo')         # self-clean (Joe 0722): a fresh full run owns the table — never mix
        try: db.execute('DELETE FROM rpl_messy_window')  # rows from a prior/killed run (their re_round would collide).
        except Exception: pass
        # NOTE (Joe 0723): rpl_centroid is deliberately NOT wiped — the candidate pool is APPEND-ONLY across runs so the
        # cross-window dataset (~40 training-window combos) accumulates. Rows are tagged cp_run + cp_iswin to stay separable.
        prepopulate_lines(SUBSETS)
        dbgroups = load_groups(db)
        TRAIN, VAL = COARSE[0::2], COARSE[1::2]   # START on the coarse panel (fast); phase 2 widens to the full 32.
                                                  # robust 20th-pct objective handles the messy tail; messy flagged dynamically
    cheap_g = [(i, g) for i, g in dbgroups if not _is_line_group(g)]
    line_g = [(i, g) for i, g in dbgroups if _is_line_group(g)]
    keep_line = max(1, round(len(line_g) / 3)) if line_g else 0     # Joe 0722: each sweep KEEPS ~1/3 of the LINE param-groups
    #    and DROPS 2/3 (line = 90% of the cost). Cheap knobs still sweep EVERY round. DETERMINISTIC rotation (Joe 0722):
    #    ONE fixed shuffle, cycled -> reproducible + every param swept once per pass (no fresh-random miss). ~3x faster rounds.
    def _line_sched():
        order = list(range(len(line_g))); np.random.default_rng(0).shuffle(order)   # single fixed permutation, cycled forever
        while True:
            for b in range(0, len(line_g), keep_line): yield [line_g[i] for i in order[b:b + keep_line]]
    lsched = _line_sched() if line_g else None
    PATIENCE = (-(-len(line_g) // keep_line) + 1) if line_g else 1   # converge only after ~one full line-rotation of no gain
    log('\n===== rpl evo sweep [%s] ' % ('SMOKE' if smoke else 'ELITIST') + time.strftime('%Y-%m-%d %H:%M') + ' =====')
    log(f'  {len(SUBSETS)} subsets, {len(dbgroups)} groups ({len(cheap_g)} cheap + {len(line_g)} line, {keep_line}/round); TRAIN {len(TRAIN)} / VAL {len(VAL)} windows')
    ctx = get_context('fork')
    seed = dict(BASE_CONFIG); seed.update({k: v for k, v in SEED_OVERRIDES.items() if k in SUBSETS})   # warm-start (r7)
    oseed = {'rc': dict(seed), 'climb': dict(seed)}                       # SPLIT per-objective warm-seed (Joe 0725): default r7 for both...
    if not smoke:                                                         # ...but if rpl_split_seed.json is present, RC <- cyc5-RC (near-sync),
        _sf = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rpl_split_seed.json')   # climb <- cyc5-climb: preserve the pre-cutover
        if os.path.exists(_sf):                                          # cornered elites instead of restarting cold from r7.
            try:
                _js = json.load(open(_sf))
                for o in ('rc', 'climb'):
                    if o in _js: oseed[o] = {**seed, **{k: v for k, v in _js[o].items() if (k in SUBSETS or k in BASE_CONFIG)}}
                log(f'  SPLIT warm-seed: rpl_split_seed.json -> RC {len(_js.get("rc",{}))} / climb {len(_js.get("climb",{}))} knobs (per-objective)')
            except Exception as _e:
                log(f'  SPLIT seed load FAILED ({_e}) -> falling back to r7 warm-start for both')
    elite = {}; o7fit = {}                                               # per-objective baseline fitness (3 reads: train, oos10, oos7)
    for o in ('rc', 'climb'):
        _tr, _va, _o7 = fitness_multi(oseed[o], [TRAIN, VAL, OOS7]); elite[o] = (dict(oseed[o]), _tr, _va); o7fit[o] = _o7
    btr, bva = elite['rc'][1], elite['rc'][2]                            # retained for downstream refs (rc's, arbitrary)
    prev = {o: _net(elite[o][1], o) for o in ('rc', 'climb')}            # monotonicity guard on the ADOPTED TRAIN NET (Joe 0723)
    last_bank = {o: None for o in ('rc', 'climb')}                        # §5.3: last banked OOS net (persists ACROSS cycles)
    last_good = {o: None for o in ('rc', 'climb')}                        #      last in-sync checkpoint config, for the revert
    _fs_dirty = [True]                                                    # Joe 0724: DEFERRED failscan (fixes the stale-snapshot loop). The old
    #   "run once AT convergence, else skip until next convergence" rule wedged: convergence coincides with the pool still holding
    #   memory (dying cycle's workers + the fresh cycle spinning up), so the RAM gate failed EVERY convergence and the snapshot
    #   froze for 3 cycles. Fix: a PENDING flag decouples the TRIGGER (staleness) from the EXECUTION window (RAM-clear). Set dirty at
    #   convergence (seeded True so cyc1 gets one), then retry at the TOP OF EVERY ROUND (a between-rounds, pool-idle, RAM-clear
    #   moment) until it lands; cleared on success -> ~once per cycle. Snapshots the current carried-forward (near-cornered) elite.
    def _try_failscan(cyc, rnd, where):
        if not cyc or not _fs_dirty[0]: return                           # only in cycle mode, only when a refresh is pending
        av = _ram_avail_gb()
        if av < FAILSCAN_RAM_GB: return                                  # stay PENDING; the next round-top retries when RAM clears
        try:
            from optimus9.orchestration import rpl_failscan as _fs        # lazy import breaks the rpl_failscan->this circular
            _snap, _cnt = _fs.snapshot(cycle=cyc, quiet=True)            # save/restores engine state; elite untouched on return
            for o in ('rc', 'climb'):                                    # wide read = OOS7 now (Joe 0726: the contaminated 32-panel is
                _f32 = fitness(elite[o][0], OOS7)                        #   retired — it rewarded over-fit via IS-overlap). Clean disjoint
                _o32 = _net(_f32, o); _is = _net(elite[o][1], o)         #   confirm; fitness() restores knobs/L0 so the live elite is untouched.
                store_oos32(db, cyc, rnd, o, _is, _o32, abs(_is - _o32))
            _fs_dirty[0] = False
            log(f"  [cyc{cyc}] failscan + OOS·32 refreshed ({where}, snap {_snap}, {_cnt} windows, RAM {av:.1f}GB) — confluence work-list")
        except Exception as _ex:
            log(f"  [cyc{cyc}] failscan/OOS·32 errored ({_ex}) — stays pending")
    msum = np.zeros(N_PANEL); mcnt = np.zeros(N_PANEL); mtot = 0          # dynamic messy-window evidence (Joe 0722):
    #                     accumulate per-window net from the EVOLVING elites -> messy = poor/untradeable across the
    #                     configs we ACTUALLY BUILT (no arbitrary reference configs). Flagged for manual review at the end.
    if not smoke: store_elite(db, 0, {o: (elite[o][0], elite[o][1], elite[o][2]) for o in elite})
    log(f'  baseline: RC tnet {_net(elite["rc"][1],"rc"):+.3f} vnet {_net(elite["rc"][2],"rc"):+.3f} | RPL tnet {_net(elite["climb"][1],"climb"):+.3f} vnet {_net(elite["climb"][2],"climb"):+.3f}')
    def _phase(train, val, oos7, label, rnd0, accrue, cyc=0, objs=('rc', 'climb')):
        """3-READ ROTATING-DRIVER loop (Joe 0726). Each round dials one of {oos10, train, oos7} as the descent driver; a move
        is ADOPTED only if it improves the driver AND regresses no read past VETO_EPS (Pareto veto). Veto-failed knobs are
        TABU'd for TABU_K rounds. A full rotation (len(ROT) rounds) with no adoption = mined out -> bail, banking the MAXIMIN
        (best worst-read) config. Returns (last_round, outcome) in {'stagnated','oos_stall_fresh'}."""
        nonlocal mtot
        global TRAIN, VAL, OOS7
        TRAIN, VAL, OOS7 = train, val, oos7
        WIN = {'train': TRAIN, 'o10': VAL, 'o7': OOS7}                   # the 3 reads the rotation dials / vetoes on
        for o in objs:                                                   # re-baseline ALL 3 reads on THIS panel (active objective only)
            tr, va, o7 = fitness_multi(elite[o][0], [TRAIN, VAL, OOS7]); elite[o] = (elite[o][0], tr, va); o7fit[o] = o7; prev[o] = _net(tr, o)
        log(f'  [{label}] TRAIN {len(TRAIN)} / VAL {len(VAL)} / OOS7 {len(OOS7)}: '
            f'RC tnet {_net(elite["rc"][1],"rc"):+.3f} vnet {_net(elite["rc"][2],"rc"):+.3f} o7 {_net(o7fit["rc"],"rc"):+.3f} | '
            f'RPL tnet {_net(elite["climb"][1],"climb"):+.3f} vnet {_net(elite["climb"][2],"climb"):+.3f} o7 {_net(o7fit["climb"],"climb"):+.3f}')
        stale = 0; rnd = rnd0
        nhist = {o: [_net(elite[o][1], o)] for o in ('rc', 'climb')}     # train-net trajectory (kept for the pulse round-line)
        oos_hist = {o: [_net(elite[o][2], o)] for o in ('rc', 'climb')}  # oos10 trajectory (kept for pulse compatibility)
        tabu = {o: {} for o in ('rc', 'climb')}                         # Joe 0726: knob -> expiry round (veto-fail fence)
        noadopt = {o: 0 for o in ('rc', 'climb')}                       #   consecutive no-adopt rounds; >= len(ROT) = mined out
        def _mm(o): return min(_net(elite[o][1], o), _net(elite[o][2], o), _net(o7fit[o], o))   # MAXIMIN = worst of the 3 reads
        best_mm = {o: (_mm(o), dict(elite[o][0]), (elite[o][1], elite[o][2], o7fit[o])) for o in ('rc', 'climb')}
        while rnd < rnd0 + max_rounds:
            rnd += 1
            _try_failscan(cyc, rnd, f'r{rnd} top')                       # deferred failscan + OOS·32: retry any pending refresh at this pool-idle moment
            sel = next(lsched) if lsched else []
            rgroups = cheap_g + sel                                      # cheap knobs every round + a deterministic 1/3 of line groups
            improved = {}
            driver = ROT[(rnd - rnd0 - 1) % len(ROT)]                   # Joe 0726: this round's descent driver (o10 -> train -> o7 -> ...)
            for o in objs:                                              # SPLIT (Joe 0725): only the active objective corners this phase
                tbset = {k for k, exp in tabu[o].items() if exp > rnd}  # knobs currently fenced (veto-fail tabu)
                seed_cfg = elite[o][0]
                cands = _round(ctx, rgroups, o, seed_cfg, WIN[driver], tbset)   # descent scored on the DRIVER window, tabu skipped
                if not smoke:                                           # bank the candidate POOL before adoption collapses it
                    store_centroids(db, cyc, rnd, o, [g for _, g in cheap_g] + [g for _, g in sel], cands, seed_cfg,
                                    run_id=RUN_ID, iswin=win_sig(TRAIN))   # tagged: append-only across runs (Joe 0723)
                DIDX = {'train': 1, 'o10': 2, 'o7': 3}          # read -> index in a candidate's (cfg, train, o10, o7) tuple
                E = {'train': _net(elite[o][1], o), 'o10': _net(elite[o][2], o), 'o7': _net(o7fit[o], o)}   # elite's 3 reads
                best = max(cands, key=lambda c: _net(c[DIDX[driver]], o)) if cands else None   # best candidate BY the driver read
                if best is not None and _net(best[DIDX[driver]], o) > E[driver] + 1e-9:   # driver improved -> veto (reads already in hand)
                    C = {m: _net(best[DIDX[m]], o) for m in ROT}                   # winner's 3 reads — computed in the worker, NO parent rebuild
                    regress = [m for m in ROT if C[m] < E[m] - VETO_EPS]            # PARETO VETO: no read may regress past eps
                    if not regress:                                                # improves driver, regresses nothing -> ADOPT
                        improved[o] = C[driver] - E[driver]; elite[o] = (best[0], best[1], best[2]); o7fit[o] = best[3]
                        mm = min(C.values())
                        if mm > best_mm[o][0]: best_mm[o] = (mm, dict(best[0]), (best[1], best[2], best[3]))   # MAXIMIN bank target
                    else:                                                          # veto-fail -> TABU the knob(s) this move changed
                        for k, v in best[0].items():
                            if seed_cfg.get(k) != v: tabu[o][k] = rnd + TABU_K
                noadopt[o] = 0 if o in improved else noadopt[o] + 1
                cur_net = _net(elite[o][1], o); prev[o] = cur_net
                nhist[o].append(cur_net)
                if not smoke and cyc and (rnd - rnd0) % len(ROT) == 0:  # once per full rotation: DB checkpoint + pulse feed
                    onet = _net(elite[o][2], o); o7net = _net(o7fit[o], o); gap = abs(cur_net - o7net)
                    store_oos_ckpt(db, RUN_ID, win_sig(TRAIN), cyc, rnd, o, driver, cur_net, onet, gap,
                                   elite[o][1], elite[o][2], ('adopt' if o in improved else 'hold'), elite[o][0])
                    store_oos32(db, cyc, rnd, o, cur_net, o7net, gap)   # dashboard 'OOS·32' column now carries the CLEAN o7 read
                    store_elite(db, rnd, {o: (elite[o][0], elite[o][1], elite[o][2])}, scope='oos')
                    ld = ', '.join(f'{k}={v}' for k, v in sorted(elite[o][0].items()) if '.' in k and BASE_CONFIG.get(k) != v)
                    log(f"  [{time.strftime('%H:%M:%S')}] OOS CHECKPOINT c{cyc} r{rnd} [{o}] (driver {driver}) -> "
                        f"IS {cur_net:+.3f} | o10 {onet:+.3f} | o7 {o7net:+.3f}  (maximin {min(cur_net,onet,o7net):+.3f}, gap {gap:.3f})")
                    log(f"      candidate line drift: {ld or '(none — cheap-knob drift only)'}")
            if not smoke:
                store_elite(db, rnd, {o: (elite[o][0], elite[o][1], elite[o][2]) for o in elite})
                if accrue and rnd % 4 == 0:                              # messy accrual (full-panel, FINE phase only; costly)
                    val_idx = list(range(1, N_PANEL, 2))                 # PANEL[1::2] = the held-out VAL windows
                    for o in ('rc', 'climb'):
                        nv = _win_nets(elite[o][0], PANEL); m = nv > -8.9
                        msum[m] += nv[m]; mcnt[m] += 1; mtot += 1
                        soft = sorted((i for i in val_idx if nv[i] > -8.9), key=lambda i: nv[i])[:3]   # WHERE IT DOESN'T STAND UP
                        if soft: log(f'    VAL soft spots [{o}] (train-cornered config fails here -> confluence gaps): '
                                     + ', '.join(f'{R.fmt(PANEL[i][0])}({nv[i]:+.2f})' for i in soft))
            msg = []
            for o in ('rc', 'climb'):
                tr, va = elite[o][1], elite[o][2]
                tnet = _net(tr, o); vnet = _net(va, o)                   # tnet = ADOPTED train net (monotonic); vnet = VAL diagnostic
                up = f' +{improved[o]:.3f}' if o in improved else ' static'
                msg.append(f'{o} tnet {tnet:+.3f}{up} | vnet {vnet:+.3f} vmm {va[OI[o]]:+.3f}')
            live = ', '.join(sorted({(s[1][0].split('.', 1)[1] if '.' in s[1][0] else 'edges') for s in sel})) if sel else '—'
            log(f'round {rnd} [{label} drv:{driver} {len(sel)}/{len(line_g)} line: {live}]: ' + ' | '.join(msg))   # DRIVER + which line-params are LIVE
            rt, ct = elite['rc'][1], elite['climb'][1]                   # timestamped MAE/MFE one-liner per rotation (Joe 0723)
            log(f"  [{time.strftime('%H:%M:%S')}] r{rnd} adopted MAE/MFE — RC mfe {rt[4]:+.3f} mae {rt[5]:+.3f} net {_net(rt,'rc'):+.3f}"
                f" | RPL mfe {ct[6]:+.3f} mae {ct[7]:+.3f} net {_net(ct,'climb'):+.3f}")
            for o in objs: oos_hist[o].append(_net(elite[o][2], o))     # kept for pulse compatibility
            for o in objs:                                              # Joe 0726: ROTATION-BAIL — a full rotation (len(ROT) rounds) with NO
                if cyc and noadopt[o] >= len(ROT):                      #   Pareto adoption = no move improves any read without regressing
                    pk = best_mm[o]                                     #   another = mined out. Bank the MAXIMIN config (best worst-read).
                    if pk[0] > MIN_OOS_NET:                             #   only if it's positive on ALL 3 reads (a genuine keeper)...
                        elite[o] = (dict(pk[1]), pk[2][0], pk[2][1]); o7fit[o] = pk[2][2]
                        last_bank[o] = pk[0]; last_good[o] = (dict(pk[1]), pk[2][0], pk[2][1]); bankmsg = f"maximin {pk[0]:+.3f} banked"
                    else:
                        bankmsg = "no all-positive config — re-window as-is"   # ...else nothing to bank; carry forward, fresh ground
                    log(f"  [{label}] ROTATION STALL on {o}: no Pareto-adopt for {len(ROT)} rounds (a full rotation) — "
                        f"mined out, {bankmsg} -> FRESH {IS_DAYS}-day window")
                    return rnd, 'oos_stall_fresh'
            stale = 0 if improved else stale + 1
            if not smoke and stale >= PATIENCE:
                log(f'  [{label}] no Pareto adoption for {PATIENCE} rounds (full line rotation) -> phase converged'); break
        return rnd, 'stagnated'
    if smoke:
        _phase(TRAIN, VAL, OOS7, 'smoke', 0, accrue=False)
        log('  SMOKE PASS: rotating-driver adoption + Pareto veto ran on both objectives, no crash.'); return
    # ===== §5.3 AUTO-MANAGING LOOP (Joe 0723) — replaces the fixed coarse phase =====
    # Each cycle: FRESH random 8-day IS window (frozen) vs the fixed disjoint OOS block. The config carries forward across
    # cycles; only the ground changes. Hunt ends when a cycle stagnates while IS/OOS are IN SYNC = the agnostic config.
    rnd = 0; agnostic = False
    import rc_window as RW                                              # SPLIT (Joe 0725): native rr_rollercoaster regime tag -> per-objective dense windows
    for cyc in range(1, MAX_CYCLES + 1):
        o7_offs, oos7 = draw_oos7(cyc)                                  # CLEAN confirm read: 7 random days, reserved BEFORE the train pool
        pool = [w for w in draw_is_pool(cyc) if w not in oos7]          # candidate pool, EXCLUDING the oos7 days -> train ⊥ oos7 ⊥ oos10
        rc_is, cl_is = RW.draw_regime_windows(pool, IS_DAYS)
        if len(rc_is) < 2 or len(cl_is) < 2:                            # degenerate pool -> fall back to the shared draw
            rc_is = cl_is = [w for w in draw_is_window(cyc) if w not in oos7]
        log(f"\n--- CYCLE {cyc}: SPLIT — r_RC on {len(rc_is)} RC-dense IS / r_RPL on {len(cl_is)} climb-dense IS vs {len(OOS_BLOCK)}d oos10 + {len(oos7)}d oos7 (disjoint) ---")
        rnd, out_rc = _phase(rc_is, OOS_BLOCK, oos7, f'cycRC{cyc}', rnd, accrue=False, cyc=cyc, objs=('rc',))    # r_RC{n}: RC corners on RC-dense, independent bail
        rnd, out_cl = _phase(cl_is, OOS_BLOCK, oos7, f'cycRPL{cyc}', rnd, accrue=False, cyc=cyc, objs=('climb',))  # r_RPL{n}: climb on climb-dense, independent bail
        outcome = out_rc if out_rc != 'stagnated' else out_cl          # driver post-cycle logic: any non-stagnated outcome carries
        # PHASE-CONVERGENCE FAILSCAN (Joe 0723/0724): the cycle just cornered its elite -> mark the failscan PENDING and try once
        # now. If RAM is tight (pool memory not yet released at convergence), it STAYS pending and the next round-top runs it
        # (see _try_failscan) — this is the fix for the stale-snapshot loop where the convergence-instant RAM gate never passed.
        _fs_dirty[0] = True
        _try_failscan(cyc, rnd, 'convergence')
        if outcome == 'stagnated':
            # AGNOSTIC requires BOTH: OOS clears the profitability floor AND the gap is inside tolerance (Joe 0723) —
            # a consistently-losing config has a tiny gap and must never be declared the winner of the hunt.
            profitable = all(_net(elite[o][2], o) > MIN_OOS_NET for o in ('rc', 'climb'))
            tight = all(abs(_net(elite[o][1], o) - _net(elite[o][2], o)) <= SYNC_TOL for o in ('rc', 'climb'))
            in_sync = profitable and tight
            log(f"  [cyc{cyc}] stagnated; OOS profitable={profitable} gap-tight={tight} -> "
                + ('IN SYNC' if in_sync else ('losing-but-tight (NOT agnostic)' if tight else 'still imbalanced')))
            if in_sync:
                agnostic = True; log('  ===== AGNOSTIC CONFIG FOUND (stagnated in sync) ====='); break
        elif outcome == 'regression':
            log(f'  [cyc{cyc}] reverted to last checkpoint -> next cycle explores fresh ground (§5.2 top-2 spawn is the next build)')
        elif outcome == 'oos_regress_fresh':
            log(f'  [cyc{cyc}] abandoned early (OOS giving back near stagnation) -> next cycle draws fresh ground')
        elif outcome == 'oos_stall_fresh':
            log(f'  [cyc{cyc}] abandoned early (OOS flat for {MAX_OOS_STALL} rounds, not in-sync = mined out) -> next cycle draws fresh ground')
    if not agnostic: log(f'  (auto-loop ran {MAX_CYCLES} cycles without a stagnated-in-sync config)')
    _phase(PANEL[0::2], PANEL[1::2], draw_oos7(0)[1], 'fine', rnd, accrue=True)   # full 32-window refinement + messy accrual (3-read)
    # held-out TEST (30-day, never touched in train/val); train==val==test here (single held-out eval)
    for fr in range(1, 3):
        lo = int(R.end_ms - (2 + fr) * FINAL_DAYS * DAY // 2)
        fin = {}
        for o in ('rc', 'climb'):
            f = fitness(elite[o][0], [(lo, int(lo + FINAL_DAYS * DAY))]); fin[o] = (elite[o][0], f, f)
        store_elite(db, 100 + fr, fin, f'{FINAL_DAYS}d')
        log(f'  30d TEST {fr}: RC net {fin["rc"][1][4]-fin["rc"][1][5]:+.3f} | RPL net {fin["climb"][1][6]-fin["climb"][1][7]:+.3f}')
    for o in ('rc', 'climb'):
        drift = {k: v for k, v in elite[o][0].items() if BASE_CONFIG.get(k) != v}
        log(f'===== EVO DONE [{o}] cornered drift {drift} =====')
    # MESSY windows (Joe 0722): poor/untradeable across ALL the evolved elites -> MANUAL REVIEW, not a config's fault.
    if mtot:
        trad = mcnt / mtot                                               # fraction of elite-evals this window was tradeable
        mean_net = np.where(mcnt > 0, msum / np.maximum(mcnt, 1), -9.0)  # mean net when tradeable
        good = mean_net[mcnt > 0]
        thr = float(np.percentile(good, 20)) if len(good) else 0.0       # bottom-20% net across the evolved elites
        messy = [i for i in range(N_PANEL) if trad[i] < 0.3 or (mcnt[i] > 0 and mean_net[i] <= thr)]
        db.execute('''CREATE TABLE IF NOT EXISTS rpl_messy_window (
            mw_id INT AUTO_INCREMENT PRIMARY KEY, mw_start BIGINT, mw_net DOUBLE, mw_tradeable DOUBLE,
            mw_evals INT, mw_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        db.execute('DELETE FROM rpl_messy_window')
        log(f'  MESSY windows (MANUAL REVIEW, {len(messy)}/{N_PANEL}) — poor/untradeable across all evolved elites:')
        for i in sorted(messy, key=lambda i: mean_net[i]):
            log(f'    {R.fmt(PANEL[i][0])}  net {mean_net[i]:+.3f}  tradeable {trad[i]*100:.0f}% of {mtot} elite-evals')
            db.execute('INSERT INTO rpl_messy_window (mw_start,mw_net,mw_tradeable,mw_evals) VALUES (%s,%s,%s,%s)',
                       (int(PANEL[i][0]), float(mean_net[i]), float(trad[i]), int(mtot)))
    coverage(db)

if __name__ == '__main__':
    if os.environ.get('SKIP_SMOKE') != '1':   # Joe 0726: skip the pilot for CONFIG-ONLY restarts (mechanic already validated);
        run(smoke=True)                        #   keep it for code/mechanic changes. SKIP_SMOKE=1 -> straight to seed + evolve.
    run()              # full elitist interleaved co-evolution (RC + climb corner together)
