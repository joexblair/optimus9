"""build_past50 — the past-50 momentum mechanic (Joe 0726). SAVED. Event-tape (px_smooth) throughout.

SPEC (corrected across the session):
  QUALIFY (both branches): s4Mage OOB (same side) sustained > 240s (TF seam) AND hs60x OOB (same side).
  trade_dir = the TURN off the s4M extreme (s4M OOB HI -> short, LO -> long; cross dir d = -de).  ROUTING, per-TF on
  r vs 50 (s15, s22 each on THEIR OWN r): r SAME-SIDE of the BREACH de (lo-breach de<0 -> r<=50; hi-breach -> r>=50)
  -> BRANCH A; not-same-side -> BRANCH B.
    BRANCH A  block until (x OR m) crosses Mage (race across TFs) -> trade.  A is the PREFERRED mode and LATCHES
              (Joe 0727): once ANY TF is same-side (A), commit to A for the rest of the walk -- B->A promotion is
              ONE-WAY, A never demotes back to B.
    BRANCH B  x is OOB & not-yet-crossed-m -> wob x×m cross -> trade.  Eligible only BEFORE A latches.
  Both branches: RGATE gates the fire (gtr%d r same-side-of-50 vs de at the fire bar, else drop).
  Crosses wob-debounced on the EVENT tape (cross_wob). 'race' = first trigger across {s15,s22} × {branch trigger}.
Scored swing-to-pivot @2% (siglab). Usage: build_past50.py [YYYY-MM-DD HH:MM ndays_hours]  (default: 06-12 diagnostic)
"""
import sys, json
import numpy as np
import datetime as dt
import optimus9.orchestration.rpl_walk as R
import linelab as LL
import siglab
from optimus9.analysis.lr_v2 import _slope_flip
from optimus9.compute.breaching_line import predict_breach

HI, LO = R.HI, R.LO          # boundary <- optimus9_system via rpl_walk (0728; was a literal 85/15 here)
A_MAGE_OOB = True            # branch-A gate: require s15 OR s22 Mage OOB (>=HI | <=LO) before an A-cross can fire
RGATE = True                 # r-confluence gate (Joe 0726): fire only when the gate line is SAME-SIDE of 50 vs breach de
GATE_TF = 2                  # gate line = k10/4/11 r at this TF (Joe 0726: dropped 15/12 -> low TF; the low-TF r is same-side
#                              at the bars the s15r/s12r gate was dropping). Both branches. Trying TF2 (TF3 lost too many longs).
AB_CROSS_WOB = 6            # branch A/B cross debounce (x/m x Mage, x x m), EMERGING 5s event bars = 30s
DWELL_S = 240
HTFS = (15, 22)

# --- lines from the climb HTF seed (the sweep-cornered config) ---
_seed = json.load(open('optimus9/orchestration/rpl_split_seed.json'))['climb']
_TOK = {'m': 'mn', 'M': 'mj', 'r': 'r', 'x': 'x'}
def _bc(line):
    b = dict(R.LN[line])
    for k, v in _seed.items():
        p = k.split('.')
        if len(p) == 3 and p[0] == 'htf' and p[1] == _TOK[line]:
            b[p[2]] = v
    return b
_cx, _cm, _cM, _cr = _bc('x'), _bc('m'), _bc('M'), _bc('r')
LL.register('s4M', kind='bb', tf=4, length=37, mult=0.83)
for tf in HTFS:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=_cx['length'], mult=_cx['mult'])
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=_cm['length'], mult=_cm['mult'])
    LL.register('s%dM' % tf, kind='bb', tf=tf, length=_cM['length'], mult=_cM['mult'])
    LL.register('s%dr' % tf, kind='k',  tf=tf, k_len=_cr['k_len'], rsi=_cr['rsi'], stc=_cr['stc'])
