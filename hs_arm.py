"""hs_arm.py — the hs30 arm, r-pred ladder gate (+ optional momo-oob gate). A/B/B. (Joe 0714)

ARM CANDIDATE   hs30m x hs30r cross while hs30r OOB   (SHORT: OOB-high & m below r · LONG: OOB-low & m above r)

GATE (Joe's rule): when an arm triggers, test r-pred BEFORE producing.
    r-pred TRUE (a coarse rung 33/37/45 still predicting SAME SIDE) -> the leg isn't committed -> DROP.
  Optional momo-oob gate (Joe 0714): ALSO require hs45 to have produced its #2 down-curl since entering
    OOB. "oob-no-momo-verdict" = OOB but no down-curl yet -> the leg hasn't topped -> DROP. Less profit,
    doesn't suck (07-11: blocks the bad 13:00, produces the good 15:00).

LATCH   a produced arm absorbs later same-side crosses until hs30r leaves its OOB (leg reset). The latch
        is what de-chops the emerging cross, so the cross can be read immediate (Joe: 2-line cross is
        self-timing -> lands MFE-side).

AXES
  GATE       rpred | rpred_momo
  PRED_CAD   emg(5s) | q4 | q6 | q8     — sub-seam sampling of the r-pred read, per rung (Joe)
  CROSS      imm(30s) | seam(30min)     — emerging cross vs the coarse seam (Joe's produce query)

Config: hs30/33/37/45 · r 7|5|7|ohlc4 · m 6|{0.56,0.45,0.45,0.56} · Mage 37|0.83 · momo BB 7|0.64|close.
SCORE jig.score.entry_quality — MAE/MFE, exit-independent, per week. No net/PnL. Causal/emerging.

  python3 hs_arm.py [days] [warmup] [swing]      (default 32,600,2.0)
  python3 hs_arm.py day 2026-07-11               (single-day produce trace, all cells)
"""
import sys, datetime as dtm
from datetime import timezone
import collections
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline

HI, LO = 85.0, 15.0
LADDER = [33, 37, 45]
ALL_TFS = [30, 33, 37, 45]
MULT = {30: 0.56, 33: 0.45, 37: 0.45, 45: 0.56}
CADS = {'emg': None, 'q4': 4, 'q6': 6, 'q8': 8}
CROSSES = {'imm': 30_000, 'seam': 1800_000}

DAYMODE = len(sys.argv) > 2 and sys.argv[1] == 'day'
if DAYMODE:
    y, mo, dd = map(int, sys.argv[2].split('-'))
    end_ms = int((dtm.datetime(y, mo, dd, tzinfo=timezone.utc) + dtm.timedelta(days=1)).timestamp() * 1000)
    HOURS, SWING = 48, 2.0
else:
    DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
    SWING = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0
    HOURS = DAYS * 24
    end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
WARM = int(sys.argv[2]) if (len(sys.argv) > 2 and not DAYMODE) else 600
win0 = end_ms - HOURS * 3600_000


def overrides():
    o = {}
    for tf in ALL_TFS:
        o.update(kline(f'hs{tf}r', tf, k_len=7, rsi=5, stc=7, src='ohlc4'))
        o.update(bbline(f'hs{tf}m', tf, length=6, mult=MULT[tf], src='ohlc4'))
        o.update(bbline(f'hs{tf}Mage', tf, length=37, mult=0.83, src='ohlc4'))
    o.update(kline('hs45k', 45, k_len=7, rsi=5, stc=7, src='ohlc4'))     # = hs45r; momo K
    o.update(bbline('hs45mo', 45, length=7, mult=0.64, src='close'))     # momo BB
    return o


def ffill_at(pred, ts, cad_ms):
    """r-pred as sampled at cad_ms sub-seams, forward-filled to every 5s bar (causal)."""
    if cad_ms is None:
        return pred
    mask = (ts % cad_ms) == 0
    pos = np.maximum.accumulate(np.where(mask, np.arange(len(ts)), -1))
    pos = np.clip(pos, 0, None)
    return pred[pos]


