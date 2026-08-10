# 260803 draft strategy

**Status: DRAFT.** Joe 0803. This is the spec of record for the exhv2 chain from this date. Where it
disagrees with `docs/exhv2_spec.md`, `docs/260802_handover.md` or the code, **this document is right and
the other is a defect to be filed** — see §2.

---

## 1. The flow

> RPL prints an r-pred → exhv2 walks forward on s4 to the first held s4Mage crossing into OOB → sets bias
> from the OOB side → while **s22 OR s15r** reads momo, re-walk to the next one (REWALK 2) → classify
> s15r/s22r → branch → ANCHOR → SIGNAL

**Joe 0803, verbatim.** Everything below is technical note and can be wrong; the quote cannot.

### 1a. The steps, numbered

| # | step | producer | note |
|---|---|---|---|
| 1 | **r-pred print** | `predict_breach` on the TF's own r/m/M, in `rpl_walk` (RPL) | the trigger. Nothing upstream gates it |
| 2 | **hand-off to exhv2** | the r-pred timestamp reaches `build_exhv2` | see §2(b) — the current hand-off is defective |
| 3 | **WALK** | the first s4Mage **crossing into OOB after the r-pred bar**, then its 240 s dwell | RULED 0803 §7(2). s4Mage = `bb 37\|0.7\|close` @TF4. Held = OOB run ≥ `WALK_DWELL_BARS` = 48 bars = 240 s, counted **backward** per bar. **The crossing itself must be after the r-pred** — the code today takes the first `oob_qualified` rising edge after the r-pred, which can belong to a run that started before it (8 of 38, §3a) |
| 3b | **`confirmed_ib`** | an IB excursion resets the dwell only once it has lasted ≥ **22 bars = 110 s** | Joe 0803, §7(3) and §7(9). **NOT IMPLEMENTED** — today any single IB bar resets the counter. Calibration in §3b |
| 4 | **SET BIAS** | `build_exhv2._derive(b)` at the walk bar | bias is set on **two** things — the s4Mage OOB side, and MFE-side detection. §1b |
| 5 | **CHECK MOMO** | `build_exhv2.momo()` at the walk bar | **gate on the re-walk.** §1c |
| 6 | **REWALK** | repeat step 3 while step 5 holds | `REWALK` = 2 |
| 7 | **classify** s15r / s22r | `momo()` at the final walk bar | states: `momo` \| `sideways` \| `curl` \| `none` |
| 8 | **branch** | momo → rev · sideways → EXIT · dirty/none → fall to s4 | |
| 9 | **ANCHOR** | s15x × s15m cross, `cross_wob` | at/after the walk bar |
| 10 | **SIGNAL** | first gcs15x × gcs15m cross at/after the anchor | gcs15x `bb 5\|0.37\|close`, gcs15m `bb 6\|0.45\|close` @TF 15 s |
| 11 | **EXIT** | next `oob_qualified` rising edge strictly after the SIGNAL bar | same producer as step 3. Side-agnostic |

### 1b. Bias is set on two things

Joe 0802, verbatim (carried forward from `exhv2_spec.md` §4a):

> --context: bias is set on 1) s4M-cross-oob, 2) MFE side detection

> "is the trade" only if MFE detection == true, otherwise it is discarded
>
> --it's discarded because we don't know if the first pivot is MAE or MFE when r-pred fires - that is why we
> wait on s4M. the side s4M breaches on is the gauranteed bias direction

Code, `build_exhv2._derive(b)`, read at the walk bar:

```python
sd = 'hi' if M4[b] >= R.HI else 'lo'    # the side s4Mage breached
wt = 'hi' if dr > 0 else 'lo'           # the side the r-pred expected
mf = int(sd != wt)                      # MFE-side detection
ed = -dr if mf else dr                  # effective direction
```

`hi → SHORT`, `lo → LONG`. Not the bias. `ed` always resolves to the direction of the move into the breach.

### 1c. CHECK MOMO — the re-walk gate

**CHANGED 0803.** The gate is now **s22 OR s15r**, either one reading `momo`.

