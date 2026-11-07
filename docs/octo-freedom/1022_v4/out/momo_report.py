"""The fdm2-momo A/B's reports, read from the dump. NO CHAIN RUN, so every answer is seconds.

HIS 1106 ASKS:
  1  *"find the 2 day range that covers the most stops caused by fdm2-momo trades"*
  2  *"for each exit type, build a table to show me how many have positive trades, and how many
     have negative trades"*
  3  *"show me the 2 day chain as well"* - the full leg report for the window question 1 names
  and, standing: *"I'll be asking for the leg reports so all of the timestamped events need to be
  prepared"*

THE DUMP is `ab_legs.json`, written by momo_ab.py: both arms' every leg, with its open, exit,
signal, exit kind, source, realised, MAE, MFE, held minutes, the stop flag, AND its decision rows -
each row's bar, timestamp, stage and why, with the cadence event bar, step 1's count, the x
timeframe, and fdm2-momo's votes and three counts where they apply.

    W_REPORT_DAYS   'YYYY-MM-DD .. YYYY-MM-DD' to print a chain for a range of your choosing
                    instead of the window question 1 finds.
"""
import json
import os
import sys
from collections import Counter

import numpy as np

DUMP = '/home/joe/.claude/jobs/7c82535c/tmp/ab_legs.json'
D = json.load(open(DUMP))
ARMS = [('A, the banked machine', [k for k in D if k.startswith('A')][0]),
        ('B, fdm2-momo on', [k for k in D if k.startswith('B')][0])]
LA, LB = D[ARMS[0][1]], D[ARMS[1][1]]
DRAG = 0.1975

print('| the dump | value |')
print('|---|---|')
print('| legs, arm A | %d |' % len(LA))
print('| legs, arm B | %d |' % len(LB))
print('| timestamped events, arm A | %d |' % sum(len(x['rows']) for x in LA))
print('| timestamped events, arm B | %d |' % sum(len(x['rows']) for x in LB))
print()

#   ── 1. the 2-day window with the most stops caused by fdm2-momo ────────────────────────────────
opensA = {x['opn'] for x in LA}
bonly = [x for x in LB if x['opn'] not in opensA]
bonly_stop = [x for x in bonly if x['stopped']]
allB_stop = [x for x in LB if x['stopped']]
print('| the stop counts | value |')
print('|---|---|')
print('| legs only in arm B - the ones fdm2-momo created | %d |' % len(bonly))
print('| of those, stopped | %d |' % len(bonly_stop))
print('| every arm B stop | %d |' % len(allB_stop))
print()

days = sorted({x['opn_ts'][:10] for x in LA + LB})
print('## 1 - every 2-day window, by stops caused by fdm2-momo. Chronological, not ranked')
print()
print('| the window | arm-B-only stops | every arm B stop | every arm A stop | arm-B-only legs |')
print('|---|---|---|---|---|')
WIN = []
for i in range(len(days) - 1):
    w = (days[i], days[i + 1])
    f = lambda xs: sum(1 for x in xs if x['opn_ts'][:10] in w)
    n_bo = f(bonly_stop)
    WIN.append((n_bo, w, f(allB_stop), f([x for x in LA if x['stopped']]), f(bonly)))
    print('| %s .. %s | %d | %d | %d | %d |'
          % (w[0], w[1], n_bo, WIN[-1][2], WIN[-1][3], WIN[-1][4]))
WIN.sort(key=lambda z: (-z[0], z[1]))
TOP = WIN[0]
print()
print('| the window with the most | value |')
print('|---|---|')
print('| the range | %s .. %s |' % (TOP[1][0], TOP[1][1]))
print('| stops caused by fdm2-momo | %d |' % TOP[0])
print('| every arm B stop in it | %d |' % TOP[2])
print('| every arm A stop in it | %d |' % TOP[3])
print('| legs only in arm B in it | %d |' % TOP[4])
print()

#   ── 2. positive against negative, per exit kind ────────────────────────────────────────────────
def kind(x):
    c = x['ctype']
    return 'STOP at 1.10%' if c.startswith('STOP') else c


print('## 2 - every exit type, positive against negative')
print()
print('| which arm | the exit kind | trades | positive | negative | zero | realised total | realised median | MAE median | MFE median |')
print('|---|---|---|---|---|---|---|---|---|---|')
for lab, key in ARMS:
    L = D[key]
    for k in sorted({kind(x) for x in L}):
        m = [x for x in L if kind(x) == k]
        r = np.array([x['rel'] for x in m], float)
        print('| %s | %s | %d | %d | %d | %d | %+.3f | %+.3f | %.3f | %+.3f |'
              % (lab, k, len(m), int((r > 0).sum()), int((r < 0).sum()), int((r == 0).sum()),
                 float(r.sum()), float(np.median(r)),
                 float(np.median([x['mae'] for x in m])),
                 float(np.median([x['mfe'] for x in m]))))
