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
from optimus9.constants import FENCE_HI, FENCE_LO


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
    cap = the setup window (i + horizon). Same-bar opposite-side conflict → **s5m wins** (setdefault).
    [TODO: window-level s5m-wins conflict + opposite-breach cap are refinements once gate_open needs them.]"""
    horizon = horizon or cfg.horizon
    n = len(W.ts)
    m = {i: (es, bd, 's5m') for i, es, bd in s5m_arm(W, cfg)}
    for i, es, bd in s5r_arm(W, cfg):
        m.setdefault(i, (es, bd, 's5r'))                 # s5m already set → s5m wins
    return [(i, es, bd, min(n, i + horizon), src) for i, (es, bd, src) in sorted(m.items())]


def _slope_flip(line):
    """Closed-line direction flip: +1 = down→up turn, -1 = up→down, else 0 (flats carry the run)."""
    d = np.diff(line); flip = np.zeros(len(line), np.int8); cur = 0
    for k in range(1, len(line)):
        s = d[k - 1]
        if s > 0:
            flip[k] = 1 if cur < 0 else 0; cur = cur + 1 if cur > 0 else 1
        elif s < 0:
            flip[k] = -1 if cur > 0 else 0; cur = cur - 1 if cur < 0 else -1
    return flip


def gate_signals(W, cfg):
    """[3] PRODUCER — per-bar signals the latch verdict consumes (s3r/s4r/s2M closed, per spec). MECHANISM
    CHOICES (surfaced for review): reverses = closed slope-flip · all-IB = s2r/s3r/s4r in-band · m-reversed
    (setup#2) = s3m/s4m slope-flip · prediction gated by s{n}m OOB ("test while OOB")."""
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
        'rev2M': _slope_flip(W._line('s2M')),                          # s2Mage reversal (path c)
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
        p3 = p4 = b3 = b4 = False; xin2 = xin3 = xin4 = False; opened = None
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
            rtr = b3 or b4 or (not p3 and not p4 and (sig['rev3m'][k] == bd or sig['rev4m'][k] == bd))
            if rtr and sig['rev2M'][k] == bd:                                        # (c) ready-to-reverse → s2Mage
                opened = (k, 'c'); break
        if opened:
            out.append((i, es, bd, opened[0], opened[1]))
    return out
