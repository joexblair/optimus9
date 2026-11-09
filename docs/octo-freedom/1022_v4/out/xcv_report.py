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
    #   HIS 1109 RULING: *"introduce ws4x to xcv. race it against ws5x"*. THIS REVERSES HIS 1108
    #   ONE-LINE RULING - *"ws5x is the one all of my timestamps were based on"* - which dropped
    #   ws4x from the report. Both lines run now and the EARLIER CROSS WINS, which is what a race
    #   is. The second line is FDM2_XCV_TF2, so a caller cannot race a line off the knob bank.
    tf2 = int(K.FDM2_XCV_TF2)
    RTF = [tf, tf2] if tf2 and tf2 != tf else [tf]
    X = {t: F2.x_of(LN, t) for t in RTF}
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
    out += ['', '# fdm2-xcv, ws%sx raced, %s' % ('x and ws'.join(str(t) for t in RTF), day), '']
    #   HIS 1108 RACE: *"the earliest 4-flat bar be in a race with the cad-walks fires"*, and
    #   *"whatever mech created the earliest 4-flat bar timestamps is where the verdict will be
    #   spawned from"*. `fdm2-rline-enhance` spawns only at a bar where ALL FOUR left lines read
    #   flat; the cad walk needs 3 raw tokens agreeing so it can only fire with at most one flat.
    #   The two triggers are disjoint, so the earlier bar wins and a tie cannot happen.
    on = int(K.FDM2_RLINE_ON)
    dp = int(K.FDM2_RLINE_DP)
    out += ['| # | the cadence event | side | which x line won | the x extremum | the x cross '
            '| the other x line | his branch | ws30 ws29 ws28 ws27 | the 3-of-4 read '
            '| the cad-walked timestamp | the verdict | the rline-enhance spawn | its verdict '
            '| which racer won |', '|' + '---|' * 15]
    n = 0
    for b, sd2, s0 in sorted(ev):
        n += 1
        #   THE RACE BETWEEN THE TWO X LINES: each runs its own three-armed race from the same
        #   window open to the same bound, and the EARLIER CROSS wins. A tie goes to the lower TF,
        #   which is MINE and stated - it is the faster line and nothing in his words picks one.
        cand = []
        for t in RTF:
            rr = F2.x_race(LN, t, sd2, int(s0) - 1, bound(b))
            if rr is not None:
                cand.append((int(rr[2]), t, rr))
        best = min(cand, key=lambda z: (z[0], z[1])) if cand else None
        r = best[2] if best else None
        xwin = best[1] if best else None
        xlost = ['ws%dx %s' % (t, ln.U(int(rr[2]))) for _c, t, rr in sorted(cand)
                 if xwin is not None and t != xwin]
        if r is None:
            out.append('| %d | %s | %s | none | - | NONE | no cross | goto START | - | NO ROWS '
                       '| - | - | - | - | - |'
                       % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW'))
            continue
        cf, which, c = r
        Mx = _JIG.mage_cascade_bar(X[xwin], int(c), int(sd2), mode='extrema',
                                   gap=int(_JIG.MC_GAP))
        if Mx is None:
            out.append('| %d | %s | %s | ws%dx | none | %s | %s | - | - | NO EXTREMUM '
                       '| - | - | - | - |'
                       % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW', xwin, ln.U(int(c)),
                          ', '.join(xlost) or 'no cross'))
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
        out.append('| %d | %s | %s | ws%dx | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s '
                   '| %s |'
                   % (n, ln.U(b), 'HIGH' if sd2 > 0 else 'LOW', xwin, ln.U(ext), ln.U(int(c)),
                      ', '.join(xlost) or 'no cross', br, ' '.join(d4), v, cw, cv, rw, rv, won))
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

