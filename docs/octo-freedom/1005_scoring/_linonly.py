"""THE LINEAGE WALK ALONE, CEILING 30. 1009.

Joe 1009: *"if we set _CEIL 30 so that ws12r is allowed to pass the baton up per lineages mechs
... where does lineage stop walking"* / *"this is lineage walk only. the other mechs around ws12r
are disabled"*.

RUNNING: arm on ws2Mage crossing into oob, KICKSTART on the highest oob TF at or under the ceiling,
then the baton to an oob TF within lin_hop 2, exit on `final stalled`.

DISABLED: the >ws12 oob handover, the ws12r exhaustion, the ws1Mage dip + ws1r/ws2r divergence exit,
the walk's x-cross exit (Joe 1009 dropped it), and the MAE stop - the question is where LINEAGE
stops, and the stop would truncate the answer. Stated because it is a choice.

THE X-CROSS ROWS, Joe 1009: *"insert a row for each first x-cross, xwob 48, for each baton holder"*.

  THE TARGET IS THE RIDER'S OWN r. Joe 1009 on ws12: *"if ws12x crosses ws12r during the dwell"*, and
  Joe 0918: *"after I sent that, I remember that we're only crossing r, so my statement was a
  misnomer"*. The BANKED walk exit crosses ws{h}x against ws{h+1}b instead (`x_tgt_role` b,
  `x_tgt_tfs` next) - a DIFFERENT target, not run here. Stated because it is a choice.

  THE HOLD RUNS PAST THE TENURE. `X_XWOB` 48 bars = 4.0 min. A rider can hold the baton for 1 bar,
  so requiring the 48-bar hold to finish inside the tenure would make most riders impossible. The
  cross must land inside the tenure; the hold is then measured forward with no window. Stated.

  ALREADY-ACROSS COUNTS. Joe 1009: *"I took any squashed cross inside the run, edge or already
  standing"* / *"more hits are better than less"*. If x is already across r on the bar the baton
  arrives, that is the row, labelled `already across`.

  THE ROW IS STAMPED AT THE CONFIRMATION BAR, cross + 47, the first bar the 48-bar hold is knowable.
  Same stamp as `ws_strat.candidates` (conf = cross + xwob - 1) and `build_s46_event.sx_series`.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
CEIL = int(os.environ.get('X_CEIL', 30))
RL, ST = {}, {}
for t in range(1, CEIL + 1):
    try:
        RL[t] = np.asarray(SC.LD(t * 60, 'r'), float)[:N]
    except Exception as e:
        print('# ws%dr did not load: %s' % (t, str(e)[:60]), flush=True)
TFS = sorted(RL)
# the stall mask the same way _chain10.py:285-291 builds it - the step and sample count come
# from each TF's OWN momo window, so they cannot be guessed.
from optimus9.analysis.jig import stall_mask
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_config, momo_bank
from optimus9.compute.momo_gated import momo_window
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
_db = DatabaseManager(**get_db_config()); _db.connect()
BK = {}
for t in TFS:
    try: BK[t] = momo_bank(_db, t)
    except Exception as e: print('# ws%d has no momo bank: %s' % (t, str(e)[:50]), flush=True)
_db.disconnect()
TFS = [t for t in TFS if t in BK]
for t in TFS:
    with momo_config(BK[t]):
        with momo_window(int(BK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for d in (+1, -1):
        ST[(t, d)] = stall_mask(RL[t], d, int(SC.LG['stall_n']), s_, n_)
print('# TAPE %d bars, end %s' % (N, os.environ.get('LG_TAPE_END', '2026-10-04 (DEFAULT)')), flush=True)
print('# lines ws%d-ws%d loaded. ceiling %d, lin_hop %d, baton passes on OOB (W_PASS %r), '
      'stall_n %s' % (TFS[0], TFS[-1], CEIL, C.LIN_HOP, C.PASS, SC.LG['stall_n']), flush=True)
XW = int(os.environ.get('X_XWOB', 48))
XL = {}
for t in TFS:
    try: XL[t] = np.asarray(SC.LD(t * 60, 'x'), float)[:N]
    except Exception as e: print('# ws%dx did not load: %s' % (t, str(e)[:60]), flush=True)
print('# x-cross rows: ws{h}x vs its OWN ws{h}r, xwob %d bars = %.1f min, %d x lines'
      % (XW, XW * 5 / 60.0, len(XL)), flush=True)
M2 = np.asarray(SC.Mg[2], float)[:N]
HI, LO = SC.HI, SC.LO
oob = lambda t, j, d: (float(RL[t][j]) >= HI) if d > 0 else (float(RL[t][j]) <= LO)
OPEN = os.environ.get('X_OPEN', '2026-07-15 03:13:15')
DR = int(os.environ.get('X_DR', -1))
k0 = SC.K(OPEN); d = DR
p0 = float(PX[k0]); sg = 1 if d > 0 else -1
pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sg)
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k0])) / 60000.0)
rows = [(k0, 'OPEN %s' % ('LONG' if d > 0 else 'SHORT'), '—')]
hold = []                      # (bar, rider) each time the baton moves — the tenure boundaries
armed = False; rider = None; stop = None
for j in range(k0 + 1, N):
    if not armed:
        if (d > 0 and float(M2[j]) >= HI and float(M2[j - 1]) < HI) or \
           (d < 0 and float(M2[j]) <= LO and float(M2[j - 1]) > LO):
            armed = True
            rows.append((j, 'exit-armed — ws2Mage %s %.0f (%.2f)'
                         % ('over' if d > 0 else 'under', HI if d > 0 else LO, float(M2[j])), '—'))
        continue
    if rider is None:
        c = [t for t in TFS if t <= CEIL and oob(t, j, d)]
        if c:
            rider = max(c)
            rows.append((j, 'KICKSTART — rider ws%d (r %.2f oob)'
                         % (rider, float(RL[rider][j])), 'ws%d' % rider))
            hold.append((j, rider))
        continue
    cand = [t for t in range(rider + 1, min(rider + C.LIN_HOP, CEIL) + 1)
            if t in RL and oob(t, j, d)]
    if cand:
        rider = max(cand)
        rows.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(RL[rider][j])),
                     'ws%d' % rider))
        hold.append((j, rider))
        continue
    if ST[(rider, d)][j]:
        rows.append((j, 'final stalled on ws%d (r %.2f)' % (rider, float(RL[rider][j])),
                     'ws%d' % rider))
        stop = j
        break
# ---- the first confirmed x-cross per baton holder
acr = lambda t, j: (float(XL[t][j]) < float(RL[t][j])) if d > 0 else (float(XL[t][j]) > float(RL[t][j]))
end = stop if stop is not None else N - 1
XROWS = []
for i, (ja, t) in enumerate(hold):
    jb = (hold[i + 1][0] - 1) if i + 1 < len(hold) else end
    if t not in XL:
        XROWS.append((ja, 'ws%dx did not load — no x-cross row' % t, 'ws%d' % t)); continue
    fails, got = 0, False
    for j in range(ja, jb + 1):
        standing = (j == ja and acr(t, j))
        if not (standing or (j > ja and acr(t, j) and not acr(t, j - 1))):
            continue
        k = j
        while k < N and acr(t, k):
            k += 1
        run = k - j
        if run >= XW:
            XROWS.append((j + XW - 1,
                          'first ws%dx cross %s ws%dr%s — crossed %s, held %d bars (%.1f min)%s'
                          % (t, 'under' if d > 0 else 'over', t,
                             ' (already across at the handover)' if standing else '',
                             U(j), run, run * 5 / 60.0,
                             '' if not fails else ' | %d earlier cross(es) failed the hold' % fails),
                          'ws%d' % t))
            got = True
            break
        fails += 1
    if not got:
        XROWS.append((jb, 'ws%d held the baton %s->%s, %d bars: no x-cross held %d bars'
                      ' (%d cross(es) tried)' % (t, U(ja), U(jb), jb - ja + 1, XW, fails),
                      'ws%d' % t))
print('\n# the lineage walk from %s %s, ceiling %d — x-cross rows at xwob %d'
      % (OPEN, 'LONG' if d > 0 else 'SHORT', CEIL, XW))
allr = sorted(rows + XROWS, key=lambda r: r[0])
box(('ts', '+min', 'event', 'pxs', 'pct', 'the rider'),
    [(U(j), mn(j), txt, '%.6f' % float(PX[j]), pct(j), rd) for j, txt, rd in allr])
if stop is None:
    print('- the walk never stalled before the tape end')
else:
    seg = np.asarray(PX[k0:stop + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sg, np.nan)
    print('- LINEAGE STOPS AT %s, %.1f min after the open, on ws%d'
          % (U(stop), (int(SC.ts[stop]) - int(SC.ts[k0])) / 60000.0, rider))
    print('- realised %+.4f   MAE %.4f   MFE %.4f'
          % (float(rel[-1]), -float(np.nanmin(rel)), float(np.nanmax(rel))))
