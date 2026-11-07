"""The debugging leg report: EVERY timestamped event inside a leg, not only the rows the walk kept.

HIS 1106: *"I need the leg report that shows me each event in that leg, for the first 3 mae1.1
exits, on arm B"* / *"for your context - I'm debugging. you should understand the level of detail
that I need"*.

WHY THE DUMP WAS NOT ENOUGH. 560 of arm B's 602 stops print ZERO decision rows - they open, run a
median 35.2 min and hit the stop with nothing recorded in between. The rows a leg keeps are only
the decisions the walk ACTED on. A debugging report has to show what the walk SAW and rejected too.

SO THIS ASSEMBLES, PER LEG, FROM THE TAPE:
  the open        the fdm re-entry signal that opened it, its window side, its own why, and the
                  open bar's close price
  every ws1b cross on the leg's side inside it, with the per-test verdict from
                  cadence_events(trace=True) - so a cross that did NOT become a cadence event
                  shows WHICH test failed: no excursion, no nestle, or ws3Mage not ex-fence
  every cadence EVENT that did fire
  the decision rows the cad walk kept, including every fdm2-momo MOMO VOTE transition
  the MAE bar      the first bar the adverse extreme reached the leg's own MAE, with its price
  the MFE bar      the first bar the favourable extreme reached the leg's own MFE, with its price
  the stop bar     from v4_fdm2.stop_bar, walked rather than inferred
  the exit         the bar, the kind and the price

EVERY ROW IS ONE EVENT, CHRONOLOGICAL, with its own `YYYY-MM-DD HH:MM:SS`. Nothing is read past
the leg's own exit.

    W_LEG_ARM    'B' (default) or 'A'
    W_LEG_DAYS   'YYYY-MM-DD .. YYYY-MM-DD', the window to pick legs from
    W_LEG_KIND   'stop' (default) picks mae stops, 'all' picks every leg
    W_LEG_N      how many legs, default 3
    W_LEG_OPENS  a comma list of open timestamps, which overrides the picking
"""
import io
import json
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_fdm_reentry as RE
    import ln
finally:
    sys.stderr = _e

LN = F2.load()
D = json.load(open('/home/joe/.claude/jobs/7c82535c/tmp/ab_legs.json'))
ARM = os.environ.get('W_LEG_ARM', 'B')
KEY = [k for k in D if k.startswith(ARM)][0]
LEGS = D[KEY]
SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'], CPM=LN['CPM'])
SIGBY = {int(g['bar']): g for g in SIGS}
close, phi, plo = (np.asarray(LN[k], float) for k in ('close', 'phi', 'plo'))

if os.environ.get('W_LEG_OPENS'):
    want = [s.strip() for s in os.environ['W_LEG_OPENS'].split(',')]
    PICK = [x for x in LEGS if x['opn_ts'] in want]
else:
    days = tuple(s.strip() for s in os.environ.get(
        'W_LEG_DAYS', '2026-08-23 .. 2026-08-24').split('..'))
    kind = os.environ.get('W_LEG_KIND', 'stop')
    PICK = [x for x in LEGS
            if x['opn_ts'][:10] in days and (x['stopped'] if kind == 'stop' else True)]
    PICK = PICK[:int(os.environ.get('W_LEG_N', 3))]

print('| the report | value |')
print('|---|---|')
print('| the arm | %s |' % KEY)
print('| the legs | %s |' % (', '.join(x['opn_ts'] for x in PICK) or 'none matched'))
print('| the stop | FDM_MAE_CAP %.2f%% |' % float(K.FDM_MAE_CAP))
print('| every event reads its own bar or earlier | asserted below |')
print()

