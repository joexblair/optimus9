"""
bias_3d_table.py — 3D map of the HTF lines at exhaustion moments.

Question (Joe 0615): both control PKs (reversals) sit at multi-TF exhaustion, but so
do 359 non-reversals. What's DIFFERENT? Map every line ≥ s6 (s6/s9/s22 × m/M/r) at two
capture moments — the s22 p-rev moment and the pool_c/pool_r floater — for every event,
then look for the pattern that separates reversals from continuations.

Universe   : all-m-OOB exhaustion events (s2/s6/s9/s22 m all OOB same side), episode-gated.
Filter     : s22m OOB only (auto-met by the universe; applied explicitly).
Rows       : the 2 control PKs (reversals) + the rest (mostly continuations).
Capture A  : @prev  — the event (p-rev) moment.
Capture B  : @float — pool_c(=9) s22-bars back (198m), the s22r divergence anchor (proxy).
Outcome    : rev_mag = signed px_smooth move in the REVERSAL dir at +60m (counter-breach).

CAVEAT: s22M reads ~+10 high vs TV (config mismatch, not warmup) — its OOB/zone calls
near a boundary are unreliable. s2M/s22M use mult 0.83; s6/s9 M use 0.72.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import argparse, csv
import numpy as np
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from bias_gravity_scan import (TF_SECONDS, ROLE, OOB_HI, OOB_LO, WARMUP_H,
                               line_on_frame, ms, fmt)

UNIVERSE_TFS = ['s2', 's6', 's9', 's22']          # all-m-OOB detector (incl s2)
TABLE_TFS    = ['s6', 's9', 's22']                # captured in the table (Joe: s6 and up)
ROLES        = ['m', 'M', 'r']
POOL_C_S22   = 9                                   # s22r p_c → floater lookback (bars)
CONTROLS     = {ms(2026, 6, 11, 4, 48): 'PK-bear', ms(2026, 6, 11, 16, 52): 'PK-bull'}
REV_THRESH   = 1.5                                 # rev_mag ≥ this (%) = a reversal materialised


def zone(v):
    if v != v:      return '  ?'
    if v >= OOB_HI: return 'OOB+'
    if v <= OOB_LO: return 'OOB-'
    if v >= 60:     return 'hi'                     # gravitating high
    if v <= 40:     return 'lo'                     # gravitating low
    return 'mid'                                    # ~50


def run(scan_h=168, end=None):
    db = DatabaseManager(**get_db_config()); db.connect()
    end = end or ms(2026, 6, 12, 14, 0)      # past the PKs so 1652 gets full 3h forward outcome
    det = BLDetect(db, lookback_hours=scan_h, warmup_hours=WARMUP_H)
    base, ts, win_start, _, px = det._setup(end)
    db.disconnect()

    # all lines aligned to base (universe m's + table s6/s9/s22 × m/M/r)
    L = {}
    for tf in UNIVERSE_TFS:
        frame = IC.resample(base, TF_SECONDS[tf])
        for role in (ROLES if tf in TABLE_TFS else ['m']):
            L[(tf, role)] = IC.align_to_base(line_on_frame(frame, role, tf), frame, base)

    s22_bar = TF_SECONDS['s22'] * 1000
    s22m_b  = L[('s22', 'm')]

    # ── p-rev universe: s30m reverses off its OOB extreme WHILE s22m is OOB same side ──
    # (the s30m breach inside the HTF breach, turning — the p-rev / value-freeze moment).
    tf30 = IC.resample(base, TF_SECONDS['s30'])
    s30m = line_on_frame(tf30, 'm', 's30')          # 30s closed (emerging is the eventual intent)
    t30  = tf30['timestamp'].to_numpy() + TF_SECONDS['s30'] * 1000
    rows = []
    armed_hi = armed_lo = False
    for i in range(2, len(s30m)):
        c = int(t30[i])
        j = int(np.searchsorted(ts, c, side='left'))
        if j <= 0 or j >= len(px) - 12:
            continue
        a, b, cc = s30m[i - 2], s30m[i - 1], s30m[i]
        if a != a or b != b or cc != cc:
            continue
        if a >= OOB_HI: armed_hi = True
        if a <= OOB_LO: armed_lo = True
        sv = s22m_b[j]
        S = +1 if sv >= OOB_HI else (-1 if sv <= OOB_LO else 0)   # HTF breach side
        if   S == +1 and armed_hi and a >= OOB_HI and cc < b < a:  # hi peak rolling over
            armed_hi = False
        elif S == -1 and armed_lo and a <= OOB_LO and cc > b > a:  # lo trough lifting
            armed_lo = False
        else:
            continue
        # outcome: max FAVOURABLE excursion (reversal dir = -S) vs adverse, over next 3h
        rev = -S
        p0 = px[j]
        j3 = min(int(np.searchsorted(ts, c + 180 * 60_000, side='left')), len(px) - 1)
        seg = (px[j:j3 + 1] - p0) / p0 * 100 * rev
        fav, adv = float(seg.max()), float(-seg.min())
        jf = int(np.searchsorted(ts, c - POOL_C_S22 * s22_bar, side='left'))
        ctrl = next((tag for t, tag in CONTROLS.items() if abs(c - t) <= 10 * 60_000), '')
        row = dict(t=c, side=S, ctrl=ctrl, fav=fav, adv=adv,
                   reversed=(fav >= REV_THRESH and fav > adv))
        for tf in TABLE_TFS:
            for role in ROLES:
                row[f'{tf}{role}_p'] = L[(tf, role)][j] if j < len(px) else float('nan')
                row[f'{tf}{role}_f'] = L[(tf, role)][jf] if 0 <= jf < len(px) else float('nan')
        rows.append(row)
    nctrl = sum(1 for r in rows if r['ctrl'])
    print(f'  p-rev events: {len(rows)}   controls captured: {nctrl}/2')

    # breach-dev: (value-50)*side → +ve = on the BREACH side (aligned/exhausted),
    #             -ve = on the OPPOSITE side (gravitating/divergent). removes side confound.
    def bd(r, tf, role, cap):
        v = r[f'{tf}{role}_{cap}']
        return (v - 50.0) * r['side'] if v == v else float('nan')

    # ── CSV (raw values + side-normalised breach-dev @prev) ──
    cols = [f'{tf}{role}_{cap}' for tf in TABLE_TFS for role in ROLES for cap in ('p', 'f')]
    path = '/home/joe/thecodes/bias_3d_table.csv'
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['time', 'side', 'ctrl', 'fav', 'adv', 'reversed'] +
                   cols + [f'{tf}{role}_dev' for tf in TABLE_TFS for role in ROLES])
        for r in rows:
            w.writerow([fmt(r['t']), r['side'], r['ctrl'], round(r['fav'], 2), round(r['adv'], 2),
                        int(r['reversed'])] +
                       [round(r[c], 1) if r[c] == r[c] else '' for c in cols] +
                       [round(bd(r, tf, role, 'p'), 1) if bd(r, tf, role, 'p') == bd(r, tf, role, 'p') else ''
                        for tf in TABLE_TFS for role in ROLES])

    # ── report ──
    revs = [r for r in rows if r['reversed']]
    nons = [r for r in rows if not r['reversed']]
    print(f'\n3D TABLE  {fmt(win_start)} → {fmt(end)}   rows={len(rows)} (s22m-OOB)  '
          f'reversals(fav≥{REV_THRESH}% & fav>adv over 3h)={len(revs)}  non={len(nons)}   → {path}')

    print('\n── the 2 control PKs: breach-dev per line (+ = breach side/aligned, − = opposite/gravitating) ──')
    print(f'  {"ctrl":8} {"side":4} {"fav":>5} {"adv":>5}  ' +
          ' '.join(f'{tf}{role:>4}' for tf in TABLE_TFS for role in ROLES))
    for r in rows:
        if r['ctrl']:
            ds = ' '.join(f'{bd(r,tf,role,"p"):+5.0f}' for tf in TABLE_TFS for role in ROLES)
            print(f"  {r['ctrl']:8} {'HI' if r['side']==1 else 'LO':4} {r['fav']:5.2f} {r['adv']:5.2f}  {ds}")

    print('\n── pattern: mean breach-dev @prev, reversals vs non-reversals (side-normalised) ──')
    print(f'  {"line":6} {"REV":>7} {"NON":>7} {"Δ":>7}   (−Δ ⇒ reversals more GRAVITATING/opposite)')
    seps = []
    for tf in TABLE_TFS:
        for role in ROLES:
            rv = np.array([bd(r, tf, role, 'p') for r in revs]); rv = rv[~np.isnan(rv)]
            nv = np.array([bd(r, tf, role, 'p') for r in nons]); nv = nv[~np.isnan(nv)]
            if len(rv) and len(nv):
                d = rv.mean() - nv.mean(); seps.append((abs(d), tf + role, d))
                print(f'  {tf+role:6} {rv.mean():7.1f} {nv.mean():7.1f} {d:+7.1f}')
    print('\n  biggest separations (|Δ breach-dev @prev|):')
    for ad, name, d in sorted(seps, reverse=True)[:5]:
        print(f'    {name}: {d:+.1f}  ({"reversals more breach-side" if d>0 else "reversals more gravitating"})')

    # ── condition lift: which filters push reversal rate above the base? ──
    base = len(revs) / len(rows) * 100
    print(f'\n── condition lift: reversal rate under candidate filters (BASE = {base:.0f}%, n={len(rows)}) ──')
    def minr(r):
        vs = [bd(r, tf, 'r', 'p') for tf in TABLE_TFS]; vs = [v for v in vs if v == v]
        return min(vs) if vs else float('nan')
    conds = {
        's22m shallow (dev<65)'      : lambda r: bd(r,'s22','m','p') < 65,
        's22m deep (dev>=78)'        : lambda r: bd(r,'s22','m','p') >= 78,
        'any r gravitating (min<-5)' : lambda r: minr(r) < -5,
        's22r gravitating (dev<5)'   : lambda r: bd(r,'s22','r','p') < 5,
        's6r gravitating (dev<0)'    : lambda r: bd(r,'s6','r','p') < 0,
        's22M aligned (dev>30)'      : lambda r: bd(r,'s22','M','p') > 30,
        'shallow s22m + r grav'      : lambda r: bd(r,'s22','m','p') < 65 and minr(r) < -5,
        'shallow s22m + s22M aligned': lambda r: bd(r,'s22','m','p') < 65 and bd(r,'s22','M','p') > 30,
    }
    for name, cond in conds.items():
        sel = [r for r in rows if cond(r) and not any(np.isnan(bd(r,tf,ro,'p')) for tf in TABLE_TFS for ro in ROLES)]
        if sel:
            k = sum(r['reversed'] for r in sel)
            lift = k/len(sel)*100 - base
            print(f'  {name:30} {k:3d}/{len(sel):3d} = {k/len(sel)*100:3.0f}%   ({lift:+.0f} vs base)')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('--hours', type=int, default=168)
    a = ap.parse_args(); run(scan_h=a.hours)
