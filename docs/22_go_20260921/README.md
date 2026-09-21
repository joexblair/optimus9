# spec_label 22_go_20260921

Banked 2026-09-20.

> **Joe's context, verbatim:** *"I've working on a way to capture more substantial trades, hence the
> Mage oob queries on higher TFs. the wsf_leash report is helping to avoid the pitfalls of early
> exit's during a large leg - this is why the mom_xfer delays are often large"*

## What is here

| file | what it is |
|------|------------|
| `_prelude.py` | the shared load — tape, ws1..ws23 role lines, momo banks, v3 config, dr latch |
| `report_leash_momtf.py` | the `wsf_leash` momTF report. `--write` updates the three columns |
| `leash_momtf_20260921.txt` | its output, 121 rows |
| `report_x_reversal_mage.py` | ws{tf}x reversals firing while ws{tf}Mage is same-side oob |
| `x_reversal_mage_ws12_20260921.txt` | ws12, wob 6, 09-01 → 09-02 |
| `x_reversal_mage_ws8_20260921.txt` | ws8, wob 6, 09-01 → 09-02 |
| `report_divergence_step2.py` | `anchor_floater` at every `wsl_sig_utc`, under the 0921 step 2 |
| `divergence_step2_20260921.txt` | its output, ws3r and ws4r, 32 v7 signals on 09-01 |

## The wsf_leash report

Three columns added to `wsf_leash` on 0920.

| column | what it holds |
|--------|---------------|
| `momtf_dr` | which of ws10, ws11, ws12 are momentum-true at `wsl_sig_utc`, at the row's own dr |
| `momtf_non_dr` | the same three at −`wsl_dr` |
| `mom_xfer` | the first bar after `wsl_sig_utc` where `mom_xfer.count_min` or more of the `momtf_dr` set have left it at the same bar. Walk ends at the dr flip |

Joe's rulings, 0920:

- the momTF set — *"reduce the momTFs to only these 3: 10,11,12"*
- `count_min` — *"2 is arbitrary. the more TFs I see leaving the dr mom, the more comfortable I'll be"*, then *"knob"* → banked as `mom_xfer.count_min` in `wsf_dtf_v3_config` **v8**
- same bar — *"at the same bar. there's strength in numbers"*
- walk end — *"dr flip"*
- the in-place UPDATE — *"the key isn't changing, so break the no-update rule"*

Counts over the 121 banked rows: `momtf_dr` non-empty 105, `momtf_non_dr` non-empty 14,
`mom_xfer` stamped 75, blank 46. `mom_xfer` lags run 0.2 min to 40.5 min.

## The x-reversal with Mage report

Every `ws{tf}x` reversal at `wob` 6 that fires while `ws{tf}Mage` is **same-side oob**, where oob is
**15/85** and same side means a −1 down-turn with the Mage ≥ 85, a +1 up-turn with the Mage ≤ 15.

| line | qualifying reversals | Mage oob stretches |
|------|----------------------|--------------------|
| ws12 | 82 | 26 |
| ws8 | 58 | 19 |

09-01 11:50:05 is in the ws8 list (ws8Mage 90.19) and not in the ws12 list (ws12Mage 75.85). The
two timeframes disagree at that bar on whether the Mage is oob.

## STRIP-MOM-AT-FENCE

Added to `momo_gated.momo_g_why` on 0920, named by Joe: a mode that strips the mom-true tag from a
line that has exited the r-momo-fence on the dr side, read **at the judged bar**, strictly past.
Pass the fence as `(lo, hi)` to switch it on; `None` is off, so every existing caller is untouched.

`walk_mom_models.momentum_true` was refactored onto `momo_g_why` at the same time — it had been a
second copy of the same verdict body, inlined only so it could set `seam_dr` between the fit and the
verdict. `momo_g_why` now takes `seam_dr`. Verified behaviour-preserving: with the mode off, 121
rows × 2 directions × ws2..ws12 reproduced the banked columns with 0 mismatches.

## The divergence step 2, spec 12.1

Joe 0921 replaced step 2 of `jig.anchor_floater`.

| item | value |
|------|-------|
| the line | `ws{tf+1}x` — a ws1r test reads ws2x, a ws4r test reads ws5x |
| the condition | in the dr-OPPOSING oob **15/85** |
| the length | tf × `anchor_floater.dwell_min_per_tf` minutes, contiguous |
| the pivot | that run's **x extreme**, chosen by Joe over the run's first or last bar |

Step 1 is unchanged. Step 3 keeps its 50 filter — that filter is Joe's own 0912 verbatim, *"find
the r extrema that is on the same side as step 1's dr"* — and drops the empty-block **stop**: a
block with no dr-side bar is now skipped and the walk continues.

On ws3r at 09-01 03:40:05 that is the whole difference: block 1 has 0 of 60 bars above 50, so the
old rule ended with no floater and the new one walks on to 88.67 at 03:06:15, d_osc −27.98,
**bearish +1**.

Verdicts over the 32 v7 signals on 09-01:

| line | bearish +1 | bullish −1 | none 0 | no result |
|------|-----------|-----------|--------|-----------|
| ws3r | 3 | 11 | 11 | 7 |
| ws4r | 2 | 10 | 18 | 2 |

`jig.divergence`, the episode-based machine, returned 0 on all 32 for both lines. The two mechs
never share a bar.

## Open items

- **`momo_expiry` is not wired into the momentum mech.** It exists (spec §18, Joe 0914), has three
  banked knobs, and one caller — `handoff_routing.py:118`. It has no unit test. On 09-01 02:40:20 it
  marks ws4, ws5, ws7 and ws11 expired while ws4 and ws7 still carry a mom-true tag.
- **`momo_expiry.expired()` reports a stale `clear_bar`.** `clear` is never reset when a line
  re-arms, so it can name a bar from an earlier cycle. The `expired` boolean is unaffected.
- **The clear condition is being changed.** Joe 0920: *"the ws4r momentum was spent at dr-1,
  therefore the clear must happen at dr+1"*. Under the bare rule that clears ws4r at 02:28:00;
  keeping §18's "past the mid-zone-fence edge" alongside it gives 02:46:20. Joe's read is ~02:50.
  Unresolved.
- **The "first reversal" wob is not computed.** Raising the wob moves a confirmation later; it does
  not filter one in place. Needs a ruling on what "make that reversal the first one" means.
- **The momTF set (10, 11, 12) is not in the config.** It lives in `report_leash_momtf.py`.
- **Two step-2s live in one producer.** `xn`, `dwell_bars` and `oob` default to None on
  `anchor_floater`, so `jig.sideways_reversal`, `jig.causal.anchor_floater` and
  `docs/mage_cascade/stopsweep.py` still run the 50 rule Joe replaced. A gap to close, not a design.
- **The floater walk has no backward horizon.** With the empty-block stop gone it ends only at a
  non-improving block or the tape start, so a floater may sit on the previous day — two do, at
  08-31 23:36:00 and 08-31 23:43:05.
- **`mom_xfer.count_min` never reaches `wsl_knobs`.** `leash_bank.knob_string` filters
  `wdc_section == 'stretchy_leash'`, so a change to the knob overwrites these rows instead of
  landing beside them.
