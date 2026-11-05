# the fdm2-reentry change batch | opened 2026-11-05

His 1105: *"we'll batch the changes to fdm2-reentry - here's the first"*. Nothing in here is built
until he says so. His words are verbatim; my notes are marked.

## 1 - ws3Mage must support ws3r at its reversal

> *"08-07 0013 fired too early because ws3r wasn't fully supported by ws3Mage. if we had waited
> for ws3Mage to be sameside ex-23/77-fence when ws3r reversed, we would have claimed an
> additional ~0.2% at 0104"*
>
> *"the same is true for highside 0432 and 0520, and many more"*

| what it reads | value |
|---|---|
| the line | ws3Mage |
| the fence | ex-23/77, same side as the reversal |
| when it is read | at the ws3r reversal |
| its effect | the signal waits until that holds |
| his named cases | 2026-08-07 00:13 LOW, 04:32 HIGH, 05:20 HIGH, *"and many more"* |
| his claimed gain on the first | ~0.2% more, taken at 01:04 |

MY NOTES, unresolved and NOT decided:

- 23/77 is a fence with no home yet. Every other fence in fdm2 has its own knob, so this needs one
- the mech's current walk triggers on ws3r nowhere - the trigger line is `FDM_RE_REV_TF` 5 and the
  gate line `FDM_RE_GATE_TF` 6. Where ws3r's reversal sits in the walk is his to place
- what the 00:13 leg actually realised, for the comparison he will want: +0.078% over 119.8 min,
  MAE 0.466, MFE 0.466

## 2 - the Mage ladder between ws1Mage and ws5Mage. EXPERIMENTAL

> *"at the ws5r reversal 08-07 0705"*
> *"the ws1Mage is oob at the lowside 0700 extremum, and ws5Mage is 54. between ws1Mage and
> ws5Mage, there is a ladder."*
> *"this needs further padding before we can apply it"*

HIS OWN HOLD. No code, no knob, no spec text until he pads it out.

## the DTF question he asked alongside the batch

> *"at 0328, is the code allowed to scan the DTF lines for ex-20/80-fence?"*

Yes. The 2026-08-07 03:28:00 rev-trade came from the director, which reads ws1..ws30.

| the mech | the lines it scans | includes DTF, above ws12 |
|---|---|---|
| step 1 | strictly above ws3, so ws4..ws30 | yes |
| the reversal population | ws3..ws30 | yes |
| the director's candidate | ws1..ws30 | yes |
| the director's clause one and clause two | ws1..ws30 | yes |
| the re-entry in-fence scan | ws7..ws12 | no |
| the re-entry mod's line scan | ws4..ws12 | no |

The director's ws1 floor and ws30 ceiling are MINE, stated when it was built. `FDM_RE_SCAN_HI` 12
is his, from the 1104 re-entry spec.

## PARKED for optimisation - ws4r sliced to 1-minute seams (2026-11-05)

His 1105: *"slice ws4r into 4 seams per bar, each seam at 01:00 -5s, and test if the ws4r '1
minute seams' create an early reversal"*, then *"it'll come in handy when we start optimising
after the mech is behaving better"*.

PARKED BY HIM. Nothing is wired: `FDM_RE_REV_READ` is still the 240 s closed-prev read. The
numbers are kept here so the test does not have to be re-run.

The slice is ws4r read at 60 s seams - four per ws4 bar, each at the minute minus 5 s, so
00:00:55, 00:01:55 and so on. Both series are read by `jig.cp_reversal`, no hold.

| 2026-08-07 ws4r HIGH, his pivot | the 240 s series reversal | the 60 s series reversal | the slice is earlier by |
|---|---|---|---|
| 00:08 | 00:16:00 | 00:10:00 | 360 s |
| 01:00 | 01:08:00 | 01:02:00 | 360 s |
| 04:00 | 04:00:00 | 04:01:00 | -60 s |
| 04:28 | 04:36:00 | 04:31:00 | 300 s |
| 06:16 | 06:16:00 | 06:17:00 | -60 s |
| 07:04 | 07:04:00 | 07:05:00 | -60 s |

| 2026-08-07 ws4r LOW, his pivot | the 240 s series reversal | the 60 s series reversal | the slice is earlier by |
|---|---|---|---|
| 00:08 | 00:08:00 | 00:08:00 | 0 |
| 01:00 | 01:00:00 | 01:00:00 | 0 |
| 04:00 | 04:08:00 | 04:05:00 | 180 s |
| 04:28 | 04:28:00 | 04:28:00 | 0 |
| 06:16 | 07:00:00 | 06:16:00 | 2640 s |
| 07:04 | 07:12:00 | 07:04:00 | 480 s |

| the whole day's reversal count | HIGH | LOW |
|---|---|---|
| the 240 s series | 176 | 164 |
| the 60 s series | 562 | 532 |

HIS OWN CAVEAT, recorded in his words: *"there's a few flips from high to low in there that would
make it a bit challenging (0704 and 0705, 0100 and 0102), but we might be able to temper them with
the ws1r line"*. The ws1r tempering is his idea and is not built.

The script is `/home/joe/.claude/jobs/7c82535c/tmp/seam60.py`; it needs no repo state.

## NEXT, from his 1105: a minimum TF for the ws{TF}x-cadence

> *"the next problem to face will be the ws10x cadence that fires next. ws2x and ws4x are likely
> too wavy for a reliable ws10x cadence, maybe it needs a minimum TF"*

HIS OBSERVATION, not built. Nothing has a minimum-TF floor on the director's candidate today.

| the setting | value | what it does |
|---|---|---|
| the director's candidate scan | ws1..ws30 | the floor and the ceiling are MINE, stated when built |
| FDM_XCAD_RULE | A | the highest away line with its ex-20/80 lines above all towards |
| FDM_XCAD_EXF | 0 | the candidate need not be ex-20/80 itself, his flat "no" |

What the 2026-08-07 data already shows about low-TF candidates:

| the cadence event | the candidate rule A picked | the race it ran |
|---|---|---|
| 02:20:00 | ws20r | ws20x to ws20Mage, confirmed 02:22:15 |
| 08:50:55 and 08:51:55 | ws1r | - |
| 03:21:00, LOW re-entry window | ws4x carried the window |
| 00:47:00, HIGH re-entry window | ws12x carried the window |

So the director has already selected ws1r at two bars on 08-07, which is the case his observation
names. A floor knob would be his value and his name; nothing is added until he gives both.
