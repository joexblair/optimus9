"""ENTRY A/B — col1 (as built) vs col2 (the jig's sanctioned 3-leg walk) at MATCHED lookback width.
Joe 1005: *"instead of moved bar, show us the MAE/MFE diff if any"*.

THE TWO ENTRIES, same mechanic knobs, only the leg STRUCTURE differs:
  col1  report_leash_walk as it stands. `rev_lookback_mask(sig, sig_conf, n, 48)` -> a per-bar
        mask; the walk fires at the first bar the mask is true. `dwell_ok` and `rev` unread.
  col2  `jig.mage_rev_walk(legs, dr, frm, sig_lookback=48)` — the producer's OWN ordered walk:
        first dwell_ok >= frm, then first rev at or after it (THE ANCHOR), then the earliest sig
        above the floor anchor-48. Returns that sig's `sig_conf`.

MATCHED WIDTH. col1's `rev_lookback` is 48 bars = 240 s, so col2 runs at `sig_lookback` 48 bars.
Joe 1005 caught the mismatch: *"col1 shows that a lookback is used ... col2 doesn't show a
lookback, so we're not really comparing like with like"*. At 0 the two differ by the window, not
the mechanic. The shapes still differ — col1 is a WINDOW bounded on the candidate bar, col2 a
FLOOR on the anchor bar, unbounded forward — and that is the thing being measured here.

`frm` = THE PRECONDITIONS-COMPLETE BAR, obtained by running the same walk with the rev mask replaced
by ones. With the rev gate removed EVERY bar whose arm+turn+qualify+race hold is emitted, so the
all-true EMITTED set is exactly the precondition-satisfied set, and a reported run is a maximal
CONTIGUOUS block of it. So for a col1 event at bar k:

    frm = the FIRST bar of the all-true run whose [first, last] CONTAINS k

PAIRING FIXED 1005. The first version keyed `frm` on the ARM BAR. Removing the rev gate merges runs,
so several col1 events sharing one arm all inherited that merged run's single early first bar - 09-29
12:41:00 and 13:12:15 both resolved to 06:59:45, and 90 % of col2's bars landed EARLIER than col1's
(median -40.7 min, worst -437.3 min) when the 48-bar floor allows at most -4.0. Containment is the
right key and needs no change to `step`: a run that contains k began where the preconditions became
satisfied in the contiguous stretch through k. If they lapse and re-satisfy inside one col1 episode
the run splits, so containment stays single-valued.

WHAT THIS CANNOT SHOW, stated: the population is the arms the CURRENT walk already fires on. Runs
that only col2 would create, or that it would destroy, need `step` rewired to call the producer's
walk — that is concretion #2 and Joe has not ruled it. This is an offline comparison with the
sanctioned producer called UNMODIFIED.

SCORING: score39's own producer, unchanged. swing_detect 0.70 %, swing-to-pivot, MAE = max(0,
adverse), NO STOP. Side = dr-bias, dr +1 = SHORT. One set, all 17 days — Joe 1005 dropped FIT/TEST.
"""
import os as _os, sys, io, contextlib, datetime as dt
import numpy as np
_HERE = _os.path.dirname(_os.path.abspath(__file__))
sys.path.insert(0, _HERE)
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
import upstream as UP
from optimus9.analysis.jig import ws1mage_rev, mage_rev_walk

RLW = UP.RLW
REAL = RLW.rev_lookback_mask
ONES = lambda s, c, n, l: np.ones(int(n), bool)
DAYS = ['2026-07-23', '2026-07-25', '2026-08-06', '2026-08-20', '2026-08-30', '2026-09-14',
        '2026-09-17', '2026-09-25', '2026-09-26', '2026-09-27', '2026-09-28', '2026-09-29',
        '2026-09-30', '2026-10-01', '2026-10-02', '2026-10-03', '2026-10-04']

