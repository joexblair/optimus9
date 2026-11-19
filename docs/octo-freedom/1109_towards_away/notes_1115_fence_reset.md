# 1115 - fdm3-fence-reset-TO, the flip at 50 swapped for the 33/67 fence (BUILT ON THE 8789 TEST PAGE, 2026-11-16)

His words: *"I want to simply swap the static 50 'line' with a (100 - {knob:33,`fdm3-fence-reset-TO`}) 33/67 fence"* /
*"the mech will reset r to TO if it crosses into the fence then crosses out if the fence on the sameside as the infence incursion"* /
*"if the line continues through the fence entirely (eg travels from 90 to 30, then back to 80) the same logic applies: the r will be tagged TO when r crosses over 67"*.
Examples: *"ws3 r examples, taken from the persepective of r landing and reversing inside the fence: 09-19 1512, 1657, 2003, 09-20 0921, 1154"*.

## What the test ran (scratch only, nothing on disk changed)

- the flip at 50 replaced in memory: HIGH target-side, the first bar of the AW with emerging r under 67, then the first
  bar strictly over 67 after it = TO; LOW target-side, over 33 then strictly under 33
- MINE, open with Joe 1115: only the target-side fence line tags TO (67 HIGH / 33 LOW); the 50 reset and void stay at 50;
  the 1110 answers carried (emerging read, an AW that starts in or beyond the fence already counts, the extremum is
  retired after the flip)
- 23/77 fence, pivots as found, A ws1-ws6 off and on; the page's other states not run

| check | result |
|---|---|
| the test's flip-at-50 state against the live page, every printed row of the five windows, A off and A ws1-ws6 on | 0 differ (asserted) |
| emerging ws1r..ws30r bars at exactly 33.00 / 67.00 / 50.00 | 0 / 0 / 0 |
| run time per state | 113.8 - 207.0 s |

## The five examples, ws3, A ws1-ws6 off

| his example | target-side | AW starts | TO, flip at 50 | TO, 33/67 fence |
|---|---|---|---|---|
| 2026-09-19 15:12 | LOW | 2026-09-19 14:55:50 | 2026-09-19 15:12:50 | 2026-09-19 15:24:55 |
| 2026-09-19 16:57 | HIGH | 2026-09-19 16:50:20 | 2026-09-19 17:12:00 | 2026-09-19 16:53:10 |
| 2026-09-19 20:03 | HIGH | 2026-09-19 19:36:25 | 2026-09-19 19:57:00 | 2026-09-19 19:40:00 |
| 2026-09-20 09:21 | HIGH | 2026-09-20 09:12:35 | 2026-09-20 09:33:00 | 2026-09-20 09:27:00 |
| 2026-09-20 11:54 | HIGH | 2026-09-20 11:57:20 | 2026-09-20 12:00:00 | 2026-09-20 12:00:00 |

The 5 s flips and ws3r's crosses of 33 / 50 / 67 per window: scratchpad fence_reset/merged0.txt (A off), merged1.txt (A ws1-ws6 on).
A ws1-ws6 on differs only at 2026-09-20 09:07-09:12: one AW from 09:07:05 in both versions, where A off has three flips.

## Whole tape, page rows (136,079), ws1..ws15, A ws1-ws6 off

| line | rows AW, flip at 50 | rows AW, 33/67 fence | rows AW -> TO | rows TO -> AW |
|---|---|---|---|---|
| ws1 | 58,349 | 73,259 | 10,692 | 25,602 |
| ws2 | 58,191 | 69,436 | 12,348 | 23,593 |
| ws3 | 60,161 | 65,605 | 14,167 | 19,611 |
| ws4 | 59,042 | 62,695 | 13,892 | 17,545 |
| ws5 | 57,162 | 59,634 | 13,625 | 16,097 |
| ws6 | 56,981 | 54,436 | 14,352 | 11,807 |
| ws7 | 51,751 | 49,679 | 13,178 | 11,106 |
| ws8 | 49,197 | 45,675 | 12,349 | 8,827 |
| ws9 | 44,789 | 43,620 | 9,972 | 8,803 |
| ws10 | 43,376 | 40,114 | 9,912 | 6,650 |
| ws11 | 39,896 | 36,401 | 8,558 | 5,063 |
| ws12 | 37,193 | 34,816 | 7,690 | 5,313 |
| ws13 | 36,068 | 32,443 | 7,609 | 3,984 |
| ws14 | 33,291 | 30,086 | 7,048 | 3,843 |
| ws15 | 31,953 | 30,447 | 5,385 | 3,879 |

## Open with Joe 1115 (asked, not built)

1. the 50 reset and void: stay at 50, or move to 33/67 with the flip
2. a counter-side incursion (HIGH: r under 33 rises over 33, drops back under 33): stays AW (test) or TO
3. 2026-09-19 20:03 and 2026-09-20 11:54 read TO in both versions - his read there
4. the carried 1110 answers and the scope (page only, all 8 states, no button; the banked towards/away run unchanged)

## His answers (1115, late) and the 8789 build

