"""ws30r reversals on a named side, and ws10x crossings UNDER a boundary, at three wobs.

THE WOB CHANGES THE EVENT SET, NOT ONLY THE STAMP. jig.lift_off takes wob as an argument and drops
a lift-off whose state re-pins inside the hold, so each wob is a fresh lift_off call, never a
shifted stamp. jig._Causal.cross_wob is the same: the run must reach n with no bar back across.

THE BOUNDARY LEVEL IS NOT RULED. Joe named "boundary", which is jig.cross_wob's own word for its
`level` argument. build_s46_momo.py's `b` leg uses HI/LO for it; the mom fence pair and 50 are the
other levels in the bank. Every one of them is printed, the choice is Joe's.

THE CROSS DIRECTION IS HIS WORD, NOT THE SIDE'S MIRROR. He has asked for UNDER on a high side,
UNDER on a low side and OVER on a low side, so the direction is its own argument and is never
derived from `side`.

usage: wob_7_11_17.py '<YYYY-MM-DD HH:MM:SS>' <high|low> <over|under>
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
from optimus9.analysis.jig import lift_off, _Causal

WOBS = (7, 11, 17)
A = ln.K(sys.argv[1])
SIDE = {'high': +1, 'low': -1}[sys.argv[2]]
XDIR = {'over': +1, 'under': -1}[sys.argv[3]]
XW = sys.argv[3].upper()
LEVELS = (K.OOB_HI, K.RMOM_FNC, 50.0, 100.0 - K.RMOM_FNC, K.OOB_LO)
C = _Causal(None)
r30, x10 = ln.line('ws30r'), ln.line('ws10x')
print('tape bars %d | A %s | the last tape bar %s | the reversal side %s | the cross direction %s'
      % (ln.N, ln.U(A), ln.U(ln.N - 1), sys.argv[2], sys.argv[3]))
print()
print('| the setting | value | what it is |')
print('|---|---|---|')
print('| the oob boundary, high | %.1f | a line is out of bounds at or above this |' % K.OOB_HI)
print('| the oob boundary, low | %.1f | a line is out of bounds at or below this |' % K.OOB_LO)
print('| the mom fence, high | %.1f | the ex-fence level |' % K.RMOM_FNC)
print('| the mom fence, low | %.1f | the ex-fence level, mirrored |' % (100.0 - K.RMOM_FNC))
print('| the midline | 50.0 | the bank\'s third level |')
print('| lattice points | %d | points a lift-off needs |' % K.LIFT_PTS)
print('| lattice tolerance | %.1f | how far off the lattice a point may sit |' % K.LIFT_TOL)
print('| lattice gap, ws30 | %d bars = %d s | %.1f bars per minute of timeframe |'
      % (K.gap_for(30), K.gap_for(30) * 5, K.GAP_PER_TF))
print('| the banked wob | %d | Joe is asking for 7, 11 and 17 instead |' % K.LIFT_WOB)
print()
print('## ws30r, %s-side reversals, the first two at or after the start bar' % sys.argv[2].upper())
print()
print('| the wob | which | the raw lift-off bar | ws30r there | the stamp = raw + wob - 1 | the lag |')
print('|---|---|---|---|---|---|')
for w in WOBS:
    L = [int(b) for b in lift_off(r30, SIDE, K.LIFT_PTS, K.gap_for(30), K.LIFT_TOL, w) if b >= A]
    for i, nm in ((0, 'first'), (1, 'second')):
        if i >= len(L):
            print('| %d | %s | NONE to the end of the tape | - | - | - |' % (w, nm)); continue
        b = L[i]; st = b + w - 1
        print('| %d | %s | %s | %.2f | %s | +%d bars = +%d s |'
              % (w, nm, ln.U(b), r30[b], ln.U(st), w - 1, (w - 1) * 5))
print()
print('## ws10x, crossings %s a boundary, the first two at or after the start bar' % XW)
print()
print('| the boundary | the wob | which | the bar before the cross | ws10x there | the raw cross bar | ws10x there | the confirm bar | ws10x there | the lag |')
print('|---|---|---|---|---|---|---|---|---|---|')
for lvl in LEVELS:
    for w in WOBS:
        f = C.cross_wob(x10, lvl, XDIR, w)
        e = np.flatnonzero(f[1:] & ~f[:-1]) + 1
        if f[0]:
            e = np.r_[0, e]
        e = [int(q) for q in e if q - w + 1 >= A]
        for i, nm in ((0, 'first'), (1, 'second')):
            if i >= len(e):
                print('| %.1f | %d | %s | NONE to the end of the tape | - | - | - | - | - | - |'
                      % (lvl, w, nm)); continue
            cf = e[i]; b = cf - w + 1
            print('| %.1f | %d | %s | %s | %.2f | %s | %.2f | %s | %.2f | +%d bars = +%d s |'
                  % (lvl, w, nm, ln.U(b - 1), x10[b - 1], ln.U(b), x10[b],
                     ln.U(cf), x10[cf], w - 1, (w - 1) * 5))