| | |
|---|---|
| spec 0803 | re-walk while **s22 OR s15r** reads `momo` |
| code today | re-walk while **s22 alone** reads `momo` — `build_exhv2.py:78` |
| status | **NOT IMPLEMENTED.** No code has been changed for this document |

`momo()` definition, unchanged:

| knob | value | role |
|---|---|---|
| `MOMO_SAMPLES` | 12 | point-samples per read |
| `MOMO_STEP_BARS` | 60 | = 5 min at the 5 s grid |
| `MOMO_WINDOW_MIN` | 60 | window. Needs **660 bars = 55 min** of prior r history |
| `MOMO_SLOPE_MIN` | 1.0 | r-units per 5-min sample |
| `MOMO_R2_MIN` | 0.50 | the "fuzzy straight line" |
| `LEVEL_SLACK` | 13.9 | tracking-weighted slack on the `r vs 50` level gate |
| `CURL_ARC_MIN` | 4.0 | a curl is not sideways |

- spec `exhv2_spec.md` §5 says 9 samples over 45 min. The code moved to 12 over 60 min on 0731. **The code
  is current; §5 is stale.**

---

## 2. Known defects in the documents this supersedes

**(a) `docs/260802_handover.md:115` names bp50 as the walker. It is wrong.** Written by me on 0802.
Corrected wording is §1 above. Evidence in §4.

**(b) The r-pred hand-off is selected using the future.** `build_exhv2.main()` iterates `rpl_exh_stat` rows
and reads `es_rpred_ms`. That column traces back to `build_rplwalk2.rpred_at(tf, dr, i)`, which looks
**backward** from a confirmed exhaustion bar:

```python
h = np.flatnonzero(st <= i)
j = int(h[-1])
```

So exhv2 only ever evaluates r-preds that **later** turned out to precede an exhaustion. Each individual
trade is causal — every input is at or before its own entry — but the **sample** is chosen with information
from after the trade closed. Worked example in §3.

Per §1 the r-pred print is the trigger and nothing upstream gates it. The current hand-off does not match
that. **UNRESOLVED — needs Joe's ruling on whether exhv2 should run on every r-pred print.**

**(c) `exhv2_spec.md` §5 momentum sampling is stale.** 9 samples / 45 min documented; 12 / 60 min in code
since 0731.

---

## 3. Worked example — r-pred 08-01 01:26:00

Banked in `rpl_dominoes_0802` (`dm_pk` 34), `rpl_exhv2_0802`, `rpl_exh_applied_0802`, `rpl_exh_stat_0802`.

| event | timestamp | source |
|---|---|---|
| r-pred | 08-01 **01:26:00** | `ea_rpred_ms` / `es_rpred_ms` |
| WALK | 08-01 **01:26:15** | `v2_walk_ms` — 3 bars after the r-pred |
| s4Mage at the walk bar | **89.68** | `dm_walk_s4m`. HI = 85.0 |
| bias | side `hi` → **SHORT** | `dm_walk_side` / `dm_dir` |
| momo at the walk bar | s15 `sideways`, s22 `sideways` | `v2_s15_state` / `v2_s22_state` |
| hops | **0** | `dm_hops` — momo did not hold, so no re-walk |
| branch | `s4` / action `EXIT` | `v2_branch` / `v2_action` |
| ANCHOR | 08-01 **01:27:35** | `v2_sig_ms` / `dm_s15x_ms` |
| SIGNAL | 08-01 **01:31:10** | `dm_sig_ms` |
| EXIT | 08-01 **02:01:40** | `dm_exit_ms` |
| return | **−0.348%**, hold 30.5 min | `dm_ret` / `dm_hold_min` |

**The chain above is forward and causal.** Every bar is at or before the one after it.

**What is not forward — the selection:**

| event | timestamp |
|---|---|
| r-pred episode ends | 08-01 02:42:35 (`ea_rpred_bars` 920 = 76.7 min) |
| bp50 setup | 08-01 **02:56:30** (`ea_setup_ms`) |
| exhaustion raw cross | 08-01 **04:18:50** (`xh_raw_ms`) |
| exhaustion confirmed | 08-01 **04:19:30** (`xh_conf_ms` = `dm_conf_ms`) |
| `v2_lead_min` | **−171.92** |

