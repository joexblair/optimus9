"""v4nuggies' stage trace, and each signal scored against sweep-pivots. Joe 1024: *"use sweep-pivot"*.

THE EXIT IS THE SWEEP-PIVOT LEG'S END, not a horizon. `v4_sweep_pivots.swing` picks the TF whose
pivot sits closest to the event and returns that TF's own leg - its `open`, its extremum `pivot`
and its `close`. MAE/MFE are measured from the ENTRY (the signal bar + 1, the router's fire bar) to
that leg's close, so nothing here chooses a window.

usage: nug_trace.py <start> <end> <gcws30Mage ib dwell, in bars>
"""
import os, sys
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import collections
import numpy as np
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_core_arm as CA
import v4_sig_nuggies as NG, v4_signal as SG, v4_sweep_pivots as SP
from v4_backstop_trades import prices

A, B, xw = ln.K(sys.argv[1]), ln.K(sys.argv[2]), int(sys.argv[3])
R = RS.load((RS.K0, RS.R0, RS.S0))
MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
CL = CA.lines(); G = NG.g30()
close, hi, lo = prices()
tr = []
sigs = NG.produce(CL, R, MG, G, A, B, xw, trace=tr)

print('# v4nuggies, %s .. %s. gcws30Mage ib dwell %d bars = %d s - NOT BANKED, Joe has not'
      % (ln.U(A), ln.U(B), xw, xw * 5))
print('#   given this knob a value; it is SP_XWOB borrowed to exercise the code.')
print('# RULED_OK %s. the control: ws5r %s = %.2f, expected %.2f'
      % (K.RULED_OK, K.CONTROL_TS, R[5][ln.K(K.CONTROL_TS)], K.CONTROL_DB))
print('# sweep-pivots: ' + ', '.join('%s %s' % (n, v) for n, v, _ in SP.knobs()))
print('')
c = collections.Counter(r['stage'].split(' - ')[0] for r in tr)
print('| the stage a candidate reached | count |')
print('|---|---|')
for k, v in c.most_common():
    print('| %s | %d |' % (k, v))

print('')
print('# EACH SIGNAL, SCORED. the entry is the signal bar + 1. the exit is the sweep-pivot leg\'s')
print('#   own end. MAE/MFE are from the entry, signed by the trade direction.')
print('#   pivot = the leg\'s extremum. given % = the favourable move already behind at the signal.')
print('#   leg MFE % = the leg\'s full favourable excursion off its pivot.')
print('#   share = given / leg MFE: how much of the swing the signal gave away before entering.')
print('')
print('| the signal | side | dir | the entry | TF | marking | the pivot | the exit | MAE % | MFE % '
      '| given % | leg MFE % | share |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for s in sigs:
    sb, sd = int(s['bar']), int(s['side'])
    en = SG.fire_bar(s)
    dirn = SG.direction(sd)
    d = 1 if dirn == 'LONG' else -1
    sw = SP.swing(sb, sd, close)
    if sw is None or sw.get('close') is None:
        print('| %s | %s | %s | %s | - | - | - | no sweep-pivot scale | - | - | - | - | - |'
              % (ln.U(sb), 'HIGH' if sd > 0 else 'LOW', dirn, ln.U(en)))
        continue
    ex = int(sw['close'])
    assert ex >= en, 'the sweep-pivot leg ends before the entry'
    p0 = float(close[en])
    h = float(np.nanmax(hi[en:ex + 1])); l = float(np.nanmin(lo[en:ex + 1]))
    mfe = ((h - p0) if d > 0 else (p0 - l)) / p0 * 100.0
    mae = ((l - p0) if d > 0 else (p0 - h)) / p0 * 100.0
    print('| %s | %s | %s | %s | %s | %d of 8 | %s | %s | %+.3f | %+.3f | %+.3f | %.3f | %s |'
          % (ln.U(sb), 'HIGH' if sd > 0 else 'LOW', dirn, ln.U(en), sw['tf'],
             sw['n_marking'], ln.U(int(sw['pivot'])), ln.U(ex), mae, mfe,
             sw['given_pct'], sw['mfe_pct'],
             ('%.3f' % sw['share']) if sw.get('share') is not None else '-'))
print('')
print('%d signals from %d candidates' % (len(sigs), len(tr)))
