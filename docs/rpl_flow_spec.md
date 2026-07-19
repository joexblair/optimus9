# rpl flow — spec

*Causal/emerging only. A **walk** = one flip cycle, labelled `DD_NN`. Storage: `docs/rpl_event_store_spec.md`.
Research impl: `rpl_flow.py` (pre-confirm) + `rpl_s8cycle.py` (post-confirm climb).*

## Cycle (per walk)
1. **Flip** (`bias_trend_flip`) fires → post-flip transitional state.
2. **s1/s2 direction confirm** — s1r AND s2r `predict_breach` the same side = flip direction within
   `s1s2_confirm_tol_ms` (240s). Opposed side → close the flip trade. Walk **terminates** at the confirm.
3. Confirmed → **s8 cycle**: the r-pred baton passes s1/s2 → **s3** and climbs.

## s8 cycle (LTF ladder s3→s8)
- **Baton** starts at s3. Rungs breach on the **confirmed bias side** (bull → HI).
- **Marker cadence** = s2x×s2m cross while s2m is OOB **on the bias side** (m2>HI for bull). The climb
  advances only on marker ticks.
- **Breach** = r{rung} reaches the bias boundary. On breach the baton advances one rung per marker.
- **x-cross-pred** (exhaustion trigger) fires when: **x{rung} crosses r{rung} before r is 25% into its
  breaching bar, OR r never breaches** (the ¼-bar clause — both halves, not just no-breach).

## Two governing rules (0719)
- **HTF handoff:** when the s8 cycle completes (baton breaches s8), **scan the HTFs (TF9–45) for
  qualifying r-pred events and set current_tf to the highest one.** The baton jumps there — it does NOT
  crawl 9→45 one marker at a time (the s2 cadence dries up above the fast thrust).
- **Higher-TF r-pred overrides lower-TF x-cross-pred:** an x-cross-pred at rung n is suppressed if ANY
  TF>n is printing a qualifying r-pred. *Why:* a fast LTF x-cross (e.g. s5 @ 01:01) is a reaction to a
  finer line that a coarser view (s10r) smooths out; the coarser r-pred is the truer read, so it wins.

## Termination → flip
- Exhaustion = an x-cross-pred at current_tf that is **not overridden** by any higher-TF r-pred.
- On exhaustion → **delegate** `max(2, current_tf − delegate_offset)` (floor=2), x-cross-r wob cross on
  the flip side → `bias_trend_flip`. The flip is the opposite of the confirmed bias.

## Knobs (all DB-sourced, `rpl_config` baseline)
boundary 85/15 · fence 65/35 · anti 50 · vmin 8 · carry 120000 · s2_tf 120 · delegate_offset 5 ·
wob_n 9 · div_net_min 3 · s1s2_confirm_tol_ms 240000. s30 = downstream finisher (parked). PARKED:
min-OOB-dwell filter on the x-cross-pred backstop.