def mage_lead_table(LN, frm_s, to_s, tf=3, offs='2,3,4', win_min=2.0, ladder=None):
    """HIS 1109 HYPOTHESIS, tested: does a higher Mage's reversal lead ws{tf}r's? -> [str].

    HIS WORDS: *"we can predict a reversal of ws{TF}r if ws{TF+2}Mage and the lower TF Mages are
    printing a semi-cascade pattern that printings timestamps in a close range (I don't know what
    close range is yet, let the data guide you). IF the conditions are true, then the reversal of
    ws{TF}r can be printed when ws{TF+2 (or +3,+4 - sweep)}Mage reverses"*, and the test:
    *"test it on every 08-25 to 08- setup when ws1r,ws2r,ws3r are exfence on the same side. the
    test passes if ws3r does actually reverse within 2 minutes of the higher Mages signal"*.

    A SETUP is one EPISODE, not one bar: a maximal run of bars where ws1r, ws2r AND ws3r are all
    ex-20/80 on the SAME side, read through `F2.ex2080_line` so the fence test is the mech's own.
    The row is the run's OPEN. One row per episode follows his standing no-duplicate-at-one-bar
    rule; counting every bar of a 60-bar run as a setup would manufacture the population. MINE,
    and stated.

    THE PASS, his: the higher Mage's stamp comes FIRST and ws{tf}r's stamp lands within `win_min`
    minutes of it. A ws{tf}r reversal that printed BEFORE the Mage is not a prediction, so a
    negative gap fails.

    `semi-cascade` IS NOT A TERM IN THE TREE, so NO pattern rule is applied. Every Mage stamp on
    the ladder is printed with the spread between the first and the last, which is the quantity
    his *"close range"* would be a threshold on. He names the rule from the data.

    CAUSAL: every stamp already carries its LIFT_WOB hold, so each is read at the bar it becomes
    knowable. The gap between two stamps is a gap between two knowable bars.
    """
    out = []
    import numpy as _np
    from optimus9.analysis import jig as _J3
    tf = int(tf)
    OFF = [int(x) for x in str(offs).split(',') if str(x).strip()]
    LAD = [int(x) for x in str(ladder).split(',')] if ladder else list(range(1, tf + max(OFF) + 1))
    A, B = ln.K(str(frm_s)), ln.K(str(to_s))
    win = int(round(float(win_min) * 60 / 5))
    off = max(1, int(K.LIFT_WOB)) - 1
    NB = len(LN['close']) - 1

    def mstamps(t, sd):
        raw = _J3.lift_off(LN['MGE'][t], int(sd), K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB)
        return sorted(int(K.lift_stamp(int(x))) for x in raw)

    def rstamps(t, sd):
        return sorted(int(b) for b in _np.asarray(LN['LIFT'][(t, int(sd))], int))

    def first_at_or_after(arr, b):
        i = _bisect.bisect_left(arr, int(b))
        return arr[i] if i < len(arr) else None

    out += ['', '# does a higher Mage reversal lead ws%dr\'s, %s .. %s' % (tf, str(frm_s),
                                                                           str(to_s)), '']
    out += [R.row('the setup', 'ws1r, ws2r AND ws3r all ex-20/80 on the same side - one row per '
                  'EPISODE, at the run\'s open'),
            R.row('the fence test', 'F2.ex2080_line, FDM_EXF_READ %r over FDM_EXF_EM_BARS %d bars'
                  % (str(K.FDM_EXF_READ), int(K.FDM_EXF_EM_BARS))),
            R.row('the pass', 'the Mage stamp FIRST, then ws%dr within %.1f min = %d bars. A '
                  'negative gap FAILS - it is not a prediction' % (tf, float(win_min), win)),
            R.row('the reversal producer', 'jig.lift_off at LIFT_PTS %d, LIFT_TOL %g, LIFT_WOB %d '
                  '- every stamp carries the hold' % (int(K.LIFT_PTS), float(K.LIFT_TOL),
                                                      int(K.LIFT_WOB))),
            R.row('the offsets swept', ', '.join('ws%dMage' % (tf + o) for o in OFF)),
            R.row('`semi-cascade`', 'NOT a term in the tree - no pattern rule is applied. The '
                  'ladder stamps and their spread are printed instead'),
            '']
    #   THE EPISODES. A run closes on the first bar any of the three is no longer ex-fence.
    eps = []
    for sd in (+1, -1):
        on = False
        for b in range(int(A), int(B) + 1):
            ok = all(bool(F2.ex2080_line(LN, t, b, sd)) for t in (1, 2, 3))
            if ok and not on:
                eps.append((b, sd))
                on = True
            elif not ok:
                on = False
    MS = {(t, sd): mstamps(t, sd) for sd in (+1, -1) for t in LAD}
    RS3 = {sd: rstamps(tf, sd) for sd in (+1, -1)}
    #   HIS 1109 READ ON THE FAILURES: *"I think the 'failures' are caused by each of them having
    #   a higher r line that is ex-fence at the time of ws{TF+2}Mage reversing, so the walk follows
    #   the higher r line"*. So at the +2 Mage's own stamp bar, every ws{TF}r ABOVE ws{tf} is read
    #   for ex-fence on the same side, and the highest one is named. If his read holds, the FAIL
    #   rows carry a higher ex-fence line and the PASS rows do not.
    HI = int(LN['HI'])
    ABOVE = list(range(tf + 1, HI + 1))
    out += ['| # | the setup opens | side | ws%dr reverses | %s | the ladder spread, first to last '
            '| at the +2 Mage bar: the highest ex-fence r above ws%d | how many above are ex-fence '
            '| the verdict |'
            % (tf, ' | '.join('ws%dMage +%d | its lead on ws%dr | pass' % (tf + o, o, tf)
                              for o in OFF), tf), '|' + '---|' * (8 + 3 * len(OFF))]
    rows = []
    for n, (b, sd) in enumerate(sorted(eps), 1):
        r3 = first_at_or_after(RS3[sd], b)
        lad = [first_at_or_after(MS[(t, sd)], b) for t in LAD]
        have = [x for x in lad if x is not None]
        spread = ('%d min %02d s' % (((max(have) - min(have)) * 5) // 60,
                                     ((max(have) - min(have)) * 5) % 60)) if len(have) > 1 else '-'
        cells = []
        res = {}
        for o in OFF:
            m = first_at_or_after(MS[(tf + o, sd)], b)
            if m is None or r3 is None:
                cells += ['-', '-', 'no data']
                res[o] = None
                continue
            d = int(r3) - int(m)
            ok = 0 <= d <= win
            res[o] = ok
            cells += [ln.U(m), '%s%d min %02d s' % ('' if d >= 0 else '-', abs(d * 5) // 60,
                                                    abs(d * 5) % 60),
                      'PASS' if ok else ('FAIL - ws%dr led' % tf if d < 0 else 'FAIL - too late')]
        #   THE HIGHER-LINE READ, at the +2 Mage's stamp bar - the bar HIS read names.
        m2 = first_at_or_after(MS[(tf + OFF[0], sd)], b) if OFF else None
        if m2 is None:
            hi_ex, n_ex = '-', '-'
        else:
            ex = [t for t in ABOVE if bool(F2.ex2080_line(LN, t, int(m2), int(sd)))]
            hi_ex = ('ws%dr %.2f' % (ex[-1], float(LN['EMR'][ex[-1]][int(m2)]))) if ex else 'none'
            n_ex = '%d of %d' % (len(ex), len(ABOVE))
        out.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s |'
                   % (n, ln.U(b), 'HIGH' if sd > 0 else 'LOW',
                      ln.U(r3) if r3 is not None else 'none to the tape end',
                      ' | '.join(cells), spread, hi_ex, n_ex,
                      'yes' if any(v for v in res.values() if v) else 'no'))
        rows.append((b, sd, r3, res, lad, hi_ex, n_ex))
    out += ['']
    out += ['| the offset | setups with data | PASS | FAIL, ws%dr led | FAIL, too late | the pass rate |'
            % tf, '|---|---|---|---|---|---|']
    for o in OFF:
        tot = sum(1 for r in rows if r[3].get(o) is not None)
        ps = sum(1 for r in rows if r[3].get(o) is True)
        out.append('| ws%dMage, +%d | %d | %d | - | - | %s |'
                   % (tf + o, o, tot, ps,
                      ('%.0f%% of %d' % (ps / tot * 100.0, tot)) if tot else 'no episodes'))
    #   HIS READ, SCORED: does a higher ex-fence r line separate the passes from the failures?
    out += ['']
    out += ['| at the +2 Mage bar | setups | a higher ex-fence r line above ws%d | none above | '
            'the share with one |' % tf, '|---|---|---|---|---|']
    for lab, sel in (('PASS on +2', [r for r in rows if r[3].get(OFF[0]) is True]),
                     ('FAIL on +2', [r for r in rows if r[3].get(OFF[0]) is False]),
                     ('every setup', rows)):
        got = [r for r in sel if r[5] not in ('-', 'none')]
        non = [r for r in sel if r[5] == 'none']
        out.append('| %s | %d | %d | %d | %s |'
                   % (lab, len(sel), len(got), len(non),
                      ('%.0f%%' % (len(got) / len(sel) * 100.0)) if sel else '-'))
    out += ['']
    out.append(R.row('episodes found', len(eps)))
    out.append(R.row('the ladder read', 'ws%s' % 'Mage, ws'.join(str(t) for t in LAD) + 'Mage'))
    return out

