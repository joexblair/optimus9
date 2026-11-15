"""Read fdm3-oracle's rows and collate his x/e-cross and AW-flip gates. A PROBE, not either scenario's code.

GOAL: answer his 1114 xe-exhaust and aw-exhaust specs from THE ORACLE'S OWN ROWS - *"all references
are based on oracle's rows"* - without rebuilding anything the oracle already holds.

IT READS THE LIVE SERVICE, NOT THE TAPE. fdm3-oracle takes ~18 minutes to start and holds its matrix
in memory with no disk cache, so a probe that rebuilt the matrix would pay that every run. The
running service serves /meta and /rows, so this reads those. ws1b and gcws30b are not in those rows,
so they come off the cached lines in the oracle's own row frame.

HIS 1114 RULINGS, all four built in here:
  #1 the N rows belong to the SCENARIO, not to the Nof15 - *"'are contained within no more than
     {knob:4,'fdm3-4-ltf-aws-rows'} consecutive rows' describes the N rows for the 4-ltf-aws
     scenario"*. His "13of15" inside 4-ltf-aws is shorthand for his own longer sentence.
  #2 N IS A MINIMUM - *"14 or 15 collective x/e crosses will qualify 13of15 and 14of15"*.
  #3 THE N ROWS ARE A WINDOW - *"if all of the gates are present inside the window, then the mech
     (the scenario) qualifies"*. So the window ends on the row it qualifies on: every gate is
     already inside it, and nothing later than that row is read.
  #4 the oracle holds no trades, only data, read from either target-side by the flip-pivots mode -
     *"the incoming trade, the one that is curated, will be using the appropriately curated data"*.

THE ROW LAYOUT comes from fdm3_oracle.build()'s own `cols` order, not from a guess:

    offset                      width      what
    0                           17         r-pred per line, gcws15 gcws30 ws1..ws15
    17                          2          the two sums, ws16-22 and ws23-30
    19                          17         the TO/AW code per line
    36                          4          the TO/AW counts, 2 per sum
    40                          17         THE CROSS CODE per line  <- what this probe reads
    57                          2          the TO(exf) counts per sum
    59                          4          M-no-rev TF, value lo, value hi, THE ROW'S TARGET-SIDE

THE CROSS CODE's bits, his 1110 and 1113: 1 an x-cross, 2 an e-cross, 3 both, on the row's
target-side; +4 the line reads AW on this row and TO on the row before - HIS TO -> AW FLIP; +8 ws1
only, TO(exf) on this row where the row before was not.

usage: oracle_rows.py                        # the rates over the whole tape, both pivot directions
       oracle_rows.py '<from>' '<to>'        # one row per minute in a span, with the window counts
       oracle_rows.py find '<from>' '<to>'   # HIS 1115 discovery over a span: the windows carrying
                                             # the signature of his 2026-09-24 22:48..22:50 window,
                                             # and the same with his two relaxations
"""
import datetime as dt
import io
import json
import os
import sys
import urllib.request

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fdm3_knobs as FK

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.chdir(V4)                                    # the tape is cwd-sensitive - every run prints its bar count
_err = sys.stderr
sys.stderr = io.StringIO()
try:
    import ln
    import v4_live_lines as LL
    import v4_closed_prev as CP
    import v4_knobs as K
finally:
    sys.stderr = _err