LL.register('s12r', kind='k', tf=12, k_len=_cr['k_len'], rsi=_cr['rsi'], stc=_cr['stc'])  # branch-B confluence gate (Joe 0726)
LL.register('gtr%d' % GATE_TF, kind='k', tf=GATE_TF, k_len=_cr['k_len'], rsi=_cr['rsi'], stc=_cr['stc'])  # RGATE line at GATE_TF (both branches)
# gcs5 finisher lines — 5-second itf, base LN configs (IDENTICAL to the RC/RPL sweep's gcs5 finisher, rpl_walk:45)
LL.register('gcs5x', kind='bb', tf=5.0 / 60, length=5, mult=0.37)
LL.register('gcs5m', kind='bb', tf=5.0 / 60, length=6, mult=0.45)
LL.register('gcs5r', kind='k',  tf=5.0 / 60, k_len=7, rsi=5, stc=11)
# s1 lines for the 2-STAGE finisher (stage 1) — s1x / s1Mage at TF1 (engine LN['s1x'], LN['s1M'])
LL.register('s1x', kind='bb', tf=1, length=5, mult=0.37)
LL.register('s1M', kind='bb', tf=1, length=37, mult=0.83)
# s3s4 GATE lines (climb-seed band configs): s2r (s2-band), s3/s4 r+m (s8-band), M frozen bb37/0.83
LL.register('s2r', kind='k', tf=2, k_len=7, rsi=4, stc=9)
LL.register('s3r', kind='k', tf=3, k_len=7, rsi=5, stc=12); LL.register('s3m', kind='bb', tf=3, length=5, mult=0.45)
LL.register('s3M', kind='bb', tf=3, length=37, mult=0.83)
LL.register('s4r', kind='k', tf=4, k_len=7, rsi=5, stc=12); LL.register('s4m', kind='bb', tf=4, length=5, mult=0.45)

cache, ets, epx, names = LL.warm(rebuild=False)
te = LL.ets_of(cache)                                              # EVENT timebase
lab = siglab.Lab(cache, ets, epx)
s4M = LL.line(cache, 's4M'); hs = LL.line(cache, 'hs60x')
L = {tf: {k: LL.line(cache, 's%d%s' % (tf, k)) for k in ('x', 'm', 'M', 'r')} for tf in HTFS}
_s12r = LL.line(cache, 's12r')                                     # (legacy branch-B gate line; superseded by _gater)
_gater = LL.line(cache, 'gtr%d' % GATE_TF)                         # RGATE line at GATE_TF — both branches gate on this now
g5x = LL.line(cache, 'gcs5x'); g5m = LL.line(cache, 'gcs5m'); g5r = LL.line(cache, 'gcs5r')
s1x = LL.line(cache, 's1x'); s1M = LL.line(cache, 's1M')
_gd = g5x - g5m                                                    # gcs5x - gcs5m (for the finisher cross)
_s1d = s1x - s1M                                                   # s1x - s1Mage (stage-1 cross)
FIN_HORIZON_MS = 60 * 60 * 1000                                    # finish must confirm within 1h of the provisional, else drop
_g_up = (_gd > 0) & (np.roll(_gd, 1) <= 0); _g_dn = (_gd < 0) & (np.roll(_gd, 1) >= 0)
_s1_up = (_s1d > 0) & (np.roll(_s1d, 1) <= 0); _s1_dn = (_s1d < 0) & (np.roll(_s1d, 1) >= 0)

