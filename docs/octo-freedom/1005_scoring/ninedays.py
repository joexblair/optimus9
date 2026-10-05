"""All 9 built days: 09-25 .. 10-03. Joe 1005 asked for a "7 day forecast" - 7 more days of
octo-sig are already built, so this MEASURES them instead of extrapolating 2 days.

Same pipeline throughout: mtd -> branch D -> stage 2 flip on with-trend -> swing_detect 0.70 ->
mae_cap 0.70 stop -> next favourable swing pivot -> 0.1975 cost.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, os, contextlib
import os as _os
import datetime as dt
import numpy as np
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
os.environ['LG_DAY'] = '2026-09-25'
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as S
PCT = 0.70; COST = 0.1975; CAP = 0.95
H, L = S.CACHE[PCT]; PX, ts = S.PX, S.ts
# The window. Override with LG_DAYS=YYYY-MM-DD[,...]. A day outside the default tape ALSO needs
# LG_TAPE_END (score39.py refuses nothing — it would silently index the tape's last bar). Each day
# needs its octo-sig at octosig/<day>.out from report_leash_walk.py --day <day> --tape-end <end>.
# In-sample: 09-25..10-03. 10-04 is the first HELD-OUT day.
_dflt = ['2026-09-%02d' % d for d in (25, 26, 27, 28, 29, 30)] + ['2026-10-%02d' % d for d in (1, 2, 3)]
DAYS = [x.strip() for x in _os.environ['LG_DAYS'].split(',')] if _os.environ.get('LG_DAYS') else _dflt
SPAN = '%d day%s' % (len(DAYS), '' if len(DAYS) == 1 else 's')
UNRESOLVED = []

def day_rows(day):
    A0, A1 = S.K(day + ' 00:00:00'), S.K(day + ' 23:59:55')
    OS = []
    for ln in open(_os.path.join(_HERE, 'octosig') + '/%s.out' % day):
        if ln.startswith('R|') and not ln.startswith('R|run'):
            f = ln.rstrip('\n').split('|')
            if len(f) >= 7:
                k = S.K(day + ' ' + f[2])
                if A0 <= k <= A1: OS.append((k, f[2]))
    out = []
    for k, lbl in OS:
        m = S.mtd(k)
        d = m['d']
        r = {'day': day, 'lbl': lbl, 'd': d, 'm': m, 'k': k}
        if m['route'] == 'mtd.r1':
            dd = S.branchD(d, m['ex']); r['D'] = dd
            if dd['fire']:
                r['status'] = 'CONFLUENCE'; r['grade'] = 'with-trend' if dd['away'] else 'against-trend'
            else:
                r['status'] = 'OPEN'; r['grade'] = dd['why']
        elif m['route'] == 'mtd.r2':
            r['status'] = 'BLOCKED'; r['grade'] = 'allows %s only' % m['allow']
        else:
            r['status'] = 'OPEN'; r['grade'] = 'no rule'
        flip = (r['status'] == 'CONFLUENCE' and r['grade'] == 'with-trend')
        de = -d if flip else d
        f, a, j = S.score(k, de, H, L)
        # UNRESOLVED: no favourable swing pivot exists after this bar INSIDE the tape. It happens on
        # the tape's last day, where a late entry has nowhere to run to. Not a zero and not a loss —
        # inventing an exit at the tape end would be a truncation. Excluded and COUNTED. The nine
        # in-sample days have 0 of these, because that tape ran a day past 10-03.
        if f is None:
            UNRESOLVED.append((day, lbl, 'flipped leg'))
            continue
        entry = float(PX[k]); seg = PX[k:j + 1]
        adv = (seg - entry) / entry * 100.0 if de > 0 else (entry - seg) / entry * 100.0
        hit = np.flatnonzero(np.isfinite(adv) & (adv >= CAP))
        ex = k + int(hit[0]) if hit.size else j
        r.update({'flip': flip, 'side': 'SHORT' if de > 0 else 'LONG', 'mfe': f, 'mae': a,
                  'net': (-CAP if hit.size else f) - COST, 'stopped': bool(hit.size),
                  'open_ms': int(ts[k]), 'close_ms': int(ts[ex]),
                  'net_asis': None})
        f2, a2, j2 = S.score(k, d, H, L)
        if f2 is None:
            UNRESOLVED.append((day, lbl, 'dr-bias leg'))
            continue
        seg2 = PX[k:j2 + 1]
        adv2 = (seg2 - entry) / entry * 100.0 if d > 0 else (entry - seg2) / entry * 100.0
        h2 = np.flatnonzero(np.isfinite(adv2) & (adv2 >= CAP))
        r['net_asis'] = (-CAP if h2.size else f2) - COST
        out.append(r)
    return out

ALL = {}
for day in DAYS:
    ALL[day] = day_rows(day)
    print('# %s built: %d octo-sig' % (day, len(ALL[day])), file=sys.stderr)

print('## PER DAY — %s, same pipeline, nothing held back' % SPAN)
print('| day | octo-sig | CONF | wt flip | at | BLOCKED | OPEN | CONF total net % | CONF mean net % | winners | stopped | ungated mean net % |')
print('|' + '---|' * 12)
for day in DAYS:
    g = ALL[day]; c = [x for x in g if x['status'] == 'CONFLUENCE']
    cn = [x['net'] for x in c]; un = [x['net'] for x in g]
    print('| %s | %d | %d | %d | %d | %d | %d | **%+.3f** | %+.3f | %d of %d | %d | %+.3f |'
          % (day[5:], len(g), len(c), sum(1 for x in c if x['flip']), sum(1 for x in c if not x['flip']),
             sum(1 for x in g if x['status'] == 'BLOCKED'), sum(1 for x in g if x['status'] == 'OPEN'),
             sum(cn) if cn else 0.0, float(np.mean(cn)) if cn else 0.0,
             sum(1 for v in cn if v > 0), len(cn), sum(1 for x in c if x['stopped']),
             float(np.mean(un)) if un else 0.0))
T = sorted([x for d in DAYS for x in ALL[d] if x['status'] == 'CONFLUENCE'], key=lambda x: x['open_ms'])
U = sorted([x for d in DAYS for x in ALL[d]], key=lambda x: x['open_ms'])
cn = [x['net'] for x in T]
print('| **' + SPAN + '** | %d | %d | %d | %d | %d | %d | **%+.3f** | %+.3f | %d of %d | %d | %+.3f |'
      % (len(U), len(T), sum(1 for x in T if x['flip']), sum(1 for x in T if not x['flip']),
         sum(1 for x in U if x['status'] == 'BLOCKED'), sum(1 for x in U if x['status'] == 'OPEN'),
         sum(cn), float(np.mean(cn)), sum(1 for v in cn if v > 0), len(cn),
         sum(1 for x in T if x['stopped']), float(np.mean([x['net'] for x in U]))))

print()
if UNRESOLVED:
    print()
    print('## UNRESOLVED — %d row%s EXCLUDED: no favourable swing pivot after the entry inside the tape'
          % (len(UNRESOLVED), '' if len(UNRESOLVED) == 1 else 's'))
    print('# tape ends %s — a late entry on the last day has nowhere to run to. Excluded, NOT scored 0.'
          % dt.datetime.fromtimestamp(int(ts[-1]) / 1000, dt.timezone.utc))
    print('| day | octo-sig | which leg |')
    print('|' + '---|' * 3)
    for _d, _l, _w in UNRESOLVED: print('| %s | %s | %s |' % (_d, _l, _w))
    print()

print('## THE STAGE 2 FLIP ACROSS %s — with-trend rows only' % SPAN)
print('| day | wt rows | total net % as published | total net % flipped | delta |')
print('|' + '---|' * 5)
tot_a = tot_f = n_wt = 0
for day in DAYS:
    g = [x for x in ALL[day] if x['flip']]
    if not g: print('| %s | 0 | — | — | — |' % day[5:]); continue
    a = sum(x['net_asis'] for x in g); b = sum(x['net'] for x in g)
    tot_a += a; tot_f += b; n_wt += len(g)
    print('| %s | %d | %+.3f | **%+.3f** | **%+.3f** |' % (day[5:], len(g), a, b, b - a))
print('| **' + SPAN + '** | %d | %+.3f | **%+.3f** | **%+.3f** (%+.3f per trade) |'
      % (n_wt, tot_a, tot_f, tot_f - tot_a, (tot_f - tot_a) / n_wt))

NET = np.array(cn)
def curve(nets, Lv):
    eq = 1.0; peak = 1.0; dd = 0.0; liq = None
    for i, r in enumerate(nets):
        f = 1.0 + Lv * r / 100.0
        if f <= 0: return 0.0, 1.0, i + 1
        eq *= f; peak = max(peak, eq); dd = max(dd, (peak - eq) / peak)
    return eq, dd, liq

print()
print('## COMPOUND — the %d confluences, chronological across %s' % (len(T), SPAN))
print('| L | final equity x | total return % | max DD % | liquidated at trade |')
print('|' + '---|' * 5)
for Lv in (1, 2, 3, 5, 10, 15, 20, 25, 30, 50, 75, 100, 112):
    e, dd, liq = curve(NET, Lv)
    print('| %dx | %s | %s | %.2f | %s |' % (Lv, ('%.4f' % e) if liq is None else '**0 — wiped**',
          ('%+.2f' % ((e - 1) * 100)) if liq is None else '**-100**', dd * 100,
          '—' if liq is None else '**#%d**' % liq))

print()
print('## THE LEVERAGE CEILING over %s' % SPAN)
worst = float(NET.min()); run = mx = 0
for r in NET:
    run = run + 1 if r < 0 else 0
    mx = max(mx, run)
print('| measure | value |')
print('|---|---|')
print('| worst single trade | %+.4f %% |' % worst)
print('| L at which ONE worst trade wipes | **%.1fx** |' % (100.0 / -worst))
print('| longest consecutive losing run | **%d trades** |' % mx)
for target in (10, 20, 25, 33, 50):
    lo, hi = 0.0, 200.0
    for _ in range(60):
        mid = (lo + hi) / 2
        _e, dd, _l = curve(NET, mid)
        if dd * 100 <= target: lo = mid
        else: hi = mid
    e, dd, _l = curve(NET, lo)
    print('| max L holding max DD <= %d %% | **%.1fx** -> final %.2fx, total %+.1f %%, DD %.1f %% |'
          % (target, lo, e, (e - 1) * 100, dd * 100))

print()
print('## DAILY EQUITY PATH at a few L — one row per day, compounding carried across days')
print('| day | trades | L=1 equity x | L=5 | L=10 | L=20 | worst DD so far at L=10 % |')
print('|' + '---|' * 7)
eqs = {1: 1.0, 5: 1.0, 10: 1.0, 20: 1.0}; pk10 = 1.0; dd10 = 0.0
for day in DAYS:
    g = sorted([x for x in ALL[day] if x['status'] == 'CONFLUENCE'], key=lambda x: x['open_ms'])
    for x in g:
        for Lv in eqs: eqs[Lv] *= (1 + Lv * x['net'] / 100.0)
        pk10 = max(pk10, eqs[10]); dd10 = max(dd10, (pk10 - eqs[10]) / pk10)
    print('| %s | %d | %.4f | %.4f | %.4f | %.4f | %.2f |'
          % (day[5:], len(g), eqs[1], eqs[5], eqs[10], eqs[20], dd10 * 100))
