"""walk_mom_models — Joe's test-point walk, 0912. Table `wsf_dtf_mom_models`.

HIS LOOP, VERBATIM:
    -on each dr flip
    --walk to same-side-dr ws1Mage crossing to oob
    ---walk to the next ws1r sideways or reverse (the test-point)
    ----scan the ws2r line for momentum-true
    ----for each r line (only ws2r for now) that continues to the dr-side fence exit, but is not
        printing momentum-true at the test-point:
    -----sweep your collection of mechs until you have a momentum-true state for the line
    -----store the config (in a db table), and make it your working config
    -----create a fake dr flip
    -----loop back to `walk to same-side-dr ws1Mage crossing to oob` and continue
    ------if the next test-point does not see momentum-true for ws2r
    -------sweep again, find a config that works for both this ws2r test-point AND the previous

EVERY CONCRETION BELOW IS JOE'S, ANSWERED 0912, EXCEPT THE FOUR MARKED MINE.
"""
import os, sys, time, datetime as dt
from datetime import timezone
import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import override, mech_lines
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.compute.momo_seam import seam_mask, seam_toward_dr
import optimus9.compute.momo_core as X
from optimus9.analysis.jig import sideways_reversal
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key

WALK        = 5                        # walks 1-4 stay; 5 adds the 35 min reach, the
#                                        20/80 exit fence and the ws3 fallback
START_UTC   = '2026-08-25 01:51:00'   # Joe 0912: "starting point: dr 1, 08-25 01:51"
START_DR    = +1                      # Joe 0912
MAGE_HI, MAGE_LO = 75.0, 25.0         # the 25/75 fence, build_wsf_dtf_v3
MAGE_DWELL  = 6                       # Joe: "the next walk begins at the opposing dr's ws1Mage oob
#                                       cross (oob-dwell=6)". 6 bars = 30 s
FENCE_HI, FENCE_LO = 83.0, 17.0       # THE SPENT TEST'S fence. Joe 0912 fixed it at 17/83 and
#                                       0913 kept it there when the exit fence moved: "20/80 for
#                                       the exit only"
EXIT_HI, EXIT_LO   = 80.0, 20.0       # THE FENCE-EXIT TEST'S fence. Joe 0913: "use a 20/80 fence"
# SPENT MOMENTUM, Joe 0912: "if ws2r is outside (or almost outside) the r-momo-fence at the
# test-point, then keep walking to the next dr flip". He set the edges at 17/83 with NO margin -
# "let's stick with 17/83, no margin. we can review when this scenario recurs" - and the test reads
# the dr SIDE only: at dr -1 a line past the LOW edge is spent, one past the high edge is not.
# The walk then resumes at the next REAL latch flip, not at a planted one.
REACH_BARS  = 420                     # Joe 0913: "let's double it: 35 minutes". 420 bars.
#                                       It was 216 bars = 18 minutes, from his 0912 reading of the
#                                       maximum ws1 oob-to-oob excursion
OOB_HI, OOB_LO = 85.0, 15.0           # Joe 0913: "oob is alwasy 15/85". This is the ws1r oob test,
#                                       and it is NOT the momo-fence-r 17/83 used for the fence exit
R_DWELL_WOB = 2                       # KNOB, Joe 0913: "add `r` dwell as a knob, but don't sweep it
#                                       during this walk. set the default to wob 2". He chose wob
#                                       semantics over dwell semantics, so 2 STEPS spans 3 bars=15 s
R_OOB_BARS  = R_DWELL_WOB + 1         # the oob run must REACH this many bars
SPAN_MIN    = 10                      # the lattice span the chain runs at
WALL_SECS   = 54000                   # Joe 0913: "you can run the test for the next 15 hours.
#                                       the cap is now time based, you can run past the set date
#                                       range if needed". 15 h. It was 7200 s on 0912.
TICK_SECS   = 900                     # Joe 0912: "with updates sent every 15 minutes"

# WS1 IS HELD FIXED FOR WALK 1. Joe 0912: "stabilise the ws1 config". These are the live chain's.
WS1_CFG = dict(momo_slope_min=0.4, momo_slack_ref=0.4, momo_r2_min=0.7,
               level_slack=13.9, momo_seam='off')
