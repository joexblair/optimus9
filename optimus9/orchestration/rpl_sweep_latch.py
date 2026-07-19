"""Sweep the s30Mage finishing latch (depth x dwell) for BOTH flips against their target flip times.
Reuses rpl_walk.run_walk (one warmup, cached) — no fork. Targets never enter run_walk; they only score
the causal result (no look-ahead). Reports per-walk grids + joint minimax pick.
Targets: 12_01 -> 00:31 (Joe), 12_02 -> 03:26:30 (manual s20 read)."""
import datetime as dtm
from datetime import timezone
import optimus9.orchestration.rpl_walk as R

fmt = R.fmt
def _t(hh, mm, ss=0): return int(dtm.datetime(2026, 7, 12, hh, mm, ss, tzinfo=timezone.utc).timestamp() * 1000)
TARGET = {'12_01': _t(0, 31, 0), '12_02': _t(3, 26, 30)}
DEPTHS = [0, 5, 10, 15, 20, 25, 30]
DWELLS = [1, 2, 3, 4, 6, 9]

def flip_of(walk, d, w):
    _, meta = R.run_walk(walk, d, w)
    return meta['flip_ts']

grids = {}
for walk in TARGET:
    print(f"\n=== {walk}  target {fmt(TARGET[walk])}   (flip time | +min from target) ===")
    print("  dep\\dwl " + "".join(f"{w:>13}" for w in DWELLS))
    g = {}
    for d in DEPTHS:
        row = f"  {d:>6} "
        for w in DWELLS:
            ft = flip_of(walk, d, w); g[(d, w)] = ft
            if ft is None: row += f"{'--':>13}"
            else: row += f"{fmt(ft)+f'{(ft-TARGET[walk])/60000.0:+.0f}':>13}"
        print(row)
    grids[walk] = g

print("\n=== joint pick (minimax over both walks, min of the worse |flip-target|) ===")
best = None
for d in DEPTHS:
    for w in DWELLS:
        a = grids['12_01'][(d, w)]; b = grids['12_02'][(d, w)]
        if a is None or b is None: continue
        ea = abs(a - TARGET['12_01']) / 60000.0; eb = abs(b - TARGET['12_02']) / 60000.0
        worse = max(ea, eb)
        if best is None or worse < best[0]: best = (worse, d, w, a, b, ea, eb)
if best:
    worse, d, w, a, b, ea, eb = best
    print(f"  depth={d} dwell={w}:  12_01 {fmt(a)} ({ea:+.1f}min)   12_02 {fmt(b)} ({eb:+.1f}min)   worse={worse:.1f}min")
else:
    print("  no combo flips both walks")