BASE = 'http://127.0.0.1:8788'
META = json.load(urllib.request.urlopen(BASE + '/meta'))
LINES, SUMS = META['lines'], META['sums']
STRIDE, NROWS = int(META['stride']), int(META['rows'])
T0, STEP = int(META['t0']), int(META['step'])
DAYS = dict((d, k) for d, k in META['days'])
O_TA = len(LINES) + len(SUMS)   # the TO/AW code per line: 0 none, 1 TO, 2 AW, 3 TO(exf), 4 AW(exf)
O_CROSS = O_TA + len(LINES) + 2 * len(SUMS)
O_SIDE = STRIDE - 1
#   THE ORACLE WAS REBUILT 2026-11-15 21:06 UTC: gcws15 and gcws30 dropped from the columns, the fence
#   locked at 23/77 with its button gone, the pivots +15 button gone, two new A buttons (ws1-ws6,
#   ws7-ws15), an SL% pair of bytes before M-no-rev, and /rows now taking flip, alo and ahi. Every
#   offset here is derived from /meta, so it followed the rebuild; this asserts the shape anyway.
assert STRIDE == len(LINES) + len(SUMS) + len(LINES) + 2 * len(SUMS) + len(LINES) + len(SUMS) + 6, STRIDE
#   HIS 1114: *"derived from ws1 to ws15"*. gcws15 and gcws30 are in the oracle's LINES and are NOT part of
#   either scenario's count.
WS = [(i, int(n[2:])) for i, n in enumerate(LINES) if n.startswith('ws') and int(n[2:]) <= 15]
assert [tf for _i, tf in WS] == list(range(1, 16)), WS

AWS_MAXTF = 6                   # HIS knob fdm3-4-ltf-aws-maxTF: the AW flips count on ws1..ws6
AWS_FLIPS = 4                   # HIS 4-ltf-aws: *">=4 AW flips on the same row"*
AWS_ROWS = 4                    # HIS knob fdm3-4-ltf-aws-rows: the window the gates sit inside
AWS_NOF15 = 13                  # HIS 4-ltf-aws: *">=13 of the ws1 to ws15 TFs"*, a MINIMUM
ALLIN_ROWS = 2                  # HIS xe-all-in: *"15of15 prints collectively in 2 rows"*
ALLIN_NOF15 = 15
#   HIS 1115 LTF-xcross knobs, his names and his values
LTFX_HITS = 6                   # fdm3-ltf-xcross-hits: TFs populated with an X-CROSS, not an e-cross
LTFX_ROWS = 2                   # fdm3-ltf-xcross-rows: the window those hits sit in
LTFX_MAXTF = 8                  # fdm3-ltf-xcross-maxTF: the hits count on ws1..ws8
LTFX_N15_ROWS = 3               # fdm3-ltf-xcross-nof15-rows: the outer window the hit window sits inside
LTFX_N15 = 13                   # HIS 13of15 inside LTF-xcross, an e-cross OR an x-cross as he defined it
LTFX_AW_PRINTS = 4              # fdm3-min-aw-prints: fields reading AW(*) inside the outer window
LTFX_AW_FLIPS = 2               # fdm3-min_aw_flips: new AW's - the TO -> AW flip - inside the outer window
#   HIS 1115 SIDENOTE: *"the 20/80 mom fence is now a 23/77 fence. this impacts the AW/TO(exf/inf)
#   timestamps"*. The oracle already serves that fence, so every AW/TO read here asks for it. v4_knobs
#   FDM_FNC_2080 is UNTOUCHED at 20.0 until he rules whether the 23 reaches its other readers.
MOM_FNC = int(FK.MOM_FNC)       # the banked fdm3 fence, his 1115 23/77 - now LOCKED in the oracle too
assert int(META['fence']) == MOM_FNC, (META['fence'], MOM_FNC)

#   HIS 1115 ltf-5aw-6x. Its shared knobs are the LTF-xcross ones - *"the knob reprints are not
#   duplications - this mech uses the same values"* - except that he wrote {knob:1} against
#   fdm3-ltf-xcross-rows where that knob is banked at 2. OPEN, so both are counted.
AW6X_N15 = 10                   # his *"3 consecutive rows printing 10of15"*
AW6X_EXF_MAXTF = (8, 15)        # his *"<=1 TFs between ws8 and ws15 printing exf"*, inclusive
AW6X_EXF_MAX = 1
AW6X_AW_PRINTS = 10             # his `fdm3-ltf-5aw-6x-min-aw-prints`
AW6X_AW_FLIPS = 5               # his `fdm3-ltf-5aw-6x-min-aw-flips`

