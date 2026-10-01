
## 1001 the walk CONTINUES - the race is a STATE, not an event

Joe: *"every bar that satisfies the race is a candidate, not just the first"* - built in
`$CLAUDE_JOB_DIR/tmp/walkon.py`. One knob set, Joe 1001 *"those settings are good for now"*:
min_tf 7, fall 3, race 1, frmin 4 (= ladder floor), pool all_above_min, lb 4 min = 48 bars,
turn first, fence 25/75, wob 6 bars = 30 s.

| episode | arm | cancel | dr | scan from | race holds | of bars | rev legs | rev in target |
|---|---|---|---|---|---|---|---|---|
| A 11:40-11:56 | 10:32:30 | 12:36:50 | +1 | 10:36:30 | 1397 | 1445 | 333 | 49 |
| B 02:29-02:49 | 02:38:10 | 03:32:00 | -1 | 02:40:00 | 498 | 625 | 95 | 19 |

BOTH targets are reached once the walk continues. A: 11:40:05 -> 11:55:45. B: 02:40:05 -> 02:48:00.

THE FINDING: the race condition is true on 96.7% of episode A and 79.7% of episode B, so it is a
near-permanent state and selects nothing. 333 rev legs across 2h04 = one every ~21 s. The rev leg
sets the cadence, not the race.

The three contiguous spans per episode, and their ONSETS (the bar the state turns true):
  A  10:36:30 -> 12:14:40 (1179 bars) | 12:15:10 -> 12:29:10 (169) | 12:32:50 -> 12:36:50 (49)
  B  02:40:00 -> 03:14:25 (414, ONSET IN TARGET) | 03:24:15 -> 03:28:15 (49) | 03:29:10 -> 03:32:00 (35)

OPEN, Joe's to rule: is a candidate every bar the state HOLDS (333 signals in episode A) or the bar
the state TURNS TRUE (3 per episode; B hits 02:40:00, A misses - onsets are 64 min early, 19 and 37
min late). Both readings are causal. Nothing else in the mech distinguishes them.

## 1001 re-walk from 00:00 - all 28 banked signals on 09-01 against the same requirement

Joe: *"I can't decide on 2 signals. re-walk from 00:00 - confirm that the other targets meet the
same requirement"*. `$CLAUDE_JOB_DIR/tmp/rewalk2.py`, knobs held.

TWO DEFECTS IN MY FIRST PASS, both corrected before reporting:
  1 `REV` was built from `LEGS[d]['rev']` - a 360,738-bar mid-chain field, not the signal bar. The
    bar coil_exit emits is `sig_conf` = cross + boundary_xwob 4 - 1 = +15 s. 21 of 28 targets are a
    `sig_conf` leg; only 3 are a `rev` bar.
  2 "a mage-rev leg at the target bar" is only the requirement on the `gap` branch.
    `actionable_confirmed` is release + 180 s, `actionable_lookback`/`_forward` are v3 rows.
    Measured, and it confirms the branch reading: lookback 0/7 are sig_conf legs; confirmed 14/14,
    gap 6/6, forward 1/1.

THE REQUIREMENT, three parts, nothing added: armed episode with matching dr | target >= scan |
race HOLDS at the target bar.

| result | count of 28 |
|---|---|
| MEET 1-3 | 17 |
| no armed episode | 8 |
| race off at the bar | 3 |

| wsb_via | meets | fails |
|---|---|---|
| confirmed | 9 | 5 |
| gap | 4 | 2 |
| lookback | 4 | 3 |
| forward | 0 | 1 |

OF THE 11 FAILURES, 6 are LATE rather than absent - the condition turns on 35-175 s after the
target: 04:26:00 arm +35 s, 13:48:00 arm +75 s, 15:08:00 arm +170 s, 16:15:35 race +35 s,
05:43:20 race +50 s, 21:18:25 race +175 s. All 3 race-off bars had 0 flat-run starts in the 4 min
lookback at the target bar.

