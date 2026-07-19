"""hs_ladder.py — predict coverage + momo curl across the coarse r-pred ladder. (Joe 0714)

The ladder cancels the premature hs30 cross (11:00) by confirming the COARSE leg is real before the
arm is valid. Joe is choosing the rungs empirically: hs37 alone doesn't pick up the prediction at
mult 0.56, so hs33 is added. This traces WHERE each rung's predict fires, so the rung set is chosen
on measured coverage, not TF-picking.

LADDER   hs30 -> hs33 -> hs37 -> hs45   (all clones)
  r    k 7|5|7|ohlc4        m  bb 6|0.56|ohlc4        Mage bb 37|0.83|ohlc4
predict = jig.causal.predict(r, m, Mage)  -> fires only when r is in the engage band (70..85 / 15..30)
momo   = the coarse curl on r (jig.causal.curl) — the TIMER Joe transposes to the hs30 cross.

QUESTION: does the UNION of the rungs' predict give continuous coverage from the 11:00 premature cross
to the 14:30 arm on 07-11?  And when does momo fire on hs45r (~12:45 in Joe's read)?

Causal/emerging; every read via the jig.
  python3 hs_ladder.py [YYYY-MM-DD] [h0] [h1]        (default 2026-07-11, 09, 16)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline

TFS = [30, 33, 37, 45]
HI, LO, FH, FL = 85.0, 15.0, 70.0, 30.0
R    = dict(k_len=7, rsi=5,  stc=7,  src='ohlc4')
MULT = {30: 0.56, 33: 0.45, 37: 0.45, 45: 0.56}     # Joe 0714: intermediaries 33/37 at 0.45
MAGE = dict(length=37, mult=0.83, src='ohlc4')

DAY = sys.argv[1] if len(sys.argv) > 1 else '2026-07-11'
H0  = int(sys.argv[2]) if len(sys.argv) > 2 else 9
H1  = int(sys.argv[3]) if len(sys.argv) > 3 else 16
y, mo, d = map(int, DAY.split('-'))
end_ms = int(dtm.datetime(y, mo, d, H1, 0, tzinfo=timezone.utc).timestamp() * 1000)


def overrides():
    o = {}
    for tf in TFS:
        o.update(kline(f'hs{tf}r', tf, **R))
        o.update(bbline(f'hs{tf}m', tf, length=6, mult=MULT[tf], src='ohlc4'))
        o.update(bbline(f'hs{tf}Mage', tf, **MAGE))
    return o


with Jig(end_ms, hours=48, warmup=600, overrides=overrides()) as j:
    C, ts = j.causal, np.asarray(j.ts, np.int64)
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc)
    w0 = int(dtm.datetime(y, mo, d, H0, 0, tzinfo=timezone.utc).timestamp() * 1000)
    w1 = int(dtm.datetime(y, mo, d, H1, 0, tzinfo=timezone.utc).timestamp() * 1000)

    print(f'{DAY}  {H0:02d}:00 → {H1:02d}:00 UTC   ·   ladder {TFS}\n')

    for tf in TFS:
        g = (ts % (tf * 60 * 1000)) == 0
        bts = ts[g]
        r    = C.line(f'hs{tf}r')[g]
        m    = C.line(f'hs{tf}m')[g]
        mage = C.line(f'hs{tf}Mage')[g]
        pred = C.predict(r, m, mage)
        curl_lo = {int(np.searchsorted(bts, t)) for t in C.curl(bts, r, +1)}   # trough
        curl_hi = {int(np.searchsorted(bts, t)) for t in C.curl(bts, r, -1)}   # peak

        win = np.flatnonzero((bts >= w0) & (bts <= w1))
        print(f'--- hs{tf}  (r 7|5|7 · m 6|{MULT[tf]} · Mage 37|0.83) ---')
        print(f"    {'time':<6} {'r':>6} {'m':>6} {'Mage':>7} {'OOB':>4} {'PRED':>5} {'curl':>5}")
        for i in win:
            oob = 'HI' if r[i] >= HI else ('LO' if r[i] <= LO else ('.hi' if r[i] >= FH else ('.lo' if r[i] <= FL else '')))
            pr = {1: 'HI', -1: 'LO', 0: ''}[int(pred[i])]
            cl = 'TRGH' if i in curl_lo else ('PEAK' if i in curl_hi else '')
            print(f"    {dt(bts[i]):%H:%M} {r[i]:>6.1f} {m[i]:>6.1f} {mage[i]:>7.1f} {oob:>4} {pr:>5} {cl:>5}")
        print()

    # union predict coverage on the 30-min grid (the arm's cadence)
    g30 = (ts % (30 * 60 * 1000)) == 0
    b30 = ts[g30]
    cov = np.zeros(len(b30), int)
    for tf in TFS:
        gt = (ts % (tf * 60 * 1000)) == 0
        bt = ts[gt]
        r = C.line(f'hs{tf}r')[gt]; m = C.line(f'hs{tf}m')[gt]; mage = C.line(f'hs{tf}Mage')[gt]
        p = C.predict(r, m, mage)
        # broadcast each rung's last-known predict onto the 30-min grid (causal)
        slot = np.searchsorted(bt, b30, side='right') - 1
        slot = np.clip(slot, 0, len(bt) - 1)
        cov = np.where(p[slot] != 0, np.where(cov == 0, p[slot], cov), cov)

    win = np.flatnonzero((b30 >= w0) & (b30 <= w1))
    print('--- UNION predict coverage on the 30-min arm grid ---')
    print(f"    {'time':<6} {'anyPRED':>8}   rung(s)")
    for i in win:
        rungs = []
        for tf in TFS:
            gt = (ts % (tf * 60 * 1000)) == 0
            bt = ts[gt]
            r = C.line(f'hs{tf}r')[gt]; m = C.line(f'hs{tf}m')[gt]; mage = C.line(f'hs{tf}Mage')[gt]
            p = C.predict(r, m, mage)
            s = min(np.searchsorted(bt, b30[i], side='right') - 1, len(bt) - 1)
            if s >= 0 and p[s] != 0:
                rungs.append(f'{tf}:{ "HI" if p[s]==1 else "LO" }')
        print(f"    {dt(b30[i]):%H:%M} {('YES' if rungs else '—'):>8}   {' '.join(rungs)}")
