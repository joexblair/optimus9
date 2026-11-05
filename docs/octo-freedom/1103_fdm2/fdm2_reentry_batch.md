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
