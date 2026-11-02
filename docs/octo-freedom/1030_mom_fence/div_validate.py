"""HIS 1101 DIVERGENCE EXAMPLES, and whether the mech exhausts 2026-09-03 04:37:55.

His examples: *"--bullish 2324, floater 2312 / --bullish 0437, floater 0418"*. Both are BULLISH,
so both rev-trade only against a LOW target side - his 1101 table.
"""
import io, os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` puts stderr back whatever happens.
#   Without that, an import error inside it produces an empty file and exit 1 with no diagnosis.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import v4_lineage2 as L2
    import ln
    from v4_backstop_trades import prices
#   THE PRODUCER LIVES IN THE JIG, which is where v4_lineage2.py imports it from. I first wrote
#   `optimus9.compute.anchor_floater`, a module that does not exist, and the run exited 1 with BOTH
#   output files empty - the import sat inside the stderr swallow below, so the traceback went into
#   a StringIO and was lost. The swallow is now restored BEFORE anything that can fail.
    from optimus9.analysis.jig import anchor_floater
finally:
    sys.stderr = _e
close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
print('# HIS 1101 DIVERGENCE EXAMPLES | LIN2_DIV_ON %d | LIN2_DIV_PM_FLOOR %.1f (PM disabled)'
      % (K.LIN2_DIV_ON, K.LIN2_DIV_PM_FLOOR))
print('# the verdict is +1 bearish / -1 bullish; the target side is +1 high / -1 low')
print('# his table: a rev-trade when verdict == target side')
print()
print('| his example | the bar | target side | the verdict | its name | the raw state |'
      ' the anchor bar | the floater bar | his floater | rev-trade? |')
print('|---|---|---|---|---|---|---|---|---|---|')
ROWS = [('bullish 2324, floater 2312', '2026-09-03 23:24:00', '2026-09-03 23:12:00'),
        ('bullish 0437, floater 0418', '2026-09-03 04:37:00', '2026-09-03 04:18:00'),
        ('the 0437 cadence bar itself', '2026-09-03 04:37:55', '2026-09-03 04:18:00')]
for lbl, t, fl in ROWS:
    k = ln.K(t)
    for sd in (-1, +1):
        v = L2.div_verdict(CL, close, sd, k)
        st = L2.div_state(CL, close, sd, k)
        got = anchor_floater(np.asarray(CL['r'][1], float), np.asarray(close, float), sd, k)
        ab = ln.U(int(got['anchor'][0])) if got else '-'
        fb = ln.U(int(got['floater'][0])) if (got and got.get('floater')) else '-'
        nm = 'none' if v is None else ('+1 bearish' if v > 0 else '-1 bullish')
        rev = (v is not None and int(v) == int(sd))
        print('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |'
              % (lbl if sd < 0 else '', t, 'low' if sd < 0 else 'high',
                 'None' if v is None else '%+d' % v, nm, st, ab[11:] if ab != '-' else '-',
                 fb[11:] if fb != '-' else '-', fl[11:], 'YES' if rev else 'no'))
