"""Does a given cadence event create the opposite trade, via the router? -> two arms, both printed.

HIS 1105 ASK: *"build a script to confirm the 0826 cadence creates (via router) the expected LONG"*.

TWO ARMS, AND THE DIFFERENCE BETWEEN THEM IS THE ANSWER:

  arm 1, THE RULED MACHINE   v4_fdm2.legs with nothing patched. It prints the verdict the machine
                             actually reaches at the cadence bar, and the leg's real exit.
  arm 2, THE INJECTION       v4_fdm2.walk is replaced FOR ONE LEG ONLY, so it hands the cadence bar
                             back as a rev-trade signal. v4_fdm2.legs then does the routing with
                             its OWN arithmetic and its own asserts.

ARM 2 IS NOT THE MACHINE. The ruled machine emits no rev-trade at 2026-08-07 08:26:00 - step 1
counts 5 of 27 and the fdm2-wsxcad-director finds no candidate, so the verdict is WALK. The signal
arm 2 injects is the one fdm2-blaster's exhaust would supply, and fdm2-blaster is unbuilt: his 1105
*"this is on hold - I need to improve the cadence event before we can accurately model"*. The arm
exists to show what the router does WITH that signal, not to claim the machine produces it.

THE ROUTING IS NOT RE-IMPLEMENTED HERE. v4_fdm2.legs owns it - close at signal + 1, open at
signal + 2, side flipped - and patching `walk` is the one point where a signal enters that driver.
A hand-rolled close/open in this file would be the fragment his "one driver" rule forbids.

    W_FDM2_PROBE_AT   the cadence bar, 'YYYY-MM-DD HH:MM:SS'. Default 2026-08-07 08:26:00.
    W_FDM2_PROBE_DAY  the day to build the chain over. Default the probe bar's own date.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_signal as SG
    import v4_fdm_reentry as RE
    import ln
finally:
    sys.stderr = _e

AT = os.environ.get('W_FDM2_PROBE_AT', '2026-08-07 08:26:00')
DAY = os.environ.get('W_FDM2_PROBE_DAY', AT.split(' ')[0])
LN = F2.load()
EV = ln.K(AT)
A, B = ln.K(DAY + ' 00:00:00'), ln.K(DAY + ' 23:59:55')
HI = int(LN['HI'])
CLOSE = LN['close']


def side_word(s):
    return 'LONG' if int(s) > 0 else 'SHORT'


def tside_word(s):
    return 'HIGH' if int(s) > 0 else 'LOW'


def leg_rows(L):
    """One row per decision the leg made, chronological."""
    for r in L['rows']:
        yield (ln.U(int(r['bar'])), str(r['stage']), str(r.get('why', '')))


#   ── the day's open, exactly as fdm2_chain picks it ────────────────────────────────────────────
SIGS = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'], CPM=LN['CPM'])
HIT = [x for x in SIGS if A <= int(x['bar']) <= B]
assert HIT, 'no fdm re-entry signal inside %s .. %s' % (ln.U(A), ln.U(B))
g = HIT[0]
D = SG.direction(int(g['side']))
OPN, TS = SG.fire_bar(g), SG.target_side(D)
OPEN_AT = (OPN, TS, 'fdm re-entry %s' % ln.U(int(g['bar'])))

print('| the probe | value |')
print('|---|---|')
print('| the cadence bar under test | %s |' % ln.U(EV))
print('| the day | %s to %s |' % (ln.U(A), ln.U(B)))
print('| the day\'s first open | %s %s, target side %s |' % (ln.U(OPN), D, tside_word(TS)))
print('| its re-entry signal | %s, gcws30b %s oob |'
      % (ln.U(int(g['bar'])), tside_word(int(g['side']))))
print('| the stop | FDM_MAE_CAP %.2f%%, ON for both arms |' % float(K.FDM_MAE_CAP))
print('| the router | v4_fdm2.legs - close at signal+1, open at signal+2, side flipped |')
print()

#   ── arm 1, the ruled machine ──────────────────────────────────────────────────────────────────
print('## arm 1, THE RULED MACHINE - nothing patched')
print()
LG1 = F2.legs(LN, OPEN_AT, B, resig=SIGS)
HOLD = [L for L in LG1 if int(L['opn']) <= EV <= int(L['exit'])]
print('| the leg that is open at %s | value |' % ln.U(EV))
print('|---|---|')
if not HOLD:
    print('| none | no leg of this day covers that bar |')
else:
    L = HOLD[0]
    print('| its open | %s %s, target side %s |'
          % (ln.U(int(L['opn'])), side_word(L['side']), tside_word(L['side'])))
    print('| its source | %s |' % L['src'])
    print('| its exit bar | %s |' % ln.U(int(L['exit'])))
    print('| its exit kind | %s |' % L['ctype'])
    print('| its realised %% | %+.3f |' % L['rel'])
    print('| held, min | %.1f |' % L['held_min'])
print()

k, n = F2.step1(LN, TS if not HOLD else HOLD[0]['side'], EV)
sd = TS if not HOLD else int(HOLD[0]['side'])
tf, ab, cwhy = F2.xcad_candidate(LN, sd, EV, int(HOLD[0]['opn']) if HOLD else OPN)
exf = [t for t in range(1, HI + 1) if F2.ex2080_line(LN, t, EV, sd)]
print('| the verdict chain at %s | value |' % ln.U(EV))
print('|---|---|')
print('| the target side read | %s |' % tside_word(sd))
print('| step 1 | %d of %d, so %s |' % (k, n, 'rev-trade' if k == 0 else 'walk'))
print('| the fdm2-wsxcad-director\'s candidate | %s |'
      % (('ws%dr' % tf) if tf else 'none - %s' % cwhy))
print('| FDM_XCAD_FALLBACK %s, its ex-20/80 lines | %s |'
      % (K.FDM_XCAD_FALLBACK, ', '.join('ws%d' % t for t in exf) or 'none'))
print('| so the rev-trade at this bar | %s |'
      % ('YES' if k == 0 else 'NO - the verdict is WALK'))
print()
print('| every decision the leg printed | the stage | why |')
print('|---|---|---|')
if HOLD:
    for a, b2, c in leg_rows(HOLD[0]):
        print('| %s | %s | %s |' % (a, b2, c.replace('|', '\\|')))
print()

#   ── arm 2, the injection ──────────────────────────────────────────────────────────────────────
print('## arm 2, THE INJECTION - a rev-trade handed to the router at %s' % ln.U(EV))
print()
print('NOT THE MACHINE. The ruled machine reaches WALK at this bar, per arm 1. This arm supplies')
print('the signal fdm2-blaster\'s exhaust would carry and lets v4_fdm2.legs route it.')
print()
TARGET_OPN = int(HOLD[0]['opn']) if HOLD else None
_real_walk = F2.walk
_fired = []


def _patched(LNx, side, opn, Bx):
    """The real walk for every leg but one; for that one, the cadence bar as the signal."""
    if TARGET_OPN is not None and int(opn) == TARGET_OPN and int(opn) < EV <= int(Bx):
        _fired.append(int(opn))
        return EV, [dict(bar=EV, stage='REV-TRADE (INJECTED)',
                         why='fdm2-blaster exhaust, supplied by fdm2_router_probe.py - '
                             'NOT emitted by the ruled machine')]
    return _real_walk(LNx, side, opn, Bx)


F2.walk = _patched
try:
    LG2 = F2.legs(LN, OPEN_AT, B, resig=SIGS)
finally:
    F2.walk = _real_walk

print('| the injection | value |')
print('|---|---|')
print('| legs that took it | %s |' % (', '.join(ln.U(x) for x in _fired) or 'none'))
print()
IDX = [i for i, L in enumerate(LG2) if int(L['opn']) == TARGET_OPN]
if IDX and IDX[0] + 1 < len(LG2):
    i = IDX[0]
    S, Lg = LG2[i], LG2[i + 1]
    print('| the router\'s arithmetic | bar | price |')
    print('|---|---|---|')
    print('| the signal | %s | %.6f |' % (ln.U(EV), float(CLOSE[EV])))
    print('| the close, signal + 1 | %s | %.6f |' % (ln.U(int(S['exit'])), float(CLOSE[int(S['exit'])])))
    print('| the open, signal + 2 | %s | %.6f |' % (ln.U(int(Lg['opn'])), float(CLOSE[int(Lg['opn'])])))
    print()
    print('| the trade it created | value |')
    print('|---|---|')
    print('| its side | %s |' % side_word(Lg['side']))
    print('| its target side | %s |' % tside_word(Lg['side']))
    print('| its source | %s |' % Lg['src'])
    print('| its exit bar | %s |' % ln.U(int(Lg['exit'])))
    print('| its exit kind | %s |' % Lg['ctype'])
    print('| its realised %% | %+.3f |' % Lg['rel'])
    print('| its MAE %% | %.3f |' % Lg['mae'])
    print('| its MFE %% | %.3f |' % Lg['mfe'])
    print('| held, min | %.1f |' % Lg['held_min'])
    print('| was it stopped | %s |' % ('YES' if Lg['stopped'] else 'no'))
    print()
    print('| the leg the rev-trade closed | value |')
    print('|---|---|')
    print('| its open | %s %s |' % (ln.U(int(S['opn'])), side_word(S['side'])))
    print('| its exit kind | %s |' % S['ctype'])
    print('| its realised %% | %+.3f |' % S['rel'])
    print('| held, min | %.1f |' % S['held_min'])
    print()
    print('| the expected LONG | value |')
    print('|---|---|')
    print('| expected | a LONG opening at %s, the signal bar + 2 |' % ln.U(EV + 2))
    print('| got | %s opening at %s |' % (side_word(Lg['side']), ln.U(int(Lg['opn']))))
    print('| CONFIRMED | %s |'
          % ('YES' if (int(Lg['side']) > 0 and int(Lg['opn']) == EV + 2) else 'NO'))
else:
    print('| the injection created no following leg | - |')
    print('|---|---|')
print()

#   ── both arms, every leg, chronological ───────────────────────────────────────────────────────
for name, LGx in (('arm 1, the ruled machine', LG1), ('arm 2, the injection', LG2)):
    print('## %s - every leg' % name)
    print()
    print('| the open | the trade | the exit | the exit kind | held min | MAE% | MFE% | realised% |')
    print('|---|---|---|---|---|---|---|---|')
    for L in LGx:
        print('| %s | %s | %s | %s | %.1f | %.3f | %+.3f | %+.3f |'
              % (ln.U(int(L['opn'])), side_word(L['side']), ln.U(int(L['exit'])),
                 str(L['ctype']).replace('|', '\\|'), L['held_min'], L['mae'], L['mfe'], L['rel']))
    s = F2.score(LGx)
    print()
    print('| %s, the totals | value |' % name)
    print('|---|---|')
    print('| legs | %d |' % s['n'])
    print('| stopped | %d |' % s['stops'])
    print('| gross %% | %+.3f |' % s['gross'])
    print('| drag %% | %-.3f |' % -s['drag'])
    print('| net %% | %+.3f |' % s['net'])
    print('| MAE %% total | %.3f |' % s['mae'])
    print('| MFE %% total | %+.3f |' % s['mfe'])
    print('| the stop | FDM_MAE_CAP %.2f%%, ON |' % float(K.FDM_MAE_CAP))
    print()
