"""09-25 walked from 00:00 wearing an mtd lens. Joe 1004.

Two populations:
  A  the octo-sig (report_leash_walk --day 2026-09-25, 39 of them)
  B  the same-dr ws1mage-rev `sig` + ws1r oob events, each walked BAR BY BAR until ws1Mage returns
     in-bounds. Joe: "you'll find cases where the first ws1mage-rev is too early (exactly the same as
     the early octo-sig reversals, but in a smaller playpen), so mtd won't 'fit' - maybe the walk
     will show you a routable decision"

THE mtd LENS, Joe 1004, nothing invented:
  step 1  LOOKBACK, mech window 2 min = 24 bars, signal-2min..signal. Find the OPPOSING-dr g5Mage
          oob extrema (dr +1 -> g5Mage <= 15, take the min; dr -1 -> >= 85, take the max).
          No find -> DISQUALIFIED, walk forward.
  step 1f FORWARD WALK to the first opposing-dr g5Mage oob, then on to the g5Mage reversal at
          wob 2 (lr_v2._mage_rev, rev_wob 2 from v3_config). That bar is the extrema.
  step 2  the 4 mtd lines g5/g15/g30/ws1 Mage at the chosen extrema.
          mtd.r1  all 4 OPPOSING-dr oob            -> delegate to branch D
          mtd.r2  the 3 above g5 NET cascade TOWARDS dr -> confluence only the opposite-of-dr trade
          neither -> NO RULE YET, reported as `neither`
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
from optimus9.analysis.jig import ws1mage_rev
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e
EM = int(dt.datetime(2026, 10, 4, tzinfo=dt.timezone.utc).timestamp() * 1000)
HI, LO, DWELL, REV_WOB, HOLD = 85.0, 15.0, 3, 2, 4
LOOKBACK_BARS = 48   # 4 min. MEASURED KNEE, 09-25: 4 min captures 39 of 39 signals and nothing
#                      past it adds one - it only ages the extrema (median staleness 2.5 m at 4 min
#                      vs 6.8 m at 20 min). 2 min caught only 29 of 39; the furthest signal needs
#                      4.0 m (17:21:30). Joe 1004 asked "can you pick better lookback value?" after
#                      09:32:00 fell to the forward walk with its extrema only 3.6 m back.
db = DatabaseManager(**get_db_config()); db.connect()
spec = {}
for g in mech_lines(db, 'wsf'):
    if g['role'] not in spec: _t, s_, m_ = g['override']; spec[g['role']] = (s_, m_)
sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
db.disconnect()
tp = np.load(os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP, {'src': sy['s'], 'len': sy['l']}) + '.npz'))
ts = tp['__ts__']; PX = tp['__pxs__']
LD = lambda tfs, role: np.asarray(np.load(os.path.join(LINE_DIR, _line_key(EM, HOURS, WARMUP, override(tfs, *spec[role])) + '.npy'), mmap_mode='r'), float)
MTD = {'g5': LD(5, 'Mage'), 'g15': LD(15, 'Mage'), 'g30': LD(30, 'Mage'), 'ws1': LD(60, 'Mage')}
SM = LD(30, 'Mage'); R1 = LD(60, 'r'); M13 = LD(13 * 60, 'm'); G1 = MTD['ws1']
DRv = np.zeros(len(ts), np.int8); cur = 0
for k in range(min(len(ts), len(G1), len(M13))):
    a, b = G1[k], M13[k]
    if a == a and b == b:
        if a >= 85.0 and b >= 85.0: cur = +1
        elif a <= 15.0 and b <= 15.0: cur = -1
    DRv[k] = cur
REV = _mage_rev(MTD['g5'], REV_WOB)
U = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
K = lambda s: int(np.searchsorted(ts, int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))
TAPE_LAST = len(ts) - 1

# THE TOLERANCE, my call 1004 on Joe's "your call on the #2 window size".
# Joe 1004 first asked for 30 s, then dropped it reasoning "a 5s extrema is going to be the extrema
# of the lines above it". MEASURED ON THE 39 ANCHORS, that does not hold: g15's own extrema lands on
# the g5 extrema bar 16 of 39 times, g30's 15 of 39, with offsets to +-30 s in both directions.
# A window sweep 5..120 s shows NO STABILITY KNEE - the extrema bar keeps moving, so g15/g30 carry
# their own swing structure rather than a lag. So the window is anchored to CONSTRUCTION, not a curve:
# each line gets its own BAR WIDTH, the most its close can lag a 5 s close. At those widths only
# 2 of 39 (g15) and 3 of 39 (g30) extrema sit at the window edge.
TOL = {'g5': 0, 'g15': 3, 'g30': 6, 'ws1': 0}      # bars at the 5 s grid = 0 s, 15 s, 30 s, 0 s

def mtd(k):
    """-> dict. The mtd lens at bar k.

    JOE 1004 CORRECTION: "that's my mistake - the extrema test is same-dr". So the LOOKBACK hunts the
    SAME-dr g5Mage oob extrema (dr +1 -> >= 85, take the MAX). His forward-walk words are unchanged
    and say OPPOSING-dr, which is coherent: either the move already topped out in the recent past, or
    it has not and you wait for the opposite extreme and its reversal. SCOPE FLAGGED - his correction
    did not say whether it reaches the forward walk too.

    JOE 1004: "add a 30s tolerance for these 3 lines to capture each one's extrema". So g5/g15/g30 are
    each read at THEIR OWN same-dr extreme within +-30 s of the chosen bar; ws1 is read AT the bar.
    """
    d = int(DRv[k])
    if d == 0: return {'route': 'no dr', 'src': '-', 'ex': None, 'd': 0}
    same = (lambda v: v >= HI) if d > 0 else (lambda v: v <= LO)
    opp  = (lambda v: v <= LO) if d > 0 else (lambda v: v >= HI)
    a = max(0, k - LOOKBACK_BARS)
    hits = [i for i in range(a, k + 1) if np.isfinite(MTD['g5'][i]) and same(MTD['g5'][i])]
    if hits:
        ex = max(hits, key=lambda i: MTD['g5'][i]) if d > 0 else min(hits, key=lambda i: MTD['g5'][i])
        src = 'lookback'
    else:
        # JOE 1004: "yes same-dr for the forward walk too". His original words said opposing-dr;
        # this ruling replaces them.
        j = k
        while j < TAPE_LAST and not (np.isfinite(MTD['g5'][j]) and same(MTD['g5'][j])): j += 1
        if not (np.isfinite(MTD['g5'][j]) and same(MTD['g5'][j])):
            return {'route': 'NO-FIND oob', 'src': 'fwd', 'ex': None, 'd': d}
        # the extrema is a HIGH at dr +1, so the reversal turns DOWN
        want = -1 if d > 0 else +1
        nxt = [i for i in range(j, TAPE_LAST + 1) if REV[i] == want]
        if not nxt: return {'route': 'NO-FIND rev', 'src': 'fwd', 'ex': None, 'd': d}
        ex = nxt[0]; src = 'fwd'
    # STEP 2 READS THE STEP-1 EXTREMA. Joe 1004 held the signal bar briefly, then rolled it back:
    # "you're absolutely right. rollback, and 07:59 will route to branch D". The reason is mechanical
    # - the step-1 extrema IS the bar where the Mages are most extreme, so reading any other bar
    # loses oob conformance by construction. Measured: signal-bar reading collapsed mtd.r1 from 22 of
    # 39 to 2 of 39.
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
    net = v['ws1'] - v['g15']
    towards = (net > 0) if d > 0 else (net < 0)
    route = 'mtd.r1' if r1 else ('mtd.r2' if towards else 'neither')
    allow = ('LONG' if d > 0 else 'SHORT') if route == 'mtd.r2' else '-'
    return {'route': route, 'src': src, 'ex': ex, 'd': d, 'v': v, 'vbar': vbar, 'net': net,
            'towards': towards, 'allow': allow, 'lag': (ts[ex] - ts[k]) / 60000.0}

A0, A1 = K('2026-09-25 00:00:00'), K('2026-09-25 23:59:55')
# ---- population A: the octo-sig
OS = []
for ln in open(_os.path.join(_HERE, 'octosig') + '/2026-09-25.out'):
    if ln.startswith('R|') and not ln.startswith('R|run'):
        f = ln.rstrip('\n').split('|')
        if len(f) >= 7:
            k = K('2026-09-25 ' + f[2])
            if A0 <= k <= A1: OS.append((k, f[2], int(f[5])))
print('## POPULATION A — the %d octo-sig of 09-25 under the mtd lens' % len(OS))
print('| octo-sig | dr | dr-bias trade | step 1 | extrema | lag | g5 | g15 | g30 | ws1 | oob 4/4 | net g15->ws1 | cascade | route | allows | verdict |')
print('|' + '---|' * 16)
cnt = {}
for k, lbl, _d in OS:
    m = mtd(k)
    cnt[m['route']] = cnt.get(m['route'], 0) + 1
    bias = 'SHORT' if m['d'] > 0 else 'LONG'
    if m['ex'] is None:
        print('| %s | %+d | %s | %s | — | — | — | — | — | — | — | **%s** | — | — |' % (lbl, m['d'], bias, m['src'], m['route']))
        continue
    verdict = ('**BLOCKED**' if m['allow'] != bias else 'allowed') if m['route'] == 'mtd.r2' else (
              'delegate to D' if m['route'] == 'mtd.r1' else 'no rule')
    same = (lambda x: x >= HI) if m['d'] > 0 else (lambda x: x <= LO)
    noob = sum(1 for n in ('g5','g15','g30','ws1') if np.isfinite(m['v'][n]) and same(m['v'][n]))
    miss = [n for n in ('g5','g15','g30','ws1') if not (np.isfinite(m['v'][n]) and same(m['v'][n]))]
    oobc = '**4/4**' if noob == 4 else '%d/4 (%s out)' % (noob, ','.join(miss))
    casc = 'lifting' if m['net'] > 0 else 'falling'
    casc += ' = %s' % ('TOWARDS dr' if m['towards'] else 'AWAY from dr')
    print('| %s | %+d | %s | %s | %s | %+.1f m | %.2f | %.2f | %.2f | %.2f | %s | %+.2f | %s | **%s** | %s | %s |'
          % (lbl, m['d'], bias, 'lookback' if m['src'] == 'lookback' else 'DISQ -> fwd', U(m['ex']),
             m['lag'], m['v']['g5'], m['v']['g15'], m['v']['g30'], m['v']['ws1'], oobc, m['net'],
             casc, m['route'], m['allow'], verdict))
print()
print('routes: %s' % ', '.join('%s %d' % (r, n) for r, n in sorted(cnt.items())))