1 is a dr mismatch: 05:01:30 dr -1, the nearest episode is +175 s away and dr +1.
4 are absent: 02:10:30 (next same-dr arm +1660 s), 12:41:45 (-7755 s, dr +1), 17:27:50 (-4745 s,
dr -1), 07:27:15 (-1790 s, dr -1). Joe has already ruled 04:26 and 07:27 ok to drop.

## 1001 the mech, re-stated - arm as a STATE, same-dr REQUIRED, rule#1 applied

Joe 1001: *"`arm` is a state, not a column"* and *"you were right to require same dr. update the
mech"*. `$CLAUDE_JOB_DIR/tmp/rewalk3.py`.

THE MECH
  arm       a STATE the walk carries. set: ws5Mage oob 25/75 on the dr side for ARM_WOB 6
            consecutive bars = 30 s. cancel: ws5Mage crosses 50, either direction. It carries the
            dr in force at the bar the dwell completed.
            THE ARM'S dr MUST EQUAL THE SIGNAL'S dr - Joe 1001. An arm live on the opposite dr
            does not arm the signal.
  turn      the first bar at or after the arm where the combined coil (CC * dr) ticks DOWN
  qualify   the FALL 3rd departure from the momTF bucket among lines >= MIN_TF ws7
  race      RACE 1 flat-run start inside LB 4 min = 48 bars, at or after scan = max(turn, qualify).
            A STATE - every bar it holds is a candidate, not only the first.
  rule#1    rule1_gate.gate at RULE1_BACK 60 bars = 5 min, Joe 0930 for the duration of this dev.

ARM STATE WALKED ACROSS 09-01: set 16 times, cancelled 16 times, live on 10,609 of 17,280 bars
(61.4%).

| population | count |
|---|---|
| banked signals on 09-01 | 28 |
| rule#1 OPEN at 5 min - the real targets | 17 |
| rule#1 SHUT - disqualified | 11 |
| of the 17, MEET the mech | 9 |
| of the 17, FAIL the mech | 8 |
| of the 11 disqualified, the mech fires anyway | 8 |

THE 8 FAILURES: 5 arm state not live (04:26:00, 07:27:15, 12:41:45, 15:08:00, 17:27:50), 3 race
off at the bar (05:43:20, 16:15:35, 21:18:25). Joe has already dropped 04:26:00 and 07:27:15.

All 3 race-off bars have ZERO flat-run starts anywhere between the arm and the target bar - not
merely none inside the 4 min lookback. The first flat-run arrives +35 to +175 s later.

## 1001 `via = confirmed` - causal, and where it couples with v3

Joe: *"if `via` prints confirmed, is that a signal that was built causally or does it couple with
v3?"*. `$CLAUDE_JOB_DIR/tmp/viachk.py`, 09-01, the real sweep_v3_signal.Rig.

BOTH. The bar is causal; the window it is found in is two v3 rows.

The CONFIRMED branch body reads NOTHING from the moment - only `pick` and `lag_bars`:
    if confirmed:
        named = pick; base = pick + lag_bars
        return dict(_blank(), named=named, base=base, actionable_confirmed=base,
                    rev=first_forward(legs, base), via=CONFIRMED)
The other three branches all read `named = moment['i1']` and `base = moment['brk']`. CONFIRMED
reads neither.

THE COUPLING IS ONE LEVEL UP, in release(cc, m['i0'], m['i1'], lag, last_bar):
  i0  the moment's FIRST full-support v3 row  -> the scan START
  i1  the moment's LAST full-support v3 row   -> the latest bar the candidate PEAK may sit on
  the confirm window may read past i1 - the docstring calls this forward in time, not lookahead

CAUSAL: pick is the first bar in [i0,i1] where the coil ticks down and never regains v[t] inside
36 bars = 180 s. The verdict is known at pick+36, actionable = pick+36, nothing past it is read.

MEASURED ON 09-01 - 255 v3 rows, 32 moments, 15 CONFIRMED / 9 gap / 7 lookback / 1 forward:

| measurement | value |
|---|---|
| CONFIRMED moments where pick == i0 (the release IS the moment's first v3 row) | 6 of 15 |
| i1-pick headroom on confirmed, bars | min 0, median 32 = 160 s, max 219 |
| confirmed moments whose confirm window read past i1 | 8 of 15 |
| the (i1, brk) gap, all 32 moments | 2,628 bars, mean 82.1 = 410 s, max 548 = 2,740 s |
| UNCONFIRMED moments with a coil turn-down inside the (i1, brk) gap | 17 of 17 |

THE LAST ROW IS THE ONE THAT MATTERS. Every unconfirmed moment has a coil turn-down in the bars
between the moment's last full-support v3 row (i1) and the bar the moment's end becomes knowable
(brk). The i1 bound is what makes them unconfirmed - not an absence of a turn.

DIRECTION: at any bar t with i1 < t < brk the moment has NOT broken; the breaking row prints at
brk. So "the moment is live" is true and knowable at t. A walk that scanned to brk would consider
those bars; release() stops at i1. That is NARROWER than a live walk, not wider - no lookahead.
Whether the mech should accept a candidate peak in that gap is Joe's rule to make.

## 1001 Joe's two-leg plan - the o9-live review

Joe's plan: *"let the in-dev spec walk the bars. if the walk produces FINAL == YES, then we place a
trade signal / if FINAL == NO AND rule#1 5 min = open, then we take the target timestamp if via =
`confirmed`"*. He asked for every moving part, 100% causal, o9-live ready, either way.

VERDICT: every ingredient IS causal - read, not assumed. The plan is NOT yet o9-live ready, for
two structural reasons and two build defects. None of them is a lookahead.

CAUSALITY AUDIT - the window each component reads, from the source:
  arm state        ws5Mage + rig.DR at bars <= k, cancel on a 50-cross                    CAUSAL
  turn             CC tick-down at bars <= k                                              CAUSAL
  qualify          momentum_true: idx0 = k-(MOMO_SAMPLES-1)*MOMO_STEP_BARS .. k           CAUSAL
  momo_fit         lattice_fit "ending at each bar"                                       CAUSAL
  curl gate        rolling_quad "the last nb bars at each bar"                            CAUSAL
  race             flat_run_at - 3 bars ending at k                                       CAUSAL
  rule#1           [k-84, k]; trade_config v3 has rule1_fwd_min 0, run_clamp 'window'     CAUSAL
  scenario leg     anchor_floater - its own docstring: "Every bar read is <= k"            CAUSAL
  v3 row           sideways_mask = lattice_fit + rolling_quad, both backward              CAUSAL
  release          peak in [i0,i1], confirm to pick+36, emitted at pick+36                CAUSAL
  sig_conf         cross + boundary_xwob - 1                                              CAUSAL

BLOCKER 1 - FINAL IS A TEST, NOT A GENERATOR. Every FINAL in my report was evaluated AT a bar that
came from the banked wsl_sig_utc. Remove the Excel and leg 1 has no bar to evaluate. Read literally
- fire on any bar the state holds - the measured output is: arm live on 10,609 of 17,280 bars of
09-01 (61.4%), race holding on 1,397 of 1,445 bars of episode A (96.7%), 333 signals in 2 h 04.

BLOCKER 2 - "FINAL == NO" HAS NO LIVE REFERENT. With no banked bar there is no bar to be NO about.
Leg 2's implementable form is "the chain resolved a moment CONFIRMED -> take its bar, unless the
in-dev mech already fired", and "already fired" needs a scope (per moment? per armed episode? per
N minutes?) that Joe has not set and that changes the count.

THE TIMESTAMP LEG 2 WOULD TAKE IS `rev`, NOT `actionable_confirmed`. chain() line 70 and
sweep_v3_signal line 235 both bank ex['rev']. For CONFIRMED, rev = first_forward(legs, pick+36) - a
ws1mage_rev sig_conf searched forward with NO bound. All 15 confirmed revs on 09-01 are in the bank.

| rev - actionable_confirmed | bars | secs |
|---|---|---|
| min | 10 | 50 |
| median | 58 | 290 |
| max | 451 | 2,255 = 37.6 min |

So the 180 s is the START of a further unbounded wait, not the end of it.

