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
    sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1109_towards_away')
    import towards_away as TA          # HIS 1118 answer 2: *"use the pivot based psuedo-trades"*
finally:
    sys.stderr = _err

#   HIS 1116: the scenarios read 8789, which carries his fdm3-fence-reset-TO at 33/67 and locks the
#   A buttons. The port is a banked knob, so an off-bank run refuses rather than reading the wrong page.
#   HIS 1118, asked which oracle orac-exhaust's row counts mean: *"1, 30sec"*. That mech alone reads
#   the 30 second page; every other mode keeps the 60 second one he banked on 1117. Both ports are
#   banked knobs, so neither is a free choice at the command line.
MODE = sys.argv[1] if len(sys.argv) > 1 else ''
PORT = int(FK.ORAC_EXHAUST_PORT) if MODE == 'orac-exhaust' else int(FK.ORACLE_PORT)
BASE = 'http://127.0.0.1:%d' % PORT
META = json.load(urllib.request.urlopen(BASE + '/meta'))
LINES, SUMS = META['lines'], META['sums']
STRIDE, NROWS = int(META['stride']), int(META['rows'])
T0, STEP = int(META['t0']), int(META['step'])
DAYS = dict((d, k) for d, k in META['days'])
#   HIS 1117 *"I'm not using r-pred at all so it can be disabled"*: with it off the page stores no
#   r-pred byte at all, so the row's first block - one byte per line and one per sum - is NOT there
#   and the TO/AW codes start at byte 0. The page says which it is, in /meta.
_RP = len(LINES) + len(SUMS) if META.get('rpred', True) else 0
O_TA = _RP                      # the TO/AW code per line: 0 none, 1 TO, 2 AW, 3 TO(exf), 4 AW(exf)
O_CROSS = O_TA + len(LINES) + 2 * len(SUMS)
O_TOEXF = O_CROSS + len(LINES)  # per sum column, how many of ITS lines read TO(exf) - his `toexf-gate`
O_SIDE = STRIDE - 1
#   THE ORACLE WAS REBUILT 2026-11-15 21:06 UTC: gcws15 and gcws30 dropped from the columns, the fence
#   locked at 23/77 with its button gone, the pivots +15 button gone, two new A buttons (ws1-ws6,
#   ws7-ws15), an SL% pair of bytes before M-no-rev, and /rows now taking flip, alo and ahi. Every
#   offset here is derived from /meta, so it followed the rebuild; this asserts the shape anyway.
#   THE ROW GREW TWICE at his 1116 and 1117: an up/dn block of len(LINES) bytes after the TO(exf) counts, then a
#   second M-no-rev column's three bytes. O_TA and O_CROSS sit before both inserts and are unmoved, and the side is
#   still the last byte. The stride is derived from the page's own layout rather than a list of accepted values, so
#   a page serving any shape this reader does not expect fails by name.
_TAIL = 3 + 3 * len(META.get('mnrtops', [1]))      # SL% as an int16, then each M-no-rev column's TF and value
_WANT = (_RP + len(LINES) + 2 * len(SUMS) + len(LINES) + len(SUMS)
         + (len(LINES) if 'updn' in META else 0) + _TAIL)
assert STRIDE == _WANT, ('the page\'s row is not the shape this reader expects', STRIDE, _WANT)
#   HIS 1114: *"derived from ws1 to ws15"*. gcws15 and gcws30 are in the oracle's LINES and are NOT part of
#   either scenario's count.
WS = [(i, int(n[2:])) for i, n in enumerate(LINES) if n.startswith('ws') and int(n[2:]) <= 15]
assert [tf for _i, tf in WS] == list(range(1, 16)), WS

AWS_MAXTF = 6                   # HIS knob fdm3-4-ltf-aws-maxTF: the AW flips count on ws1..ws6
AWS_FLIPS = 4                   # HIS 4-ltf-aws: *">=4 AW flips on the same row"*
AWS_ROWS = 4                    # HIS knob fdm3-4-ltf-aws-rows: the window the gates sit inside
AWS_NOF15 = 13                  # HIS 4-ltf-aws: *">=13 of the ws1 to ws15 TFs"*, a MINIMUM
NOF_ROWS = 2                    # HIS Nof15 event's own window - the 2 rows he used to define it
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
#   THE PAGE MUST BE THE ONE HIS RULING NAMES: its reset fence and its locked A state have to match
#   the bank, or every count below is off a different mech. On the bank this is a hard stop; under
#   W_FDM3_EXPERIMENT it prints the mismatch instead, so the two pages can be compared on purpose.
_PAGE = [('its reset fence', META.get('reset'), float(FK.FENCE_RESET_TO)),
         ('its ex-fence fence', META.get('fence'), float(FK.ORACLE_FENCE)),
         ('its pivot offset', META.get('shift'), int(FK.ORACLE_SHIFT)),
         ('its M-no-rev ceilings', META.get('mnrtops'), list(FK.MNR_TOPS)),
         ('its locked A state', META.get('alock'), [int(FK.A_WS1_WS6), int(FK.A_WS7_WS15)]),
         ('its Mage-side-of-50 paint', META.get('mage50'), int(FK.ORACLE_MAGE50_PCT))]
