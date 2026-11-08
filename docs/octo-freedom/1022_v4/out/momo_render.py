"""ONE copy of every fdm2 debugging table. Imported by the live process AND by the one-shot runs.

HIS 1106: *"every single event cached in a table or memory, instead of re-deriving"*. The renderers
live here so the live process and a one-shot script cannot drift apart - a second copy of a report
is where two answers to the same question come from.

Every table follows his format: one record per row, markdown, timestamps carry the date, a figure
never sits in prose, and a per-row MAE/MFE table always carries its aggregate underneath.
"""
import hashlib
import sys

import bisect as _bisect
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K        # noqa: E402
import v4_fdm2 as F2        # noqa: E402
import v4_closed_prev as CP # noqa: E402
import ln                   # noqa: E402
import v4_sweep_pivots as SP # noqa: E402
from optimus9.analysis import jig as JIG   # noqa: E402


DRAG_PCT = 0.1975   # the round trip, percent of the open. ONE name, not fourteen literals: it was
#                     written as a bare number at fourteen sites in this file and any two of them
#                     could have drifted apart without a single test failing.
_C3R = {}      # ws3b and the ws1Mage lift-off sets, built once per import


def row(*c):
    return '| ' + ' | '.join(str(x) for x in c) + ' |'


def head(*c):
    return [row(*c), row(*(['---'] * len(c)))]


def knob_hash():
    """A hash over EVERY banked knob's live value. -> (the hash, the off-bank knobs).

    HIS STANDING RULE, applied to the cache: a knob that changes rows goes in the key. A cached
    event whose key does not carry the knobs that produced it is the fault that made a leg report
    replay the old arm after the arm changed.
    """
    items = sorted((n, str(getattr(K, n, None))) for n in K.RULED)
    h = hashlib.sha256('|'.join('%s=%s' % kv for kv in items).encode()).hexdigest()[:12]
    off = [n for n in K.RULED if str(getattr(K, n, None)) != str(K.RULED[n][0])]
    return h, sorted(off)


def stamp(LN):
    """The provenance block every answer carries. -> [str].

    The bar count is here because the tape silently resolves shorter outside its own directory, and
    the knob hash is here because a cached row without it cannot be told from a stale one.
    """
    h, off = knob_hash()
    out = ['| the provenance | value |', '|---|---|']
    out.append(row('the tape', '%d bars, %s .. %s'
                   % (len(LN['close']), ln.U(0), ln.U(len(LN['close']) - 1))))
    out.append(row('the knob hash', h + ' - over all %d banked knobs' % len(K.RULED)))
    out.append(row('knobs off the bank', ', '.join('%s = %s (banked %s)'
                                                   % (n, getattr(K, n), K.RULED[n][0])
                                                   for n in off) if off else 'none'))
    out.append(row('the bank check', 'RULED_OK %s' % K.RULED_OK))
    out.append(row('fdm2-momo', 'ON' if int(K.FDM2_MOMO_ON) else 'OFF'))
    #   THE STOP ROW NAMES THE CAP, NOT THE RULE IN USE. Every report that scores against a
    #   different stop says so in its own block; this row said *"carried by every number below"*
    #   while cad3r_scan was running his 1108 dynamic level, which is a label that misreports its
    #   own table. It now states the cap's value and nothing about what a given report used.
    out.append(row('FDM_MAE_CAP', '%.2f%% adverse from the open. Each report names the stop IT ran '
                                  'under in its own block' % float(K.FDM_MAE_CAP)))
    return out


def legs_table(LN, LG):
    """The day's legs, one row each, with the aggregate block under it. -> [str]."""
    out = head('the open', 'dir', 'target side', 'what opened it', 'the rev-trade signal',
               'the exit', 'the exit kind', 'held min', 'MAE %', 'MFE %', 'realised %')
    for L in LG:
        out.append(row(ln.U(int(L['opn'])), 'LONG' if int(L['side']) > 0 else 'SHORT',
                       'HIGH' if int(L['side']) > 0 else 'LOW', str(L['src']),
                       ln.U(int(L['sig'])) if L['sig'] is not None else 'none',
                       ln.U(int(L['exit'])), str(L['ctype']), '%.1f' % float(L['held_min']),
                       '%.3f' % abs(float(L['mae'])), '%+.3f' % float(L['mfe']),
                       '%+.3f' % float(L['rel'])))
    if not LG:
        return out
    mae = [abs(float(L['mae'])) for L in LG]
    mfe = [float(L['mfe']) for L in LG]
    rel = [float(L['rel']) for L in LG]
    rat = [f / m for f, m in zip(mfe, mae) if m > 0]
    out += ['', '| the aggregate | value |', '|---|---|']
    out.append(row('legs', len(LG)))
    out.append(row('legs that stopped', sum(1 for L in LG if 'STOP' in str(L['ctype']))))
    out.append(row('MAE %, median', '%.3f' % float(np.median(mae))))
    out.append(row('MAE %, total', '%.3f' % sum(mae)))
    out.append(row('MFE %, median', '%+.3f' % float(np.median(mfe))))
    out.append(row('MFE %, total', '%+.3f' % sum(mfe)))
    out.append(row('realised %, median', '%+.3f' % float(np.median(rel))))
    out.append(row('realised %, total', '%+.3f' % sum(rel)))
    out.append(row('MFE over MAE, median', '%.2f' % float(np.median(rat)) if rat else 'nan'))
    out.append(row('drag %', '-%.3f (%.4f%% round trip x %d legs)' % (DRAG_PCT * len(LG), DRAG_PCT, len(LG))))
    out.append(row('net %', '%+.3f' % (sum(rel) - DRAG_PCT * len(LG))))
    out.append(row('MFE captured', '%.1f%% of MFE' % (sum(rel) / sum(mfe) * 100.0)
                   if sum(mfe) else 'nan'))
    return out


def leg_table(LN, L, SIGS, drop_misses=True):
    """ONE leg's every timestamped event. -> [str].

    `drop_misses` is HIS 1106 *"without the ws1b "misses" rows"*. The leg's own decision rows never
    held a miss - those come from a separate cadence_events(trace=True) pass - so at True that pass
    is not run at all, which is also why this form is fast.
    """
    o, ex, sd = int(L['opn']), int(L['exit']), int(L['side'])
    op = float(LN['close'][o])
    out = ['| the leg | value |', '|---|---|']
    out.append(row('the open', '%s, %s, target side %s'
                   % (ln.U(o), 'LONG' if sd > 0 else 'SHORT', 'HIGH' if sd > 0 else 'LOW')))
    out.append(row('what opened it', str(L['src'])))
    out.append(row('the open price', '%.6f' % op))
    out.append(row('the exit', ln.U(ex)))
    out.append(row('the exit kind', str(L['ctype'])))
    out.append(row('the exit price', '%.6f' % float(LN['close'][ex])))
    out.append(row('held, min', '%.1f' % float(L['held_min'])))
    out.append(row('MAE %', '%.3f' % abs(float(L['mae']))))
    out.append(row('MFE %', '%+.3f' % float(L['mfe'])))
    out.append(row('realised %', '%+.3f' % float(L['rel'])))
    out.append(row('MFE over MAE', '%.2f' % (float(L['mfe']) / abs(float(L['mae'])))
                   if abs(float(L['mae'])) > 0 else 'nan'))
    out.append(row('the rev-trade signal', ln.U(int(L['sig'])) if L['sig'] is not None else 'none'))
    out.append(row('the OUTGOING trade it opens',
                   ('%s at the signal + 2 bars' % ('SHORT' if sd > 0 else 'LONG'))
                   if L['sig'] is not None else 'none - this leg did not rev-trade'))
    out.append(row('bars it lived', ex - o + 1))

    EV = []
    if SIGS is not None:
        for g in SIGS:
            if str(L['src']).startswith('fdm re-entry') and ln.U(int(g['bar'])) in str(L['src']):
                EV.append((int(g['bar']), 'RE-ENTRY SIGNAL',
                           'gcws30b window side %s. %s'
                           % ('HIGH' if int(g['side']) > 0 else 'LOW', str(g.get('why', '')))))
    EV.append((o, 'OPEN', '%s at %.6f, %s' % ('LONG' if sd > 0 else 'SHORT', op, L['src'])))
    for r in L['rows']:
        EV.append((int(r['bar']), str(r['stage']), str(r['why'])))
    #   HIS 1106: *"drop the mae and mfe events"*. The MAE BAR and MFE BAR rows are gone from the
    #   event list. Their VALUES stay in the leg's summary block above, which is where he has
    #   always read them; only the two timestamped rows are dropped.
    sb = F2.stop_bar(LN, o, ex, sd, float(K.FDM_MAE_CAP))
    if sb is not None:
        EV.append((int(sb), 'STOP BAR', 'the adverse excursion reached FDM_MAE_CAP %.2f%% here'
                   % float(K.FDM_MAE_CAP)))
    if L['sig'] is not None:
        EV.append((int(L['sig']), 'REV-TRADE SIGNAL', 'the router closes at signal + 1'))
    EV.append((ex, 'EXIT', '%s at %.6f, realised %+.3f%%'
               % (str(L['ctype']), float(LN['close'][ex]), float(L['rel']))))
    assert all(b <= ex for b, _, _ in EV), 'a leg event reads past the leg\'s own exit'
    #   HIS 1107: *"when a rev-trade event prints, add the trade direction (SHORT/LONG)"*. A
    #   rev-trade closes the incoming trade and opens the opposite, so BOTH directions are named -
    #   his own 1106 question was about the incoming one, and the outgoing one is what the router
    #   produces. Naming only one of them is the ambiguity he asked to be called out.
    inc = 'LONG' if sd > 0 else 'SHORT'
    outg = 'SHORT' if sd > 0 else 'LONG'
    tag = ' [closes the %s, opens a %s]' % (inc, outg)
    out += ['', '| the bar | min from the open | the event | what it says |', '|---|---|---|---|']
    for b, stage, why in sorted(EV, key=lambda z: (z[0], z[1])):
        out.append('| %s | %.1f | %s | %s |'
                   % (ln.U(int(b)), (int(b) - o) * 5 / 60.0, stage,
                      (why + (tag if 'rev_trade' in stage or 'REV-TRADE' in stage
                              else '')).replace('|', '\\|')))
    return out


def cadwalk_summary(TR):
    """Every cad walk in a trace, and what ended it. -> [str]."""
    W = {}
    for t in TR:
        W.setdefault(t['b0'], []).append(t)
    out = head('the cad walk starts', 'target side', 'bars read', 'bars `walk` vetoed',
               'bars the truncation test ran', 'the rev-trade bar', 's from the start',
               'which branch ended it')
    for b0 in sorted(W):
        rs = W[b0]
        vet = [r for r in rs if r['vetoed']]
        tst = [r for r in rs if r['tested']]
        pas = [r for r in rs if r['ok']]
        out.append(row(ln.U(b0), 'LOW' if rs[0]['side'] < 0 else 'HIGH', len(rs), len(vet),
                       len(tst), ln.U(pas[0]['bar']) if pas else 'no rev-trade',
                       pas[0]['since_s'] if pas else '-',
                       'NOT `passed` - no r was towards while ex-fence, so the rev-trade printed'
                       if pas else
                       ('fdm2-momo voted `walk` on every bar' if len(vet) == len(rs) else
                        '`passed` on every tested bar - an r stayed towards while ex-fence')))
    return out


def cadwalk_table(TR, b0):
    """One cad walk, bar by bar. -> [str]."""
    rs = [t for t in TR if t['b0'] == b0]
    pas = [r for r in rs if r['ok']]
    cap = int(K.FDM2_MOMO_MAX_TF) - int(K.FDM_STEP1_ABOVE_TF)
    full = int(K.L2_MOM_MAXTF) - int(K.FDM_STEP1_ABOVE_TF)
    #   THE COLUMN NAMES FOLLOW HIS 1106 SECOND RCA: there is ONE test now - is any r towards while
    #   ex-20/80-fence - so "which clause failed" became "which lines blocked it".
    out = ['', '| the bar | s in | the vote | r-pred of %d | Mage-x of %d | pinned of %d | '
           'fdm2-momo | the 4-pronged read | which lines printed `passed` |' % (cap, cap, full),
           '|---|---|---|---|---|---|---|---|---|']
    for r in rs:
        why = r['why']
        if not r['tested']:
            short = '-'
        elif ' ex-' in why and 'AND towards on ws' in why:
            short = why.split(' is ex-')[0].split(' are ex-')[0] + ' towards while ex-fence'
        else:
            short = why
        out.append('| %s | %d | %s | %s | %s | %s | %s | %s | %s |'
                   % (ln.U(r['bar']), r['since_s'],
                      '%d of 3' % r['votes'] if r['votes'] is not None else '-',
                      r['rpred'] if r['rpred'] is not None else '-',
                      r['mx'] if r['mx'] is not None else '-',
                      r['pin'] if r['pin'] is not None else '-',
                      'VETO' if r['vetoed'] else 'no verdict',
                      '-' if not r['tested'] else
                      ('**NOT `passed` - REV-TRADE**' if r['ok'] else '`passed` - walk on'),
                      short.replace('|', '\\|')))
    if pas:
        out += ['', row('the rev-trade bar', '%s, %d s into the cad walk'
                        % (ln.U(pas[0]['bar']), pas[0]['since_s']))]
    return out

