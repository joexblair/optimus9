"""CHAINS ANCHORED TO THE SANCTIONED OCTO-SIG EVENTS. 1007.

JOE:
  seed   *"building out these chains from the sanctioned octo-sig events"*
  stop   *"for each run, stop the chain when MAE is >1.1 and start again on the next octo-sig"*
  flip   *"if a leg is met by a target dr sanctioned octo-sig, then you must accept it as a exit
         and enter timestamp"*

SANCTIONED = os_grade = 'with-trend' ONLY - 53 rows over 12 days. Joe 1007: *"we haven't
         sanctioned `no r block`"*, so its 45 rows neither seed a chain nor force an exit.

ONE LEG, open -> exit:
  OPEN         the seeding octo-sig bar (leg 1) or the previous leg's exit bar. Side = towards dr.
  MAE BREACH   the running adverse excursion from THIS leg's open exceeds MAE_STOP (1.1%).
               Exit at that bar. THE CHAIN STOPS. Read causally - the breach bar is the first bar
               on which the 1.1 is known, so it is the bar that acts.
  OCTO-SIG     a sanctioned octo-sig whose dr is the TARGET dr (opposite the open leg) - exit at
               that bar and open the next leg at that bar. Mandatory, outranks the walk.
               A same-dr sanctioned octo-sig inside an open leg is ignored: no pyramid.
  exit-armed   ws2Mage crosses the fence on the leg's own dr side (over 85 LONG, under 15 SHORT).
  KICKSTART    one-time: the highest r-oob line becomes the rider. The established lineage walk
               then owns the rider - baton on an oob crossing within LIN_HOP.
  exit         x-cross (stashed while ws2Mage is oob, released after IB_WOB ib bars) or final
               stalled.

A CHAIN ends on the MAE breach, or at the last bar of its day - the tape is 12 separate days with
gaps between them, so a leg cannot be carried across one. The next chain seeds at the next
sanctioned octo-sig strictly after the stop bar.
"""
import os, io, contextlib, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%6.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

MAE_STOP = float(os.environ.get('MAE_STOP', '1.1'))      # Joe 1007, percent, per leg, from its open
IB_WOB = int(os.environ.get('IB_WOB', '6'))              # bars ws2Mage must hold inside the fence
STASH = os.environ.get('STASH', '0') == '1'              # Joe 1007: the stash is in LIMBO, so OFF
KNOB = ('lazy_g_config.v1|gcws30Mage|flip-towards+norblock|stamp-resolved|'
        'routing-banked|lineage-ws1|mtdwalk-drguard')
GRADES = ('with-trend',)   # Joe 1007: *"we haven't sanctioned `no r block`"*
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
NEED = sorted(set(LIN_TF) | {LIN_TF[-1] + 1, LIN_TF[-2] + 2})
N = len(SC.ts)
R = {t: SC.LD(t * 60, 'r')[:N] for t in NEED}
X = {t: SC.LD(t * 60, 'x')[:N] for t in LIN_TF}
M2 = SC.Mg[2][:N]; PX = SC.PX[:N]
DAY = np.array([datetime.datetime.utcfromtimestamp(int(t) / 1000).strftime('%Y-%m-%d')
                for t in SC.ts])
DAY_LAST = {}
for d in sorted(set(DAY)):
    DAY_LAST[d] = int(np.nonzero(DAY == d)[0][-1])
_P('tape %d bars, %d days, lineage TFs ws%d..ws%d, hop %d, MAE stop %.2f%%, stash %s (ib wob %d)'
   % (N, len(DAY_LAST), LIN_TF[0], LIN_TF[-1], LIN_HOP, MAE_STOP,
      'ON' if STASH else 'OFF — limbo', IB_WOB))

db = DatabaseManager(**get_db_config()); db.connect()
SIG = db.execute("SELECT os_day, os_ts, os_dr, os_grade FROM octosig_rulings "
                 "WHERE os_knob_key=%s AND os_grade IN (" +
                 ','.join(['%s'] * len(GRADES)) + ") ORDER BY os_day, os_ts",
                 (KNOB,) + GRADES, fetch=True)
BANK = {t: momo_bank(db, t) for t in LIN_TF}
db.disconnect()
SANC = {}; SEEDS = []
for r in SIG:
    k = SC.K('%s %s' % (r['os_day'], r['os_ts']))
    if k is None: continue
    SANC[k] = int(r['os_dr'])
    SEEDS.append((k, int(r['os_dr']), str(r['os_day']), r['os_ts'], r['os_grade']))
