"""The two fdm3 pivot knobs, readable from the oracle's own directory.

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

PIVOT_TF = int(_FK.ORAC_PIVOT_TF)
PIVOT_DWELL_S = int(_FK.ORAC_PIVOT_DWELL_S)
OOB_JUMP = int(_FK.ORAC_OOB_JUMP)
SMALL_TRADE_MAX_TOEXF = int(_FK.SMALL_TRADE_MAX_TOEXF)    # HIS 1119 `fdm3-small-trade-max-toexf`
assert _FK.RULED_OK or os.environ.get('W_FDM3_EXPERIMENT') == '1', \
    'the fdm3 knobs are off the bank; the oracle will not read them'
