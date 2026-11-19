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
import re
import sys
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))   # docs/fdm3 - where the out files live
sys.path.insert(0, HERE)
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
    import v4_sweep_pivots as SP      # HIS 1118: *"use sweep-pivot's MAE/MFE"*
    import v4_backstop_trades as BT   # the price series towards_away's own pivots are built on
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
#   every orac- mode reads his 30 second page; the rest read the 60 second one he banked
PORT = int(FK.ORAC_EXHAUST_PORT) if MODE in ('orac-exhaust', 'setups') else int(FK.ORACLE_PORT)
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
#   THE PAGE SAYS WHERE ITS BLOCKS ARE when it publishes them; the derivation is the fall-back for a
#   page built before it did. Deriving an offset is how this reader came to hold TWO answers for
#   O_TA, the stale one last - every TO/AW, cross and TO(exf) read came out of the wrong bytes and
#   nothing complained.
O_TA = int(META.get('ta', _RP))     # the TO/AW code per line: 0 none, 1 TO, 2 AW, 3 TO(exf), 4 AW(exf)
O_CROSS = int(META.get('xc', O_TA + len(LINES) + 2 * len(SUMS)))
O_TOEXF = int(META.get('toexf', O_CROSS + len(LINES)))   # per sum, how many of ITS lines read TO(exf)
#   how many lines each sum column holds, off its own label - "ws16-22" is 7 lines. Its TO(exf)
#   count can never exceed that, which is what the byte check below leans on.
SUM_N = [int(m.group(2)) - int(m.group(1)) + 1 if m else len(LINES)
         for m in (re.match(r'ws(\d+)-(\d+)$', x) for x in SUMS)]
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
         ('its Mage-side-of-50 paint', META.get('mage50'), int(FK.ORACLE_MAGE50_PCT)),
         ('its x race re-open', META.get('xreopen'), FK.ORACLE_X_REOPEN),
         ('its e race re-open', META.get('ereopen'), FK.ORACLE_E_REOPEN)]
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
        #   EVERY BLOCK IS CHECKED AGAINST THE VALUES IT CAN HOLD. A TO/AW code is 0..4, a cross
        #   code 0..15, a sum's TO(exf) count 0 .. the lines in that sum. Reading one block at
        #   another's offset lands outside its range almost at once, which is what was missing when
        #   O_TA was stale.
        _ta = b[:, O_TA:O_TA + len(LINES)].astype(int)
        assert _ta.min() >= 0 and _ta.max() <= 4, \
            ('the TO/AW block is not at byte %d on this page' % O_TA, int(_ta.min()), int(_ta.max()))
        _xc = b[:, O_CROSS:O_CROSS + len(LINES)].astype(int)
        assert _xc.min() >= 0 and _xc.max() <= 15, \
            ('the cross block is not at byte %d on this page' % O_CROSS, int(_xc.min()), int(_xc.max()))
        for k, _lab in enumerate(SUMS):
            _c = b[:, O_TOEXF + k].astype(int)
            assert _c.min() >= 0 and _c.max() <= SUM_N[k], \
                ('the %s TO(exf) count is not at byte %d' % (_lab, O_TOEXF + k), int(_c.max()))
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


