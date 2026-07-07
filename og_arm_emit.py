"""og_arm_emit.py — modular pine (5s chart): the OG s5m-breach arm as bgcolor. yellow=long (es=-1), blue=short
(es=+1). Raw s5m OOB breach only (no r-predict, no delay, no cap) — the "s5m breaches -> ARMED" spec, causal.
Leverages lp_cascade_emit's array-bgcolor pattern. Lines on the event tape (filler_invisible via DB default).
Window = last WINDOW_DAYS. Run:  python3 og_arm_emit.py
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

WINDOW_DAYS = 3
def d5(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%m-%d")


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    now = int(time.time() * 1000)
    W = bm.BiasWindow(dev, now, lookback=WINDOW_DAYS * 24 + 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS))
    ts = np.asarray(W.ts); n = len(ts); cutoff = now - WINDOW_DAYS * 86400000
    m = np.asarray(W.line("s5m"), float)
    dev.disconnect()
    sign = np.where(m >= HI, 1, np.where(m <= LO, -1, 0))
    # OG s5m breach: OOB cross (sign flip). es = breach side. long=es-1 (breach low), short=es+1 (breach high).
    og_long = sorted(int(ts[i]) for i in range(1, n)
                     if sign[i] == -1 and sign[i] != sign[i - 1] and int(ts[i]) >= cutoff)
    og_short = sorted(int(ts[i]) for i in range(1, n)
                      if sign[i] == 1 and sign[i] != sign[i - 1] and int(ts[i]) >= cutoff)

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

    pairs = [emit_arr("ogL", og_long), emit_arr("ogS", og_short)]
    defs = "\n".join(p[0] for p in pairs); calls = "\n".join(p[1] for p in pairs)
    body = f'''//@version=5
indicator("OG s5m breach ({d5(cutoff)}→{d5(now)})  yellow=long  blue=short", overlay = true)
show = input.bool(true, "OG s5m breach (yellow long / blue short)")
// raw s5m OOB cross -> arm. es=-1 breach-low=long (yellow), es=+1 breach-high=short (blue). causal, no delay/cap.
{defs}
{calls}
bg = color(na)
if show and array.binary_search(ogL, time) >= 0
    bg := color.new(color.yellow, 0)
if show and array.binary_search(ogS, time) >= 0
    bg := color.new(color.blue, 0)
bgcolor(bg)
'''
    path = "/home/joe/thecodes/og_arm.pine"
    open(path, "w").write(body)
    print("og_long=%d  og_short=%d  (last %dd) -> %s" % (len(og_long), len(og_short), WINDOW_DAYS, path))


if __name__ == "__main__":
    main()
