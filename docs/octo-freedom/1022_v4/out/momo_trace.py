"""Every bar of every cad walk on one day, and the bar the rev-trade fires. HIS 1106 ASK.

> to make it real, you need to walk forward on the cad-walk after 0755 and pick when rev-trade
> will fire

IT GOES THROUGH v4_fdm2.legs, THE DRIVER THAT OWNS THE LEG STATE - the same call fdm2_chain.py
makes, with the same re-entry signal source and the same FDM_MAE_CAP stop. The per-bar rows come
out of v4_fdm2.XCAD_TRACE, which the cad walk fills from the SAME momo_vote and truncation-test
calls its verdict came from, so the trace and the decision cannot disagree.

  W_TRACE_DAY   the day, default 2026-08-23
  W_TRACE_B0    print only the cad walk that starts at this bar, 'YYYY-MM-DD HH:MM:SS'
  W_TRACE_ALL   'on' prints every bar of every cad walk, not just the deciding ones
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.environ.setdefault('W_V4_EXPERIMENT', '1')
os.environ.setdefault('W_V4_FDM2_MOMO_ON', '1')
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

DAY = os.environ.get('W_TRACE_DAY', '2026-08-23')
ONLY = os.environ.get('W_TRACE_B0', '')
ALLB = os.environ.get('W_TRACE_ALL', '') == 'on'

LN = F2.load()
A, B = ln.K(DAY + ' 00:00:00'), ln.K(DAY + ' 23:59:55')
SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'], CPM=LN['CPM'])
HIT = [x for x in SIGS if int(x['bar']) >= A]
assert HIT, 'no fdm re-entry signal at or after %s' % ln.U(A)
g = HIT[0]
D = SG.direction(int(g['side']))
OPN, TS = SG.fire_bar(g), SG.target_side(D)

F2.XCAD_TRACE = []
LG = F2.legs(LN, (OPN, TS, 'fdm re-entry %s' % ln.U(int(g['bar']))), B, resig=SIGS)
TR = F2.XCAD_TRACE


def row(*c):
    print('| ' + ' | '.join(str(x) for x in c) + ' |')


def head(*c):
    row(*c)
    row(*(['---'] * len(c)))


print('| the run | value |')
print('|---|---|')
row('the day', DAY)
row('the tape', '%d bars, %s .. %s' % (len(LN['close']), ln.U(0), ln.U(len(LN['close']) - 1)))
row('the first re-entry', '%s, %s, target side %s' % (ln.U(int(g['bar'])), D,
                                                      'HIGH' if TS > 0 else 'LOW'))
row('the legs', len(LG))
row('fdm2-momo', 'ON. maxTF %d, r-pred floor %d, Mage-beyond-x median %d, pinned median %d, '
                 'votes %d of 3, read %s'
    % (int(K.FDM2_MOMO_MAX_TF), int(K.FDM2_MOMO_FLOOR_RPRED), int(K.FDM2_MOMO_MED_MX),
       int(K.FDM2_MOMO_MED_PIN), int(K.FDM2_MOMO_VOTES), K.FDM2_MOMO_READ))
row('the cad walk length', 'FDM_XCAD_WALK_MIN %.1f min = %d bars'
    % (float(K.FDM_XCAD_WALK_MIN), int(round(float(K.FDM_XCAD_WALK_MIN) * 60.0 / 5.0))))
row('the stop', 'FDM_MAE_CAP %.2f%% adverse from the open' % float(K.FDM_MAE_CAP))
row('the trace rows', len(TR))
row('the cad walks traced', len({t['b0'] for t in TR}))

#   group the rows by the cad walk that produced them
WALKS = {}
for t in TR:
    WALKS.setdefault(t['b0'], []).append(t)

print()
print('# every cad walk on the day, and what ended it')
print()
head('the cad walk starts', 'target side', 'bars read', 'bars `walk` vetoed',
     'bars the truncation test ran', 'the first bar that passed', 'the rev-trade bar',
     'seconds from the start', 'what ended it')
for b0 in sorted(WALKS):
    rs = WALKS[b0]
    sd = rs[0]['side']
    vet = [r for r in rs if r['vetoed']]
    tst = [r for r in rs if r['tested']]
    pas = [r for r in rs if r['ok']]
    row(ln.U(b0), 'LOW' if sd < 0 else 'HIGH', len(rs), len(vet), len(tst),
        ln.U(pas[0]['bar']) if pas else 'none',
        ln.U(pas[0]['bar']) if pas else 'no rev-trade from this cad walk',
        pas[0]['since_s'] if pas else '-',
        'the truncation test passed' if pas else
        ('fdm2-momo voted `walk` on every bar' if len(vet) == len(rs) else
         'the test never passed in the cad walk\'s length'))

#   the per-bar walk forward
for b0 in sorted(WALKS):
    if ONLY and ln.U(b0) != ONLY:
        continue
    rs = WALKS[b0]
    pas = [r for r in rs if r['ok']]
    print()
    print('## the cad walk from %s, target side %s - %s'
          % (ln.U(b0), 'LOW' if rs[0]['side'] < 0 else 'HIGH',
             ('the rev-trade fires at %s, %d s in' % (ln.U(pas[0]['bar']), pas[0]['since_s']))
             if pas else 'no rev-trade'))
    print()
    print('| the bar | s from the start | the vote | r-pred of %d | Mage-beyond-x of %d | '
          'pinned of %d | fdm2-momo | the truncation test | what it says |'
          % (int(K.FDM2_MOMO_MAX_TF) - int(K.FDM_STEP1_ABOVE_TF),
             int(K.FDM2_MOMO_MAX_TF) - int(K.FDM_STEP1_ABOVE_TF),
             int(LN['HI']) - int(K.FDM_STEP1_ABOVE_TF)))
    print('|---|---|---|---|---|---|---|---|---|')
    #   EVERY BAR UP TO AND INCLUDING THE DECIDING ONE. Without W_TRACE_ALL the rows after the
    #   rev-trade are not printed because the cad walk returned at that bar and read no further -
    #   there are no later rows to hide.
    for r in rs:
        print('| %s | %d | %s | %s | %s | %s | %s | %s | %s |'
              % (ln.U(r['bar']), r['since_s'],
                 '%d of 3' % r['votes'] if r['votes'] is not None else '-',
                 r['rpred'] if r['rpred'] is not None else '-',
                 r['mx'] if r['mx'] is not None else '-',
                 r['pin'] if r['pin'] is not None else '-',
                 '`walk` - VETO' if r['vetoed'] else 'no `walk` verdict',
                 ('did not run' if not r['tested'] else
                  ('PASSED - REV-TRADE' if r['ok'] else 'failed')),
                 r['why'].replace('|', '\\|')))

print()
print('# the legs the day produced')
print()
head('the leg opens', 'dir', 'target side', 'what opened it', 'the exit', 'the exit kind',
     'held, min', 'MAE %', 'MFE %', 'realised %')
for L in LG:
    row(ln.U(int(L['opn'])), 'LONG' if int(L['side']) > 0 else 'SHORT',
        'HIGH' if int(L['side']) > 0 else 'LOW', str(L['src']), ln.U(int(L['exit'])),
        str(L['ctype']), '%.1f' % float(L['held_min']),
        '%.3f' % abs(float(L['mae'])), '%+.3f' % float(L['mfe']), '%+.3f' % float(L['rel']))
mae = [abs(float(L['mae'])) for L in LG]
mfe = [float(L['mfe']) for L in LG]
rel = [float(L['rel']) for L in LG]
print()
print('| the aggregate, all numbers carry the FDM_MAE_CAP %.2f%% stop | value |'
      % float(K.FDM_MAE_CAP))
print('|---|---|')
row('legs', len(LG))
row('MAE %, median', '%.3f' % float(np.median(mae)))
row('MFE %, median', '%+.3f' % float(np.median(mfe)))
row('realised %, median', '%+.3f' % float(np.median(rel)))
row('realised %, total', '%+.3f' % sum(rel))
row('MFE over MAE, median', '%.2f' % float(np.median([f / m if m > 0 else np.nan
                                                      for f, m in zip(mfe, mae)])))
row('legs that stopped', sum(1 for L in LG if 'STOP' in str(L['ctype'])))


#   ── HIS 1106 ASK: the incoming trade's debugging table, without the ws1b miss rows ────────────
#   *"show me their incoming trade (+ cad-walk) debugging table (without the ws1b "misses" rows)"*.
#   The INCOMING trade is the one being CLOSED by the rev-trade - his banked definition. The rows
#   here are the leg's OWN decision rows out of v4_fdm2.legs, which never contained a ws1b miss:
#   those came from a separate cadence_events(trace=True) pass and are not read at all.
WANT = [x.strip() for x in os.environ.get('W_TRACE_LEGS', '').split(',') if x.strip()]
for L in LG:
    if ln.U(int(L['opn'])) not in WANT:
        continue
    o, ex, sd = int(L['opn']), int(L['exit']), int(L['side'])
    op = float(LN['close'][o])
    print()
    print('## the incoming trade %s | %s | target side %s'
          % (ln.U(o), 'LONG' if sd > 0 else 'SHORT', 'HIGH' if sd > 0 else 'LOW'))
    print()
    print('| the leg | value |')
    print('|---|---|')
    row('what opened it', str(L['src']))
    row('the open price', '%.6f' % op)
    row('the exit', ln.U(ex))
    row('the exit kind', str(L['ctype']))
    row('the exit price', '%.6f' % float(LN['close'][ex]))
    row('held, min', '%.1f' % float(L['held_min']))
    row('MAE %', '%.3f' % abs(float(L['mae'])))
    row('MFE %', '%+.3f' % float(L['mfe']))
    row('realised %', '%+.3f' % float(L['rel']))
    row('the rev-trade signal', ln.U(int(L['sig'])) if L['sig'] is not None else 'none')
    row('the OUTGOING trade it opens', 'at the signal + 2 bars, the opposite direction - %s'
        % ('SHORT' if sd > 0 else 'LONG') if L['sig'] is not None else 'none')
    print()
    EV = []
    for g in SIGS:
        if str(L['src']).startswith('fdm re-entry') and ln.U(int(g['bar'])) in str(L['src']):
            EV.append((int(g['bar']), 'RE-ENTRY SIGNAL',
                       'gcws30b window side %s. %s'
                       % ('HIGH' if int(g['side']) > 0 else 'LOW', str(g.get('why', '')))))
    EV.append((o, 'OPEN', '%s at %.6f, %s' % ('LONG' if sd > 0 else 'SHORT', op, L['src'])))
    for r in L['rows']:
        EV.append((int(r['bar']), str(r['stage']), str(r['why'])))
    adv = (np.asarray(LN['plo'], float) if sd > 0 else np.asarray(LN['phi'], float))[o:ex + 1]
    fav = (np.asarray(LN['phi'], float) if sd > 0 else np.asarray(LN['plo'], float))[o:ex + 1]
    ap = sd * (adv - op) / op * 100.0
    fp = sd * (fav - op) / op * 100.0
    ab, fb = o + int(np.nanargmin(ap)), o + int(np.nanargmax(fp))
    EV.append((ab, 'MAE BAR', 'the adverse extreme %.3f%% at %.6f'
               % (float(np.nanmin(ap)), float(adv[ab - o]))))
    EV.append((fb, 'MFE BAR', 'the favourable extreme %+.3f%% at %.6f'
               % (float(np.nanmax(fp)), float(fav[fb - o]))))
    sbar = F2.stop_bar(LN, o, ex, sd, float(K.FDM_MAE_CAP))
    if sbar is not None:
        EV.append((int(sbar), 'STOP BAR', 'the adverse excursion reached FDM_MAE_CAP %.2f%% here'
                   % float(K.FDM_MAE_CAP)))
    if L['sig'] is not None:
        EV.append((int(L['sig']), 'REV-TRADE SIGNAL', 'the router closes at signal + 1'))
    EV.append((ex, 'EXIT', '%s at %.6f, realised %+.3f%%'
               % (str(L['ctype']), float(LN['close'][ex]), float(L['rel']))))
    assert all(b <= ex for b, _, _ in EV), 'a leg event reads past the leg\'s own exit'
    print('| the bar | min from the open | the event | what it says |')
    print('|---|---|---|---|')
    for b, stage, why in sorted(EV, key=lambda z: (z[0], z[1])):
        print('| %s | %.1f | %s | %s |'
              % (ln.U(int(b)), (int(b) - o) * 5 / 60.0, stage, why.replace('|', '\\|')))
