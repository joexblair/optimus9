"""
lr_exit_sweep.py (Joe 0629) — find the most profitable exit config. Pred+breach fixed on s5; sweep the curl
line {s5,s6,s7,s8} × the exit trigger {curl, s30a, s30a_s15a}. Test set = entries with MAE < 0.5% (the rest
are entry-filtering's job). Then trace the exit-flow for two named trades under the best config.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_detect, lr_walk, lr_exit, lr_config
from optimus9.compute.breaching_line import predict_breach
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.constants import FENCE_HI, FENCE_LO


def ms(d): return int(d.replace(tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000).strftime('%m%d %H:%M:%S')


COINS, CAP0, COST = 66000, 500.0, 0.31
db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
R1 = ms(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc)); START = ms(dtm.datetime(2026, 6, 17, tzinfo=timezone.utc))
W = bm.BiasWindow(db, R1, cfg=cfg); lrcfg = lr_config(db)
ts, px = W.ts, W.px
entries = lr_detect(W, lrcfg, start_ms=START)
walk = lr_walk(W, entries, lrcfg)
mae = np.array([r[4] for r in walk])
keep = [entries[i] for i in range(len(entries)) if mae[i] < 0.5]
print(f"entries {len(entries)} → MAE<0.5% kept {len(keep)}")


def netpnl(rows):
    rets = np.array([r[5] for r in rows]); net = rets - COST
    pnl = (net / 100.0 * COINS * np.array([r[3] for r in rows])).sum()
    return pnl, int((rets > 0).sum()), len(rows), net.mean()


print(f"\n{'curl':5} {'exit_on':11} {'PnL':>9} {'acct':>8} {'win':>11} {'net/t':>7}")
best = None
for curl_fam in ['s5', 's6', 's7', 's8']:
    for exit_on in ['curl', 's30a', 's30a_s15a']:
        rows = lr_exit(W, keep, lrcfg, curl_fam=curl_fam, exit_on=exit_on)
        pnl, wins, nn, nt = netpnl(rows)
        print(f"{curl_fam:5} {exit_on:11} ${pnl:+8,.0f} ${CAP0 + pnl:7,.0f}  {wins:3}/{nn:<3}={wins / nn * 100:3.0f}% {nt:+.2f}%")
        if best is None or pnl > best[0]:
            best = (pnl, curl_fam, exit_on)
print(f"\nBEST: curl={best[1]} · exit_on={best[2]} → ${best[0]:+,.0f}  (acct ${CAP0 + best[0]:,.0f})")


def trace(label, curl_fam, exit_on):
    ent = next((e for e in entries if dts(e[0]) == label), None)
    if ent is None:
        print(f"\n{label}: not found"); return
    tms, es, bd, tj = ent; fav_hi = (bd == 1)
    s5m = W.line('s5m')
    pred = predict_breach(W.line('s5r'), s5m, W.line('s5M'), lrcfg.hi, lrcfg.lo, FENCE_HI, FENCE_LO)
    cr = W.line(f'{curl_fam}r'); cwob = IC.wobble_slayer(cr, lrcfg.curl_n, lrcfg.hi, lrcfg.lo, anchored=True, strict=True)
    arm = (s5m >= lrcfg.hi) if fav_hi else (s5m <= lrcfg.lo)
    curl = ((cwob == -1) & (cr >= lrcfg.hi)) if fav_hi else ((cwob == 1) & (cr <= lrcfg.lo))
    r = lr_exit(W, [ent], lrcfg, curl_fam=curl_fam, exit_on=exit_on)[0]
    ek = int(np.searchsorted(ts, r[1]))
    print(f"\nTRACE {label}  bd{bd:+d}  entry@{px[tj]:.4f}  [curl={curl_fam} exit_on={exit_on}]  → {r[6]} ret{r[5]:+.2f}%")
    for kk in range(tj + 1, ek + 1):
        tags = []
        if arm[kk] and not arm[kk - 1]:
            tags.append('s5m-ARM')
        if pred[kk] == bd and pred[kk - 1] != bd:
            tags.append('s5r-PRED')
        if curl[kk] and not curl[kk - 1]:
            tags.append(f'{curl_fam}r-CURL')
        if kk == ek:
            tags.append('EXIT')
        if tags:
            print(f"  +{(kk - tj) * 5:>5}s  {dts(ts[kk])}  ret{(px[kk] - px[tj]) / px[tj] * 100 * bd:+.2f}%  {' · '.join(tags)}")


trace('0617 12:29:35', best[1], best[2])
trace('0617 05:42:10', best[1], best[2])
db.disconnect()