The trade opened and closed before the exhaustion that put it in the sample existed. §2(b).

**The walk bar is not a crossing.** `oob_qualified` returns the rising edge of "OOB for the last 48 bars,
counted backward", which for a run starting at bar z is `z + 47` = **crossing + 235 s**. Applied to this
row: walk 01:26:15 − 235 s ⇒ crossing at **01:22:20**.

**MEASURED 0803** against the s4Mage series, not derived:

| | |
|---|---|
| crossing into OOB | 08-01 **01:22:20**, s4M **86.03** |
| its run | **236 bars = 1,180 s = 19.7 min**, HELD |
| crossing → walk | **47 bars = 235 s** — `z + D − 1` matches the walk bar exactly |
| r-pred → crossing | **−44 bars = −220 s.** The crossing is **before** the r-pred |
| s4Mage at the r-pred bar | **92.45**, already OOB |

Only **2 of 8** crossings in 01:00 → 02:10 hold the dwell — 01:22:20 (the walk) and 01:57:45 (the exit).
The other six are pokes of 20–105 s.

**The 01:26:15 walk exists only because of a 60 s IB dip at 01:21:20** (depth 4.24 below HI). s4Mage was
OOB either side of it for 44 min. Without that dip the run merges with the preceding one, whose qualifying
edge is 01:02:00 — **before** the r-pred — and the walk moves to **02:01:40**, 35.4 min later. This is what
`confirmed_ib` = 22 bars addresses: at 110 s the 60 s dip does not confirm, so the dwell is not reset.

The exit checks out under the same arithmetic: `rpl_walkcand_0802` idx 5 crossing 01:57:45, run 106 bars;
01:57:45 + 235 s = **02:01:40**, matching `dm_exit_ms` exactly.

**`rpl_walkcand` cannot show the walk on this row.** It enumerates crossings from the **r-pred bar
forward**, and this run began before it. All six of its rows have `wc_chosen` = 0. Across the whole
rebuild `wc_chosen` fires on **30 of 38** events, so **8 of 38** walk on a spell that began before the
r-pred.

---

## 3a. The 8 rows whose walk came from a pre-r-pred crossing

Verified on `wc_conf_ms` (not the minute-precision `wc_conf_utc`). 38 events, 8 with no `wc_chosen`, 0 with more than one.

| event | candidates in lifetime |
|---|---|
| 0727 14:06 | 3 |
| 0728 13:23 | 14 |
| 0728 19:45 | 6 |
| 0729 18:19 | 5 |
| 0730 14:14 | 7 |
| 0731 19:12 | 6 |
| 0801 04:19 | 6 |
| 0801 10:04 | 3 |

## 3b. `confirmed_ib` calibration — measured

Every IB excursion in s4Mage, 08-01 00:00 → 04:00. 29 excursions in 4 h, one every 8.3 min, **median 55 s**.

The two the rule must separate:

| | duration | depth below HI | |
|---|---|---|---|
| 01:21:20 | **60 s** (12 bars) | **4.24** | must NOT confirm — it manufactured the 01:26:15 walk |
| 02:29:05 | **130 s** (26 bars) | **4.13** | must confirm |

- **depth cannot separate them** — the excluded dip is *deeper* than the admitted one
- **duration can.** Any value in **13–26 bars** separates them. **Joe set 22 bars = 110 s**, §7(9)

Joe's named ~02:28–02:40 band is **six** separate excursions, not one:

| start | bars | secs | depth | confirms at 22 bars? |
|---|---|---|---|---|
| 02:29:05 | 26 | 130 | 4.13 | **yes** |
| 02:31:55 | 4 | 20 | 1.08 | no |
| 02:32:25 | 1 | 5 | 0.15 | no |
| 02:32:35 | 1 | 5 | 2.95 | no |
| 02:32:45 | 22 | 110 | 6.14 | **yes** — exactly at the threshold |
| 02:34:50 | 138 | 690 | 14.88 | **yes** |

