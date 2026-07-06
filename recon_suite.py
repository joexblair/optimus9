"""recon_suite.py — o9-live <-> backtest reconcile hypothesis battery (Joe 0707).

Backtest = source of truth (v2_cascade, the v2_walk_ad chain). o9-live is audited against it: for every live
arm/s3s4_gate event in o9_state_log, faithfully REPRODUCE o9-live's own per-bar computation offline and check the
backtest agrees. o9-live is stateless (runs the backtest producer on a window ending at the decision instant, reads
bar T) -> a faithful offline repro of that bar IS what o9-live should have emitted.

THE LOAD-BEARING FIX (0707): the live decision logged kline_ms = now_ms = bar_open + 5301 (bar 5000 + delay 301).
At live time the tape's newest row was the JUST-CLOSED bar (the forming bar isn't stored yet). Offline the tape has
advanced, so window(kline_ms) lands one bar too far forward (a one-bar look-ahead). Reproduce at now_ms = K - BAR so
W.ts[-1] == the bar o9-live actually decided on (K - 5301). Validated: 0.00000 line diff across all 19 lines.

Run:  python3 recon_suite.py [N]        # audit the last N live arm/gate events (default 20)
      python3 recon_suite.py K <kline_ms>   # audit one specific event
Each event -> a battery of PASS/FAIL hypotheses + an aggregate scoreboard (matched / o9-spurious / bt-extra).
"""
import subprocess
import sys
import time

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.strategy import StrategyLoop

SYM = "FARTCOINUSDT"
BAR = 5000
DELAY = 301                         # seam grace; decision instant = bar_open + BAR + DELAY
LINE_EPS = 0.05                     # line-fidelity tolerance (rounding is 4dp; 0.05 is generous)
STATES = ("arm", "s3s4_gate")


def _utc(ms):
    return time.strftime("%H:%M:%S", time.gmtime(int(ms) / 1000))


class Repro:
    """Faithfully reproduce o9-live's per-bar state for a live event at kline_ms K (SRP: build the window o9-live
    saw, expose bar T + mech_events + line values). now_ms = K - BAR undoes the offline forward-tape look-ahead."""

    def __init__(self, dev, strat):
        self.dev = dev
        self.strat = strat

    def at(self, K):
        W = self.strat.window(int(K) - BAR)          # one bar back -> W.ts[-1] == o9-live's decision bar (K-5301)
        T = len(W.ts) - 1
        return W, T

    def events(self, W):
        return self.strat.mech_events(W)             # [(state, side, meta)] at T — what o9-live should have logged

    @staticmethod
    def line_at(W, T, ln):
        try:
            return round(float(W.line(ln)[T]), 4)
        except Exception:
            return None


# ---- hypotheses: each takes (o9_event_row, snapshot, W, T, bt_events) -> (name, verdict_bool_or_None, detail) ----

def h_bar_align(r, snap, W, T, bt):
    exp = int(r["kline_ms"]) - BAR - DELAY
    return ("bar_align", int(W.ts[T]) == exp, "W.ts[T]=%d expected=%d" % (int(W.ts[T]), exp))


def h_line_fidelity(r, snap, W, T, bt):
    ds = [(ln, abs(v - Repro.line_at(W, T, ln))) for ln, v in snap.items()
          if Repro.line_at(W, T, ln) is not None]
    if not ds:
        return ("line_fidelity", None, "no line snapshot")
    worst = max(ds, key=lambda x: x[1])
    return ("line_fidelity", worst[1] < LINE_EPS, "max |diff|=%.5f on %s" % (worst[1], worst[0]))


def h_event_reproduced(r, snap, W, T, bt):
    want = (r["state"], int(r["es"]), r["meta"])
    got = any(e[0] == r["state"] and int(e[1]) == int(r["es"]) and (e[2] or None) == (r["meta"] or None) for e in bt)
    return ("event_reproduced", got, "o9=%s | bt@T=%s" % (str(want), bt))


def h_bt_extra(r, snap, W, T, bt):
    """Backtest events at this bar that the o9 row didn't carry (e.g. stale_exit alongside arm) — informational."""
    extra = [e for e in bt if e[0] not in STATES]         # non-audited producer events co-emitted at T
    return ("bt_extra_events", None, str(extra) if extra else "none")


