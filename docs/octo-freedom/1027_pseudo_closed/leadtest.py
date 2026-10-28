"""DOES THE PSEUDO-CLOSED LINE LEAD THE CLOSED EX-FENCE ENTRY, AND HOW OFTEN IS IT WRONG?

The agreement test in validate.py measured STALENESS, not quality: the closed read is late by up to
one TF by construction, so every current read disagrees with it at about the rate the lag implies.
This is the test that separates them, on the read Joe says the mech needs - *"we only need the line
to reach ex-fence"*.

PER LINE, PER SIDE, three reads of the same line:
    CLOSED    v4_closed_prev - the series whose ex-fence entries land where TV's closed bars land
    PSEUDO    the bar sequence ENDING AT t, so every bucket is complete
    EMERGING  the raw 5 s series the mech reads today

AN ENTRY is a bar where the read goes from not-ex-fence to ex-fence on that side.

    LEAD          for each CLOSED entry, the nearest candidate entry inside the one TF BEFORE it
    UNCONFIRMED   a candidate entry with NO closed entry inside the one TF AFTER it - the read
                  claimed ex-fence and the chart never agreed

NO HORIZON IS CHOSEN: the matching window is ONE TF WIDTH, which is the lag the closed read can
carry by construction. Nothing else is truncated.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
IDX = np.arange(A, B + 1)
TFS = [13, 14, 15, 16]
_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')


def entries(vals, sd):
    f = np.array([bool(K.ex_fence(v, sd)) for v in vals])
    return np.flatnonzero(f[1:] & ~f[:-1]) + 1


print('# EX-FENCE ENTRY: LEAD AND UNCONFIRMED RATE, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the reference is the CLOSED read - where TV\'s closed bars put the entry.')
print('# LEAD = the candidate entry inside the one TF BEFORE a closed entry, in minutes.')
print('# UNCONFIRMED = a candidate entry with no closed entry inside the one TF after it.')
print('# the matching window is ONE TF WIDTH - the lag the closed read carries by construction.')
print('# RULED_OK %s | pseudo BARS %d' % (K.RULED_OK, PC.BARS))
print('')
print('| the line | side | the read | entries | closed entries matched | median lead min |'
      ' unconfirmed | unconfirmed % |')
print('|---|---|---|---|---|---|---|---|')
for t in TFS:
    em = np.asarray(E[t], float)[IDX]
    cl = CP.series(np.asarray(E[t], float), t * 60)[IDX]
    ps = PC.series(close, t, IDX)
    w = t * 60 // 5
    for sd in (-1, +1):
        ec = entries(cl, sd)
        for nm, vals in (('pseudo', ps), ('emerging', em)):
            ex = entries(vals, sd)
            if len(ec) == 0 or len(ex) == 0:
                print('| ws%dr | %s | %s | %d | - | - | - | - |'
                      % (t, 'LOW' if sd < 0 else 'HIGH', nm, len(ex)))
                continue
            leads, hit = [], 0
            for c in ec:
                near = ex[(ex >= c - w) & (ex <= c)]
                if len(near):
                    hit += 1
                    leads.append((c - near[-1]) * 5 / 60.0)
            unconf = sum(1 for x in ex if not len(ec[(ec >= x) & (ec <= x + w)]))
            print('| ws%dr | %s | %s | %d | %d of %d | %s | %d | %.1f%% |'
                  % (t, 'LOW' if sd < 0 else 'HIGH', nm, len(ex), hit, len(ec),
                     '%.1f' % _med(leads) if leads else '-', unconf, 100.0 * unconf / len(ex)))
