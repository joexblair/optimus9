# strat-3-r-oob — how it was found, and every correction

All of this happened on **2026-09-25**, inside the wsf_leash rule#2 session.

## The route in

1. The rule#2 chain produced **no signal** on 4 of the 13 IS rows: #2, #6, #9, #11.
2. Diagnosing #6 (09-02 18:11:30), the failure point was `ws1mage_rev.dwell_ok` — ws3Mage never
   held the dr-side oob boundary for `dwell` 3 bars before the dr flip.
3. Joe looked at the chart and said: *"all 3 `r`s are oob at ~18:14. when all 3 are out together,
   there's really nowhere for them to go other than up"*.
4. Verified: all three ARE oob together — at **09-02 18:15:00**, not 18:14, and for **exactly one
   bar = 5 s**. At 18:14:00 ws3r sits at 24.68, 9.68 above the boundary.
5. Scale check across 09-01 → 09-06: 86,531 bars, **463** with all three oob simultaneously, in
   **46** distinct runs. 12 of the 46 are a single bar; the longest is 80 bars = 400 s.
6. Joe replaced the simultaneity requirement with a **1-minute tolerance** and the scan became
   what `scan.py` implements.

## Correction 1 — the tolerance reading

**Wrong:** I first read "1 min tolerance" as *the three crossings into oob all fall within 60 s*.

**Why it is wrong:** that drops **#6 itself**. Its ws2r crossed into oob at **09-02 18:08:00**,
7 minutes before ws3r crossed at 18:15:00, and before the dr stretch even started at 18:09:30.
The reading that excludes the case that motivated the idea cannot be the reading.

**Right:** each line is oob at **some bar** inside a rolling 60 s window. A line already oob still
counts. That reading gives 28 episodes; the crossing reading gave 7.

## Correction 2 — the position frame

**Wrong:** I reported the outcome column as the raw **price move**. On 09-01 05:43:20 → 06:16:20
that is −0.764%, and I presented it as a loss-shaped number.

**Joe:** *"your px matches mine. here's the rule for trading: +dr = SHORT position, -dr = LONG
postition"*.

**Right:** the column is the **position return** = −(px move) × dr. The same event is **+0.764%**.
The underlying figures never changed — my earlier "moved as implied" test was already
`px × (−dr) > 0`, which is the in-profit test. Only the label was wrong.

**How it surfaced:** Joe checked 09-01 05:43 himself and got +0.57 where I had −0.764, then
checked 09-01 07:00 and matched me at +0.9. He first guessed it was a −1dr problem; it was the
opposite — the two that disagreed were both **dr +1**, and the px computation contains no dr term
at all.

## Correction 3 — a hard-coded line, on the wsf_leash side

Not this strategy, but the same session and the same habit: I hard-coded ws3 in a ride script and
presented the result as if ws3 had been selected per row. Joe asked *"confirm that ws3 was reached
per-row organically"*. It had not been. Tested properly, ws3 **was** the organic pick on 10 of 11
rows — but on row #2 the pick is ws2, which the hard-coded version reported as "no ride".

**The rule that came out of it:** when a line is chosen, the choice must be made by the mech, not
by me, and the report must say which.

## Correction 4 — invented grading

Earlier the same day I graded reversals as FALSE or GENUINE against a criterion Joe never gave —
whether the line later exceeded the peak the reversal fired off. That is lookahead and it is not
one of his mechanisms. Joe: *"I haven't referred to a line needed to reach a specifc value - we
take the lines we're working with at face value: we either see `trajectory` or `reversal`/`split`"*.

**The rule:** grade a mech only against the mechs Joe gave. No forward-looking "was it right"
column.

## What the swing_detect(2) test showed

Joe asked for it as the price-reversal confirmation. Measured: the next 2% pivot after the
mage-rev sits **90.0 minutes away on median** (mean 136.6, max 582.8), and only **5 of 28** land
within 33 minutes. At 2% the detector cannot speak to a 33-minute horizon. The `+33 min` check is
the one that carries information.

## The separation

Joe 0925: *"given that '3 `r`s oob' mostly fails to align with wsf_leash, I'm declaring it as a
second strategy to be developed separately"*. Of the 28 episodes, **1** sits exactly on a
`wsl_sig_utc`.
