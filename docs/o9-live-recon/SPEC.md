# The mech being handed over

**ONE MECHANISM IS HANDED OVER: the one the MAE cap was applied to.** Joe 0929-late: *"you should be
handing over only the mech that the MAE cap was applied to"*.

Anything measured without the cap is a **different mech**. It is not a baseline, not a target and not
a comparison. If a number in this package is not from the capped mech, it is a mistake — say so.

## The mech, end to end

| stage | what it is |
|---|---|
| signal | `wsf_leash` v7 `wsl_sig_utc`, from the banked `wsf_dtf_v3` knobs — span 10, slope 0.40, fence 25/75, samples 21, tf 1..23, support_min 23 |
| gate | `rule1_gate` config v2 — backward-only `[k-84 bars, k]` = 7 min, a run clamped at the window edge |
| entry | **the sig bar** — the bar the signal names |
| close #1 | an **opposing-dr** `sig_utc`. A same-dr `sig_utc` is INERT |
| close #2 | the **dr-flip backstop**, if no opposing signal came first. It CLOSES and the book goes flat |
| stop | **MAE cap 0.70%** — the trade ends at the first bar its adverse excursion reaches it |
| same-bar, flip vs signal | the **dr-flip** wins |
| same-bar, stop vs opposing signal | the **STOP** wins |
| order type | **market**, both legs |
| score | MAE/MFE as percentages of entry. **NO P&L** — Joe 0917 |

`dr +1 = SHORT, dr -1 = LONG`. Joe 0925: *"+dr = SHORT position, -dr = LONG postition"*.

## The numbers — 90 days of line cache, 2026-06-10 .. 2026-09-08

Produced by `sweep_live_stop.py` at the 0.70 rung, and independently by the canonical
`trade_walk.walk` run over the same pipeline. The two agree exactly.

| | |
|---|---|
| sig bars | 1,863 |
| pass rule#1 | 1,045 |
| **trades** | **894** |
| net > 0 | 479 of 894 = 53.6% |
| stopped at the cap | 381 of 894 = 42.6% |
| MAE sum | 403.022 |
| net sum | +349.638 |
| **net per trade** | **+0.3911** |

| closed by | n | of 894 |
|---|---|---|
| stop | 381 | 42.6% |
| dr-flip | 362 | 40.5% |
| sig_utc | 151 | 16.9% |

Every trade is opened by a `sig_utc`. The dr-flip has never opened one since Joe's 0929-late ruling.

Entry is the bar the signal NAMES. That is the spec and it is what these numbers measure.

**QUALIFIED 1001. The sentence is true on the majority of moments and false on a minority, so it is
qualified rather than struck** — an earlier 1001 edit struck it outright on an overstated figure and
that edit is withdrawn. Measured per branch over the 32 moments on 09-01:

| via | moments | entry at `rev` is causal |
|---|---|---|
| CONFIRMED | 15 | **YES, 15 of 15** |
| FORWARD | 1 | **YES** |
| GAP | 9 | no, 8 of 9 |
| LOOKBACK | 7 | no, 7 of 7 |
| **total** | **32** | **17 causal, 15 not** |

The 15 non-causal entries are on the branches reached only by deciding the moment did NOT confirm —
which needs the breaking row — while their `rev` sits at or before it. `CAUSALITY.md` carries the
full derivation. `OPEN.md:207`'s *"measured at a bar o9-live cannot act on"* is right about those 15
and wrong as a blanket statement.

**Separately**, `report_realtime_replay.py` measures how long after that bar the chain can first
EMIT the timestamp — a median 165 s. Joe 0929 read that and ruled: *"latency is ok for now"*. It is
a **recon** number: it tells the recon job what wall-clock-to-bar gap is normal so a normal gap is
not read as a fault. `RECON.md` carries it.

**CORRECTED 1001 — this used to end "It is not a discount on the figures above." Strike that too.**
It is not a *recon-only* number: the gap is exactly the distance between the bar the figures are
measured at and the first bar o9-live can act on. `OPEN.md`'s emit-bar table prices it at
+0.3911 -> +0.3352 eager / +0.3495 settled, with 1,045 -> 901/900 gated opens.

