"""Bank the ACTIONABLE reference beside the ceiling one. Joe 0929: "show them alongside".

wsf_trades already holds the reference backtest entered at `wsl_sig_utc` - 120 rows, the CEILING,
because that bar is a median 2.8 min before o9-live could know it. This banks the same trades
entered at the EMIT BAR - max(brk, rev, actionable), the first bar o9-live can act on - which is the
baseline every number in the 0929 sweep was measured against.

WHERE IT LANDS, and why. The unique key is (wt_key, wt_win, wt_open_ms). The entry rule is a
property of the CONFIG, not of the window, so it goes in `wt_key` and `wt_win` stays a truthful
window string. A new key lands BESIDE the existing rows - nothing is updated, nothing is dropped.

    wtc_v2_v7_rule1_gateopen                         entry at wsl_sig_utc   120 rows  the ceiling
    wtc_v2_v7_rule1_gateopen_entry_emit              entry at the emit bar  119 rows  the baseline
    wtc_v2_v7_rule1_gateopen_entry_emit_noflipopen   ... and the backstop
                                                     never opens             67 rows  Joe 0929

THE BACKSTOP NO LONGER OPENS, Joe 0929. He ruled it after seeing the measurement: "now we have the
data I can see that dr-flip as an open is not helpful. the cost is accceptable - it gives us space
to apply other mechs (lazy-g for example)". It still CLOSES - without that a trade would run to the
next sig_utc whatever happened. His 0929 rule had been "closes and opens"; this is that rule minus
the open, and it supersedes it.

The 66 sig_utc-opened trades are byte-identical either way - verified, 0 differ. Dropping the open
deletes the 52 the backstop manufactured and touches nothing else. The book then sits FLAT for
43.8 h of the 119.5 h window, 36.6%, which is the space Joe is making room in.

`_noflipopen` follows the key's own house style - `rule1_gateopen` already names a rule that way.

TWO TRADES DO NOT APPEAR in the emit-bar set: the signal was not emittable until at or after the
bar the trade closed, so o9-live could not have taken them at all. They are listed on stdout, not
silently dropped.
"""
import sys, io, numpy as np, datetime as dt
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
import build_wsf_trades as BWT, report_coil_exit as RCE
from optimus9.compute import trade_config as TC
from optimus9.compute.v3_config import v3_config
from optimus9.compute.dr_latch import latch_wob
from optimus9.compute.rule1_gate import gate
from optimus9.compute.trade_walk import walk as twalk, mae_mfe


def walk_no_flip_open(opens, dr, start, end):
    """trade_walk.walk with the dr-flip's OPEN removed. The close is untouched, and so is the
    same-bar priority. Joe 0929 ruled the open out; the walk is otherwise his 0929 rule."""
    O = set(int(x) for x in opens); start = max(1, int(start)); out = []; pos = None
    for k in range(start, int(end) + 1):
        if pos is not None:
            d = int(dr[k])
            if d == -pos['dr'] and d != 0:
                pos['left'] = True
            if pos['left'] and d == pos['dr'] and d != int(dr[k - 1]):
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='dr-flip'))
                pos = None                       # the only change: the backstop does not re-open
                continue
        if k in O:
            if pos is not None:
                out.append(dict(open=pos['open'], close=k, dr=pos['dr'],
                                opened_by=pos['opened_by'], closed_by='sig_utc'))
            pos = dict(open=k, dr=int(dr[k]), opened_by='sig_utc', left=False)
    return out, pos
from optimus9.analysis.jig import anchor_floater
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e

SRC_KEY = 'wtc_v2_v7_rule1_gateopen'
NEW_KEY = SRC_KEY + '_entry_emit' + ('_noflipopen' if '--no-flip-open' in sys.argv else '')
WIN = '2026-09-01..2026-09-06'

