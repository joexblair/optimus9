"""`fdm2-xcv`'s reporting: the six readings the live process routes to, and nothing else.

ITS ONE JOB: build the lines for one `fdm2-xcv` reading from `LN` and the caller's plain values.
It parses no request, it holds no state, and it decides nothing - a caller hands in the bars and
the labels, and a list of markdown lines comes back.

WHY IT EXISTS - the fault it removes, measured on 1108: these six readings lived inside the live
process's single routing function, 317 of its 577 lines. One of them assigned a local named `R`,
which Python binds at compile time, so the module-level render import became a local for the WHOLE
function and every other reading's `R.stamp(LN)` raised UnboundLocalError until it was called.
Commit `08f89c1` renamed the local; this module removes the arrangement that allowed it.

THE RULE: a builder takes `LN` and plain values. It never takes the request dict, and it never
assigns a one-letter name that an import already holds.

HIS 1108 GO: *"re the SRP - I'm sure you want to make that clean - set up a SRP plan to make your
house pretty, then apply it"*. The plan and the byte-identical proof are in
`docs/octo-freedom/1108_srp_live.md`.
"""
import bisect as _bisect
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')

import ln
import v4_knobs as K
import v4_fdm2 as F2
import momo_render as R

#   `importlib.reload` mutates a module object in place, so the live process's `reload` refreshes
#   K, F2 and R for this module too - these names point at the same objects it reloads.


def _sd(side):
    """The side as the mech reads it, from the caller's own label. -> +1 or -1."""
    return +1 if str(side).upper() == 'HIGH' else -1


def tenths(v):
    """A line value as an INTEGER number of tenths. -> int.

    HIS 1108 RULING: *"can you int test it or reduce the dp? I only need 1dp for line values -
    there must be a way to handle it so that the float variance doesn't bite us"*.

    WHY IT IS NEEDED, measured the same day: `stoch_d` inside the developing K line is computed
    `(100 * numerator) / denominator` rather than `100 * (numerator / denominator)`, so on a HIGH
    pin - where those two are the same quantity - it lands on 100.00000000000001 instead of 100.
    The r line therefore JITTERS by up to 1.42e-14 while it is mathematically frozen. On the real
    cached arrays for 2026-08-25 that is 78 sub-1e-9 moves on ws30r alone, smallest 3.55e-15, and
    the direction reader below treated every one of them as a DIRECTION.

    THE INTEGER IS THE POINT, not the rounding: two ints are either equal or they are not, so no
    comparison downstream can be decided by a last bit. NaN has no integer, so it returns None and
    the caller reads no direction.
    """
    return None if v != v else int(round(float(v) * 10.0))


def direction(anchor_v, bar_v):
    """The direction of a line's move from one bar to another, at 1 dp. -> 'up' | 'down' | 'flat'.

    HIS 1 dp RULING, in one place so the xcv diff block and the table cannot disagree.
    """
    a, b = tenths(anchor_v), tenths(bar_v)
    if a is None or b is None:
        return 'flat'
    return 'up' if b > a else 'down' if b < a else 'flat'


def tawaway_table(LN, at_s, ev_s, s0_s, side='HIGH', hi=30, lo=10):
    """towards / away per line at one bar, with how long each state has held. -> [str]."""
    out = []
    #   HIS 1108: *"show the towards/away data at 0551, for ws10 to ws30. add a column that
    #   tells how long an away line has been printing away"*.
    #   THE SAME READ THE CAD WALK USES. exf_passed calls JIG.fdm2_cad_mom_detector on
    #   LN['EMR'][t] with the cadence window's own s0, the LIFT_* knobs, the lift-off stamp
    #   gate and rev_since - FDM_XCAD_REV_FROM 'window' puts rev_since at s0. Reproduced here
    #   bar for bar so the two cannot disagree.
    import numpy as _np
    from optimus9.analysis import jig as _JIG
    at = ln.K(str(at_s))
    sd = _sd(side)
    ev = ln.K(str(ev_s))
    s0 = ln.K(str(s0_s))
    TFS = list(range(int(hi), int(lo) - 1, -1))
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
            % (ln.U(at), side, ln.U(ev), ln.U(s0)), '']
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


