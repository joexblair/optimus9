# v4nuggies — spec

Named by Joe 1024: *"mechname :v4nuggies"*. His words are quoted verbatim; everything outside a
quote is the build.

## 1. His spec, as handed over

> IF cws1b is oob AND (cws1Mage's extrema is ex 5/95, and has now reversed) AND cws1r is ex-fence
> (r-momo-fence)
> -IF mage cascade's verdict (anchor: ws1Mage extrema) is counter oob-side (ie low-oob, verdict:UP.
> high-oob, verdict:DOWN)
> --walk until g30Mage is IB
> --IF any ws{TF2 to TF10}r is same-side oob
> ---STOP
> --create a rev-trade

Read on his indentation rule — a deeper level nests INSIDE the one above, so `--` under `-` is AND:

| level | the clause |
|---|---|
| 0 | the trigger: three conditions ANDed |
| 1 `-` | AND the mage cascade's verdict is counter to the oob side |
| 2 `--` | the walk, to gcws30Mage ib |
| 2 `--` | the STOP test, a sibling of the walk |
| 3 `---` | STOP, inside that test |
| 2 `--` | the rev-trade, a sibling of the walk |

## 2. THE SIDE

> everything is same side as the cws1b oob. mage cascade is agnostic, it provides only a direction

cws1b's oob side sets the side for every clause. oob is 15/85, always. The cascade is the one
clause read against the side rather than on it — its verdict must be the COUNTER direction.

## 3. The trigger

| the clause | the line | the test | the knob |
|---|---|---|---|
| cws1b is oob | cws1b, closed | `K.oob(v, side)` | `OOB_FNC` 15 → (15, 85) |
| cws1Mage's extrema is ex 5/95 | cws1Mage, closed | `K.past_v4core_mage(ex, side)` | `V4CORE_MAGE_FNC` 5 → (5, 95) |
| cws1r is ex-fence | cws1r, closed | `K.ex_fence(v, side)` | `RMOM_FNC` 80 → (20, 80) |

**The extrema's span.** Joe 1024, asked over what span:

> cws1Mage's extrema over what span:
> -since cws1Mage went oob

So the span opens on the first bar of the cws1Mage oob run on `side` and closes at the lift-off
bar. The extrema is the min over that span on the LOW side, the max on the HIGH side.

**"has now reversed".** Joe 1024: *"reversal detector: -liftoff"*. `jig.lift_off(line, side,
LIFT_PTS 6, K.gap_for(1), LIFT_TOL 2.0, LIFT_WOB 8)` on cws1Mage. The bar it returns is when the
line left its extreme; the bar a consumer may act on is `K.lift_stamp(b)` = `b + LIFT_WOB - 1`,
his standing rule, 35 s later at wob 8.

**"which side?"** Joe 1024: *"which side? cws1b side"* — the cws1r ex-fence test is on the cws1b
oob side.

## 4. The cascade

> cws1Mage is the anchor for mage cascade

`jig.mage_cascade(MG, the extrema bar, zoom, min_lines)`, read AT the cws1Mage extrema bar. That
bar is at or before the lift-off stamp, so reading it at the stamp reads a past bar — causal.

The verdict must be COUNTER to the oob side, which is his own mapping:

| the cws1b oob side | the verdict that passes |
|---|---|
| low | `up` |
| high | `down` |

`verdict` is `'up'`, `'down'` or `'neither'`; `'neither'` does not pass.

## 5. The walk

> g30Mage is shorthand for gcws30Mage. it will need to be mode:closed

`gcws30Mage` is registered in indicator_configs at 30 s, bb 38 / 0.93 / close, value_mode
**emerging**. The closed array was BUILT 1024 by `v4_build_closed.py` as an override on its own
cache key — the DB row is not changed, which is v4core's own precedent for its cws set. Proof of
mode, from that build: the closed array steps on 16.6% of bars, against the emerging array's
69.7%. A 30 s line on the 5 s grid can change on at most 1 bar in 6 = 16.7%.

**IB is the banked reading**: strictly inside the oob fence, `line > OOB_LO and line < OOB_HI`, the
same expression `v4_fast.ib_cross` uses. Both sides, not a same-side test.

**The walk starts at the lift-off stamp** and runs forward to the first gcws30Mage ib cross whose
dwell is proven. If no such cross lands inside the window there is no event.

## 6. The STOP

> your indentation makes it a sibling of the walk, which reads as "at the g30Mage ib bar"
> -this is correct - the STOP is tested when s30Mage is ib

So the test fires ONCE, at the gcws30Mage ib bar, not continuously during the walk.

> ws2–ws10r closed or emerging
> -emerging. if we have poor MAEMFE, we'll test closed mode

ws2r..ws10r, EMERGING, read at the ib bar. Any one of them oob on the cws1b side → STOP, no event.

## 7. The rev-trade

A signal to the router, which owns the fire bar, the direction and the pyramid test. The signal's
side is the cws1b oob side, and that follows from his own cascade mapping rather than from a
choice: low-oob gives verdict `up`, an up verdict opens a LONG, and `v4_signal.direction(-1)` is
`LONG`. So side = the oob side, and the router closes the opposite direction first — his
rev-trade order.

## 8. OPEN — one knob, no value

**The dwell on the gcws30Mage ib cross.** Every banked ib cross must prove a dwell, and each mech
carries its own number — `SAV_IB_XWOB` 2 on ws1r, `LIN_W4_G1_XWOB` 4 on ws1Mage, `SP_XWOB` 18 on a
Mage oob→ib cross, `LIN_IB_DWELL` scaled by TF in lineage. There is no value for v4nuggies.

`v4_sig_nuggies.produce` takes `ib_xwob` as a REQUIRED argument. There is no default anywhere, so
nothing can run on a number Joe has not given.
