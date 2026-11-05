# the spine census — the four petri-dish values, DERIVED. 2026-11-05

HIS ASK: *"honestly I wouldn't know the four spine values - can you build a jig that derives them,
or reverse-engineers them?"* and *"you'll need a large sample to create stable results"*.

Jig: `docs/octo-freedom/1022_v4/out/spine_census.py`. Output: `spine_full2.out`, 1,534 rows.
IT PICKS NOTHING. Every combination is reported and the values fall out of the numbers.

## THE SAMPLE

| the tape | value |
|---|---|
| bars | 1,632,960 |
| span | 2026-07-02 12:00:00 to 2026-10-04 23:59:55, 94.5 days |
| legs across the eight Mage lines | 32,374 |
| leg-by-line observations | 970,028 |
| run time | 480 passes in 28 s |

| the Mage line | legs | non-overlapping legs | median length, min | overlap factor |
|---|---|---|---|---|
| ws1Mage | 9254 | 2251 | 35.0 | 3.11 |
| ws2Mage | 6328 | 1265 | 66.1 | 4.01 |
| ws3Mage | 5077 | 877 | 99.7 | 4.85 |
| ws5Mage | 3784 | 556 | 165.0 | 6.08 |
| ws10Mage | 2641 | 311 | 319.8 | 7.75 |
| ws15Mage | 2135 | 205 | 468.6 | 9.46 |
| ws20Mage | 1735 | 167 | 620.9 | 10.03 |
| ws30Mage | 1420 | 105 | 948.7 | 12.93 |

THE LEGS OVERLAP, 3.11x to 12.93x, so every rate is reported over all legs AND over a
non-overlapping subset taken greedily by earliest close. The rates agree to within a point, so
the overlap does not bias them - it only inflates the apparent sample.

## SPINE 1 AND 2 ARE ONE VALUE, NOT TWO

The base rate rises with the Mage leg's length and falls with the r line's bar width, so it is
driven by ONE ratio. The r line nearest a coin flip, per Mage line:

| the Mage line | closed-prev 20/80 HIGH | its rate | ratio to the Mage TF |
|---|---|---|---|
| ws1Mage | ws3r | 54.4% of 2251 | 3.0 |
| ws2Mage | ws6r | 50.8% of 1265 | 3.0 |
| ws3Mage | ws9r | 51.1% of 877 | 3.0 |
| ws5Mage | ws14r | 50.9% of 556 | 2.8 |
| ws10Mage | ws27r | 49.5% of 311 | 2.7 |
| ws15Mage | ws28r | 58.0% of 205 | the r ladder's ceiling, not a 50 point |
| ws20Mage | ws28r | 59.9% of 167 | the ceiling |
| ws30Mage | ws30r | 71.4% of 105 | the ceiling |

**r TF at a coin flip is about 2.7 to 3.0 x the Mage TF**, on closed-prev at the 20/80 fence. Above
ws10Mage the ws30 ladder runs out, so those rows are capped by the ladder rather than by the mech.

The fence and the read move the ratio, nothing else:

| the arm | the ratio |
|---|---|
| closed-prev, 20/80 | 2.7 to 3.0 |
| closed-prev, 15/85 | 1.0 to 2.0 - a deeper fence needs a faster r line |
| emerging, 20/80 | about 3.6 to 4.0 - emerging reaches further, so a slower line suffices |

## SPINE 3 - THE FENCE

Both fences work. They shift the contour and nothing else. 15/85 is the indicator spec's own
boundary (ic_high_boundary 85.00, ic_low_boundary 15.00); 20/80 is a knob we added.

## SPINE 4 - THE DAYS

Settled. Over 970,028 observations the running base rate moves under +/-0.16 points per day
through the last week, ending at 45.214%. The whole tape is past the point where more days move it.

## THE SIDE QUESTION IS A NEAR-FENCE-VERSUS-FAR-FENCE QUESTION

| the Mage line | closed-prev 20/80, opened LOW -> HIGH fence | opened LOW -> LOW fence | which wins |
|---|---|---|---|
| ws1Mage | 17.7% of 141246 | 37.6% of 141246 | the LOW fence |
| ws2Mage | 24.2% of 95062 | 48.5% of 95062 | the LOW fence |
| ws3Mage | 30.8% of 75012 | 55.7% of 75012 | the LOW fence |
| ws5Mage | 43.0% of 55347 | 58.9% of 55347 | the LOW fence |
| ws10Mage | 67.6% of 39480 | 62.9% of 39480 | the HIGH fence |
| ws15Mage | 77.1% of 33450 | 66.6% of 33450 | the HIGH fence |
| ws20Mage | 85.2% of 28170 | 69.9% of 28170 | the HIGH fence |
| ws30Mage | 89.8% of 21450 | 76.7% of 21450 | the HIGH fence |

MY SMOKE TEST WAS WRONG AS A GENERAL CLAIM. I ran it on ws10Mage alone, which sits exactly on the
crossover, and reported the side reading as settled. It flips below ws10Mage: a short leg re-touches
the fence the lines came from, a long leg has time to traverse to the far one. 35.0 min against
948.7 min is the whole explanation.

## WHAT IS STILL HIS

Which leg length the petri dish should run at. Three pairs sit on the contour:

| the pair | median leg, min | non-overlapping legs | its rate |
|---|---|---|---|
| ws1Mage + ws3r | 35.0 | 2251 | 54.4% |
| ws5Mage + ws14r | 165.0 | 556 | 50.9% |
| ws10Mage + ws27r | 319.8 | 311 | 49.5% |

The leg he brought this work to me over - the 2026-08-07 04:16:00 LONG - ran 152.1 min and he reads
its exit as early by about four hours. That horizon is bracketed by ws5Mage and ws10Mage. ws1Mage
is the largest-sample control. NOT PICKED HERE.