# ---- s3s4 gate signals (event tape; faithful to lr_v2.gate_signals) ----
_s2r = LL.line(cache, 's2r')
_s3r, _s3m, _s3M = LL.line(cache, 's3r'), LL.line(cache, 's3m'), LL.line(cache, 's3M')
_s4r, _s4m, _s4Mg = LL.line(cache, 's4r'), LL.line(cache, 's4m'), LL.line(cache, 's4M')
_FH, _FL = R.FH, R.FL
GSIG = dict(
    pred3=predict_breach(_s3r, _s3m, _s3M, HI, LO, _FH, _FL), pred4=predict_breach(_s4r, _s4m, _s4Mg, HI, LO, _FH, _FL),
    brc3=np.where(_s3r >= HI, 1, np.where(_s3r <= LO, -1, 0)), brc4=np.where(_s4r >= HI, 1, np.where(_s4r <= LO, -1, 0)),
    s3m_oob=(_s3m >= HI) | (_s3m <= LO), s4m_oob=(_s4m >= HI) | (_s4m <= LO),
    rev3r=_slope_flip(_s3r), rev4r=_slope_flip(_s4r), rev3m=_slope_flip(_s3m), rev4m=_slope_flip(_s4m),
    rev2M=_slope_flip(s1M),                                        # gate_rev = s1M (60s, engine default)
    oob2=(_s2r >= HI) | (_s2r <= LO), oob3=(_s3r >= HI) | (_s3r <= LO), oob4=(_s4r >= HI) | (_s4r <= LO))


def s3s4_gate(i0, de):
    """s3s4 arm→gate lifecycle (faithful to lr_v2.gate_open). es = exhaustion side (de), bd = turn dir (-de).
    Opens via path a (all 3 r cross OOB→IB), b (predict-then-reverse-before-breach), or c (ready-to-reverse →
    s1Mage reverse). -> gate-open bar idx or None (no open within FIN_HORIZON_MS -> drop). Applied BEFORE the finisher."""
    es, bd = de, -de
    endt = te[i0] + FIN_HORIZON_MS
    p3 = p4 = b3 = b4 = rtr = xin2 = xin3 = xin4 = False
    g = GSIG
    for k in range(i0 + 1, n):
        if te[k] > endt:
            return None
        if g['oob2'][k - 1] and not g['oob2'][k]: xin2 = True
        if g['oob3'][k - 1] and not g['oob3'][k]: xin3 = True
        if g['oob4'][k - 1] and not g['oob4'][k]: xin4 = True
        if xin2 and xin3 and xin4:
            return k                                              # (a) all 3 r crossed into IB
        if g['pred3'][k] == es and g['s3m_oob'][k]: p3 = True
        if g['pred4'][k] == es and g['s4m_oob'][k]: p4 = True
        if p3 and g['brc3'][k] == es: b3 = True
        if p4 and g['brc4'][k] == es: b4 = True
        if (p3 and not b3 and g['rev3r'][k] == bd) or (p4 and not b4 and g['rev4r'][k] == bd):
            return k                                              # (b) reverse before breach
        rtr = rtr or b3 or b4 or (not p3 and not p4 and (g['rev3m'][k] == bd or g['rev4m'][k] == bd))
        if rtr and g['rev2M'][k] == bd:
            return k                                              # (c) ready-to-reverse -> s1Mage reverse
    return None
n = len(te)
f = lambda i: dt.datetime.utcfromtimestamp(te[i] / 1000).strftime('%m-%d %H:%M:%S')


def _sustained_oob(line, side, secs):
    """per-bar bool: `line` has been continuously OOB on `side` (+1 hi / -1 lo) for >= secs wall-clock (event tape)."""
    oob = (line >= HI) if side > 0 else (line <= LO)
    start = np.empty(n); cur = -1
    for i in range(n):
        if oob[i]:
            if i == 0 or not oob[i - 1]:
                cur = te[i]
            start[i] = cur
        else:
            start[i] = -1
    return oob & (start >= 0) & ((te - start) >= secs * 1000)


def _wcross(a, b, direction, wob=AB_CROSS_WOB):
    """wob-debounced cross of (a-b) through 0 in `direction`, rising-edge, on the event tape."""
    wc = cache.causal.cross_wob(a - b, 0.0, direction, wob)
    return wc & ~np.roll(wc, 1)


