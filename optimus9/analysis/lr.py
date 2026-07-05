"""
lr.py (Joe 0628) — the latch-release reversal cascade, FULLY DECOUPLED. The SHAPE (the state machine) lives
in lr_detect; the gate-sets are DATA (lr_gate/lr_gate_line), the knobs are DATA (lp_config), the OOB is DATA
(optimus9_system). Nothing baked in.

  lr_config(db) → LRConfig   — load gate-sets (by role) + knobs + OOB. One config source.
  lr_detect(W, cfg) → entries — THE STRATEGY: arm breach → wobslay reversal → (any active FINISHER re-breaches
                                AND all active BIAS gates agree) = the entry. Walks the gate-sets; emits only.
  lr_walk(W, entries, cfg)    — the BACKTEST verdict (MAE/MFE). Separate concern.

Gate-sets: a gate = lines (ic_pk → name) + per-line `check` (oob | lookback | mid) + an op (AND|OR). Roles
combine: finishers OR'd · bias AND'd · arms each independent. Add a finisher = a row, no code (#decouple).
"""
import numpy as np
import pandas as pd
import datetime as dtm
from dataclasses import dataclass, field, replace
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots
from optimus9.compute.breaching_line import predict_breach
from optimus9.constants import FENCE_HI, FENCE_LO

# fallback defaults (live values from lp_config / optimus9_system / lr_gate)
HI, LO = 85.0, 15.0
STEP = 30000
WOB_N, FLOOR, TARGET, HORIZON = 4, 8.0, 0.9, 90 * 12
BASE_TF = 5                                                  # base kline interval (s) — structural, not a knob


@dataclass
class LineRef:
    name: str                                               # ind_name (resolved from ic_pk)
    check: str                                              # oob | lookback | mid
    tf: int                                                 # itf_seconds (lookback window scales off this)
    lookback: int = 0                                       # per-line lookback bars (0 → fall back to lp_s30r_lb)


@dataclass
class Gate:
    role: str
    name: str
    op: str
    lines: list


@dataclass
class LRConfig:
    floor: float; wob_n: int; horizon: int; target: float
    swing_ms: int; swing_pct: float; bias_mid: float; s30r_lb: int; s15r_lb: int
    hi: float; lo: float
    exit_rlb: int = 22; sl: float = 0.5; curl_n: int = 1
    fin_mage_wob: int = 0; fin_s30M_oob: int = 1; fin_lb: int = 42; fin_fwd: int = 12
    arm_wob: int = 2; arm_bigleg: int = 1; fin_both: int = 1; fin_dedup: int = 0
    arms: list = field(default_factory=list)
    finishers: list = field(default_factory=list)
    gates: list = field(default_factory=list)
    exit_finishers: list = field(default_factory=list)


def _gate_from_row(db, g):
    """One lr_gate row → a Gate (its lines resolved ic_pk → name+TF+check+per-line lookback)."""
    lines = [LineRef(r['nm'], r['ch'], int(r['tf']), int(r['lb'] or 0)) for r in db.execute(
        "SELECT i.ind_name nm, l.lrgl_check ch, i.itf_seconds tf, l.lrgl_lookback lb FROM lr_gate_line l "
        "JOIN vw_indicator_configs_live i ON i.ic_pk = l.lrgl_ic_pk WHERE l.lrgl_lrg_pk = %s",
        (g['lrg_pk'],), fetch=True)]
    return Gate(g['lrg_role'], g['lrg_name'], g['lrg_op'], lines)


