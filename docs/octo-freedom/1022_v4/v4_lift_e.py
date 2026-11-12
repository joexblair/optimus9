"""Lift-off's e-cross reversal for v4 - its knobs and the e_path every v4 lift-off call hands in. Joe 1110.

HIS SPEC, 1110: *"when ws{TF}e crosses a racer, "walk back to look forward" for the time when ws{TF}e was most
extreme, before the cross. capture the ws{TF}r value at that time"* / *"-make that bar's value the new r
extremum"* / *"-if the following lift-off sample is less extreme (ie is closer to 50), then print the
reversal"* / *"--this might need a "minimum less extreme" knob - the data will tell us when I review the
update"*. The producer is jig.lift_off_e; jig.lift_off and jig.lift_off_pivot take the e_path built here.

HIS RULING ON REACH, 1110: 6B - in lift-off itself, so every lift-off reader gets it (*"SRP rules"*), and
2A - on for all of them at once: *"if they move, they move"*.

BANKED AND LIVE, Joe 1110: *"after that's validated, bank both mechs and make their configs the live machine"*. An
off-ruled run refuses on import unless W_LIFTE_EXPERIMENT=1. The spec is docs/octo-freedom/1110_lift_off_e.md.

THE KNOBS live here, NOT in v4_knobs (that file is not touched). Env overrides W_LIFTE_<NAME>.

    LIFT_E_ON        1        the e path on (1) or off (0). 0 is the 1022 lift-off exactly
    LIFT_E_STEP      48 bars  the walk-back step, 240 s, every TF - HIS 1A, jig.MC_GAP, his 1017 number
    LIFT_E_MIN_LESS  0.0      r-points a following sample must be closer to 50 than the extremum. HIS
                              "minimum less extreme" knob; 0 = any move closer prints. He sets it from the data
    LIFT_E_RACE      boundary,Mage,r   the race lines, in tie-report order - his race:{boundary,Mage,r}
    LIFT_E_RACE_READ closed_prev       the r and Mage it races to - the standard race (v4_fdm2.x_race)

ws1..ws30 HAVE AN e LINE since his 1110 *"add ws1-3 to towards/away and liftoff, and update webUI"* (config
version 2). A grid that is not the cached tape (a live harness) gets None - the e lines exist only on the tape -
and so does any TF outside the e line's band. Both are counted in SKIPS so a caller can print them.
"""
import os

import numpy as np

LIFT_E_ON = int(os.environ.get('W_LIFTE_ON', 1))
LIFT_E_STEP = int(os.environ.get('W_LIFTE_STEP', 48))
LIFT_E_MIN_LESS = float(os.environ.get('W_LIFTE_MIN_LESS', 0.0))
LIFT_E_RACE = tuple(os.environ.get('W_LIFTE_RACE', 'boundary,Mage,r').split(','))
LIFT_E_RACE_READ = os.environ.get('W_LIFTE_RACE_READ', 'closed_prev')
assert set(LIFT_E_RACE) <= {'boundary', 'Mage', 'r'} and LIFT_E_RACE, LIFT_E_RACE
assert LIFT_E_RACE_READ in ('closed_prev', 'emerging'), LIFT_E_RACE_READ

EXPERIMENT = os.environ.get('W_LIFTE_EXPERIMENT', '0') == '1'

#   THE RULED REGISTRY: knob -> (ruled value, provenance). check() runs on import.
RULED = {
    'LIFT_E_ON': (1, 'his 1110 6B + 2A: in lift-off itself, on for every reader - "if they move, they move"'),
    'LIFT_E_STEP': (48, 'his 1110 1A: the walk-back step, 48 bars = 240 s, every TF'),
    'LIFT_E_MIN_LESS': (0.0, 'his "minimum less extreme" knob; 0 = any move closer to 50 prints'),
    'LIFT_E_RACE': (('boundary', 'Mage', 'r'), 'his race:{boundary,Mage,r}'),
    'LIFT_E_RACE_READ': ('closed_prev', 'the standard race, v4_fdm2.x_race'),
}


