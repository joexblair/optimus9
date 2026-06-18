"""
bias_pk_foundation.py — OG grind of the s6 + s3 line VALUES that the pk signal interrogates.

Per-line coordinate sweep (others held at baseline) maximising correct-placement RATE (≥FLOOR
placements). Lines: s6m, s6r (detection) · s3m, s3M, s3r (entry). [s6M not consumed → excluded.]
BB min/maj swept tight, K r swept wider, × 5 sources. Pass 1 = one 7d window (end 0607); the
winner config is then validated across all 8 windows (run with VALIDATE=1).

Metric: s6 anchor · oob gate · cancel-on-opposite · MAE 0.4 / target 0.9 (current locked rules).
Writes bias_pk_foundation; prints each line's top configs + the all-bests confirm pass.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.indicator_computer import IndicatorComputer as IC
import bias_machine as bm

H = bm.H; MAE, TARGET, FLOOR = 0.4, 0.9, 30
SRCS = ['close', 'hl2', 'hlc3', 'ohlc4', 'hlcc4']
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')

# baseline per line: BB = (kind, tf, len, mult, src) · K = (kind, tf, rsi, stc, k, src)
BASE = {'s6m': ('bb', 6, 10, 0.4, 'hlc3'), 's3m': ('bb', 3, 10, 0.4, 'hlc3'),
        's3M': ('bb', 3, 37, 0.72, 'ohlc4'), 's6r': ('k', 6, 6, 6, 5, 'close'), 's3r': ('k', 3, 6, 6, 5, 'close')}
def gbbmin(tf): return [('bb', tf, L, m, s) for L in (8, 10, 12) for m in (0.3, 0.4, 0.5) for s in SRCS]
def gbbmaj(tf): return [('bb', tf, L, m, s) for L in (30, 37, 44) for m in (0.6, 0.72, 0.84) for s in SRCS]
def gk(tf): return [('k', tf, r, st, k, s) for r in (2, 3, 4, 5, 6, 8, 10) for st in (2, 3, 4, 5, 6, 8) for k in (3, 4, 5, 6, 7) for s in SRCS]
GRIDS = {'s6m': gbbmin(6), 's3m': gbbmin(3), 's3M': gbbmaj(3), 's6r': gk(6), 's3r': gk(3)}


def set_line(W, line, cfg):
    base = W.base
    fr = IC.resample(base, cfg[1] * 60)
    if cfg[0] == 'bb':
        raw = IC.f_bb(IC.build_source(fr, cfg[4]), cfg[2], cfg[3])
        if line == 's6m':
            W.tf(6); W._tfcache[6]['mb'] = raw                # arming raw line (reversals read this)
        elif line == 's3m':
            W.s3m_sign = bm._sign(IC.align_to_base(raw, fr, base))
        elif line == 's3M':
            W.s3M_sign = bm._sign(IC.align_to_base(raw, fr, base))
    else:
        al = IC.align_to_base(IC.f_k(IC.build_source(fr, cfg[5]), cfg[2], cfg[3], cfg[4]), fr, base)
        if line == 's6r':
            W.s6r = al
        elif line == 's3r':
            W.s3r_sign = bm._sign(al)


def score(W):
    pls = W.placements(W.ups_s6r_anchor('oob', 6), MAE, TARGET)
    n = len(pls); c = sum(p['hit'] for p in pls)
    return c, n, (c / n if n else 0.0)


db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
end = next(x for x in ends if dd(x) == '0607')

W = bm.BiasWindow(db, end)
bc, bn, brate = score(W)
print(f'window end {dd(end)} · baseline: {bc}/{bn} correct = {brate:.0%}  (floor ≥{FLOOR})')

rows = []; bests = {}
for line, grid in GRIDS.items():
    res = []
    for cfg in grid:
        set_line(W, line, cfg); c, n, r = score(W); res.append((r, c, n, cfg))
        a = cfg[2]; b = cfg[3]; cc = cfg[4] if cfg[0] == 'k' else None; src = cfg[-1]
        rows.append([line, cfg[0], a, b, cc, src, c, n, round(r, 4)])
    set_line(W, line, BASE[line])                             # restore baseline for next line
    elig = [x for x in res if x[2] >= FLOOR] or res
    best = max(elig, key=lambda x: x[0]); bests[line] = best[3]
    print(f'\n{line}  (baseline {brate:.0%}) — top 5 by rate (≥{FLOOR}):')
    for r, c, n, cfg in sorted([x for x in res if x[2] >= FLOOR], reverse=True)[:5]:
        p = f'{cfg[2]}|{cfg[3]}' + (f'|{cfg[4]}' if cfg[0] == 'k' else '') + f'|{cfg[-1]}'
        print(f'    {p:<22} {c:>3}/{n:<3} {r:>5.0%}{"  *baseline" if cfg == BASE[line] else ""}')

# confirm pass: all per-line bests together
for line, cfg in bests.items():
    set_line(W, line, cfg)
cc, cn, crate = score(W)
print(f'\nCONFIRM (all line-bests together): {cc}/{cn} = {crate:.0%}   vs baseline {brate:.0%}')
print('  bests: ' + ' · '.join(f'{ln}={"|".join(str(x) for x in cfg[2:])}' for ln, cfg in bests.items()))

db.execute('DROP TABLE IF EXISTS bias_pk_foundation')
db.execute('''CREATE TABLE bias_pk_foundation (pk BIGINT AUTO_INCREMENT PRIMARY KEY, line VARCHAR(4),
    kind VARCHAR(2), param_a FLOAT, param_b FLOAT, param_c INT, src VARCHAR(6),
    correct INT, total INT, rate FLOAT)''')
db.executemany('INSERT INTO bias_pk_foundation (line,kind,param_a,param_b,param_c,src,correct,total,rate) '
               'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
db.disconnect()
print(f'\n→ db table bias_pk_foundation ({len(rows)} rows)')
