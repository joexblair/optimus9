# exhaustion v2 — `exhv2`

**Joe 0730.** A re-timing of the exhaustion signal, **adjunct to RPL, not part of it**. RPL's ladder,
`rp_matrix`, `seeded_ladder` and `current_tf` are untouched. exhv2 runs on **TF ≤ 22 only** — s4, s15, s22 —
with **standalone r-prediction** on those three lines.

Build notes: `transfer/260730_exhv2_notes.csv` — 14 hand-marked rows with a `corrected_conf` target.
Prerequisite mechanic: `docs/rpred_spec.md`.

---

## 1. Vocabulary (Joe's preamble, verbatim intent)

| term | meaning |
|---|---|
| **momentum** | r past 50 (`>= 50` for bias bull) **AND** r tracking a fuzzy straight line for the last 45 min |
| **0rp** | none of s4, s15, s22 are r-pred'd |
| **0momo** | no momentum |
| **rev** | reverse trade, using the finishers |
| **Moob** | s4Mage out of bounds |
| **es_rpred_utc** | whichever mechanism printed the signal |
| **sideways** | s15r or s22r have horizontal momentum. Needs a floor knob |

- **"flat" in the source notes means horizontal**, not "no momentum". This doc uses `sideways` for the state
  and never "flat" for a slope

---

## 2. Trigger and scope

- exhv2 is evaluated **once per `es_rpred_utc` print**. On the current table that is **87 opportunities**
- **TF ≤ 22.** The lines in play are s4, s15, s22
- **r-prediction on s4/s15/s22 is standalone** — a direct `predict_breach` evaluation on those lines. It is
  not `rp_matrix`, not the ladder, and not gated by the RPL clean/dirty flag

---

## 3. The flow

```
unless there is not an es_rpred_utc signal
- walk forward on s4
- if s4M is oob
-- the same process applies if the r-pred signal is on the MAE or MFE side. If on the MFE side, bias
   reverses. The walk to the first s4M oob tells you which side you are on
-- test s15s22 for bias-aligned momentum
-- if s15s22 has momentum
--- unless s15r or s22r are dirty
---- test bias-aligned r-predict on s{[15,22]}r
---- if either are r-pred'd
----- rev on next s{r-pred'd TF}x X (boundary, r, Mage as a race)
--- #momentum branch
--- rev on next s{lowest momo TF}x X (boundary, r, Mage as a race)
```

**Branches the notes add that the text does not state:**

- **dirty → fall through to s4.** *"if s4 fails to get higher support, the leg is exhausted and
  `s4xXm over/under Moob` will signal (and handoff to the finishers)"* — Joe. Row `0520 07:42`
- **sideways → `EXIT`, not `rev`.** *"we EXIT only when momo is sideways. A sideways market is unstable —
  rev is too risky"* — Joe. Rows `0521 18:49`, `21:57`, `22:01`

---

## 4. The walk

- forward on **s4**, bar by bar, from the exhaustion bar
- **nothing terminates it before s4Mage reaches OOB** (Joe). No horizon, no cap
- it may pass over the side it was looking for: `0521 18:49` finds **no low s4M**, keeps walking, and
  finds a **hi** s4M
- **the walk destination is where everything downstream is evaluated** — r-pred, momentum, dirty, sideways.
  Not the exhaustion bar
  - `0521 05:13` and `0521 08:50` both record `walk:s4M@05:20`
- **MFE-side detection**: if the first s4Mage OOB is on the side opposite to the bias, the signal was on the
  MFE side and **bias reverses**

---

## 5. Momentum

**Definition.** Evaluated at the walk bar, on s15r and s22r independently.

1. **level** — `r >= 50` (bull) / `r <= 50` (bear), read **at the walk bar**
2. **slope** — `> 0` (bull) / `< 0` (bear) over the **45 min leading up to** that bar
3. **straightness** — the line over those 45 min is ~straight

Joe: *"it needs to have a slope > 0 plus straightness, before r >= 50. Eg the walk finds r at 63
(qualified), and the line below it must be ~straight and slope > 0 (qualified)."*