_OFF = [(w, g, want) for w, g, want in _PAGE
        if (float(g) if w.endswith('fence') and g is not None else g) != want]
if _OFF:
    _msg = '; '.join('%s is %r, the bank says %r' % t for t in _OFF)
    if FK.RULED_OK:
        raise SystemExit('the oracle on port %d is not the page the bank names: %s'
                         % (PORT, _msg))
    sys.stderr.write('# the page on port %d is NOT the banked one: %s\n' % (PORT, _msg))

#   HIS 1115 ltf-5aw-6x. Its shared knobs are the LTF-xcross ones - *"the knob reprints are not
#   duplications - this mech uses the same values"* - except the x-cross hit window, which he gave
#   its own knob: *"use this new knob: fdm3-ltf-5aw-6x-xcross-rows, value=1"*.
AW6X_N15 = 10                   # his *"3 consecutive rows printing 10of15"*
AW6X_EXF_MAXTF = (8, 15)        # his *"<=1 TFs between ws8 and ws15 printing exf"*, inclusive
AW6X_EXF_MAX = 1
AW6X_AW_PRINTS = int(FK.LTF_5AW_6X_MIN_AW_PRINTS)   # his `fdm3-ltf-5aw-6x-min-aw-prints`
AW6X_AW_FLIPS = int(FK.LTF_5AW_6X_MIN_AW_FLIPS)     # his `fdm3-ltf-5aw-6x-min-aw-flips`

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
#   row i opens at t0 + step * i and its print bar is step/5 five-second bars on - *"the cell is the value
#   where closed-prev shows it"*.
#   THE ROW LENGTH COMES FROM THE PAGE, not from a 60 that was true until his 1117 30 second page: at 30
#   second rows a hardcoded 60 s frame would read every cell against the wrong bar.
TS = np.asarray(ln.ts, np.int64)
ROW_MS = STEP                                   # ms per row, straight off /meta
RB = ROW_MS // 5000                             # 5 s bars per row
assert RB * 5000 == ROW_MS, ('the page row is not a whole number of 5 s bars', ROW_MS)
FIRST = np.flatnonzero((TS % ROW_MS) == 0)
FIRST = FIRST[FIRST + RB < ln.N]
PRT = FIRST + RB
assert len(PRT) == NROWS, (len(PRT), NROWS)
assert TS[FIRST[0]] == T0, 'the row frame does not start where the oracle says it does'
assert (TS[PRT] - TS[FIRST] == ROW_MS).all(), 'a print bar is not one row on from its row'


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


def load(flip=0, alo=None, ahi=None, chunk=20000):
    """-> a dict of [n,16] bool per ws TF 1..15, plus the row's target-side [n].

    'cross'  an x-cross OR an e-cross - what his Nof15 counts
    'x'      an x-cross alone - what his LTF-xcross hits count
    'e'      an e-cross alone, printed beside the x count so the mix is visible
    'exf'    the cell reads TO(exf) or AW(exf) - at or past the fence pair on the target side
    'toexf'  the cell reads TO(exf) ALONE. HIS 1116 scene1 distinguishes the two: his 09-22 0216
             example passes max-allowed-*-toexf-at-last-row only on TO(exf), not on either code
    'newaw'  the TO -> AW flip - his *"new AW"*
    'aw'     the cell reads AW(*), either AW(inf) or AW(exf)
    """
    #   HIS 1116: the A ws1-ws6 button is the LIVE MACHINE, so the banked state is the default here
    #   and a caller has to pass something else on purpose.
    alo = int(FK.A_WS1_WS6) if alo is None else int(alo)
    ahi = int(FK.A_WS7_WS15) if ahi is None else int(ahi)
    out = {k: np.zeros((NROWS, 16), bool) for k in ('cross', 'x', 'e', 'newaw', 'aw', 'exf', 'toexf')}
    #   HIS 1118 `toexf-gate`: the ws16-22 and ws23-30 columns each print how many of their own lines
    #   read TO(exf). His condition1 reads *"the sum of the 2 columns"*, kept here per column so the
    #   sum is taken where it is used.
    out['sumtoexf'] = np.zeros((NROWS, len(SUMS)), np.int32)
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
            out['toexf'][a:a + n, tf] = st == 3
        for k in range(len(SUMS)):
            out['sumtoexf'][a:a + n, k] = b[:, O_TOEXF + k].astype(np.int32)
        sd[a:a + n] = b[:, O_SIDE]
    return out, sd