DUPLICATE revs: moments at 18:28:10 and 18:31:00 both resolve to rev 18:40:45. The bank dedups
with a set; leg 2 live must dedup too.

BUILD DEFECT 1 - TWO dr SERIES. My arm state reads rig.DR (dr_latch.latch, no wob); gate_open and
the trade walk read rig.DRW (latch_wob at latch_wob 8). They differ on 7 of 242 banked rows. Joe's
to rule which series the arm uses.

BUILD DEFECT 2 - THE 5 MIN LOOKBACK IS NOT IN THE CONFIG. trade_config v3 holds rule1_back_min 7.0.
The 5 min is a dev-path override, is not in trade_config.key(), and has never been OOS'd (+0.4347
in-sample only). o9-live would read 7 min.

LEG 2's MEASURED OUTPUT ON 09-01: rule#1 at the rev bar is open on 8 of 15 confirmed moments at
5 min, 9 of 15 at 7 min. Of those 8, six already have FINAL == YES, so leg 2 adds exactly two:
05:43:20 and 16:15:35.

## 1001 what FINAL YES is worth - the base rate I should have published with it

Joe: *"why would you share a big CAPS title with YES and NO, if it doesn't mean anything useful? I
thought FINAL YES meant you've applied the new dev spec against the target and found success"*.

FINAL YES does mean the spec was satisfied at the target bar. The missing number is how hard that
is to satisfy. Measured over every armed bar on 09-01, no target bars involved
(`$CLAUDE_JOB_DIR/tmp/baserate.py`):

| population | bars | % of armed |
|---|---|---|
| armed bars on 09-01 | 10,625 | 100% |
| armed bars at or after scan | 10,303 | 97.0% |
| armed bars where the mech is SATISFIED | 7,716 | 72.6% |

| the targets | count | rate |
|---|---|---|
| rule#1-qualified targets | 17 | - |
| of those, armed with matching dr | 12 | 70.6% |
| of those 12, mech satisfied | 9 | 75.0% |

75.0% against a 72.6% base rate. MECH==YES at a target is AT CHANCE - the spec permits a target
about as readily as it permits any armed bar. The YES column is a necessary-condition check, not
evidence the target is special.

WHERE THE INFORMATION ACTUALLY IS
  1 the 8 NOs - bars where the spec actively contradicts a target
  2 the per-episode spread, 0.0% to 93.6% of armed bars satisfying: episodes 4 (04:26:35) and 5
    (05:04:25) have ZERO satisfying bars, so the race does discriminate at episode level -
    2 of 16 episodes never satisfy
  3 the arm state itself - 5 of 17 targets fail it

THE KNOB THAT WOULD MAKE THE YES COLUMN MEAN SOMETHING is frmin, the minimum TF for a flat-run
event, currently ws4 = the ladder floor. The 1001 sweep showed the race's first fire moving from
10:36:30 to 11:55:50 as frmin rises ws4 -> ws21. Joe parked it: *"no need to sweep - those settings
are good for now"*. At frmin ws4 / race 1 / lb 4 min the race is on 72.6% of armed bars.

## 1001 the mech has a GATE, not a TRIGGER - measured

Joe: *"does this mean you need a way to pinpoint the target (within tolerance), but you don't have
one in the mech yet?"* - yes. `$CLAUDE_JOB_DIR/tmp/pinpoint.py`.

A state true on 72.6% of armed bars cannot name a bar. Only an event can. The mech already
contains five events, all causal, no new mechanic. Measured against the 17 rule#1-qualified targets
on 09-01 (12 of which are armed with a matching dr). Sign: offset = event - target in seconds,
NEGATIVE = the event is EARLY.

| event | n | min | median | max | median ABS | within +-60 s | +-120 s | +-300 s |
|---|---|---|---|---|---|---|---|---|
| arm | 12 | -8085 | -492 | -100 | 492 | 0 | 2 | 4 |
| turn | 12 | -8075 | -482 | -90 | 482 | 0 | 2 | 4 |
| qualify | 12 | -8075 | -428 | -35 | 428 | 2 | 3 | 4 |
| scan | 12 | -8075 | -428 | -35 | 428 | 2 | 3 | 4 |
| race ONSET | 12 | -1235 | **+0** | +1815 | **138** | **4** | **5** | **8** |

