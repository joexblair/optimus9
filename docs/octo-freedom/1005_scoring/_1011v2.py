"""1011-v2 — the ws1-cp / W_LOOP / lineage events from a given bar to a given bar.

Joe 1011: *"confirm that lineage is behaving as expected when a leg has not advanced past the first
w_loop (ie the trade has not walked to ws{w_loop_tf}r oob) - at 07-17 13:25:15, walk forward. create
the row-timestamped ws1cp, the w_loop definition, and lineage events until 20:00"*.

THE SIDE is taken from the FIRST ws1-cp after the open - the cp that arms the walk is the mech's own
first event and the only in-mech anchor available before the walk exists. Joe named no side.
MY READING, stated. `V_SIDE` overrides it.

THE WINDOW runs to `V_END` across as many legs as it takes. Every leg's open is a row.

THE ws1-cp IS MODE 1 ONLY - ws1Mage AND ws1r both oob, same side. Mode 2, ws1Mage oob + an ws1r
divergence, is NOT BUILT: `jig.divergence` requires the RAW close and the tape cache holds only
px_smooth. Raised with Joe 1011, unruled.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, U, PX = C.SC, C.SC.U, C.PX
N = len(SC.ts); HI, LO = SC.HI, SC.LO
R, MG1 = C.R, C.MG1
D = os.environ.get('V_DAY', '2026-07-17')
k0 = SC.K('%s %s' % (D, os.environ.get('V_OPEN', '13:25:15')))
kE = SC.K('%s %s' % (D, os.environ.get('V_END', '20:00:00')))
cp = lambda j, s: (((float(R[1][j]) >= HI) and (float(MG1[j]) >= HI)) if s > 0
                   else ((float(R[1][j]) <= LO) and (float(MG1[j]) <= LO)))

# THE SIDE IS READ ONCE, AT THE TRADE'S OPEN. Joe 1012: *"it can only be set once at the open of
# the trade"*. `SC.DRv` at the open bar is the TRADE's side: +1 a SHORT, -1 a LONG. The board the
# walk hunts is the end the trade is heading to, so a SHORT hunts LOW and a LONG hunts HIGH.
# V_SIDE FORCES THE TRADE'S SIDE. Joe 1012 asked for a SHORT opened at the 07-17 14:10:45 g15r
# lineage finisher, where global dr reads the other way. The side is still set ONCE, at the open -
# this only changes WHERE that one read comes from, and the row says which.
_vs = os.environ.get('V_SIDE', '')
if _vs:
    d0 = int(_vs); src = 'V_SIDE, forced'
else:
    d0 = int(SC.DRv[k0]); src = "global dr at the trade's open"
assert d0 != 0, 'global dr is 0 at the open bar - it has not resolved a side yet'
print('# 1011-v2  %s  %s -> %s   dr %+d at the open (from %s) = a %s, hunting the %s board'
      % (D, U(k0), U(kE), d0, src, 'SHORT' if d0 > 0 else 'LONG',
         'LOW' if d0 > 0 else 'HIGH'))
print('# MECH  W_ARM %s  W_CP %s  W_KICK %s  loop %s  W_LOOP_END %s  W_LOOP_EXH %s  W_GC %s  '
      'W_NOX %s  W_STALL_UP %s  ceiling ws%d  lin_hop %d'
      % (C.ARM, C.CP, C.KICK, C.LOOP_TFS or 'off', C.LOOP_END, C.EXH_LOOP, C.GC, C.NOX,
         C.STALL_UP, C.CEIL_HI, C.LIN_HOP), flush=True)

rows = []
k, d, leg = k0, d0, 0
while k < kE:
    leg += 1
    rows.append((k, 'OPEN — dr %+d, a %s, so the walk hunts the %s board  '
                    '(leg %d of this window)'
                 % (d, 'SHORT' if d > 0 else 'LONG', 'LOW' if d > 0 else 'HIGH', leg)))
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    for j, t in tr:
        if j <= kE: rows.append((j, t))
    if xk is None or xk > kE:
        rows.append((kE, 'WINDOW ENDS — this leg is still open. its exit is %s'
                     % ('past the tape end' if xk is None else '%s, %s' % (U(xk), why))))
        break
    rows.append((xk, 'EXIT — %s' % why))
    k = xk; d = -d

W = int(os.environ.get('V_W', 200))
rows.sort(key=lambda r: r[0])
print()
print('┌' + '─' * 10 + '┬' + '─' * (W + 2) + '┐')
print('│ ' + 'ts'.center(8) + ' │ ' + 'event'.center(W) + ' │')
print('├' + '─' * 10 + '┼' + '─' * (W + 2) + '┤')
for j, t in rows:
    print('│ ' + U(j).ljust(8) + ' │ ' + t[:W].ljust(W) + ' │')
print('└' + '─' * 10 + '┴' + '─' * (W + 2) + '┘')
print('- %d rows, %d leg open(s) in the window.' % (len(rows), leg))