def mage50(chunk=20000):
    """HIS 1118 -> (m50, MNR). m50 is [n,16] int8 per ws TF 1..15: 0 neither, 1 over 50.00, 2 under.

    The Mage's side of 50 rides in bits 4-5 of each line's up/dn byte, so the row did not grow and
    this reader's stride assert is unchanged. MNR is [(tf, value)] per M-no-rev column, kept so a
    row can be read beside the column that named it. THE CHECK BELOW DOES NOT USE IT: the
    paint reads the EMERGING Mage and that column reads the closed-prev one, so the two differ
    by design. mage50_check reads the line off the tape instead.
    """
    m50 = np.zeros((NROWS, 16), np.int8)
    MNR = [(np.zeros(NROWS, np.int16), np.zeros(NROWS, np.int32)) for _ in META['mnrtops']]
    for a in range(0, NROWS, chunk):
        n = min(chunk, NROWS - a)
        u = '%s/rows?start=%d&count=%d&flip=0&alo=%d&ahi=%d' % (BASE, a, n, int(FK.A_WS1_WS6),
                                                                int(FK.A_WS7_WS15))
        b = np.frombuffer(urllib.request.urlopen(u).read(), np.int8).reshape(-1, STRIDE)
        for j, tf in WS:
            m50[a:a + n, tf] = (b[:, int(META['updn']) + j].astype(int) >> 4) & 3
        for k, (tfs, vals) in enumerate(MNR):
            o = STRIDE - 1 - 3 * (len(MNR) - k)
            tfs[a:a + n] = b[:, o].astype(int)
            vals[a:a + n] = (b[:, o + 2].astype(int) << 8) | (b[:, o + 1].astype(int) & 255)
    return m50, MNR


def mage50_check(m50):
    """-> [(line, rows judged, rows the paint disagrees, the offending rows)] per ws1..ws15.

    THE INDEPENDENT CHECK: it reads ws{TF}Mage off the tape at each row's own print bar - the
    EMERGING value, his 1118 read - and demands 1 over 50.00, 2 under it, and 0 both at 50.00
    exactly and where the line has no value yet.
    """
    out = []
    for _j, tf in WS:
        v = np.asarray(ln.line('ws%dMage' % tf), float)[PRT]
        with np.errstate(invalid='ignore'):
            want = np.where(v > 50.0, 1, np.where(v < 50.0, 2, 0)).astype(np.int8)
        off = np.flatnonzero(m50[:, tf] != want)
        out.append(('ws%d' % tf, NROWS, len(off), off))
    return out


#   ── HIS 1118 orac-exhaust ────────────────────────────────────────────────────────────────────
#   HIS SPEC, verbatim: *"1) six x-crosses printing in 2 rows in lowband (refered to as `6x`) / ***the
#   next 2 must qualify within 3 rows, and those 3 rows encompass 6x*** / 2) lowband is printing >=5
#   AW(any) and 0 TOexf / 3) the conditional highband output: >=3 AW(any) are required if any of these
#   conditions qualify: condition1: ws>15 printed TO(exf): {>1}; condition2: more than 3 Mages have
#   been oob during the trade; condition3: ws1r did not cross to oob during the trade / IF all of
#   these highband conditions fail: highband must print 0 TOexf and >=1 x/e cross"*.
#   HIS 1118 ANSWERS: the page is the 30 second one; the trade is the pivot-based pseudo trade; *"the
#   zero TOexf condtion belongs to the final row, the other conditions are placed anywhere in the
#   three rows"*; condition1 adds the two sum columns; condition2 counts ws1..ws15 Mages.
#   HIS GENERAL NOTE: *"all sides are target-side unless otherwise specified"*, so the Mage oob and the
#   ws1r oob reads below are on the row's own target side.


def trade_frame(TR):
    """-> (tk, topen) per row: the pseudo trade the row sits in, and that trade's open BAR. -1 / -1
    before the first trade opens. TR is towards_away.pseudo_trades()'s trades, [(open, close, side)]."""
    o = np.asarray([t[0] for t in TR], np.int64)
    k = np.searchsorted(o, PRT, side='right') - 1
    tk = np.where(k >= 0, k, -1)
    return tk, np.where(tk >= 0, o[np.clip(tk, 0, len(o) - 1)], -1)


def _any_in_trade(flag, topen):
    """Did `flag` (per 5 s bar) fire anywhere from the trade's open bar to THIS row's print bar?

    CAUSAL BY CONSTRUCTION: the window closes on the row's own print bar, so no later bar is read.
    """
    c = np.concatenate(([0], np.cumsum(flag.astype(np.int64))))   # c[i] = flags in bars 0..i-1
    assert len(c) == len(flag) + 1
    lo = np.where(topen >= 0, topen, 0)
    assert (lo <= PRT).all(), 'a trade opens after the row that reads it'
    return (c[PRT + 1] - c[lo]) > 0


