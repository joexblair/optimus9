"""THE WALK OF THE LEGS THAT RELY ON A STOP ABOVE 1.90 AND OPENED TOO EARLY. 1008.

Joe 1008: *"go for B, then show me the walk of these 24 legs. for each, I'll need the incoming
trade's timestamps so that I have both sides of the coin"*.

WHY THE INCOMING TRADE IS ON THE SAME TIMELINE. The chain is always in the market, so a leg's OPEN
BAR *is* the previous leg's EXIT BAR. Relocating an open therefore relocates the previous leg's
exit - there is no way to move one without moving the other. That is both sides of the coin, and it
is why every block below starts with the incoming leg and runs straight through the open.

The one exception is a leg that follows a STOP. There the incoming leg closed at its breach bar and
the re-entry router chose the open, so the block carries three incoming timestamps instead of one:
the breach, the ws1x return bar, and the conf bar that became this leg's open.

THE SELECTION is Joe's group from _maetiming.py, unchanged: a leg that did NOT stop and whose
measured MAE is above 1.90 - the band that cannot live under a 2.0 stop - and whose ADVERSE extreme
came BEFORE its favourable one, which is the only shape a later open can fix.

W_NOX=1 reproduces the 1.06 build (the lineage walk exits on `final stalled` only). Unset it for the
banked B build (the x-cross live, target ws{h+1}b, no in-fence test).
"""
import os, sys, json, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts); FEE = 0.11; BAND = 1.90
BUILD = 'the 1.06 build — stall-only, x-cross OFF' if C.NOX else \
        'the BANKED B build — x-cross live on ws{h+1}%s, in-fence %s' \
        % (C.XT_ROLE, 'ON' if C.XT_FENCE else 'OFF')
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
print('# BUILD: %s' % BUILD)
print('# tape %d bars, %s -> %s, stop %.2f, reent_xwob %d, knob key %s'
      % (N, U(0), U(N - 1), C.MAE_STOP, T.XWOB, C.W.key()), flush=True)

# ---- the chain, exactly as the sweep ran it, and every leg's walk kept
legs = []; k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    seg = PX[k:xk + 1]
    ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sgn, 0.0)
    iw, ib = int(np.argmin(rel)), int(np.argmax(rel))
    legs.append(dict(day=DAYOF(k), open=k, exit=xk, d=d, why=why, tr=tr,
                     side='LONG' if d > 0 else 'SHORT', hand=hand,
                     mae=-float(rel[iw]), mfe=float(rel[ib]), maebar=k + iw, mfebar=k + ib,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, rb=None, cf=None))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd
        legs[-1]['nextrb'] = rb; legs[-1]['nextcf'] = cf
        continue
    if xk >= N - 1: break
    k = xk; d = -d
for i, r in enumerate(legs):
    if i and legs[i - 1]['why'] == 'mae breach':
        r['rb'], r['cf'] = legs[i - 1].get('nextrb'), legs[i - 1].get('nextcf')

# ---- the control block: does this build reproduce the arm it was banked from
days = sorted({r['day'] for r in legs})
BL = {'all': set(days), 'fit': set(days[:47]), 'hold': set(days[47:])}
def sc(blk):
    gr = lg = st = 0; a_ = f_ = 0.0
    for r in legs:
        if r['day'] not in BL[blk]: continue
        gr += r['real']; lg += 1; st += 1 if r['why'] == 'mae breach' else 0
        if r['why'] == 'mae breach': a_ += C.MAE_STOP
        else:
            a_ += r['mae']; f_ += r['mfe']
    return gr, lg, st, gr - lg * FEE, (f_ / a_ if a_ else 0.0)
print('\n# THE CONTROL — this build scored over the same 95 days, %d of them' % len(days))
box(('block', 'days', 'legs', 'stops', 'gross', 'drag at %.2f/leg' % FEE, 'NET AFTER DRAG',
     'MFE/MAE'),
    [(blk, str(len(BL[blk])), str(s[1]), str(s[2]), '%+.4f' % s[0], '%.4f' % (s[1] * FEE),
      '%+.4f' % s[3], '%.4f' % s[4]) for blk in ('fit', 'hold', 'all') for s in [sc(blk)]])
whys = collections.Counter(r['why'] for r in legs)
box(('the exit', 'legs'), [(w, str(c)) for w, c in whys.most_common()])

# ---- Joe's group
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
sel = [r for r in legs if r['why'] != 'mae breach' and r['mae'] > BAND
       and r['maebar'] < r['mfebar']]
