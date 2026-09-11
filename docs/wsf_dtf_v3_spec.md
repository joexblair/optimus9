# wsf-dtf-v3 — spec

Opened 0911 on Joe's word: *"we're going to begin the v3 spec build"* / *"open a wsfdtfv3 spec
doc"* / *"bank the report's details in the doc, and add a knobs section"*.

Producer `build_wsf_dtf_v3.py`. Table `wsf_dtf_v3`.

This doc is the spec. `docs/tf_walk_spec.md` holds the TF2-23 walk and the Mage-crosses-boundary
signal; the wsf-dtf-v3 material there is the build record, and this doc supersedes it as the spec.

---

## 1. The bands

Joe 0911, verbatim:

> spec: wsf = the lines between ws1 and ws12. sub-wsf = gcws30 to ws4. dtf = ws13 to ws23

| band | lines |
|---|---|
| sub-wsf | gcws30 to ws4 |
| wsf | ws1 to ws12 |
| dtf | ws13 to ws23 |

**sub-wsf and wsf overlap on ws1 to ws4.** That is what Joe wrote; it is recorded as written and
not reconciled.

## 2. The dr flip

Joe 0911, verbatim:

> spec: the dr flip is the handoff between wsf and dtf

**As built today:** dr is set when **ws1Mage** and **ws13m** are both out of bounds on the SAME
side, and it LATCHES — the previous dr holds until that condition is met again on the other side.
Joe 0909 set the pair (he replaced ws2Mage with ws1Mage); the boundary is 85.0 at dr +1 and 15.0
at dr -1, read live from `optimus9_system`.

`dr +1` is the high side. `dr -1` is the low side.

**Proposed 0911, NOT BUILT:** swap ws1Mage for the ws1Mage-reversal mech, so the pair becomes
**ws1Mage-rev + ws13m**. Open — see §5.

## 3. The row

One row per (line, dr run): the FIRST bar in that dr run where the line's r reads `sideways` AND
sits outside the fence. Joe 0909: *"keep the first sideways event per dr flip"*.

## 4. Knobs

Every knob that moves a row. The ones marked **in KNOBS** are inside `wdv_knobs`, which is the
first part of the unique key `(wdv_knobs, wdv_utc, wdv_line)`, so a change lands BESIDE the
existing bank instead of overwriting it.

| knob | value | in KNOBS | source |
|---|---|---|---|
| timeframe range | ws1 to ws23 | yes, `tf1.23` | Joe 0910 *"increase the max r lines to ws23"* then *"add the ws1,2,3,4 r lines to the report"*. It moves rows — `top mom TF` and `prev mom` both scan it |
| lattice span | 10 minutes, every line | yes, `sp10` | **FITTED** |
| `momo_slope_min` | 0.4 | yes, `sl0.4` | **FITTED** |
| fence | 25.0 / 75.0 | yes, `f25.75` | Joe 0910, raised from 30/70 |
| dr pair | ws1Mage + ws13m | yes, `drws1Mage.ws13m` | Joe 0909 |
| `momo_config` version | 1 | yes, `bv1` | the banked-bank HTF column |
| x-cross-race hold | 5 bars, a run spanning 20 s | **NO** | `XCROSS_XWOB` in `build_wsf_x_cross`, same value. A different hold OVERWRITES the two backstop columns instead of landing beside them |
| oob boundary | 85.0 / 15.0 | **NO** | live from `optimus9_system` |
| mask sequence | gcws30 then ws1..ws18 — 19 tags, 18 pairs | **NO** | Joe 0910 |
| HTF lines | ws120, ws90, ws60, ws45, ws30 | **NO** | Joe 0910 |
| warm-up | 2026-08-23 00:00:00 | **NO** | mine — the 21-sample lattice and the dr latch need history |
| window | 2026-08-25 00:00:00 to 2026-08-28 00:00:00 | **NO** | Joe 0910 *"extend the report to 08-27 (full days)"* |

### THE SPAN AND THE SLOPE FLOOR ARE FITTED, NOT MEASURED

Both were chosen by sweeping until ws7r read `sideways` at Joe's eyeballed ~05:36 on 08-25. Joe
0910 selected them: *"these 2 line's feel less like fitting, and the timing is close enough"*. A
knob chosen by scoring against Joe's label is fitted. Re-declare it as fitted every time it is
quoted. Nothing anchors either number to a mechanism.

