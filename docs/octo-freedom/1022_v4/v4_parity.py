"""Parity over 12 windows tiling the tape, on the BANKED line config.

WHY NOT ONE FULL-TAPE RUN. It timed out at 900 s, exit 124, and wrote a 0-byte file. `check()`
calls the UN-CACHED v4_lineage_trace.walk, which rebuilds a full-tape lift_off mask per timeframe
per fire - over a thousand fires is hours, and avoiding exactly that is why v4_fast exists. 12
bounded windows also give 12 DIFFERENT `B` boundaries, and the boundary is where the 1023 audit
found the two ib_cross implementations diverging (111 of 339 probes). More coverage, affordable.

WHY THE BANKED CONFIG AND NOT ln.line's. Parity is a code-equivalence claim and should hold on any
input, but the first run used the lines `ln.line` resolves - the DB's mech_lines('wsf') spec - and
the banked config produces a different reversal and cross pattern. Proving it on arrays the
machine does not use is weaker than it looks.

MEASURED 1023 ON THE BANK: 1,086 fires, 1,086 verdicts, 11,184 boundary probes, 0 disagreements.
On the DB-ruled lines: 602 / 602 / 11,184 / 0.

NOTE ON THE CONFIG LABELS. `RS.K0/R0/S0` fill the legacy tuple slots ('k', rsi, stc, k_len), so the
three axes are rsi, stc and k_len in that order - NOT k, rsi, stc. See the 1023 note in
v4_rcfg_sweep. The arrays are right; the names on them were not.

usage: v4_parity.py            (writes to stdout; redirect to out/parity_banked.md)
"""
import sys, os, datetime as dt
sys.path.insert(0,'/home/joe/thecodes'); sys.path.insert(0,'/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END','2026-10-05')
import ln, v4_knobs as K, v4_fast as F, v4_rcfg_sweep as RS
MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
R_all = RS.load((RS.K0, RS.R0, RS.S0))
R = {t: R_all[t] for t in list(range(1, 4)) + list(range(5, K.TF_CEILING + 3))}
print('# PARITY on the BANKED config k%d rsi%d stc%d, 12 windows tiling the tape.'
      % (RS.K0, RS.R0, RS.S0))
print('# control ws5r %s: banked %.2f (known-good %.2f), DB-ruled %.2f (known-good %.2f)'
      % (K.CONTROL_TS, R_all[5][ln.K(K.CONTROL_TS)], K.CONTROL_BANK,
         ln.line('ws5r')[ln.K(K.CONTROL_TS)], K.CONTROL_DB))
print()
print('| the window | fires | verdicts | ib_cross probes | disagreements |')
print('|---|---|---|---|---|')
T0 = dt.datetime(2026, 7, 2, 12, 0, 0)
END = dt.datetime(2026, 10, 4, 23, 59, 55)
bad = 0
for i in range(12):
    s = T0 + dt.timedelta(days=8 * i)
    e = min(T0 + dt.timedelta(days=8 * (i + 1)) - dt.timedelta(seconds=5), END)
    A, B = ln.K(s.strftime('%Y-%m-%d %H:%M:%S')), ln.K(e.strftime('%Y-%m-%d %H:%M:%S'))
    F.reset()
    lines = []
    n = F.check(A, B, R, MG, 'window', log=lambda t: lines.append(t))
    bad += n
    nf = nv = np_ = 0
    for t in lines:
        if 'fires | OK' in t:
            nf = int(t.split('|')[3].strip().split()[0])
        if 'verdicts |' in t:
            nv = int(t.split('|')[3].strip().split()[0])
        if 'probes' in t:
            np_ = int(t.split('|')[3].strip().split()[0])
    print('| %s .. %s | %d | %d | %d | %d |'
          % (s.strftime('%Y-%m-%d %H:%M:%S'), e.strftime('%Y-%m-%d %H:%M:%S'), nf, nv, np_, n))
    for t in lines:
        if 'MISMATCH' in t:
            print(t)
print()
print('| PARITY on the banked config | %s |'
      % ('OK, 0 disagreements across all 12 windows' if bad == 0 else '%d DISAGREEMENTS' % bad))