**Sampling.** 9 point-samples, one per 5 min, ending at the walk bar. 5 min = 60 bars at the 5 s grid.
Point-sample, not a bucket mean — matches *"if you collected 9 samples, 1 per 5 minutes"*.

**Metrics.** Measured on Joe's two reference series:

```
momo     = [ 9.5, 12, 11.5, 13.5, 15, 19, 24, 29, 32]
sideways = [64, 67, 63, 59, 70, 65, 62, 68, 59]

          slope /sample  slope /min    R²      eff    step-agree   RMSE   range
momo          2.858        0.572     0.921    0.957     0.88       2.16    22.5
sideways     -0.217       -0.043     0.024   -0.111     0.62       3.56    11.0
separation:   13.2x                  38.2x    8.6x      1.4x      0.61x
```

**Two knobs, because each fails alone:**

| knob | role | momo | sideways | proposed |
|---|---|---|---|---|
| `momo_r2_min` | the "fuzzy straight line" | 0.921 | 0.024 | **0.50** |
| `momo_slope_min` | the floor knob — separates momentum from sideways | 2.858 | 0.217 | **1.0** /5-min sample |

- **R² alone** passes a straight but horizontal line — which *is* sideways
- **slope alone** passes a noisy line with a large net move
- step-agreement (1.4×) and RMSE (0.61×) are too weak to carry a threshold — **not used**
- efficiency (8.6×) tracks R² and adds nothing independent — **not used**
- anything in R² 0.10-0.85 and |slope| 0.3-2.7 separates the reference pair. **The proposed values are
  proposals; they are Joe's to set**

**Which line wins.** Either s15 or s22 qualifying is enough. **If both, the final cross is on s15x** (Joe).

---

## 6. Cross targets

| form | meaning |
|---|---|
| `X85` | crosses the hi boundary, `HI` = 85 |
| `X15` | crosses the lo boundary, `LO` = 15 |
| `Xr` | crosses r |
| `Xm` | crosses m (mini_bb) |

- the spec's `X (boundary, r, Mage as a race)` is a **three-way race — first to fire wins**. The single form
  named in each note is the race winner recorded after the fact
- **the race is IN** (Joe 0730): *"there's no harm and it handles an outlier"*
- **only s15 or s22 may use Mage as a cross target.** s4 uses m

**Tie-break — same-bar ties, explicit.** Precedent is `build_exhaust.py:134`:

```python
legs = (('r', r, True), ('M', M, True), ('b', np.full(len(r), p['CB'], float), False))
```

and `build_exhaust.py:162` sorts on `(tf, bias, episode, raw)` with **no leg term**, so v1's tie-break is
Python's stable sort falling back on that append order — implicit, never stated.

- exhv2 adopts the same order, **explicitly**: **r → Mage → boundary**
- Joe's spec text lists them "boundary, r, Mage"; that reads as a listing rather than a priority. Flipping
  it is a one-line change and only matters on same-bar ties
- **every target firing on the winning bar is recorded**, not just the winner, so a tie is visible rather
  than silently resolved

**`over Moob` / `under Moob`** — LOCKED, Joe 0731, verbatim:

> *"if you're hi OOB, you need Moob to be under (so that the x-cross-m event is contained to a profitable
> space). inverse for lo oob."*

- hi-side walk → the `s4x × s4m` cross must sit **above** s4Mage: `x > Mage` at the cross bar
- lo-side walk → the cross must sit **below** s4Mage: `x < Mage`
- it is a **positional** test between x and the Mage value, not a test of whether Mage is OOB at the cross
- **KNOWN WEAKNESS**: when s4Mage has crossed to the far side by the cross bar the test is vacuous.
  `0520 07:42` fires SHORT at 07:58 where s4Mage is −3.71 (lo-OOB) and `x > −3.71` passes for almost any x.
  The strict alternative — require s4Mage still OOB on the walk side at the cross — pushed two signals
  three days out and was rejected.

