"""
cf15_rig.py — THROWAWAY (Joe 0627). Sweeps the window for 15:24-style setups and measures their quality,
to inform the cascade_redesign spec (does the latch-release-on-s6m-reversal mechanic produce good entries?).

Setup (the 06-17 15:24 shape):
  s6m breaches (arm, side es) → s6m floor-gated wobslay REVERSAL (dir -es; magnitude >= FLOOR separates
  near-flat from true reversion) → the NEXT same-side s30a RE-breach = the trade (side bd = -es).

Per trade: the cf_bias walk (reused from concept_run stage 3b) → MAE (prox_mae, worst adverse) + MFE +
mfe_ok (the "opened on the MFE side of the swing" test = MFE reaches the 0.9% swing target). Stored in
cf15_walk alongside the trade time. Params (WOB_N, FLOOR, TARGET) are throwaway dials — sweep + eyeball.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, pandas as pd, datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots
import bias_machine as bm

HI, LO = 85.0, 15.0
STEP = 30000                          # 30s grid (the swing/price cadence, matching concept_run)
WOB_N = 4                             # s6m wobslay bars (throwaway dial)
FLOOR = 8.0                           # s6m reversal-magnitude floor in line-units (near-flat vs true reversion)
TARGET = 0.9                          # swing target % → mfe_ok
HORIZON = 90 * 12                     # 90 min search horizon (5s bars) for reversal + s30a re-breach


def ms(dt): return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000)


def _roll_or(a, k):
    """Rolling OR over the current + k preceding bars (the s30r lift-off lookback)."""
    out = a.copy()
    for s in range(1, int(k) + 1):
        out[s:] |= a[:-s]
    return out


def s30a_active(W, s30r_lb=0):
    """Per 5s base bar: same-side s30a active — M & m OOB at the bar; s30r OOB within s30r_lb 5s-bars
    (the lift-off lookback); s14M on side → (hi, lo). Each s30 line via W.line — honours its DB
    value_mode (#42), so the s30 gates read EMERGING/realtime (validated 99.89% OOB vs TV over 24h),
    not the lagged closed bar that broke the 02:29:30 trigger. No hardcoded config; all from the view."""
    M = W.line('s30M'); m = W.line('s30m'); r = W.line('s30r')             # base-aligned, value_mode-honoured
    rhi = _roll_or(r >= HI, s30r_lb); rlo = _roll_or(r <= LO, s30r_lb)      # s30r OOB within the lookback
    s14 = W.s14M
    return (M >= HI) & (m >= HI) & rhi & (s14 > 50), (M <= LO) & (m <= LO) & rlo & (s14 < 50)


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    R1 = ms(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc))
    START = ms(dtm.datetime(2026, 6, 17, tzinfo=timezone.utc))    # window starts 06-17 00:00 (warmup precedes it)
    cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                        mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
    W = bm.BiasWindow(db, R1, cfg=cfg); ts = W.ts; n = len(ts)
    idx30 = np.where(ts % STEP == 0)[0]; ts30 = ts[idx30]

    s6 = W._line_emerging('s6m')                                  # emerging s6m (5s) — the wobslay rides this
    s6c = W._line('s6m')                                          # CLOSED s6m (precursor3) — the breach/arm
    sign = np.where(s6c >= HI, 1, np.where(s6c <= LO, -1, 0))     # breach onset on closed bars (far fewer)
    wob = IC.wobble_slayer(s6, WOB_N, HI, LO, anchored=True, strict=True)
    LP = int(db.execute("SELECT val FROM lp_config WHERE name='lp_s30r_lb'", fetch=True)[0]['val'])
    s30tf = W._ls.resolve('s30r')[0]                             # s30 TF (s) from the view — no hardcode
    s30a_hi, s30a_lo = s30a_active(W, LP * (s30tf // 5))         # lift-off lookback: LP s30-bars → 5s-bars

    close30 = pd.Series(W.px[idx30]).ffill().bfill().to_numpy()
    piv = find_pivots(close30, 0.9)

    def detect_walk(floor):
        """Detect 15:24 setups at this floor + walk each → rows (cf_bias logic). floor only gates the reversal."""
        trades = []; i = 1
        while i < n:
            if sign[i] != 0 and sign[i] != sign[i - 1]:          # s6m OOB onset (closed), side es
                es = int(sign[i]); rj = None
                for j in range(i, min(n, i + HORIZON)):
                    if sign[j] == -es:
                        break                                     # flipped to opposite OOB → abort this arm
                    if wob[j] == -es and j - WOB_N >= 0 and abs(s6[j] - s6[j - WOB_N]) >= floor:
                        rj = j; break                             # the floor-gated reversal
                if rj is not None:
                    side = s30a_hi if es == 1 else s30a_lo        # finisher = same side as s6m's breach
                    cap = next((k for k in range(rj + 1, min(n, rj + HORIZON)) if sign[k] == -es),
                               min(n, rj + HORIZON))               # setup DIES if s6m breaches the opposite side
                    tj = next((k for k in range(rj + 1, cap) if side[k] and not side[k - 1]), None)
                    if tj is not None and int(ts[tj]) >= START:
                        trades.append((int(ts[tj]), es, -es))
                i = next((k for k in range(i + 1, n) if sign[k] != es), n)
                continue
            i += 1
        rows = []
        for tms, es, bd in trades:
            j = min(int(np.searchsorted(ts30, tms)), len(close30) - 1)
            fav = 'H' if bd == 1 else 'L'
            nxt = next((pi for pi, pk in piv if pi > j and pk == fav), None)
            nextpk = next((pk for pi, pk in piv if pi > j), None)     # the IMMEDIATE next pivot
            mfe_side = int(nextpk == fav)                             # opened on MFE side = next swing pivot is favourable
            seg = close30[j:(nxt + 1)] if nxt is not None else close30[j:]
            mfe = mae = 0.0
            if len(seg):
                d = (seg - close30[j]) / close30[j] * 100.0 * bd
                mfe = float(d.max()); mae = float(-d.min())
            rows.append((tms, dts(tms), es, bd, round(mae, 3), round(mfe, 3), int(mfe >= TARGET), mfe_side))
        return rows

    rows = detect_walk(FLOOR)
    db.execute('DROP TABLE IF EXISTS cf15_walk')
    db.execute('''CREATE TABLE cf15_walk (trade_ms BIGINT, trade_dt DATETIME, breach_side TINYINT,
                  trade_dir TINYINT, mae FLOAT, mfe FLOAT, mfe_ok TINYINT, mfe_swing_side TINYINT,
                  wob_n INT, floor FLOAT)''')
    db.executemany('INSERT INTO cf15_walk VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                   [r + (WOB_N, FLOOR) for r in rows])
    if rows:
        mae = np.array([r[4] for r in rows]); mfe = np.array([r[5] for r in rows])
        ok = np.array([r[6] for r in rows]); side = np.array([r[7] for r in rows])
        print(f"cf15_walk: {len(rows)} trades  ·  06-17 00:00 → 06-22  (WOB_N={WOB_N} FLOOR={FLOOR})")
        print(f"  mfe_swing_side (entry on favourable leg):  {side.sum()}/{len(rows)} = {side.mean()*100:.0f}%   [structural metric]")
        print(f"  mfe_ok (favourable reached {TARGET}%):       {ok.sum()}/{len(rows)} = {ok.mean()*100:.0f}%   [outcome metric]")
        print(f"  MAE  median {np.median(mae):.2f}%  mean {mae.mean():.2f}%  max {mae.max():.2f}%")
        print(f"  MFE  median {np.median(mfe):.2f}%  mean {mfe.mean():.2f}%  max {mfe.max():.2f}%")
    else:
        print("cf15_walk: 0 trades — loosen FLOOR/WOB_N or widen the shape")
    db.disconnect()


if __name__ == '__main__':
    main()