#   HIS 1115 REFERENCE WINDOW, 2026-09-24 22:48:00 .. 22:50:00, as it reads at that fence:
#   *"I see 8 AW flips and a 14of15 event in the 09-24 2248 to 2250 window, with an abundance of x
#   crosses"*. Its three print counts and its row count are the signature the discovery searches for.
REF_WINDOW = '2026-09-24 22:48:00'
REF_ROWS = 3                    # his 2248, 2249, 2250
REF_NOF15 = 14                  # his *"14of15 event"*, his own 2 row Nof15 definition, peak inside the window
REF_FLIPS = 8                   # his *"8 AW flips"* - new AW PRINTS over ws1..ws15
#   HIS 1115 COUNTING RULE: *"the x and e crosses are 1 type per TF per scenario (ie the max for any
#   scenario is 15 of e and 15 of x)"*. So a cross is counted ONCE per timeframe per window however
#   many times it prints inside it, and the ceiling on either count is 15. His own per-TF double
#   prints stay unused until he rules on them. The new-AW count is NOT covered by this: he ruled only
#   the crosses, and his *"8 AW flips"* is a print count.
REF_XTFS = 12                   # his *"abundance of x crosses"*, measured: 12 of ws1..ws15 carry an x-cross
#   HIS #5 gate, asked of the xe-all-in rows: ws1b oob, or gcws30b external of a 7/93 fence
OOB = float(K.FDM_FNC_OOB) if hasattr(K, 'FDM_FNC_OOB') else 15.0
G30_FNC = 7.0

#   THE ORACLE'S OWN ROW FRAME, rebuilt here so a line can be read where a row reads it. fdm3_oracle.build():
#   row i is the ws1 bar opening at t0 + 60 s * i, and its print bar is 12 five-second bars on - *"the cell is
#   the value where closed-prev shows it"*.
TS = np.asarray(ln.ts, np.int64)
FIRST = np.flatnonzero((TS % 60000) == 0)
FIRST = FIRST[FIRST + 12 < ln.N]
PRT = FIRST + 12
assert len(PRT) == NROWS, (len(PRT), NROWS)
assert TS[FIRST[0]] == T0, 'the row frame does not start where the oracle says it does'
assert (TS[PRT] - TS[FIRST] == 60000).all(), 'a print bar is not one ws1 bar on from its row'


def closed(emerging, tf_seconds):
    """The chart-matched value of an emerging line - closed-prev, the banked read for everything but lift-off."""
    return np.asarray(CP.series(np.asarray(emerging, float), tf_seconds), float)


W1B = closed(ln.line('ws1b'), 60)
G30B = closed(LL.sub_line('gcws30b'), 30)


def U(k):
    return dt.datetime.fromtimestamp((T0 + int(k) * STEP) / 1000,
                                     dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def K_OF(s):
    return (int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                .replace(tzinfo=dt.timezone.utc).timestamp() * 1000) - T0) // STEP


O_TA = len(LINES) + len(SUMS)   # the TO/AW code per line: 0 none, 1 TO, 2 AW, 3 TO(exf), 4 AW(exf)


def load(flip=0, alo=0, ahi=0, chunk=20000):
    """-> a dict of [n,16] bool per ws TF 1..15, plus the row's target-side [n].

    'cross'  an x-cross OR an e-cross - what his Nof15 counts
    'x'      an x-cross alone - what his LTF-xcross hits count
    'e'      an e-cross alone, printed beside the x count so the mix is visible
    'exf'    the cell reads TO(exf) or AW(exf) - at or past the fence pair on the target side
    'newaw'  the TO -> AW flip - his *"new AW"*
    'aw'     the cell reads AW(*), either AW(inf) or AW(exf)
    """
    out = {k: np.zeros((NROWS, 16), bool) for k in ('cross', 'x', 'e', 'newaw', 'aw', 'exf')}
    sd = np.zeros(NROWS, np.int8)
    for a in range(0, NROWS, chunk):
        n = min(chunk, NROWS - a)
        u = '%s/rows?start=%d&count=%d&flip=%d&alo=%d&ahi=%d' % (BASE, a, n, flip, alo, ahi)
        b = np.frombuffer(urllib.request.urlopen(u).read(), np.int8).reshape(-1, STRIDE)
        for j, tf in WS:
            c = b[:, O_CROSS + j].astype(int)
            out['cross'][a:a + n, tf] = (c & 3) > 0
            out['x'][a:a + n, tf] = (c & 1) > 0
            out['e'][a:a + n, tf] = (c & 2) > 0
            out['newaw'][a:a + n, tf] = (c & 4) > 0
            st = b[:, O_TA + j].astype(int)
            out['aw'][a:a + n, tf] = np.isin(st, (2, 4))
            #   HIS *"printing exf"*: the ex-fence bit set - 3 TO(exf), 4 AW(exf). `ex` includes oob.
            out['exf'][a:a + n, tf] = np.isin(st, (3, 4))
        sd[a:a + n] = b[:, O_SIDE]
    return out, sd


