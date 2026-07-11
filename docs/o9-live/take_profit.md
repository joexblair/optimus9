# Take-profit — the arm-delay machine, exit direction

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**, every read via the jig.
> `arm_walk.take_profit_ad` (real) · `arm_walk.take_profit`/`tp_tf` (interim).

The REAL TP: the SAME arm-delay pipeline ([arm_ladder](./arm_ladder.md)) run in the **exit direction**
(`B_tp.es = -es_entry`), **SEEDED on exit-side `s5m` breaches after the entry** — NOT a single walk from the
entry bar.

## Why seeded, not walked-from-entry
A slow reversal (10:22 long: the exit-side `s5m` HI breach is at 13:05) only starts hunting when its `s5m`
breach lands. Walking continuously from the entry stalls the ladder at TF5 for hours (10:22 walk-from-entry
armed 15:43; seeded, it exits 11:12). Each exit-side `s5m` IB→OOB crossing seeds a ladder. The entry's own
`s5m` breach is the seed for a fast mover (the entry replaces it).

## Per hunt
`walk(..., arm_mode='both', latch=True, permission=False, cancel_on='none', allib='off')` →
- **Arm** → `fin_unlatch_6of9(arm, cap, es_tp, q15_tp, q30_tp, N=6)` fires the exit. The 7×30s back-lookback
  ([`fin_box_qualified`](./finisher_6of9.md), gated internally — returns None if unqualified) authorises at the
  **arm bar** (option **a**, Joe's call); the 6of9 lines-OOB confluence triggers. **Symmetric with the entry:**
  `ladder → arm → fin_box_qualified → fin_unlatch_6of9`.
- **Backstop (Joe 0710):** if a base (`s5m` + `s5r`) reverses but never produces `s30a+s15a`, and BOTH `s5m`
  and `s5r` return IB, exit immediately at that IB-return bar — the reversal fizzled; don't hold for the next.

`q15_tp/q30_tp` = the `es_tp`-side finishers (qlo for a long exit / qhi for a short exit; `bd_tp = es_entry`).

## Why the 6of9, not `fin_gate` (s_qualify)
The clean `s_qualify` co-fires are sparse (19:42 long side: 20:20:05, then a 35-min gap to 20:55:40).
`fin_gate` scans forward-only from the arm and lands at 20:55:40 (+0.06%). The 6of9's lines-OOB confluence
tracks the reversal as it develops and fires on the second dip at **20:25:30 (+0.45%)** — Joe's "20:26", 8× the
gain. (`fin_gate` was the first build; that verdict was baked in without measuring. The 6of9 measured better.)

## arm_mode='both' matters for the TP
Fast reversals are single-TF (s6 quiet), so the base TF5 arm is required — see the
[entry/TP asymmetry](./arm_ladder.md#arm_mode--the-entrytp-asymmetry-deliberate).

## Interim TP (`take_profit` / `tp_tf`) — superseded, kept for entry-MAE runs only
At the arm, scan UP the HTF `r` lines until `r` is not OOB; the **TP TF = the highest OOB `r`** (17:40 arm →
TF16, TF19=83.8 stops the scan). Follow `s{TF}m` to the far side; TP on its first OOB reversal there. Worth
+0.821% on the 17:40 trade alone (s7m −0.071% → s16m +0.750%). **Untrustworthy on fast movers** (reads MFE 0.00
because `s5m` already breached the cancel side before the trade opens) — use only for entry-MAE, never
MFE/PnL-sensitive A/Bs.

## Shared-lens caveat (front of mind)
Entry and exit share the ladder/curl/finisher code, so one knob (curl_div, bind_tol, r-lookbacks, wob) moves
BOTH. A knob A/B's book delta = entry-effect + exit-effect summed; split the knob per system if a result looks
confounded.

## Last A/B (24h, stayed cancel)
Interim `sum +2.74% / mean +0.392%` vs 6of9 real `sum +8.01% / mean +1.144%`, zero negatives. 19:42 exits
20:25:30 (+0.45%); 14:01 & 19:17 exit via the **backstop** (box unqualified at the arm) — but 14:01's backstop
holds to 16:45 (MFE 2.93 → net 1.73, 1.2% give-back), a candidate for a tighter anchor.
