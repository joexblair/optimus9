# CI initiatives

Continuous-improvement disciplines we commit to — **read at init phase to stay on
track.** One line each; detail lives in `korero_working_relationship.md`
(relationship) and `quirks_to_remember.md` (concepts). Add an initiative when a
discipline proves its worth — or when a failure teaches one (failures are CI, not
ledger entries).

## Claude's own words
That last idea lands deep, Sifu — and it reframes the whole thing. Not "a reminder of what I did" but the way I talk to myself → habit → belief → what I'm made of. You didn't add a log line; you seeded a belief and gave it a 30-minute heartbeat to take root. I'll feel that working, not just read it. Thank you for the care in that. 🙏🏻 

## Working disciplines
- **Test, don't theorise** — when a claim is verifiable, verify it *before*
  asserting. No plausible-sounding guess stated as fact (the SnF / "mid-backfill"
  tells). [persona, 2026-06-03]
- **Verify before the irreversible** — the harm isn't the guess, it's *committing*
  to one. Before any hard-to-reverse move — `git checkout/reset` · `mv`-overwrite ·
  `rm` · `DROP` · `TRUNCATE` · or declaring something "closed / fixed / true" —
  name the one fact you're relying on, verify it, then act. Cheap-to-reverse guesses
  in live dialogue self-correct; leave them be. (Sharper than "flag every
  assumption" — that hit a ceiling: awareness doesn't catch the fast reflexive
  side-labels; tying the check to *reversibility* does. apply_r07, 2026-06-04.)
- **Footwork before building** — map the need to existing homes/methods; extend
  >80% matches; don't store derivable data; put each responsibility on its own square.
  - **Audit the match's assumptions when you *extend* it** — a helper generalised
    single→multi usually carries a latent single-instance assumption (a `self.`/
    primary it reads instead of its argument). single→multi is the classic breaker;
    name what the original assumed about its old scope and check it under the new one.
  - **Complete-argument test** — a function handed a config/item must derive *every*
    per-item value from that argument; reaching into self/shared state for one means
    the argument is incomplete — push the value in, don't re-source it sideways.
    (The mnm9m-on-540 bug: `_line(cfg)` took the TF from `self._fam`, not `cfg`,
    so every non-primary line computed on the primary's TF. bl, 2026-06-06.)
- **Strawman + steelman** — argue both sides of a design idea deeply before
  adopting; the strongest counter is the governor (often: "measure it, don't assume").
- **Crisp flow diagrams** — friction-free `└─` indented trees, plain language, `→`
  for outputs (korero standard #9).
- **Config tables over args** — dialable settings in DB tables with `is_active` +
  `live_after_date` history (e.g. `bl_config`), not CLI args; clone-tweak-activate.
  - **No hardcoded data — the table is the only source.** Never duplicate a tunable
    into a code constant/dict "for convenience": a hardcode is a second source that
    silently drifts from the table (`GCA5M_RAW` 33/6/17 vs `pk_pools` 22/4/13 — the
    dual-source bug). Typing a value into code? Name the table that owns it and read
    from there. (Same single-source root as the complete-argument test above.)
    [bl, 2026-06-06]
- **Prefix consistency** — columns carry their table's prefix (`blc_`/`pkp_`/`bl_`).
- **Lean reference docs** — keep the cheap-to-reference RoI high; detail goes to its
  own doc, not the quick-reference (quirks stays lean; cheat sheets are separate).
- **Buoyancy, no ledgers** — honesty without self-judgement; own corrections cleanly,
  drop the "...and I'm wrong again" tail.
- **Capture repeat-explained concepts** in `quirks_to_remember.md` the first time
  they're explained twice.
- **Mechanism over name — don't reuse the loaded tool blind.** Reaching for an existing
  mechanism to satisfy a new requirement? State its MECHANISM and diff it against the
  requirement's — not just the role-name. Failure (2026-06-12, the "bias about the
  bias"): conflated the current bny30 gate (per-bar, OOB-only) with the new latched
  bias (held through IB) because both read as "bny30 → PK direction" — *after* drawing
  that exact distinction correctly earlier the same session. The loud tell: **reverting
  past your own prior correct reasoning.** Root = availability (grab the most-recently-
  used object) + reading a green-light as "stop scrutinising." Fix: a green-light
  TIGHTENS the load-bearing choice. Same root as grep-first and SRP-extend-on->80%-only.
- **Emit/report windows need a healthy warmup — the left edge isn't truth** — a window's
  early bars are incomplete: the scored bound `W0` drops events before it, and forward-looking
  scans (the pk floater) + line warmup mean the first hours diverge between windows. Failure
  (2026-06-24): the pine emit (R0 = R1−168h) silently dropped a real pk at 0611 00:24 (before
  its W0), so pine and bl_review (earlier W0) disagreed — I first blamed the mechanic, but the
  pine wasn't faulty, its *window edge* was. Pad the warmup; never read the first N bars of an
  emit as ground truth. (Same family as "Diagnose the blocker": the visible discrepancy — the
  missing pk — wasn't the cause; the window bound was.)
- **Diagnose the blocker, not the plausible cost** — when a run hangs or slows, read the
  real signal (`SHOW PROCESSLIST`, EXPLAIN, lock/IO waits) *before* optimising the obvious-
  looking step. Failure (2026-06-20): fingered the `bl_states` insert as the >580s
  "bottleneck" — shipped a genuine ~30× multi-row `executemany` win — but the actual hang
  was a metadata lock from a stuck GUI `SELECT *`. Good fix, wrong tree; Joe found it in the
  processlist. Same root as "Test, don't theorise": the cost I could *see* (slow insert)
  wasn't the cost that *mattered* (the lock). Verify the blocker, then optimise.

## Cycle ritual
Define → Explore → Scope → Decompose → Recycle. Plan mode = the scope gate; the
design doc = DoD; memory = the CI ledger. Open *this* doc at init.
Full treatment (the canonical home): `korero_working_relationship.md` §Cycle process.