def orac_reads(TR):
    """Every trade-scoped read his conditions 2 and 3 need, per oracle row. -> dict of bool/int arrays."""
    tk, topen = trade_frame(TR)
    sd = np.asarray([t[2] for t in TR], np.int8)
    side = np.where(tk >= 0, sd[np.clip(tk, 0, len(sd) - 1)], 0)   # the row's trade target-side
    oobf = float(K.FDM_FNC_OOB) if hasattr(K, 'FDM_FNC_OOB') else 15.0
    #   HIS condition2, ws1..ws15 Mages, CLOSED-PREV and on the target side
    nmage = np.zeros(NROWS, np.int32)
    for tf in range(1, int(FK.ORAC_MAGE_HI) + 1):
        m = closed(ln.line('ws%dMage' % tf), tf * 60)
        with np.errstate(invalid='ignore'):
            hi, lo = _any_in_trade(m >= 100 - oobf, topen), _any_in_trade(m <= oobf, topen)
        nmage += np.where(side > 0, hi, np.where(side < 0, lo, False)).astype(np.int32)
    #   HIS condition3, ws1r crossing INTO oob during the trade, closed-prev, on the target side
    r1 = closed(ln.line('ws1r'), 60)
    with np.errstate(invalid='ignore'):
        inhi = (r1 >= 100 - oobf); inlo = (r1 <= oobf)
    xhi = np.zeros(len(r1), bool); xlo = np.zeros(len(r1), bool)
    xhi[1:] = inhi[1:] & ~inhi[:-1]; xlo[1:] = inlo[1:] & ~inlo[:-1]
    r1oob = np.where(side > 0, _any_in_trade(xhi, topen),
                     np.where(side < 0, _any_in_trade(xlo, topen), False))
    #   THE WALK, his general note: ws1r crosses to ib FROM oob, then walk to ws2r's AW flip, then to
    #   the first AW flip of the ws3r/ws4r/ws5r race. The row is gated in while that walk is running.
    bhi = np.zeros(len(r1), bool); blo = np.zeros(len(r1), bool)
    bhi[1:] = ~inhi[1:] & inhi[:-1]; blo[1:] = ~inlo[1:] & inlo[:-1]
    back = np.where(side > 0, bhi[PRT], np.where(side < 0, blo[PRT], False))
    return dict(tk=tk, topen=topen, side=side, nmage=nmage, r1oob=r1oob, backin=back)


def orac_walk(R, reads):
    """HIS general note's walk, as a gate. -> bool per row, True while the walk is running.

    STUB, and he asked for one: the second trigger - *"crosses to infence from ex-ws1r-mom-fence"* -
    is NOT built, because `ex-ws1r-mom-fence` is not yet defined. Only *"crosses to ib from oob"*
    starts a walk here, so the gate is NARROWER than his spec, never wider.
    MINE: a fresh trigger inside a running walk restarts it at stage 1.
    """
    aw2 = R['newaw'][:, 2]
    race = R['newaw'][:, 3] | R['newaw'][:, 4] | R['newaw'][:, 5]
    start, stage = reads['backin'], 0
    on = np.zeros(NROWS, bool)
    for i in range(NROWS):
        if start[i]:
            stage = 1                            # walking to ws2r's AW flip
        if stage == 1:
            on[i] = True
            if aw2[i]:
                stage = 2                        # now walking to the ws3/4/5r race's AW flip
        elif stage == 2:
            on[i] = True
            if race[i]:
                stage = 0
    return on


def orac_exhaust(R, reads, gate_window):
    """-> dict of the per-row verdicts his three states need. `gate_window` picks his condition1's
    span, which he has not ruled: 'row' reads the final row alone, 'trade' any row of the trade up
    to and including it."""
    lo_hi, hi_lo, hi_hi = int(FK.ORAC_LOW_HI), int(FK.ORAC_LOW_HI) + 1, int(FK.ORAC_HIGH_HI)
    nrow, n6 = int(FK.ORAC_ROWS), int(FK.ORAC_6X_ROWS)
    #   STATE 1: six distinct lowband TFs carry an x-cross inside 2 rows, and those 2 rows sit inside
    #   the 3. A cross counts ONCE per TF per window - his 1115 ruling.
    six = window(R['x'], n6)[:, 1:lo_hi + 1].sum(1) >= int(FK.ORAC_6X_HITS)
    s1 = six.copy()
    for d in range(1, nrow - n6 + 1):            # 6x may end on the row or up to (3 - 2) rows earlier
        s1[d:] |= six[:-d]
    #   STATE 2: >=5 lowband AW(any) anywhere in the 3 rows, and 0 lowband TO(exf) ON THE FINAL ROW
    low_aw = window(R['aw'], nrow)[:, 1:lo_hi + 1].sum(1)
    low_toexf = R['toexf'][:, 1:lo_hi + 1].sum(1)
    s2 = (low_aw >= int(FK.ORAC_LOW_AW)) & (low_toexf == 0)
    #   STATE 3: the conditional highband output
    high_aw = window(R['aw'], nrow)[:, hi_lo:hi_hi + 1].sum(1)
    high_toexf = R['toexf'][:, hi_lo:hi_hi + 1].sum(1)
    high_xe = window(R['cross'], nrow)[:, hi_lo:hi_hi + 1].sum(1)
    #   condition1 `toexf-gate`: the two sum columns added together, strictly above the knob
    gsum = R['sumtoexf'].sum(1)
    if gate_window == 'row':
        c1 = gsum > int(FK.ORAC_TOEXF_GATE)
    else:
        hit = (gsum > int(FK.ORAC_TOEXF_GATE))
        c = np.concatenate(([0], np.cumsum(hit.astype(np.int64))))
        orow = np.searchsorted(PRT, np.where(reads['topen'] >= 0, reads['topen'], 0), side='left')
        c1 = (c[np.arange(NROWS) + 1] - c[np.minimum(orow, np.arange(NROWS))]) > 0
    c2 = reads['nmage'] > int(FK.ORAC_MAGE_OOB)
    c3 = ~reads['r1oob']
    anyc = c1 | c2 | c3
    s3 = np.where(anyc, high_aw >= int(FK.ORAC_HIGH_AW),
                  (high_toexf == 0) & (high_xe >= int(FK.ORAC_HIGH_XE)))
    #   HIS GENERAL NOTE reads the other way too: *"'printing TOexf' means 'any of the cells in the
    #   current row, between ws1 and ws15, that are printing TO(exf)'"* - the WHOLE range, where his
    #   state 2 says "lowband is printing ... 0 TOexf". Both readings are carried so the difference
    #   is a number he can look at, not a choice I made for him.
    all_toexf = R['toexf'][:, 1:hi_hi + 1].sum(1)
    s2w = (low_aw >= int(FK.ORAC_LOW_AW)) & (all_toexf == 0)
    return dict(s1=s1, s2=s2, s2w=s2w, s3=s3, six=six, low_aw=low_aw, low_toexf=low_toexf,
                all_toexf=all_toexf, high_aw=high_aw, high_toexf=high_toexf, high_xe=high_xe,
                c1=c1, c2=c2, c3=c3, anyc=anyc, gsum=gsum,
                fires=s1 & s2 & s3, fires_w=s1 & s2w & s3)


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


