"""rule1_gate — does a wsf_leash signal open the trade gate. Joe 0923/0924.

ONE JOB: given the four r lines and a divergence verdict at one signal bar, say open or closed.
It owns no threshold — the fence, the oob pair, the window and the verdict all arrive as
arguments — and it does not read the DB, build lines, run the divergence, or score anything.

RULE#1, JOE VERBATIM 0923:
  "a sig_utc timestamp must be qualified by ws1r and (ws2r or ws3r) exiting the same fence,
   within {knob:4} minutes of each other. -the fence is 27:73"
  and his rulings that followed, each one a separate answer:
    0923  "1, exiting the same edge, on dr side / 2, dr side / 3, between sig_utc and the `r`
           lines / 4, within (either side) / 7, `rule1_tol`"
    0924  "update the `r` line qualification - the lines can be qualifed at any time they are
           outside of the fence"          -> no dwell, one bar outside is enough
    0924  "I was wrong about the tolerance. change it to 7 minutes"
    0924  "so far, it looks like the dwell is hurting so we'll drop it"
    0923  "disable this ws1Mage-support mech for now"   -> the ws1Mage override is NOT here

THE SCENARIO, JOE 0924:
  "how often do you see the scenario of ws1 diverging away from dr while ws2r, ws3r, and gcws30r
   are oob on dr side?  test at each wsl_sig_utc"
  then, on the window: "the same 7 minute window that we've been using since last night"
  then: "bake it into rule#1 and recreate the gate data"
  Joe has not named this mechanic. `scenario` is his own word for it, used here rather than a
  coined one.

  `anchor_floater` can only return the dr's own sign or zero — its step 4 fires bearish at dr +1
  and bullish at dr -1, never the opposite — so "diverging away from dr" is exactly a non-zero
  verdict. Joe 0924 confirmed the direction: "-1dr = low board = launchpad for a long postion".

OOB IS 15/85. Always. 27/73 is rule#1's fence, 25/75 is the Mage fence, 17/83 is the r-momo
fence. They are four different numbers and this module keeps them apart by never defaulting one.

MINE, AND UNRULED BY JOE
  the OR            he said "bake it into rule#1", not how the two legs combine. A row-level OR
                    is what this module does. On the 121-row v7 bank it adds 3 rows at 2 distinct
                    timestamps, which is what Joe's own chart read said it should add
  the comparison    STRICTLY outside the fence and STRICTLY outside oob, never >= or <=. Measured
                    on the same 121 rows: switching to inclusive changes 0 rows
  `dwell_bars`      reports the rule#1 leg only, so a row opened by the scenario alone reads 0.
                    It is a reporting field, never a gate — Joe dropped dwell as a gate on 0924

NOT CAUSAL AT THE SIGNAL BAR. Joe 0924 ruled the window is "either side" of sig_utc, so the gate
reads up to `tol_bars` AFTER the signal and is only knowable that far past it. At tol_bars 42 the
verdict lands 210 s late. That is his rule, stated here so no caller mistakes it for a live gate.

THE WINDOW IS BACKWARD-ONLY NOW - Joe 0929: *"the -3.5 and + 3.5 logic is what's making it
non-causal, so let's drop the forward and simply say: if I see the `r` lines correctly positioned (or
the #1 mode that allows for divergence), inside of the last {knob:7} minutes, then rule#1 is
qualified"*.

  the `r` lines correctly positioned   = the rule#1 leg, ws1r outside AND (ws2r OR ws3r) outside
  the #1 mode that allows divergence   = the scenario leg
  inside of the last 7 minutes         = [k - 84 bars, k]

WHAT IT REPLACED, AND WHY.  The v1 build used `[k - tol, k + tol]` at `rule1_tol` 7 min TOTAL, so it
read 42 bars = 210 s AFTER the signal bar, and `longest_outside` walked a run forward with no bound
at all. A verdict at bar `k` was not knowable at bar `k`. Joe 0929 asked for everything causal, was
shown the cost, and dropped the forward half.

BOTH SHAPES STILL RUN, because the v1 trades are banked and must stay reproducible:
    config v1   back 3.5 min, fwd 3.5 min, run_clamp 'none'    the original, NOT causal
    config v2   back 7.0 min, fwd 0,       run_clamp 'window'  Joe's rule, causal

MEASURED over the 109 distinct v7 sig bars, 2026-09-01..09-06:
    v1  gate open 64   closed 45
    v2  gate open 68   closed 41      18 verdicts change: 7 open->closed, 11 closed->open
"""
import numpy as np


