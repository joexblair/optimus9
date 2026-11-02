# HIS 1101 DIVERGENCE EXAMPLES | LIN2_DIV_ON 0 | LIN2_DIV_PM_FLOOR 0.0 (PM disabled)
# the verdict is +1 bearish / -1 bullish; the target side is +1 high / -1 low
# his table: a rev-trade when verdict == target side

| his example | the bar | target side | the verdict | its name | the raw state | the anchor bar | the floater bar | his floater | rev-trade? |
|---|---|---|---|---|---|---|---|---|---|
| bullish 2324, floater 2312 | 2026-09-03 23:24:00 | low | None | none | -2 | 23:24:00 | 23:12:55 | 23:12:00 | no |
|  | 2026-09-03 23:24:00 | high | None | none | 2 | 23:24:00 | 23:02:20 | 23:12:00 | no |
| bullish 0437, floater 0418 | 2026-09-03 04:37:00 | low | -1 | -1 bullish | -1 | 04:37:00 | 04:17:50 | 04:18:00 | YES |
|  | 2026-09-03 04:37:00 | high | None | none | 2 | 04:37:00 | 04:28:10 | 04:18:00 | no |
| the 0437 cadence bar itself | 2026-09-03 04:37:55 | low | -1 | -1 bullish | -1 | 04:37:55 | 04:17:50 | 04:18:00 | YES |
|  | 2026-09-03 04:37:55 | high | None | none | 2 | 04:37:55 | 04:28:10 | 04:18:00 | no |
