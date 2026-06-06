# BL dialable settings — cheat sheet

Reference for the Breaching Lines tuning surface. (Conventions live in
`quirks_to_remember.md`; this is the per-setting reference.)

## `bl_config` — machine tuning
One active row (`blc_is_active`); manage with `run.py bl_config --list / --activate PK
/ --new <overrides>`. Columns are `blc_`-prefixed; CLI args are not (`--curl_floor` →
`blc_curl_floor`).

| setting | default | what it does |
|---|---|---|
| `blc_curl_floor` | 1.0 | min slope for K to count as *curling* (reversing). Higher = needs a sharper turn; lower = twitchier. |
| `blc_curl_lookback` | 7 | bars back the curl slope is measured: `k[i] − k[i−N]`. ~avg bars before K reverses. Short = local turns; long = HTF-scale only. |
| `blc_grace` | 2 | if **exit3** (a cross) fires *before* a curl, wait this many bars for the curl; if it lands, complete. Bridges cross→curl when the cross leads. |
| `blc_pseudo_cross` | 15 | exit3's near-cross tolerance: BB & K count as crossing-toward-IB when within this distance and converging (not just a hard cross). |
| `blc_fence_pad` | 5 | widens the no-prediction fence symmetrically: `hi = 70+pad`, `lo = 30−pad` (5 → 25:75). Bigger = fewer predictions (K must be more extreme to engage). |
| `blc_bb_pad` | 0 | pads **BB OOB detection toward IB for exit1** (same idea as `fence_pad`): a BB that only reaches `hi−pad` still counts as OOB, so exit1's "BB was OB" step arms on a near-miss (max 83.1 vs boundary 85 → OOB at pad≥2). Bigger = exit1 arms more readily. |
| `blc_exit2_ref` | now | **which TF9 seam's pre-`bl_line` references exit2** (the "line clearly reversed" completion). exit2 fires when the bl_line reverses back past that reference. `now` = the seam just before the extreme (tight → can trip on a micro-dip); `prior` = one seam further back (needs a *deeper* reversal); `avg` = mean of the two (derived, not seam-based → no ref bar/dt). On a fresh breach the ref is bounded to the breach-edge (no pre-breach reach). **Further-back = stricter.** |

## Running it against the DB configs
```bash
# detect: walk N hours of 5s bars through the active bl_config + bl_lines → bl_states (+ Pine)
python3 run.py bl_detect --lookback_hours 48          # default 12; --pine bl_hb9_states.pine

# config: list / activate / clone-with-overrides (versioned — never edits the active row)
python3 run.py bl_config                               # list all rows (* = active)
python3 run.py bl_config --activate 2                  # make row 2 the live config
python3 run.py bl_config --new --label "bb_pad 3" --bb_pad 3   # clone active + override → new active
#   knobs: --curl_floor --curl_lookback --grace --pseudo_cross --fence_pad --bb_pad --exit2_ref

# review: materialise bl_review (state-change/exit rows + 11-bar run-up + gate-open stop/profit)
python3 run.py bl_review
```
Edits go through `bl_config --new` (a new `blc_is_active` row, history kept), then
`bl_detect` re-reads the active row. Lines/roles live in `bl_lines`; pools in `pk_pools`.

## `pk_pools` — PK machine pools (exit4)
Per-series, versioned by `pkp_live_after_date`; `pkp_`-prefixed.
`pkp_pool_c`/`pkp_pool_w` (close/wide lookback bars) · `pkp_pool_range` (window
width) · `pkp_slope_floor` (noise threshold) · `pkp_multiplier` (TF scale) ·
`pkp_weight_close`/`pkp_weight_wide` (vote weights). **hb9 = 5 / 22 / 4 / 13 / 1,
votes 5,2.**

## `bl_lines` — per line
`bl_`-prefixed. `bl_role` (breach / support) · `bl_exit_mask` — enabled-exits bitmask
(**exit1=1, exit2=2, exit3=4, exit4=8**; e.g. 7 = exits 1+2+3) · `bl_pk_ic_pk` — the
PK line for exit4 (swappable). Raw exit conditions are still recorded in `bl_states`
for eyeballing; the mask only gates which *complete* the journey.
