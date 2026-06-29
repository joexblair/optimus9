"""
lr_exit_s5_report.py (Joe 0629) — report the cases where the s5 exit prediction fires. Wiring per Joe:
predict_breach(s5r, s5m, s5M) is RE-TESTED every bar while s5m is OOB favourable (not once at the arm).
On fire, wait for s5r to curl OOB (wobslay curl_n) — but if the swing flips adverse mid-wait (s5m breaches
the OTHER side), the swing's gone: that's the missed-swing case Joe flagged. Per-trade outcome + aggregate.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_detect, lr_config
from optimus9.compute.breaching_line import predict_breach
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.constants import FENCE_HI, FENCE_LO


def ms(d): return int(d.replace(tzinfo=timezone.utc).timestamp() * 1000)


def dt(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000).strftime('%m%d %H:%M')


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
R1 = ms(dtm.datetime(2026, 6, 22, tzinfo=timezone.utc)); START = ms(dtm.datetime(2026, 6, 17, tzinfo=timezone.utc))
W = bm.BiasWindow(db, R1, cfg=cfg); lrcfg = lr_config(db)
entries = lr_detect(W, lrcfg, start_ms=START)
ts, px, n, hi, lo = W.ts, W.px, len(W.ts), lrcfg.hi, lrcfg.lo
s5m, s5r, s5M = W.line('s5m'), W.line('s5r'), W.line('s5M')
pred = predict_breach(s5r, s5m, s5M, hi, lo, FENCE_HI, FENCE_LO)
wob = IC.wobble_slayer(s5r, lrcfg.curl_n, hi, lo, anchored=True, strict=True)
curl_hi = (wob == -1) & (s5r >= hi); curl_lo = (wob == 1) & (s5r <= lo)

fired = curled = flipped = ranout = adv_before = 0
rides = []
print(f"cases where prediction fired (s5, re-tested while s5m OOB):")
print(f"  {'entry':11} bd  predLag  outcome   en→curl%")
for tms, es, bd, tj in entries:
    armf = (s5m >= hi) if bd == 1 else (s5m <= lo)
    arma = (s5m <= lo) if bd == 1 else (s5m >= hi)
    curl = curl_hi if bd == 1 else curl_lo
    armk = firek = curlk = flipk = advk = None
    for kk in range(tj + 1, min(n, tj + lrcfg.horizon)):
        if firek is None:
            if arma[kk] and advk is None:
                advk = kk
            if armf[kk]:
                if armk is None:
                    armk = kk
                if pred[kk] == bd:
                    firek = kk
        else:                                              # waiting for the curl
            if arma[kk]:
                flipk = kk; break                          # swing flipped adverse mid-wait → missed
            if armf[kk] and curl[kk]:
                curlk = kk; break
    if firek is None:
        if advk is not None:
            adv_before += 1
        continue
    fired += 1
    if curlk is not None:
        curled += 1; en = (px[curlk] - px[tj]) / px[tj] * 100 * bd; rides.append(en); out, val = 'CURL', f"{en:+.2f}"
    elif flipk is not None:
        flipped += 1; out, val = 'flip-adv', '-'
    else:
        ranout += 1; out, val = 'ranout', '-'
    lag = f"{(firek - armk) * 5}s" if armk is not None else '-'
    print(f"  {dt(tms):11} {bd:+d}  {lag:>6}  {out:8}  {val:>7}")

print(f"\nfired {fired}/{len(entries)}  ·  outcomes: CURL {curled} · flip-adverse {flipped} · ranout {ranout}")
print(f"never-fired (swing flipped adverse before any predict): {adv_before}")
if rides:
    rides = np.array(rides)
    print(f"entry→curl when it curls: median {np.median(rides):+.2f}%  mean {rides.mean():+.2f}%  "
          f"win {int((rides > 0).sum())}/{len(rides)}")
db.disconnect()