## The stop races the other exits — it does not replace them

Joe 0929-late, correcting a build that had it wrong: *"research how a stop is applied in trading -
you'll learn that it's both: (at its signal or flip bar) OR (at the stop bar)"*.

An open trade carries **three live exits** and ends at whichever fires first; the rest are cancelled.

| exit | fires when |
|---|---|
| opposing-dr `sig_utc` | an ungated signal arrives whose dr is the opposite of the trade's |
| dr-flip backstop | the dr flips back to the trade's own dr, having left it |
| **the stop** | the adverse excursion reaches **0.70% of entry** |

**No trade re-scores because of the stop.** A stopped trade is −0.70 whether the stop is live or
applied afterwards in scoring. What moves is its **close bar**, and therefore when the book frees up.

| | measured over the 90 days |
|---|---|
| stopped trades, cap in scoring only | 311 of 753 |
| bars the book was held past the stop bar | p25 808, median 1,177, p75 1,589, max 4,421 |
| the same in time | median 98 min, max 6.1 h |
| ungated `sig_utc` bars inside those windows | 216, across 158 of the 311 |
| trades once the stop is live | **753 -> 894** |
| net per trade | **+0.3776 -> +0.3911** |

216 signals give +141 trades, not +216: opening inside a freed window consumes the book again and
suppresses later signals in it, and the new trades have their own stops and their own windows.

**Same-bar ties: the STOP wins.** Joe 0929-late, asked directly: *"use stop"*. Measured over this
window the tie never occurs — **0 stop-and-flip and 0 stop-and-sig_utc collisions across all 381
stops** — so the rule exists for a window that does collide, not for this one.

## The cap is 0.70, re-ruled against the re-walked ladder

Joe specified 0.9 on 0929, was shown the 0.05-step ladder, and ruled 0.70. That ladder scored ONE
fixed trade set of 753 at every rung, because the cap was applied after the walk. With the stop live
**every rung has its own trade population**, so all 80 rungs were re-walked from the tape
(`sweep_live_stop.py`). Joe then re-ruled it: *"retain 0.7% as the stop"*.