- at 22 bars, **3 of the 6** confirm. The other three are 1–4 bars and cannot be separated from the 12-bar dip by any rule
- **unresolved**: whether Joe means the first excursion or the whole 02:29:05 → 02:46:20 stretch read as one
- the 01:48:00 excursion on the same row (**350 s**, depth 10.38) sits between the walk and the exit and **confirms** at 22 bars, ending that s4Mage cycle mid-trade
- measured on **one 4-hour window**. The 7-day excursion distribution is not measured


---

## 4. bp50 — notes, verbatim

Reproduced exactly as established 0803. Everything here is measured or read from source.

> **Validated. You're right — `bp50` in that sentence is wrong. The walker is exhv2.**
>
> **Evidence 1 — exhv2 does not import bp50**
>
> ```
> build_exhv2.py imports:  build_exhaust · build_rplwalk2 · rpl_walk
>                          predict_breach · jig · rpl_cache · DatabaseManager · config
> ```
>
> - `build_past50` is **not** among them. exhv2 cannot call bp50
>
> **Evidence 2 — the walk code lives only in `build_exhv2.py`**
>
> - `def oob_qualified` is defined in **one file: `build_exhv2.py`**
> - the walk block, `build_exhv2.py:292-302`:
>
> ```python
> i = int(np.searchsorted(ts, int(r_['es_rpred_ms'])))    # <- the r-pred, handed in
> dr = 1 if r_['es_bias'] == 'bull' else -1
> M4 = MG[4]
> oob = np.flatnonzero(oob_qualified(M4, R.HI, R.LO)[i + 1:])
> if not len(oob):
>     continue
> cand = (oob + i + 1).tolist()                          # every QUALIFIED bar after the r-pred
> ```
>
> - and bias is set three lines later, `_derive(b)`:
>
> ```python
> sd = 'hi' if M4[b] >= R.HI else 'lo'    # the side s4Mage breached
> wt = 'hi' if dr > 0 else 'lo'           # the side the r-pred expected
> mf = int(sd != wt)                      # MFE-side detection
> ed = -dr if mf else dr                  # effective direction
> ```
>
> **Evidence 3 — bp50 has no r-pred walk at all**
>
> - `build_past50.py` calls `predict_breach` **twice**, both at line 87, building `pred3` / `pred4` as
>   **line arrays** — never to trigger a walk
> - `bp50.qualify()` is a different mechanic entirely:
>   - s4Mage OOB same-side, dwell ≥ `DWELL_S` = 240 s
>   - **AND** hs60x OOB same side, latched anywhere in that episode
>   - onset = `max(dwell-met bar, first hs60x-OOB bar)`
> - no r-pred appears in it
>
> **The corrected sentence**
>
> > RPL prints an **r-pred** → **exhv2** walks forward on s4 to the first held s4Mage crossing into OOB →
> > sets bias from the OOB side → while s22 reads `momo`, re-walk to the next one (REWALK 2) → classify
> > s15r/s22r → branch → ANCHOR → SIGNAL
>
> - `docs/260802_handover.md:115` names bp50 as the walker. **That line is wrong** and was written by me
>   on 0802
>
> **Where bp50 actually sits**
>
> | | |
> |---|---|
> | `build_past50` | imported by **`build_rplwalk2`** (`import build_past50 as BP`) |
> | its output | `BP.qualify()` onsets + `BP.trigger()` fires → the setups `build_rplwalk2.applied()` uses to establish `current_tf` |
> | its relation to exhv2 | **two steps removed** — bp50 → `rpl_exh_applied` → `rpl_exh_stat` → exhv2 reads `es_rpred_ms` |
> | what it shares with exhv2 | the number 240 s, on **different** tests: bp50's `DWELL_S` on the raw OOB episode, exhv2's `WALK_DWELL_BARS` = 48 bars on the backward per-bar test |
>
> **Caveat**
>
> - I have not checked whether `docs/260802_handover.md` says "bp50 walks" anywhere else, or whether the
>   same error propagated into other docs I wrote on 0802

---

## 5. History