def handoff_table(LN, day, offs='2,3,4', anchor_lo=1):
    """HIS 1109 HANDOFF: the Mage-timed TF jump chain from each cadence event. -> [str].

    HIS WORDS: *"the work we're dialing presently tells me that using the ws{TF+2 or TF+2
    (sweep)}Mage reversal is a strong candidate for handoff timing"*, *"we'll be jumping TFs
    without bound"*, and *"for each of the cadences in 08-26, print a table that shows the
    ws{TF}r which formed the cadence, and when the Mage-based handoff runs out of candidates.
    print the TF jump chain as well"*.

    THE THREE GAPS I FILLED, each stated and none of them his:

      the cadence's own ws{TF}r   HIS 1109 CORRECTION: *"cadence windows open on ws1r, ws2r,ws3r
                                  + the other gates"*. I had written that the producer was always
                                  ws1-based, which was WRONG - `F2.cadence_events`'s nestle test
                                  loops `for rt in (1, 2, 3)` and records which one qualified. The
                                  chain starts on THAT line. It is read out of the event's own
                                  `why` string, whose nestle clause has one format and one writer;
                                  the regex asserts rather than falling back, so a format change
                                  fails loudly instead of silently picking ws1.
                                  The highest ex-fence towards line is printed BESIDE it, because
                                  that was his 1109 anchor for the 0658 question and the two can
                                  disagree.
      the handoff                 from rider ws{t}, the next rider is ws{t+off} at the bar
                                  ws{t+off}Mage's lift-off reversal STAMPS on the cadence side.
                                  The stamp, not the raw turn, because the raw turn is not
                                  knowable at itself.
      no gate on the receiver     he said *"without bound"* and named no condition, so the chain
                                  takes every hop its Mage offers. Whether the receiver was
                                  ex-fence at the handoff is PRINTED as data, never applied.

    IT RUNS OUT two ways and the table says which: `ws{t+off} is past ws30` - the ladder top - or
    `no ws{t+off}Mage reversal ahead` to the tape end. No forward bound is applied.

    CAUSAL: each hop reads a stamp at or after the previous hop's bar, and a stamp already carries
    its own LIFT_WOB hold.
    """
    out = []
    import re
    import numpy as _np
    from optimus9.analysis import jig as _J4
    OFF = [int(x) for x in str(offs).split(',') if str(x).strip()]
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    NB = len(LN['close']) - 1
    HI = int(LN['HI'])
    MST = {}

    def mstamps(t, sd):
        if (t, sd) not in MST:
            raw = _J4.lift_off(LN['MGE'][t], int(sd), K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                               K.LIFT_WOB)
            MST[(t, sd)] = sorted(int(K.lift_stamp(int(x))) for x in raw)
        return MST[(t, sd)]

    def nxt(t, sd, frm):
        a = mstamps(t, sd)
        i = _bisect.bisect_left(a, int(frm))
        return a[i] if i < len(a) else None

    def anchor_at(bar, sd):
        """The highest ws{TF}r that is ex-20/80 AND towards at `bar`. -> tf or None."""
        rs = int(bar)
        best = None
        for t in range(int(anchor_lo), HI + 1):
            if not bool(F2.ex2080_line(LN, t, int(bar), int(sd))):
                continue
            st = _J4.fdm2_cad_mom_detector(LN['EMR'][t], LN['EMR'][t], int(bar), int(sd), rs,
                                           K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB,
                                           stamps=_np.asarray(LN['LIFT'][(t, int(sd))], int),
                                           rev_since=rs)['state']
            if st == 'towards':
                best = t
        return best

    #   THE NESTLE'S OWN r LINE, out of the event's `why`. One format, one writer - and the
    #   assert below means a format change fails loudly instead of silently picking ws1.
    NEST = re.compile(r'deeper than ws(\d+)r')
    ev = []
    for sd in (+1, -1):
        for e in F2.cadence_events(LN, sd, A, B):
            mm = NEST.search(str(e[2]))
            assert mm, 'the nestle clause is not in the why string: %r' % (str(e[2])[:120],)
            ev.append((int(e[0]), sd, int(mm.group(1))))
    out += ['', '# the Mage-timed TF handoff chain from every cadence event, %s' % day, '']
    out += [R.row('the handoff', 'from rider ws{t}, the next rider is ws{t+off} at the bar '
                  'ws{t+off}Mage\'s lift-off reversal STAMPS on the cadence side'),
            R.row('the chain start', 'the ws{TF}r that qualified the cadence\'s NESTLE, one of '
                  'ws1r, ws2r, ws3r - HIS 1109 correction *"cadence windows open on ws1r, '
                  'ws2r,ws3r + the other gates"*'),
            R.row('the column beside it', 'the highest ex-fence towards line at the cadence bar - '
                  'his 1109 anchor for the 0658 question, printed because the two can disagree'),
            R.row('the gate on a receiver', 'NONE - his *"without bound"*. Its ex-fence state at '
                  'the handoff is printed as data'),
            R.row('the ladder top', 'ws%d - L2_MOM_MAXTF' % HI),
            R.row('the reversal producer', 'jig.lift_off on LN[\'MGE\'] at LIFT_PTS %d, LIFT_TOL '
                  '%g, LIFT_WOB %d' % (int(K.LIFT_PTS), float(K.LIFT_TOL), int(K.LIFT_WOB))),
            '']
    out += ['| # | the cadence event | side | the nestle\'s r line - the chain start | the highest '
            'ex-fence towards line there | %s |'
            % ' | '.join('+%d: the TF jump chain | its last handoff | hops | how it ran out' % o
                         for o in OFF),
            '|' + '---|' * (5 + 4 * len(OFF))]
    n = 0
    for b, sd, rt in sorted(ev):
        n += 1
        a0 = int(rt)
        hiex = anchor_at(b, sd)
        cells = []
        for o in OFF:
            if a0 is None:
                cells += ['-', '-', '-', 'no ex-fence towards line at the cadence bar']
                continue
            t, bar, chain, hops = a0, int(b), ['ws%d' % a0], 0
            why = ''
            while True:
                t2 = t + o
                if t2 > HI:
                    why = 'ws%d is past ws%d, the ladder top' % (t2, HI)
                    break
                m = nxt(t2, sd, bar)
                if m is None:
                    why = 'no ws%dMage reversal ahead to the tape end' % t2
                    break
                exf = 'EXF' if bool(F2.ex2080_line(LN, t2, int(m), int(sd))) else 'in-fence'
                chain.append('ws%d @ %s %s' % (t2, ln.U(m), exf))
                t, bar, hops = t2, int(m), hops + 1
            cells += [' > '.join(chain), ln.U(bar) if hops else '-', str(hops), why]
        out.append('| %d | %s | %s | ws%dr | %s | %s |'
                   % (n, ln.U(b), 'HIGH' if sd > 0 else 'LOW', a0,
                      ('ws%dr' % hiex) if hiex is not None else 'none', ' | '.join(cells)))
    out += ['']
    out.append(R.row('cadence events on the day', n))
    return out

