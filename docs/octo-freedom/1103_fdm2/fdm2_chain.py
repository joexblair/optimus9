"""fdm2's driver - his 1103 pen-test: walk the first leg from the 08-03 re-entry.

HIS ASK, standing from 1102: *"we'll walk from the 08-03 reentry / pre-chain check: walk the first
leg manually to pen-test the mech"*. The default here is ONE leg because that is what he asked
for, not because a leg count is a cap of mine. W_FDM2_LEGS=all walks to the tape end.

THE MECH IS v4_fdm2. Nothing is computed in this file - it loads, walks, and prints.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_fdm_reentry as RE
    import v4_signal as SG
    import ln
finally:
    sys.stderr = _e

RE_AT = os.environ.get('W_FDM2_OPEN', '2026-08-03 00:41:30')
ALL = os.environ.get('W_FDM2_LEGS', '1') == 'all'
#   W_FDM2_DAY=YYYY-MM-DD runs ONE DAY end to end: the first re-entry at or after 00:00:00 opens,
#   and the walk stops at 23:59:55. The day bound is HIS - *"pick one day to test it on"* - not a
#   horizon of mine, and the driver prints both edges so the span is on the page.
DAY = os.environ.get('W_FDM2_DAY')

LN = F2.load()
B = len(LN['close']) - 1
A = 0
if DAY:
    A, B = ln.K(DAY + ' 00:00:00'), ln.K(DAY + ' 23:59:55')
    ALL = True
print('# fdm2 | TAPE %d bars, ends %s | RULED_OK %s'
      % (len(LN['close']), ln.U(len(LN['close']) - 1), K.RULED_OK))
print('# THE WALK RUNS %s .. %s%s'
      % (ln.U(A), ln.U(B), ' - HIS one-day bound' if DAY else ' - the whole tape'))
print('# THE STOP IS ON: FDM_MAE_CAP %.2f%% adverse from the open, his "yes, move it to default"'
      % float(K.FDM_MAE_CAP))
print()
print('| the knob | value | what it is |')
print('|---|---|---|')
for nm, what in (('FDM_FNC_2080', 'his "fdm-20-80-fnc" - step 1 AND the population. "ex" includes oob'),
                 ('FDM_STEP1_ABOVE_TF', 'step 1 scans STRICTLY above this TF, so ws4..ws30 = 27 lines'),
                 ('FDM_POP_LO', 'the reversal population floor, so ws3..ws30 = 28 before the filter'),
                 ('FDM_M3_FNC', 'ws3Mage\'s fence in the preamble, 25 -> 25/75'),
                 ('FDM_X10_WOB', 'the ws10x race hold, bars. His 1103 "use 24"'),
                 ('FDM_X10_GRACE_PCT', 'his "fdm-ws10x-cad-grace" - the grace walk\'s floor, %'),
                 ('FDM_X10_TRADE_PCT', 'the grace walk\'s rev-trade threshold, %'),
                 ('FDM_X10_GRACE_MIN', 'the grace walk\'s length, minutes'),
                 ('FDM_MAE_CAP', 'the stop, % adverse from the open'),
                 ('FDM_X10_FRM', 'must the race CROSS follow the cadence event, or only its CONFIRM'),
                 ('FDM_REV_FROM', 'where the reversal count starts: the cadence event bar, or that event\'s window open'),
                 ('LIFT_WOB', 'the lift-off hold; the reversal STAMP is lift + 7 bars = 35 s')):
    v = getattr(K, nm)
    print('| %s | %s | %s |' % (nm, ('%g' % v) if not isinstance(v, str) else v, what))
print()

#   ── the open: his banked re-entry ─────────────────────────────────────────────────────────────
SIGS = RE.signals(LN['G30B'], LN['EMR'])
if DAY:
    HIT = [x for x in SIGS if A <= int(x['bar']) <= B]
    assert HIT, 'no fdm re-entry signal inside %s .. %s' % (ln.U(A), ln.U(B))
    g = HIT[0]
else:
    k0 = ln.K(RE_AT)
    HIT = [x for x in SIGS if int(x['bar']) == k0]
    assert len(HIT) == 1, ('the %s re-entry signal is not in the list - %d matches'
                           % (RE_AT, len(HIT)))
    g = HIT[0]
D = SG.direction(int(g['side']))
OPN = SG.fire_bar(g)
TS = SG.target_side(D)
print('| the open | value |')
print('|---|---|')
print('| the re-entry signal bar | %s |' % ln.U(int(g['bar'])))
print('| the gcws30b window side | %s oob |' % ('HIGH' if int(g['side']) > 0 else 'LOW'))
print('| the trade | %s |' % D)
print('| its target side | %s |' % ('HIGH' if TS > 0 else 'LOW'))
print('| the open price bar | %s - the router\'s "just OPEN", 1 bar |' % ln.U(OPN))
print('| why | %s |' % g['why'])
print()

LG = F2.legs(LN, (OPN, TS, 'fdm re-entry %s' % ln.U(int(g['bar']))), B, resig=SIGS)
if not ALL:
    LG = LG[:1]

#   ── the decision rows, chronological ──────────────────────────────────────────────────────────
for i, L in enumerate(LG):
    print('## leg %s | %s | target side %s | %s'
          % (ln.U(L['opn']), 'LONG' if L['side'] > 0 else 'SHORT',
             'HIGH' if L['side'] > 0 else 'LOW', L['src']))
    print()
    print('| the bar | the stage | why |')
    print('|---|---|---|')
    for r in L['rows']:
        print('| %s | %s | %s |' % (ln.U(int(r['bar'])), r['stage'], r['why']))
    if not L['rows']:
        print('| %s | NO CADENCE EVENT | no cadence event on the %s side from the open to %s |'
              % (ln.U(L['opn']), 'HIGH' if L['side'] > 0 else 'LOW', ln.U(B)))
    print()

#   ── the population at every ws10x-cadence ─────────────────────────────────────────────────────
#   HIS 1103 *"how many of the 28 lines were ex-fence and contributed to the ws10x-cadence?"*.
#   28 lines are eligible, ws3..ws30. A line enters the POPULATION by printing ex-20/80 on the
#   target side at least once between the trade's open and the ws10x-cadence; it CONTRIBUTES by
#   also having a lift-off stamp inside the reversal window. The two lists are the row's own, so
#   this table cannot drift from the decision that used them.
X = [(L, r) for L in LG for r in L['rows'] if 'pop' in r]
if X:
    print('## the 28 eligible lines at every ws10x-cadence | ws%d..ws%d'
          % (int(K.FDM_POP_LO), int(LN['HI'])))
    print()
    print('| the ws10x-cadence | the trade it was deciding | ex-20/80 at least once |'
          ' contributed a reversal | silent - ex-fence but no reversal | never ex-fence |')
    print('|---|---|---|---|---|---|')
    ALLTF = list(range(int(K.FDM_POP_LO), int(LN['HI']) + 1))
    for L, r in X:
        pop, rtf = list(r['pop']), list(r.get('rev_tfs') or ())
        sil = [t for t in pop if t not in rtf]
        nev = [t for t in ALLTF if t not in pop]
        f = lambda v: ('ws' + ', ws'.join(str(t) for t in v)) if v else 'none'
        print('| %s | %s %s | %d of %d - %s | %d of %d - %s | %d - %s | %d - %s |'
              % (ln.U(int(r['bar'])), ln.U(L['opn']),
                 'LONG' if L['side'] > 0 else 'SHORT',
                 len(pop), len(ALLTF), f(pop), len(rtf), len(pop), f(rtf),
                 len(sil), f(sil), len(nev), f(nev)))
    print()
    print('| the roll-up over %d ws10x-cadences | value |' % len(X))
    print('|---|---|')
    ps = [len(list(r['pop'])) for _, r in X]
    rs = [len(list(r.get('rev_tfs') or ())) for _, r in X]
    print('| eligible lines, every time | %d |' % len(ALLTF))
    print('| population, smallest .. largest | %d .. %d |' % (min(ps), max(ps)))
    print('| population, mean | %.1f |' % (sum(ps) / len(ps)))
    print('| contributed, smallest .. largest | %d .. %d |' % (min(rs), max(rs)))
    print('| contributed, mean | %.1f |' % (sum(rs) / len(rs)))
    cnt = {}
    for _, r in X:
        for t in list(r.get('rev_tfs') or ()):
            cnt[t] = cnt.get(t, 0) + 1
    pcnt = {}
    for _, r in X:
        for t in list(r['pop']):
            pcnt[t] = pcnt.get(t, 0) + 1
    print()
    print('| the line | times in the population | times it contributed |')
    print('|---|---|---|')
    for t in ALLTF:
        print('| ws%d | %d of %d | %d of %d |' % (t, pcnt.get(t, 0), len(X), cnt.get(t, 0), len(X)))
    print()

#   ── the legs ──────────────────────────────────────────────────────────────────────────────────
print('## the legs | every number carries the FDM_MAE_CAP %.2f%% stop' % float(K.FDM_MAE_CAP))
print()
print('| the open | the trade | the rev-trade signal | the exit | the exit kind | held min |'
      ' MAE% | MFE% | realised% |')
print('|---|---|---|---|---|---|---|---|---|')
for L in LG:
    print('| %s | %s | %s | %s | %s | %.1f | %.3f | %.3f | %+.3f |'
          % (ln.U(L['opn']), 'LONG' if L['side'] > 0 else 'SHORT',
             '-' if L['sig'] is None else ln.U(int(L['sig'])), ln.U(L['exit']), L['ctype'],
             L['held_min'], L['mae'], L['mfe'], L['rel']))
print()
S = F2.score(LG)
print('| the aggregate | value |')
print('|---|---|')
print('| legs | %d |' % S['n'])
print('| stopped | %d |' % S['stops'])
print('| gross %% | %+.3f |' % S['gross'])
print('| drag %% | -%.3f (%.4f%% round trip x %d legs) |' % (S['drag'], F2.DRAG_PCT, S['n']))
print('| net %% | %+.3f |' % S['net'])
print('| MAE %% total | %.3f |' % S['mae'])
print('| MFE %% total | %.3f |' % S['mfe'])
print('| MFE captured | %.1f%% of MFE |'
      % ((S['gross'] / S['mfe'] * 100.0) if S['mfe'] else float('nan')))
print('| held min, shortest .. longest | %.1f .. %.1f |' % (S['min_held'], S['max_held']))


#   ── W_FDM2_VERIFY=on: the machine's own numbers at his six 08-03 trades ───────────────────────
#   HIS SIX 08-03 TRADES and the side of the trade being CLOSED at each cadence. The span of the
#   last one, 1841, ENDS AT MIDNIGHT AND THAT BOUND IS MINE - there is no seventh trade to close
#   it. Every other span ends at the next trade.
#
#   THE WALK IS F2.walk, NOT A LOOP OVER THE EVENTS. A hand-rolled loop printed every cadence
#   event in a span, which for 1841 was three - but the mech CLOSES the trade at its first
#   rev-trade, so the 21:03 and 23:01 rows were decision points for a trade that ended at 18:51:55,
#   with populations measured from an open that no longer existed. F2.walk stops where the mech
#   stops, so the table cannot drift from the machine again.
#
#   THE RAW-BAR COLUMNS ARE A DIAGNOSTIC OF THE SUPERSEDED CENSUS, NOT A MACHINE ARM. They count
#   the lift-off bar itself, which is 35 s of lookahead at LIFT_WOB 8, over the row's OWN frozen
#   population - so the only difference between the two pcts is the stamp.
if os.environ.get('W_FDM2_VERIFY') == 'on':
    from optimus9.analysis.jig import lift_off as _lo

    def _raw(sd, pop, a, b):
        n = 0
        for tf in pop:
            bars = _lo(LN['EMR'][tf], sd, K.LIFT_PTS, K.gap_for(tf), K.LIFT_TOL, K.LIFT_WOB)
            if any(int(a) < int(x) <= int(b) for x in bars):
                n += 1
        return n

    #   THE SIDE AT A CADENCE EVENT IS THE OUTGOING TRADE'S TARGET - the trade being CLOSED.
    #   HIS 1103 *"that was a rule for me to adhere to - not for the code or the spec"*: his
    #   incoming-only convention is how HE will refer to trades in conversation. It is not a change
    #   to the mech, and the sides below are back to where they were.
    #
    #   0702 RUNS BOTH SIDES. The day's first trade has no prior trade to take a side from, and his
    #   *"completely delete my 'low side long' statement"* removes the only thing that set it.
    HIS = [('0702', '2026-08-03 07:02:00', '2026-08-03 10:08:00', None),
           ('1008', '2026-08-03 10:08:00', '2026-08-03 13:15:00', +1),
           ('1315', '2026-08-03 13:15:00', '2026-08-03 14:06:00', -1),
           ('1406', '2026-08-03 14:06:00', '2026-08-03 16:44:00', +1),
           ('1644', '2026-08-03 16:44:00', '2026-08-03 18:41:00', -1),
           ('1841', '2026-08-03 18:41:00', '2026-08-04 00:00:00', +1)]
    print()
    print('## his 08-03 trades through v4_fdm2 | ws10x hold FDM_X10_WOB %d bars = %d s |'
          ' each walk STOPS at its first rev-trade, as the mech does'
          % (int(K.FDM_X10_WOB), int(K.FDM_X10_WOB) * 5))
    print()
    print('| the trade | the outgoing trade\'s target side | the bar | the stage | step 1 nestled+towards | the ws10x-cadence | which |'
          ' reversed, STAMP | pct, STAMP | reversed, RAW lift bar | pct, RAW |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for nm, t0, t1, psd in HIS:
        a, b = ln.K(t0), ln.K(t1)
        for sd in ((psd,) if psd is not None else (-1, +1)):
            sn = 'HIGH' if sd > 0 else 'LOW'
            sig, rows = F2.walk(LN, sd, a, b)
            if not rows:
                print('| %s | %s | - | NO CADENCE EVENT | - | - | - | - | - | - | - |'
                      % (nm, sn))
                continue
            for r in rows:
                st = str(r['stage'])
                k = '%d of %d' % (int(r['k']), int(r['n'])) if 'k' in r else '-'
                if 'pop' in r:
                    pop = list(r['pop'])
                    rw = _raw(sd, pop, int(r['ev']), int(r['bar']))
                    pr = (rw / len(pop) * 100.0) if pop else 0.0
                    print('| %s | %s | %s | %s | %s | %s | %s | %d of %d | %.1f%% |'
                          ' %d of %d | %.1f%% |'
                          % (nm, sn, ln.U(int(r['bar'])), st, k, ln.U(int(r['bar'])),
                             r['which'], int(r['rv']), len(pop), float(r['pct']),
                             rw, len(pop), pr))
                else:
                    print('| %s | %s | %s | %s | %s | - | - | - | - | - | - |'
                          % (nm, sn, ln.U(int(r['bar'])), st, k))
            if sig is not None:
                print('| %s | %s | %s | TRADE CLOSES | - | - | - | - | - | - | - |'
                      % (nm, sn, ln.U(int(sig) + 1)))


#   ── W_FDM2_WHY='<side> <from> <to>': every ws1b cross on that side, with its per-test verdict ──
#   HIS 1103 *"why was 1644 tagged as NO CADENCE EVENT?  I see ws2r low oob at 1640, well inside of
#   ws1b's low oob excursion"*. The trace view of F2.cadence_events reads the rejection off the
#   data. side is 'high' or 'low'; the window bounds the CROSS, and an excursion may start before
#   the window and still be reported.
_W = os.environ.get('W_FDM2_WHY')
if _W:
    _p = _W.split(None, 1)
    _sd = +1 if _p[0].lower().startswith('h') else -1
    _a, _b = [ln.K(x.strip()) for x in _p[1].split('..')]
    print()
    print('## every ws1b %s oob->ib cross | the cross in %s .. %s | the cadence preamble, test by'
          ' test' % ('HIGH' if _sd > 0 else 'LOW', ln.U(_a), ln.U(_b)))
    print()
    print('| the ws1b cross | the cross is in the window | the ws1b excursion | the nestle |'
          ' ws3Mage ex-%g/%g | the verdict |'
          % (float(K.FDM_M3_FNC), 100.0 - float(K.FDM_M3_FNC)))
    print('|---|---|---|---|---|')
    for t in F2.cadence_events(LN, _sd, _a, _b, trace=True):
        if not (_a <= int(t['cross']) <= _b):
            if t['s0'] is None or int(t['s0']) > _b or int(t['s1']) < _a:
                continue
        ok = (t['nestle'] is not None and t['m3'] and t['inwin'])
        fail = ('-' if ok else
                'the cross is outside the window' if not t['inwin'] else
                'no excursion' if t['s0'] is None else
                'the nestle - no ws1,2Mage deeper than an oob ws1,2,3r' if t['nestle'] is None
                else 'ws3Mage never ex-fence')
        print('| %s | %s | %s | %s | %s | %s |'
              % (ln.U(int(t['cross'])), 'yes' if t['inwin'] else 'NO',
                 '-' if t['s0'] is None else '%s .. %s' % (ln.U(int(t['s0'])),
                                                           ln.U(int(t['s1']))),
                 '-' if t['nestle'] is None else 'ws%dMage %.2f vs ws%dr %.2f at %s'
                 % (t['nestle'][1], t['nestle'][2], t['nestle'][3], t['nestle'][4],
                    ln.U(int(t['nestle'][0]))),
                 'yes' if t['m3'] else 'NO', 'CADENCE EVENT' if ok else fail))


#   ── W_FDM2_SAV='<the open bar>': v4saviour on one fdm2 leg ────────────────────────────────────
#   HIS 1103 *"I think we can use it to reverse the 1356 LONG"*. v4saviour is banked and unchanged;
#   this only hands it a leg's open bar and the leg's own target side.
#   THE LINES ARE THE LIVE ONES, as banked. v4saviour was validated against his four 09-01/09-02
#   examples on the live lines; fdm2's chart-matched reads would move its verdicts off them.
_S = os.environ.get('W_FDM2_SAV')
if _S:
    _e2 = sys.stderr; sys.stderr = io.StringIO()
    try:
        import v4_saviour as SAV
    finally:
        sys.stderr = _e2
    k = ln.K(_S)
    hit = [L for L in LG if int(L['opn']) == k]
    assert hit, 'no fdm2 leg opens at %s in this run' % _S
    L = hit[0]
    #   HIS 1103 *"convert it to closed-prev and remove the armed gate"*.
    #     R    the fence reads - the oob runs, the ib crosses, the cascade ladder, the past-50
    #          gate, the route's extrema anchor. CHART-MATCHED
    #     RE   the lift-off only. EMERGING, his standing rule
    #     arm  False - the ws5r walkback is out, so ws5r is not read at all
    #   v4saviour's own default is still the arm ON with one array for both reads, so v4_machine.py
    #   is untouched.
    R = {t: LN['CPR'][t] for t in (1, 2)}
    RE = {t: LN['EMR'][t] for t in (1, 2)}
    MG = {t: LN['CPM'][t] for t in range(1, 13)}
    v = SAV.walk(int(L['opn']), int(L['side']), R, MG, ln.U, RE=RE, arm=False)
    print()
    print('## v4saviour on the %s %s | target side %s | chart-matched, lift-off emerging, no arm'
          % (ln.U(L['opn']), 'LONG' if L['side'] > 0 else 'SHORT',
             'HIGH' if L['side'] > 0 else 'LOW'))
    print()
    print('| the step | the bar | what it read |')
    print('|---|---|---|')
    for a, b, c in v['why']:
        print('| %s | %s | %s |' % (a, b, str(c).replace('|', '\\|')))
    print()
    print('| the verdict | value |')
    print('|---|---|')
    print('| v4saviour | %s |' % v['verdict'])
    if v.get('fill') is not None:
        o = float(LN['close'][int(L['opn'])])
        px = float(LN['close'][int(v['fill'])])
        print('| it ends the trade at | %s |' % ln.U(int(v['fill'])))
        print('| it opens the reverse at | %s |' % ln.U(int(v['reopen'])))
        print('| from | %s |' % v['from_line'])
        print('| the leg would realise | %+.3f%% |' % (int(L['side']) * (px - o) / o * 100.0))
    print('| what fdm2 did instead | %s at %s, %+.3f%% |'
          % (L['ctype'], ln.U(L['exit']), L['rel']))