def xcvdiff_table(LN, ext_s, at_s, tf=5, label='cross', anchor=None):
    """The four-row diff block for any (anchor bar, read bar) pair. -> [str]."""
    out = []
    tf = int(tf)
    anchor = anchor if anchor is not None else 'ws%dx high extremum' % tf
    #   HIS 1108: *"show the 'xcross validator report · HIGH' report that created the up
    #   verdict at 0551. show also the report at 0535"*. The 0535 block is in the report FILE;
    #   the 0551 block is a cad-walked bar and the file has no report for it, so this prints
    #   the same four rows for any (extremum, read bar) pair.
    import numpy as _np
    ext = ln.K(str(ext_s))
    at = ln.K(str(at_s))
    lab = str(label)
    alab = str(anchor)
    #   HIS 1108: *"for the cad walk only: instead of anchoring on the pre-x-cross extremum,
    #   anchor on the x-cross values"*. So the first row's label is the CALLER'S - it is the
    #   extremum for the report's own block and the x-cross for a cad-walked bar - and the diff
    #   row names whichever one was handed in. A row labelled `extremum` while holding the
    #   cross's values is the kind of label that outlives the rule it described.
    TFS = list(range(30, 9, -1))
    EM = LN['EMR']
    #   The heading names the ANCHOR it was handed, not the word `extremum`: the cad walk
    #   anchors on the x-cross under his 1108 ruling, so a heading that says `extremum`
    #   while holding the cross's values is the same stale label as the diff row's was.
    out += ['', '# ws%dx, %s %s against %s (%s)'
            % (tf, alab, ln.U(ext), ln.U(at), lab), '']
    hdr = ['line · timestamp'] + ['ws%d' % t for t in TFS]
    out += ['| ' + ' | '.join(hdr) + ' |', '|' + '---|' * len(hdr)]
    e = ['%.2f' % float(EM[t][ext]) for t in TFS]
    a = ['%.2f' % float(EM[t][at]) for t in TFS]
    d = [float(EM[t][at]) - float(EM[t][ext]) for t in TFS]
    #   HIS 1 dp RULING: the printed diff stays at 2 dp so the size is visible, and the DIRECTION
    #   is read on the integer tenths - the two can disagree, and when they do the diff is noise.
    dr = [direction(EM[t][ext], EM[t][at]) for t in TFS]
    out.append('| r · %s (%s) | %s |' % (ln.U(ext), alab, ' | '.join(e)))
    out.append('| r · %s (%s) | %s |' % (ln.U(at), lab, ' | '.join(a)))
    out.append('| r · ws%dx diff (%s - %s) | %s |'
               % (tf, lab, alab.replace('ws%dx high ' % tf, '').replace('ws%dx low ' % tf, ''),
                  ' | '.join('%+.2f' % x for x in d)))
    out.append('| r · ws%dx direction of the diff, at 1 dp | %s |' % (tf, ' | '.join(dr)))
    L4 = dr[:4]
    u = L4.count('up')
    dn = L4.count('down')
    out += ['']
    out.append(R.row('the 4 lefthand TFs, ws30 ws29 ws28 ws27', ' '.join(L4)))
    out.append(R.row('ups / downs / flats of those 4', '%d / %d / %d' % (u, dn, 4 - u - dn)))
    out.append(R.row('the 3-of-4 read',
                     'up' if u >= 3 else 'down' if dn >= 3 else 'none'))
    return out