def jump_table(LN, day, offs='2,3,4'):
    """HIS 1109 UNBOUNDED JUMP: the handoff is Mage-TIMED, the destination is unbounded. -> [str].

    HIS WORDS: *"we'll be jumping TFs without bound, but at the moment I'm not clear on the handoff
    timing"* and *"using the ws{TF+2 or TF+2 (sweep)}Mage reversal is a strong candidate for
    handoff timing"*, then *"which column reports the unbounded jump?"* against my fixed-stride
    chain, and *"build it thanks"*.

    THE TWO THINGS HIS MESSAGE SEPARATES, which `handoff_table` conflated into one:

      WHEN   ws{t+off}Mage's lift-off reversal stamps, with `t` the CURRENT rider. The offset is
             swept because he called it a candidate, not a ruling. The timer line moves with the
             rider.
      WHERE  UNBOUNDED. Any TF above the rider may receive - ws3 to ws22 in one hop is allowed.

    THE DESTINATION RULE IS MINE, and it is HIS OWN 1109 ANCHOR rather than something invented: at
    the handoff bar the new rider is the HIGHEST ws{TF}r above the current rider that is ex-20/80
    AND printing towards. That is the rule he gave for the 0658 question - *"the highest ws{TF}r
    that's printing ex-fence + towards"* - applied at each handoff instead of only at the start.

    A BARREN HANDOFF is a Mage stamp where no line above the rider qualifies. The chain does NOT
    stop there: it takes the next stamp and tries again, and every barren bar is counted. Stopping
    at the first one is the other reading of his *"runs out of candidates"* and the row carries the
    bar it would have stopped on, so both readings are in front of him. NOTHING IS APPLIED.

    IT ENDS two ways: `no ws{t+off}Mage stamp ahead` with `t+off` still on the ladder, or the rider
    reaches ws{HI} and `t+off` passes the ladder top.

    THE towards ANCHOR is the cadence event's own excursion start, the same window `F2.cadence_events`
    returns, so every read in the chain is anchored where the cadence is.

    CAUSAL: each hop reads a Mage stamp at or after the previous hop's bar, and reads the board AT
    that stamp. A stamp already carries its LIFT_WOB hold.
    """
    out = []
    import re
    import numpy as _np
    from optimus9.analysis import jig as _J5
    OFF = [int(x) for x in str(offs).split(',') if str(x).strip()]
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    HI = int(LN['HI'])
    MST = {}

    def mstamps(t, sd):
        if (t, sd) not in MST:
            raw = _J5.lift_off(LN['MGE'][t], int(sd), K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                               K.LIFT_WOB)
            MST[(t, sd)] = sorted(int(K.lift_stamp(int(x))) for x in raw)
        return MST[(t, sd)]

    def nxt(t, sd, frm):
        a = mstamps(t, sd)
        i = _bisect.bisect_left(a, int(frm))
        return a[i] if i < len(a) else None

    def board_above(t, bar, sd, s0):
        """The highest ws{TF}r above ws{t} that is ex-20/80 AND towards at `bar`. -> tf or None."""
        best = None
        for u in range(int(t) + 1, HI + 1):
            if not bool(F2.ex2080_line(LN, u, int(bar), int(sd))):
                continue
            st = _J5.fdm2_cad_mom_detector(LN['EMR'][u], LN['EMR'][u], int(bar), int(sd), int(s0),
                                           K.LIFT_PTS, K.gap_for(u), K.LIFT_TOL, K.LIFT_WOB,
                                           stamps=_np.asarray(LN['LIFT'][(u, int(sd))], int),
                                           rev_since=int(s0))['state']
            if st == 'towards':
                best = u
        return best

    NEST = re.compile(r'deeper than ws(\d+)r')
    ev = []
    for sd in (+1, -1):
        for e in F2.cadence_events(LN, sd, A, B):
            mm = NEST.search(str(e[2]))
            assert mm, 'the nestle clause is not in the why string: %r' % (str(e[2])[:120],)
            ev.append((int(e[0]), sd, int(mm.group(1)), int(e[1])))
    out += ['', '# the UNBOUNDED TF jump chain, Mage-timed, from every cadence event, %s' % day, '']
    out += [R.row('WHEN a handoff happens', 'ws{t+off}Mage\'s lift-off reversal STAMPS, with t the '
                  'CURRENT rider - his timing candidate, offset swept'),
            R.row('WHERE it jumps to', 'UNBOUNDED - the HIGHEST ws{TF}r above the rider that is '
                  'ex-20/80 AND towards at that bar. MINE, and it is HIS OWN 1109 anchor rule '
                  'applied at every handoff instead of only at the start'),
            R.row('the chain start', 'the ws{TF}r that qualified the cadence\'s nestle'),
            R.row('a barren handoff', 'a Mage stamp with no qualifying line above the rider. The '
                  'chain takes the NEXT stamp and the barren bar is counted - stopping there is '
                  'the other reading of his *"runs out of candidates"* and both are printed'),
            R.row('the towards anchor', 'the cadence event\'s own excursion start'),
            R.row('the ladder top', 'ws%d - L2_MOM_MAXTF' % HI), '']
    out += ['| # | the cadence event | side | the nestle r line | %s |'
            % ' | '.join('+%d hops | +%d last handoff | +%d min from the cadence | +%d the jump '
                         'sizes | +%d barren handoffs | +%d its first barren bar | +%d how it ended'
                         % (o, o, o, o, o, o, o) for o in OFF),
            '|' + '---|' * (4 + 7 * len(OFF))]
    n = 0
    for b, sd, rt, s0 in sorted(ev):
        n += 1
        cells = []
        for o in OFF:
            t, bar = int(rt), int(b)
            chain, jumps, barren, first_barren, why = ['ws%d' % rt], [], 0, None, ''
            #   THE LAST SUCCESSFUL HANDOFF, tracked apart from `bar`, which a barren stamp moves
            #   forward without a handoff. HIS 1109: *"that table doesn't tell me the time when it
            #   ended. I'm blind without that data"*.
            last = None
            while True:
                if t + o > HI:
                    why = 'ws%d, the timer line, is past ws%d' % (t + o, HI)
                    break
                m = nxt(t + o, sd, bar)
                if m is None:
                    why = 'no ws%dMage stamp ahead to the tape end' % (t + o)
                    break
                u = board_above(t, m, sd, s0)
                if u is None:
                    barren += 1
                    if first_barren is None:
                        first_barren = m
                    bar = int(m) + 1
                    continue
                chain.append('ws%d @ %s' % (u, ln.U(m)))
                jumps.append(u - t)
                t, bar, last = int(u), int(m), int(m)
            dmin = ('%d' % (((last - int(b)) * 5) // 60)) if last is not None else '-'
            cells += [str(len(jumps)), ln.U(last) if last is not None else 'no handoff', dmin,
                      ', '.join('+%d' % j for j in jumps) if jumps else '-',
                      str(barren), ln.U(first_barren) if first_barren is not None else 'none', why]
        out.append('| %d | %s | %s | ws%dr | %s |'
                   % (n, ln.U(b), 'HIGH' if sd > 0 else 'LOW', rt, ' | '.join(cells)))
    out += ['']
    out.append(R.row('cadence events on the day', n))
    return out