Which side s4Mage is out on also sets the trade direction:

- **`over Moob`** → hi breach → **short**. The s4x × s4m cross must occur **above** s4Mage
- **`under Moob`** → lo breach → **long**. Inverse

Joe: *"for a hi breach the x X m cross must be 'over' Moob, ie higher."*

**Confirmed positional** (Joe: *"ie higher"*). At the cross bar `s4x == s4m` and that value is above the
**s4Mage value**. A hi Moob means `s4Mage > HI` = 85, so the cross is above 85 too — implied, not a
separate test.

**The signal — A ungated, ADOPTED Joe 0731.** *"let's adopt A ungated as the exit signal."*

Joe 0731, clarifying: *"I was using exit generically for exit and rev."* So **A is the signal on all 87
rows**, whatever `act` says. It is:

> the **first `s15x × s15m` cross at or after the WALK bar, in the trade direction, with no qualify and no
> gate** — the arm the A/B called `A ungated`.

**Naming.** `signal` (`v2_sig_ms`) is the emitted moment; `act` is the two-valued classifier `rev` / `EXIT`.
`act` says which kind, `signal` says when. No third term.

- the **branch race is still computed and stored** (`v2_race_ms` / `v2_race_utc`) — it decides `act`, so it
  stays a classifier, and it stays visible for validation
- **`over/under Moob` still gates the race** on s4-branch rows; it does **not** gate A — A is ungated by
  definition
- Joe's validation row: `0525 20:56` walk, branch `momo`, race `Mage s22` at `21:20` → **A at `21:50`**

Evidence (distance to the next `swing_detect` 1.00% pivot, measured inside each of the 87 `[walk, signal]`
windows — two-stage protocol, timestamps banked first):

| arm | n | mean | median | \|err\| mean | \|err\| median | w15 | w30 |
|---|---|---|---|---|---|---|---|
| exhv2 signal (base, s4 `m`) | 87 | −10.3 | −1.9 | 48.7 | 34.4 | 29 | 38 |
| **A ungated `s15x × s15m`** | 87 | −22.8 | −5.8 | **42.5** | **16.7** | **40** | **51** |
| B `s15a` event (qualify) | 87 | +888.2 | +471.9 | 899.8 | 471.9 | 22 | 24 |
| C `s15a` + x × m | 87 | +1022.5 | +737.6 | 1030.2 | 737.6 | 17 | 19 |

`s15a` qualify is true on only **0.29%** of bars (hi) / **0.26%** (lo) — far too sparse to serve as a
"what happens next" trigger, which is why B and C are unusable.

**Movement, all 87 rows:** 82 moved, 5 unchanged. 57 fire **earlier** than the race, 25 later.
`A − race` median **−5 min**, mean **−12**; worst late **+76**, worst early **−121**. By branch:
`momo` n=45 median **−3 min**, `s4` n=42 median **−20 min** — the pull-forward is almost entirely the s4
delegation rows. `A − walk` lag: median **10 min**, mean 18, max 118.

**Worst row:** `0521 21:04` walk → A at `23:02`, 118 min. One walk bar reached from two r-preds
(`20:40`, `20:54`), so it is one event counted twice. No floor applied — OPEN.

**STILL OPEN — EXIT colouring.** 20 of the 87 rows are `EXIT` and still paint red/green like a reversal,
so an exit is indistinguishable from an entry on the chart. Raised twice, not yet ruled on.

---

## 7. clean/dirty on s4, s15, s22

**Same logic as RPL** (Joe 0730), **separate instance**. `build_rplwalk2.line_state` covers TF22-120, so s4
and s15 have no flag at all and s22's RPL flag belongs to a different mechanic.

| event | condition | scope |
|---|---|---|
| **dirty** | this line's **x crosses the boundary or crosses r** **AND** the line is outside its fence | **line-local** |
| **clean** | **either** x crosses back through r **or** r returns to the FH/FL fence | **line-local** |

