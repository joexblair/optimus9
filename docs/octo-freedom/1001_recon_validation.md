# 1001 — o9-live recon session: Phase 2 validation and Phase 3 report

Written 2026-10-01 by the o9-live recon session (harness name `read o9-live-recon readme`, job
`639244ab`), following `docs/o9-live-recon/README.md` `## The startup prompt`. Filed here after the
fact: the report first went to chat and a Claude Docs page, which `docs/octo-freedom/README.md` says is
not a report. The harness that produced every mutation number is in
`docs/octo-freedom/1001_recon_validation/`, byte-identical to what ran (sha256 checked on copy).

## Where it ran

| thing | value |
|---|---|
| repo HEAD at run time | `3fed91a` |
| `arm_state.py`, `leash_walk.py` changed since | no (`git diff 3fed91a 4c162a9` lists neither) |
| tape | `TAPE_END` 2026-09-08 00:00, pinned by `report_leash_walk.py:36-38` and `1001_recon_validation/day.py:26-28`. Repo constant is 2026-09-30 |
| day | 2026-09-01, bars 1512000..1529279 = 17,280 bars |
| config | `wsf_trade_config` v4, key `wtc_v4_v7_rule1_gateopen_mae0.70` |

## The knobs in force, with their source

| knob | value | source |
|---|---|---|
| arm line / fence / wob | ws5Mage, 25/75, 6 bars = 30 s | v4 `arm_line`, `arm_fence_*`, `arm_wob` |
| ladder | ws4..ws23 | v4 `walk_ladder_lo/hi` |
| `min_tf` / `fall` / `race` / `frmin` | ws7 / 3 / 1 / ws4 | v4 `walk_*` |
| race lookback | 48 bars = 4 min | v4 `walk_lb_bars` |
| rule#1 lookback | 60 bars = 5 min | v4 `walk_rule1_back_min` 5.0 |
| rev lookback | 48 bars = 240 s | `wsf_dtf_v3_config` `lookback_s` 240 |
| ws1mage-rev line, dwell, rev_wob, hold | gcws30Mage, 3, 2, 4 | `wsf_dtf_v3_config` `sig_line`, `dwell`, `rev_wob`, `boundary_xwob` |
| ws1mage-rev fence | 85/15 | `lr_config` `hi`/`lo`, via `report_coil_exit.py:71` |
| momentum fence | 17/83 | `wsf_dtf_v3_config` `momo_fence_r` 17 |
| coil lines | gcws30, ws1 | `wsf_dtf_v3_config` `coil_lines` |
| flat-run samples / tolerance | 3 / 2.0 r points | hardcoded, `report_leash_walk.py:73-74` |
| MID | 50.0 | hardcoded, `arm_state.py:34` |
| rule#1 fence / oob / div_tf, `rig.DRW` latch | 27/73, 15/85, 1, ws13m 75/25 wob 8 | v3 via `Rig.Ct` (`sweep_v3_signal.py:89, 107-109, 180-195`). v3 and v4 agree on all 18 shared rows |

## The commands, verbatim

```
cd /home/joe/thecodes
python3 report_leash_walk.py                         # acceptance, exit 0, 82 s
python3 tests/test_arm_state.py                      # 7 OK
python3 tests/test_leash_walk.py                     # 5 OK

# acceptance test with arm_wob 6 -> 7, scratch copy only (T = the job's scratch dir, removed when
# the job is deleted; any directory outside the repo works)
T=/home/joe/.claude/jobs/639244ab/tmp; mkdir -p $T/accept
cp /home/joe/thecodes/report_leash_walk.py $T/accept/report_leash_walk_wob7.py
sed -i "s/        arm_wob=int(cfg\['arm_wob'\]),/        arm_wob=7,                                    # SCRATCH PERTURBATION: v4 holds 6/" $T/accept/report_leash_walk_wob7.py
cd $T/accept && python3 report_leash_walk_wob7.py    # exit 1

# the mutation harness, from its own directory
cd docs/octo-freedom/1001_recon_validation
for m in BASE A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 A13 L1 L2 L3 L4 L5 L6 L7 L8 L9 L10 L11 L12 L13 L14 L15 L16 L17 L18 L19 L20 L21 L22 L23 L24; do timeout 300 python3 unit.py $m 2>/dev/null | tail -1; done > unit_results.jsonl
rm -f day_results.jsonl && python3 day.py BASE P_ltmax+P_drcons+P_midrun A1 A2 A3 A4 A5 A6 A7 A8 A9 A10 A11 A12 A13 L1 L2 L3 L4 L5 L6 L7 L8 L9 L10 L11 L12 L13 L14 L15 L16 L17 L18 L19 L20 L21 L22 L23 L24 LB=1000000000
python3 seed.py                                      # warmup_from and seeding checks
python3 eps.py                                       # armed episodes touching 09-01, cold vs seeded
```