def lr_config(db):
    """Load the full lr config — gate-sets (active, by role) + knobs (lp_config) + OOB (optimus9_system).
    The ONE config source for rig + strat_review producer + o9-live. Lines by ic_pk (no hardcoded names).
    exit_finishers = ALL finisher gates (active+inactive) — the exit ANDs them regardless of entry-active."""
    k = {r['name']: r['val'] for r in db.execute(
        "SELECT name, val FROM lp_config WHERE name IN ('lp_lr_floor','lp_lr_wob_n','lp_lr_horizon',"
        "'lp_lr_target','lp_lr_swing_ms','lp_lr_swing_pct','lp_lr_bias_mid','lp_s30r_lb','lp_s15r_lb',"
        "'lp_lr_exit_rlb','lp_lr_sl','lp_lr_curl_n',"
        "'lp_fin_mage_wob','lp_fin_s30M_oob','lp_fin_lb','lp_fin_fwd',"
        "'lp_arm_wob','lp_arm_bigleg','lp_fin_both','lp_fin_dedup')", fetch=True)}
    sb = db.execute("SELECT hi_boundary, lo_boundary FROM optimus9_system LIMIT 1", fetch=True)[0]
    roles = {'arm': [], 'finisher': [], 'gate': []}
    for g in db.execute("SELECT * FROM lr_gate WHERE lrg_active=1", fetch=True):
        roles[g['lrg_role']].append(_gate_from_row(db, g))
    exit_fins = [_gate_from_row(db, g) for g in
                 db.execute("SELECT * FROM lr_gate WHERE lrg_role='finisher' ORDER BY lrg_name", fetch=True)]
    return LRConfig(
        floor=k.get('lp_lr_floor', FLOOR), wob_n=int(k.get('lp_lr_wob_n', WOB_N)),
        horizon=int(k.get('lp_lr_horizon', HORIZON)), target=k.get('lp_lr_target', TARGET),
        swing_ms=int(k.get('lp_lr_swing_ms', STEP)), swing_pct=k.get('lp_lr_swing_pct', 0.9),
        bias_mid=k.get('lp_lr_bias_mid', 50.0), s30r_lb=int(k.get('lp_s30r_lb', 0)),
        s15r_lb=int(k.get('lp_s15r_lb', k.get('lp_s30r_lb', 0))),
        exit_rlb=int(k.get('lp_lr_exit_rlb', 22)), sl=float(k.get('lp_lr_sl', 0.5)),
        curl_n=int(k.get('lp_lr_curl_n', 1)),
        fin_mage_wob=int(k.get('lp_fin_mage_wob', 0)), fin_s30M_oob=int(k.get('lp_fin_s30M_oob', 1)),
        fin_lb=int(k.get('lp_fin_lb', 42)), fin_fwd=int(k.get('lp_fin_fwd', 12)),
        arm_wob=int(k.get('lp_arm_wob', 2)), arm_bigleg=int(k.get('lp_arm_bigleg', 1)), fin_both=int(k.get('lp_fin_both', 1)),
        fin_dedup=int(k.get('lp_fin_dedup', 0)),
        hi=float(sb['hi_boundary']), lo=float(sb['lo_boundary']),
        arms=roles['arm'], finishers=roles['finisher'], gates=roles['gate'], exit_finishers=exit_fins)


def _dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000)


def _roll_or(a, k):
    """Rolling OR over the current + k preceding bars (the lookback window)."""
    out = a.copy()
    for s in range(1, int(k) + 1):
        out[s:] |= a[:-s]
    return out


