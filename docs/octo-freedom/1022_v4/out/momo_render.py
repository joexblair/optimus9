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
import ln                   # noqa: E402


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
    out += ['', '| the bar | min from the open | the event | what it says |', '|---|---|---|---|']
    for b, stage, why in sorted(EV, key=lambda z: (z[0], z[1])):
        out.append('| %s | %.1f | %s | %s |'
                   % (ln.U(int(b)), (int(b) - o) * 5 / 60.0, stage, why.replace('|', '\\|')))
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