| file in `1001_recon_validation/` | what it is |
|---|---|
| `muts.py` | the 37 mutations and 3 probes, each one textual change to `arm_state.py` or `leash_walk.py`, applied alone |
| `unit.py` | the 12 checks against one mutation, fresh process, one JSON line out |
| `day.py` | the acceptance test's walk on 09-01, tape loaded once, one JSON line per mutation. Its inputs mirror `report_leash_walk.main()` |
| `seed.py` | `warmup_from(12:00:00)`, and the walk seeded 3 h, `warmup_from(00:00)` and 24 h before midnight |
| `eps.py` | armed episodes touching 09-01, cold at 00:00 vs seeded 24 h earlier |
| `unit_results.jsonl` | 38 rows: BASE + 37 mutations |
| `day_results.jsonl` | 40 rows: BASE, the probes, 37 mutations, unbounded `walk_lb_bars` |

`muts.py` matches its `old` strings against the CURRENT `arm_state.py` / `leash_walk.py` and raises if
any string does not occur exactly once. An edit to either module will stop the harness rather than
mutate the wrong line.

DB checks, run inline:

```
SELECT COUNT(*) c FROM wsf_trade_config WHERE wtc_version=%s      -- v2 16, v3 18, v4 36
TC.load(db, 3) vs TC.load(db, 4)                                   -- 18 of 18 shared rows equal
optimus9.analysis.jig.lr_config(db).hi, .lo                        -- 85.0, 15.0
```

## 1 — Acceptance test and the 12 checks

| command | exit | result |
|---|---|---|
| `python3 report_leash_walk.py` | 0 | `M\|PASS`, 82 s |
| `python3 tests/test_arm_state.py` | 0 | 7 OK |
| `python3 tests/test_leash_walk.py` | 0 | 5 OK |

