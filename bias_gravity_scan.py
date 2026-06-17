"""
bias_gravity_scan.py — gravity-scan harness for the BIAS MACHINE (build #4).

Foundation first: config in TABLES (no hardcoding), one validated native-TF line
computer, structures defined early so the science can grow into them.

VALIDATED (2026-06-14 spot-checks vs TV prints):
  - native value = the JUST-CLOSED bar, read at its close boundary (HH:MM:00). no emerging.
  - HTF lines need DEEP warmup (160h+) or RSI/STC under-converge.
  - m (bb10/0.40/hlc3) and r (k5/6/6/hl2) match TV to the decimal.
  - PARKED: M (bb37/0.72/ohlc4) reads +8..+12 high on s2/s22 (perfect on s6). config/source/TF-quirk TBD.

GRAVITY HYPOTHESIS (Joe, corrected grammar):
  "for gravitation to occur, the M value must be higher than 50 if m+r are lo breach,
   or less than 50 if m+r are hi breach."
  i.e. M sits on the OPPOSITE side of 50 from the m+r breach → price gravitates toward M.
    lo-breach (m,r <=15) + M>50  -> gravity LONG
    hi-breach (m,r >=85) + M<50  -> gravity SHORT
  The reading is grabbed at the s6m wobble_slayer (s6m OOB-reversal: 2 bias-aligned bars).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import argparse, datetime as dtm
from datetime import timezone
import numpy as np
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.indicator_computer import IndicatorComputer as IC

# ── config TABLES ───────────────────────────────────────────────────────────
TF_SECONDS = {                          # native closed-bar timeframes (seconds)
    's2': 120, 's6': 360, 's9': 540, 's22': 1320,
    's30': 30,                          # the ONLY emerging line (centroid/lookahead)
}
# blown-up emulations (shorter TF x scaled lengths) — context, parked:
#   s18 = TF6 (360s) x3   |   s14 = TF7 (420s) x2
ROLE = {                                # centroid s-set roles (the 'a' = all three)
    'm': ('bb', dict(bb_len=10, bb_mult=0.40, src='hlc3')),
    'M': ('bb', dict(bb_len=37, bb_mult=0.72, src='ohlc4')),   # default mult; per-TF override below
    'r': ('k',  dict(rsi_len=6, stc_len=6,    k_len=5, src='hl2')),
}
M_MULT_BY_TF = {'s2': 0.83, 's22': 0.83}    # Joe 0615: s2M & s22M use 0.83 (s6M validated at 0.72 default)
OOB_HI, OOB_LO, MID = 85.0, 15.0, 50.0
WARMUP_H = 160                          # deep warmup so HTF RSI/STC converge


def line_on_frame(tf_df, role, tf_name=None):
    """Compute one centroid role on a resampled frame → per-bar values.
    tf_name resolves the per-TF M-mult override (M_MULT_BY_TF)."""
    kind, p = ROLE[role]
    src = IC.build_source(tf_df, p['src'])
    if kind == 'bb':
        mult = M_MULT_BY_TF.get(tf_name, p['bb_mult']) if role == 'M' else p['bb_mult']
        return IC.f_bb(src, p['bb_len'], mult)
    return IC.f_k(src, p['rsi_len'], p['stc_len'], p['k_len'])


def ms(y, mo, d, h, mi):
    return int(dtm.datetime(y, mo, d, h, mi, tzinfo=timezone.utc).timestamp() * 1000)


def fmt(t_ms):
    return dtm.datetime.fromtimestamp(t_ms / 1000, timezone.utc).strftime('%m%d %H:%M')


def scan(scan_h=96, end=None):
    db = DatabaseManager(**get_db_config()); db.connect()
    end = end or ms(2026, 6, 11, 17, 4)
    det = BLDetect(db, lookback_hours=scan_h, warmup_hours=WARMUP_H)
    base, ts, win_start, _, px = det._setup(end)
    db.disconnect()

    # s6 native frame (validated all three lines)
    tf6 = IC.resample(base, TF_SECONDS['s6'])
    m6 = line_on_frame(tf6, 'm'); M6 = line_on_frame(tf6, 'M'); r6 = line_on_frame(tf6, 'r')
    t6 = tf6['timestamp'].to_numpy()                 # s6 bar OPEN ts; closes ~ +360s
    close6 = t6 + TF_SECONDS['s6'] * 1000            # value available at close
    nb = len(t6)

    # breach side per s6 bar: m+r BOTH oob same side
    def side(i):
        if m6[i] >= OOB_HI and r6[i] >= OOB_HI: return +1   # hi breach
        if m6[i] <= OOB_LO and r6[i] <= OOB_LO: return -1   # lo breach
        return 0

    events = []
    cur_side, fired = 0, False                        # episode-gating: 1 event per breach episode
    for i in range(2, nb):
        if np.isnan(m6[i]) or np.isnan(M6[i]) or np.isnan(r6[i]):
            continue
        s = side(i)
        if s == 0:
            cur_side, fired = 0, False; continue
        if s != cur_side:                             # new breach episode
            cur_side, fired = s, False
        if fired:
            continue
        # gravity rule: M on the OPPOSITE side of 50, and M itself NOT oob on the breach side
        if s == -1:                                   # lo breach → want M>50 → LONG
            if not (MID < M6[i] < OOB_HI): continue
            grav = +1
        else:                                         # hi breach → want M<50 → SHORT
            if not (OOB_LO < M6[i] < MID): continue
            grav = -1
        # s6m wobble_slayer: 2 bias-aligned bars off the OOB extreme
        if s == -1:                                   # lo: s6m turning UP from a lo trough
            wob = (m6[i-2] <= OOB_LO and m6[i] > m6[i-1] > m6[i-2])
        else:                                         # hi: s6m turning DOWN from a hi peak
            wob = (m6[i-2] >= OOB_HI and m6[i] < m6[i-1] < m6[i-2])
        if not wob:
            continue
        fired = True                                  # episode spent
        # px_smooth outcome from the wobble bar's close
        j0 = int(np.searchsorted(ts, close6[i], side='left'))
        if j0 >= len(px) - 12:
            continue
        p0 = px[j0]
        horizons = {}
        for label, mins in (('+15m', 15), ('+30m', 30), ('+60m', 60)):
            j1 = int(np.searchsorted(ts, close6[i] + mins * 60_000, side='left'))
            j1 = min(j1, len(px) - 1)
            horizons[label] = (px[j1] - p0) / p0 * 100 * grav    # signed in gravity dir
        # excursions over next 60m (favorable in gravity dir / adverse against)
        jN = min(int(np.searchsorted(ts, close6[i] + 60 * 60_000, side='left')), len(px) - 1)
        seg = (px[j0:jN + 1] - p0) / p0 * 100 * grav
        fav, adv = float(seg.max()), float(-seg.min())
        # take-money-and-run proxy: did +2% favorable arrive before -1% adverse?
        hit2 = next((k for k in range(len(seg)) if seg[k] >= 2.0), None)
        stop1 = next((k for k in range(len(seg)) if seg[k] <= -1.0), None)
        tmar = (hit2 is not None and (stop1 is None or hit2 < stop1))
        events.append(dict(t=close6[i], side=s, grav=grav, M=M6[i], m=m6[i], r=r6[i],
                           depth=abs(M6[i] - MID),
                           h15=horizons['+15m'], h30=horizons['+30m'], h60=horizons['+60m'],
                           fav=fav, adv=adv, tmar=tmar))

    # ── report ──
    print(f'\nGRAVITY SCAN  window {fmt(win_start)} → {fmt(end)}  ({scan_h}h, warmup {WARMUP_H}h)')
    print(f's6 bars: {nb}   gravity-confirmed wobbles: {len(events)}')
    if not events:
        print('  no events.'); return
    print('\n  time        brch  grav   M     s6m    s6r  | +15m   +30m   +60m  | fav   adv   tmar')
    for e in events:
        bl = 'HI' if e['side'] == +1 else 'LO'
        gl = 'SHORT' if e['grav'] == -1 else 'LONG '
        print(f"  {fmt(e['t'])}  {bl}   {gl} {e['M']:5.1f} {e['m']:6.1f} {e['r']:5.1f} | "
              f"{e['h15']:+5.2f}  {e['h30']:+5.2f}  {e['h60']:+5.2f} | "
              f"{e['fav']:4.2f}  {e['adv']:4.2f}  {'Y' if e['tmar'] else '.'}")
    def summ(evs, tag):
        if not evs: print(f'    [{tag}] n=0'); return
        a = lambda k: np.array([e[k] for e in evs]); n = len(evs)
        h30 = a('h30')
        print(f'    [{tag}] n={n:2d}  h30 median {np.median(h30):+.2f}%  hit {(h30>0).mean()*100:3.0f}%  '
              f'fav {np.median(a("fav")):.2f}  adv {np.median(a("adv")):.2f}  '
              f'tmar {a("tmar").sum()}/{n}')
    n = len(events)
    print(f'\n  SUMMARY (n={n}):')
    summ(events, 'ALL')
    summ([e for e in events if e['side'] == +1], 'HI/short')
    summ([e for e in events if e['side'] == -1], 'LO/long ')
    print('  by M-depth |M-50| (lead #1: does deeper-M = stronger gravity?):')
    summ([e for e in events if e['depth'] < 10],            'depth<10 ')
    summ([e for e in events if 10 <= e['depth'] < 20],      'depth10-20')
    summ([e for e in events if e['depth'] >= 20],           'depth>=20 ')


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--hours', type=int, default=96)
    a = ap.parse_args()
    scan(scan_h=a.hours)
