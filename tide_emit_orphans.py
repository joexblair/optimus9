"""tide_emit_orphans.py — pine of ORPHANED entries (exit_walk never fired a real exit -> x==n-1, route nocasc/r1bound/
r2bound) so we can design an exit against what strands. Two pines: wb=ON (ride) and wb=OFF (scalp). Uncapped arm.
Each orphan gets: entry (side/time/values), its MFE peak (where a good exit COULD have banked), and the strand point
(route/held/ret/MAE). Green=long/red=short. Run:  python3 tide_emit_orphans.py"""
import time, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

END = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
HOURS = 72                                                                            # 07-04 20:00 .. 07-07 20:00
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging'),
       's1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
       's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
BASE = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, seam=150000, stall_floor=0.0, exit_gate='oob')
BOUND = {'nocasc', 'r1bound', 'r2bound'}
hm = lambda t: time.strftime('%m-%d %H:%M', time.gmtime(int(t) / 1000))
si = lambda a, k: (int(a[k]) if np.isfinite(a[k]) else 0)


def emit(J, wb, tag):
    m = run_config(J, dict(BASE, wait_breach=wb))
    ts, px = J.ts, J.px
    L = {k: J.causal.line(k) for k in ('s5M', 's7M', 's2M', 's10r', 's5r')}
    labels = []; norph = 0
    for e, x, side, ret, mae, route in m['trades']:
        if route not in BOUND:
            continue
        norph += 1
        lng = side == 'long'; d = 1 if lng else -1
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * d
        pk = e + int(np.nanargmax(seg)); mfe = float(np.nanmax(seg)); held = (ts[x] - ts[e]) / 60000.0
        labels.append({'ts': int(ts[e]), 'y': float(px[e]), 'green': lng, 'up': True,
                       'text': "%s IN %s\\ns5M%d s7M%d s2M%d\\ns10r%d s5r%d"
                       % ('LONG' if lng else 'SHORT', hm(ts[e])[6:], si(L['s5M'], e), si(L['s7M'], e),
                          si(L['s2M'], e), si(L['s10r'], e), si(L['s5r'], e))})
        if pk != e:
            labels.append({'ts': int(ts[pk]), 'y': float(px[pk]), 'green': lng, 'up': True,
                           'text': "MFE %+.2f%% %s\\ns10r%d s5r%d" % (mfe, hm(ts[pk])[6:], si(L['s10r'], pk), si(L['s5r'], pk))})
        labels.append({'ts': int(ts[x]), 'y': float(px[x]), 'green': lng, 'up': False,
                       'text': "ORPHAN %s (%s)\\nheld %.0fm ret %+.2f%% MAE %.2f" % (hm(ts[x])[6:], route, held, ret, mae)})
    path = "/home/joe/thecodes/tide_orphans_%s.pine" % tag
    nlab = J.score.emit_labels(labels, path, "orphans %s %s->%s" % (tag, hm(END - HOURS * 3600000), hm(END)))
    print("%-5s: %d orphans of %d entries -> %s (%d labels)" % (tag, norph, m['n'], path.split('/')[-1], nlab))


def main():
    J = Jig(END, hours=HOURS, warmup=24, overrides=OVR)
    emit(J, True, 'wbon')
    emit(J, False, 'wboff')
    J.close()


if __name__ == "__main__":
    main()
