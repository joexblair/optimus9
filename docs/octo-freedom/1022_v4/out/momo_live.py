"""The live fdm2 process: load the arrays ONCE, then answer debugging queries in seconds.

HIS 1106 GO: *"that's definietly the goal - every single event cached in a table or memory, instead
of re-deriving"* / *"yes thanks"*.

WHY IT EXISTS, measured rather than assumed: a one-shot debugging table spends almost all of its
time in F2.load() and _momo_lines() building whole-tape arrays, and NONE of that shrinks when the
leg's open bar is handed in - the leg walk already starts at the open. Holding the arrays is the
only change that moves the number.

THE PROTOCOL IS FILES, not a socket or a port - nothing to bind, nothing to leak:

    <DIR>/req/<id>.json     {"kind": "...", ...}        written by the caller
    <DIR>/out/<id>.md       the answer, markdown         written here
    <DIR>/out/<id>.done     written LAST, so a reader never sees a half-written answer
    <DIR>/READY             written once the arrays are up, with the load timings

THE KINDS:

    day      {"day": "2026-08-23"}                     the day's legs + the cad walk summary
    leg      {"day": ..., "open": "YYYY-MM-DD HH:MM:SS"}   one leg's every timestamped event
    cadwalk  {"day": ..., "b0": "YYYY-MM-DD HH:MM:SS"}     one cad walk, bar by bar
    knobs    {}                                        every banked knob, its value and its gloss
    reload   {}                                        re-import the knobs and fdm2 WITHOUT
                                                       touching the tape, so a knob edit costs
                                                       seconds instead of a full rebuild
    stop     {}                                        exit

EVERY ANSWER CARRIES ITS PROVENANCE: the bar count, the hash over all banked knobs, and which
knobs sit off the bank. A cached answer that cannot say which knob set produced it is the exact
fault that made a leg report replay a superseded arm.

THE DAY'S CHAIN IS MEMOISED per (day, knob hash). A knob change changes the hash, so the next
query recomputes instead of serving a stale chain - the staleness is designed out rather than
remembered.
"""
import bisect as _bisect
import importlib
import io
import json
import os
import sys
import time
import traceback

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.environ.setdefault('W_V4_EXPERIMENT', '1')

DIR = os.environ.get('W_LIVE_DIR', '/home/joe/.claude/jobs/7c82535c/tmp/live')
for d in ('req', 'out'):
    os.makedirs(os.path.join(DIR, d), exist_ok=True)

T = {}
t0 = time.time()
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_signal as SG
    import v4_fdm_reentry as RE
    import ln
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import momo_render as R
    import re_sigcache as SC
finally:
    sys.stderr = _e
T['the imports'] = time.time() - t0

t = time.time()
LN = F2.load()
T['F2.load - the tape and every line array'] = time.time() - t
t = time.time()
M = F2._momo_lines(LN)
T['_momo_lines - the x and m ladders, the r-pred flags and the pinned masks'] = time.time() - t
t = time.time()
#   THE SIGNAL LIST COMES FROM THE KEYED CACHE. Measured: the scan is 1,484.7 s of a 1,532.2 s
#   cold start - 96.9% - and its answer only changes when one of the 32 re-entry knobs or one of
#   its input arrays changes. The key carries both, so a hit cannot be stale.
SIGS, SCI = SC.load_or_build(K, RE, LN['B1'], LN['CPR'], LN['G30B'], LN['EMR'], LN['CPM'])
T['the re-entry signals - %s' % ('a CACHE HIT, key %s' % SCI['key'] if SCI['hit']
                                 else 'a cache MISS, scanned and saved under key %s' % SCI['key'])
  ] = time.time() - t
LOADED = time.time() - t0

CHAIN = {}          # (day, knob hash) -> (the legs, the cad walk trace)


def chain(day):
    """The day's legs and cad walk trace, memoised on (day, the knob hash). -> (LG, TR)."""
    h, _ = R.knob_hash()
    key = (day, h)
    if key in CHAIN:
        return CHAIN[key]
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    hit = [x for x in SIGS if int(x['bar']) >= A]
    assert hit, 'no fdm re-entry signal at or after %s' % ln.U(A)
    g = hit[0]
    F2.XCAD_TRACE = []
    LG = F2.legs(LN, (SG.fire_bar(g), SG.target_side(SG.direction(int(g['side']))),
                      'fdm re-entry %s' % ln.U(int(g['bar']))), B, resig=SIGS)
    TR = list(F2.XCAD_TRACE)
    F2.XCAD_TRACE = None
    CHAIN[key] = (LG, TR)
    return CHAIN[key]


