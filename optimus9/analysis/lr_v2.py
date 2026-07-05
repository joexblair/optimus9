"""
lr_v2.py (Joe 0630) — the prediction-gated pl-cascade v2 (docs/lr_cascade_design.md §v2). Built ALONGSIDE
the baseline lr.py (lr_detect untouched) until proven, then integrated. SRP nodes, plumbed:

    arm (s5m OR s5r) → gate_open (3 producers: predict / reverse / ib-clear) → finisher (qualify + trigger) → entries

Each node is a pure producer or a verdict — no fusion (the footwork riff). Build order:
  [1] s5r_arm        — the divergence arm producer            ← THIS
  [2] s5m arm        — straight-breach arm (lr_setups, arm=s5m; needs the 0.65 re-clone + s7-exit test)
  [3] gate_open      — predict_events / reverse_events / ib_clear → the open verdict (reason a/b/c)
  [4] finisher       — window-walker (4×30s lookback + 2×30s fwd) → qualify (s30a+s15a) + trigger (s30M-wob)
  [5] wire + measure
"""
import numpy as np
from optimus9.compute.breaching_line import predict_breach
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.constants import FENCE_HI, FENCE_LO
from optimus9.analysis.lr import _roll_or, BASE_TF


def s5r_arm(W, cfg, slip=15):
    """[1] s5r DIVERGENCE arm producer. s5r sits OOB on the side *opposing* the breach (slip fence =
    hi-slip / lo+slip = 70/30); when s4m breaches OOB on that opposing (leg / trade-breach) side, s4m's
    OOB travel pulls s5r back to the leg → arm. Stoch-RSI veer: as a leg's momentum slows, the stoch veers
    off it — that pull is the signal.

    Emits [(bar_i, es, bd)] — es = the s4m breach side, bd = -es = the trade side. Closed-bar. PURE producer,
    no gate/finisher verdict. e.g. s4m low + s5r ≥70 → LONG. TODO: source `slip` from lp_config (no-hardcode)."""
    ts = W.ts; n = len(ts); hi, lo = cfg.hi, cfg.lo
    fence_hi, fence_lo = hi - slip, lo + slip            # 70 / 30 — s5r's opposing-side OOB fence
    s4m = W._line('s4m'); s5r = W._line('s5r')
    arms = []
    for i in range(1, n):
        s4_lo = s4m[i] <= lo and s4m[i - 1] > lo         # fresh s4m LOW breach (the leg)
        s4_hi = s4m[i] >= hi and s4m[i - 1] < hi         # fresh s4m HIGH breach
        if s4_lo and s5r[i] >= fence_hi:                 # low leg + s5r high opposing → LONG
            arms.append((i, -1, 1))
        elif s4_hi and s5r[i] <= fence_lo:               # high leg + s5r low opposing → SHORT
            arms.append((i, 1, -1))
    return arms


def s5m_arm(W, cfg):
    """Straight-breach arm — s5m crosses OOB (closed) → arm; trade = the reversal (bd = -es).
    Emits [(bar_i, es, bd)]. On the CURRENT 0.4-multi s5m until the 0.65 re-clone (task #45)."""
    ts = W.ts; n = len(ts); hi, lo = cfg.hi, cfg.lo
    s5m = W._line('s5m')
    sign = np.where(s5m >= hi, 1, np.where(s5m <= lo, -1, 0))
    return [(i, int(sign[i]), -int(sign[i])) for i in range(1, n) if sign[i] != 0 and sign[i] != sign[i - 1]]


def v2_arm(W, cfg, horizon=None):
    """[2] The v2 ARM = s5m straight-breach OR s5r divergence, unified → setups [(i, es, bd, cap, src)].
    cap = the arm's life = min(OPPOSITE-side s5m breach, i + horizon) (Joe 0704, opt-a): the arm cancels the
    moment s5m breaches the other side (a hi-breach kills a lo-arm, and vice-versa); the 1.5h horizon stays a
    backstop. Same-bar opposite-side conflict → **s5m wins** (setdefault)."""
    horizon = horizon or cfg.horizon
    n = len(W.ts); hi, lo = cfg.hi, cfg.lo
    s5m = W._line('s5m'); sign = np.where(s5m >= hi, 1, np.where(s5m <= lo, -1, 0))
    idx = np.arange(n)
    nxt_hi = np.minimum.accumulate(np.where(sign == 1, idx, n)[::-1])[::-1]   # next hi-breach bar >= k
    nxt_lo = np.minimum.accumulate(np.where(sign == -1, idx, n)[::-1])[::-1]  # next lo-breach bar >= k
    m = {i: (es, bd, 's5m') for i, es, bd in s5m_arm(W, cfg)}
    for i, es, bd in s5r_arm(W, cfg):
        m.setdefault(i, (es, bd, 's5r'))                 # s5m already set → s5m wins
    out = []
    for i, (es, bd, src) in sorted(m.items()):
        opp = (nxt_lo[i + 1] if es == 1 else nxt_hi[i + 1]) if i + 1 < n else n   # opposite-side breach = -es
        out.append((i, es, bd, min(opp, i + horizon), src))
    return out


