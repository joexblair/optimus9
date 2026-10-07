"""The 39 octo-sig of 09-25: mtd route -> branch D -> swing_detect MAE/MFE. Joe 1005.

Joe: "you can decide if the status is correct based on swing_detect + MAE/MFE. your choice on the
swing size - measure for effect. let's say that any signal which creates >0.7 MAE% (or maybe 0.8%
- your call) should be blocked".

THE SCORING CONVENTION is the banked one, not a new one. docs/linelab_spec.md s0, "Locked by Joe:
swing_detect 1%, swing-to-pivot, no stops":
  entry   = the octo-sig bar, px = __pxs__ at that bar
  side    = the dr-bias trade. dr +1 = SHORT, dr -1 = LONG
  segment = entry -> the next FAVOURABLE pivot (SHORT: the next 'L'; LONG: the next 'H')
  MFE     = max favourable excursion over the segment, %
  MAE     = max adverse excursion over the segment, % -- max(0, ...), so a clean favourable-side
            entry scores 0. A pre-entry adverse move belongs to a different leg.
  no stop. Identical arithmetic to score_shorts.score and siglab.Lab.score.

MY TWO CHOICES, both delegated by Joe this turn, both measured below not preferred:
  swing pct      swept 0.4 .. 2.0
  MAE% threshold 0.7 vs 0.8
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import datetime as dt, io, os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.line_config import override, mech_lines
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.compute.swing_detect import find_pivots
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import anchor_floater, AF_BLOCK
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e
# TAPE END, exclusive. Override with LG_TAPE_END=YYYY-MM-DD when the window needs a later tape:
# a day AFTER this date is NOT in the cache, and K() would searchsorted past the end of ts and
# index the last bar instead of failing. 2026-10-04 covers 09-25..10-03. For 10-04 use 2026-10-05
# (build it first: build_tape.py 2026-10-05).
EM = int(dt.datetime.strptime(_os.environ.get('LG_TAPE_END', '2026-10-04'), '%Y-%m-%d')
        .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
# HI, LO, REV_WOB, GAP_MAX, G5EXTREMA_LOOKBACK_BARS and TOL are read from `lazy_g_config`
# below, once `db` exists. Joe 1006: *"anything that's currently hardcoded in lazy-g and
# octo-freedom can go into their respective config tables now"*.
_G5EX_DOC = """Joe 1006: *"mod the knob label - add `g5extrema`"*. Renamed from `LOOKBACK_BARS`, which sat one
word away from `rev_lookback` (the ws1mage-rev mask in the walk) at the SAME 48 bars / 240 s while
doing an unrelated job. Same naming hazard Joe caught earlier today in `rev_lookback_mask`, which
does not read `rev` at all.