# THE WORKING CONFIG AT CYCLE 1 - MINE. Something has to be in hand before the first test-point,
# and the live chain is what the system runs today.
CFG0 = dict(WS1_CFG)

# THE GRID, Joe 0912. Step 0.05 ("use sweep steps that are more granular, eg 0.05"), ranges agreed,
# level_slack's step MINE at 1.0 ("level_slack's range dictates less granular than 0.05. your
# choice"), the momo_slope_min order MINE ("ultimately, the whole range will be tested so I'm
# agnostic"). Walked LOOSEST FIRST - Joe 0912: "work from the loosest outwards".
G_SLACK  = [40.0 - i for i in range(27)] + [13.9]          # 40.0 down to 14.0, then 13.9
G_R2     = [round(0.05 * i, 2) for i in range(20)]          # 0.00 up to 0.95
G_SREF   = [round(0.05 * (i + 1), 2) for i in range(24)]    # 0.05 up to 1.20
G_SLOPE  = [round(0.05 * (i + 1), 2) for i in range(24)]    # 0.05 up to 1.20
G_SEAM   = ['skip_r2', 'off']
G_GATE   = ['none', 'lower TF momentum-true', 'lower r beyond', 'lower Mage beyond']
GRID_N   = len(G_SLACK) * len(G_R2) * len(G_SREF) * len(G_SLOPE) * len(G_SEAM) * len(G_GATE)


def grid():
    """The collection, in Joe's order: loosest first, last dimension varying fastest."""
    for sk in G_SLACK:
        for r2 in G_R2:
            for sr in G_SREF:
                for sl in G_SLOPE:
                    for sm in G_SEAM:
                        for gt in G_GATE:
                            yield dict(level_slack=sk, momo_r2_min=r2, momo_slack_ref=sr,
                                       momo_slope_min=sl, momo_seam=sm, gate=gt)


def knobstr(c):
    return (f"sl{c['momo_slope_min']:g}_sr{c['momo_slack_ref']:g}_r2{c['momo_r2_min']:g}"
            f"_sk{c['level_slack']:g}_sm{c['momo_seam']}_g{c['gate'].replace(' ', '')}")


def load():
    db = DatabaseManager(**get_db_config()); db.connect()
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                    'WHERE sys_pk=1', fetch=True)[0]
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']; spec[g['role']] = (s_, m_)
    bk = {tf: momo_bank(db, tf, version=1) for tf in (1, 2, 3, 4)}
    db.disconnect()
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    ln = lambda tf, role: np.load(os.path.join(
        LINE_DIR, _line_key(END_MS, HOURS, WARMUP, override(tf * 60, *spec[role])) + '.npy'))
    return ts, bk, dict(r1=ln(1, 'r'), m1=ln(1, 'Mage'), r2=ln(2, 'r'), m2=ln(2, 'Mage'),
                        r3=ln(3, 'r'), m3=ln(3, 'Mage'), r4=ln(4, 'r'), m4=ln(4, 'Mage'),
                        m13=ln(13, 'm'))


def momentum_true(line, bank, cfg, dr, k, seam, tf, strip_mom_at_fence=None):
    """Is `line` momentum-true at bar k under `cfg`. momo, or curl facing dr - Joe's rule.
    DELEGATES to momo_g_why; the seam fact is measured in momo_seam and handed over.

    REFACTORED 0920. This used to inline momo_fit / verdict / curl_gates so it could set seam_dr
    between the fit and the verdict - a second copy of momo_g_why's body, which is exactly the fork
    momo_gated was written to prevent. momo_g_why now takes seam_dr, so there is one verdict path.

    strip_mom_at_fence is STRIP-MOM-AT-FENCE, Joe 0920. Pass the r-momo-fence as (lo, hi) to strip
    the tag from a line that has exited it on the dr side at bar k. None is off.
    """
    b = dict(bank); b.update({q: cfg[q] for q in
                              ('momo_slope_min', 'momo_slack_ref', 'momo_r2_min',
                               'level_slack', 'momo_seam')})
    with momo_config(b), momo_window(SPAN_MIN):
        # idx0 MUST be read inside momo_window - it mutates X.MOMO_SAMPLES for the duration
        # (momo_gated.py:195). Computing it outside silently uses the module default window.
        idx0 = k - (X.MOMO_SAMPLES - 1) * X.MOMO_STEP_BARS
        sd = seam_toward_dr(line, seam, idx0, k, dr)
        from optimus9.compute.momo_gated import momo_g_why
        st, why, f = momo_g_why(line, dr, k, quad=True, gate2=True, seam_dr=sd,
                                strip_mom_at_fence=strip_mom_at_fence)
    return st in ('momo', 'curl'), st


