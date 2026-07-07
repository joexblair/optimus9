"""arm_gate_emit.py — modular pine (5s chart): causal-arm-delay arms = WHITE bgcolor, s3s4 gate opens = GREEN
bgcolor (Joe 0707). Leverages lp_cascade_emit's array-bgcolor pattern (array.from + binary_search, function-wrapped
for TV's op-limit).

Arm = the validated candidate: arm-line s5m (len8 = the DB default), PREDICTED by s10r (predict_breach) while s5m OOB
-> DELAY to where s10r reverses (_mage_rev wob8); else s5m breach. Gate = s3s4 gate_open (reasons a/b/c), standard
dial-in. Both causal/emerging. Window = last WINDOW_DAYS ending now. Only override = s10r (not in DB).
  python3 arm_gate_emit.py
"""
import sys; sys.path.insert(0, "/home/joe/thecodes")
import time, datetime as dtm
from datetime import timezone
import numpy as np

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from optimus9.analysis.lr_v2 import _mage_rev, v2_arm, gate_open

WINDOW_DAYS = 3
WOB = 8
def d5(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%m-%d")


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    now = int(time.time() * 1000)
    ovr = {"s10r": (600, ("k", 6, 6, 5, "close"), "emerging")}        # the only non-DB line
    W = bm.BiasWindow(dev, now, lookback=WINDOW_DAYS * 24 + 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS),
                      line_overrides=ovr)
    ts = np.asarray(W.ts); n = len(ts); cutoff = now - WINDOW_DAYS * 86400000

    # --- ARM events (candidate: s5m arm, predict s10r, delay to r-reversal wob8) ---
    m = np.asarray(W.line("s5m"), float); M = np.asarray(W.line("s5M"), float); r = np.asarray(W.line("s10r"), float)
    pred = predict_breach(r, m, M, HI, LO, FENCE_HI, FENCE_LO); rrev = np.asarray(_mage_rev(r, WOB))
    msign = np.where(m >= HI, 1, np.where(m <= LO, -1, 0))
    arms = [(i, int(msign[i])) for i in range(1, n) if msign[i] != 0 and msign[i] != msign[i - 1]]
    arm_ts = []
    for b, es in arms:
        e = next((k for k in range(b + 1, n) if msign[k] != es), n)
        anchor = b
        pf = next((k for k in range(b, e) if pred[k] == es), None)
        if pf is not None:
            rk = next((k for k in range(pf, e) if rrev[k] == -es), None)
            if rk is not None:
                anchor = rk
        if int(ts[anchor]) >= cutoff:
            arm_ts.append(int(ts[anchor]))                            # pine `time` is ms (lp_cascade pattern)

    # --- s3s4 GATE opens, split by direction (es=-1 long/green · es=+1 short/red; ledger ground truth) ---
    gates = gate_open(W, lr_config(dev), v2_arm(W, lr_config(dev)))
    gate_long = sorted({int(ts[ok]) for (i, es, bd, ok, rsn, cap) in gates if int(ts[ok]) >= cutoff and es == -1})
    gate_short = sorted({int(ts[ok]) for (i, es, bd, ok, rsn, cap) in gates if int(ts[ok]) >= cutoff and es == 1})
    arm_ts = sorted(set(arm_ts))
    dev.disconnect()

    # --- emit (array.binary_search on 5s time; function-wrapped for TV op-limit) — lp_cascade_emit pattern ---
    arr = lambda v: ("array.from(" + ", ".join(map(str, v)) + ")") if v else "array.new_int(0)"

    def emit_arr(nm, vals):
        if len(vals) <= 400:
            return "f_%s() =>\n    %s" % (nm, arr(vals)), "%s = f_%s()" % (nm, nm)
        chunks = [vals[i:i + 400] for i in range(0, len(vals), 400)]
        d = "\n".join("f_%s_%d() =>\n    %s" % (nm, i, arr(c)) for i, c in enumerate(chunks))
        d += "\nf_%s() =>\n    a = f_%s_0()\n" % (nm, nm)
        d += "".join("    array.concat(a, f_%s_%d())\n" % (nm, i) for i in range(1, len(chunks)))
        d += "    a"
        return d, "%s = f_%s()" % (nm, nm)

    pairs = [emit_arr("armA", arm_ts), emit_arr("gateL", gate_long), emit_arr("gateS", gate_short)]
    defs = "\n".join(p[0] for p in pairs); calls = "\n".join(p[1] for p in pairs)
    body = f'''//@version=5
indicator("arm+s3s4 gate ({d5(cutoff)}→{d5(now)})  white=arm  green=gate long  red=gate short", overlay = true)
showArm  = input.bool(true, "arm (white bg)")
showGate = input.bool(true, "s3s4 gate open (green long / red short)")
// arm = s5m armed, predicted by s10r, delayed to r-reversal (wob {WOB}). gate = s3s4 open (a/b/c), es-directional.
{defs}
{calls}
bg = color(na)
if showArm and array.binary_search(armA, time) >= 0
    bg := color.new(color.white, 0)
if showGate and array.binary_search(gateL, time) >= 0
    bg := color.new(color.green, 0)       // gate long — priority over arm
if showGate and array.binary_search(gateS, time) >= 0
    bg := color.new(color.red, 0)         // gate short
bgcolor(bg)
'''
    path = "/home/joe/thecodes/arm_gate.pine"
    open(path, "w").write(body)
    print("arms=%d  gate_long=%d  gate_short=%d  (last %dd) -> %s" % (
        len(arm_ts), len(gate_long), len(gate_short), WINDOW_DAYS, path))


if __name__ == "__main__":
    main()
