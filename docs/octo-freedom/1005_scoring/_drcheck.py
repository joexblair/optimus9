"""For every leg of the 30 chains: the alternating `d` the run used vs the tape's OWN dr at the
leg's open bar. No decision - just how often they agree."""
import io, contextlib, re, sys, collections
sys.path.insert(0, '/home/joe/thecodes')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
DRv = SC.DR if hasattr(SC, 'DR') else SC.DRv
rows = []; day = None; legn = 0
for ln in open('/home/joe/.claude/jobs/6eb9931e/tmp/chain_os_legs.txt'):
    m = re.match(r'## CHAIN (\S+) (\S+)', ln)
    if m: day, seed = m.group(1), m.group(2); continue
    m = re.match(r'### leg (\d+) — (LONG|SHORT) open (\S+)\s+exit (\S+)\s+realised (\S+)', ln)
    if m:
        n, side, op, ex, real = int(m.group(1)), m.group(2), m.group(3), m.group(4), float(m.group(5))
        k = SC.K('%s %s' % (day, op))
        rows.append((day, seed, n, side, op, ex, real, int(DRv[k])))
print('# 101 LEGS: the side the run used vs the tape dr at the open bar')
print('| leg no | side used | tape dr at open | dr-bias side (dr+1=SHORT) | agree? | legs | realised |')
print('|---|---|---|---|---|---|---|')
agg = collections.OrderedDict()
for d_, s_, n, side, op, ex, real, dr in rows:
    bias = 'SHORT' if dr > 0 else ('LONG' if dr < 0 else 'flat')
    key = ('leg 1' if n == 1 else 'leg 2+', side, dr, bias, 'Y' if side == bias else 'n')
    e = agg.setdefault(key, [0, 0.0]); e[0] += 1; e[1] += real
for k_, v in agg.items():
    print('| %s | %s | %+d | %s | %s | %d | %+.4f |' % (k_[0], k_[1], k_[2], k_[3], k_[4], v[0], v[1]))
n1 = [r for r in rows if r[2] == 1]; n2 = [r for r in rows if r[2] > 1]
for lbl, grp in (('leg 1', n1), ('leg 2+', n2)):
    ag = sum(1 for r in grp if r[3] == ('SHORT' if r[7] > 0 else 'LONG'))
    print('\n- %s: %d legs, %d agree with the dr-bias side, %d disagree'
          % (lbl, len(grp), ag, len(grp) - ag))
