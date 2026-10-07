"""The legs where the alternating `d` and the tape's own dr disagree. Joe 1007."""
import io, contextlib, re, sys
sys.path.insert(0, '/home/joe/thecodes')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
DRv = SC.DR if hasattr(SC, 'DR') else SC.DRv
day = None; seed = None; out = []
for ln in open('/home/joe/.claude/jobs/6eb9931e/tmp/chain_os_legs.txt'):
    m = re.match(r'## CHAIN (\S+) (\S+)', ln)
    if m: day, seed = m.group(1), m.group(2); continue
    m = re.match(r'### leg (\d+) — (LONG|SHORT) open (\S+)\s+exit (\S+)\s+realised (\S+)\s+leg MAE (\S+)\s+why (.+)', ln)
    if m:
        n, side, op, ex, real, mae, why = (int(m.group(1)), m.group(2), m.group(3), m.group(4),
                                           float(m.group(5)), float(m.group(6)), m.group(7).strip())
        dr = int(DRv[SC.K('%s %s' % (day, op))])
        bias = 'SHORT' if dr > 0 else 'LONG'
        if n > 1 and side != bias:
            out.append((day, seed, n, side, bias, dr, op, ex, real, why))
def box(hdr, rows):
    w = [max(len(hdr[i]), max((len(str(r[i])) for r in rows), default=0)) for i in range(len(hdr))]
    L = lambda a, m, b: a + m.join('─' * (x + 2) for x in w) + b
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for r in rows:
        print('│' + '│'.join(' ' + str(r[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))
print('# THE %d LEGS WHERE THE ALTERNATION FIGHTS THE TAPE dr' % len(out))
box(('day', 'chain seed', 'leg no', 'side used', 'dr-bias side', 'tape dr', 'open', 'exit',
     'realised', 'why'),
    [(o[0], o[1], str(o[2]), o[3], o[4], '%+d' % o[5], o[6], o[7], '%+.4f' % o[8], o[9])
     for o in out]
    + [('total', '', '', '', '', '', '', '', '%+.4f' % sum(o[8] for o in out), '')])
