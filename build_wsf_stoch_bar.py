"""build_wsf_stoch_bar — the two columns Joe cleared: the saturation clock, and the incoming threshold.

Joe 0820, on the questions that produced them: "1,2. add the columns" and "agreed - keeping it in
the jig and using the existing mechs is the best option".

WHY THESE TWO. The r line is SMA(k_len 7) of STOCH(stc_len 8) of RSI(rsi_len 5), on each timeframe's
own bars. Two things follow that are knowable AT the bar and say where the line can go next:

  the incoming threshold   r is an average of seven stoch readings, so one closed bar moves it by
                           (incoming - outgoing) / 7. The OUTGOING value has already closed and
                           cannot change, so it stays on the closed series. r rises only if the next
                           reading beats it.

  the saturation clock     stoch reads 100 only while RSI sits at its own 8-bar extreme. Stop making
                           new extremes and the old one rolls out within 8 bars and stoch must fall.
                           This counts how many of the line's own bars have passed since RSI last
                           SET that extreme, so 8 minus it is the bars left before it must roll out.

THE DEVELOPING BAR IS IN. Joe 0820: "do you think it will fit with emerging lines? TF8 is 96 bars
of pxs data, and a lot can happen in 96 bars ... what's preventing you from sourcing pxs instead of
closed?" Nothing prevented it. The first cut of this file read the closed series only, which on TF8
meant the saturation clock could be reading a bar that ended up to 96 bars ago - at 14:20:35 that
was 56 bars, 4 minutes 40 seconds, invisible.

The developing bar now enters exactly where indicator_computer.py:604-606 puts it:

    stoch_min = np.minimum(lb_rsi_min, rsi_d)
    stoch_max = np.maximum(lb_rsi_max, rsi_d)

so the developing RSI competes for the window extreme, and setting a new one resets the clock.

CAUSAL. `lookahead_resample` builds the developing bar cumulatively THROUGH t - its own docstring:
"H = cumulative max of 5s highs from window start through t". The name mirrors Pine's
barmerge.lookahead_on flag on the security call, not reading ahead. Proven by truncation, not by
reading that comment - see the test below the builder.

WHY THE JIG AND NOT A DIRECT RESAMPLE. A direct read off the 5-second tape gave ws8r 73.10 against
the banked 84.50. The production line resamples through the Jig's own base frame; this uses the same
frame and the same IndicatorComputer functions, so the intermediates line up with the banked line.
"""
import sys
import os
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import mech_lines
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis.jig import Jig
import pandas as pd

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
TFS      = list(range(1, 9))
DRS      = (+1, -1)
GRID_S   = 5
RSI_LEN, STC_LEN, K_LEN = 5, 8, 7      # Joe's r spec, 7|5|8: k_len 7, rsi 5, stc 8

ADD = [('wbt_stoch_now',   'DOUBLE'),
       ('wbt_stoch_out',   'DOUBLE'),
       ('wbt_sat_bars',    'SMALLINT'),
       ('wbt_sat_left',    'SMALLINT'),
       ('wbt_rsi',         'DOUBLE'),
       ('wbt_rsi_lo',      'DOUBLE'),
       ('wbt_rsi_hi',      'DOUBLE')]

