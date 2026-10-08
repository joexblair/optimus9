"""THE NEVER-ARMED LEGS' LINE STATE AT THEIR OPENS. 09-25 + 09-26, option A. 1007.

Joe 1007 asked for the line state at the opens, plus three measures:
  1  *"at what higher TF (to ws30) do the r lines stop printing oob or ex-fence"*
  2  *"at which TF do the wsf Mages begin to peg (ie Mage has not crossed into counter-dr ex-fence
     before returning to dr ex-fence). eg 10:56(open), ws3MAge did not cross into low ex-fence when
     ws2Mage and ws1Mage both crossed into low ex-fence at ~10:06. 'ws3' is the answer I want for
     the 10:56 open"*
  3  *"note the trajectory of ws7r to ws11r, and tell me if they left their last ex-fence in a
     matryoshaic way. compare the angles and force of the 'leaving ex-fence' moves against the
     trades that didn't stop"*

THE FENCES: oob is oob_hi/oob_lo 85/15. The EX-FENCE is 100-momo_fence_r / momo_fence_r = 83/17.

MY CODINGS, each stated so it can be corrected:

  (1) scanning ws1..ws30 upward, the STOP TF is the first TF whose r is neither oob nor ex-fence on
      the side being read. Gaps are real, so the HIGHEST TF that still is, is reported beside it.
      Reported on BOTH frames - the LEG's own side and the TAPE's dr at the open - because Joe did
      not name one and the mech's arm reads the leg's side.

  (2) PEGGING, read on the TAPE's dr at the open, because Joe's sentence says "counter-dr" and his
      worked example has ws1/ws2 reaching the LOW ex-fence as the counter move.
        dr-ex-fence        >= 83 at dr +1, <= 17 at dr -1
        counter-ex-fence   <= 17 at dr +1, >= 83 at dr -1
        pegged(t)          the Mage's most recent dr-ex-fence visit at or before the open is `b1`;
                           the previous DISTINCT dr-ex-fence visit before it is `b0`; pegged when
                           NO counter-ex-fence bar lies in (b0, b1).
        the answer         the LOWEST pegged TF.
      SELF-CHECK: this must return ws3 for the 10:56:40 open. If it does not, the coding is wrong
      and the raw ws1/ws2/ws3 Mage paths are printed below so Joe can adjudicate.

  (3) THE LEAVE MOVE, cap-free. For each of ws7r..ws11r: `fb` is the most recent bar at or before
      the open where r was at an ex-fence (either side); the leave bar is fb + 1; the move runs from
      fb until r reaches its extreme in the leaving direction and turns back. No window is imposed -
      the turn ends the move, not a knob.
        force   |r at the extreme - r at fb|, in r-points
        angle   force / minutes elapsed, in r-points per minute
        matryoshka  are the leave bars in INCREASING TF order across ws7..ws11? Joe 0824: *"a lower
                    TF r line will always stall or curl before the higher TFs"*.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, MAE_STOP = C.SC, C.PX, C.box, C.MAE_STOP
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
RR = {t: SC.LD(t * 60, 'r')[:N] for t in range(1, 31)}
MM = {t: SC.LD(t * 60, 'Mage')[:N] for t in range(1, 31)}
M2 = C.M2
HI, LO = SC.HI, SC.LO
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
XWOB = int(C.W['x_rev_xwob'])
R1, X1 = C.R[1], C.X[1]
K = lambda d, t: SC.K('%s %s' % (d, t))
LAST_OPEN = K('2026-09-26', '23:59:55')
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')

below = (X1 < R1) & np.isfinite(X1) & np.isfinite(R1)
idx = np.arange(N)
ar = (idx + 1) - np.maximum.accumulate(np.where(below, 0, idx + 1))
heldm = ar >= XWOB
RETURNS = [(int(c) - (XWOB - 1), int(c)) for c in np.flatnonzero(heldm & ~np.r_[False, heldm[:-1]])
           if int(c) - (XWOB - 1) >= 1]
gate_A = lambda rb, cf: (float(R1[rb]) <= EXF_LO
                         and float(MM[30 if False else SC.TF[-1]][cf]) > float(MM[1][cf]))

def find_reentry(stop_bar):
    for rb, cf in RETURNS:
        if cf <= stop_bar: continue
        if cf > LAST_OPEN: return None
        if gate_A(rb, cf): return cf
    return None

LEGS = []
k, d, seg_n, n = K('2026-09-25', '02:48:50'), +1, 0, 0
while True:
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    n += 1; seg_n += 1
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    LEGS.append(dict(leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, d=d, why=why,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
    if why == 'mae breach' or (seg_n == 7 and n == 7):
        cf = find_reentry(xk)
        if cf is None: break
        k, d, seg_n = cf, +1, 0
        continue
    if xk >= LAST_OPEN: break
    k = xk; d = -d

STOPPED = [L for L in LEGS if L['why'] == 'mae breach']
ARMED = [L for L in LEGS if L['why'] != 'mae breach']
print('# option A: %d legs, %d stopped (never armed), %d armed' % (len(LEGS), len(STOPPED), len(ARMED)))

# ---- (1) the r-ladder stop TF
def rstop(k, side):
    """side +1 reads the hi fences, -1 the lo. -> (first TF not oob/exf, highest TF that is)."""
    ok = lambda t: ((float(RR[t][k]) >= EXF_HI) if side > 0 else (float(RR[t][k]) <= EXF_LO))
    first = None; high = None
    for t in range(1, 31):
        if ok(t):
            high = t
        elif first is None:
            first = t
    return first, high

# ---- (2) pegging, CORRECTED. The first coding found the previous dr-ex-fence BAR and was
# degenerate: ws1Mage chatters across its fence so two "visits" sat 10 s apart and the test was
# vacuous. It returned ws1 on 11 of 12 legs and failed Joe's self-check (he says ws3 for 10:56:40).
#
# JOE'S SENTENCE ANCHORS IT: *"ws3MAge did not cross into low ex-fence when ws2Mage and ws1Mage both
# crossed into low ex-fence at ~10:06"*. That shared crossing IS the anchor, and ws1 defines it
# because the matryoshka order makes the lowest TF the one that leads.
#   anchor      ws1Mage's most recent COUNTER-dr ex-fence bar at or before the open
#   pegged(t)   ws{t}Mage has NO counter-dr ex-fence bar in [anchor, open]
#   the answer  the LOWEST pegged TF
# Knob-free. Reproduces ws3 at 10:56:40 - verified in _peg2.py.
def pegged_tf(k, dr):
    ctf = (lambda v: v <= EXF_LO) if dr > 0 else (lambda v: v >= EXF_HI)
    anc = None
    for j in range(k, max(0, k - 34560) - 1, -1):
        v = float(MM[1][j])
        if np.isfinite(v) and ctf(v): anc = j; break
    if anc is None:
        return None, [], None
    det = []
    for t in range(1, 31):
        hits = [j for j in range(anc, k + 1) if np.isfinite(MM[t][j]) and ctf(float(MM[t][j]))]
        det.append((t, len(hits), SC.U(hits[0]) if hits else '-',
                    'crossed' if hits else 'PEGGED'))
    pg = [t for t, n_, f, st in det if st == 'PEGGED']
    return (pg[0] if pg else None), det, anc

# ---- (3) the leave move on ws7r..ws11r
def leave(k, t):
    """-> (fence bar, leave bar, side, force, minutes, angle) or None."""
    r = RR[t]
    fb = None; fs = 0
    for j in range(k, max(0, k - 34560) - 1, -1):
        v = float(r[j])
        if not np.isfinite(v): continue
        if v >= EXF_HI: fb, fs = j, +1; break
        if v <= EXF_LO: fb, fs = j, -1; break
    if fb is None or fb >= N - 2: return None
    lb = fb + 1
    best = float(r[fb]); bj = fb
    j = lb
    while j <= min(N - 1, k):
        v = float(r[j])
        if np.isfinite(v):
            if (v < best) if fs > 0 else (v > best):
                best, bj = v, j
            elif (v - best) > 2.0 if fs > 0 else (best - v) > 2.0:
                break                      # turned back by more than 2 r-points: the move ended
        j += 1
    mins = (int(SC.ts[bj]) - int(SC.ts[fb])) / 60000.0
    force = abs(best - float(r[fb]))
    if mins <= 0:
        return None          # the extreme IS the fence bar: there is no move to measure
    return (fb, lb, fs, force, mins, force / mins)

print('\n# THE 10:56:40 SELF-CHECK — Joe says the answer is ws3')
k56 = K('2026-09-25', '10:56:40')
p56, det56, anc56 = pegged_tf(k56, int(DRv[k56]))
print('- dr at 10:56:40 is %+d, so the dr ex-fence is %s' % (int(DRv[k56]),
      'HIGH >= %.0f' % EXF_HI if int(DRv[k56]) > 0 else 'LOW <= %.0f' % EXF_LO))
print('- my coding returns: %s' % ('ws%d' % p56 if p56 else 'no pegged TF'))
print('- anchor = ws1Mage\'s most recent counter-dr ex-fence bar: %s'
      % (SC.U(anc56) if anc56 else '—'))
box(('TF', 'counter-ex-fence bars in [anchor, open]', 'first one', 'verdict'),
    [('ws%d' % t, str(n_), f, st) for t, n_, f, st in det56[:8]])

print('\n# THE NEVER-ARMED LEGS AT THEIR OPENS')
rows = []
for L in STOPPED:
    k = L['open']; dr = int(DRv[k]); d = L['d']
    f_leg, h_leg = rstop(k, d)
    f_dr, h_dr = rstop(k, dr)
    pg, _, _anc = pegged_tf(k, dr)
    rows.append((DAYOF(k)[5:], L['side'], SC.U(k), '%+d' % dr,
                 '%.2f' % float(M2[k]),
                 '%.1f' % (float(M2[k]) - HI if d > 0 else LO - float(M2[k])),
                 '%.2f' % float(RR[1][k]), '%.2f' % float(RR[12][k]),
                 ('ws%d' % f_leg) if f_leg else 'none', ('ws%d' % h_leg) if h_leg else 'none',
                 ('ws%d' % f_dr) if f_dr else 'none', ('ws%d' % h_dr) if h_dr else 'none',
                 ('ws%d' % pg) if pg else 'none'))
box(('day', 'side', 'open', 'dr', 'ws2Mage', 'ws2Mage to its arm fence', 'ws1r', 'ws12r',
     'r stops at (leg side)', 'highest still (leg)', 'r stops at (tape dr)', 'highest still (dr)',
     'Mages peg at'), rows)
print('- `Mages peg at` is ws1-anchored and knob-free; it reproduces Joe\'s ws3 at 10:56:40.')

print('\n# ws7r TO ws11r — THE LEAVE MOVE, NEVER-ARMED LEGS')
rows = []
for L in STOPPED:
    k = L['open']
    lv = {t: leave(k, t) for t in range(7, 12)}
    bars = [(t, lv[t][0]) for t in range(7, 12) if lv[t]]
    mat = 'YES' if bars == sorted(bars, key=lambda z: z[1]) and len(bars) > 1 else 'no'
    for t in range(7, 12):
        z = lv[t]
        rows.append((DAYOF(k)[5:] + ' ' + SC.U(k), 'ws%dr' % t,
                     SC.U(z[0]) if z else '—',
                     ('hi' if z[2] > 0 else 'lo') if z else '—',
                     '%.2f' % float(RR[t][z[0]]) if z else '—',
                     '%.2f' % z[3] if z else '—', '%.1f' % z[4] if z else '—',
                     '%.3f' % z[5] if z else '—',
                     mat if t == 7 else ''))
box(('leg open', 'line', 'last ex-fence bar', 'side', 'r at the fence', 'force r-pts',
     'minutes', 'angle r-pts/min', 'matryoshka ws7->ws11'), rows)

print('\n# THE SAME, ARMED LEGS (the trades that did not stop)')
rows = []
for L in ARMED:
    k = L['open']
    lv = {t: leave(k, t) for t in range(7, 12)}
    bars = [(t, lv[t][0]) for t in range(7, 12) if lv[t]]
    mat = 'YES' if bars == sorted(bars, key=lambda z: z[1]) and len(bars) > 1 else 'no'
    fo = [lv[t][3] for t in range(7, 12) if lv[t]]
    an = [lv[t][5] for t in range(7, 12) if lv[t]]
    rows.append((DAYOF(k)[5:], L['side'], SC.U(k), L['why'], '%+.4f' % L['real'],
                 mat, str(len(fo)),
                 '%.2f' % (sum(fo) / len(fo)) if fo else '—',
                 '%.3f' % (sum(an) / len(an)) if an else '—'))
box(('day', 'side', 'open', 'why it exited', 'realised', 'matryoshka', 'lines with a move',
     'mean force', 'mean angle'), rows)

print('\n# THE COMPARISON')
def agg(pop):
    fo = []; an = []; mats = 0; tot = 0
    for L in pop:
        k = L['open']
        lv = {t: leave(k, t) for t in range(7, 12)}
        bars = [(t, lv[t][0]) for t in range(7, 12) if lv[t]]
        if len(bars) > 1:
            tot += 1
            if bars == sorted(bars, key=lambda z: z[1]): mats += 1
        fo += [lv[t][3] for t in range(7, 12) if lv[t]]
        an += [lv[t][5] for t in range(7, 12) if lv[t]]
    fo = [v for v in fo if np.isfinite(v)]; an = [v for v in an if np.isfinite(v)]
    md = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
    return dict(n=len(pop), mats=mats, tot=tot, fo_med=md(fo), fo_mean=sum(fo) / len(fo) if fo else 0,
                an_med=md(an), an_mean=sum(an) / len(an) if an else 0, nlines=len(fo),
                nomove=len(pop) * 5 - len(fo))
A_, B_ = agg(STOPPED), agg(ARMED)
box(('population', 'legs', 'matryoshka ws7->ws11', 'lines with a move', 'lines with none',
     'force med', 'force mean', 'angle med', 'angle mean'),
    [('never armed (stopped)', str(A_['n']), '%d of %d' % (A_['mats'], A_['tot']),
      str(A_['nlines']), str(A_['nomove']), '%.2f' % A_['fo_med'], '%.2f' % A_['fo_mean'],
      '%.3f' % A_['an_med'], '%.3f' % A_['an_mean']),
     ('armed (did not stop)', str(B_['n']), '%d of %d' % (B_['mats'], B_['tot']),
      str(B_['nlines']), str(B_['nomove']), '%.2f' % B_['fo_med'], '%.2f' % B_['fo_mean'],
      '%.3f' % B_['an_med'], '%.3f' % B_['an_mean'])])
print('\n- the leave move ends when r turns back more than 2.00 r-points. That 2.00 is MINE and the')
print('  only knob in measure (3) - it is a turn detector, not a window.')
