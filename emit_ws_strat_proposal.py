"""emit_ws_strat_proposal — blue/yellow pine for the SWEPT PROPOSAL. Joe 0806.

NOT the banked config. ws_strat_walk / ws_strat_bar and ws_strat_walk.pine (red/green) stay at the
banked knobs; this file only draws what the 3-sweep proposal would paint, so the two can be stacked
on one chart and compared.

    banked     b 48|0.98  Mage 37|0.90  oobw  8  fence 22  xrev 4  -> 116 signals, 94 ungated
    proposal   b 49|0.95  Mage 38|0.93  oobw 16  fence 10  xrev 2  ->  87 signals, 63 ungated

SEVEN knobs move at once, and b-mult 0.95 / xrev 2 are each ONE POINT WIDE — 0.94 and 0.96 lose a
target (the nearest surviving signal is 70 s / 2380 s away), xrev 1 and 3 lose one at 785 s. Joe
0806: "agreed, but it's nothing we can't re-sweep later."

COLOURS: blue = hi-side cross, yellow = lo-side. The pairing in jig._bgcolor_frag's locked block
(s_walk_hi blue / s_walk_lo yellow). The banked emit owns red/green; this one must not collide.

    python3 emit_ws_strat_proposal.py
"""
import datetime as dt
from datetime import timezone
import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, BBLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis.ws_strat import walk
from optimus9.analysis.jig import _Score, _Causal

HI, LO = 85., 15.
BLEN, BMULT = 49, 0.95        # gcws30b @30s AND ws1b @60s  (banked 48|0.98)
MLEN, MMULT = 38, 0.93        # ws1Mage @60s                (banked 37|0.90)
OOBW, XWOB, FENCE, LB, XREV = 16, 2, 10, 19, 2
START = dt.datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
BUCKET_MS = 15_000
OUT = 'ws_strat_proposal.pine'
CONF = ['08-04 14:20:25', '08-04 15:53:00', '08-04 16:56:50', '08-04 19:46:10', '08-04 20:20:00',
        '08-04 21:25:55', '08-05 00:09:05', '08-05 01:04:15', '08-05 02:36:20', '08-05 04:03:50',
        '08-05 05:28:25', '08-05 07:45:50']
u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    r = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',
                   fetch=True)[0]
    ls = LineStore(db)
    ovr = {'ws1x': (*ls.resolve('ws1x'), ls.value_mode('ws1x')),
           'g30b': override(30, BBLine(length=BLEN, mult=BMULT, src='close'), 'emerging'),
           'ws1b': override(60, BBLine(length=BLEN, mult=BMULT, src='close'), 'emerging'),
           'ws1M': override(60, BBLine(length=MLEN, mult=MMULT, src='close'), 'emerging')}
    db.disconnect()
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg={'src': r['s'], 'len': r['l']})
    ts = np.asarray(J.ts); V = {n: np.asarray(J.W.line(n), float) for n in ovr}
    i0 = int(np.searchsorted(ts, int(START.timestamp() * 1000)))
    ev = walk(V['g30b'], HI, LO, OOBW, XWOB, i0=i0)
    rev = _Causal(None).reversal(V['ws1x'], XREV)
    M, B, X = V['ws1M'], V['ws1b'], V['ws1x']

    ung = []
    for e in ev:                                   # Joe's gate, unchanged; only the knobs differ
        c = e['conf']
        if M[c] >= HI or M[c] <= LO:               e['by'] = 'ws1Mage'
        elif B[c] > 100 - FENCE or B[c] < FENCE:   e['by'] = 'ws1b'
        elif rev[c] == (-1 if X[c] > 50 else 1):   e['by'] = 'ws1x'
        elif not (B[c] >= HI or B[c] <= LO) and (
                (B[max(0, c - LB + 1):c + 1] >= HI).any()
                or (B[max(0, c - LB + 1):c + 1] <= LO).any()):  e['by'] = 'lookback'
        else:                                      e['by'] = ''
        if e['by']:
            ung.append(e)
    print(f'{len(ev)} signals, {len(ung)} ungated, {len(ev) - len(ung)} gated')

    cms = [int(dt.datetime.strptime('2026-' + t, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
               .timestamp() * 1000) for t in CONF]
    ums = np.array([int(ts[e['cross']]) for e in ung])
    print(f"\n{'confirmed target':<19} {'nearest ungated':<19} {'delta_s':>8}")
    for t, m in zip(CONF, cms):
        j = int(np.abs(ums - m).argmin())
        print(f'{"2026-" + t:<19} {u(ums[j]):<19} {(ums[j] - m) / 1000:>8.0f}')

    bkt = _Score(None).bucket_spans
    hi_ts = bkt([int(ts[e['cross']]) for e in ung if e['side'] > 0], BUCKET_MS)
    lo_ts = bkt([int(ts[e['cross']]) for e in ung if e['side'] < 0], BUCKET_MS)
    streams = [{'name': 'prop_hi_x_ib', 'ts': hi_ts, 'color': 'color.blue'},
               {'name': 'prop_lo_x_ib', 'ts': lo_ts, 'color': 'color.yellow'}]
    notes = (f'ws_strat PROPOSAL (swept 0806) | blue = gcws30b crossed OOB(hi>={HI:.0f})->IB | '
             f'yellow = OOB(lo<={LO:.0f})->IB'
             f' | gcws30b + ws1b = bb {BLEN}|{BMULT}|close  (banked 48|0.98)'
             f' | ws1Mage = bb {MLEN}|{MMULT}|close  (banked 37|0.90)'
             f' | OOB dwell > {OOBW} bars of 5s (>= {(OOBW + 1) * 5}s)  (banked 8)'
             f' | XWOB {XWOB} | fence {FENCE} outside [{FENCE},{100 - FENCE}]  (banked 22)'
             f' | ws1x reversed toward 50 wob {XREV}  (banked 4) | ws1b lookback {LB} bars (95s)'
             f' | PAINTS THE UNGATED ONLY: {len(ung)} of {len(ev)} signals'
             f' | walk {u(ts[i0])} -> {u(ts[-1])}'
             f' | NOT BANKED. b-mult 0.95 and xrev 2 are each ONE POINT WIDE: 0.94/0.96 and 1/3 each'
             f' lose a confirmed target.')
    total = _Score(None).emit_bgcolor(streams, OUT, 'ws_strat PROPOSAL — gcws30b OOB x IB (15s)',
                                      notes=notes)
    print(f'\n{OUT} -> {total} painted 15s bars')
    print(f'  blue   prop_hi_x_ib  {sum(1 for e in ung if e["side"] > 0):>3} events -> {len(hi_ts):>3} bars')
    print(f'  yellow prop_lo_x_ib  {sum(1 for e in ung if e["side"] < 0):>3} events -> {len(lo_ts):>3} bars')
    seam = sum(1 for e in ung if int(ts[e['cross']]) % BUCKET_MS == 0)
    print(f'  {seam} of {len(ung)} already on a 15s seam; {len(ung) - seam} floored to the prior 15s bar')


if __name__ == '__main__':
    main()