def pct50_table(LN, side, opn, ev, s0, xb, which):
    """HIS ESTABLISHED 50% TEST TABLE, from his 1103 00:34 ask and the 01:24 census. -> [str].

    HIS ASK, verbatim: *"report the percentage of towards (at the cadence event) against the
    percentage of reversals (at the ws10x-cadence) --report in TF ranges to curtail the data, ie
    ws3 to ws9, ws10 to ws16, ws17 to ws23, ws24 to ws30"*.

    THE COLUMNS AND THE DENOMINATOR ARE THE ONES THAT TABLE ALREADY USED, found by searching the
    transcript rather than rebuilt - HIS 1107 *"you'll need to find the genesis of the mech in the
    transcript to find the correct report. if you can't find it, don't invent a new one without
    talking to me first"*. The denominator per range is the lines in it that printed ex-20/80 at
    least once inside the trade's span, and "ex" includes oob.

    EVERY FIGURE COMES FROM THE SAME PRODUCERS THE DECISION USES - population, towards and
    reversed_tfs - so the table and the verdict cannot disagree.
    """
    RANGES = ((3, 9), (10, 16), (17, 23), (24, 30))
    pop = F2.population(LN, side, opn, xb)
    rf = F2.rev_from(ev, s0)
    rev = set(F2.reversed_tfs(LN, side, pop, rf, xb))
    tw = {t for t in pop if F2.towards(LN['CPR'][t], t, int(ev), int(side))}
    out = ['| the census | value |', '|---|---|']
    out.append(row('the trade', '%s %s, %s'
                   % (ln.U(int(opn)), 'LONG' if int(side) > 0 else 'SHORT',
                      'high' if int(side) > 0 else 'low')))
    out.append(row('the cadence event', ln.U(int(ev))))
    out.append(row('the ws{TF}x-cadence', ln.U(int(xb))))
    out.append(row('the winner', str(which)))
    out.append(row('the reversal count starts at', '%s (FDM_REV_FROM %s)'
                   % (ln.U(int(rf)), K.FDM_REV_FROM)))
    out.append(row('the ex-fence population', '%d lines - the lines ex-%g/%g at least once in '
                                              '%s .. %s. "ex" includes oob'
                   % (len(pop), *K.fnc_pair(K.FDM_FNC_2080), ln.U(int(opn)), ln.U(int(xb)))))
    out.append(row('the thresholds', 'FDM_X10_TRADE_PCT %g%% to trade, FDM_X10_GRACE_PCT %g%% for '
                                     'the grace walk' % (float(K.FDM_X10_TRADE_PCT),
                                                         float(K.FDM_X10_GRACE_PCT))))
    out += ['', '| the trade | the cadence event | the ws{TF}x-cadence | the winner | the TF range '
            '| towards at the event | reversed by the ws{TF}x-cadence | the ex-fence population |',
            '|---|---|---|---|---|---|---|---|']
    for lo, hi in RANGES:
        sub = [t for t in pop if lo <= t <= hi]
        out.append(row('%s %s, %s' % (ln.U(int(opn)), 'LONG' if int(side) > 0 else 'SHORT',
                                      'high' if int(side) > 0 else 'low'),
                       ln.U(int(ev)), ln.U(int(xb)), str(which), 'ws%d to ws%d' % (lo, hi),
                       '%d of %d' % (len([t for t in sub if t in tw]), len(sub)),
                       '%d of %d' % (len([t for t in sub if t in rev]), len(sub)),
                       len(sub)))
    out.append(row('**the whole population**', ln.U(int(ev)), ln.U(int(xb)), str(which),
                   '**ws%d to ws%d**' % (min(pop) if pop else 0, max(pop) if pop else 0),
                   '**%d of %d**' % (len(tw), len(pop)),
                   '**%d of %d = %.1f%%**' % (len(rev), len(pop),
                                              (len(rev) / len(pop) * 100.0) if pop else 0.0),
                   '**%d**' % len(pop)))
    out += ['', '| the lines, one row each | in range | ex-fence population | towards at the event '
            '| reversed by the ws{TF}x-cadence |', '|---|---|---|---|---|']
    for t in range(int(K.FDM_POP_LO), int(LN['HI']) + 1):
        rg = next(('ws%d to ws%d' % (lo, hi) for lo, hi in RANGES if lo <= t <= hi), '-')
        out.append(row('ws%d' % t, rg, 'yes' if t in pop else 'NO',
                       'yes' if t in tw else ('.' if t in pop else '-'),
                       'YES' if t in rev else ('.' if t in pop else '-')))
    return out


def window_table(LN, side, A, B):
    """The RAW oob->ib crosses of ws1b and ws1r/ws2r/ws3r in a range, side-filtered. -> [str].

    HIS 1107: *"my eyes say that the 0232 LONG would be reversed at 0250. 0250 uses ws3r oob as a
    replacement for ws1b oob - this a mech that I speced in the last few weeks, but I might have
    overlooked banking it"*.

    IT BUILDS NO MECH. His fdm_spec_VERBATIM.md line 8 opens the cadence window on ws1r OR ws2r OR
    ws3r oob; the code opens it on ws1b's oob excursion, from his 1103 preamble. This read shows
    what each of those four lines actually did in the range, so the two openers can be compared on
    data instead of on either of our recollections.

    EVERY CROSS COMES FROM jig.oob_ib_cross AT xwob 1 - the raw first-ib bar, no hold - and the
    excursion's start is walked back from it while the line was still oob. Causal: nothing past the
    cross bar is read.
    """
    import numpy as _np
    lines = [('ws1b', LN['B1'])] + [('ws%dr' % t, LN['CPR'][t]) for t in (1, 2, 3)]
    out = ['| the read | value |', '|---|---|']
    out.append(row('the range', '%s .. %s' % (ln.U(int(A)), ln.U(int(B)))))
    out.append(row('the side', '%s - oob means %s' % ('HIGH' if int(side) > 0 else 'LOW',
                                                      'at or above %g' % K.OOB_HI if int(side) > 0
                                                      else 'at or below %g' % K.OOB_LO)))
    out.append(row('what opens the window today', "ws1b's oob excursion, his 1103 preamble"))
    out.append(row('what his verbatim spec opens it on',
                   'ws1r OR ws2r OR ws3r oob, and it closes when the LOWEST of those that is oob '
                   'crosses to ib while ws3Mage is ex-%g/%g' % K.fnc_pair(K.FDM_FNC_2080)))
    out += ['', '| the line | the excursion opens | the excursion closes, the first ib bar | '
            'bars oob | the side extreme in it | ws3Mage at the close | ws3Mage ex-%g/%g there |'
            % K.fnc_pair(K.FDM_FNC_2080), '|---|---|---|---|---|---|---|']
    m3 = _np.asarray(LN['CPM'][3], float)
    lo3, hi3 = K.fnc_pair(K.FDM_FNC_2080)
    rows_ = []
    for nm, ser in lines:
        v = _np.asarray(ser, float)
        oob = (v >= K.OOB_HI) if int(side) > 0 else (v <= K.OOB_LO)
        for c, cf, sd in JIG.oob_ib_cross(v, K.OOB_HI, K.OOB_LO, 1):
            if int(sd) != int(side) or not (int(A) <= int(c) <= int(B)):
                continue
            j = int(c) - 1
            if j < 0 or not oob[j]:
                continue
            s1 = j
            while s1 > 0 and oob[s1 - 1]:
                s1 -= 1
            seg = v[s1:int(c)]
            ext = float(_np.nanmax(seg)) if int(side) > 0 else float(_np.nanmin(seg))
            mv = float(m3[int(c)])
            exf = (mv >= hi3) if int(side) > 0 else (mv <= lo3)
            rows_.append((int(c), nm, s1, ext, mv, exf))
    for c, nm, s1, ext, mv, exf in sorted(rows_):
        out.append(row(nm, ln.U(s1), ln.U(c), c - s1, '%.2f' % ext, '%.2f' % mv,
                       'yes' if exf else 'NO'))
    if not rows_:
        out.append(row('none', '-', '-', '-', '-', '-', '-'))
    return out


def trail_table(LN, side, mark):
    """Every state change of ws1r, ws3r, ws3Mage, ws3b and ws1b around one of his markers. -> [str].

    HIS 1107 SPEC, five nested conditions ending in a rev-trade. This builds NO mech and decides
    nothing - it prints the raw crossings his five clauses read, on BOTH the closed-prev and the
    emerging read, so his spec lands on data instead of on either of our recollections.

    THE SPAN IS ANCHORED TO HIS OWN CLAUSE BOUNDARIES, not to a window I picked:
      it starts   at the most recent ws1r oob ENTRY at or before the marker - his clause 1 reads
                  ws1r up to its ib cross, so its oob entry is where the trail begins
      it ends     at the first ws3r cross to in-20/80-fence at or after the marker - his clause 4,
                  the last line of the chain before the verdict
    Both ends are events in his spec. Nothing is truncated to a length of mine.

    THE STATES PRINTED, per line, both reads:
      oob          at or past 15/85 on the side
      ex-fence     at or past 20/80 on the side
      past 50      the COUNTER side of 50 - his *"without printing lower than 50"* for a high-side
                   trajectory, and the inverse for a low-side one
    """
    import numpy as _np
    hi_oob, lo_oob = float(K.OOB_HI), float(K.OOB_LO)
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    mk = int(mark)
    sd = int(side)

    def oob_of(v):
        return (v >= hi_oob) if sd > 0 else (v <= lo_oob)

    def exf_of(v):
        return (v >= hi_f) if sd > 0 else (v <= lo_f)

    def past50_of(v):
        return (v < 50.0) if sd > 0 else (v > 50.0)

    #   ws3b IS HIS CLAUSE 3's SECOND LINE - *"IF ws3Mage or ws3b is past counter-side 50"* - and it
    #   is not in LN, so it comes off ln.line directly. ws1b is HIS CLAUSE 5's line and LN carries
    #   it as B1, closed-prev only.
    _w3b = _np.asarray(ln.line('ws3b'), float)
    _w3b_cp = _np.asarray(CP.series(_w3b, 3 * 60), float)
    SER = [('ws1r', _np.asarray(LN['CPR'][1], float), _np.asarray(LN['EMR'][1], float)),
           ('ws3r', _np.asarray(LN['CPR'][3], float), _np.asarray(LN['EMR'][3], float)),
           ('ws3Mage', _np.asarray(LN['CPM'][3], float), _np.asarray(LN['MGE'][3], float)),
           ('ws3b', _w3b_cp, _w3b),
           ('ws1b', _np.asarray(LN['B1'], float), _np.asarray(LN['B1'], float))]

    #   the span's start: the most recent ws1r oob ENTRY at or before the marker, closed-prev
    w1 = SER[0][1]
    o1 = oob_of(w1)
    a = mk
    while a > 0 and not o1[a]:
        a -= 1
    while a > 0 and o1[a - 1]:
        a -= 1
    #   the span's end: the first ws3r cross to in-fence at or after the marker, closed-prev
    w3 = SER[1][1]
    e3 = exf_of(w3)
    b = mk
    while b < len(w3) - 1 and e3[b]:
        b += 1
    b = min(b + 1, len(w3) - 1)

    out = ['| the trail | value |', '|---|---|']
    out.append(row('his marker', ln.U(mk)))
    out.append(row('the side', '%s' % ('HIGH' if sd > 0 else 'LOW')))
    out.append(row('the span', '%s .. %s - %d bars = %.1f min'
                   % (ln.U(a), ln.U(b), b - a + 1, (b - a + 1) * 5 / 60.0)))
    out.append(row('the span start', "the most recent ws1r oob entry at or before the marker, "
                                     "closed-prev - his clause 1"))
    out.append(row('the span end', 'the first ws3r cross to in-%g/%g at or after the marker, '
                                   'closed-prev - his clause 4' % (lo_f, hi_f)))
    out.append(row('oob', 'at or past %g/%g on the side' % (lo_oob, hi_oob)))
    out.append(row('ex-fence', 'at or past %g/%g on the side' % (lo_f, hi_f)))
    out.append(row('past 50', 'the COUNTER side of 50 - %s 50 for this %s-side trail'
                   % ('below' if sd > 0 else 'above', 'high' if sd > 0 else 'low')))

    EV = []
    for nm, cp, em in SER:
        for lab, v in (('closed-prev', cp), ('emerging', em)):
            if nm == 'ws1b' and lab == 'emerging':
                continue
            for tag, fn in (('oob', oob_of), ('ex-fence', exf_of), ('past 50', past50_of)):
                st = fn(v)
                for i in range(max(a, 1), b + 1):
                    if bool(st[i]) != bool(st[i - 1]):
                        EV.append((i, nm, lab, tag, 'ENTERS' if st[i] else 'leaves',
                                   float(v[i])))
    out += ['', '| the bar | min from the marker | the line | the read | the state | in or out | '
            'its value |', '|---|---|---|---|---|---|---|']
    for i, nm, lab, tag, io, val in sorted(EV, key=lambda z: (z[0], z[1], z[2], z[3])):
        out.append(row(ln.U(i), '%+.1f' % ((i - mk) * 5 / 60.0), nm, lab, tag, io,
                       '%.2f' % val))
    if not EV:
        out.append(row('none', '-', '-', '-', '-', '-', '-'))

    out += ['', '| the line | the read | at his marker | oob there | ex-fence there | past 50 there |',
            '|---|---|---|---|---|---|']
    for nm, cp, em in SER:
        for lab, v in (('closed-prev', cp), ('emerging', em)):
            if nm == 'ws1b' and lab == 'emerging':
                continue
            out.append(row(nm, lab, '%.2f' % float(v[mk]),
                           'yes' if oob_of(v[mk]) else 'NO',
                           'yes' if exf_of(v[mk]) else 'NO',
                           'yes' if past50_of(v[mk]) else 'NO'))
    return out


