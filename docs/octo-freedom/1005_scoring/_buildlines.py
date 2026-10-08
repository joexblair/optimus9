"""BUILD THE r AND Mage LINE VARIANTS. 1008.

Joe 1008: *"if you want to sweep the Mage and r configs, go for it"*.

THE LIVE SPECS, read from `mech_lines(db, 'wsf')` and not from literals:
    r     ('k',  5, 8, 7, 'close')   -> KLine(rsi=5, stc=8, k_len=7)
    Mage  ('bb', 38, 0.93, 'close')  -> BB %B, length 38, mult 0.93

WHAT EACH VARIANT NEEDS BUILT:
    an r variant     ws1..ws25 r  - `_chain10` loads RL to CEIL_HI + 3 = ws26 exclusive
    a Mage variant   ws1..ws12 Mage, plus the 5 s / 15 s / 30 s Mage that `MTD` carries

BUILT SEQUENTIALLY, ON PURPOSE. Each Jig context is memory-heavy - rpl_cache's own comment says a
360-line build OOMs on 18 GB and caps a batch at 24 - and this box has 15 GB free. The CHAIN runs
are what gets parallelised afterwards; the builds do not.

NOTHING IS DELETED. Each variant's lines are their own cache files keyed on their own spec, so the
banked lines are untouched and a re-run of this script rebuilds only what is missing.
"""
import os, sys, time, json, itertools
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import mech_lines, override
from optimus9.orchestration.rpl_cache import LINE_DIR, _line_key, cache_jig_perline
import build_wsf_role_lines as B

# THE WINDOW MUST BE score39'S, NOT THE BUILDER'S. 1008.
#
# build_wsf_role_lines inherits build_ws_lines' END_MS, which sits at 2026-09-30, while score39
# keys on LG_TAPE_END - 2026-10-05 here. The cache key is md5(end|hours|warmup|spec), so a 5-day
# window difference produces a DIFFERENT FILE for the same spec. My first run of this script built
# all 421 lines at the builder's window; every one was a real line, none of them was the line
# score39 loads, and the sweep's own LIVE control scored -113.3843 against the +4.0627 the identical
# config scores through score39. That gap is what caught it.
#
# The builder's docstring names the hazard and exposes WSF_TAPE_END for it. Set it from the same
# env var score39 reads, so the two can never drift.
import datetime as _dt
_END = os.environ.get('LG_TAPE_END', '2026-10-04')
os.environ['WSF_TAPE_END'] = _END
END_MS = int(_dt.datetime.strptime(_END, '%Y-%m-%d')
             .replace(tzinfo=_dt.timezone.utc).timestamp() * 1000)
HOURS, WARMUP = B.HOURS, B.WARMUP
R_TFS = list(range(1, 26))            # ws1..ws25, what _chain10's RL covers
M_TFS = list(range(1, 13))            # ws1..ws12, what Mg covers
M_SUB = [5, 15, 30]                   # the sub-minute Mage lines MTD carries, in SECONDS

db = DatabaseManager(**get_db_config()); db.connect()
SPEC = {}
for g in mech_lines(db, 'wsf'):
    if g['role'] not in SPEC:
        _t, s_, m_ = g['override']; SPEC[g['role']] = (s_, m_)
row = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system LIMIT 1',
                 fetch=True)[0]
PXS = {'src': row['s'], 'len': row['l']}
db.disconnect()
R0 = SPEC['r'][0]; M0 = SPEC['Mage'][0]
print('# live r    %s' % (R0,), flush=True)
print('# live Mage %s' % (M0,), flush=True)
print('# end %d hours %s warmup %s' % (END_MS, HOURS, WARMUP), flush=True)