Joe 0731: *"'exhaustion' only applies to RPL. The definition needs to state 'an x crossing boundary or r'."*
exhv2's spend is this line's own x, not the applied-exhaustion set — the flag is fully line-local.

- bull: spend = x crosses **down** through r or **down** through `HI` = 85; clean = x crosses **over** r,
  or r falls back below `FH` = 70
- bear: spend = x crosses **up** through r or **up** through `LO` = 15; clean = x crosses **under** r,
  or r rises back above `FL` = 30
- direction matches `_polar`: `WOB_DIR` = −1 and `CB` = `HI` for bull
- **lines start dirty.** At bar 0 a line already outside the fence cannot be told from a retreat. Cleared by
  the first recovery of either kind — x back through r, or r re-entering the fence
- fence crossings `cross_wob`-debounced at `WOBN` = 9 bars = 45 s
- full rationale and the measurements behind each choice: `docs/rpred_spec.md` §4

**Superseded** (Joe 0731): the spend is neither `rpl_exh_applied` nor exhv2's own output — it is this
line's x crossing the boundary or r. No iteration needed, no self-reference.

---

## 8. The marked rows

`transfer/260730_exhv2_notes.csv`. `corrected_conf` is the scoring target.

| es_conf_utc | es_rpred_utc | note | corrected_conf | Δ min |
|---|---|---|---|---|
| 0520 06:26 | 0520 05:50 | s15momo. 1522 rp. rev s15xX85 | 06:14 | −12 |
| 0520 07:42 | 0520 07:03 | 1522 dirty. 0rp. rev s4xXm over Moob | 07:22 | −20 |
| 0520 10:26 | 0520 10:21 | 0rp. 1522momo. rev s15xX85 | 10:32 | +6 |
| 0520 10:50 | 0520 10:48 | MFEside. rev low:s4xXm under Moob. 0rp. 0momo | 11:50 | +60 |
| 0520 10:59 | 0520 10:59 | MFEside. rev low:s4xXm under Moob. 0rp. 0momo | 11:50 | +51 |
| 0520 13:25 | 0520 12:43 | s4rp. 0momo. rev:s4xXm over Moob | 13:00 | −25 |
| 0520 17:58 | 0520 15:52 | 0rp. 1522momo. rev s15x-cross | 16:08 | −110 |
| 0521 04:19 | 0521 02:05 | MFEside 15momo. 0rp. rev low, s15xX15 | 03:00 | −79 |
| 0521 05:13 | 0521 04:36 | MFEside. walk:s4M@05:20. 22momo. 15rp. rev low:s15xXr | 06:48 | +95 |
| 0521 08:50 | 0521 05:30 | MFEside. walk:s4M@05:20. 22momo. 15rp. rev low:s15xXr | 06:48 | −122 |
| 0521 11:31 | 0521 10:27 | MFEside. 15rp. 15momo. rev low: 15xX15 | 10:40 | −51 |
| 0521 18:49 | 0521 18:48 | MFEside BUT walk finds no low s4M. 1522momo sideways: EXIT on next s4xXm over Moob | 19:20 | +31 |
| 0521 21:57 | 0521 20:40 | 1522momo sideways: EXIT on next s4xXm over/under Moob | 20:48 | −69 |
| 0521 22:01 | 0521 20:54 | 1522momo sideways: EXIT on next s4xXm over/under Moob | 21:08 | −53 |

- **9 corrections earlier, 5 later**, range **−122 to +60 min**
- **de-duplication**: `05:13` and `08:50` share one walk result and one `corrected_conf` — Joe confirmed
  they are the same underlying move, collapsing to a single event at 06:48. exhv2 therefore produces
  **fewer** signals than v1, so a 14-vs-14 comparison is the wrong frame

---

## 9. Branch census over the 14 rows