| date | change | by |
|---|---|---|
| 0730 | exhv2 first spec'd. `docs/exhv2_spec.md`. Trigger = one evaluation per `es_rpred_utc` print, TF ≤ 22, standalone `predict_breach` on s4/s15/s22 | Joe |
| 0730 | r-pred recorded **at the producer** rather than reconstructed downstream. `docs/rpred_spec.md`. Three prior derives gave three different answers for the same event | Joe |
| 0731 | Mage mult corrected to **0.70** for exhv2's own line set; four of five exhv2 lines now differ from the `rpl_config` baseline | Joe |
| 0731 | `WALK_DWELL_BARS` = 48 bars = 240 s introduced — *"if s4M has crossed to oob AND STAYED CONSISTENTLY OOB FOR 240 SECONDS"* | Joe |
| 0731 | momentum window 45 → **60 min**, samples 9 → **12**. `CURL_ARC_MIN` added — a curl is not sideways | Joe |
| 0801 | **REWALK 2** adopted — re-walk to the next held s4Mage OOB crossing while s22 reads momo | Joe |
| 0801 | **gcs15 confirm** adopted. The s15x × s15m cross is demoted to ANCHOR; the SIGNAL is the next gcs15x × gcs15m cross | Joe |
| 0802 | the 240 s test made **causal** — per-bar and backward. The old form stamped the verdict at the crossing, needing 240 s of future; 17 of 147 signals had fired before their own walk bar was confirmable. The stamp moves +47 bars = +235 s | Joe |
| 0802 | lookahead scoring columns dropped — *"no need to report lookahead numbers - they're meaningless"* | Joe |
| 0802 | tape registry consolidated into `rpl_walk.TAPES`; three disagreeing literals collapsed | — |
| 0803 | `rpl_exhaust` found stale against the tape; `build_exhaust.py --persist` prepended to the rebuild chain. Applied exhaustions 37 → 367. **Task #47** | — |
| 0803 | 7-day rebuild on tape `'08-02'` — 38 signals, 07-26 → 08-01. `dominoes_0802.pine` | — |
| **0803** | **`docs/260802_handover.md:115` corrected: exhv2 walks, not bp50.** §4 | Joe |
| **0803** | **re-walk gate changed to `s22 OR s15r`.** NOT IMPLEMENTED | Joe |
| **0803** | this document created as the spec of record | Joe |
| **0803** | **the walk must follow a s4Mage crossing that is itself after the r-pred.** 8 of 38 rows violate it. §7(2), §3a | Joe |
| **0803** | **`confirmed_ib` named and set to 22 bars = 110 s.** An IB excursion resets the dwell only once it has lasted that long. NOT IMPLEMENTED. §7(3), §7(9), §3b | Joe |
| **0803** | dirty lines are **not** excluded from the widened re-walk gate. §7(1) | Joe |
| **0803** | `momo_ride_oob_slip` (#44) and over/under Moob (#40) — **no change for now**. §7(6) | Joe |
| **0803** | the jig's trigger found to be a **random 30–60 min timer**, not an r-pred. It proved the chain causal, never the trigger. §7(5) resolved | — |
| **0803** | **`final_r_pred` spec'd** — the RPL ladder fires on a stalled climb, replacing the exhaustion as exhv2's trigger. NOT IMPLEMENTED, 8 gaps open. §7(11), §8 | Joe |

---

## 6. Open, needing Joe

| # | item |
|---|---|
| §8 | the 8 gaps in the `final_r_pred` ladder rule |
| §1c | `s22 OR s15r` re-walk gate — implement, and A/B against `s22` alone |

**CLOSED 0803**

| item | ruling |
|---|---|
| dirty lines in the OR re-walk gate | **no** — do not exclude dirty. §7(1) |
| must the s4Mage crossing be after the r-pred | **yes.** §7(2) |
| `confirmed_ib` | **yes**, value **22 bars = 110 s**. §7(3), §7(9) |
| #44 slip / #40 over-under Moob | **don't change anything for now.** §7(6) |
| pine filename | **`dominoes.pine`**, unchanged. §7(7) |
| §2(b) r-pred selection is lookahead | confirmed by Joe, §7(5). Superseded by §8 — `final_r_pred` is the replacement trigger |
| the 01:22:20 crossing | **measured**, §3 |

---

## 7. Joe's notes — verbatim, 0803

Reproduced exactly as written, typos included. These cannot be wrong; everything outside them can.

**(1) — on excluding `dirty` lines from the widened re-walk gate**

> no

**(2) — on whether the s4Mage crossing must follow the r-pred**

> s4Mage can't cross itself - it's a single entity.  if your saying "do I have to walk to the next s4Mage cross and dwell after rpred?", the answe r is yes.  be very careful about the dwell code - it needs to stay causal

**(3) — on an IB-dip tolerance, and naming it**

> this is a great question, and I say yes to it. the ideal value should allow the IB excursion between ~02:28 and ~02:40 to trigger "confirmed_ib"

**(4) — on the walk predating the r-pred**

> """ walk, even when it predates the r-pred""" - the walk can absolutely not predate r-pred.  can you see scenarios where it does, or are you just filling the screen space without backing data

**(5) — on the r-pred selection, and the jig mismatch. THE SHOW STOPPER**

> """ only those an exhaustion later selected""" is 100% lookahead bias. however, our overnight causal test on the realtime jig was proven to be causal - there is a mismatch. is your "current" read of r-pred signalling correct?    this is a show stopper until we have a clear path

**(6) — on the slip gate and over/under Moob**

> you haven't given enough data to make a decision. knowing what they both effect would be helpful

> point 6 - don't change anything for now

**(7) — on the pine**

> keep the same pine name - I don't need to re-tool

**(8) — on the r-pred trigger's timeframe**

> does "every r-pred rising edge" mean that RPL will fire each time a higher TF is sewt to r-pred=ture?

**(9) — the `confirmed_ib` value**

> 22

**(10) — on the s15r momo read**

> the issue is in s15r momo. show me the samples that produced a sideways result for s15r

> TV makes it look like a differnet line; I trust your pxs based numbers

**(11) — THE RPL LADDER AND `final_r_pred`. The pre-text, in full**

> in RPL: after the initial setting of `current_tf`, which is set by RPL scanning all TFs in descending order until it finds a TF that is  either a) tested true for r prediction (r-pred), or B) has r in OOB, the code walks the bars.
>
> whenever an r-pred is found in {current_tf+1}, current_tf will become current_tf+1. if current_tf cannot see a r-pred in current_tf+1, and s{current_tf+1}r momo is not tracking towards the bias's OOB, then fire the "final_r_pred" event and delegate to exhv2
>
> --caveat - this is not easy to measure from my side, so we might need to tweak as we test