def check():
    """THE RULED CHECK. Refuses an off-ruled run unless W_LIFTE_EXPERIMENT=1. -> [(knob, live, ruled, ok)].

    The ws{TF}e line's identity is checked too (v4_ws_e E_MECH 'towards-away', E_VERSION 2).
    """
    import v4_ws_e as WSE
    lv = dict(LIFT_E_ON=LIFT_E_ON, LIFT_E_STEP=LIFT_E_STEP, LIFT_E_MIN_LESS=LIFT_E_MIN_LESS,
              LIFT_E_RACE=LIFT_E_RACE, LIFT_E_RACE_READ=LIFT_E_RACE_READ)
    rows = [(k, lv[k], RULED[k][0], lv[k] == RULED[k][0]) for k in RULED]
    rows += [('WSE_E_MECH', WSE.E_MECH, 'towards-away', WSE.E_MECH == 'towards-away'),
             ('WSE_E_VERSION', WSE.E_VERSION, 2, WSE.E_VERSION == 2)]
    off = [r for r in rows if not r[3]]
    if off and not EXPERIMENT:
        raise SystemExit('REFUSED - lift-off e-path knobs off the bank: %s. Set W_LIFTE_EXPERIMENT=1 to run them.'
                         % ', '.join('%s=%r (ruled %r)' % (k, v, rv) for k, v, rv, _ in off))
    return rows


KNOBS = check()

_EP = {}
SKIPS = {'no e line': 0, 'not the tape grid': 0}


def knobs():
    """-> [(name, value)], every knob this module reads. Callers print it and key caches on it."""
    return [('LIFT_E_ON', LIFT_E_ON), ('LIFT_E_STEP', LIFT_E_STEP), ('LIFT_E_MIN_LESS', LIFT_E_MIN_LESS),
            ('LIFT_E_RACE', ','.join(LIFT_E_RACE)), ('LIFT_E_RACE_READ', LIFT_E_RACE_READ)]


def epath(tf, n):
    """The e_path for ws{tf}r on a grid of `n` bars. -> dict for jig.lift_off, or None (the 1022 producer).

    The race lines are ws{tf}'s own: the oob boundary (15 LOW / 85 HIGH - the side picks it inside the
    producer from this pair), ws{tf}Mage and ws{tf}r, read by LIFT_E_RACE_READ. Built once per TF.
    """
    if not LIFT_E_ON:
        return None
    import v4_ws_e as WSE
    tf = int(tf)
    if not (WSE.TF_LO <= tf <= WSE.TF_HI):
        SKIPS['no e line'] += 1
        return None
    import ln
    if int(n) != int(ln.N):
        SKIPS['not the tape grid'] += 1
        return None
    return _build(tf)


def race(tf, side):
    """ws{tf}e's race lines for one side, whatever LIFT_E_ON says. -> [(name, array)].

    HIS 1110 4A, *"one e-sample **method** everywhere"*: the towards/away mech samples with the same race and
    the same walk back as lift-off's e path, so it reads them from here.
    """
    return for_side(_build(int(tf)), side)['race']


def _build(tf):
    """ws{tf}'s e line and race lines, built once per TF. -> dict."""
    import v4_ws_e as WSE
    tf = int(tf)
    assert WSE.TF_LO <= tf <= WSE.TF_HI, 'ws%de does not exist' % tf
    import ln
    if tf not in _EP:
        import v4_knobs as K
        import v4_closed_prev as CP
        e = WSE.lines()[tf]
        r = np.asarray(ln.line('ws%dr' % tf), float)
        m = np.asarray(ln.line('ws%dMage' % tf), float)
        cp = LIFT_E_RACE_READ == 'closed_prev'
        line_of = {'Mage': np.asarray(CP.series(m, tf * 60), float) if cp else m,
                   'r': np.asarray(CP.series(r, tf * 60), float) if cp else r}
        _EP[tf] = {'e': e, 'line_of': line_of, 'oob': (float(K.OOB_LO), float(K.OOB_HI)),
                   'step': LIFT_E_STEP, 'min_less': LIFT_E_MIN_LESS}
    return _EP[tf]


def for_side(ep, side):
    """The e_path with its race list resolved for one side: the boundary is 15 LOW / 85 HIGH."""
    if ep is None:
        return None
    lo, hi = ep['oob']
    n = len(ep['e'])
    edge = np.full(n, hi if int(side) > 0 else lo, float)
    race = [(nm, edge if nm == 'boundary' else ep['line_of'][nm]) for nm in LIFT_E_RACE]
    return {'e': ep['e'], 'race': race, 'step': ep['step'], 'min_less': ep['min_less']}


def get(tf, n, side):
    """epath + for_side in one call - what every v4 lift-off call site passes as `e_path`."""
    return for_side(epath(tf, n), side)
