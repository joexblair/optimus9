"""The fdm re-entry signal list, cached on disk and keyed so it CANNOT serve a stale answer.

WHY THIS AND NOT SOMETHING ELSE. Measured on 2026-11-06: a one-day debugging table costs 1,532 s,
and 1,484.7 s of that - 96.9% - is RE.signals scanning the whole 1,632,960-bar tape. The tape load
is 23.5 s and the x/m ladders 18.7 s. Caching the signal list is the only change that moves the
number, and it is HIS 1106 ask applied to the thing that actually costs: *"every single event
cached in a table or memory, instead of re-deriving"*.

THE KEY IS THE THING THAT MAKES THIS SAFE, and it is built from two parts:

  1  the 32 knobs v4_fdm_reentry actually reads, by name, taken from a grep of the module rather
     than from a list I keep in my head. NOT every banked knob: arming fdm2-momo changes no signal,
     and keying on it would throw away a 25-minute scan for nothing.
  2  a sha256 over the BYTES of every input array - ws1b, all 30 r lines in both reads, gcws30b and
     the closed-prev Mage set. That covers any upstream change to the line config without my having
     to enumerate what feeds it. A changed input is a changed key, full stop.

THE FAULT THIS DESIGNS OUT is the one that already bit us today: ab_legs.json held 2,453 decision
rows with no record of which knobs produced them, so a leg report replayed a superseded arm and
printed two identical arms for two different mechs. A cache without a key is a trap.

    python3 out/re_sigcache.py          builds and saves, printing the key and the timings
"""
import hashlib
import io
import os
import pickle
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
#   THE EXPERIMENT FLAG IS NOT SET ON IMPORT. It used to be, and on 1108 that leaked: the live
#   process imports this module, so a `reload` re-read W_V4_EXPERIMENT as SET and reported an
#   experiment on a run nobody asked to be one - and an off-bank reload would have stopped
#   refusing. An import must not change the process's ruling posture. A standalone run of THIS
#   module still declares itself, under __main__ below.

CACHE_DIR = os.environ.get('W_SIGCACHE_DIR', '/home/joe/.claude/jobs/7c82535c/tmp/sigcache')

#   EVERY KNOB v4_fdm_reentry READS, from a grep of the module. Adding a knob there without adding
#   it here would let a changed rule serve an unchanged cache, so the assert below re-greps the
#   module on every call and refuses when the two lists disagree.
RE_KNOBS = (
    'FDM_FNC_2080', 'FDM_RE_B_FNC', 'FDM_RE_CLIMB', 'FDM_RE_CLIMB_HI', 'FDM_RE_FIRE_IB',
    'FDM_RE_GATE_TF', 'FDM_RE_IB_XWOB', 'FDM_RE_M4_AT', 'FDM_RE_M4_FNC', 'FDM_RE_M4_ON',
    'FDM_RE_REV_MECH', 'FDM_RE_REV_READ', 'FDM_RE_REV_TF', 'FDM_RE_SCAN_FLOOR', 'FDM_RE_SCAN_HI',
    'FDM_RE_WIN_CLOSE', 'FDM_RE_WIN_OPEN', 'FDM_RE_WS5_FNC', 'FDM_RE_WS6_GATE',
    'FDM_RE_XCROSS_FNC_AT', 'FDM_RE_XCROSS_LO', 'FDM_RE_XCROSS_ON', 'FDM_RE_XCROSS_TFS',
    'FDM_RE_XCROSS_UP_READ', 'FDM_RE_XWOB', 'L2_MOM_MAXTF', 'LIFT_PTS', 'LIFT_TOL', 'LIFT_WOB',
    'OOB_FNC', 'OOB_HI', 'OOB_LO',
)


def _grep_knobs():
    """The knobs v4_fdm_reentry reads, re-read from the module's own source. -> set."""
    import re
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v4_fdm_reentry.py')
    src = open(os.path.abspath(p)).read()
    return set(re.findall(r'K\.([A-Z][A-Z0-9_]*)', src))


def _hash_arrays(*objs):
    """sha256 over the bytes of every array handed in, dicts walked in key order. -> hex."""
    h = hashlib.sha256()
    for o in objs:
        if isinstance(o, dict):
            for k in sorted(o, key=lambda z: (str(type(z)), z)):
                h.update(str(k).encode())
                h.update(np.ascontiguousarray(np.asarray(o[k], float)).tobytes())
        elif o is None:
            h.update(b'None')
        else:
            h.update(np.ascontiguousarray(np.asarray(o, float)).tobytes())
    return h.hexdigest()