with Jig(end_ms, hours=HOURS, warmup=WARM, overrides=overrides()) as j:
    C, ts = j.causal, np.asarray(j.ts, np.int64)
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)
    n = len(ts)

    rs30 = C.sign('hs30r')
    # ladder predict per rung (5s emerging), + sub-seam sampled per cadence
    pred_raw = {tf: C.predict(C.line(f'hs{tf}r'), C.line(f'hs{tf}m'), C.line(f'hs{tf}Mage')) for tf in LADDER}
    pred_cad = {(tf, cn): ffill_at(pred_raw[tf], ts, None if cv is None else int(round(tf * 60000 / cv / 5000) * 5000))
                for tf in LADDER for cn, cv in CADS.items()}

    # momo hs45 down-curl latch: per 5s, has hs45 produced its #2 curl since entering the current OOB?
    g45 = (ts % (45 * 60 * 1000)) == 0
    b45 = ts[g45]; r45 = C.line('hs45k')[g45]
    s45 = np.where(r45 >= HI, 1, np.where(r45 <= LO, -1, 0))
    peaks = {int(np.searchsorted(b45, t)) for t in C.curl(b45, r45, -1)}   # #2 for OOB-high
    trghs = {int(np.searchsorted(b45, t)) for t in C.curl(b45, r45, +1)}   # #2 for OOB-low
    latch_hi = np.zeros(len(b45), bool); latch_lo = np.zeros(len(b45), bool)
    lh = ll = False
    for i in range(len(b45)):
        if s45[i] == 1:
            if i in peaks: lh = True
        else:
            lh = False
        if s45[i] == -1:
            if i in trghs: ll = True
        else:
            ll = False
        latch_hi[i], latch_lo[i] = lh, ll
    slot = np.clip(np.searchsorted(b45, ts, side='right') - 1, 0, len(b45) - 1)
    momo_hi = latch_hi[slot]; momo_lo = latch_lo[slot]

    def run(gate, cadn, crossn):
        x = C.cross('hs30m', 'hs30r', CROSSES[crossn])
        cand = np.flatnonzero(((rs30 == 1) & (x == -1)) | ((rs30 == -1) & (x == 1)))
        cand = cand[ts[cand] >= win0]
        events = []
        latched = 0
        for i in cand:
            side = int(rs30[i])
            if latched != 0 and side != latched:
                latched = 0
            if latched == side:
                events.append((int(ts[i]), side, False, 'latch')); continue
            rpred_block = any(int(pred_cad[(tf, cadn)][i]) == side for tf in LADDER)
            momo_ok = True
            if gate == 'rpred_momo':
                momo_ok = (momo_hi[i] if side == 1 else momo_lo[i])
            if rpred_block or not momo_ok:
                events.append((int(ts[i]), side, False, 'rpred' if rpred_block else 'momo'))
            else:
                events.append((int(ts[i]), side, True, '')); latched = side
        return events

    if DAYMODE:
        d0 = int(dtm.datetime(y, mo, dd, tzinfo=timezone.utc).timestamp() * 1000)
        for gate in ('rpred', 'rpred_momo'):
            for crossn in ('seam', 'imm'):
                ev = run(gate, 'emg', crossn)
                prod = [(dt(t), 'SHORT' if s == 1 else 'LONG') for (t, s, p, b) in ev if p and t >= d0]
                print(f'{gate:<11} cross={crossn:<5} cad=emg  produced: ' +
                      ', '.join(f'{d:%H:%M} {s}' for d, s in prod))
    else:
        print(f'{HOURS//24}d · swing {SWING}%   (MFE/MAE · MAE>2 · n produced)\n')
        print(f"  {'gate':<11} {'cross':<5} {'cad':<4} {'n':>4} {'MFEmed':>7} {'MAEmed':>7} {'MFE/MAE':>8} {'MAE>2':>6}")
        best = None
        for gate in ('rpred', 'rpred_momo'):
            for crossn in ('imm', 'seam'):
                for cadn in CADS:
                    ev = run(gate, cadn, crossn)
                    prod = [(t, s) for (t, s, p, b) in ev if p]
                    if len(prod) < 5:
                        print(f"  {gate:<11} {crossn:<5} {cadn:<4} {len(prod):>4}   (too few)"); continue
                    ent = [(t, s, -s, int(np.searchsorted(ts, t))) for (t, s) in prod]
                    q = j.score.entry_quality(ent, swing_pct=SWING)
                    m = np.array([float(r[4]) for r in q]); f = np.array([float(r[5]) for r in q])
                    ratio = np.median(f) / max(np.median(m), 1e-9)
                    print(f"  {gate:<11} {crossn:<5} {cadn:<4} {len(prod):>4} {np.median(f):>7.2f} "
                          f"{np.median(m):>7.2f} {ratio:>8.2f} {100*np.mean(m>2):>5.0f}%")
