# Tape & value hazards

> [o9-live arm-delay spec](./README.md) · **causal / emerging-only**.
> Detail: `../emerging_bar_open.md`, `../arm_drift_rootcause.md`.

## Emerging bar-open sawtooth (`emerging_bar_open.md`)
1-in-5 OOB crossings land on the single bar where the higher-TF bar opens (s5m 19.6% / s5r 20.1% / s6r 19.1%
vs uniform 1.4–1.7% = 12–16× concentration). The line steps **16× harder** there (|step| s5m mean 14.41 at
open vs 0.91 elsewhere) AND those crossings **stick better** (s6r still OOB after 1 min: 85.4% open vs 54.4%
elsewhere) — the whole bar's information in one 5s step, not noise.

Mechanism (`indicator_computer.py:405-433,468-497`): `lookahead_resample`'s forming bar at offset 0 is one 5s
candle (O=H=L=C, ohlc4 = a single tick) while the bar it replaced averaged a full range, and the closed window
rolls the same bar — two step-changes on one bar. **Not fixable by reading closed.**

Worked: Joe's TV 122.8 @20:00 = the bar that *ended* there (= emerging at 19:59:55); 72.96 = the new bar's one
5s candle = what o9-live genuinely holds. Every round-number timestamp in the design sits on a bar open.

Four ways out, all causal, none picked: accept-and-don't-decide-at-open / warm-up-inside-bar / **roll the
window** (define the HTF bar as the 300s ending now — preferred, but changes every line → Joe's call) / put it
in the spec as a first-class event.

## filler-invisible (default ON since 0705)
Line computation uses the event tape (V>0 bars); klinecollect V=0 filler bars are carry-forward; TV omits
fillers. A bgcolor on a filler bar's `time` never paints — snap each event to the last V>0 bar at/before it
(`arm_report.snap`). CHECK the flag's live value before theorising tape contamination.

## ARM-DRIFT is a warmup artifact, not a live bug (`arm_drift_rootcause.md`)
`r`-lines need **~12h** to converge (RSI inside `f_k_lookahead` uses Wilder RMA α=1/rsi_len=1/6;
(5/6)^144=4e-12, 144×5min=12h; BB lines converge in one window). Arms 0–12h from the window head drift (s5r up
to 15.4 pts). **o9-live is unaffected:** its decision bar sits ~14h back (buffer 8h + warmup 6h), accurate to
5e-12; `buffer_hours=12` would double the 2h margin at no signal cost (flagged, Joe's call). The
`recon_arm_daemon` `STABLE_MS=2h` is 6× too small; `_mage_rev` has no step-epsilon (a +1e-15 diff counts as an
up-step) — both Joe's calls (signals belong to Joe; never narrow a monitor).