def ltf_xcross(R):
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
    #   HIS 1115 RULING on *">=4 fields prints `AW(*)`"*: *"4 distinct TFs reading AW(*) anywhere in
    #   the 3 rows"*. So it counts timeframes, not cells, and there is no second reading here.
    g3a = window(R['aw'], LTFX_N15_ROWS)[:, 1:16].sum(1) >= LTFX_AW_PRINTS
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


def ltf_5aw_6x(R, xrows=None):
    """HIS 1115 ltf-5aw-6x. -> bool per row, True on the row the scenario qualifies on.

    HIS #3 holds: every window ENDS on the qualifying row. The outer window is his
    fdm3-ltf-xcross-nof15-rows, 3 rows; the x-cross hit window is `xrows` rows and sits inside it.

    HIS 1116 BANK: *"bank docs/fdm3/out/ltf_5aw_6x_0920_0923_A_ws1_ws6.txt as a confirmed
    aw-exhaust scenario"*. That file counts DISTINCT TIMEFRAMES reading AW(*) and was read with the
    oracle's A ws1-ws6 button on, so both are the bank and neither is an option here any more.

    `xrows` defaults to his own fdm3-ltf-5aw-6x-xcross-rows, 1.
    """
    rows = int(FK.LTF_XCROSS_NOF15_ROWS)
    xrows = int(FK.LTF_5AW_6X_XCROSS_ROWS) if xrows is None else int(xrows)
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
    g4 = window(R['aw'], rows)[:, 1:16].sum(1) >= AW6X_AW_PRINTS
    g5 = count(R['newaw'], rows) >= AW6X_AW_FLIPS
    return g1 & g2 & g3 & g4 & g5


def dump(R, SD, a, z, path, alo=0, ahi=0):
    """Write every ltf-5aw-6x instance in rows a..z to `path`, in HIS 1115 columns.

    `alo` / `ahi` are the oracle's two A buttons, his 1115 *"the first button shows A for ws1-ws6,
    and the second shows A for ws7-ws15"*: with one on, every r line in that band takes its lift-off
    reads - natural and e-cross - off the window extreme on every bar of the span, which moves that
    line's AW and the scenario-2 test of the lines above it. It cannot move an x or e cross.
    """
    rows = int(FK.LTF_XCROSS_NOF15_ROWS)
    m = ltf_5aw_6x(R)
    nof = nof15(R['cross'], NOF_ROWS)    # HIS Nof15 event, his own 2 row definition
    hit = [i for i in range(a, z + 1) if m[i]]
    with open(path, 'w') as f:
        f.write('# his ltf-5aw-6x, every instance from %s to %s\n' % (U(a), U(z)))
        f.write('# read off fdm3-oracle\'s rows, %d bars on the tape, the oracle fence %g/%g,\n'
                '# the pivots as found, A %s %s and A %s %s\n'
                % (ln.N, META['fence'], 100 - META['fence'],
                   META['abands'][0], 'ON' if alo else 'off',
                   META['abands'][1], 'ON' if ahi else 'off'))
        if alo or ahi:
            f.write('# A ON means every r line in that band takes its lift-off reads - natural and\n'
                    '# e-cross - off the window extreme on every bar of the span, which moves that\n'
                    '# line\'s AW and the scenario-2 test of the lines above it. It cannot move an x\n'
                    '# or an e cross, so the x-cross and e-cross columns are the same as with A off.\n')
        f.write('# %s\n' % control(R))
        f.write('#\n# the knobs this run read:\n')
        for k, v in FK.live():
            f.write('#   %-26s %s\n' % (k, v))
        f.write('#\n# the columns:\n'
                '#   the window                 its FIRST row - the window is %d rows long\n'
                '#   its last row               the row the scenario qualifies on\n'
                '#   the incoming pseudo trade  the trade live on these rows, the one that closes next\n'
                '#   Nof15 peak inside it       the highest 2 row Nof15 event inside the window\n'
                '#   new AW prints              TO -> AW flip cells over the window, ws1..ws15\n'
                '#   x-cross TFs                distinct timeframes with an x-cross, ws1..ws15\n'
                '#   e-cross TFs                distinct timeframes with an e-cross, ws1..ws15\n'
                '#   AW(*) TFs                  distinct timeframes reading AW(inf) or AW(exf)\n'
                '#\n%s# %d instances\n\n'
                % (rows,
                   '# BANKED by Joe 1116 as a confirmed aw-exhaust scenario\n'
                   if alo == int(FK.A_WS1_WS6)
                   and ahi == int(FK.A_WS7_WS15) and FK.RULED_OK else '',
                   len(hit)))
        hd = ['the window', 'its last row', 'the incoming pseudo trade', 'Nof15 peak inside it',
              'new AW prints', 'x-cross TFs', 'e-cross TFs', 'AW(*) TFs']
        wd = [19, 12, 25, 20, 13, 11, 11, 9]
        f.write(' | '.join(h.ljust(w) for h, w in zip(hd, wd)).rstrip() + '\n')
        f.write('-+-'.join('-' * w for w in wd) + '\n')
        for i in hit:
            w = slice(i - rows + 1, i + 1)
            vals = [U(i - rows + 1), U(i)[11:19], direction(SD, i - rows + 1, i + 1),
                    str(int(nof[w].max())), str(int(R['newaw'][w, 1:16].sum())),
                    str(int(R['x'][w, 1:16].any(0).sum())), str(int(R['e'][w, 1:16].any(0).sum())),
                    str(int(R['aw'][w, 1:16].any(0).sum()))]
            f.write(' | '.join(v.ljust(x) for v, x in zip(vals, wd)).rstrip() + '\n')
    print('wrote %d instances to %s' % (len(hit), path))


