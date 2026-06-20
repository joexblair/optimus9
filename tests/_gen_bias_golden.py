"""
_gen_bias_golden.py — regenerate the bias_machine golden-master fixture (run when the ACCEPTED
behaviour changes, not on every edit). Freezes window 1781753040000's engine arrays + trigs + the
known-good ups() outputs so test_bias_machine.py can assert parity with NO live DB at test time.

  python3 tests/_gen_bias_golden.py
"""
import sys, json, pathlib; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm

END = 1781753040000
FIX = pathlib.Path(__file__).parent / 'fixtures'; FIX.mkdir(exist_ok=True)

db = DatabaseManager(**get_db_config()); db.connect()
W = bm.BiasWindow(db, END); db.disconnect()

# arrays pk_events / verdict_* read off self
np.savez(FIX / 'bias_pk_arrays.npz',
         osc=W._osc, px=W.px, s14M_sign=W.s14M_sign, s14r_sign=W.s14r_sign, s14M=W.s14M)

trigs = {str(tf): [dict(t=int(r['t']), j=int(r['j']), s=int(r['s']), oscv=float(r['oscv']))
                   for r in W.trigs(tf)] for tf in (6, 12)}
golden = {}
for trig in (6, 12):
    for gate in ('oob', 'mid'):
        for fh in (2, 0, None):
            golden[f'{trig}|{gate}|{fh}'] = W.ups(W.trigs(trig), gate, flt_half=fh)

meta = dict(end=END, bpt=int(W._bpt), W0=int(W.W0), W1=int(W.W1), trigs=trigs, golden=golden)
json.dump(meta, open(FIX / 'bias_pk_golden.json', 'w'))
n6 = len(trigs['6']); n12 = len(trigs['12'])
print(f'→ {FIX}/bias_pk_arrays.npz  ({W._osc.shape[0]} bars)')
print(f'→ {FIX}/bias_pk_golden.json  ({len(golden)} config keys · trigs6={n6} trigs12={n12})')