def qualify():
    """onset bars where s4M OOB(same side) dwell>=DWELL_S AND hs60x OOB(same side) LATCHED at ANY point during
    that s4M OOB episode (Joe 0727 — hs60x need NOT be OOB on the dwell bar itself; the old same-bar conjunction
    was inference). ONE onset per episode: onset = max(dwell-met bar, first hs60x-OOB bar in the episode).
    -> [(i, de)] de=s4M side."""
    out = []
    for de in (+1, -1):
        oob = (s4M >= HI) if de > 0 else (s4M <= LO)
        hoob = (hs >= HI) if de > 0 else (hs <= LO)
        for k in np.flatnonzero(oob & ~np.roll(oob, 1)):
            e = k
            while e < n and oob[e]:
                e += 1
            dw = next((j for j in range(k, e) if te[j] - te[k] >= DWELL_S * 1000), None)
            h = np.flatnonzero(hoob[k:e])
            if dw is None or not len(h):
                continue                                       # episode never served the dwell, or hs60x never OOB in it
            out.append((int(max(dw, int(h[0]) + k)), de))
    return sorted(out)


def _r_same_side(r, de):
    """Per-bar STATE (Joe 0726): r same-side of 50 as the s4Mage BREACH side de (hi-breach de>0 -> r>=50 is same-side;
    lo-breach de<0 -> r<=50 is same-side). Inclusive. same-side -> branch-A path; not-same-side -> branch-B path.
    (Reference is the BREACH side de, NOT the trade side -de — the trade is the reversal: hi-breach -> short, lo -> long.)"""
    return (r >= 50.0) if de > 0 else (r <= 50.0)


def _stage(start, arm, fire):
    """One latch stage: from `start`, latch when `arm` true, fire at the first `fire` while latched (within
    FIN_HORIZON_MS). -> bar idx or None. The reusable primitive behind both the gcs5 and s1 stages."""
    endt = te[start] + FIN_HORIZON_MS; latched = False
    for i in range(start, n):
        if te[i] > endt:
            return None
        if arm[i]:
            latched = True
        if latched and fire[i]:
            return i
    return None


def finish(i_prov, de, two_stage=False):
    """LATCH finisher — refine a provisional entry forward to the confirmed turn. cur = the exhaustion leg
    (de>0 bull -> OOB>=HI + down-cross; de<0 bear -> OOB<=LO + up-cross).
      STAGE 2 (gcs5, IDENTICAL to rpl_walk:166-169): latch gcs5r OOB, fire at first gcs5x×gcs5m flip-cross.
      STAGE 1 (two_stage=True, Joe 0726): FIRST require s1Mage OOB, unlatch on s1x×s1Mage flip-cross — the s1-level
      turn confirms BEFORE the gcs5 stage runs (s1 turn -> then gcs5 times the entry). -> bar idx or None (drop)."""
    start = i_prov
    if two_stage:                                                 # STAGE 1: s1Mage OOB -> s1x crosses s1Mage
        s1_arm = (s1M >= HI) if de > 0 else (s1M <= LO)
        s1_fire = _s1_dn if de > 0 else _s1_up
        start = _stage(i_prov, s1_arm, s1_fire)
        if start is None:
            return None
    g_arm = (g5r >= HI) if de > 0 else (g5r <= LO)                # STAGE 2: gcs5r OOB -> gcs5x crosses gcs5m
    g_fire = _g_dn if de > 0 else _g_up
    return _stage(start, g_arm, g_fire)


