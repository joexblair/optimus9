"""Legs 10 and 11: the MFE/MAE bars, and what leg 11 was waiting on. Joe 1007."""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
M2, R12 = C.M2, C.R[12]
K = lambda t: SC.K('2026-09-25 %s' % t)
def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; idx = np.arange(s_, e_ + 1)
    ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
    p_ = float(PX[s_])
    f = int(seg.argmax()) if dd > 0 else int(seg.argmin())
    g = int(seg.argmin()) if dd > 0 else int(seg.argmax())
    return dict(mfe=(float(seg[f]) - p_) / p_ * 100.0 * dd, mfe_bar=int(idx[f]),
                mae=max(0.0, -((float(seg[g]) - p_) / p_ * 100.0 * dd)), mae_bar=int(idx[g]))
print('# THE MFE AND MAE BARS')
rows = []
for lbl, a, b, dd in (('leg 10 LONG', '10:17:05', '10:56:40', +1),
                      ('leg 11 SHORT', '10:56:40', '11:07:45', -1)):
    m = mm(K(a), K(b), dd)
    rows.append((lbl, a, b, '%.4f' % m['mae'], SC.U(m['mae_bar']),
                 '%.4f' % m['mfe'], SC.U(m['mfe_bar']),
                 '%+.1f' % ((int(SC.ts[m['mfe_bar']]) - int(SC.ts[K(a)])) / 60000.0)))
box(('leg', 'open', 'exit', 'MAE% measured', 'MAE ts', 'MFE% measured', 'MFE ts',
     'MFE at +min'), rows)
print('\n# LEG 11 — ws2Mage AND ws12r EVERY 30 s. THE ARM NEEDS ws2Mage UNDER 15')
a, b = K('10:56:40'), K('11:07:45')
p0 = float(PX[a])
box(('ts', '+min', 'ws2Mage', 'under 15?', 'ws12r', 'pxs', 'pct SHORT'),
    [(SC.U(k), '%+.1f' % ((int(SC.ts[k]) - int(SC.ts[a])) / 60000.0),
      '%.2f' % float(M2[k]), 'Y' if float(M2[k]) <= SC.LO else '-',
      '%.2f' % float(R12[k]), '%.6f' % float(PX[k]),
      '%+.4f' % ((float(PX[k]) - p0) / p0 * 100.0 * -1)) for k in range(a, b + 1, 6)])
print('- ws2Mage min over the leg: %.2f at %s; fence is %.0f'
      % (float(np.nanmin(M2[a:b + 1])), SC.U(a + int(np.nanargmin(M2[a:b + 1]))), SC.LO))
print('- ws2Mage bars at or under %.0f: %d of %d' % (SC.LO,
      sum(1 for k in range(a, b + 1) if float(M2[k]) <= SC.LO), b - a + 1))
