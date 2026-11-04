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
    from optimus9.analysis.jig import towards_away as TA
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
#   W_FDM2_DAY also takes a RANGE - '2026-09-15 .. 2026-09-17' - which is ONE continuous chain
#   across those days, not three separate runs. His 1103: *"extend the 09-15 window to 09-16 and
#   09-17, and continue with the chain walk"*. A leg that opens on one day and exits on the next
#   stays one leg, which is the whole point of extending rather than re-running.
DAY = os.environ.get('W_FDM2_DAY')

LN = F2.load()
B = len(LN['close']) - 1
A = 0
if DAY:
    if '..' in DAY:
        _d1, _d2 = [x.strip() for x in DAY.split('..')]
    else:
        _d1 = _d2 = DAY
    A, B = ln.K(_d1 + ' 00:00:00'), ln.K(_d2 + ' 23:59:55')
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

#   THE READ-ONLY ARMS NEED NO CHAIN. W_FDM2_WHY, W_FDM2_LINE and W_FDM2_BOARD are value reads, so
#   with no day given they skip the walk entirely. Before this they fell through to the single-leg
#   path, whose RE_AT default is the 2026-08-03 00:41:30 signal - a bar that stopped existing the
#   moment FDM_RE_WIN_OPEN moved to 'both', so every read-only arm asserted on a stale default.
#   EVERY PURE-READ ARM GOES IN THIS ONE LIST. Adding an arm and forgetting the list is how
#   W_FDM2_AWAY hit the stale 2026-08-03 00:41:30 default on its first run.
READ_ARMS = ('W_FDM2_WHY', 'W_FDM2_LINE', 'W_FDM2_BOARD', 'W_FDM2_AWAY', 'W_FDM2_WS5REV')
#   W_FDM2_CONF needs the chain, so it is NOT a read arm
READONLY = (not DAY) and any(os.environ.get(v) for v in READ_ARMS)
LG = []

#   ── the open: his banked re-entry ─────────────────────────────────────────────────────────────
#   HIS 1104 BANK: the re-entry reads the CHART-MATCHED ladder, and the emerging one is handed
#   in only so FDM_RE_REV_READ='emerging' can be run as the arm it replaced.
SIGS = [] if READONLY else RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'])
if not READONLY:
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
            print('| %s | %s | %s%s |'
                  % (ln.U(int(r['bar'])), r['stage'], r['why'],
                     '' if not r.get('cwhy') else ' || ' + str(r['cwhy'])))
        if not L['rows']:
            print('| %s | NO CADENCE EVENT | no cadence event on the %s side from the open to %s |'
                  % (ln.U(L['opn']), 'HIGH' if L['side'] > 0 else 'LOW', ln.U(B)))
        print()

