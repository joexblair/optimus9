"""Which of the 30 chain seeds and 6 mandatory-exit bars move when the seed becomes KNOWN AT."""
import io, contextlib, re, sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
KNOB = ('lazy_g_config.v1|gcws30Mage|flip-towards+norblock|stamp-resolved|'
        'routing-banked|lineage-ws1|mtdwalk-drguard')
db = DatabaseManager(**get_db_config()); db.connect()
SIG = db.execute("SELECT os_day, os_ts, os_walk_ts FROM octosig_rulings WHERE os_knob_key=%s "
                 "AND os_grade='with-trend' ORDER BY os_day, os_walk_ts", (KNOB,), fetch=True)
db.disconnect()
KN = {}
for r in SIG:
    d = str(r['os_day']); wb = SC.K('%s %s' % (d, r['os_walk_ts']))
    c = SC.classify(wb); ex = c['m'].get('ex')
    known = max([wb, int(c['kw'])] + ([int(ex)] if ex is not None else []))
    KN[(d, r['os_ts'])] = (SC.U(known), (int(SC.ts[known]) - int(SC.ts[SC.K('%s %s' % (d, r['os_ts']))])) / 60000.0)
seeds = []; day = None
for ln in open('/home/joe/.claude/jobs/6eb9931e/tmp/chain_os_legs.txt'):
    m = re.match(r'## CHAIN (\S+) (\S+)', ln)
    if m: seeds.append((m.group(1), m.group(2)))
FLIPS = [('2026-09-14', '14:44:10'), ('2026-09-27', '03:10:05'), ('2026-09-27', '15:18:25'),
         ('2026-09-28', '05:57:00'), ('2026-10-01', '07:29:30'), ('2026-10-03', '19:15:20')]
def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    L = lambda a, m, b: a + m.join('─' * (x + 2) for x in w) + b
    print(L('┌', '┬', '┐')); print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for x in rr: print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))
mv = [(d, t, KN[(d, t)][0], '%+.2f' % KN[(d, t)][1]) for d, t in seeds
      if (d, t) in KN and KN[(d, t)][1] != 0]
print('# OF THE 30 CHAIN SEEDS, THE ONES THAT MOVE')
box(('day', 'seed used (os_ts)', 'KNOWN AT', 'moves by min'), mv or [('—', '—', '—', '—')])
print('\n- %d of %d seeds move. %d are unchanged.' % (len(mv), len(seeds), len(seeds) - len(mv)))
miss = [(d, t) for d, t in seeds if (d, t) not in KN]
if miss: print('- NOT FOUND in the with-trend rows: %s' % miss)
