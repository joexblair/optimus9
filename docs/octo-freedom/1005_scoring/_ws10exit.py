"""THE ws10 EXIT + THE RE-ENTRY ROUTER AS THE WHOLE CHAIN. 1010.

Joe 1009: *"exit trades when ws10r is oob and ws10x crosses r. pick a wob that lands the exit
within +/-5 minutes of 04:30"* / *"open the next trade using the re-entry mech"*.

THE EXIT, as given:
  ws10r is oob on the LEG's side, AND ws10x crosses ws10r, AND the crossed side holds `wob` bars.
  The cross direction is the counter-side one: a SHORT leg rides the LOW oob, so ws10x crosses UP
  OVER ws10r; a LONG leg rides the HIGH oob, so ws10x crosses DOWN UNDER it.
  THE OOB IS READ AT THE CROSS BAR - that is the event Joe described. Whether ws10r is still oob at
  the confirmation bar is REPORTED, not required. STATED.
  THE EXIT IS STAMPED AT THE CONFIRMATION BAR, cross + wob - 1, the first bar the hold is knowable.
  Same stamp as `ws_strat.candidates` and the re-entry router's own conf.

THE OPEN: `_chain_2day.find_reentry` with `gate_A`, untouched - the banked re-entry router at
  `reent_xwob` 18. It chooses the bar AND the side, so this chain does not alternate.

WHAT IS NOT IN THIS BUILD, stated because each is a removal:
  the lineage walk has NO exit here - no arm, no KICKSTART, no baton, no stall, no x-cross. Joe's
  sentence names one exit and this is it, so the walk is not consulted. The >ws12r oob mech stays
  off. The MAE stop stays at its banked 2.50 - Joe has not dropped it.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
TF10 = int(os.environ.get('W_X_TF', 10))
R10 = np.asarray(SC.LD(TF10 * 60, 'r'), float)[:N]
X10 = np.asarray(SC.LD(TF10 * 60, 'x'), float)[:N]
HI, LO = SC.HI, SC.LO
print('# TAPE %d bars, end %s. ws%dr / ws%dx loaded. oob %.0f/%.0f, MAE stop %.2f, '
      'reent_xwob %d' % (N, os.environ.get('LG_TAPE_END', 'DEFAULT'), TF10, TF10, LO, HI,
                         C.MAE_STOP, T.XWOB), flush=True)

goob = lambda j, d: (float(R10[j]) >= HI) if d > 0 else (float(R10[j]) <= LO)
# the COUNTER-side cross: d>0 (riding high oob) -> x under r;  d<0 (low oob) -> x over r
acr = lambda j, d: (float(X10[j]) < float(R10[j])) if d > 0 else (float(X10[j]) > float(R10[j]))


def crosses(k0, d, k1=None):
    """every counter-side ws10x cross of ws10r after k0 with ws10r oob AT THE CROSS BAR.
    -> [(cross_bar, hold_run_bars)]   hold measured forward with no window."""
    k1 = N - 1 if k1 is None else k1
    out = []
    for j in range(k0 + 1, k1 + 1):
        if not (acr(j, d) and not acr(j - 1, d)):
            continue
        if not goob(j, d):
            continue
        k = j
        while k < N and acr(k, d):
            k += 1
        out.append((j, k - j))
    return out


def exit_at(k0, d, wob, k1=None):
    """the first confirmed ws10 exit at this wob. -> (conf_bar, cross_bar, hold) or (None,None,None)"""
    for j, run in crosses(k0, d, k1):
        if run >= wob and j + wob - 1 <= N - 1:
            return j + wob - 1, j, run
    return None, None, None


# ---------------------------------------------------------------- PART A: pick the wob
OPEN = os.environ.get('X_OPEN', '2026-07-15 03:13:15')
DR = int(os.environ.get('X_DR', -1))
k0 = SC.K(OPEN); d = DR
TGT = os.environ.get('X_TARGET', '2026-07-15 04:30:00')
TOL_MIN = float(os.environ.get('X_TOL_MIN', 5.0))
kt = SC.K(TGT)
lo_b = kt - int(TOL_MIN * 60 / 5); hi_b = kt + int(TOL_MIN * 60 / 5)
cx = crosses(k0, d)
print('\n# every counter-side ws%dx cross of ws%dr with ws%dr oob, from %s %s'
      % (TF10, TF10, TF10, OPEN, 'LONG' if d > 0 else 'SHORT'))
box(('#', 'cross ts', '+min', 'ws%dx' % TF10, 'ws%dr' % TF10, 'hold (bars)', '= min'),
    [(str(i + 1), U(j), '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k0])) / 60000.0),
      '%.2f' % float(X10[j]), '%.2f' % float(R10[j]), str(run), '%.1f' % (run * 5 / 60.0))
     for i, (j, run) in enumerate(cx[:40])])
print('- %d crosses in total; the table shows the first %d.' % (len(cx), min(40, len(cx))))

rows = []; good = []
seen = None
for wob in range(1, 601):
    cf, cr, run = exit_at(k0, d, wob)
    if cf is None:
        rows.append((str(wob), '—', '—', '—', '—', '—', 'no cross holds this long')); break
    key = (cr, cf)
    if key == seen:
        continue
    seen = key
    off = (int(SC.ts[cf]) - int(SC.ts[kt])) / 60000.0
    inw = lo_b <= cf <= hi_b
    if inw: good.append(wob)
    rows.append((str(wob), U(cr), U(cf), '%.1f' % (wob * 5 / 60.0), '%+.1f' % off,
                 '%.2f' % float(R10[cf]), 'IN THE WINDOW' if inw else ''))
print('\n# the exit each wob produces on this leg. target %s +/- %.0f min = %s to %s'
      % (TGT.split()[1], TOL_MIN, U(lo_b), U(hi_b)))
box(('wob', 'cross ts', 'EXIT ts (conf)', 'wob min', 'vs target min', 'ws%dr at exit' % TF10,
     'note'), rows)
if good:
    g0, g1 = min(good), max(good)
    print('- WOB %d to %d land the exit in the window. The lowest is %d = %.1f min of hold.'
          % (g0, g1, g0, g0 * 5 / 60.0))
else:
    print('- NO wob lands the exit in the window.')

# ---------------------------------------------------------------- PART B: the chain
WOB = int(os.environ.get('W_X10_WOB', good[0] if good else 0))
if WOB <= 0:
    print('\n- no wob to run the chain with. PART B skipped.')
    sys.exit(0)
print('\n# THE CHAIN — ws%d exit at wob %d (%.1f min), opens by the re-entry router (gate A)'
      % (TF10, WOB, WOB * 5 / 60.0))
LAST = N - 1
k, dd, legs = k0, d, []
while True:
    cf, cr, run = exit_at(k, dd, WOB)
    # the MAE stop, banked 2.50, measured bar by bar up to whichever comes first
    p0 = float(PX[k]); sg = 1 if dd > 0 else -1
    stop = None; mx = 0.0
    end = cf if cf is not None else LAST
    for j in range(k + 1, end + 1):
        px = float(PX[j])
        if not (np.isfinite(px) and px > 0): continue
        adv = -((px - p0) / p0 * 100.0 * sg)
        if adv > mx: mx = adv
        if adv > C.MAE_STOP: stop = j; break
    if stop is not None:
        xk, why = stop, 'mae breach'
    elif cf is not None:
        xk, why = cf, 'ws%d exit (cross %s, held %d)' % (TF10, U(cr), run)
    else:
        legs.append(dict(open=k, d=dd, exit=None, why='no ws%d exit before the tape end' % TF10))
        break
    legs.append(dict(open=k, d=dd, exit=xk, why=why,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sg, mae=mx,
                     cross=cr if why.startswith('ws') else None))
    rb, nf, sd = T.find_reentry(xk, T.gate_A, LAST)
    if nf is None:
        legs[-1]['reent'] = None; break
    legs[-1]['reent'] = (rb, nf, sd)
    if len(legs) >= int(os.environ.get('X_NLEG', 8)): break
    k, dd = nf, sd

out = []
for i, L in enumerate(legs):
    out.append((str(i + 1), 'LONG' if L['d'] > 0 else 'SHORT', U(L['open']),
                U(L['exit']) if L['exit'] is not None else '—',
                '%.1f' % ((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0)
                if L['exit'] is not None else '—',
                '%.4f' % L.get('mae', 0.0), '%+.4f' % L.get('real', 0.0), L['why'],
                ('re-entry %s -> opens %s %s' % (U(L['reent'][0]), U(L['reent'][1]),
                                                 'LONG' if L['reent'][2] > 0 else 'SHORT'))
                if L.get('reent') else 'no re-entry found'))
box(('leg', 'side', 'open', 'exit', 'hold min', 'leg MAE', 'realised', 'why the exit',
     'the next open'), out)
print('- the re-entry router picks the bar AND the side, so the chain does not alternate.')
print('- leg MAE is the measured running adverse excursion; a stopped leg scores %.4f by Joe\'s '
      '1007 rule.' % C.MAE_STOP)
print('- realised sums %+.4f over %d legs.'
      % (sum(L.get('real', 0.0) for L in legs), len(legs)))
