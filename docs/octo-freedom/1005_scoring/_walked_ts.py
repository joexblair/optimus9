"""THE WALKED TIMESTAMPS of every sanctioned octo-sig. Joe 1007: *"we still need to print the
lineage walked octo-sig timestamps, which will have a considerable impact"*.

THREE BARS CARRY A RULING FORWARD OF `WALK FIRES FROM`:
  os_walk_ts   what report_leash_walk.py emits - the WALK's own fire bar.
  g5extrema    `m['ex']`, the bar mtd and branch D are READ at. `fwd` lands AFTER the fire bar.
  mtd walk kw  classify() walks forward up to MTD_WALK_BARS when mtd returns `neither`; `kw` is the
               bar that supplied the route.
  os_ts        the STAMPED anchor already banked - the fwd-g5extrema when there was no lookback,
               else the fire bar.

KNOWN AT = max(walk bar, g5extrema bar, kw). The first bar on which the row's own ruling exists.
Nothing here is applied to a trade - this is the print.
"""
import io, contextlib, sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
KNOB = ('lazy_g_config.v1|gcws30Mage|flip-towards+norblock|stamp-resolved|'
        'routing-banked|lineage-ws1|mtdwalk-drguard')
db = DatabaseManager(**get_db_config()); db.connect()
SIG = db.execute(
    "SELECT os_day, os_ts, os_walk_ts, os_stamp_src, os_g5ex_ts, os_g5ex_src, os_g5ex_lag_min, "
    "os_dr, os_route, os_grade FROM octosig_rulings WHERE os_knob_key=%s AND os_grade='with-trend' "
    "ORDER BY os_day, os_walk_ts", (KNOB,), fetch=True)
db.disconnect()
MIN = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
rows = []
for r in SIG:
    d = str(r['os_day'])
    kw_bar = SC.K('%s %s' % (d, r['os_walk_ts']))
    c = SC.classify(kw_bar)
    kw = int(c['kw']); ex = c['m'].get('ex')
    ex = int(ex) if ex is not None else None
    known = max([kw_bar, kw] + ([ex] if ex is not None else []))
    rows.append(dict(day=d, walk=r['os_walk_ts'], walk_bar=kw_bar, stamp=r['os_ts'],
                     src=r['os_stamp_src'], ex=(SC.U(ex) if ex is not None else '—'),
                     ex_src=r['os_g5ex_src'], ex_lag=float(r['os_g5ex_lag_min']),
                     kw=SC.U(kw), kw_lag=MIN(kw_bar, kw), walk_bars=int(c['walk_bars']),
                     known=SC.U(known), known_lag=MIN(kw_bar, known),
                     dr=int(r['os_dr']), route=r['os_route']))
def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    L = lambda a, m, b: a + m.join('─' * (x + 2) for x in w) + b
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))

print('\n# THE 53 SANCTIONED OCTO-SIGS — EVERY WALKED TIMESTAMP')
box(('day', 'WALK FIRES FROM', 'dr', 'route', 'g5extrema', 'ex src', 'ex lag min',
     'mtd walk kw', 'kw lag min', 'os_ts (stamped)', 'stamp src', 'KNOWN AT', 'known lag min'),
    [(r['day'], r['walk'], '%+d' % r['dr'], r['route'], r['ex'], r['ex_src'],
      '%+.2f' % r['ex_lag'], r['kw'], '%+.2f' % r['kw_lag'], r['stamp'], r['src'],
      r['known'], '%+.2f' % r['known_lag']) for r in rows])

print('\n# WHERE THE RULING IS KNOWN, RELATIVE TO `WALK FIRES FROM`')
import collections
b = collections.Counter()
for r in rows:
    g = ('0 — known at the fire bar' if r['known_lag'] == 0 else
         ('<= 1 min later' if r['known_lag'] <= 1 else
          ('1 to 5 min later' if r['known_lag'] <= 5 else
           ('5 to 15 min later' if r['known_lag'] <= 15 else 'over 15 min later'))))
    b[g] += 1
box(('known at', 'rows'), [(k, str(b[k])) for k in
    ['0 — known at the fire bar', '<= 1 min later', '1 to 5 min later', '5 to 15 min later',
     'over 15 min later'] if k in b])
lag = sorted(r['known_lag'] for r in rows)
print('\n- %d of %d rows are known LATER than `WALK FIRES FROM`'
      % (sum(1 for x in lag if x > 0), len(lag)))
print('- lag min: min %+.2f, median %+.2f, max %+.2f'
      % (lag[0], lag[len(lag) // 2], lag[-1]))
print('\n# WHICH BAR SETS `KNOWN AT`')
w2 = collections.Counter()
for r in rows:
    exb = None if r['ex'] == '—' else SC.K('%s %s' % (r['day'], r['ex']))
    kwb = SC.K('%s %s' % (r['day'], r['kw']))
    kb = SC.K('%s %s' % (r['day'], r['known']))
    tag = []
    if kb == r['walk_bar']: tag.append('fire bar')
    if exb is not None and kb == exb: tag.append('g5extrema')
    if kb == kwb: tag.append('mtd walk kw')
    w2[' + '.join(tag) or '?'] += 1
box(('the bar that sets KNOWN AT', 'rows'),
    [(k, str(w2[k])) for k in sorted(w2, key=lambda z: -w2[z])])
print('\n# THE mtd WALK ITSELF')
ww = collections.Counter('walked %d bars' % r['walk_bars'] if r['walk_bars'] else 'did not walk'
                         for r in rows)
box(('mtd walk', 'rows'), [(k, str(ww[k])) for k in sorted(ww, key=lambda z: -ww[z])])
