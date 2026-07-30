"""build_flips — point-to-point per-flip MFE/MAE on the merged short+long signal stream (Joe 0724). SAVED.

Best short config (s26>=8 & s12>=6) + best long config (s30>=12 & s16>=6) fired signals, merged chronologically.
Each trade is held from its flip to the NEXT flip (point-to-point) and MFE/MAE measured over that hold in its dir.
Flags non-alternating pairs (two same-dir flips in a row -> not a clean point-to-point handover).
Usage: build_flips.py <YYYY-MM-DD> <ndays>   (default 06-22 +7d)
"""
import sys, time
import numpy as np
from datetime import datetime, timezone, timedelta
import linelab as LL
import siglab

SHORT_CFG = {26: 8, 12: 6}          # slow,fast : thr
LONG_CFG = {30: 12, 16: 6}
ALL = sorted(set(list(SHORT_CFG) + list(LONG_CFG)))
CADENCE = 's5'
FMT = lambda ms: time.strftime('%m-%d %H:%M', time.gmtime(ms / 1000))

_day = next((a for a in sys.argv[1:] if a[:1].isdigit() and '-' in a), '2026-06-22')
_ndays = next((int(a) for a in sys.argv[1:] if a.isdigit()), 7)
_d0 = datetime.strptime(_day, '%Y-%m-%d').replace(tzinfo=timezone.utc)
S = int(_d0.timestamp() * 1000); E = int((_d0 + timedelta(days=_ndays)).timestamp() * 1000)

for tf in ALL:
    LL.register('s%dx' % tf, kind='bb', tf=tf, length=5, mult=0.37)
    LL.register('s%dm' % tf, kind='bb', tf=tf, length=6, mult=0.45)
cache, ets, epx, names = LL.warm(rebuild=False)
lab = siglab.Lab(cache, ets, epx)


def pick(d, cfg):
    M = siglab.markers(cache, lab, CADENCE, S, E, ALL, d)
    return [m for m in M if all(m['strn'][tf] >= thr for tf, thr in cfg.items())]


flips = pick(-1, SHORT_CFG) + pick(1, LONG_CFG)
flips.sort(key=lambda m: m['tms'])
print('=== point-to-point flips | %s +%dd | cadence=%s | short(s26&s12) + long(s30&s16) | %d flips ===' % (
    _day, _ndays, CADENCE, len(flips)))
print(' entry        | dir   | hold->next   | entry_px | exit_px | MFE   | MAE   | net    | alt?')
tot_mfe = tot_mae = tot_net = 0.0; nbank = 0; nonalt = 0
for k, m in enumerate(flips):
    nxt = flips[k + 1]['tms'] if k + 1 < len(flips) else None
    ep, xp, mfe, mae = lab.leg(m['tms'], nxt, m['d'])
    net = mfe - mae; tot_mfe += mfe; tot_mae += mae; tot_net += net; nbank += (mae < 1.0)
    alt = '' if (k + 1 >= len(flips) or flips[k + 1]['d'] != m['d']) else 'SAME-dir'
    if alt:
        nonalt += 1
    print('  %s | %-5s | %11s | %8.4f | %7.4f | %5.2f | %5.2f | %+5.2f | %s' % (
        FMT(m['tms']), 'LONG' if m['d'] == 1 else 'SHORT',
        FMT(nxt) if nxt else '(end)', ep, xp, mfe, mae, net, alt))
print('--- %d flips | sum MFE %.1f%% MAE %.1f%% net %+.1f%% | bank(MAE<1%%) %d/%d | non-alternating pairs %d ---' % (
    len(flips), tot_mfe, tot_mae, tot_net, nbank, len(flips), nonalt))