def _gate_side(W, gate, cfg, lookback_override=None):
    """A gate's per-side activation: each line's `check`, combined by the gate's op → (hi, lo) bool arrays.
    Each line read via W.line (value_mode-honoured, #42). The `lookback` window uses the line's per-line
    lookback (or lookback_override for the exit's wider window; falls back to lp_s30r_lb), auto-scaled by TF."""
    hi, lo = [], []
    for ln in gate.lines:
        v = W.line(ln.name)
        if ln.check == 'oob':
            hi.append(v >= cfg.hi); lo.append(v <= cfg.lo)
        elif ln.check == 'lookback':
            lb = (lookback_override or ln.lookback or cfg.s30r_lb) * (ln.tf // BASE_TF)
            hi.append(_roll_or(v >= cfg.hi, lb)); lo.append(_roll_or(v <= cfg.lo, lb))
        elif ln.check == 'mid':
            hi.append(v > cfg.bias_mid); lo.append(v < cfg.bias_mid)
    comb = np.all if gate.op == 'AND' else np.any
    return comb(hi, axis=0), comb(lo, axis=0)


def _finisher_active(W, cfg):
    """OR across active finisher gates → (hi, lo)."""
    n = len(W.ts); hi = np.zeros(n, bool); lo = np.zeros(n, bool)
    for g in cfg.finishers:
        ghi, glo = _gate_side(W, g, cfg); hi |= ghi; lo |= glo
    return hi, lo


def _gate_ok(W, cfg):
    """AND across active gate-role gates (clearances, e.g. s2r lookback) → (hi, lo). No gates → all-pass."""
    n = len(W.ts); hi = np.ones(n, bool); lo = np.ones(n, bool)
    for g in cfg.gates:
        ghi, glo = _gate_side(W, g, cfg); hi &= ghi; lo &= glo
    return hi, lo


def lr_setups(W, cfg):
    """PRODUCER — the latch-release SETUP events, no entry verdict. arm gate breaches OOB → the arm line's
    wobslay reverses ≥ floor. Emits [(arm_i, reversal_rj, es, bd, cap)] where cap is the window end (next
    opposite breach, or rj+horizon). Consumers apply their OWN finisher over (rj, cap): lr_detect uses the
    finisher+gate; the kernel walk uses s3r/s4r→s2M. SRP — build the setup here, decide the entry downstream."""
    ts = W.ts; n = len(ts)
    arm_line = cfg.arms[0].lines[0].name                     # the arm line (breach + wobslay)
    s6c = W._line(arm_line)                                   # CLOSED — the breach / arm
    s6 = W._line_emerging(arm_line)                           # emerging — the wobslay rides this
    sign = np.where(s6c >= cfg.hi, 1, np.where(s6c <= cfg.lo, -1, 0))
    wob = IC.wobble_slayer(s6, cfg.wob_n, cfg.hi, cfg.lo, anchored=True, strict=True)
    setups = []; i = 1
    while i < n:
        if sign[i] != 0 and sign[i] != sign[i - 1]:           # arm breach onset, side es
            es = int(sign[i]); rj = None
            for j in range(i, min(n, i + cfg.horizon)):
                if sign[j] == -es:
                    break
                if wob[j] == -es and j - cfg.wob_n >= 0 and abs(s6[j] - s6[j - cfg.wob_n]) >= cfg.floor:
                    rj = j; break                             # floor-gated wobslay reversal
            if rj is not None:
                cap = next((k for k in range(rj + 1, min(n, rj + cfg.horizon)) if sign[k] == -es),
                           min(n, rj + cfg.horizon))
                setups.append((i, rj, es, -es, cap))
            i = next((k for k in range(i + 1, n) if sign[k] != es), n)
            continue
        i += 1
    return setups


def lr_detect(W, cfg, start_ms=None):
    """THE STRATEGY — apply the finisher+gate VERDICT over lr_setups. Returns [(trade_ms, es, bd, tj)].
    Per setup: any active FINISHER re-breaches (same side) AND all active GATE clearances pass → entry."""
    ts = W.ts
    fin_hi, fin_lo = _finisher_active(W, cfg)
    gate_hi, gate_lo = _gate_ok(W, cfg)
    side_hi = fin_hi & gate_hi; side_lo = fin_lo & gate_lo    # finisher cleared by the gate(s) = the entry side
    if start_ms is None:
        start_ms = int(ts[0])
    entries = []
    for i, rj, es, bd, cap in lr_setups(W, cfg):
        side = side_hi if es == 1 else side_lo                # finisher = same side as the breach
        tj = next((k for k in range(rj + 1, cap) if side[k] and not side[k - 1]), None)
        if tj is not None and int(ts[tj]) >= start_ms:
            entries.append((int(ts[tj]), es, bd, int(tj)))
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


# ── the EXIT (Joe 0629) — a separate concern from lr_detect (entry) / lr_walk (verdict) ─────────────
def _finisher_signal(W, cfg, exit_on):
    """The exit-trigger signal for the chosen exit_on, with the EXTENDED exit lookback window (cfg.exit_rlb,
    overriding the per-line entry lookback — they fire out of sync, so the exit widens). 's30a'→s30a only ·
    's30a_s15a'→both AND'd."""
    gates = {g.name: g for g in cfg.exit_finishers}
    hi, lo = _gate_side(W, gates['s30a'], cfg, lookback_override=cfg.exit_rlb)
    if exit_on == 's30a_s15a':
        h15, l15 = _gate_side(W, gates['s15a'], cfg, lookback_override=cfg.exit_rlb); hi, lo = hi & h15, lo & l15
    return hi, lo


def lr_exit(W, entries, cfg, curl_fam='s5', exit_on='s30a_s15a', predict_gate=True, arm_gate=False):
    """The lr exit. Prediction + breach are FIXED on s5 (predict s5r via s5m/s5M; arm on s5m). Two knobs:
      curl_fam — the curl line family (s5/s6/s7/s8): a slower r curls LATER, so the ride runs longer.
      exit_on  — what ends the trade: 'curl' (exit at the curl) · 's30a' · 's30a_s15a' (finisher after the curl).
    predict_gate=True: while s5m OOB favourable, re-test predict_breach every bar; if predicted, BLOCK the
    trigger (ride) until s{curl_fam}r CURLS OOB. Hold through an s5m adverse flip (precursor, not failure);
    SL floor (-sl%) is the stop. NO time cap — holds to curl or SL (in backtest, runs to the data's end).
    Returns [(trade_ms, exit_ms, bd, entry_px, exit_px, ret, reason)]."""
    ts, px, n = W.ts, W.px, len(W.ts)
    s5m = W.line('s5m'); arm_hi = s5m >= cfg.hi; arm_lo = s5m <= cfg.lo
    pred = predict_breach(W.line('s5r'), s5m, W.line('s5M'), cfg.hi, cfg.lo, FENCE_HI, FENCE_LO)
    cr = W.line(f'{curl_fam}r')
    cwob = IC.wobble_slayer(cr, cfg.curl_n, cfg.hi, cfg.lo, anchored=True, strict=True)
    curl_hi = (cwob == -1) & (cr >= cfg.hi); curl_lo = (cwob == 1) & (cr <= cfg.lo)
    fin_hi, fin_lo = _finisher_signal(W, cfg, exit_on)
    rows = []
    for tms, es, bd, tj in entries:
        entry_px = float(px[tj]); fav_hi = (bd == 1)
        arm = arm_hi if fav_hi else arm_lo
        curl = curl_hi if fav_hi else curl_lo
        trig = curl if exit_on == 'curl' else (fin_hi if fav_hi else fin_lo)
        blocked = ever_curled = False; armed = not arm_gate  # arm_gate: gate the trigger on the s5m breach first
        ek = None; reason = 'end'
        for kk in range(tj + 1, n):                          # NO exit timeout (Joe) — hold to curl or SL only
            ret = (px[kk] - entry_px) / entry_px * 100.0 * bd
            if ret <= -cfg.sl:
                ek = kk; reason = 'SL'; break
            if arm[kk]:
                armed = True                               # favourable s5m breach has occurred (the given)
            if predict_gate and arm[kk] and not ever_curled:   # re-test while s5m OOB favourable
                if pred[kk] == bd:
                    blocked = True                         # predicted → ride (block the trigger)
                if blocked and curl[kk]:
                    blocked = False; ever_curled = True    # s{curl_fam}r curled OOB → release
            if armed and trig[kk] and not blocked:         # corrected exit: no trigger before the breach
                ek = kk; reason = 'exit'; break
        if ek is None:
            ek = n - 1                                        # reached the data's end (backtest), not a time cap
        exit_px = float(px[ek])
        ret = -cfg.sl if reason == 'SL' else (exit_px - entry_px) / entry_px * 100.0 * bd
        rows.append((tms, int(ts[ek]), bd, entry_px, exit_px, round(ret, 3), reason))
    return rows


def bracket_walk(W, entries, tp, sl, horizon):
    """The fixed TP/SL bracket baseline (what the lr exit is measured against). Per entry, walk the 5s grid
    → +tp or -sl whichever first, else horizon close. Returns ret% per entry."""
    ts = W.ts; px = W.px; n = len(ts)
    out = []
    for tms, es, bd, tj in entries:
        entry_px = float(px[tj]); r = None
        for kk in range(tj + 1, min(n, tj + horizon)):
            ret = (px[kk] - entry_px) / entry_px * 100.0 * bd
            if ret >= tp:
                r = tp; break
            if ret <= -sl:
                r = -sl; break
        if r is None:
            ek = min(n - 1, tj + horizon - 1)
            r = (float(px[ek]) - entry_px) / entry_px * 100.0 * bd
        out.append(round(r, 3))
    return out
