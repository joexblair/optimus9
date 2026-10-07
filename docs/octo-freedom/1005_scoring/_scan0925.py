"""EVERY ws12r oob RUN > 6 MIN ON 09-25, AND THE >ws12 BATON MECH WALKED ON EACH. 1007.

Joe 1007: *"scan 09-25 and find all of the ws12r oob >6 minutes. walk the process and share what
you see"*.

EVERY KNOB IS READ FROM ws12_baton_config v1. Nothing here is hardcoded.

THREE THINGS I AM NOT DECIDING, each reported instead of chosen:

  A  WHICH SIDE IS WHICH dr. A hi-oob run (ws12r >= oob_hi) is walked as dr +1 and a lo-oob run
     (<= oob_lo) as dr -1, because the mech reads "over 85 for a LONG leg, under 15 for a SHORT
     one". That is IMPLIED by Joe's wording, not ruled by him.

  B  DOES THE MECH STAY ARMED AFTER ws12r LEAVES oob? Spec open question #1. Reading A keeps
     looking forward with no re-check (what _ws12mech.py did). Reading B requires the 50 dip to
     BEGIN at or before the run's last oob bar. Both are printed per run.

  C  DOES THE EXIT REQUIRE THE xwob-HELD x-CROSS? `x_rev_xwob` 8 was measured as the xwob that
     picks the cross that precedes a reversal, but Joe never ruled that the EXIT must use it. Leg 8
     was measured on a bare `x under r` at the reversal bar. Both are printed per run.

NO pct COLUMN FOR MOST RUNS, ON PURPOSE. Branch 1's cross is a trade signal, so it is an open bar;
branch 2's exit closes a leg opened elsewhere. Where there is no branch-1 cross there is no open,
so a percentage would be invented. The pxs at each bar is printed instead.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import anchor_floater
from optimus9.compute.spec_config import spec_config
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%6.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D = os.environ.get('W_DAY', '2026-09-25')
db = DatabaseManager(**get_db_config()); db.connect()
W = spec_config(db, 'ws12_baton_config'); db.disconnect()
GATE_BARS = int(W['oob_gate_bars'])
SIG_WIN = int(W['sig_window_bars'])
TRIG_TF = int(W['ceil_trig_tf'])
DIP_MID = float(W['dip_mid'])
DIP_DWELL = int(W['dip_dwell_bars'])
XWOB = int(W['x_rev_xwob'])
RREV = int(W['rrev_wob'])
DIV_TFS = [int(s.strip().replace('ws', '').replace('r', '')) for s in W['div_lines'].split(',')]
N = len(SC.ts)
_P('knobs %s: gate %d bars, dip dwell %d, xwob %d, rrev_wob %d, div lines %s'
   % (W.key(), GATE_BARS, DIP_DWELL, XWOB, RREV, DIV_TFS))
_P('tape %d bars, last %s' % (N, SC.U(N - 1)))

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

# ---- STEP 1: every ws12r oob run on 09-25, both sides
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
        RUNS.append(dict(side=side, dr=dd, a=a, b=k - 1, bars=k - a))
RUNS.sort(key=lambda r: r['a'])
LONG = [r for r in RUNS if (r['bars'] - 1) > GATE_BARS]
print('\n# STEP 1 — EVERY ws12r oob RUN ON %s (both fences), and which pass > %d bars'
      % (D, GATE_BARS))
box(('#', 'side', 'dr', 'oob from', 'to', 'bars', 'run min', 'ws12r at start', 'ws12r at end',
     '> %d bars?' % GATE_BARS),
    [(str(i + 1), r['side'], '%+d' % r['dr'], SC.U(r['a']), SC.U(r['b']), str(r['bars']),
      '%.1f' % ((int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0),
      '%.2f' % float(R12[r['a']]), '%.2f' % float(R12[r['b']]),
      'YES' if (r['bars'] - 1) > GATE_BARS else 'no')
     for i, r in enumerate(RUNS)])
print('- %d runs on the day, %d longer than %d bars (%.0f min)'
      % (len(RUNS), len(LONG), GATE_BARS, GATE_BARS * 5 / 60.0))

# ---- producers for the walk
def oobf(t, k, d): return (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
def xund(t, k, d):
    return (float(X[t][k]) < float(R[t][k])) if d > 0 else (float(X[t][k]) > float(R[t][k]))
def xheld(t, k, d, n):
    """x under r (for +dr) on every one of the n bars ending at k."""
    return all(xund(t, j, d) for j in range(max(0, k - n + 1), k + 1))
def indip(k, d): return (float(G1[k]) < DIP_MID) if d > 0 else (float(G1[k]) > DIP_MID)
WANT = lambda d: (-1 if d > 0 else +1)

def walk(r):
    """-> dict with every stage of the mech for one run."""
    a, b, d = r['a'], r['b'], r['dr']
    gate = a + GATE_BARS + 1
    out = dict(gate=gate, sig=None, dip=None, dip_bars=None, conf=None,
               exitA=None, exitA_tf=None, exitA_x=None, exitB=None, dip_in_run=None)
    # branch 1 — the counter-dr ws12x cross of ws12r inside the first SIG_WIN bars of oob
    u = lambda k: float(X12[k]) < float(R12[k])
    for k in range(a + 1, min(b, a + SIG_WIN) + 1):
        c = (u(k) and not u(k - 1)) if d > 0 else ((not u(k)) and u(k - 1))
        if c:
            out['sig'] = k; break
    # branch 2 — the first 50 dip at or after the gate with a run > DIP_DWELL
    for k in range(gate, d1 + 1):
        if indip(k, d) and not indip(k - 1, d):
            n = 0
            while k + n <= N - 1 and indip(k + n, d):
                n += 1
            if n > DIP_DWELL:
                out['dip'], out['dip_bars'] = k, n
                out['conf'] = k + DIP_DWELL - 1
                out['dip_in_run'] = (k <= b)
                break
    if out['conf'] is None:
        return out
    # the exit — the first r reversal after the confirm bar carrying a divergence, OR over the lines
    for k in range(out['conf'] + 1, d1 + 1):
        for t in DIV_TFS:
            if REV[t][k] != WANT(d): continue
            af = anchor_floater(R[t], PX, d, k)
            if af is None or int(af['fired']) == 0: continue
            if out['exitA'] is None and xund(t, k, d):
                out['exitA'], out['exitA_tf'] = k, t
            if out['exitB'] is None and xheld(t, k, d, XWOB):
                out['exitB'] = k
        if out['exitA'] is not None and out['exitB'] is not None:
            break
    return out

print('\n# STEP 2 — THE MECH WALKED ON EACH QUALIFYING RUN')
rows = []
WK = []
for i, r in enumerate(RUNS):
    if (r['bars'] - 1) <= GATE_BARS: continue
    w = walk(r); WK.append((r, w))
    rows.append((SC.U(r['a']), '%+d' % r['dr'],
                 '%.1f' % ((int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0),
                 SC.U(w['gate']),
                 SC.U(w['sig']) if w['sig'] else '—',
                 SC.U(w['dip']) if w['dip'] else '—',
                 str(w['dip_bars']) if w['dip_bars'] else '—',
                 ('%.1f' % ((int(SC.ts[w['dip']]) - int(SC.ts[r['b']])) / 60000.0))
                 if w['dip'] else '—',
                 ('in run' if w['dip_in_run'] else 'after run') if w['dip'] is not None else '—',
                 SC.U(w['conf']) if w['conf'] else '—',
                 SC.U(w['exitA']) if w['exitA'] else '—',
                 ('ws%dr' % w['exitA_tf']) if w['exitA_tf'] else '—',
                 SC.U(w['exitB']) if w['exitB'] else '—'))
box(('oob from', 'dr', 'run min', 'gate bar', 'branch 1 cross', 'dip bar', 'dip bars',
     'dip vs run end min', 'reading B', 'confirm bar', 'exit (bare x under r)', 'on',
     'exit (xwob %d held)' % XWOB), rows or [('—',) * 13])

print('\n# STEP 3 — THE LINE VALUES AT EACH STAGE')
for r, w in WK:
    print('\n## RUN FROM %s, dr %+d, %.1f min oob'
          % (SC.U(r['a']), r['dr'], (int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0))
    st = [('ws12r oob from', r['a']), ('ws12r oob to', r['b']), ('gate bar', w['gate'])]
    if w['sig']: st.append(('branch 1 cross', w['sig']))
    if w['dip']: st += [('50 dip', w['dip']), ('dip confirmed', w['conf'])]
    if w['exitA']: st.append(('EXIT bare x under r', w['exitA']))
    if w['exitB']: st.append(('EXIT xwob %d held' % XWOB, w['exitB']))
    box(('stage', 'ts', 'ws12r', 'ws12x', 'ws1Mage', 'ws1r', 'ws2r', 'pxs'),
        [(lbl, SC.U(k), '%.2f' % float(R12[k]), '%.2f' % float(X12[k]), '%.2f' % float(G1[k]),
          '%.2f' % float(R[1][k]), '%.2f' % float(R[2][k]), '%.6f' % float(PX[k]))
         for lbl, k in st if k is not None and k < N])

print('\n# STEP 4 — THE MOVE FROM THE GATE BAR TO EACH EXIT  (NOT a trade result)')
box(('oob from', 'dr', 'gate bar', 'pxs at gate', 'exit bare', 'pxs at exit', 'move pct on dr',
     'exit xwob', 'pxs at exit', 'move pct on dr'),
    [(SC.U(r['a']), '%+d' % r['dr'], SC.U(w['gate']), '%.6f' % float(PX[w['gate']]),
      SC.U(w['exitA']) if w['exitA'] else '—',
      '%.6f' % float(PX[w['exitA']]) if w['exitA'] else '—',
      ('%+.4f' % ((float(PX[w['exitA']]) - float(PX[w['gate']])) / float(PX[w['gate']])
                  * 100.0 * r['dr'])) if w['exitA'] else '—',
      SC.U(w['exitB']) if w['exitB'] else '—',
      '%.6f' % float(PX[w['exitB']]) if w['exitB'] else '—',
      ('%+.4f' % ((float(PX[w['exitB']]) - float(PX[w['gate']])) / float(PX[w['gate']])
                  * 100.0 * r['dr'])) if w['exitB'] else '—')
     for r, w in WK] or [('—',) * 10])
print('\n- the dr sign is applied so a +dr move up and a -dr move down both read positive')
print('- knob key %s' % W.key())

# ---- STEP 5: MAE and MFE. Joe 1007: *"I need to see MAE and MFE to understand the data"*
#
# TWO DIFFERENT STRETCHES, both printed, because conflating them inflated a figure 2.7x on 1007:
#   HOLDING WINDOW   the gate bar to the mech's own exit bar. What the mech actually delivers.
#   SWING-TO-PIVOT   score39.score(): the gate bar to the next FAVOURABLE pivot at the banked
#                    swing 1.25, NO STOP. The project's banked convention. Joe 1006: *"scoring
#                    comes from MAE and MFE. there is no other scoring"*.
#
# THE CONVENTION CLASH IS REAL AND HANDLED: score39.score() reads `d +1 = SHORT`, this scan reads
# dr +1 = the hi fence = up is favourable. So score() is called with -dr. Said out loud because
# getting it wrong silently flips every row.
#
# MAE is max(0, adverse) and MFE is the favourable excursion, both from the START bar, in the
# direction dr makes favourable. NO CAP IS APPLIED - `mae_stop_pct` 1.1 is reported as a flag only.
SWING = float(SC.LG['swing'])
HS, LS = SC.pivots(SWING)
MAE_STOP = float(W['mae_stop_pct'])

def mm(s, e, dd):
    """MAE / MFE over [s, e] in the direction dr makes favourable. -> dict."""
    seg = PX[s:e + 1]; idx = np.arange(s, e + 1)
    ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
    if seg.size == 0:
        return None
    p = float(PX[s])
    f = int(seg.argmax()) if dd > 0 else int(seg.argmin())
    a = int(seg.argmin()) if dd > 0 else int(seg.argmax())
    mfe = (float(seg[f]) - p) / p * 100.0 * dd
    mae = max(0.0, -((float(seg[a]) - p) / p * 100.0 * dd))
    return dict(mfe=mfe, mfe_bar=int(idx[f]), mae=mae, mae_bar=int(idx[a]),
                real=(float(PX[e]) - p) / p * 100.0 * dd)

print('\n# STEP 5a — MAE / MFE OVER THE HOLDING WINDOW: the gate bar to the mech\'s exit')
rows = []
for r, w in WK:
    for lbl, xk in (('bare x under r', w['exitA']), ('xwob %d held' % XWOB, w['exitB'])):
        if xk is None:
            rows.append((SC.U(r['a']), '%+d' % r['dr'], lbl, SC.U(w['gate']), '—', '—',
                         '—', '—', '—', '—', '—', '—', '—')); continue
        m = mm(w['gate'], xk, r['dr'])
        rows.append((SC.U(r['a']), '%+d' % r['dr'], lbl, SC.U(w['gate']), SC.U(xk),
                     '%.1f' % ((int(SC.ts[xk]) - int(SC.ts[w['gate']])) / 60000.0),
                     '%.4f' % m['mae'], SC.U(m['mae_bar']),
                     '%.4f' % m['mfe'], SC.U(m['mfe_bar']),
                     ('%.2f' % (m['mfe'] / m['mae'])) if m['mae'] > 0 else 'inf',
                     '%+.4f' % m['real'],
                     'BREACH' if m['mae'] > MAE_STOP else '-'))
box(('oob from', 'dr', 'exit rule', 'start (gate)', 'exit', 'hold min', 'MAE%', 'MAE ts',
     'MFE%', 'MFE ts', 'MFE/MAE', 'realised', 'vs stop %.2f' % MAE_STOP), rows)

print('\n# STEP 5b — MAE / MFE ON THE BANKED CONVENTION: score39.score, gate bar to the next')
print('#           favourable pivot at swing %.2f, NO STOP' % SWING)
rows = []
for r, w in WK:
    mfe, mae, pb = SC.score(w['gate'], -r['dr'], HS, LS)
    rows.append((SC.U(r['a']), '%+d' % r['dr'], SC.U(w['gate']),
                 SC.U(pb) if pb is not None else '—',
                 ('%.1f' % ((int(SC.ts[pb]) - int(SC.ts[w['gate']])) / 60000.0))
                 if pb is not None else '—',
                 '%.4f' % mae if mae is not None else '—',
                 '%.4f' % mfe if mfe is not None else '—',
                 ('%.2f' % (mfe / mae)) if (mae not in (None, 0) and mfe is not None)
                 else ('inf' if mae == 0 else '—'),
                 'BREACH' if (mae is not None and mae > MAE_STOP) else '-'))
box(('oob from', 'dr', 'start (gate)', 'pivot bar', 'stretch min', 'MAE%', 'MFE%', 'MFE/MAE',
     'vs stop %.2f' % MAE_STOP), rows)

print('\n# STEP 5c — THE SAME HOLDING WINDOW FROM BRANCH 1\'S CROSS, where one fired')
rows = []
for r, w in WK:
    if w['sig'] is None: continue
    for lbl, xk in (('bare x under r', w['exitA']), ('xwob %d held' % XWOB, w['exitB'])):
        if xk is None:
            rows.append((SC.U(r['a']), '%+d' % r['dr'], lbl, SC.U(w['sig']), '—', '—',
                         '—', '—', '—', '—', '—', '—')); continue
        m = mm(w['sig'], xk, r['dr'])
        rows.append((SC.U(r['a']), '%+d' % r['dr'], lbl, SC.U(w['sig']), SC.U(xk),
                     '%.1f' % ((int(SC.ts[xk]) - int(SC.ts[w['sig']])) / 60000.0),
                     '%.4f' % m['mae'], SC.U(m['mae_bar']),
                     '%.4f' % m['mfe'], SC.U(m['mfe_bar']),
                     ('%.2f' % (m['mfe'] / m['mae'])) if m['mae'] > 0 else 'inf',
                     '%+.4f' % m['real']))
box(('oob from', 'dr', 'exit rule', 'start (branch 1 cross)', 'exit', 'hold min', 'MAE%',
     'MAE ts', 'MFE%', 'MFE ts', 'MFE/MAE', 'realised'), rows or [('—',) * 12])
print('\n- swing %.2f, %d H and %d L pivots on the tape' % (SWING, HS.size, LS.size))
print('- score39.score was called with -dr: its own frame is d +1 = SHORT, this scan\'s is dr +1 = up')
