# Redundant websocket (N-socket collector) — spec (Joe 0708)

**Goal.** Reduce tick loss + client-side arrival stalls by ingesting the Bybit public-trade stream over **≥2 independent
websocket connections** and taking the union. Attacks the *client/connection* half of the desync (per-socket stalls,
reconnect gaps, dropped frames) — complementary to the SG box (network floor) and the finalization-read (timing race).
See [[project_o9live_desync_fix]], [[receipt_lag_spec]].

## The elegant core: aggregation is already free
`TickCollector._on_message` writes `INSERT IGNORE INTO ticks … (tk_tp_pk, tk_trade_id, …)`. The PK is
`(tk_tp_pk, tk_trade_id)`. **Two sockets delivering the same trade → the second INSERT is a no-op collision.** The union
and dedup are the *existing primary-key behaviour* — there is NO merge/aggregation code to write. A trade dropped on
socket A but delivered on socket B simply lands via B. Row count is unchanged; only completeness improves.

## Design (SRP-clean)
- **`BybitWebSocketClient` = one connection.** Today `_WS_URL` is hardcoded. **Parameterize it** (`__init__(url=...)`).
  Its job (connect / subscribe / heartbeat / auto-reconnect) is unchanged.
- **`TickCollector` = orchestrate many.** `run()` spawns **one daemon thread per endpoint**, each running its own
  `BybitWebSocketClient(url).stream(topic, cb)` (`.stream()` blocks on its own asyncio loop, so one thread each).
  Endpoint list comes from **config, not hardcoded** (default: primary + mirror; `n≥1`, so a 1-socket config == today).
- **Per-thread DB connection (load-bearing).** MySQL connections aren't thread-safe — the existing backfill thread already
  opens its own. So `_on_message` must stop using `self._db`: refactor to **`_on_message(db, tp_pk, msg)`** and inject each
  thread's own connection. The write path stays a single shared method (all sockets funnel through it) — only the
  connection is owned per-thread. This is the SRP split: *write-path* (stateless re connection) vs *connection ownership*
  (per socket). Do NOT fork `_on_message` per socket.
- **Prune once.** `_prune` is hourly; N threads would race the DELETE. Designate the **primary thread as the sole pruner**
  (pass a `prune=True` flag to one thread), or lift prune to its own timer. Don't let every socket prune.

## Endpoint diversity is the actual redundancy lever
- Two sockets to the **same URL** only cover per-socket stalls + reconnect gaps.
- Two sockets to **different hosts** — `stream.bybit.com` + `stream.bytick.com` (Bybit's mirror domain, identical data) —
  ride **different DNS / edge / network paths**, so their stalls are **decorrelated**. That's what makes the union recover
  real losses rather than duplicating one connection's fate.
- On the **SG box** both sockets sit near Bybit, so this buys *connection resilience + client-tail*, not network floor
  (SG already owns the floor). The three levers stay orthogonal.

## Compose with the receipt-lag instrumentation (the payoff — zero extra measurement code)
Once `tk_received_ms` exists ([[receipt_lag_spec]]), change the write from `INSERT IGNORE` to:
```
INSERT INTO ticks (…, tk_received_ms) VALUES (…)
ON DUPLICATE KEY UPDATE tk_received_ms = LEAST(tk_received_ms, VALUES(tk_received_ms))
```
Now `tk_received_ms` automatically holds the **earliest arrival across all sockets** (the raced time). The *same*
`receipt_lag_report`, run before vs after enabling the 2nd socket, **measures exactly how much the race recovered** — no
bespoke A/B harness. That before/after delta is the go/no-go evidence.

## Decision gate — do NOT ship the 2nd socket blind
Sequence, so the add is data-backed not hopeful:
1. Instrument (1 socket) → read the `receipt_lag` tail shape.
2. **Fat, variable tail** (client stalls) → the 2nd socket races them out → ship it, confirm via the before/after delta.
3. **Tight distribution** → the 2nd socket buys only drop/reconnect *redundancy* — still worth it for robustness, but it
   won't move the desync, and we say so rather than claiming a win we didn't measure.

## Cost
- 2× WS connections + heartbeats + threads — trivial CPU/RAM.
- 2× ingest attempts, but dedup collapses them to the same rows — the duplicate INSERT is a cheap PK-collision no-op.
- Negligible; the constraint is *whether it helps*, answered by the receipt-lag delta above.