def h_double_log(r, snap, W, T, bt, o9=None):
    n = o9.execute("SELECT COUNT(*) c FROM o9_state_log WHERE state=%s AND kline_ms=%s",
                   (r["state"], int(r["kline_ms"])), fetch=True)[0]["c"]
    return ("double_log", n == 1, "%d rows at this (state,kline_ms)" % n)


def h_lag(r, snap, W, T, bt, o9=None):
    row = o9.execute("SELECT MIN(created_ms) mn FROM o9_state_log WHERE state=%s AND kline_ms=%s",
                     (r["state"], int(r["kline_ms"])), fetch=True)[0]
    lag = (int(row["mn"]) - int(r["kline_ms"])) / 1000.0
    return ("emit_lag", 0 <= lag < 15, "%.1fs after decision instant" % lag)


def process_singleton():
    out = subprocess.run(["pgrep", "-f", "run_o9live.py"], capture_output=True, text=True).stdout.split()
    n = len(out)
    return ("loop_singleton", n <= 1, "%d run_o9live processes alive" % n)


def audit_event(dev, o9, repro, r):
    K = int(r["kline_ms"])
    snap = {x["line"]: float(x["val"]) for x in
            o9.execute("SELECT line,val FROM o9_state_log_line WHERE sl_id=%s", (int(r["sl_id"]),), fetch=True)}
    W, T = repro.at(K)
    bt = repro.events(W)
    results = [h_bar_align(r, snap, W, T, bt), h_line_fidelity(r, snap, W, T, bt),
               h_event_reproduced(r, snap, W, T, bt), h_bt_extra(r, snap, W, T, bt),
               h_double_log(r, snap, W, T, bt, o9=o9), h_lag(r, snap, W, T, bt, o9=o9)]
    return bt, results


def main():
    args = sys.argv[1:]
    dev = DatabaseManager(**get_db_config()); dev.connect()
    o9c = get_db_config(); o9c["database"] = "o9_live"; o9 = DatabaseManager(**o9c); o9.connect()
    strat = StrategyLoop(dev, bm.BiasConfig(**BASE_BIAS), lr_config(dev), SYM, buffer_hours=8, warmup_hours=6)
    repro = Repro(dev, strat)

    if args and args[0] == "K":
        rows = o9.execute("SELECT MIN(sl_id) sl_id,kline_ms,state,es,meta FROM o9_state_log WHERE kline_ms=%s AND "
                          "state IN ('arm','s3s4_gate') GROUP BY kline_ms,state,es,meta ORDER BY kline_ms",
                          (int(args[1]),), fetch=True)
    else:
        n = int(args[0]) if args else 20
        rows = o9.execute("SELECT MIN(sl_id) sl_id,kline_ms,state,es,meta FROM o9_state_log WHERE state IN "
                          "('arm','s3s4_gate') GROUP BY kline_ms,state,es,meta ORDER BY MIN(sl_id) DESC LIMIT %s",
                          (n,), fetch=True)
        rows = list(reversed(rows))

    env = process_singleton()
    print("[recon_suite] %s: %s   (auditing %d events, backtest=truth)" % (env[0], env[2], len(rows)))
    tally = {"matched": 0, "o9_spurious": 0, "fidelity_fail": 0}
    for r in rows:
        bt, results = audit_event(dev, o9, repro, r)
        flags = "  ".join("%s=%s" % (nm, "OK" if v else ("--" if v is None else "FAIL")) for nm, v, _ in results)
        det = next(d for nm, v, d in results if nm == "event_reproduced")
        fid = next(v for nm, v, d in results if nm == "line_fidelity")
        rep = next(v for nm, v, d in results if nm == "event_reproduced")
        tag = "MATCH" if rep else ("O9-SPURIOUS" if fid else "FIDELITY?")
        tally["matched" if rep else ("fidelity_fail" if fid is False else "o9_spurious")] += 1
        print("%s %-11s %-9s es=%+d %-6s | %s" % (
            _utc(int(r["kline_ms"])), r["state"], tag, int(r["es"]), r["meta"] or "", flags))
    print("SCOREBOARD: matched=%d  o9_spurious=%d  fidelity_fail=%d  of %d" % (
        tally["matched"], tally["o9_spurious"], tally["fidelity_fail"], len(rows)))


if __name__ == "__main__":
    main()
