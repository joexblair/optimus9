"""Stop 0.70 vs 0.80, with pyramid max 2 concurrent. Joe 1005: "apply a 0.7% and 0.8% stop / and
pyramid max 2 trades". 9 days, 09-25 .. 10-03.

PYRAMID 2, from the banked precedent (docs/sneaky_trade_1_handover.md:176, "pyramid | max 2
concurrent | Joe 0916, verified held-out 0917"):
  - a confluence arriving while 2 trades are STILL OPEN is SKIPPED. Skipping is the only causal
    reading of a concurrency cap; queueing would need a rule that does not exist.
  - the cap is flat across the BOOK, not per side. sneaky-1's "staggered pair" is 2 legs total.
  - SIZE IS FULL ON EACH LEG, not split. Same source, line 174: "22,000 coins, fixed. On a
    staggered pair that is 22,000 EACH".

COMPOUNDING: each taken trade multiplies equity by (1 + L*net/100), applied in CLOSE-TIME order.
LIMITATION, FLAGGED: with full size on each leg, peak exposure during an overlap is 2x. A realised
close-order chain cannot see the simultaneous unrealised dip of two open legs, so the drawdown below
UNDERSTATES the overlap. The exposure census says how often that applies.

THE 0.80 STOP IS WIDER THAN THE 0.70 SWING used to place the exit pivot. So under it a trade can
lose more than the swing that defines a move. Stated, not corrected - Joe named both levels.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, os, contextlib
import numpy as np
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
exec(open(_os.path.join(_HERE, 'ninedays.py')).read().split('ALL = {}')[0])
COST = 0.1975

def build(cap):
    """-> all confluences across the 9 days, chronological, scored at this stop."""
    out = []
    for day in DAYS:
        A0, A1 = S.K(day + ' 00:00:00'), S.K(day + ' 23:59:55')
        OS = []
        for ln in open(_os.path.join(_HERE, 'octosig') + '/%s.out' % day):
            if ln.startswith('R|') and not ln.startswith('R|run'):
                f = ln.rstrip('\n').split('|')
                if len(f) >= 7:
                    k = S.K(day + ' ' + f[2])
                    if A0 <= k <= A1: OS.append((k, f[2]))
        for k, lbl in OS:
            m = S.mtd(k); d = m['d']
            if m['route'] != 'mtd.r1': continue
            dd = S.branchD(d, m['ex'])
            if not dd['fire']: continue
            grade = 'with-trend' if dd['away'] else 'against-trend'
            flip = (grade == 'with-trend')
            rec = {'day': day, 'lbl': lbl, 'grade': grade, 'flip': flip, 'open_ms': int(ts[k])}
            for tag, de in (('net', -d if flip else d), ('net_asis', d)):
                f_, a_, j_ = S.score(k, de, H, L)
                entry = float(PX[k]); seg = PX[k:j_ + 1]
                adv = (seg - entry) / entry * 100.0 if de > 0 else (entry - seg) / entry * 100.0
                hit = np.flatnonzero(np.isfinite(adv) & (adv >= cap))
                ex = k + int(hit[0]) if hit.size else j_
                rec[tag] = (-cap if hit.size else f_) - COST
                rec[tag + '_close'] = int(ts[ex])
                rec[tag + '_stopped'] = bool(hit.size)
            out.append(rec)
    out.sort(key=lambda x: x['open_ms'])
    return out

def pyr2(rows, key):
    """Max 2 concurrent. -> (taken, skipped). Causal: decided at the arriving bar."""
    taken, skipped, live = [], [], []
    for x in rows:
        live = [c for c in live if c > x['open_ms']]
        if len(live) >= 2: skipped.append(x); continue
        taken.append(x); live.append(x[key + '_close'])
    return taken, skipped

def compound(rows, key, Lv):
    ev = sorted(rows, key=lambda x: x[key + '_close'])
    eq = 1.0; pk = 1.0; dd = 0.0
    for x in ev:
        f = 1.0 + Lv * x[key] / 100.0
        if f <= 0: return 0.0, 1.0, True
        eq *= f; pk = max(pk, eq); dd = max(dd, (pk - eq) / pk)
    return eq, dd, False

CAPS = (0.70, 0.80)
SETS = {}
for cap in CAPS: SETS[cap] = build(cap)

print('# STOP 0.70 vs 0.80, PYRAMID MAX 2 — 9 days, 09-25 .. 10-03')
print()
print('## THE GATE — how many confluences the pyramid-2 cap drops')
print('| stop | side rule | confluences | taken | skipped by pyramid 2 | stopped out | of taken |')
print('|' + '---|' * 6)
for cap in CAPS:
    for key, lab in (('net', 'stage 2 flip'), ('net_asis', 'dr-bias, no flip')):
        tk, sk = pyr2(SETS[cap], key)
        print('| %.2f %% | %s | %d | **%d** | %d | %d | %.0f %% |'
              % (cap, lab, len(SETS[cap]), len(tk), len(sk),
                 sum(1 for x in tk if x[key + '_stopped']),
                 100.0 * sum(1 for x in tk if x[key + '_stopped']) / len(tk)))

print()
print('## NET RESULT — 4 combinations, all 9 days')
print('| stop | side rule | taken | total net % | mean net % | median net % | winners | worst trade % |')
print('|' + '---|' * 8)
BEST = {}
for cap in CAPS:
    for key, lab in (('net', 'stage 2 flip'), ('net_asis', 'dr-bias, no flip')):
        tk, sk = pyr2(SETS[cap], key)
        v = np.array([x[key] for x in tk])
        BEST[(cap, key)] = tk
        print('| %.2f %% | %s | %d | **%+.3f** | %+.3f | %+.3f | %d of %d | %+.3f |'
              % (cap, lab, len(tk), v.sum(), v.mean(), float(np.median(v)),
                 int((v > 0).sum()), len(v), v.min()))

print()
print('## AGAINST NO PYRAMID CAP — what the cap costs or saves')
print('| stop | side rule | ungated n | ungated total % | pyramid-2 n | pyramid-2 total % | delta | mean before | mean after |')
print('|' + '---|' * 9)
for cap in CAPS:
    for key, lab in (('net', 'stage 2 flip'), ('net_asis', 'dr-bias, no flip')):
        allv = np.array([x[key] for x in SETS[cap]])
        tk, sk = pyr2(SETS[cap], key); v = np.array([x[key] for x in tk])
        print('| %.2f %% | %s | %d | %+.3f | %d | **%+.3f** | **%+.3f** | %+.3f | %+.3f |'
              % (cap, lab, len(allv), allv.sum(), len(v), v.sum(), v.sum() - allv.sum(),
                 allv.mean(), v.mean()))

print()
print('## COMPOUND, pyramid 2 applied')
print('| stop | side rule | L=1 x | L=2 x | L=3 x | L=5 x | L=10 x | max DD at L=5 % | max DD at L=10 % |')
print('|' + '---|' * 9)
for cap in CAPS:
    for key, lab in (('net', 'stage 2 flip'), ('net_asis', 'dr-bias, no flip')):
        tk = BEST[(cap, key)]
        cells = []
        for Lv in (1, 2, 3, 5, 10):
            e, dd, wipe = compound(tk, key, Lv)
            cells.append('**0 wiped**' if wipe else '%.4f' % e)
        _e5, dd5, _w = compound(tk, key, 5); _e10, dd10, _w2 = compound(tk, key, 10)
        print('| %.2f %% | %s | %s | %.2f | %.2f |' % (cap, lab, ' | '.join(cells), dd5 * 100, dd10 * 100))

print()
print('## PER DAY — the combination with the best 9-day total')
bk = max(BEST, key=lambda k: sum(x[k[1]] for x in BEST[k]))
cap, key = bk
print('# stop %.2f %%, %s, pyramid 2' % (cap, 'stage 2 flip' if key == 'net' else 'dr-bias no flip'))
print('| day | taken | skipped | total net % | mean net % | winners | stopped |')
print('|' + '---|' * 7)
tk, sk = pyr2(SETS[cap], key)
for day in DAYS:
    g = [x for x in tk if x['day'] == day]; s = [x for x in sk if x['day'] == day]
    v = np.array([x[key] for x in g])
    print('| %s | %d | %d | **%+.3f** | %+.3f | %d of %d | %d |'
          % (day[5:], len(g), len(s), v.sum() if len(v) else 0.0, v.mean() if len(v) else 0.0,
             int((v > 0).sum()), len(v), sum(1 for x in g if x[key + '_stopped'])))
v = np.array([x[key] for x in tk])
print('| **9 days** | %d | %d | **%+.3f** | %+.3f | %d of %d | %d |'
      % (len(tk), len(sk), v.sum(), v.mean(), int((v > 0).sum()), len(v),
         sum(1 for x in tk if x[key + '_stopped'])))

print()
print('## EXPOSURE CENSUS under pyramid 2 — how often 2 legs are open at once')
for cap in CAPS:
    for key, lab in (('net', 'stage 2 flip'), ('net_asis', 'dr-bias, no flip')):
        tk, sk = pyr2(SETS[cap], key)
        iv = sorted([(x['open_ms'], x[key + '_close']) for x in tk])
        both = 0; tot = 0
        for i, (o, c) in enumerate(iv):
            tot += c - o
            for o2, c2 in iv[i + 1:]:
                if o2 >= c: break
                both += max(0, min(c, c2) - o2)
        print('- stop %.2f %%, %s: %d trades, total open time %.1f h, both-legs-open %.1f h = %.1f %% of it'
              % (cap, lab, len(tk), tot / 3600000.0, both / 3600000.0, 100.0 * both / tot))