def _slope_flip(line):
    """Closed-line direction flip: +1 = down→up turn, -1 = up→down, else 0 (flats carry the run).
    Vectorized (was an O(N) Python loop; bit-exact). NaN steps = flat (the loop's NaN>0 / NaN<0 are False)."""
    n = len(line); flip = np.zeros(n, np.int8)
    if n < 2:
        return flip
    dd = np.diff(line); ss = np.where(np.isnan(dd), 0, np.sign(dd)).astype(np.int8)
    idx = np.arange(len(ss)); nz = ss != 0
    lastidx = np.maximum.accumulate(np.where(nz, idx, -1))          # last nonzero-sign index ≤ j
    run = np.where(lastidx >= 0, ss[lastidx], 0).astype(np.int8)    # run sign through step j (0 pre-first)
    prev = np.empty(len(ss), np.int8); prev[0] = 0; prev[1:] = run[:-1]   # run sign just before step j
    flip[1:] = np.where(nz & (prev != 0) & (ss != prev), ss, 0).astype(np.int8)
    return flip


def gate_signals(W, cfg, gate_rev='s1M'):
    """[3] PRODUCER — per-bar signals the latch verdict consumes. MECHANISM CHOICES (surfaced for review):
    reverses = slope-flip · all-IB = s2r/s3r/s4r in-band · m-reversed (setup#2) = s3m/s4m slope-flip ·
    prediction gated by s{n}m OOB ("test while OOB"). gate_rev = the gate reversal Mage line (DATA, Joe 0704):
    's1M' (60s, default) or 's2M' (120s) — a sweep knob now both exist. Boundary-agnostic reversal."""
    hi, lo = cfg.hi, cfg.lo
    s3r, s3m, s3M = W._line('s3r'), W._line('s3m'), W._line('s3M')
    s4r, s4m, s4M = W._line('s4r'), W._line('s4m'), W._line('s4M')
    s2r = W._line('s2r')
    return {
        'pred3': predict_breach(s3r, s3m, s3M, hi, lo, FENCE_HI, FENCE_LO),
        'pred4': predict_breach(s4r, s4m, s4M, hi, lo, FENCE_HI, FENCE_LO),
        'brc3': np.where(s3r >= hi, 1, np.where(s3r <= lo, -1, 0)),     # s3r OOB side
        'brc4': np.where(s4r >= hi, 1, np.where(s4r <= lo, -1, 0)),
        's3m_oob': (s3m >= hi) | (s3m <= lo), 's4m_oob': (s4m >= hi) | (s4m <= lo),
        'rev3r': _slope_flip(s3r), 'rev4r': _slope_flip(s4r),          # r reversal (reverse-before-breach)
        'rev3m': _slope_flip(s3m), 'rev4m': _slope_flip(s4m),          # m reversal (setup#2)
        'rev2M': _slope_flip(W._line(gate_rev)),                       # gate Mage reversal (path c) — s1M/s2M
        # per-line OOB state — path 'a' fires when all 3 CROSS OOB→IB (a transition, not the static all-IB)
        'oob2': (s2r >= hi) | (s2r <= lo), 'oob3': (s3r >= hi) | (s3r <= lo), 'oob4': (s4r >= hi) | (s4r <= lo),
    }


