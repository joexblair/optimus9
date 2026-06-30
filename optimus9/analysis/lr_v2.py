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