def key(K, B1, R, G, EMR, CPM):
    """The cache key: the re-entry knobs plus a hash of every input array. -> (hex, [str]).

    THE ASSERT IS THE CONTRACT: the module's own source is re-grepped and compared to RE_KNOBS, so
    a knob added to the re-entry rules cannot silently keep serving an old cache.
    """
    found = _grep_knobs()
    missing = sorted(found - set(RE_KNOBS))
    assert not missing, ('v4_fdm_reentry now reads %s, which is not in the cache key - add it to '
                         'RE_KNOBS or the cache will serve a stale signal list' % ', '.join(missing))
    kv = ['%s=%s' % (n, getattr(K, n, None)) for n in RE_KNOBS]
    #   HIS 1110 LIFT-OFF e PATH: v4_fdm_reentry's lift-off now takes the ws{TF}e e-cross reversals (6B). Its
    #   knobs and the e lines themselves are in the key, or a scan built before it would keep being served.
    import v4_lift_e as LE
    kv += ['%s=%s' % kv2 for kv2 in LE.knobs()]
    if LE.LIFT_E_ON:
        import v4_ws_e as WSE
        kv.append('WSE=%s|%s' % (WSE.E_MECH, WSE.E_VERSION))
        ah0 = _hash_arrays(WSE.lines())
        kv.append('E_LINES=%s' % ah0[:16])
    ah = _hash_arrays(B1, R, G, EMR, CPM)
    h = hashlib.sha256(('|'.join(kv) + '|' + ah).encode()).hexdigest()[:16]
    return h, kv


def path(h):
    os.makedirs(CACHE_DIR, exist_ok=True)
    return os.path.join(CACHE_DIR, 'resig_%s.pkl' % h)


def load_or_build(K, RE, B1, R, G, EMR, CPM, verbose=True):
    """The signal list for these inputs, from the cache when the key matches. -> (list, dict).

    The returned dict carries the key, whether it was a hit, and the seconds each step took, so a
    caller can print its own provenance instead of asserting that the cache was used.
    """
    t0 = time.time()
    h, kv = key(K, B1, R, G, EMR, CPM)
    tk = time.time() - t0
    p = path(h)
    if os.path.exists(p):
        t = time.time()
        with open(p, 'rb') as fh:
            sigs = pickle.load(fh)
        return sigs, dict(key=h, hit=True, key_s=tk, io_s=time.time() - t, build_s=0.0,
                          n=len(sigs), path=p)
    t = time.time()
    sigs = RE.signals(B1, R, G=G, EMR=EMR, CPM=CPM)
    bs = time.time() - t
    t = time.time()
    tmp = p + '.part'
    with open(tmp, 'wb') as fh:
        pickle.dump(sigs, fh, protocol=4)
    os.replace(tmp, p)      # the rename is atomic, so a reader never sees a half-written cache
    return sigs, dict(key=h, hit=False, key_s=tk, io_s=time.time() - t, build_s=bs,
                      n=len(sigs), path=p)


if __name__ == '__main__':
    #   A standalone build of the signal cache reads the arm's knobs off the bank on purpose, so it
    #   declares itself here rather than at import - see the note at the top.
    os.environ.setdefault('W_V4_EXPERIMENT', '1')
    _e = sys.stderr
    sys.stderr = io.StringIO()
    try:
        import v4_knobs as K
        import v4_fdm2 as F2
        import v4_fdm_reentry as RE
        import ln
    finally:
        sys.stderr = _e
    t = time.time()
    LN = F2.load()
    tl = time.time() - t
    sigs, info = load_or_build(K, RE, LN['B1'], LN['CPR'], LN['G30B'], LN['EMR'], LN['CPM'])
    print('| the cache | value |')
    print('|---|---|')
    print('| the tape | %d bars, %s .. %s |'
          % (len(LN['close']), ln.U(0), ln.U(len(LN['close']) - 1)))
    print('| the key | %s |' % info['key'])
    print('| a hit | %s |' % ('yes' if info['hit'] else 'no - it was built and saved'))
    print('| the signals | %d on the tape |' % info['n'])
    print('| the file | %s |' % info['path'])
    print('| F2.load, s | %.1f |' % tl)
    print('| keying, s | %.1f |' % info['key_s'])
    print('| the scan, s | %.1f |' % info['build_s'])
    print('| reading or writing the cache, s | %.1f |' % info['io_s'])
    print('| the knobs in the key | %d - %s |' % (len(RE_KNOBS), ', '.join(RE_KNOBS)))