```
K|wsf_trade_config v4|key wtc_v4_v7_rule1_gateopen_mae0.70
K|arm ws5Mage fence 25.0/75.0 wob 6 bars = 30 s|same dr 1
K|ladder ws4..ws23|min_tf ws7|fall 3|race 1|frmin ws4|lb 48 bars = 4 min
K|rev lookback 48 bars = 240 s|rule#1 back 60 bars = 5.0 min
K|tape END_MS 2026-09-08 00:00|day 2026-09-01|bars 1512000..1529279
D|dr recipe ws1Mage + ws13m at 15.0/85.0 wob 0|rebuilt vs rig.DR: 0 of 1632960 bars differ
W|MECH bars 2768|rule#1 cut 1673|EMITTED 1095|momentum_true calls 53958|flat_run_at calls 212180
R|run|WALK FIRES FROM|last emitted bar|bars|dr|arm bar
R|1|00:27:35|00:31:20|46|+1|00:19:20
R|2|02:40:35|02:44:20|46|-1|02:38:10
R|3|03:38:00|03:42:25|54|+1|03:36:55
R|4|05:44:10|05:47:05|36|+1|05:30:05
R|5|07:00:40|07:04:25|46|-1|06:57:25
R|6|08:09:15|08:09:30|4|-1|08:06:20
R|7|08:12:45|08:16:30|46|-1|08:06:20
R|8|09:02:15|09:06:30|52|-1|08:06:20
R|9|11:30:20|11:34:05|46|+1|10:32:30
R|10|11:34:15|11:34:55|9|+1|10:32:30
R|11|11:37:00|11:42:30|67|+1|10:32:30
R|12|13:05:25|13:11:20|72|-1|13:01:55
R|13|13:54:20|13:55:55|20|+1|13:49:15
R|14|14:50:00|14:53:45|46|+1|14:48:00
R|15|15:13:00|15:15:00|25|-1|15:10:50
R|16|16:16:10|16:19:20|39|-1|16:08:45
R|17|16:21:20|16:26:00|57|-1|16:08:45
R|18|17:59:25|18:03:55|55|-1|17:58:30
R|19|18:11:35|18:18:00|78|-1|17:58:30
R|20|18:20:00|18:24:40|57|-1|17:58:30
R|21|22:24:10|22:27:55|46|-1|21:10:15
R|22|23:18:50|23:27:10|101|-1|21:10:15
R|23|23:27:20|23:31:10|47|-1|21:10:15
V|validated bar|emitted|is it a run FIRST bar|arm bar|arm dr
V|00:27:35|YES|YES|00:19:20|+1
V|02:40:35|YES|YES|02:38:10|-1
V|03:38:00|YES|YES|03:36:55|+1
V|09:02:15|YES|YES|08:06:20|-1
V|14:50:00|YES|YES|14:48:00|+1
V|17:59:25|YES|YES|17:58:30|-1
V|18:20:00|YES|YES|17:58:30|-1
V|22:24:10|YES|YES|21:10:15|-1
V|23:18:50|YES|YES|21:10:15|-1
M|validated bars 9|reproduced as a run FIRST bar 9|missing 0
M|run first bars the walk emits that are NOT validated bars|14  05:44:10, 07:00:40, 08:09:15, 08:12:45, 11:30:20, 11:34:15, 11:37:00, 13:05:25, 13:54:20, 15:13:00, 16:16:10, 16:21:20, 18:11:35, 23:27:20
S|the day's shape|field|validated|this run|match
S|mech|2768|2768|YES
S|cut|1673|1673|YES
S|emitted|1095|1095|YES
S|runs|23|23|YES
M|PASS|all 9 validated bars reproduced, and the day's shape is unchanged
```

```
P1 warmup is bounded                     OK  565 bars checked
P2 arm = first bar the run reaches wob   OK  arm at bar 6
P3 MID cross cancels either direction    OK
P4 dr change restarts the run            OK  re-arm at bar 9
P5 dr 0 cannot arm                       OK  arm at bar 8 once dr arrives
episodes match the live array            OK  3 episodes
step refuses non-consecutive bars        OK
Q1 qualify counter == sorted form        OK  200 trials
Q2 rev mask == coil_exit._knowable       OK  3000 bars, 0 disagree
Q3 no state crosses an arm               OK  episode 2 arm at bar 26
Q4 race lookback trailing + inclusive    OK  11 fires
step refuses non-consecutive bars        OK
```

**The acceptance test can fail.** `arm_wob` (bars ws5Mage must stay past its fence to set the arm),
changed in a scratch copy only:

| knob | exit | what it named |
|---|---|---|
| `arm_wob` 6 → 7 | 1 | `M\|FAIL\|missing 03:38:00` · `mech moved: validated 2768, this run 2754` · `cut moved: 1673 → 1671` · `emitted moved: 1095 → 1083` |

- Harness mutation A7 (the arm one bar late) gives the same output row for row.

## 2 — Mutations: what each check catches

Each mutation is one change, applied alone. The last column is the 09-01 walk through the acceptance
test's logic: MECH bars / rule#1 cut / EMITTED / runs. Unmutated: 2768 / 1673 / 1095 / 23.