**(12) — rulings on the 8 `final_r_pred` gaps, 0803**

On the climb term being *r-pred OR OOB, not r-pred alone*:

> --this is the correct version (update in our newspec)

On the momo term and the event not existing yet:

> --yes, it needes to be built in order for RPL to become causal

On `oob_climb` never being cancelled:

> -cancel on final_r_pred

> 2 - keep walking with continuous momo sampling.  if it sidewats before OOB THEN fire the final_r_pred

> 3 - tracking is momo. same mecahnisms as 4 15 22 momo

> 4 - scale with TF

> 5 - """final_r_pred fires later, when the climb stalls.""" - this is the same for the current lookahead regime. the difference you sense is that I added the {current_tf+1} context for you to understand the flow

> 6 - final_r_pred fires once (then cancels, per above)

> 7 - what does the window serve?  I don't know what a "bp50 setup fire bar" does

> 8 - fire final_r_pred if the climb reaches the ceiling. we will deal with these when they show up in the pine emit

---

## 8. `final_r_pred` — the RPL trigger. NOT IMPLEMENTED

Joe's words are §7(11). This section is technical note and can be wrong.

### 8a. Against the existing code

| Joe's step | existing code | |
|---|---|---|
| initial `current_tf` = scan TFs **descending** until r-pred true **OR** r OOB | `build_rplwalk2.seeded_ladder:220` — `si = int(np.flatnonzero(col)[-1])`, a one-bar top-down scan. `rp_matrix:165` — `rp[i] = live \| p['oob_climb'](E[t]['r'])` | **matches exactly** |
| climb when `current_tf+1` participates | `alive = np.logical_and.accumulate(w, axis=0)` — contiguous climb on **r-pred OR OOB** | **matches.** RULED 0803 §7b(1): *"this is the correct version"* — the climb term is r-pred OR OOB, same as the seed |
| stop and fire `final_r_pred` when `current_tf+1` stops participating and its momo goes sideways | **does not exist.** No momentum term in the ladder, no such event. Today the exhaustion marker fires instead — a different mechanic on a different line | **new.** Joe 0803: *"yes, it needes to be built in order for RPL to become causal"* |