print('\n# THE GROUP — did not stop, MAE above %.2f, and the ADVERSE extreme came FIRST' % BAND)
box(('the measure', 'value'),
    [('legs in the group', '**%d**' % len(sel)),
     ('their summed realised', '%+.4f' % sum(r['real'] for r in sel)),
     ('their drag at %.2f per leg' % FEE, '%.4f' % (len(sel) * FEE)),
     ('of them, opened by the re-entry router after a stop',
      str(sum(1 for r in sel if r['cf'] is not None))),
     ('of them, opened by the previous leg\'s own exit',
      str(sum(1 for r in sel if r['cf'] is None)))])

sel.sort(key=lambda r: r['open'])
print('\n# THE INDEX — one row per leg, in time order')
box(('#', 'day', 'side', 'the incoming leg opens', 'it exits / THIS LEG OPENS', 'how it opened',
     'this leg exits', 'why', 'hold min', 'MAE', 'at +min', 'MFE', 'at +min', 'realised',
     'walk events'),
    [(str(i + 1), r['day'], r['side'],
      U(legs[legs.index(r) - 1]['open']) if legs.index(r) else '— the seed bar',
      U(r['open']),
      ('re-entry: return %s, conf %s' % (U(r['rb']), U(r['cf']))) if r['cf'] is not None
      else ('the previous leg\'s %s' % legs[legs.index(r) - 1]['why'] if legs.index(r) else 'seed'),
      U(r['exit']), r['why'], '%.1f' % mn(r['open'], r['exit']),
      '%.4f' % r['mae'], '%.1f' % mn(r['open'], r['maebar']),
      '%.4f' % r['mfe'], '%.1f' % mn(r['open'], r['mfebar']),
      '%+.4f' % r['real'], str(len(r['tr']))) for i, r in enumerate(sel)])

# ---- the walks, one block per leg, one record per row, top to bottom
for i, r in enumerate(sel):
    ii = legs.index(r); prev = legs[ii - 1] if ii else None
    p0 = float(PX[r['open']]); sgn = 1 if r['d'] > 0 else -1
    pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
    rel = lambda j: '%+.1f' % mn(r['open'], j)
    print('\n\n## %d of %d — %s %s   opens %s   exits %s on %s   MAE %.4f at +%.1f min   '
          'MFE %.4f at +%.1f min   realised %+.4f'
          % (i + 1, len(sel), r['day'], r['side'], U(r['open']), U(r['exit']), r['why'],
             r['mae'], mn(r['open'], r['maebar']), r['mfe'], mn(r['open'], r['mfebar']),
             r['real']))
    rows = []
    if prev is not None:
        pp = float(PX[prev['open']]); ps = 1 if prev['d'] > 0 else -1
        rows.append((U(prev['open']), rel(prev['open']),
                     'INCOMING LEG OPENS %s' % prev['side'],
                     '%.6f' % pp, pct(prev['open'])))
        for j, lbl in prev['tr']:
            rows.append((U(j), rel(j), 'incoming: %s' % lbl, '%.6f' % float(PX[j]), pct(j)))
        rows.append((U(prev['exit']), rel(prev['exit']),
                     'INCOMING LEG CLOSES on %s, realised %+.4f'
                     % (prev['why'], (float(PX[prev['exit']]) - pp) / pp * 100.0 * ps),
                     '%.6f' % float(PX[prev['exit']]), pct(prev['exit'])))
        if r['cf'] is not None:
            rows.append((U(r['rb']), rel(r['rb']),
                         're-entry: ws1x return, the %d-bar hold starts' % T.XWOB,
                         '%.6f' % float(PX[r['rb']]), pct(r['rb'])))
    rows.append((U(r['open']), '+0.0', '>>> THIS LEG OPENS %s%s' % (r['side'],
                 ' (the re-entry conf bar)' if r['cf'] is not None else ''),
                 '%.6f' % p0, '+0.0000'))
    ev = [(j, lbl) for j, lbl in r['tr']]
    ev.append((r['maebar'], 'the ADVERSE extreme — MAE %.4f' % r['mae']))
    ev.append((r['mfebar'], 'the favourable extreme — MFE %.4f' % r['mfe']))
    for j, lbl in sorted(ev, key=lambda z: z[0]):
        rows.append((U(j), rel(j), lbl, '%.6f' % float(PX[j]), pct(j)))
    rows.append((U(r['exit']), rel(r['exit']), 'EXIT on %s' % r['why'],
                 '%.6f' % float(PX[r['exit']]), pct(r['exit'])))
    box(('ts', 'min from THIS open', 'event', 'pxs', 'pct for THIS leg'), rows)
print('\n- "pct for THIS leg" is measured from this leg\'s own open on this leg\'s own side, so the')
print('  incoming leg\'s rows read NEGATIVE where price was beyond this open - that gap is exactly')
print('  what a relocated open gives up or gains on the incoming side.')