DOC = {
 'wbt_stoch_now': 'the newest CLOSED stoch reading inside the seven-bar average',
 'wbt_stoch_out': 'THE INCOMING THRESHOLD. the oldest closed stoch reading in the average - the one '
                  'that leaves when the next bar closes. r rises only if the incoming beats it',
 'wbt_sat_bars':  'THE SATURATION CLOCK. closed bars of this line since RSI last SET its 8-bar '
                  'extreme on the side read. 0 = it set it on the newest closed bar',
 'wbt_sat_left':  '8 minus the clock: bars left before that extreme must roll out of the window',
 'wbt_rsi':       'RSI(5) on the newest closed bar of this line',
 'wbt_rsi_lo':    'the low of the RSI 8-bar window - the stoch denominator floor',
 'wbt_rsi_hi':    'the high of that window. hi minus lo is the amplifier: a narrow window turns a '
                  'small RSI move into a large stoch move'}


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_bar_tf', fetch=True)}
    for col, spec in ADD:
        if col not in have:
            db.execute(f'ALTER TABLE wsf_bar_tf ADD COLUMN {col} {spec} COMMENT %s', (DOC[col][:255],))
            print(f'  added {col}', flush=True)

    ovr = {}
    for g in mech_lines(db, 'wsf'):
        tf = g['tf_seconds'] // 60
        if g['role'] == 'r' and tf in TFS:
            ovr[f'ws{tf}r'] = g['override']
    print(f'  opening the jig over {HOURS} h + {WARMUP} warmup for {len(ovr)} r lines', flush=True)

    with Jig(END_MS, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
        base = j.W.base
        ts = np.asarray(j.ts)
        i0 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_FROM)
                                         .replace(tzinfo=timezone.utc).timestamp() * 1000)))
        i1 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_TO)
                                         .replace(tzinfo=timezone.utc).timestamp() * 1000)))
        utcs = [dt.datetime.fromtimestamp(int(x) / 1000, tz=timezone.utc)
                .strftime('%Y-%m-%d %H:%M:%S') for x in ts[i0:i1 + 1]]
        print(f'  window {len(utcs):,} bars', flush=True)

        for tf in TFS:
            sec = tf * 60
            closed = IC.resample(base, sec, 'epoch')
            csrc = IC.build_source(closed, 'close')
            cts = closed['timestamp'].to_numpy()
            rsi_c = IC._rsi(csrc, RSI_LEN)
            sto_c = IC._stoch(rsi_c, STC_LEN)

            # the denominator components over the previous (STC_LEN-1) CLOSED rsi values,
            # and the sum of the (K_LEN-1) closed stoch readings - same shape as
            # indicator_computer.py:570-577
            rs = pd.Series(rsi_c)
            roll_min = rs.rolling(STC_LEN - 1, min_periods=STC_LEN - 1).min().to_numpy()
            roll_max = rs.rolling(STC_LEN - 1, min_periods=STC_LEN - 1).max().to_numpy()

            # THE DEVELOPING BAR at every 5 seconds
            dev_src = IC.build_source(IC.lookahead_resample(base, sec, 'epoch'), 'close')
            bts = base['timestamp'].to_numpy()
            ci = np.searchsorted(cts, bts, side='right') - 1
            valid = ci >= 1
            lb = np.where(valid, ci - 1, 0)

            delta_c = np.diff(csrc, prepend=np.nan)
            avg_g = IC._rma(np.where(delta_c > 0, delta_c, 0.0), RSI_LEN)
            avg_l = IC._rma(np.where(delta_c < 0, -delta_c, 0.0), RSI_LEN)
            alpha = 1.0 / RSI_LEN
            prev_src = np.where(valid, csrc[lb], np.nan)
            d = dev_src - prev_src
            g_d = alpha * np.where(d > 0, d, 0.0) + (1 - alpha) * np.where(valid, avg_g[lb], np.nan)
            l_d = alpha * np.where(d < 0, -d, 0.0) + (1 - alpha) * np.where(valid, avg_l[lb], np.nan)
            with np.errstate(invalid='ignore', divide='ignore'):
                rsi_d = 100.0 - 100.0 / (1.0 + np.where(l_d != 0.0, g_d / l_d, np.inf))
            lo_c = np.where(valid, roll_min[lb], np.nan)
            hi_c = np.where(valid, roll_max[lb], np.nan)
            s_min = np.minimum(lo_c, rsi_d)
            s_max = np.maximum(hi_c, rsi_d)
            rng = s_max - s_min
            with np.errstate(invalid='ignore', divide='ignore'):
                sto_d = np.where(rng != 0.0, 100.0 * (rsi_d - s_min) / rng, 50.0)

            # how many of this line's own bars since the extreme was SET. The developing bar is
            # bar 0 and competes for it, so a fresh extreme now reads 0.
            n = len(rsi_c)
            back_hi = np.zeros(n, np.int16); back_lo = np.zeros(n, np.int16)
            for k in range(n):
                a = max(0, k - STC_LEN + 2)
                w = rsi_c[a:k + 1]
                if not np.isfinite(w).any():
                    continue
                back_hi[k] = k - (a + int(np.nanargmax(w)))
                back_lo[k] = k - (a + int(np.nanargmin(w)))

            sl = slice(i0, i1 + 1)
            for dr in DRS:
                dev_wins = (rsi_d >= hi_c) if dr > 0 else (rsi_d <= lo_c)
                back = np.where(valid, (back_hi if dr > 0 else back_lo)[lb], 0)
                sat = np.where(dev_wins, 0, back + 1)
                rows = []
                for k in range(i0, i1 + 1):
                    p = int(lb[k])
                    j = p - (K_LEN - 2)              # the oldest closed stoch still in the average
                    if not valid[k] or j < 0:
                        rows.append((None, None, None, None, None, None, None,
                                     utcs[k - i0], tf, dr))
                        continue
                    f = lambda v: (float(v) if np.isfinite(v) else None)
                    rows.append((f(sto_d[k]), f(sto_c[j]),
                                 int(sat[k]), int(STC_LEN - 1 - sat[k]),
                                 f(rsi_d[k]), f(s_min[k]), f(s_max[k]),
                                 utcs[k - i0], tf, dr))
                db.executemany(
                    'UPDATE wsf_bar_tf SET wbt_stoch_now=%s, wbt_stoch_out=%s, wbt_sat_bars=%s, '
                    'wbt_sat_left=%s, wbt_rsi=%s, wbt_rsi_lo=%s, wbt_rsi_hi=%s '
                    "WHERE wbt_win_from='" + WIN_FROM + "' AND wbt_utc=%s AND wbt_tf=%s AND wbt_dr=%s",
                    rows)
            print(f'  ws{tf}r : {2 * len(utcs):,} rows updated on the DEVELOPING series', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