- the r-pred term is already a **latch**: set on the predict rising edge, reset by the polarity-matched x/r cross (`fx_bull` = x crosses UNDER r)
- `oob_climb` is **not** cancelled today — *"r sitting out of bounds is a fact, not a prediction"* (`rp_matrix` docstring). **CHANGED 0803 §7b(3): cancel on `final_r_pred`**
- LEAPFROG (TF+2 when TF+1 is quiet) is **BENCHED**, Joe 0729. `current_tf+1` only

### 8b. The rule, as ruled 0803

Per bar, at `current_tf+1`, for one bias:

| state at `current_tf+1` | action |
|---|---|
| r-pred **or** r OOB | **CLIMB** — `current_tf` becomes `current_tf+1` |
| neither, `s{current_tf+1}r` momo reads **`momo`** | **KEEP WALKING** — continuous momo sampling, bar by bar |
| neither, momo reads **`sideways`** before r reaches OOB | **FIRE `final_r_pred`**, delegate to exhv2, then **cancel** |
| `current_tf` = ceiling 120, no TF 121 | **FIRE `final_r_pred`** |

- Joe 0803 §7b(2): *"keep walking with continuous momo sampling. if it sidewats before OOB THEN fire the final_r_pred"*
- Joe 0803 §7b(3): *"tracking is momo. same mecahnisms as 4 15 22 momo"* — `build_exhv2.momo()`, unchanged producer
- Joe 0803 §7b(6): *"final_r_pred fires once (then cancels, per above)"*
- Joe 0803 §7b(8): *"fire final_r_pred if the climb reaches the ceiling. we will deal with these when they show up in the pine emit"*
- Joe 0803 §7b(4): the momo window **scales with TF**

### 8c. Decided, structural

| | decision | why |
|---|---|---|
| "r in OOB" is **bias-directional** | `p['oob_climb'](r)` — bull reads `r >= HI` 85.0, bear reads `r <= LO` 15.0 | every OOB test in `rp_matrix` / `_polar` is already directional. Non-directional would make both biases participate on the same bar |
| `final_r_pred` fires **per bias**, independently | `rp_matrix(bias, ceiling)` is already built per bias | the ladder is two separate structures; a shared event needs a tie-break that does not exist |
| the momo term and the fire rule are **knobs**, not hardcodes | CLI overrides, precedent `REWALK` | Joe 0803: *"we might need to tweak as we test"* |

### 8d. STILL OPEN — 5 concretions

| # | concretion |
|---|---|
| **N1** | **cancel scope.** §7b(3)/(6) say cancel on `final_r_pred`. Cancel **what** — `oob_climb` on the fired rung only, on every TF for that bias, or the whole participation array? And re-arm on what? |
| **N2** | **the momo scaling law.** "Scale with TF" needs an equation. Today `MOMO_STEP_BARS` 60 = 5 min, `MOMO_SAMPLES` 12 → 60 min, applied to s15r and s22r. That is 4.0 TF15 bars but 2.7 TF22 bars — **no single constant is implied by the existing values** |
| **N3** | **which momo states fire.** §7b(2) names `sideways`. `momo()` also returns `curl` and `none`. Do those fire, keep walking, or something else? |
| **N4** | **the walk start bar.** §7b(5) says the later-firing is the same as today. Today exhv2 walks from `es_rpred_ms`, the r-pred episode start. If `final_r_pred` is the delegate but the walk starts at the r-pred, the walk/anchor/signal/exit can all complete **before** the delegate — which is the §2(b) fault in a new place. Arithmetic in §8e |
| **N5** | **the window.** The ladder runs `[g, stop)` where `g` = a bp50 **fire** bar and `stop` = `cap_of`. Joe 0803 §7b(7): *"what does the window serve? I don't know what a 'bp50 setup fire bar' does"* — explanation in §8f, decision outstanding |