def find(R, SD, a, z):
    """HIS 1115 DISCOVERY over rows a..z. Prints the windows carrying his reference signature, then the
    counts under each relaxation he named - *"reducing the required print counts by a small amount, or
    increasing the row counts by a small amount"*.

    A WINDOW IS NAMED BY ITS FIRST ROW here, because his own words name his by its first row - *"the
    09-24 2248 to 2250 window"*. Overlapping starts are grouped into one cluster, since the same
    stretch qualifying three times running is one pattern, not three.
    """
    nof = nof15(R['cross'], NOF_ROWS)    # HIS Nof15 event, his own 2 row definition
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
    checks it after, so a changed row layout cannot pass silently.

    IT HOLDS IN EVERY A STATE. fdm3_oracle.build() makes the x and e cross bits outside its state
    loop, from the lift-off race alone, so no A button and no pivot flip can move them; the A list
    goes to towards_away.run, which makes the TO/AW codes and so the AW(*) and TO -> AW flip bits.
    """
    #   HIS TWO ROWS ARE TWO MINUTES, 00:27:00 up to 00:29:00. On the 60 s page that is rows 0027
    #   and 0028; on the 30 s page it is four rows covering the same wall clock. Taking it as a span
    #   rather than a row count is what lets the same control check either page.
    a, z = K_OF('2026-09-23 00:27:00'), K_OF('2026-09-23 00:29:00')
    tfs = [t for t in range(1, 16) if R['cross'][a:z, t].any()]
    assert len(tfs) == 14 and 15 not in tfs, tfs
    return ('CONTROL ok: his 09-23 00:27:00 .. 00:29:00 reads 14of15 over %d rows of %d s, '
            'ws15 the only one missing' % (z - a, STEP // 1000))


def main():
    if MODE == 'orac-exhaust':
        #   HIS 1118: report the orac-exhaust events on the day he names, on the 30 second oracle
        day = sys.argv[2]
        assert int(META['step']) == int(FK.ORAC_EXHAUST_ROW_S) * 1000, \
            ('orac-exhaust reads his 30 second oracle', META['step'])
        a, z = K_OF(day + ' 00:00:00'), K_OF(day + ' 23:59:59')
        z = min(z, NROWS - 1)
        R, SD = load()
        print(control(R))
        TR = TA.pseudo_trades()[1]
        reads = orac_reads(TR)
        walk = orac_walk(R, reads)
        V = {w: orac_exhaust(R, reads, w) for w in ('row', 'trade')}
        print('bars %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
        print('page port %d, %d rows %d s apart, %s .. %s'
              % (PORT, NROWS, int(META['step']) // 1000, U(0), U(NROWS - 1)))
        print('%s: rows %d .. %d (%s .. %s), pseudo trades on the tape %d'
              % (day, a, z, U(a), U(z), len(TR)))
        print('knobs (banked): ' + ' '.join('%s=%s' % (k, v) for k, v in FK.live()
                                            if k.startswith('ORAC')))
        print()
        print('| the reading | rows in %s |' % day)
        print('|' + '---|' * 2)
        for lab, m in (('6x: %d of ws1..ws%d carry an x-cross inside %d rows'
                        % (int(FK.ORAC_6X_HITS), int(FK.ORAC_LOW_HI), int(FK.ORAC_6X_ROWS)),
                        V['row']['six']),
                       ('state 1: that 6x sits inside the %d rows ending here'
                        % int(FK.ORAC_ROWS), V['row']['s1']),
                       ('state 2: >=%d lowband AW(any) in the %d rows AND 0 lowband TO(exf) here'
                        % (int(FK.ORAC_LOW_AW), int(FK.ORAC_ROWS)), V['row']['s2']),
                       ('state 1 + state 2', V['row']['s1'] & V['row']['s2']),
                       ('state 3, toexf-gate read on the final row', V['row']['s3']),
                       ('state 3, toexf-gate read across the trade', V['trade']['s3']),
                       ('orac-exhaust, toexf-gate on the final row', V['row']['fires']),
                       ('orac-exhaust, toexf-gate across the trade', V['trade']['fires']),
                       ('the ws1r walk gate is open', walk),
                       ('orac-exhaust (final row) AND the walk gate open',
                        V['row']['fires'] & walk),
                       ('orac-exhaust if "0 TOexf" in state 2 means ws1..ws15, not ws1..ws%d'
                        % int(FK.ORAC_LOW_HI), V['row']['fires_w'])):
            print('| %s | %d |' % (lab, int(m[a:z + 1].sum())))
        print()
        #   every row that gets past his first two states, so a row that dies later shows WHERE
        k = np.flatnonzero((V['row']['s1'] & V['row']['s2'])[a:z + 1]) + a
        print('| the row | trade opened | side | 6x here | lowband AW in 3 | lowband TO(exf) here '
              '| highband AW in 3 | highband TO(exf) here | highband x/e in 3 | toexf-gate sum here '
              '| cond1 row | cond1 trade | cond2 Mages oob | cond3 no ws1r oob | highband branch '
              '| state 3 row | state 3 trade | walk gate | ORAC-EXHAUST |')
        print('|' + '---|' * 19)
        for i in k:
            vr, vt = V['row'], V['trade']
            print('| %s | %s | %s | %s | %d | %d | %d | %d | %d | %d | %s | %s | %d | %s | %s | %s '
                  '| %s | %s | %s |'
                  % (U(int(i)), U(int(np.searchsorted(PRT, reads['topen'][i], 'left'))),
                     'HIGH' if reads['side'][i] > 0 else 'LOW' if reads['side'][i] < 0 else '-',
                     'yes' if vr['six'][i] else 'earlier row',
                     vr['low_aw'][i], vr['low_toexf'][i], vr['high_aw'][i], vr['high_toexf'][i],
                     vr['high_xe'][i], vr['gsum'][i],
                     'yes' if vr['c1'][i] else 'no', 'yes' if vt['c1'][i] else 'no',
                     reads['nmage'][i], 'yes' if vr['c3'][i] else 'no',
                     '>=%d AW' % int(FK.ORAC_HIGH_AW) if vr['anyc'][i] else '0 TO(exf) + x/e',
                     'PASS' if vr['s3'][i] else 'fail', 'PASS' if vt['s3'][i] else 'fail',
                     'open' if walk[i] else 'shut',
                     'FIRES' if vr['fires'][i] else '-'))
        if not len(k):
            print('| no row in %s passes state 1 and state 2 | | | | | | | | | | | | | | | | | | |'
                  % day)
        #   every row of every firing event's 3 row window, so the counts above can be read off the
        #   rows themselves rather than taken on trust
        nrow = int(FK.ORAC_ROWS)
        lo_hi, hi_lo = int(FK.ORAC_LOW_HI), int(FK.ORAC_LOW_HI) + 1
        hi_hi = int(FK.ORAC_HIGH_HI)
        tfs = lambda m, a_, b_: ','.join('ws%d' % t for t in range(a_, b_ + 1) if m[t]) or '-'
        for i in np.flatnonzero(V['row']['fires'][a:z + 1]) + a:
            print()
            print('| orac-exhaust %s | lowband x-cross | lowband AW(any) | lowband TO(exf) '
                  '| highband AW(any) | highband TO(exf) | highband x or e | ws16-22 TO(exf) '
                  '| ws23-30 TO(exf) |' % U(int(i)))
            print('|' + '---|' * 9)
            for j in range(i - nrow + 1, i + 1):
                print('| %s | %s | %s | %s | %s | %s | %s | %d | %d |'
                      % (U(int(j)), tfs(R['x'][j], 1, lo_hi), tfs(R['aw'][j], 1, lo_hi),
                         tfs(R['toexf'][j], 1, lo_hi), tfs(R['aw'][j], hi_lo, hi_hi),
                         tfs(R['toexf'][j], hi_lo, hi_hi), tfs(R['cross'][j], hi_lo, hi_hi),
                         R['sumtoexf'][j, 0], R['sumtoexf'][j, 1]))
        return
    if len(sys.argv) >= 4 and sys.argv[1] == 'aw6x':
        #   HIS 1116: the A state is fdm3-wide infrastructure, banked at A ws1-ws6 ON. The two
        #   buttons are knobs like any other, so fdm3_knobs.check() is what refuses an off-bank run -
        #   there is no second refusal here and no way to ask for a state from the command line.
        alo = int(FK.A_WS1_WS6)
        ahi = int(FK.A_WS7_WS15)
        R, _SD = load(alo=alo, ahi=ahi)
        print(control(R))
        a, z = K_OF(sys.argv[2]), K_OF(sys.argv[3])
        print('tape bars: %d. the oracle fence is %g/%g.' % (ln.N, META['fence'], 100 - META['fence']))
        print('| the reading | fires between %s and %s |' % (sys.argv[2], sys.argv[3]))
        print('|---|---|')
        m = ltf_5aw_6x(R)
        print('| A %s %s, A %s %s, AW(*) as distinct timeframes%s | %d |'
              % (META['abands'][0], 'on' if alo else 'off',
                 META['abands'][1], 'on' if ahi else 'off',
                 '' if FK.RULED_OK else ' - NOT THE BANK, an experiment',
                 int(m[a:z + 1].sum())))
        if len(sys.argv) >= 5:
            dump(R, _SD, a, z, sys.argv[4], alo, ahi)
        return
    if len(sys.argv) >= 4 and sys.argv[1] == 'find':
        R, SD = load()
        print(control(R))
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
        c = nof15(x, NOF_ROWS)
        f4 = nof15(x, AWS_ROWS)
        nf = window((aw[:, 1:AWS_MAXTF + 1].sum(1) >= AWS_FLIPS)[:, None], AWS_ROWS)[:, 0]
        print()
        print('| %s | rows | per day |' % lab)
        print('|---|---|---|')
        print('| rows with no target-side, so no cross can print | %d | %.1f |'
              % (int((sd == 0).sum()), (sd == 0).sum() / days))
        for n in (13, 14, 15):
            m = c >= n
            print('| %dof15 in a %d row window | %d | %.1f |' % (n, NOF_ROWS, int(m.sum()), m.sum() / days))
        print('| %d+ AW flips on one row within ws1..ws%d | %d | %.1f |'
              % (AWS_FLIPS, AWS_MAXTF, int(nf.sum()), nf.sum() / days))
        print('| %dof15 in a %d row window | %d | %.1f |'
              % (AWS_NOF15, AWS_ROWS, int((f4 >= AWS_NOF15).sum()), (f4 >= AWS_NOF15).sum() / days))
        a4 = nf & (f4 >= AWS_NOF15)
        print('| 4-ltf-aws - both gates inside the %d row window | %d | %.1f |'
              % (AWS_ROWS, int(a4.sum()), a4.sum() / days))
        print('| 4-ltf-aws + ws1b oob or gcws30b ex-%.0f/%.0f | %d | %.1f |'
              % (G30_FNC, 100 - G30_FNC, int((a4 & exc).sum()), (a4 & exc).sum() / days))
        m = ltf_xcross(R)
        print('| LTF-xcross | %d | %.1f |' % (int(m.sum()), m.sum() / days))
    if len(sys.argv) >= 2 and sys.argv[1] == 'mage50':
        #   HIS 1118: the Mage's side of 50 on the ws1..ws15 cells, with the line read off the tape
        #   at every row's print bar as the check on it
        m50, MNR = mage50()
        print('page port %d, %d rows, %s .. %s, paint %d%%'
              % (PORT, NROWS, U(0), U(NROWS - 1), int(META['mage50'])))
        print()
        print('| the line | over 50.00 | under 50.00 | neither | rows |')
        print('|' + '---|' * 5)
        for _j, tf in WS:
            c = m50[:, tf]
            print('| ws%d | %d | %d | %d | %d |'
                  % (tf, int((c == 1).sum()), int((c == 2).sum()), int((c == 0).sum()), NROWS))
        print()
        print('| the line | rows judged | rows the paint disagrees with the emerging Mage |')
        print('|' + '---|' * 3)
        _chk = mage50_check(m50)
        for lab, n, nbad, _off in _chk:
            print('| %s | %d | %d |' % (lab, n, nbad))
        for lab, _n, _nb, off in _chk:
            for k in off:
                print('| %s | %s | DISAGREES |' % (U(int(k)), lab))
        return
    if len(sys.argv) >= 3:
        R, sd = load(fnc=MOM_FNC)
        x, aw = R['cross'], R['newaw']
        c, f4 = nof15(x, NOF_ROWS), nof15(x, AWS_ROWS)
        lx = ltf_xcross(R)
        xh = window(R['x'], LTFX_ROWS)[:, 1:LTFX_MAXTF + 1].sum(1)
        awc = count(R['aw'], LTFX_N15_ROWS)
        nac = count(R['newaw'], LTFX_N15_ROWS)
        a, z = K_OF(sys.argv[1]), K_OF(sys.argv[2])
        print()
        print('| the row | its target-side | the TFs that crossed | %d row Nof15 | %d row Nof15 '
              '| AW flips ws1..ws%d | x-hits ws1..ws%d over %d rows | AW(*) cells over %d rows '
              '| new AW cells over %d rows | LTF-xcross | ws1b | gcws30b |'
              % (NOF_ROWS, AWS_ROWS, AWS_MAXTF, LTFX_MAXTF, LTFX_ROWS, LTFX_N15_ROWS, LTFX_N15_ROWS))
        print('|' + '---|' * 12)
        for k in range(a, z + 1):
            tfs = [str(tf) for tf in range(1, 16) if x[k, tf]]
            fl = [str(tf) for tf in range(1, AWS_MAXTF + 1) if aw[k, tf]]
            print('| %s | %+d | %d: %s | %d | %d | %d: %s | %d | %d | %d | %s | %.2f | %.2f |'
                  % (U(k), sd[k], len(tfs), ','.join(tfs), c[k], f4[k], len(fl),
                     ','.join(fl) or '-', xh[k], awc[k], nac[k], 'FIRES' if lx[k] else '-',
                     W1B[PRT[k]], G30B[PRT[k]]))


if __name__ == '__main__':
    main()
