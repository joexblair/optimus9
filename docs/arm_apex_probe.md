# ARM DELAY SPEC 0709 — first trace (Joe's 07-08 06:01 / TF19 example)

Tool: `arm_apex_probe.py` (read-only). Builds `s{tf}{r,m,Mage}` for `tf ∈ [5,7,9…45,50]` as in-memory
`line_overrides` (emerging/causal), walks the tape per bar, logs `HUNT · PRED · BREACH · CLIMB · CURL · ARM ·
BACK · CANCEL`. Both curl lenses traced: `--curl mage` (spec) and `--curl r` (Joe 0710).

Spec lines used: `s{tf}r = 5|5|6|close` · `s{tf}m = 7|0.5|ohlc4` · `s{tf}Mage = 37|0.7|ohlc4`, all `emerging`.
Prediction = `predict_breach` with a `tol` value-point allowance on the anchor's overshoot (`tol=4.0`).
Coarse-curl seam = TF/4. Prediction seam = TF/3. Seam grid anchored to UTC midnight.

## The 07-08 05:40 hunt (es = +1, hunting a short)

`[measured]` real tape, `filler_invisible=True`, all bars real-tick (06:01:05→06:01:15 vol 115k/205k/180k).

| time | fact |
|---|---|
| 05:40:00 | `s5m` breaches hi → hunt starts |
| 05:42:00 | `s19r` predicted (`tol=0` and `tol=4` identical) — 19-min bar open |
| 05:52:30 | `s19Mage` coarse-curls (24.7→24.5, a plateau dip, still climbing overall) |
| 05:55:00 | `s17r` breaches → ladder finally climbs 5→7→9→11→13→15→17→**19** |
| 05:57:15 | `s21r` predicted → apex climbs off 19 |
| 06:00:00 | apex runs 21→23→…→39 on already-breached slow r's |
| **06:01:00** | **`s19r` crosses 85** — exactly a TF19 bar open |
| **06:01:15** | **price top, close 0.15077** (15 s later) |
| 06:02:00 | `s19Mage` peaks (28.4) |
| 06:06:45 | `s19Mage` coarse-curl confirms — 5 m 30 s past the top, price −0.68% |
| 06:20:00 | opposite `s5m` breach → cancel. **No arm on TF19.** |

Literal-spec arms: `--curl mage` → 06:36:45 TF7 · `--curl r` → 05:24:00 TF11. Neither is the turn.

## Gaps the trace exposed

1. **Hunt re-latch.** `in_hunt_mode` is written as a *state* (`s5m is breached`), so it re-fires at every 300 s
   seam. Works if it latches on the OOB **crossing** and holds until arm or cancel.
2. **Ladder contiguity lags the apex.** The climb only advances one TF at a time, so TF19 — predicted at
   **05:42:00** — is not reachable until **05:55:00**, when TF17 finally breaches. 13 minutes of lag on a
   19-minute apex. Works if the apex is the **highest predicted TF** by scan, not by contiguous walk.
3. **`predicted OR breached` never goes quiet.** TF23–39 sat at r = 86…98 through the whole hunt, so the
   "HTF has nothing to contribute" test can never pass. Works if the HTF test is *predicted, or breached and
   still advancing toward the boundary since the apex was set*.
4. **Curl is an edge; `r is IB` is a state.** Both must hold on the same bar and almost never do. Works if the
   curl **latches** and the arm fires on the first bar the apex `r` returns IB.
5. **Curl fires on a plateau.** `_curl_detect` uses `<=` / `>=`, so a flat seam counts as a turn. `[measured]`
   24 h at the TF/4 seam grid: `r` repeats the previous seam value **17–27%** of the time; `Mage` **~0%**.
   That is what produced the false 05:52:30 curl. Works if the curl on `r` requires strict `<` / `>`.
6. **Tolerance is not load-bearing here.** `[measured]` 24 h, `tol 0 → 4` adds ~9% more predicted bars
   (TF19: 3338 → 3636); TF45 unchanged. On the 05:40 hunt, TF19's first prediction is 05:42:00 either way.

## r-line character (both lenses)

`[measured]` 24 h. `r` does not move on **~50%** of consecutive 5 s bars (`Mage` ~20%). During the 05:42–06:01
TF19 bar `s19r` was frozen at **76.9 for the full 19 minutes** (developing stoch saturated above its closed
window) and stepped to 92.9 only at the bar open. Conditional flatness while OOB is 42–62% vs 43–56% IB —
so the freeze is an episode of the trend leg, not a rule of the line.

Curl counts are comparable at the TF/4 seam (TF19, 24 h: `r` 151, `Mage` 131) — the lens choice is not
settled by frequency. Re-run the A/B after gaps 1–4 are closed.

## Open question for the spec

Joe's "06:01, TF19" coincides with a TF19 **bar open** on the midnight grid. Is the intended arm signal
`s19r` completing its predicted breach (the step at the bar open, 15 s before the top), or `s19Mage` rolling
over (5 m 30 s after it)? The two are 6 minutes and 0.68% apart.
