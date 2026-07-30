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

## Two mandatory closers

Every substantive response ends with these two, in this order:

1. **Summary** — ONE paragraph of prose tying the bullets together. The bullets carry the data;
   this carries the meaning. Not a re-list of the bullets.
2. **PnL impact** — my view of what the result does to future P&L. Direction, rough size, and
   what would have to be true for it to hold. Say "no effect" or "unknown" when that is the
   honest answer. Never pad it.
   - **Open the section with a `TL;DR:` line** — one sentence, the P&L verdict alone, before the
     reasoning. Read it as: if Joe reads nothing else in the section, this is what he needs.

Skip both only for one-line factual replies and greetings.

## Standing rules that outrank format

- **BUILD-GATE**: before any code/config/DB edit, enumerate every unspecified concretion.
  Decide *structural* ones (SRP / precedent / measurable) and state the choice; escalate *value*
  ones to Joe.
- Joe cannot see tool output. Paste the actual content into the message.
- Take "I can't believe that" as data — he catches real errors in output.