if not READONLY:
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
    #   PER DAY, BY THE LEG'S OPEN BAR. A leg that straddles midnight is counted on the day it opened,
    #   stated so the rows add to the total exactly once.
    _days = sorted({ln.U(L['opn'])[:10] for L in LG})
    if len(_days) > 1:
        print()
        print('## each day\'s contribution | a leg counts on the day it OPENED')
        print()
        print('| the day | legs | stopped | gross % | drag % | net % | MAE % | MFE % | MFE'
              ' captured | rescued cadences |')
        print('|---|---|---|---|---|---|---|---|---|---|')
        for _dd in _days:
            _sub = [L for L in LG if ln.U(L['opn'])[:10] == _dd]
            _s2 = F2.score(_sub)
            _rc = sum(1 for L in _sub for r in L['rows'] if 'RESCUED' in str(r.get('cwhy') or ''))
            print('| %s | %d | %d | %+.3f | -%.3f | %+.3f | %.3f | %.3f | %.1f%% | %d |'
                  % (_dd, _s2['n'], _s2['stops'], _s2['gross'], _s2['drag'], _s2['net'],
                     _s2['mae'], _s2['mfe'],
                     (_s2['gross'] / _s2['mfe'] * 100.0) if _s2['mfe'] else float('nan'), _rc))


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
              ' ws3r extremum in the excursion | ws3Mage extremum in the excursion |'
              ' ws3Mage ex-%g/%g | the verdict |'
              % K.fnc_pair(K.FDM_M3_FNC))
        print('|---|---|---|---|---|---|---|')
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
            #   ws3r AND ws3Mage AT THEIR DEEPEST IN THE EXCURSION, on the cross's own side. His 1103
            #   ask on the ws3Mage-gated list: the gate's verdict with no number beside it does not say
            #   how far short the line came.
            if t['s0'] is None:
                _x3r = _x3m = float('nan')
            else:
                _g3r = LN['CPR'][3][int(t['s0']):int(t['s1']) + 1]
                _g3m = LN['CPM'][3][int(t['s0']):int(t['s1']) + 1]
                _x3r = float(np.nanmax(_g3r)) if _sd > 0 else float(np.nanmin(_g3r))
                _x3m = float(np.nanmax(_g3m)) if _sd > 0 else float(np.nanmin(_g3m))
            print('| %s | %s | %s | %s | %.2f | %.2f | %s | %s |'
                  % (ln.U(int(t['cross'])), 'yes' if t['inwin'] else 'NO',
                     '-' if t['s0'] is None else '%s .. %s' % (ln.U(int(t['s0'])),
                                                               ln.U(int(t['s1']))),
                     '-' if t['nestle'] is None else 'ws%dMage %.2f vs ws%dr %.2f at %s'
                     % (t['nestle'][1], t['nestle'][2], t['nestle'][3], t['nestle'][4],
                        ln.U(int(t['nestle'][0]))),
                     _x3r, _x3m,
                     ('yes' if t.get('rsc') is None else 'RESCUED at %g/%g'
                      % K.fnc_pair(K.FDM_M3_RESCUE_FNC))
                     if t['m3'] else 'NO', 'CADENCE EVENT' if ok else fail))


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
        import v4_closed_prev as CP
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
    #   HIS 1103 *"use emerging values, at the emerging ws1Mage extermum, and reduce the cascade
    #   to ws1-3"*. Every read is the EMERGING set now, so R and RE are the same array and the
    #   chart-matched/lift-off split does not arise. The sampler takes NO seam lattice: an emerging
    #   line steps on every 5 s bar, so every bar is its own value's bar.
    SAV_TF_HI = int(os.environ.get('W_FDM2_SAV_TFHI', '3'))
    R = {t: LN['EMR'][t] for t in (1, 2)}
    RE = R
    MG = {t: LN['MGE'][t] for t in range(1, 13)}
    #   THE SAMPLER LANDS ON THE SEAM BARS. His 1103 *"the sampling should match closed-prev, ie
    #   seam-5s"*. ws1Mage is a 60 s line, so its seams are the xx:xx:55 bars, and the array comes
    #   from v4_closed_prev.seam_bars - the same arithmetic that built the closed-prev series.
    v = SAV.walk(int(L['opn']), int(L['side']), R, MG, ln.U, RE=RE, arm=False,
                 tf_hi=SAV_TF_HI, anchor='ws1mage', sample_bars=None)
    print()
    print('## v4saviour on the %s %s | target side %s | EMERGING reads, the emerging ws1Mage'
          ' extremum, ws1..ws%d, min %d lines, zoom %d rungs, no arm'
          % (ln.U(L['opn']), 'LONG' if L['side'] > 0 else 'SHORT',
             'HIGH' if L['side'] > 0 else 'LOW', SAV_TF_HI, int(K.SAV_CASCADE_MIN),
             int(K.SAV_CASCADE_ZOOM)))
    print()
    print('| the step | the bar | what it read |')
    print('|---|---|---|')
    for a, b, c in v['why']:
        print('| %s | %s | %s |' % (a, b, str(c).replace('|', '\\|')))
    print()
    #   THE LADDER, LINE BY LINE. The why-string gives each cluster's span and length but not the
    #   values, so a 3/3 split reads as a fact with no cause on the page. `step to the next rung`
    #   is the adjacent diff; `step across the zoom` is the one _mc_run actually tests, comparing a
    #   line with the line SAV_CASCADE_ZOOM rungs along.
    _AB = [b2 for a2, b2, c2 in v['why'] if a2 in ('the cascade anchor',
                                                   'the ws1Mage target-side extrema anchor')]
    _z = int(K.SAV_CASCADE_ZOOM)
    #   ONE TABLE PER DISTINCT ANCHOR. Branch A's anchor and the route's resolve to the same
    #   extremum whenever the walk stays inside one of ws1Mage's own steps, and printing it twice
    #   is noise.
    for _i, _bar in enumerate(sorted(set(_AB), key=_AB.index)):
        _k = ln.K(_bar)
        print()
        print('### the ws1..ws%d Mage ladder at %s | zoom %d rungs, a cluster needs %d lines'
              % (SAV_TF_HI, _bar, _z, int(K.SAV_CASCADE_MIN)))
        print()
        print('| the line | its value | step to the next rung | step across the zoom to ws%d+ |'
              % _z)
        print('|---|---|---|---|')
        _H = SAV_TF_HI
        _v = [float(LN['MGE'][t][_k]) for t in range(1, _H + 1)]
        for _t in range(1, _H + 1):
            _n = ('%+.4f' % (_v[_t] - _v[_t - 1])) if _t < _H else '-'
            _zz = ('%+.4f' % (_v[_t - 1 + _z] - _v[_t - 1])) if _t - 1 + _z < _H else '-'
            print('| ws%dMage | %.4f | %s | %s |' % (_t, _v[_t - 1], _n, _zz))
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


#   ── W_FDM2_LINE='<name> <from> .. <to>': one line, both reads, bar by bar ──────────────────────
#   A value read is not a mech - it is here so a timestamp he quotes can be checked against the
#   same arrays the walk uses, on both reads, without a fragment script.
_L = os.environ.get('W_FDM2_LINE')
if _L:
    _p2 = _L.split(None, 1)
    _nm = _p2[0]
    _a1, _b1 = [ln.K(x.strip()) for x in _p2[1].split('..')]
    if _nm == 'ws1b':
        _emg, _cp = np.asarray(ln.line('ws1b'), float), LN['B1']
    elif _nm.endswith('Mage'):
        _t = int(_nm[2:-4]); _emg, _cp = LN['MGE'][_t], LN['CPM'][_t]
    else:
        _t = int(_nm[2:-1]); _emg, _cp = LN['EMR'][_t], LN['CPR'][_t]
    print()
    print('## %s bar by bar | %s .. %s | oob is %g/%g'
          % (_nm, ln.U(_a1), ln.U(_b1), float(K.OOB_LO), float(K.OOB_HI)))
    print()
    print('| the bar | %s emerging | %s chart-matched | emerging oob | chart-matched oob |'
          % (_nm, _nm))
    print('|---|---|---|---|---|')
    for _i2 in range(_a1, min(_b1, B) + 1):
        _e4, _c4 = float(_emg[_i2]), float(_cp[_i2])
        _f = lambda v: ('HIGH' if v >= float(K.OOB_HI) else
                        ('LOW' if v <= float(K.OOB_LO) else '-'))
        print('| %s | %.2f | %.2f | %s | %s |' % (ln.U(_i2), _e4, _c4, _f(_e4), _f(_c4)))