def gate_open(W, cfg, setups, sig=None):
    """[3] VERDICT — the latch lifecycle over each arm setup. Returns [(i, es, bd, open_k, reason)].
    reason 'a' all-IB → open · 'b' predicted then reversed BEFORE breaching → open · 'c' ready-to-reverse
    (setup#1 predicted-then-breached, or setup#2 no-predict + s{n}m reversed) → open on s2Mage reverse."""
    sig = sig or gate_signals(W, cfg)
    out = []
    for (i, es, bd, cap, src) in setups:
        p3 = p4 = b3 = b4 = rtr = False; xin2 = xin3 = xin4 = False; opened = None
        for k in range(i + 1, cap):
            if sig['oob2'][k - 1] and not sig['oob2'][k]: xin2 = True                 # s2r crossed OOB→IB
            if sig['oob3'][k - 1] and not sig['oob3'][k]: xin3 = True
            if sig['oob4'][k - 1] and not sig['oob4'][k]: xin4 = True
            if xin2 and xin3 and xin4:                                               # (a) all 3 crossed into IB
                opened = (k, 'a'); break
            if sig['pred3'][k] == es and sig['s3m_oob'][k]: p3 = True
            if sig['pred4'][k] == es and sig['s4m_oob'][k]: p4 = True
            if p3 and sig['brc3'][k] == es: b3 = True                                # predicted → breached (setup#1)
            if p4 and sig['brc4'][k] == es: b4 = True
            if (p3 and not b3 and sig['rev3r'][k] == bd) or (p4 and not b4 and sig['rev4r'][k] == bd):
                opened = (k, 'b'); break                                             # (b) reverse before breach
            # rtr is a LATCH (Joe 0703): once ready-to-reverse is signalled it PERSISTS, so s2Mage is free to
            # reverse and open the gate on ANY later bar (not a same-bar coincidence). The LTF finishers then time the entry.
            rtr = rtr or b3 or b4 or (not p3 and not p4 and (sig['rev3m'][k] == bd or sig['rev4m'][k] == bd))
            if rtr and sig['rev2M'][k] == bd:                                        # (c) ready-to-reverse → s2Mage
                opened = (k, 'c'); break
        if opened:
            out.append((i, es, bd, opened[0], opened[1], cap))
    return out


