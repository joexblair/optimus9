"""arm_cancel_ab.py — A/B the s2Mage cancel-stay on the last N hours. (Joe 0710)

Baseline cancel: the arm dies at the FIRST opposite-side s5m breach.
Stayed cancel : an opposite s5m breach is STAYED if s2Mage reverses toward es within `win` after it
                (the sell-off that drove the breach is reversing) — the arm survives to the next breach.
Both feed fin_unlatch_6of9 (breach mode). Prints every arm's trade + MAE/MFE under each, and the diff.
All reads via the jig.  python3 arm_cancel_ab.py --hours 24
"""
import argparse, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from optimus9.analysis.lr_v2 import s_qualify, fin_box_qualified
import arm_walk as AW
from optimus9 import DatabaseManager
from optimus9.config import get_db_config

ap = argparse.ArgumentParser()
ap.add_argument('--hours', type=float, default=24)
ap.add_argument('--win', type=int, default=60, help='5s bars after an opposite breach to look for the s2Mage stay (60=300s)')
ap.add_argument('--wob', type=int, default=1)
cli = ap.parse_args()

_d = DatabaseManager(**get_db_config()); _d.connect()
now = int(_d.execute('SELECT MAX(kc_timestamp) t FROM kline_collection', fetch=True)[0]['t']); _d.disconnect()
t0 = now - int(cli.hours * 3600_000)
TFS = AW.DEFAULT_TFS; bands = AW.parse_bands(AW.DEFAULT_BANDS)
ov = AW.overrides(TFS, 7, 0.50)
ov['gcs5M'] = (5, ('bb', 37, 0.6, 'ohlc4'), 'emerging'); ov['s15M'] = (15, ('bb', 37, 0.6, 'ohlc4'), 'emerging')
ov['s2Mage'] = (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging')             # spec 60s line, not in DB

with Jig(now + 60_000, hours=max(30, cli.hours + 6), warmup=90, overrides=ov) as j:
    W, cfg, C = j.W, j.cfg, j.causal
    ts, px = np.asarray(j.ts, np.int64), j.px
    f = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
    s5m = C.line('s5m'); seam = (ts % 300_000) == 0
    sd = lambda k: 1 if s5m[k] >= 85 else (-1 if s5m[k] <= 15 else 0)
    ks = [int(k) for k in np.flatnonzero(seam)]
    rev2M = C.reversal(C.line('s2Mage'), cli.wob)                      # +1 up-turn / -1 down-turn
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
            arms.setdefault((armed[0], es), True)

    def cancel_base(kA, es):
        return next((k for k in ks if k > kA and sd(k) == -es), len(ts) - 1)

    def cancel_stay(kA, es):
        for kb in [k for k in ks if k > kA and sd(k) == -es]:
            w1 = min(kb + cli.win, len(ts) - 1)
            if not np.any(rev2M[kb + 1:w1 + 1] == es):                # s2Mage did NOT reverse toward es -> real cancel
                return kb
        return len(ts) - 1

    def trade(kA, es, cap):
        bd = -es; q15 = q15hi if bd == -1 else q15lo; q30 = q30hi if bd == -1 else q30lo
        if not fin_box_qualified(q15, q30, kA, cfg.fin_lb, cfg.fin_fwd):
            return None
        return C.fin_unlatch_6of9(kA, cap, es, q15, q30, N=6)

    def exc(kT, kx, bd):
        e = px[kT]; path = bd * (px[kT:kx + 1] - e) / e * 100
        return -float(np.nanmin(np.minimum(path, 0.0))), float(np.nanmax(np.maximum(path, 0.0)))

    rows = []
    for (kA, es) in sorted(arms):
        bd = -es
        cb, cs = cancel_base(kA, es), cancel_stay(kA, es)
        kTb, kTs = trade(kA, es, cb), trade(kA, es, cs)
        r = dict(kA=kA, es=es, bd=bd, cb=cb, cs=cs, kTb=kTb, kTs=kTs)
        for tag, kT, cap in (('b', kTb, cb), ('s', kTs, cs)):
            if kT is not None and kT < cap:
                kx = AW.take_profit(AW.board(j, TFS, es, 0.0, bands), kT, AW.tp_tf(AW.board(j, TFS, es, 0.0, bands), kT, 5), cap) or cap
                mae, mfe = exc(kT, kx, bd)
                r[tag] = dict(kT=kT, kx=kx, mae=mae, mfe=mfe)
            else:
                r[tag] = None
        rows.append(r)

    print(f"\ns2Mage cancel-stay A/B, last {cli.hours:.0f}h  win={cli.win*5}s  wob={cli.wob}")
    print(f"{'arm':<16} {'es':>3} {'baseline trade':<16} {'baseMAE/MFE':>12} {'stayed trade':<16} {'stayMAE/MFE':>12}  diff")
    nb = ns = 0
    for r in rows:
        b, s = r['b'], r['s']
        bt = f(b['kT']) if b else '-'; st = f(s['kT']) if s else '-'
        bm = f"{b['mae']:.2f}/{b['mfe']:.2f}" if b else '-'; sm = f"{s['mae']:.2f}/{s['mfe']:.2f}" if s else '-'
        diff = ''
        if not b and s: diff = 'NEW'; ns += 1
        elif b and not s: diff = 'LOST'
        elif b and s and b['kT'] != s['kT']: diff = 'MOVED'
        if b: nb += 1
        if s: ns += 0
        if diff or b or s:
            print(f"{f(r['kA']):<16} {r['es']:+3d} {bt:<16} {bm:>12} {st:<16} {sm:>12}  {diff}")
    tb = [r['b'] for r in rows if r['b']]; tsr = [r['s'] for r in rows if r['s']]
    print(f"\nbaseline: {len(tb)} trades  MAE p50 {np.median([x['mae'] for x in tb]) if tb else 0:.2f}  MFE p50 {np.median([x['mfe'] for x in tb]) if tb else 0:.2f}")
    print(f"stayed  : {len(tsr)} trades  MAE p50 {np.median([x['mae'] for x in tsr]) if tsr else 0:.2f}  MFE p50 {np.median([x['mfe'] for x in tsr]) if tsr else 0:.2f}")
    new = [r for r in rows if not r['b'] and r['s']]; lost = [r for r in rows if r['b'] and not r['s']]
    print(f"NEW trades: {len(new)}   LOST trades: {len(lost)}")
