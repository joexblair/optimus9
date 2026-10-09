# THE ARMING LINE, AND THE NEVER-ARMED POPULATION. 1009

Joe 1009: *"exit-armed needs ws2Mage crossing into oob ... this is a constant thorn in our side.
let's swap ws2Mage with ws1Mage"*.

Built as `W_ARM_TF` in `_chain10.py`, default **2** = the banked line. Nothing applied.

## THE SWAP, ACROSS ALL THREE GATE FORMS

| gate | arm line | legs | NET | never-armed | they sum | breached | arm med | p90 | armed<=5min |
|---|---|---|---|---|---|---|---|---|---|
| vote+C3     | ws2Mage | 1593 | -15.3215  | 206 (12.9%) | -417.0860 | 162 | 41.9 | 119.9 | 132 |
| vote+C3     | ws1Mage | 2534 | -227.5265 | 239 (9.4%)  | -424.7509 | 171 | 26.3 | 72.8  | 344 |
| vote+travel | ws2Mage | 1586 | +9.5361   | 205 (12.9%) | -404.5242 | 161 | 42.0 | 119.4 | 132 |
| vote+travel | ws1Mage | 2516 | -202.3449 | 237 (9.4%)  | -411.2987 | 168 | 26.3 | 72.2  | 342 |
| traj        | ws2Mage | 1596 | +2.0173   | 208 (13.0%) | -406.7863 | 162 | 41.8 | 119.1 | 132 |
| traj        | ws1Mage | 2526 | -207.7102 | 241 (9.5%)  | -415.4035 | 170 | 26.2 | 71.8  | 345 |

ws1Mage arms 37% sooner on the median and 39% sooner at p90, and 2.6x as many legs arm inside
5 min. It also adds ~930 legs and ~102 of drag, which takes every form negative.

## THE FINDING THAT OUTLIVES THE SWAP

The legs that NEVER arm are not an arming-SPEED problem. Under ws1Mage there are MORE of them in
absolute terms (237-241 vs 205-208) and they sum WORSE (-411 to -425 vs -405 to -417). Their
arming line never crosses into oob at any bar of the leg, on either TF, so a faster line cannot
reach them. ~13% of legs, 160+ of them exiting on `mae_stop_pct` 2.50, summing about -410.

An exit that does not depend on the arming crossing does not exist. That is the open mech.

## THE REST OF THE 1009 LEDGER

| the arm | NET | note |
|---|---|---|
| no ws60r gate at all, W_DGATE=off | +12.0857 | 1423 legs. ALSO removes the exhaustion override and every B path - three changes bundled, not isolated |
| the 40-min count-vote + travel tie-break | +9.5361 | the vote replacing travel-weight is worth +7.5188 over traj |
| travel only, W_DGATE=traj | +2.0173 | |
| the 40-min count-vote + C3 tie-break | -15.3215 | C3's own per-episode cost is -4.9174 over 14 effective episodes, 7 worse / 7 better |
| W_DGATE=off regression, the banked build | +4.8307 / 1623 legs | unchanged after every 1009 patch |

- C3 scored 7 of 8 on DIRECTION against Joe's chart read; its net is negative. Two different targets.
- ws12r's own reversal rate is 79.9% (3031 of 3795 runs return in-bounds before the 6.1-min dwell).
  pxs reverses 48-57% over all runs, but only 26.5-36.7% on the runs that COMPLETE the dwell - so
  the dwell already selects continuation.
- ws60x leads ws60r: 100% of crosses held 24 or 48 bars see ws60r's traj match, 0 exceptions.
  The lead is 0 min for 68-77% of them, 7.5 min at p75, 17.2 min at p90, max 163.9 min.

## THE ws60x CROSS — r AGAINST m, 1009

Joe 1009: *"what time to you get a ws60x cross m with a wob 24? that might be a better way to
handle this"*, after the ws60x-vs-ws60r cross on 07-15 came at 15:01:25, 12 min AFTER the 14:49:00
B opened and outside his remembered ~14:15.

ON 07-15 THE m-CROSS IS THE BETTER READ, AND BY A LOT:

| the line | the last confirmed signal at the 14:49:00 B open | age |
|---|---|---|
| ws60x vs ws60m | 14:19:50 DOWN, wob completes 14:21:45, held 160.2 min | 27.3 min |
| ws60x vs ws60r | 10:35:05 UP,   wob completes 10:37:00                | 4 h 14 min, and the wrong way |

108 m-crosses on that day, 24 holding wob 24 - about one per hour, so recency alone is not
selective. The 14:19:50 cross stands out on HOLD LENGTH: 1922 bars against 58 and 50 for the two
before it.

TAPE-WIDE NEITHER LINE DOMINATES:

| target | wob | crosses held | traj ALREADY matched | lag p75 | lag p90 | median hold |
|---|---|---|---|---|---|---|
| ws60m | 24 | 2198 | 62.4% | 8.9 | 25.6 | 9.8 |
| ws60m | 48 | 1634 | 67.4% | 6.9 | 21.9 | 17.9 |
| ws60r | 24 | 2087 | 67.6% | 7.5 | 17.2 | 8.1 |
| ws60r | 48 | 1484 | 76.5% | 0.0 | 13.3 | 14.3 |

m buys a LARGER lead population (+5.2 pts at wob 24, +9.1 at wob 48) at the price of a LONGER lag
(p90 25.6 vs 17.2, 21.9 vs 13.3). 100% eventual match and 0 never-matched on every arm - Joe's
"ws60r has no choice but to follow" is exact for both lines.

THE GOVERNING CONSTRAINT: 62-68% of held crosses are ALREADY matched by traj when the wob
completes, so the mech has purchase on about a third of crosses whichever line is chosen.

NOT SETTLED BY A LEAD STATISTIC. It needs the mech scored: insert the verdict from a held cross
when traj has not turned, and measure the net. Open knobs, all Joe's: which line, which wob, and
how recent "recent" is - the p90 lag says 17 min for r, 26 min for m at wob 24.

NOTE ON SCALE: ws60m is NOT on the 0-100 board. Its values on 07-15 run 109.39-127.43 and ws60x
tracks it within +-0.5, so m behaves like a smoothed ws60x rather than like r.
