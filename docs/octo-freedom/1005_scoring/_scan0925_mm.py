"""09-25: the walked event timestamps per ws12r oob>6min run, and the resulting MAE/MFE. 1007.

Joe 1007: *"I only need to see the timestamps of the walked events, per oob>6, and the resulting
maemfe. from there, we can dive deeper on the exits that are MAE > MFE"*.

ONE exit rule only - the mech as ruled: the first r reversal after the dip confirm carrying a
divergence on ws1r OR ws2r, with x under r at that bar. The xwob-held variant and the
swing-to-pivot variant are in _scan0925.py and are not repeated here.

MAE/MFE run from the GATE BAR to the exit. Branch 1 gave a real open on only 3 of the 11 runs, so
on the other 8 the gate bar is a stand-in - said once here, not per row.

Knobs from ws12_baton_config v1.
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
MAE_STOP = float(W['mae_stop_pct'])
DIV_TFS = [int(s.strip().replace('ws', '').replace('r', '')) for s in W['div_lines'].split(',')]
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
R12 = SC.LD(TRIG_TF * 60, 'r')[:N]; X12 = SC.LD(TRIG_TF * 60, 'x')[:N]
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
    o = dict(gate=a + GATE_BARS + 1, sig=None, dip=None, conf=None, exit=None, tf=None)
    u = lambda k: float(X12[k]) < float(R12[k])
    for k in range(a + 1, min(b, a + SIG_WIN) + 1):
        if (u(k) and not u(k - 1)) if d > 0 else ((not u(k)) and u(k - 1)):
            o['sig'] = k; break
    for k in range(o['gate'], d1 + 1):
        if indip(k, d) and not indip(k - 1, d):
            n = 0
            while k + n <= N - 1 and indip(k + n, d):
                n += 1
            if n > DIP_DWELL:
                o['dip'], o['conf'] = k, k + DIP_DWELL - 1
                break
    if o['conf'] is None:
        return o
    for k in range(o['conf'] + 1, d1 + 1):
        for t in DIV_TFS:
            if REV[t][k] != WANT(d) or not xund(t, k, d): continue
            af = anchor_floater(R[t], PX, d, k)
            if af is None or int(af['fired']) == 0: continue
            o['exit'], o['tf'] = k, t
            return o
    return o

def mm(s, e, dd):
    seg = PX[s:e + 1]; idx = np.arange(s, e + 1)
    ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
    if seg.size == 0: return None
    p = float(PX[s])
    f = int(seg.argmax()) if dd > 0 else int(seg.argmin())
    g = int(seg.argmin()) if dd > 0 else int(seg.argmax())
    return dict(mfe=(float(seg[f]) - p) / p * 100.0 * dd, mfe_bar=int(idx[f]),
                mae=max(0.0, -((float(seg[g]) - p) / p * 100.0 * dd)), mae_bar=int(idx[g]),
                real=(float(PX[e]) - p) / p * 100.0 * dd)

OUT = []
for r in RUNS:
    w = walk(r)
    m = mm(w['gate'], w['exit'], r['dr']) if w['exit'] else None
    OUT.append((r, w, m))
    print('\n## oob from %s   dr %+d' % (SC.U(r['a']), r['dr']))
    st = [('ws12r oob from', r['a']), ('ws12r oob to', r['b']), ('gate bar', w['gate']),
          ('branch 1 cross', w['sig']), ('50 dip', w['dip']), ('dip confirmed', w['conf']),
          ('EXIT on ws%dr' % w['tf'] if w['tf'] else 'EXIT', w['exit'])]
    box(('walked event', 'ts'),
        [(lbl, SC.U(k) if k is not None else '—') for lbl, k in st])
    if m:
        box(('MAE%', 'MAE ts', 'MFE%', 'MFE ts', 'MFE/MAE', 'realised', 'hold min'),
            [['%.4f' % m['mae'], SC.U(m['mae_bar']), '%.4f' % m['mfe'], SC.U(m['mfe_bar']),
              ('%.2f' % (m['mfe'] / m['mae'])) if m['mae'] > 0 else 'inf',
              '%+.4f' % m['real'],
              '%.1f' % ((int(SC.ts[w['exit']]) - int(SC.ts[w['gate']])) / 60000.0)]])
    else:
        print('- no exit before the day end')

print('\n# ALL %d RUNS, ONE ROW EACH' % len(OUT))
box(('oob from', 'dr', 'gate', 'branch 1', '50 dip', 'confirm', 'exit', 'on', 'MAE%', 'MFE%',
     'MFE/MAE', 'realised', 'MAE > MFE?'),
    [(SC.U(r['a']), '%+d' % r['dr'], SC.U(w['gate']),
      SC.U(w['sig']) if w['sig'] else '—', SC.U(w['dip']) if w['dip'] else '—',
      SC.U(w['conf']) if w['conf'] else '—', SC.U(w['exit']) if w['exit'] else '—',
      ('ws%dr' % w['tf']) if w['tf'] else '—',
      '%.4f' % m['mae'] if m else '—', '%.4f' % m['mfe'] if m else '—',
      (('%.2f' % (m['mfe'] / m['mae'])) if m['mae'] > 0 else 'inf') if m else '—',
      '%+.4f' % m['real'] if m else '—',
      ('YES' if m['mae'] > m['mfe'] else '-') if m else '—')
     for r, w, m in OUT])
bad = [(r, w, m) for r, w, m in OUT if m and m['mae'] > m['mfe']]
print('\n- %d of %d runs have MAE > MFE: %s'
      % (len(bad), len(OUT), ', '.join(SC.U(r['a']) for r, w, m in bad) or 'none'))
print('- %d runs breach the %.2f stop inside the window: %s'
      % (sum(1 for r, w, m in OUT if m and m['mae'] > MAE_STOP), MAE_STOP,
         ', '.join(SC.U(r['a']) for r, w, m in OUT if m and m['mae'] > MAE_STOP) or 'none'))
print('- MAE/MFE run from the GATE bar. Branch 1 gave a real open on only %d of %d runs.'
      % (sum(1 for r, w, m in OUT if w['sig']), len(OUT)))
