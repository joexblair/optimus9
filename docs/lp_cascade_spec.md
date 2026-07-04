# lp-cascade spec — canonical ground (Joe's flow, verbatim intent)

GROUND FACT: **causal/emerging ONLY** — closed values are the o9-live live-trade failure (`project_v2_lookahead`). TV shows closed; a realtime engine only ever has the forming (emerging) value. Never "use closed to match TV".

## Flow (per window)
1. **s5m breaches → ARMED**, ready to take inputs. `es` set, gate(s) latched. (s5m is THE arm; s5r = divergence arm.) Arm persists until the gate resolves — **no fixed deadline** (opposite-side s5m breach cancels; horizon-90min is being removed).
2. **Stale-exit (AB toggle):** if s2r/s3r/s4r are in their lookbacks AND all 3 have progressed to IB when s5m breaches → **exit flow, no trade**.
3. **Gate lifecycle** — test s3r predict while s3m OOB, s4r predict while s4m OOB. Gate opens by ONE of:
   - **(a) all-IB:** s2/s3/s4 all cross OOB→IB → open immediately.
   - **(b) predict-then-reverse-before-breach:** an r predicted but reverses before breaching → open immediately.
   - **(c) ready-to-reverse → s2Mage reverses.** Reached via setup#1 (an r predicted THEN breached) or setup#2 (no predict + s3m/s4m reversed). **s2Mage reverses ANYWHERE on the board — BOUNDARY-AGNOSTIC.** Do NOT add an OOB requirement to s2Mage.
4. **Gate open → FINISHERS.** Lookback **7×30s** bars for s30a + s15a (each honouring its own r-lookback: s30r_lb, s15r_lb). Trade immediately if both signalled in the lookback. Then walk FORWARD with **2×30s tolerance** for a late line.
5. Read bias state. While curating: place the trade WITHOUT the bias check; when the spec locks, consult bias and adhere (block counter-bias).

## Current dial-in (0703, causal)
- **s2Mage = itf 60s, bb 37|0.72|hlcc4, EMERGING.** (60s twitches into OOB earlier than 120s on small moves; both reach OOB on bigger ones.) Boundary-agnostic reversal.
- **s5m len** = under causal re-sweep (the look-ahead-era len=6 armed ~8 min too early; len=8 lands the arm at the setup). m-lines (s2m/s3m/s4m/s5m) len swept 6-11.
- bb m/M spec: m {2,3,4}=10·0.56·close, {5}=6·0.40·ohlc4, {7}=10·0.77·ohlc4, {15,30}=10·0.60·hlc3; Mage {2,3,4}=37·0.72·ohlc4, {5,7,15,30}=37·0.83·ohlc4 (s2Mage src=hlcc4).
- **r-lookbacks:** s30r_lb=19, s15r_lb=29 (split from a single hardcoded rlb=19). r-lines 5|6|6; s15r/s30r src=hl2.
- **s30M-wobslay = dropped** (subsumed by the s30a latch). **gcs5** (5s clone of s15) planned as the fast finisher trigger (gcs5Mage wob1; 5s-native ⇒ inherently causal).

METHOD: hold each find lightly — "what more exposes its nature?" — don't inflate a 1-D result to THE answer (`feedback_expand_dont_grasp`).