def cad3r_eval(LN, side, mark, lab):
    """`fdm2-3r-cadence` - HIS NAME. The five clauses at one arm, on one read. -> dict.

    THE ONE EVALUATOR. The single-marker report and the multi-day scan both call this, so the two
    can never disagree about what fired - a second copy of a five-clause chain is exactly where two
    answers to one question come from.

    HIS RULINGS, every one of them:
      clause 1, "matching"      *"both lines read towards the same side"*
      clause 1, where it starts *"ws1r's oob entry... this makes the "ws1r's oob entry." test a
                                one-time-only test"*
      clause 2, where it arms   *"ws3r's first print on the target side of 50 after ws1r's
                                target-side oob entry"*
      clause 2, how many        *"one return is enough to trigger unstable"*
      clause 3, which bar       *"the full TF bar before the cross to infence"*
      clause 4's branch B       *"ws1Mage is same-side oob and reversing while ws3r is oob, and
                                ws4r is infence"*, with *"ws1Mge reversal is lift-off driven"*
      branch B's anchors        *"the branch-B bar replaces the cross"* for clauses 3 and 5 alike
      clause 5, "ws1r reversal" *"same event: ws1r to ib"*
      clause 6, "ELSE stop"     *"the outcomes are either rev-trade, or kill (stop) the 3r-cadence
                                mech"* - the TRADE is untouched
      the read                  *"I want to know both"*, and his 1108 *"if we make ws3r emerging
                                for this c3r mech"*

    `lab` picks the read: 'closed-prev', 'emerging', or 'ws3r emerging, rest closed-prev'.

    TWO THINGS STAY MINE AND SAY SO IN THE RESULT:
      clause 3's bar        the complete ws3 closed-prev bar - 3 min = 36 bars - ending at the last
                            ws3 seam at or before the clause-4 bar
      branch B's firing bar the lift-off STAMP, not the lift bar. The lift bar is not knowable at
                            the lift bar, and K.lift_stamp is the one home for that offset

    CAUSAL: every read is at its own bar or earlier, and the assert carries the bar order.
    """
    import numpy as _np
    sd = int(side)
    hi_oob, lo_oob = float(K.OOB_HI), float(K.OOB_LO)
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    mk = int(mark)
    emx = lab == 'emerging'
    em3 = lab != 'closed-prev'
    r1 = _np.asarray(LN['EMR'][1] if emx else LN['CPR'][1], float)
    r3 = _np.asarray(LN['EMR'][3] if em3 else LN['CPR'][3], float)
    m3 = _np.asarray(LN['MGE'][3] if emx else LN['CPM'][3], float)
    #   ws3b AND ws1Mage's LIFT-OFF SET ARE BUILT ONCE, not per arm. My first draft called
    #   ln.line('ws3b') and JIG.lift_off on every call, which turned a 7-day scan of ~200 arms into
    #   200 whole-tape builds. _C3R is cleared by a reload because the module is re-imported.
    if 'ws3b' not in _C3R:
        _C3R['ws3b'] = _np.asarray(ln.line('ws3b'), float)
        _C3R['ws3b_cp'] = _np.asarray(CP.series(_C3R['ws3b'], 3 * 60), float)
    if ('lift_m1', sd) not in _C3R:
        _C3R[('lift_m1', sd)] = set(
            K.lift_stamp(int(x)) for x in
            JIG.lift_off(_np.asarray(LN['MGE'][1], float), sd, K.LIFT_PTS, K.gap_for(1),
                         K.LIFT_TOL, K.LIFT_WOB))
    b3 = _C3R['ws3b'] if emx else _C3R['ws3b_cp']
    b1 = _np.asarray(LN['B1'], float)
    m1 = _np.asarray(LN['MGE'][1] if emx else LN['CPM'][1], float)
    r4 = _np.asarray(LN['EMR'][4] if emx else LN['CPR'][4], float)
    lift_m1 = _C3R[('lift_m1', sd)]

    def oob(v):
        return (v >= hi_oob) if sd > 0 else (v <= lo_oob)

    def exf(v):
        return (v >= hi_f) if sd > 0 else (v <= lo_f)

    def p50(v):
        return (v < 50.0) if sd > 0 else (v > 50.0)

    R = dict(read=lab, side=sd, mark=mk, kill=None, arm=None, oob1=None, ib1=None, oob3=None,
             x4=None, branch=None, c3_bar=None, c3_mage=None, c3_b=None, c5_ext=None,
             c5_oob=None, c5_exf=None, ret=None, dwell=None, fires=False, why={})

    o1 = oob(r1)
    a = mk
    while a > 0 and not o1[a]:
        a -= 1
    while a > 0 and o1[a - 1]:
        a -= 1
    if not o1[a]:
        R['kill'] = '1'
        R['why']['1'] = 'no ws1r oob entry at or before the marker'
        return R
    R['oob1'] = a
    t1 = F2.towards(r1, 1, a, sd)
    t3 = F2.towards(r3, 3, a, sd)
    R['why']['1'] = ('ws1r oob entry at %.2f. towards at that bar - ws1r %s, ws3r %s'
                     % (r1[a], 'yes' if t1 else 'NO', 'yes' if t3 else 'NO'))
    if not (t1 and t3):
        R['kill'] = '1'
        return R
    i = a
    while i < len(r1) - 1 and o1[i]:
        i += 1
    R['ib1'] = i
    R['why']['1 end'] = 'ws1r crosses to ib at %.2f' % r1[i]
    o3, p3 = oob(r3), p50(r3)
    arm = None
    for q in range(a, len(r3)):
        if not p3[q]:
            arm = q
            break
        if o3[q]:
            break
    R['arm'] = arm
    R['why']['2 arm'] = ('ws3r prints on the target side of 50 at %.2f' % r3[arm]
                         if arm is not None else
                         'ws3r never printed on the target side of 50 - the test stays unarmed')
    j, bad = i, None
    while j < len(r3) - 1 and not o3[j]:
        if arm is not None and j >= arm and p3[j] and bad is None:
            bad = j
        j += 1
    if not o3[j]:
        R['kill'] = '2'
        R['why']['2'] = 'ws3r does not reach oob after %s' % ln.U(i)
        return R
    if bad is not None:
        R['kill'] = '2'
        R['ret'] = bad
        R['why']['2'] = ('ws3r RETURNED past counter-side 50 at %.2f, after arming at %s, before '
                         'reaching oob' % (r3[bad], ln.U(arm)))
        return R
    R['oob3'] = j
    R['why']['2'] = 'ws3r reaches oob at %.2f with no RETURN past counter-side 50' % r3[j]
    e3, o3b, o1m = exf(r3), oob(r3), oob(m1)
    inf4 = ~exf(r4)
    k = j
    while k < len(r3) - 1:
        if not e3[k]:
            R['x4'], R['branch'] = k, 'A'
            break
        if k in lift_m1 and o1m[k] and o3b[k] and inf4[k]:
            R['x4'], R['branch'] = k, 'B'
            break
        k += 1
    if R['x4'] is None:
        R['kill'] = '4'
        R['why']['4'] = 'neither branch fired before the tape ends'
        return R
    x4 = R['x4']
    #   HIS 1108 ws3r MINIMUM DWELL: *"ws3r minimum dwell should be 3 minutes"*, `FDM2_C3R_DWELL`
    #   36 bars = 180 s. THE SPAN IS MINE AND STATED: the run of CONSECUTIVE oob bars that starts
    #   at `oob3`, counted forward and stopped at the clause-4 bar. Branch B is still oob at x4 so
    #   its run is the whole window; branch A's run ends where ws3r left oob. Reading forward from
    #   oob3 to x4 only touches bars at or before x4, so the gate is knowable AT x4 and nowhere
    #   earlier - a run that would reach 36 bars after x4 does not count, because at x4 it had not.
    dw, t = 0, R['oob3']
    while t <= x4 and o3b[t]:
        dw += 1
        t += 1
    R['dwell'] = dw
    R['why']['dwell'] = ("ws3r's consecutive oob run from %s is %d bars = %d s, against the %d bar "
                         '= %d s minimum' % (ln.U(R['oob3']), dw, dw * 5, int(K.FDM2_C3R_DWELL),
                                             int(K.FDM2_C3R_DWELL) * 5))
    if dw < int(K.FDM2_C3R_DWELL):
        R['kill'] = 'dwell'
        return R
    R['why']['4'] = ('ws3r crosses to in-%g/%g at %.2f' % (lo_f, hi_f, r3[x4])
                     if R['branch'] == 'A' else
                     ('ws1Mage lift-off STAMP here, ws1Mage %.2f oob, ws3r %.2f still oob, ws4r '
                      '%.2f in-%g/%g. The lift bar was %s'
                      % (m1[x4], r3[x4], r4[x4], lo_f, hi_f,
                         ln.U(x4 - (int(K.LIFT_WOB) - 1)))))
    span = 3 * 60 // 5
    seam = (x4 // span) * span - 1
    s_a = max(0, seam - span + 1)
    mv = float(m3[seam]) if not emx else (float(_np.nanmin(m3[s_a:seam + 1])) if sd > 0
                                          else float(_np.nanmax(m3[s_a:seam + 1])))
    bv = float(b3[seam]) if not emx else (float(_np.nanmin(b3[s_a:seam + 1])) if sd > 0
                                          else float(_np.nanmax(b3[s_a:seam + 1])))
    R['c3_bar'], R['c3_mage'], R['c3_b'] = seam, mv, bv
    R['why']['3'] = ('the full ws3 bar %s .. %s - ws3Mage %.2f, ws3b %.2f. past counter-side 50 - '
                     'ws3Mage %s, ws3b %s. THE BAR CHOICE IS MINE'
                     % (ln.U(s_a), ln.U(seam), mv, bv,
                        'yes' if p50(mv) else 'NO', 'yes' if p50(bv) else 'NO'))
    if not (p50(mv) or p50(bv)):
        R['kill'] = '3'
        return R
    seg = b1[i:x4 + 1]
    ext = float(_np.nanmax(seg)) if sd > 0 else float(_np.nanmin(seg))
    R['c5_ext'] = ext
    R['c5_oob'] = bool(oob(_np.array([ext]))[0])
    R['c5_exf'] = bool(exf(_np.array([ext]))[0])
    R['why']['5'] = ("ws1b's %s print in the window is %.2f. same-side oob at %g - %s. ex-fence at "
                     '%g - %s'
                     % ('highest' if sd > 0 else 'lowest', ext, hi_oob if sd > 0 else lo_oob,
                        'REACHED' if R['c5_oob'] else 'not reached', hi_f if sd > 0 else lo_f,
                        'REACHED' if R['c5_exf'] else 'not reached'))
    R['fires'] = not R['c5_oob']
    if not R['fires']:
        R['kill'] = '5'
    assert R['x4'] >= R['oob3'] >= R['ib1'] >= R['oob1'], 'the clause bars are out of order'
    return R


def pivstop_table(LN, A, B, lab='ws3r emerging, rest closed-prev', gaps=(24, 48, 60)):
    """The stop level from HIS walk-back-to-look-forward mech, per c3r firing. -> the markdown.

    HIS 1108: *"if you're using sweep pivots to find it, it won't show up. to find the 'last
    pivot', it will need to be handled manually: use the 'walk back to look forward' mech"*.

    SO THE PRODUCER IS `jig.mage_cascade_bar(line, bar, side, mode='extrema', gap=...)`. My first
    build used the percentage zigzag in optimus9/compute/swing_detect.py, and at every scale I
    read it the 0724 HIGH came back 0.325%, 2.283% or 5.055% - never his 1.9%. That read is
    withdrawn for this purpose.

    HIS MECH, 1017, quoted in the jig: *"to find the extrema, look back from the event bar in 4
    minute gaps until you see an extrema, then step back another 4 minutes to validate the
    extrema"*, and *"the whole point of walking back to look forward for the extrema is to confirm
    the only extrema it can see"*. The coarse walk back finds a sample bar; the level is the
    series' true extreme FORWARD of it, bounded by the event bar.

    THE LINE IS pxs. His own docstring: *"the extrema source on the 5 s grid. ws1Mage today ...
    The TF is the CALLER'S"*. The caller hands it a series, so price is admissible, and pxs is the
    series his 1108 stop ruling put the stop on.

    THE SIDE IS THE c3r ARM'S SIDE. His rule: *"extrema must be same-side as the event's side
    (not the events' SHORT or LONG verdict)"*. A HIGH-side arm opens a SHORT, whose stop sits
    above the last HIGH extreme, so the level side and the arm side are the same number.

    sample_bars IS NONE. That argument exists for a closed-prev series, which is flat between its
    seams; pxs carries its own value on every 5 s bar, so every bar is a candidate.

    THE GAPS SWEPT ARE ALL HIS OWN NUMBERS, not a spread of mine: 24 bars = 2 min from *"walk
    backwards in 2 minute gaps to look forward for the counter-side extrema"*, 48 bars = 4 min =
    `MC_GAP` from *"look back from the event bar in 4 minute gaps"*, 60 bars = 5 min from *"at
    trade open, walkback in 5 minute jumps"*.

    THE BUFFER IS 0.00%. The sixteen sources read on 1108 give 0.5%..1.0%, $0.10..$0.50 or
    0.5x..3.5x ATR and agree on nothing, and HE HAS NOT RULED ONE. The raw structural distance
    prints so he can pick a buffer from the distribution.

    THE OUTCOME COLUMNS GO THROUGH F2.stop_bar, his own stop walk, with the structural distance
    handed in as the cap. Nothing else about the scoring changes.
    """
    import numpy as _np
    import sys as _sys
    if '/home/joe/thecodes' not in _sys.path:
        _sys.path.insert(0, '/home/joe/thecodes')
    from optimus9.analysis import jig as _jig
    close = _np.asarray(LN['close'], float)
    _, fired = cad3r_arms(LN, A, B, lab)
    #   ONE ROW PER DISTINCT FIRING BAR AND SIDE. Several ws1r oob entry arms converge on one
    #   firing bar and produce byte-identical rows; a per-signal stop read has one record per
    #   signal. The 64-row-per-arm count stays in cad3r_scan, unchanged.
    sigs = {}
    for q, sd, E in fired:
        sigs.setdefault((int(E['x4']), int(sd)), E)
    keys = sorted(sigs)
    out = ['| the read | value |', '|---|---|']
    out.append(row('the firings read', '%d distinct firing bars, from %d arms that fired'
                   % (len(keys), len(fired))))
    out.append(row('the producer', "`jig.mage_cascade_bar(pxs, the open bar, the arm's side, "
                                   "mode='extrema', gap=...)` - HIS walk back to look forward"))
    out.append(row('the level', "the extreme FORWARD of the coarse sample bar, bounded by the "
                                'open bar. One extrema, not many'))
    out.append(row('the side', "the c3r arm's own side, his *extrema must be same-side as the "
                               "event's side* rule"))
    out.append(row('the price series', 'pxs = DEMA(close, 2) on the 5 s grid, his 1108 ruling'))
    out.append(row('the sampling', 'every 5 s bar - `sample_bars` is for a closed-prev series, '
                                   'and pxs is not one'))
    out.append(row('the walk', 'UNBOUNDED back, his standing rule. No cap'))
    out.append(row('the buffer', '0.00% - the sixteen sources agree on nothing and HE HAS NOT '
                                 'RULED ONE'))
    out.append(row('the stop walk', 'F2.stop_bar, unchanged, with the structural distance handed '
                                    'in as the cap'))
    out.append(row('the gaps swept', ', '.join('%d bars = %d min' % (g, g * 5 // 60) for g in gaps)
                   + ' - EVERY ONE IS HIS OWN NUMBER'))
    #   HIS 1108: *"isn't one of the points of sweep-pivots is to print the MFE based on the next
    #   pivot after a signal opens?"*. It is, and this table never called it. The MFE columns above
    #   are the excursion across my own hold-to-the-stop span, which is not a swing at all.
    #   sweep-pivots bounds the leg with a Mage oob->ib cross and sets the swing scale from which
    #   TF's pivot marks the event, so its mfe_pct is the number he is asking for.
    for nm, val, why in SP.knobs():
        out.append(row('sweep-pivots `%s`' % nm, '%s - %s' % (val, why)))

    def score(opn, osd, capd):
        sb = F2.stop_bar(LN, opn, int(B), osd, capd)
        ex = int(sb) if sb is not None else int(B)
        op = float(close[opn])
        pp = osd * (_np.asarray(close[opn:ex + 1], float) - op) / op * 100.0
        return dict(ex=ex, sb=sb, mae=abs(float(_np.nanmin(pp))), mfe=float(_np.nanmax(pp)),
                    rel=-capd if sb is not None else osd * (float(close[ex]) - op) / op * 100.0)

    DEF = 48 if 48 in gaps else gaps[0]
    out += ['', '## the structural stop per signal, gap %d bars = %d min' % (DEF, DEF * 5 // 60), '']
    out += head('the firing bar', 'the side it fired on', 'the OUTGOING trade', 'it opens at',
                'the open price', 'the extrema bar', 'bars back', 'the extrema price',
                'the stop distance %', 'the exit', 'the exit kind', 'held min', 'MAE %',
                'MFE % - MY hold-to-the-stop span', 'realised %',
                'sweep-pivots marking TF', 'sweep-pivots leg opened at',
                'sweep-pivots leg closed at', 'sweep-pivots pivot bar',
                'sweep-pivots mfe_pct - THE SWING MFE', 'sweep-pivots given_pct',
                'sweep-pivots share', 'why the coarse walk stopped there')
    agg = {g: [] for g in gaps}
    for (x4, sd) in keys:
        opn = int(x4) + 2
        osd = -int(sd)
        if opn > int(B):
            continue
        op = float(close[opn])
        for g in gaps:
            W = SP.swing(opn, int(sd), close) if g == DEF else None
            sp = (['-'] * 7 if W is None else
                  [W['tf'], ln.U(int(W['open'])), ln.U(int(W['close'])), ln.U(int(W['pivot'])),
                   '%+.3f' % W['mfe_pct'], '%+.3f' % W['given_pct'],
                   '%.2f' % W['share'] if W['share'] is not None else 'nan'])
            M = _jig.mage_cascade_bar(close, opn, int(sd), mode='extrema', gap=int(g))
            if M is None:
                agg[g].append(None)
                if g == DEF:
                    out.append(row(ln.U(x4), 'HIGH' if sd > 0 else 'LOW',
                                   'SHORT' if osd < 0 else 'LONG', ln.U(opn), '%.6f' % op,
                                   'none', '-', '-', 'no same-side extrema back to the tape start',
                                   '-', '-', '-', '-', '-', '-', *sp, '-'))
                continue
            k, why = M
            lv = float(close[int(k)])
            d = -osd * (lv - op) / op * 100.0        # positive when the level sits adverse
            if d <= 0:
                agg[g].append(None)
                if g == DEF:
                    out.append(row(ln.U(x4), 'HIGH' if sd > 0 else 'LOW',
                                   'SHORT' if osd < 0 else 'LONG', ln.U(opn), '%.6f' % op,
                                   ln.U(int(k)), opn - int(k), '%.6f' % lv,
                                   'the extrema is already favourable', '-', '-', '-', '-', '-',
                                   '-', *sp, why))
                continue
            S = score(opn, osd, d)
            agg[g].append(dict(d=d, **S))
            if g == DEF:
                out.append(row(ln.U(x4), 'HIGH' if sd > 0 else 'LOW',
                               'SHORT' if osd < 0 else 'LONG', ln.U(opn), '%.6f' % op,
                               ln.U(int(k)), opn - int(k), '%.6f' % lv, '%.3f' % d,
                               ln.U(S['ex']),
                               'STOP at %.3f%%' % d if S['sb'] is not None
                               else 'still open at the span end',
                               '%.1f' % ((S['ex'] - opn) * 5 / 60.0), '%.3f' % S['mae'],
                               '%+.3f' % S['mfe'], '%+.3f' % S['rel'], *sp, why))

    out += ['', '## the gap curve, every gap on the same signals', '']
    out += head('the gap, bars', 'the gap, min', 'signals with an adverse extrema',
                'signals whose extrema is already FAVOURABLE, so there is no stop level',
                'the stop distance %, median', 'the stop distance %, min',
                'the stop distance %, max', 'that stopped', 'still open at the span end',
                'realised %, total - RESOLVED ROWS ONLY', 'drag % - resolved rows',
                'net % - RESOLVED ROWS ONLY', 'realised %, total - every row',
                'net % - every row')
    for g in gaps:
        grp = [x for x in agg[g] if x]
        n = len(grp)
        if not n:
            out.append(row(g, g * 5 // 60, 0, len(agg[g]), *['-'] * 10))
            continue
        d = sorted(x['d'] for x in grp)
        res = [x for x in grp if x['sb'] is not None]
        tr = sum(x['rel'] for x in res)
        ta = sum(x['rel'] for x in grp)
        out.append(row(g, g * 5 // 60, n, len(agg[g]) - n,
                       '%.3f' % float(_np.median(d)), '%.3f' % d[0], '%.3f' % d[-1],
                       len(res), n - len(res),
                       '%+.3f' % tr, '%.3f' % (-DRAG_PCT * len(res)),
                       '%+.3f' % (tr - DRAG_PCT * len(res)),
                       '%+.3f' % ta, '%+.3f' % (ta - DRAG_PCT * n)))
    return out


def legmfe_table(LN, A, B, tfs=('ws1Mage', 'ws2Mage', 'ws3Mage', 'gcws30Mage'),
                 win_h=8.0, step_h=1.0):
    """How much each Mage's legs travel, over a rolling window. -> the markdown.

    HIS 1108: *"the stop loss needs to be larger when the swings are producing more profit between
    pivots"*, then *"before I invent something new, can you derive that from sweep-pivots? using a
    rolling 8 hour window, and measuring on TF1,2,3 and gcws30 timeframes, what MFE differences
    can you detect inside of 08-08 to 08-30?"*.

    THE LEG IS sweep-pivots' OWN. `SP.legs(name)` brackets a leg with that Mage's consecutive
    opposite-side oob->ib crosses - no pct and no horizon, which is the whole reason that module
    exists. A leg's MFE is the favourable travel from its own extremum to its end, which is his
    *"profit between pivots"*.

    CAUSALITY. A leg is knowable only once its CLOSING cross has confirmed, at close + SP_XWOB - 1.
    Each window therefore counts only the legs confirmed at or before its own right edge, so every
    number is one a reader at that bar could have had. No leg still running is counted.

    THE WINDOW IS HIS - 8 hours. THE STEP IS MINE and stated: %g h, so consecutive windows overlap
    rather than tile. Changing it changes how many windows print and nothing about a leg.
    """ % step_h
    import numpy as _np
    close = _np.asarray(LN['close'], float)
    W = int(round(float(win_h) * 3600 / 5))
    ST = int(round(float(step_h) * 3600 / 5))
    out = ['| the read | value |', '|---|---|']
    out.append(row('the leg', "sweep-pivots' own: a Mage oob->ib cross to its next OPPOSITE-side "
                              'cross of the same line'))
    out.append(row("the leg's MFE", 'the favourable travel from the leg\'s own extremum to its '
                                    'end, in percent of that extremum - HIS *"profit between '
                                    'pivots"*'))
    out.append(row('the window', '%g h = %d bars - HIS NUMBER' % (float(win_h), W)))
    out.append(row('the step', '%g h = %d bars - MINE, stated' % (float(step_h), ST)))
    out.append(row('what a window counts', 'every leg whose CLOSING cross confirmed inside it. '
                                           'Confirm is close + SP_XWOB %d - 1 bars, so nothing '
                                           'unknowable at the right edge is counted'
                   % int(K.SP_XWOB)))
    out.append(row('the span', '%s .. %s' % (ln.U(int(A)), ln.U(int(B)))))
    out.append(row('the price series', 'pxs = DEMA(close, 2) on the 5 s grid'))

    xw = int(K.SP_XWOB)
    LEG = {}
    for tf in tfs:
        rows = []
        for o, z, sd in SP.legs(tf):
            if z + xw - 1 > int(B) or o < 0:
                continue
            seg = close[int(o):int(z) + 1]
            if not _np.isfinite(seg).any():
                continue
            fav = -int(sd)                      # a LOW-opened leg rises off its low
            p0 = float(_np.nanmin(seg)) if fav > 0 else float(_np.nanmax(seg))
            ext = float(_np.nanmax(seg)) if fav > 0 else float(_np.nanmin(seg))
            if p0 <= 0:
                continue
            rows.append((int(z) + xw - 1, abs(ext - p0) / p0 * 100.0, int(z) - int(o)))
        rows.sort()
        LEG[tf] = rows

    out += ['', '## every leg, per timeframe, across the whole span', '']
    out += head('the timeframe', 'legs confirmed in the span', "the leg's MFE %, min",
                "the leg's MFE %, median", "the leg's MFE %, max",
                'the leg length, min - median', 'the leg length, min - max')
    for tf in tfs:
        r = [x for x in LEG[tf] if int(A) <= x[0] <= int(B)]
        if not r:
            out.append(row(tf, 0, *['-'] * 5))
            continue
        m = sorted(x[1] for x in r)
        L = sorted(x[2] * 5 / 60.0 for x in r)
        out.append(row(tf, len(r), '%.3f' % m[0], '%.3f' % m[len(m) // 2], '%.3f' % m[-1],
                       '%.1f' % L[len(L) // 2], '%.1f' % L[-1]))

    out += ['', '## the rolling %g h window - how far the median leg MFE moves' % float(win_h), '']
    out += head('the timeframe', 'windows with at least one leg', 'windows with none',
                'legs per window, median', 'the window median MFE %, min',
                'the window median MFE %, median', 'the window median MFE %, max',
                'max over min - how many times bigger the widest window is')
    SER = {}
    for tf in tfs:
        rows = LEG[tf]
        bars = [x[0] for x in rows]
        ser, empty = [], 0
        e = int(A) + W
        while e <= int(B):
            lo = _bisect.bisect_left(bars, e - W + 1)
            hi = _bisect.bisect_right(bars, e)
            g = [rows[i][1] for i in range(lo, hi)]
            if g:
                ser.append((e, float(_np.median(g)), len(g)))
            else:
                empty += 1
            e += ST
        SER[tf] = ser
        if not ser:
            out.append(row(tf, 0, empty, *['-'] * 5))
            continue
        v = sorted(x[1] for x in ser)
        n = sorted(x[2] for x in ser)
        out.append(row(tf, len(ser), empty, n[len(n) // 2], '%.3f' % v[0],
                       '%.3f' % v[len(v) // 2], '%.3f' % v[-1],
                       '%.1fx' % (v[-1] / v[0]) if v[0] > 0 else 'nan'))

    for tf in tfs:
        out += ['', '## %s - every rolling window, chronological' % tf, '']
        out += head('the window ends at', 'the window opens at', 'legs confirmed in it',
                    'the median leg MFE %', 'the smallest leg MFE %', 'the largest leg MFE %')
        rows = LEG[tf]
        bars = [x[0] for x in rows]
        for e, med, cnt in SER[tf]:
            lo = _bisect.bisect_left(bars, e - W + 1)
            hi = _bisect.bisect_right(bars, e)
            g = sorted(rows[i][1] for i in range(lo, hi))
            out.append(row(ln.U(int(e)), ln.U(int(e) - W + 1), cnt, '%.3f' % med,
                           '%.3f' % g[0], '%.3f' % g[-1]))
    return out


def c3r_mage_gate(v, sd, gate, lo_f, hi_f):
    """Does ws1Mage at `v` satisfy `gate` on side `sd`? -> bool.

    HIS 1108 five gates. ONE reader, called by both the banked c3r scan and the gate sweep, so the
    sweep's `oob` column and the banked default can never diverge.

      none       no level requirement - his 1108 *"where ever it is on the board"*
      oob        at or beyond OOB, %g high / %g low
      ib         inside OOB
      ex-fence   at or beyond the 20/80 fence
      in-fence   inside the 20/80 fence
    """ % (float(K.OOB_HI), float(K.OOB_LO))
    if gate == 'none':
        return True
    if gate == 'oob':
        return v >= float(K.OOB_HI) if sd > 0 else v <= float(K.OOB_LO)
    if gate == 'ib':
        return v < float(K.OOB_HI) if sd > 0 else v > float(K.OOB_LO)
    if gate == 'ex-fence':
        return v >= float(hi_f) if sd > 0 else v <= float(lo_f)
    if gate == 'in-fence':
        return v < float(hi_f) if sd > 0 else v > float(lo_f)
    raise ValueError('the ws1Mage gate is none, oob, ib, ex-fence or in-fence')


def c3r_mage_level(LN):
    """The ws1Mage series the GATE reads. -> array.

    HIS 1108: *"change the 'ws1MAge oob requirement' from emerging to close-prev"*. The reversal
    bar still comes from jig.lift_off on EMERGING ws1Mage - that producer's own contract and his
    standing *"lift-off reads emerging"* - and only the LEVEL test moves to closed-prev. An
    emerging line goes oob before its closed-prev value does, so the gate now passes later.
    """
    import numpy as _np
    r = str(K.FDM2_C3R_MAGE_READ)
    assert r in ('closed-prev', 'emerging'), 'FDM2_C3R_MAGE_READ is %r' % r
    return _np.asarray(LN['CPM'][1] if r == 'closed-prev' else LN['MGE'][1], float)


def c3r_mage_hold(m1g, st, sd, gate, lo_f, hi_f, wob, n):
    """Does the gate HOLD for `wob` bars from `st`? -> the bar it is knowable at, or None.

    HIS 1108: *"add a wob 8 to it"*, `FDM2_C3R_MAGE_WOB` 8 bars = 40 s.

    jig.lift_off's OWN CONVENTION, not a new one: `wob` bars the state must STAY satisfied counting
    the first bar, and the event is not KNOWABLE until bar + wob - 1. So this tests `st` through
    `st + wob - 1` and returns that last bar, which is the one a consumer may act on. Every bar it
    reads is at or before the bar it returns - there is no forward look past the hold.
    """
    w = max(1, int(wob))
    if int(st) + w > int(n):
        return None
    for t in range(int(st), int(st) + w):
        if not c3r_mage_gate(float(m1g[t]), int(sd), gate, lo_f, hi_f):
            return None
    return int(st) + w - 1


def c3r_mage_stamps(LN, sd):
    """Every ws1Mage same-side lift-off STAMP on `sd`, ascending. -> int list.

    HIS 1108 pick of producer: jig.lift_off on ws1Mage EMERGING, acted on at K.lift_stamp(b) =
    b + LIFT_WOB - 1, because a lift-off is not knowable until its hold completes.
    """
    import numpy as _np
    m1e = _np.asarray(LN['MGE'][1], float)
    return sorted(K.lift_stamp(int(x)) for x in
                  JIG.lift_off(m1e, int(sd), K.LIFT_PTS, K.gap_for(1), K.LIFT_TOL, K.LIFT_WOB))


def c3rmage_table(LN, A, B, lab='ws3r emerging, rest closed-prev'):
    """Open the c3r trade at the ws1Mage reversal instead of at the clause-4 bar. -> the markdown.

    HIS 1108: *"yes, I want to see what improvements we get from opening a c3r trade at the
    ws1Mage reversal. I'm not sure if ws1Mage needs to be oob or ib or ex fence or in fence. it
    will be good to find out"*.

    THE REVERSAL PRODUCER IS HIS 1108 PICK: `jig.lift_off(ws1Mage EMERGING, the c3r arm's side,
    LIFT_PTS, gap_for(1), LIFT_TOL, LIFT_WOB)`, acted on at `K.lift_stamp(b)` = b + LIFT_WOB - 1,
    because a lift-off is not knowable until its hold completes.

    THE FIVE GATES, all read at the stamp bar on the c3r arm's own side:

      none       no level requirement at all - his 1108 *"where ever it is on the board"*
      oob        ws1Mage at or beyond OOB, 85 high / 15 low
      ib         ws1Mage inside OOB
      ex-fence   ws1Mage at or beyond the 20/80 fence
      in-fence   ws1Mage inside the 20/80 fence

    WHAT ENDS THE WAIT IS NOT MEASURED HERE, AND THAT IS STATED. His 1108 race was *"race mae stop
    and next cadence event (first of)"*, and the stop in that race belongs to the INCOMING trade,
    which this scan does not model. So the walk here runs forward with no ender and reports how far
    it travelled; a wait-ender can only remove rows, never add them.

    EVERY OTHER PART IS UNCHANGED from cad3r_scan: his dynamic stop off the walk back to look
    forward, and his target-side cadence close.
    """
    import numpy as _np
    close = _np.asarray(LN['close'], float)
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    m1e = c3r_mage_level(LN)
    RAW = {+1: _np.asarray(LN['phi'], float), -1: _np.asarray(LN['plo'], float)}
    CE = {sd2: sorted(int(e[0]) for e in F2.cadence_events(LN, sd2, int(A), int(B)))
          for sd2 in (+1, -1)}
    LF = {sd2: c3r_mage_stamps(LN, sd2) for sd2 in (+1, -1)}
    _, fired = cad3r_arms(LN, A, B, lab)
    sigs = {}
    for q, sd, E in fired:
        sigs.setdefault((int(E['x4']), int(sd)), E)
    keys = sorted(sigs)

    GATES = ('none', 'oob', 'ib', 'ex-fence', 'in-fence')

    def passes(gate, v, sd2):
        return c3r_mage_gate(v, int(sd2), gate, lo_f, hi_f)

    out = ['| the read | value |', '|---|---|']
    out.append(row('the firings read', '%d distinct firing bars, from %d ws1r oob entries that '
                                       'fired' % (len(keys), len(fired))))
    out.append(row('the reversal producer', "`jig.lift_off(ws1Mage emerging, the c3r arm's side, "
                                            'LIFT_PTS %d, gap_for(1) %d, LIFT_TOL %g, LIFT_WOB %d)`'
                   % (int(K.LIFT_PTS), int(K.gap_for(1)), float(K.LIFT_TOL), int(K.LIFT_WOB))))
    out.append(row('the bar acted on', '`K.lift_stamp(b)` = b + %d bars = b + %d s'
                   % (int(K.LIFT_WOB) - 1, (int(K.LIFT_WOB) - 1) * 5)))
    out.append(row('the oob fence', '%g high / %g low' % (float(K.OOB_HI), float(K.OOB_LO))))
    out.append(row('the 20/80 fence', '%g high / %g low' % (float(hi_f), float(lo_f))))
    out.append(row('what ends the wait', 'NOTHING, in this read. His race needs the incoming '
                                         'trade, which this scan does not model. A wait-ender can '
                                         'only remove rows'))
    out.append(row('the stop LEVEL', 'a RAW kline extreme from his walk back to look forward, '
                                     'gap %d bars = %d min' % (int(JIG.MC_GAP),
                                                               int(JIG.MC_GAP) * 5 // 60)))
    out.append(row('the stop TRIGGER', 'pxs reaching that absolute price - his 1108 reason: only '
                                       'a real price push fires it'))
    out.append(row('the exit', 'his target-side cadence event, or the stop, first of'))

    def score(opn, osd, cap, price=None):
        sb = (F2.stop_bar_at(LN, opn, int(B), osd, price) if price is not None
              else F2.stop_bar(LN, opn, int(B), osd, cap))
        ce = _bisect.bisect_right(CE[osd], opn)
        cb = CE[osd][ce] if ce < len(CE[osd]) else None
        if cb is not None and (sb is None or int(cb) < int(sb)):
            ex, how = int(cb), 'CLOSED at the target-side cadence'
        elif sb is not None:
            ex, how = int(sb), 'STOP'
        else:
            ex, how = int(B), 'still open at the span end'
        op = float(close[opn])
        pp = osd * (_np.asarray(close[opn:ex + 1], float) - op) / op * 100.0
        return dict(ex=ex, how=how, mae=abs(float(_np.nanmin(pp))), mfe=float(_np.nanmax(pp)),
                    rel=-cap if how == 'STOP' else osd * (float(close[ex]) - op) / op * 100.0)

    def level(opn, sd2, osd):
        """HIS 1108 two-series stop. -> (the distance in percent, the raw price or None)."""
        Mx = JIG.mage_cascade_bar(RAW[int(sd2)], opn, int(sd2), mode='extrema',
                                  gap=int(JIG.MC_GAP))
        if Mx is None:
            return float(K.FDM_MAE_CAP), None
        pv = float(RAW[int(sd2)][int(Mx[0])])
        o_px = float(close[opn])
        d = -osd * (pv - o_px) / o_px * 100.0
        return (d, pv) if d > 0 else (float(K.FDM_MAE_CAP), None)

    rowsg = {}
    for gate in GATES:
        acc = []
        for (x4, sd) in keys:
            osd = -int(sd)
            land = None
            for st in LF[int(sd)]:
                if st < int(x4) or st > int(B):
                    continue
                k = c3r_mage_hold(m1e, st, int(sd), gate, lo_f, hi_f,
                                  int(K.FDM2_C3R_MAGE_WOB), int(B) + 1)
                if k is not None:
                    land = int(k)
                    break
            if land is None:
                acc.append(dict(x4=x4, sd=sd, land=None))
                continue
            opn = land + 2
            if opn > int(B):
                acc.append(dict(x4=x4, sd=sd, land=land, opn=None))
                continue
            cap, price = level(opn, int(sd), osd)
            S = score(opn, osd, cap, price)
            acc.append(dict(x4=x4, sd=sd, land=land, opn=opn, cap=cap,
                            m1=float(m1e[land]), **S))
        rowsg[gate] = acc

    out += ['', '## the gate curve - every gate on the same %d signals' % len(keys), '']
    out += head('the ws1Mage gate', 'signals that found a reversal', 'signals that found none',
                'the wait, min - median', 'the wait, min - max', 'trades scored', 'that stopped',
                'that closed at a target-side cadence', 'MAE %, median', 'MFE %, median',
                'realised %, total', 'drag %', 'net %', 'net % per trade')
    for gate in GATES:
        g = [x for x in rowsg[gate] if x.get('opn') is not None]
        miss = sum(1 for x in rowsg[gate] if x.get('land') is None)
        if not g:
            out.append(row(gate, 0, miss, *['-'] * 11))
            continue
        w = sorted((x['opn'] - 2 - x['x4']) * 5 / 60.0 for x in g)
        rl = [x['rel'] for x in g]
        n = len(g)
        out.append(row(gate, n, miss, '%.1f' % w[len(w) // 2], '%.1f' % w[-1], n,
                       sum(1 for x in g if x['how'] == 'STOP'),
                       sum(1 for x in g if x['how'].startswith('CLOSED')),
                       '%.3f' % float(_np.median([x['mae'] for x in g])),
                       '%+.3f' % float(_np.median([x['mfe'] for x in g])),
                       '%+.3f' % sum(rl), '%.3f' % (-DRAG_PCT * n),
                       '%+.3f' % (sum(rl) - DRAG_PCT * n),
                       '%+.4f' % ((sum(rl) - DRAG_PCT * n) / n)))

    for gate in GATES:
        out += ['', '## every signal under the `%s` gate' % gate, '']
        out += head('the firing bar', 'the side it fired on', 'the OUTGOING trade',
                    'the ws1Mage reversal stamp', 'ws1Mage there', 'the wait, min', 'it opens at',
                    'the open price', 'the stop distance %', 'the exit', 'the exit kind',
                    'held min', 'MAE %', 'MFE %', 'realised %')
        for x in rowsg[gate]:
            sd, osd = int(x['sd']), -int(x['sd'])
            if x.get('land') is None:
                out.append(row(ln.U(x['x4']), 'HIGH' if sd > 0 else 'LOW',
                               'SHORT' if osd < 0 else 'LONG',
                               'no ws1Mage reversal passes this gate before the span ends',
                               *['-'] * 11))
                continue
            if x.get('opn') is None:
                out.append(row(ln.U(x['x4']), 'HIGH' if sd > 0 else 'LOW',
                               'SHORT' if osd < 0 else 'LONG', ln.U(x['land']),
                               '%.2f' % float(m1e[x['land']]),
                               '%.1f' % ((x['land'] - x['x4']) * 5 / 60.0),
                               'past the span end', *['-'] * 8))
                continue
            out.append(row(ln.U(x['x4']), 'HIGH' if sd > 0 else 'LOW',
                           'SHORT' if osd < 0 else 'LONG', ln.U(x['land']), '%.2f' % x['m1'],
                           '%.1f' % ((x['land'] - x['x4']) * 5 / 60.0), ln.U(x['opn']),
                           '%.6f' % float(close[x['opn']]), '%.3f' % x['cap'], ln.U(x['ex']),
                           x['how'] if x['how'] != 'STOP' else 'STOP at %.3f%%' % x['cap'],
                           '%.1f' % ((x['ex'] - x['opn']) * 5 / 60.0), '%.3f' % x['mae'],
                           '%+.3f' % x['mfe'], '%+.3f' % x['rel']))
    return out


def cad3r_arms(LN, A, B, lab):
    """Every ws1r oob entry in the span, evaluated. -> (every arm, the ones that fired).

    ONE PLACE FINDS THE FIRINGS. cad3r_scan scores them against his FDM_MAE_CAP stop and
    pivstop_table scores the same list against a pivot-derived stop, so the two reports can never
    disagree about which bars fired.
    """
    import numpy as _np
    rows_, fired = [], []
    for sd in (+1, -1):
        r1 = _np.asarray(LN['CPR'][1] if lab != 'emerging' else LN['EMR'][1], float)
        o1 = (r1 >= float(K.OOB_HI)) if sd > 0 else (r1 <= float(K.OOB_LO))
        arms = [q for q in range(max(1, int(A)), int(B) + 1) if o1[q] and not o1[q - 1]]
        for q in arms:
            E = cad3r_eval(LN, sd, q, lab)
            if E['oob1'] != q:
                continue
            rows_.append((q, sd, E))
            if E['fires'] and int(A) <= int(E['x4']) <= int(B):
                fired.append((q, sd, E))
    return rows_, fired


def cad3r_scan(LN, A, B, lab='ws3r emerging, rest closed-prev'):
    """Every `fdm2-3r-cadence` arm in a span, both sides, with the outgoing trade scored. -> [str].

    HIS 1108: *"we'll need a list of the firings across 08-25 to 08-31 (with maemfe) to validate
    the change"*, and *"run the 7 day anyway - I'll investigate the 1809 signal"*.

    AN ARM IS A ws1r OOB ENTRY. Every one in the span is evaluated through cad3r_eval, on both
    sides, so a kill is listed beside a firing and the hit rate is readable rather than asserted.

    HOW MAE/MFE IS MEASURED - HE DID NOT RULE THIS AND I AM STATING MY CHOICE. A c3r firing is a
    rev-trade signal, not a trade, so there is nothing to score until the router acts on it. I score
    the OUTGOING trade it would open: the opposite direction, from the firing bar + 2 bars, which is
    the router's own "close then open", to its FDM_MAE_CAP 1.10% stop. That is how every other fdm2
    number in this session is scored, so these are comparable with them. No other horizon is
    applied - the stop is his, and a trade with no stop in the span is reported as still open.
    """
    import numpy as _np
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    close = _np.asarray(LN['close'], float)
    phi = _np.asarray(LN['phi'], float)
    plo = _np.asarray(LN['plo'], float)
    out = ['| the scan | value |', '|---|---|']
    out.append(row('the mech', '`fdm2-3r-cadence`, HIS NAME. Prefix `c3r_`'))
    out.append(row('the read', lab))
    out.append(row('the span', '%s .. %s - %d bars = %.1f days'
                   % (ln.U(int(A)), ln.U(int(B)), int(B) - int(A) + 1,
                      (int(B) - int(A) + 1) * 5 / 86400.0)))
    out.append(row('an arm', "every ws1r oob entry on either side"))
    out.append(row('MAE/MFE basis', 'THE OUTGOING trade the firing would open - the opposite '
                                    'direction, from the firing bar + 2 bars to its stop. MY '
                                    'CHOICE, he did not rule it'))
    out.append(row('the stop LEVEL', 'HIS 1108: *"we set the stop level using raw high/low"*. '
                                     '`jig.mage_cascade_bar(the RAW kline high for a HIGH arm or '
                                     "the raw low for a LOW one, the open bar, the c3r arm's side, "
                                     "mode='extrema', gap=%d)` - HIS walk back to look forward at "
                                     'his own `MC_GAP` %d bars = %d min. No buffer: he has not '
                                     'ruled one' % (int(JIG.MC_GAP), int(JIG.MC_GAP),
                                                    int(JIG.MC_GAP) * 5 // 60)))
    out.append(row('the stop TRIGGER', 'HIS 1108: *"we use pxs to match the stop level ... pxs '
                                       "smoothes out the bumps, so small spikes near the stop won't "
                                       'appear to pxs, therefore the stop is avoided - only a real '
                                       'price push can trigger the stop"*. `F2.stop_bar_at` walks '
                                       'pxs to that absolute price'))
    out.append(row('the row unit', 'HIS 1108: *"consolidate and count the trade as a single '
                                   'evemt"*. ONE row per firing bar and side, however many ws1r '
                                   'oob entries walked into it'))
    out.append(row('the ws1Mage reads', 'the REVERSAL on emerging ws1Mage via `jig.lift_off`; '
                                        'the LEVEL on %s ws1Mage - HIS 1108 ruling'
                   % str(K.FDM2_C3R_MAGE_READ)))
    out.append(row('the ws1Mage oob hold', 'HIS 1108 *"add a wob 8 to it"*. `FDM2_C3R_MAGE_WOB` %d '
                                           'bars = %d s. The gate must hold across all %d bars '
                                           'from the lift-off stamp, and the rev-trade lands on '
                                           'the LAST of them, stamp + %d'
                   % (int(K.FDM2_C3R_MAGE_WOB), int(K.FDM2_C3R_MAGE_WOB) * 5,
                      int(K.FDM2_C3R_MAGE_WOB), int(K.FDM2_C3R_MAGE_WOB) - 1)))
    out.append(row('the ws1Mage wait', ('ON, gate `%s` - HIS 1108 *"apply the ws1Mage oob to the '
                                        'mech so that we are net positive"*. The rev-trade is '
                                        'placed at the first ws1Mage same-side lift-off STAMP at '
                                        'or after the clause-4 bar where ws1Mage holds that level, '
                                        'and the trade opens 2 bars later'
                                        % str(K.FDM2_C3R_MAGE_GATE))
                   if int(K.FDM2_C3R_MAGE_ON) else
                   'OFF - the rev-trade is placed at the clause-4 bar'))
    out.append(row('the fallback', 'FDM_MAE_CAP %.2f%% - used only where the walk back finds no '
                                   'adverse extrema, which would otherwise leave the trade with '
                                   'no stop at all. MY CHOICE, stated' % float(K.FDM_MAE_CAP)))
    out.append(row('the exit', 'HIS 1108 ruling: the first TARGET-SIDE cadence event after the '
                               'open, or the stop, whichever comes first. His words - *"the next '
                               'opposite-side cadence event. it\'s the best option we have because '
                               'the c3r trade events are not continuous"* and *"the cadence must be '
                               'target-side (example c3r opens a high SHORT, the only thing that '
                               'can close it is a target (low) side cadence or a stop)"*'))
    out.append(row('the target side', 'a SHORT hunts the LOW cadence, a LONG the HIGH one - so a '
                                      "HIGH-side c3r arm's SHORT is closed by a LOW cadence"))
    out.append(row('ws3r minimum dwell', '`FDM2_C3R_DWELL` %d bars = %d s - HIS 1108 *"ws3r '
                                         'minimum dwell should be 3 minutes"*'
                   % (int(K.FDM2_C3R_DWELL), int(K.FDM2_C3R_DWELL) * 5)))
    out.append(row('the price series', 'pxs - DEMA(close, 2) on the 5 s grid. HIS 1108 ruling: '
                                       'the stop, MAE and MFE all read it. The raw kline high/low '
                                       'MFE is printed in the aggregate for comparison only'))
    #   HIS 1108 EXIT. The target-side cadence bars are built ONCE per side for the whole span,
    #   not per firing: F2.cadence_events walks the span and a 30-row scan must not walk it 30
    #   times. `CE[+1]` are the HIGH events, which close a LONG; `CE[-1]` the LOW, which close a
    #   SHORT.
    CE = {sd2: sorted(int(e[0]) for e in F2.cadence_events(LN, sd2, int(A), int(B)))
          for sd2 in (+1, -1)}
    #   THE LEVEL SERIES PER SIDE. A HIGH-side c3r arm opens a SHORT whose stop sits above, so its
    #   level is a RAW kline HIGH; a LOW arm's LONG takes a raw LOW.
    RAW = {+1: phi, -1: plo}
    #   HIS 1108 ws1Mage WAIT, BANKED AT GATE `oob`. The stamps are built once per side.
    DRAG = DRAG_PCT
    MW = int(K.FDM2_C3R_MAGE_ON)
    MG = str(K.FDM2_C3R_MAGE_GATE)
    MWOB = int(K.FDM2_C3R_MAGE_WOB)
    LF = {sd2: c3r_mage_stamps(LN, sd2) for sd2 in (+1, -1)} if MW else None
    m1g = c3r_mage_level(LN)
    rows_, fired = cad3r_arms(LN, A, B, lab)
    out += ['', '| the arm - ws1r oob entry | side | the verdict | the clause that killed it | '
            'the firing bar | branch | ws3r oob at | clause 3 ws3Mage | clause 3 ws3b | '
            "clause 5 ws1b's extreme |", '|---|---|---|---|---|---|---|---|---|---|']
    for q, sd, E in sorted(rows_):
        out.append(row(ln.U(q), 'HIGH' if sd > 0 else 'LOW',
                       '**REV-TRADE**' if E['fires'] else 'killed',
                       '-' if E['fires'] else E['kill'],
                       ln.U(int(E['x4'])) if E['x4'] is not None else '-',
                       E['branch'] or '-',
                       ln.U(int(E['oob3'])) if E['oob3'] is not None else '-',
                       '%.2f' % E['c3_mage'] if E['c3_mage'] is not None else '-',
                       '%.2f' % E['c3_b'] if E['c3_b'] is not None else '-',
                       '%.2f' % E['c5_ext'] if E['c5_ext'] is not None else '-'))
    if not rows_:
        out.append(row('none', '-', '-', '-', '-', '-', '-', '-', '-', '-'))

    out += ['', '## the firings, with the outgoing trade scored', '']
    #   HIS 1108 COLUMN SET. *"add a column: the timestamp of the pivot that created the stop /
    #   drop mfe over mae, held min"*. The pivot's bar and the level's distance come out of the
    #   exit-kind text and into their own columns, and `realised %` is GROSS - drag is its own
    #   column and net is its own, per his standing rule that the cost never hides inside a net.
    out += head('the c3r firing bar', 'the side it fired on', 'branch',
                'the ws1Mage %s reversal' % (str(K.FDM2_C3R_MAGE_GATE)
                                             if int(K.FDM2_C3R_MAGE_ON) else 'wait is OFF'),
                'the wait, min', 'the OUTGOING trade', 'it opens at', 'the open price',
                'the pivot that set the stop', 'the stop level', 'the stop distance %',
                'the exit', 'the exit kind', 'MAE %', 'MFE %', 'realised % GROSS', 'drag %',
                'net %')
    mae_l, mfe_l, mfer_l, rel_l, stop_l, cap_l, how_l = [], [], [], [], [], [], []
    out_rows_skipped = []
    #   HIS 1108, TWICE. First *"consolidate and count the trade as a single evemt"*, which deduped
    #   on the c3r firing bar. The ws1Mage wait then moved the collision one step later - three
    #   firings waited into 2026-08-31 00:52:30 and opened the same SHORT at one price - so his
    #   second ruling: *"we can't have duplicate trades firing off at the same consolidated moment
    #   (like ws1Mage for c3r, and for any other mech where individual signals boil down to one
    #   bar)"*. SO THE DEDUP IS ON THE BAR THE TRADE OPENS ON, not on the signal that found it, and
    #   the EARLIEST firing keeps the row because it is the one that got there first.
    _seen = {}
    for q, sd, E in sorted(fired):
        _seen.setdefault((int(E['x4']), int(sd)), (q, sd, E))
    waited, nomage, _open_seen, _dupes = [], 0, set(), 0
    for q, sd, E in [v for _, v in sorted(_seen.items())]:
        sig = int(E['x4'])
        #   THE ws1Mage WAIT. His 1108 ruling moves the rev-trade off the clause-4 bar and onto the
        #   first same-side lift-off stamp at or after it where ws1Mage holds the gate. Reading the
        #   stamp means every bar the decision rests on is at or before that stamp.
        if MW:
            land = None
            for st in LF[int(sd)]:
                if st < sig or st > int(B):
                    continue
                k = c3r_mage_hold(m1g, st, int(sd), MG, lo_f, hi_f, MWOB, int(B) + 1)
                if k is not None:
                    land = int(k)
                    break
            if land is None:
                nomage += 1
                out_rows_skipped.append((sig, sd, 'no ws1Mage %s reversal before the span ends'
                                         % MG))
                continue
            if (int(land), int(sd)) in _open_seen:
                _dupes += 1
                out_rows_skipped.append((int(E['x4']), sd,
                                         'DROPPED - a trade already opens at %s' % ln.U(int(land))))
                continue
            _open_seen.add((int(land), int(sd)))
            waited.append((land - sig) * 5 / 60.0)
            sig = land
        opn = sig + 2
        osd = -sd                     # the outgoing trade hunts the opposite side
        if opn > int(B):
            out.append(row(ln.U(int(E['x4'])), 'HIGH' if sd > 0 else 'LOW', E['branch'],
                           ln.U(sig) if MW else '-',
                           '%.1f' % ((sig - int(E['x4'])) * 5 / 60.0) if MW else '-',
                           'SHORT' if osd < 0 else 'LONG', 'past the span', *['-'] * 10))
            continue
        #   HIS 1108 TWO-SERIES STOP. The LEVEL is a raw kline extreme found by his walk back;
        #   the TRIGGER is pxs reaching that absolute price. `cap` is kept as the level's distance
        #   from the open purely so the realised column and the aggregate read in percent.
        Mx = JIG.mage_cascade_bar(RAW[int(sd)], opn, int(sd), mode='extrema', gap=int(JIG.MC_GAP))
        o_px = float(close[opn])
        cap, lvl, price = float(K.FDM_MAE_CAP), 'the FDM_MAE_CAP fallback', None
        if Mx is not None:
            pv = float(RAW[int(sd)][int(Mx[0])])
            dyn = -osd * (pv - o_px) / o_px * 100.0
            if dyn > 0:
                cap, lvl, price = dyn, ln.U(int(Mx[0])), pv
        sb = (F2.stop_bar_at(LN, opn, int(B), osd, price) if price is not None
              else F2.stop_bar(LN, opn, int(B), osd, cap))
        #   THE TARGET-SIDE CADENCE, STRICTLY AFTER THE OPEN. A cadence event ON the open bar
        #   belongs to the bar the trade opened on and cannot also close it.
        ce = _bisect.bisect_right(CE[osd], opn)
        cb = CE[osd][ce] if ce < len(CE[osd]) else None
        if cb is not None and (sb is None or int(cb) < int(sb)):
            ex, how = int(cb), 'CLOSED at the target-side cadence'
        elif sb is not None:
            ex, how = int(sb), ('STOP - pxs reached the raw extreme' if price is not None
                                else 'STOP - the FDM_MAE_CAP fallback')
        else:
            ex, how = int(B), 'still open at the span end'
        op = float(close[opn])
        #   HIS 1108: *"the mae1.1 stops need to be on pxs"*. MAE and MFE read pxs, the same
        #   series the stop now fires on, so the three columns describe one price series. The raw
        #   kline high/low MFE is carried alongside for the aggregate only - he has not ruled which
        #   series MFE belongs on, and printing both leaves that ruling his.
        pxw = _np.asarray(close[opn:ex + 1], float)
        pp = osd * (pxw - op) / op * 100.0
        mae = abs(float(_np.nanmin(pp)))      # UNCLAMPED: the old min(.., cap) hid a gap through
        mfe = float(_np.nanmax(pp))           #            the stop, which is the number he needs
        fav = (phi if osd > 0 else plo)[opn:ex + 1]
        mfe_raw = float(_np.nanmax(osd * (fav - op) / op * 100.0))
        #   A CADENCE CLOSE REALISES THE PRICE AT ITS BAR; a stop realises the level it fired on.
        rel = (-cap if how.startswith('STOP')
               else osd * (float(close[ex]) - op) / op * 100.0)
        mae_l.append(mae)
        mfe_l.append(mfe)
        mfer_l.append(mfe_raw)
        rel_l.append(rel)
        stop_l.append(how.startswith('STOP'))
        how_l.append(how)
        cap_l.append(cap)
        out.append(row(ln.U(int(E['x4'])), 'HIGH' if sd > 0 else 'LOW', E['branch'],
                       ln.U(sig) if MW else '-',
                       '%.1f' % ((sig - int(E['x4'])) * 5 / 60.0) if MW else '-',
                       'SHORT' if osd < 0 else 'LONG', ln.U(opn), '%.6f' % op,
                       lvl, '%.6f' % price if price is not None else '-', '%.3f' % cap,
                       ln.U(ex), how, '%.3f' % mae, '%+.3f' % mfe, '%+.3f' % rel,
                       '%.4f' % -DRAG, '%+.3f' % (rel - DRAG)))
    for sig0, sd0, why0 in out_rows_skipped:
        out.append(row(ln.U(int(sig0)), 'HIGH' if sd0 > 0 else 'LOW', '-', why0, *['-'] * 13))
    if not fired:
        out.append(row(*(['none'] + ['-'] * 16)))
    else:
        out += ['', '| the aggregate, every number carrying HIS DYNAMIC stop - the walk back to '
                'look forward at gap %d bars = %d min, FDM_MAE_CAP %.2f%% only as the fallback '
                '| value |' % (int(JIG.MC_GAP), int(JIG.MC_GAP) * 5 // 60,
                               float(K.FDM_MAE_CAP)), '|---|---|']
        out.append(row('arms evaluated', len(rows_)))
        out.append(row('firings', '%d of %d arms = %.1f%%'
                       % (len(fired), len(rows_), len(fired) / len(rows_) * 100.0)))
        out.append(row('killed at clause 1 / 2 / 3 / 4 / 5',
                       ' / '.join(str(sum(1 for _, _, E in rows_ if E['kill'] == c))
                                  for c in '12345')))
        out.append(row("killed at his ws3r minimum dwell, %d bars = %d s"
                       % (int(K.FDM2_C3R_DWELL), int(K.FDM2_C3R_DWELL) * 5),
                       sum(1 for _, _, E in rows_ if E['kill'] == 'dwell')))
        out.append(row("ws3r's oob dwell on the arms that fired, bars - median",
                       '%.0f = %.0f s' % (float(_np.median([E['dwell'] for _, _, E in fired])),
                                          float(_np.median([E['dwell'] for _, _, E in fired])) * 5)
                       if fired else '-'))
        if MW:
            out.append(row('the ws1Mage %s wait, min - median' % MG,
                           '%.1f' % float(_np.median(waited)) if waited else '-'))
            out.append(row('the ws1Mage %s wait, min - max' % MG,
                           '%.1f' % max(waited) if waited else '-'))
            out.append(row('signals with no ws1Mage %s reversal before the span ends' % MG,
                           nomage))
            out.append(row('signals DROPPED because a trade already opens on that bar', _dupes))
        out.append(row('outgoing trades scored', len(mae_l)))
        out.append(row('that stopped', sum(1 for r in stop_l if r)))
        out.append(row('that closed at a target-side cadence event',
                       sum(1 for h in how_l if h.startswith('CLOSED'))))
        out.append(row('still open at the span end',
                       sum(1 for h in how_l if h.startswith('still'))))
        out.append(row('realised %, the cadence closes only',
                       '%+.3f total, %+.3f median over %d rows'
                       % (sum(r for r, h in zip(rel_l, how_l) if h.startswith('CLOSED')),
                          float(_np.median([r for r, h in zip(rel_l, how_l)
                                            if h.startswith('CLOSED')])),
                          sum(1 for h in how_l if h.startswith('CLOSED')))
                       if any(h.startswith('CLOSED') for h in how_l) else 'none'))
        out.append(row('realised %, the stops only',
                       '%+.3f total, %+.3f median over %d rows'
                       % (sum(r for r, h in zip(rel_l, how_l) if h.startswith('STOP')),
                          float(_np.median([r for r, h in zip(rel_l, how_l)
                                            if h.startswith('STOP')])),
                          sum(1 for h in how_l if h.startswith('STOP')))
                       if any(h.startswith('STOP') for h in how_l) else 'none'))
        out.append(row('MAE %, median', '%.3f' % float(_np.median(mae_l))))
        out.append(row('MFE %, median', '%+.3f' % float(_np.median(mfe_l))))
        out.append(row('MFE %, total', '%+.3f' % sum(mfe_l)))
        out.append(row('MFE %, median - on the RAW kline high/low instead of pxs',
                       '%+.3f' % float(_np.median(mfer_l))))
        out.append(row('MFE %, total - on the RAW kline high/low instead of pxs',
                       '%+.3f' % sum(mfer_l)))
        out.append(row('realised %, median - GROSS, before drag',
                       '%+.3f' % float(_np.median(rel_l))))
        out.append(row('net %%, median - after the %.4f%% round trip' % DRAG,
                       '%+.3f' % float(_np.median([r - DRAG for r in rel_l]))))
        out.append(row('realised %, total - GROSS, before drag', '%+.3f' % sum(rel_l)))
        out.append(row('the dynamic stop distance %, median', '%.3f' % float(_np.median(cap_l))))
        out.append(row('the dynamic stop distance %, min .. max',
                       '%.3f .. %.3f' % (min(cap_l), max(cap_l))))
        out.append(row('rows that fell back to FDM_MAE_CAP %.2f%%' % float(K.FDM_MAE_CAP),
                       sum(1 for c in cap_l if abs(c - float(K.FDM_MAE_CAP)) < 1e-12)))
        out.append(row('drag %', '-%.3f (%.4f%% round trip x %d)'
                       % (DRAG_PCT * len(rel_l), DRAG_PCT, len(rel_l))))
        out.append(row('net %', '%+.3f' % (sum(rel_l) - DRAG_PCT * len(rel_l))))
    return out


def cad3r_table(LN, side, mark):
    """`fdm2-3r-cadence` - HIS NAME, 1107. His five clauses evaluated at one marker. -> [str].

    HIS SPEC, verbatim and in his indentation:

        1) IF a ws3r line's trajectory is matching ws1r's trajectory until ws1r crosses to ib
        2) -IF the ws3r line continues its trajectory and reaches oob without returning past
             counter-side 50
        3) --IF ws3Mage or ws3b is past counter-side 50
        4) ---IF ws3r crosses to in-20/80-fence
        5) ----IF ws1b has not been same-side oob between "ws1r reversal" and "ws3r crossing to
                in-20/80-fence"
        6) -----rev-trade ELSE stop

    HIS 1107 RULINGS ON EVERY GAP I RAISED:
      clause 1, "matching"   *"both lines read towards the same side"*
      clause 1, where it starts  *"ws1r's oob entry. note that ws1r will not be oob shortly after
                             and ws3r will not.. this makes the "ws1r's oob entry." test a
                             one-time-only test"* - so clause 1 is read at ONE bar and never again
      the read               *"I want to know both. closed-prev is what I built on, but my small
                             sample size doesn't give enough data to make a call on emerging"* -
                             so BOTH are reported and neither is banked
      clause 3, which bar    *"the full TF bar before the cross to infence"*
      clause 5, "ws1r reversal"  *"same event: ws1r to ib"*
      clause 6, "ELSE stop"  *"I'm saying the outcomes are either rev-trade, or kill (stop) the
                             3r-cadence mech"* - it kills the mech, NOT the trade

    TWO THINGS ARE STILL HIS AND ARE REPORTED BOTH WAYS RATHER THAN CHOSEN:
      clause 5's threshold   oob at 15/85, or ex-fence at 20/80. At his 2026-08-24 01:09 example
                             ws1b's highest print in the window is 82.94, so the two disagree there
      MY READING OF "the full TF bar"   the complete ws3 closed-prev bar - 3 min = 36 bars - ending
                             at the last ws3 seam at or before the clause-4 cross. Marked MINE.

    IT DECIDES NOTHING IN THE MACHINE. No leg reads this; it is a report on his own markers.
    """
    import numpy as _np
    sd = int(side)
    hi_oob, lo_oob = float(K.OOB_HI), float(K.OOB_LO)
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    mk = int(mark)
    w3b = _np.asarray(ln.line('ws3b'), float)

    def oob(v):
        return (v >= hi_oob) if sd > 0 else (v <= lo_oob)

    def exf(v):
        return (v >= hi_f) if sd > 0 else (v <= lo_f)

    def p50(v):
        return (v < 50.0) if sd > 0 else (v > 50.0)

    out = ['| the mech | value |', '|---|---|']
    out.append(row('the mech', '`fdm2-3r-cadence` - HIS NAME, 1107'))
    out.append(row('his marker', ln.U(mk)))
    out.append(row('the side', 'HIGH' if sd > 0 else 'LOW'))
    out.append(row('oob', 'at or past %g/%g' % (lo_oob, hi_oob)))
    out.append(row('ex-fence', 'at or past %g/%g' % (lo_f, hi_f)))
    out.append(row('past counter-side 50', '%s 50' % ('below' if sd > 0 else 'above')))
    out.append(row('the outcomes', 'a rev-trade, or the mech is killed - HIS 1107'))

    #   THREE VARIANTS, not two. HIS 1108: *"it's closed-prev causing the problem. if we make ws3r
    #   emerging for this c3r mech, does it satisfy all of examples?"* - so ws3r alone moves to
    #   emerging while every other line keeps his standing rule, *"closed-prev is the standard for
    #   everything except lift-off"*. The two pure variants stay beside it so the change is visible.
    for lab in ('closed-prev', 'emerging', 'ws3r emerging, rest closed-prev'):
        em3 = lab != 'closed-prev'
        emx = lab == 'emerging'
        r1 = _np.asarray(LN['EMR'][1] if emx else LN['CPR'][1], float)
        r3 = _np.asarray(LN['EMR'][3] if em3 else LN['CPR'][3], float)
        m3 = _np.asarray(LN['MGE'][3] if emx else LN['CPM'][3], float)
        b3 = _np.asarray(w3b if emx else CP.series(w3b, 3 * 60), float)
        b1 = _np.asarray(LN['B1'], float)
        rows_ = []
        kill = None

        #   clause 1 - ONE bar: ws1r's oob ENTRY at or before the marker, then both towards
        o1 = oob(r1)
        a = mk
        while a > 0 and not o1[a]:
            a -= 1
        while a > 0 and o1[a - 1]:
            a -= 1
        if not o1[a]:
            rows_.append(('1', '-', 'no ws1r oob entry at or before the marker', 'KILL'))
            kill = '1'
        else:
            t1 = F2.towards(r1, 1, a, sd)
            t3 = F2.towards(r3, 3, a, sd)
            rows_.append(('1', ln.U(a),
                           'ws1r oob entry at %.2f. towards at that bar - ws1r %s, ws3r %s'
                           % (r1[a], 'yes' if t1 else 'NO', 'yes' if t3 else 'NO'),
                           'PASS' if (t1 and t3) else 'KILL'))
            if not (t1 and t3):
                kill = '1'

        #   ws1r's ib cross - clause 1's end AND clause 5's start, his *"same event"*
        ib1 = None
        if kill is None:
            i = a
            while i < len(r1) - 1 and o1[i]:
                i += 1
            ib1 = i
            rows_.append(('1 end', ln.U(ib1), 'ws1r crosses to ib at %.2f - this is also clause '
                          "5's \"ws1r reversal\", his *\"same event\"*" % r1[ib1], 'the anchor'))

        #   clause 2 - ws3r reaches oob after ws1r's ib cross, and does not RETURN past
        #   counter-side 50 on the way.
        #
        #   HIS 1108 CORRECTION OF MY READING, and the word that carries it: *"clause 2 is more
        #   nuanced that I thought. the issue I see is that when ws1r reaches oob, ws3r is still
        #   climbing and has not travelled far enough to print on the target-side of 50 --this
        #   isn't the spirit of clause 2: clause 2 was designed to reject an unstable ws3r, a line
        #   that bends back and forth before it reaches the target side"*.
        #
        #   I HAD TESTED "ever printed counter-side 50", which fires on a line that STARTED there
        #   and was merely climbing. At 2026-08-25 08:22:00 ws3r sat at 48.61 on a high-side
        #   trajectory with no earlier print above 50, so there was nothing to return from, and my
        #   reading killed it wrongly.
        #
        #   HIS TWO 1108 RULINGS CLOSE IT:
        #     where the test ARMS   *"ws3r's first print on the target side of 50 after ws1r's
        #                           target-side oob entry"* - so the arm bar is anchored on clause
        #                           1's START, not on its end
        #     how many returns      *"one return is enough to trigger unstable"*
        oob3bar = None
        if kill is None:
            o3, p3 = oob(r3), p50(r3)
            arm = None
            for q in range(a, len(r3)):
                if not p3[q]:
                    arm = q
                    break
                if o3[q]:
                    break
            if arm is None:
                rows_.append(('2 arm', '-', 'ws3r never printed on the target side of 50 after '
                              "ws1r's oob entry %s - the counter-side test has nothing to return "
                              'from' % ln.U(a), 'the test stays unarmed'))
            else:
                rows_.append(('2 arm', ln.U(arm), 'ws3r prints on the target side of 50 at %.2f - '
                              "the counter-side test ARMS here, HIS 1108 anchor on ws1r's oob "
                              'entry %s' % (r3[arm], ln.U(a)), 'armed'))
            j, bad = ib1, None
            while j < len(r3) - 1 and not o3[j]:
                if arm is not None and j >= arm and p3[j] and bad is None:
                    bad = j
                j += 1
            if not o3[j]:
                rows_.append(('2', '-', 'ws3r does not reach oob after %s' % ln.U(ib1), 'KILL'))
                kill = '2'
            elif bad is not None:
                rows_.append(('2', ln.U(bad), 'ws3r RETURNED past counter-side 50 at %.2f, after '
                              'arming at %s, before reaching oob. ONE return is enough - HIS 1108'
                              % (r3[bad], ln.U(arm)), 'KILL'))
                kill = '2'
            else:
                oob3bar = j
                rows_.append(('2', ln.U(j), 'ws3r reaches oob at %.2f with no RETURN past '
                              'counter-side 50 %s'
                              % (r3[j], ('after arming at %s' % ln.U(arm)) if arm is not None
                                 else '- the test never armed'), 'PASS'))

        #   clause 4 - EITHER branch. Taken BEFORE clause 3, because clause 3's bar is defined
        #   relative to it - his *"the full TF bar before the cross"* - and HIS 1108 ruling that
        #   *"the branch-B bar replaces the cross"* for clauses 3 and 5 alike.
        #
        #   HIS 1107 UPDATE, verbatim: *"IF ws3r crosses to in-20/80-fence OR (ws1Mage is same-side
        #   oob and reversing while ws3r is oob, and ws4r is infence)"*, with *"ws1Mge reversal is
        #   lift-off driven"*.
        #
        #   BRANCH B FIRES ON THE LIFT-OFF STAMP, not the lift bar: the stamp is K.lift_stamp's
        #   LIFT_WOB-1 = 7 bars = 35 s offset, and it is the first bar the reversal is knowable.
        #   Firing on the lift bar would read a hold that has not completed.
        #
        #   THE LIFT-OFF IS ALWAYS EMERGING, whichever read the rest of the chain is on - his
        #   standing rule *"closed-prev is the standard for everything except lift-off"*. The three
        #   VALUE tests follow the chain's read, so both variants are visible.
        x4, branch = None, None
        if kill is None:
            m1 = _np.asarray(LN['MGE'][1] if emx else LN['CPM'][1], float)
            r4 = _np.asarray(LN['EMR'][4] if emx else LN['CPR'][4], float)
            lift1 = set(int(x) for x in LN['LIFT'][(1, sd)])
            m1g = _np.asarray(LN['MGE'][1], float)
            lift_m1 = set(K.lift_stamp(int(x)) for x in
                          JIG.lift_off(m1g, sd, K.LIFT_PTS, K.gap_for(1), K.LIFT_TOL, K.LIFT_WOB))
            e3, o3b, o1m = exf(r3), oob(r3), oob(m1)
            inf4 = ~exf(r4)
            j = oob3bar
            while j < len(r3) - 1:
                if not e3[j]:
                    x4, branch = j, 'A'
                    break
                if j in lift_m1 and o1m[j] and o3b[j] and inf4[j]:
                    x4, branch = j, 'B'
                    break
                j += 1
            if x4 is None:
                rows_.append(('4', '-', 'neither branch fired before the tape ends - ws3r stayed '
                              'ex-%g/%g and no qualifying ws1Mage lift-off landed' % (lo_f, hi_f),
                              'KILL'))
                kill = '4'
            elif branch == 'A':
                rows_.append(('4 branch A', ln.U(x4), 'ws3r crosses to in-%g/%g at %.2f'
                              % (lo_f, hi_f, r3[x4]), 'PASS'))
            else:
                rows_.append(('4 branch B', ln.U(x4),
                              'ws1Mage lift-off STAMP here, ws1Mage %.2f oob, ws3r %.2f still oob, '
                              'ws4r %.2f in-%g/%g. The lift bar was %s, %d bars = %d s earlier'
                              % (m1[x4], r3[x4], r4[x4], lo_f, hi_f,
                                 ln.U(x4 - (int(K.LIFT_WOB) - 1)), int(K.LIFT_WOB) - 1,
                                 (int(K.LIFT_WOB) - 1) * 5), 'PASS'))
            if x4 is not None:
                #   HIS 1108: *"have you propely explained why branch B failed? I can't see your
                #   notes on it"*. A bare "did not qualify" names no blocker, so every one of its
                #   four conditions is counted over the window and the binding one is named.
                W = range(oob3bar, x4 + 1)
                n = len(list(W))
                c_oob1m = [q for q in W if o1m[q]]
                c_lift = [q for q in W if q in lift_m1]
                c_oob3 = [q for q in W if o3b[q]]
                c_in4 = [q for q in W if inf4[q]]
                both = [q for q in W if q in lift_m1 and o1m[q] and o3b[q] and inf4[q]]
                worst = min((len(c_lift), 'a ws1Mage lift-off stamp'),
                            (len(c_oob1m), 'ws1Mage same-side oob'),
                            (len(c_oob3), 'ws3r still oob'),
                            (len(c_in4), 'ws4r in-fence'))
                rows_.append(('4 branch B, why', '%s .. %s' % (ln.U(oob3bar), ln.U(x4)),
                              'over the %d bars from ws3r going oob to the clause-4 bar: ws1Mage '
                              'oob on %d, a ws1Mage lift-off stamp on %d, ws3r still oob on %d, '
                              'ws4r in-fence on %d. ALL FOUR on %d. THE BINDING ONE IS %s, at %d '
                              'of %d bars'
                              % (n, len(c_oob1m), len(c_lift), len(c_oob3), len(c_in4),
                                 len(both), worst[1], worst[0], n),
                              'fired at %s' % ln.U(both[0]) if both else 'did not fire'))

        #   clause 3 - at the full ws3 TF bar before that cross. THE BAR CHOICE IS MINE.
        if kill is None:
            span = 3 * 60 // 5
            seam = (x4 // span) * span - 1
            s_a = max(0, seam - span + 1)
            mv = float(m3[seam]) if lab == 'closed-prev' else (
                float(_np.nanmin(m3[s_a:seam + 1])) if sd > 0
                else float(_np.nanmax(m3[s_a:seam + 1])))
            bv = float(b3[seam]) if lab == 'closed-prev' else (
                float(_np.nanmin(b3[s_a:seam + 1])) if sd > 0
                else float(_np.nanmax(b3[s_a:seam + 1])))
            ok3 = p50(mv) or p50(bv)
            rows_.append(('3', ln.U(seam), 'the full ws3 bar %s .. %s before the clause-4 bar '
                          '- ws3Mage %.2f, ws3b %.2f. past counter-side 50 - ws3Mage %s, ws3b %s. '
                          'THE BAR CHOICE IS MINE'
                          % (ln.U(s_a), ln.U(seam), mv, bv,
                             'yes' if p50(mv) else 'NO', 'yes' if p50(bv) else 'NO'),
                          'PASS' if ok3 else 'KILL'))
            if not ok3:
                kill = '3'

        #   clause 5 - ws1b between ws1r's ib cross and the clause-4 cross. BOTH thresholds.
        if kill is None:
            seg = b1[ib1:x4 + 1]
            ext = float(_np.nanmax(seg)) if sd > 0 else float(_np.nanmin(seg))
            v_oob = oob(_np.array([ext]))[0]
            v_exf = exf(_np.array([ext]))[0]
            rows_.append(('5', '%s .. %s' % (ln.U(ib1), ln.U(x4)),
                          "ws1b's %s print in the window is %.2f. same-side oob at %g - %s. "
                          'ex-fence at %g - %s'
                          % ('highest' if sd > 0 else 'lowest', ext,
                             hi_oob if sd > 0 else lo_oob, 'REACHED' if v_oob else 'not reached',
                             hi_f if sd > 0 else lo_f, 'REACHED' if v_exf else 'not reached'),
                          'PASS at oob, %s at ex-fence' % ('KILL' if v_exf else 'PASS')))
            rows_.append(('6', ln.U(x4),
                          'the verdict at the clause-4 bar',
                          'REV-TRADE at the oob threshold, %s at the ex-fence threshold'
                          % ('KILLED' if v_exf else 'REV-TRADE')))

        out += ['', '### the %s read' % lab, '']
        out += head('his clause', 'the bar', 'what the lines did', 'the verdict')
        for c, b, w, v in rows_:
            out.append(row(c, b, w.replace('|', '\\|'), v))
        if kill is not None:
            out.append(row('the outcome', '-', 'clause %s failed' % kill,
                           '**the mech is KILLED**'))
    return out


def runs_table(LN, name, side, A, B):
    """Every ex-20/80 run and every oob run of one line in a span, both reads. -> [str].

    HIS 1108: *"I need the range where ws3r is ex-20/80-fence to understand your data"*. A RANGE,
    not a crossing list - the entry bar, the exit bar, how long it held and the side extreme inside
    it, so a clause that fires mid-run can be placed against the run that contains it.

    A run that is still open at `B` is printed with its exit as "open at <B>", because its real end
    is a bar past the span and reading it would be reading past the question.
    """
    import numpy as _np
    sd = int(side)
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    tf = int(''.join(c for c in name if c.isdigit()) or 1)
    base = name[len(('ws%d' % tf)):] or 'r'
    if base == 'r':
        cp, em = LN['CPR'][tf], LN['EMR'][tf]
    elif base == 'Mage':
        cp, em = LN['CPM'][tf], LN['MGE'][tf]
    elif base == 'b' and tf == 1:
        cp = em = LN['B1']
    else:
        raw = _np.asarray(ln.line(name), float)
        cp, em = CP.series(raw, tf * 60), raw
    out = ['| the read | value |', '|---|---|']
    out.append(row('the line', name))
    out.append(row('the span', '%s .. %s - %d bars = %.1f min'
                   % (ln.U(int(A)), ln.U(int(B)), int(B) - int(A) + 1,
                      (int(B) - int(A) + 1) * 5 / 60.0)))
    out.append(row('the side', 'HIGH' if sd > 0 else 'LOW'))
    out.append(row('ex-20/80-fence', 'at or past %g' % (hi_f if sd > 0 else lo_f)))
    out.append(row('oob', 'at or past %g' % (K.OOB_HI if sd > 0 else K.OOB_LO)))
    out += ['', '| the read | the state | the run opens | the run closes | bars | minutes | '
            'the side extreme in it | at |', '|---|---|---|---|---|---|---|---|']
    for lab, ser in (('closed-prev', cp), ('emerging', em)):
        v = _np.asarray(ser, float)
        for tag, thr in (('ex-20/80', hi_f if sd > 0 else lo_f),
                         ('oob', K.OOB_HI if sd > 0 else K.OOB_LO)):
            st = (v >= thr) if sd > 0 else (v <= thr)
            i = int(A)
            while i <= int(B):
                if not st[i]:
                    i += 1
                    continue
                j = i
                while j < int(B) and st[j + 1]:
                    j += 1
                seg = v[i:j + 1]
                ext = float(_np.nanmax(seg)) if sd > 0 else float(_np.nanmin(seg))
                at = i + int(_np.nanargmax(seg) if sd > 0 else _np.nanargmin(seg))
                out.append(row(lab, tag, ln.U(i),
                               ln.U(j) if j < int(B) else 'open at %s' % ln.U(int(B)),
                               j - i + 1, '%.1f' % ((j - i + 1) * 5 / 60.0),
                               '%.2f' % ext, ln.U(at)))
                i = j + 1
    return out


def vals_table(LN, names, side, A, B):
    """One row per 5 s bar: each named line's closed-prev and emerging value. -> [str].

    HIS 1108: *"print me a table of closed-prev and emerging values between 0824 and 0828"*. Raw
    values, one bar per row, with the oob and ex-fence flags beside each so a threshold crossing is
    readable without arithmetic.
    """
    import numpy as _np
    sd = int(side)
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    oob_t = float(K.OOB_HI) if sd > 0 else float(K.OOB_LO)
    exf_t = hi_f if sd > 0 else lo_f
    SER = []
    for nm in names:
        tf = int(''.join(c for c in nm if c.isdigit()) or 1)
        base = nm[len('ws%d' % tf):] or 'r'
        if base == 'r':
            SER.append((nm, _np.asarray(LN['CPR'][tf], float), _np.asarray(LN['EMR'][tf], float)))
        elif base == 'Mage':
            SER.append((nm, _np.asarray(LN['CPM'][tf], float), _np.asarray(LN['MGE'][tf], float)))
        elif base == 'b' and tf == 1:
            SER.append((nm, _np.asarray(LN['B1'], float), _np.asarray(LN['B1'], float)))
        else:
            raw = _np.asarray(ln.line(nm), float)
            SER.append((nm, _np.asarray(CP.series(raw, tf * 60), float), raw))
    out = ['| the read | value |', '|---|---|']
    out.append(row('the lines', ', '.join(names)))
    out.append(row('the span', '%s .. %s - %d bars' % (ln.U(int(A)), ln.U(int(B)),
                                                       int(B) - int(A) + 1)))
    out.append(row('the side', 'HIGH' if sd > 0 else 'LOW'))
    out.append(row('oob', 'at or past %g' % oob_t))
    out.append(row('ex-20/80-fence', 'at or past %g' % exf_t))
    hdr = ['the bar']
    for nm, _, _ in SER:
        hdr += ['%s closed-prev' % nm, 'oob', 'ex-fence', '%s emerging' % nm, 'oob', 'ex-fence']
    out += ['', row(*hdr), row(*(['---'] * len(hdr)))]
    for i in range(int(A), int(B) + 1):
        cells = [ln.U(i)]
        for nm, cp, em in SER:
            for v in (cp[i], em[i]):
                hit_o = (v >= oob_t) if sd > 0 else (v <= oob_t)
                hit_e = (v >= exf_t) if sd > 0 else (v <= exf_t)
                cells += ['%.2f' % v, 'OOB' if hit_o else '.', 'EXF' if hit_e else '.']
        out.append(row(*cells))
    return out