| branch | n | rows |
|---|---|---|
| momentum → rev on s15/s22 | 6 | 06:26, 10:26, 17:58, 04:19, 11:31, and one of 05:13/08:50 |
| dirty → fall through to s4 | 1 | 07:42 |
| 0rp + 0momo → s4 | 3 | 10:50, 10:59, 13:25 |
| sideways → EXIT | 3 | 18:49, 21:57, 22:01 |
| collapsed duplicate | 1 | 08:50 into 05:13 |

- **MFEside on 7 of 14** — bias reversal is the common case, not the exception

---

## 10. Open items

- **`momo_r2_min` and `momo_slope_min` values** (§5) — proposals of 0.50 and 1.0. Anything in R² 0.10-0.85
  and |slope| 0.3-2.7 separates the reference pair, so these are sweepable rather than blocking
- **the spend signal for the exhv2 clean/dirty instance** (§7) — my reading is `rpl_exh_applied`, the same
  set RPL's flag reads. Using exhv2's own output would make it self-referential
- **nothing built yet.** No code, no table, no measurement against `corrected_conf` — SUPERSEDED, built

---

### 10a. NEXT SESSION, FIRST JOB — the Mage-develop hold (Joe 0731, verbatim)

Three rows Joe read off the chart. Nothing built. `recently` is unmeasured and is the gate on all of it.

> **05-25 21:50**
> -the long signal has been created just after s22Mage has crossed into lo oob. these 2 signals are
> opposing each other - s15Mage and s22Mage should be allowed to develop if either has `recently`
> crossed into OOB
> --first job is to measure `recently`
> --the mechanism will test when exit triggers, and before exit fires. if s{15,22}M has recently crossed
> into OOB, drop the exit trigger
> --walk forward from the start of the flow
>
> same goes for **05-27 15:13**. s22Mage has crossed hi oob, so the 15:13 trigger is dropped.
> the walk then picks a hi oob s4M excursion at 16:08, and fires on s4x cross over Moob
>
> **05-28 09:13**
> -s15momo should have kicked in and delayed the signal to 10:45

Reading notes, to be confirmed before any code:

- Joe's "exit" here is generic — it means **the signal**, `rev` and `EXIT` alike (Joe 0731: *"I was using
  exit generically for exit and rev"*)
- the hold is a **pre-fire test**: at the bar the signal would emit, look back; if `s15Mage` **or**
  `s22Mage` crossed into OOB within `recently`, **drop that trigger** and keep walking
- **`recently` is a duration and is UNMEASURED.** Measuring it is job one. Do not pick a value — Joe named
  the mechanic, not the number
- the 05-27 row shows what happens after a drop: the walk resumes, finds the next hi-OOB `s4Mage`
  excursion at 16:08, and fires on `s4x` crossing **over Moob** — i.e. the existing §6 machinery, re-run
- **"walk forward from the start of the flow"** — the re-walk restarts at the flow start, not at the
  dropped bar
- 05-28 09:13 is a **different** miss: `s15` momentum should have held the signal to 10:45. That is a §5
  momentum-detection question, not the Mage hold. Keep the two separate

Current values on those three rows for reference (from `rpl_exhv2`):

| r-pred | walk | bias | branch cross | signal now | Joe's read |
|---|---|---|---|---|---|
| `0525 20:40` | `0525 20:56` | bear | momo `Mage s22` | **21:50** | hold — s22Mage just crossed lo OOB |
| `0527 15:10` | `0527 15:12` | bull | s4 `m s4` | **15:13** | drop → re-walk → **16:08** |
| `0528 08:20` | `0528 09:05` | bear | momo `boundary s15` | **09:13** | s15 momo should delay → **10:45** |

## 11. Closed

- **the three-way race** — IN. Tie-break `r → Mage → boundary`, explicit, matching `build_exhaust`'s
  implicit append order (§6). All same-bar firings recorded, not just the winner
- **momentum ordering** (§5) — three conditions, all ending at the walk bar: slope > 0, straightness, and
  `r >= 50`. No crossing requirement; the reference momo series runs 9.5 → 32 and never reaches 50, so the
  shape test is level-independent and the level gate is separate
