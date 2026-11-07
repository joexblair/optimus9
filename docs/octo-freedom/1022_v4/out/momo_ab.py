"""The fdm2-momo A/B. HIS GO, 1106: *"yes to the AB"*.

ARM A   FDM2_MOMO_ON 0 - the banked machine, untouched
ARM B   FDM2_MOMO_ON 1 - fdm2-momo reads at EVERY bar of the cad walk and, at FDM2_MOMO_VOTES 3
        on FDM2_MOMO_READ emerging, prints his `walk` verdict, which vetoes the truncation test at
        that bar only. The bar the verdict stops being `walk` is decided by the cad walk's own
        test and can print the rev-trade. HIS 1106 RCA.

THE ARM B SHAPE CHANGED AFTER THIS A/B RAN. The banked numbers in 1105_momo_dish.md came from the
one-shot latch - one read at the cad walk's first bar, silencing the whole cad walk - which he
replaced on 1106. Those numbers belong to that shape and not to this one, so the A/B needs
re-running before any of them is quoted again.

ONE PROCESS, ONE TAPE LOAD, BOTH ARMS, one continuous chain each over the whole 94.5 days. The arm
is switched by setting the knob on the module between runs, so both arms read the same arrays and
nothing else differs.

WHY THE KNOB IS SET AT RUNTIME: v4_knobs.check() refuses an off-ruled run, and the BANKED value of
FDM2_MOMO_ON is 0. Setting it here bypasses that check for arm B on purpose - the arm is the
experiment, and the bank does not move until he banks it.
"""
import io
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_signal as SG
    import v4_fdm_reentry as RE
    import ln
finally:
    sys.stderr = _e

LN = F2.load()
B = len(LN['close']) - 1
SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'], CPM=LN['CPM'])
g = SIGS[0]
OPEN_AT = (SG.fire_bar(g), SG.target_side(SG.direction(int(g['side']))), 'fdm re-entry')

print('| the A/B | value |')
print('|---|---|')
print('| the tape | %d bars, %.1f days, %s to %s |'
      % (B + 1, (B + 1) * 5 / 86400.0, ln.U(0), ln.U(B)))
print('| arm A | FDM2_MOMO_ON 0 - the banked machine |')
print('| arm B | FDM2_MOMO_ON 1, FDM2_MOMO_VOTES %d, FDM2_MOMO_READ %s |'
      % (int(K.FDM2_MOMO_VOTES), K.FDM2_MOMO_READ))
print('| the medians it votes against | r-pred %d, Mage-beyond-x %d, pinned %d |'
      % (int(K.FDM2_MOMO_FLOOR_RPRED), int(K.FDM2_MOMO_MED_MX), int(K.FDM2_MOMO_MED_PIN)))
print('| the stop | FDM_MAE_CAP %.2f%%, ON in both arms |' % float(K.FDM_MAE_CAP))
print()

RES = {}
for arm, on in (('A, the banked machine', 0), ('B, fdm2-momo on', 1)):
    K.FDM2_MOMO_ON = on
    t0 = time.time()
    lg = F2.legs(LN, OPEN_AT, B, resig=SIGS)
    RES[arm] = (lg, F2.score(lg), time.time() - t0)
    sys.stderr.write('%s: %d legs, %.0f s\n' % (arm, len(lg), time.time() - t0))
    sys.stderr.flush()
K.FDM2_MOMO_ON = 0

#   BOTH ARMS' FULL LEG LISTS, DUMPED. The two chains cost ~32 minutes; every later question off
#   this A/B reads the dump instead of paying that again.
import json
DUMP = '/home/joe/.claude/jobs/7c82535c/tmp/ab_legs.json'
#   EVERY TIMESTAMPED EVENT, not just the leg's ends. HIS 1106: *"I'll be asking for the leg
#   reports so all of the timestamped events need to be prepared"*. Each leg carries its own
#   decision rows - the cadence events, the SEAM reads, fdm2-momo's MOMO VOTE rows, the saviour rows
#   and the REV-TRADE - with the bar, its timestamp, the stage and the why. Chronological, because
#   `legs` sorts them by bar before it returns them.
def _rows(x):
    out = []
    for r in x['rows']:
        d = dict(bar=int(r['bar']), ts=ln.U(int(r['bar'])), stage=str(r['stage']),
                 why=str(r.get('why', '')))
        for k2 in ('ev', 'k', 'n', 'xtf', 'votes', 'rpred', 'mx', 'pin', 'which', 'cross'):
            if r.get(k2) is not None:
                d[k2] = (ln.U(int(r[k2])) if k2 in ('ev', 'cross') else r[k2])
        out.append(d)
    return out