def orac_exhaust(R):
    """HIS 1118 DENOMINATOR SPEC, verbatim: *"1) six x-crosses printing in 2 rows in lowband
    (refered to as `6x`) / ***the next 2 must qualify within 3 rows, and those 3 rows encompass
    6x*** / 2) lowband is printing (>=5 AW(any) OR >=2 AW flips) and 0 TOexf / 3) highband must
    print 0 TOexf and >=1 x/e cross"*.

    His 1118 answers still hold: the page is the 30 second oracle, and *"the zero TOexf condtion
    belongs to the final row, the other conditions are placed anywhere in the three rows"*.
    An AW flip is the TO -> AW flip, his *"new AW"*.
    THE CONDITIONAL HIGHBAND IS NOT IN THIS SPEC - he replaced it to find the denominator. Its
    three conditions live in orac_conditions below and nothing here reads them.
    """
    lo_hi, hi_lo, hi_hi = int(FK.ORAC_LOW_HI), int(FK.ORAC_LOW_HI) + 1, int(FK.ORAC_HIGH_HI)
    nrow, n6 = int(FK.ORAC_ROWS), int(FK.ORAC_6X_ROWS)
    #   STATE 1: six distinct lowband TFs carry an x-cross inside 2 rows, and those 2 rows sit
    #   inside the 3. A cross counts ONCE per TF per window - his 1115 ruling.
    six = window(R['x'], n6)[:, 1:lo_hi + 1].sum(1) >= int(FK.ORAC_6X_HITS)
    s1 = six.copy()
    for d in range(1, nrow - n6 + 1):            # 6x may end on the row or up to (3 - 2) rows earlier
        s1[d:] |= six[:-d]
    #   STATE 2: across the 3 rows, >=5 lowband AW(any) OR >=2 lowband AW flips; and 0 lowband
    #   TO(exf) ON THE FINAL ROW
    low_aw = window(R['aw'], nrow)[:, 1:lo_hi + 1].sum(1)
    low_fl = window(R['newaw'], nrow)[:, 1:lo_hi + 1].sum(1)
    low_toexf = R['toexf'][:, 1:lo_hi + 1].sum(1)
    s2 = ((low_aw >= int(FK.ORAC_LOW_AW)) | (low_fl >= int(FK.ORAC_LOW_FLIPS))) & (low_toexf == 0)
    #   STATE 3, HIS 1118 REWRITE: *"IF >=6 AWs print in lowband at the 3rd row / -highband has 5
    #   minutes (walk forward) grace to produce >=2 AW flips and a maximum of 1 TOexf"*.
    #   CAUSAL: a grace that walks FORWARD cannot be answered at the 3rd row, so the event fires at
    #   the bar inside the grace where highband completes, not at the 3rd row. s3 is True on THAT
    #   row and gate_row says which 3rd row opened it.
    #   HIS 1118 CORRECTED MECH: *"IF >=4 AWs print in lowband at the 3rd row"*. His 6 became 4
    #   after he settled the counting - *"AW, TO, x, e prints are all per distinct TF"* - so the
    #   count is DISTINCT ws1..ws7 reading AW(any), and his 00:08:30 reaches exactly 4 of them on
    #   its 3rd row. The gate reads THE 3rd ROW ALONE, which is what his spec text says; the 3 row
    #   count sits beside it in the report so the difference is a number he can look at.
    #   His earlier *"Read the 3 rows instead ... and 00:08:30 comes back"* was aimed at recovering
    #   that row, and dropping the gate to 4 recovers it on the 3rd row alone.
    #   MINE, stated to him and still open: the grace is the 3rd row and the rows after it up to 5
    #   minutes, the 3rd row included; the flips are distinct ws8..ws15 counted from the 3rd row to
    #   the bar being tested; the TO(exf) ceiling is read on that bar. A 3rd row whose gate fails
    #   produces nothing - his spec has no ELSE.
    high_toexf = R['toexf'][:, hi_lo:hi_hi + 1].sum(1)
    low_aw3 = R['aw'][:, 1:lo_hi + 1].sum(1)
    gate = low_aw3 >= int(FK.ORAC_LOW_AW_3RD)
    grace = int(round(float(FK.ORAC_GRACE_MIN) * 60000 / STEP))   # rows in his 5 minutes
    assert grace * STEP == int(round(float(FK.ORAC_GRACE_MIN) * 60000)), \
        ('%g minutes is not a whole number of %d s rows' % (float(FK.ORAC_GRACE_MIN), STEP // 1000))
    hf = R['newaw'][:, hi_lo:hi_hi + 1]
    s3 = np.zeros(NROWS, bool)
    gate_row = np.full(NROWS, -1, np.int64)
    ok_toexf = high_toexf <= int(FK.ORAC_HIGH_TOEXF_MAX)
    for g in np.flatnonzero(gate & s1 & s2):
        seen = np.zeros(hi_hi + 1 - hi_lo, bool)
        for j in range(g, min(g + grace, NROWS)):
            seen |= hf[j]
            if seen.sum() >= int(FK.ORAC_HIGH_FLIPS) and ok_toexf[j]:
                s3[j] = True
                if gate_row[j] < 0:
                    gate_row[j] = g
                break
    assert (gate_row[s3] >= 0).all() and (gate_row[s3] <= np.flatnonzero(s3)).all(), \
        'an orac-exhaust fired before the 3rd row that opened it'
    #   HIS GENERAL NOTE reads the other way too: *"'printing TOexf' means 'any of the cells in the
    #   current row, between ws1 and ws15, that are printing TO(exf)'"* - the WHOLE range, where his
    #   states say lowband and highband. Carried beside it so the difference is a number.
    all_toexf = R['toexf'][:, 1:hi_hi + 1].sum(1)
    #   THE EVENT IS STATE 3's OWN ROW. States 1 and 2 were read at the 3rd row that opened the
    #   grace - s3 is only set for a 3rd row where both passed - so the fire is s3 alone.
    return dict(s1=s1, s2=s2, s3=s3, six=six, low_aw=low_aw, low_fl=low_fl, low_toexf=low_toexf,
                all_toexf=all_toexf, high_toexf=high_toexf, low_aw3=low_aw3, gate=gate,
                gate_row=gate_row, grace=grace, fires=s3)


def max_oob_line(reads, suffix='Mage'):
    """HIS 1118: *"the maximum oob Mage at any decision defines the max(ws1 to 15) that needs to
    'weigh in' on the decision"*, and *"there might be a difference for `b` instead of `mage`"* -
    so `suffix` picks which line of ws{TF} is read, 'Mage' or 'b'. -> (step, top) per row.

      step  HIS RULING: *"I've only measured in single steps: ws1 to 2, 2 to 3, 3 to 4. let's stick
            with that logic to find the max"*, then his 1118 follow-up after seeing ws2Mage miss the
            fence by 1.08 at 09:20 and strand ws3..ws15 behind it: *"jumps of 2 should be allowed to
            make it more sane"*. Start at the LOWEST ws1..ws15 whose line is oob and climb while the
            next one OR the one after it is oob; the max is the top of that run. A gap of 2 or more
            timeframes stops it.
      top   the highest oob line anywhere in ws1..ws15, gap or no gap - what this returned before
            his ruling, kept beside it so the difference is a number.

    CLOSED-PREV, the banked read for every line but lift-off's, and the read the M-no-rev column's
    own oob test uses. PLAIN OOB: no lift-off reversal condition, which is what M-no-rev adds.
    """
    oobf = float(K.FDM_FNC_OOB) if hasattr(K, 'FDM_FNC_OOB') else 15.0
    side = reads['side']
    hi = int(FK.ORAC_HIGH_HI)
    OOBM = np.zeros((NROWS, hi + 1), bool)
    for tf in range(1, hi + 1):
        m = closed(ln.line('ws%d%s' % (tf, suffix)), tf * 60)[PRT]
        with np.errstate(invalid='ignore'):
            OOBM[:, tf] = np.where(side > 0, m >= 100 - oobf,
                                   np.where(side < 0, m <= oobf, False))
    top = np.zeros(NROWS, np.int16)
    for tf in range(1, hi + 1):
        top = np.where(OOBM[:, tf], tf, top).astype(np.int16)
    #   the unbroken run from the lowest oob line up
    step = np.zeros(NROWS, np.int16)
    lo = np.zeros(NROWS, np.int16)
    for tf in range(hi, 0, -1):
        lo = np.where(OOBM[:, tf], tf, lo).astype(np.int16)   # the LOWEST oob line
    run = lo.copy()
    jump = int(FK.ORAC_OOB_JUMP)
    for tf in range(2, hi + 1):
        #   tf extends the run when it is oob and the run's top is within `jump` of it - his 1118
        #   *"jumps of 2 should be allowed"*, so one missing timeframe is stepped over, two are not
        run = np.where(OOBM[:, tf] & (run > 0) & (tf - run <= jump), tf, run).astype(np.int16)
    step = np.where(lo > 0, run, 0).astype(np.int16)
    assert (step[step > 0] >= lo[step > 0]).all() and (step <= top).all(), \
        'the single-step run is not inside the lines that are oob'
    return step, top


def setup_maemfe(bars, side):
    """HIS 1118: *"then we can use sweep-pivot's MAE/MFE to find what works and what doesn't"*.
    -> [(leg close bar or None, mae %, mfe %)] per bar in `bars`.

    THE SETUP IS THE INCOMING TRADE, THE ONE BEING CLOSED. What is scored is the OUTGOING trade,
    the one being opened. HIS 1118, in his own words:

        " LOW target-side creates a *OUTGOING* LONG,..."

    so a LOW target-side scores a LONG - up is favourable - and a HIGH target-side scores an
    OUTGOING SHORT, down favourable. THE FAVOURABLE DIRECTION IS THE OPPOSITE OF THE ROW'S
    TARGET-SIDE. It is not derived from price: it is his ruling, and the row's side is the input.
    v4_sweep_pivots.swing takes the side of the CROSS that opened the leg and its own fav is
    -side, so it is handed the target-side as-is and the two agree.

    THE SPAN IS MECHANISM-DEFINED, no horizon and no percentage: the setup's own bar to the bar
    v4_sweep_pivots closes its leg on, the same read l2_barrage uses for a cadence event.
    """
    close = BT.prices()[0]
    out = []
    for b, sd in zip(bars, side):
        if not sd:
            out.append((None, None, None))
            continue
        sw = SP.swing(int(b), int(sd), close)   # its fav is -side, and -target_side is his outgoing
        if not sw or sw.get('close') is None:
            out.append((None, None, None))
            continue
        z = int(sw['close'])
        a2, b2 = min(int(b), z), max(int(b), z)
        seg = np.asarray(close[a2:b2 + 1], float)
        p0 = float(close[int(b)])
        if not np.isfinite(seg).any() or not np.isfinite(p0) or p0 == 0:
            out.append((z, None, None))
            continue
        up = (float(np.nanmax(seg)) - p0) / p0 * 100.0
        dn = (float(np.nanmin(seg)) - p0) / p0 * 100.0
        #   LOW target-side -> OUTGOING LONG -> up favourable; HIGH -> OUTGOING SHORT -> down
        mfe, mae = (up, dn) if int(sd) < 0 else (-dn, -up)
        assert mfe >= 0 >= mae, ('the favourable side is the wrong way round', b, sd, mfe, mae)
        out.append((z, mae, mfe))
    return out


def orac_setups(R, reads, rows):
    """HIS 1118 SETUP HUNT: *"6x or 7x (low band) / with at least 1 aw flip / across 2 or 3 rows /
    with any AW flips in the post 6x/8x grace walk, seperated to high and low bands"*, plus *"thr
    number of x crosses in the high band might have meaning"*. `rows` is his 2 or 3.

    -> a dict of per-row arrays. The setup row is the row its window ENDS on, so nothing later than
    the row is read for the setup itself; the grace walk forward is reported apart from it.
    """
    lo_hi, hi_lo = int(FK.ORAC_LOW_HI), int(FK.ORAC_LOW_HI) + 1
    hi_hi = int(FK.ORAC_HIGH_HI)
    xl = window(R['x'], rows)[:, 1:lo_hi + 1].sum(1)        # distinct lowband TFs with an x-cross
    fl = window(R['newaw'], rows)[:, 1:lo_hi + 1].sum(1)    # distinct lowband AW flips
    hx = window(R['x'], rows)[:, hi_lo:hi_hi + 1].sum(1)    # his highband x-cross count
    setup = (xl >= int(FK.ORAC_6X_HITS)) & (fl >= 1)
    grace = int(round(float(FK.ORAC_GRACE_MIN) * 60000 / STEP))
    #   the grace walk: the setup row and the rows after it up to his 5 minutes, the setup row
    #   included - the same span his state 3 grace uses
    glo = np.zeros(NROWS, np.int16)
    ghi = np.zeros(NROWS, np.int16)
    gx = np.zeros(NROWS, np.int16)
    for g in np.flatnonzero(setup):
        z = min(g + grace, NROWS)
        glo[g] = int(R['newaw'][g:z, 1:lo_hi + 1].any(0).sum())
        ghi[g] = int(R['newaw'][g:z, hi_lo:hi_hi + 1].any(0).sum())
        gx[g] = int(R['x'][g:z, hi_lo:hi_hi + 1].any(0).sum())
    return dict(setup=setup, xl=xl, fl=fl, hx=hx, glo=glo, ghi=ghi, gx=gx, grace=grace, rows=rows)


def orac_conditions(R, reads, gate_window):
    """HIS 1118 CONDITIONAL HIGHBAND - *"3) the conditional highband output"* with its condition1,
    condition2 and condition3. OUT OF THE CURRENT SPEC: he replaced states 2 and 3 to find the
    denominator first, so nothing fires off this. Kept whole, with his values, for when he builds
    out from the denominator. `gate_window` is his condition1 span, which he never ruled: 'row'
    reads the final row alone, 'trade' any row of the trade up to and including it.
    """
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
    return dict(c1=c1, c2=c2, c3=c3, anyc=c1 | c2 | c3, gsum=gsum)


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


def fixed_table(head, rows):
    """HIS 1118 *"is there a way to make that txt file more Joe friendly? perhaps fixed width will
    sort it out"*. -> the lines of one table whose columns all line up, read in a plain editor.

    Every cell is padded to its column's widest entry, so column n starts at the same character on
    every row. The pipes stay, so it is still a markdown table if he pastes it somewhere that cares.
    """
    cols = [list(map(str, head))] + [list(map(str, r)) for r in rows]
    w = [max(len(c[i]) for c in cols) for i in range(len(head))]
    line = lambda c: '| ' + ' | '.join(x.ljust(w[i]) for i, x in enumerate(c)) + ' |'
    return [line(cols[0]), '|' + '|'.join('-' * (n + 2) for n in w) + '|'] + [line(c) for c in cols[1:]]


def orac_file(day, a, z, R, reads, walk, V, path):
    """HIS 1118: every row of `day` that opens one of his three states, one record per row, then
    every orac-exhaust event's grace traced bar by bar. Fixed width, his 1118 ask."""
    lo_hi, hi_lo = int(FK.ORAC_LOW_HI), int(FK.ORAC_LOW_HI) + 1
    hi_hi, nrow = int(FK.ORAC_HIGH_HI), int(FK.ORAC_ROWS)
    k = np.flatnonzero(V['s2'][a:z + 1]) + a
    tfs = lambda m, a_, b_: ','.join('ws%d' % t for t in range(a_, b_ + 1) if m[t]) or '-'
    sdof = lambda i: ('HIGH' if reads['side'][i] > 0 else 'LOW' if reads['side'][i] < 0 else '-')
    with open(path, 'w') as f:
        w = lambda t: f.write(t + '\n')
        for t in fixed_table(['x'], [['y']])[:0]:
            pass
        w('# orac-exhaust on %s - HIS 1118 SPEC' % day)
        w('#')
        w('# HIS SPEC, verbatim:')
        w('#   1) six x-crosses printing in 2 rows in lowband (refered to as `6x`)')
        w('#   ***the next 2 must qualify within 3 rows, and those 3 rows encompass 6x***')
        w('#   2) lowband is printing (>=5 AW(any) OR >=2 AW flips) and 0 TOexf')
        w('#   3)')
        w('#   IF >=6 AWs print in lowband at the 3rd row')
        w('#   -highband has 5 minutes (walk forward) grace to produce >=2 AW flips and a maximum')
        w('#    of 1 TOexf')
        w('#')
        w('# HIS 1118 ANSWERS, still in force: the page is the 30 second oracle; *"the zero TOexf')
        w('# condtion belongs to the final row, the other conditions are placed anywhere in the')
        w('# three rows"*; lowband is ws1-ws%d, highband is ws%d-ws%d.' % (lo_hi, hi_lo, hi_hi))
        w('# An AW flip is the TO -> AW flip, his *"new AW"*. A cross counts once per TF per window.')
        w('#')
        w('# CAUSAL. His state 3 walks FORWARD, so it cannot be answered at the 3rd row. The event')
        w('# fires at the bar inside the grace where highband completes, and that bar is the')
        w('# event\'s timestamp. States 1, 2 and the gate were read at the 3rd row, so the event')
        w('# row need not pass them itself.')
        w('#')
        w('# MINE, open until he rules: the gate counts AW(any) on the 3rd row ALONE; the grace is')
        w('# the 3rd row and the rows after it up to %g minutes, the 3rd row included (%d rows of'
          % (float(FK.ORAC_GRACE_MIN), V['grace']))
        w('# %d s); the AW flips are distinct ws%d..ws%d counted from the 3rd row to the bar being'
          % (STEP // 1000, hi_lo, hi_hi))
        w('# tested; the TO(exf) ceiling is read ON that bar. A 3rd row whose gate fails produces')
        w('# nothing - his spec has no ELSE.')
        w('#')
        w('# the page: port %d, %d rows %d s apart, %s .. %s'
          % (PORT, NROWS, STEP // 1000, U(0), U(NROWS - 1)))
        w('# the tape: %d bars, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
        w('# the knobs (banked): ' + ' '.join('%s=%s' % (kk, vv) for kk, vv in FK.live()
                                              if kk.startswith('ORAC_')))
        w('')
        w('## 1. EVERY ROW OF %s THAT PASSES STATE 2' % day)
        w('#')
        w('#   the row                 the oracle row, its own open time. HH:MM:SS at his 1118')
        w('#                          *"for this report format only"* - the day is %s' % day)
        w('#   side                    that trade\'s target-side')
        w('#   6x                      where the 6x landed: this row / the row before / no')
        w('#   lowAW/%d                 distinct ws1..ws%d reading AW(any) across the %d rows - state'
          % (nrow, lo_hi, nrow))
        w('#                           2 wants >=%d' % int(FK.ORAC_LOW_AW))
        w('#   lowFLIP/%d               distinct ws1..ws%d that flipped TO -> AW across the %d rows -'
          % (nrow, lo_hi, nrow))
        w('#                           the other side of his OR, wants >=%d' % int(FK.ORAC_LOW_FLIPS))
        w('#   lowTOexf                ws1..ws%d reading TO(exf) ON THIS ROW - 0 on every row here' % lo_hi)
        w('#   ws1-15TOexf             the same count over ws1..ws%d, his general note\'s range' % hi_hi)
        w('#   lowAW here              distinct ws1..ws%d reading AW(any) ON THIS ROW - THE STATE 3'
          % lo_hi)
        w('#                           GATE, which wants >=%d' % int(FK.ORAC_LOW_AW_3RD))
        w('#   highTOexf               ws%d..ws%d reading TO(exf) ON THIS ROW' % (hi_lo, hi_hi))
        w('#   state 1 / state 2       PASS or fail')
        w('#   gate                    >=%d of "lowAW here": PASS opens a %g minute grace'
          % (int(FK.ORAC_LOW_AW_3RD), float(FK.ORAC_GRACE_MIN)))
        w('#   MAE %% / MFE %%          this row\'s bar to the bar sweep-pivots closes its leg on,')
        w('#                          scoring the OUTGOING trade: a LOW target-side creates an')
        w('#                          OUTGOING LONG so up is favourable, a HIGH one an OUTGOING')
        w('#                          SHORT so down is. MAE never above 0, MFE never below it')
        w('#   the 57                  yes where state 1, state 2 and the gate all pass - the rows')
        w('#                          a %g minute grace opens on' % float(FK.ORAC_GRACE_MIN))
        w('#   x in %d rows             distinct ws1..ws%d carrying an x-cross across the %d rows'
          % (nrow, hi_hi, nrow))
        w('#   fired at                the bar that grace completed on, or - when it never did')
        w('#   the leg closes          the bar v4_sweep_pivots closes the leg on')
        w('')
        FIRED = {}
        for i in np.flatnonzero(V['s3'][a:z + 1]) + a:
            FIRED.setdefault(int(V['gate_row'][i]), U(int(i)))
        #   HIS 1118: *"add a column that flags these 57 rows"* - the rows that pass states 1 and 2
        #   AND the gate, which is where one of his graces opens. It is the AND of the three
        #   columns beside it, in one place so the 57 can be grepped.
        OPENS = V['s1'] & V['s2'] & V['gate']
        #   HIS 1118: *"drop any rows that do not print a 6x event, unless they are one of the
        #   57"*. "print" is the row's own 6x - V['six'] - so a row whose 6x landed on the row
        #   before is dropped unless it is one of the 57.
        k = np.asarray([i for i in k if V['six'][i] or OPENS[i]], np.int64)
        #   HIS 1118: *"for this report format only, show timestamps as hh:mm:ss"*
        HM = lambda ms_i: U(int(ms_i))[11:]
        HMB = lambda b: ln.U(int(b))[11:]
        #   distinct ws1..ws%d carrying an x-cross across the %d rows - his *"how many distinct x
        #   were printed inside of the 3 rows"*, the whole range since he named no band
        XIN3 = window(R['x'], nrow)[:, 1:hi_hi + 1].sum(1)
        #   HIS 1118 MAE/MFE here too: this file had none at all. The same read as the setup hunt -
        #   the row's own bar to the bar sweep-pivots closes its leg on, scoring the OUTGOING trade
        MM = {int(i): mm for i, mm in zip(k, setup_maemfe(PRT[k], reads['side'][k]))}
        rows = []
        for i in k:
            six = ('this row' if V['six'][i] else
                   'the row before' if (i > 0 and V['six'][i - 1]) else 'no')
            _zc, _mae, _mfe = MM[int(i)]
            #   HIS 1118: the flag sits *"next to the timestamp"*, so it is column 2.
            #   DROPPED at his word: `trade opened` duplicated the oracle's own pivot flips, and
            #   `ws1r walk`. `the leg closes` stays - it is a v4_sweep_pivots leg on whichever line
            #   marks the bar (ws10Mage, ws30Mage and others on this day), not the ws2Mage pivots
            #   the oracle flips on, so it is not a duplicate.
            rows.append([HM(i), 'yes' if OPENS[i] else '-', sdof(i),
                         '-' if _mae is None else '%+.3f' % _mae,
                         '-' if _mfe is None else '%+.3f' % _mfe,
                         FIRED.get(int(i), '-')[11:] if OPENS[i] and int(i) in FIRED else '-',
                         six, XIN3[i], V['low_aw'][i], V['low_fl'][i], V['low_toexf'][i],
                         V['all_toexf'][i], V['low_aw3'][i], V['high_toexf'][i],
                         'PASS' if V['s1'][i] else 'fail', 'PASS' if V['s2'][i] else 'fail',
                         'PASS' if V['gate'][i] else 'fail',
                         HMB(_zc) if _zc is not None else '-'])
        for t in fixed_table(['the row', 'the 57', 'side', 'MAE %', 'MFE %', 'fired at',
                              '6x', 'x in %d rows' % nrow, 'lowAW/%d' % nrow, 'lowFLIP/%d' % nrow,
                              'lowTOexf', 'ws1-15TOexf', 'lowAW here', 'highTOexf',
                              'state 1', 'state 2', 'gate', 'the leg closes'],
                             rows):
            w(t)
        w('')
        w('## 2. THE COUNTS')
        w('')
        cnt = [('rows in %s' % day, np.ones(NROWS, bool)),
               ('6x: %d of ws1..ws%d carry an x-cross inside %d rows'
                % (int(FK.ORAC_6X_HITS), lo_hi, int(FK.ORAC_6X_ROWS)), V['six']),
               ('state 1', V['s1']), ('state 2', V['s2']),
               ('state 1 + state 2', V['s1'] & V['s2']),
               ('the state 3 gate: >=%d lowband AW(any) on the 3rd row'
                % int(FK.ORAC_LOW_AW_3RD), V['gate']),
               ('the same gate read across the %d rows instead' % int(FK.ORAC_ROWS),
                V['low_aw'] >= int(FK.ORAC_LOW_AW_3RD)),
               ('states 1 + 2 AND the gate - a %g minute grace opens here'
                % float(FK.ORAC_GRACE_MIN), V['s1'] & V['s2'] & V['gate']),
               ('ORAC-EXHAUST', V['fires']),
               ('orac-exhaust with his ws1r walk running', V['fires'] & walk)]
        for t in fixed_table(['the count', 'rows'],
                             [[lab, int(m[a:z + 1].sum())] for lab, m in cnt]):
            w(t)
        w('')
        w('## 3. EVERY GRACE, AND WHAT HIGHBAND DID INSIDE IT')
        w('')
        hf = R['newaw'][:, hi_lo:hi_hi + 1]
        gr = []
        for g in np.flatnonzero((V['s1'] & V['s2'] & V['gate'])[a:z + 1]) + a:
            seen = np.zeros(hi_hi - lo_hi, bool)
            best, fired, when = 0, '-', '-'
            for j in range(g, min(g + V['grace'], NROWS)):
                seen |= hf[j]
                best = max(best, int(seen.sum()))
                if V['s3'][j] and V['gate_row'][j] == g:
                    fired, when = 'FIRES', U(int(j))
                    break
            gr.append([HM(g), sdof(g), V['low_aw'][g], V['low_aw3'][g], best,
                       V['high_toexf'][g], when[11:] if when != '-' else '-', fired])
        for t in fixed_table(['the 3rd row', 'side', 'lowAW/%d' % nrow, 'lowAW here',
                              'most highband flips reached', 'highTOexf at the 3rd row',
                              'fired at', ''], gr):
            w(t)
        w('')
        w('## 4. EACH ORAC-EXHAUST, ITS GRACE BAR BY BAR')
        for g in sorted(FIRED):
            w('')
            rows = []
            for j in range(g, min(g + V['grace'], NROWS)):
                rows.append([HM(j), tfs(R['newaw'][j], hi_lo, hi_hi), V['high_toexf'][j],
                             'FIRES' if (V['s3'][j] and V['gate_row'][j] == g) else '-'])
                if V['s3'][j] and V['gate_row'][j] == g:
                    break
            for t in fixed_table(['grace opened %s' % HM(g), 'highband AW flip', 'highTOexf', ''],
                                 rows):
                w(t)
        w('')
        w('## 5. THE THREE ROWS OF EACH 3rd ROW THAT OPENED A GRACE')
        for g in np.flatnonzero((V['s1'] & V['s2'] & V['gate'])[a:z + 1]) + a:
            w('')
            rows = []
            for j in range(g - nrow + 1, g + 1):
                rows.append([HM(j), tfs(R['x'][j], 1, lo_hi), tfs(R['aw'][j], 1, lo_hi),
                             tfs(R['newaw'][j], 1, lo_hi), tfs(R['toexf'][j], 1, lo_hi),
                             tfs(R['aw'][j], hi_lo, hi_hi), tfs(R['toexf'][j], hi_lo, hi_hi),
                             tfs(R['cross'][j], hi_lo, hi_hi)])
            for t in fixed_table(['3rd row %s' % HM(g), 'lowband x-cross', 'lowband AW(any)',
                                  'lowband AW flip', 'lowband TO(exf)', 'highband AW(any)',
                                  'highband TO(exf)', 'highband x or e'], rows):
                w(t)
    return len(k)


def main():
    if MODE == 'line':
        #   HIS 1118: *"drop the the ws6x emerging values, sampled at 15s gaps, between 0255 snd
        #   0320, into a txt file"*. A line read straight off the tape, EMERGING - the value at the
        #   bar itself, no closed-prev step. The gap is his, in seconds, on the 5 s bar grid.
        name, t0s, t1s, gap = sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
        assert gap % 5 == 0, ('a %d s gap is not a whole number of 5 s bars' % gap)
        v = np.asarray(ln.line(name), float)
        k0, k1 = ln.K(t0s), ln.K(t1s)
        assert k0 <= k1, (t0s, t1s)
        bars = list(range(k0, k1 + 1, gap // 5))
        out = sys.argv[6] if os.path.isabs(sys.argv[6]) else os.path.join(HERE, sys.argv[6])
        with open(out, 'w') as f:
            w = lambda t: f.write(t + '\n')
            w('# %s, EMERGING, every %d s from %s to %s' % (name, gap, t0s, t1s))
            w('#')
            w('# EMERGING means the value at that bar itself - no closed-prev step, so this is what')
            w('# the line reads live on that bar rather than what a closed %s bar would show.' % name)
            w('# the tape is 5 s bars, so a %d s gap is every %d bars. Both ends are included.'
              % (gap, gap // 5))
            w('# the tape: %d bars, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
            w('#')
            w('# THE COLUMNS')
            w('#   the bar     the 5 s bar, its own time (UTC)')
            w('#   %-11s the emerging value there, 4 dp. "-" where the line has no value yet' % name)
            w('')
            w('| the bar | %s |' % name)
            w('|---|---|')
            for b in bars:
                w('| %s | %s |' % (ln.U(b), '-' if not np.isfinite(v[b]) else '%.4f' % v[b]))
            fin = np.asarray([v[b] for b in bars], float)
            fin = fin[np.isfinite(fin)]
            w('')
            w('| the count | value |')
            w('|---|---|')
            w('| samples | %d |' % len(bars))
            w('| with a value | %d |' % len(fin))
            w('| lowest | %s |' % ('-' if not len(fin) else '%.4f' % fin.min()))
            w('| highest | %s |' % ('-' if not len(fin) else '%.4f' % fin.max()))
        print('bars %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
        print('file: %s, %d samples of %s every %d s, %s .. %s'
              % (out, len(bars), name, gap, t0s, t1s))
        return
    if MODE == 'setups':
        #   HIS 1118: find his setups, tag each with the max oob Mage TF, and show whether that
        #   number separates the 00:08 kind from the 03:05 kind
        day = sys.argv[2]
        assert int(META['step']) == int(FK.ORAC_EXHAUST_ROW_S) * 1000, \
            ('this reads his 30 second oracle', META['step'])
        a, z = K_OF(day + ' 00:00:00'), min(K_OF(day + ' 23:59:59'), NROWS - 1)
        R, SD = load()
        print(control(R))
        TR = TA.pseudo_trades()[1]
        reads = orac_reads(TR)
        TAG = {sfx: max_oob_line(reads, sfx) for sfx in ('Mage', 'b')}
        step, top = TAG['Mage']
        MNR = mage50()[1][0][0] if 'mnrtops' in META else np.zeros(NROWS, np.int16)
        print('bars %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
        print('page port %d, %d rows %d s apart' % (PORT, NROWS, int(META['step']) // 1000))
        print('%s: rows %d .. %d (%s .. %s)' % (day, a, z, U(a), U(z)))
        out = (sys.argv[3] if len(sys.argv) >= 4 else None)
        if out and not os.path.isabs(out):
            out = os.path.join(HERE, out)
        lo_hi, hi_lo = int(FK.ORAC_LOW_HI), int(FK.ORAC_LOW_HI) + 1
        hi_hi = int(FK.ORAC_HIGH_HI)
        buf = []
        wr = buf.append
        for rows in (2, 3):
            S = orac_setups(R, reads, rows)
            k = np.flatnonzero(S['setup'][a:z + 1]) + a
            wr('')
            wr('## SETUPS ACROSS %d ROWS - >=%d of ws1..ws%d carry an x-cross AND >=1 lowband AW flip'
               % (rows, int(FK.ORAC_6X_HITS), int(FK.ORAC_LOW_HI)))
            wr('')
            MM = setup_maemfe(PRT[k], reads['side'][k])
            MAE = [m for _z, m, _f in MM if m is not None]
            MFE = [f for _z, _m, f in MM if f is not None]
            #   HIS 1118: *"I can't see the maefe in the txt file"* - it was column 13 of 14 at
            #   character 220 of a 241 character line, off the right edge. His 0815 rule is that a
            #   report is read top to bottom with no second page bolted on, so MAE and MFE come
            #   FIRST and every header is short enough to keep the line on one screen. The legend
            #   above the table says what each short name holds.
            wr('#   the setup row          the setup row, its own open time (UTC)')
            wr('#   side                   the pseudo trade\'s target-side there')
            wr('#   MAE %% / MFE %%          the setup bar to the bar sweep-pivots closes its leg on,')
            wr('#                          scoring the OUTGOING trade: a LOW target-side creates an')
            wr('#                          OUTGOING LONG so up is favourable, a HIGH one an OUTGOING')
            wr('#                          SHORT so down is. MAE never above 0, MFE never below it')
            wr('#   max oob Mage           the oob climb on ws{TF}Mage, - when no line is oob')
            wr('#   max oob b              the same climb on ws{TF}b')
            wr('#   M-no-rev               the M-no-rev column\'s TF at that row')
            wr('#   lowband x-cross        distinct ws1..ws%d with an x-cross across the %d rows'
               % (lo_hi, rows))
            wr('#   lowband AW flip        distinct ws1..ws%d flipping TO -> AW across the %d rows'
               % (lo_hi, rows))
            wr('#   highband x-cross       distinct ws%d..ws%d with an x-cross across the %d rows'
               % (hi_lo, hi_hi, rows))
            wr('#   grace lowband AW flips distinct ws1..ws%d flipping TO -> AW in the %g minute grace'
               % (lo_hi, float(FK.ORAC_GRACE_MIN)))
            wr('#   grace highband AW flips distinct ws%d..ws%d flipping TO -> AW in that grace'
               % (hi_lo, hi_hi))
            wr('#   grace highband x-cross distinct ws%d..ws%d with an x-cross in that grace'
               % (hi_lo, hi_hi))
            wr('#   the leg closes         the bar v4_sweep_pivots closes the leg on')
            wr('')
            tab = []
            for i, (zc, mae, mfe) in zip(k, MM):
                tab.append([U(int(i)),
                            'HIGH' if reads['side'][i] > 0 else 'LOW' if reads['side'][i] < 0 else '-',
                            '-' if mae is None else '%+.3f' % mae,
                            '-' if mfe is None else '%+.3f' % mfe,
                            'ws%d' % TAG['Mage'][0][i] if TAG['Mage'][0][i] else '-',
                            'ws%d' % TAG['b'][0][i] if TAG['b'][0][i] else '-',
                            'ws%d' % MNR[i] if MNR[i] else '-',
                            S['xl'][i], S['fl'][i], S['hx'][i],
                            S['glo'][i], S['ghi'][i], S['gx'][i],
                            ln.U(int(zc)) if zc is not None else '-'])
            #   HIS 1118: *"please use the prior txt format"* - the long names are back. The
            #   short ones were codes I coined, which he cannot read. MAE and MFE stay at the
            #   front, which was the other half of his ask.
            for t in fixed_table(['the setup row', 'side', 'MAE %', 'MFE %', 'max oob Mage',
                                  'max oob b', 'M-no-rev', 'lowband x-cross', 'lowband AW flip',
                                  'highband x-cross', 'grace lowband AW flips',
                                  'grace highband AW flips', 'grace highband x-crosses',
                                  'the leg closes'], tab):
                wr(t)
            #   HIS 1027 STANDING RULE: per-row MAE/MFE always carries its aggregate under it
            wr('')
            wr('## THE MAE/MFE SUMMARY - the setup bar to the bar sweep-pivots closes its leg on')
            wr('')
            _med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
            agg = [['setups scored', '%d of %d' % (len(MAE), len(k))]]
            if MAE:
                agg += [['sum MAE %', '%+.3f' % sum(MAE)], ['sum MFE %', '%+.3f' % sum(MFE)],
                        ['mean MAE %', '%+.3f' % (sum(MAE) / len(MAE))],
                        ['mean MFE %', '%+.3f' % (sum(MFE) / len(MFE))],
                        ['median MAE %', '%+.3f' % _med(MAE)],
                        ['median MFE %', '%+.3f' % _med(MFE)],
                        ['worst MAE %', '%+.3f' % min(MAE)],
                        ['best MFE %', '%+.3f' % max(MFE)],
                        ['MFE > abs(MAE)', '%d of %d'
                         % (sum(1 for m, f in zip(MAE, MFE) if f > abs(m)), len(MAE))]]
            for t in fixed_table(['the read', 'value'], agg):
                wr(t)
            MAP = {int(i): (m, f) for i, (_z, m, f) in zip(k, MM)}
            for sfx in ('Mage', 'b'):
                wr('')
                wr('## THE SAME SETUPS GROUPED BY THEIR MAX OOB %s' % sfx.upper())
                wr('')
                tag = TAG[sfx][0]
                grp = []
                for t_ in range(0, int(FK.ORAC_HIGH_HI) + 1):
                    sel = k[tag[k] == t_]
                    if not len(sel):
                        continue
                    mm = [MAP[int(x)] for x in sel if MAP[int(x)][0] is not None]
                    grp.append(['ws%d' % t_ if t_ else 'none oob', len(sel), len(mm),
                                '-' if not mm else '%+.3f' % (sum(m for m, _ in mm) / len(mm)),
                                '-' if not mm else '%+.3f' % (sum(f for _, f in mm) / len(mm)),
                                '-' if not mm else '%d' % sum(1 for m, f in mm if f > abs(m)),
                                '%.1f' % S['glo'][sel].mean(), '%.1f' % S['ghi'][sel].mean(),
                                '%.1f' % S['hx'][sel].mean(), '%.1f' % S['gx'][sel].mean(),
                                int((S['ghi'][sel] >= 2).sum())])
                wr('#   setups          how many setups carry this tag')
                wr('#   scored          how many of them sweep-pivots could close a leg for')
                wr('#   MFE > abs(MAE)  how many of the scored have MFE above abs(MAE)')
                wr('#   the means are per setup, over the same columns as the row table above')
                wr('')
                for t in fixed_table(['max oob %s' % sfx, 'setups', 'scored', 'mean MAE %',
                                      'mean MFE %', 'MFE > abs(MAE)', 'mean grace lowband AW flips',
                                      'mean grace highband AW flips', 'mean highband x-cross',
                                      'mean grace highband x-crosses',
                                      'setups reaching >=2 grace highband flips'], grp):
                    wr(t)
        for t in buf:
            print(t)
        if out:
            with open(out, 'w') as f:
                f.write('# HIS 1118 SETUP HUNT on %s\n#\n' % day)
                f.write('# HIS WORDS: *"6x or 7x (low band) / with at least 1 aw flip / across 2 or\n')
                f.write('# 3 rows / with any AW flips in the post 6x/8x grace walk, seperated to high\n')
                f.write('# and low bands"*, and *"thr number of x crosses in the high band might have\n')
                f.write('# meaning"*.\n#\n')
                f.write('# max oob Mage / max oob b: HIS *"the maximum oob Mage at any decision defines the\n')
                f.write('# max(ws1 to 15) that needs to weigh in on the decision"* - the highest\n')
                f.write('# ws1..ws%d whose CLOSED-PREV Mage is oob %g/%g on the row\'s own target-side\n'
                        % (int(FK.ORAC_HIGH_HI), float(OOB), 100 - float(OOB)))
                f.write('# at that row. PLAIN OOB, no lift-off reversal condition - that is what the\n')
                f.write('# M-no-rev column beside it adds, so the two can be compared.\n')
                f.write('# BOTH LINES: his *"there might be a difference for `b` instead of `mage`"*, so the\n')
                f.write('# same climb runs on ws{TF}Mage and on ws{TF}b and each gets its own tag and its\n')
                f.write('# own grouping.\n')
                f.write('# MAE/MFE: his *"use sweep-pivot\'s MAE/MFE"*. The span is the setup bar to the bar\n')
                f.write('# v4_sweep_pivots closes its leg on - mechanism-defined, no horizon and no percentage.\n')
                f.write('# THE SETUP IS THE INCOMING TRADE, the one being closed. What is scored is the\n')
                f.write('# OUTGOING trade, the one being opened. HIS 1118, verbatim:\n')
                f.write('#     " LOW target-side creates a *OUTGOING* LONG,..."\n')
                f.write('# so a LOW target-side scores a LONG (up favourable) and a HIGH target-side scores an\n')
                f.write('# OUTGOING SHORT (down favourable). MAE is never above 0 and MFE never below it.\n')
                f.write('# THE CLIMB: start at the LOWEST ws1..ws%d that is oob and step up one timeframe at\n'
                        % int(FK.ORAC_HIGH_HI))
                f.write('# a time while the next is oob too - his *"I\'ve only measured in single steps: ws1\n')
                f.write('# to 2, 2 to 3, 3 to 4"*. A gap stops the climb. "highest oob anywhere" ignores gaps.\n#\n')
                f.write('# the grace walk is the setup row and the rows after it up to %g minutes,\n'
                        % float(FK.ORAC_GRACE_MIN))
                f.write('# the setup row included. Every count is DISTINCT TFs - his *"AW, TO, x, e\n')
                f.write('# prints are all per distinct TF"*.\n#\n')
                f.write('# the page: port %d, %d rows %d s apart\n' % (PORT, NROWS, STEP // 1000))
                f.write('# the tape: %d bars, %s .. %s\n' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
                f.write('\n'.join(buf) + '\n')
            print('file: %s' % out)
        return
    if MODE == 'orac-exhaust':
        #   HIS 1118: *"let's find the denominator and build out from there"* - his three states,
        #   with the conditional highband out, reported on the day he names
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
        V = orac_exhaust(R)
        print('bars %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
        print('page port %d, %d rows %d s apart, %s .. %s'
              % (PORT, NROWS, int(META['step']) // 1000, U(0), U(NROWS - 1)))
        print('%s: rows %d .. %d (%s .. %s), pseudo trades on the tape %d'
              % (day, a, z, U(a), U(z), len(TR)))
        print('knobs (banked): ' + ' '.join('%s=%s' % (k, v) for k, v in FK.live()
                                            if k.startswith('ORAC_')))
        if len(sys.argv) >= 4:
            #   THIS MODULE CHDIRS TO THE TAPE'S DIRECTORY at import, so a relative path would land
            #   beside the oracle rather than with the other fdm3 out files. It is resolved here.
            out = sys.argv[3] if os.path.isabs(sys.argv[3]) else os.path.join(HERE, sys.argv[3])
            n = orac_file(day, a, z, R, reads, walk, V, out)
            print('file: %s, %d state 2 rows' % (out, n))
        print()
        print('| the reading | rows in %s |' % day)
        print('|' + '---|' * 2)
        for lab, m in (('rows in the day', np.ones(NROWS, bool)),
                       ('6x: %d of ws1..ws%d carry an x-cross inside %d rows'
                        % (int(FK.ORAC_6X_HITS), int(FK.ORAC_LOW_HI), int(FK.ORAC_6X_ROWS)),
                        V['six']),
                       ('state 1: that 6x sits inside the %d rows ending here'
                        % int(FK.ORAC_ROWS), V['s1']),
                       ('state 2: (>=%d lowband AW(any) OR >=%d lowband AW flips) in the %d rows, '
                        'AND 0 lowband TO(exf) here'
                        % (int(FK.ORAC_LOW_AW), int(FK.ORAC_LOW_FLIPS), int(FK.ORAC_ROWS)),
                        V['s2']),
                       ('state 2, the >=%d AW(any) side alone' % int(FK.ORAC_LOW_AW),
                        (V['low_aw'] >= int(FK.ORAC_LOW_AW)) & (V['low_toexf'] == 0)),
                       ('state 2, the >=%d AW flips side alone' % int(FK.ORAC_LOW_FLIPS),
                        (V['low_fl'] >= int(FK.ORAC_LOW_FLIPS)) & (V['low_toexf'] == 0)),
                       ('state 1 + state 2', V['s1'] & V['s2']),
                       ('the state 3 gate: >=%d lowband AW(any) on the 3rd row'
                        % int(FK.ORAC_LOW_AW_3RD), V['gate']),
                       ('the same gate read across the %d rows instead' % int(FK.ORAC_ROWS),
                        V['low_aw'] >= int(FK.ORAC_LOW_AW_3RD)),
                       ('states 1 + 2 AND the gate - a %g minute grace opens here'
                        % float(FK.ORAC_GRACE_MIN), V['s1'] & V['s2'] & V['gate']),
                       ('state 3: highband made >=%d AW flips with <=%d TO(exf) inside the grace'
                        % (int(FK.ORAC_HIGH_FLIPS), int(FK.ORAC_HIGH_TOEXF_MAX)), V['s3']),
                       ('ORAC-EXHAUST', V['fires']),
                       ('his ws1r walk is running', walk),
                       ('orac-exhaust with that ws1r walk running', V['fires'] & walk)):
            print('| %s | %d |' % (lab, int(m[a:z + 1].sum())))
        return
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