| cap % | trades | net > 0 | net > 0 % | stopped | stopped % | MAE sum | net sum | net per trade |
|---|---|---|---|---|---|---|---|---|
| 0.05 | 1027 | 94 | 9.2% | 933 | 90.8% | 48.355 | +105.520 | +0.1027 |
| 0.10 | 1017 | 155 | 15.2% | 862 | 84.8% | 92.471 | +152.639 | +0.1501 |
| 0.15 | 1003 | 206 | 20.5% | 797 | 79.5% | 132.463 | +171.109 | +0.1706 |
| 0.20 | 990 | 249 | 25.2% | 741 | 74.8% | 169.011 | +192.074 | +0.1940 |
| 0.25 | 977 | 287 | 29.4% | 690 | 70.6% | 202.413 | +198.065 | +0.2027 |
| 0.30 | 966 | 329 | 34.1% | 637 | 65.9% | 233.266 | +226.428 | +0.2344 |
| 0.35 | 957 | 356 | 37.2% | 596 | 62.3% | 262.188 | +244.639 | +0.2556 |
| 0.40 | 943 | 386 | 40.9% | 550 | 58.3% | 286.628 | +265.156 | +0.2812 |
| 0.45 | 939 | 409 | 43.6% | 518 | 55.2% | 311.968 | +281.823 | +0.3001 |
| 0.50 | 928 | 433 | 46.7% | 481 | 51.8% | 332.160 | +295.991 | +0.3190 |
| 0.55 | 921 | 450 | 48.9% | 453 | 49.2% | 352.890 | +315.792 | +0.3429 |
| 0.60 | 909 | 455 | 50.1% | 433 | 47.6% | 369.655 | +328.288 | +0.3612 |
| 0.65 | 905 | 466 | 51.5% | 413 | 45.6% | 388.986 | +330.470 | +0.3652 |
| **0.70** | **894** | 479 | 53.6% | 381 | 42.6% | 403.022 | +349.638 | **+0.3911** |
| 0.75 | 887 | 483 | 54.5% | 365 | 41.1% | 418.344 | +343.209 | +0.3869 |
| 0.80 | 883 | 488 | 55.3% | 350 | 39.6% | 433.085 | +343.479 | +0.3890 |
| 0.85 | 876 | 491 | 56.1% | 330 | 37.7% | 446.137 | +341.754 | +0.3901 |
| 0.90 | 872 | 492 | 56.4% | 315 | 36.1% | 460.711 | +332.640 | +0.3815 |
| 0.95 | 866 | 496 | 57.3% | 300 | 34.6% | 474.546 | +331.712 | +0.3830 |
| 1.00 | 860 | 495 | 57.6% | 285 | 33.1% | 485.282 | +327.592 | +0.3809 |
| 1.05 | 856 | 498 | 58.2% | 271 | 31.7% | 496.570 | +328.816 | +0.3841 |
| 1.10 | 850 | 502 | 59.1% | 256 | 30.1% | 506.583 | +332.518 | +0.3912 |
| 1.15 | 847 | 502 | 59.3% | 248 | 29.3% | 517.373 | +326.752 | +0.3858 |
| 1.20 | 844 | 505 | 59.8% | 236 | 28.0% | 527.891 | +330.587 | +0.3917 |
| 1.25 | 843 | 507 | 60.1% | 229 | 27.2% | 538.863 | +331.098 | +0.3928 |
| 1.30 | 842 | 508 | 60.3% | 220 | 26.1% | 549.093 | +326.572 | +0.3879 |
| 1.35 | 838 | 508 | 60.6% | 207 | 24.7% | 556.802 | +322.357 | +0.3847 |
| 1.40 | 831 | 508 | 61.1% | 195 | 23.5% | 558.488 | +320.517 | +0.3857 |
| 1.45 | 829 | 509 | 61.4% | 188 | 22.7% | 566.677 | +316.459 | +0.3817 |
| 1.50 | 826 | 507 | 61.4% | 179 | 21.7% | 573.922 | +309.156 | +0.3743 |
| 1.55 | 824 | 507 | 61.5% | 172 | 20.9% | 580.063 | +304.684 | +0.3698 |
| 1.60 | 823 | 508 | 61.7% | 166 | 20.2% | 586.948 | +302.889 | +0.3680 |
| 1.65 | 819 | 508 | 62.0% | 161 | 19.7% | 590.595 | +300.438 | +0.3668 |
| 1.70 | 817 | 508 | 62.2% | 154 | 18.8% | 596.160 | +299.747 | +0.3669 |
| 1.75 | 814 | 505 | 62.0% | 146 | 17.9% | 602.868 | +293.018 | +0.3600 |
| 1.80 | 809 | 501 | 61.9% | 142 | 17.6% | 607.533 | +278.326 | +0.3440 |
| 1.85 | 808 | 501 | 62.0% | 138 | 17.1% | 612.711 | +274.292 | +0.3395 |
| 1.90 | 806 | 499 | 61.9% | 133 | 16.5% | 618.721 | +267.578 | +0.3320 |
| 1.95 | 805 | 499 | 62.0% | 129 | 16.0% | 625.251 | +262.556 | +0.3262 |
| 2.00 | 805 | 500 | 62.1% | 126 | 15.7% | 631.371 | +263.934 | +0.3279 |
| 2.05 | 801 | 498 | 62.2% | 122 | 15.2% | 633.102 | +259.485 | +0.3240 |
| 2.10 | 798 | 495 | 62.0% | 120 | 15.0% | 637.793 | +247.447 | +0.3101 |
| 2.15 | 796 | 494 | 62.1% | 114 | 14.3% | 641.004 | +247.472 | +0.3109 |
| 2.20 | 794 | 492 | 62.0% | 109 | 13.7% | 645.258 | +244.974 | +0.3085 |
| 2.25 | 793 | 492 | 62.0% | 106 | 13.4% | 649.889 | +242.913 | +0.3063 |
| 2.30 | 791 | 491 | 62.1% | 101 | 12.8% | 652.777 | +241.342 | +0.3051 |
| 2.35 | 791 | 491 | 62.1% | 100 | 12.6% | 657.806 | +237.082 | +0.2997 |
| 2.40 | 791 | 491 | 62.1% | 99 | 12.5% | 662.802 | +233.874 | +0.2957 |
| 2.45 | 791 | 492 | 62.2% | 97 | 12.3% | 665.855 | +233.235 | +0.2949 |
| 2.50 | 790 | 492 | 62.3% | 93 | 11.8% | 667.514 | +233.253 | +0.2953 |
| 2.55 | 788 | 492 | 62.4% | 90 | 11.4% | 670.849 | +232.567 | +0.2951 |
| 2.60 | 787 | 492 | 62.5% | 86 | 10.9% | 674.837 | +231.466 | +0.2941 |
| 2.65 | 785 | 490 | 62.4% | 82 | 10.4% | 677.959 | +223.329 | +0.2845 |
| 2.70 | 783 | 488 | 62.3% | 78 | 10.0% | 681.101 | +219.788 | +0.2807 |
| 2.75 | 782 | 487 | 62.3% | 74 | 9.5% | 684.233 | +219.031 | +0.2801 |
| 2.80 | 780 | 485 | 62.2% | 73 | 9.4% | 686.525 | +210.879 | +0.2704 |
| 2.85 | 779 | 484 | 62.1% | 70 | 9.0% | 689.625 | +206.463 | +0.2650 |
| 2.90 | 776 | 483 | 62.2% | 65 | 8.4% | 690.429 | +206.284 | +0.2658 |
| 2.95 | 775 | 482 | 62.2% | 61 | 7.9% | 693.304 | +203.670 | +0.2628 |
| 3.00 | 774 | 481 | 62.1% | 60 | 7.8% | 696.308 | +199.406 | +0.2576 |
| 3.05 | 774 | 481 | 62.1% | 58 | 7.5% | 699.267 | +196.658 | +0.2541 |
| 3.10 | 773 | 480 | 62.1% | 54 | 7.0% | 700.892 | +194.418 | +0.2515 |
| 3.15 | 772 | 480 | 62.2% | 53 | 6.9% | 703.060 | +189.959 | +0.2461 |
| 3.20 | 770 | 479 | 62.2% | 49 | 6.4% | 701.869 | +189.731 | +0.2464 |
| 3.25 | 769 | 479 | 62.3% | 48 | 6.2% | 701.069 | +190.531 | +0.2478 |
| 3.30 | 769 | 479 | 62.3% | 48 | 6.2% | 703.469 | +188.131 | +0.2446 |
| 3.35 | 769 | 480 | 62.4% | 48 | 6.2% | 703.254 | +187.723 | +0.2441 |
| 3.40 | 767 | 479 | 62.5% | 46 | 6.0% | 703.041 | +187.935 | +0.2450 |
| 3.45 | 767 | 479 | 62.5% | 46 | 6.0% | 705.341 | +185.635 | +0.2420 |
| 3.50 | 765 | 477 | 62.4% | 44 | 5.8% | 706.575 | +179.232 | +0.2343 |
| 3.55 | 764 | 476 | 62.3% | 44 | 5.8% | 707.694 | +176.851 | +0.2315 |
| 3.60 | 763 | 475 | 62.3% | 44 | 5.8% | 709.064 | +173.719 | +0.2277 |
| 3.65 | 763 | 475 | 62.3% | 42 | 5.5% | 711.200 | +172.502 | +0.2261 |
| 3.70 | 763 | 475 | 62.3% | 42 | 5.5% | 713.300 | +170.402 | +0.2233 |
| 3.75 | 763 | 475 | 62.3% | 41 | 5.4% | 715.392 | +169.040 | +0.2215 |
| 3.80 | 761 | 473 | 62.2% | 38 | 5.0% | 716.076 | +163.358 | +0.2147 |
| 3.85 | 761 | 473 | 62.2% | 38 | 5.0% | 717.976 | +161.458 | +0.2122 |
| 3.90 | 761 | 473 | 62.2% | 38 | 5.0% | 719.876 | +159.558 | +0.2097 |
| 3.95 | 761 | 473 | 62.2% | 36 | 4.7% | 721.750 | +157.874 | +0.2075 |
| 4.00 | 761 | 473 | 62.2% | 33 | 4.3% | 723.485 | +156.884 | +0.2062 |
| no stop | 753 | 468 | 62.2% | 0 | 0.0% | 775.197 | +110.223 | +0.1464 |

