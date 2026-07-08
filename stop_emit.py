"""stop_emit.py — pine emit of the o9-live LOSING closed trades over the last N hours (Joe 0708). Each entry is
labelled with the cascade line states AT ENTRY (s5M/s7M/s2M reversal context + s3r/s4r gate + s10r curl) so the
conditions that allowed the loss are visible; the exit label carries the net. Foundation artifact for the
stop-troubleshooting tool. NOTE: no hard-SL fired in this window — these are shared-TP reversal exits that closed
UNDERWATER, so 'stop' = reversal-at-a-loss, driven by entry quality. Run:  python3 stop_emit.py [hours]"""
import sys, time, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.jig import Jig

HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
TF_S = int(sys.argv[2]) if len(sys.argv) > 2 else 15                 # CHART timeframe (s) — snap labels to its bar grid
END = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
OVR = {'s10r': (600, ('k', 6, 6, 5, 'close'), 'emerging')}          # exit-curl line (matches tide_emit)
snap = lambda t: int(t) // (TF_S * 1000) * (TF_S * 1000)            # floor to the chart's bar so xloc.bar_time lands on it
hm = lambda t: time.strftime('%m-%d %H:%M', time.gmtime(int(t) / 1000))


def losers(hours):
    c = get_db_config(); c['database'] = 'o9_live'; d = DatabaseManager(**c); d.connect()
    rows = d.execute('''SELECT led_id, side, entry_px, exit_px, net, opened_ms, closed_ms
        FROM o9_ledger WHERE status='closed' AND net<0 AND closed_ms>=%s ORDER BY opened_ms''',
        (END - hours * 3600000,), fetch=True)
    d.disconnect(); return rows


def main():
    J = Jig(END, hours=HOURS, warmup=24, overrides=OVR)
    ts, px = J.ts, J.px
    L = {k: J.causal.line(k) for k in ('s5M', 's7M', 's2M', 's10r', 's3r', 's4r')}
    si = lambda a, i: (int(a[i]) if 0 <= i < len(a) and np.isfinite(a[i]) else 0)
    rows = losers(HOURS)
    labels = []
    for r in rows:
        lng = r['side'] == 'Buy'
        e = int(np.searchsorted(ts, int(r['opened_ms']) // 5000 * 5000))
        x = int(np.searchsorted(ts, int(r['closed_ms']) // 5000 * 5000))
        if e >= len(ts):
            continue
        labels.append({'ts': snap(ts[e]), 'y': float(r['entry_px']), 'green': lng, 'up': True,
                       'text': "L%d %s IN %s\\ns3r%d s4r%d\\ns5M%d s7M%d s2M%d\\ns10r%d"
                       % (r['led_id'], 'LONG' if lng else 'SHORT', hm(ts[e])[6:], si(L['s3r'], e), si(L['s4r'], e),
                          si(L['s5M'], e), si(L['s7M'], e), si(L['s2M'], e), si(L['s10r'], e))})
        if x < len(ts):
            labels.append({'ts': snap(ts[x]), 'y': float(r['exit_px']), 'green': lng, 'up': False,
                           'text': "L%d OUT %s  net %+.2f\\ns5M%d s2M%d s10r%d"
                           % (r['led_id'], hm(ts[x])[6:], float(r['net']), si(L['s5M'], x), si(L['s2M'], x), si(L['s10r'], x))})
    J.close()
    n = J.score.emit_labels(labels, "/home/joe/thecodes/stop_trades.pine",
                            "o9 LOSING trades %s->%s (%d)" % (hm(END - HOURS * 3600000), hm(END), len(rows)))
    tot = sum(float(r['net']) for r in rows)
    print("losers=%d over %dh, net $%.2f -> stop_trades.pine (%d labels)" % (len(rows), HOURS, tot, n))


if __name__ == "__main__":
    main()