def gate_ok(name, L, dr, k, banks, seams, tf):
    """The lower-TF gate, read RELATIVE to the line under test.

    Joe 0912 described it as "the r and Mage value of the TF BELOW it", so testing ws3 reads ws2,
    and the same config later applied to ws2 reads ws1. Hard-coding ws1/ws2 while testing ws3 would
    contradict his own words. MINE, and unruled - the alternative is a fixed ws1/ws2 pair."""
    if name == 'none':
        return True
    lo = tf - 1
    if lo < 1:
        return True                                  # ws1 has no TF below it
    rl, ml = L[f'r{lo}'], L[f'm{lo}']
    if name == 'lower TF momentum-true':
        cfg = WS1_CFG if lo == 1 else WS1_CFG        # walk 1 holds ws1 fixed; the lower line is
        #                                              read at the same held config, Joe 0913
        t, _ = momentum_true(rl, banks[lo], cfg, dr, k, seams[lo], lo)
        return t
    if name == 'lower r beyond':
        return bool(rl[k] < L[f'r{tf}'][k]) if dr < 0 else bool(rl[k] > L[f'r{tf}'][k])
    if name == 'lower Mage beyond':
        return bool(ml[k] < L[f'm{tf}'][k]) if dr < 0 else bool(ml[k] > L[f'm{tf}'][k])
    raise ValueError(name)


def dr_latch(m1, m13, i0, i1):
    """The dr series, VERBATIM from build_wsf_dtf_v3: ws1Mage AND ws13m both oob, SAME side,
    latched. The previous dr holds until both agree on a side."""
    out = np.zeros(len(m1), np.int8); cur = 0
    for k in range(int(i0), int(i1) + 1):
        a, b = float(m1[k]), float(m13[k])
        if a == a and b == b:
            if a >= MAGE_HI and b >= MAGE_HI:   cur = +1
            elif a <= MAGE_LO and b <= MAGE_LO: cur = -1
        out[k] = cur
    return out


def next_real_flip(DR, k0, i1):
    """The first bar after k0 where the latch changes the dr. Joe 0912 chose this over a planted
    flip: "resume at the next real latch flip ... at whatever dr it sets"."""
    for k in range(int(k0) + 1, int(i1) + 1):
        if DR[k] != DR[k - 1] and DR[k] != 0:
            return k, int(DR[k])
    return None, None


def spent(r2, dr, k):
    """Is ws2r already past the dr-SIDE fence edge at the test-point. Joe 0912."""
    return bool(r2[k] >= FENCE_HI) if dr > 0 else bool(r2[k] <= FENCE_LO)


def mage_oob_start(m1, dr, k0):
    """The first bar at or after k0 where ws1Mage's run oob ON THE dr SIDE reaches MAGE_DWELL.
    dr +1 -> at or above 75. dr -1 -> at or below 25."""
    oob = (m1 >= MAGE_HI) if dr > 0 else (m1 <= MAGE_LO)
    run = 0
    for k in range(int(k0), len(m1)):
        run = run + 1 if oob[k] else 0
        if run >= MAGE_DWELL:
            return k
    return None


def r_oob_start(r1, dr, k0):
    """The first bar at or after k0 where ws1r's run oob ON THE dr SIDE reaches R_OOB_BARS.
    Joe 0913: "after walking to ws1Mage, the walk needs to walk to the next oob ws1r", at 15/85."""
    oob = (r1 >= OOB_HI) if dr > 0 else (r1 <= OOB_LO)
    run = 0
    for k in range(int(k0), len(r1)):
        run = run + 1 if oob[k] else 0
        if run >= R_OOB_BARS:
            return k
    return None


