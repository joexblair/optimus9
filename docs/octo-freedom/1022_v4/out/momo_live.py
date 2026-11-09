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
import bisect as _bisect
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
#   NO EXPERIMENT FLAG IS GRANTED HERE. HIS 1108 GO: *"yes thanks"*, on making the live process
#   refuse unless the request asks for an experiment. It used to run
#   `os.environ.setdefault('W_V4_EXPERIMENT', '1')`, which declared EVERY live run an experiment,
#   so v4_knobs.check() never refused a knob off the bank and the provenance block was the only
#   guard. On 1108 that guard failed in the one way it can: a paste that started at the table's
#   first row cut the block out, and he held an off-ruled xcv table for a turn without any way to
#   see it. Now an off-bank launch refuses at import, and a caller who WANTS an experiment passes
#   W_V4_EXPERIMENT=1 itself.

DIR = os.environ.get('W_LIVE_DIR', '/home/joe/.claude/jobs/7c82535c/tmp/live')
for d in ('req', 'out'):
    os.makedirs(os.path.join(DIR, d), exist_ok=True)

#   ONE PROCESS PER REQUEST DIRECTORY. On 1108 two of them served one directory for 23 minutes:
#   a `stop` or a `reload` is consumed by whichever polls first, so one process reloaded and the
#   other kept answering with the old code and a stale ruling posture. The pid file is written
#   AFTER the check and removed on a clean exit; a stale one whose pid is gone does not block.
_LOCK = os.path.join(DIR, 'SERVING.pid')
if os.path.exists(_LOCK):
    try:
        _old = int(open(_LOCK).read().strip())
        os.kill(_old, 0)
    except (ValueError, ProcessLookupError, PermissionError, OSError):
        _old = None
    if _old:
        sys.stderr.write('REFUSED: pid %d is already serving %s. Stop it first.\n' % (_old, DIR))
        raise SystemExit(2)
with open(_LOCK, 'w') as _fh:
    _fh.write('%d\n' % os.getpid())