def longest_outside(v, dr, k, back_bars, fence, fwd_bars=0, run_clamp='window'):
    """The longest CONTIGUOUS run of bars strictly outside `fence` on the dr side, touching the
    window [k - back_bars, k + fwd_bars]. -> length in bars, 0 when the line never leaves.

    The run is measured WHOLE to the LEFT: a run that starts before the window and is still out at
    `k` counts its full length backward. Joe 0924 asked for "the run length", and clipping the left
    edge would report the window's width instead of the line's behaviour.

    `run_clamp` decides how far RIGHT the run may be measured, and it is the causality knob:
      'window'  stop at the window's right edge, `k + fwd_bars`. At `fwd_bars` 0 that is `k`
      'none'    walk right with no bound at all - what the v1 build did, and NOT causal
    """
    v = np.asarray(v, float)
    out = (v > fence[1]) if dr > 0 else (v < fence[0])
    a = max(0, int(k) - int(back_bars))
    b = min(len(out) - 1, int(k) + int(fwd_bars))
    lim = (len(out) - 1) if run_clamp == 'none' else b
    best, i = 0, a
    while i <= b:
        if not out[i]:
            i += 1
            continue
        s = i
        while s > 0 and out[s - 1]:
            s -= 1
        e = i
        while e + 1 <= lim and out[e + 1]:
            e += 1
        best = max(best, e - s + 1)
        i = e + 1
    return best


def bars_oob(v, dr, k, back_bars, oob, fwd_bars=0):
    """How many bars INSIDE the window [k - back_bars, k + fwd_bars] sit strictly out of bounds on
    the dr side. -> count.

    dr -1 counts bars below oob[0], dr +1 counts bars above oob[1]. Unlike `longest_outside` this
    one is a plain window count, because the scenario asks only whether the line was there.
    """
    v = np.asarray(v, float)
    a = max(0, int(k) - int(back_bars))
    b = min(len(v) - 1, int(k) + int(fwd_bars))
    seg = v[a:b + 1]
    return int(((seg < oob[0]) if dr < 0 else (seg > oob[1])).sum())


def gate(r1, r2, r3, g30r, dr, k, back_bars, fence, oob, div_fired,
         fwd_bars=0, run_clamp='window'):
    """The gate at signal bar `k`. -> a dict, never None.

    r1, r2, r3   ws1r, ws2r, ws3r on the 5 s grid
    g30r         gcws30r, resampled onto the same grid
    dr           the signal's own dr, +1 or -1
    back_bars    how far BACK the window reaches, in bars
    fwd_bars     how far FORWARD. 0 is causal. 42 reproduces the v1 build
    run_clamp    'window' stops a run at the right edge, 'none' walks it forward unbounded (v1)
    fence        rule#1's pair, (27.0, 73.0). NOT oob
    oob          (15.0, 85.0). Always
    div_fired    `anchor_floater(...)['fired']` for ws1r at this bar, or 0 when it returned None

    keys: rule1, scenario, open, ws1_bars, ws2_bars, ws3_bars, dwell_bars,
          ws2_oob, ws3_oob, g30_oob
    """
    dr = int(dr)
    l1 = longest_outside(r1, dr, k, back_bars, fence, fwd_bars, run_clamp)
    l2 = longest_outside(r2, dr, k, back_bars, fence, fwd_bars, run_clamp)
    l3 = longest_outside(r3, dr, k, back_bars, fence, fwd_bars, run_clamp)
    rule1 = bool(l1) and bool(l2 or l3)

    c2 = bars_oob(r2, dr, k, back_bars, oob, fwd_bars)
    c3 = bars_oob(r3, dr, k, back_bars, oob, fwd_bars)
    cg = bars_oob(g30r, dr, k, back_bars, oob, fwd_bars)
    scenario = bool(div_fired) and bool(c2) and bool(c3) and bool(cg)

    return {'rule1': rule1, 'scenario': scenario, 'open': rule1 or scenario,
            'ws1_bars': l1, 'ws2_bars': l2, 'ws3_bars': l3,
            'dwell_bars': min(l1, max(l2, l3)) if rule1 else 0,
            'ws2_oob': c2, 'ws3_oob': c3, 'g30_oob': cg}