| id | the one change | checks that fail | acceptance on 09-01 |
|---|---|---|---|
| A1 | ws5Mage crossing 50 no longer resets `_run` (count of consecutive bars past the fence on the dr side) | none | PASS, identical |
| A2 | ws5Mage crossing 50 never cancels the arm | P1, P3, Q3 | FAIL 1921/1152/769/24, 6 of 9 missing |
| A3 | the 50-cross test fires at exactly 50 | none | PASS, identical |
| A4 | the dr-consistency clause removed | none | PASS, identical |
| A5 | the dr 0 guard removed | P5 | PASS, identical |
| A6 | the arm bar is re-set on every bar of the run | P2, episodes, Q1, Q3, Q4 | FAIL 569/303/266/9, 8 of 9 missing |
| A7 | the arm sets one bar late | P2, P3, P4, P5, Q3 | FAIL 2754/1671/1083/23, 03:38:00 missing |
| A8 | the fence test is strict (`> 75`, `< 25`) | none | PASS, identical |
| A9 | the arm's dr is re-read from each bar's dr while the arm is live | none | FAIL 3066/1925/1141/27, all 9 kept |
| A10 | ArmState's skipped-bar guard removed | arm guard | PASS, identical |
| A11 | `warmup_from` always returns bar 0 | none | PASS, identical (nothing in the walk calls it) |
| A12 | `warmup_from` returns the bar after the 50-cross | none | PASS, identical (nothing in the walk calls it) |
| A13 | `episodes` end bar = the last live bar | episodes | PASS, identical (nothing in the walk calls it) |
| L1 | the turn requirement removed | none | PASS, identical |
| L2 | the turn may land on the arm bar | none | PASS, identical |
| L3 | the turn is the coil ticking UP | Q4 | PASS, identical |
| L4 | the turn ignores the arm's dr sign | none | PASS, identical |
| L5 | a timeframe that has departed can depart again | Q1 | FAIL 2851/1696/1155/29, 17:59:25 missing |
| L6 | the qualify set excludes ws7 | Q1 | FAIL 2756/1673/1083/23, all 9 kept, 15:13:00 → 15:14:00 |
| L7 | qualify needs 4 departures | Q1 | FAIL 2740/1671/1069/22, 03:38:00 and 14:50:00 missing |
| L8 | the qualify bar is overwritten by every later departure | none | PASS, identical |
| L9 | a departure counts without the timeframe having been momentum-true | Q1, Q3 | FAIL 2927/1730/1197/29, 17:59:25 missing |
| L10 | the race set excludes ws4 | Q4 | FAIL 2615/1669/946/21, 17:59:25 missing |
| L11 | every flat-run bar counts as a start, not only the first | none | FAIL 2859/1763/1096/22, all 9 kept |
| L12 | the race's previous-bar flags carry across arms | none | PASS, identical |
| L13 | flat-run starts carry across arms | none | PASS, identical |
| L14 | the race window excludes the bar 48 back | Q4 | FAIL 2763/1669/1094/23, all 9 kept |
| L15 | the race needs 2 starts | Q4 | FAIL 2554/1538/1016/23, 17:59:25 missing |
| L16 | race starts must be at or after both the turn and the qualify | none | FAIL 2706/1663/1043/21, 03:38:00 and 17:59:25 missing |
| L17 | the ws1mage-rev leg ignored | none | FAIL 7708/5829/1879/24, 7 of 9 missing |
| L18 | the `k < max(_turn, _qual)` clause removed | none | PASS, identical |
| L19 | the per-arm reset skipped when a new arm sets | Q3 | FAIL 2935/1733/1202/29, 17:59:25 missing |
| L20 | LeashWalk's own skipped-bar guard removed | none | PASS, identical |
| L21 | the rev mask is true from the cross bar, ignoring `sig_conf` | Q2 | FAIL 2876/1742/1134/22, 7 of 9 missing |
| L22 | the rev lookback is 47 bars | Q2 | FAIL 2723/1648/1075/23, all 9 kept |
| L23 | the rev lookback is measured from `sig_conf` instead of the cross bar | Q2 | FAIL 2901/1745/1156/22, 09:02:15 missing |
| L24 | `walk()` feeds each bar's dr, not the arm's dr, to the mom / fr / rev reads | none | FAIL 3069/1927/1142/27, all 9 kept |

| check | the mutations it catches |
|---|---|
| P1 warmup is bounded | A2 |
| P2 arm on the first bar the run reaches wob | A6, A7 |
| P3 a 50-cross cancels | A2, A7 |
| P4 a dr change restarts the run | A7 |
| P5 dr 0 cannot arm | A5, A7 |
| episodes | A6, A13 |
| arm guard (ArmState skipped bar) | A10 |
| Q1 qualify counter | A6, L5, L6, L7, L9 |
| Q2 rev mask = `_knowable` | L21, L22, L23 |
| Q3 no state crosses an arm | A2, A6, A7, L9, L19 |
| Q4 race lookback | A6, L3, L10, L14, L15 |
| leash guard (LeashWalk skipped bar) | none. `leash_walk.py:133` calls `ArmState.step`, which raises first (`arm_state.py:66-68`) |
| acceptance, 09-01 | A2, A6, A7, A9, L5, L6, L7, L9, L10, L11, L14, L15, L16, L17, L19, L21, L22, L23, L24 |

