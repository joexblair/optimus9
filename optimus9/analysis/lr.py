"""
lr.py (Joe 0628) — the latch-release reversal cascade, FULLY DECOUPLED. The SHAPE (the state machine) lives
in lr_detect; the gate-sets are DATA (lr_gate/lr_gate_line), the knobs are DATA (lp_config), the OOB is DATA
(optimus9_system). Nothing baked in.

  lr_config(db) → LRConfig   — load gate-sets (by role) + knobs + OOB. One config source.
  lr_detect(W, cfg) → entries — THE STRATEGY: arm breach → wobslay reversal → (any active FINISHER re-breaches
                                AND all active BIAS gates agree) = the entry. Walks the gate-sets; emits only.
  lr_walk(W, entries, cfg)    — the BACKTEST verdict (MAE/MFE). Separate concern.

Gate-sets: a gate = lines (ic_pk → name) + per-line `check` (oob | liftoff | mid) + an op (AND|OR). Roles
combine: finishers OR'd · bias AND'd · arms each independent. Add a finisher = a row, no code (#decouple).
"""
import numpy as np
import pandas as pd
import datetime as dtm
from dataclasses import dataclass, field
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots

# fallback defaults (live values from lp_config / optimus9_system / lr_gate)
HI, LO = 85.0, 15.0
STEP = 30000
WOB_N, FLOOR, TARGET, HORIZON = 4, 8.0, 0.9, 90 * 12
BASE_TF = 5                                                  # base kline interval (s) — structural, not a knob


@dataclass
class LineRef:
    name: str                                               # ind_name (resolved from ic_pk)
    check: str                                              # oob | liftoff | mid
    tf: int                                                 # itf_seconds (liftoff lookback scales off this)


@dataclass
class Gate:
    role: str
    name: str
    op: str
    lines: list


@dataclass
class LRConfig:
    floor: float; wob_n: int; horizon: int; target: float
    swing_ms: int; swing_pct: float; bias_mid: float; s30r_lb: int
    hi: float; lo: float
    arms: list = field(default_factory=list)
    finishers: list = field(default_factory=list)
    biases: list = field(default_factory=list)


def lr_config(db):
    """Load the full lr config — gate-sets (active, by role) + knobs (lp_config) + OOB (optimus9_system).
    The ONE config source for rig + strat_review producer + o9-live. Lines by ic_pk (no hardcoded names)."""
    k = {r['name']: r['val'] for r in db.execute(
        "SELECT name, val FROM lp_config WHERE name IN ('lp_lr_floor','lp_lr_wob_n','lp_lr_horizon',"
        "'lp_lr_target','lp_lr_swing_ms','lp_lr_swing_pct','lp_lr_bias_mid','lp_s30r_lb')", fetch=True)}
    sb = db.execute("SELECT hi_boundary, lo_boundary FROM optimus9_system LIMIT 1", fetch=True)[0]
    roles = {'arm': [], 'finisher': [], 'bias': []}
    for g in db.execute("SELECT * FROM lr_gate WHERE lrg_active=1", fetch=True):
        lines = [LineRef(r['nm'], r['ch'], int(r['tf'])) for r in db.execute(
            "SELECT i.ind_name nm, l.lrgl_check ch, i.itf_seconds tf FROM lr_gate_line l "
            "JOIN vw_indicator_configs_live i ON i.ic_pk = l.lrgl_ic_pk WHERE l.lrgl_lrg_pk = %s",
            (g['lrg_pk'],), fetch=True)]
        roles[g['lrg_role']].append(Gate(g['lrg_role'], g['lrg_name'], g['lrg_op'], lines))
    return LRConfig(
        floor=k.get('lp_lr_floor', FLOOR), wob_n=int(k.get('lp_lr_wob_n', WOB_N)),
        horizon=int(k.get('lp_lr_horizon', HORIZON)), target=k.get('lp_lr_target', TARGET),
        swing_ms=int(k.get('lp_lr_swing_ms', STEP)), swing_pct=k.get('lp_lr_swing_pct', 0.9),
        bias_mid=k.get('lp_lr_bias_mid', 50.0), s30r_lb=int(k.get('lp_s30r_lb', 0)),
        hi=float(sb['hi_boundary']), lo=float(sb['lo_boundary']),
        arms=roles['arm'], finishers=roles['finisher'], biases=roles['bias'])


def _dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000)


def _roll_or(a, k):
    """Rolling OR over the current + k preceding bars (the liftoff lookback)."""
    out = a.copy()
    for s in range(1, int(k) + 1):
        out[s:] |= a[:-s]
    return out


