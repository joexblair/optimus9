# The emerging line's bar-open sawtooth (0710)

`[measured]` 24 h of 5-second bars, every bar tagged by its offset inside its own higher-TF bar.

```
             |step| at the TF bar open     |step| elsewhere
s5m          mean 14.41   p90 31.17        mean 0.91   p90 2.22
s5r          mean  9.72   p90 19.73        mean 0.68   p90 1.98
s6r          mean  9.56   p90 19.83        mean 0.63   p90 1.86
s7r          mean  9.63   p90 19.80        mean 0.59   p90 1.71
```

The emerging line moves **16× harder** on the one bar where its higher-TF bar opens.

```
line   OOB crossings   at the TF bar open   uniform would be
s5m         1436         282  (19.6%)            1.7%
s5r         1038         209  (20.1%)            1.7%
s6r          930         178  (19.1%)            1.4%
s7r          993         152  (15.3%)            1.2%
```

**One in five out-of-bounds crossings happens on that single bar.**

## They are not noise

```
                            still OOB after:   5s     30s     60s    5min
s5m   crossings at the open                  95.7%   85.1%   81.6%   60.3%
      crossings elsewhere                    79.1%   65.0%   61.0%   52.3%
s5r   crossings at the open                  93.3%   85.2%   78.5%   59.3%
      crossings elsewhere                    73.0%   60.9%   55.7%   33.3%
s6r   crossings at the open                  94.9%   88.2%   85.4%   72.5%
      crossings elsewhere                    75.7%   59.6%   54.4%   31.0%
s7r   crossings at the open                  98.0%   90.1%   84.9%   70.4%
      crossings elsewhere                    76.0%   58.9%   53.6%   35.3%
```

A crossing at the bar open is roughly **twice as likely** to still hold five minutes later. Discarding
them would throw away the most informative bars on the board.

## The mechanism

`[read]` `indicator_computer.lookahead_resample` (:405) builds the forming bar as `O = first 5s open`,
`H = running max`, `L = running min`, `C = current close`. `f_bb_lookahead` (:468) combines
`length - 1` closed source values with that one developing value.

At offset 0 the forming bar is a **single 5-second candle**, so `O = H = L = C` and its `ohlc4` is one
tick. The bar it replaced was a mature 5-minute bar whose `ohlc4` averaged a full range. On the same
bar the closed window rolls and the just-finished bar enters the Bollinger history.

Two step-changes at once. Worked example, `s5m = 8|0.65|ohlc4`, 2026-07-08:

```
  19:59:30   123.17
  19:59:45   121.37
  20:00:00    72.96   <-- 5m bar open, one 5s candle in the forming bar
  20:00:15    71.24
  20:01:45    87.77
  20:02:00    89.41
```

TradingView's **closed** value at 20:00 is `122.8` — the bar that *ended* there, which our emerging line
reads at 19:59:55. Both are right; they describe different bars. `72.96` is what o9-live holds at
20:00:00. It is not a backtest artefact, and reading `closed` instead is the look-ahead that voided the
live account (`project_v2_lookahead`).

## Four options, none chosen

1. **Accept and avoid** — no decisions in the first `M` bars of a higher-TF bar. Costs the best bars.
2. **Warm up inside the bar** — hold the previous closed bar as the newest window element until the
   forming bar has `M` five-second bars of its own. One knob, sweepable, causal.
3. **Roll the window** — for each 5-second bar, the higher-TF bar is the `target_seconds` *ending now*,
   its predecessors the `target_seconds` before that. No bar opens, no sawtooth, strictly causal.
   Changes every line on the board.
4. **Put the sawtooth in the spec** — treat "the line jumped at the bar open" as a first-class event.

Every timestamp in the arm-delay work that landed on a round boundary (`06:01:00` on TF19, `20:00:00`
and `18:45:00` on TF5, `05:10:00`/`05:15:00` on TF5) sits on a bar open. Read those with this in hand.