- **net per trade** peaks at cap **1.25**, +0.3928 on 843 trades. 0.70 sits **0.0017 below it — 0.4%**.
- **net sum** peaks at cap **0.70**, +349.638. It is the best rung on that measure, not merely acceptable.
- the band 0.70 -> 1.30 runs +0.3809 to +0.3928 on net per trade. Spread 0.012. **There is no knee in it.**
- trades fall monotonically, 1,027 at cap 0.05 to 753 with no stop.
- **CORRECTED 1001.** This bullet used to read *"`net > 0 %` rises monotonically 9.2% -> 62.2%, and
  peaks where net per trade is worst. Ranking on win% picks the worst mech here."* Recomputed from
  the 79 cap rows in the table below:

| measurement | value |
|---|---|
| `net > 0 %` monotonic | **no** — 13 decreasing steps of 78 |
| first decrease | cap 1.70 62.2% -> cap 1.75 62.0% |
| `net > 0 %` maximum | **62.5%**, at caps 2.60, 3.40 and 3.45 |
| the no-stop row's `net > 0 %` | 62.2% |
| net per trade at the win% maximum, cap 2.60 | +0.2941 |
| net per trade minimum | +0.1027, at cap 0.05 where win% is 9.2% |
| net per trade with no stop | +0.1464 |

  So ranking on win% picks cap **2.60** at +0.2941 — neither the worst rung nor the no-stop rung.
  It still does not pick 0.70, and it costs 0.097 per trade against it. Whether win% is a ranking
  measure at all is Joe's call; the old bullet's arithmetic was wrong and is not a basis for it.

