"""curl_emit.py — s45r coarse curls, boundary-agnostic, on a 5-min pane. (Joe 0714)

  LINE    s45r   itf 45min   k_len 7 | rsi 5 | stc 7 | ohlc4   (the baked-in s-series r)
  SEAM    TF/9  ->  45*60/9 = 300s = 5 min   (one coarse sample per 5-min bar — the pane's own bar)
  CURL    jig.coarse + jig.curl -> lr_v2._curl_detect.  Coarse, NO wob — the same producer every s-line
          curl in the system uses.  Fires one seam AFTER the turn, past data only.
  BOUNDARY-AGNOSTIC — both directions, anywhere on the board:
          GREEN = trough (s45r turns UP)      RED = peak (s45r turns DOWN)

Causal/emerging. Every read via the jig.
  python3 curl_emit.py [days] [seam_div]        (default 7 days, TF/9)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig

TF = 45
SEAM_DIV = int(sys.argv[2]) if len(sys.argv) > 2 else 9
R_CFG = ('k', 5, 7, 7, 'ohlc4')            # Joe's notation: k_len 7 | rsi 5 | stc 7
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 7

PAINT_TF_S = 180                           # paint on the NEXT 3-min bar after the curl (Joe 0714). The curl
                                           # still FIRES on the 5s grid off the TF/4 seam — the seam does NOT
                                           # align to 3min and is NOT changed. Painting the bar that CONTAINS
                                           # the curl would light a bar that opened BEFORE the curl was
                                           # confirmed; the next bar is the first one that could have known.
SEAM_S = TF * 60 // SEAM_DIV
end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)

with Jig(end_ms, hours=DAYS * 24, warmup=120,
         overrides={f's{TF}r': (TF * 60, R_CFG, 'emerging')}) as j:
    C = j.causal
    ts = np.asarray(j.ts, np.int64)
    win = ts >= (end_ms - DAYS * 24 * 3600_000)
    r = C.line(f's{TF}r')
    dt = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M')

    ts_c, c = C.coarse(f's{TF}r', SEAM_S * 1000)
    P = PAINT_TF_S * 1000
    snap = lambda t: ((int(t) // P) + 1) * P            # the NEXT 3-min bar after the curl
    lo0, hi0 = ts[win][0], ts[win][-1]
    up = sorted({snap(t) for t in C.curl(ts_c, c, +1) if lo0 <= t <= hi0})   # trough -> turning UP
    dn = sorted({snap(t) for t in C.curl(ts_c, c, -1) if lo0 <= t <= hi0})   # peak   -> turning DOWN
    kof = lambda t: int(np.searchsorted(ts, t))

    notes = [
        f's{TF}r COARSE CURLS — boundary-agnostic — {dt(int(np.flatnonzero(win)[0]))} -> {dt(len(ts)-1)} UTC',
        '',
        'GREEN = trough (s45r turns UP)     RED = peak (s45r turns DOWN)',
        '',
        f's{TF}r   itf {TF}min   k_len {R_CFG[3]} | rsi {R_CFG[1]} | stc {R_CFG[2]} | {R_CFG[4]}',
        f'seam    TF/{SEAM_DIV} = {SEAM_S}s = {SEAM_S / 60:.2f}min   (the coarse sampling grid)',
        f'paint   the NEXT {PAINT_TF_S // 60}-min bar after the curl (the first bar that could have known)',
        'curl    jig.coarse + jig.curl (lr_v2._curl_detect). Coarse, NO wob. Fires one seam AFTER the turn.',
        'causal / emerging. no boundary condition — every turn, anywhere on the board.',
    ]
    streams = [
        {'name': 'curl_up', 'ts': up, 'color': 'color.green'},
        {'name': 'curl_dn', 'ts': dn, 'color': 'color.red'},
    ]
    path = f'/home/joe/thecodes/transfer/curl_emit_s{SEAM_DIV}.pine'
    n = j.score.emit_bgcolor(streams, path, f's{TF}r coarse curls — seam TF/{SEAM_DIV}', opacity=0, notes=notes)

    print('\n'.join(notes))
    print()
    print(f'  green (up)   {len(up):>4}')
    print(f'  red   (down) {len(dn):>4}')
    print(f'  painted {n}  ->  {path}')
    print()
    print(f'  {"3-min bar":<14} {"dir":>5} {"s45r":>7}')
    U = set(up)
    for t in sorted(set(up) | set(dn)):
        k = kof(t)
        d = 'UP' if t in U else 'DOWN'
        if t in U and t in set(dn):
            d = 'BOTH'
        print(f'  {dt(k):<14} {d:>5} {r[k]:>7.1f}')