def _gate_side(W, gate, cfg):
    """A gate's per-side activation: each line's `check`, combined by the gate's op → (hi, lo) bool arrays.
    Each line read via W.line (value_mode-honoured, #42). liftoff lookback auto-scales off the line's TF."""
    hi, lo = [], []
    for ln in gate.lines:
        v = W.line(ln.name)
        if ln.check == 'oob':
            hi.append(v >= cfg.hi); lo.append(v <= cfg.lo)
        elif ln.check == 'liftoff':
            lb = cfg.s30r_lb * (ln.tf // BASE_TF)
            hi.append(_roll_or(v >= cfg.hi, lb)); lo.append(_roll_or(v <= cfg.lo, lb))
        elif ln.check == 'mid':
            hi.append(v > cfg.bias_mid); lo.append(v < cfg.bias_mid)     # v = W.line (value_mode-honoured; s14M=closed)
    comb = np.all if gate.op == 'AND' else np.any
    return comb(hi, axis=0), comb(lo, axis=0)


def _finisher_active(W, cfg):
    """OR across active finisher gates → (hi, lo)."""
    n = len(W.ts); hi = np.zeros(n, bool); lo = np.zeros(n, bool)
    for g in cfg.finishers:
        ghi, glo = _gate_side(W, g, cfg); hi |= ghi; lo |= glo
    return hi, lo


def _bias_ok(W, cfg):
    """AND across active bias gates → (hi, lo). No bias gates → all-pass (un-gated)."""
    n = len(W.ts); hi = np.ones(n, bool); lo = np.ones(n, bool)
    for g in cfg.biases:
        ghi, glo = _gate_side(W, g, cfg); hi &= ghi; lo &= glo
    return hi, lo


def lr_detect(W, cfg, start_ms=None):
    """THE STRATEGY — walk the latch-release shape over the gate-sets. Returns [(trade_ms, es, bd, tj)].
    arm gate breaches OOB → armed; the arm line's wobslay reverses ≥ floor; then any active FINISHER
    re-breaches (same side) AND all active BIAS gates agree → entry. Emits entries only — no verdict."""
    ts = W.ts; n = len(ts)
    arm_line = cfg.arms[0].lines[0].name                     # the arm line (breach + wobslay)
    s6c = W._line(arm_line)                                   # CLOSED — the breach / arm
    s6 = W._line_emerging(arm_line)                           # emerging — the wobslay rides this
    sign = np.where(s6c >= cfg.hi, 1, np.where(s6c <= cfg.lo, -1, 0))
    wob = IC.wobble_slayer(s6, cfg.wob_n, cfg.hi, cfg.lo, anchored=True, strict=True)
    fin_hi, fin_lo = _finisher_active(W, cfg)
    bias_hi, bias_lo = _bias_ok(W, cfg)
    side_hi = fin_hi & bias_hi; side_lo = fin_lo & bias_lo    # finisher gated by bias = the entry side
    if start_ms is None:
        start_ms = int(ts[0])
    entries = []; i = 1
    while i < n:
        if sign[i] != 0 and sign[i] != sign[i - 1]:           # arm breach onset, side es
            es = int(sign[i]); rj = None
            for j in range(i, min(n, i + cfg.horizon)):
                if sign[j] == -es:
                    break
                if wob[j] == -es and j - cfg.wob_n >= 0 and abs(s6[j] - s6[j - cfg.wob_n]) >= cfg.floor:
                    rj = j; break                             # floor-gated wobslay reversal
            if rj is not None:
                side = side_hi if es == 1 else side_lo        # finisher = same side as the breach
                cap = next((k for k in range(rj + 1, min(n, rj + cfg.horizon)) if sign[k] == -es),
                           min(n, rj + cfg.horizon))
                tj = next((k for k in range(rj + 1, cap) if side[k] and not side[k - 1]), None)
                if tj is not None and int(ts[tj]) >= start_ms:
                    entries.append((int(ts[tj]), es, -es, int(tj)))
            i = next((k for k in range(i + 1, n) if sign[k] != es), n)
            continue
        i += 1
    return entries


def lr_walk(W, entries, cfg):
    """The BACKTEST VERDICT — MAE/MFE per entry to the favourable swing (cfg.swing_pct). Returns
    [(trade_ms, dt, es, bd, mae, mfe, mfe_ok, mfe_swing_side, price)]. Computes its own price/swing signals."""
    ts = W.ts
    idx30 = np.where(ts % cfg.swing_ms == 0)[0]; ts30 = ts[idx30]
    close30 = pd.Series(W.px[idx30]).ffill().bfill().to_numpy()
    piv = find_pivots(close30, cfg.swing_pct)
    rows = []
    for tms, es, bd, tj in entries:
        j = min(int(np.searchsorted(ts30, tms)), len(close30) - 1)
        fav = 'H' if bd == 1 else 'L'
        nxt = next((pi for pi, pk in piv if pi > j and pk == fav), None)
        nextpk = next((pk for pi, pk in piv if pi > j), None)
        mfe_side = int(nextpk == fav)
        seg = close30[j:(nxt + 1)] if nxt is not None else close30[j:]
        mfe = mae = 0.0
        if len(seg):
            d = (seg - close30[j]) / close30[j] * 100.0 * bd
            mfe = float(d.max()); mae = float(-d.min())
        rows.append((tms, _dts(tms), es, bd, round(mae, 3), round(mfe, 3), int(mfe >= cfg.target), mfe_side, float(W.px[tj])))
    return rows
