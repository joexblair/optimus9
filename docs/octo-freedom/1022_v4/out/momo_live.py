"""The live fdm2 process: load the arrays ONCE, then answer debugging queries in seconds.

HIS 1106 GO: *"that's definietly the goal - every single event cached in a table or memory, instead
of re-deriving"* / *"yes thanks"*.

WHY IT EXISTS, measured rather than assumed: a one-shot debugging table spends almost all of its
time in F2.load() and _momo_lines() building whole-tape arrays, and NONE of that shrinks when the
leg's open bar is handed in - the leg walk already starts at the open. Holding the arrays is the
only change that moves the number.

THE PROTOCOL IS FILES, not a socket or a port - nothing to bind, nothing to leak:

    <DIR>/req/<id>.json     {"kind": "...", ...}        written by the caller
    <DIR>/out/<id>.md       the answer, markdown         written here
    <DIR>/out/<id>.done     written LAST, so a reader never sees a half-written answer
    <DIR>/READY             written once the arrays are up, with the load timings

THE KINDS:

    day      {"day": "2026-08-23"}                     the day's legs + the cad walk summary
    leg      {"day": ..., "open": "YYYY-MM-DD HH:MM:SS"}   one leg's every timestamped event
    cadwalk  {"day": ..., "b0": "YYYY-MM-DD HH:MM:SS"}     one cad walk, bar by bar
    knobs    {}                                        every banked knob, its value and its gloss
    reload   {}                                        re-import the knobs and fdm2 WITHOUT
                                                       touching the tape, so a knob edit costs
                                                       seconds instead of a full rebuild
    stop     {}                                        exit

EVERY ANSWER CARRIES ITS PROVENANCE: the bar count, the hash over all banked knobs, and which
knobs sit off the bank. A cached answer that cannot say which knob set produced it is the exact
fault that made a leg report replay a superseded arm.

THE DAY'S CHAIN IS MEMOISED per (day, knob hash). A knob change changes the hash, so the next
query recomputes instead of serving a stale chain - the staleness is designed out rather than
remembered.
"""
import importlib
import io
import json
import os
import sys
import time
import traceback

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.environ.setdefault('W_V4_EXPERIMENT', '1')

DIR = os.environ.get('W_LIVE_DIR', '/home/joe/.claude/jobs/7c82535c/tmp/live')
for d in ('req', 'out'):
    os.makedirs(os.path.join(DIR, d), exist_ok=True)

T = {}
t0 = time.time()
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_signal as SG
    import v4_fdm_reentry as RE
    import ln
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
    import momo_render as R
    import re_sigcache as SC
finally:
    sys.stderr = _e
T['the imports'] = time.time() - t0

t = time.time()
LN = F2.load()
T['F2.load - the tape and every line array'] = time.time() - t
t = time.time()
M = F2._momo_lines(LN)
T['_momo_lines - the x and m ladders, the r-pred flags and the pinned masks'] = time.time() - t
t = time.time()
#   THE SIGNAL LIST COMES FROM THE KEYED CACHE. Measured: the scan is 1,484.7 s of a 1,532.2 s
#   cold start - 96.9% - and its answer only changes when one of the 32 re-entry knobs or one of
#   its input arrays changes. The key carries both, so a hit cannot be stale.
SIGS, SCI = SC.load_or_build(K, RE, LN['B1'], LN['CPR'], LN['G30B'], LN['EMR'], LN['CPM'])
T['the re-entry signals - %s' % ('a CACHE HIT, key %s' % SCI['key'] if SCI['hit']
                                 else 'a cache MISS, scanned and saved under key %s' % SCI['key'])
  ] = time.time() - t
LOADED = time.time() - t0

CHAIN = {}          # (day, knob hash) -> (the legs, the cad walk trace)