json.dump({arm: [dict(opn=int(x['opn']), side=int(x['side']), exit=int(x['exit']),
                      ctype=str(x['ctype']), src=str(x['src']), rel=float(x['rel']),
                      mae=float(x['mae']), mfe=float(x['mfe']), held=float(x['held_min']),
                      stopped=bool(x['stopped']), opn_ts=ln.U(int(x['opn'])),
                      exit_ts=ln.U(int(x['exit'])), sig=(int(x['sig']) if x['sig'] is not None
                                                         else None),
                      sig_ts=(ln.U(int(x['sig'])) if x['sig'] is not None else None),
                      rows=_rows(x))
                 for x in RES[arm][0]] for arm in RES}, open(DUMP, 'w'))
sys.stderr.write('dumped both arms to %s - %d + %d legs, %d + %d rows\n'
                 % (DUMP, len(RES['A, the banked machine'][0]),
                    len(RES['B, fdm2-momo on'][0]),
                    sum(len(x['rows']) for x in RES['A, the banked machine'][0]),
                    sum(len(x['rows']) for x in RES['B, fdm2-momo on'][0])))

print('| the total | arm A, the banked machine | arm B, fdm2-momo on | the move |')
print('|---|---|---|---|')
a, b = RES['A, the banked machine'][1], RES['B, fdm2-momo on'][1]
for key, lab, fmt in (('n', 'legs', '%d'), ('stops', 'stopped', '%d'),
                      ('gross', 'gross %', '%+.3f'), ('drag', 'drag %', '%-.3f'),
                      ('net', 'net %', '%+.3f'), ('mae', 'MAE % total', '%.3f'),
                      ('mfe', 'MFE % total', '%+.3f')):
    av, bv = a[key], b[key]
    if key == 'drag':
        av, bv = -av, -bv
    print(('| %s | ' + fmt + ' | ' + fmt + ' | ' + (('%+d' if fmt == '%d' else '%+.3f')) + ' |')
          % (lab, av, bv, bv - av))
print('| MFE captured | %.1f%% | %.1f%% | %+.1f |'
      % (100.0 * a['gross'] / a['mfe'] if a['mfe'] else float('nan'),
         100.0 * b['gross'] / b['mfe'] if b['mfe'] else float('nan'),
         (100.0 * b['gross'] / b['mfe'] - 100.0 * a['gross'] / a['mfe'])
         if a['mfe'] and b['mfe'] else float('nan')))
print('| run time, s | %.0f | %.0f | - |'
      % (RES['A, the banked machine'][2], RES['B, fdm2-momo on'][2]))
print()

#   where the two arms part company: the first leg whose open or exit differs
LA, LB = RES['A, the banked machine'][0], RES['B, fdm2-momo on'][0]
print('## how many of fdm2-momo\'s latches actually changed a leg')
print()
opensA = {int(x['opn']) for x in LA}
opensB = {int(x['opn']) for x in LB}
print('| the count | value |')
print('|---|---|')
print('| legs in arm A | %d |' % len(LA))
print('| legs in arm B | %d |' % len(LB))
print('| leg opens only in arm A | %d |' % len(opensA - opensB))
print('| leg opens only in arm B | %d |' % len(opensB - opensA))
print('| leg opens in both | %d |' % len(opensA & opensB))
print()

print('## the legs that differ, chronological')
print()
print('| arm | the open | the trade | the exit | the exit kind | held min | MAE% | MFE% | realised% |')
print('|---|---|---|---|---|---|---|---|---|')
byA = {int(x['opn']): x for x in LA}
byB = {int(x['opn']): x for x in LB}
for o in sorted(set(byA) | set(byB)):
    xa, xb = byA.get(o), byB.get(o)
    same = (xa is not None and xb is not None and int(xa['exit']) == int(xb['exit'])
            and abs(xa['rel'] - xb['rel']) < 1e-9)
    if same:
        continue
    for arm, x in (('A', xa), ('B', xb)):
        if x is None:
            print('| %s | %s | - | - | the leg does not exist in this arm | - | - | - | - |'
                  % (arm, ln.U(o)))
            continue
        print('| %s | %s | %s | %s | %s | %.1f | %.3f | %+.3f | %+.3f |'
              % (arm, ln.U(int(x['opn'])), 'LONG' if x['side'] > 0 else 'SHORT',
                 ln.U(int(x['exit'])), str(x['ctype']).replace('|', '\\|'),
                 x['held_min'], x['mae'], x['mfe'], x['rel']))
