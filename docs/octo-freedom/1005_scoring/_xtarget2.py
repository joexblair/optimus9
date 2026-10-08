"""#61, THE PART THAT WAS NEVER RUN — THE COMBINED [Mage, b, boundary] TARGET. 1008.

Joe 1008: *"run #61. I see you were exapanding to multi TFs - that's a good call and should be
included in the sweep"*.

THE FIRST SWEEP (`_xtarget.py`, 25 arms) only ever ran SINGLE targets. #61's CURRENT SETTING is the
SET: Joe 0818 *"use ' x X [MAge,b,boundary]' for now"*. That set was never measured. #61 also names
its own open question, still unasked: *"whether the cross must be of ALL of Mage, b and the
boundary, or ANY one of them"*. A sweep is the measurement, so BOTH are arms here.

FOUR DIMENSIONS, 48 ARMS, plus a control:

  the combine rule   **all** = the x must be beyond EVERY target in the set.
                     **any** = beyond at least ONE of them.
                     #61's own open question. Neither is a default.

  the target TFs     **self** = the same TF as the x. THIS IS #61's OWN STRUCTURE -
                     `ws{weak-mage-tf}x` crossing `ws{weak-mage-tf}<target>`.
                     **next** = h+1 only.
                     **both** = h+1 AND h+2.
                     Joe 1008 ratified the multi-TF expansion: *"that's a good call and should be
                     included in the sweep"*.

  the in-fence test on the LINE targets   on / off. Carried from the first sweep.
                     ONE CONVENTION IN BOTH COMBINE RULES: every LINE target (Mage and b), at
                     every TF in the offset, must be in-fence. It does NOT follow the combine rule,
                     because a fence test that moved with `any` would mean two different things in
                     the two arms and the arms would not be comparable. STATED, not hidden.

  what `boundary` IS   #61 lists it beside Mage and b, but there is no `boundary` ROLE - the wsf
                     roles are r, m, x, Mage, b. So it is a LEVEL, and which level is unspecified.
                     Four readings are swept rather than picked:
                       exf_dr   the dr-side ex-fence   - 83 on a +1 leg, 17 on a -1 leg
                       exf_ctr  the counter-side ex-fence - 17 on a +1 leg, 83 on a -1 leg
                       oob_dr   the dr-side oob        - 85 on a +1 leg, 15 on a -1 leg
                       oob_ctr  the counter-side oob   - 15 on a +1 leg, 85 on a -1 leg
                     `exf_ctr` is what the first sweep's `fence` role did, so it cross-checks.

THE CROSS DIRECTION is untouched, Joe 0818: x crosses UNDER its target on a +1 leg, OVER on a -1.
That applies to the levels exactly as it applies to the lines.

THE CONTROL ARM reproduces the BANKED build (`x_tgt_role` b, `x_tgt_tfs` next, `x_tgt_fence` 0) and
must score fit +0.7511 / hold +4.0801 / all +4.8312 on 1623 legs. A hash-keyed line cache fails
silently with real-but-wrong arrays, so the control is the only thing that proves the window.

Knobs as banked: mae_stop_pct 2.5, reent_xwob 18. Asserted, not overridden.
"""
import os, sys, json, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

MODE = os.environ['X_MODE']            # 'all' | 'any' | 'control'
TFS = os.environ.get('X_TFS', 'next')
FENCE = os.environ.get('X_FENCE', '0') == '1'
BND = os.environ.get('X_BND', 'exf_ctr')
SC, PX = C.SC, C.PX
N = len(SC.ts); FEE = 0.11
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
assert abs(C.MAE_STOP - 2.5) < 1e-9, 'mae_stop_pct is %s, the arm needs 2.5' % C.MAE_STOP
assert T.XWOB == 18, 'reent_xwob is %d, the arm needs 18' % T.XWOB

OFF = {'both': (1, 2), 'next': (1,), 'self': (0,)}[TFS]
LINES = {role: {t: np.asarray(SC.LD(t * 60, role), float)[:N] for t in C.RL}
         for role in ('Mage', 'b')}
LVL = {'exf_dr': (C.EXF_HI, C.EXF_LO), 'exf_ctr': (C.EXF_LO, C.EXF_HI),
       'oob_dr': (SC.HI, SC.LO), 'oob_ctr': (SC.LO, SC.HI)}[BND]
#      (the level a +1 leg's x must fall under, the level a -1 leg's x must rise over)

def beyond(xv, tv, d):
    return (xv < tv) if d > 0 else (xv > tv)

def xcond_set(h, k, d):
    tt = [h + o for o in OFF]
    if any(t not in LINES['Mage'] for t in tt): return False
    xv = float(C.X[h][k])
    hits = [beyond(xv, float(LINES[role][t][k]), d) for t in tt for role in ('Mage', 'b')]
    hits.append(beyond(xv, LVL[0] if d > 0 else LVL[1], d))
    if not (all(hits) if MODE == 'all' else any(hits)): return False
    if not FENCE: return True
    return all(((float(LINES[role][t][k]) < C.EXF_HI) if d > 0
                else (float(LINES[role][t][k]) > C.EXF_LO))
               for t in tt for role in ('Mage', 'b'))

if MODE != 'control':
    C.xcond = xcond_set       # 'control' leaves the banked xcond in place

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

legs = []; k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    legs.append(dict(day=DAYOF(k), why=why, open=k, exit=xk, dd=d,
                     real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

per = collections.defaultdict(lambda: [0.0, 0, 0, 0.0, 0.0]); whys = collections.Counter()
for r in legs:
    a_, f_ = (C.MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['dd'])
    e = per[r['day']]
    e[0] += r['real']; e[1] += 1; e[2] += 1 if r['why'] == 'mae breach' else 0
    e[3] += a_; e[4] += f_
    whys[r['why']] += 1
print(json.dumps(dict(mode=MODE, tfs=TFS, fence=int(FENCE), bnd=BND, legs=len(legs),
                      whys=dict(whys),
                      per={k_: [round(v[0], 4), v[1], v[2], round(v[3], 4), round(v[4], 4)]
                           for k_, v in sorted(per.items())})), flush=True)