**No check catches these — neither the 12 nor the acceptance test:**

| rule | id | count on 09-01 (17,280 bars) | note |
|---|---|---|---|
| a 50-cross resets `_run` | A1 | 50-crosses while `_run` > 0: 0 of 326 | P3's setup zeroes the run through the fence test, not this reset. P3's docstring says "and resets the run" (`test_arm_state.py:15`) |
| a 50-cross at exactly 50 | A3 | — | an exact-value edge |
| dr-consistency clause | A4 | times it decided: 0 | dead while 25 < 50 < 75: a dr flip mid-run needs a 50-cross, which has already zeroed `_run` |
| fence inclusive at 25/75 | A8 | — | an exact-value edge |
| how tight `warmup_from` is | A11, A12 | — | nothing calls it. P1 passes even when it returns bar 0 |
| turn requirement | L1 | — | |
| turn strictly after the arm bar | L2 | — | |
| turn reads the arm's dr sign | L4 | — | the turn's direction (L3) is caught by Q4 only |
| qualify = the 3rd departure | L8 | — | emitted bars do not change; the `qualify` / `scan` fields in the walk's reported state do |
| race state reset per arm | L12, L13 | — | Q3 only asserts on departures |
| `k < max(_turn, _qual)` | L18 | times true: 0 | `_turn` and `_qual` are only ever set to the current bar (`leash_walk.py:144, 156`) |
| LeashWalk's skipped-bar guard | L20 | — | ArmState's guard fires first |