def answer(q):
    """One request -> the markdown answer. -> [str]."""
    kind = str(q.get('kind', ''))
    out = R.stamp(LN)
    if kind == 'knobs':
        out += ['', '# every banked knob, its live value and what it sets', '']
        out += R.head('the knob = its value', 'in the bank', 'the ruled value')
        for n in sorted(K.RULED):
            v = getattr(K, n, None)
            out.append(R.row('%s = %s' % (n, v),
                             'yes' if str(v) == str(K.RULED[n][0]) else 'OFF THE BANK',
                             K.RULED[n][0]))
        return out
    if kind == 'stages':
        #   HIS 1106: *"cadence event can only produce cad_walk or cad_rev-trade - there is no
        #   third option... where is the gap?"*. This counts every verdict row the day produced,
        #   by label, and names the bar each one landed on relative to its own cadence event - so a
        #   verdict that did not land ON the cadence event is visible as such.
        day = str(q['day'])
        LG, TR = chain(day)
        cnt, late = {}, []
        for L in LG:
            for r in L['rows']:
                st = str(r['stage'])
                cnt[st] = cnt.get(st, 0) + 1
                if st.startswith('cad_') and int(r.get('ev', r['bar'])) != int(r['bar']):
                    late.append((int(r['ev']), int(r['bar']), st, str(r['why'])))
        out += ['', '# every verdict row on %s, by label' % day, '']
        out += R.head('the label', 'rows', 'whose verdict it is', 'is it one of your two')
        OWN = {'cad_walk': ('the cadence event', 'yes - walk'),
               'cad_rev_trade': ('the cadence event', 'yes - rev-trade'),
               'cad_no_action': ('the cadence event', 'NO - a THIRD verdict'),
               'cwlk_seam': ('the cad walk', 'neither - a setup row'),
               'cwlk_start': ('the cad walk', 'neither - a setup row'),
               'cwlk_momo_vote': ('the cad walk', 'neither - a vote row'),
               'cwlk_rev_trade': ('the cad walk', 'yes - rev-trade')}
        for st in sorted(cnt):
            w, y = OWN.get(st, ('?', '?'))
            out.append(R.row(st, cnt[st], w, y))
        out += ['', '# every cadence-event verdict that did NOT land on its own cadence event bar',
                '']
        out += R.head('the cadence event', 'the bar the verdict landed on', 'seconds late',
                      'the label', 'why')
        for ev, b, st, why in sorted(late):
            out.append(R.row(ln.U(ev), ln.U(b), (b - ev) * 5, st, why.replace('|', '\\|')[:160]))
        if not late:
            out.append(R.row('none', '-', '-', '-', '-'))
        return out
    if kind == 'c3rmage':
        #   HIS 1108 item 10: *"I want to see what improvements we get from opening a c3r trade at
        #   the ws1Mage reversal. I'm not sure if ws1Mage needs to be oob or ib or ex fence or in
        #   fence. it will be good to find out"*.
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        lab = str(q.get('read', 'ws3r emerging, rest closed-prev'))
        out += ['', '# c3r opened at the ws1Mage reversal, %s to %s'
                % (str(q['from']), str(q['to'])), '']
        out += R.c3rmage_table(LN, A, B, lab)
        return out
    if kind == 'tawaway':
        #   HIS 1108: *"show the towards/away data at 0551, for ws10 to ws30. add a column that
        #   tells how long an away line has been printing away"*.
        #   THE SAME READ THE CAD WALK USES. exf_passed calls JIG.fdm2_cad_mom_detector on
        #   LN['EMR'][t] with the cadence window's own s0, the LIFT_* knobs, the lift-off stamp
        #   gate and rev_since - FDM_XCAD_REV_FROM 'window' puts rev_since at s0. Reproduced here
        #   bar for bar so the two cannot disagree.
        import numpy as _np
        from optimus9.analysis import jig as _JIG
        at = ln.K(str(q['at']))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        ev = ln.K(str(q['ev']))
        s0 = ln.K(str(q['s0']))
        TFS = list(range(int(q.get('hi', 30)), int(q.get('lo', 10)) - 1, -1))
        rs = int(s0) if str(K.FDM_XCAD_REV_FROM) == 'window' else None
        to_read = str(K.FDM_XCAD_REV_TO) == 'read'
        gate = {t: (_np.asarray(LN['LIFT'][(t, int(sd))], int) if to_read
                    else _np.asarray([b for b in LN['LIFT'][(t, int(sd))]
                                      if (rs if rs is not None else 0) <= b <= int(ev)], int))
                for t in TFS}

        def state(t, b):
            return _JIG.fdm2_cad_mom_detector(LN['EMR'][t], LN['EMR'][t], int(b), int(sd),
                                              int(s0), K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                                              K.LIFT_WOB, stamps=gate[t], rev_since=rs)['state']
        out += ['', '# towards / away at %s, %s side. The cadence event %s, its window opens %s'
                % (ln.U(at), q.get('side', 'HIGH'), ln.U(ev), ln.U(s0)), '']
        out += ['| the line | the state at %s | ex-20/80 there | its r value | how long it has held '
                'that state | since |' % ln.U(at), '|---|---|---|---|---|---|']
        for t in TFS:
            st = state(t, at)
            #   HOW LONG: walk BACK bar by bar while the state is unchanged. NO CAP - it runs to
            #   the cadence window's open and reports that it reached it, rather than inventing a
            #   lookback. Every bar it reads is at or before `at`.
            b = int(at)
            while b - 1 >= int(s0) and state(t, b - 1) == st:
                b -= 1
            n = int(at) - b + 1
            hit = (b > int(s0))
            out.append('| ws%dr | %s | %s | %.2f | %d bars = %.1f min | %s |'
                       % (t, st,
                          'EXF' if F2.ex2080_line(LN, t, int(at), int(sd)) else '.',
                          float(LN['EMR'][t][int(at)]), n, n * 5 / 60.0,
                          ln.U(b) if hit else 'the window open %s or earlier' % ln.U(int(s0))))
        out += ['']
        sts = [state(t, at) for t in TFS]
        out.append(R.row('towards', '%d of %d' % (sts.count('towards'), len(TFS))))
        out.append(R.row('away', '%d of %d' % (sts.count('away'), len(TFS))))
        out.append(R.row('neither', '%d of %d' % (len(TFS) - sts.count('towards')
                                                  - sts.count('away'), len(TFS))))
        hits = [t for t in TFS if state(t, at) == 'towards'
                and F2.ex2080_line(LN, t, int(at), int(sd))]
        out.append(R.row('towards AND ex-20/80 - the 4-pronged test over this range',
                         ', '.join('ws%d' % t for t in hits) if hits else 'none'))
        out.append(R.row('the knobs', 'FDM_XCAD_REV_FROM %s, FDM_XCAD_REV_TO %s, LIFT_PTS %d, '
                                      'LIFT_TOL %g, LIFT_WOB %d'
                         % (K.FDM_XCAD_REV_FROM, K.FDM_XCAD_REV_TO, int(K.LIFT_PTS),
                            float(K.LIFT_TOL), int(K.LIFT_WOB))))
        out.append(R.row('the range read', 'ws%d..ws%d - HIS ASK. The cad walk\'s own test reads '
                                           'ws%d..ws%d' % (TFS[-1], TFS[0],
                                                           int(K.FDM_STEP1_ABOVE_TF) + 1,
                                                           int(LN['HI']))))
        return out
    if kind == 'xcvdiff':
        #   HIS 1108: *"show the 'xcross validator report · HIGH' report that created the up
        #   verdict at 0551. show also the report at 0535"*. The 0535 block is in the report FILE;
        #   the 0551 block is a cad-walked bar and the file has no report for it, so this prints
        #   the same four rows for any (extremum, read bar) pair.
        import numpy as _np
        tf = int(q.get('tf', 5))
        ext = ln.K(str(q['ext']))
        at = ln.K(str(q['at']))
        lab = str(q.get('label', 'cross'))
        #   HIS 1108: *"for the cad walk only: instead of anchoring on the pre-x-cross extremum,
        #   anchor on the x-cross values"*. So the first row's label is the CALLER'S - it is the
        #   extremum for the report's own block and the x-cross for a cad-walked bar - and the diff
        #   row names whichever one was handed in. A row labelled `extremum` while holding the
        #   cross's values is the kind of label that outlives the rule it described.
        alab = str(q.get('anchor', 'ws%dx high extremum' % tf))
        TFS = list(range(30, 9, -1))
        EM = LN['EMR']
        out += ['', '# ws%dx, the extremum %s against %s (%s)'
                % (tf, ln.U(ext), ln.U(at), lab), '']
        hdr = ['line · timestamp'] + ['ws%d' % t for t in TFS]
        out += ['| ' + ' | '.join(hdr) + ' |', '|' + '---|' * len(hdr)]
        e = ['%.2f' % float(EM[t][ext]) for t in TFS]
        a = ['%.2f' % float(EM[t][at]) for t in TFS]
        d = [float(EM[t][at]) - float(EM[t][ext]) for t in TFS]
        out.append('| r · %s (%s) | %s |' % (ln.U(ext), alab, ' | '.join(e)))
        out.append('| r · %s (%s) | %s |' % (ln.U(at), lab, ' | '.join(a)))
        out.append('| r · ws%dx diff (%s - %s) | %s |'
                   % (tf, lab, alab.replace('ws%dx high ' % tf, '').replace('ws%dx low ' % tf, ''),
                      ' | '.join('%+.2f' % x for x in d)))
        out.append('| r · ws%dx direction of the diff | %s |'
                   % (tf, ' | '.join('up' if x > 0 else 'down' if x < 0 else 'flat' for x in d)))
        L4 = d[:4]
        u = sum(1 for x in L4 if x > 0)
        dn = sum(1 for x in L4 if x < 0)
        out += ['']
        out.append(R.row('the 4 lefthand TFs, ws30 ws29 ws28 ws27',
                         ' '.join('up' if x > 0 else 'down' if x < 0 else 'flat' for x in L4)))
        out.append(R.row('ups / downs / flats of those 4', '%d / %d / %d' % (u, dn, 4 - u - dn)))
        out.append(R.row('the 3-of-4 read',
                         'up' if u >= 3 else 'down' if dn >= 3 else 'none'))
        return out
    if kind == 'xcv':
        #   HIS 1108 `fdm2-xcv` TABLE, with his two new columns. His spec: one x line
        #   `ws{knob:5}x`, the race started at the cadence WINDOW OPEN, bounded by the next cadence
        #   event on either side, the FDM_X10_WOB hold restored - *"ok - that makes the wob
        #   necessary"* - and the pre-cross extremum from jig.mage_cascade_bar.
        #   THE TWO NEW COLUMNS, his words: *"1) the cad-walked timestamp when 3 ups or 3 downs
        #   print after a 'none' 3of4 read, 2) the up/down verdict"*, and *"if the 3-of-4 read is
        #   not none for a row, the fields in the new columns will read '-'"*.
        import numpy as _np
        from optimus9.analysis import jig as _JIG
        tf = int(q.get('tf', 5))
        day = str(q['day'])
        A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
        NB = len(LN['close']) - 1
        TFS = list(range(30, 9, -1))
        LEFT = (30, 29, 28, 27)
        X = F2.x_of(LN, tf)
        EM = LN['EMR']
        #   EVERY cadence event bar on the tape, both sides - the race bound is the next one on
        #   either side, his *"the next {any_}cadence"*.
        allcad = sorted(set(int(e[0]) for sd2 in (+1, -1)
                            for e in F2.cadence_events(LN, sd2, 0, NB)))

        def bound(ev):
            i = _bisect.bisect_right(allcad, int(ev))
            return allcad[i] if i < len(allcad) else NB

        def dirs(ext, bar):
            out2 = []
            for t in LEFT:
                d = float(EM[t][int(bar)]) - float(EM[t][int(ext)])
                out2.append('up' if d > 0 else 'down' if d < 0 else 'flat')
            return out2

        def read34(c):
            u, d = c.count('up'), c.count('down')
            return 'up' if u >= 3 else 'down' if d >= 3 else 'none'

        ev = []
        for sd2 in (+1, -1):
            for e in F2.cadence_events(LN, sd2, A, B):
                ev.append((int(e[0]), sd2, int(e[1])))
        out += ['', '# fdm2-xcv, ws%dx, %s' % (tf, day), '']
        out += ['| # | the cadence event | side | the ws%dx extremum | the ws%dx cross | his branch '
                '| ws30 ws29 ws28 ws27 | the 3-of-4 read | the cad-walked timestamp | the verdict |'
                % (tf, tf), '|---|---|---|---|---|---|---|---|---|---|']
        n = 0
        for b, sd2, s0 in sorted(ev):
            n += 1
            r = F2.x_race(LN, tf, sd2, int(s0) - 1, bound(b))
            if r is None:
                out.append('| %d | %s | %s | - | NONE | goto START | - | NO ROWS | - | - |'
                           % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW'))
                continue
            cf, which, c = r
            Mx = _JIG.mage_cascade_bar(X, int(c), int(sd2), mode='extrema',
                                       gap=int(_JIG.MC_GAP))
            if Mx is None:
                out.append('| %d | %s | %s | none | %s | - | - | NO EXTREMUM | - | - |'
                           % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW', ln.U(int(c))))
                continue
            ext = int(Mx[0])
            d4 = dirs(ext, int(c))
            v = read34(d4)
            br = ('1 - inside the window' if int(c) <= int(b) else '2 - the x-cross won')
            #   HIS CAD WALK, and HIS 1108 ANCHOR RULING: *"for the cad walk only: instead of
            #   anchoring on the pre-x-cross extremum, anchor on the x-cross values"*. So the
            #   report's own block still reads cross - extremum, and the cad walk reads
            #   the current bar - THE CROSS. The anchor is `c`, not `ext`.
            #   NO BOUND IS APPLIED: he has not ruled one here, so the cad walk runs to the tape
            #   end and the delay is reported beside it. A bound can only cut rows, never add them.
            cw, cv = '-', '-'
            if v == 'none':
                for t2 in range(int(c) + 1, NB + 1):
                    vv = read34(dirs(int(c), t2))
                    if vv != 'none':
                        cw, cv = ln.U(t2), vv
                        break
                else:
                    cw, cv = 'never to the tape end', 'none'
            out.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s |'
                       % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW', ln.U(ext), ln.U(int(c)), br,
                          ' '.join(d4), v, cw, cv))
        return out
    if kind == 'xdiag':
        #   HIS 1108: *"what exactly happens at the timestamps in 'the x line with no cross'?"*.
        #   Every CROSS CANDIDATE in the span and why it did not become the race's cross - the
        #   three arms of F2.x_race, reported rather than decided.
        import numpy as _np
        tf = int(q['tf'])
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        w = max(1, int(K.FDM_X10_WOB))
        X = F2.x_of(LN, tf)
        #   NOT `R` and `M`: `R` is the module-level momo_render import, and assigning it here
        #   makes it a local for the WHOLE answer() body, so every other kind's `R.stamp(LN)`
        #   raises UnboundLocalError. Python decides that at compile time, not at the assignment.
        Rr, Mm = LN['CPR'][tf], LN['CPM'][tf]
        out += ['', '# ws%dx race candidates, %s side, %s .. %s'
                % (tf, q.get('side', 'HIGH'), str(q['from']), str(q['to'])), '']
        out += ['| the arm | the candidate bar | ws%dx there | the racer there | what happened |' % tf,
                '|---|---|---|---|---|']
        n = 0
        for c, cf, s2 in F2.oob_ib_cross(X, K.OOB_HI, K.OOB_LO, w):
            if int(s2) != sd or int(c) < int(A) or int(c) > int(B):
                continue
            n += 1
            out.append('| ib | %s | %.2f | the %g/%g oob fence | crosses oob to ib, confirms %s - %s |'
                       % (ln.U(int(c)), float(X[int(c)]), float(K.OOB_HI), float(K.OOB_LO),
                          ln.U(int(cf)),
                          'INSIDE the span' if int(cf) <= int(B) else 'PAST the span end'))
        for nm, other in (('ws%dr' % tf, Rr), ('ws%dMage' % tf, Mm)):
            for i in range(max(1, int(A)), int(B) + 1):
                a, b = X[i - 1], X[i]
                oa, ob = other[i - 1], other[i]
                if not _np.isfinite([a, b, oa, ob]).all():
                    continue
                crossed = (a >= oa and b < ob) if sd > 0 else (a <= oa and b > ob)
                if not crossed:
                    continue
                n += 1
                end = i + w
                if end > len(X) or i + w - 1 > int(B):
                    out.append('| %s | %s | %.2f | %.2f | crosses, but its %d-bar = %d s hold ends '
                               '%s - PAST the span end |'
                               % (nm, ln.U(i), float(X[i]), float(other[i]), w, w * 5,
                                  ln.U(min(i + w - 1, len(X) - 1))))
                    continue
                broke = None
                for j in range(i, end):
                    held = (X[j] < other[j]) if sd > 0 else (X[j] > other[j])
                    if not held:
                        broke = j
                        break
                out.append('| %s | %s | %.2f | %.2f | %s |'
                           % (nm, ln.U(i), float(X[i]), float(other[i]),
                              'crosses and HOLDS all %d bars, confirming %s' % (w, ln.U(i + w - 1))
                              if broke is None else
                              'crosses, but the hold BREAKS at %s - ws%dx %.2f against %.2f'
                              % (ln.U(broke), tf, float(X[broke]), float(other[broke]))))
        if not n:
            out.append('| none | - | - | - | no bar in the span crosses any of the three racers |')
        out.append('')
        out.append('| the span read | value |')
        out.append('|---|---|')
        out.append(R.row('ws%dx over the span' % tf, 'min %.2f, max %.2f'
                         % (float(_np.nanmin(X[int(A):int(B) + 1])),
                            float(_np.nanmax(X[int(A):int(B) + 1])))))
        oobm = (X[int(A):int(B) + 1] >= float(K.OOB_HI)) if sd > 0 \
            else (X[int(A):int(B) + 1] <= float(K.OOB_LO))
        out.append(R.row('bars where ws%dx is same-side oob' % tf,
                         '%d of %d' % (int(oobm.sum()), int(B) - int(A) + 1)))
        out.append(R.row('the hold', '%d bars = %d s, counting the cross bar' % (w, w * 5)))
        return out
    if kind == 'xcross':
        #   HIS 1108: *"using the known cadences (not the fake cadences), apply the xcross
        #   validator mech to 08-25 and confirm you can recreate the same ws5x cross timestamps as
        #   seen in the xcross-validator report"*.
        #   INDEPENDENT REBUILD. This calls F2.cadence_events and F2.x_race directly off the live
        #   tape - it does not import the sandbox script or read its output files. If the two
        #   agree, two separate call sites produced the same bars.
        day = str(q['day'])
        A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
        tf = int(q.get('tf', 5))
        out += ['', '# the ws%dx race from every KNOWN cadence event, %s' % (tf, day), '']
        out += ['| the cadence event | side | the ws%dx cross | which racer | the confirm bar | '
                'the race bound |' % tf, '|---|---|---|---|---|---|']
        ev = []
        for sd in (+1, -1):
            for e in F2.cadence_events(LN, sd, A, B):
                ev.append((int(e[0]), sd))
        NB = len(LN['close']) - 1
        for b, sd in sorted(ev):
            r = F2.x_race(LN, tf, sd, int(b), NB)
            if r is None:
                out.append('| %s | %s | none to the tape end | - | - | %s |'
                           % (ln.U(b), 'HIGH' if sd > 0 else 'LOW', ln.U(NB)))
                continue
            cf, which, cx = r
            out.append('| %s | %s | %s | %s | %s | %s |'
                       % (ln.U(b), 'HIGH' if sd > 0 else 'LOW', ln.U(int(cx)), which,
                          ln.U(int(cf)), ln.U(NB)))
        return out
    if kind == 'legmfe':
        #   HIS 1108: *"can you derive that from sweep-pivots? using a rolling 8 hour window, and
        #   measuring on TF1,2,3 and gcws30 timeframes, what MFE differences can you detect inside
        #   of 08-08 to 08-30?"*
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        tfs = tuple(q.get('tfs') or ('ws1Mage', 'ws2Mage', 'ws3Mage', 'gcws30Mage'))
        out += ['', '# the leg MFE per timeframe, rolling %g h, %s to %s'
                % (float(q.get('win_h', 8.0)), str(q['from']), str(q['to'])), '']
        out += R.legmfe_table(LN, A, B, tfs, float(q.get('win_h', 8.0)),
                              float(q.get('step_h', 1.0)))
        return out
    if kind == 'cadlist':
        #   HIS 1108 CHECK on three c3r rows: *"the low cadence at 0853"*, *"high side cadence at
        #   1226"*, *"the leg ultimately lands on low side 1634 cadence"*. His eyes are a
        #   measurement, so the cadence events are read off F2.cadence_events and listed beside
        #   his quoted times rather than taken on trust either way.
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        out += ['', '# every cadence event, both sides, %s to %s'
                % (str(q['from']), str(q['to'])), '']
        #   THE pxs PRICE AT THE EVENT BAR rides along: his 1108 three rows ask what the outgoing
        #   trade would realise if an opposite-side cadence event closed it, and that needs the
        #   price on the event bar, not just its timestamp.
        import numpy as _np
        _px = _np.asarray(LN['close'], float)
        out += ['| the cadence event | side | the ws1b excursion opened at | pxs at the event bar '
                '| why |', '|---|---|---|---|---|']
        ev = []
        for sd in (+1, -1):
            for e in F2.cadence_events(LN, sd, A, B):
                ev.append((int(e[0]), sd, int(e[1]), str(e[2])))
        for b, sd, s0, why in sorted(ev):
            out.append('| %s | %s | %s | %.6f | %s |'
                       % (ln.U(b), 'HIGH' if sd > 0 else 'LOW', ln.U(s0), float(_px[b]),
                          why.replace('|', '\\|')))
        if not ev:
            out.append('| none | - | - | - | - |')
        return out
    if kind == 'pivstop':
        #   HIS 1108: *"lets see if you can use your research to find a dynamic stop for each
        #   signal"*. The structural stop off the last CONFIRMED price pivot, per c3r firing.
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        lab = str(q.get('read', 'ws3r emerging, rest closed-prev'))
        pcs = tuple(int(x) for x in q.get('gaps', (24, 48, 60)))
        out += ['', '# the structural stop per c3r signal, %s to %s'
                % (str(q['from']), str(q['to'])), '']
        out += R.pivstop_table(LN, A, B, lab, pcs)
        return out
    if kind == 'c3rscan':
        #   HIS 1108: *"we'll need a list of the firings across 08-25 to 08-31 (with maemfe) to
        #   validate the change"* / *"run the 7 day anyway"*.
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        lab = str(q.get('read', 'ws3r emerging, rest closed-prev'))
        out += ['', '# fdm2-3r-cadence, every arm from %s to %s' % (str(q['from']), str(q['to'])),
                '']
        out += R.cad3r_scan(LN, A, B, lab)
        return out
    if kind == 'vals':
        #   HIS 1108: raw per-bar values, both reads, with the oob and ex-fence flags beside each.
        nms = q.get('lines') or [str(q.get('line', 'ws1Mage'))]
        if isinstance(nms, str):
            nms = [x.strip() for x in nms.split(',') if x.strip()]
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        out += ['', '# %s values, %s side, %s .. %s'
                % (', '.join(nms), q.get('side', 'HIGH'), str(q['from']), str(q['to'])), '']
        out += R.vals_table(LN, nms, sd, A, B)
        return out
    if kind == 'runs':
        #   HIS 1108: *"I need the range where ws3r is ex-20/80-fence to understand your data"*.
        nm = str(q.get('line', 'ws3r'))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        out += ['', '# %s ex-20/80 and oob runs, %s side' % (nm, q.get('side', 'HIGH')), '']
        out += R.runs_table(LN, nm, sd, A, B)
        return out
    if kind == 'board':
        #   THE BOARD AT ONE BAR, from v4_fdm2.xcad_probe - the producer the director's own seam
        #   read uses. Not a second implementation: the report and the verdict read the same call.
        bar = ln.K(str(q['at']))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        s0 = ln.K(str(q['since'])) if q.get('since') else bar
        hi = int(LN['HI'])
        pr = F2.xcad_probe(LN, sd, s0, bar, list(range(1, hi + 1)), bar)
        out += ['', '# the board at %s, %s side' % (str(q['at']), q.get('side', 'HIGH')), '']
        out += ['| the read | value |', '|---|---|']
        out.append(R.row('the bar', ln.U(bar)))
        out.append(R.row('the target side', 'HIGH' if sd > 0 else 'LOW'))
        out.append(R.row('the extremum anchor', '%s - the cadence window open, '
                         'FDM_XCAD_REV_FROM %s' % (ln.U(s0), K.FDM_XCAD_REV_FROM)))
        out.append(R.row('ex-fence', 'at or past %g/%g, FDM_EXF_READ %s'
                         % (*K.fnc_pair(K.FDM_FNC_2080), K.FDM_EXF_READ)))
        aw = [z for z in pr if z['state'] == 'away']
        tw = [z for z in pr if z['state'] == 'towards']
        ot = [z for z in pr if z['state'] not in ('away', 'towards')]
        out.append(R.row('away', '%d lines - ws%s' % (len(aw), ', ws'.join(str(z['tf'])
                                                                          for z in aw)) if aw
                         else '0 lines'))
        out.append(R.row('towards', '%d lines - ws%s' % (len(tw), ', ws'.join(str(z['tf'])
                                                                             for z in tw)) if tw
                         else '0 lines'))
        if ot:
            out.append(R.row('neither', '%d lines - ws%s'
                             % (len(ot), ', ws'.join(str(z['tf']) for z in ot))))
        out.append(R.row('ex-fence AND towards', '%d lines - ws%s'
                         % (len([z for z in tw if z['exf']]),
                            ', ws'.join(str(z['tf']) for z in tw if z['exf']))
                         if [z for z in tw if z['exf']] else '0 lines'))
        out += ['', '| the line | its value | its state | ex-fence | the extremum | at | the gap | '
                'its reversal stamp |', '|---|---|---|---|---|---|---|---|']
        for z in pr:
            out.append(R.row('ws%d' % z['tf'], '%.2f' % z['value'], z['state'],
                             'yes' if z['exf'] else 'NO',
                             '%.2f' % z['extremum'] if z['extremum'] is not None else '-',
                             ln.U(int(z['at'])) if z['at'] is not None else '-',
                             '%.2f' % z['gap'] if z['gap'] is not None else '-',
                             ln.U(int(z['rev'])) if z['rev'] is not None else 'none'))
        return out
    if kind == 'legfrom':
        #   HIS 1107: a leg opened at a bar HE names, with a side HE names, walked by the chain's
        #   own v4_fdm2.walk. It is how a hypothetical open - *"an incoming SHORT which would have
        #   opened at high 0730-0733 on fdm-3r-cadence"* - gets tested without inventing a leg.
        opn = ln.K(str(q['open']))
        sd = +1 if str(q.get('dir', 'LONG')).upper() == 'LONG' else -1
        B = ln.K(str(q['to'])) if q.get('to') else len(LN['close']) - 1
        sig, rws = F2.walk(LN, sd, opn, int(B))
        out += ['', '# a %s opened at %s, target side %s, walked to %s'
                % ('LONG' if sd > 0 else 'SHORT', ln.U(opn), 'HIGH' if sd > 0 else 'LOW',
                   ln.U(int(B))), '']
        out += ['| the walk | value |', '|---|---|']
        out.append(R.row('the open', ln.U(opn)))
        out.append(R.row('the target side', 'HIGH' if sd > 0 else 'LOW'))
        out.append(R.row('walked to', ln.U(int(B))))
        out.append(R.row('the rev-trade signal', ln.U(int(sig)) if sig is not None
                         else 'none before the walk ended'))
        out.append(R.row('the decision rows', len(rws)))
        out += ['', '| the bar | min from the open | the event | what it says |',
                '|---|---|---|---|']
        for r in sorted(rws, key=lambda z: (int(z['bar']), str(z['stage']))):
            out.append('| %s | %.1f | %s | %s |'
                       % (ln.U(int(r['bar'])), (int(r['bar']) - opn) * 5 / 60.0,
                          str(r['stage']), str(r['why']).replace('|', '\\|')))
        return out
    if kind == 'cad3r':
        #   HIS 1107 `fdm2-3r-cadence`. A REPORT on his own markers - no leg reads it.
        mk = ln.K(str(q['at']))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        out += ['', '# fdm2-3r-cadence at %s, %s side' % (str(q['at']), q.get('side', 'HIGH')), '']
        out += R.cad3r_table(LN, sd, mk)
        return out
    if kind == 'trail':
        #   HIS 1107 FIVE-CLAUSE SPEC. A raw read at one of his own markers - no mech, no verdict.
        mk = ln.K(str(q['at']))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        out += ['', '# the trail at %s, %s side' % (str(q['at']), q.get('side', 'HIGH')), '']
        out += R.trail_table(LN, sd, mk)
        return out
    if kind == 'window':
        #   HIS 1107 ws3r-opener question. A pure line read in a bar range - no mech, no chain.
        day = str(q['day'])
        A = ln.K(str(q.get('from', day + ' 00:00:00')))
        B = ln.K(str(q.get('to', day + ' 23:59:55')))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        out += ['', '# the oob crosses of ws1b and ws1r, ws2r, ws3r, %s side' % q.get('side'), '']
        out += R.window_table(LN, sd, A, B)
        return out
    if kind == 'pct50':
        #   HIS 1107: *"show me the 50% test table for 0232"*. The cadence event and the
        #   ws{TF}x-cadence are taken from the leg's OWN rows, so the table describes the decision
        #   the chain actually made rather than a pair of bars I chose.
        day = str(q['day'])
        LG, TR = chain(day)
        want = str(q.get('at', ''))
        hit = None
        for L in LG:
            for r in L['rows']:
                if str(r['stage']) == 'cwsx_pct' and (not want or ln.U(int(r['bar'])) == want
                                                      or ln.U(int(r['bar'])).endswith(want)
                                                      or want in ln.U(int(r['bar']))):
                    hit = (L, r)
                    break
            if hit:
                break
        assert hit, 'no 50%% test row matching %r on %s' % (want, day)
        L, r = hit
        ev = int(r['ev'])
        s0 = next(int(z['bar']) for z in L['rows']
                  if str(z['stage']) == 'cad_window_open' and int(z['ev']) == ev)
        out += ['', '# the 50%% test at %s' % ln.U(int(r['bar'])), '']
        out += R.pct50_table(LN, int(L['side']), int(L['opn']), ev, s0, int(r['bar']),
                             'ws%dx to %s' % (int(r.get('xtf') or 0), r.get('which', '?')))
        return out
    if kind == 'day':
        day = str(q['day'])
        LG, TR = chain(day)
        out += ['', '# the legs of %s' % day, '']
        out += R.legs_table(LN, LG)
        out += ['', '# every cad walk on %s, and which branch ended it' % day, '']
        out += R.cadwalk_summary(TR)
        return out
    if kind == 'leg':
        day = str(q['day'])
        LG, TR = chain(day)
        want = [str(x) for x in (q['open'] if isinstance(q['open'], list) else [q['open']])]
        hit = [L for L in LG if ln.U(int(L['opn'])) in want]
        assert hit, 'no leg opens at %s on %s' % (', '.join(want), day)
        for L in hit:
            sd = int(L['side'])
            out += ['', '# the incoming trade %s | %s | target side %s'
                    % (ln.U(int(L['opn'])), 'LONG' if sd > 0 else 'SHORT',
                       'HIGH' if sd > 0 else 'LOW'), '']
            out += R.leg_table(LN, L, SIGS if q.get('resig', True) else None)
            bs = sorted({t['b0'] for t in TR
                         if int(L['opn']) <= t['b0'] <= int(L['exit'])})
            for b0 in bs:
                out += ['', '## its cad walk from %s' % ln.U(b0)]
                out += R.cadwalk_table(TR, b0)
        return out
    if kind == 'cadwalk':
        day = str(q['day'])
        LG, TR = chain(day)
        b0 = ln.K(str(q['b0']))
        assert any(t['b0'] == b0 for t in TR), 'no cad walk starts at %s on %s' % (q['b0'], day)
        out += ['', '# the cad walk from %s, bar by bar' % str(q['b0'])]
        out += R.cadwalk_table(TR, b0)
        return out
    raise AssertionError('unknown kind %r' % kind)