arm, turn, qualify and scan are STRUCTURALLY EARLY - median -428 to -492 s, 0 of 12 inside +-60 s.
Only the race onset straddles the targets: median +0 s, median absolute 138 s.

THE CAVEAT THAT DECIDES ITS VALUE: the onset column picked the onset NEAREST the target, using the
target to choose. That is not a live selector. Episodes carry 1 to 4 onsets. The causal forms
available are "the first onset", "the Nth onset", "the first onset after <another event>". None has
been chosen or measured.

5 of the 17 targets have no arm at all, so no event of any kind exists for them; a trigger cannot
reach those.

NO TOLERANCE IS DEFINED ANYWHERE IN THE MECH. The +-60/120/300 s columns are a diagnostic I used
to size the question, not a knob.

## 1001 ws1mage-rev re-inserted with resolve()'s lookback - all three reports recreated

Joe 1001: *"ws1mage-rev is load-bearing"* / *"it has to be re-inserted in the same way it was
before, exhibiting the same forward and lookback behaviour. ie, when the mech finds a scenario
matching the mech's rules, lookback for ws1mage"*. `$CLAUDE_JOB_DIR/tmp/mech4.py`.

THE LEG, mapped onto coil_exit.resolve with `named` = the mech's own bar k:
    LOOKBACK   _knowable(legs, k - 48, k, k) non-empty -> the signal IS k
               lookback_s 240 = 48 bars, read exactly as resolve reads it
Verified: sig_conf - sig is EXACTLY 3 bars on all 24,237 legs (boundary_xwob 4 - 1), and the
vectorised lookback matches coil_exit._knowable on 400 random bars with 0 mismatches.

HALTED: the GAP and FORWARD legs need `base`, which in resolve is moment['brk'] - the bar the
moment's end becomes knowable. The mech has no equivalent. 4,948 race bars have no rev cross in the
240 s lookback; those are the rows gap/forward would decide. Not invented.

REPORT 1 - THE BASE RATE MOVED

| population | bars | % of armed |
|---|---|---|
| armed bars on 09-01 | 10,625 | 100% |
| race holds | 7,716 | 72.6% |
| race + rev lookback = MECH | 2,768 | **26.1%** |

The rev leg cuts 4,948 of 7,716 race bars = 64.1%.

| the targets | count | rate |
|---|---|---|
| rule#1-qualified | 17 | - |
| armed with matching dr | 12 | - |
| of those 12, mech satisfied | 9 | 75.0% |

75.0% against a 26.1% base rate - 2.9x. Before the rev leg it was 75.0% against 72.6%, at chance.

REPORT 3 - THE MECH NOW LANDS ON THE TARGET BAR

| event | n | min s | median s | max s | median ABS s | +-60 s | +-120 s | +-300 s |
|---|---|---|---|---|---|---|---|---|
| arm | 12 | -8085 | -492 | -100 | 492 | 0 | 2 | 4 |
| turn | 12 | -8075 | -482 | -90 | 482 | 0 | 2 | 4 |
| qualify | 12 | -8075 | -428 | -35 | 428 | 2 | 3 | 4 |
| scan | 12 | -8075 | -428 | -35 | 428 | 2 | 3 | 4 |
| MECH bar | 12 | **+0** | **+0** | +175 | **0** | **11** | **11** | **12** |

9 of 12 land EXACTLY on the target bar. The 3 others: +35 s, +50 s, +175 s.

THE CIRCULARITY TO BE AWARE OF: the rev LOOKBACK column is YES on all 28 banked targets, and that
is NOT independent evidence. The banked sig_utc for a `confirmed` or `gap` row IS a sig_conf (its
cross sits 3 bars behind it), and a `lookback` row was set BECAUSE a rev cross was in its 240 s
lookback. So 28/28 is the bank's own construction reflected back. The non-circular measurement is
the 64.1% cut on every other armed bar.