## The knobs

All in `wsf_trade_config`, **version 3 — 18 rows**. Each row carries Joe's own words.

| version | rows | the mech it describes |
|---|---|---|
| **v3** | **18** | **this mech** — v2's 16 plus `mae_cap` and `stop_same_bar_priority` |
| v2 | 16 | the uncapped mech. Kept as the knob set the 332 historical rows were written under |

| name | value | source |
|---|---|---|
| `leash_instance` | v7 | Joe 0929: *"v7"* |
| `gate` | `rule1_gate.open` — the rule#1 leg OR the scenario leg | Joe 0929: *"using the gate that you validated in our shared sheet, col L"* |
| `same_bar_priority` | dr-flip | Joe 0929: *"same bar priority: dr-flip"* |
| `rule1_back_min` | **7.0 — minutes BACK, 84 bars** | Joe 0929: *"inside of the last {knob:7} minutes"* |
| `rule1_fwd_min` | **0 — causal** | Joe 0929: *"let's drop the forward"* |
| `rule1_run_clamp` | **window — a run stops at the window edge** | Joe 0929 |
| `rule1_fence_lo/hi` | 27.0 / 73.0 | Joe 0923 |
| `oob_lo/hi` | 15.0 / 85.0 | Joe 0913: *"oob is alwasy 15/85"* |
| `latch_tf` | 13 | Joe 0925 |
| `latch_wob` | 8 bars = 40 s | Joe 0926: *"we have to stick on 8"* |
| `mage_fence_lo/hi` | 25.0 / 75.0 | build_wsf_dtf_v3 |
| `div_tf` | 1 — the divergence runs on ws1r | Joe 0924 |
| `scenario_lines` | ws2r, ws3r, gcws30r | Joe 0924 |

