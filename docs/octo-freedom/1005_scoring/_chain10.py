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
                and NOT ACTED ON. It is a trade SIGNAL, and acting on it would change the leg set,
                which Joe has not asked for.

                CORRECTED 1009. This block used to say the signal was blocked on "spec open
                question #4 - what closes a branch-1 trade in an always-in-market chain". THOSE
                WERE MY WORDS, NOT JOE'S, and the question was never real: the chain is CONTINUOUS,
                so a signal bar is the current leg's EXIT and the next leg's OPEN on the flipped
                side, exactly like `final stalled`, `x-cross` and the >ws12 divergence. None of
                those has a close rule either. Joe 1009: *"the query on a close rule is confusing -
                our chain is continuous"*.

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
# W_TRACE_NOX=1 records the x-cross exits that W_NOX=1 SUPPRESSES, and names them at the bar the
# ws12r oob run ends. Joe 1009: *"squashed was my shorthand - I was refering to the x-cross that we
# disabled 2 or 3 turns back"*. REPORTING ONLY - no branch reads it. Off by default because it
# restores the per-bar `xcond` call that W_NOX=1 saves.
TRACE_NOX = os.environ.get('W_TRACE_NOX', '0') == '1'
# W_SQX=1 TURNS JOE'S 1009 RULE ON. *"if oob ended before dwell completed, and a x-cross was
# squashed during the oob, then a B-trade is created and the A-trade is closed"*, and on the exit
# bar: *"re the causal oversight - we use the run ends timestamp to keep us live-ready"* - so A
# closes on the bar ws12r RETURNS IN-BOUNDS, the first bar where "the run ended short of the dwell"
# is knowable. Not the cross bar, which would need 3 bars of lookahead.
#
# ANY squashed cross inside the run counts - edge or already standing. RULED by Joe 1009 once the
# edge option was put to him with its count: *"I don't know how to handle x-cross correctly yet -
# the data will make it obvious in time so more hits are better than less"*. So the wide reading
# stands: 23 A-trades on the 94-day tape, against 10 for an EDGE-only test.
SQX = os.environ.get('W_SQX', '0') == '1'
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
assert not (SQX and not NOX), 'W_SQX=1 needs W_NOX=1 - with the x-cross live there is nothing ' \
                              'squashed for the rule to read'

