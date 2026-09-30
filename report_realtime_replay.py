"""report_realtime_replay - run the sig_utc chain IN REALTIME and see whether it ever revises itself.

    python3 report_realtime_replay.py

THE RESULT, 2026-09-29, over 2026-09-01..09-06 at the banked v7 knobs: 121 of 121 historical moments
emitted, ZERO revisions under either emission rule, ZERO historical moments never reached. The chain
can run live. What it costs is LATENCY, and that is in the mech, not the implementation:

    eager    p25 0 s   median 165 s   p75 440 s   p90 860 s   max 4955 s   mean 405 s
    settled  p25 0 s   median 180 s   p75 440 s   p90 890 s   max 4955 s   mean 416 s

measured as (the bar the answer could first be emitted) - (the sig bar it names). o9-live will know
the timestamp, correctly, that far after the bar it points at. Any recon that does not carry this
number will read the delay as a fault.

IT IS BIMODAL, AND THE MEDIAN ALONE MISLEADS. 41 of 121 rows emit at EXACTLY 0 s - the moment had
already ended and the sig bar is the last event in the chain; all 11 `forward` rows and 30 of 62
`confirmed` rows are in that group. The other 80 bind on the moment's END ROW, which is not knowable
until the breaking v3 row prints, and those run a median 340 s. Every `lookback` and `gap` row is in
the second group by construction.

THE LADDER IS NOT THE EMIT BAR. The revision test below steps a ladder of v3 row bars, which is the
right stepping for "did an answer change" - answers only change when a row prints. It is the WRONG
stepping for latency: a moment's end is always a v3 row, but `rev` and `actionable` are ordinary tape
bars and can fall between two rows, so the ladder rounds those UP. `emit_bar()` computes the true bar
and the latency block reports from that. Reporting the rung gave a median of 325 s, which is 160 s
too high.


Joe 0929: *"your 'run forward on a bounded window' sounds like lookahead, but you could just be
saying 'run in realtime'"*. The second one. At every cutoff bar `k` the producer is handed ONLY
bars 0..k - the v3 rows that have printed, the ws1mage-rev legs whose own confirmation bar is at or
before `k`, and `release(last_bar=k)` - and asked what it would emit. The cutoff ladder is every v3
row bar in the window, because that is when new information actually arrives.

THE TEST IS NOT "does it match history". It is "does an answer it has already given ever change".
A timestamp emitted at cutoff k and different at cutoff k' is the producer using data the live run
will not have. Nothing else produces that signature.

Two emission rules are replayed side by side:
  EAGER  emit as soon as the moment's run is broken and the resolved bars have passed
  SETTLED  same, but wait for k >= i1 + lag_bars first, so `release`'s confirm window is never
           clipped. coil_moment.release's own docstring flags the clip as the hazard: "A clipped
           window can only fail to disconfirm, so a release confirmed on one is confirmed on less
           evidence than the rest".
"""
import sys, numpy as np, datetime as dt, io, collections
sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
import report_coil_exit as RCE
from optimus9.compute import coil_exit
from optimus9.compute.coil_moment import moments, release
from optimus9.compute.stretchy_leash import combined_coil, support_count
from optimus9.compute.v3_config import v3_config
from optimus9.analysis.jig import ws1mage_rev
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr = _e
ROLES = RCE.ROLES

db = DatabaseManager(**get_db_config()); db.connect()
C = v3_config(db)
ts, lines, hi, lo, tfs = RCE.load(db, C)
U = lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000.0, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
grid = C['grid_s']; lag = C['confirm_lag_s']//grid; look = C['lookback_s']//grid
keys = C['coil_lines']; support_keys = ['ws%d' % t for t in tfs]
LEGS = ws1mage_rev(lines[C['dr_line_a'].replace('Mage','')]['Mage'],
                   lines[C['sig_line'].replace('Mage','')]['Mage'], hi, lo,
                   dwell=C['dwell'], rev_wob=C['rev_wob'], hold=C['boundary_xwob'])
r_ = db.execute("SELECT wsl_v3_knobs k, wsl_win w FROM wsf_leash WHERE wsl_knobs LIKE 'v7%%' LIMIT 1",
                fetch=True)[0]
knobs = r_['k']; w0, w1 = r_['w'].split('..')
src = db.execute('SELECT wdv_ms, wdv_dr FROM wsf_dtf_v3 WHERE wdv_knobs=%s AND wdv_utc>=%s '
                 'AND wdv_utc<%s ORDER BY wdv_ms, wdv_line', (knobs, w0, w1), fetch=True)
ann = [dict(i=int(np.searchsorted(ts, int(r['wdv_ms']))), dr=int(r['wdv_dr']),
            ok=support_count(lines, support_keys, int(r['wdv_dr']),
                             int(np.searchsorted(ts, int(r['wdv_ms'])))) >= C['support_min'])
       for r in src]
print('R|v3 rows (the cutoff ladder)|%d|first %s|last %s' % (len(ann), U(ann[0]['i']), U(ann[-1]['i'])))

