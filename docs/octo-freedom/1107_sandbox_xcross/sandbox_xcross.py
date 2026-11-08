"""`fdm2-xcv` - HIS NAME, 1108. One xcross validator report per cadence event. -> text files.

HIS 1108: *"take ownership of the files. bank them as the fdm2-xcv mech"*. Built in another session
and handed over at chat log #46; owned here from 1108. The indented spec is section 0 of
docs/octo-freedom/1107_sandbox_xcross.md.

HIS FOUR ITEMS, in his words: *"the next data collection will be built by these 4 items: the cadence, the
highest TF selected, the ws{TF}x cross after the cadence, and the report"*.

    1 the cadence    v4_fdm2.cadence_events - the BUILT version, his *"we'll be using the built version"*:
                     ws1b's oob excursion, the nestle and the ws3Mage gate, his 1103 preamble
    2 the TF         HIS SANDBOX RULE: *"at the cadence event, find the highest es-20/80-fence towards line
                     and make that the TF for the ws{TF}x cross"*. ex-20/80 is v4_fdm2.ex2080_line, towards
                     is step 1's v4_fdm2.towards, so no trade is read - his *"the trade won't be considered.
                     this means you can use the side of the cadence to dictate the side of the ws{}x cross"*
    3 the x-cross    v4_fdm2.x_race on that TF, from the cadence event: the first of {ib, ws{TF}r, ws{TF}Mage}
                     to hold FDM_X10_WOB bars
    4 the report     THE xcross validator report, his 1108 name (*"let's name that report "xcross validator
                     report" - it matches what it does"*). His 1107 table: ws30..ws10 r, emerging, at the ws{TF}x extremum and at the cross, the
                     diff and its direction - then the same r rows on ws5x, his *"drop the r2 rows, and replace
                     them with r rows that were calculated on ws5x"*. The extremum is jig.mage_cascade_bar's walk back to
                     look forward from the cross bar, on the cadence side

THE r2 LINE, HIS 1107: *"create a new `ws{TF}r2` stochrsi line: klen:6, rsilen:6, stochrange:10, src close"*
and *"drop the mages from the reports, and replace their rows with the ws{TF}r2 data"*. It is built IN
MEMORY on every run, the same Jig and warmup every cached line uses, through the named KLine so the legacy
tuple cannot transpose (KLine(6, 6, 10) -> ('k', 6, 10, 6, 'close')). Nothing is written to the line
cache. A ws30r built the same way must equal the cached ws30r exactly, or the run refuses.

MINE, every one flagged in the file's own legend:
    - towards is step 1's reader. The director's reader needs an extremum anchor, and that anchor is the trade
      open in the built walk, which is the dependency his sandbox rule exists to remove
    - the scan is ws1..ws{HI}, the director's range; step 1 scans ws4..ws30
    - the race runs to the tape end. In the built walk the next cadence event would end it first; here the
      next same-side cadence event is printed beside it instead
    - the report's first row is the ws{TF}x extremum, read from his "this table" after the ws15x table
    - the walk back is unbounded, as jig.mage_cascade_bar is, so the extremum can sit before the cadence event

THE KNOBS ARE BANKED in sandbox_knobs.py, his 1108 *"bank, update specs and make knobs durable"*: the
report's columns, the ws5x block, ws{TF}r2, ws{TF}e and the fake cadence window. A run with any of them off
the bank refuses unless W_SBX_EXPERIMENT=1; every run prints them first. The spec is ../1107_sandbox_xcross.md.

THE FAKE CADENCE, HIS 1107 EXPERIMENTAL: *"fake a cadence event whenever ws1b crosses to ib, while ws1Mage was
oob during ws1b's oob excursion, from 1745 to 1920. these will all be high side events"*. --fake runs it over
the banked window and prints each one's report on screen, his *"show the list of reports onscreen"*.

THE ws{TF}e LINE, HIS 1107: BB%B len 4, mult 0.5, src close. e_line(tf) builds it in memory; no report reads it.

Usage:  python3 sandbox_xcross.py 2026-08-25        (run from 1022_v4, or anywhere - the paths are absolute)
        python3 sandbox_xcross.py --fake            the fake cadence reports, on screen
"""
import io
import bisect as _bisect
import os
import sys

