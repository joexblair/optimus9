"""recon_arm_daemon.py — arm-event recon: are the klines stable, and does the backtest still agree? (Joe 0709)

On every new o9-live `arm` event it writes one row to `o9_recon`:
    armevent_ts, kline_close_ts, es, meta, price
    <line>_open  = the line's value at the PREVIOUS bar's close   (i.e. this bar's open)
    <line>_close = the line's value at THIS bar's close
for every line in the strategy. Two samples per bar, two free dimensions (Joe: "always try to add more free
dimensions when testing, you never know what you'll find").

Then it RECONCILES the previous row: rebuild that bar's window from the klines as they are NOW and recompute
every line. The window is pinned to end at the SAME bar, so window growth cannot confound the comparison —
any difference is the TAPE changing underneath us (late ticks, a sanitiser overwrite, a backfill).

It also snapshots the backtest arm set each pass and reports arms that APPEARED or DISAPPEARED since the last
wake. After the causal arm_delay (a breach is never an arm; the s5m reversal is the trigger; the big leg
postpones it) an arm must NEVER disappear — the machine is window-invariant. A disappearing arm means
something still reads the future.

Writes discrepancies to stdout prefixed DISCREPANCY / ARM-DRIFT so a grep-based monitor can wake on them.
Run:  python3 recon_arm_daemon.py
"""
import datetime as dtm
import sys
import time
from datetime import timezone

import numpy as np

import bias_machine as bm
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import arm_delay, v2_arm
from optimus9.config import get_db_config
from sweep_eval import BASE_BIAS

BAR = 5000
LB_H, WM_H = 14, 6                      # window: 14h lookback / 6h warmup (live loop's floors + margin)
POLL_S = 20
TOL = 1e-9                              # bit-comparison; the tape either changed or it did not

LINES = ('s2m', 's2M', 's2r', 's3m', 's3M', 's3r', 's4m', 's4M', 's4r', 's5m', 's5M', 's5r',
         's7m', 's7M', 's7r', 's15m', 's15M', 's15r', 's30m', 's30M', 's30r')


def col(line):
    """MySQL identifiers are case-INSENSITIVE: `s2m_open` and `s2M_open` collide. The uppercase M is the
    Mage line, so spell it out — s2M -> s2Mage_open/close, s2m -> s2m_open/close."""
    return line[:-1] + 'Mage' if line.endswith('M') else line

