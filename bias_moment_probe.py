"""
bias_moment_probe.py — descriptive probe over the bias-machine lines.

Reuses the validated foundation in bias_gravity_scan (native-closed line computer,
read at the bar-close boundary). Two jobs:
  1. dump the full line state (s2/s6/s9/s22 × m/M/r) at given wall-times — for the
     two PK test cases (0611 0448 bearish, 1652 bullish).
  2. scan s22r for "lifts" (OOB → IB): Joe's requested test cases where s22r was
     out-of-bounds and has since come inside.

Descriptive only — no PK vote machine yet; this sets up the morning's wiring of
_states_standard for the s22r divergence / p-rev anchor.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from bias_gravity_scan import (TF_SECONDS, ROLE, OOB_HI, OOB_LO, MID, WARMUP_H,
                               line_on_frame, ms, fmt)

PROBE_TFS = ['s2', 's6', 's9', 's22']     # native lines (s2/s6/s22 validated m/r vs TV; s9 inferred)


def oob_tag(v):
    if v >= OOB_HI: return 'HI'
    if v <= OOB_LO: return 'LO'
    return 'ib'


def build(end):
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=24, warmup_hours=WARMUP_H)
    base, ts, win_start, _, px = det._setup(end)
    db.disconnect()
    lines = {}                                        # (tf, role) → aligned-to-base series
    for tf in PROBE_TFS:
        frame = IC.resample(base, TF_SECONDS[tf])
        for role in ROLE:
            v = line_on_frame(frame, role)
            lines[(tf, role)] = IC.align_to_base(v, frame, base)
    return base, ts, win_start, px, lines


def dump_moment(ts, lines, px, t_ms, label):
    i = int(np.searchsorted(ts, t_ms, side='right')) - 1
    print(f'\n── {label}  @ {fmt(t_ms)}  (px {px[i]:.4f}) ──')
    print(f'   {"TF":4} {"m (bb10)":>12} {"M (bb37)":>12} {"r (k5)":>12}')
    for tf in PROBE_TFS:
        vm, vM, vr = lines[(tf,'m')][i], lines[(tf,'M')][i], lines[(tf,'r')][i]
        print(f'   {tf:4} {vm:8.1f} {oob_tag(vm):>3} {vM:8.1f} {oob_tag(vM):>3} {vr:8.1f} {oob_tag(vr):>3}')


def scan_s22r_lifts(base, ts, lines, px):
    """s22r OOB→IB transitions on closed s22 bars (the 'lift')."""
    frame = IC.resample(base, TF_SECONDS['s22'])
    r22 = line_on_frame(frame, 'r')
    t22 = frame['timestamp'].to_numpy() + TF_SECONDS['s22'] * 1000   # close ts
    print('\n── s22r LIFTS (OOB → IB on closed s22 bars) ──')
    print(f'   {"close":11} {"from":>5} {"r_prev":>7} {"r_now":>7}  px@lift')
    prev = 0
    cnt = 0
    for k in range(1, len(r22)):
        if np.isnan(r22[k]) or np.isnan(r22[k-1]):
            continue
        was = oob_tag(r22[k-1]); now = oob_tag(r22[k])
        if was in ('HI', 'LO') and now == 'ib':
            j = int(np.searchsorted(ts, t22[k], side='right')) - 1
            if 0 <= j < len(px):
                print(f'   {fmt(t22[k]):11} {was:>5} {r22[k-1]:7.1f} {r22[k]:7.1f}  {px[j]:.4f}')
                cnt += 1
    print(f'   ({cnt} lifts)')


if __name__ == '__main__':
    end = ms(2026, 6, 11, 17, 4)
    base, ts, win_start, px, lines = build(end)
    print(f'window {fmt(win_start)} → {fmt(end)}  (warmup {WARMUP_H}h)')
    dump_moment(ts, lines, px, ms(2026, 6, 11, 4, 48),  'PK #1  BEARISH')
    dump_moment(ts, lines, px, ms(2026, 6, 11, 16, 52), 'PK #2  BULLISH')
    scan_s22r_lifts(base, ts, lines, px)