STILL OPEN: 36 to 698 MECH bars per episode, so a selector is still needed - but the candidate set
now contains the exact target bar in 9 of 12 cases. Episodes 4 (04:26:35) and 5 (05:04:25) still
have 0 MECH bars.

## 1001 actionable_confirmed alone - tested, and what it costs

Joe: *"this is the lookahead component, yes? my understanding from you 4 or 5 responses ago is that
`confirmed` does not need the moment's end. confirm that this is still true, and you don't need to
know the 'moment's end' because I'm only asking for the `actionable_confirmed` branch"*.
`$CLAUDE_JOB_DIR/tmp/confirmonly.py`.

1 `brk` IS NOT A LOOKAHEAD. It is the bar the breaking v3 row prints, so it is knowable AT brk -
  forward in TIME, which a walk simply waits for. My HALT was because the mech has no equivalent of
  brk, not because brk is unknowable. Correcting that framing.

2 STILL TRUE, AND NOW TESTED. release() was re-run on all 32 moments with the candidate-peak bound
  at i1 (as banked), at brk-1, and at i1+720 bars = 60 min past the last row:

  | result | count |
  |---|---|
  | banked CONFIRMED moments | 15 |
  | of those, pick UNCHANGED at BOTH wider bounds | 15 of 15 |
  | of those, pick MOVED | 0 of 15 |

  The CONFIRMED branch body also reads neither i1 nor brk - `base = pick + lag_bars`.

3 CORRECT. actionable_confirmed needs only: i0 (the moment's FIRST full-support v3 row, knowable
  when that row prints), the coil walked forward from it, and the 180 s confirm window.
  actionable_confirmed = pick + 36 bars. The HALT dissolves for a confirmed-only path.

WIDENING THE BOUND ADMITS MORE MOMENTS - and every wider bound is non-causal:

| bound | UNCONFIRMED that become CONFIRMED | confirmed total on 09-01 | causal |
|---|---|---|---|
| i1 (as banked) | - | 15 | YES - verdict at pick+180 s, nothing later read |
| brk-1 | 15 of 17 | 30 | NO - needs brk, the bar the breaking row prints |
| i1+720 (no practical bound) | 17 of 17 | 32 | NO - never terminates on a live walk |

WITHDRAWN 1001. This block previously described brk-1 as "a live walk's real scan range" and said
"live it DOUBLES the count", framing the extra 15 moments as something a live producer would get for
free. Joe: *"I think you've reinserted a mech that I called out as lookahead... have you let a bias
find its way into the handover docs?"* He was right. Both wider bounds need `brk`, which
`coil_moment.moments()` states is "only knowable when the next row prints". The i1 bound is the only
causal one, AND it never chose a confirmed pick - 0 of 15 moved at either wider bound. There was
nothing to rule and the three options were the writer's, not the mech's.

THE MECH IN DEVELOPMENT DOES NOT USE release() AT ALL. blindwalk.py, fires.py and mae.py - the
scripts that produced the validated 09-01 report - contain ZERO references to release, i1, brk,
moments() or coil_exit. The arm episode replaces the moment: set on ws5Mage 25/75 dr-side for 6 bars
= 30 s, cancelled on `(Mg[k]-50)*(Mg[k-1]-50) < 0`, which reads bar k and k-1 only. The turn
replaces release: the first bar at or after the arm where the combined coil ticks down. Neither has
an end-of-run to wait for.

## 1001 the BLIND walk - can FINAL YES be recreated? YES, 9 of 9 exactly

Joe 1001: *"the table doesn't tell us if the FINAL YES can be recreated in the walk"* - correct,
every prior report tested a bar handed to it. `$CLAUDE_JOB_DIR/tmp/blindwalk.py` walks
00:00 -> 23:59:55 and EMITS; the targets are checked against the emitted set afterwards.
`via` dropped from the 28-row table per Joe 1001.

