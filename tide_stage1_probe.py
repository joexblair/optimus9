"""tide_stage1_probe.py — isolate STAGE 1 of exit_walk (the b2/cascade former) on the CURRENT (uncapped) machine and
report why it does/doesn't form. Stage 1 = after entry, find an s5m breach to the trade side (s5s flips to d), then
both s15a & s30a (favourable side) within exit_fin_lb bars -> b2. Faithful replica of tide_machine.py lines 101-111.
Run:  python3 tide_stage1_probe.py"""
import datetime as dtm, time
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config, _sgn

END = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging'),
       's1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
       's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
CFG = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, seam=150000, stall_floor=0.0, exit_gate='oob', wait_breach=False)
hm = lambda t: time.strftime('%m-%d %H:%M', time.gmtime(int(t) / 1000))


def main():
    J = Jig(END, hours=72, warmup=24, overrides=OVR)
    m = run_config(J, CFG)
    n = J.n; ts = J.ts; HI, LO = J.hi, J.lo
    s5m = J.causal.line('s5m'); s5s = _sgn(s5m, HI, LO)
    q15h, q15l = J.causal.finishers('s15'); q30h, q30l = J.causal.finishers('s30')
    lb = J.cfg.fin_lb                                                # exit_fin_lb default
    print("=== STAGE 1 on %d uncapped entries — s5m breach(->trade side) then s15a & s30a within %d bars ===" % (m['n'], lb + 1))
    print("HI/LO = %d/%d ; s5s==d means: long-> s5m>=HI, short-> s5m<=LO" % (HI, LO))
    agg = {'nob1': 0, 'b1_no_both': 0, 'b1_s15_only': 0, 'b1_s30_only': 0, 'b1_neither': 0, 'formed': 0}
    for e, x, side, ret, mae, route in m['trades']:
        d = 1 if side == 'long' else -1
        f15, f30 = (q15h, q30h) if side == 'long' else (q15l, q30l)
        # how many s5m breaches to the trade side ever occur after entry, and did any assemble both finishers?
        b1s = [k for k in range(e + 1, n) if s5s[k] == d and s5s[k - 1] != d]
        first_b1 = b1s[0] - e if b1s else None
        formed = False; had15 = had30 = False
        for b1 in b1s:
            w1 = min(n, b1 + lb + 1)
            s15 = np.flatnonzero(f15[b1:w1]).size > 0; s30 = np.flatnonzero(f30[b1:w1]).size > 0
            had15 |= s15; had30 |= s30
            if s15 and s30:
                formed = True; break
        # also: is s5m EVER on the trade side after entry (breach-agnostic)?
        ever_side = bool((s5s[e + 1:] == d).any())
        if not b1s:
            agg['nob1'] += 1; tag = 'NO b1 (s5m never fresh-breaches trade side; ever_on_side=%s)' % ever_side
        elif formed:
            agg['formed'] += 1; tag = 'formed b2'
        else:
            agg['b1_no_both'] += 1
            k = 's15_only' if (had15 and not had30) else 's30_only' if (had30 and not had15) else 'neither'
            agg['b1_%s' % k] += 1
            tag = '%d b1s but never BOTH finishers (%s reached)' % (len(b1s), k)
        print("%-5s IN %s route=%-7s | first_b1 +%s bars | %s" % (side, hm(ts[e]), route, first_b1, tag))
    print("\nAGG:", agg)
    J.close()


if __name__ == "__main__":
    main()
