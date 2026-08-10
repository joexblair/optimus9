Read. Live state verified against the DB.

**Where the tables actually stand right now**

| table | contents | rows |
|---|---|---|
| `s46_window` | `sw_src` = `item13 A f7 x3` — variant A's exits, NOT Joe's item-15 baseline | 36 |
| | window 07-27 02:13:50 → 07-29 22:00:10, `sw_ret` sum **+11.567** (= A, matches handover) | |
| `s46_event` | 3 configs banked: `CUR f3 x6`, `CUR f7 x3`, `A f7 x3` | 4 kinds each |

- `s46_event` per-config event counts:

| cfg | fence | xwob | momo_act | momo_exit | opp_curl | s6x_cross |
|---|---|---|---|---|---|---|
| CUR | 3 | 6 | 27 | 25 | 3 | 36 |
| CUR | 7 | 3 | 27 | 25 | 3 | 36 |
| A | 7 | 3 | 27 | **27** | 3 | 36 |

- A latches `momo_exit` on all 27 armed trades vs CUR's 25 — the `7|5|12` oob duty reaches the 22/78 fence on 2 trades CUR never releases.
- `momo_act` 27 of 36 is identical across all three — arming is bit-identical by construction, only the release differs.

**The task on the table (handover §5): filter or flip the bad trades**

- signature to catch: **MFE ≈ 0 with a large MAE** — the trade never went favourable at any point.

| # | entry | dr | MAE | MFE | ret |
|---|---|---|---|---|---|
| 11 | 07-27 13:32:30 | −1 | 1.234 | **0.000** | −1.234 |
| 30 | 07-29 09:40:20 | +1 | 1.801 | **0.017** | −1.543 |
| 19 | 07-28 07:47:20 | −1 | 1.977 | **0.076** | −1.615 |
| 21 | 07-28 11:03:25 | −1 | — | — | +1.887 (Joe: "should have been filtered or flipped") |

- MFE/MAE are **outcome** variables — a filter built on them is lookahead. Whatever filters n=11/19/30 has to be readable at the entry bar.
- one candidate entry-side defect is already named: the **s4Mage pinhole** on n=30 — s4Mage touched 85.17 for ONE 5 s bar. Existing gates (`sr_ib_bars` 475 = 39.6 min, `sr_s1hold` 109 = 9.1 min) measure the run-up, not the breach; they move the one-bar share only 22.0% → 24.1%.
- `S4HOLD_MIN` (`s46_momo.py`, default **0 = OFF**) is the built lever for it, but turning it on delays entry into the stretch, contradicting item 11's "no waiting, no confirmation". **Your call, not made.**

**Caveats standing**

- 36 trades over 3 days (07-27 → 07-29) is the entire evidence base. Tape runs to 07-31; `kline_collection` is live past that.
- fence 7 was picked as best-of-49 on those same 36 rows — that is selection.
- `sr_dwell_bars` / `sr_m4_min` / `sr_m4_max` in `s46_run` are lookahead; only `sr_ib_bars` is causal.

**Summary**

The handover matches the database exactly: item 13 is built, causal and swept, variant A's exits are what `s46_window` is showing right now, and three configs sit banked in `s46_event` with arming identical across all of them so only the release rule varies. The open task is the entry side, not the exit side — three of the 36 trades never went a tick favourable, and the one entry defect diagnosed so far (the one-bar s4Mage pinhole on n=30) is unfiltered by both existing gates because they measure how long price took to get there rather than how convincingly it broke through. The lever for it exists and is switched off, and switching it on trades against item 11's no-confirmation rule, which is a value decision I'm not making for you.

**PnL impact**

TL;DR: unknown until a causal entry filter is specified — the three worst trades are −4.39 combined, ~18% of the +24.62 gross, so a clean filter is worth roughly +0.12/trade if it costs no winners.

Removing n=11, n=19 and n=30 lifts the CUR window from +0.5740 to ~+0.697/trade net, but that is a fit to three known losers on 36 rows and carries no OOS weight. The real size depends entirely on how many winners the same filter kills — the s4Mage pinhole test would touch ~24% of qualifying entries, so it is not a surgical cut. Nothing here holds unless it survives the 07-30 → 07-31 tape that is already collected and unscored.

Which do you want first — extend the window to 07-31 so the filter has more than 36 rows to argue with, or specify the entry filter now and measure it on the 36?
