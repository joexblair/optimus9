"""The all-39 table with BOTH confluence paths + the gap column. Joe 1005.
Imports score39 so every number comes from the one scorer, not a transcription."""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, numpy as np
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
import io, contextlib
_buf = io.StringIO()
with contextlib.redirect_stdout(_buf):
    import score39 as S
ROWS, PX, ts, Rl = S.ROWS, S.PX, S.ts, S.Rl
THR = 0.70        # = mae_cap 0.70, the stop already live inside trade_walk. Not a new knob.
PCT = 0.70        # the swing size. MEASURED: the separation knee (see score39.out)
H, L = S.CACHE[PCT]

for r in ROWS:
    f, a, j = S.score(r['k'], r['d'], H, L)
    r['mfe'], r['mae'], r['exit'] = f, a, j
    entry = float(PX[r['k']]); seg = PX[r['k']:j + 1]
    adv = (seg - entry) / entry * 100.0 if r['d'] > 0 else (entry - seg) / entry * 100.0
    hit = np.flatnonzero(np.isfinite(adv) & (adv >= THR))
    r['stop'] = (ts[r['k'] + int(hit[0])] - ts[r['k']]) / 60000.0 if hit.size else None
    D = r.get('D')
    r['one'] = bool(D and D['keep'] and len(D['keep']) == 1)
    r['deep'] = max((min(Rl[t][r['m']['ex']] - D['band'][0], D['band'][1] - Rl[t][r['m']['ex']])
                     for t in D['claim']), default=None) if D and D['claim'] else None

HOT = [r for r in ROWS if r['mae'] > THR]
B_OK = [r for r in ROWS if r['status'] == 'BLOCKED' and r['mae'] > THR]
nei = [r for r in ROWS if r['m']['route'] == 'neither']

def verdict(r):
    if r['status'] == 'CONFLUENCE': return 'correct' if r['mae'] <= THR else '**let heat through**'
    if r['status'] == 'BLOCKED':    return 'correct' if r['mae'] > THR else '**over-blocked**'
    return 'open -> **block**' if r['mae'] > THR else 'open -> **fire**'

def gap(r):
    D = r.get('D'); m = r['m']
    if r['status'] == 'CONFLUENCE':
        if r['one']:
            return ('band degenerate: ws%d alone, no TF can object' % D['keep'][0]) + \
                   (' — the ONE D lever that tracks heat (1-member 3 of 6 vs 2+ 4 of 14)' if r['mae'] > THR else '')
        if r['mae'] > THR:
            return 'no TF objected, nothing in D separates it — named unbuilt lever: the stall-contiguity gate (your 07:57 verdict)'
        return '—'
    if r['status'] == 'BLOCKED':
        if r['mae'] > THR: return '—'
        return 'mtd.r2 has no magnitude floor; net %+.2f vs the 2 correct blocks %s — no split' % (
            m['net'], '/'.join('%+.2f' % x['m']['net'] for x in B_OK))
    if m['route'] == 'neither':
        if r['mae'] > THR:
            return 'rule `neither`=BLOCK (5 of 7 take >%.2f); nearest miss %s by %.2f, distance does not sort the 7' % (
                THR, min(m['miss'], key=lambda n: abs((S.HI - m['v'][n]) if m['d'] > 0 else (m['v'][n] - S.LO))),
                abs(min((S.HI - m['v'][n]) if m['d'] > 0 else (m['v'][n] - S.LO) for n in m['miss'])))
        return 'rule `neither`=BLOCK costs this entry (MFE %.3f, no %.2f touch)' % (r['mfe'], THR)
    if D and not D['fire'] and D['claim']:
        if r['mae'] > THR:
            return 'rule `no fire`=BLOCK correct here; deepest claim %.2f inside the band' % r['deep']
        return 'rule `no fire`=BLOCK costs this entry (MFE %.3f); deepest claim %.2f inside' % (r['mfe'], r['deep'])
    return 'rule D empty-block=BLOCK correct here (MAE %.3f)' % r['mae']

def why(r):
    D = r.get('D'); m = r['m']
    if r['status'] == 'CONFLUENCE':
        return 'block %s, no claim; Mage %+.2f %s' % (
            ','.join('ws%d' % t for t in D['keep']), D['net'], 'AWAY' if D['away'] else 'TOWARDS')
    if r['status'] == 'BLOCKED':
        return '%s TOWARDS dr, net %+.2f; only %s allowed' % (
            'lifting' if m['net'] > 0 else 'falling', m['net'], m['allow'])
    if m['route'] == 'neither':
        return '%s AWAY from dr, net %+.2f; no rule' % ('lifting' if m['net'] > 0 else 'falling', m['net'])
    if D and D['claim']:
        return 'band [%.2f, %.2f] claimed by %s' % (D['band'][0], D['band'][1],
            ','.join('ws%d' % t for t in D['claim']))
    return 'mtd 4/4, then no ws1..ws12 r is ex-fence at the extrema'