**Caught only by the acceptance test — one day:** A9 (the arm carries its dr), L11 (a race start is
the first bar of a flat run), L16 (race starts not limited to after the turn and qualify), L17 (the
ws1mage-rev leg), L24 (`walk()` routes the arm's dr).

- L16 reproduces the numbers in the `leash_walk.py:23-26` docstring exactly.

## 3 — Causality verdict on `arm_state` and `leash_walk`

No read in either stepper gives a verdict at bar k using bars after k. One read is DEFERRED, the rev
mask. This re-derivation agrees with `CAUSALITY.md`'s 1001 table.

| read | bars it reads | the bar the verdict is given at | label | file:line |
|---|---|---|---|---|
| 50-cross cancel | ws5Mage at k and k−1 | k | CAUSAL | `arm_state.py:70-74` |
| fence test on the dr side, and the dr 0 guard | ws5Mage at k, dr at k | k | CAUSAL | `arm_state.py:83` |
| run count | carried `_run`, dr at k−1 and k | k | CAUSAL | `arm_state.py:84-87` |
| arm set | carried `_run` and `live`; writes arm bar = k, arm dr = dr[k] | k | CAUSAL | `arm_state.py:88-91` |
| `warmup_from` | ws5Mage at j and j−1, walking back from k | returns a bar ≤ k | CAUSAL | `arm_state.py:95-108` |
| turn | combined coil at k and k−1, carried arm bar and arm dr, only for k > arm bar | k | CAUSAL | `leash_walk.py:142-144` |
| qualify | `mom(t)` at k for ws7..ws23; carried seen / departed sets and count | k | CAUSAL | `leash_walk.py:147-156` |
| `mom(t)`, as `report_leash_walk` supplies it | `ws{t}r` at the 3 sample bars ending at k; quadratic fit window `r[k−nb+1 : k+1]`; r at k; last seam step ≤ k | k | CAUSAL | `walk_mom_models.py:138-142`, `momo_core.py` sample index and quadratic slice, `momo_gated.py:95`, `momo_seam.py:58-66` |
| race starts | `fr(t)` at k for ws4..ws23; carried previous-bar flag per timeframe; starts older than k−48 dropped | k | CAUSAL | `leash_walk.py:159-167` |
| `fr(t)` | `ws{t}r` at k−2..k | k | CAUSAL | `test_points.py:60-71` |
| scan + race count | carried turn and qualify bars; starts in [k−48, k] | k | CAUSAL | `leash_walk.py:170-176` |
| rev mask | legs whose cross bar is in [k−48, k] and whose `sig_conf` ≤ k | k | **DEFERRED** — the cross is named at its own bar, usable only from `sig_conf` = cross + 3 bars = 15 s | `leash_walk.py:198-204` |
| rev legs | gcws30Mage at bars ≤ `sig_conf`; past 85/15 then back inside for 4 bars | `sig_conf` | CAUSAL | `jig.py:124-138` |
| `walk()` routing | ws5Mage, dr, coil at k and k−1; mom / fr / rev read at the arm's dr carried from bar k−1, else dr[k] | k | CAUSAL | `leash_walk.py:226-233` |

The two dr series are not lookahead. Each carries the bar it started from, so a live run that starts
later can hold a different dr while both sides stay causal.

| input | built from | depends on everything since | file:line |
|---|---|---|---|
| `rig.DR`, the walk's dr | ws1Mage + ws13m, 85/15, no wob | bar 0 of the 94.5-day tape | `sweep_v3_signal.py:97-106` |
| `rig.DRW`, rule#1's dr | ws1Mage + ws13m, 75/25, wob 8 | bar 0 of the tape | `sweep_v3_signal.py:107-109, 184` |
| ArmState + LeashWalk state | — | the last ws5Mage 50-cross before the arm | `arm_state.py:70-74`, `leash_walk.py:137-139` |

Where the 09-01 walk starts, checked against `CAUSALITY.md:35-39` (`seed.py`):

| starting bar | MECH bars on 09-01 | bars that differ from a start at 00:00 | arm live at 00:00 |
|---|---|---|---|
| 00:00 (what the acceptance test does) | 2768 | — | no |
| 3 h earlier | 2768 | 0 | yes, armed 08-31 22:30:15 |
| `warmup_from(00:00)` = 08-31 22:29:25 | 2768 | 0 | yes |
| 24 h earlier | 2768 | 0 | yes |
| `warmup_from(12:00:00)` | 1,187 bars = 98.9 min back, seed 10:21:05 | — | matches the doc |

## 4 — The "Known open" table: confirm or refute

| item | result |
|---|---|
| the evidence is one day: 9 bars, 16 armed episodes | confirmed 9 of 9 and 16, counting from a 00:00 start. Started earlier (`eps.py`), 17 episodes touch 09-01: the extra one is armed 08-31 22:30:15 at dr −1, cancelled 00:15:45, and adds 0 MECH bars |
| 14 run-first bars that are not validated | confirmed — the same 14 |
| `walk_rule1_back_min` 5.0 | confirmed: the v4 row is 5.0 min = 60 bars. The only code that reads it is `report_leash_walk.py:112`, on 09-01 |
| `k < max(_turn, _qual)` is dead | confirmed: true on 0 of 17,280 bars; removing it changes nothing |
| dr-consistency clause is dead | confirmed: decided 0 of 17,280; removing it changes nothing |
| turn requirement, turn strictly after the arm, 50-cross `_run` reset: no test, identical on 09-01 | confirmed for all three. The turn's sign (L4) and direction (L3) are also identical on 09-01 |
| `warmup_from` and `episodes` have no caller in the mech | confirmed: the only caller is `tests/test_arm_state.py` |
| `walk_lb_bars` 48 does not bind on 09-01 | true for the 9 validated bars, false for the day's shape. Unbounded: 2977/1881/1096/22, all 9 kept, the 23:27:20 run-first bar disappears |
| `fastverdict.py` names a `verify()` that does not exist | confirmed. Its `sideways_mask` is never called on octo-freedom's path: the only caller is `Rig.sideways`, used only by `sweep_v3_signal.run` (`:209`), the v7 chain |
| `latch_wob`'s live window is unmeasured | confirmed and still unmeasured: `strategy.py:23, 39` gives a 24 h buffer + 80 h warmup = 104 h. The same dependence applies to `rig.DR`, which the list does not name. ADDED 1001: `ops/run_o9live.py:37` overrides those to 8 h + 6 h = 14 h, which is what o9-live runs |
| hardcoded values | confirmed: `MOMO_SAMPLES` 3 and `MOMO_TOL` 2.0 (`report_leash_walk.py:73-74`), `MID` 50.0 (`arm_state.py:34`), the five `WS1_CFG` values (`walk_mom_models.py:66-67`), `SPAN_MIN` 10 (`:59`). Also on the path, not on the list: `'ws1'` as ws1mage-rev's line (`report_leash_walk.py:173`) and `mid=50.0` in rule#1's `anchor_floater` call (`sweep_v3_signal.py:185`) |
| `build_wsf_trades.py` | confirmed: `WIN_MS` is 09-01..09-06 (`build_wsf_trades.py:66`). Not on octo-freedom's path |

## 5 — Doc statements that contradict the machine

| where | statement | what the code does |
|---|---|---|
| `CODE_MAP.md:97` | "`latch_wob` IS THE WALK'S dr" | the walk reads `rig.DR`, the 85/15 no-wob latch (`report_leash_walk.py:180`). `latch_wob` (`rig.DRW`) is rule#1's dr (`sweep_v3_signal.py:184`) |
| `OPEN.md:16`, Ruled table, not struck | "dr producer: `latch_wob` at `LATCH_W` 8" | same as the row above; `OPEN.md:39` holds the octo-freedom ruling |
| `OPEN.md:27`, Ruled table, not struck | "gate window: backward-only, 7 min" | rule#1 reads 60 bars = 5 min (`report_leash_walk.py:112, 181`) |
| `OPEN.md:24`, Ruled table, not struck | config v3, key `wtc_v3_v7_rule1_gateopen_mae0.70` | the walk loads v4, key `wtc_v4_v7_rule1_gateopen_mae0.70` |
| `README.md:142` | "the knobs: `wsf_trade_config` v4" | only the walk's 18 rows come from v4. Rule#1's fence, oob and `div_tf`, and `rig.DRW`'s latch knobs, come from v3 through `Rig.Ct`. The rev lookback, momentum fence, `sig_line` and `coil_lines` come from `wsf_dtf_v3_config`. v3 and v4 agree on all 18 shared rows |
| `README.md:144` | "the exits and the stop: `trade_walk.py`, `mae_cap` 0.70 — unchanged" | no repo code feeds WALK FIRES FROM bars into `trade_walk.walk`. The 09-01 MAE/MFE (`NOTES:447-469`) came from a scratch `mae.py` not in the repo |
| `CAUSALITY.md:33`, `arm_state.py:24-27` | "THE ARM'S WARMUP IS BOUNDED, AND THAT IS WHAT MAKES IT LIVE-SAFE" | the arm's own fields are bounded (seeding: 0 bars differ). The dr it reads is seeded at bar 0 of the tape (`sweep_v3_signal.py:99-106`) |
| `trade_walk.py:119` | "`pxs` = DEMA(close, 2) on the event tape" | `RECON.md:137` corrected this on 1001: DEMA over the full 5 s base |
| `trade_walk.py:5` | "the signals are `wsf_leash.wsl_sig_utc`" | octo-freedom opens on WALK FIRES FROM bars |
| `NOTES_momtf_mechdev.md:481-496` | "6 checks", "5 checks", "ALL 11 TESTS PASS", check G `gate_open(k) == gate_open(k, 84)` | 7 + 5 = 12 checks; no G check in any file under `tests/` |
| `NOTES_momtf_mechdev.md:484` | "`WALK_V = 4` · 31 rows, 13 new" | 36 rows, 18 new (`trade_config.py:88-124`; DB v4 count 36) |

Line numbers are as of `3fed91a`. `OPEN.md` has since grown; see `1001_open_items.md` for where they sit now.

## 6 — The ten mechs of `octo-freedom`

| mech | how it contributes |
|---|---|
| arm | ws5Mage ≥ 75 at dr +1, or ≤ 25 at dr −1, for 6 bars in a row = 30 s sets the arm on the 6th bar and keeps that bar's dr. ws5Mage crossing 50 either way cancels it. Nothing else is tested while it is off, and every later test reads its dr |
| turn | the first bar after the arm bar where the combined coil — (m + Mage)/2 − r, summed over gcws30 and ws1, times the arm's dr — is lower than on the bar before. Nothing emits before this bar |
| qualify | the bar on which the 3rd distinct timeframe from ws7..ws23 leaves the momTF bucket, having been momentum-true since the arm. Only each timeframe's first departure counts. Nothing emits before this bar |
| race | at least 1 flat-run start in the last 48 bars = 4 min, including the current bar. A flat run is a ws4..ws23 r line beyond 17/83 on the dr side for 3 bars with max − min ≤ 2.0 r points; it counts on its first bar. Starts before the turn or qualify still count |
| ws1mage-rev | a gcws30Mage cross from beyond 85/15 on the dr side back inside, with the cross bar in the last 48 bars = 240 s and 4 bars held inside already printed (`sig_conf` ≤ bar) |
| rule#1 | on a bar that passes the five tests: ws1r beyond 27/73 on the dr side AND (ws2r OR ws3r) beyond it, anywhere in the last 60 bars = 5 min — OR the scenario leg (ws1r divergence, with ws2r, ws3r and gcws30r beyond 15/85 in the same window). Its dr comes from the 75/25 wob-8 latch |
| WALK FIRES FROM | bars that pass the five tests and rule#1 form runs of consecutive bars; the first bar of each run is the signal. 23 on 09-01 |
| opposing-dr close | a WALK FIRES FROM bar whose dr is opposite to the open trade's closes it and opens the new trade. A same-dr bar does nothing |
| dr-flip backstop | after the dr has been on the far side of the trade's dr, the first bar it flips back closes the trade. Nothing opens on that bar |
| stop | closes the trade on the first bar px moves 0.70% of the entry against the trade's dr. It wins a same-bar tie with the other two exits |

- No file in the package lists ten mechs. This split is the recon session's own count. The dr series
  sits inside every row as the side being tested; counted as its own row, the list is eleven.
- The trade-side dr in the bottom three rows is the latch_wob series, as the scratch 09-01 MAE/MFE
  run used it (`NOTES:447`). That is a reading of a scratch script, not repo code.

## 7 — What to build first, as reported

Recommendation: a producer for o9-live that outputs WALK FIRES FROM bars, proved offline first by
replaying 09-01 bar by bar (bars ≤ k only) and asserting it reproduces `report_leash_walk`'s 23
run-first bars exactly. `CODE_MAP.md:117-128`'s five steps are the v7 producer.

- CORRECTED 1001, after reading the live side: the report said the producer "plugs into
  `ops/run_o9live.py:29`'s producer map". That map supplies ENTRIES only. `StrategyLoop.intents`
  (`optimus9/live/strategy.py:69-109`) applies its own exits (`lr_exit_v2`, `strand_rescue`), runs
  Buy and Sell as independent books with pyramids, and stops each leg at `lr_config.sl` from its
  fill. None of that is `trade_walk`. octo-freedom needs its own decide layer, not a producer entry.

The three decisions it asked for, and what `OPEN.md` says now:

| # | decision | `OPEN.md` after 1001 |
|---|---|---|
| 1 | re-walk a bounded window every bar vs carry state live | ruled: bounded re-walk |
| 2 | the window length | not ruled. Measured on `rig.DR`: longest stretch 7.2 h, 0 of 2,487 reach 24 h, against the 104 h window. `rig.DRW` not measured |
| 3 | signals only vs run the three exits | ruled: signals become trade actions; P&L as a percentage |

## What was NOT measured

| not measured | why it matters |
|---|---|
| any day other than 09-01 | every mutation verdict above is one day |
| `rig.DRW`'s stretch distribution | decides whether rule#1's dr converges inside a bounded live window |
| mutations of `rule1_gate`, `trade_walk`, the line builders | only `arm_state.py` and `leash_walk.py` were mutated |
| the exits on octo-freedom's fires | nothing in the repo walks WALK FIRES FROM bars through `trade_walk` |
| why L1–L4 (the turn) are identical on 09-01 | the order of turn vs qualify per episode was not measured |
| a bar-by-bar replay of a live-shaped producer | not built; it is the recommended first build |