import atexit as _atexit
_atexit.register(lambda: os.path.exists(_LOCK) and os.remove(_LOCK))

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
    import xcv_report as XR
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
        LG, TR = chain(str(q['day']))
        out += R.stages_table(LG, str(q['day']))
        return out
    if kind == 'c3rmage':
        #   HIS 1108 item 10: *"I want to see what improvements we get from opening a c3r trade at
        #   the ws1Mage reversal. I'm not sure if ws1Mage needs to be oob or ib or ex fence or in
        #   fence. it will be good to find out"*.
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        lab = str(q.get('read', 'ws3r emerging, rest closed-prev'))
        out += ['', '# c3r opened at the ws1Mage reversal, %s to %s'
                % (str(q['from']), str(q['to'])), '']
        out += R.c3rmage_table(LN, A, B, lab)
        return out
    if kind == 'tawaway':
        out += XR.tawaway_table(LN, str(q['at']), str(q['ev']), str(q['s0']),
                                side=str(q.get('side', 'HIGH')),
                                hi=int(q.get('hi', 30)), lo=int(q.get('lo', 10)))
        return out
    if kind == 'xcvdiff':
        out += XR.xcvdiff_table(LN, str(q['ext']), str(q['at']),
                                tf=int(q.get('tf', 5)),
                                label=str(q.get('label', 'cross')),
                                anchor=q.get('anchor'))
        return out
    if kind == 'lift':
        out += XR.lift_table(LN, str(q['from']), str(q['to']), side=str(q.get('side', 'LOW')),
                             tfs=str(q.get('tfs', '1,2,3')), also=str(q.get('also', '4,5')))
        return out
    if kind == 'xcvopp':
        out += XR.xcvopp_table(LN, str(q['day']), tf=int(q.get('tf', 5)),
                               cap_min=q.get('cap_min'))
        return out
    if kind == 'xcv':
        out += XR.xcv_table(LN, str(q['day']), tf=int(q.get('tf', 5)))
        return out
    if kind == 'xdiag':
        out += XR.xdiag_table(LN, str(q['from']), str(q['to']), int(q['tf']),
                              side=str(q.get('side', 'HIGH')))
        return out
    if kind == 'xcross':
        out += XR.xcross_table(LN, str(q['day']), tf=int(q.get('tf', 5)))
        return out
    if kind == 'legmfe':
        #   HIS 1108: *"can you derive that from sweep-pivots? using a rolling 8 hour window, and
        #   measuring on TF1,2,3 and gcws30 timeframes, what MFE differences can you detect inside
        #   of 08-08 to 08-30?"*
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        tfs = tuple(q.get('tfs') or ('ws1Mage', 'ws2Mage', 'ws3Mage', 'gcws30Mage'))
        out += ['', '# the leg MFE per timeframe, rolling %g h, %s to %s'
                % (float(q.get('win_h', 8.0)), str(q['from']), str(q['to'])), '']
        out += R.legmfe_table(LN, A, B, tfs, float(q.get('win_h', 8.0)),
                              float(q.get('step_h', 1.0)))
        return out
    if kind == 'cadlist':
        out += XR.cadlist_table(LN, str(q['from']), str(q['to']))
        return out
    if kind == 'pivstop':
        #   HIS 1108: *"lets see if you can use your research to find a dynamic stop for each
        #   signal"*. The structural stop off the last CONFIRMED price pivot, per c3r firing.
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        lab = str(q.get('read', 'ws3r emerging, rest closed-prev'))
        pcs = tuple(int(x) for x in q.get('gaps', (24, 48, 60)))
        out += ['', '# the structural stop per c3r signal, %s to %s'
                % (str(q['from']), str(q['to'])), '']
        out += R.pivstop_table(LN, A, B, lab, pcs)
        return out
    if kind == 'c3rscan':
        #   HIS 1108: *"we'll need a list of the firings across 08-25 to 08-31 (with maemfe) to
        #   validate the change"* / *"run the 7 day anyway"*.
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        lab = str(q.get('read', 'ws3r emerging, rest closed-prev'))
        out += ['', '# fdm2-3r-cadence, every arm from %s to %s' % (str(q['from']), str(q['to'])),
                '']
        out += R.cad3r_scan(LN, A, B, lab)
        return out
    if kind == 'vals':
        #   HIS 1108: raw per-bar values, both reads, with the oob and ex-fence flags beside each.
        nms = q.get('lines') or [str(q.get('line', 'ws1Mage'))]
        if isinstance(nms, str):
            nms = [x.strip() for x in nms.split(',') if x.strip()]
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        out += ['', '# %s values, %s side, %s .. %s'
                % (', '.join(nms), q.get('side', 'HIGH'), str(q['from']), str(q['to'])), '']
        out += R.vals_table(LN, nms, sd, A, B)
        return out
    if kind == 'runs':
        #   HIS 1108: *"I need the range where ws3r is ex-20/80-fence to understand your data"*.
        nm = str(q.get('line', 'ws3r'))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        A, B = ln.K(str(q['from'])), ln.K(str(q['to']))
        out += ['', '# %s ex-20/80 and oob runs, %s side' % (nm, q.get('side', 'HIGH')), '']
        out += R.runs_table(LN, nm, sd, A, B)
        return out
    if kind == 'board':
        out += R.board_table(LN, str(q['at']), since_s=q.get('since'),
                             side=str(q.get('side', 'HIGH')))
        return out
    if kind == 'legfrom':
        out += R.legfrom_table(LN, str(q['open']), to_s=q.get('to'),
                               dr=str(q.get('dir', 'LONG')))
        return out
    if kind == 'cad3r':
        #   HIS 1107 `fdm2-3r-cadence`. A REPORT on his own markers - no leg reads it.
        mk = ln.K(str(q['at']))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        out += ['', '# fdm2-3r-cadence at %s, %s side' % (str(q['at']), q.get('side', 'HIGH')), '']
        out += R.cad3r_table(LN, sd, mk)
        return out
    if kind == 'trail':
        #   HIS 1107 FIVE-CLAUSE SPEC. A raw read at one of his own markers - no mech, no verdict.
        mk = ln.K(str(q['at']))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        out += ['', '# the trail at %s, %s side' % (str(q['at']), q.get('side', 'HIGH')), '']
        out += R.trail_table(LN, sd, mk)
        return out
    if kind == 'window':
        #   HIS 1107 ws3r-opener question. A pure line read in a bar range - no mech, no chain.
        day = str(q['day'])
        A = ln.K(str(q.get('from', day + ' 00:00:00')))
        B = ln.K(str(q.get('to', day + ' 23:59:55')))
        sd = +1 if str(q.get('side', 'HIGH')).upper() == 'HIGH' else -1
        out += ['', '# the oob crosses of ws1b and ws1r, ws2r, ws3r, %s side' % q.get('side'), '']
        out += R.window_table(LN, sd, A, B)
        return out
    if kind == 'pct50':
        LG, TR = chain(str(q['day']))
        out += R.pct50_for(LN, LG, str(q['day']), at=str(q.get('at', '')))
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
        LG, TR = chain(str(q['day']))
        out += R.leg_report(LN, LG, TR, SIGS, str(q['day']), q['open'],
                            resig=bool(q.get('resig', True)))
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
                #   IT ANSWERS BEFORE IT EXITS. It used to return without writing one, so `ask.py`
                #   always timed out on a stop and I could not tell a stop that worked from one
                #   that was never read. On 1108 that hid TWO live processes serving one request
                #   directory: each restart posted a stop, one process took it, the other kept
                #   answering, and a `reload` then landed on only one of them.
                with open(os.path.join(DIR, 'out', i + '.md'), 'w') as fh:
                    fh.write('\nSTOPPING - pid %d\n' % os.getpid())
                with open(os.path.join(DIR, 'out', i + '.done'), 'w') as fh:
                    fh.write('0.00\n')
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
                globals()['XR'] = importlib.reload(XR)
                assert set(LN) >= {'close', 'CPR', 'EMR', 'MGE', 'CPM', 'HI', 'PIN',
                                   'RSID'}, \
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
