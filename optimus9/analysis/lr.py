"""
lr.py (Joe 0628) — the latch-release reversal cascade: the production strategy (was the cf15 rig mechanic,
applied to prod because the 8-window superscope validated it). SRP-split into two one-job functions:

  lr_detect(W, ...) → entry events    — THE STRATEGY: arm on s6m closed breach → s6m floor-gated wobslay
                                         REVERSAL → next same-side s30a RE-breach = the entry. Emits only.
  lr_walk(W, entries, ...) → +MAE/MFE  — the BACKTEST verdict (a separate concern, never baked into detect).

One detect, three consumers apply their own verdict — strat_review (report the entries), the superscope
(lr_walk), o9-live (send to the exchange; fills are the verdict). Each function computes only the signals
IT needs — detect: breach/wob/s30a arrays · walk: price/swing arrays — no shared bundle, no recompute.
Dials default here; step 3 hoists them to lp_config.
"""
import numpy as np
import pandas as pd
import datetime as dtm
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots

HI, LO = 85.0, 15.0
STEP = 30000                                                 # 30s swing/price grid
WOB_N, FLOOR, TARGET, HORIZON = 4, 8.0, 0.9, 90 * 12         # latch-release dials (→ lp_config in step 3)


def _dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000)


def _roll_or(a, k):
    """Rolling OR over the current + k preceding bars (the s30r lift-off lookback)."""
    out = a.copy()
    for s in range(1, int(k) + 1):
        out[s:] |= a[:-s]
    return out


def s30a_active(W, s30r_lb=0):
    """Per 5s base bar: same-side s30a active — M & m OOB; s30r OOB within s30r_lb bars; s14M on side.
    Each s30 line via W.line (value_mode-honoured, #42) → the gates read emerging/realtime."""
    M = W.line('s30M'); m = W.line('s30m'); r = W.line('s30r')
    rhi = _roll_or(r >= HI, s30r_lb); rlo = _roll_or(r <= LO, s30r_lb)
    s14 = W.s14M
    return (M >= HI) & (m >= HI) & rhi & (s14 > 50), (M <= LO) & (m <= LO) & rlo & (s14 < 50)


def resolve_s30r_lb(db, W):
    """s30r lift-off lookback in 5s bars: lp_config `lp_s30r_lb` × (s30 TF in 5s units). The ONE source for
    rig + strat_review producer + o9-live (no duplicated derivation). Folds into the lr_params loader (step 3)."""
    lp = int(db.execute("SELECT val FROM lp_config WHERE name='lp_s30r_lb'", fetch=True)[0]['val'])
    return lp * (W._ls.resolve('s30r')[0] // 5)


def lr_detect(W, floor=FLOOR, wob_n=WOB_N, horizon=HORIZON, s30r_lb_bars=0, start_ms=None):
    """THE STRATEGY — find latch-release setups up to W's end, trades gated to >= start_ms.
    Returns [(trade_ms, es, bd, tj)]: es = s6m breach side (the arm), bd = -es (trade dir), tj = 5s bar idx.
    Computes its own detect signals (s6m breach + wobslay + s30a); emits entries only — no verdict."""
    ts = W.ts; n = len(ts)
    s6 = W._line_emerging('s6m')                                 # emerging s6m — the wobslay rides this
    s6c = W._line('s6m')                                         # CLOSED s6m — the breach / arm
    sign = np.where(s6c >= HI, 1, np.where(s6c <= LO, -1, 0))
    wob = IC.wobble_slayer(s6, wob_n, HI, LO, anchored=True, strict=True)
    s30a_hi, s30a_lo = s30a_active(W, s30r_lb_bars)
    if start_ms is None:
        start_ms = int(ts[0])
    entries = []; i = 1
    while i < n:
        if sign[i] != 0 and sign[i] != sign[i - 1]:              # s6m breach onset, side es (the arm)
            es = int(sign[i]); rj = None
            for j in range(i, min(n, i + horizon)):
                if sign[j] == -es:
                    break                                         # flipped opposite OOB → arm dies
                if wob[j] == -es and j - wob_n >= 0 and abs(s6[j] - s6[j - wob_n]) >= floor:
                    rj = j; break                                 # floor-gated wobslay reversal
            if rj is not None:
                side = s30a_hi if es == 1 else s30a_lo           # finisher = same side as the breach
                cap = next((k for k in range(rj + 1, min(n, rj + horizon)) if sign[k] == -es),
                           min(n, rj + horizon))                  # dies if s6m breaches the opposite side
                tj = next((k for k in range(rj + 1, cap) if side[k] and not side[k - 1]), None)
                if tj is not None and int(ts[tj]) >= start_ms:
                    entries.append((int(ts[tj]), es, -es, int(tj)))
            i = next((k for k in range(i + 1, n) if sign[k] != es), n)
            continue
        i += 1
    return entries


def lr_walk(W, entries, target=TARGET):
    """The BACKTEST VERDICT — MAE/MFE per entry to the 0.9% favourable swing. Returns
    [(trade_ms, dt, es, bd, mae, mfe, mfe_ok, mfe_swing_side, price)]. Computes its own price/swing signals."""
    ts = W.ts
    idx30 = np.where(ts % STEP == 0)[0]; ts30 = ts[idx30]
    close30 = pd.Series(W.px[idx30]).ffill().bfill().to_numpy()
    piv = find_pivots(close30, 0.9)
    rows = []
    for tms, es, bd, tj in entries:
        j = min(int(np.searchsorted(ts30, tms)), len(close30) - 1)
        fav = 'H' if bd == 1 else 'L'
        nxt = next((pi for pi, pk in piv if pi > j and pk == fav), None)
        nextpk = next((pk for pi, pk in piv if pi > j), None)     # the IMMEDIATE next pivot
        mfe_side = int(nextpk == fav)
        seg = close30[j:(nxt + 1)] if nxt is not None else close30[j:]
        mfe = mae = 0.0
        if len(seg):
            d = (seg - close30[j]) / close30[j] * 100.0 * bd
            mfe = float(d.max()); mae = float(-d.min())
        rows.append((tms, _dts(tms), es, bd, round(mae, 3), round(mfe, 3), int(mfe >= target), mfe_side, float(W.px[tj])))
    return rows