### 8e. N4 — the arithmetic, on the §3 row

| event | timestamp |
|---|---|
| r-pred episode start on `cur_tf` s86 | 08-01 **01:26:00** |
| exhv2 walk / anchor / signal | 01:26:15 / 01:27:35 / **01:31:10** |
| exhv2 exit | **02:01:40** |
| r-pred episode **ends** | 08-01 02:42:35 (920 bars = 76.7 min) |
| exhaustion confirmed — today's delegate | 08-01 **04:19:30** |

- the trade is flat at 02:01:40; today's delegate is at 04:19:30. `v2_lead_min` = **−171.92**
- **when `final_r_pred` would fire on this row is UNKNOWN.** It fires when `s{cur_tf+1}r` — here s87 — stops
  participating and its momo reads `sideways`. That is a property of s87, not of s86's r-pred episode, so it
  can land anywhere. Deriving it needs the per-bar ladder, which is a rebuild
- **the causality question is therefore arithmetic, not opinion**: if the walk starts at the r-pred bar but
  the delegate only exists at `final_r_pred`, then any row where `final_r_pred` > the signal bar is
  untradeable — the same §2(b) fault in a new place. If the walk starts at the `final_r_pred` bar, the
  question cannot arise
- **the measurement that settles it**: the distribution of `final_r_pred − signal_bar` across the population.
  It does not exist yet

### 8f. N5 — what the window is, and where it comes from

`build_rplwalk2.applied()`:

```python
for oi, de, ti, tf, br, tev in B._fires(S, int(gts[-1]) + 1):    # bp50 triggers
    fts = int(BP.te[ti])                                          # the FIRE bar
    ...
    stop = B.cap_of(g, 1 if bias == 'bull' else -1)
    cur, seed = seeded_ladder(RPM[bias][0], RPM[bias][1], g, stop)
```

| term | what it is |
|---|---|
| `g` | the bar index of a **bp50 trigger fire** — `BP.trigger()`'s branch A (x-or-m × Mage) or branch B (x × m) cross, after `BP.qualify()` found s4Mage OOB ≥ 240 s **and** hs60x OOB same side |
| `stop` | `B.cap_of` — the **spec'd unlatch**, Joe 0727: *"the setup stays latched until it fires branch a/b, or s60x breaches on opposing oob"* |
| what it serves | `current_tf` is only defined inside `[g, stop)`. The code's own words: *"current_tf exists only relative to a setup"* |

- so today **RPL cannot climb at all** without a bp50 fire to anchor the window
- §7(11) describes RPL as running continuously — *"the code walks the bars"* — with no setup mentioned
- **the decision is whether the ladder stays bounded by bp50 fires, or runs continuously over the tape.** Continuous removes bp50 from the trigger chain entirely

### 8d. Measured — where the current trigger sits

`cur_tf` on all 38 rows of the 0803 rebuild:

| cur_tf | n |
|---|---|
| s120 | **8** |
| s49 · s57 · s89 · s93 · s119 | 2 each |
| s28 · s37 · s42 · s44 · s51 · s52 · s62 · s65 · s66 · s68 · s73 · s74 · s75 · s79 · s81 · s86 · s101 · s109 · s111 · s116 | 1 each |

- range **s28 … s120**. **None** is s4, s15 or s22
- this contradicts `exhv2_spec.md` §2 (*"exhv2 runs on TF ≤ 22 only"*). The standalone s4/s15/s22 `predict_breach` is used **inside** the branch, not as the trigger

r-pred episode starts in `rpl_rpred_0802`, 07-26 → 08-02:

| TF band | episodes in window |
|---|---|
| TF 1–4 | 3,476 |
| TF 5–22 | 3,766 |
| TF 23–60 | 2,719 |
| TF 61–120 | 2,403 |
| **TOTAL** | **12,364** — against **38** evaluated |

- full tape 06-06 21:39 → 08-01 23:59: **99,777** episodes over 120 TFs
- `final_r_pred`'s own count is **unmeasured** — it needs the per-bar `current_tf` array, which is a rebuild
