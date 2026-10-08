"""THE CHAIN RECREATED: the existing lineage walk + the new >ws12 oob mech. 09-25. 1007.

Joe 1007: *"'recreate the chain' means using the exisitng lineage walk + the new ws12 oob mech"* /
*"let's see where the next MAE 1.1 stop"*.

ONE LEG, with both mechs composed:

  OPEN          the previous leg's exit, or the seed bar.
  MAE STOP      at the first bar the adverse excursion from this leg's open exceeds mae_stop_pct
                1.10, the leg closes AT that bar and THE CHAIN STOPS. Outranks everything.
  THE CEILING   ws12r crossing into oob extends the baton's ceiling to ws23, per leg.
  THE WALK      until the handover: exit-armed on ws2Mage, one-time KICKSTART, baton on an oob
                crossing within lin_hop, exit on x-cross or final stalled.
  THE HANDOVER  the first bar where a CONSECUTIVE ws12r oob run on the leg's dr side exceeds
                oob_gate_bars 72. From that bar the >ws12 mech owns the exit and the walk's
                x-cross and stall are SUPPRESSED.

                THIS IS MY COMPOSITION DECISION, stated so it can be flipped. Joe's spec says
                "apply this logic after ws12r is oob for >6 minutes", which reads as a handover,
                and the mech exists because the walk's ws23 x-cross fired 56.6 min after the pivot
                on leg 8. The alternative - both live, first to fire wins - is one line away.
  AFTER IT      the ws1Mage 50 dip with a dwell > dip_dwell_bars 12, confirmed at dip + 11, then
                the first ws1r or ws2r reversal carrying a divergence with x under r (dr +1).

  BRANCH 1      a counter-dr ws12x cross of ws12r inside the first 6 min of an oob run is RECORDED
                and NOT ACTED ON. It is a trade SIGNAL and spec open question #4 - what closes a
                branch-1 trade in an always-in-market chain - is unanswered. Acting on it here
                would be me answering it.

Knobs from ws12_baton_config v1 and lazy_g_config v1.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import stall_mask, anchor_floater
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
START = os.environ.get('W_START', '08:10:00')
FIRST = int(os.environ.get('W_SIDE', '1'))
LEG0 = int(os.environ.get('W_LEG0', '7'))
db = DatabaseManager(**get_db_config()); db.connect()
W = spec_config(db, 'ws12_baton_config')
LIN_HOP = int(SC.LG['lin_hop']); BASE_HI = SC.TF[-1]
TRIG_TF, CEIL_HI = int(W['ceil_trig_tf']), int(W['ceil_hi'])
GATE_BARS, SIG_WIN = int(W['oob_gate_bars']), int(W['sig_window_bars'])
DIP_MID, DIP_DWELL = float(W['dip_mid']), int(W['dip_dwell_bars'])
# THE >ws12 MECH'S OWN oob FENCE, 1008. Joe: *"we should have a knob for >12 oob"*.
#
# The 72-bar gate, the branch-1 window and the ceiling trigger were all reading the GLOBAL oob
# 15/85 out of lazy_g - the same shape as reent_xwob borrowing the divergence mech's x_rev_xwob.
# `goob` is the >ws12 mech's test and nothing else uses it; the KICKSTART and the baton stay on
# `oobf` and the global fence.
#
# oob_gate_fence 15.0 reproduces today's behaviour exactly, so the knob changes nothing until it is
# swept. Symmetric: lo = the knob, hi = 100 - the knob.
G_LO = float(W['oob_gate_fence']); G_HI = 100.0 - G_LO
#   `goob` itself is defined beside `oobf`, once R exists.
DIP_FENCE = float(W['dip_fence'])            # Joe 1008: the dip is a BAND, not a level
DIP_HI, DIP_LO = DIP_FENCE, 100.0 - DIP_FENCE   # 53.0 and 47.0
RREV, MAE_STOP = int(W['rrev_wob']), float(W['mae_stop_pct'])
PASS = os.environ.get('W_PASS', 'oob')  # 'oob' (as built, Joe's tag ruling) or 'stalled'.
#                                        THE BATON'S PASS TEST. Joe 1007: *"keeping the
#                                        x-cross and swapping oob with stalled"*.
NOX = os.environ.get('W_NOX') == '1'   # 1 disables the lineage walk's x-cross exit, leaving
#                                        `final stalled` as its only exit. Joe 1007 asked what
#                                        the swap left behind; this is the switch that shows it.
# ---- JOE'S DELEGATION GATE, 1008. ENV-SWITCHED AND OFF BY DEFAULT, so nothing is banked.
#
# Joe 1008: *"presently, whenever ws12r crosses to oob we automatically delegate to the >12 oob
# mech. sometimes, the delegation is a bad move ... to gate the delegation, we can look at ws60r's
# trajectory (per the traj spec). if ws60r's trajectory matches the oob side that ws12r is crossed
# into ... then we open the delegation gate"*.
#
# W_DGATE   'off'    as built - the handover fires on the oob run alone. THE DEFAULT.
#           'once'   tested ONCE, at the handover bar. If ws60r's trajectory is against the oob
#                    side there, this oob RUN never delegates - the lineage walk keeps the exit.
#           'retest' tested every bar while the oob run lasts; the handover fires on the first bar
#                    the trajectory agrees.
#
# 'once' vs 'retest' IS NOT IN JOE'S SPEC. Both are arms, neither is decided.
#
# WHAT A CLOSED GATE DOES is also unspecified, and there is only one other mech in the leg: the
# lineage walk keeps the exit (`final stalled` or the x-cross). Stated because it is a choice.
#
# THE TRAJECTORY IS READ AT THE BAR THE HANDOVER WOULD FIRE ON, never later. Reading it after that
# bar would be information past the decision.
#
# THE SIDE: inside run_leg the ws12r oob test is `goob(TRIG_TF, j, d)` on the LEG's own direction,
# so the oob side IS `d` and `TRAJ60[j] == d` is the test. _delegate.py measured dr to add nothing
# - the oob side alone separated 71.3% / 37.5% against the three-way's 71.0% / 39.3%.
DGATE = os.environ.get('W_DGATE', 'off')
assert DGATE in ('off', 'once', 'retest'), 'W_DGATE must be off, once or retest'
DIV_TFS = [int(s.strip().replace('ws', '').replace('r', '')) for s in W['div_lines'].split(',')]
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
N = len(SC.ts)
ALL_TF = list(range(SC.TF[0], CEIL_HI + 1))
RL = {t: SC.LD(t * 60, 'r') for t in range(SC.TF[0], CEIL_HI + 3)}
R = {t: RL[t][:N] for t in RL}
X = {t: SC.LD(t * 60, 'x')[:N] for t in ALL_TF}
M2 = SC.Mg[2][:N]; G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
BANK = {t: momo_bank(db, t) for t in ALL_TF}; db.disconnect()
ST = {}
for t in ALL_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(RL[t], dd, int(SC.LG['stall_n']), s_, n_)
REV = {t: _mage_rev(R[t], RREV) for t in DIV_TFS}
_P('producers ready; ceiling ws%d->ws%d, gate %d bars at oob %.0f/%.0f, dip band %.0f-%.0f '
   'dwell %d, stop %.2f'
   % (BASE_HI, CEIL_HI, GATE_BARS, G_LO, G_HI, DIP_LO, DIP_HI, DIP_DWELL, MAE_STOP))

# ws60r's TRAJECTORY, per the traj spec: the sign of (ws60r now - ws60r at its last step change).
# No lookback window, no cap. Built only when the gate is on. Verified against `step_dir` in
# _delegate.py at 16,815 sampled bars.
if DGATE != 'off':
    _R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
    TRAJ60 = np.zeros(N, np.int8)
    _cur = _prev = np.nan
    for _k in range(N):
        _v = float(_R60[_k])
        if np.isfinite(_v):
            if not np.isfinite(_cur): _cur = _v
            elif _v != _cur: _prev, _cur = _cur, _v
        TRAJ60[_k] = 0 if not np.isfinite(_prev) else (1 if _cur > _prev else (-1 if _cur < _prev else 0))
    _P('ws60r trajectory built; delegation gate %s' % DGATE)
else:
    TRAJ60 = None

def bnd(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
# the >ws12 mech's own oob test, on the oob_gate_fence read above. Nothing else
# uses it: the KICKSTART and the baton stay on `oobf` and the global 15/85.
goob = lambda t, k, d: (float(R[t][k]) >= G_HI) if d > 0 else (float(R[t][k]) <= G_LO)
# THE LINEAGE WALK'S x-CROSS TARGET, NOW KNOB-DRIVEN. 1008. Joe: *"go for B"*.
#
# WAS, and it is still what x_tgt_role r + x_tgt_tfs both + x_tgt_fence 1 reproduces:
#     the rider's x against the r of h+1 AND h+2, with BOTH targets in-fence.
# NOW, #61 arm B:
#     the rider's x against the `b` line of h+1 ONLY, with no in-fence test on it.
#
# THE THREE KNOBS, and what each value means:
#   x_tgt_role   'b'     the LINE the x must cross. The five wsf roles are the same oscillator at
#                        five speeds - r is k 5/8/7, x is bb 5/0.35, m is bb 6/0.4, Mage is
#                        bb 38/0.93, and b is bb 49/0.95, the SLOWEST of them.
#   x_tgt_tfs    'next'  which TFs above the rider carry the target. 'both' = h+1 and h+2,
#                        'next' = h+1 only, 'self' = h itself.
#   x_tgt_fence  0       1 = the target must also be in-fence (neither oob nor past the ex-fence),
#                        which is what `bnd(t, k, d) == '.'` tested. 0 = no such test.
#
# THE IN-FENCE TEST IS READ ON THE TARGET LINE, not on r, so that it keeps testing the same lines
# it crosses when the role moves. Stated because #61 does not say.
XT_ROLE, XT_TFS = str(W['x_tgt_role']), str(W['x_tgt_tfs'])
XT_FENCE = int(W['x_tgt_fence'])
XT_OFF = {'both': (1, 2), 'next': (1,), 'self': (0,)}[XT_TFS]
TGT = R if XT_ROLE == 'r' else {t: SC.LD(t * 60, XT_ROLE)[:N] for t in RL}
def xcond(h, k, d):
    tt = [h + o for o in XT_OFF]
    if any(t not in TGT for t in tt): return False
    xv = float(X[h][k])
    if not all((xv < float(TGT[t][k])) if d > 0 else (xv > float(TGT[t][k])) for t in tt):
        return False
    if not XT_FENCE: return True
    return all(((float(TGT[t][k]) < EXF_HI) if d > 0 else (float(TGT[t][k]) > EXF_LO))
               for t in tt)
xund = lambda t, k, d: (float(X[t][k]) < float(R[t][k])) if d > 0 else (float(X[t][k]) > float(R[t][k]))
# THE DIP IS A BAND, 1008. Joe: *"we'll use a small 100-{knob:53} fence, ie 47 to 53"* /
# *"fence 53 + dwell 6"*.
#
# WAS: `indip = G1 < dip_mid 50` for a LONG leg, `> 50` for a SHORT. A single level, and the dwell
# counted bars on the far side of it. At 17:54 on 09-25 that rejected the dip SEVEN times - the
# longest sub-50 run is 4 bars against a dwell of 12.
#
# NOW: the dip region is the BAND dip_lo 47 to dip_hi 53, symmetric about dip_mid 50.
#
# THE ENTRY IS STILL dr-ALIGNED, which the band alone is not: a LONG leg must come DOWN into the
# band from above DIP_HI, and a SHORT leg must come UP into it from below DIP_LO. Without this the
# band test is direction-blind and `dr_aligned` 1 would be contradicted.
#
# ONE EDGE, STATED: a dip that goes DEEPER than DIP_LO leaves the band and breaks the dwell, so a
# deeper dip can disqualify. The alternative - a one-sided `G1 <= DIP_HI` for a LONG - has no such
# edge. Joe's words name the band, so the band is what is built.
inband = lambda k: DIP_LO <= float(G1[k]) <= DIP_HI
indip = lambda k, d: inband(k)
entered = lambda k, d: (inband(k) and not inband(k - 1)
                        and ((float(G1[k - 1]) > DIP_HI) if d > 0
                             else (float(G1[k - 1]) < DIP_LO)))
WANT = lambda d: (-1 if d > 0 else +1)
def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))

def run_leg(k0, d):
    tr = []; p0 = float(PX[k0]); sgn = 1 if d > 0 else -1
    armed = False; rider = None; mae = 0.0
    ceil = BASE_HI; ceil_bar = None
    oob_a = None; hand = None; dip = None; conf = None; ib_run = 0
    gate_shut = False      # W_DGATE 'once': latched when the gate refused THIS oob run
    for j in range(k0 + 1, N):
        px = float(PX[j])
        if np.isfinite(px) and px > 0:
            adv = -((px - p0) / p0 * 100.0 * sgn)
            if adv > mae: mae = adv
            if adv > MAE_STOP:
                tr.append((j, 'MAE BREACH %.4f%% over %.2f%% - chain stops for review'
                           % (adv, MAE_STOP)))
                return j, 'mae breach', mae, ceil_bar, hand, tr
        # the ws12r oob run on the leg's dr side, and the handover
        if goob(TRIG_TF, j, d):
            if oob_a is None:
                oob_a = j
                # DEAD LOOP DELETED 1008. It read
                #     for q in range(j + 1, min(N, j + SIG_WIN) + 1):
                #         if not oobf(TRIG_TF, q, d): break
                # and assigned nothing, returned nothing and had no side effect - the branch-1
                # scan immediately below is the real one. Its only behaviour was a CRASH: the
                # bound is min(N, ...) + 1 where the real loop uses min(N - 1, ...) + 1, so q
                # reached N and indexed one past the end of a 1,632,960-bar line. It killed the
                # overnight sweep at the tape end on configs whose chain ran within SIG_WIN
                # (72 bars) of the last bar. Deleting it changes no result.
                u = lambda z: float(X[TRIG_TF][z]) < float(R[TRIG_TF][z])
                for q in range(j + 1, min(N - 1, j + SIG_WIN) + 1):
                    if not goob(TRIG_TF, q, d): break
                    c = (u(q) and not u(q - 1)) if d > 0 else ((not u(q)) and u(q - 1))
                    if c:
                        tr.append((q, 'branch 1 cross — RECORDED, not acted on (ws%dx %.2f vs r %.2f)'
                                   % (TRIG_TF, float(X[TRIG_TF][q]), float(R[TRIG_TF][q]))))
                        break
            if hand is None and not gate_shut and (j - oob_a) > GATE_BARS:
                tj = 0 if TRAJ60 is None else int(TRAJ60[j])
                if DGATE == 'off' or tj == (1 if d > 0 else -1):
                    hand = j
                    tr.append((j, 'HANDOVER — ws%dr oob %.1f min; the >ws12 mech owns the exit%s'
                               % (TRIG_TF, (int(SC.ts[j]) - int(SC.ts[oob_a])) / 60000.0,
                                  '' if DGATE == 'off'
                                  else ' (gate OPEN, ws60r traj %+d)' % tj)))
                elif DGATE == 'once':
                    gate_shut = True
                    tr.append((j, 'DELEGATION REFUSED — ws60r traj %+d against the oob side %+d; '
                                  'this oob run never delegates and the walk keeps the exit'
                               % (tj, 1 if d > 0 else -1)))
        else:
            oob_a = None; gate_shut = False     # the oob run broke, so the latch clears with it
        if ceil == BASE_HI and goob(TRIG_TF, j, d) and not goob(TRIG_TF, j - 1, d):
            ceil = CEIL_HI; ceil_bar = j
            tr.append((j, 'CEILING ws%d -> ws%d (ws%dr %.2f)'
                       % (BASE_HI, CEIL_HI, TRIG_TF, float(R[TRIG_TF][j]))))
        # ---- after the handover: the >ws12 mech owns the exit
        if hand is not None:
            if dip is None:
                if entered(j, d):
                    n = 0
                    while j + n <= N - 1 and indip(j + n, d):
                        n += 1
                    if n > DIP_DWELL:
                        dip, conf = j, j + DIP_DWELL - 1
                        tr.append((j, 'dip into %.0f-%.0f — ws1Mage %.2f, run %d bars (%.1f min),'
                                   ' confirms %s'
                                   % (DIP_LO, DIP_HI, float(G1[j]), n, n * 5 / 60.0,
                                      SC.U(conf))))
                continue
            if j <= conf:
                continue
            for t in DIV_TFS:
                if REV[t][j] != WANT(d) or not xund(t, j, d): continue
                af = anchor_floater(R[t], PX, d, j)
                if af is None or int(af['fired']) == 0: continue
                tr.append((j, 'ws%dr reversal + divergence, x under r (floater %s, d_osc %+.2f)'
                           % (t, SC.U(af['floater'][0]), af['d_osc'])))
                return j, '>ws12 divergence on ws%dr' % t, mae, ceil_bar, hand, tr
            continue
        # ---- before the handover: the lineage walk
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
            c = [t for t in ALL_TF if t <= ceil and oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f oob, ceiling ws%d)'
                           % (rider, float(R[rider][j]), ceil)))
            continue
        cand = [t for t in range(rider + 1, min(rider + LIN_HOP, ceil) + 1)
                if (ST[(t, d)][j] if PASS == 'stalled' else oobf(t, j, d))]
        if cand:
            rider = max(cand)
            tr.append((j, 'baton -> ws%d %s (r %.2f)'
                       % (rider, PASS, float(R[rider][j])))); continue
        if ST[(rider, d)][j]:
            tr.append((j, 'final stalled on ws%d (r %.2f %s)'
                       % (rider, float(R[rider][j]), bnd(rider, j, d))))
            return j, 'final stalled', mae, ceil_bar, hand, tr
        if (not NOX) and xcond(rider, j, d):
            tr.append((j, 'x-cross on ws%d' % rider))
            return j, 'x-cross', mae, ceil_bar, hand, tr
    return None, 'tape end', mae, ceil_bar, hand, tr

def main():
    k0 = SC.K('%s %s' % (D, START))
    print('\n# THE CHAIN RECREATED FROM %s %s, side %s — lineage walk + the >ws12 oob mech'
          % (D, START, 'LONG' if FIRST > 0 else 'SHORT'))
    k, d, legs, n = k0, FIRST, [], LEG0
    while True:
        xk, why, mae, cb, hand, tr = run_leg(k, d)
        if xk is None:
            print('\n- leg %d found no exit before the tape end. the chain ends.' % (n + 1)); break
        n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
        legs.append(dict(leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, real=real,
                         mae=mae, why=why, hand=hand))
        pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
        mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
        print('\n## LEG %d — %s   open %s   pxs %.6f' % (n, legs[-1]['side'], SC.U(k), p0))
        box(('ts', '+min', 'event', 'pxs', 'pct'),
            [(SC.U(k), '+0.0', 'OPEN %s' % legs[-1]['side'], '%.6f' % p0, '+0.0000')]
            + [(SC.U(j), mn(j), lbl, '%.6f' % float(PX[j]), pct(j)) for j, lbl in tr]
            + [(SC.U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), pct(xk))])
        if why == 'mae breach':
            print('\n- MAE breach at %s. THE CHAIN IS STOPPED FOR REVIEW.' % SC.U(xk)); break
        k = xk; d = -d

    def mm(s_, e_, dd):
        """MAE / MFE over the leg's own holding window, in the direction dr makes favourable."""
        seg = PX[s_:e_ + 1]
        seg = seg[np.isfinite(seg) & (seg > 0)]
        if seg.size == 0: return 0.0, 0.0
        p_ = float(PX[s_])
        f = float(seg.max()) if dd > 0 else float(seg.min())
        g = float(seg.min()) if dd > 0 else float(seg.max())
        return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

    # JOE'S SCORING RULE, 1007: *"if mae1.1 was hit, then MFE is zero and MAE is 1.1"*. A stopped leg
    # scores the KNOB value, not the measured overshoot - 1.1000, not 1.1504.
    print('\n# EVERY LEG AND THE RUNNING MAE / MFE')
    rows = []; rA = 0.0; rF = 0.0; rR = 0.0
    for L in legs:
        dd = 1 if L['side'] == 'LONG' else -1
        if L['why'] == 'mae breach':
            a_, f_ = MAE_STOP, 0.0
        else:
            a_, f_ = mm(L['open'], L['exit'], dd)
        rA += a_; rF += f_; rR += L['real']
        rows.append((str(L['leg']), L['side'], SC.U(L['open']), SC.U(L['exit']),
                     '%.1f' % ((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0),
                     L['why'], '%.4f' % a_, '%.4f' % f_,
                     ('%.2f' % (f_ / a_)) if a_ > 0 else 'inf',
                     '%+.4f' % L['real'], '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
    box(('leg', 'side', 'open', 'exit', 'hold min', 'why', 'leg MAE', 'leg MFE', 'MFE/MAE',
         'realised', 'running MAE', 'running MFE', 'running realised'), rows)
    print('- a leg that hit the stop scores MFE 0.0000 and MAE %.4f, the knob value - Joe 1007.'
          % MAE_STOP)
    print('- running MFE/MAE over the chain: %.2f' % (rF / rA) if rA > 0 else '- running MAE is 0')

    print('\n# THE CHAIN FROM %s' % START)
    box(('leg', 'side', 'open', 'exit', 'hold min', 'handover', 'leg MAE', 'realised', 'why'),
        [(str(L['leg']), L['side'], SC.U(L['open']), SC.U(L['exit']),
          '%.1f' % ((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0),
          SC.U(L['hand']) if L['hand'] else '—',
          '%.4f' % L['mae'], '%+.4f' % L['real'], L['why']) for L in legs]
        + [('legs %d-%d' % (legs[0]['leg'], legs[-1]['leg']), '', SC.U(legs[0]['open']),
            SC.U(legs[-1]['exit']),
            '%.1f' % sum((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0 for L in legs),
            '%d of %d' % (sum(1 for L in legs if L['hand']), len(legs)),
            '%.4f' % max(L['mae'] for L in legs), '%+.4f' % sum(L['real'] for L in legs), '')])
    print('\n- %d legs, %d positive, %d handed over to the >ws12 mech'
          % (len(legs), sum(1 for L in legs if L['real'] > 0), sum(1 for L in legs if L['hand'])))


if __name__ == '__main__':
    main()