def fence_exit(r, dr, k0, reach):
    """The first bar in (k0, k0+reach] where `r` is outside the EXIT fence on the dr side.
    Joe 0913 set this fence to 20/80, separately from the spent test's 17/83."""
    hi = int(min(len(r) - 1, k0 + reach))
    for k in range(int(k0) + 1, hi + 1):
        if (r[k] >= EXIT_HI) if dr > 0 else (r[k] <= EXIT_LO):
            return k
    return None


def bank_row(db, **kw):
    cols = list(kw); vals = [kw[c] for c in cols]
    db.execute(f"INSERT INTO wsf_dtf_mom_models ({','.join(cols)}) "
               f"VALUES ({','.join(['%s'] * len(cols))}) ON DUPLICATE KEY UPDATE "
               + ','.join(f'{c}=VALUES({c})' for c in cols), tuple(vals))


def main():
    t_start = time.time(); t_tick = t_start
    ts, BK, L = load()
    SEAM = {tf: seam_mask(ts, tf) for tf in (1, 2, 3, 4)}
    seam1, seam2 = SEAM[1], SEAM[2]
    ms = lambda x: int(dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
                       .replace(tzinfo=timezone.utc).timestamp() * 1000)
    U = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc)
    us = lambda i: U(i).strftime('%m-%d %H:%M:%S')
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute('DELETE FROM wsf_dtf_mom_models WHERE wdm_walk=%s', (WALK,))
    # the latch, warmed from 08-23 the way build_wsf_dtf_v3 warms it
    i_warm = int(np.searchsorted(ts, ms('2026-08-23 00:00:00')))
    i_end = len(ts) - 1
    DR = dr_latch(L['m1'], L['m13'], i_warm, i_end)

    print(f'  walk {WALK}. start {START_UTC} dr {START_DR:+d}. grid {GRID_N:,} configurations.', flush=True)
    print(f'  ws1 held at slope {WS1_CFG["momo_slope_min"]} / straightness {WS1_CFG["momo_r2_min"]} '
          f'/ slack {WS1_CFG["level_slack"]} / seam {WS1_CFG["momo_seam"]}', flush=True)
    print(f'  fence reach {REACH_BARS} bars = {REACH_BARS*5//60} minutes. wall limit '
          f'{WALL_SECS//60} minutes, update every {TICK_SECS//60}.', flush=True)
    print(flush=True)

    cfg = dict(CFG0)                 # the working config
    POOL = []                        # Joe 0913: test-points that no line could carry, drawn on
    #                                  when the forward walk stalls
    points = []                      # every accumulated test-point: (bar, dr, line)
    k = int(np.searchsorted(ts, ms(START_UTC))); dr = START_DR
    cycle = 0
    while time.time() - t_start < WALL_SECS:
        cycle += 1
        mk = mage_oob_start(L['m1'], dr, k)
        if mk is None:
            print(f'  cycle {cycle}: ws1Mage never reaches the dr {dr:+d} side again. stop.', flush=True); break
        # THE ws1r OOB STEP, Joe 0913. From the ws1Mage event, race the dr-side ws1r oob against an
        # OPPOSITE-dr ws1Mage oob. If the opposite Mage lands first the walk ABANDONS this dr -
        # "it abandons it. treat a dr flip as a fresh start" - and restarts its event hunt there.
        rk = r_oob_start(L['r1'], dr, mk)
        ok = mage_oob_start(L['m1'], -dr, mk)
        if ok is not None and (rk is None or ok < rk):
            print(f'  cycle {cycle}  dr {dr:+d}  ws1Mage oob {us(mk)}  -> no dr {dr:+d} ws1r oob first; '
                  f'opposite ws1Mage oob {us(ok)} abandons this dr', flush=True)
            cycle -= 1; dr = -dr; k = ok; continue
        if rk is None:
            print(f'  cycle {cycle}: ws1r never reaches oob on the dr {dr:+d} side again. stop.', flush=True); break
        ev = sideways_reversal(L['r1'], np.zeros(len(ts)), dr, i0=rk, first=True)
        if not ev:
            print(f'  cycle {cycle}: no ws1r sideways after {us(rk)}. stop.', flush=True); break
        tp = ev[0][0]
        fx = fence_exit(L['r2'], dr, tp, REACH_BARS)
        now_true, st = momentum_true(L['r2'], BK[2], cfg, dr, tp, seam2, 2)
        sp = spent(L['r2'], dr, tp)
        print(f'  cycle {cycle}  dr {dr:+d}  ws1Mage oob {us(mk)}  ws1r oob {us(rk)}  test-point {us(tp)}  '
              f'ws2r {L["r2"][tp]:.2f} reads {st}  fence exit '
              f'{us(fx) if fx is not None else f"none inside {REACH_BARS*5//60} min"}'
              f'{"  SPENT - already past the dr-side fence edge" if sp else ""}', flush=True)

        if sp:
            # Joe 0912: "if ws2r is outside ... the r-momo-fence at the test-point, then keep
            # walking to the next dr flip". The next REAL latch flip, at whatever dr it sets.
            bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=2, wdm_dr=dr,
                     wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='spent-momentum',
                     wdm_fence_exit_utc=U(fx).replace(tzinfo=None) if fx is not None else None,
                     wdm_of=len(points),
                     wdm_note=f'ws2r {L["r2"][tp]:.2f} already past the dr {dr:+d} fence edge '
                              f'{FENCE_HI if dr > 0 else FENCE_LO:g}; walked on to the next real flip')
            nk, ndr = next_real_flip(DR, tp, i_end)
            if nk is None:
                print(f'  cycle {cycle}: no further real latch flip after {us(tp)}. stop.', flush=True); break
            print(f'    spent -> next real latch flip {us(nk)} dr {ndr:+d}', flush=True)
            dr = ndr; k = nk
        elif fx is None and fence_exit(L['r3'], dr, tp, REACH_BARS) is not None:
            # THE ws3 FALLBACK, Joe 0913: "if you can't get a ws2 within 35 minutes and 20/80 fence,
            # look to ws3 on the same 35min,20/80". A SEPARATE mechanic from the stalemate
            # digression, his choice 0913. The test-point is banked against ws3 and joins the
            # accumulated set as a ws3 entry; the next cycle goes back to ws2.
            fx3 = fence_exit(L['r3'], dr, tp, REACH_BARS)
            t3, st3 = momentum_true(L['r3'], BK[3], cfg, dr, tp, SEAM[3], 3)
            print(f'    ws2 has no exit; ws3 {L["r3"][tp]:.2f} reads {st3}, exit {us(fx3)}', flush=True)
            points.append((tp, dr, 3))
            if t3 and gate_ok(cfg.get('gate', 'none'), L, dr, tp, BK, SEAM, 3):
                bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=3, wdm_dr=dr,
                         wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='momentum',
                         wdm_digression='ws3-fallback',
                         wdm_fence_exit_utc=U(fx3).replace(tzinfo=None),
                         wdm_momo_slope_min=cfg['momo_slope_min'],
                         wdm_momo_slack_ref=cfg['momo_slack_ref'],
                         wdm_momo_r2_min=cfg['momo_r2_min'], wdm_level_slack=cfg['level_slack'],
                         wdm_momo_seam=cfg['momo_seam'], wdm_lower_gate=cfg.get('gate', 'none'),
                         wdm_knobs=knobstr({**cfg, 'gate': cfg.get('gate', 'none')}),
                         wdm_satisfies=len(points), wdm_of=len(points),
                         wdm_note=f'ws2 had no exit; ws3 {L["r3"][tp]:.2f} already {st3}')
                dr = -dr; k = fx3 + 1
            else:
                print(f'    sweeping {GRID_N:,} configurations against {len(points)} test-point(s)'
                      f' [ws3 fallback]...', flush=True)
                found = None; tried = 0
                for c in grid():
                    tried += 1
                    ok = True
                    for (pb, pd, pl) in points:
                        t, _ = momentum_true(L[f'r{pl}'], BK[pl], c, pd, pb, SEAM[pl], pl)
                        if not (t and gate_ok(c['gate'], L, pd, pb, BK, SEAM, pl)):
                            ok = False; break
                    if ok:
                        found = c; break
                    if time.time() - t_tick >= TICK_SECS:
                        t_tick = time.time()
                        print(f'    [{dt.datetime.now():%H:%M:%S}] cycle {cycle} [ws3]: {tried:,} of '
                              f'{GRID_N:,} tried, none yet satisfies all {len(points)}', flush=True)
                    if time.time() - t_start >= WALL_SECS:
                        break
                if found is None:
                    print(f'    ws3 fallback found nothing in {tried:,}. pooling this test-point.',
                          flush=True)
                    points.pop(); POOL.append((tp, dr))
                    bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=3, wdm_dr=dr,
                             wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='pooled',
                             wdm_digression='ws3-fallback',
                             wdm_fence_exit_utc=U(fx3).replace(tzinfo=None),
                             wdm_satisfies=0, wdm_of=len(points) + 1,
                             wdm_note=f'{tried:,} tried on ws3, none works with the rest')
                else:
                    cfg = dict(found)
                    bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=3, wdm_dr=dr,
                             wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='swept',
                             wdm_digression='ws3-fallback',
                             wdm_fence_exit_utc=U(fx3).replace(tzinfo=None),
                             wdm_momo_slope_min=cfg['momo_slope_min'],
                             wdm_momo_slack_ref=cfg['momo_slack_ref'],
                             wdm_momo_r2_min=cfg['momo_r2_min'], wdm_level_slack=cfg['level_slack'],
                             wdm_momo_seam=cfg['momo_seam'], wdm_lower_gate=cfg['gate'],
                             wdm_knobs=knobstr(cfg), wdm_satisfies=len(points), wdm_of=len(points),
                             wdm_note=f'ws2 had no exit; first working config, {tried:,} tried')
                    print(f'    -> {knobstr(cfg)}   after {tried:,} tried', flush=True)
                dr = -dr; k = fx3 + 1
        elif fx is None:
            bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=2, wdm_dr=dr,
                     wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='no-continuation',
                     wdm_note=f'ws2r {L["r2"][tp]:.2f} reads {st}; no dr-side fence exit inside {REACH_BARS*5//60} min',
                     wdm_of=len(points))
            dr = -dr; k = tp + 1                      # Joe: "note it ... then break - dr flip and keep walking"
        elif now_true:
            bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=2, wdm_dr=dr,
                     wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='momentum',
                     wdm_fence_exit_utc=U(fx).replace(tzinfo=None),
                     wdm_momo_slope_min=cfg['momo_slope_min'], wdm_momo_slack_ref=cfg['momo_slack_ref'],
                     wdm_momo_r2_min=cfg['momo_r2_min'], wdm_level_slack=cfg['level_slack'],
                     wdm_momo_seam=cfg['momo_seam'], wdm_lower_gate=cfg.get('gate', 'none'),
                     wdm_knobs=knobstr({**cfg, 'gate': cfg.get('gate', 'none')}),
                     wdm_satisfies=len(points) + 1, wdm_of=len(points) + 1,
                     wdm_note=f'ws2r {L["r2"][tp]:.2f} already {st} under the working config')
            points.append((tp, dr, 2)); dr = -dr; k = fx + 1
        else:
            points.append((tp, dr, 2))
            print(f'    sweeping {GRID_N:,} configurations against {len(points)} test-point(s)...', flush=True)
            found = None; tried = 0
            for c in grid():
                tried += 1
                ok = True
                for (pb, pd, pl) in points:
                    t, _ = momentum_true(L[f'r{pl}'], BK[pl], c, pd, pb, SEAM[pl], pl)
                    if not (t and gate_ok(c['gate'], L, pd, pb, BK, SEAM, pl)):
                        ok = False; break
                if ok:
                    found = c; break
                if time.time() - t_tick >= TICK_SECS:
                    t_tick = time.time()
                    print(f'    [{dt.datetime.now():%H:%M:%S}] cycle {cycle}: {tried:,} of {GRID_N:,} '
                          f'configurations tried, none yet satisfies all {len(points)} test-points',
                          flush=True)
                if time.time() - t_start >= WALL_SECS:
                    break
            if found is None:
                print(f'    STALEMATE at cycle {cycle}: no configuration satisfies all '
                      f'{len(points)} test-points. {tried:,} tried.', flush=True)
                # THE DIGRESSION, Joe 0912/0913. "run the same logic on ws3 and ws4. if either exit
                # the fence and a sweep config gives them momentum at the test-point, bank the
                # config and continue the loop on ws2 only (until the next stalemate)".
                #   - the config need only satisfy THE ONE TEST-POINT IT IS TESTED AT, Joe 0913
                #   - "i stop at the first that works", so ws3 is tried before ws4
                #   - "mark the ws2 as dropped so that the loop can continue"
                #   - "if neither works, mark it for later review and keep walking"
                # DROPPING THE ws2 TEST-POINT IS FORCED IN BOTH CASES: it is unsatisfiable, so
                # leaving it in the accumulated list would stall the very next sweep identically.
                dig = None; dig_cfg = None; dig_tried = 0
                for tf in (3, 4):
                    rl = L[f'r{tf}']
                    fxl = fence_exit(rl, dr, tp, REACH_BARS)
                    if fxl is None:
                        print(f'    digression ws{tf}: {rl[tp]:.2f} at the test-point, no dr-side '
                              f'fence exit inside 18 min - not a line that continued', flush=True)
                        continue
                    for c in grid():
                        dig_tried += 1
                        t, _ = momentum_true(rl, BK[tf], c, dr, tp, SEAM[tf], tf)
                        if t and gate_ok(c['gate'], L, dr, tp, BK, SEAM, tf):
                            dig, dig_cfg = f'ws{tf}', dict(c); break
                        if time.time() - t_start >= WALL_SECS:
                            break
                    if dig:
                        print(f'    digression ws{tf}: {rl[tp]:.2f} at the test-point, fence exit '
                              f'{us(fxl)}, config found after {dig_tried:,} tried -> '
                              f'{knobstr(dig_cfg)}', flush=True)
                        break
                    print(f'    digression ws{tf}: fence exit {us(fxl)}, but no configuration in '
                          f'{dig_tried:,} gives it momentum at the test-point', flush=True)
                bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=2, wdm_dr=dr,
                         wdm_testpoint_utc=U(tp).replace(tzinfo=None),
                         wdm_outcome='stalemate-dropped',
                         wdm_digression=dig or 'none-worked',
                         wdm_fence_exit_utc=U(fx).replace(tzinfo=None),
                         wdm_satisfies=0, wdm_of=len(points),
                         wdm_note=f'{tried:,} tried on ws2; ws2 test-point dropped so the walk '
                                  f'continues' + ('' if dig else '. MARKED FOR LATER REVIEW'))
                points.pop()                       # drop the unsatisfiable ws2 test-point
                if dig:
                    cfg = dict(dig_cfg)
                    bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=int(dig[2:]), wdm_dr=dr,
                             wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='digression',
                             wdm_digression=dig,
                             wdm_momo_slope_min=cfg['momo_slope_min'],
                             wdm_momo_slack_ref=cfg['momo_slack_ref'],
                             wdm_momo_r2_min=cfg['momo_r2_min'], wdm_level_slack=cfg['level_slack'],
                             wdm_momo_seam=cfg['momo_seam'], wdm_lower_gate=cfg['gate'],
                             wdm_knobs=knobstr(cfg), wdm_satisfies=1, wdm_of=1,
                             wdm_note=f'{dig_tried:,} tried; satisfies this test-point only, '
                                      f'per Joe 0913')
                dr = -dr; k = fx + 1
                continue
            cfg = dict(found)
            bank_row(db, wdm_walk=WALK, wdm_cycle=cycle, wdm_line=2, wdm_dr=dr,
                     wdm_testpoint_utc=U(tp).replace(tzinfo=None), wdm_outcome='swept',
                     wdm_fence_exit_utc=U(fx).replace(tzinfo=None),
                     wdm_momo_slope_min=cfg['momo_slope_min'], wdm_momo_slack_ref=cfg['momo_slack_ref'],
                     wdm_momo_r2_min=cfg['momo_r2_min'], wdm_level_slack=cfg['level_slack'],
                     wdm_momo_seam=cfg['momo_seam'], wdm_lower_gate=cfg['gate'],
                     wdm_knobs=knobstr(cfg), wdm_satisfies=len(points), wdm_of=len(points),
                     wdm_note=f'first working configuration, {tried:,} tried')
            print(f'    -> {knobstr(cfg)}   after {tried:,} tried', flush=True)
            dr = -dr; k = fx + 1
    print(f'\n  stopped after {time.time()-t_start:.0f}s, {cycle} cycles', flush=True)
    db.disconnect()


if __name__ == '__main__':
    sys.exit(main() or 0)