def trigger(i0, de, wob=AB_CROSS_WOB, a_variant='both', fin=False, gate=False, trace=False):
    """From onset i0, s4Mage breach side de. The breach SETS the trade as the REVERSAL: hi-breach (de>0) -> SHORT,
    lo-breach (de<0) -> LONG, so trade/cross direction d = -de. Route on r same-side-of-50 vs the BREACH de
    (inclusive): same-side on EITHER TF LATCHES branch-A (x/m × Mage, dir d; preferred, one-way, never demotes);
    before the latch, not-same-side -> branch-B (x OOB, x×m).
    a_variant selects the A trigger: 'x' = x×Mage, 'm' = m×Mage, 'both' = either. PER-TF, each independently.

    SETUP LATCH (Joe 0727): the setup latches at i0 and holds until it fires branch A/B or hs60x breaches the
    OPPOSING boundary — there is NO time cap on when the cross may come (the old 5h cap was inference).
    RGATE LATCH (Joe 0727): once the gate line is same-side of 50 it LATCHES for the setup's life; a cross before
    the latch is SKIPPED, not fatal (the old per-bar test + `break` was inference).
    Returns [(trigger_i, tf, branch), ...]; trace=True -> (result, events) where events carries the RGATE latch
    bar and the firing cross-pair so a report reads THIS walk instead of re-deriving it."""
    d = -de                                            # trade/cross direction = reversal of the breach (hi->short, lo->long)
    opp = (hs <= LO) if de > 0 else (hs >= HI)                     # opposing-side hs60x OOB releases the setup
    u = np.flatnonzero(opp & (np.arange(n) > i0))
    unl = int(u[0]) if len(u) else n                               # no opposing breach -> scan to end of tape
    # branch A is a LATCH from EITHER TF (Joe 0726): once ANY TF's r is same-side of 50 (vs breach de), commit to A
    # (preferred) — its A-cross wins the race across TFs. Before the latch, branch B (x OOB, x×m) is eligible. One trade.
    SS = {}; Ax = {}; Am = {}; A = {}; B = {}; MgO = {}
    Z = np.zeros(n, bool)
    for tf in HTFS:
        x, m, Mg, r = L[tf]['x'], L[tf]['m'], L[tf]['M'], L[tf]['r']
        SS[tf] = _r_same_side(r, de)                               # per-bar: r same-side of 50 vs breach de
        MgO[tf] = (Mg >= HI) | (Mg <= LO)                          # this TF's Mage OOB
        Ax[tf] = _wcross(x, Mg, d, wob) if a_variant in ('x', 'both') else Z
        Am[tf] = _wcross(m, Mg, d, wob) if a_variant in ('m', 'both') else Z
        A[tf] = Ax[tf] | Am[tf]                                    # kept split so the fire can name its cross pair
        B[tf] = _wcross(x, m, d, wob) & ((x >= HI) | (x <= LO))
    hits = []; ev = []; latched_A = False; rg = False               # RGATE line = _gater (k10/4/11 r at GATE_TF), both branches
    for i in range(i0, unl):                                       # setup latched i0 .. opposing hs60x breach (exclusive)
        if any(SS[tf][i] for tf in HTFS):                          # r same-side of breach on EITHER TF -> latch A
            latched_A = True                                       # Joe 0727: A is PREFERRED and LATCHES (one-way B->A, never demotes)
        if not rg and _r_same_side(_gater[i], de):                 # RGATE latches on the first same-side bar and HOLDS
            rg = True; ev.append((i, 'rgate', None, None, float(_gater[i])))
        ok = rg or not RGATE
        if latched_A:                                              # once A, stay A for the rest of the walk
            if A_MAGE_OOB and not any(MgO[tf][i] for tf in HTFS):  # gate: need s15 OR s22 Mage OOB for an A-fire
                continue
            fired = next((tf for tf in HTFS if A[tf][i]), None)    # A preferred: first A-cross across TFs wins (race)
            if fired is not None and ok:
                ev.append((i, 'fire', fired, 'x*Mage' if Ax[fired][i] else 'm*Mage', None))
                hits.append((i, fired, 'A')); break
        else:                                                      # not same-side this bar -> branch B (x OOB) eligible
            fired = next((tf for tf in HTFS if B[tf][i]), None)
            if fired is not None and ok:
                ev.append((i, 'fire', fired, 'x*m', None))
                hits.append((i, fired, 'B')); break
    res = hits
    if gate or fin:                                                # chain: provisional -> [s3s4 gate] -> [finisher] -> entry
        out = []                                                   # fin: 0=off/1=gcs5/2=2-stage · gate: apply s3s4 BEFORE finisher
        for i, tf, br in hits:
            k = i
            if gate:                                               # s3s4 gate must open first (else drop)
                k = s3s4_gate(k, de)
                if k is None:
                    continue
            if fin:                                                # then the finisher refines forward
                k = finish(k, de, two_stage=(fin == 2))
                if k is None:
                    continue
            out.append((k, tf, br))
        res = out
    return (res, ev) if trace else res