THIS KNOB HAS EXACTLY ONE JOB, used once at :76 - how far back mtd step 1 searches for the g5Mage
oob extrema. It never touches the arm, the coil, the qualify, the race, the TOL windows or branch D.
"""
db = DatabaseManager(**get_db_config()); db.connect()
from optimus9.compute.spec_config import spec_config
LG = spec_config(db, 'lazy_g_config')
LG_KEY = LG.key()                                   # 'lazy_g_config.v1' - goes in the knob key
HI, LO = float(LG['oob_hi']), float(LG['oob_lo'])
REV_WOB, GAP_MAX = int(LG['rev_wob']), int(LG['gap_max'])
G5EXTREMA_LOOKBACK_BARS = int(LG['g5extrema_lookback_bars'])
TOL = {n: int(LG['tol_' + n]) for n in ('g5', 'g15', 'g30', 'ws1')}
spec = {}
for g in mech_lines(db, 'wsf'):
    if g['role'] not in spec: _t, s_, m_ = g['override']; spec[g['role']] = (s_, m_)
sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
db.disconnect()
tp = np.load(os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP, {'src': sy['s'], 'len': sy['l']}) + '.npz'))
ts = tp['__ts__']; PX = np.asarray(tp['__pxs__'], float)
LD = lambda tfs, role: np.asarray(np.load(os.path.join(LINE_DIR, _line_key(EM, HOURS, WARMUP, override(tfs, *spec[role])) + '.npy'), mmap_mode='r'), float)
MTD = {'g5': LD(5, 'Mage'), 'g15': LD(15, 'Mage'), 'g30': LD(30, 'Mage'), 'ws1': LD(60, 'Mage')}
TF = list(range(int(LG['band_lo']), int(LG['band_hi']) + 1))
Rl = {t: LD(t * 60, 'r') for t in TF}
Mg = {t: (MTD['ws1'] if t == 1 else LD(t * 60, 'Mage')) for t in TF}
M13 = LD(13 * 60, 'm'); G1 = MTD['ws1']
DRv = np.zeros(len(ts), np.int8); cur = 0
for k in range(min(len(ts), len(G1), len(M13))):
    a, b = G1[k], M13[k]
    if a == a and b == b:
        if a >= 85.0 and b >= 85.0: cur = +1
        elif a <= 15.0 and b <= 15.0: cur = -1
    DRv[k] = cur
REV = _mage_rev(MTD['g5'], REV_WOB)
TAPE_LAST = len(ts) - 1
U = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
K = lambda s: int(np.searchsorted(ts, int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))

# ---------------- mtd, verbatim from mtd_lens.py
def mtd(k):
    d = int(DRv[k])
    if d == 0: return {'route': 'no dr', 'src': '-', 'ex': None, 'd': 0}
    same = (lambda v: v >= HI) if d > 0 else (lambda v: v <= LO)
    a = max(0, k - G5EXTREMA_LOOKBACK_BARS)
    hits = [i for i in range(a, k + 1) if np.isfinite(MTD['g5'][i]) and same(MTD['g5'][i])]
    if hits:
        ex = max(hits, key=lambda i: MTD['g5'][i]) if d > 0 else min(hits, key=lambda i: MTD['g5'][i])
        src = 'lookback'
    else:
        j = k
        while j < TAPE_LAST and not (np.isfinite(MTD['g5'][j]) and same(MTD['g5'][j])): j += 1
        if not (np.isfinite(MTD['g5'][j]) and same(MTD['g5'][j])):
            return {'route': 'NO-FIND oob', 'src': 'fwd', 'ex': None, 'd': d}
        want = -1 if d > 0 else +1
        nxt = [i for i in range(j, TAPE_LAST + 1) if REV[i] == want]
        if not nxt: return {'route': 'NO-FIND rev', 'src': 'fwd', 'ex': None, 'd': d}
        ex = nxt[0]; src = 'fwd'
    base = ex
    v, vbar = {}, {}
    for n in ('g5', 'g15', 'g30', 'ws1'):
        w = TOL[n]
        if w == 0:
            v[n], vbar[n] = MTD[n][base], base; continue
        lo_, hi_ = max(0, base - w), min(TAPE_LAST, base + w)
        seg = MTD[n][lo_:hi_ + 1]
        if not np.isfinite(seg).any(): v[n], vbar[n] = np.nan, base; continue
        j = int(np.nanargmax(seg)) if d > 0 else int(np.nanargmin(seg))
        v[n], vbar[n] = float(seg[j]), lo_ + j
    r1 = all(np.isfinite(v[n]) and same(v[n]) for n in v)
    noob = sum(1 for n in ('g5','g15','g30','ws1') if np.isfinite(v[n]) and same(v[n]))
    miss = [n for n in ('g5','g15','g30','ws1') if not (np.isfinite(v[n]) and same(v[n]))]
    net = v['ws1'] - v['g15']
    towards = (net > 0) if d > 0 else (net < 0)
    route = 'mtd.r1' if r1 else ('mtd.r2' if towards else 'neither')
    allow = ('LONG' if d > 0 else 'SHORT') if route == 'mtd.r2' else '-'
    # `vbar` added 1005 for octosig_neither_why: the BAR each line's tolerance-window extremum was
    # taken from. Nothing else reads it, so the report's output is unchanged - verified.
    return {'route': route, 'src': src, 'ex': ex, 'd': d, 'v': v, 'vbar': vbar, 'net': net,
            'noob': noob, 'miss': miss, 'towards': towards, 'allow': allow,
            'lag': (ts[ex] - ts[k]) / 60000.0}

# ---------------- branch D, verbatim from branchD.py
CLAIM_HOP = int(LG['claim_hop'])
"""THE CLAIM ADJACENCY BOUND. Joe 1005: *"this can't be claimed by lines that are so far away from
the action (action = ws2r is stronger than ws3r)"* and *"if the ws4r or ws5r were printing r
ex-fence, that would qualify band claimed. skipping 1 or 2 TFs in a baton handoff is not unusual"*.
Block top ws2 -> ws4 is +2 and ws5 is +3, so his examples reach +3. His ruling, 1005: *"A at +3
makes sense based your findings"*.