def window(a, rows):
    """HIS #3: a window of `rows` oracle rows ENDING on the row, so nothing later than the row is read.
    -> the OR of `a` over the window, per row."""
    c = a.copy()
    for d in range(1, rows):
        s = np.zeros_like(a)
        s[d:] = a[:-d]
        c = c | s
    return c


def count(a, rows):
    """How many CELLS of `a` sit inside the window ending on the row, over ws1..ws15."""
    c = a[:, 1:16].astype(np.int32)
    t = c.copy()
    for d in range(1, rows):
        s = np.zeros_like(t)
        s[d:] = c[:-d]
        t = t + s
    return t.sum(1)


def ltf_xcross(R, aw_cells=True):
    """HIS 1115 LTF-xcross. -> bool per row, True on the row the scenario qualifies on.

    HIS #3 holds: every window ENDS on the qualifying row, so nothing later than it is read. The
    outer window is LTFX_N15_ROWS rows; the hit window is LTFX_ROWS rows and must sit INSIDE it,
    which at these values is either its last two rows or the two before them.

    HIS 13of15 here is read COLLECTIVELY over the outer window. His own five examples settle it:
    not one of them has all three rows carrying 13 on their own.
    """
    hits = window(R['x'], LTFX_ROWS)[:, 1:LTFX_MAXTF + 1].sum(1)
    g1 = np.maximum(hits, np.roll(hits, 1)) >= LTFX_HITS
    g2 = nof15(R['cross'], LTFX_N15_ROWS) >= LTFX_N15
    #   OPEN: his *">=4 fields prints `AW(*)`"* - 4 cells inside the window, or 4 distinct TFs
    g3a = ((count(R['aw'], LTFX_N15_ROWS) if aw_cells
            else window(R['aw'], LTFX_N15_ROWS)[:, 1:16].sum(1)) >= LTFX_AW_PRINTS)
    g3b = count(R['newaw'], LTFX_N15_ROWS) >= LTFX_AW_FLIPS
    return g1 & g2 & g3a & g3b


def nof15(x, rows):
    """How many of ws1..ws15 printed an x OR an e cross anywhere in the window. HIS *"collectively"*."""
    return window(x, rows)[:, 1:16].sum(1)


def direction(sd, a, z):
    """The incoming pseudo trade's direction over rows a..z-1. -> 'LONG', 'SHORT', 'none', or both when the
    window straddles a flip.

    THE SIDE IS READ, NEVER DERIVED. The oracle's last row byte is the pseudo trade's TARGET side at the
    row's print bar - -1 LOW, +1 HIGH - and towards_away.pseudo_trades() sets a trade's side to the
    NEGATIVE of its ws2Mage pivot's side, so a LOW pivot makes a trade whose target is the HIGH. A trade
    hunting the HIGH oob is LONG and one hunting the LOW oob is SHORT, which is the banked mapping.

    The trade live on a row is the one that closes next, so it is the INCOMING one there.
    """
    seen = [{-1: 'SHORT', 0: 'none', +1: 'LONG'}[int(v)] for v in dict.fromkeys(sd[a:z])]
    return ' then '.join(seen)


