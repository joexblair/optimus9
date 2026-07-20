"""Sweep the GENERIC r (k_len,rsi,stc) + m (mult) line configs, applied board-wide INCLUDING s30
(s30 unified onto the swept generic; separate s30r/s30M parked). Reuses one base tape (base_cache) so
each combo only recomputes lines, not the resample. Runs all 3 walks per combo; metric = pull 12_03's
flip_finisher toward 06:30 while holding 12_01 00:07:55 / 12_02 03:30:55.
Targets never enter run_walk — they only score (causal). Usage: python3 -m optimus9.orchestration.rpl_sweep_config [timing]."""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline, BASE_BIAS
import bias_machine as bm
from optimus9.orchestration.rpl_cache import JigCache
import optimus9.orchestration.rpl_walk as R

end_ms = R.end_ms; TFS = R.TFS; LN = R.LN
fmt = R.fmt
def _t(hh, mm, ss=0): return int(dtm.datetime(2026, 7, 12, hh, mm, ss, tzinfo=timezone.utc).timestamp() * 1000)
TARGET = {'12_01': _t(0, 7, 55), '12_02': _t(3, 30, 55), '12_03': _t(6, 30, 0)}   # hold 01/02, pull 03 to 06:30

# baseline (unswept) generic configs
X = LN['x']; M = LN['M']   # x, Mage not swept
def build_ovr(k_len, rsi, stc, mult):
    """Generic r=(k_len,rsi,stc,close), m=(6,mult,close) applied to EVERY TF incl s30; x/Mage baseline."""
    ovr = {}
    for TF in TFS:
        ovr.update(kline(f'r{TF}', TF, k_len=k_len, rsi=rsi, stc=stc, src='close'))
        ovr.update(bbline(f'x{TF}', TF, length=X['length'], mult=X['mult'], src=X['src']))
        ovr.update(bbline(f'm{TF}', TF, length=6, mult=mult, src='close'))
        ovr.update(bbline(f'M{TF}', TF, length=M['length'], mult=M['mult'], src=M['src']))
    ovr.update(bbline('s1x', 1.0, length=X['length'], mult=X['mult'], src=X['src']))
    ovr.update(bbline('s1m', 1.0, length=6, mult=mult, src='close'))
    ovr.update(kline('s30r', 0.5, k_len=k_len, rsi=rsi, stc=stc, src='close'))   # s30 unified onto generic
    ovr.update(bbline('s30m', 0.5, length=6, mult=mult, src='close'))
    ovr.update(bbline('s30M', 0.5, length=M['length'], mult=M['mult'], src=M['src']))
    ovr.update(bbline('s30x', 0.5, length=X['length'], mult=X['mult'], src=X['src']))
    return ovr

# --- base tape once (live) ---
JB = Jig(end_ms, hours=40, warmup=600)
BC = (JB.W.base, JB.W.ts, JB.W.px); TS = np.asarray(JB.W.ts, np.int64)
FILLER = JB.W._filler_invisible

def run_combo(k_len, rsi, stc, mult):
    ovr = build_ovr(k_len, rsi, stc, mult)
    W = bm.BiasWindow(JB.dev, end_ms, lookback=640, warmup=600, cfg=bm.BiasConfig(**BASE_BIAS),
                      line_overrides=ovr, base_cache=BC, lean=True, filler_invisible=FILLER)
    d = {'__ts__': TS}
    for name in ovr: d[name] = np.asarray(W.line(name), float)
    src = JigCache(d)
    out = {}
    for walk in ('12_01', '12_02', '12_03'):
        _, meta = R.run_walk(walk, src=src)
        out[walk] = meta['flip_ts']
    return out

BASE = (LN['r']['k_len'], LN['r']['rsi'], LN['r']['stc'], LN['m']['mult'])   # (7,5,11,0.45)

if len(sys.argv) > 1 and sys.argv[1] == 'timing':
    import time
    combos = [BASE, (6, 5, 11, 0.45), (7, 5, 11, 0.55), (8, 6, 12, 0.35)]
    for c in combos:
        t0 = time.time(); o = run_combo(*c); dt = time.time() - t0
        print(f"  k{c[0]} rsi{c[1]} stc{c[2]} m{c[3]}:  " +
              "  ".join(f"{w}={fmt(o[w]) if o[w] else '--'}" for w in ('12_01', '12_02', '12_03')) +
              f"   [{dt:.1f}s]")
    sys.exit(0)

# --- full grid ---
K = [5, 6, 7, 8, 9]; RSI = [3, 4, 5, 6, 7]; STC = [9, 10, 11, 12, 13]; MULT = [0.25, 0.35, 0.45, 0.55, 0.65]
rows = []
n = 0; total = len(K) * len(RSI) * len(STC) * len(MULT)
for k in K:
    for rsi in RSI:
        for stc in STC:
            for mult in MULT:
                o = run_combo(k, rsi, stc, mult); n += 1
                d03 = abs(o['12_03'] - TARGET['12_03']) / 60000.0 if o['12_03'] else 9e9
                hold01 = o['12_01'] is not None and abs(o['12_01'] - TARGET['12_01']) <= 120000
                hold02 = o['12_02'] is not None and abs(o['12_02'] - TARGET['12_02']) <= 120000
                rows.append((k, rsi, stc, mult, o, d03, hold01, hold02))
                if n % 25 == 0: print(f"  ... {n}/{total}")

# hold 01/02 (within 2min) and rank by 12_03 closeness to 06:30
keep = [r for r in rows if r[6] and r[7] and r[5] < 9e9]
keep.sort(key=lambda r: r[5])
print(f"\n=== combos holding 12_01/12_02 (+-2min), ranked by 12_03 closeness to 06:30 ({len(keep)}/{total}) ===")
print(f"  {'k':>2} {'rsi':>3} {'stc':>3} {'mult':>5}   {'12_01':>8} {'12_02':>8} {'12_03':>8}  d03(min)")
for k, rsi, stc, mult, o, d03, _, _ in keep[:20]:
    print(f"  {k:>2} {rsi:>3} {stc:>3} {mult:>5.2f}   {fmt(o['12_01']):>8} {fmt(o['12_02']):>8} {fmt(o['12_03']):>8}  {d03:+.1f}")
b = next((r for r in rows if (r[0], r[1], r[2], r[3]) == BASE), None)
if b: print(f"\n  baseline (7,5,11,0.45): 12_01 {fmt(b[4]['12_01'])} 12_02 {fmt(b[4]['12_02'])} 12_03 {fmt(b[4]['12_03'])}")
