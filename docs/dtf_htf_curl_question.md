# do we need to add this to dtf modelling?

Task #5, opened 0824. Joe: *"add your response verbatim to a task labelled 'do we need to add this
to dtf modelling?' - the modelling plan for dtf that we've agreed on in principle (earlier today)
might use this dtf HTF curl data, but not in the way that I originally considered"*.

The response below is verbatim, as delivered 0824. It is the complete pretext and context around
`RESCUE_REJECTED_CURL`, reconstructed from session `c0597645`, lines 1119 to 1207.

---

## the chain, from Joe's challenge to his ruling

**1 — Joe challenged a BLOCKED row (line 1119)**

> `44 | 07:21:50 | ... | BLOCKED | ws27r | ...`
>
> *"this shouldn't be blocked. 13 to 22 are all showing a reversal/curl while only the 4 HTFs are
> showing momentum. what was the fix for that? I think we tangented and haven't come back to it
> until now"*

**2 — the answer then: the fix exists and cannot fire (line 1131)**

- 8 lines running down — ws20r through ws27r.
- **zero lines reading as carrying the move up**, so Joe's three-line release count was zero.
- ws13r through ws19r had not moved in 30 minutes; three sat at exactly 0.00.
- the explanation given at the time: *"those seven lines are on the floor ... a line that cannot
  fall further stops having a slope"*.

**3 — Joe asked for the samples (line 1136)**

> *"that's a difference between our view. let's pull the line samples for 19 to 25, see what we can
> find"*

**4 — Joe read the flattening himself (line 1151)**

> *"you can just see it forming here, but not soon enough. understood"*
>
> *"what votes do sideways and none have?"*

**5 — the answer: neither votes (line 1154)**

| verdict | carries the move | opposes it |
|---|---|---|
| momo | yes | yes, read the other way |
| curl | yes | yes, read the other way |
| **sideways** | **no** | **no** |
| **none** | **no** | **no** |

- 7 of 15 lines silent at that bar — exactly the ones Joe read as reversed.
- flagged: *"whether a silent line should count towards the release when it sits at the floor, which
  is the only route by which 07:21:50 could free itself"*.

**6 — Joe proposed a sideways vote (line 1159)**

> *"I think sideways for a LTF (13/14/15) has a vote. sideways inidicates indecision, which is always
> voliatile - it needs the finisher to navigate the chop. how would you vote that? I rate LTF signals
> higher than HTF (>=22)"*

**7 — Joe came back to the flagged item (line 1176)**

> *"this is curious — whether a silent line should count towards the release when it sits at the
> floor, which is the only route by which 07:21:50 could free itself."*

**8 — the correction. THIS IS THE PRETEXT (line 1190)**

> **"correction to what I said last turn.** I called those lines silent because they sit at the floor
> and have no slope. That is wrong. **The code found a bend on all three and threw it away twice.**"

| line | value | what the test found first | final answer | why it was rejected |
|---|---|---|---|---|
| ws16r | 2.61 | **curl** | none | the bend points the wrong way — slope +0.080 |
| ws17r | 0.00 | **curl** | none | the bend **curves upward** — curvature +27.879 |
| ws18r | 0.00 | **curl** | none | the bend **curves upward** — curvature +25.914 |

- asked about the down move: the bend exists but **points up**, so it is not a down-curl. Discarded.
- asked about the up move: all three sit below 3 and need to be at or above 43.31 to 49.94.
  **Rejected on level before the bend is looked at.** Discarded.
- **"the line reads as nothing in both directions while the code holds a curvature of +27.9 that says
  it is turning up."**
- *"the floor is not the cause. ws16r is at 2.61 and moving, and it still reads as nothing."*
- flagged: *"whether a rejected down-curl that curves upward should be read as an upward vote, which
  is the exact signal being discarded here"*.

**9 — JOE'S RULING (lines 1195 and 1204, given twice)**

> *"— whether a rejected down-curl that curves upward should be read as an upward vote, which is the
> exact signal being discarded here."*
>
> **-yes**
>
> **-if other lines are backing the curl line, it has considerable weight**

and in the same message, on the sideways band:

> *"-I don't have an answer - the tuning process will expose it"*

**10 — the build gate raised in reply (line 1207)**

| # | concretion | resolution |
|---|---|---|
| 1 | which rejections get rescued | the two meaning *the bend points against the move*: rejected for **direction** (ws16r, slope +0.080) or for **curvature** (ws17r +27.9, ws18r +25.9) |
| 2 | the third rejection reason | **not rescued.** A bend rejected for poor fit quality is in the right direction and badly described — a different thing |
| 3 | *"if other lines are backing the curl line, it has considerable weight"* | **Joe's existing three-or-more release count is that requirement.** A rescued vote joins that count, so it only acts when other lines back it. No new number invented |
| 4 | the short-band edge | **not built.** Joe said tuning will expose it, so the sideways-vote idea stays unbuilt |

---

## what is still open on this

- **the question in the task title.** Does the discarded-curl data belong in the dtf setup model, and
  in what form. Joe 0824: *"might use this dtf HTF curl data, but not in the way that I originally
  considered"*.
- **Joe's sideways-vote idea from line 1159 was never built.** He rates ws13/14/15 higher than
  ws22+, and 16 to 21 is unassigned. His answer on where the band ends: *"I don't have an answer -
  the tuning process will expose it"*.
- **`build_dtf_delegation.py` omits the rescue.** It reads the cached tagged masks, which carry only
  the plain momo-or-curl verdict, so `RESCUE_REJECTED_CURL` is absent from the opposition count in
  the 85 delegation moments. The rescue can only ADD opposing lines, so it can only empty more
  blocking lists, so the list of free moments could be LONGER, never shorter. Joe validated the 85
  as they stand on 0824.
- **07:21:50 is one of the 28 signals the nested-opposition rule fires on**, and one of the three
  exhaust rows lost to the rising-edge fix.