AT EACH BAR, using only bars <= k: arm live (dr = the arm's own) -> k >= scan -> race holds ->
ws1mage-rev cross in [k-48, k] with sig_conf <= k -> rule#1 open at 60 bars = 5 min -> EMIT.

| result | value |
|---|---|
| armed episodes | 16 |
| MECH bars | 2,768 |
| rule#1 cut | 1,673 |
| EMITTED bars | 1,095 |
| contiguous runs | 23 |
| FINAL YES targets emitted at the EXACT bar | **9 of 9** |
| emitted bars per target hit | 121.7 |

| the cost | value |
|---|---|
| runs carrying a FINAL YES target | 9 of 23 |
| runs carrying NO target | 14 of 23 |
| emitted bars in target-carrying runs | 503 |
| emitted bars in the other runs | 592 |

THE SELECTOR LEAD. 6 of the 9 targets sit on the FIRST BAR of their emitted run:
00:27:35, 02:40:35, 09:02:15, 14:50:00, 18:20:00, 22:24:10 - offset +0 s.
The other 3 are inside their run: 18:00:10 at +45 s, 03:40:05 at +125 s, 23:25:00 at +370 s.

So "the first bar of each emitted run" is a CAUSAL selector that would fire 23 signals on 09-01 and
land exactly on 6 of the 9. Not applied - Joe's to rule.

## 1001 the fire timestamp added to the 28-row report

Joe 1001: *"which column in these reports tell us when the signal fires? I'd prefer it in the
'28 banked signals, via dropped' report, as a timestamp"*. NONE of them did - FINAL YES says the
mech PERMITS the bar handed to it. `$CLAUDE_JOB_DIR/tmp/fires.py` joins the blind walk's emitted
runs onto the table:

  in run                   the target bar is itself one of the 1,095 emitted bars
  WALK FIRES FROM          the first emitted bar of that run - the fire timestamp
  walk fires to            its last emitted bar; the walk fires on every bar between
  run bars                 the run's width
  target - fires from s    signed. NEGATIVE = the run starts AFTER the target

When the target is not in a run, the run shown is the NEAREST one.

| result | value |
|---|---|
| MECH bars | 2,768 |
| EMITTED bars | 1,095 |
| runs | 23 |
| targets the walk emits at | 9 of 28 |

THE FIRE IS A RUN, NOT A BAR. `WALK FIRES FROM` is the earliest bar the walk fires in that run, and
it keeps firing to `walk fires to` - 20 to 101 bars. There is no single fire time until a selector
is chosen.

ROWS WITH MECH YES BUT `in run` no: 07:15:00, 08:18:15, 08:42:15, 16:37:15, 18:40:45, 21:21:20,
21:37:20, 21:57:35 - all 8 are rule#1 SHUT, and the walk's emit requires rule#1 open.

## 1001 MAE/MFE on 09-01 - the 9 FINAL YES fire bars and Joe's 5

Joe's rulings this turn: the dr series stays as the report ran it (arm on dr_latch.latch NO wob,
rule#1 on latch_wob 8) | lazy-g sits BESIDE rule#1, not behind it | the 5th timestamp is 13:05,
"the arm firing on signal trade" | 12:41 -> 13:05 was not a cost, it landed on the correct bar |
effective-n agreed | *"use the same logic that banked the 0.3991"*.

trade_walk.walk(opens, rig.DRW, rig.px, min(opens), B, mae_cap 0.70), then
measure_live_stop.score's rule: -cap if stopped, else MFE - MAE. `$CLAUDE_JOB_DIR/tmp/mae.py`.

| set | opens | trades closed | stopped | MFE>MAE | MAE sum | MFE sum | summed score | per trade |
|---|---|---|---|---|---|---|---|---|
| A  the 9 FINAL YES fire bars | 9 | 8 | 2 | 6 | 2.813 | 10.986 | +8.153 | +1.0191 |
| B  Joe's 5 | 5 | 5 | 1 | 4 | 1.649 | 13.068 | +11.341 | +2.2682 |
| UNION | 14 | 13 | 3 | 10 | 4.462 | 20.202 | +15.642 | +1.2032 |

JOE'S 12:41 READ IS CONFIRMED: it stopped. MAE 0.763 against the 0.70 cap, closed 13:01:30 after
237 bars = 19.75 min. And 13:05:25 survived with MAE 0.693 - 0.007 UNDER the cap.

THE UNION IS NOT A + B. 8.153 + 11.341 = 19.494 against a union of 15.642, a delta of -3.852, and
the whole of it is one trade: 17:27:50 runs to 19:11:20 for +4.960 alone, but in the union the
17:59:25 opposite-dr signal closes it at +1.107. Mech signals and lazy-g signals close each other.

THE TWO STOPS IN SET A are both in the 17:58:30 arm episode: 17:59:25 (MAE 0.792) and 18:20:00
(MAE 1.026).

23:18:50 is UNCLOSED at the 23:59:55 cache end - MAE 0.249, MFE 0.873 so far - and is excluded from
every total rather than being closed at the boundary.

EFFECTIVE-N: one day, 13 trades, 16 armed episodes. No rate is claimed from this.

## 1001 THE PORT — the walk is repo code, with a hard acceptance test

Joe 1001: *"5"* (the rule#1 lookback) and *"for each file you work on, test yourself for bias before
you save. stringently self monitor so that we can get our only validated machine into SIT without
delay"*.

| file | what it is |
|---|---|
| `optimus9/compute/arm_state.py` | the arm as carried STATE - a stepper, because it is path-dependent |
| `optimus9/compute/leash_walk.py` | the walk that emits `WALK FIRES FROM` |
| `tests/test_arm_state.py` | 6 checks |
| `tests/test_leash_walk.py` | 5 checks |
| `report_leash_walk.py` | the acceptance test and the recon's reference |
| `trade_config.WALK_V = 4` | 31 rows, 13 new. `V` stays 3 |
| `Rig.gate_open(k, back_bars=None)` | optional override, proven non-breaking |

ACCEPTANCE: all 9 validated 09-01 bars reproduced from repo code, each as a run FIRST bar, with the
arm bar and arm dr matching Joe's validated table on every row. MECH 2,768 | rule#1 cut 1,673 |
emitted 1,095 | 23 runs - identical to the scratch run.

ALL 11 TESTS PASS. The ones that earn their keep:
  P1  the arm's warmup is BOUNDED - seeding at `warmup_from(k)` == seeding at bar 0, 565 bars.
      This is the property `dr_latch.latch_wob` does NOT have
  Q1  the live qualify counter == the offline sorted form, 200 random departure schedules
  Q2  `rev_lookback_mask` == `coil_exit._knowable`, 3,000 bars, 0 disagree
  G   `gate_open(k)` == `gate_open(k, 84)` on 17 bars - the v7 chain is untouched

FIVE DEFECTS FOUND BY THE PER-FILE BIAS CHECK, all mine, all before Joe saw a number:
  1 `arm_state.py` cited a test file that did not exist - the `fastverdict.verify()` failure
  2 that test then found `cancel_bar` carrying TWO meanings. Split into `end_bar` + `cancelled`
  3 `leash_walk.py` cited two equivalences; both written as tests rather than asserted
  4 `report_leash_walk.py` printed the WRONG arm bar beside every correct fire bar -
    `states[emit.index(k)]` indexed a MECH-ordered list with an emit-ordered position. `walk()` now
    returns state keyed by bar so a caller cannot repeat it
  5 a patch script failed on an arity error and I nearly reported the unfixed output as fixed

THREE THINGS JOE ACCEPTED AS STATED, 1001:
  - the walk emits 14 run-first bars that are NOT validated bars: 05:44:10, 07:00:40, 08:09:15,
    08:12:45, 11:30:20, 11:34:15, 11:37:00, 13:05:25, 13:54:20, 15:13:00, 16:16:10, 16:21:20,
    18:11:35, 23:27:20. He has endorsed 13:05:25; the rest are unscored
  - `gate_open(k, 60)` differs from the config's 84 on 4 of 17 sampled bars, and 5 min is un-OOS'd
  - `TC.V` stays 3; bumping it is his call when the walk replaces the v7 chain as the default
