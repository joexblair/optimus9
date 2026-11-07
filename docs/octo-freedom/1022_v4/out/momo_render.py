"""ONE copy of every fdm2 debugging table. Imported by the live process AND by the one-shot runs.

HIS 1106: *"every single event cached in a table or memory, instead of re-deriving"*. The renderers
live here so the live process and a one-shot script cannot drift apart - a second copy of a report
is where two answers to the same question come from.

Every table follows his format: one record per row, markdown, timestamps carry the date, a figure
never sits in prose, and a per-row MAE/MFE table always carries its aggregate underneath.
"""
import hashlib
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K        # noqa: E402
import v4_fdm2 as F2        # noqa: E402
import v4_closed_prev as CP # noqa: E402
import ln                   # noqa: E402
from optimus9.analysis import jig as JIG   # noqa: E402


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
    out.append(row('the stop', 'FDM_MAE_CAP %.2f%% adverse from the open, carried by every number '
                               'below' % float(K.FDM_MAE_CAP)))
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
    out.append(row('drag %', '-%.3f (0.1975%% round trip x %d legs)' % (0.1975 * len(LG), len(LG))))
    out.append(row('net %', '%+.3f' % (sum(rel) - 0.1975 * len(LG))))
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

    for lab in ('closed-prev', 'emerging'):
        r1 = _np.asarray(LN['CPR'][1] if lab == 'closed-prev' else LN['EMR'][1], float)
        r3 = _np.asarray(LN['CPR'][3] if lab == 'closed-prev' else LN['EMR'][3], float)
        m3 = _np.asarray(LN['CPM'][3] if lab == 'closed-prev' else LN['MGE'][3], float)
        b3 = _np.asarray(CP.series(w3b, 3 * 60) if lab == 'closed-prev' else w3b, float)
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

        #   clause 2 - ws3r reaches oob after ws1r's ib cross, with no print past counter-side 50
        oob3bar = None
        if kill is None:
            o3, p3 = oob(r3), p50(r3)
            j, bad = ib1, None
            while j < len(r3) - 1 and not o3[j]:
                if p3[j] and bad is None:
                    bad = j
                j += 1
            if not o3[j]:
                rows_.append(('2', '-', 'ws3r does not reach oob after %s' % ln.U(ib1), 'KILL'))
                kill = '2'
            elif bad is not None:
                rows_.append(('2', ln.U(bad), 'ws3r printed %s 50 at %.2f before reaching oob'
                              % ('below' if sd > 0 else 'above', r3[bad]), 'KILL'))
                kill = '2'
            else:
                oob3bar = j
                rows_.append(('2', ln.U(j), 'ws3r reaches oob at %.2f, with no print past '
                              'counter-side 50 from %s' % (r3[j], ln.U(ib1)), 'PASS'))

        #   clause 4 - ws3r crosses to in-20/80-fence. Taken BEFORE clause 3, because clause 3's
        #   bar is defined relative to this cross - his *"the full TF bar before the cross"*.
        x4 = None
        if kill is None:
            e3 = exf(r3)
            j = oob3bar
            while j < len(r3) - 1 and e3[j]:
                j += 1
            if e3[j]:
                rows_.append(('4', '-', 'ws3r never crosses to in-%g/%g before the tape ends'
                              % (lo_f, hi_f), 'KILL'))
                kill = '4'
            else:
                x4 = j
                rows_.append(('4', ln.U(j), 'ws3r crosses to in-%g/%g at %.2f'
                              % (lo_f, hi_f, r3[j]), 'PASS'))

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
            rows_.append(('3', ln.U(seam), 'the full ws3 bar %s .. %s - ws3Mage %.2f, ws3b %.2f. '
                          'past counter-side 50 - ws3Mage %s, ws3b %s. THE BAR CHOICE IS MINE'
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