#   ── W_FDM2_BOARD='<side> <bar> , <bar> , ...': the board at named bars ─────────────────────────
#   ws1..ws30 at each bar: ex-FDM_FNC_2080 on the side, `towards` the side, and both. A value read,
#   not a mech - it answers "how many lines" without a fragment script.
_BD = os.environ.get('W_FDM2_BOARD')
if _BD:
    _pb = _BD.split(None, 1)
    _sb = +1 if _pb[0].lower().startswith('h') else -1
    _bars = [ln.K(x.strip()) for x in _pb[1].split(',')]
    _sn2 = 'HIGH' if _sb > 0 else 'LOW'
    for _bk in _bars:
        print()
        print('## the board at %s | the %s side | ex-%g/%g and towards'
              % (ln.U(_bk), _sn2, *K.fnc_pair(K.FDM_FNC_2080)))
        print()
        #   BOTH DIRECTIONS PER LINE. His 1103: *"there's a potential discrepancy: the sum of
        #   travelling incoming and travelling outgoing is greater than the set size"*. The two
        #   `towards` reads are NOT complements - each anchors on the OPPOSED extreme for its own
        #   side, so a line between its block's high and its block low can satisfy both.
        #   THE LIFT-OFF STAMPS ARE HERE TOO, both sides, because his 1103 `away` is defined by
        #   one: *"`away` is travelling away from the low side after it has lift-off reversed"*.
        #   A line's most recent lift-off off the TRADE'S side at or before the bar is what
        #   separates `away` from `towards` under that reading.
        print('| the line | its value | ex-%g/%g %s | towards HIGH, old test |'
              ' towards LOW, old test | last lift-off off the LOW | last lift-off off the HIGH |'
              % (*K.fnc_pair(K.FDM_FNC_2080), _sn2))
        print('|---|---|---|---|---|---|---|')
        _ne = _nt = _nb = 0
        for _t3 in range(1, int(LN['HI']) + 1):
            _a3 = LN['CPR'][_t3]
            _v3 = float(_a3[_bk])
            _e7 = F2.ex2080(_v3, _sb)
            _th = F2.towards(_a3, _t3, _bk, +1)
            _tl = F2.towards(_a3, _t3, _bk, -1)
            _t7 = _th if _sb > 0 else _tl
            _ne += int(_e7); _nt += int(_t7); _nb += int(_th and _tl)
            _sl = LN['LIFT'][(_t3, -1)]; _sh = LN['LIFT'][(_t3, +1)]
            _sl = _sl[_sl <= _bk]; _sh = _sh[_sh <= _bk]
            print('| ws%dr | %.2f | %s | %s | %s | %s | %s |'
                  % (_t3, _v3, 'yes' if _e7 else '-', 'yes' if _th else '-',
                     'yes' if _tl else '-',
                     ln.U(int(_sl[-1])) if _sl.size else 'none on the tape',
                     ln.U(int(_sh[-1])) if _sh.size else 'none on the tape'))
        print()
        print('| the count at %s | ws1..ws30 | ws4..ws30 |' % ln.U(_bk))
        print('|---|---|---|')
        _e4b = sum(1 for t in range(1, int(LN['HI']) + 1)
                   if F2.ex2080(float(LN['CPR'][t][_bk]), _sb))
        _t4b = sum(1 for t in range(1, int(LN['HI']) + 1)
                   if F2.towards(LN['CPR'][t], t, _bk, _sb))
        _lo4 = int(K.FDM_STEP1_ABOVE_TF) + 1
        _e4c = sum(1 for t in range(_lo4, int(LN['HI']) + 1)
                   if F2.ex2080(float(LN['CPR'][t][_bk]), _sb))
        _t4c = sum(1 for t in range(_lo4, int(LN['HI']) + 1)
                   if F2.towards(LN['CPR'][t], t, _bk, _sb))
        _b4b = sum(1 for t in range(1, int(LN['HI']) + 1)
                   if F2.ex2080(float(LN['CPR'][t][_bk]), _sb)
                   and F2.towards(LN['CPR'][t], t, _bk, _sb))
        _b4c = sum(1 for t in range(_lo4, int(LN['HI']) + 1)
                   if F2.ex2080(float(LN['CPR'][t][_bk]), _sb)
                   and F2.towards(LN['CPR'][t], t, _bk, _sb))
        _bothn = sum(1 for t in range(1, int(LN['HI']) + 1)
                     if F2.towards(LN['CPR'][t], t, _bk, +1)
                     and F2.towards(LN['CPR'][t], t, _bk, -1))
        _neith = sum(1 for t in range(1, int(LN['HI']) + 1)
                     if not F2.towards(LN['CPR'][t], t, _bk, +1)
                     and not F2.towards(LN['CPR'][t], t, _bk, -1))
        _thn = sum(1 for t in range(1, int(LN['HI']) + 1)
                   if F2.towards(LN['CPR'][t], t, _bk, +1))
        _tln = sum(1 for t in range(1, int(LN['HI']) + 1)
                   if F2.towards(LN['CPR'][t], t, _bk, -1))
        print('| towards HIGH | %d of %d | - |' % (_thn, int(LN['HI'])))
        print('| towards LOW | %d of %d | - |' % (_tln, int(LN['HI'])))
        print('| BOTH directions at once | %d of %d | - |' % (_bothn, int(LN['HI'])))
        print('| NEITHER direction | %d of %d | - |' % (_neith, int(LN['HI'])))
        print('| towards HIGH + towards LOW | %d | - |' % (_thn + _tln))
        print('| HIGH + LOW - both + neither | %d, must equal %d |  - |'
              % (_thn + _tln - _bothn + _neith, int(LN['HI'])))
        print('| towards %s | %d of %d | %d of %d |'
              % (_sn2, _t4b, int(LN['HI']), _t4c, int(LN['HI']) - _lo4 + 1))
        print('| ex-%g/%g %s | %d of %d | %d of %d |'
              % (*K.fnc_pair(K.FDM_FNC_2080), _sn2, _e4b,
                 int(LN['HI']), _e4c, int(LN['HI']) - _lo4 + 1))
        print('| both | %d of %d | %d of %d |'
              % (_b4b, int(LN['HI']), _b4c, int(LN['HI']) - _lo4 + 1))