def ltf_5aw_6x(R, xrows=1, aw_cells=False):
    """HIS 1115 ltf-5aw-6x. -> bool per row, True on the row the scenario qualifies on.

    HIS #3 holds: every window ENDS on the qualifying row. The outer window is his
    fdm3-ltf-xcross-nof15-rows, 3 rows; the x-cross hit window is `xrows` rows and sits inside it.

    `xrows` 1 is the value he wrote in this spec, 2 is where fdm3-ltf-xcross-rows is banked.
    `aw_cells` False counts DISTINCT TIMEFRAMES reading AW(*), his 1115 ruling on the same wording
    in LTF-xcross; True counts cells.
    """
    rows = int(FK.LTF_XCROSS_NOF15_ROWS)
    lo, hi = AW6X_EXF_MAXTF
    hits = window(R['x'], xrows)[:, 1:int(FK.LTF_XCROSS_MAXTF) + 1].sum(1)
    #   the hit window sits anywhere inside the outer one, so take the best placement
    g1 = np.zeros(NROWS, bool)
    for d in range(0, rows - xrows + 1):
        g1 |= np.roll(hits, d) >= int(FK.LTF_XCROSS_HITS)
    g1[:rows] = False
    g2 = nof15(R['cross'], rows) >= AW6X_N15
    #   his exf line carries no window of its own, so it inherits the scenario's outer window
    g3 = window(R['exf'], rows)[:, lo:hi + 1].sum(1) <= AW6X_EXF_MAX
    g4 = ((count(R['aw'], rows) if aw_cells
           else window(R['aw'], rows)[:, 1:16].sum(1)) >= AW6X_AW_PRINTS)
    g5 = count(R['newaw'], rows) >= AW6X_AW_FLIPS
    return g1 & g2 & g3 & g4 & g5


def find(R, SD, a, z):
    """HIS 1115 DISCOVERY over rows a..z. Prints the windows carrying his reference signature, then the
    counts under each relaxation he named - *"reducing the required print counts by a small amount, or
    increasing the row counts by a small amount"*.

    A WINDOW IS NAMED BY ITS FIRST ROW here, because his own words name his by its first row - *"the
    09-24 2248 to 2250 window"*. Overlapping starts are grouped into one cluster, since the same
    stretch qualifying three times running is one pattern, not three.
    """
    nof = nof15(R['cross'], 2)           # HIS Nof15 event, his own 2 row definition
    cases = [('his window as it reads', REF_ROWS, REF_NOF15, REF_FLIPS, REF_XTFS),
             ('print counts down 1', REF_ROWS, REF_NOF15 - 1, REF_FLIPS - 1, REF_XTFS - 1),
             ('print counts down 2', REF_ROWS, REF_NOF15 - 1, REF_FLIPS - 2, REF_XTFS - 2),
             ('rows up 1', REF_ROWS + 1, REF_NOF15, REF_FLIPS, REF_XTFS),
             ('rows up 2', REF_ROWS + 2, REF_NOF15, REF_FLIPS, REF_XTFS)]
    out = {}
    print('| the relaxation | rows per window | Nof15 peak | new AW prints | x-cross timeframes '
          '| windows | clusters |')
    print('|' + '---|' * 7)
    for lab, rows, n, f, xp in cases:
        hit = [i for i in range(a, z - rows)
               if nof[i:i + rows].max() >= n
               and int(R['newaw'][i:i + rows, 1:16].sum()) >= f
               and int(R['x'][i:i + rows, 1:16].any(0).sum()) >= xp]
        hs = set(hit)
        cl = [h for i, h in enumerate(hit) if i == 0 or h - hit[i - 1] > 1]
        out[lab] = (hit, cl, rows)
        print('| %s | %d | >=%d | >=%d | >=%d | %d | %d |' % (lab, rows, n, f, xp, len(hit), len(cl)))
    hit, cl, rows = out['his window as it reads']
    hs = set(hit)
    ref = K_OF(REF_WINDOW)

    def run(h):
        n = 1
        while h + n in hs:
            n += 1
        return n
    print()
    print('| the window | its last row | the incoming pseudo trade | Nof15 peak inside it '
          '| new AW prints | x-cross timeframes | e-cross timeframes | AW(*) timeframes | his own |')
    print('|' + '---|' * 9)
    for h in cl:
        w = slice(h, h + rows)
        print('| %s | %s | %s | %d | %d | %d | %d | %d | %s |'
              % (U(h), U(h + rows - 1)[11:19], direction(SD, h, h + rows),
                 int(nof[h:h + rows].max()), int(R['newaw'][w, 1:16].sum()),
                 int(R['x'][w, 1:16].any(0).sum()), int(R['e'][w, 1:16].any(0).sum()),
                 int(R['aw'][w, 1:16].any(0).sum()), 'HIS' if h <= ref <= h + run(h) - 1 else '-'))
    return out