_cc = {}
def mkcc(d):
    def cc(i, _d=d):
        v = _cc.get((i, _d))
        if v is None:
            v = float(combined_coil({k: {rr: lines[k][rr][i] for rr in ROLES} for k in keys}, keys, _d))
            _cc[(i, _d)] = v
        return v
    return cc

def legs_at(d, k):
    L = LEGS[d]; s, sc = L['sig'], L['sig_conf']
    m = sc <= k
    return {'dwell_ok': L['dwell_ok'][L['dwell_ok'] <= k], 'rev': L['rev'][L['rev'] <= k],
            'sig': s[m], 'sig_conf': sc[m]}

def emit_bar(m, ex, lag_bars, settled):
    """The true bar this moment's answer can first be emitted. Not the ladder rung - see above.

    The moment is known-ended at its breaking row; the answer needs `rev` and `actionable` to have
    passed; `settled` additionally waits for the confirm window to be unclipped.
    """
    brk = m['brk'] if m['brk'] is not None else m['i1']
    b = max(brk, ex['rev'], coil_exit.fired(ex)[1])
    return max(b, m['i1'] + lag_bars) if settled else b


FIRST = {'eager': {}, 'settled': {}}
REV   = {'eager': [], 'settled': []}
LATENCY = {'eager': [], 'settled': []}
for j in range(len(ann)):
    k = ann[j]['i']
    for m in moments(ann[:j+1]):
        if m['brk'] is None:
            continue                                   # the run is not broken yet - no moment
        d = m['dr']
        p, conf = release(mkcc(d), m['i0'], m['i1'], lag, last_bar=k)
        ex = coil_exit.resolve(m, p, conf, legs_at(d, k), lag, look, bool(C['gap_fill']))
        if ex['rev'] is None or ex['rev'] > k or coil_exit.fired(ex)[1] > k:
            continue                                   # not resolvable yet - this is latency
        ansr = (ex['rev'], coil_exit.fired(ex)[1], ex['via'])
        for mode in ('eager', 'settled'):
            if mode == 'settled' and k < m['i1'] + lag:
                continue
            F = FIRST[mode]
            if m['i0'] not in F:
                F[m['i0']] = (k, ansr)
                LATENCY[mode].append(int(ts[emit_bar(m, ex, lag, mode == 'settled')])
                                     - int(ts[ex['rev']]))
            elif F[m['i0']][1] != ansr:
                REV[mode].append((m['i0'], F[m['i0']], (k, ansr)))
                F[m['i0']] = (F[m['i0']][0], ansr)      # carry the new one so repeats aren't re-counted

# the historical full-window answer, for coverage
_t, hist = RCE.walk(db, C, knobs, w0, w1)
H = {r['mo']['i0']: (r['rev'], coil_exit.fired(r)[1], r['via']) for r in hist}
print()
print('S|mode|moments emitted|of %d historical|REVISIONS|matches history|differs from history' % len(H))
for mode in ('eager', 'settled'):
    F = FIRST[mode]
    same = sum(1 for i0, (_k, a) in F.items() if i0 in H and H[i0] == a)
    diff = sum(1 for i0, (_k, a) in F.items() if i0 in H and H[i0] != a)
    print('S|%s|%d|%d|%d|%d|%d' % (mode, len(F), len(H), len(REV[mode]), same, diff))
print()
for mode in ('eager', 'settled'):
    L = sorted(LATENCY[mode])
    if not L: continue
    print('L|%s emission latency (emit bar - sig bar)|n %d|p25 %d s|median %d s|p75 %d s|p90 %d s'
          '|max %d s|mean %.0f s'
          % (mode, len(L), L[int(len(L)*.25)]//1000, L[len(L)//2]//1000, L[int(len(L)*.75)]//1000,
             L[int(len(L)*.90)]//1000, L[-1]//1000, np.mean(L)/1000.0))
    z = sum(1 for v in L if v == 0)
    print('L|%s|exactly 0 s|%d of %d (%.1f%%)' % (mode, z, len(L), 100.0*z/len(L)))
print()
for mode in ('eager', 'settled'):
    if not REV[mode]:
        print('V|%s|NO REVISIONS - every answer it gave, it kept' % mode); continue
    print('V|%s|%d REVISIONS' % (mode, len(REV[mode])))
    print('V|moment first|first said at|rev|act|via|then at|rev|act|via')
    for i0, (k1, a1), (k2, a2) in REV[mode][:40]:
        print('V|%s|%s|%s|%s|%s|%s|%s|%s|%s' % (U(i0), U(k1), U(a1[0]), U(a1[1]), a1[2],
                                                U(k2), U(a2[0]), U(a2[1]), a2[2]))
print()
miss = [i0 for i0 in H if i0 not in FIRST['settled']]
print('M|historical moments NEVER emitted in realtime|%d' % len(miss))
for i0 in sorted(miss)[:20]:
    print('M|%s|hist rev %s|via %s' % (U(i0), U(H[i0][0]) if H[i0][0] is not None else '-', H[i0][2]))
db.disconnect()