#   ── W_FDM2_STOPSRC=on: every stopped leg, what opened it, and the board at its open ────────────
#   HIS 1103: *"how many other ws10x cadences were responsible for an open that ended on a stop,
#   while showing a table of data (like the one we see here) that has lines printing ex-fence and a
#   cluster(s) of 'incoming trade direction' trajectory?"*
#
#   BOTH SIDES ARE REPORTED at every open. In the 2026-09-17 00:06 case the board he asked for was
#   the HIGH side, which is the OUTGOING trade's target - the incoming SHORT hunts LOW. Rather than
#   pick which "incoming trade direction" means, each row carries both.
#
#   A CLUSTER IS A RUN OF CONSECUTIVE TIMEFRAMES, so each side reports its longest contiguous run
#   of `towards` and of ex-20/80 beside the plain counts.
if os.environ.get('W_FDM2_STOPSRC') == 'on':
    def _runlen(flags):
        best = cur = 0
        a = b = ba = bb = 0
        for i, v in enumerate(flags):
            if v:
                cur += 1
                if cur == 1:
                    a = i
                b = i
                if cur > best:
                    best, ba, bb = cur, a, b
            else:
                cur = 0
        return best, ba + 1, bb + 1

    def _bd(bar, side):
        ex = [F2.ex2080(float(LN['CPR'][t][bar]), side) for t in range(1, int(LN['HI']) + 1)]
        tw = [F2.towards(LN['CPR'][t], t, bar, side) for t in range(1, int(LN['HI']) + 1)]
        re_, ra, rb = _runlen(ex)
        tr, ta, tb = _runlen(tw)
        return (sum(ex), re_, ra, rb, sum(tw), tr, ta, tb)

    print()
    print('## every NON-PROFITABLE leg, what opened it, and the board at its open bar')
    print('# his 1103: *"stopped" was the wrong wording. I should have said "non-profitable"*')
    print('# non-profitable means realised at or below 0. The "under drag" column marks the ones')
    print('# that are positive but below the %.4f%% round trip, so net negative anyway' % F2.DRAG_PCT)
    print('# a cluster is a run of consecutive timeframes. ws1..ws%d, both sides at every open'
          % int(LN['HI']))
    print()
    #   HIS 1103 *"add a column to tell me if the setup is reentry based or incoming trade
    #   based"*, against his own definition: *"setup can be 1) an incoming trade or 2) a reentry"*.
    #   The fdm re-entry opens from FLAT, so its setup is the re-entry's own window. Every other
    #   opener - the ws10x-cadence, the grace walk, step 1 - is a rev-trade off a live trade, so
    #   the setup is the incoming trade.
    print('| the leg | its side | the setup | the exit kind | realised % | what opened it |'
          ' the signal bar |'
          ' ex-20/80 HIGH | the longest ex-20/80 HIGH cluster | towards HIGH |'
          ' the longest towards HIGH cluster | ex-20/80 LOW | the longest ex-20/80 LOW cluster |'
          ' towards LOW | the longest towards LOW cluster |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    for _i6, _L6 in enumerate(LG):
        if float(_L6['rel']) > 0:
            continue
        _src = str(_L6['src'])
        _kind, _sigb = _src, '-'
        if _i6 > 0 and _src.startswith('rev-trade'):
            _pr = [r for r in LG[_i6 - 1]['rows'] if r['stage'] == 'REV-TRADE']
            if _pr:
                _w6 = str(_pr[-1]['why'])
                _kind = ('the ws10x-cadence' if 'the ws10x-cadence -' in _w6 else
                         'the grace walk' if 'grace walk,' in _w6 else
                         'step 1, 0 of' if 'if the answer is no' in _w6 else 'a rev-trade')
                _sigb = ln.U(int(_pr[-1]['bar']))
        elif _src.startswith('fdm re-entry'):
            _kind = 'the fdm re-entry'
        _h = _bd(int(_L6['opn']), +1)
        _l = _bd(int(_L6['opn']), -1)
        _setup = ('re-entry based' if _kind == 'the fdm re-entry' else 'incoming trade based')
        print('| %s | %s | %s | %s | %+.3f | %s | %s | %d of %d | %d, ws%d-ws%d | %d of %d |'
              ' %d, ws%d-ws%d | %d of %d | %d, ws%d-ws%d | %d of %d | %d, ws%d-ws%d |'
              % (ln.U(_L6['opn']), 'LONG' if _L6['side'] > 0 else 'SHORT', _setup, _L6['ctype'],
                 _L6['rel'], _kind, _sigb,
                 _h[0], int(LN['HI']), _h[1], _h[2], _h[3], _h[4], int(LN['HI']), _h[5], _h[6], _h[7],
                 _l[0], int(LN['HI']), _l[1], _l[2], _l[3], _l[4], int(LN['HI']), _l[5], _l[6], _l[7]))

    _np = [L for L in LG if float(L['rel']) <= 0]
    _ud = [L for L in LG if 0 < float(L['rel']) < F2.DRAG_PCT]
    _k2 = {}
    for _i7, _L7 in enumerate(_np):
        pass
    print()
    print('| the reading | value |')
    print('|---|---|')
    print('| legs | %d |' % len(LG))
    print('| non-profitable, realised at or below 0 | %d |' % len(_np))
    print('| positive but under the %.4f%% drag | %d |' % (F2.DRAG_PCT, len(_ud)))
    print('| net negative once drag is taken | %d |' % (len(_np) + len(_ud)))
    if _ud:
        print()
        print('| the leg positive but under drag | its side | the exit kind | realised % |')
        print('|---|---|---|---|')
        for _L8 in _ud:
            print('| %s | %s | %s | %+.3f |'
                  % (ln.U(_L8['opn']), 'LONG' if _L8['side'] > 0 else 'SHORT', _L8['ctype'],
                     _L8['rel']))


#   ── W_FDM2_AWAY='<side> <the trade open> <the read bar>': his rolling-extremum `away` ──────────
#   HIS 1103: *"track the trade's target-side extremum for each line (rolling update of the value
#   at each bar). if the value for a line is printing further away from the target side extremum,
#   the line is deemed `away`"*.
#
#   THE EXTREMUM IS ROLLING AND CAUSAL: at each bar it is the most extreme value the line has
#   printed on the trade's target side since the trade opened, up to and including that bar. For a
#   LOW target that is the running minimum, for a HIGH target the running maximum.
#
#   "FURTHER AWAY" HAS TWO READINGS and both are printed, because his words do not pick one:
#     the gap        value minus the extremum on a LOW target, extremum minus value on a HIGH one.
#                    Positive on any bar the line is not AT its own extremum
#     the gap's move the gap at this bar against the gap one bar earlier. Positive means the line
#                    is moving further away right now
_AW = os.environ.get('W_FDM2_AWAY')
if _AW:
    _pa = _AW.split(None, 1)
    _sa = +1 if _pa[0].lower().startswith('h') else -1
    _o9, _r9 = [ln.K(x.strip()) for x in _pa[1].split(',')]
    print()
    print('## his rolling-extremum `away` | the %s target side | the trade opened %s | read at %s'
          % ('HIGH' if _sa > 0 else 'LOW', ln.U(_o9), ln.U(_r9)))
    print()
    print('| the line | its value | the rolling target-side extremum | at which bar |'
          ' the gap from it | the gap one bar earlier | the gap is | so `away` by the gap |'
          ' so `away` by the gap moving |')
    print('|---|---|---|---|---|---|---|---|---|')
    _g1 = _g2 = 0
    for _t9 in range(1, int(LN['HI']) + 1):
        _a9 = np.asarray(LN['CPR'][_t9], float)
        _seg9 = _a9[_o9:_r9 + 1]
        if _sa > 0:
            _xi = int(np.nanargmax(_seg9)); _xv = float(_seg9[_xi])
            _gap = _xv - float(_a9[_r9])
            _seg8 = _a9[_o9:_r9]
            _xv8 = float(np.nanmax(_seg8)) if _seg8.size else _xv
            _gap8 = _xv8 - float(_a9[_r9 - 1])
        else:
            _xi = int(np.nanargmin(_seg9)); _xv = float(_seg9[_xi])
            _gap = float(_a9[_r9]) - _xv
            _seg8 = _a9[_o9:_r9]
            _xv8 = float(np.nanmin(_seg8)) if _seg8.size else _xv
            _gap8 = float(_a9[_r9 - 1]) - _xv8
        _mv = 'widening' if _gap > _gap8 else ('narrowing' if _gap < _gap8 else 'flat')
        _aw1 = _gap > 0.0
        _aw2 = _gap > _gap8
        _g1 += int(_aw1); _g2 += int(_aw2)
        print('| ws%dr | %.2f | %.2f | %s | %+.2f | %+.2f | %s | %s | %s |'
              % (_t9, float(_a9[_r9]), _xv, ln.U(_o9 + _xi), _gap, _gap8, _mv,
                 'away' if _aw1 else 'towards', 'away' if _aw2 else 'towards'))
    print()
    print('| the count at %s | value |' % ln.U(_r9))
    print('|---|---|')
    #   THE SIDE GOES IN EVERY LABEL, his 1103: *"correction so that a future read doesn't
    #   misconstrue: 'away by the gap being positive FOR A SHORT'"*. The gap's arithmetic is
    #   side-dependent - value minus the running MINIMUM for a SHORT, the running MAXIMUM minus
    #   value for a LONG - so a bare "the gap being positive" invites the wrong one.
    _tn = 'SHORT' if _sa < 0 else 'LONG'
    _ar = ('value minus the running minimum' if _sa < 0 else
           'the running maximum minus value')
    print('| the gap, FOR A %s | %s |' % (_tn, _ar))
    print('| `away` by the gap being positive, FOR A %s | %d of %d |'
          % (_tn, _g1, int(LN['HI'])))
    print('| `towards` by the gap being zero, FOR A %s | %d of %d |'
          % (_tn, int(LN['HI']) - _g1, int(LN['HI'])))
    print('| `away` by the gap widening, FOR A %s | %d of %d |' % (_tn, _g2, int(LN['HI'])))
    print('| `towards` by the gap not widening, FOR A %s | %d of %d |'
          % (_tn, int(LN['HI']) - _g2, int(LN['HI'])))


#   ── W_FDM2_CONF=on: the fdm2-conf table, on the banked towards/away ───────────────────────────
#   HIS NAME, 1104: *"the table will be known as the fdm2-conf table"*. Renamed from W_FDM2_SETUPS,
#   the arm it used to answer to - the table has his name now, so the arm carries it.
#
#   HIS 1103 TABLE, rebuilt on jig.towards_away rather than the superseded two-sided `towards`.
#
#   THE ROWS, his 1104: *"show me all of the reentry legs, stopped or not"*. So every re-entry leg
#   prints whatever it realised, and an incoming-trade setup still prints only when it realised at
#   or under zero - the population the table carried before his change. The two longest-run columns
#   are deleted, also 1104.
#
#   EMERGING VALUES, his ruling: *"if we use closed-p, a ws22 bar will stay the same value for 22
#   minutes.  that's no bueno, so emerging must be the answer to the larger question"*. A rolling
#   extremum over a step function cannot update between its steps.
#
#   THE EXTREMUM'S ANCHOR. For an incoming-trade setup it is the INCOMING trade's own open - the
#   trade being closed. For a re-entry setup there is no incoming trade; his 1103 was *"that can
#   only be derived when the reentry lines qualify.  the mech behaves the same way - at the signal,
#   measure the lines"*, so the READ is at the signal and THE ANCHOR I USE IS THE RE-ENTRY WINDOW'S
#   OPEN, the only bar the re-entry owns before its signal. That choice is mine.
if os.environ.get('W_FDM2_CONF') == 'on':
    def _band(lo, hi, since, bar, side):
        """towards and ex-20/80 counts over ws{lo}..ws{hi} at `bar`, anchored at `since`.

        -> (towards, ex2080, the band's line count). The longest-run pair this used to return went
        with the two columns he deleted, 1104.
        """
        tw, ex = [], []
        for t in range(lo, hi + 1):
            r = TA(LN['EMR'][t], bar, side, since)
            tw.append(r['state'] == 'towards')
            ex.append(F2.ex2080(float(LN['CPR'][t][bar]), side))
        return sum(tw), sum(ex), hi - lo + 1

    print()
    print('## the fdm2-conf table | jig.towards_away on EMERGING values, exact gap, no tolerance')
    print('# `towards` means the line is AT its own rolling target-side extremum since the anchor')
    print('# `away` means the gap from that extremum is positive - FOR A SHORT, value minus the')
    print('# running minimum; FOR A LONG, the running maximum minus value')
    print('# the anchor is the incoming trade\'s open, or the re-entry window\'s open')
    print('# ex-20/80 stays on the chart-matched read, his standing rule for a fence')
    print()
    print('# every re-entry leg prints, whatever it realised - his 1104. an incoming-trade setup'
          ' prints when it realised at or under zero')
    print()
    print('| the signal bar | the setup | the incoming trade | the outgoing trade |'
          ' the outgoing realised % | the anchor | towards the incoming way, ws1-ws30 |'
          ' ex-20/80 the incoming way, ws1-ws30 |'
          ' towards the incoming way, ws25-ws30 | ex-20/80 the incoming way, ws25-ws30 |'
          ' towards the outgoing way, ws1-ws30 |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    for _i0, _L0 in enumerate(LG):
        _out_sd = int(_L0['side'])
        _src0 = str(_L0['src'])
        if not _src0.startswith('fdm re-entry') and float(_L0['rel']) > 0:
            continue
        if _src0.startswith('fdm re-entry'):
            _setup, _in_sd = 're-entry based', _out_sd
            _wo = [g for g in SIGS if SG.fire_bar(g) == int(_L0['opn'])]
            _anchor = int(_wo[0]['src']) if _wo else int(_L0['opn'])
            _sig0 = int(_wo[0]['bar']) if _wo else int(_L0['opn'])
            _in_nm = 'none - a re-entry'
        elif _i0 > 0:
            _setup, _in_sd = 'incoming trade based', -_out_sd
            _anchor = int(LG[_i0 - 1]['opn'])
            _pr0 = [r for r in LG[_i0 - 1]['rows'] if r['stage'] == 'REV-TRADE']
            _sig0 = int(_pr0[-1]['bar']) if _pr0 else int(_L0['opn']) - 2
            _in_nm = 'LONG' if _in_sd > 0 else 'SHORT'
        else:
            continue
        _ib = _band(1, int(LN['HI']), _anchor, _sig0, _in_sd)
        _i25 = _band(25, int(LN['HI']), _anchor, _sig0, _in_sd)
        _ob = _band(1, int(LN['HI']), _anchor, _sig0, _out_sd)
        print('| %s | %s | %s | %s | %+.3f | %s | %d of %d | %d of %d |'
              ' %d of %d | %d of %d | %d of %d |'
              % (ln.U(_sig0), _setup, _in_nm, 'LONG' if _out_sd > 0 else 'SHORT', _L0['rel'],
                 ln.U(_anchor), _ib[0], _ib[2], _ib[1], _ib[2],
                 _i25[0], _i25[2], _i25[1], _i25[2], _ob[0], _ob[2]))


#   ── W_FDM2_WS5REV='<from> .. <to>': the banked re-entry's own trace ────────────────────────────
#   THE MECH LIVES IN v4_fdm_reentry.signals, banked 1104. This arm REPORTS it and computes
#   nothing: the second implementation that used to live here is exactly how the 1841 three-row
#   defect got in, and his own rule is one driver per state.
#   EVERY COLUMN COMES OFF THE SIGNAL DICT the mech hands back.
_W5 = os.environ.get('W_FDM2_WS5REV')
if _W5:
    import v4_sweep_pivots as SP
    if _W5 != 'on':
        _w5d = [x.strip() for x in _W5.split('..')] if '..' in _W5 else [_W5.strip()] * 2
        _W5A, _W5B = ln.K(_w5d[0] + ' 00:00:00'), ln.K(_w5d[1] + ' 23:59:55')
    else:
        _W5A, _W5B = (A, B) if DAY else (0, len(LN['close']) - 1)
    _w5cl = np.asarray(LN['close'], float)
    _w5sig = [g for g in RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'])
              if _W5A <= int(g['bar']) <= _W5B]
    print()
    print('## the banked re-entry | the ws5/ws6 reversal walk | %s .. %s'
          % (ln.U(_W5A), ln.U(_W5B)))
    print('# the window is arm E: ws1b oob AND gcws30b ex-%g/%g, same side, paired with its own'
          ' ws1b ib close' % K.fnc_pair(K.FDM_RE_B_FNC))
    print('# the reversal read is %s, the ws6r gate is %s, the ws5r fence is %g/%g, the scan band'
          ' is ws%d..ws%d, the ib close is %s the last-to-fire set'
          % (K.FDM_RE_REV_READ, K.FDM_RE_WS6_GATE, *K.fnc_pair(K.FDM_RE_WS5_FNC),
             int(K.FDM_RE_SCAN_LO), int(K.FDM_RE_SCAN_HI),
             'IN' if int(K.FDM_RE_FIRE_IB) else 'OUT of'))
    print('# the open is the signal bar + 1, the router\'s "just OPEN, 1 bar"')
    print('# NO STOP AND NO EXIT RULE ON THESE NUMBERS: the scale is sweep-pivots, from the open')
    print('# sweep-pivots: ' + ', '.join('%s %s' % (n, v) for n, v, _ in SP.knobs()))
    print()
    print('| the window open | the oob side | the window close, ws1b ib | the ws5 reversal |'
          ' ws5r there | ws6r there | the ws6 branch | the ws6 reversal | the scan bar |'
          ' in-fence ws%d..ws%d | the last to fire | the signal bar | the trade | its open |'
          ' MAE %% | MFE %% | the scale TF | the leg close | the leg MFE %% |'
          % (int(K.FDM_RE_SCAN_LO), int(K.FDM_RE_SCAN_HI)))
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    _W5MAE, _W5MFE, _W5LEG, _W5REL, _W5D = [], [], [], [], {}
    for _g5 in _w5sig:
        _sd5 = int(_g5['side'])
        _op5 = SG.fire_bar(_g5)
        _ts5 = SG.target_side(SG.direction(_sd5))
        _sw5 = SP.swing(int(_op5), _sd5, _w5cl) if _op5 < len(_w5cl) else None
        _mae5 = _mfe5 = None
        if _sw5 and _sw5.get('close') is not None:
            _z5 = int(_sw5['close'])
            _a5, _b5x = min(int(_op5), _z5), max(int(_op5), _z5)
            _sg5 = _w5cl[_a5:_b5x + 1]
            _pb5 = float(_w5cl[int(_op5)])
            if np.isfinite(_sg5).any():
                _up5 = (float(np.nanmax(_sg5)) - _pb5) / _pb5 * 100.0
                _dn5 = (float(np.nanmin(_sg5)) - _pb5) / _pb5 * 100.0
                _mfe5, _mae5 = (_up5, _dn5) if _ts5 > 0 else (-_dn5, -_up5)
                #   THE REALISED AT THE LEG'S OWN CLOSE, signed by the trade's side. It answers
                #   one question and only one: what the open would have made with NO rev-trade and
                #   NO stop, riding to the bar sweep-pivots ends the leg on. It is a REPORTING
                #   column - nothing in the mech reads it, and the leg close is a lookahead read
                #   that only scoring may touch.
                _rel5 = _ts5 * (float(_w5cl[_z5]) - _pb5) / _pb5 * 100.0
                _W5MAE.append(_mae5)
                _W5MFE.append(_mfe5)
                _W5LEG.append(float(_sw5['mfe_pct']))
                _W5REL.append(_rel5)
                _W5D.setdefault(int(_op5), (_mae5, _mfe5, float(_sw5['mfe_pct']), _rel5))
        print('| %s | %s | %s | %s | %.2f | %.2f | %s | %s | %s | %s | %s | %s | %s | %s | %s |'
              ' %s | %s | %s | %s |'
              % (ln.U(int(_g5['src'])), 'HIGH' if _sd5 > 0 else 'LOW', ln.U(int(_g5['close'])),
                 ln.U(int(_g5['b5'])), _g5['v5'], _g5['v6'],
                 'held, waited' if _g5['held6'] else 'failed, scanned at once',
                 '-' if _g5['b6'] is None else ln.U(int(_g5['b6'])), ln.U(int(_g5['scan'])),
                 ', '.join('ws%d' % t for t in _g5['got']), _g5['last'], ln.U(int(_g5['bar'])),
                 SG.direction(_sd5), ln.U(int(_op5)),
                 '-' if _mae5 is None else '%+.3f' % _mae5,
                 '-' if _mfe5 is None else '%+.3f' % _mfe5,
                 '-' if _sw5 is None else _sw5['tf'],
                 '-' if _sw5 is None or _sw5.get('close') is None else ln.U(int(_sw5['close'])),
                 '-' if _sw5 is None else '%.3f' % _sw5['mfe_pct']))
    _w5med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
    print()
    print('| the population | value |')
    print('|---|---|')
    print('| re-entry signals in the span | %d |' % len(_w5sig))
    print('| of those, HIGH oob | %d |' % sum(1 for g in _w5sig if int(g['side']) > 0))
    print('| of those, LOW oob | %d |' % sum(1 for g in _w5sig if int(g['side']) < 0))
    print('| distinct open bars | %d |' % len(_W5D))
    for _lb in ('the ws5 reversal', 'the ws6 reversal', 'the ws1b ib close'):
        print('| last to fire was %s | %d |' % (_lb, sum(1 for g in _w5sig if g['last'] == _lb)))
    print('| ws6r held the gate so the walk waited | %d |' % sum(1 for g in _w5sig if g['held6']))
    print('| ws6r failed the gate so the scan ran at once | %d |'
          % sum(1 for g in _w5sig if not g['held6']))
    _dm5 = sorted(_W5D.items())
    print()
    print('| the MAE/MFE per DISTINCT open, the open bar to the leg close | value |')
    print('|---|---|')
    print('| distinct opens scored | %d |' % len(_dm5))
    if _dm5:
        _m5 = [v[0] for _, v in _dm5]
        _f5 = [v[1] for _, v in _dm5]
        _l5 = [v[2] for _, v in _dm5]
        print('| sum MAE %% | %+.3f |' % sum(_m5))
        print('| sum MFE %% | %+.3f |' % sum(_f5))
        print('| median MAE %% | %+.3f |' % _w5med(_m5))
        print('| median MFE %% | %+.3f |' % _w5med(_f5))
        print('| worst MAE %% | %+.3f |' % min(_m5))
        print('| best MFE %% | %+.3f |' % max(_f5))
        print('| MFE > abs(MAE) | %d of %d |'
              % (sum(1 for m, f in zip(_m5, _f5) if f > abs(m)), len(_m5)))
        print('| MAE past -%.2f%%, the fdm2 stop - NOT applied here | %d of %d |'
              % (float(K.FDM_MAE_CAP), sum(1 for m in _m5 if m < -float(K.FDM_MAE_CAP)), len(_m5)))
        print('| median leg MFE %% | %.3f |' % _w5med(_l5))
        print('| the MFE as a share of the leg MFE, median of %d | %.1f%% |'
              % (len(_l5), 100.0 * _w5med([f / g for f, g in zip(_f5, _l5) if g > 0])))
        _r5v = [v[3] for _, v in _dm5]
        print('| the realised at the leg close, sum %% | %+.3f |' % sum(_r5v))
        print('| the realised at the leg close, per open %% | %+.4f |' % (sum(_r5v) / len(_r5v)))
        print('| the round trip it has to beat %% | %.4f |' % F2.DRAG_PCT)
        print('| opens whose realised cleared the round trip | %d of %d |'
              % (sum(1 for v in _r5v if v > F2.DRAG_PCT), len(_r5v)))
        print('| median realised %% | %+.3f |' % _w5med(_r5v))
    print('| the span | the open bar to the bar sweep-pivots ends the leg on - NOT a horizon'
          ' chosen here |')