# ---- the variant grids, one knob at a time around the live spec
RV, MV = [], []
for rsi in (3, 4, 6, 8):      RV.append(('r', 'rsi=%d' % rsi,   ('k', rsi, R0[2], R0[3], R0[4])))
for stc in (5, 6, 10, 14):    RV.append(('r', 'stc=%d' % stc,   ('k', R0[1], stc, R0[3], R0[4])))
for kl in (4, 5, 9, 12):      RV.append(('r', 'k_len=%d' % kl,  ('k', R0[1], R0[2], kl, R0[4])))
for ln in (24, 30, 48, 60):   MV.append(('Mage', 'len=%d' % ln, ('bb', ln, M0[2], M0[3])))
for mu in (0.85, 0.90, 1.00, 1.10):
    MV.append(('Mage', 'mult=%.2f' % mu, ('bb', M0[1], mu, M0[3])))
VARIANTS = [('r', 'LIVE', R0)] + RV + [('Mage', 'LIVE', M0)] + MV

def ovr_for(role, spec):
    mode = SPEC[role][1]
    if role == 'r':
        return {'ws%dr' % t: override(t * 60, spec, mode) for t in R_TFS}
    o = {'ws%dMage' % t: override(t * 60, spec, mode) for t in M_TFS}
    o.update({'g%dMage' % s: override(s, spec, mode) for s in M_SUB})
    return o

# THE INVARIANT, not a comment: the LIVE variant's key MUST be the file score39 loads. If it is
# not, every variant is at the wrong window and the sweep is meaningless. Fail here, not in the
# results.
import io as _io, contextlib as _cl
_buf = _io.StringIO()
with _cl.redirect_stdout(_buf):
    import score39 as _SC
_live = override(60, *SPEC['r'])
assert _line_key(END_MS, HOURS, WARMUP, _live) == _line_key(_SC.EM, _SC.HOURS, _SC.WARMUP, _live), (
    'window mismatch: this script keys on end=%d hours=%s warmup=%s and score39 on end=%d '
    'hours=%s warmup=%s - every line would be built at the wrong window'
    % (END_MS, HOURS, WARMUP, _SC.EM, _SC.HOURS, _SC.WARMUP))
print('# window check PASSED: end %d hours %s warmup %s matches score39'
      % (END_MS, HOURS, WARMUP), flush=True)

have = set(os.listdir(LINE_DIR))
plan = []
for role, lbl, spec in VARIANTS:
    o = ovr_for(role, spec)
    miss = [n for n in o if _line_key(END_MS, HOURS, WARMUP, o[n]) + '.npy' not in have]
    plan.append((role, lbl, spec, o, miss))
print('\n# THE BUILD PLAN')
print('| role | variant | spec | lines needed | already cached | to build |')
print('|---|---|---|---|---|---|')
for role, lbl, spec, o, miss in plan:
    print('| %s | %s | %s | %d | %d | %d |'
          % (role, lbl, spec, len(o), len(o) - len(miss), len(miss)))
tot = sum(len(m) for _, _, _, _, m in plan)
print('\n# %d lines to build, ~2.6 s each plus ~23 s per Jig context -> roughly %d min'
      % (tot, int((tot * 2.6 + (tot / 24 + len(plan)) * 23) / 60)), flush=True)

MAP = {}
for role, lbl, spec, o, miss in plan:
    t0 = time.time()
    if miss:
        cache_jig_perline(END_MS, HOURS, WARMUP, {n: o[n] for n in miss}, pxs_cfg=PXS)
    paths = {n: os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, o[n]) + '.npy')
             for n in o}
    gone = [n for n, p in paths.items() if not os.path.exists(p)]
    MAP['%s|%s' % (role, lbl)] = dict(role=role, label=lbl, spec=list(spec), paths=paths,
                                      missing=gone)
    print('#   %-4s %-12s built %2d  missing %d  in %5.1fs'
          % (role, lbl, len(miss), len(gone), time.time() - t0), flush=True)
out = '/home/joe/.claude/jobs/6eb9931e/tmp/linemap.json'
json.dump(MAP, open(out, 'w'), indent=1)
print('\n# wrote %s with %d variants' % (out, len(MAP)), flush=True)
print('# BUILD COMPLETE', flush=True)
