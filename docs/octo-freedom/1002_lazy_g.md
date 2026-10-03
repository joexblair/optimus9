# 1002 — lazy-g, Joe's read off the first live `octo-sig` bar

Joe's words, verbatim, on the bar that opened the first live trade:

> *"btw, that setup is exactly lazy-g. at the bar, the Mage goes from a low board position at
> g15Mage, to a higher board position in the HTF Mages, and along the way the `r` swaps its
> positioning with the Mage. you can see this in ws4Mage vs ws4r: Mage has shifted from under r at
> g15, and over r at ws4"*

**This is a measurement, not a hypothesis** — Joe read it off the board. Nothing here is mine.

## THE BAR IT WAS READ FROM

| | |
|---|---|
| trade | `o9_ledger.led_id` 1, the first `octo-sig` row ever written |
| side / qty | **Buy** = LONG, so **dr = −1** | 66,000 |
| entry | 0.17581696, FARTCOINUSDT |
| opened | **2026-10-02 01:45:10 UTC** |
| 0.70% stop | 0.17458624, distance 0.00123072 — client-side, no resting order at the exchange |
| o9-live enabled | ~3 min before the open, per Joe |

## THE STRUCTURE, AS I READ HIS WORDS

Two things happen together, ascending the timeframe ladder at ONE bar:

| | what moves |
|---|---|
| 1 | the **Mage's board position rises** — low at the fast end, higher in the HTF Mages |
| 2 | the **Mage/r ORDERING SWAPS** along the way — Mage UNDER r at the fast end, Mage OVER r at ws4 |

So the mech's signature is a **sign change in `Mage − r` as the timeframe increases**, read across
the ladder at a single bar — not across time at a single timeframe.

## WHAT WOULD TURN IT INTO A MECH

The measurement is `sign(Mage − r)` per timeframe at the bar, ascending the ladder, which exposes
the **crossover timeframe** — the TF where the ordering flips.

**TWO THINGS ONLY JOE CAN SETTLE, and they change what gets built:**

| # | the question |
|---|---|
| 1 | ~~**which line is `g15Mage`?**~~ **ANSWERED 1003 by Joe's own next instruction** — *"the next job requires Mage and r from gcws15 and gcws5 built into the line cache. 15sec and 5sec"*. So `g15Mage` is **`gcws15Mage`, itf 15 SECONDS**, which is registered in `vw_indicator_configs_live` with `bb_len` 38 / `bb_mult` 0.93 / src close / emerging — the wsf Mage role's spec exactly. My inference from the ladder's direction was right, and it is now his word, not my inference. ORIGINAL NOTE: It does not resolve in either registry. `g` prefixes are `gca`, `gcb`, `gcs`, `gcws`; there is no `g15`. The candidates named `15` are `s15M` at itf **15 s**, and `ws15Mage` / `hs15m` at itf **900 s = 15 min**. His ladder runs fast -> slow with ws4 (240 s) ABOVE it, which points at the 15-SECOND line — but that is my inference from direction, not his word, so it is his to confirm |
| 2 | is the **crossover TIMEFRAME** load-bearing, or only the PRESENCE of a flip anywhere in the ladder? A flip between g15 and ws4 is a different mech from a flip anywhere in ws1..ws23 |

## THE SPEC QUESTION THIS BAR RAISES, AND IT IS NEW

Joe's earlier ruling put lazy-g on the signals the ARM does not catch: *"the not-armed/open rows will
be carried by the lazy-g mech"*, and *"lazy-g sits BESIDE rule#1, not behind it"*.

**But this bar ARMED.** It is an `octo-sig`, and `octo-sig` requires a live arm — `leash_walk.py:134-136`
returns False whenever the arm is not live. So:

- if this setup is "exactly lazy-g", then **lazy-g and octo-freedom OVERLAP on at least this bar**, rather than lazy-g only filling the gaps.
- that changes lazy-g's job description. Either it is a second opener that can agree with the arm, or it is a DESCRIPTION of what the armed setup looks like and the non-armed rows share it.
- **UNMEASURED:** whether the Mage/r ladder swap is present at the 9 validated 09-01 `WALK FIRES FROM` bars, at the 14 other run-first bars, and at the 4 non-armed signals Joe assigned to lazy-g (05:01:30, 07:27:15, 12:41:45, 17:27:50). That single measurement would say whether the swap SELECTS or merely ACCOMPANIES.

That is the first thing to run when lazy-g dev starts, and it needs answer 1 above before it can run.

## WHY THE LIVE BAR CANNOT BE MEASURED FROM THE DB AS IT STANDS

| | |
|---|---|
| `o9_state_log_line` | 3,800,076 rows of per-bar line values — but of the **`s` family** (`s30r`, `s30M`, `s30m`), not the `ws`/`gcws` family octo-freedom reads |
| the backtest tape | ends 2026-09-30; this bar is 10-02, outside it |

So the live bar's Mage/r ladder has to be rebuilt from `kline_collection`, or the producer has to log
the ladder it already computes. **The second is nearly free** — the producer holds every `ws{tf}Mage`
and `ws{tf}r` at the decision bar under shape B, and writing them to `o9_state_log_line` would make
every future lazy-g read measurable instead of visual.