A claimer must now sit within +3 TFs of the top of `keep`. The in-band test is unchanged.

WHY NOT HIS SENTENCE READ LITERALLY (near AND ex-fence): that case is EMPTY BY CONSTRUCTION, and it
was measured. `keep` absorbs anything ex-fence within a GAP_MAX = 4 gap, so an ex-fence line within
4 TFs of the top is already a block MEMBER and cannot be a claimer. Across the 43 `band claimed`
rows on 12 days there were ZERO ex-fence claimers at hop <= 5; every one sat at +6 or further.
Requiring ex-fence would have released all 43, i.e. deleted the test.

MEASURED AT +3: 11 of 43 rows released, median MAE 0.2032, mean MFE 0.8555, 4 of the 11 over 0.70.
"""


def branchD(d, ex):
    exf = (lambda v: v >= HI) if d > 0 else (lambda v: v <= LO)
    blk = [t for t in TF if np.isfinite(Rl[t][ex]) and exf(Rl[t][ex])]
    af = anchor_floater(Rl[1], PX, d, ex, block=AF_BLOCK)
    div = bool(af.get('fired')) if isinstance(af, dict) else False
    w1 = float(af['floater'][1]) if div else float(Rl[1][ex])
    keep, drop = [], []
    if blk:
        keep = [blk[0]]
        for t in blk[1:]:
            if t - keep[-1] - 1 <= GAP_MAX: keep.append(t)
        drop = [t for t in blk if t not in keep]
    if not keep:
        return {'fire': False, 'why': 'no r block', 'keep': [], 'claim': [], 'net': None, 'band': None}
    weak = min(keep, key=lambda t: Rl[t][ex]) if d > 0 else max(keep, key=lambda t: Rl[t][ex])
    band = (min(w1, Rl[weak][ex]), max(w1, Rl[weak][ex]))
    top = max(keep)
    claim = [t for t in TF if top < t <= top + CLAIM_HOP and np.isfinite(Rl[t][ex])
             and band[0] <= Rl[t][ex] <= band[1]]
    net = Mg[12][ex] - Mg[1][ex]
    away = (net < 0) if d > 0 else (net > 0)
    return {'fire': not claim, 'why': 'band claimed' if claim else 'fires', 'keep': keep, 'drop': drop,
            'claim': claim, 'net': net, 'away': away, 'band': band, 'weak': weak}

# ---------------- swing_detect scoring, banked convention
def pivots(pct):
    piv = find_pivots(PX, pct)
    return (np.array([p for p, kk in piv if kk == 'H']), np.array([p for p, kk in piv if kk == 'L']))

def score(k, d, Hs, Ls):
    """-> (mfe, mae, pivot_bar) over the stretch from `k` to swing_detect's next FAVOURABLE pivot.

    d +1 = SHORT, favourable = the next L. d -1 = LONG, favourable = the next H.

    `pivot_bar` WAS NAMED `exit_bar` AND THAT WAS WRONG. Joe 1006: *"scoring comes from MAE and MFE.
    there is no other scoring"*. There is no exit mech in this project and this bar is not standing in
    for one - MAE and MFE are EXCURSIONS over a stretch, and the stretch's far edge IS the next
    favourable pivot. Nothing opens, nothing closes, nothing is realised. The old name carried a P&L
    frame into every sentence written about it, and it did leak: 1006 I described two stretches as a
    trade that "had already closed, in profit".

    THE ONE THING THIS BAR DOES MEAN FOR AN A/B: the stretch has two edges, the start bar and this
    pivot. Move the start and the stretch moves. Measured 1006 on the g5-extrema-vs-octo-sig start
    comparison: 340 of 356 rows ran to the SAME pivot (comparable), and the 16 that did not averaged
    a 1.1 minute stretch against 54.2 minutes - which alone produced a false improvement of
    0.6470 -> 0.6097 until they were separated out.
    """
    entry = float(PX[k])
    tgt = Ls if d > 0 else Hs
    nxt = tgt[tgt > k]
    if nxt.size == 0: return (None, None, None)
    j = int(nxt[0]); seg = PX[k:j + 1]
    seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return (None, None, None)
    if d > 0:
        mfe = (entry - float(seg.min())) / entry * 100.0
        mae = max(0.0, (float(seg.max()) - entry) / entry * 100.0)
    else:
        mfe = (float(seg.max()) - entry) / entry * 100.0
        mae = max(0.0, (entry - float(seg.min())) / entry * 100.0)
    return (mfe, mae, j)

# ---------------- population
DAY = os.environ.get('LG_DAY', '2026-09-25')
A0, A1 = K(DAY + ' 00:00:00'), K(DAY + ' 23:59:55')
OS = []
for ln in open(_os.path.join(_HERE, 'octosig') + '/%s.out' % DAY):
    if ln.startswith('R|') and not ln.startswith('R|run'):
        f = ln.rstrip('\n').split('|')
        if len(f) >= 7:
            k = K(DAY + ' ' + f[2])
            if A0 <= k <= A1: OS.append((k, f[2]))

MTD_WALK_BARS = int(LG['mtd_walk_bars'])
"""THE 2 MINUTE FORWARD WALK. Joe 1005: *"bake the 2 minute forward walk"*.