def xcv_table(LN, day, tf=5):
    """`fdm2-xcv` over one day: a row per cadence event, with his two cad-walk columns. -> [str]."""
    out = []
    #   HIS 1108 `fdm2-xcv` TABLE, with his two new columns. His spec: one x line
    #   `ws{knob:5}x`, the race started at the cadence WINDOW OPEN, bounded by the next cadence
    #   event on either side, the FDM_X10_WOB hold restored - *"ok - that makes the wob
    #   necessary"* - and the pre-cross extremum from jig.mage_cascade_bar.
    #   THE TWO NEW COLUMNS, his words: *"1) the cad-walked timestamp when 3 ups or 3 downs
    #   print after a 'none' 3of4 read, 2) the up/down verdict"*, and *"if the 3-of-4 read is
    #   not none for a row, the fields in the new columns will read '-'"*.
    import numpy as _np
    from optimus9.analysis import jig as _JIG
    tf = int(tf)
    day = str(day)
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
        #   HIS 1 dp RULING: the direction is read on the INTEGER tenths of each line value, so a
        #   1.42e-14 jitter in a mathematically frozen line can no longer read as a direction.
        return [direction(EM[t][int(ext)], EM[t][int(bar)]) for t in LEFT]

    def read34(c):
        u, d = c.count('up'), c.count('down')
        return 'up' if u >= 3 else 'down' if d >= 3 else 'none'

    ev = []
    for sd2 in (+1, -1):
        for e in F2.cadence_events(LN, sd2, A, B):
            ev.append((int(e[0]), sd2, int(e[1])))
    out += ['', '# fdm2-xcv, ws%dx, %s' % (tf, day), '']
    #   HIS 1108 RACE: *"the earliest 4-flat bar be in a race with the cad-walks fires"*, and
    #   *"whatever mech created the earliest 4-flat bar timestamps is where the verdict will be
    #   spawned from"*. `fdm2-rline-enhance` spawns only at a bar where ALL FOUR left lines read
    #   flat; the cad walk needs 3 raw tokens agreeing so it can only fire with at most one flat.
    #   The two triggers are disjoint, so the earlier bar wins and a tie cannot happen.
    on = int(K.FDM2_RLINE_ON)
    dp = int(K.FDM2_RLINE_DP)
    out += ['| # | the cadence event | side | the ws%dx extremum | the ws%dx cross | his branch '
            '| ws30 ws29 ws28 ws27 | the 3-of-4 read | the cad-walked timestamp | the verdict '
            '| the rline-enhance spawn | its verdict | which racer won |'
            % (tf, tf), '|' + '---|' * 13]
    n = 0
    for b, sd2, s0 in sorted(ev):
        n += 1
        r = F2.x_race(LN, tf, sd2, int(s0) - 1, bound(b))
        if r is None:
            out.append('| %d | %s | %s | - | NONE | goto START | - | NO ROWS | - | - | - | - | - |'
                       % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW'))
            continue
        cf, which, c = r
        Mx = _JIG.mage_cascade_bar(X, int(c), int(sd2), mode='extrema',
                                   gap=int(_JIG.MC_GAP))
        if Mx is None:
            out.append('| %d | %s | %s | none | %s | - | - | NO EXTREMUM | - | - | - | - | - |'
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
        #   THE OTHER RACER, run from the SAME anchor over the SAME span. It walks forward from
        #   the bar after the cross and stops at the FIRST bar that spawns a verdict - no bound,
        #   because he has not ruled one here either.
        rw, rv = '-', '-'
        if on and v == 'none':
            for t3 in range(int(c) + 1, NB + 1):
                e = _JIG.rline_enhance(EM, LN['PIN'], LN['RSID'], LEFT, int(c), t3, need=3, dp=dp)
                if e['spawn'] and e['verdict']:
                    rw, rv = ln.U(t3), e['verdict']
                    break
            else:
                rw, rv = 'never to the tape end', 'none'
        won = '-'
        if v != 'none':
            won = 'the 3-of-4 read at the cross'
        elif rw not in ('-', 'never to the tape end') and cw not in ('never to the tape end',):
            won = ('fdm2-rline-enhance' if ln.K(rw) < ln.K(cw)
                   else 'the cad walk' if ln.K(cw) < ln.K(rw) else 'a tie - both at this bar')
        elif rw not in ('-', 'never to the tape end'):
            won = 'fdm2-rline-enhance'
        elif cw != 'never to the tape end':
            won = 'the cad walk'
        out.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |'
                   % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW', ln.U(ext), ln.U(int(c)), br,
                      ' '.join(d4), v, cw, cv, rw, rv, won))
    return out


