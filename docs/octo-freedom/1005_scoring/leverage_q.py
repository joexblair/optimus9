"""The leverage comparison o9-live recon asked for, on the 10-day confluence set, dr-bias basis.
Joe 1005 via the recon session: "we need to set the leverage correctly."

    LG_TAPE_END=2026-10-05 LG_DAYS=<the ten> python3 leverage_q.py
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, contextlib
import numpy as np
sys.path.insert(0, _HERE)
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    exec(open(_os.path.join(_HERE, 'ninedays.py')).read().split('ALL = {}')[0])
ALL = {}
for day in DAYS: ALL[day] = day_rows(day)
T = sorted([x for d in DAYS for x in ALL[d] if x['status'] == 'CONFLUENCE'], key=lambda x: x['open_ms'])
NET = np.array([x['net_asis'] for x in T])          # dr-bias basis

def curve(nets, Lv):
    eq = 1.0; pk = 1.0; dd = 0.0
    for i, r in enumerate(nets):
        f = 1.0 + Lv * r / 100.0
        if f <= 0: return 0.0, 1.0, i + 1
        eq *= f; pk = max(pk, eq); dd = max(dd, (pk - eq) / pk)
    return eq, dd, None

print('## LEVERAGE — %s, %d confluences, dr-bias basis, $888 start' % (SPAN, len(T)))
print('| the rule | leverage | one worst trade costs | final $ | total return % | max DD % |')
print('|' + '---|' * 6)
ROWS = [('live now: fixed 66,000 coins at 0.18291 on $888', 13.595, 0.8975),
        ('2 % risk, LIVE stop 0.70 + 0.1975 drag = 0.8975 worst', 2.0 / 0.8975, 0.8975),
        ('2 % risk, SCORED stop 0.80 + 0.1975 = 0.9975 worst', 2.0 / 0.9975, 0.9975),
        ('max L holding max DD <= 25 %', 4.8, 0.9975),
        ('max L holding max DD <= 50 %', 10.7, 0.9975)]
for lab, Lv, w in ROWS:
    e, dd, liq = curve(NET, Lv)
    print('| %s | **%.3fx** | %.2f %% of equity | %s | %s | **%.2f** |'
          % (lab, Lv, Lv * w, ('%.2f' % (888 * e)) if liq is None else '**WIPED at trade #%d**' % liq,
             ('%+.2f' % ((e - 1) * 100)) if liq is None else '-100', dd * 100))

run = mx = 0
for r in NET:
    run = run + 1 if r < 0 else 0; mx = max(mx, run)
print()
print('## THE MEASURED LOSING RUN — %d consecutive losers is the worst over %s' % (mx, SPAN))
print('| the rule | leverage | %d straight worst-case stops cost | survives? |' % mx)
print('|' + '---|' * 4)
for lab, Lv, w in ROWS:
    eq = 1.0
    for _ in range(mx): eq *= (1 - Lv * w / 100.0)
    print('| %s | %.3fx | **%.2f %%** of equity | %s |'
          % (lab, Lv, (1 - eq) * 100, 'yes' if eq > 0 else '**NO**'))
print()
print('- L at which ONE worst trade wipes the account: **%.1fx** at the 0.70 stop, **%.1fx** at 0.80'
      % (100 / 0.8975, 100 / 0.9975))
print('- the fixed-coin size is not a risk rule: 66,000 coins is a CONSTANT NOTIONAL, so the fraction')
print('  of equity it risks changes every time equity or price moves. At $888 it is 13.595x; the same')
print('  66,000 coins on the $500 the ledger started from was 24.1x.')