24 bars = 120 s at the 5 s grid. When mtd does not route at the octo-sig bar, the walk walks: mtd is
re-tested at EVERY bar forward until it routes r1 or r2, or the window runs out. CAUSAL - mtd(j)
reads only bars at or before j.

MEASURED BEFORE BAKING, on the 64 `neither` signals over 12 days:
  changed at 1 min   11 of 64
  changed at 2 min   22 of 64   (21 -> mtd.r1, 1 -> mtd.r2)
  MAE mean           0.5941 -> 0.5920   (-0.0021)
  MFE mean           0.7787 -> 0.8653   (+0.0867)
  MAE > 0.70 BLOCK   7 -> 5
The arm-bar alternative was measured and REJECTED: mtd qualifies somewhere in the arm -> octo-sig
stretch on 55 of 64 but on only a median 53.8 % of its bars and on every bar for NONE of them - it
flickers - and taking the first qualification moved entry a median 54.5 min earlier for MAE mean
+0.2970, MFE mean -0.2399 and 12 more BLOCKs.

THE ENTRY BAR MOVES TO THE QUALIFYING BAR. That is the version the numbers above were measured on.
"""


def classify(k, lbl=None):
    """mtd + branch D -> the BLOCK / CONFLUENCE / OPEN row for one octo-sig bar.

    LIFTED OUT OF THE ROWS LOOP 1005 so `octosig_db.py` calls it instead of copying these fourteen
    lines. Joe 1005: *"using sanctioned producers keeps us whole and prevents sweeping
    misunderstandings"*. The loop below now calls it, so the report and the DB table cannot answer
    the status question differently. Behaviour unchanged.
    """
    m = mtd(k)
    kw = k                                    # the bar the route was taken on
    d_sig = int(DRv[k])                       # the OCTO-SIG's own dr. The routing must read its fence.
    if m['route'] not in ('mtd.r1', 'mtd.r2') and MTD_WALK_BARS > 0:
        for j in range(k + 1, min(TAPE_LAST, k + MTD_WALK_BARS) + 1):
            # THE dr GUARD, 1006. The walk had none, so a bar whose dr had flipped could supply the
            # route - and mtd() picks its fence from THAT bar's dr. The whole branch-D read (blk,
            # keep, the r ladder, the mage net, the grade) was then taken on the OPPOSITE fence from
            # the signal, while os_dr still recorded the signal's dr. Joe 1006 found it on 09-30
            # 15:25:45: dr +1, mtd `neither` with ex 15:22:10, the walk moves ONE bar to 15:25:50
            # where dr is -1, and the row takes that bar's mtd.r1 and its LOW-side ex 15:24:55 -
            # which is how a +1 and a -1 signal came to share one g5extrema.
            #
            # MEASURED BEFORE THE FIX, 397 rows / 12 days: the walk ran on 22, and 2 crossed a flip -
            # 09-17 07:49:00 (-1 -> +1 after 14 bars) and 09-30 15:25:45 (+1 -> -1 after 1 bar).
            # ZERO with-trend rows of 53 were affected.
            #
            # THE RULE IS MINE, and it is the minimal one: a bar may supply the route only if its dr
            # EQUALS the signal's. Mismatched bars are SKIPPED, not terminal, so a dr that flips away
            # and returns inside the window can still serve. The stricter reading - stop the walk at
            # the first flip - differs on neither of the 2 measured rows, because each crossed on the
            # bar that gave it its route.
            if int(DRv[j]) != d_sig:
                continue
            m2 = mtd(j)
            if m2['route'] in ('mtd.r1', 'mtd.r2'):
                m, kw = m2, j
                break
    d = m['d']; side = 'SHORT' if d > 0 else 'LONG'
    r = {'k': k, 'kw': kw, 'walk_bars': kw - k, 'lbl': lbl, 'd': d, 'side': side, 'm': m}
    if m['route'] == 'mtd.r1':
        dd = branchD(d, m['ex']); r['D'] = dd
        if dd['fire']:
            # GRADE CORRECTED 1006. Joe: *"`with-trend` would be SHORT because dr is -1. the truth is
            # what the MAE and MFE are reporting - the only change to make is `against-trend`"*. The
            # mapping was recorded in 1005_knobs.md:22 as his 1004 ruling, AWAY = with-trend, and it is
            # inverted. AWAY from dr is now **against-trend**; TOWARDS is **with-trend**, which matches
            # 1003_lazy_g_spec.md:403 - *"present = with-trend, absent = against-trend"*.
            # THE STAGE-2 FLIP POPULATION DOES NOT MOVE. Every selector is pinned to `away` itself, not
            # to the label, so the rows Joe flipped on 1005 are the same rows. Only their NAME changed.
            r['status'] = 'CONFLUENCE'; r['grade'] = 'against-trend' if dd['away'] else 'with-trend'
        else:
            r['status'] = 'OPEN'; r['grade'] = dd['why']
    elif m['route'] == 'mtd.r2':
        r['status'] = 'BLOCKED'; r['grade'] = 'allows %s only' % m['allow']
    else:
        r['status'] = 'OPEN'; r['grade'] = 'no rule'
    return r


ROWS = [classify(k, lbl) for k, lbl in OS]

# ---------------- the swing-size sweep
print('## SWING SIZE SWEEP — the measurement that picks the pct')
print('| swing pct | pivots on the tape | median hold (min) | scored | MAE>0.7 | MAE>0.8 | MFE med | MAE med | MFE>MAE |')
print('|' + '---|' * 9)
CACHE = {}
for pct in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0):
    Hs, Ls = pivots(pct); CACHE[pct] = (Hs, Ls)
    sc = [score(r['k'], r['d'], Hs, Ls) for r in ROWS]
    ok = [(f, a, j, r) for (f, a, j), r in zip(sc, ROWS) if f is not None]
    hold = [(ts[j] - ts[r['k']]) / 60000.0 for f, a, j, r in ok]
    mfes = [f for f, a, j, r in ok]; maes = [a for f, a, j, r in ok]
    print('| %.2f | %d | %.1f | %d | %d | %d | %.3f | %.3f | %d |'
          % (pct, len(Hs) + len(Ls), float(np.median(hold)), len(ok),
             sum(1 for a in maes if a > 0.7), sum(1 for a in maes if a > 0.8),
             float(np.median(mfes)), float(np.median(maes)),
             sum(1 for f, a, j, r in ok if f > a)))

# ---------------- which swing size DISCRIMINATES? the mech's own split vs the MAE line
print()
print('## DISCRIMINATION — does the mech already separate MAE at this swing size?')
print('# CONF = the 20 branch-D confluences · NOT-CONF = the 5 BLOCKED + 14 OPEN')
print('| swing pct | CONF MAE med | NOT-CONF MAE med | CONF MAE>0.7 | NOT-CONF MAE>0.7 | CONF MFE>MAE | NOT MFE>MAE | agree with 0.7 line |')
print('|' + '---|' * 8)
for pct in (0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.25, 1.5, 2.0):
    Hs, Ls = CACHE[pct]
    C, Nn = [], []
    for r in ROWS:
        f, a, j = score(r['k'], r['d'], Hs, Ls)
        (C if r['status'] == 'CONFLUENCE' else Nn).append((f, a))
    agree = sum(1 for f, a in C if a <= 0.7) + sum(1 for f, a in Nn if a > 0.7)
    print('| %.2f | %.3f | %.3f | %d of %d | %d of %d | %d of %d | %d of %d | %d of 39 |'
          % (pct, float(np.median([a for f, a in C])), float(np.median([a for f, a in Nn])),
             sum(1 for f, a in C if a > 0.7), len(C), sum(1 for f, a in Nn if a > 0.7), len(Nn),
             sum(1 for f, a in C if f > a), len(C), sum(1 for f, a in Nn if f > a), len(Nn), agree))

# ---------------- grade vs MAE, both candidate swing sizes
print()
print('## MAE BY GRADE — is the heat concentrated in one of the two confluence paths?')
print('| swing pct | with-trend MAE med | against-trend MAE med | with MAE>0.7 | against MAE>0.7 | with MFE med | against MFE med |')
print('|' + '---|' * 7)
for pct in (0.7, 1.0):
    Hs, Ls = CACHE[pct]
    W, Ag = [], []
    for r in ROWS:
        if r['status'] != 'CONFLUENCE': continue
        f, a, j = score(r['k'], r['d'], Hs, Ls)
        (W if r['grade'] == 'with-trend' else Ag).append((f, a))
    print('| %.2f | %.3f | %.3f | %d of %d | %d of %d | %.3f | %.3f |'
          % (pct, float(np.median([a for f, a in W])), float(np.median([a for f, a in Ag])),
             sum(1 for f, a in W if a > 0.7), len(W), sum(1 for f, a in Ag if a > 0.7), len(Ag),
             float(np.median([f for f, a in W])), float(np.median([f for f, a in Ag]))))

# ---------------- per-row dump, everything needed to write the gap column
print()
print('## PER-ROW — swing 1.0 (banked) and swing 0.7 (the knee)')
print('| octo-sig | dr | side | status | grade | route | mtd oob | mtd net | D keep | D band | D claim | mage net | MAE@1.0 | MFE@1.0 | MAE@0.7 | MFE@0.7 | hold@1.0 min |')
print('|' + '---|' * 17)
H10, L10 = CACHE[1.0]; H07, L07 = CACHE[0.7]
for r in ROWS:
    m = r['m']; d = r['d']
    f1, a1, j1 = score(r['k'], d, H10, L10)
    f7, a7, j7 = score(r['k'], d, H07, L07)
    oob = '4/4' if m.get('noob') == 4 else '%d/4 (%s)' % (m.get('noob', 0), ','.join(m.get('miss', [])))
    D = r.get('D')
    print('| %s | %+d | %s | %s | %s | %s | %s | %+.2f | %s | %s | %s | %s | %.3f | %.3f | %.3f | %.3f | %.1f |'
          % (r['lbl'], d, r['side'], r['status'], r['grade'], m['route'], oob, m.get('net', float('nan')),
             (','.join('ws%d' % t for t in D['keep']) if D and D['keep'] else '-') if D else '-',
             ('[%.2f, %.2f]' % D['band']) if D and D['band'] else '-',
             (','.join('ws%d' % t for t in D['claim']) if D and D['claim'] else 'none') if D else '-',
             ('%+.2f' % D['net']) if D and D['net'] is not None else '-',
             a1, f1, a7, f7, (ts[j1] - ts[r['k']]) / 60000.0))

# ---------------- the distances the gap column needs
print()
print('## FENCE DISTANCES for the `neither` rows — how far the failing line is from its oob fence')
print('| octo-sig | dr | fence | g5 | g15 | g30 | ws1 | failing line | distance to fence |')
print('|' + '---|' * 9)
for r in ROWS:
    m = r['m']
    if m['route'] != 'neither': continue
    d = m['d']; fence = HI if d > 0 else LO
    dist = {n: (fence - m['v'][n]) if d > 0 else (m['v'][n] - fence) for n in m['miss']}
    print('| %s | %+d | %s %.0f | %.2f | %.2f | %.2f | %.2f | %s | %s |'
          % (r['lbl'], d, 'hi' if d > 0 else 'lo', fence, m['v']['g5'], m['v']['g15'], m['v']['g30'],
             m['v']['ws1'], ','.join(m['miss']), ', '.join('%s %+.2f' % (n, -dist[n]) for n in m['miss'])))

print()
print('## BAND DISTANCES for the `D no fire` rows — how far the claiming TF is inside the band')
print('| octo-sig | dr | band | claiming TF | its r | distance inside the nearer edge |')
print('|' + '---|' * 6)
for r in ROWS:
    D = r.get('D')
    if not D or D['fire'] or not D['claim']: continue
    lo_, hi_ = D['band']
    for t in D['claim']:
        v = Rl[t][r['m']['ex']]
        print('| %s | %+d | [%.2f, %.2f] | ws%d | %.2f | %.2f |' % (r['lbl'], r['d'], lo_, hi_, t, v, min(v - lo_, hi_ - v)))

# ---------------- FIRST TOUCH: would the live mae_cap 0.70 stop fire, and when?
# mae_cap 0.70 % of entry is NOT a knob I am choosing - it is live inside trade_walk today
# (memory `mae-mfe-only`). The banked scoring convention has no stop, so the MAE above is the
# UNSTOPPED heat. This block asks the only question that distinguishes them: which came first.
print()
print('## FIRST TOUCH — adverse 0.70%% vs the favourable pivot, swing 0.70')
print('| octo-sig | status | MAE% | MFE% | adverse 0.70 touched | at (min) | pivot at (min) | stop fires first |')
print('|' + '---|' * 8)
H07, L07 = CACHE[0.7]
FT = {}
for r in ROWS:
    d = r['d']; k = r['k']; entry = float(PX[k])
    f, a, j = score(k, d, H07, L07)
    if f is None:
        FT[r['lbl']] = None; continue
    seg = PX[k:j + 1]
    adv = (seg - entry) / entry * 100.0 if d > 0 else (entry - seg) / entry * 100.0
    hit = np.flatnonzero(np.isfinite(adv) & (adv >= 0.70))
    tmin = (ts[j] - ts[k]) / 60000.0
    if hit.size:
        hmin = (ts[k + int(hit[0])] - ts[k]) / 60000.0
        FT[r['lbl']] = hmin
        print('| %s | %s | %.3f | %.3f | yes | %.1f | %.1f | %s |'
              % (r['lbl'], r['status'], a, f, hmin, tmin, 'YES' if hmin < tmin else 'no'))
    else:
        FT[r['lbl']] = None
        print('| %s | %s | %.3f | %.3f | no | — | %.1f | no |' % (r['lbl'], r['status'], a, f, tmin))

# ---------------- the degenerate band: a one-member ex-fence block
print()
print('## ONE-MEMBER ex-fence BLOCK — the band collapses to [ws1r, its floater], so no TF can object')
print('| block size | confluences | MAE>0.7 | MAE med |')
print('|' + '---|' * 4)
buck = {}
for r in ROWS:
    if r['status'] != 'CONFLUENCE': continue
    f, a, j = score(r['k'], r['d'], H07, L07)
    buck.setdefault(1 if len(r['D']['keep']) == 1 else 2, []).append(a)
for kk in sorted(buck):
    v = buck[kk]
    print('| %s | %d | %d | %.3f |' % ('1 member' if kk == 1 else '2+ members', len(v),
                                       sum(1 for a in v if a > 0.7), float(np.median(v))))