db = DatabaseManager(**get_db_config()); db.connect()
TC.seed(db, TC.V); Ct = TC.load(db, TC.V); V3 = v3_config(db)
ts, r1, r2, r3, g30r, xn, px, m1, mx = BWT.load(db, Ct); n = len(ts)
U = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, dt.timezone.utc).replace(tzinfo=None)
dr = latch_wob(m1, mx, 0, n - 1, wob=int(Ct['latch_wob']),
               hi=float(Ct['mage_fence_hi']), lo=float(Ct['mage_fence_lo']))
r_ = db.execute("SELECT wsl_v3_knobs k, wsl_win w FROM wsf_leash WHERE wsl_knobs LIKE 'v7%%' LIMIT 1",
                fetch=True)[0]
w0, w1 = r_['w'].split('..')
_t, hist = RCE.walk(db, V3, r_['k'], w0, w1)
EMIT = {}
for h in hist:
    if h['rev'] is None: continue
    m = h['mo']; brk = m['brk'] if m['brk'] is not None else m['i1']
    e = max(brk, int(h['rev']), int(coil_exit.fired(h)[1])); k = int(h['rev'])
    if k not in EMIT or e < EMIT[k]: EMIT[k] = e
fence = (float(Ct['rule1_fence_lo']), float(Ct['rule1_fence_hi']))
oob = (float(Ct['oob_lo']), float(Ct['oob_hi']))
back = int(float(Ct['rule1_back_min']) * 60 / 5); fwd = int(float(Ct['rule1_fwd_min']) * 60 / 5)
dwb = int(Ct['div_tf']) * int(V3['dwell_min_per_tf']) * 12; blk = int(V3['block'])
opens = []
for k in sorted(EMIT):
    d = int(dr[k])
    res = anchor_floater(r1, px, d, k, block=blk, mid=50.0, xn=xn, dwell_bars=dwb, oob=oob)
    if gate(r1, r2, r3, g30r, d, k, back, fence, oob, 0 if res is None else int(res['fired']),
            fwd_bars=fwd, run_clamp=Ct['rule1_run_clamp'])['open']:
        opens.append(k)
opens = sorted(set(opens)); HIB = int(np.searchsorted(ts, BWT.WIN_MS[1]))
_w = walk_no_flip_open if '--no-flip-open' in sys.argv else twalk
T, still = _w(opens, dr, min(opens), HIB)

rows, miss = [], []
nth = 0
for t in T:
    o = EMIT.get(t['open'], t['open'])
    if o >= t['close']:
        miss.append((t, o)); continue
    a, b = mae_mfe(px, o, t['close'], t['dr'])
    nth += 1
    rows.append((NEW_KEY, WIN, nth, int(t['dr']), 'SHORT' if t['dr'] > 0 else 'LONG',
                 U(o), int(ts[o]), U(t['close']), int(ts[t['close']]),
                 t['opened_by'], t['closed_by'],
                 float(px[o]), float(px[t['close']]), float(a), float(b)))
if still is not None:
    o = EMIT.get(still['open'], still['open']); nth += 1
    rows.append((NEW_KEY, WIN, nth, int(still['dr']), 'SHORT' if still['dr'] > 0 else 'LONG',
                 U(o), int(ts[o]), None, None, still['opened_by'], None,
                 float(px[o]), None, None, None))

print('UNREACHABLE - closed before the signal was emittable, so not banked: %d' % len(miss))
for t, o in miss:
    print('  open %s  emit %s  close %s  %s'
          % (U(t['open']), U(o), U(t['close']), 'SHORT' if t['dr'] > 0 else 'LONG'))
if '--write' in sys.argv:
    db.execute("DELETE FROM wsf_trades WHERE wt_key=%s AND wt_win=%s", (NEW_KEY, WIN))
    db.executemany(
        "INSERT INTO wsf_trades (wt_key,wt_win,wt_n,wt_dr,wt_side,wt_open_utc,wt_open_ms,"
        "wt_close_utc,wt_close_ms,wt_opened_by,wt_closed_by,wt_open_px,wt_close_px,"
        "wt_mae_pct,wt_mfe_pct) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
    print('banked %d rows under %s' % (len(rows), NEW_KEY))
else:
    print('DRY RUN - %d rows would be banked under %s' % (len(rows), NEW_KEY))
db.disconnect()