*"this will need to be built on the port 8789 ui first"* / *"Q1: move them to the fence"* - his pick: the 50 reset and void
read the same line as the flip, 67 HIGH / 33 LOW / *"Q2: In the test it reads AW, because only a cross back over 67 gives
TO."* / *"Q3: I agree with your tags.  I forgot that this mech uses emerging, so my view was tainted"* (his Q3 was on the
test above, reset and void at 50) / *"Q4: the question's answers stay the same"*. A locked on 8789: ws1-ws6 on, ws7-ws15 off.

- towards_away.run `rst` (line50), default None = the banked 50 line; the 8789 page runs from a test copy of the page
  (scratchpad page8789t), 8788 and its file untouched

| check | result |
|---|---|
| rst None against the earlier flip-at-50 test, ws1..ws15, A ws1-ws6 on | 0 of 24,494,400 bars differ |
| rst 33 against the per-side composite of two global-line runs (67 on HIGH trades, 33 on LOW), ws1..ws30 | 0 of 48,988,800 bars differ |
| 8789 start-up, 2 states | 378.5 s |
| 8789 1109 r-pred control | 257,295, MATCH |
| 8789 against 8788 (A ws1-ws6 on, ws7-ws15 off), both flips: r-pred and sums, SL%, M-no-rev, target-side, X/E cross bits | 0 cells differ |
| 8789 flip 0 TO/AW against the separate rst 33 run, ws1..ws15 | 0 of 2,041,185 differ |

| his example | 8788 now | the test (reset and void at 50) | 8789 (reset and void at 67) |
|---|---|---|---|
| 2026-09-19 15:12 | TO from 2026-09-19 15:12:50 | AW to 2026-09-19 15:24:55 | the same as the test |
| 2026-09-19 16:57 | AW to 2026-09-19 17:12:00 | TO from 2026-09-19 16:53:10 | the same as the test |
| 2026-09-19 20:03 | TO | TO | AW from 2026-09-19 19:42:20 to the trade's close, 2026-09-19 20:17:05 |
| 2026-09-20 09:21 | AW to 2026-09-20 09:33:00 | TO from 2026-09-20 09:27:00 | TO 2026-09-20 09:27:00, AW 2026-09-20 09:27:05 to 09:30:00, TO from 2026-09-20 09:30:00 |
| 2026-09-20 11:54 | TO, AW 2026-09-20 11:57:20 to 12:00:00 | the same as 8788 | TO, no AW at 2026-09-20 11:57:20 (its samples, 62.09 to 63.81, are void under 67) |

| line | rows AW, 8788 now | rows AW, 8789 | rows AW -> TO | rows TO -> AW |
|---|---|---|---|---|
| ws1 | 59,952 | 60,124 | 19,921 | 20,093 |
| ws2 | 60,611 | 58,639 | 20,453 | 18,481 |
| ws3 | 63,227 | 56,303 | 21,993 | 15,069 |
| ws4 | 62,195 | 54,852 | 21,163 | 13,820 |
| ws5 | 61,194 | 54,029 | 20,271 | 13,106 |
| ws6 | 60,611 | 46,740 | 22,095 | 8,224 |
| ws7 | 52,062 | 41,170 | 19,296 | 8,404 |
| ws8 | 49,506 | 37,685 | 18,319 | 6,498 |
| ws9 | 45,109 | 34,764 | 16,595 | 6,250 |
| ws10 | 43,587 | 31,799 | 16,501 | 4,713 |
| ws11 | 40,017 | 28,164 | 15,076 | 3,223 |
| ws12 | 37,193 | 26,030 | 14,358 | 3,195 |
| ws13 | 36,068 | 24,077 | 14,224 | 2,233 |
| ws14 | 33,291 | 21,919 | 13,151 | 1,779 |
| ws15 | 31,953 | 21,482 | 12,239 | 1,768 |

PENDING his review of 8789. Nothing on 8788, nothing committed, the workmate not told.

## 1116 - his flip pivots question, 2026-09-22 00:53 / 00:54, ws16-22

His report: TO(exf):1 on the 00:53 row with flip pivots off, TO(exf):5 on the 00:54 row with it on.

| pseudo trade | target-side, as found | target-side, flip pivots |
|---|---|---|
| 2026-09-21 21:05:10 to 2026-09-22 00:54:55 | HIGH | LOW |
| 2026-09-22 00:54:55 to 2026-09-22 02:24:50 | LOW | HIGH |

| line | closed-prev r | row 00:53 (read 00:54:00), as found, HIGH | row 00:54 (read 00:55:00), flipped, HIGH |
|---|---|---|---|
| ws16 | 67.3 | TO(inf) | TO(inf) |
| ws17 | 63.6 | TO(inf) | TO(inf) |
| ws18 | 82.2 | AW(exf) | TO(exf) |
| ws19 | 79.2 | AW(exf) | TO(exf) |
| ws20 | 90.6 | TO(exf) | TO(exf) |
| ws21 | 77.3 | AW(exf) | TO(exf) |
| ws22 | 80.7 | AW(exf) | TO(exf) |

- 8789 config (23/77, A ws1-ws6, fence reset 33). TO(exf) on those two cells is the same on 8788 (1 and 5); 8788's 00:53 TO/AW split is 2/5, 8789's 3/4
- the flipped 00:54 row is a new HIGH trade opened at 00:54:55 (the ws2Mage HIGH pivot); every line starts TO at a trade's open