def excursion():
    """HIS #5: ws1b oob, or gcws30b external of 7/93, at the row's print bar."""
    return ((np.abs(W1B[PRT] - 50.0) >= (50.0 - OOB))
            | (np.abs(G30B[PRT] - 50.0) >= (50.0 - G30_FNC)))


def control(R):
    """HIS OWN 09-23 0028 EXAMPLE as the live control: 14 of ws1..ws15 crossing over 0027 and 0028,
    ws15 the only one missing. Verified against his words before the oracle was rebuilt; every run
    checks it after, so a changed row layout cannot pass silently."""
    k = K_OF('2026-09-23 00:28:00')
    tfs = [t for t in range(1, 16) if R['cross'][k - 1:k + 1, t].any()]
    assert len(tfs) == 14 and 15 not in tfs, tfs
    print('CONTROL ok: his 09-23 0028 reads 14of15 over 0027+0028, ws15 the only one missing')


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == 'aw6x':
        R, _SD = load()
        control(R)
        a, z = K_OF(sys.argv[2]), K_OF(sys.argv[3])
        print('tape bars: %d. the oracle fence is %g/%g.' % (ln.N, META['fence'], 100 - META['fence']))
        print('| the reading | fires between %s and %s |' % (sys.argv[2], sys.argv[3]))
        print('|---|---|')
        for xr in (1, 2):
            for cells in (False, True):
                m = ltf_5aw_6x(R, xrows=xr, aw_cells=cells)
                print('| x-hits inside %d row%s, AW(*) as %s | %d |'
                      % (xr, '' if xr == 1 else 's', 'cells' if cells else 'distinct timeframes',
                         int(m[a:z + 1].sum())))
        return
    if len(sys.argv) >= 4 and sys.argv[1] == 'find':
        R, SD = load()
        control(R)
        print('tape bars: %d. the fdm3 fence is %g/%g.' % (ln.N, FK.MOM_FNC, 100 - FK.MOM_FNC))
        print('a cross counts ONCE per timeframe per window, his 1115 rule, so either count tops out at 15.')
        print('his reference: %s .. %s, Nof15 %d, new AW prints %d, x-cross timeframes %d'
              % (REF_WINDOW, U(K_OF(REF_WINDOW) + REF_ROWS - 1), REF_NOF15, REF_FLIPS, REF_XTFS))
        print()
        find(R, SD, K_OF(sys.argv[2]), K_OF(sys.argv[3]))
        return
    days = NROWS / 1440.0
    exc = excursion()
    print('tape bars: %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
    print('legend: Nof15 = N or more of ws1..ws15 crossed inside the window (HIS #2, a minimum). '
          'the window ENDS on the row (HIS #3). ws1b oob = %.0f/%.0f, gcws30b fence = %.0f/%.0f.'
          % (OOB, 100 - OOB, G30_FNC, 100 - G30_FNC))
    for flip in (0, 1):
        R, sd = load(flip=flip)
        x, aw = R['cross'], R['newaw']
        lab = 'pivots as found' + (', flipped' if flip else '')
        c = nof15(x, ALLIN_ROWS)
        f4 = nof15(x, AWS_ROWS)
        nf = window((aw[:, 1:AWS_MAXTF + 1].sum(1) >= AWS_FLIPS)[:, None], AWS_ROWS)[:, 0]
        print()
        print('| %s | rows | per day |' % lab)
        print('|---|---|---|')
        print('| rows with no target-side, so no cross can print | %d | %.1f |'
              % (int((sd == 0).sum()), (sd == 0).sum() / days))
        for n in (13, 14, 15):
            m = c >= n
            print('| %dof15 in a %d row window | %d | %.1f |' % (n, ALLIN_ROWS, int(m.sum()), m.sum() / days))
        m = c >= ALLIN_NOF15
        print('| xe-all-in - %dof15 in %d rows | %d | %.1f |'
              % (ALLIN_NOF15, ALLIN_ROWS, int(m.sum()), m.sum() / days))
        print('| xe-all-in + ws1b oob or gcws30b ex-%.0f/%.0f | %d | %.1f |'
              % (G30_FNC, 100 - G30_FNC, int((m & exc).sum()), (m & exc).sum() / days))
        print('| %d+ AW flips on one row within ws1..ws%d | %d | %.1f |'
              % (AWS_FLIPS, AWS_MAXTF, int(nf.sum()), nf.sum() / days))
        print('| %dof15 in a %d row window | %d | %.1f |'
              % (AWS_NOF15, AWS_ROWS, int((f4 >= AWS_NOF15).sum()), (f4 >= AWS_NOF15).sum() / days))
        a4 = nf & (f4 >= AWS_NOF15)
        print('| 4-ltf-aws - both gates inside the %d row window | %d | %.1f |'
              % (AWS_ROWS, int(a4.sum()), a4.sum() / days))
        print('| 4-ltf-aws + ws1b oob or gcws30b ex-%.0f/%.0f | %d | %.1f |'
              % (G30_FNC, 100 - G30_FNC, int((a4 & exc).sum()), (a4 & exc).sum() / days))
        for cells in (True, False):
            m = ltf_xcross(R, aw_cells=cells)
            print('| LTF-xcross, AW(*) read as %s | %d | %.1f |'
                  % ('cells' if cells else 'distinct TFs', int(m.sum()), m.sum() / days))
    if len(sys.argv) >= 3:
        R, sd = load(fnc=MOM_FNC)
        x, aw = R['cross'], R['newaw']
        c, f4 = nof15(x, ALLIN_ROWS), nof15(x, AWS_ROWS)
        lx = ltf_xcross(R)
        xh = window(R['x'], LTFX_ROWS)[:, 1:LTFX_MAXTF + 1].sum(1)
        awc = count(R['aw'], LTFX_N15_ROWS)
        nac = count(R['newaw'], LTFX_N15_ROWS)
        a, z = K_OF(sys.argv[1]), K_OF(sys.argv[2])
        print()
        print('| the row | its target-side | the TFs that crossed | %d row Nof15 | %d row Nof15 '
              '| AW flips ws1..ws%d | x-hits ws1..ws%d over %d rows | AW(*) cells over %d rows '
              '| new AW cells over %d rows | LTF-xcross | ws1b | gcws30b |'
              % (ALLIN_ROWS, AWS_ROWS, AWS_MAXTF, LTFX_MAXTF, LTFX_ROWS, LTFX_N15_ROWS, LTFX_N15_ROWS))
        print('|' + '---|' * 12)
        for k in range(a, z + 1):
            tfs = [str(tf) for tf in range(1, 16) if x[k, tf]]
            fl = [str(tf) for tf in range(1, AWS_MAXTF + 1) if aw[k, tf]]
            print('| %s | %+d | %d: %s | %d | %d | %d: %s | %d | %d | %d | %s | %.2f | %.2f |'
                  % (U(k), sd[k], len(tfs), ','.join(tfs), c[k], f4[k], len(fl),
                     ','.join(fl) or '-', xh[k], awc[k], nac[k], 'FIRES' if lx[k] else '-',
                     W1B[PRT[k]], G30B[PRT[k]]))


main()