# W_DGATE   'off'    as built - the handover fires on the oob run alone. THE DEFAULT.
#           'once'   tested ONCE, at the handover bar. If ws60r's trajectory is against the oob
#                    side there, this oob RUN never delegates - the lineage walk keeps the exit.
#
# 'retest' IS GONE, 1009. It was tested every bar while the oob run lasted and measured ZERO
# refusals at every width and both ceilings, so it was never a gate - it only delayed.
#
# THE DIRECTION SOURCE WAS REPLACED, 1009. It used to be `step_dir` - the sign of (ws60r now vs
# ws60r before its last step change) - a definition I wrote in 1007 for ws1r and then reused here
# "per the traj spec". JOE'S ESTABLISHED MECH IS `optimus9/compute/rule2_trajectory.py`, Joe 0924,
# task #22's first mechanism, and ITS OWN DOCSTRING diagnoses the bug: *"WHY THE BAR-TO-BAR READING
# WAS WRONG ... an unbroken-climb test returns 0 bars on every line"*. Measured on ws60r at
# 2026-08-22 13:33:50: step_dir's reference bar was 13:33:45, FIVE SECONDS back, on a line that had
# climbed +13.94 since 11:03. Every ws60r number taken before 1009 used step_dir and is void.
#
# `_trajmech.traj` is the ruled replacement - block samples, the run of same-signed sample diffs,
# the run's far end truncating the tail, a one-sample-at-a-time deferral through a flat tail, and
# `dir 0` on a wholly flat lookback. Its knobs, all Joe's unless marked:
#   W_TRAJ_BLOCK  60 bars = 5 min   Joe 1009 *"I think 5 minutes stays"*
#   W_TRAJ_TAIL   2 samples = 10 min   TRAJ_TAIL_TF_SAMP. Swept 1/2/3/6/12; all within 2.2 pts
#   W_TRAJ_LOOK   24 samples = 120 min  TRAJ_MULTI_TF_SAMP 2 x the 60 min TF-width
#   W_TRAJ_KIND   'close'   MINE - what one sample IS. Beats 'extreme' +22.4 vs +17.8
# TRAJ_MIN_TAIL_LIFE IS NOT HERE: Joe 1009 *"drop the tail-life deferral and keep #7 for dir 0
# only"*, after it overrode a correct call on 08-22's only paying reversal.
#
# ON `dir 0` the 4 mage/r rules decide, Joe 1008's #7: TRUE - pxs reverses - iff
# sign(ws60Mage - ws60r) == -(the oob side). It fired 1 time in 764 dwell-endings, and its own
# premise measured as a coin flip (sign(Mage-r) predicts ws60r's next move 49.7-53.6%), so it is
# recorded as Joe's rule with that caveat attached and nothing more.
#
# WHAT A CLOSED GATE DOES is unspecified, and there is only one other mech in the leg: the
# lineage walk keeps the exit (`final stalled` or the x-cross). Stated because it is a choice.
#
# THE TRAJECTORY IS READ AT THE BAR THE HANDOVER WOULD FIRE ON, never later. Reading it after that
# bar would be information past the decision.
#
# THE BAR IS THE LEG'S OWN. `oob_a` is set inside `run_leg` and resets at the leg's open, so a leg
# that opens mid-oob-run gets its own 6-minute clock. Measured on 08-22 leg 853: the global oob run
# starts 01:24:00 and my offline scripts put the dwell-ending at 01:30:05, but the leg opens
# 01:37:25 and THE CHAIN'S HANDOVER IS 01:43:35 - 13.5 min apart. The gate here has always read the
# leg's bar; it is the offline event lists that were wrong, including the one behind the +22.4.
#
# THE SIDE: inside run_leg the ws12r oob test is `goob(TRIG_TF, j, d)` on the LEG's own direction,
# so the oob side IS `d`. _delegate.py measured dr to add nothing
# - the oob side alone separated 71.3% / 37.5% against the three-way's 71.0% / 39.3%.
DGATE = os.environ.get('W_DGATE', 'off')
assert DGATE in ('off', 'once', 'traj', 'vote'), 'W_DGATE must be off, once, traj or vote'
# ---- W_DGATE='vote', Joe 1009. THE THREE-STEP DIRECTION, every step his.
# 1  THE 40-MINUTE VOTE on ws60r. *"let's replace diff weight with a simple how many UPS vs how
#    many DOWNS are in the tail"* / *"I meant the last 40 minutes"*. 40.0 min / the 5.0-min block =
#    8 diffs, counted not weighted. It replaces `travel` as the primary.
# 2  C3 BREAKS A TIE. *"maybe C3 is all we need - 1 miss out of 8 isn't trivial"* / *"we landed here
#    because of a tie in our test walk. let's apply C3"*. C3 is the traj majority across ws5-ws11,
#    which scored 7 of 8 on the 8 measured ties against Joe's own chart read - against 5 of 8 for
#    the 36-sample diff, 5 of 8 for the Mage count and 5 of 8 for the always-UP constant.
#    NOTE: on a tied bar the direction no longer comes from ws60r at all; it comes from ws5-ws11.
# 3  IF C3 ALSO TIES -> `travel`. NOT RULED BY JOE. C3 reads 7 lines so it can only tie on a flat
#    (3D 3U 1F); it did not tie once in the 56 readings measured across the 8 ties. Falling back to
#    `travel` is the minimum-change option and keeps a verdict always available. STATED, not chosen
#    by him.
#
# WHAT IS NOT CARRIED OVER: the 36-sample earliest-to-latest diff was built as a tie-breaker and
# C3 replaces it in that job, so it is not read here. `W_TRAJ_LOOK` 36 still bounds how far the
# flat-span deferral inside `travel` can reach, which is its only remaining effect.
VOTE_MIN = float(os.environ.get('W_VOTE_MIN', 40))
C3_LO = int(os.environ.get('W_C3_LO', 5))
C3_HI = int(os.environ.get('W_C3_HI', 11))
# W_VOTE_TIE picks what breaks a 4-4 vote: 'c3' is Joe's ruling, 'travel' is the ISOLATION ARM -
# the same 40-min vote with the old reading as the tie-break, so the vote's effect and C3's effect
# can be read apart instead of being one number.
VOTE_TIE = os.environ.get('W_VOTE_TIE', 'c3')
assert VOTE_TIE in ('c3', 'travel'), 'W_VOTE_TIE must be c3 or travel'
# W_TRACE_DGATE=1 adds ws60r's OWN reading to the trace at every bar the gate is or would be
# consulted. Joe 1009: *"there's also no events recorded from ws60r - they need to be visible to
# understnad its return"*. REPORTING ONLY - the extra rows carry no branch, so a run with the flag
# on and a run with it off take the same exits. It is off by default because it costs a `traj` call
# per oob-run OPENING (~5,700 over the 95-day tape) that the mech itself does not need.
TRACE_DG = os.environ.get('W_TRACE_DGATE', '0') == '1'
# ---- THE FULL SPEC, W_DGATE='traj', Joe 1009. OFF BY DEFAULT.
#
# 1  ws12r crosses to oob on the LEG's side. A-trade is already open. The dwell clock starts at
#    `oob_a` and RESETS whenever ws12r returns in-bounds.
# 2  an x-cross INSIDE the exhaustion window -> EXHAUSTION. Joe 1009: *"EXHAUSTION is the same as
#    weakness, and weakness signals a reveral. so if we get an x-cross inside ws12r's dwell, it
#    overrides ws60r (because ws60r is in a future that won't come) and creates a B-trade after
#    closing A-trade"*. ws60r is NOT consulted on this path.
# 3  the window completes with no x-cross -> ws12r is ESTABLISHED -> ws60r is consulted at the
#    dwell-ending (`oob_gate_bars`):
#      3a traj MATCHES the oob side  -> A stays open, the >ws12 mech owns the exit
#      3b traj AGAINST the oob side  -> wait for ws12r's own stall or x-cross AFTER the dwell, then
#                                       close A there. Joe 1009: *"we test ws60r at the end of the
#                                       dwell, and act on the stall/x-cross"*
# 4  the oob run ends before the dwell-ending -> no decision; the lineage walk keeps the exit.
#
# A's CLOSE IS B's OPEN. The chain alternates on every exit (`k = xk; d = -d` in the driver), so
# returning at the B bar closes A and opens B on the opposite side with no new driver code. Joe
# 1009: *"the traj decision allows for only one trade to exist"*.
#
# THE EXHAUSTION RULE IS JOE'S 0728/0729 MECH, `build_exhaust.py`: *"if x crosses r in the first 1/4
# seam"*. r oob and HOLDING past the 1/4 seam is ESTABLISHED -> continuation; x crossing back inside
# it means r never established -> exhaustion. 1/4 seam = TF minutes / 4 = TF x 3 bars.
#   W_EXH_FRAC  0.25   the window as a fraction of the trigger TF. Joe 1009: *"needs a metric-based
#                      sweep, but I don't hink it will be far from 0.25"*. SWEEPABLE, not settled.
#   XWOB_WS12X  4      bars the crossed side must HOLD before the cross is acted on. Joe 1009:
#                      *"let's pick a number between raw and safe - wob {knob:4, `XWOB_WS12X`}"*,
#                      between the raw cross bar and `build_exhaust.py`'s wob_n-1 = 8 bars.
#                      Joe 0729 in that file: *"Line values must be read at the RAW bar; a live
#                      system can only act at the CONFIRMED bar"*.
# THE CROSS IS THE STANDARD dr-BASED ONE, Joe 1009 *"yes - the standard dr based cross"*: on a leg
# with d > 0 the cross is ws12x going UNDER ws12r, on d < 0 it is ws12x going OVER. Identical to
# branch 1's condition at :300 and to the x-cross direction ruling of 0818.
EXH_FRAC = float(os.environ.get('W_EXH_FRAC', 0.25))
XW12 = int(os.environ.get('XWOB_WS12X', 4))
TRAJ_BLOCK = int(os.environ.get('W_TRAJ_BLOCK', 60))
TRAJ_TAIL = int(os.environ.get('W_TRAJ_TAIL', 2))
TRAJ_LOOK = int(os.environ.get('W_TRAJ_LOOK', 24))
TRAJ_KIND = os.environ.get('W_TRAJ_KIND', 'close')
assert TRAJ_KIND in ('close', 'extreme'), 'W_TRAJ_KIND must be close or extreme'
EXH_BARS = int(round(TRIG_TF * EXH_FRAC * 60.0 / 5.0))   # TF12 x 0.25 = 3.0 min = 36 bars
DIV_TFS = [int(s.strip().replace('ws', '').replace('r', '')) for s in W['div_lines'].split(',')]
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
N = len(SC.ts)
ALL_TF = list(range(SC.TF[0], CEIL_HI + 1))
RL = {t: SC.LD(t * 60, 'r') for t in range(SC.TF[0], CEIL_HI + 3)}
R = {t: RL[t][:N] for t in RL}
X = {t: SC.LD(t * 60, 'x')[:N] for t in ALL_TF}
M2 = SC.Mg[2][:N]; G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
# THE ARMING LINE IS A KNOB, 1009. Joe: *"exit-armed needs ws2Mage crossing into oob ... this is a
# constant thorn in our side. let's swap ws2Mage with ws1Mage"*. The walk cannot exit before it
# arms, and 206 of 1,593 legs never armed at all - they summed -417.09, with 162 of them exiting on
# `mae breach`. W_ARM_TF 2 is the banked line; 1 is Joe's swap.
ARM_TF = int(os.environ.get('W_ARM_TF', 2))
MARM = SC.Mg[ARM_TF][:N] if ARM_TF in SC.Mg else np.asarray(SC.LD(ARM_TF * 60, 'Mage'), float)[:N]
_P('the arming line is ws%dMage (banked ws2Mage)' % ARM_TF)
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

