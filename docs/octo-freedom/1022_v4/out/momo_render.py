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
             c5_oob=None, c5_exf=None, ret=None, fires=False, why={})

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
                                    'direction, from the firing bar + 2 bars to its FDM_MAE_CAP '
                                    '%.2f%% stop. MY CHOICE, he did not rule it' % float(K.FDM_MAE_CAP)))
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
    out += head('the firing bar', 'the side it fired on', 'branch', 'the OUTGOING trade',
                'it opens at', 'the open price', 'the exit', 'the exit kind', 'held min',
                'MAE %', 'MFE %', 'realised %', 'MFE over MAE')
    mae_l, mfe_l, rel_l = [], [], []
    for q, sd, E in sorted(fired):
        sig = int(E['x4'])
        opn = sig + 2
        osd = -sd                     # the outgoing trade hunts the opposite side
        if opn > int(B):
            out.append(row(ln.U(sig), 'HIGH' if sd > 0 else 'LOW', E['branch'],
                           'SHORT' if osd < 0 else 'LONG', 'past the span', '-', '-', '-', '-',
                           '-', '-', '-', '-'))
            continue
        cap = float(K.FDM_MAE_CAP)
        sb = F2.stop_bar(LN, opn, int(B), osd, cap)
        ex = int(sb) if sb is not None else int(B)
        op = float(close[opn])
        adv = (plo if osd > 0 else phi)[opn:ex + 1]
        fav = (phi if osd > 0 else plo)[opn:ex + 1]
        ap = osd * (adv - op) / op * 100.0
        fp = osd * (fav - op) / op * 100.0
        mae = min(abs(float(_np.nanmin(ap))), cap)
        mfe = float(_np.nanmax(fp))
        rel = -cap if sb is not None else osd * (float(close[ex]) - op) / op * 100.0
        mae_l.append(mae)
        mfe_l.append(mfe)
        rel_l.append(rel)
        out.append(row(ln.U(sig), 'HIGH' if sd > 0 else 'LOW', E['branch'],
                       'SHORT' if osd < 0 else 'LONG', ln.U(opn), '%.6f' % op, ln.U(ex),
                       'STOP at %.2f%%' % cap if sb is not None else 'still open at the span end',
                       '%.1f' % ((ex - opn) * 5 / 60.0), '%.3f' % mae, '%+.3f' % mfe,
                       '%+.3f' % rel, '%.2f' % (mfe / mae) if mae > 0 else 'nan'))
    if not fired:
        out.append(row(*(['none'] + ['-'] * 12)))
    else:
        out += ['', '| the aggregate, every number carrying the FDM_MAE_CAP %.2f%% stop | value |'
                % float(K.FDM_MAE_CAP), '|---|---|']
        out.append(row('arms evaluated', len(rows_)))
        out.append(row('firings', '%d of %d arms = %.1f%%'
                       % (len(fired), len(rows_), len(fired) / len(rows_) * 100.0)))
        out.append(row('killed at clause 1 / 2 / 3 / 4 / 5',
                       ' / '.join(str(sum(1 for _, _, E in rows_ if E['kill'] == c))
                                  for c in '12345')))
        out.append(row('outgoing trades scored', len(mae_l)))
        out.append(row('that stopped', sum(1 for r in rel_l if r <= -float(K.FDM_MAE_CAP))))
        out.append(row('MAE %, median', '%.3f' % float(_np.median(mae_l))))
        out.append(row('MFE %, median', '%+.3f' % float(_np.median(mfe_l))))
        out.append(row('MFE %, total', '%+.3f' % sum(mfe_l)))
        out.append(row('realised %, median', '%+.3f' % float(_np.median(rel_l))))
        out.append(row('realised %, total', '%+.3f' % sum(rel_l)))
        out.append(row('MFE over MAE, median',
                       '%.2f' % float(_np.median([f / m for f, m in zip(mfe_l, mae_l) if m > 0]))))
        out.append(row('drag %', '-%.3f (0.1975%% round trip x %d)'
                       % (0.1975 * len(rel_l), len(rel_l))))
        out.append(row('net %', '%+.3f' % (sum(rel_l) - 0.1975 * len(rel_l))))
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