def xdiag_table(LN, frm_s, to_s, tf, side='HIGH'):
    """Every ws{tf}x cross candidate in a span, and why it did not win the race. -> [str]."""
    out = []
    #   HIS 1108: *"what exactly happens at the timestamps in 'the x line with no cross'?"*.
    #   Every CROSS CANDIDATE in the span and why it did not become the race's cross - the
    #   three arms of F2.x_race, reported rather than decided.
    import numpy as _np
    tf = int(tf)
    sd = _sd(side)
    A, B = ln.K(str(frm_s)), ln.K(str(to_s))
    w = max(1, int(K.FDM_X10_WOB))
    X = F2.x_of(LN, tf)
    #   NOT `R` and `M`: `R` is the module-level momo_render import, and assigning it here
    #   makes it a local for the WHOLE answer() body, so every other kind's `R.stamp(LN)`
    #   raises UnboundLocalError. Python decides that at compile time, not at the assignment.
    Rr, Mm = LN['CPR'][tf], LN['CPM'][tf]
    out += ['', '# ws%dx race candidates, %s side, %s .. %s'
            % (tf, side, str(frm_s), str(to_s)), '']
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


def xcross_table(LN, day, tf=5):
    """The ws{tf}x race from every known cadence event, rebuilt off the live tape. -> [str]."""
    out = []
    #   HIS 1108: *"using the known cadences (not the fake cadences), apply the xcross
    #   validator mech to 08-25 and confirm you can recreate the same ws5x cross timestamps as
    #   seen in the xcross-validator report"*.
    #   INDEPENDENT REBUILD. This calls F2.cadence_events and F2.x_race directly off the live
    #   tape - it does not import the sandbox script or read its output files. If the two
    #   agree, two separate call sites produced the same bars.
    day = str(day)
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    tf = int(tf)
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


def cadlist_table(LN, frm_s, to_s):
    """Every cadence event in a span, both sides, with the pxs price at its bar. -> [str]."""
    out = []
    #   HIS 1108 CHECK on three c3r rows: *"the low cadence at 0853"*, *"high side cadence at
    #   1226"*, *"the leg ultimately lands on low side 1634 cadence"*. His eyes are a
    #   measurement, so the cadence events are read off F2.cadence_events and listed beside
    #   his quoted times rather than taken on trust either way.
    A, B = ln.K(str(frm_s)), ln.K(str(to_s))
    out += ['', '# every cadence event, both sides, %s to %s'
            % (str(frm_s), str(to_s)), '']
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