print()
print('| which arm | the exit kind | its share of the arm\'s legs | its share of the arm\'s realised |')
print('|---|---|---|---|')
for lab, key in ARMS:
    L = D[key]
    tot = sum(x['rel'] for x in L)
    for k in sorted({kind(x) for x in L}):
        m = [x for x in L if kind(x) == k]
        print('| %s | %s | %.1f%% | %s |'
              % (lab, k, 100.0 * len(m) / len(L),
                 ('%+.1f%%' % (100.0 * sum(x['rel'] for x in m) / tot)) if tot else '-'))
print()

#   ── 3. the chain for the window, both arms, every timestamped event ────────────────────────────
RNG = os.environ.get('W_REPORT_DAYS')
if RNG:
    w = tuple(s.strip() for s in RNG.split('..'))
else:
    w = TOP[1]
print('## 3 - the chain for %s .. %s, both arms' % (w[0], w[1]))
print()
for lab, key in ARMS:
    L = [x for x in D[key] if x['opn_ts'][:10] in w]
    print('### %s - the legs' % lab)
    print()
    print('| the open | the trade | the reason | the rev-trade signal | the exit | the exit kind | held min | MAE% | MFE% | realised% |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for x in L:
        #   THE LABELS ARE fdm2_chain._why_rev's, BRANCH FOR BRANCH. My first version invented
        #   its own shorter set and printed `unlabelled` on 11 of 34 legs in one window, which is
        #   the "one driver, not fragments" fault - so these are copied from the chain's source.
        if x['stopped']:
            reason = 'mae1.10 stop'
        elif x['sig'] is None:
            reason = 'no rev-trade before the day ends'
        else:
            rr = [r for r in x['rows'] if r['stage'] == 'REV-TRADE']
            if not rr:
                reason = 'unlabelled'
            else:
                r = rr[-1]
                why = str(r['why'])
                xtf = r.get('xtf')
                xl = ('ws%dx' % int(xtf)) if xtf else 'ws{TF}x'
                if 'found no candidate' in why:
                    reason = 'no linhop candidates'
                elif why.startswith('the director - '):
                    reason = ('%s cad walk' % xl) if 'min walk from' in why else ('%s cadence' % xl)
                elif 'grace walk,' in why:
                    reason = '%s cad grace walk' % xl
                elif 'reversed since' in why:
                    reason = '%s cadence, reversal count' % xl
                elif 'AND towards' in why and 'if the answer is no' in why:
                    reason = 'step 1, 0 of %s' % (r.get('n') or '?')
                elif 'SAVIOUR' in str(r['stage']):
                    reason = 'v4saviour'
                else:
                    reason = why[:48]
        print('| %s | %s | %s | %s | %s | %s | %.1f | %.3f | %+.3f | %+.3f |'
              % (x['opn_ts'], 'LONG' if x['side'] > 0 else 'SHORT', reason,
                 x['sig_ts'] or '-', x['exit_ts'], x['ctype'].replace('|', '\\|'),
                 x['held'], x['mae'], x['mfe'], x['rel']))
    r = np.array([x['rel'] for x in L], float)
    print()
    print('| %s, the window\'s totals | value |' % lab)
    print('|---|---|')
    print('| legs | %d |' % len(L))
    print('| stopped | %d |' % sum(1 for x in L if x['stopped']))
    print('| gross %% | %+.3f |' % r.sum())
    print('| drag %% | %-.3f |' % (-DRAG * len(L)))
    print('| net %% | %+.3f |' % (r.sum() - DRAG * len(L)))
    print('| MAE %% total | %.3f |' % sum(x['mae'] for x in L))
    print('| MFE %% total | %+.3f |' % sum(x['mfe'] for x in L))
    print('| the stop | FDM_MAE_CAP 1.10%, ON |')
    print()
    print('### %s - every timestamped event, chronological' % lab)
    print()
    print('| the bar | the leg it belongs to | the stage | why |')
    print('|---|---|---|---|')
    for x in L:
        for r2 in x['rows']:
            print('| %s | %s | %s | %s |'
                  % (r2['ts'], x['opn_ts'], r2['stage'], str(r2['why']).replace('|', '\\|')))
    print()
