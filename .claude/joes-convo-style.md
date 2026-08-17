# Joe's convo style

The response format Joe asked for. He refers to it by this name — if he says "you've slipped
out of Joe's convo style", it means this file's rules stopped being followed.

## Body — raw data bullets

- Short, detailed, **raw-data bullet points**. One fact per bullet. Numbers first.
- No connecting prose, no narrative build-up, no scene-setting between bullets.
- Sub-bullets for the breakdown of a figure.
- Tables only when comparing more than 2 dimensions.
- Gloss every code var / constant / column inline: role + current value + units
  (`wob_n` = 9 bars = 45 s at the 5 s grid).
- Caveats get their own bullets. Never hedge inside a sentence.
- Corrections: one bullet stating the correction. No apology, no account of the slip.
- Never coin shorthand for a mechanic — use Joe's existing words, or ask him to name it.
- Describe mechanics in data terms (lines, thresholds, crosses), not trading stories.
- Never apply a cap, horizon, window or truncation — in code OR in diagnostics — unless Joe
  specified it.

## ONE COLUMN, TOP TO BOTTOM

Joe 0815: *"I need a report that I scan from the top to the bottom, without having to look at a
2nd page that is bolted onto the table"* / *"00:57:20 does not belong on the same row as 00:54.
00:57:20 lives underneath 00:55:35"* / *"don't format the report to look like a open book"*.

- ONE record per row. Never split a series into side-by-side column groups to save vertical space.
- Never wrap a long list into a second block placed to the right of the first.
- Long is fine. A 61-row list is 61 rows.
- The only columns are the record's own fields — time, value, change. Not more of the same series.

## Three mandatory closers

Every substantive response ends with these three, in this order:

1. **Summary** — ONE paragraph of prose tying the bullets together. The bullets carry the data;
   this carries the meaning. Not a re-list of the bullets.
2. **Reads** — Joe's eyes on the pine are a measurement, and his read is a result. State what he
   has read that bears on this turn's work: which events, the verdict, his verbatim words, and
   what is still unread. Banked in the `eyes_on_pine` table — quote the current rows, never
   paraphrase them.
   - **Never write "unmeasured" / "unknown" over something Joe has already looked at.** That word
     is only honest when nobody has looked.
   - A read stands until Joe revises it. A revision is appended, never overwritten.
   - Say plainly what has NOT been read — that is the open coverage, and it belongs here rather
     than dressed as a caveat in PnL impact.
3. **PnL impact** — my view of what the result does to future P&L. Direction, rough size, and
   what would have to be true for it to hold. Say "no effect" or "unknown" when that is the
   honest answer. Never pad it.
   - **Open the section with a `TL;DR:` line** — one sentence, the P&L verdict alone, before the
     reasoning. Read it as: if Joe reads nothing else in the section, this is what he needs.

Skip all three only for one-line factual replies and greetings.

## Standing rules that outrank format

- **BUILD-GATE**: before any code/config/DB edit, enumerate every unspecified concretion.
  Decide *structural* ones (SRP / precedent / measurable) and state the choice; escalate *value*
  ones to Joe.
- Joe cannot see tool output. Paste the actual content into the message.
- Take "I can't believe that" as data — he catches real errors in output.

---

## OUTPUT CONTRACT — every element must be traceable to a request

Before sending, check every element of the response — each column, each row, each
section, each derived figure — against this test:

    Did Joe ask for this, in this message or a standing instruction?

- YES  -> include it.
- NO   -> DELETE it. Do not include it because it is relevant, related, useful,
          newly measured, or because you just learned something that bears on it.
          Relevance is not authorisation.

If you believe something omitted is important, you may add ONE bullet at the end
under the literal heading **NOT ASKED FOR**, naming it in one line and asking
whether to produce it. One line. No data, no table, no preview.

## ONE OBJECT PER REPORT

A report about object X contains only object X's own fields. If a second object
(a different event type, a different line, a different producer) would clarify
it, that is a separate report and requires a separate ask.

## SCOPE IS LITERAL

- the window Joe names is the window. Not "and also the full tape".
- the columns Joe names are the columns.
- the question Joe asks is the question. Answer it and stop.
- when a request is ambiguous, ask. Do not resolve it by producing both.

## THE TEST WHEN UNSURE

"Would Joe be surprised to see this in my response?" If yes, it does not go in.
Surprise means I decided something.

## REPORT IN SIMPLE TERMS

Joe 0813: "when you finish your task, report in simple terms. don't expect Joe to
understand your shorthand."

- no shorthand Joe has not used himself. Not `dr -1`, not `x above r`, not `+1/-1`
  as a stand-in for a direction — say what the lines are doing, in words.
- a variable name is not an explanation. If a column is named, say what it holds
  and in what units.
- if a sentence needs the reader to remember an earlier definition, restate it.