def qualify_in(S, E):
    """qualified onsets with onset-time in [S,E). -> [(i, de)]"""
    return [(i, de) for i, de in qualify() if S <= te[i] < E]


def deduped_trades(days, wob=AB_CROSS_WOB, a_variant='both', fin=False, gate=False):
    """Run the mechanic across day-windows [(S,E),...], collapse trades sharing a (trigger_ts, tf) — the
    overlapping-onset duplicates — to one. fin: 0/1/2 finisher stages; gate: s3s4 gate before finisher. -> dict{(trig_ts,tf):dir}."""
    tr = {}
    for S, E in days:
        for i, de in qualify_in(S, E):
            for ti, tf, br in trigger(i, de, wob, a_variant, fin=fin, gate=gate):
                tr[(int(te[ti]), tf)] = -de            # dedup key = trigger bar + TF; dir = -de (reversal of breach)
    return tr


def setups(S, E):
    """qualified onsets in [S,E) with per-TF triggers. -> [(onset_i, de, [(ti,tf,br),...])]"""
    out = []
    for i, de in qualify():
        if S <= te[i] < E:
            out.append((i, de, trigger(i, de)))
    return out


if __name__ == '__main__':
    D0 = int(dt.datetime(2026, 6, 12, tzinfo=dt.timezone.utc).timestamp() * 1000)
    if len(sys.argv) >= 3 and sys.argv[1][:4].isdigit():
        d0 = dt.datetime.strptime(sys.argv[1] + ' ' + sys.argv[2], '%Y-%m-%d %H:%M').replace(tzinfo=dt.timezone.utc)
        hrs = float(sys.argv[3]) if len(sys.argv) > 3 else 48
        S = int(d0.timestamp() * 1000); E = int(S + hrs * 3600 * 1000)
        sc = True
    else:
        S, E = D0, D0 + 24 * 3600 * 1000; sc = False           # default: 06-12 diagnostic vs examples
    print('=== past-50 mechanic | %s .. %s | event tape, wob=%d, dwell=%ds ===' % (
        f(int(np.searchsorted(te, S))), f(min(int(np.searchsorted(te, E)), n - 1)), AB_CROSS_WOB, DWELL_S))
    rows = setups(S, E)
    nets = {-1: [], 1: []}
    for oi, de, trig in rows:
        d = -de
        if not trig:
            print('  onset %s  s4M-exh %+d -> NO TRIGGER in 5h' % (f(oi), de)); continue
        for ti, tf, br in trig:                                    # per-TF: each fires its own trade
            line = 'onset %s  exh %+d -> TRIGGER %s  s%d  Branch %s  (trade %s)' % (
                f(oi), de, f(ti), tf, br, 'LONG' if d > 0 else 'SHORT')
            if sc:
                _, mfe, mae = lab.score(int(te[ti]), d); nets[d].append(mfe - mae)
                line += '  net %+.2f' % (mfe - mae)
            print('  ' + line)
    if sc:
        alln = nets[-1] + nets[1]
        if alln:
            import numpy as _np
            print('--- %d trades | net(med) %+.3f | win %.0f%% | SHORT %d LONG %d ---' % (
                len(alln), float(_np.median(alln)), 100 * _np.mean([x > 0 for x in alln]), len(nets[-1]), len(nets[1])))
