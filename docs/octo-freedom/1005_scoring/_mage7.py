"""OPEN 7 — ws60Mage vs ws60r AS THE FLAT-LOOKBACK FALLBACK. 1009.

Joe 1008, verbatim, the four cases:
  *"-if ws60Mage is HIGHER than ws60r, and ws12r is HIGH oob, pxs will not reverse because the Mage
    is pulling r UPWARDS, and pxs follows r. the return for this scenario is FALSE, and ws12r will
    delegate to `>ws12r oob`
   -if ws60Mage is LOWER than ws60r, and ws12r is HIGH oob, pxs will reverse ... TRUE, and ws12r
    will print a trade signal on it's stalled or x-cross event
   -if ws60Mage is LOWER than ws60r, and ws12r is LOW oob, pxs will not reverse ... FALSE ...
   -if ws60Mage is HIGHER than ws60r, and ws12r is LOW oob, pxs will reverse ... TRUE ..."*
  *"you must stop and visualise #7 carefully ... Mage pulls/leads r. it's tricky logic and has
  strong potential to be inverted"*

THIS SCRIPT DOES NOT IMPLEMENT ANYTHING. It tests the two things the rule rests on:

  1 THE MODEL: does ws60Mage above ws60r actually precede ws60r RISING? Joe's *"the Mage is pulling
    r UPWARDS"*. Measured as the sign of (ws60r later - ws60r now) against the sign of
    (ws60Mage now - ws60r now), over a spread of horizons, across the whole 95-day tape. If the
    model is right the agreement runs well above 50%.

  2 THE POLARITY. Joe's return is a REVERSAL answer: TRUE = pxs reverses = refuse the delegation.
    `rule2_trajectory.trajectory(line, dr, ...)` returns a CONTINUATION answer: True = the line is
    travelling TOWARDS dr. Wired into one function those two are OPPOSITE in sign, which is the
    inversion Joe warned about. The mapping is printed as a table, not assumed.

  3 the 15:05-15:55 flat run on 08-22, where ws60r held 63.9604 for 50 minutes - the case that
    created OPEN 7 - with ws60Mage beside it bar by bar.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
R12 = C.R[C.TRIG_TF]
HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
print('# tape %d bars; ws60r and ws60Mage both cached at score39\'s window' % N, flush=True)

# ---- 1. THE MODEL: does Mage above r precede r rising
print('\n# 1. DOES ws60Mage ABOVE ws60r PRECEDE ws60r RISING — the whole tape, every 60th bar')
rows = []
idx = np.arange(0, N, 60)
gap = M60[idx] - R60[idx]
ok0 = np.isfinite(gap) & (np.abs(gap) > 0)
for mins in (5, 15, 30, 60, 120, 180):
    off = int(mins * 60 / 5)
    j = idx + off
    m = ok0 & (j < N)
    later = np.where(m, R60[np.minimum(j, N - 1)], np.nan)
    move = later - R60[idx]
    good = m & np.isfinite(move) & (move != 0)
    agree = np.sign(gap[good]) == np.sign(move[good])
    n = int(good.sum())
    # the same, restricted to a WIDE gap, so the model is tested where it should be strongest
    wide = good & (np.abs(gap) >= 10.0)
    agw = np.sign(gap[wide]) == np.sign(move[wide])
    rows.append(('%d min' % mins, str(n), '%.1f%%' % (100.0 * agree.mean()),
                 '%+.4f' % float(np.mean(np.abs(move[good]))),
                 str(int(wide.sum())), '%.1f%%' % (100.0 * agw.mean()) if wide.sum() else '—'))
box(('ws60r measured this far ahead', 'samples', 'sign(Mage-r) agrees with sign(r move)',
     'mean |r move|', 'samples with |Mage-r| >= 10', 'agreement on those'), rows)
print('- 50.0%% is the coin flip. Above it, Joe\'s "the Mage pulls r" holds on this tape.')

# ---- 2. THE POLARITY TABLE
print('\n# 2. THE POLARITY — Joe\'s four cases, and what each one means to each function')
box(('ws60Mage vs ws60r', 'ws12r', 'Joe: does pxs reverse', 'Joe\'s RETURN',
     'what the chain does', 'the implied ws60r direction',
     'trajectory(ws60r, dr=the oob side) would return'),
    [('Mage HIGHER', 'HIGH oob', 'no', 'FALSE', 'delegate to >ws12r oob', 'UP, towards high oob',
      'True — continuation'),
     ('Mage LOWER', 'HIGH oob', 'yes', '**TRUE**', 'ws12r prints a trade signal on stalled/x-cross',
      'DOWN, against high oob', 'False'),
     ('Mage LOWER', 'LOW oob', 'no', 'FALSE', 'delegate to >ws12r oob', 'DOWN, towards low oob',
      'True — continuation'),
     ('Mage HIGHER', 'LOW oob', 'yes', '**TRUE**', 'ws12r prints a trade signal on stalled/x-cross',
      'UP, against low oob', 'False')])
print('- Joe\'s rule in one line: TRUE when the Mage\'s pull OPPOSES the oob side.')
print('- sign test: TRUE iff sign(ws60Mage - ws60r) == -(the oob side).')
print('- **THE INVERSION RISK, NAMED**: Joe\'s TRUE is a REVERSAL answer; `trajectory`\'s True is a')
print('  CONTINUATION answer. They are OPPOSITE. Any function returning both must negate one.')

# ---- 3. the flat run that created OPEN 7
print('\n# 3. THE 08-22 15:05-15:55 FLAT RUN — ws60r held one value for 50 min')
rows = []
for t in ('14:45:00', '14:55:00', '15:00:00', '15:05:00', '15:15:00', '15:21:15', '15:26:15',
          '15:35:00', '15:45:00', '15:55:00', '16:00:00'):
    k = SC.K('2026-08-22 ' + t)
    side = 'high oob' if float(R12[k]) >= HI else ('low oob' if float(R12[k]) <= LO else 'in-fence')
    g = float(M60[k]) - float(R60[k])
    sd = +1 if float(R12[k]) >= HI else (-1 if float(R12[k]) <= LO else 0)
    ret = ('—' if sd == 0 else
           ('TRUE — trade signal' if (1 if g > 0 else -1) == -sd else 'FALSE — delegate'))
    rows.append((t, '%.4f' % float(R60[k]), '%.4f' % float(M60[k]), '%+.4f' % g,
                 'HIGHER' if g > 0 else 'LOWER', '%.4f' % float(R12[k]), side, ret,
                 '%.6f' % float(PX[k])))
box(('ts', 'ws60r', 'ws60Mage', 'Mage - r', 'Mage is', 'ws12r', 'ws12r side',
     'Joe\'s #7 return', 'pxs'), rows)
print('\n- 15:26:15 is the bar Joe confirmed UP by eye. ws12r is in-fence there, not oob, so #7')
print('  returns nothing on it - #7 only fires when ws12r IS oob and the lookback is flat.')