def xcvopp_table(LN, day, tf=5, cap_min=None):
    """HIS 1108 TEST: does an OPPOSING verdict print inside the cad walk's cap? -> [str].

    HIS RULE: *"if a (race winner) prints a verdict that matches the side (ie UP for high, DOWN for
    low), continue the walk cad to either a) its cap or b) until an 'opposing' verdict prints"*,
    and *"both xcv 3-of-4, and rline-enhancer are racing"*.

    So a side-matching verdict is NOT the answer: on a HIGH cadence event the usable verdict is
    `down`, on a LOW event it is `up`. This walks from the bar after the cross and tests BOTH
    racers at every bar, and reports the first opposing verdict either of them prints.

    THE CAP IS HIS, not mine: *"does a DOWN verdict from either mech print inside the 10 minute cad
    walk cap?"*. `FDM_XCAD_WALK_MIN` carries that 10.0 minutes and is where the default comes
    from. It is measured FROM THE CROSS, because the cross is where this walk starts.
    """
    out = []
    import numpy as _np
    from optimus9.analysis import jig as _JIG
    tf = int(tf)
    cap_bars = int(round(float(cap_min if cap_min is not None else K.FDM_XCAD_WALK_MIN) * 60 / 5))
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    NB = len(LN['close']) - 1
    LEFT = (30, 29, 28, 27)
    dp = int(K.FDM2_RLINE_DP)
    X = F2.x_of(LN, tf)
    EM = LN['EMR']
    allcad = sorted(set(int(e[0]) for sd2 in (+1, -1)
                        for e in F2.cadence_events(LN, sd2, 0, NB)))

    def bound(ev):
        i = _bisect.bisect_right(allcad, int(ev))
        return allcad[i] if i < len(allcad) else NB

    def raw34(anchor, bar):
        c = [direction(EM[t][int(anchor)], EM[t][int(bar)]) for t in LEFT]
        u, d = c.count('up'), c.count('down')
        return ('up' if u >= 3 else 'down' if d >= 3 else 'none'), c

    ev = []
    for sd2 in (+1, -1):
        for e in F2.cadence_events(LN, sd2, A, B):
            ev.append((int(e[0]), sd2, int(e[1])))
    out += ['', '# fdm2-xcv: does an OPPOSING verdict print inside the cap, ws%dx, %s' % (tf, day),
            '']
    out += [R.row('the cap', '%.1f min = %d bars at 5 s, from the ws%dx cross. FDM_XCAD_WALK_MIN'
                  % (cap_bars * 5 / 60.0, cap_bars, tf)),
            R.row('the opposing verdict', 'HIGH side wants `down`, LOW side wants `up` - HIS RULE'),
            R.row('both racers test every bar', 'the xcv 3-of-4 raw read, and fdm2-rline-enhance'),
            '']
    out += ['| # | the cadence event | side | the ws%dx cross | the opposing verdict wanted | the '
            'first verdict either racer prints | its mech | does it match the side | the first '
            'OPPOSING verdict | its mech | s from the cross | inside the cap |' % tf,
            '|' + '---|' * 12]
    n = 0
    for b, sd2, s0 in sorted(ev):
        n += 1
        side = 'HIGH' if sd2 > 0 else 'LOW'
        want = 'down' if sd2 > 0 else 'up'
        r = F2.x_race(LN, tf, sd2, int(s0) - 1, bound(b))
        if r is None:
            out.append('| %d | %s | %s | NONE | %s | - | - | - | - | - | - | - |'
                       % (n, ln.U(b), side, want))
            continue
        cf, which, c = r
        c = int(c)
        first_v, first_m = None, '-'
        opp_bar, opp_m = None, '-'
        #   EVERY BAR FROM THE CROSS ONWARD. The cross bar itself is read too: the xcv table's own
        #   3-of-4 is cross-against-extremum, and this walk is bar-against-cross, so at the cross
        #   the raw read is all-flat by construction and only a later bar can say anything.
        for t3 in range(c, NB + 1):
            rv, _ = raw34(c, t3)
            e = _JIG.rline_enhance(EM, LN['PIN'], LN['RSID'], LEFT, c, t3, need=3, dp=dp)
            ev2 = e['verdict'] if e['spawn'] else None
            for v, m in ((rv if rv != 'none' else None, 'the xcv 3-of-4'),
                         (ev2, 'fdm2-rline-enhance')):
                if v is None:
                    continue
                if first_v is None:
                    first_v, first_m, first_bar = v, m, t3
                if v == want and opp_bar is None:
                    opp_bar, opp_m = t3, m
            if opp_bar is not None:
                break
        if first_v is None:
            out.append('| %d | %s | %s | %s | %s | none to the tape end | - | - | none | - | - | no |'
                       % (n, ln.U(b), side, ln.U(c), want))
            continue
        d = (opp_bar - c) * 5 if opp_bar is not None else None
        out.append('| %d | %s | %s | %s | %s | %s at %s | %s | %s | %s | %s | %s | %s |'
                   % (n, ln.U(b), side, ln.U(c), want, first_v, ln.U(first_bar), first_m,
                      'YES - keep walking' if first_v != want else 'no - it opposes already',
                      ln.U(opp_bar) if opp_bar is not None else 'none to the tape end', opp_m,
                      ('%d min %02d s' % (d // 60, d % 60)) if d is not None else '-',
                      ('YES' if d is not None and d <= cap_bars * 5 else 'NO') if d is not None
                      else 'NO'))
    return out

def lift_table(LN, frm_s, to_s, side='LOW', tfs='1,2,3', also='4,5', base='r'):
    """Each ws{tf}r's lift-off reversal stamps in a span, and what other lines read at each. -> [str].

    HIS 1109 ASK: *"using 6 samples per TF, what time does ws1r,ws2r,ws3r anti-race reverse? low
    side after 0659. does ws4r and ws5r print infence at that anti-race reversal time?"*.

    `6 samples per TF` is `LIFT_PTS`, banked 6 - the knob's own gloss is *"samples in the window"*.
    The stamps come from `LN['LIFT'][(tf, side)]`, which `v4_fdm2.load` precomputes from
    `jig.lift_off` at the banked LIFT_* knobs and which already carries the LIFT_WOB offset, so a
    stamp is the bar the reversal becomes KNOWABLE rather than the bar it turned on.

    `anti-race` IS NOT A TERM IN THE TREE, so no selection rule is applied: every stamp is printed
    and the `also` lines are read at EACH of them. The first and the last are both in front of him.

    in-fence means NOT ex-20/80 - his standing rule that ex-any-fence includes oob, so a fence is
    an edge and never a band.
    """
    out = []
    import numpy as _np
    sd = _sd(side)
    A, B = ln.K(str(frm_s)), ln.K(str(to_s))
    TF = [int(x) for x in str(tfs).split(',') if str(x).strip()]
    AL = [int(x) for x in str(also).split(',') if str(x).strip()]
    lo_f, hi_f = K.fnc_pair(K.FDM_FNC_2080)
    out += ['', '# ws%s%s lift-off reversal stamps, %s side, %s .. %s'
            % (('%s, ws' % str(base)).join(str(t) for t in TF), str(base), side, str(frm_s),
               str(to_s)), '']
    out += [R.row('the samples per TF', 'LIFT_PTS %d - the knob\'s own gloss is "samples in the '
                  'window"' % int(K.LIFT_PTS)),
            R.row('the tolerance', 'LIFT_TOL %g r-points' % float(K.LIFT_TOL)),
            R.row('the hold', 'LIFT_WOB %d bars = %d s, already carried by every stamp below'
                  % (int(K.LIFT_WOB), int(K.LIFT_WOB) * 5)),
            R.row('in-fence', 'strictly inside %g..%g - NOT ex-20/80' % (lo_f, hi_f)),
            R.row('oob', 'at or past %g' % (float(K.OOB_HI) if sd > 0 else float(K.OOB_LO))),
            '']
    st = {}
    #   `base` PICKS THE LINE THE REVERSAL IS READ ON. 'r' uses LN['LIFT'], the per-(tf, side)
    #   stamps v4_fdm2.load precomputes. 'Mage' runs the same producer on LN['MGE'] here, because
    #   no Mage stamp table is precomputed - the c3r mech calls jig.lift_off on it the same way.
    from optimus9.analysis import jig as _J2
    bs = str(base)
    out += ['| the line | its lift-off reversal stamps in the span | the RAW turn behind the '
            'first | the first stamp | the last stamp | how many |', '|' + '---|' * 6]
    #   THE RAW TURN AND THE STAMP, BOTH. HIS 1109: *"are the reversal times immediately
    #   visible?"*. No - `K.lift_stamp` is the raw bar + LIFT_WOB - 1, so at LIFT_WOB 8 the turn
    #   becomes knowable 35 s after the line left its extreme. The raw bar is printed so the delay
    #   is a column rather than a claim, and it is NOT usable on its own: reading it at itself is
    #   lookahead, which is what the hold exists to prevent.
    off = max(1, int(K.LIFT_WOB)) - 1
    for t in TF:
        if bs == 'r':
            arr = _np.asarray(LN['LIFT'][(t, int(sd))], int)
            rawb = {int(b): int(b) - off for b in arr}
        else:
            raw = _J2.lift_off(LN['MGE'][t], int(sd), K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                               K.LIFT_WOB)
            arr = _np.asarray([K.lift_stamp(int(x)) for x in raw], int)
            rawb = {int(K.lift_stamp(int(x))): int(x) for x in raw}
            #   THE ARITHMETIC IS ONE PLACE. If the native raw bar and stamp - LIFT_WOB + 1 ever
            #   disagree, lift_stamp has changed under this reader and the column would lie.
            assert all(rawb[int(b)] == int(b) - off for b in arr), \
                'lift_stamp no longer equals the raw bar + LIFT_WOB - 1'
        got = [int(b) for b in arr if A <= int(b) <= B]
        st[t] = got
        out.append('| ws%d%s | %s | %s | %s | %s | %d |'
                   % (t, bs, ', '.join(ln.U(b) for b in got) if got else 'none in the span',
                      ln.U(rawb[got[0]]) if got else '-',
                      ln.U(got[0]) if got else '-', ln.U(got[-1]) if got else '-', len(got)))
    firsts = {t: (st[t][0] if st[t] else None) for t in TF}
    have = [b for b in firsts.values() if b is not None]
    out += ['']
    out += ['| the selection | the bar | which line stamped it |', '|---|---|---|']
    if have:
        fb, lb = min(have), max(have)
        out.append('| the FIRST to reverse | %s | %s |'
                   % (ln.U(fb), ', '.join('ws%d%s' % (t, bs) for t in TF if firsts[t] == fb)))
        #   HIS 1109 WORD FOR IT: *"the anti-race is my shorthand - I couldn't think how else to
        #   label 'the last of the three'"*. So `anti-race` means the LAST, and it is his term.
        out.append('| the anti-race - the LAST to reverse, HIS 1109 term | %s | %s |'
                   % (ln.U(lb), ', '.join('ws%d%s' % (t, bs) for t in TF if firsts[t] == lb)))
        out.append('| the span between them | %d min %02d s | - |'
                   % (((lb - fb) * 5) // 60, ((lb - fb) * 5) % 60))
    else:
        out.append('| none | - | - |')
    out += ['']
    #   EVERY COLUMN THE FLAG READS, so the flag cannot disagree with what is shown. HIS 1105
    #   RULE lives in F2.ex2080_line at FDM_EXF_READ 'either': the closed-prev value OR the
    #   emerging EXTREME over FDM_EXF_EM_BARS bars ENDING at the bar. A single emerging value in
    #   this table said `22.53, EXF` on 1109, which is a label describing a read it did not make.
    nb = int(K.FDM_EXF_EM_BARS)
    out += [R.row('the ex-20/80 read', 'FDM_EXF_READ %r - HIS 1105 *"if either closed-prev or '
                  'emerging values qualify"*. The emerging side is the EXTREME over '
                  'FDM_EXF_EM_BARS %d bars = %d s ending at the bar'
                  % (str(K.FDM_EXF_READ), nb, nb * 5)), '']
    out += ['| the bar read | which selection it is | the line | emerging, this bar | closed-prev, '
            'this bar | the emerging %d-bar extreme | ex-20/80 | in-fence | oob |' % nb,
            '|' + '---|' * 9]
    for t in TF:
        b = firsts[t]
        if b is None:
            continue
        lab = 'ws%d%s\'s own first reversal' % (t, bs)
        if have and b == min(have):
            lab += ' - THE FIRST of the three'
        if have and b == max(have):
            lab += ' - THE LAST of the three'
        for a in AL:
            v = float(LN['EMR'][a][int(b)])
            cp = float(LN['CPR'][a][int(b)])
            seg = _np.asarray(LN['EMR'][a], float)[max(0, int(b) - nb + 1):int(b) + 1]
            xt = float(_np.nanmax(seg)) if sd > 0 else float(_np.nanmin(seg))
            ex = bool(F2.ex2080_line(LN, a, int(b), int(sd)))
            ob = (v >= float(K.OOB_HI)) if sd > 0 else (v <= float(K.OOB_LO))
            out.append('| %s | %s | ws%dr | %.2f | %.2f | %.2f | %s | %s | %s |'
                       % (ln.U(b), lab, a, v, cp, xt, 'EXF' if ex else '.',
                          'IN-FENCE' if not ex else 'no', 'OOB' if ob else '.'))
    return out
