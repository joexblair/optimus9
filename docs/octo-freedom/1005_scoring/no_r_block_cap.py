"""`no r block` with Joe's 0.95% MAE cap.

JOE 1006: *"apply an MAE cap of 0.95%. if the cap is reached, mark the traded MFE as 0."*

MAE_CAP IS JOE'S, 0.95 pct. It is not swept and not fitted.

WHY THE ORDERING IS REPORTED. score39.score takes BOTH extremes over the SAME stretch - mfe from
seg.max()/seg.min() and mae from the other end of the same segment - so neither is time-ordered
against the other. Joe's rule zeroes the MFE whenever the cap is touched, which is right when the
adverse extreme comes FIRST and pessimistic when the favourable one does. This file re-walks each
stretch to find WHICH bar each extreme sits on, so the pessimistic rows are counted rather than
assumed away. The rule is applied exactly as Joe stated it either way.
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

MAE_CAP, CAP = 0.95, 0.75
DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
H, L = SC.pivots(float(SC.LG['swing']))

rows = []
for day in DAYS:
    p = os.path.join('octosig', '%s.out' % day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f = ln.rstrip('\n').split('|')
        if len(f) < 7 or not re.match(r'^\d\d:\d\d:\d\d$', f[2]): continue
        k = SC.K('%s %s' % (day, f[2])); r = SC.classify(k, f[2])
        if (r.get('D') or {}).get('why') != 'no r block': continue
        ex = int(r['m']['ex']) if r['m'].get('ex') is not None else k
        d = int(SC.DRv[k])
        if d == 0: continue
        kk = ex if ex > k else k
        dt = -d                                           # counter-dr, the baked flip
        mfe, mae, j = SC.score(kk, dt, H, L)
        if mae is None: continue
        # which BAR each extreme sits on, over the same stretch score() used
        seg = SC.PX[kk:j + 1]; idx = np.arange(kk, j + 1)
        ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
        if dt > 0: kf, km = int(idx[int(seg.argmin())]), int(idx[int(seg.argmax())])
        else:      kf, km = int(idx[int(seg.argmax())]), int(idx[int(seg.argmin())])
        rows.append(dict(day=day, sig=f[2], side=('LONG' if dt < 0 else 'SHORT'),
                         mae=mae, mfe=mfe, kf=kf, km=km,
                         capped=(mae >= MAE_CAP), mfe_first=(kf < km),
                         kmae=SC.U(km), kmfe=SC.U(kf)))

n = len(rows)
cp = [r for r in rows if r['capped']]
for r in rows: r['mfe_cap'] = 0.0 if r['capped'] else r['mfe']

print('# `no r block` WITH JOE\'S %.2f%% MAE CAP   capture %.0f%% of MFE   %s'
      % (MAE_CAP, CAP*100, SC.LG_KEY))
print('# rule: MAE >= %.2f -> traded MFE = 0' % MAE_CAP)
print('\n| | trades |'); print('|---|---|')
print('| population | %d |' % n)
print('| **cap reached (MAE >= %.2f)** | **%d** |' % (MAE_CAP, len(cp)))
print('| under the cap | %d |' % (n - len(cp)))
print('| of the capped, MFE extreme came BEFORE the MAE extreme | %d |'
      % sum(1 for r in cp if r['mfe_first']))
print('| of the capped, MAE extreme came first (rule is exact) | %d |'
      % sum(1 for r in cp if not r['mfe_first']))

print('\n# THE CAPPED TRADES — MFE zeroed by the rule')
print('| day | octo-sig | side | MAE | MFE before the cap | MAE bar | MFE bar | MFE came first? | MFE lost |')
print('|---|---|---|---|---|---|---|---|---|')
for r in sorted(cp, key=lambda x: (x['day'], x['sig'])):
    print('| %s | %s | %s | %.4f | %.4f | %s | %s | %s | %.4f |'
          % (r['day'], r['sig'], r['side'], r['mae'], r['mfe'], r['kmae'], r['kmfe'],
             'YES' if r['mfe_first'] else 'no', r['mfe']))

print('\n# THE SUMMARY, BEFORE AND AFTER THE CAP')
print('| | trades | sum MFE | sum CAPTURE @75%% | mean capture | MFE>MAE | zero-MFE trades |')
print('|---|---|---|---|---|---|---|')
for lbl, key in (('no cap (as banked)', 'mfe'), ('**MAE cap %.2f**' % MAE_CAP, 'mfe_cap')):
    s = sum(r[key] for r in rows)
    print('| %s | %d | %+.3f | %+.3f | %+.4f | %d of %d | %d |'
          % (lbl, n, s, CAP*s, CAP*s/n,
             sum(1 for r in rows if r[key] > r['mae']), n,
             sum(1 for r in rows if r[key] == 0.0)))

print('\n# PER DAY, WITH THE CAP APPLIED')
print('| day | trades | capped | sum MFE capped | sum CAPTURE @75%% | median MAE | worst MAE |')
print('|---|---|---|---|---|---|---|')
for d in sorted({r['day'] for r in rows}):
    s = [r for r in rows if r['day'] == d]
    mm = sorted(x['mae'] for x in s); ff = sum(x['mfe_cap'] for x in s)
    print('| %s | %d | %d | %+.3f | %+.3f | %.4f | %.4f |'
          % (d, len(s), sum(1 for x in s if x['capped']), ff, CAP*ff, mm[len(mm)//2], max(mm)))
tot = sum(r['mfe_cap'] for r in rows)
print('| **TOTAL** | **%d** | **%d** | **%+.3f** | **%+.3f** | | |' % (n, len(cp), tot, CAP*tot))
print('\n| | value |'); print('|---|---|')
print('| capture per trade | %+.4f |' % (CAP*tot/n))
print('| capture per day | %+.4f |' % (CAP*tot/len({r['day'] for r in rows})))
