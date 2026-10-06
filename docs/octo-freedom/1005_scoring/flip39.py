"""CONF with-trend flipped — Joe 1005: "CONF with-trend is reading upside down - this is the stage 2
we talked of earlier ... flip the LONG with SHORT and recreate".

STAGE 2, Joe's words from the dev genesis: "flipping early-reversal-octa-sig-events to a
continuation trade (pyramid)". So for every branch-D confluence graded with-trend (Mage net AWAY
from dr), the TRADE SIDE is the opposite of the dr-bias side. against-trend is untouched.

THREE ENTRIES MEASURED, because Joe asked "do you want to apply your suggestion to walk to the
extrema for a better position?":
  A  as published  side = dr-bias,  entry = the octo-sig bar
  B  FLIPPED       side = opposite, entry = the octo-sig bar          <- fully causal
  C  FLIPPED       side = opposite, entry = the mtd step-1 extrema    <- causal ONLY where the
                   extrema is at or after the signal bar. Where the extrema is in the PAST the bar
                   is gone and the entry cannot be taken: reported as a REFERENCE, flagged per row.
Scoring is unchanged: swing_detect 0.70 %, swing-to-pivot, MAE = max(0, adverse), no stop.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, os, contextlib
import numpy as np
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    import score39 as S
ROWS, PX, ts = S.ROWS, S.PX, S.ts
THR = 0.70; PCT = 0.70
H, L = S.CACHE[PCT]
U = S.U

def sc(k, d):
    f, a, j = S.score(k, d, H, L)
    if f is None: return None
    entry = float(PX[k]); seg = PX[k:j + 1]
    adv = (seg - entry) / entry * 100.0 if d > 0 else (entry - seg) / entry * 100.0
    hit = np.flatnonzero(np.isfinite(adv) & (adv >= THR))
    return {'mfe': f, 'mae': a, 'exit': j,
            'stop': (ts[k + int(hit[0])] - ts[k]) / 60000.0 if hit.size else None,
            'hold': (ts[j] - ts[k]) / 60000.0}

side = lambda d: 'SHORT' if d > 0 else 'LONG'
for r in ROWS:
    d = r['d']; k = r['k']
    # REPINNED TO `towards` 1006. Joe: *"understood - make them towards"*, after identifying the
    # flip population from the table itself: *"979 (os_pk) and more are `CONFLUENCE with-trend`
    # which is our agreed pyramid signal"*. with-trend is net TOWARDS dr under the 1006 label
    # correction, so the flip is `not away`. Measured before repinning, 53 towards rows:
    #   MAE mean  0.921 -> 0.403   MFE mean  0.799 -> 1.189   rows over 0.70  19 -> 11
    # The 175 `away` rows barely move when flipped (MAE 0.603 -> 0.452), which is why towards is
    # the population that behaves like a pyramid signal.
    # CONSEQUENCE, STATED: stop 0.95 and risk 1.5 % were derived with the flip on `away`. They are
    # PROVISIONAL until re-derived. Joe 1006: no P&L activity for now, so nothing here is re-run.
    r['flip'] = (r['status'] == 'CONFLUENCE' and not r.get('D', {}).get('away', True))
    r['deff'] = -d if r['flip'] else d                     # +1 = SHORT in the scorer
    r['A'] = sc(k, d)
    r['B'] = sc(k, r['deff'])
    ex = r['m'].get('ex')
    r['exlag'] = (ts[ex] - ts[k]) / 60000.0 if ex is not None else None
    r['C'] = sc(ex, r['deff']) if ex is not None else None

WT = [r for r in ROWS if r['flip']]
print('# DAY %s | %d octo-sig' % (S.DAY, len(ROWS)))
print()
print('## THE with-trend ROWS — A as published vs B flipped, both entering at the octo-sig bar')
print('| octo-sig | dr | side A | MAE A | MFE A | side B (flipped) | MAE B | MFE B | B hold min | B 0.70 hit at | B verdict |')
print('|' + '---|' * 11)
for r in sorted(WT, key=lambda x: x['lbl']):
    a, b = r['A'], r['B']
    print('| %s | %+d | %s | %.3f | %.3f | **%s** | %.3f | %.3f | %.1f | %s | %s |'
          % (r['lbl'], r['d'], side(r['d']), a['mae'], a['mfe'], side(r['deff']), b['mae'], b['mfe'],
             b['hold'], ('%.1f m' % b['stop']) if b['stop'] is not None else '—',
             'clean' if b['mae'] <= THR else '**heat**'))
print()
print('| entry | clean of %d | heat of %d | MAE med | MFE med | MFE>MAE |' % (len(WT), len(WT)))
print('|' + '---|' * 6)
for tag in ('A', 'B'):
    g = [r[tag] for r in WT]
    print('| %s | %d | %d | %.3f | %.3f | %d |' % (
        'A as published (dr-bias side)' if tag == 'A' else 'B flipped (stage 2)',
        sum(1 for x in g if x['mae'] <= THR), sum(1 for x in g if x['mae'] > THR),
        float(np.median([x['mae'] for x in g])), float(np.median([x['mfe'] for x in g])),
        sum(1 for x in g if x['mfe'] > x['mae'])))

print()
print('## C — ENTERING AT THE mtd EXTREMA. Is that bar even available at the signal?')
print('| octo-sig | step 1 | extrema | lag from the signal | takeable? | MAE C | MFE C | vs MAE B |')
print('|' + '---|' * 8)
for r in sorted(WT, key=lambda x: x['lbl']):
    c, b = r['C'], r['B']
    ok = r['exlag'] >= 0
    print('| %s | %s | %s | %+.1f m | %s | %.3f | %.3f | %+.3f |'
          % (r['lbl'], r['m']['src'], U(r['m']['ex']), r['exlag'],
             'YES' if ok else '**NO — bar is in the past**', c['mae'], c['mfe'], c['mae'] - b['mae']))
tk = [r for r in WT if r['exlag'] >= 0]
print()
print('| population | n | clean | heat | MAE med | MFE med |')
print('|' + '---|' * 6)
for tag, g, lab in (('B', WT, 'B flipped, signal-bar entry (all)'),
                    ('C', WT, 'C flipped, extrema entry (all; see takeable column)'),
                    ('B', tk, 'B flipped, signal bar — the %d takeable-extrema rows' % len(tk)),
                    ('C', tk, 'C flipped, extrema — the %d takeable rows only' % len(tk))):
    v = [r[tag] for r in g]
    if not v: print('| %s | 0 | — | — | — | — |' % lab); continue
    print('| %s | %d | %d | %d | %.3f | %.3f |' % (lab, len(v), sum(1 for x in v if x['mae'] <= THR),
          sum(1 for x in v if x['mae'] > THR), float(np.median([x['mae'] for x in v])),
          float(np.median([x['mfe'] for x in v]))))

print()
print('## THE DAY RECREATED — with-trend flipped, entry at the octo-sig bar (option B)')
ORD = {'CONFLUENCE': 0, 'BLOCKED': 1, 'OPEN': 2}
print('| octo-sig | dr | side | status | route | MAE% | MFE% | 0.70 hit at | verdict vs the 0.70 line |')
print('|' + '---|' * 9)
for r in sorted(ROWS, key=lambda x: (ORD[x['status']], x['grade'], x['lbl'])):
    b = r['B']
    st = r['status'] + (' · ' + r['grade'] + (' · STAGE 2 FLIP' if r['flip'] else '') if r['status'] == 'CONFLUENCE' else '')
    if r['status'] == 'CONFLUENCE': v = 'correct' if b['mae'] <= THR else '**let heat through**'
    elif r['status'] == 'BLOCKED':  v = 'correct' if b['mae'] > THR else '**over-blocked**'
    else:                           v = 'open -> **block**' if b['mae'] > THR else 'open -> **fire**'
    print('| %s | %+d | %s | %s | %s | %.3f | %.3f | %s | %s |'
          % (r['lbl'], r['d'], side(r['deff']), st, r['m']['route'], b['mae'], b['mfe'],
             ('%.1f m' % b['stop']) if b['stop'] is not None else '—', v))

print()
print('## THE SCORE, RECREATED')
print('| mech says | n | MAE <= 0.70 | MAE > 0.70 | reading |')
print('|' + '---|' * 5)
for lab, sel, good in (('CONFLUENCE · with-trend · STAGE 2 FLIP', lambda r: r['flip'], 'le'),
                       ('CONFLUENCE · against-trend', lambda r: r['status'] == 'CONFLUENCE' and r['grade'] == 'against-trend', 'le'),
                       ('BLOCKED (mtd.r2)', lambda r: r['status'] == 'BLOCKED', 'gt'),
                       ('OPEN · neither', lambda r: r['status'] == 'OPEN' and r['m']['route'] == 'neither', None),
                       ('OPEN · D no fire', lambda r: r['status'] == 'OPEN' and r['grade'] == 'band claimed', None),
                       ('OPEN · no r block', lambda r: r['grade'] == 'no r block', None)):
    g = [r for r in ROWS if sel(r)]
    lo_ = sum(1 for r in g if r['B']['mae'] <= THR); hi_ = len(g) - lo_
    rd = ('%d of %d correct' % (lo_, len(g))) if good == 'le' else (
         ('%d of %d correct' % (hi_, len(g))) if good == 'gt' else '%d would block, %d would fire' % (hi_, lo_))
    print('| %s | %d | %d | %d | %s |' % (lab, len(g), lo_, hi_, rd))
cur = sum(1 for r in ROWS if r['status'] == 'CONFLUENCE' and r['B']['mae'] <= THR) + \
      sum(1 for r in ROWS if r['status'] == 'BLOCKED' and r['B']['mae'] > THR)
allr = cur + sum(1 for r in ROWS if r['status'] == 'OPEN' and r['B']['mae'] > THR)
nv = sum(1 for r in ROWS if r['status'] != 'OPEN')
print('| agreement now, the %d rows with a verdict | | | | %d of %d |' % (nv, cur, nv))
print('| agreement with all three OPEN rulings | | | | %d of %d |' % (allr, len(ROWS)))
print()
print('| ruling | rows | right | wrong | net |')
print('|' + '---|' * 5)
for lab, sel in (('`neither` = BLOCK', lambda r: r['m']['route'] == 'neither'),
                 ('`no fire` = BLOCK', lambda r: r['status'] == 'OPEN' and r['grade'] == 'band claimed'),
                 ('D empty block = BLOCK', lambda r: r['grade'] == 'no r block')):
    g = [r for r in ROWS if sel(r)]
    ok = sum(1 for r in g if r['B']['mae'] > THR)
    print('| %s | %d | %d | %d | %+d |' % (lab, len(g), ok, len(g) - ok, ok - (len(g) - ok)))