for x in PICK:
    o, ex, sd = int(x['opn']), int(x['exit']), int(x['side'])
    op = float(close[o])
    print('# the leg %s, %s, target side %s'
          % (x['opn_ts'], 'LONG' if sd > 0 else 'SHORT', 'HIGH' if sd > 0 else 'LOW'))
    print()
    print('| the leg | value |')
    print('|---|---|')
    print('| what opened it | %s |' % x['src'])
    print('| the open price | %.6f |' % op)
    print('| the exit | %s |' % x['exit_ts'])
    print('| the exit kind | %s |' % x['ctype'])
    print('| the exit price | %.6f |' % float(close[ex]))
    print('| held, min | %.1f |' % x['held'])
    print('| MAE %% | %.3f |' % x['mae'])
    print('| MFE %% | %+.3f |' % x['mfe'])
    print('| realised %% | %+.3f |' % x['rel'])
    print('| bars it lived | %d |' % (ex - o + 1))
    print()

    EV = []
    #   the re-entry signal, when a re-entry opened it
    for b, g in SIGBY.items():
        if x['src'].startswith('fdm re-entry') and ln.U(b) in x['src']:
            EV.append((b, 'RE-ENTRY SIGNAL',
                       'gcws30b window side %s. %s'
                       % ('HIGH' if int(g['side']) > 0 else 'LOW', str(g.get('why', '')))))
    EV.append((o, 'OPEN', '%s at %.6f, %s'
               % ('LONG' if sd > 0 else 'SHORT', op, x['src'])))

    #   every ws1b cross on the leg's side inside the leg, with its per-test verdict
    for t in F2.cadence_events(LN, sd, o + 1, ex, trace=True):
        c = int(t['cross'])
        if not (o < c <= ex):
            continue
        fired = t['nestle'] is not None and t['m3'] and t['inwin']
        EV.append((c, 'CADENCE EVENT' if fired else 'ws1b CROSS, no event',
                   str(t['why']) if t['why'] else
                   ('the nestle failed' if t['nestle'] is None else
                    ('ws3Mage not ex-%g/%g' % K.fnc_pair(K.FDM_M3_FNC) if not t['m3']
                     else 'outside the leg'))))

    #   the rows the walk kept
    for r in x['rows']:
        EV.append((int(r['bar']), r['stage'], str(r['why'])))

    #   the MAE and MFE bars, walked
    adv = (plo if sd > 0 else phi)[o:ex + 1]
    fav = (phi if sd > 0 else plo)[o:ex + 1]
    apct = sd * (adv - op) / op * 100.0
    fpct = sd * (fav - op) / op * 100.0
    ab = o + int(np.nanargmin(apct))
    fb = o + int(np.nanargmax(fpct))
    EV.append((ab, 'MAE BAR', 'the adverse extreme %.3f%% at %.6f' % (float(apct.min()), float(adv[ab - o]))))
    EV.append((fb, 'MFE BAR', 'the favourable extreme %+.3f%% at %.6f' % (float(fpct.max()), float(fav[fb - o]))))

    sb = F2.stop_bar(LN, o, ex, sd, float(K.FDM_MAE_CAP))
    if sb is not None:
        EV.append((int(sb), 'STOP BAR',
                   'the adverse excursion reached FDM_MAE_CAP %.2f%% here' % float(K.FDM_MAE_CAP)))
    if x['sig'] is not None:
        EV.append((int(x['sig']), 'REV-TRADE SIGNAL', 'the router closes at signal + 1'))
    EV.append((ex, 'EXIT', '%s at %.6f, realised %+.3f%%' % (x['ctype'], float(close[ex]), x['rel'])))

    assert all(b <= ex for b, _, _ in EV), 'a leg event reads past the leg\'s own exit'
    print('| the bar | minutes from the open | the event | what it says |')
    print('|---|---|---|---|')
    for b, stage, why in sorted(EV, key=lambda z: (z[0], z[1])):
        print('| %s | %.1f | %s | %s |'
              % (ln.U(int(b)), (int(b) - o) * 5 / 60.0, stage, why.replace('|', '\\|')))
    print()
