"""HTF PEGGING (Joe's term, 1007) across the 11 ws12r oob>6min runs on 09-25.

JOE 1007: *"what jumps out at me is ws12Mage - it stayed higher than 50 after travlling from a high
oob at 20:24. that's my definition of HTF pegging, and it's also the peak of a mage cascade/mage
ladder that's predicting a counter-dr trend. -- how often does that appear in the other trades?"*

WHAT IS MEASURED, read straight off his sentence:
  the last oob visit   the most recent bar at or before the gate where ws12Mage was oob, and WHICH
                       SIDE. Pegging needs it on the COUNTER-dr side: hi (>= oob_hi) for a -dr run,
                       lo (<= oob_lo) for a +dr run.
  stayed past 50       ws12Mage has NOT crossed 50 to the dr side since that visit. For a -dr run
                       the dr side is below 50; for +dr it is above.
  PEGGED               both of the above. Reported over two windows, because Joe's sentence does
                       not say which: [last oob -> gate] and [last oob -> exit].

WHAT IS NOT MEASURED: *"the peak of a mage cascade/mage ladder"*. Task #22, the mage-cascade, is
PARKED - *"rebuild dr-free before anything else"* - and there is no ruled producer for a cascade
peak. Testing it would mean inventing the test. The ws12Mage half is all this file claims.

Knobs from ws12_baton_config v1 and lazy_g_config v1.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import anchor_floater
from optimus9.compute.spec_config import spec_config
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

D = os.environ.get('W_DAY', '2026-09-25')
db = DatabaseManager(**get_db_config()); db.connect()
W = spec_config(db, 'ws12_baton_config'); db.disconnect()
GATE_BARS, SIG_WIN = int(W['oob_gate_bars']), int(W['sig_window_bars'])
TRIG_TF, DIP_MID = int(W['ceil_trig_tf']), float(W['dip_mid'])
DIP_DWELL, RREV = int(W['dip_dwell_bars']), int(W['rrev_wob'])
DIV_TFS = [int(s.strip().replace('ws', '').replace('r', '')) for s in W['div_lines'].split(',')]
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
R12 = SC.LD(TRIG_TF * 60, 'r')[:N]; X12 = SC.LD(TRIG_TF * 60, 'x')[:N]
M12 = SC.Mg[TRIG_TF][:N]
R = {t: SC.LD(t * 60, 'r')[:N] for t in DIV_TFS}
X = {t: SC.LD(t * 60, 'x')[:N] for t in DIV_TFS}
G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
REV = {t: _mage_rev(R[t], RREV) for t in DIV_TFS}
d0, d1 = K('00:00:00'), K('23:59:55')

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))

xund = lambda t, k, d: (float(X[t][k]) < float(R[t][k])) if d > 0 else (float(X[t][k]) > float(R[t][k]))
indip = lambda k, d: (float(G1[k]) < DIP_MID) if d > 0 else (float(G1[k]) > DIP_MID)
WANT = lambda d: (-1 if d > 0 else +1)

# ---- Joe's 20:24 read, pinned
print('# JOE\'S 20:24 READ — ws12Mage\'s oob visit before the 21:48 run')
a24 = K('20:00:00')
hi_bars = [k for k in range(a24, K('21:54:05') + 1) if float(M12[k]) >= SC.HI]
box(('what', 'ts', 'ws12Mage'),
    ([('first hi-oob bar after 20:00', SC.U(hi_bars[0]), '%.2f' % float(M12[hi_bars[0]])),
      ('LAST hi-oob bar before the gate', SC.U(hi_bars[-1]), '%.2f' % float(M12[hi_bars[-1]])),
      ('hi-oob bars in 20:00..21:54:05', str(len(hi_bars)), '—')]
     if hi_bars else [('no hi-oob bar in 20:00..21:54:05', '—', '—')]))
if hi_bars:
    lo50 = [k for k in range(hi_bars[-1], K('23:22:45') + 1) if float(M12[k]) < DIP_MID]
    print('- ws12Mage bars BELOW 50 between that visit and the 23:22:45 exit: %d of %d'
          % (len(lo50), K('23:22:45') - hi_bars[-1] + 1))
    print('- ws12Mage min over that stretch: %.2f at %s'
          % (float(np.nanmin(M12[hi_bars[-1]:K('23:22:45') + 1])),
             SC.U(hi_bars[-1] + int(np.nanargmin(M12[hi_bars[-1]:K('23:22:45') + 1])))))

# ---- the 11 runs
RUNS = []
for side, dd in (('hi', +1), ('lo', -1)):
    oob = (R12 >= SC.HI) if dd > 0 else (R12 <= SC.LO)
    k = d0
    while k <= d1:
        if not (np.isfinite(R12[k]) and oob[k]):
            k += 1; continue
        a = k
        while k <= d1 and np.isfinite(R12[k]) and oob[k]:
            k += 1
        if (k - a - 1) > GATE_BARS:
            RUNS.append(dict(dr=dd, a=a, b=k - 1))
RUNS.sort(key=lambda r: r['a'])

def walk(r):
    a, b, d = r['a'], r['b'], r['dr']
    o = dict(gate=a + GATE_BARS + 1, dip=None, conf=None, exit=None, tf=None)
    for k in range(o['gate'], d1 + 1):
        if indip(k, d) and not indip(k - 1, d):
            n = 0
            while k + n <= N - 1 and indip(k + n, d):
                n += 1
            if n > DIP_DWELL:
                o['dip'], o['conf'] = k, k + DIP_DWELL - 1
                break
    if o['conf'] is None: return o
    for k in range(o['conf'] + 1, d1 + 1):
        for t in DIV_TFS:
            if REV[t][k] != WANT(d) or not xund(t, k, d): continue
            af = anchor_floater(R[t], PX, d, k)
            if af is None or int(af['fired']) == 0: continue
            o['exit'], o['tf'] = k, t
            return o
    return o

def mm(s, e, dd):
    seg = PX[s:e + 1]
    seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return None
    p = float(PX[s])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return dict(mfe=(f - p) / p * 100.0 * dd, mae=max(0.0, -((g - p) / p * 100.0 * dd)),
                real=(float(PX[e]) - p) / p * 100.0 * dd)

def peg(r, w):
    """-> dict. The last ws12Mage oob visit at or before the gate, its side, and whether ws12Mage
    has crossed 50 to the dr side since - over [visit, gate] and [visit, exit]."""
    d, g = r['dr'], w['gate']
    vis = None; vside = None
    for k in range(g, max(d0, g - 17280) - 1, -1):          # back to the day start at most
        v = float(M12[k])
        if not np.isfinite(v): continue
        if v >= SC.HI: vis, vside = k, 'hi'; break
        if v <= SC.LO: vis, vside = k, 'lo'; break
    if vis is None:
        return dict(vis=None, vside=None, counter=None, pg_gate=None, pg_exit=None,
                    mn_gate=None, mn_exit=None)
    counter = (vside == 'lo') if d > 0 else (vside == 'hi')
    drside = (lambda v: v > DIP_MID) if d > 0 else (lambda v: v < DIP_MID)
    seg_g = M12[vis:g + 1]
    cross_g = bool(np.any([drside(float(v)) for v in seg_g if np.isfinite(v)]))
    ext_g = (float(np.nanmin(seg_g)) if d > 0 else float(np.nanmax(seg_g)))
    out = dict(vis=vis, vside=vside, counter=counter, pg_gate=(counter and not cross_g),
               mn_gate=ext_g, pg_exit=None, mn_exit=None)
    if w['exit'] is not None:
        seg_e = M12[vis:w['exit'] + 1]
        cross_e = bool(np.any([drside(float(v)) for v in seg_e if np.isfinite(v)]))
        out['pg_exit'] = (counter and not cross_e)
        out['mn_exit'] = (float(np.nanmin(seg_e)) if d > 0 else float(np.nanmax(seg_e)))
    return out

OUT = []
for r in RUNS:
    w = walk(r)
    m = mm(w['gate'], w['exit'], r['dr']) if w['exit'] else None
    OUT.append((r, w, m, peg(r, w)))

print('\n# HTF PEGGING ACROSS THE 11 RUNS')
box(('oob from', 'dr', 'ws12Mage at gate', 'last oob visit', 'side', 'min since',
     'counter-dr side?', 'PEGGED to the gate', 'PEGGED to the exit', 'MAE%', 'MFE%',
     'MAE > MFE?'),
    [(SC.U(r['a']), '%+d' % r['dr'], '%.2f' % float(M12[w['gate']]),
      SC.U(p['vis']) if p['vis'] else '—', p['vside'] or '—',
      ('%.2f' % p['mn_gate']) if p['mn_gate'] is not None else '—',
      ('YES' if p['counter'] else 'no') if p['counter'] is not None else '—',
      ('YES' if p['pg_gate'] else 'no') if p['pg_gate'] is not None else '—',
      ('YES' if p['pg_exit'] else 'no') if p['pg_exit'] is not None else '—',
      '%.4f' % m['mae'] if m else '—', '%.4f' % m['mfe'] if m else '—',
      ('YES' if m['mae'] > m['mfe'] else '-') if m else '—')
     for r, w, m, p in OUT])

pg = [(r, w, m, p) for r, w, m, p in OUT if p['pg_gate']]
bad = [(r, w, m, p) for r, w, m, p in OUT if m and m['mae'] > m['mfe']]
print('\n- PEGGED to the gate: %d of %d — %s'
      % (len(pg), len(OUT), ', '.join(SC.U(r['a']) for r, w, m, p in pg) or 'none'))
print('- of the %d pegged, %d have MAE > MFE'
      % (len(pg), sum(1 for r, w, m, p in pg if m and m['mae'] > m['mfe'])))
print('- of the %d with MAE > MFE, %d are pegged'
      % (len(bad), sum(1 for r, w, m, p in bad if p['pg_gate'])))
print('- counter-dr last visit (without the 50 test): %d of %d'
      % (sum(1 for r, w, m, p in OUT if p['counter']), len(OUT)))