SEEDS.sort()
_P('sanctioned octo-sig rows %d, resolved to bars %d' % (len(SIG), len(SEEDS)))

ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(SC.Rl[t], dd, int(SC.LG['stall_n']), s_, n_)
_mt = {}
def mt(t, k, d):
    key = (t, k, d)
    if key in _mt: return _mt[key]
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            v = momo_g_why(SC.Rl[t], int(d), int(k))[0] in ('momo', 'curl')
    _mt[key] = v; return v
_P('producers ready')

def bnd(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
m2oob = lambda k, d: (float(M2[k]) >= SC.HI) if d > 0 else (float(M2[k]) <= SC.LO)
def xcond(h, k, d):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    c = (xv < float(R[t1][k]) and xv < float(R[t2][k])) if d > 0 else \
        (xv > float(R[t1][k]) and xv > float(R[t2][k]))
    return c and bnd(t1, k, d) == '.' and bnd(t2, k, d) == '.'

def run_leg(k0, d, last):
    """ONE leg from its open bar. -> (exit_k, why, mae, trace)."""
    tr = []; p0 = float(PX[k0]); sgn = 1 if d > 0 else -1
    armed = False; rider = None; stash = None; ib_run = 0; mae = 0.0
    for j in range(k0 + 1, last + 1):
        px = float(PX[j])
        if np.isfinite(px) and px > 0:
            adv = -((px - p0) / p0 * 100.0 * sgn)
            if adv > mae: mae = adv
            if adv > MAE_STOP:
                tr.append((j, 'MAE BREACH %.4f%% over %.2f%% — chain stops' % (adv, MAE_STOP)))
                return j, 'mae breach', mae, tr
        if SANC.get(j) == -d:
            tr.append((j, 'target-dr sanctioned octo-sig — mandatory exit and enter'))
            return j, 'octo-sig flip', mae, tr
        if not armed:
            if (d > 0 and float(M2[j]) >= SC.HI and float(M2[j - 1]) < SC.HI) or \
               (d < 0 and float(M2[j]) <= SC.LO and float(M2[j - 1]) > SC.LO):
                armed = True
                tr.append((j, 'exit-armed — ws2Mage %s %.0f (%.2f)'
                           % ('over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO,
                              float(M2[j]))))
            else:
                continue
        if rider is None:
            c = [t for t in LIN_TF if oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f oob)' % (rider, float(R[rider][j]))))
            continue
        cand = [t for t in range(rider + 1, min(rider + LIN_HOP, LIN_TF[-1]) + 1)
                if oobf(t, j, d)]
        if cand:
            rider = max(cand); stash = None
            tr.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(R[rider][j])))); continue
        if ST[(rider, d)][j]:
            tr.append((j, 'final stalled on ws%d (r %.2f %s)'
                       % (rider, float(R[rider][j]), bnd(rider, j, d))))
            return j, 'final stalled', mae, tr
        xc = xcond(rider, j, d)
        if not STASH:
            if xc:
                tr.append((j, 'x-cross on ws%d' % rider))
                return j, 'x-cross', mae, tr
            continue
        if m2oob(j, d):
            ib_run = 0
            if xc and stash is None:
                stash = j
                tr.append((j, 'x-cross STASHED on ws%d (ws2Mage %.2f oob)'
                           % (rider, float(M2[j]))))
            continue
        ib_run += 1
        if ib_run == IB_WOB:
            live = any(mt(t, j, d) for t in LIN_TF if t >= rider)
            tr.append((j, 'ws2Mage ib confirmed (%d bars) — momentum at/above ws%d: %s'
                       % (IB_WOB, rider, 'YES' if live else 'NO')))
            if stash is not None and not live:
                tr.append((j, 'stashed x-cross (from %s) FIRES' % SC.U(stash)))
                return j, 'stashed x-cross', mae, tr
        if ib_run >= IB_WOB and xc:
            tr.append((j, 'x-cross on ws%d' % rider))
            return j, 'x-cross', mae, tr
    return last, 'day end', mae, tr

