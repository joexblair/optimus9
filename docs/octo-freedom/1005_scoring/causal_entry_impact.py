"""THE COST OF PINNING THE ENTRY TO THE INFORMATION BAR.

THE DEFECT, 1006. score39's own docstring says the 1005 design pinned the entry to the mtd walk's
QUALIFYING bar - *"THE ENTRY BAR MOVES TO THE QUALIFYING BAR"* - which is what made the forward walk
causal. Joe's 1006 stamp ruling pointed the stamp at the g5extrema, and `octosig_db.py` ended up
with `entry = max(octo_sig_bar, ex)`, dropping the qualifying bar `kw` entirely. `classify` still
RETURNS kw and walk_bars; nothing read them.

THE FIX: entry = max(octo_sig_bar, kw, ex). Joe 1006: *"we're walking a forward loop, so the use of
`IF this bar has condition THEN...` is an easy way out of lookahead"* - in the production loop the
entry lands on the qualifying bar by construction, and this is the backtest's equivalent.

THIS FILE ONLY MEASURES. It changes no mech and no table.
"""
import os, io, contextlib, re
import numpy as np
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

DAYS = os.environ.get('LG_DAYS',
    '2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
    '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
H, L = SC.pivots(float(SC.LG['swing'])); BLOCK = float(SC.LG['mae_block'])

rows = []
for day in DAYS:
    p = os.path.join('octosig', '%s.out' % day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f = ln.rstrip('\n').split('|')
        if len(f) < 7 or not re.match(r'^\d\d:\d\d:\d\d$', f[2]): continue
        k = SC.K('%s %s' % (day, f[2]))
        r = SC.classify(k, f[2])
        D = r.get('D') or {}
        d = int(SC.DRv[k])
        if d == 0: continue
        ex = r['m'].get('ex'); ex = int(ex) if ex is not None else k
        kw = int(r['kw'])
        old = max(k, ex)                      # what octosig_db stamps today
        new = max(k, kw, ex)                  # the entry pinned to the information bar
        flip = (r['status'] == 'CONFLUENCE' and not D.get('away', True)) or D.get('why') == 'no r block'
        dt = -d if flip else d
        fo, ao, _ = SC.score(old, dt, H, L)
        fn, an, _ = SC.score(new, dt, H, L)
        rows.append(dict(day=day, sig=f[2], moved=(new != old), bars=(new - old),
                         secs=(int(SC.ts[new]) - int(SC.ts[old])) / 1000.0,
                         status=r['status'], grade=r['grade'], why=D.get('why'),
                         side=('LONG' if dt < 0 else 'SHORT'),
                         mo=ao, fo=fo, mn=an, fn=fn))

n = len(rows); mv = [r for r in rows if r['moved']]
print('# PINNING THE ENTRY TO THE INFORMATION BAR — the cost   %s' % SC.LG_KEY)
print('\n| | rows | of %d | days |' % n); print('|---|---|---|---|')
print('| total octo-sigs | %d | 100%% | %d |' % (n, len({r['day'] for r in rows})))
print('| **entry moves** | **%d** | **%.1f%%** | %d |'
      % (len(mv), 100.0*len(mv)/n, len({r['day'] for r in mv})))
if mv:
    s = sorted(r['secs'] for r in mv)
    print('\n| entry shift, seconds | value |'); print('|---|---|')
    print('| min | %.0f |' % s[0]); print('| median | %.0f |' % s[len(s)//2]); print('| max | %.0f |' % s[-1])

ok = lambda r, mk, fk: (r[mk] is not None and r[fk] is not None)
def blk(sub, mk, fk, lbl):
    g = [r for r in sub if ok(r, mk, fk)]
    if not g: return None
    mm = sorted(r[mk] for r in g); ff = [r[fk] for r in g]
    return (lbl, len(g), mm[len(mm)//2], sorted(ff)[len(ff)//2], sum(ff),
            sum(1 for r in g if r[fk] > r[mk]), sum(1 for r in g if r[mk] > BLOCK))

print('\n# THE MOVED ROWS ONLY — before and after')
print('| entry | rows | median MAE | median MFE | sum MFE | MFE>MAE | MAE>%.2f |' % BLOCK)
print('|---|---|---|---|---|---|---|')
for mk, fk, lbl in (('mo', 'fo', 'at the octo-sig bar (today)'), ('mn', 'fn', 'at the information bar (causal)')):
    b = blk(mv, mk, fk, lbl)
    if b: print('| %s | %d | %.4f | %.4f | %+.3f | %d of %d | %d |' % (b[0], b[1], b[2], b[3], b[4], b[5], b[1], b[6]))

print('\n# ALL %d ROWS — before and after' % n)
print('| entry | rows | median MAE | median MFE | sum MFE | MFE>MAE | MAE>%.2f |' % BLOCK)
print('|---|---|---|---|---|---|---|')
for mk, fk, lbl in (('mo', 'fo', 'at the octo-sig bar (today)'), ('mn', 'fn', 'at the information bar (causal)')):
    b = blk(rows, mk, fk, lbl)
    if b: print('| %s | %d | %.4f | %.4f | %+.3f | %d of %d | %d |' % (b[0], b[1], b[2], b[3], b[4], b[5], b[1], b[6]))

if mv:
    print('\n# EVERY MOVED ROW')
    print('| day | octo-sig | +s | status | grade | side | MAE now | MFE now | MAE causal | MFE causal |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    fm = lambda v: ('%.4f' % v) if v is not None else '—'
    for r in sorted(mv, key=lambda x: (x['day'], x['sig'])):
        print('| %s | %s | %+.0f | %s | %s | %s | %s | %s | %s | %s |'
              % (r['day'], r['sig'], r['secs'], r['status'], r['grade'], r['side'],
                 fm(r['mo']), fm(r['fo']), fm(r['mn']), fm(r['fn'])))
