"""tide_emit_failed.py — pine of the entries that FAILED TO REACH R under the OOB exit gate (Joe 0708). With
exit_gate='oob' a trade only exits when its tracking r (s10r in R1, s5r in R2) reaches the favourable extreme; the
losers whose r never gets there walk to the window boundary (route r1bound/r2bound). This emits ONLY those, so we can
eyeball what stranded them. Labels: entry (side/values) + boundary-OUT (route/ret/MAE). Run:  python3 tide_emit_failed.py"""
import time, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from tide_machine import run_config

END = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
HOURS = 72
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging'),
       's1m': (60, ('bb', 6, 0.56, 'close'), 'emerging'), 's1M': (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging'),
       's1r': (60, ('k', 6, 6, 5, 'close'), 'emerging')}
SCALP = dict(fin_sets=('s1', 's15', 's30'), rev_sets=(), N=6, tol=24, wait_breach=False, seam=150000, stall_floor=0.0,
             exit_gate='oob')
BOUND = {'r1bound', 'r2bound'}                              # tracking r never reached the favourable extreme
hm = lambda t: time.strftime('%m-%d %H:%M', time.gmtime(int(t) / 1000))


def main():
    J = Jig(END, hours=HOURS, warmup=24, overrides=OVR)
    m = run_config(J, SCALP)
    ts, px = J.ts, J.px
    L = {k: J.causal.line(k) for k in ('s5M', 's7M', 's2M', 's10r', 's5r', 's3r', 's4r')}
    si = lambda a, k: (int(a[k]) if np.isfinite(a[k]) else 0)
    labels = []; nfail = 0
    for e, x, side, ret, mae, route in m['trades']:
        if route not in BOUND:
            continue
        nfail += 1
        lng = side == 'long'
        trk = 's10r' if route == 'r1bound' else 's5r'      # which r stranded it
        labels.append({'ts': int(ts[e]), 'y': float(px[e]), 'green': lng, 'up': True,
                       'text': "%s IN %s\\ns3r%d s4r%d  s5r%d\\ns5M%d s7M%d s2M%d"
                       % ('LONG' if lng else 'SHORT', hm(ts[e])[6:], si(L['s3r'], e), si(L['s4r'], e), si(L['s5r'], e),
                          si(L['s5M'], e), si(L['s7M'], e), si(L['s2M'], e))})
        labels.append({'ts': int(ts[x]), 'y': float(px[x]), 'green': lng, 'up': False,
                       'text': "STRANDED %s (%s)\\nret %+.2f%% MAE %.2f\\n%s@out %d"
                       % (hm(ts[x])[6:], route, ret, mae, trk, si(L[trk], x))})
    J.close()
    n = J.score.emit_labels(labels, "/home/joe/thecodes/tide_failed.pine",
                            "OOB failed-to-reach-r %s->%s" % (hm(END - HOURS * 3600000), hm(END)))
    print("failed-to-reach-r: %d of %d trades stranded to boundary -> tide_failed.pine (%d labels)"
          % (nfail, m['n'], n))


if __name__ == "__main__":
    main()