OUT = open(os.environ.get('LEGS_FILE', '/home/joe/.claude/jobs/6eb9931e/tmp/chain_os_legs.txt'), 'w')
chains = []; stop_bar = -1
SKIP = []
for k0, dr, day, ts, grade in SEEDS:
    if k0 <= stop_bar: continue
    if day not in DAY_LAST:
        SKIP.append((day, ts)); continue          # the tape does not reach this day
    last = DAY_LAST[day]
    if k0 >= last: continue
    legs = []; k, d = k0, dr; p_chain = float(PX[k0]); dd_worst = 0.0; eq = 0.0
    print('\n## CHAIN %s %s  seed grade %s  dr %+d  (%s)'
          % (day, ts, grade, dr, 'LONG' if dr > 0 else 'SHORT'), file=OUT)
    while True:
        xk, why, mae, tr = run_leg(k, d, last)
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
        eq += real
        if eq - max(0.0, dd_worst) < 0: pass
        legs.append(dict(side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, real=real,
                         mae=mae, why=why, eq=eq))
        print('\n### leg %d — %s open %s  exit %s  realised %+.4f  leg MAE %.4f  why %s'
              % (len(legs), legs[-1]['side'], SC.U(k), SC.U(xk), real, mae, why), file=OUT)
        for j, lbl in tr:
            print('  %s  %+7.1f min  %s' % (SC.U(j), (int(SC.ts[j]) - int(SC.ts[k])) / 60000.0,
                                            lbl), file=OUT)
        if why in ('mae breach', 'day end'): break
        k = xk; d = -d
    run = 0.0; peak = 0.0; dd = 0.0
    for L in legs:
        run = L['eq']
        if run > peak: peak = run
        if peak - run > dd: dd = peak - run
    chains.append(dict(day=day, seed=ts, grade=grade, dr=dr, legs=legs,
                       tot=eq, n=len(legs), dd=dd, why=legs[-1]['why'],
                       stop=SC.U(legs[-1]['exit'])))
    stop_bar = legs[-1]['exit']
    _P('chain %s %s: %d legs, %+.4f, ended %s' % (day, ts, len(legs), eq, legs[-1]['why']))
OUT.close()

def box(hdr, rows):
    w = [max(len(hdr[i]), max((len(str(r[i])) for r in rows), default=0)) for i in range(len(hdr))]
    L = lambda a, m, b: a + m.join('─' * (x + 2) for x in w) + b
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for r in rows:
        print('│' + '│'.join(' ' + str(r[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))

print('\n# EVERY CHAIN — seeded on a sanctioned octo-sig, MAE stop %.2f%% per leg' % MAE_STOP)
box(('day', 'seed', 'seed grade', 'side', 'legs', 'stop ts', 'ended on', 'worst leg MAE',
     'chain drawdown', 'realised'),
    [(c['day'], c['seed'], c['grade'], 'LONG' if c['dr'] > 0 else 'SHORT', str(c['n']),
      c['stop'], c['why'], '%.4f' % max(L['mae'] for L in c['legs']), '%.4f' % c['dd'],
      '%+.4f' % c['tot']) for c in chains])

print('\n# PER DAY')
pd = collections.OrderedDict()
for c in chains:
    e = pd.setdefault(c['day'], dict(ch=0, legs=0, tot=0.0, brk=0))
    e['ch'] += 1; e['legs'] += c['n']; e['tot'] += c['tot']
    e['brk'] += 1 if c['why'] == 'mae breach' else 0
box(('day', 'chains', 'legs', 'mae-breach stops', 'realised'),
    [(d, str(e['ch']), str(e['legs']), str(e['brk']), '%+.4f' % e['tot']) for d, e in pd.items()]
    + [('12 days', str(sum(e['ch'] for e in pd.values())), str(sum(e['legs'] for e in pd.values())),
        str(sum(e['brk'] for e in pd.values())), '%+.4f' % sum(e['tot'] for e in pd.values()))])

print('\n# HOW EVERY LEG EXITED')
wc = collections.Counter(); wr = collections.Counter()
for c in chains:
    for L in c['legs']:
        wc[L['why']] += 1; wr[L['why']] += L['real']
box(('why', 'legs', 'realised', 'per leg'),
    [(w, str(wc[w]), '%+.4f' % wr[w], '%+.4f' % (wr[w] / wc[w])) for w in sorted(wc, key=lambda z: -wc[z])]
    + [('all', str(sum(wc.values())), '%+.4f' % sum(wr.values()),
        '%+.4f' % (sum(wr.values()) / sum(wc.values())))])

print('\n# HOW EVERY CHAIN ENDED')
cc = collections.Counter(c['why'] for c in chains)
box(('ended on', 'chains', 'realised'),
    [(w, str(cc[w]), '%+.4f' % sum(c['tot'] for c in chains if c['why'] == w))
     for w in sorted(cc, key=lambda z: -cc[z])])
print('\n- %d of %d sanctioned octo-sigs seeded a chain; the rest fell inside a running chain.'
      % (len(chains), len(SEEDS)))
if SKIP:
    print('- %d sanctioned octo-sigs had NO TAPE: %s'
          % (len(SKIP), ', '.join('%s %s' % z for z in SKIP)))
print('- per-leg detail: %s' % OUT.name)
