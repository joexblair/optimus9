# mech_line_config — the dynamic line config table

Opened 2026-08-19. Joe: *"earlier on, I suggested a new IC table that would apply configs dynamically
- ie the line configs are defined once, and the code spreads the config across the mech's TFs. this
should be written up somewhere; if its not then build it (SRP) from scratch"*.

It was not written up. One sentence existed anywhere in the repo, `docs/260805_handover.md` line 212:
*"Joe 0805 floated a dynamic IC table instead; the cost was never measured."* Task **#38 Indicator
config spec/readme** has been open since 0707 with nothing behind it.

---

## the two problems this solves

| problem | before |
|---|---|
| the same config written out once per timeframe | `indicator_configs` holds **70 rows** for the ws and gcws families carrying **5 distinct configs**. ws1r through ws22r all say `7\|5\|8\|close` |
| the timeframes domTF needs are not in the table at all | `build_ws_fin.py` hardcodes them: `override(tf * 60, KLine(**B.R_SPEC), 'emerging')` for timeframes 13 to 27 |

Both have the same shape. One row per mechanic, role and timeframe band fixes both.

**Nothing is deleted.** `indicator_configs` and its 70 rows are untouched — Joe 0819 ruled D3 that
way, and `bias_machine`, `bl` and `arm` all read `vw_indicator_configs_live`. This table serves
**wsf and domTF only**, per Joe 0819.

---

## what is built

| | |
|---|---|
| `mech_line_config` | the table. **7 rows** at version 1 |
| `vw_mech_line_config_live` | the live view. Same rule as `vw_indicator_configs_live` |
| `line_config.mech_lines(db, mech, version=None)` | the expansion. One row in, every line out |
| `line_config.from_mech_row(c)` | the row-to-tuple bridge. The only place this table's column order is read |
| `build_mech_line_config.py` | creates the table and the view, seeds version 1 |

`mech_lines` and `from_mech_row` live in `optimus9/compute/line_config.py` because that module's own
docstring says it is *"the ONLY place in the system that knows the DB column order or the positional
tuple layout"*.

---

## the seven rows

| mechanic | role | band | step | line type | config | value mode | fences | offset |
|---|---|---|---|---|---|---|---|---|
| wsf | b | 1-8 min | 60 s | bb | 49\|0.95\|close | emerging | 85/15 | 0 |
| wsf | m | 1-8 min | 60 s | bb | 6\|0.4\|close | emerging | 85/15 | 0 |
| wsf | Mage | 1-8 min | 60 s | bb | 38\|0.93\|close | emerging | 85/15 | 0 |
| wsf | r | 1-8 min | 60 s | k | 7\|5\|8\|close | emerging | 85/15 | 0 |
| wsf | x | 1-8 min | 60 s | bb | 5\|0.35\|close | emerging | 85/15 | 0 |
| domtf | r | 13-27 min | 60 s | k | 7\|5\|8\|close | emerging | 85/15 | 0 |
| domtf | x | 13-27 min | 60 s | bb | 5\|0.35\|close | emerging | 85/15 | 0 |

The five configs are Joe's, given verbatim 0819:

> m: 6|0.4|close
> Mage:38|0.93|close
> x: 5|0.35|close
> b: 49|0.95|close
> r: 7|5|8|close

Every one already matched what `indicator_configs` held on every ws timeframe. **This is a move,
not a change** — verified, 40 existing ws1-ws8 rows compared against the expansion, 0 mismatches.

Expansion counts: wsf gives **40 lines** (5 roles × 8 timeframes), domtf gives **30** (2 × 15).

---

## THE VERSIONING CONSEQUENCE — read this before writing a sweep

Joe 0819: *"we're using versioning in 2 ways: backtesting/sweeping, and live-config. consider both
scenarios, and build whatever is needed to satisfy both"*. Two mechanisms, not one:

| column | serves |
|---|---|
| `mlc_version` | **the sweep.** The config's identity. It is in the unique key, so two versions land alongside each other. A run records the version it used |
| `mlc_live_after_dt` | **the live system.** Which version is in force right now, resolved by the view |

> **A SWEEP MUST PASS A VERSION AND MUST NOT READ THE VIEW.**
>
> `mech_lines(db, mech)` reads the live view. `mech_lines(db, mech, version=N)` reads version N.
>
> If a sweep reads the live view and the live config is changed while the sweep is running, the run
> silently changes underneath it, the results are a mixture of two configs, and **nothing on the
> rows says so**.

`mech_lines` raises rather than falling back when a version does not exist. A typo in a version
number fails loudly instead of quietly returning the live config.

---

## the boundary is an offset, not a pair

Joe 0819, ruling D6: *"boundary changes per mechanic or role can be expressed as a single number in
the mech's config table. eg, if config_boundary = 3, then the boundary is represented as 100 -
{o9_system.lo_boundary} - config_boundary = 82/18"*.

- the fences stay in `optimus9_system`, currently 85 and 15.
- `mlc_boundary_offset` says how far **inside** them a mechanic sits.
- `mech_lines` returns `hi` and `lo` already offset.

| offset | fences |
|---|---|
| 0 | 85 / 15 |
| 3 | 82 / 18 |
| 5 | 80 / 20 |

Joe 0819 on r-weakness pass one: *"in the first pass, use an arbitrary level (eg 80/20)"* — that is
an offset of **5**, so it needs no new knob type.

---

## the band is in seconds

Joe 0819 ruled D2 that way, and it removes a real trap: **the timeframe in a line's name means
different units per family.** `ws1r` is 60 seconds. `gcws15r` is **15 seconds**, not 15 minutes.
Storing the band in seconds means the name's unit never has to be guessed.

`mlc_tf_step` says how far apart the timeframes inside a band are — 60 seconds means every minute.
Low and high alone do not say that, and this was a concretion found during the build rather than
one Joe ruled on.

---

## naming is not done here

The two consumers disagree on what to call the same line:

| consumer | calls ws13's r line |
|---|---|
| the database, `vw_indicator_configs_live` | `ws13r` |
| `build_ws_fin.py` | `r13` |

`mech_lines` returns the **role** and the **timeframe** and lets the caller name it. Putting a name
pattern in the table would force one convention on both, and neither is wrong.

---

## the decisions behind the shape, Joe 0819

| # | decision | ruling |
|---|---|---|
| a | what a config is keyed on | role plus mechanic plus timeframe band |
| b | which mechanics consume it | wsf and domTF only |
| c | the existing hardcodes | move into the new table |
| d | versioned | yes |
| D1 | how a band is expressed | a low and a high column |
| D2 | the band's unit | seconds |
| D3 | the 70 existing rows | untouched |
| D4 | how the code reads it | a function that expands one row into `override()` entries; `LineStore` is not extended |
| D5 | versioning | a version integer **and** a live-after date, both |
| D6 | the boundary | a single offset per row |
| D7 | the emerging/closed setting | carried on the row |

---

## what is NOT in here

- **the ws4-8 and ws1-3 momentum bands** the ws-finisher walk uses. D12 — whether they live in this
  table, in the walk, or hardcoded — has not been ruled on, so they are not seeded.
- the gcws family. It stays on `indicator_configs`; this table covers wsf and domTF.
- any mechanic other than those two.
