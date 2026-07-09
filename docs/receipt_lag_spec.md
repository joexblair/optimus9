# Tick receipt-lag instrumentation — spec (Joe 0708)

**Why.** The o9-live⇄backtest desync is late ticks landing after the loop's read-grace, mutating the std-sensitive BB
(see `project_o9live_desync_fix`). Two open questions this measurement answers:
1. **Is the lateness ours (client-side) or the exchange's (dispatch)?** → decides whether a 2nd websocket actually helps
   the desync (it races out *client* stalls; it can't beat the exchange's dispatch clock).
2. **How long must we wait for a bar to be complete?** → tunes the real fix (read the finalized bar, not a fixed grace),
   and validates the 2000ms interim.

The `ticks` table only stores `tk_timestamp` (exchange trade time) — never the local **receipt** time. Add it.

## The change (2 lines + 1 column)
- **Schema:** `ALTER TABLE ticks ADD COLUMN tk_received_ms BIGINT NULL;`
- **`optimus9/data/tick_collector.py` → `_on_message` (line ~89):** capture `recv = int(time.time()*1000)` as the FIRST
  statement (before any work), and add `tk_received_ms` to the INSERT column list + `recv` to each row's values.
  - Backfill path (`_backfill_recent`, REST) writes `tk_received_ms = NULL` — REST fills aren't the live path, exclude
    them from the analysis (`WHERE tk_received_ms IS NOT NULL`).
  - No buffering change; still one INSERT per message. Negligible cost.

## Derived metrics (analysis-side, no more code)
For each live tick:
- **`receipt_lag = tk_received_ms − tk_timestamp`** — total exchange→receipt lag (network + exchange dispatch + our processing).
- **`arrival_vs_seam = tk_received_ms − ceil(tk_timestamp/5000)*5000`** — how late, relative to the bar's CLOSE, the tick
  was *received*. This is the number that governs the grace/finalization wait.

## What answers Joe's question
- **Grace/finalization timing (actionable):** the distribution of `arrival_vs_seam` for a bar's ticks. `p99`/`max` = how
  long to wait to be "complete." Cross-tab by bar **volume** — confirms the desync scales with vol and gives the wait per
  vol bucket. If p99 ≤ ~1s on most bars but the high-vol tail runs to 2s+, that's the residual the 2000ms grace still misses.
- **Client vs exchange (the 2nd-WS decision):** the **shape** of `receipt_lag`.
  - **Tight distribution / stable floor** → network+dispatch dominated → a 2nd WS reduces the *tail* but not the *floor*;
    limited desync help (still worth it for stability/redundancy).
  - **Low floor + fat, variable tail** (occasional 100ms→2s spikes) → **client-side stalls** → a 2nd WS **races them out**
    (first-of-two-arrivals) → real desync help. This is the signature that justifies the second socket for the desync,
    not just for robustness.
  - Caveat: `receipt_lag` can't *perfectly* split network from exchange from client — but the variance/tail vs floor split
    is the honest proxy, and it's decisive enough to make the call. A true split needs the 2nd WS itself (compare arrival
    times) — which is exactly the thing we'd only build once this says it's worth it.

## Sequence
1. Ship the 2-line change + column (touches the live collector → Joe's go to deploy).
2. Let it run ~a few hours (needs high-vol bars in the sample — the tail is what matters).
3. Analyse `arrival_vs_seam` (grace tuning) + `receipt_lag` shape (client-vs-exchange) → data-backed 2nd-WS decision +
   the finalization-read wait value. See [[project_o9live_desync_fix]].