# ws60r AND ws60Mage, loaded only when the gate is on. `traj` is called per handover bar, not
# precomputed: the block walk reads at most TRAJ_LOOK x TRAJ_BLOCK bars and there are ~130
# handovers in a 95-day run, so the cost is nothing and nothing is cached that could drift.
if DGATE != 'off':
    from _trajmech import traj as _traj, sample_series as _samp
    R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
    M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
    _P('ws60r + ws60Mage loaded; gate %s, traj block %d tail %d look %d kind %s'
       % (DGATE, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND))
else:
    _traj = _samp = R60 = M60 = None
VOTE_ND = int(round(VOTE_MIN / (TRAJ_BLOCK * 5 / 60.0)))
_sgn = lambda z: 0 if z == 0 else (1 if z > 0 else -1)

def vote40(j, d):
    """Joe's 40-minute UP/DOWN COUNT on ws60r. -> (dir, ups, downs, flats). Counted, not weighted."""
    sm = _samp(R60, j, TRAJ_BLOCK, TRAJ_LOOK, TRAJ_KIND, d)
    if len(sm) < VOTE_ND + 1:
        return 0, 0, 0, 0
    u = dn = fl = 0
    for i in range(VOTE_ND):
        z = _sgn(float(R60[sm[i][0]]) - float(R60[sm[i + 1][0]]))
        u += z > 0; dn += z < 0; fl += z == 0
    return _sgn(u - dn), u, dn, fl

