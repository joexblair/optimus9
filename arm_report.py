"""arm_report.py — arm-delay trades over a window: arm/trade times + two-anchor MAE/MFE. (Joe 0710)

Uses the nof9 build (arm ladder -> box qualifier -> 6of9 trigger -> far-side-mini TP), all via the jig.
Prints the table and (re)writes a bgcolor pine. Excursions run to the real TP exit — no fixed horizon.

  python3 arm_report.py --hours 24 --pine transfer/arm_20260709.pine
"""
import argparse, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from optimus9.analysis.lr_v2 import gate_open, s_qualify, fin_gate, fin_box_qualified
import arm_walk as AW

COST = 0.20


def exc(px, k0, kx, bd):
    e = px[k0]; path = bd * (px[k0:kx + 1] - e) / e * 100
    return float(np.nanmax(np.maximum(path, 0.0))), -float(np.nanmin(np.minimum(path, 0.0)))


ap = argparse.ArgumentParser()
ap.add_argument('--hours', type=float, default=24)
ap.add_argument('--producer', default='nof9', choices=['nof9', 'gate'])
ap.add_argument('--n-of9', type=int, default=6)
ap.add_argument('--pine', default='transfer/arm_20260709.pine')
cli = ap.parse_args()

from optimus9 import DatabaseManager
from optimus9.config import get_db_config
_d = DatabaseManager(**get_db_config()); _d.connect()
now = int(_d.execute('SELECT MAX(kc_timestamp) t FROM kline_collection', fetch=True)[0]['t'])
_d.disconnect()
t0 = now - int(cli.hours * 3600_000)
TFS = AW.DEFAULT_TFS; bands = AW.parse_bands(AW.DEFAULT_BANDS)
ov = AW.overrides(TFS, 7, 0.50)
ov['gcs5M'] = (5, ('bb', 37, 0.6, 'ohlc4'), 'emerging')
ov['s15M'] = (15, ('bb', 37, 0.6, 'ohlc4'), 'emerging')

with Jig(now + 60_000, hours=max(30, cli.hours + 6), warmup=90, overrides=ov) as j:
    W, cfg = j.W, j.cfg
    ts, px = np.asarray(j.ts, np.int64), j.px
    f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
    s5m = j.causal.line('s5m'); seam5 = (ts % 300_000) == 0
    sd = lambda k: 1 if s5m[k] >= 85 else (-1 if s5m[k] <= 15 else 0)
    ks = [int(k) for k in np.flatnonzero(seam5)]
    hunts = [(ks[i], sd(ks[i])) for i in range(1, len(ks))
             if sd(ks[i]) and sd(ks[i]) != sd(ks[i - 1]) and t0 <= ts[ks[i]] <= now]
    q15hi, q15lo = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
    q30hi, q30lo = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
    arms = {}
    for (kh, es) in hunts:
        B = AW.board(j, TFS, es, 0.0, bands)
        _e, armed, _c = AW.walk(B, kh, len(ts) - 1, cancel_on='none', permission=False,
                                latch=True, arm_mode='latch', allib='off')
        if armed:
            arms.setdefault((armed[0], es), {'tf': armed[1], 'B': B})
    def cancel_bar(kA, es):                                        # arm's natural life = next opposite s5m breach
        nb = next((k for k in ks if k > kA and sd(k) == -es), None)
        return nb if nb is not None else len(ts) - 1
    rows = []
    for (kA, es), v in sorted(arms.items()):
        bd = -es
        cap = cancel_bar(kA, es)                                   # arm live until the opposite s5m breach — no cap
        q15 = q15hi if bd == -1 else q15lo; q30 = q30hi if bd == -1 else q30lo
        qual = fin_box_qualified(q15, q30, kA, cfg.fin_lb, cfg.fin_fwd)
        if cli.producer == 'nof9':
            kT = j.causal.fin_unlatch_6of9(kA, cap, es, q15, q30, N=cli.n_of9) if qual else None
        else:
            g = gate_open(W, cfg, [(kA, es, bd, cap, 'arm')]); ok = g[0][3] if g else None
            kT = fin_gate(q15, q30, ok, cap) if ok is not None else None
        traded = kT is not None and kT < cap
        kend = cap                                                 # arm excursion runs to the arm's cancel
        amf, ama = exc(px, kA, kend, bd)
        if traded:
            kx = AW.take_profit(v['B'], kT, AW.tp_tf(v['B'], kT, v['tf']), cap) or cap
            tmf, tma = exc(px, kT, kx, bd)
            status = 'TRADED'
        else:
            kx = None; tmf = tma = None
            status = 'QUALIFIED' if qual else 'ARMED'             # QUALIFIED = box ok but no 6of9 trigger
        rows.append(dict(kA=kA, kT=kT, kx=kx, tf=v['tf'], bd=bd, status=status,
                         armed=f(kA), trade=(f(kT) if traded else '-'), amf=amf, ama=ama, tmf=tmf, tma=tma))

nT = sum(1 for r in rows if r['status'] == 'TRADED')
nQ = sum(1 for r in rows if r['status'] == 'QUALIFIED')
print(f"\narm-delay report, last {cli.hours:.0f}h ({dtm.datetime.utcfromtimestamp(t0/1000):%m-%d %H:%M} -> "
      f"{dtm.datetime.utcfromtimestamp(now/1000):%m-%d %H:%M})  producer={cli.producer}")
print(f"  {len(rows)} arms · {nQ+nT} box-qualified · {nT} traded    (armMAE/MFE = arm->cancel · trMAE/MFE = trade->exit)")
print(f"{'arm':<16} {'trade':<16} {'side':>4} {'status':>10} {'armMAE':>7} {'armMFE':>7} {'trMAE':>7} {'trMFE':>7}")
for r in rows:
    tm = f"{r['tma']:6.2f}% {r['tmf']:6.2f}%" if r['status'] == 'TRADED' else f"{'-':>7} {'-':>7}"
    print(f"{r['armed']:<16} {r['trade']:<16} {'S' if r['bd']<0 else 'L':>4} {r['status']:>10}"
          f" {r['ama']:6.2f}% {r['amf']:6.2f}% {tm}")

tr = [r for r in rows if r['status'] == 'TRADED']
streams = [
    {'name': 'arm', 'ts': [int(j.ts[r['kA']]) for r in rows], 'color': 'color.gray'},
    {'name': 'long', 'ts': [int(j.ts[r['kT']]) for r in tr if r['bd'] == 1], 'color': 'color.green'},
    {'name': 'short', 'ts': [int(j.ts[r['kT']]) for r in tr if r['bd'] == -1], 'color': 'color.red'},
    {'name': 'exit', 'ts': [int(j.ts[r['kx']]) for r in tr], 'color': 'color.white'},
]
n = j.score.emit_bgcolor(streams, cli.pine, f"arm-delay last {cli.hours:.0f}h ({len(rows)} trades)  grey=arm green=long red=short white=exit")
print(f"\npine -> {cli.pine}  ({n} painted bars)")