def chain(day):
    """The day's legs and cad walk trace, memoised on (day, the knob hash). -> (LG, TR)."""
    h, _ = R.knob_hash()
    key = (day, h)
    if key in CHAIN:
        return CHAIN[key]
    A, B = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
    hit = [x for x in SIGS if int(x['bar']) >= A]
    assert hit, 'no fdm re-entry signal at or after %s' % ln.U(A)
    g = hit[0]
    F2.XCAD_TRACE = []
    LG = F2.legs(LN, (SG.fire_bar(g), SG.target_side(SG.direction(int(g['side']))),
                      'fdm re-entry %s' % ln.U(int(g['bar']))), B, resig=SIGS)
    TR = list(F2.XCAD_TRACE)
    F2.XCAD_TRACE = None
    CHAIN[key] = (LG, TR)
    return CHAIN[key]


def answer(q):
    """One request -> the markdown answer. -> [str]."""
    kind = str(q.get('kind', ''))
    out = R.stamp(LN)
    if kind == 'knobs':
        out += ['', '# every banked knob, its live value and what it sets', '']
        out += R.head('the knob = its value', 'in the bank', 'the ruled value')
        for n in sorted(K.RULED):
            v = getattr(K, n, None)
            out.append(R.row('%s = %s' % (n, v),
                             'yes' if str(v) == str(K.RULED[n][0]) else 'OFF THE BANK',
                             K.RULED[n][0]))
        return out
    if kind == 'stages':
        #   HIS 1106: *"cadence event can only produce cad_walk or cad_rev-trade - there is no
        #   third option... where is the gap?"*. This counts every verdict row the day produced,
        #   by label, and names the bar each one landed on relative to its own cadence event - so a
        #   verdict that did not land ON the cadence event is visible as such.
        day = str(q['day'])
        LG, TR = chain(day)
        cnt, late = {}, []
        for L in LG:
            for r in L['rows']:
                st = str(r['stage'])
                cnt[st] = cnt.get(st, 0) + 1
                if st.startswith('cad_') and int(r.get('ev', r['bar'])) != int(r['bar']):
                    late.append((int(r['ev']), int(r['bar']), st, str(r['why'])))
        out += ['', '# every verdict row on %s, by label' % day, '']
        out += R.head('the label', 'rows', 'whose verdict it is', 'is it one of your two')
        OWN = {'cad_walk': ('the cadence event', 'yes - walk'),
               'cad_rev_trade': ('the cadence event', 'yes - rev-trade'),
               'cad_no_action': ('the cadence event', 'NO - a THIRD verdict'),
               'cwlk_seam': ('the cad walk', 'neither - a setup row'),
               'cwlk_start': ('the cad walk', 'neither - a setup row'),
               'cwlk_momo_vote': ('the cad walk', 'neither - a vote row'),
               'cwlk_rev_trade': ('the cad walk', 'yes - rev-trade')}
        for st in sorted(cnt):
            w, y = OWN.get(st, ('?', '?'))
            out.append(R.row(st, cnt[st], w, y))
        out += ['', '# every cadence-event verdict that did NOT land on its own cadence event bar',
                '']
        out += R.head('the cadence event', 'the bar the verdict landed on', 'seconds late',
                      'the label', 'why')
        for ev, b, st, why in sorted(late):
            out.append(R.row(ln.U(ev), ln.U(b), (b - ev) * 5, st, why.replace('|', '\\|')[:160]))
        if not late:
            out.append(R.row('none', '-', '-', '-', '-'))
        return out
    if kind == 'day':
        day = str(q['day'])
        LG, TR = chain(day)
        out += ['', '# the legs of %s' % day, '']
        out += R.legs_table(LN, LG)
        out += ['', '# every cad walk on %s, and which branch ended it' % day, '']
        out += R.cadwalk_summary(TR)
        return out
    if kind == 'leg':
        day = str(q['day'])
        LG, TR = chain(day)
        want = [str(x) for x in (q['open'] if isinstance(q['open'], list) else [q['open']])]
        hit = [L for L in LG if ln.U(int(L['opn'])) in want]
        assert hit, 'no leg opens at %s on %s' % (', '.join(want), day)
        for L in hit:
            sd = int(L['side'])
            out += ['', '# the incoming trade %s | %s | target side %s'
                    % (ln.U(int(L['opn'])), 'LONG' if sd > 0 else 'SHORT',
                       'HIGH' if sd > 0 else 'LOW'), '']
            out += R.leg_table(LN, L, SIGS if q.get('resig', True) else None)
            bs = sorted({t['b0'] for t in TR
                         if int(L['opn']) <= t['b0'] <= int(L['exit'])})
            for b0 in bs:
                out += ['', '## its cad walk from %s' % ln.U(b0)]
                out += R.cadwalk_table(TR, b0)
        return out
    if kind == 'cadwalk':
        day = str(q['day'])
        LG, TR = chain(day)
        b0 = ln.K(str(q['b0']))
        assert any(t['b0'] == b0 for t in TR), 'no cad walk starts at %s on %s' % (q['b0'], day)
        out += ['', '# the cad walk from %s, bar by bar' % str(q['b0'])]
        out += R.cadwalk_table(TR, b0)
        return out
    raise AssertionError('unknown kind %r' % kind)