def c3dir(j, d):
    """C3 - the traj majority across ws{C3_LO}r..ws{C3_HI}r. -> (dir, downs, ups, flats)."""
    u = dn = fl = 0
    for t in range(C3_LO, C3_HI + 1):
        if t not in R: continue
        r = _traj(np.asarray(R[t], float), j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
        u += r['dir'] > 0; dn += r['dir'] < 0; fl += r['dir'] == 0
    return _sgn(u - dn), dn, u, fl

def dgate_dir(j, d):
    """The delegation direction at bar j for a leg on side d. -> (dir, source, travel)

    dir is ws60r's trajectory per `_trajmech.traj`. On `dir 0` - a wholly flat lookback - Joe
    1008's 4 mage/r rules supply it from sign(ws60Mage - ws60r), which is the direction his rule
    implies: the Mage pulls r towards itself.
    """
    if DGATE == 'vote':
        v, u, dn, fl = vote40(j, d)
        if v != 0:
            return v, ('the %.0f-min vote, %d UP vs %d DOWN' % (VOTE_MIN, u, dn)), float(u - dn), \
                   _dgdet(j, d)
        c, cd, cu, cf = (0, 0, 0, 0) if VOTE_TIE == 'travel' else c3dir(j, d)
        if c != 0:
            return c, ('C3 broke the %d-%d tie — ws%d-ws%d traj %dD %dU %dF'
                       % (u, dn, C3_LO, C3_HI, cd, cu, cf)), float(cu - cd), _dgdet(j, d)
        r = _traj(R60, j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
        return r['dir'], (('the vote tied %d-%d — travel decides (W_VOTE_TIE=travel)' % (u, dn))
                          if VOTE_TIE == 'travel' else
                          ('the vote AND C3 both tied (%d-%d, %dD %dU %dF) — travel decides'
                           % (u, dn, cd, cu, cf))), r['travel'], _dgdet(j, d, r)
    r = _traj(R60, j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
    if r['dir'] != 0:
        return r['dir'], 'traj', r['travel'], _dgdet(j, d, r)
    g = float(M60[j]) - float(R60[j])
    if g == 0:
        return 0, 'flat and Mage == r', 0.0, _dgdet(j, d, r)
    return (1 if g > 0 else -1), 'the 4 mage/r rules', g, _dgdet(j, d, r)

DG_READ = {}      # (bar, side) -> ws60r's reading as ONE SHORT CELL, for the report's own
                  # column. Written only by `_dgdet`, read only by a report. Nothing branches on
                  # it, and it is keyed by side because the traj is read on the leg's dr.

def _dgdet(j, d, r=None):
    """EVERY NUMBER WS60r RETURNED AT BAR j, as one trace string. Joe 1009.

    Nothing branches on this. It exists so a walk shows what ws60r SAID, not only what the gate
    did with it - in particular the three readings that are invisible otherwise: the reading at
    the oob-run opening, the reading at a run that ends before the dwell completes, and the tail
    the traj actually used.
    """
    if r is None:
        r = _traj(R60, j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
    f = lambda v: ('%+.4f' % v) if np.isfinite(v) else 'n/a'
    rb = r['reversal_bar']
    DG_READ[(j, d)] = '%.2f %s %s' % (float(R60[j]),
                                      {1: 'UP +1', -1: 'DOWN -1', 0: 'FLAT 0'}[int(r['dir'])],
                                      f(float(r['travel'])))
    return ('ws60r %.2f, ws60Mage %.2f, Mage-r %+.2f | traj dir %s, travel %s over its tail of %d '
            'samples = %.1f min (run %d same-signed, %d deferred, the dr-opposed extremum at %s)'
            % (float(R60[j]), float(M60[j]), float(M60[j]) - float(R60[j]),
               {1: 'UP +1', -1: 'DOWN -1', 0: 'FLAT 0'}[int(r['dir'])], f(float(r['travel'])),
               int(r['tail_used']), r['tail_used'] * TRAJ_BLOCK * 5 / 60.0, int(r['run']),
               int(r['deferred']), SC.U(rb) if rb is not None else 'none'))

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
    gate_shut = False      # latched when the gate refused THIS oob run
    exh_x = None           # W_DGATE 'traj': the bar an in-window x-cross fired, awaiting XW12
    b_armed = False        # path 3b: traj said reverse, waiting for ws12r's stall or x-cross
    b_x = None             # that post-dwell x-cross, awaiting XW12
    nox_x = None           # W_TRACE_NOX: the first SUPPRESSED walk x-cross inside this oob run
    nox_r = None           # the rider it fired on
    nox_e = None           # was that cross an EDGE on its rider, or already standing?
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
                if DGATE in ('traj', 'vote') and TRACE_DG:
                    tr.append((j, 'ws60r READ at the oob-run opening — NOT a consultation, the '
                                  'dwell has not run. %s' % _dgdet(j, d)))
            if DGATE in ('traj', 'vote') and hand is None:
                xu = lambda z: float(X[TRIG_TF][z]) < float(R[TRIG_TF][z])
                held = xu(j) if d > 0 else (not xu(j))
                xc = (xu(j) and not xu(j - 1)) if d > 0 else ((not xu(j)) and xu(j - 1))
                # ---- 2: the EXHAUSTION window
                if (j - oob_a) <= EXH_BARS:
                    if exh_x is None and xc:
                        exh_x = j
                        tr.append((j, 'ws%dx crossed ws%dr inside the %d-bar exhaustion window '
                                      '(%.1f min of %.1f) — awaiting %d bars of hold'
                                   % (TRIG_TF, TRIG_TF, EXH_BARS,
                                      (j - oob_a) * 5 / 60.0, EXH_BARS * 5 / 60.0, XW12)))
                    elif exh_x is not None and not held:
                        tr.append((j, 'the exhaustion cross did NOT hold %d bars — cancelled'
                                   % XW12)); exh_x = None
                if exh_x is not None and held and (j - exh_x + 1) >= XW12:
                    tr.append((j, 'EXHAUSTION CONFIRMED — ws%dr never established, ws60r is '
                                  'overridden. A closes here and B opens on the opposite side%s'
                               % (TRIG_TF, (' | THE READING IT OVERRODE: %s' % _dgdet(j, d))
                                  if TRACE_DG else '')))
                    return j, 'ws%dr exhaustion' % TRIG_TF, mae, ceil_bar, hand, tr
                # ---- 3b: traj said reverse; act on ws12r's own stall or x-cross
                if b_armed:
                    if ST[(TRIG_TF, d)][j]:
                        tr.append((j, 'ws%dr STALLED after the dwell — A closes here and B opens '
                                      'on the opposite side' % TRIG_TF))
                        return j, 'ws%dr reversal on stalled' % TRIG_TF, mae, ceil_bar, hand, tr
                    if b_x is None and xc:
                        b_x = j
                        tr.append((j, 'ws%dx crossed ws%dr after the dwell — awaiting %d bars '
                                      'of hold' % (TRIG_TF, TRIG_TF, XW12)))
                    elif b_x is not None and not held:
                        tr.append((j, 'the post-dwell cross did NOT hold %d bars — cancelled'
                                   % XW12)); b_x = None
                    if b_x is not None and held and (j - b_x + 1) >= XW12:
                        tr.append((j, 'ws%dx CROSS CONFIRMED after the dwell — A closes here and B '
                                      'opens on the opposite side' % TRIG_TF))
                        return j, 'ws%dr reversal on x-cross' % TRIG_TF, mae, ceil_bar, hand, tr
            if hand is None and not gate_shut and not b_armed and (j - oob_a) > GATE_BARS:
                if DGATE == 'off':
                    tj, src, tv, det = 0, 'the gate is off', 0.0, ''
                else:
                    tj, src, tv, det = dgate_dir(j, d)
                    if TRACE_DG:
                        tr.append((j, 'ws60r CONSULTED at the dwell-ending — ws%dr oob %.1f min of '
                                      'the %.1f required. %s'
                                   % (TRIG_TF, (j - oob_a) * 5 / 60.0,
                                      (GATE_BARS + 1) * 5 / 60.0, det)))
                if DGATE == 'off' or tj == d:
                    hand = j
                    tr.append((j, 'HANDOVER — ws%dr oob %.1f min; the >ws12 mech owns the exit%s'
                               % (TRIG_TF, (int(SC.ts[j]) - int(SC.ts[oob_a])) / 60000.0,
                                  '' if DGATE == 'off'
                                  else ' (gate OPEN — ws60r traj %+d matches the oob side %+d,'
                                       ' travel %+.4f, from %s)' % (tj, d, tv, src))))
                elif DGATE in ('traj', 'vote'):
                    b_armed = True
                    tr.append((j, 'DELEGATION REFUSED at the dwell-ending — ws60r traj %+d against '
                                  'the oob side %+d (travel %+.4f, from %s). ARMED: B opens on '
                                  'ws%dr\'s next stall or x-cross inside this oob run'
                               % (tj, d, tv, src, TRIG_TF)))
                else:
                    gate_shut = True
                    tr.append((j, 'DELEGATION REFUSED — ws60r traj %+d against the oob side %+d '
                                  '(travel %+.4f, from %s); this oob run never delegates and the '
                                  'walk keeps the exit' % (tj, d, tv, src)))
        else:
            # the oob run broke, so every latch clears with it. Joe 1009: the dwell clock is
            # continuous - any bar where ws12r returns in-bounds resets it.
            if oob_a is not None and DGATE in ('traj', 'vote') and TRACE_DG and hand is None \
               and not b_armed and not gate_shut:
                tr.append((j, 'ws60r NEVER CONSULTED on this oob run — ws%dr returned in-bounds at '
                              '%.2f after %.1f min, and the dwell-ending needs %.1f. The run ended '
                              '%.1f min short, so there was no delegation decision to make. Its '
                              'reading HERE, had it been asked: %s'
                           % (TRIG_TF, float(R[TRIG_TF][j]), (j - oob_a) * 5 / 60.0,
                              (GATE_BARS + 1) * 5 / 60.0,
                              (oob_a + GATE_BARS + 1 - j) * 5 / 60.0, _dgdet(j, d))))
            if oob_a is not None and TRACE_NOX and NOX and j < oob_a + GATE_BARS + 1:
                tr.append((j, 'THE RUN ENDED SHORT OF THE DWELL and %s'
                           % (('a SQUASHED x-cross fired in it at %s on ws%d — Joe 1009\'s rule '
                               'would close A here and open B [the cross was %s]'
                               % (SC.U(nox_x), nox_r,
                                  'an EDGE on ws%d' % nox_r if nox_e
                                  else 'ALREADY STANDING when it entered the run'))
                              if nox_x is not None
                              else 'NO squashed x-cross fired in it — the rule does not fire')))
            if SQX and nox_x is not None and hand is None and j < oob_a + GATE_BARS + 1:
                tr.append((j, 'A CLOSES — ws%dr returned in-bounds at %.2f after %.1f min, short '
                              'of the %.1f-min dwell-ending, and a walk x-cross was squashed in '
                              'the run at %s on ws%d. B opens here on the opposite side.'
                           % (TRIG_TF, float(R[TRIG_TF][j]), (j - oob_a) * 5 / 60.0,
                              (GATE_BARS + 1) * 5 / 60.0, SC.U(nox_x), nox_r)))
                return j, 'ws%dr run short on a squashed x-cross' % TRIG_TF, mae, ceil_bar, hand, tr
            oob_a = None; gate_shut = False; exh_x = None; b_armed = False; b_x = None
            nox_x = None; nox_r = None; nox_e = None
        # CEIL_HI > BASE_HI guards the ceil_hi 12 arm: with CEIL_HI == BASE_HI the assignment
        # leaves `ceil == BASE_HI` true, so this branch re-fired on EVERY later oob crossing and
        # appended a duplicate 'CEILING ws12 -> ws12' line. Behaviour was always identical.
        if CEIL_HI > BASE_HI and ceil == BASE_HI \
           and goob(TRIG_TF, j, d) and not goob(TRIG_TF, j - 1, d):
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
            if (d > 0 and float(MARM[j]) >= SC.HI and float(MARM[j - 1]) < SC.HI) or \
               (d < 0 and float(MARM[j]) <= SC.LO and float(MARM[j - 1]) > SC.LO):
                armed = True
                tr.append((j, 'exit-armed — ws%dMage %s %.0f (%.2f)'
                           % (ARM_TF, 'over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO,
                              float(MARM[j]))))
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
        if NOX and (TRACE_NOX or SQX) and xcond(rider, j, d):
            # the bar the W_NOX=0 build would have EXITED on. Everything after the FIRST one is a
            # path that build never had, so only the first per oob run is named at the run's end.
            first = nox_x is None
            # EDGE vs LEVEL: `xcond` is a level test - ws{rider}x BELOW its target - so it stays
            # true for long stretches. An EDGE is its first true bar after a false one on the same
            # rider. The W_NOX=0 build exits on the first true bar it meets, which need not be an
            # edge: the baton can hand to a rider whose x is ALREADY across.
            edge = not xcond(rider, j - 1, d)
            if first and oob_a is not None:
                nox_x, nox_r, nox_e = j, rider, edge
            if not TRACE_NOX:
                continue
            tr.append((j, 'x-cross SQUASHED on ws%d — W_NOX=1, so the walk did NOT exit here '
                          '(ws%dx %.2f vs its target; %s)'
                       % (rider, rider, float(X[rider][j]),
                          ('inside the ws%dr oob run that opened %s'
                           % (TRIG_TF, SC.U(oob_a))) if oob_a is not None
                          else 'ws%dr is NOT oob on this bar' % TRIG_TF)))
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