def _finisher_signal(W, cfg, Mn, mn, rn, rlb, rtf):
    """s30a/s15a-style finisher: M & m both OOB (same side) AND r OOB within the lookback (auto-scaled by TF,
    same as the baseline _gate_side). Returns (hi, lo) per-bar bool. value_mode-honoured via W.line."""
    M, m, r = W.line(Mn), W.line(mn), W.line(rn)
    lb = rlb * (rtf // BASE_TF)
    hi = (M >= cfg.hi) & (m >= cfg.hi) & _roll_or(r >= cfg.hi, lb)
    lo = (M <= cfg.lo) & (m <= cfg.lo) & _roll_or(r <= cfg.lo, lb)
    return hi, lo


def s30M_wob(W, cfg, wob_n=2):
    """The s30M TRIGGER — closed-bar slope turn held `wob_n` consecutive bd-steps (the spec's "2-wob"). The
    std wobslay is dead on the closed step-line (flats break strict-monotonic); this is the slope-flip + N-bar
    confirm — i.e. the SAME mechanic the kernel-AB debounce previewed. +1 = up-turn confirmed, -1 = down."""
    s = W._line('s30M'); d = np.diff(s); out = np.zeros(len(s), np.int8); cur = 0
    for k in range(1, len(s)):
        st = d[k - 1]
        if st > 0:
            cur = cur + 1 if cur > 0 else 1
        elif st < 0:
            cur = cur - 1 if cur < 0 else -1
        if cur == wob_n:
            out[k] = 1
        elif cur == -wob_n:
            out[k] = -1
    return out


def _finish(s30hi, s30lo, s15hi, s15lo, side, anchor, release, cap):
    """SHARED finisher core (entry + exit — one responsibility, two callers). LATCH s30a AND s15a on `side`
    (+1 hi / −1 lo) from `anchor` onward; they breach at their own times, the latch carries each. DELATCH
    (fire) at `max(latched, release)` — both pre-latched ⇒ fire at `release`; a late finisher ⇒ fire when it
    latches. Returns the trade/exit bar k, or None if both never latch in [anchor, cap)."""
    s30 = s30hi if side == 1 else s30lo
    s15 = s15hi if side == 1 else s15lo
    g30 = g15 = False
    for k in range(anchor, cap):
        g30 = g30 or bool(s30[k]); g15 = g15 or bool(s15[k])
        if g30 and g15:
            return max(k, release)
    return None


def finisher(W, cfg, opens):
    """[4] FINISHER (LATCH model) — ENTRY caller of the shared `_finish` core: latch s30a+s15a on the es side
    from the ARM (i), delatch at the gate-open (ok). s30M is just a component of the s30a latch (no separate wob
    trigger). NO drop — every gate-open trades once both latch. Returns [(trade_ms, es, bd, trade_k)].
    r-lookback split (Joe 0703): s30a honours cfg.s30r_lb, s15a honours cfg.s15r_lb — two independent DB knobs
    (lp_s30r_lb / lp_s15r_lb), how far back each scans for a same-side r breach."""
    ts = W.ts
    s30hi, s30lo = _finisher_signal(W, cfg, 's30M', 's30m', 's30r', cfg.s30r_lb, 30)
    s15hi, s15lo = _finisher_signal(W, cfg, 's15M', 's15m', 's15r', cfg.s15r_lb, 15)
    ent = []
    for (i, es, bd, ok, r, cap) in opens:
        tk = _finish(s30hi, s30lo, s15hi, s15lo, es, i, ok, cap)
        if tk is not None:
            ent.append((int(ts[tk]), es, bd, tk))
    return ent


def _mage_rev(line, wob_n):
    """Boundary-agnostic reversal detector. wob_n<=0 → slope-flip (first turn); wob_n>=1 → the turn is
    confirmed only after wob_n consecutive same-direction steps (semantics-B: flats extend the run)."""
    if wob_n <= 0:
        return _slope_flip(line)
    n = len(line); out = np.zeros(n, np.int8)                       # vectorized (was O(N) loop; bit-exact)
    if n < 2:
        return out
    dd = np.diff(line); ss = np.where(np.isnan(dd), 0, np.sign(dd)).astype(np.int8)   # NaN = flat (extends run)
    idx = np.arange(len(ss)); nz = ss != 0
    run = np.where(np.maximum.accumulate(np.where(nz, idx, -1)) >= 0,
                   ss[np.maximum.accumulate(np.where(nz, idx, -1))], 0).astype(np.int8)
    prevrun = np.empty(len(ss), np.int8); prevrun[0] = 0; prevrun[1:] = run[:-1]
    startidx = np.maximum.accumulate(np.where(run != prevrun, idx, -1))   # last run-start (dir change/first)
    cur = np.where(startidx >= 0, run * (idx - startidx + 1), 0)          # signed run-length (flats extend)
    out[1:] = np.where(cur == wob_n, 1, np.where(cur == -wob_n, -1, 0)).astype(np.int8)
    return out


def s_qualify(W, cfg, mn, Mn, rn, r_lb):
    """[4v2·PRODUCER] Mage-anchored qualify for one TF line-set (Joe 0704). s{TF}a qualifies at the s{TF}Mage
    reversal (wob cfg.fin_mage_wob) toward the trade side, with m OOB (+ M OOB unless cfg.fin_s30M_oob=0 →
    m-only) and a same-side OOB r within r_lb base-bars back. Returns (qhi, qlo): es-high (bd short) / es-low
    (bd long) qualify bars. value_mode-honoured via W.line (emerging = causal)."""
    m, M, r = W.line(mn), W.line(Mn), W.line(rn)
    rlb = r_lb * (W._ls.resolve(rn)[0] // 5)          # r_lb is in the r-line's OWN TF bars → convert to base(5s) bars
    revM = _mage_rev(M, cfg.fin_mage_wob); hi, lo = cfg.hi, cfg.lo; strict = bool(cfg.fin_s30M_oob)
    n = len(M); qhi = np.zeros(n, bool); qlo = np.zeros(n, bool); r_hi, r_lo = r >= hi, r <= lo
    for k in range(n):
        if revM[k] == -1 and m[k] >= hi and (M[k] >= hi or not strict) and r_hi[max(0, k - rlb):k + 1].any():
            qhi[k] = True
        if revM[k] == 1 and m[k] <= lo and (M[k] <= lo or not strict) and r_lo[max(0, k - rlb):k + 1].any():
            qlo[k] = True
    return qhi, qlo


def q1_gate(qA, qB, w0, w1):
    """[4v2·VERDICT] Ordered latch — both A (fast/LTF) and B (slow/HTF) must qualify in [w0,w1). Returns the
    Q1-complete bar = max of the two first-qualifies (LTF banks first, HTF completes it), or None."""
    jA = next((k for k in range(w0, w1) if qA[k]), None)
    jB = next((k for k in range(w0, w1) if qB[k]), None)
    return max(jA, jB) if (jA is not None and jB is not None) else None


def fin_trigger(revT, bd, q1, cap):
    """[4v2·VERDICT] First reversal on the trigger line toward bd at/after Q1 → the entry bar (or None)."""
    return next((k for k in range(q1, cap) if revT[k] == bd), None)


def finisher_v2(W, cfg, opens, trig_line='gcs5M', window='lookback'):
    """[4v2·WIRE] Mage-anchored ordered-qualify finisher (Joe 0704). Q1 = s15a banks → s30a (ordered latch,
    each honouring its own r_lb); trigger = a reversal on `trig_line` toward bd after Q1. trig_line = DATA
    (gcs5M now; gcs1M post-1s-tape — never baked). `window` (Joe 0704): 'lookback' = 7×30s back from gate-open
    (the spec) · 'forward' = build from the arm forward (arm-delay) · 'both' = union (both proven profitable).
    Returns [(trade_ms, es, bd, trade_k)]; caller dedups."""
    ts = W.ts
    q15h, q15l = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
    q30h, q30l = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
    revT = _mage_rev(W.line(trig_line), cfg.fin_mage_wob)
    wins = {'lookback': ('lb',), 'forward': ('fw',), 'both': ('lb', 'fw')}[window]
    ent = []
    for (i, es, bd, ok, r, cap) in opens:
        qA, qB = (q15h, q30h) if es == 1 else (q15l, q30l)
        for wn in wins:
            w0, w1 = (max(0, ok - cfg.fin_lb), min(cap, ok + cfg.fin_fwd)) if wn == 'lb' \
                else (i, min(cap, i + cfg.fin_lb + cfg.fin_fwd))
            q1 = q1_gate(qA, qB, w0, w1)
            if q1 is None:
                continue
            tk = fin_trigger(revT, bd, q1, cap)
            if tk is not None:
                ent.append((int(ts[tk]), es, bd, tk))
    return ent


def _stale(W, cfg, setups, sig=None):
    """Flow-2 STALE-EXIT (AB toggle): at the arm bar, s2r AND s3r AND s4r all already IB → drop the setup
    (the move resolved before we could act). Returns the kept setups."""
    sig = sig or gate_signals(W, cfg)
    return [s for s in setups if not (not sig['oob2'][s[0]] and not sig['oob3'][s[0]] and not sig['oob4'][s[0]])]


def v2_walk(W, cfg, stale_exit=False):
    """[5] WIRE — arm → (stale_exit?) → gate_open → finisher → entries. stale_exit = the flow-2 AB toggle.
    Dedup by trade bar: two arm setups can collapse to the same gate-open→finisher trade — one trade, once."""
    setups = v2_arm(W, cfg)
    sig = gate_signals(W, cfg)
    if stale_exit:
        setups = _stale(W, cfg, setups, sig)
    seen, out = set(), []
    for e in finisher(W, cfg, gate_open(W, cfg, setups, sig)):
        if e[3] not in seen:
            seen.add(e[3]); out.append(e)
    return out


def oob_2_oob(line, hi, lo):
    """[AD·PRODUCER] Per bar: has `line` swept from the OPPOSITE OOB to THIS OOB with no return between?
    dir_hi[k] = came low→high directly (holds until it re-touches low); dir_lo = mirror. A causal impulse-leg
    / no-retracement detector (an ADX substitute) for the arm-delay big-leg gate (Joe 0704)."""
    n = len(line); idx = np.arange(n)                              # vectorized (was O(N) loop; bit-exact)
    th = line >= hi; tl = line <= lo                               # NaN → both False (carry state), as the loop
    ext = np.where(th, 1, np.where(tl, -1, 0)).astype(np.int8)
    fillidx = np.maximum.accumulate(np.where(ext != 0, idx, -1))
    fill = np.where(fillidx >= 0, ext[fillidx], 0).astype(np.int8)
    last_before = np.empty(n, np.int8)
    if n:
        last_before[0] = 0
    if n > 1:
        last_before[1:] = fill[:-1]                                # last extreme strictly before k
    ls_dh = np.maximum.accumulate(np.where(th & (last_before == -1), idx, -1))   # dh SET at lo→hi
    ls_dl = np.maximum.accumulate(np.where(tl & (last_before == 1), idx, -1))    # dl SET at hi→lo
    lr_dh = np.maximum.accumulate(np.where(tl, idx, -1))                          # dh RESET at any lo touch
    lr_dl = np.maximum.accumulate(np.where(th, idx, -1))                          # dl RESET at any hi touch
    return ls_dh > lr_dh, ls_dl > lr_dl


def bigleg_gate(W, cfg):
    """[AD·VERDICT] Big-leg condition per side (Joe 0704): s5Mage AND s7Mage each travelled directly to the es
    side, AND s7r predicted-or-breached (== es) — a strong impulse leg still under momentum. Returns
    (cond_hi, cond_lo) per-bar bool for es=+1 / es=-1. Lines value_mode-honoured (emerging = causal)."""
    hi, lo = cfg.hi, cfg.lo
    s5M, s7M, s7m, s7r = W.line('s5M'), W.line('s7M'), W.line('s7m'), W.line('s7r')
    d5h, d5l = oob_2_oob(s5M, hi, lo); d7h, d7l = oob_2_oob(s7M, hi, lo)
    p7 = predict_breach(s7r, s7m, s7M, hi, lo, FENCE_HI, FENCE_LO)
    return (d5h & d7h & ((s7r >= hi) | (p7 == 1)), d5l & d7l & ((s7r <= lo) | (p7 == -1)))


def arm_delay(W, cfg, setups):
    """[AD·VERDICT] Dynamic arm-delay (Joe 0704) — Elder's 'tide' screen. Per arm setup: if the big-leg gate
    fires (a strong leg still running), HOLD the arm to the s5Mage reversal (wob cfg.arm_wob) toward bd — don't
    enter the ripple before the tide turns; else keep the breach arm. Returns re-timed setups. NOTE: the spec's
    unconditional 'base = s5m reversal' for non-big-leg is NOT here (the validated build kept the breach arm)."""
    ch, cl = bigleg_gate(W, cfg); rev5M = _mage_rev(W.line('s5M'), cfg.arm_wob); out = []
    for (i, es, bd, cap, src) in setups:
        cond = ch if es == 1 else cl
        kc = next((k for k in range(i + 1, cap) if cond[k]), None)
        if kc is None:
            out.append((i, es, bd, cap, src)); continue
        da = next((k for k in range(kc, cap) if rev5M[k] == bd), None)
        out.append((da if da is not None else i, es, bd, cap, src))
    return out


def fin_unlatch(q15, q30, i, cap, fin_lb, fin_fwd):
    """[4v2·M1] Finisher lookback on arm unlatch (Joe 0704). If s15a AND s30a were both qualified in the
    proximal box [unlatch-fin_lb, unlatch+fin_fwd], the trade fires on the NEXT same-side s15a at/after the
    unlatch (the unlatch bar itself isn't an optimal entry). Returns the trade bar, or None."""
    w0, w1 = max(0, i - fin_lb), min(cap, i + fin_fwd + 1)
    if q15[w0:w1].any() and q30[w0:w1].any():
        return next((k for k in range(i, cap) if q15[k]), None)
    return None


def fin_gate(q15, q30, ok, cap):
    """[4v2·M2] Post-s3s4-gate finisher (Joe 0704). After the s3s4 gate opens (ok), the finishers get a chance
    with NO time limit (until the arm cancels = cap); trade the bar BOTH s15a + s30a are qualified. Returns the
    trade bar, or None. (No gcs5M trigger — 'trade when they qualify'.)"""
    j15 = next((k for k in range(ok, cap) if q15[k]), None)
    j30 = next((k for k in range(ok, cap) if q30[k]), None)
    return max(j15, j30) if (j15 is not None and j30 is not None) else None


def v2_walk_ad(W, cfg):
    """[5·AD·WIRE] The arm-delay stack (Joe 0704, o9-live producer): arm → arm_delay-s7r (big-leg → s5Mage
    reversal / unlatch) → per arm: M1 finisher-lookback-on-arm-unlatch, else (if the s3s4 gate opened) M2
    post-gate finisher. Trade placed on the next same-side s15a (M1) / both-qualified bar (M2). Dedup by bar."""
    setups = v2_arm(W, cfg)
    if cfg.arm_bigleg:
        setups = arm_delay(W, cfg, setups)
    opens = {o[0]: o for o in gate_open(W, cfg, setups)}                  # arm bar -> gate-open tuple
    q15h, q15l = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
    q30h, q30l = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
    ts = W.ts; seen, out = set(), []
    for (i, es, bd, cap, src) in setups:
        q15, q30 = (q15h, q30h) if es == 1 else (q15l, q30l)             # qhi = short-side, qlo = long-side
        tk = fin_unlatch(q15, q30, i, cap, cfg.fin_lb, cfg.fin_fwd)      # M1
        if tk is None and i in opens:
            tk = fin_gate(q15, q30, opens[i][3], cap)                    # M2 (only if M1 didn't fire)
        if tk is not None and tk not in seen:
            seen.add(tk); out.append((int(ts[tk]), es, bd, tk))
    return out


def v2_walk_diag(W, cfg):
    """[DIAG·#54] Realtime-fidelity PROBE (Joe 0704-05) — NOT a real producer; swap in via StrategyLoop(producer=).
    Arm always UNLATCHED + s3s4/fin_gate always OPEN + fin_unlatch OFF → fire on the finisher signal so the live UI
    open-time can be eyeballed against the finisher bar (seam+301ms offset). cfg.fin_both=0 → fire on every s15a
    alone. fin_both=1 → require the s15a+s30a PAIR: fire at the pair-completion bar (the LATER qualifier), EITHER
    order, when the other finisher qualified within fin_lb+fin_fwd bars (the spec's proximal-box span). Causal —
    backward-only at the fire bar (a late s30a completes the pair at ITS bar, not the earlier s15a's). Side =
    finisher polarity."""
    q15h, q15l = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
    q30h, q30l = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
    ts = W.ts; both = bool(cfg.fin_both); win = cfg.fin_lb + cfg.fin_fwd; dd = cfg.fin_dedup; out = []
    for es, bd, q15, q30 in ((1, -1, q15h, q30h), (-1, 1, q15l, q30l)):        # (es,bd): qhi=short/Sell, qlo=long/Buy
        last = -(1 << 30)                                                      # last FIRED bar this side (dedup anchor)
        for k in range(len(ts)):
            if not both:
                fire = bool(q15[k])
            else:
                w0 = max(0, k - win)                                           # pair completes at k (later qualifier), either order
                fire = bool((q15[k] and q30[w0:k + 1].any()) or (q30[k] and q15[w0:k + 1].any()))
            if fire and (dd <= 0 or k - last >= dd):                           # fin_dedup=0 → every fire · >0 → one per umbrella
                out.append((int(ts[k]), es, bd, k)); last = k
    return sorted(out)


def v2_phase(W, cfg, in_position=0, exit_fam='s7'):
    """[AD·READOUT] Live cascade phase at the latest bar T (SRP: REPORTS state, never decides/enters — reuses the
    SAME arm→arm_delay→gate_open streams as v2_walk_ad, so the readout can't diverge from the entry producer).
    Three concurrent tracks composed like the terminal chip:
      arm   — the latest v2_arm setup whose window still covers T (s5m breach / s5r divergence)
      gate  — that arm's gate_open verdict: 'open' (reason a/b/c) once open_k<=T, else 'latched' (waiting)
      exit  — driven by the loop's live net side (in_position: +1/-1/0); the exit machine is watching to close
    tone = 'go' (gate-open or holding) · 'wait' (armed/latched) · 'idle' (flat) — drives the block colour."""
    T = len(W.ts) - 1
    setups = v2_arm(W, cfg)
    if cfg.arm_bigleg:
        setups = arm_delay(W, cfg, setups)
    opens = {s[0]: (s[3], s[4]) for s in gate_open(W, cfg, setups)}   # arm_bar -> (open_k, reason)
    arm = gate = greason = None
    live = [s for s in setups if s[0] <= T < s[3]]                    # arm windows still open at T
    if live:
        i, es, bd, cap, src = max(live, key=lambda s: s[0])          # the most-recent live arm
        arm = src
        if i in opens and opens[i][0] <= T:
            gate, greason = 'open', opens[i][1]
        else:
            gate = 'latched'
    tracks = []
    if arm:
        tracks.append(arm + ' armed')
    if gate == 'open':
        tracks.append('GATE OPEN ' + greason)
    elif gate == 'latched':
        tracks.append('gate latched')
    if in_position:
        tracks.append(exit_fam + ' exit-watch')
    tone = 'go' if (gate == 'open' or in_position) else 'wait' if arm else 'idle'
    return {'label': ' · '.join(tracks) if tracks else 'flat', 'tone': tone, 'arm': arm,
            'gate': gate, 'gate_reason': greason, 'in_position': bool(in_position),
            'exit': exit_fam if in_position else None}


def lr_exit_v2(W, cfg, entries, predict=True, gate_fam='s7', slip=0.0, rlb=19):
    """EXIT cascade = the entry machine pointed at the −es (favourable) extreme — ONE machine, two polarities.
    Per entry (tms, es, bd, tj), arm_side = bd:
      exit-arm : s5m breach on bd →
      gate     : {gate_fam}r predict-then-breach on bd (predict_breach over its m/M pair; `predict` toggles the
                 predict requirement — False = breach-only = the sweep's no-predict arm; `slip` moves the OOB
                 boundary INWARD by `slip` so a near-OOB curl still counts as a breach) →
      unlatch  : s5r reversal toward es (= −bd) — the curl predictor (s5r : {gate_fam}r :: s2M : s3r/s4r) →
      finisher : `_finish(side=bd, anchor=exit-arm, release=unlatch)` = the exit bar (the SAME latch finisher).
    AB knobs: gate_fam (s5/s6/s7 — the gate oscillator) · slip (boundary slip). SL floor (−cfg.sl%) every bar;
    no time cap. Returns [(trade_ms, exit_ms, bd, entry_px, exit_px, ret, reason)] — same shape as lr_exit."""
    ts, px, n = W.ts, W.px, len(W.ts)
    hi, lo = cfg.hi, cfg.lo
    ghi, glo = hi - slip, lo + slip                              # boundary slip: inward ⇒ easier gate breach
    s5m, s5r = W.line('s5m'), W.line('s5r')
    gr, gm, gM = W.line(f'{gate_fam}r'), W.line(f'{gate_fam}m'), W.line(f'{gate_fam}M')
    predg = predict_breach(gr, gm, gM, hi, lo, FENCE_HI, FENCE_LO)
    rev5 = _slope_flip(s5r)
    s30hi, s30lo = _finisher_signal(W, cfg, 's30M', 's30m', 's30r', rlb, 30)
    s15hi, s15lo = _finisher_signal(W, cfg, 's15M', 's15m', 's15r', rlb, 15)
    rows = []
    for tms, es, bd, tj in entries:
        entry_px = float(px[tj])
        arm = gate = unlatch = xk = None
        predicted = not predict                                  # predict off ⇒ gate fires on the breach alone
        ek = None; reason = 'end'
        for k in range(tj + 1, n):
            if (px[k] - entry_px) / entry_px * 100.0 * bd <= -cfg.sl:
                ek = k; reason = 'SL'; break
            if xk is not None:
                if k >= xk:
                    ek = k; reason = 'exit'; break
            elif arm is None:
                if (s5m[k] <= lo) if bd == -1 else (s5m[k] >= hi):
                    arm = k
            elif gate is None:
                if predg[k] == bd:
                    predicted = True
                s7b = (gr[k] <= glo) if bd == -1 else (gr[k] >= ghi)
                if predicted and s7b:
                    gate = k
            elif unlatch is None:
                if rev5[k] == es:                                # s5r reverses toward es = the curl unlatch
                    unlatch = k
                    xk = _finish(s30hi, s30lo, s15hi, s15lo, bd, arm, unlatch, n)
                    if xk is not None and k >= xk:               # both finishers already latched ⇒ exit now
                        ek = k; reason = 'exit'; break
        if ek is None:
            ek = n - 1
        exit_px = float(px[ek])
        ret = -cfg.sl if reason == 'SL' else (exit_px - entry_px) / entry_px * 100.0 * bd
        rows.append((tms, int(ts[ek]), bd, entry_px, exit_px, round(ret, 3), reason))
    return rows


def strand_rescue(W, cfg, entries, cascade_exits, fence_hi=80.0, fence_lo=20.0):
    """The SIDEWAYS-market exit (Joe 0701). For trades the cascade SL'd because s7r NEVER breaches (strands),
    the finishers take the **s5r curl at the favourable extreme** — because s7r is *invisible* (inside the 20/80
    fence), so no bigger move is coming and holding just bleeds into the SL. If at the curl s7r is *visible*
    (outside the fence, so it might yet breach), HOLD to the next same-side s5m breach and re-test. s5m-favourable
    guard on the exit (no adverse-side exits). Re-works only the SLs. Returns cascade_exits with strands rescued.
    NOTE: fence 80/20 = spec values; hoist to the DB (like the OOB boundary) later — see [[thresholds_constants]]."""
    ts, px, n = W.ts, W.px, len(W.ts)
    hi, lo = cfg.hi, cfg.lo
    s5m, s5r, s7r = W.line('s5m'), W.line('s5r'), W.line('s7r')
    rev5 = _slope_flip(s5r)
    exd = {x[0]: x for x in cascade_exits}
    out = []
    for tms, es, bd, tj in entries:
        x = exd[tms]
        if x[6] != 'SL':
            out.append(x); continue                              # only re-work the SLs
        kx = int(np.searchsorted(ts, x[1]))
        arm = next((j for j in range(tj + 1, kx + 1) if (s5m[j] <= lo if bd == -1 else s5m[j] >= hi)), None)
        breached = arm is not None and ((s7r[arm:kx + 1] <= lo).any() if bd == -1 else (s7r[arm:kx + 1] >= hi).any())
        if arm is None or breached:
            out.append(x); continue                              # not a strand — keep the SL
        entry_px = float(px[tj]); ek = None; j = arm
        while j <= kx:
            visible = (s7r[j] >= fence_hi) if bd == 1 else (s7r[j] <= fence_lo)
            adverse = (s5m[j] <= lo) if bd == 1 else (s5m[j] >= hi)
            if rev5[j] == es and visible:                        # s7r still in play → hold to the next s5m breach
                nb = next((q for q in range(j + 1, kx + 1) if (s5m[q] <= lo if bd == -1 else s5m[q] >= hi)), None)
                if nb is None:
                    break                                        # no next breach → let the SL stand
                j = nb; continue
            if rev5[j] == es and not adverse:                    # s7r invisible + s5m favourable → finishers exit
                ek = j; break
            j += 1
        if ek is None:
            out.append(x)                                        # no clean curl → keep the SL
        else:
            ret = (px[ek] - entry_px) / entry_px * 100.0 * bd
            out.append((tms, int(ts[ek]), bd, entry_px, float(px[ek]), round(ret, 3), 'strand'))
    return out
