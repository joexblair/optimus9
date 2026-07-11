# Prediction & curl — the timing primitives

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**, every read via the jig.
> `jig.causal.predict_set` · `jig.causal.curl` · `arm_walk.parse_bands`/`curl_div`.

## Prediction — `jig.causal.predict_set` (never hand-rolled)
`predict_breach` (`breaching_line.py`): anchor `max(m, Mage)` hi-side / `min` lo-side. Fires when the anchor is
OOB and its overshoot exceeds `r`'s undershoot, while `r` sits between the **fence (70/30)** and the **boundary
(85/15)**.
- **`tol` knob** (Joe 0710): value-point allowance, default **0.0 = spec = bit-identical to prior**. Pinned by
  `tests/test_predict_tol.py`. `tol=4` fired 914 phantom `s11` bars over 24h where `tol=0` fired none — the
  00:55 `s11r` "prediction" Joe caught on the chart existed ONLY because of the tolerance. Swept: `tol=4`
  (draft value) is WORSE than 0 on the book; `tol=0` is spec.
- **The Major rarely participates:** `Mage` sits deep IB (24–26) on these sets, so `max()` = the mini and a
  prediction already implies the mini is OOB. The `s{n}m OOB` gate is a **separate CONSUMER read**
  (`mini_oob`), kept apart from `predict_set` (SRP) as `lr_v2.gate_signals` keeps them.
- **Origin (the correction):** a hand-rolled `arm_apex_probe.predict_tol` was the bug. Joe: "expose prediction
  on the jig API. you haven't researched how r prediction works." → one implementation, `tol` a knob, all
  probes point at `jig.causal.predict_set`. Standing rule since: **no hand-roll when designing; data and events
  come only from the jig.**

## Reversal vs curl
The 5s slope-flip (`reversal`, wob=1) fires on the first down-tick and carries no timing over the breach. The
**coarse curl** (`curl` on a `coarse` seam-sampled series) needs three seams to form the triangle and fires one
seam after the turn — it *is* the timing signal, and it costs more on slower TFs (longer seam).

## Curl divisor bands — `arm_walk.parse_bands` / `curl_div`
Coarse-curl seam = `TF·60 // div`, `div` from the first band whose ceiling ≥ TF. Default
`DEFAULT_BANDS = '7:2,14:4,999:6'`: `TF≤7 → TF/2` · `8..14 → TF/4` · `>14 → TF/6`. Measured seams: `s5r`=150s,
s6=180, s7=210, s8=120, s9=135, s10=150, s11=165, s12=180, s14=210, s16=160, s19=190, s22=220.

Why banded (Joe): the TF/4 = 75s seam armed `s5r` on a 2.4-point wobble at 05:11:15; the TF/2 = 150s seam
fired at 05:15:00 where `s7r` breached 5s later and the ladder climbed as narrated. LTF wants a coarser (TF/2)
seam to ignore twitch; HTF a finer one. **Sweepable once the logic is clean** — the optimal mid-band (8–14)
divisor is an open sweep (task #6, the 150s-vs-5min granularity that drives the TP give-back; see
[take_profit](./take_profit.md)).