def serve():
    with open(os.path.join(DIR, 'READY'), 'w') as fh:
        fh.write('| the stage | seconds |\n|---|---|\n')
        for k, v in T.items():
            fh.write('| %s | %.1f |\n' % (k, v))
        fh.write('| **the whole load** | **%.1f** |\n' % LOADED)
        fh.write('\n| the arrays | value |\n|---|---|\n')
        fh.write('| the tape | %d bars |\n' % len(LN['close']))
        fh.write('| the ladder timeframes | ws%d..ws%d |\n' % (M['tfs'][0], M['tfs'][-1]))
        fh.write('| the re-entry signals | %d on the tape |\n' % len(SIGS))
        fh.write('| the knob hash | %s |\n' % R.knob_hash()[0])
    print('READY in %.1f s' % LOADED, flush=True)
    while True:
        reqs = sorted(f for f in os.listdir(os.path.join(DIR, 'req')) if f.endswith('.json'))
        if not reqs:
            time.sleep(0.25)
            continue
        for f in reqs:
            rp = os.path.join(DIR, 'req', f)
            i = f[:-5]
            try:
                q = json.load(open(rp))
            except Exception:
                time.sleep(0.1)
                continue
            os.remove(rp)
            t1 = time.time()
            if str(q.get('kind')) == 'stop':
                print('STOP', flush=True)
                return
            if str(q.get('kind')) == 'reload':
                #   THE TAPE IS NOT RELOADED. LN is plain arrays and dicts, so the re-imported
                #   module reads the same data; only the code and the knobs move. _MOMO is rebuilt
                #   because the module-level cache resets, and the memoised chains are dropped
                #   because their knob hash may now be wrong.
                globals()['K'] = importlib.reload(K)
                globals()['F2'] = importlib.reload(F2)
                globals()['R'] = importlib.reload(R)
                assert set(LN) >= {'close', 'CPR', 'EMR', 'MGE', 'CPM', 'HI'}, \
                    'load() contract changed - the held arrays are no longer valid'
                globals()['M'] = F2._momo_lines(LN)
                CHAIN.clear()
                body = R.stamp(LN) + ['', 'reloaded the knobs and fdm2 in %.1f s, the tape was not '
                                      'touched, %d memoised chains dropped'
                                      % (time.time() - t1, 0)]
            else:
                try:
                    body = answer(q)
                except Exception:
                    body = ['```', traceback.format_exc(), '```']
            body.append('')
            body.append('_answered in %.2f s_' % (time.time() - t1))
            with open(os.path.join(DIR, 'out', i + '.md'), 'w') as fh:
                fh.write('\n'.join(body) + '\n')
            with open(os.path.join(DIR, 'out', i + '.done'), 'w') as fh:
                fh.write('%.2f\n' % (time.time() - t1))
            print('%s %s in %.2f s' % (i, q.get('kind'), time.time() - t1), flush=True)


serve()