def serve():
    with open(os.path.join(DIR, 'READY'), 'w') as fh:
        fh.write('| the stage | seconds |\n|---|---|\n')
        for k, v in T.items():
            fh.write('| %s | %.1f |\n' % (k, v))
        fh.write('| **the whole load** | **%.1f** |\n' % LOADED)
        fh.write('\n| the arrays | value |\n|---|---|\n')
        fh.write('| the tape | %d bars |\n' % len(LN['close']))
        fh.write('| the ladder timeframes | ws%d..ws%d |\n' % (M['tfs'][0], M['tfs'][-1]))
        fh.write('| the re-entry signals | %d on the tape |\n' % len(SIGS))
        fh.write('| the knob hash | %s |\n' % R.knob_hash()[0])
    print('READY in %.1f s' % LOADED, flush=True)
    while True:
        reqs = sorted(f for f in os.listdir(os.path.join(DIR, 'req')) if f.endswith('.json'))
        if not reqs:
            time.sleep(0.25)
            continue
        for f in reqs:
            rp = os.path.join(DIR, 'req', f)
            i = f[:-5]
            try:
                q = json.load(open(rp))
            except Exception:
                time.sleep(0.1)
                continue
            os.remove(rp)
            t1 = time.time()
            if str(q.get('kind')) == 'stop':
                print('STOP', flush=True)
                return
            if str(q.get('kind')) == 'reload':
                #   THE TAPE IS NOT RELOADED. LN is plain arrays and dicts, so the re-imported
                #   module reads the same data; only the code and the knobs move. _MOMO is rebuilt
                #   because the module-level cache resets, and the memoised chains are dropped
                #   because their knob hash may now be wrong.
                globals()['K'] = importlib.reload(K)
                globals()['F2'] = importlib.reload(F2)
                globals()['R'] = importlib.reload(R)
                assert set(LN) >= {'close', 'CPR', 'EMR', 'MGE', 'CPM', 'HI'}, \
                    'load() contract changed - the held arrays are no longer valid'
                globals()['M'] = F2._momo_lines(LN)
                CHAIN.clear()
                body = R.stamp(LN) + ['', 'reloaded the knobs and fdm2 in %.1f s, the tape was not '
                                      'touched, %d memoised chains dropped'
                                      % (time.time() - t1, 0)]
            else:
                try:
                    body = answer(q)
                except Exception:
                    body = ['```', traceback.format_exc(), '```']
            body.append('')
            body.append('_answered in %.2f s_' % (time.time() - t1))
            with open(os.path.join(DIR, 'out', i + '.md'), 'w') as fh:
                fh.write('\n'.join(body) + '\n')
            with open(os.path.join(DIR, 'out', i + '.done'), 'w') as fh:
                fh.write('%.2f\n' % (time.time() - t1))
            print('%s %s in %.2f s' % (i, q.get('kind'), time.time() - t1), flush=True)


serve()