os.environ.setdefault('LG_TAPE_END', '2026-10-05')
V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
sys.path.insert(0, os.path.join(V4, 'out'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(V4)
import numpy as np

_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import ln
    import momo_render as MR
    from optimus9.analysis import jig as JIG
    from optimus9.analysis.jig import Jig
    from optimus9.compute.line_config import override, KLine, BBLine
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
finally:
    sys.stderr = _e
import sandbox_knobs as SK

OUT = os.path.dirname(os.path.abspath(__file__))
TFS = list(range(SK.REPORT_TF_HI, SK.REPORT_TF_LO - 1, -1))     # his report's columns, ws30 down to ws10
SIDE_NAME = {+1: 'HIGH', -1: 'LOW'}
REPORT_NAME = 'xcross validator report'  # HIS 1108 name, printed in every file title and every report banner
R2_CFG = KLine(k_len=SK.R2_KLEN, rsi=SK.R2_RSI, stc=SK.R2_STC, src=SK.R2_SRC)    # HIS 1107 ws{TF}r2, 6|6|10|close
R2 = {}                                  # tf -> the ws{tf}r2 array, built once per run by r2_lines()
#   r2_lines() IS NOT READ BY THE REPORT. Joe 1107 dropped the r2 rows for the ws5x ones; the producer stays so
#   ws{TF}r2 - his named line - can be read again without re-deriving it.
WS5X_TF = SK.WS5X_TF                     # HIS 1107 second block: r rows calculated on ws5x
XCV_TFS = (int(SK.WS5X_TF),)
#   HIS 1108: ONE x line, `WS5X_TF` 5 - his `ws{knob:5}x`. 4 rows per cadence event.
E_CFG = BBLine(length=SK.E_LEN, mult=SK.E_MULT, src=SK.E_SRC)  # HIS 1107 ws{TF}e, BB%B 4|0.5|close


def r2_lines():
    """ws10r2..ws30r2 on the 5 s grid, EMERGING, built in memory. -> {tf: array}. Cached in R2.

    THE CONTROL ROW: ws30r built in the same Jig must equal the cached ln.line('ws30r') exactly - his
    standing rule that every build carries a live control row against the known-good array.
    """
    if R2:
        return R2
    ovr = {'ws%dr2' % t: override(t * 60, R2_CFG.as_tuple(), 'emerging') for t in TFS}
    ovr['ws30r_control'] = override(1800, ln.SPEC['r'][0], 'emerging')
    with Jig(ln.EM, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
        assert len(j.ts) >= ln.N and (np.asarray(j.ts, np.int64)[:ln.N] == ln.ts).all(), 'the r2 grid is off the tape'
        got = {n: np.asarray(j.W.line(n), float)[:ln.N] for n in ovr}
    c, ref = got.pop('ws30r_control'), np.asarray(ln.line('ws30r'), float)
    assert (np.isnan(c) == np.isnan(ref)).all() and np.nanmax(np.abs(c - ref)) == 0.0, \
        'the ws30r control row does not match the cached ws30r - the r2 build cannot be trusted'
    R2.update({t: got['ws%dr2' % t] for t in TFS})
    return R2


def e_line(tf):
    """ws{tf}e on the 5 s grid, EMERGING, built in memory. -> array. Nothing is written to the line cache.

    THE CONTROL ROW: ws{tf}Mage built in the same Jig must equal the cached ln.line('ws{tf}Mage') exactly, or
    the build refuses - the same standing rule r2_lines() carries.
    """
    ovr = {'ws%de' % tf: override(tf * 60, E_CFG.as_tuple(), 'emerging'),
           'ws%dMage_control' % tf: override(tf * 60, ln.SPEC['Mage'][0], 'emerging')}
    with Jig(ln.EM, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
        assert len(j.ts) >= ln.N and (np.asarray(j.ts, np.int64)[:ln.N] == ln.ts).all(), 'the e grid is off the tape'
        got = {n: np.asarray(j.W.line(n), float)[:ln.N] for n in ovr}
    c, ref = got['ws%dMage_control' % tf], np.asarray(ln.line('ws%dMage' % tf), float)
    assert (np.isnan(c) == np.isnan(ref)).all() and np.nanmax(np.abs(c - ref)) == 0.0, \
        'the ws%dMage control row does not match the cached ws%dMage - the e build cannot be trusted' % (tf, tf)
    return got['ws%de' % tf]


def fake_events(LN):
    """HIS 1107 EXPERIMENTAL fake HIGH cadence events over the banked window. -> ([(ev, s0, s1, mx)], [comment]).

    A fake event is a closed-prev ws1b cross from oob back to ib whose oob excursion (s0..s1, the bars before
    the cross) saw closed-prev ws1Mage at or past the high oob on at least one bar - the reads the built
    cadence makes. Every cross in the window prints a comment line, kept or not.
    """
    A, B = ln.K(SK.FAKE_DAY + ' ' + SK.FAKE_FROM), ln.K(SK.FAKE_DAY + ' ' + SK.FAKE_TO)
    B1, M1 = LN['B1'], LN['CPM'][1]
    oob = B1 >= K.OOB_HI
    evs, notes = [], []
    for c, cf, s in JIG.oob_ib_cross(B1, K.OOB_HI, K.OOB_LO, 1):
        if int(s) != +1 or not (A <= int(c) <= B):
            continue
        j = int(c) - 1
        if j < 0 or not oob[j]:
            continue
        while j > 0 and oob[j - 1]:
            j -= 1
        s0, s1 = j, int(c) - 1
        m = M1[s0:s1 + 1]
        hit = np.flatnonzero(m >= K.OOB_HI)
        notes.append('<!-- cross %s excursion %s..%s ws1Mage max %.2f oob bars %d -->'
                     % (ln.U(int(c)), ln.U(s0), ln.U(s1), np.nanmax(m), hit.size))
        if hit.size:
            evs.append((int(c), s0, s1, float(np.nanmax(m))))
    return evs, notes


def fake_main():
    """The fake cadence reports, ON SCREEN - his *"show the list of reports onscreen - no summaries"*."""
    LN = F2.load()
    evs, notes = fake_events(LN)
    print('\n'.join(notes))
    print('<!-- bars %d, fake events %d -->' % (len(LN['close']), len(evs)))
    for i, (ev, s0, s1, mx) in enumerate(evs):
        out = report(LN, +1, ev, '%d of %d' % (i + 1, len(evs)))
        out = [l.replace('HIGH cadence event', 'HIGH FAKE cadence event') for l in out if not set(l) <= {'='}]
        print('\n'.join(out))


def table(rows):
    """A markdown table padded to fixed width, so it reads in a plain text viewer too. -> [str]."""
    w = [max(len(str(r[i])) for r in rows) for i in range(len(rows[0]))]
    fmt = lambda r: '| ' + ' | '.join(str(c).ljust(w[i]) for i, c in enumerate(r)) + ' |'
    return [fmt(rows[0]), '|' + '|'.join('-' * (x + 2) for x in w) + '|'] + [fmt(r) for r in rows[1:]]


def report(LN, side, ev, n_of, s0=None):
    """THE xcross validator report for one cadence event: its banner and its r table. -> [str].

    HIS 1108: *"bank the latest version, the one that has ws5x as a static line for each table"* - every
    report carries the selected ws{TF}x block AND the fixed ws5x block (WS5X_TF, banked 5).

    HIS 1107: the per-event item table (the cadence, the TF, the cross, the extremum) is DELETED from the
    files - his *"delete these sections from both files"*. The cadence event stays in the banner, the
    extremum and the cross bars stay in the report table's own row labels.
    """
    out = ['', '=' * 100, '%s · %s cadence event %s  (%s)' % (REPORT_NAME, SIDE_NAME[side], ln.U(ev), n_of),
           '=' * 100, '']
    g = [('line · timestamp',) + tuple('ws%d' % t for t in TFS)]
    notes = []
    #   HIS 1108: *"drop the 4 dynamic rows from the report, and replace them with ws4x. the end
    #   result is 8 rows per cadence, covering ws4 and ws5 x crosses"*. TWO FIXED BLOCKS, no
    #   dynamic TF selection anywhere: 4 rows for each x line in XCV_TFS, banked '4,5'. The highest
    #   ex-20/80 towards line is no longer read, so his item 2 and item 3 are off the report path.
    for xtf in XCV_TFS:
        rows, why = r_block(LN, side, ev, int(xtf), s0)
        if rows is None:
            if why:
                notes.append(why)
            continue
        g += rows
    return out + (table(g) if len(g) > 1 else []) + notes


_XC = {}


def all_x_crosses(LN, xtf, side):
    """Every ws{xtf}x race cross on `side`, over the WHOLE tape. -> [(confirm, which, cross)].

    HIS 1108: *"find the nearest cross, looking back or forward"*. Unbounded on purpose - a
    nearest read that stopped at the race bound would only restate the bound that already failed.
    One F2.x_race call with collect=True, so the three race arms live in one place; cached per
    (xtf, side) because it is a full-tape scan.
    """
    key = (int(xtf), int(side))
    if key not in _XC:
        _XC[key] = F2.x_race(LN, xtf, side, -1, len(LN['close']) - 1, collect=True)
    return _XC[key]


def nearest_cross(LN, xtf, side, ev):
    """The nearest ws{xtf}x cross before and after `ev`, by CROSS bar. -> (back, fwd), each
    (confirm, which, cross) or None."""
    xs = all_x_crosses(LN, xtf, side)
    back = fwd = None
    for cf, nm, c in xs:
        if int(c) <= int(ev):
            back = (int(cf), nm, int(c))
        elif fwd is None:
            fwd = (int(cf), nm, int(c))
            break
    return back, fwd


def nearest_cross_note(LN, xtf, side, ev):
    """One sentence naming the nearest cross each way, with its distance. -> str."""
    back, fwd = nearest_cross(LN, xtf, side, ev)
    def one(t, lab):
        if t is None:
            return 'no %s cross anywhere on the tape' % lab
        cf, nm, c = t
        d = (int(c) - int(ev)) * 5 / 60.0
        return ('the nearest %s cross is %s on %s, %+.1f min, confirming %s'
                % (lab, ln.U(c), nm, d, ln.U(cf)))
    return '%s. %s' % (one(back, 'BACK'), one(fwd, 'FORWARD'))


_ALLCAD = None


def all_cadence_bars(LN):
    """Every cadence event bar on the tape, BOTH sides, ascending. -> int list.

    HIS 1108 RULING on the race bound: *"the next {any_}cadence"*. Not the tape end, and not only
    the same side - any cadence event on either side ends the race. Built once per process because
    it is a full-tape scan; a per-event scan would repeat it 28 times on one day.
    """
    global _ALLCAD
    if _ALLCAD is None:
        n = len(LN['close']) - 1
        b = []
        for sd in (+1, -1):
            b += [int(e[0]) for e in F2.cadence_events(LN, sd, 0, n)]
        _ALLCAD = sorted(set(b))
    return _ALLCAD


def race_bound(LN, ev):
    """The bar the ws{TF}x race may not pass. -> int.

    HIS 1108: *"the next {any_}cadence"*. The first cadence event STRICTLY after `ev`, on either
    side; the tape end when none follows. Strictly after, because the event the race started from
    cannot also end it.
    """
    cads = all_cadence_bars(LN)
    i = _bisect.bisect_right(cads, int(ev))
    return cads[i] if i < len(cads) else len(LN['close']) - 1


def r_block(LN, side, ev, xtf, s0=None):
    """ws30r..ws10r at ws{xtf}x's extremum and cross after the cadence event. -> (rows, None) | (None, why).

    3 THE x-CROSS: x_race on ws{xtf} from the cadence event. 4 THE REPORT ROWS: the walk back to look forward
    from that cross, on the cadence side, then the r values, EMERGING, at both bars.
    """
    bnd = race_bound(LN, ev)
    #   HIS 1108: *"accept an x-cross that fires inside a cadence window"*. The window is ws1b's
    #   own oob excursion, from `s0` to the cadence event bar, and F2.cadence_events hands `s0`
    #   back. The race therefore starts at the EXCURSION OPEN, not at the event bar + 1, so a
    #   cross that fired while ws1b was still oob is this event's cross.
    #   HIS 1108 ON THE HOLD, IN TWO STEPS. First *"there is no hold - the cross is read raw"*,
    #   which I built and measured. On the 2026-08-25 02:22:00 HIGH event the raw cross was
    #   02:22:40 - ws5x crossing the 85 boundary downward at 83.76 and bouncing back to 91.62 ONE
    #   BAR later - against 02:31:55 for the held race. He read that and reversed himself: *"ok -
    #   that makes the wob necessary"*. So the hold is back and F2.x_race owns the cross.
    #   `FDM_X10_WOB` 24 bars = 120 s, counting the cross bar.
    frm = (int(s0) - 1) if s0 is not None else int(ev)
    r = F2.x_race(LN, xtf, side, frm, bnd)
    if r is None:
        #   HIS 1108 race bound is the next cadence event, so the message names THAT bar. It read
        #   "before the tape ends" after the bound moved, which is a label describing a rule the
        #   code no longer runs.
        #   HIS 1108: *"to make this table useful, I need you to find the nearest cross, looking
        #   back or forward. with that data, I can make decisions"*. So the note also carries the
        #   NEAREST cross either side of the cadence event, found with NO bound at all - the whole
        #   tape - because a bounded nearest read would just restate the bound that failed.
        #   HIS 1108: *"no note. if there's a fault to diagnose, I'll be looking at the charts
        #   and it will be obvious to me if the 'skipped' cadence has any impact on the
        #   debugging"*. So a cadence event the next cadence event beat prints NOTHING - his spec's
        #   `goto START`, and the next event's own report is the record.
        return None, None
    cf, which, c = r
    X = F2.x_of(LN, xtf)
    wb = JIG.mage_cascade_bar(X, c, side, mode='extrema', gap=JIG.MC_GAP)
    if wb is None:
        return None, 'the ws%dx walk back from the cross finds no extremum' % xtf
    E, _ = wb
    vals = {}
    for t in TFS:
        v = np.asarray(ln.line('ws%dr' % t), float)
        vals[t] = (v[E], v[c], v[c] - v[E])
    lab = 'ws%dx %s extremum' % (xtf, 'high' if side > 0 else 'low')
    return [('r · %s (%s)' % (ln.U(E), lab),) + tuple('%.2f' % vals[t][0] for t in TFS),
            ('r · %s (ws%dx cross)' % (ln.U(c), xtf),) + tuple('%.2f' % vals[t][1] for t in TFS),
            ('r · ws%dx diff (cross - extremum)' % xtf,) + tuple('%+.2f' % vals[t][2] for t in TFS),
            ('r · ws%dx direction of the diff' % xtf,)
            + tuple('up' if vals[t][2] > 0 else ('down' if vals[t][2] < 0 else 'flat') for t in TFS)], None


def legend(LN, day, side, n):
    h, off = MR.knob_hash()
    rows = [('the read', 'value'),
            ('the day', day),
            ('the cadence side', SIDE_NAME[side]),
            ('cadence events on the day', n),
            ('the tape', '%d bars, %s .. %s' % (len(LN['close']), ln.U(0), ln.U(len(LN['close']) - 1))),
            ('the knob hash', '%s, off the bank: %s' % (h, ', '.join(off) or 'none')),
            ('the cadence', 'the BUILT version: ws1b oob excursion, nestle, ws3Mage ex-%g/%g (rescue %s)'
             % (*K.fnc_pair(K.FDM_M3_FNC), 'on' if int(K.FDM_M3_RESCUE_ON) else 'off')),
            ('the x lines', 'HIS 1108: %s, both FIXED. No dynamic TF selection - the highest ex-%g/%g towards '
             'line is no longer read, so his items 2 and 3 are off the report path'
             % (', '.join('ws%dx' % t for t in XCV_TFS), *K.fnc_pair(K.FDM_FNC_2080))),
            ('the x-cross', 'the first of ws{TF}x to ib, to ws{TF}r, to ws{TF}Mage that holds %d bars = %d s, counting '
             'the cross bar. ws{TF}x is emerging, its r and Mage racers are closed-prev, as built'
             % (int(K.FDM_X10_WOB), int(K.FDM_X10_WOB) * 5)),
            ('the extremum', 'jig.mage_cascade_bar, walk back to look forward in %d-bar = %d s steps from the cross'
             % (JIG.MC_GAP, JIG.MC_GAP * 5)),
            ('the report table', '%d rows per cadence event: 4 for each of %s. ws30..ws10 r, EMERGING, at that x '
             'line\'s extremum and at its cross. diff = cross - extremum, flat = exactly 0'
             % (4 * len(XCV_TFS), ', '.join('ws%dx' % t for t in XCV_TFS))),
            ('the r line', 'ws{TF}r, the stored r: StochRSI %s (Joe notation k_len|rsi|stc|src)'
             % '|'.join(str(x) for x in (ln.SPEC['r'][0][3], ln.SPEC['r'][0][1], ln.SPEC['r'][0][2], ln.SPEC['r'][0][4]))),
            ('towards - HIS 1108 RULING', "step 1's trajectory reader with no anchor"),
            ('the scan range - HIS 1108', 'no longer read. The report takes its x lines from XCV_TFS'),
            ('duplicates - HIS 1108 RULING', 'the existing no-duplicate-at-one-bar rule applies. Two cadence '
             'events whose x cross lands on one bar are one event'),
            ('the hold - HIS 1108 RULING', 'FDM_X10_WOB %d bars = %d s, counting the cross bar. He tried it '
             'without - *"there is no hold - the cross is read raw"* - then reversed on the 02:22:00 evidence: '
             '*"ok - that makes the wob necessary"*'
             % (int(K.FDM_X10_WOB), int(K.FDM_X10_WOB) * 5)),
            ('the race start - HIS 1108 RULING', 'the CADENCE WINDOW OPEN, which is ws1b\'s own oob '
             'excursion start - his *"accept an x-cross that fires inside a cadence window"*. Not the cadence '
             'event bar, so a cross that fired while ws1b was still oob belongs to this event'),
            ('the race bound - HIS 1108 RULING', 'the next cadence event on EITHER side, strictly after this '
             'one. His *"the next {any_}cadence"*. The tape end only when no cadence event follows'),
            ('the walk back - HIS 1108 RULING', 'UNBOUNDED. The extremum may sit BEFORE the cadence event and '
             'on 2026-08-25 it does on 29 of the 56 extremum rows - his *"finding an extremum before the '
             'cadence event is fine"*')]
    return ['# %s, %s, %s side' % (REPORT_NAME, day, SIDE_NAME[side]), ''] + table(rows)


def main(day):
    LN = F2.load()
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    for side in (+1, -1):
        evs = F2.cadence_events(LN, side, A, B)
        out = legend(LN, day, side, len(evs))
        for i, (ev, s0, _) in enumerate(evs):
            out += report(LN, side, int(ev), '%d of %d' % (i + 1, len(evs)), int(s0))
        p = os.path.join(OUT, 'sandbox_xcross_%s_%s.txt' % (day, SIDE_NAME[side]))
        with open(p, 'w') as fh:
            fh.write('\n'.join(out) + '\n')
        print(p, len(evs), 'cadence events')


if __name__ == '__main__':
    for k_, lv, ruled, ok in SK.check():                            # printed FIRST, refuses off-ruled
        print('%-14s live %-10s ruled %-10s %s' % (k_, lv, ruled, 'ok' if ok else 'OFF THE BANK'),
              file=sys.stderr if '--fake' in sys.argv else sys.stdout)
    if '--fake' in sys.argv:
        fake_main()
    else:
        main(sys.argv[1] if len(sys.argv) > 1 else '2026-08-25')