## 5. The columns

| column | holds |
|---|---|
| `wdv_knobs` | the knob string. First part of the unique key |
| `wdv_utc` | the row bar, exact |
| `wdv_ms` | the same bar in epoch ms, for ordering |
| `wdv_line` | the timeframe whose r went sideways, in minutes. An INT, not a line name — `WHERE wdv_line = 7`, never `'ws7r'` |
| `wdv_backstop_utc` | THE BACKSTOP. The first ws{`wdv_line`} x-cross-race confirmation strictly after the row bar, at the row's dr |
| `wdv_dr_run` | which dr run inside the window, 1-based |
| `wdv_dr` | +1 or -1 at the row bar |
| `wdv_r` | that line's r at the row bar |
| `wdv_top_mom_tf` | highest timeframe in the range that is momentum-true. 0 = none; it is not a timeframe number |
| `wdv_top` | r of `wdv_top_mom_tf`. NULL when it is 0 |
| `wdv_top1` | r of `wdv_top_mom_tf` + 1. NULL when 0 or above ws23 |
| `wdv_top_backstop_utc` | the same backstop mech read off ws{`wdv_top_mom_tf`}. NULL when that is 0. **Column name is MINE** — Joe has not named it |
| `wdv_prev_mom` | `'{TF} {verdict} -{mins}m'`. NULL when `wdv_top_mom_tf` is non-zero |
| `wdv_run_bars` | length of the sideways run this row opens, in 5 s bars |
| `wdv_nx1` .. `wdv_nx4` | r of the next four timeframes ascending, as `'{r} ({TF})'` |
| `wdv_mage_mask` | 18 pairs, gcws30 v ws1 ... ws17 v ws18. One char per ADJACENT PAIR: `+` the lower timeframe's Mage above the higher's, `-` below, `0` equal, `.` missing |
| `wdv_htf_bank` | which of ws120/90/60/45/30 are momentum-true at their own banked banks, eg `'120, 30'` |
| `wdv_htf_fit` | the same five at the report's own 10-minute span and slope 0.4 |

### The backstop mech

`build_wsf_x_cross`'s, verbatim. The race is the FIRST of three to cross — x against its Mage, its
b, or the boundary. `x X r` is stored beside the race in that producer and is not in it. dr +1 the
x crosses DOWN under its target, dr -1 it crosses UP over. x must hold the far side for 5
consecutive bars and must have been on the NEAR side before it crossed; the crossing confirms on
the bar the run reaches 5, not the bar it started.

## 6. The banks

| knob string | rows | lines | dr runs | span |
|---|---|---|---|---|
| `v3_sp10_sl0.4_f25.75_drws1Mage.ws13m_bv1` | 565 | ws5..ws23 | 61 | 08-25 00:00:00 -> 08-27 23:12:10 |
| `v3_tf1.23_sp10_sl0.4_f25.75_drws1Mage.ws13m_bv1` | 654 | ws1..ws23 | 62 | 08-25 00:00:00 -> 08-27 23:12:10 |

The first string carries no `tf` prefix; that absence means ws5..ws23.

## 7. Open

1. **The dr-flip swap.** Joe 0911 proposed replacing ws1Mage with the ws1Mage-reversal mech.
   Not built — the substitution is not yet defined. See the question in §8.
2. **Name `wdv_top_backstop_utc`.** The name and its position after `wdv_top1` are both mine.
3. **The x-cross-race hold is not in the unique key.** A sweep of it overwrites both backstop
   columns.
4. **sub-wsf and wsf overlap on ws1..ws4**, as Joe wrote the bands.

## 8. The dr-flip swap — what has to be settled first

The rule today needs both members to have a SIDE: "ws1Mage and ws13m both oob on the same side".
`_mage_rev(ws1Mage, 2)` returns a TURN, not a side: `+1` a down-to-up turn, `-1` an up-to-down
turn, `0` no turn. There is no single obvious mapping from a turn to a side, and the two candidate
mappings are opposites of each other, so the choice changes every dr run in the report.

Not built until Joe rules it.