ORD = {'CONFLUENCE': 0, 'BLOCKED': 1, 'OPEN': 2}
print('## THE 39 OCTO-SIG OF 09-25 — both confluence paths, scored on swing_detect %.2f%%, blocked at MAE > %.2f%%' % (PCT, THR))
print()
print('| octo-sig | dr | side | status | route | mtd oob | why it landed there | MAE% | MFE% | 0.70 hit at | verdict vs the ' + ('%.2f' % THR) + ' line | the gap that would close it |')
print('|' + '---|' * 12)
for r in sorted(ROWS, key=lambda x: (ORD[x['status']], x['grade'], x['lbl'])):
    m = r['m']
    st = r['status'] + (' · ' + r['grade'] if r['status'] == 'CONFLUENCE' else '')
    oob = '4/4' if m.get('noob') == 4 else '%d/4 (%s out)' % (m.get('noob', 0), ','.join(m.get('miss', [])))
    print('| %s | %+d | %s | %s | %s | %s | %s | %.3f | %.3f | %s | %s | %s |'
          % (r['lbl'], r['d'], r['side'], st, m['route'], oob, why(r), r['mae'], r['mfe'],
             ('%.1f m' % r['stop']) if r['stop'] is not None else '—', verdict(r), gap(r)))

print()
print('## THE SCORE — the mech has a verdict on 25 of 39')
print('| mech says | n | MAE <= ' + ('%.2f' % THR) + ' | MAE > ' + ('%.2f' % THR) + ' | reading |')
print('|' + '---|' * 5)
for lab, sel, good in (('CONFLUENCE · with-trend', lambda r: r['status'] == 'CONFLUENCE' and r['grade'] == 'with-trend', 'le'),
                       ('CONFLUENCE · against-trend', lambda r: r['status'] == 'CONFLUENCE' and r['grade'] == 'against-trend', 'le'),
                       ('BLOCKED (mtd.r2)', lambda r: r['status'] == 'BLOCKED', 'gt'),
                       ('OPEN · neither', lambda r: r['status'] == 'OPEN' and r['m']['route'] == 'neither', None),
                       ('OPEN · D no fire', lambda r: r['status'] == 'OPEN' and r['grade'] == 'band claimed', None),
                       ('OPEN · no r block', lambda r: r['grade'] == 'no r block', None)):
    g = [r for r in ROWS if sel(r)]
    lo_ = sum(1 for r in g if r['mae'] <= THR); hi_ = len(g) - lo_
    rd = ('%d of %d correct' % (lo_, len(g))) if good == 'le' else (
         ('%d of %d correct' % (hi_, len(g))) if good == 'gt' else '%d would block, %d would fire' % (hi_, lo_))
    print('| %s | %d | %d | %d | %s |' % (lab, len(g), lo_, hi_, rd))

print()
print('## WHAT EACH PENDING RULING BUYS — all three are yours, none is built')
print('| ruling | rows | right | wrong | net |')
print('|' + '---|' * 5)
for lab, sel in (('`neither` = BLOCK', lambda r: r['m']['route'] == 'neither'),
                 ('`no fire` = BLOCK', lambda r: r['status'] == 'OPEN' and r['grade'] == 'band claimed'),
                 ('D empty block = BLOCK', lambda r: r['grade'] == 'no r block')):
    g = [r for r in ROWS if sel(r)]
    ok = sum(1 for r in g if r['mae'] > THR)
    print('| %s | %d | %d | %d | %+d |' % (lab, len(g), ok, len(g) - ok, ok - (len(g) - ok)))
cur = sum(1 for r in ROWS if r['status'] == 'CONFLUENCE' and r['mae'] <= THR) + len(B_OK)
allr = cur + sum(1 for r in ROWS if r['status'] == 'OPEN' and r['mae'] > THR)
print('| | | | | |')
print('| agreement now (25 rows with a verdict) | | | | %d of 25 |' % cur)
print('| agreement with all three ruled (39 rows) | | | | %d of 39 |' % allr)

print()
print('## THE BAND-DEPTH KNOB — a claim counts only if it is at least X inside the band')
nf = [r for r in ROWS if r['status'] == 'OPEN' and r['grade'] == 'band claimed']
print('| octo-sig | deepest claim inside the band | MAE% | firing would be |')
print('|' + '---|' * 4)
for r in sorted(nf, key=lambda x: x['deep']):
    print('| %s | %.2f | %.3f | %s |' % (r['lbl'], r['deep'], r['mae'], 'right' if r['mae'] <= THR else 'WRONG'))
print()
print('| depth floor X | rows that FIRE instead | right | wrong | `no fire` correct of 6 |')
print('|' + '---|' * 5)
for X in (0.0, 1.0, 2.0, 5.0, 10.0, 19.0, 20.0, 21.0, 22.0, 27.0):
    flip = [r for r in nf if r['deep'] is not None and r['deep'] < X]
    ok = sum(1 for r in flip if r['mae'] <= THR) + sum(1 for r in nf if r not in flip and r['mae'] > THR)
    print('| %.1f | %d | %d | %d | %d |' % (X, len(flip), sum(1 for r in flip if r['mae'] <= THR),
                                            sum(1 for r in flip if r['mae'] > THR), ok))
