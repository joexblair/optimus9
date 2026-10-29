# HIS ws1b FIRING MECH, READ AGAINST THE 2026-08-29 23:50 SHORT
# SPAN 2026-08-29 23:00:00 .. 2026-08-30 00:30:00 | RULED_OK True
# oob is 15/85. ws1b and the Mage ladder are the CLOSED reads.
# LIN2_CROSS_WOB 12 bars = 60 s - his 1027 "add the wob12 to all crosses".
# the trailing oob lookback is 300 s - his "last 5 minutes".
# the band is ws6..ws12 - wsf is ws1..ws12, his 1017 names.

## 1 - every ws1b oob->ib cross in the span

| the raw cross bar | the wob 12 confirm bar | the candidate side | ws1b at raw | ws1b at confirm |
|---|---|---|---|---|
| 2026-08-29 23:17:00 | 2026-08-29 23:17:55 | LOW | 26.59 | 26.59 |
| 2026-08-29 23:28:00 | 2026-08-29 23:28:55 | LOW | 17.25 | 17.25 |
| 2026-08-29 23:54:00 | 2026-08-29 23:54:55 | HIGH | 81.82 | 81.82 |
| 2026-08-29 23:57:00 | 2026-08-29 23:57:55 | HIGH | 77.03 | 77.03 |
| 2026-08-30 00:19:00 | 2026-08-30 00:19:55 | HIGH | 73.24 | 73.24 |
| 2026-08-30 00:21:00 | 2026-08-30 00:21:55 | HIGH | 58.78 | 58.78 |

## 2 - every ws5Mage oob RUN in the span, with its extremum

| the side | the run enters | the run leaves | bars | the extremum bar | ws5Mage at the extremum |
|---|---|---|---|---|---|
| HIGH | 2026-08-29 23:50:00 | 2026-08-29 23:54:55 | 60 | 2026-08-29 23:50:00 | 87.75 |
| HIGH | 2026-08-30 00:20:00 | 2026-08-30 00:24:55 | 60 | 2026-08-30 00:20:00 | 93.77 |

## 3 - the ws5Mage gate at each cross, and the anchor it selects

| the raw cross bar | the confirm bar | candidate side | ws5Mage oob AT the cross? | oob inside the trailing 300 s? | the anchor bar | ws5Mage at the anchor |
|---|---|---|---|---|---|---|
| 2026-08-29 23:17:00 | 2026-08-29 23:17:55 | LOW | no | no | - | - |
| 2026-08-29 23:28:00 | 2026-08-29 23:28:55 | LOW | no | no | - | - |
| 2026-08-29 23:54:00 | 2026-08-29 23:54:55 | HIGH | YES | YES | 2026-08-29 23:50:00 | 87.75 |
| 2026-08-29 23:57:00 | 2026-08-29 23:57:55 | HIGH | no | YES | 2026-08-29 23:50:00 | 87.75 |
| 2026-08-30 00:19:00 | 2026-08-30 00:19:55 | HIGH | no | no | - | - |
| 2026-08-30 00:21:00 | 2026-08-30 00:21:55 | HIGH | YES | YES | 2026-08-30 00:20:00 | 93.77 |

## 4 - the ws6..ws12 Mage ladder AT THE ANCHOR BAR, per candidate cross

| the cross bar | candidate side | the anchor bar | the line | value at the anchor | ws5Mage at the anchor | away from the candidate side? |
|---|---|---|---|---|---|---|
| 2026-08-29 23:54:00 | HIGH | 2026-08-29 23:50:00 | ws6Mage | 76.60 | 87.75 | YES |
| 2026-08-29 23:54:00 | HIGH | 2026-08-29 23:50:00 | ws7Mage | 72.61 | 87.75 | YES |
| 2026-08-29 23:54:00 | HIGH | 2026-08-29 23:50:00 | ws8Mage | 44.41 | 87.75 | YES |
| 2026-08-29 23:54:00 | HIGH | 2026-08-29 23:50:00 | ws9Mage | 51.23 | 87.75 | YES |
| 2026-08-29 23:54:00 | HIGH | 2026-08-29 23:50:00 | ws10Mage | 70.95 | 87.75 | YES |
| 2026-08-29 23:54:00 | HIGH | 2026-08-29 23:50:00 | ws11Mage | 69.02 | 87.75 | YES |
| 2026-08-29 23:54:00 | HIGH | 2026-08-29 23:50:00 | ws12Mage | 59.25 | 87.75 | YES |
| 2026-08-29 23:57:00 | HIGH | 2026-08-29 23:50:00 | ws6Mage | 76.60 | 87.75 | YES |
| 2026-08-29 23:57:00 | HIGH | 2026-08-29 23:50:00 | ws7Mage | 72.61 | 87.75 | YES |
| 2026-08-29 23:57:00 | HIGH | 2026-08-29 23:50:00 | ws8Mage | 44.41 | 87.75 | YES |
| 2026-08-29 23:57:00 | HIGH | 2026-08-29 23:50:00 | ws9Mage | 51.23 | 87.75 | YES |
| 2026-08-29 23:57:00 | HIGH | 2026-08-29 23:50:00 | ws10Mage | 70.95 | 87.75 | YES |
| 2026-08-29 23:57:00 | HIGH | 2026-08-29 23:50:00 | ws11Mage | 69.02 | 87.75 | YES |
| 2026-08-29 23:57:00 | HIGH | 2026-08-29 23:50:00 | ws12Mage | 59.25 | 87.75 | YES |
| 2026-08-30 00:21:00 | HIGH | 2026-08-30 00:20:00 | ws6Mage | 102.25 | 93.77 | no |
| 2026-08-30 00:21:00 | HIGH | 2026-08-30 00:20:00 | ws7Mage | 59.55 | 93.77 | YES |
| 2026-08-30 00:21:00 | HIGH | 2026-08-30 00:20:00 | ws8Mage | 62.44 | 93.77 | YES |
| 2026-08-30 00:21:00 | HIGH | 2026-08-30 00:20:00 | ws9Mage | 84.08 | 93.77 | YES |
| 2026-08-30 00:21:00 | HIGH | 2026-08-30 00:20:00 | ws10Mage | 78.19 | 93.77 | YES |
| 2026-08-30 00:21:00 | HIGH | 2026-08-30 00:20:00 | ws11Mage | 47.33 | 93.77 | YES |
| 2026-08-30 00:21:00 | HIGH | 2026-08-30 00:20:00 | ws12Mage | 46.79 | 93.77 | YES |

## the verdict per cross

| the raw cross bar | the confirm bar | candidate side | the anchor bar | lines away at the anchor | required | FIRES? | the trade side |
|---|---|---|---|---|---|---|---|
| 2026-08-29 23:54:00 | 2026-08-29 23:54:55 | HIGH | 2026-08-29 23:50:00 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | 2 | YES | SHORT |
| 2026-08-29 23:57:00 | 2026-08-29 23:57:55 | HIGH | 2026-08-29 23:50:00 | 7 - ws6,ws7,ws8,ws9,ws10,ws11,ws12 | 2 | YES | SHORT |
| 2026-08-30 00:21:00 | 2026-08-30 00:21:55 | HIGH | 2026-08-30 00:20:00 | 6 - ws7,ws8,ws9,ws10,ws11,ws12 | 2 | YES | SHORT |

| the read | value |
|---|---|
| his prediction | the 23:50 open moves forward to ~23:53 |
| crosses in the span | 6 |
| crosses passing the ws5Mage gate with an anchor | 3 |