f = lambda m: dtm.datetime.fromtimestamp(m / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')
log = lambda *a: (print(*a, flush=True))


def ddl():
    cols = ",\n  ".join("`%s_open` DOUBLE NULL,\n  `%s_close` DOUBLE NULL" % (col(n), col(n)) for n in LINES)
    return """CREATE TABLE IF NOT EXISTS o9_recon (
  recon_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
  armevent_ts   BIGINT NOT NULL,
  kline_close_ts BIGINT NOT NULL,
  es            TINYINT NULL,
  meta          VARCHAR(16) NULL,
  price         DECIMAL(20,8) NULL,
  %s,
  recon_status  VARCHAR(16) NULL,
  recon_maxdiff DOUBLE NULL,
  recon_worst   VARCHAR(24) NULL,
  created_ms    BIGINT NOT NULL,
  UNIQUE KEY uq_arm (armevent_ts, es)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""" % cols


def window_at(dev, bar_ms, cfg):
    """A window ending exactly at `bar_ms` — the same edge the live loop had (driver: now = ts + bar + delay)."""
    return bm.BiasWindow(dev, bar_ms + BAR + 700, lookback=LB_H, warmup=WM_H, cfg=cfg, lean=True)


def sample(W):
    """-> {line: (open_v, close_v)}; close = value at the last bar, open = value at the bar before it."""
    out = {}
    for n in LINES:
        v = np.asarray(W.line(n), float)
        out[n] = (float(v[-2]) if len(v) > 1 else float('nan'), float(v[-1]))
    return out


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    c = get_db_config(); c['database'] = 'o9_live'; o9 = DatabaseManager(**c); o9.connect()
    o9.execute(ddl())
    cfg = bm.BiasConfig(**BASE_BIAS)
    log("recon daemon up · lines=%d · poll=%ds · window=%dh/%dh" % (len(LINES), POLL_S, LB_H, WM_H))

    seen = {r['armevent_ts'] for r in (o9.execute("SELECT armevent_ts FROM o9_recon", fetch=True) or [])}
    prev_arms, last_recon = None, None

    while True:
        try:
            rows = o9.execute(
                "SELECT kline_ms, es, meta, price FROM o9_state_log WHERE state='arm' ORDER BY kline_ms", fetch=True) or []
            for r in rows:
                bar = int(r['kline_ms']) // BAR * BAR - BAR          # decision instant -> the bar acted on
                if bar in seen:
                    continue
                W = window_at(dev, bar, cfg)
                if int(np.asarray(W.ts)[-1]) != bar:
                    log("SKIP %s — window edge %s != arm bar" % (f(bar), f(int(np.asarray(W.ts)[-1]))))
                    continue
                s = sample(W)
                cols = ['armevent_ts', 'kline_close_ts', 'es', 'meta', 'price', 'created_ms']
                vals = [bar, bar + BAR, int(r['es'] or 0), r['meta'], r['price'], int(time.time() * 1000)]
                for n in LINES:
                    cols += ['%s_open' % col(n), '%s_close' % col(n)]; vals += [s[n][0], s[n][1]]
                o9.execute("INSERT IGNORE INTO o9_recon (%s) VALUES (%s)"
                           % (",".join("`%s`" % x for x in cols), ",".join(["%s"] * len(cols))), tuple(vals))
                seen.add(bar); last_recon = bar
                log("ARM %s es=%+d %s  -> recon row written" % (f(bar), int(r['es'] or 0), r['meta']))

            # ── recon the last row against the klines AS THEY ARE NOW ────────
            if last_recon is not None:
                row = (o9.execute("SELECT * FROM o9_recon WHERE armevent_ts=%s", (last_recon,), fetch=True) or [None])[0]
                if row and row.get('recon_status') is None:
                    W = window_at(dev, last_recon, cfg)
                    if int(np.asarray(W.ts)[-1]) == last_recon:
                        s = sample(W)
                        worst, md = None, 0.0
                        for n in LINES:
                            for k, i in (('open', 0), ('close', 1)):
                                a, b = row['%s_%s' % (col(n), k)], s[n][i]
                                if a is None or (a != a and b != b):
                                    continue
                                d = abs(float(a) - float(b))
                                if d > md:
                                    md, worst = d, '%s_%s' % (col(n), k)
                        st = 'CLEAN' if md <= TOL else 'DRIFT'
                        o9.execute("UPDATE o9_recon SET recon_status=%s, recon_maxdiff=%s, recon_worst=%s WHERE armevent_ts=%s",
                                   (st, md, worst, last_recon))
                        if st == 'DRIFT':
                            log("DISCREPANCY %s  maxdiff=%.9g on %s — the tape moved under a closed bar" % (f(last_recon), md, worst))
                        else:
                            log("recon %s CLEAN (maxdiff=%.3g)" % (f(last_recon), md))
                        last_recon = None

            # ── backtest arm drift since the last wake ───────────────────────
            now = int(time.time() * 1000)
            W = bm.BiasWindow(dev, now, lookback=LB_H, warmup=WM_H, cfg=cfg, lean=True)
            lr = lr_config(dev)
            ts = np.asarray(W.ts)
            arms = {int(ts[a[0]]) for a in arm_delay(W, lr, v2_arm(W, lr))}
            if prev_arms is not None:
                gone = sorted(a for a in prev_arms - arms if a >= int(ts[0]))
                new = sorted(arms - prev_arms)
                if gone:
                    log("ARM-DRIFT %d arm(s) DISAPPEARED (window-invariance broken): %s"
                        % (len(gone), [f(x) for x in gone[:5]]))
                if new:
                    log("arms appeared: %s" % [f(x) for x in new[:5]])
            prev_arms = arms
        except Exception as e:                                       # a daemon must not die on one bad pass
            log("ERROR %s: %s" % (type(e).__name__, e))
        time.sleep(POLL_S)


if __name__ == "__main__":
    sys.exit(main())
