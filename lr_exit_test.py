"""
lr_exit_test.py (Joe 0629) — Stage A exit validation against the 131 cf15 entries. Head-to-head:
  lr_exit (A)   — the finisher-core take-profit + SL floor (s30a AND s15a, rlb22). REAL net (incl. losers).
  bracket 0.7/SL — the dumb fixed TP/SL baseline. REAL net.
  mfe ceiling   — the OLD winners-only metric (mfe>=0.7 → 0.7% each). Upper bound, no losers.
PnL: 66k coins · per-trade notional = coins×entry_px · RT cost 0.31% (0.11 fees + 0.20 slip) · $500 start.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_detect, lr_walk, lr_exit, bracket_walk, lr_config


def ms(d): return int(d.replace(tzinfo=timezone.utc).timestamp() * 1000)


COINS, CAP0, COST = 66000, 500.0, 0.31

db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
R1 = ms(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc)); START = ms(dtm.datetime(2026, 6, 17, tzinfo=timezone.utc))
W = bm.BiasWindow(db, R1, cfg=cfg)
lrcfg = lr_config(db)
entries = lr_detect(W, lrcfg, start_ms=START)
exits_a = lr_exit(W, entries, lrcfg, predict_gate=False, fam='s5')
exits_b = lr_exit(W, entries, lrcfg, predict_gate=True, fam='s5')
brk = bracket_walk(W, entries, 0.7, lrcfg.sl, lrcfg.horizon)
walk = lr_walk(W, entries, lrcfg)
entry_pxs = [r[3] for r in exits_a]
print(f"entries: {len(entries)}  ·  exit_rlb={lrcfg.exit_rlb}  sl={lrcfg.sl}%  curl_n={lrcfg.curl_n}")


def summarise(name, rets, pxs):
    rets = np.array(rets, float); net = rets - COST
    pnl = net / 100.0 * COINS * np.array(pxs, float)
    wins = int((rets > 0).sum())
    print(f"  {name:18} n={len(rets):3}  win={wins:3}/{len(rets):<3}={wins/len(rets)*100:3.0f}%  "
          f"gross/t={rets.mean():+.2f}%  net/t={net.mean():+.2f}%  PnL=${pnl.sum():+,.0f}  acct=${CAP0 + pnl.sum():,.0f}")


def reasons_of(ex):
    d = {}
    for r in ex:
        d[r[6]] = d.get(r[6], 0) + 1
    return d


print("\nreasons  A:", reasons_of(exits_a), " B:", reasons_of(exits_b))
summarise("lr_exit A (bare)", [r[5] for r in exits_a], entry_pxs)
summarise("lr_exit B (let-run)", [r[5] for r in exits_b], entry_pxs)
summarise(f"bracket 0.7/{lrcfg.sl}", brk, entry_pxs)

mfe = np.array([r[5] for r in walk]); ok = np.where(mfe >= 0.7)[0]
summarise("mfe ceiling", [0.7] * len(ok), [entry_pxs[i] for i in ok])

# B's question: of the trades whose swing FLIPPED (s5m breached adverse mid-hold), how many hit the SL?
s5m = W.line('s5m')
flip_by_reason = {}; n_flip = 0
for ex, (etms, es, bd, tj) in zip(exits_b, entries):
    ke = int(np.searchsorted(W.ts, ex[1]))                # exit bar
    seg = s5m[tj + 1:ke + 1]
    flipped = bool((seg <= lrcfg.lo).any()) if bd == 1 else bool((seg >= lrcfg.hi).any())
    if flipped:
        n_flip += 1
        flip_by_reason[ex[6]] = flip_by_reason.get(ex[6], 0) + 1
print(f"\nflipped trades (s5m breached adverse mid-hold): {n_flip}  ·  by exit reason: {flip_by_reason}")
diff = sum(1 for a, b in zip(exits_a, exits_b) if a[1] != b[1])
print(f"A (bare) ↔ B (let-run) differing exits: {diff}")

# SL is the obvious suspect (half the trades stop out) — sweep it (entry MAE median ~0.68%)
from dataclasses import replace
mae = np.array([r[4] for r in walk])
print(f"\nentry MAE: median {np.median(mae):.2f}%  mean {mae.mean():.2f}%  (the adverse excursion the SL fights)")
print("SL sweep (lr_exit B let-run, s5):")
for sl in [0.5, 0.68, 0.9, 1.2, 1.5, 2.0]:
    ex = lr_exit(W, entries, replace(lrcfg, sl=sl), predict_gate=True, fam='s5')
    nsl = sum(1 for r in ex if r[6] == 'SL')
    summarise(f"sl={sl} ({nsl}SL)", [r[5] for r in ex], [r[3] for r in ex])
db.disconnect()
