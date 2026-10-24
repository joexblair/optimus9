"""v4nuggies' stage trace, so every candidate's falling-off point is visible. Joe 1024."""
import os, sys
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import collections
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_core_arm as CA, v4_sig_nuggies as NG

A, B, xw = ln.K(sys.argv[1]), ln.K(sys.argv[2]), int(sys.argv[3])
R = RS.load((RS.K0, RS.R0, RS.S0))
MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
CL = CA.lines(); G = NG.g30()
tr = []
sigs = NG.produce(CL, R, MG, G, A, B, xw, trace=tr)
print('# v4nuggies, %s .. %s, gcws30Mage ib dwell %d bars = %d s'
      % (ln.U(A), ln.U(B), xw, xw * 5))
print('# RULED_OK %s. the control: ws5r %s = %.2f, expected %.2f'
      % (K.RULED_OK, K.CONTROL_TS, R[5][ln.K(K.CONTROL_TS)], K.CONTROL_DB))
print('')
c = collections.Counter(r['stage'].split(' - ')[0] for r in tr)
print('| the stage a candidate reached | count |')
print('|---|---|')
for k, v in c.most_common():
    print('| %s | %d |' % (k, v))
print('')
print('| the stamp | side | cws1Mage extrema | at | verdict | gcws30Mage ib | the stage |')
print('|---|---|---|---|---|---|---|')
for r in sorted(tr, key=lambda z: z['stamp']):
    print('| %s | %s | %s | %s | %s | %s | %s |'
          % (ln.U(r['stamp']), 'HIGH' if r['side'] > 0 else 'LOW',
             ('%.2f' % r['extrema']) if 'extrema' in r else '-',
             ln.U(r['extrema_bar'])[11:] if 'extrema_bar' in r else '-',
             r.get('verdict') or '-',
             ln.U(r['ib'])[11:] if 'ib' in r else '-', r['stage']))
print('')
print('| the signal | side | why |')
print('|---|---|---|')
for s in sigs:
    print('| %s | %s | %s |' % (ln.U(s['bar']), 'HIGH' if s['side'] > 0 else 'LOW', s['why']))
print('')
print('%d signals from %d candidates' % (len(sigs), len(tr)))
