"""Branch D derived for every mtd.r1 row of 09-25. Joe 1004.

D = the r-cascade (fires it) + the mage-cascade (grades the trend). Spec: 1003_lazy_g_spec.md D.1-D.5.
  r-cascade  an ex-fence block of ws{t}r on the dr side (oob 15/85), block membership tolerating a
             gap of up to LAZY_G_D_GAP_MAX 4 SKIPPED TFs; ws1 is in the ladder and is accepted when
             the divergence test fires, in which case ws1r CLAIMS ITS FLOATER VALUE (Joe: "the
             floater, ie the moment when ws1r completed its purpose"); and the Q3 band test - higher
             TFs have NO CLAIM unless they print between ws1r and the weakest ex-fence r.
  mage-cascade  net Mage ws1->ws12. AWAY from dr = with-trend, TOWARDS dr = against-trend (smaller
             size is MVP2, not here).
  verdict    confluence.

ANCHOR, MY READING, STATED: D runs at the extrema mtd chose. mtd is the priority gate and that bar is
the turn it identified; both anchors are a g5Mage same-dr oob extrema found by different procedures.
THE "LOOKBACK TEST" for ws1 is still undefined by Joe, so only the DIVERGENCE test is applied, and
the ib-return lead is reported beside it as data.
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
from optimus9.analysis.jig import anchor_floater, AF_BLOCK
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e
EM = int(dt.datetime(2026, 10, 4, tzinfo=dt.timezone.utc).timestamp() * 1000)
HI, LO, GAP_MAX = 85.0, 15.0, 4
db = DatabaseManager(**get_db_config()); db.connect()
spec = {}
for g in mech_lines(db, 'wsf'):
    if g['role'] not in spec: _t, s_, m_ = g['override']; spec[g['role']] = (s_, m_)
sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
db.disconnect()
tp = np.load(os.path.join(TAPE_DIR, _tape_key(EM, HOURS, WARMUP, {'src': sy['s'], 'len': sy['l']}) + '.npz'))
ts = tp['__ts__']; PX = tp['__pxs__']
LD = lambda tfs, role: np.asarray(np.load(os.path.join(LINE_DIR, _line_key(EM, HOURS, WARMUP, override(tfs, *spec[role])) + '.npy'), mmap_mode='r'), float)
TF = list(range(1, 13))
Rl = {t: LD(t * 60, 'r') for t in TF}
Mg = {t: LD(t * 60, 'Mage') for t in TF}
U = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')
K = lambda s: int(np.searchsorted(ts, int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))

ROWS = []
for ln in open(_os.path.join(_HERE, 'mtd_A7.out')):
    f = ln.split('|')
    if len(f) < 16 or 'mtd.r1' not in ln: continue
    ROWS.append((f[1].strip(), +1 if '+1' in f[2] else -1, K('2026-09-25 ' + f[5].strip())))
print('## BRANCH D at the mtd.r1 extrema — %d rows' % len(ROWS))
print('| octo-sig | dr | D anchor | ws1r raw | ws1 div | ws1r used | ex-fence block | gaps ok | weakest | band | higher TFs with a claim | r-cascade | Mage ws1->ws12 | mage-cascade | branch D |')
print('|' + '---|' * 15)
tally = {}
for lbl, d, ex in ROWS:
    exf = (lambda v: v >= HI) if d > 0 else (lambda v: v <= LO)
    blk = [t for t in TF if np.isfinite(Rl[t][ex]) and exf(Rl[t][ex])]
    af = anchor_floater(Rl[1], PX, d, ex, block=AF_BLOCK)
    # anchor_floater returns None when the 4-step chooser cannot seat an anchor/pivot/floater
    div = bool(af.get('fired')) if isinstance(af, dict) else False
    w1raw = Rl[1][ex]
    w1 = float(af['floater'][1]) if div else float(w1raw)
    # block membership with the gap tolerance: walk up from the lowest member, allow <= GAP_MAX skips
    keep = []
    if blk:
        keep = [blk[0]]
        for t in blk[1:]:
            if t - keep[-1] - 1 <= GAP_MAX: keep.append(t)
        drop = [t for t in blk if t not in keep]
    else:
        drop = []
    if not keep:
        print('| %s | %+d | %s | %.2f | %s | %.2f | **none** | - | - | - | - | **no** | - | - | **no fire** |'
              % (lbl, d, U(ex), w1raw, 'fires' if div else 'no', w1)); tally['no fire'] = tally.get('no fire', 0) + 1
        continue
    weak = min(keep, key=lambda t: Rl[t][ex]) if d > 0 else max(keep, key=lambda t: Rl[t][ex])
    band = (min(w1, Rl[weak][ex]), max(w1, Rl[weak][ex]))
    claim = [t for t in TF if t > max(keep) and np.isfinite(Rl[t][ex]) and band[0] <= Rl[t][ex] <= band[1]]
    rcasc = not claim
    net = Mg[12][ex] - Mg[1][ex]
    away = (net < 0) if d > 0 else (net > 0)
    mc = ('AWAY = with-trend' if away else 'TOWARDS = against-trend')
    out = ('**confluence, %s**' % ('with-trend' if away else 'against-trend')) if rcasc else '**no fire**'
    tally[out] = tally.get(out, 0) + 1
    print('| %s | %+d | %s | %.2f | %s | %.2f | %s | %s | ws%d %.2f | [%.2f, %.2f] | %s | %s | %+.2f | %s | %s |'
          % (lbl, d, U(ex), w1raw, 'fires' if div else 'no', w1,
             ','.join('ws%d' % t for t in keep), 'yes' if not drop else 'dropped ' + ','.join('ws%d' % t for t in drop),
             weak, Rl[weak][ex], band[0], band[1],
             ', '.join('ws%d' % t for t in claim) if claim else '**none**',
             '**fires**' if rcasc else 'no', net, mc, out))
print()
print('outcomes: %s' % ', '.join('%s %d' % (k, v) for k, v in sorted(tally.items())))