**THE CAP IS IN THE TABLE AND IN THE KEY.** Joe 0929-late asked for both — first *"put the cap in
the key"*, then *"move MAE_CAP to the DB"*.

| where | what it is |
|---|---|
| `wsf_trade_config` v3, row `mae_cap` | **0.70** — the only source of the value |
| `trade_config.key(cfg)` | `wtc_v3_v7_rule1_gateopen_mae0.70` — readable without joining |
| `trade_walk.walk(..., mae_cap)` | a **required** argument. No default, no module constant |

**There is no hard-coded cap anywhere in the mech.** `trade_walk.py` is pure — no DB — so it takes
the value rather than owning it, and `build_wsf_trades.py` reads `C['mae_cap']` and passes it. A
caller that forgets the argument gets a `TypeError`, not a silent default.

`stop_same_bar_priority` = `stop` is the second new row — Joe's *"use stop"*, recorded as a knob so
the rule is in the DB with the value it governs.

**The knobs are NOT in `wsf_dtf_v3_config`, deliberately.** Spec §21.6: `leash_bank.knob_string` puts
the v3 config version inside `wsl_knobs`, so a bump would split the next leash write off from the
121-row bank. That consequence is Joe's to sanction and he has not.

## Banking it

**`build_wsf_trades.py` DOES NOT PRODUCE THIS MECH YET, AND IT IS NOT THE ONE THAT MEASURED IT.**
It reads its signal bars FROM the bank - `build_wsf_trades.py:163`:

    SELECT wsl_sig_ms FROM wsf_leash WHERE wsl_knobs=%s AND wsl_sig_ms IS NOT NULL

so it inherits two limits the sweep does not have:

| limit | consequence |
|---|---|
| the 121 banked rows still hold the OLD cross bars | every row that moved is 15 s early |
| the bank covers 2026-09-01..09-06 only | it cannot run the 90-day window at all |

Joe 0929-late ruled the fix: **re-bank the 121 rows in place** - *"rebank in place - the old 121
rows are incorrect"*. Until that is done, `build_wsf_trades.py` is on stale bars.

**The numbers in this file come from `sweep_live_stop.py`**, which recomputes the whole chain in
memory through `coil_exit.resolve` and therefore uses the CORRECTED confirmed bars. The stale bank
is never read by it.

Once the re-bank lands, `build_wsf_trades.py` banks under `wtc_v3_v7_rule1_gateopen_mae0.70`.
`trade_walk.walk` carries the stop, so there is one walk and one shape.

**The 332 rows already in `wsf_trades` are an UNCAPPED mech** — written before the stop and before
the two close rules, under the bare keys. They are history. Do not compare o9-live against them,
and do not quote their numbers.

| key | what it holds |
|---|---|
| `wtc_v3_v7_rule1_gateopen_mae0.70` | **this mech** |
| `wtc_v2_v7_rule1_gateopen` and its two `_entry_emit` variants | uncapped. History |

## What the recon must prove

1. **Selection** — o9-live opens and closes on the same bars this mech does.
2. **Causality** — the verdicts do not change when re-run later over the same bars. A verdict that
   moves is lookahead. Joe 0929: *"it every recon job, review the backtest's last 24 hours and
   re-validate all validated o9-live trades (this re-validation will expose lookahead if there is
   any)"*.
3. **Cache integrity** — Joe 0929 chose the line-cache over a live tape deliberately: *"I'm going to
   say the line-cache because that organically gives us another test-point (ie, is cache and
   real-time kline collection in sync)"*.
4. **The stop** — level, timing, fill and priority. `RECON.md` has the per-trade checks.

**Price is out of scope.** Joe 0929: *"no need to recon price yet, that will be MVP2"*. `MVP2.md`.

## The timestamp gap is the point

Joe 0929: *"this is exactly what we're reconcilling. o9-live has no choice - it must use wall-clock"*.
The backtest is bar-indexed on the 5 s grid; o9-live stamps wall-clock. Mapping one to the other **is**
the test, not a nuisance to be papered over.
