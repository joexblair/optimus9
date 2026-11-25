"""The fdm3 knobs the oracle reads, from the oracle's own directory. HIS 1120 SRP: the pivot knobs are not
here any more - they are sweep-pivots' own (v4_sweep_pivots POOL_TF, POOL_DWELL_S, SET_SHIFT_MIN).

fdm3_knobs.py lives in docs/fdm3 and the oracle runs from docs/octo-freedom/1022_v4/out, which is
not on its path. This reads the one banked file rather than keeping a second copy of the values:
a drift between the two would be invisible, and the knob file is the single home.
"""
import os
import sys

_H = '/home/joe/thecodes/docs/fdm3'
if _H not in sys.path:
    sys.path.insert(0, _H)
import fdm3_knobs as _FK                                    # noqa: E402

OOB_JUMP = int(_FK.ORAC_OOB_JUMP)
SMALL_TRADE_MAX_TOEXF = int(_FK.SMALL_TRADE_MAX_TOEXF)    # HIS 1119 `fdm3-small-trade-max-toexf`
INFENCE_READ = str(_FK.INFENCE_READ)                     # HIS 1120: the r the in-fence power band reads
INFENCE_EDGES = tuple(float(v) for v in _FK.INFENCE_EDGES)   # HIS 1119 band edges; HIS 1121 +4/-4 adds 8 and 92 on 8793
RED4_TFS = tuple(range(int(str(_FK.RED4_LINES).split('-')[0]), int(str(_FK.RED4_LINES).split('-')[1]) + 1))   # HIS 1122
assert RED4_TFS and 1 <= RED4_TFS[0] <= RED4_TFS[-1] <= 15, _FK.RED4_LINES
EXF_SUFFIX = int(_FK.EXF_SUFFIX)                         # HIS 1121: the seven-band suffix on the (exf) codes too, 1 on
ORACLE_R_CFG = str(_FK.ORACLE_R_CFG)                     # HIS 1121: the ws{TF}r config, 'db' or 'k_len,rsi,stc'
UNTAG50 = int(_FK.UNTAG50)                               # HIS 1120: "-" on the counter side of 50, 1 on
#   HIS 1120 "hold 1, tolerance 0.67", towards/away only: None = v4's banked pair, else (tolerance r-points, hold bars)
_tl = str(_FK.TA_LIFT)
TA_LIFT = None if _tl == 'v4' else (float(_tl.split(',')[0]), int(_tl.split(',')[1]))
assert _tl == 'v4' or len(_tl.split(',')) == 2, 'W_FDM3_TA_LIFT is "v4" or "tolerance,hold": %r' % _tl
assert _FK.RULED_OK or os.environ.get('W_FDM3_EXPERIMENT') == '1', \
    'the fdm3 knobs are off the bank; the oracle will not read them'
