"""tide_emit.py — pine emit of the wb=OFF scalp trades over a window (Joe 0708). Runs tide_machine.run_config for the
scalp, labels each entry+exit (green=long/red=short) with live values + realized return, via jig.score.emit_labels.
Run:  python3 tide_emit.py"""
import time, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

END = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)   # window end
HOURS = 72                                                                            # -> 07-04 20:00 .. 07-07 20:00
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging'),
       's1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
       's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
SCALP = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, wait_breach=False, seam=150000, stall_floor=0.0,
             exit_gate='oob')                                                          # exit only on the favourable extreme (your 20:35)
hm = lambda t: time.strftime('%m-%d %H:%M', time.gmtime(int(t) / 1000))


def main():
    J = Jig(END, hours=HOURS, warmup=24, overrides=OVR)
    m = run_config(J, SCALP)
    ts, px = J.ts, J.px
    L = {k: J.causal.line(k) for k in ('s5M', 's7M', 's2M', 's10r', 's3r', 's4r')}
    si = lambda a, k: (int(a[k]) if np.isfinite(a[k]) else 0)
    labels = []
    for e, x, side, ret, mae, route in m['trades']:
        lng = side == 'long'
        labels.append({'ts': int(ts[e]), 'y': float(px[e]), 'green': lng, 'up': True,
                       'text': "%s IN %s\\ns3r%d s4r%d\\ns5M%d s7M%d s2M%d\\ns10r%d"
                       % ('LONG' if lng else 'SHORT', hm(ts[e])[6:], si(L['s3r'], e), si(L['s4r'], e),
                          si(L['s5M'], e), si(L['s7M'], e), si(L['s2M'], e), si(L['s10r'], e))})
        labels.append({'ts': int(ts[x]), 'y': float(px[x]), 'green': lng, 'up': False,
                       'text': "OUT %s (%s)\\nret %+.2f%% MAE %.2f\\ns10r%d" % (hm(ts[x])[6:], route, ret, mae, si(L['s10r'], x))})
    J.close()
    n = J.score.emit_labels(labels, "/home/joe/thecodes/tide_scalp.pine",
                            "wb=off scalp %s->%s" % (hm(END - HOURS * 3600000), hm(END)))
    print("scalp: n=%d ret=%+.3f MAE=%.2f MFE=%.2f win=%.2f -> tide_scalp.pine (%d labels)"
          % (m['n'], m['r_ret'], m['r_mae'], m['r_mfe'], m['win'], n))


if __name__ == "__main__":
    main()