def runs(day):
    sys.argv = ['x', '--day', day, '--tape-end', _os.environ.get('LG_TAPE_END', '2026-10-05')]
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        with contextlib.redirect_stderr(io.StringIO()):
            try: RLW.main()
            except SystemExit: pass
    out = []
    for l in buf.getvalue().splitlines():
        if l.startswith('R|') and not l.startswith('R|run'):
            f = l.split('|')
            out.append(dict(first=f[2], last=f[3], arm=f[6], dr=int(f[5])))
    return out

RLW.rev_lookback_mask = REAL
_ = runs(DAYS[0])                         # force the Rig load before anything is timed
R = UP._RIG
ts = np.asarray(R.ts, np.int64)
LB = int(R.C['lookback_s']) // 5
SL = R.C['sig_line']
LEGS = ws1mage_rev(R.lines['ws1']['Mage'], R.lines[SL.replace('Mage', '')]['Mage'], R.hi, R.lo,
                   dwell=int(R.C['dwell']), rev_wob=int(R.C['rev_wob']),
                   hold=int(R.C['boundary_xwob']))
H, L = SC.pivots(0.70)
K = lambda day, hms: int(np.searchsorted(ts, int(dt.datetime.strptime(day + ' ' + hms,
      '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp() * 1000)))
U = lambda i: dt.datetime.fromtimestamp(int(ts[int(i)]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')

print('# col1 rev_lookback %d bars = %s s | col2 sig_lookback %d bars (MATCHED)' % (LB, R.C['lookback_s'], LB))
print('# rig.C dwell=%d | rev_wob=%d | hold=%d | sig_line=%s | fences %.0f/%.0f'
      % (int(R.C['dwell']), int(R.C['rev_wob']), int(R.C['boundary_xwob']), SL, R.hi, R.lo))
print('# scoring: score39.score, swing 0.70, swing-to-pivot, MAE=max(0,adverse), NO STOP, dr+1=SHORT')
print()
ROWS = []
for day in DAYS:
    RLW.rev_lookback_mask = REAL; A = runs(day)
    RLW.rev_lookback_mask = ONES; B = runs(day)
    RLW.rev_lookback_mask = REAL
    iv = sorted((K(day, r['first']), K(day, r['last'])) for r in B)   # all-true runs, as bar spans
    unpaired = 0
    for r in A:
        k1 = K(day, r['first']); d = r['dr']
        hit = [a for a, b in iv if a <= k1 <= b]
        frm = max(hit) if hit else k1
        if not hit: unpaired += 1
        k2 = mage_rev_walk(LEGS, d, frm, sig_lookback=LB)
        f1 = SC.score(k1, d, H, L)
        f2 = SC.score(int(k2), d, H, L) if k2 is not None else (None, None, None)
        ROWS.append(dict(day=day, arm=r['arm'], dr=d, b1=k1, b2=k2,
                         mfe1=f1[0], mae1=f1[1], mfe2=f2[0], mae2=f2[1]))
    print('# %s done, %d runs, %d unpaired' % (day, len(A), unpaired), flush=True)

def agg(rs, key):
    v = [r[key] for r in rs if r[key] is not None]
    return (len(v), float(np.mean(v)) if v else float('nan'),
            float(np.median(v)) if v else float('nan'), float(np.sum(v)) if v else float('nan'))

print()
print('## PER DAY — MAE / MFE, col1 vs col2 at matched width')
print('| day | events | col2 fires | same bar | MAE col1 | MAE col2 | MFE col1 | MFE col2 |')
print('|' + '---|' * 8)
for day in DAYS:
    rs = [r for r in ROWS if r['day'] == day]
    n2 = sum(1 for r in rs if r['b2'] is not None)
    sm = sum(1 for r in rs if r['b2'] is not None and int(r['b2']) == r['b1'])
    a1 = agg(rs, 'mae1'); a2 = agg(rs, 'mae2'); f1 = agg(rs, 'mfe1'); f2 = agg(rs, 'mfe2')
    print('| %s | %d | %d | **%d** | %.3f | %.3f | %.3f | %.3f |'
          % (day, len(rs), n2, sm, a1[1], a2[1], f1[1], f2[1]))
print()
print('## ALL 17 DAYS, ONE SET')
print('| measure | col1 as built | col2 jig 3-leg | diff |')
print('|---|---|---|---|')
same = [r for r in ROWS if r['b2'] is not None and r['mae1'] is not None and r['mae2'] is not None]
for key, nm in (('mae', 'MAE %'), ('mfe', 'MFE %')):
    x = [r[key + '1'] for r in same]; y = [r[key + '2'] for r in same]
    print('| %s mean | **%.4f** | **%.4f** | **%+.4f** |' % (nm, np.mean(x), np.mean(y), np.mean(y) - np.mean(x)))
    print('| %s median | %.4f | %.4f | %+.4f |' % (nm, np.median(x), np.median(y), np.median(y) - np.median(x)))
    print('| %s total | %.3f | %.3f | **%+.3f** |' % (nm, np.sum(x), np.sum(y), np.sum(y) - np.sum(x)))
print('| scored events | %d | %d | — |' % (len(same), len(same)))
print('| events where col2 does NOT fire | %d | — | — |' % sum(1 for r in ROWS if r['b2'] is None))
print('| events on the SAME bar | **%d of %d** | — | — |'
      % (sum(1 for r in ROWS if r['b2'] is not None and int(r['b2']) == r['b1']), len(ROWS)))
print()
print('## SEPTEMBER + OCTOBER ONLY, 12 days — the set Joe reduced the report to')
print('| measure | col1 as built | col2 jig 3-leg | diff |')
print('|---|---|---|---|')
so = [r for r in same if r['day'] >= '2026-09-01']
for key, nm in (('mae', 'MAE %'), ('mfe', 'MFE %')):
    x = [r[key + '1'] for r in so]; y = [r[key + '2'] for r in so]
    print('| %s mean | **%.4f** | **%.4f** | **%+.4f** |' % (nm, np.mean(x), np.mean(y), np.mean(y) - np.mean(x)))
    print('| %s median | %.4f | %.4f | %+.4f |' % (nm, np.median(x), np.median(y), np.median(y) - np.median(x)))
    print('| %s total | %.3f | %.3f | **%+.3f** |' % (nm, np.sum(x), np.sum(y), np.sum(y) - np.sum(x)))
print('| scored events | %d | %d | — |' % (len(so), len(so)))
sm12 = sum(1 for r in ROWS if r['day'] >= '2026-09-01' and r['b2'] is not None and int(r['b2']) == r['b1'])
n12 = sum(1 for r in ROWS if r['day'] >= '2026-09-01')
print('| events on the SAME bar | **%d of %d** | — | — |' % (sm12, n12))
print()
print('## THE EVENTS WHERE THE BAR MOVED — every one, chronological')
print('| day | col1 bar | col2 bar | shift min | MAE col1 | MAE col2 | MAE diff | MFE col1 | MFE col2 | MFE diff |')
print('|' + '---|' * 10)
mv = [r for r in ROWS if r['b2'] is not None and int(r['b2']) != r['b1']]
for r in mv:
    md = (r['mae2'] - r['mae1']) if (r['mae1'] is not None and r['mae2'] is not None) else float('nan')
    fd = (r['mfe2'] - r['mfe1']) if (r['mfe1'] is not None and r['mfe2'] is not None) else float('nan')
    print('| %s | %s | %s | %+.1f | %s | %s | **%+.3f** | %s | %s | **%+.3f** |'
          % (r['day'], U(r['b1']), U(r['b2']), (ts[int(r['b2'])] - ts[r['b1']]) / 60000.0,
             '%.3f' % r['mae1'] if r['mae1'] is not None else '—',
             '%.3f' % r['mae2'] if r['mae2'] is not None else '—', md,
             '%.3f' % r['mfe1'] if r['mfe1'] is not None else '—',
             '%.3f' % r['mfe2'] if r['mfe2'] is not None else '—', fd))
print()
print('| moved events | %d of %d = %.1f%% |' % (len(mv), len(ROWS), 100.0 * len(mv) / max(1, len(ROWS))))