- **`over Moob`** (§6) — positional, not temporal. At the cross bar `s4x == s4m` and that value is above
  `s4Mage`. Joe: *"ie higher"*
- **clean/dirty on s4/s15/s22** (§7) — same logic as RPL, separate instance

---

## 12. The report format — LOCKED

Joe 0731: *"I need consistency on reporting."* Every exhv2 row report uses this and nothing else:

```
  r-pred      | walk        | bias       | s15      s22      act  | branch cross       | signal
  0520 05:50  | 0520 07:48  | bull>bear  | momo     none     rev  | momo   boundary s15 | 0520 08:31
  0520 10:48  | 0520 11:48  | bull>bear  | sideways sideways EXIT | s4     m s4        | 0520 12:22
  0520 12:43  | 0520 13:37  | bull>bear  | curl     curl     rev  | s4     m s4        | 0520 15:09
```

| column | source | notes |
|---|---|---|
| `r-pred` | `rpl_exh_stat.es_rpred_utc` | where the walk starts |
| `walk` | `v2_walk_utc` | first s4Mage OOB crossing that holds `WALK_DWELL_BARS`. **Everything downstream is read at this bar** |
| `bias` | `v2_bias` / `v2_eff_bias` | `bull` or `bear`; **`bull>bear`** when the walk is on the MFE side and the bias reverses |
| `s15` / `s22` | `v2_s15_state` / `v2_s22_state` | `momo` \| `sideways` \| `curl` \| `none` |
| `act` | `v2_action` | `rev` \| `EXIT` |
| `branch` | `v2_branch` | `momo` (cross on s15/s22) \| `s4` |
| `cross` | `v2_cross_tgt` + `v2_cross_tf` | e.g. `boundary s15`, `Mage s22`, `m s4` |
| `signal` | `v2_sig_utc` | the emitted bar |

- **no `v2-v1` column** — dropped Joe 0731
- when reporting **mismatches**, the walk timestamp is mandatory (Joe 0731)

---

## 13. Line set — Joe 0731, exhv2 builds its own

Four of the five differ from the live `rpl_config` baseline, and s4r differs from s15r/s22r.

| line | exhv2 | live baseline |
|---|---|---|
| `x` s4/s15/s22 | bb **4**\|0.37\|close | bb 5\|0.37\|close |
| `m` s4/s15/s22 | bb 6\|0.45\|close | same |
| `M` s4/s15/s22 | bb 37\|**0.7**\|close | bb 37\|0.83\|close |
| `r` **s4** | kline 7\|**6**\|11\|close | kline 7\|5\|11\|close |
| `r` **s15 / s22** | kline **10\|4**\|11\|close | kline 7\|5\|11\|close |

Nothing in exhv2 reads `R.L0['E']` any more except the timestamp grid.

## 14. Knobs

| knob | value | role |
|---|---|---|
| `MOMO_WINDOW_MIN` | 60 | momentum sample window, minutes |
| `MOMO_STEP_MIN` | 5 | sample spacing → 12 point-samples |
| `MOMO_SLOPE_MIN` | 1.0 | slope floor, r-units per 5-min sample |
| `MOMO_R2_MIN` | 0.50 | straightness floor |
| `CURL_ARC_MIN` | 4.0 | quadratic arc height above which a sideways verdict is a curl |
| `CURL_VTX_LO/HI` | 0.05 / 0.95 | vertex must sit inside the window |
| `WALK_DWELL_BARS` | 48 | 240 s. OOB run must hold CONTIGUOUSLY for the crossing to set the walk |
| `LEVEL_SLACK` | 13.9 | level gate slackens by `LEVEL_SLACK × T`, `T = R² × min(1, \|slope\|/slope_min)` |

`LEVEL_SLACK` was drawn uniform 0-15 on OS entropy at Joe's instruction — *"coin-toss it… your random
choice might uncover other quirks"*. It did: at 13.9 the mechanic **over-fires** momentum on `0520 07:03`
and `0521 02:05`, the first over-fires seen. A tighter value trades those back against the rows it fixes.
