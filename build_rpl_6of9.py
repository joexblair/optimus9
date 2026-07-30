"""build_rpl_6of9 — bp50 + RPL interception, on the CLIMB-CENTROID r/fence (Joe 0727). ADDITIVE: bp50's
qualify()/trigger() imported & reused byte-for-byte.  Persists every mechanism-decision to rpl_micro so the
micro-decision reports are INSTANT (a SELECT, no recompute).

CONFIG (per Joe 0727): r per TF band + fence are PINNED to the climb-centroid snapshot at panel re_round 14
(NOT a live query -> reproducible; re-pin only on explicit instruction). Applied via the sweep's OWN machinery
(_apply_knobs + _build_line_L0) with a MINIMAL config = only the band.r.* keys + fence_lo, so ONLY r-per-band and
fence change (x/m/M and other knobs stay at base LN).  Band map (s2_top/s8_top): TF<=2 -> s2, 3..8 -> s8, >=9 -> htf.

CHAIN: qualify()+trigger() [bp50 event tape] -> BLOCK -> _climb_to_prov from the fire bar (first-rung >=5 -> takeover
else release) -> s3s4 gate_open (a/b/c) -> rpl_fin_6of9.  cap = hs60x opposing-breach, NO horizon.
Usage:
  python3 build_rpl_6of9.py --persist YYYY-MM-DD          # run the chain, write rpl_micro rows
  python3 build_rpl_6of9.py --report  YYYY-MM-DD [mmdd_NN]   # read rpl_micro by trade-id, print (instant)
"""
import sys, json, datetime as dt
import numpy as np
import optimus9.orchestration.rpl_walk as R
import optimus9.orchestration.rpl_evo_sweep as SW
import build_past50 as BP
from optimus9.analysis import lr_v2
from optimus9.analysis.jig import Jig, kline, bbline
from optimus9.analysis.lr_v2 import gate_open, gate_signals
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

HI, LO = R.HI, R.LO                 # boundary <- optimus9_system via rpl_walk (0728; was a literal 85/15 here)
TF5_FLOOR = 5                       # xpred_thresh/xpred_band now come from rpl_config via rpl_walk (0727, no hardcoding)
FIN6 = (('s1a', 19), ('s2a', 19), ('s15a', 19))
ms = lambda M, D, h=0, m=0: int(dt.datetime(2026, M, D, h, m, tzinfo=dt.timezone.utc).timestamp() * 1000)
JUNE_END = ms(6, 14)


# PINNED r-per-band (0727): the climb-centroid re_round-14 snapshot. Re-pin ONLY on explicit instruction.
# fence_lo was here too until 0728 — it now lives in rpl_config.fence (fl=30 / fh=70), one SRP home. Reproducibility
# is the named-baseline mechanism's job (rpl_config.rc_name + rr_engine_rev), not a literal in this file.
MINI = {'s2.r.stc': 8, 's8.r.rsi': 6, 'htf.r.k_len': 10, 'htf.r.stc': 12}
S2T, S8T = 2, 8                                                                               # s2_top/s8_top base in the pin

# --- engine on the JUNE window under the centroid r + the config fence (sweep's own builder; new cache key) ---
R.end_ms = JUNE_END
SW._apply_knobs(MINI)
R.L0 = SW._build_line_L0(MINI)                                                                 # per-band r on June
lr_v2.FENCE_HI, lr_v2.FENCE_LO = R.FH, R.FL                    # gate_signals fence <- rpl_config (FL=30 / FH=70)


def band_r(tf):
    g = 's2' if tf <= S2T else ('s8' if tf <= S8T else 'htf'); r = dict(R.LN['r'])
    for comp in ('k_len', 'rsi', 'stc'):
        k = f'{g}.r.{comp}'
        if k in MINI: r[comp] = MINI[k]
    return r

# --- J3: gate + bundle lines on the SAME June grid, centroid per-band r ---
ov = {}
for tf in (1, 2, 15):
    ov.update(bbline('s%dam' % tf, tf, length=6, mult=0.45)); ov.update(bbline('s%daM' % tf, tf, length=37, mult=0.83))
    b = band_r(tf); ov.update(kline('s%dar' % tf, tf, k_len=b['k_len'], rsi=b['rsi'], stc=b['stc']))
for tf in (2, 3, 4):
    b = band_r(tf); ov.update(kline('s%dr' % tf, tf, k_len=b['k_len'], rsi=b['rsi'], stc=b['stc']))
# s3a PRE-FINISHER bundle (Joe 0727): a literal clone of s2a at TF3, plus the x line the stage crosses.
# r is Joe's AUTHORITATIVE config 7|5|8|close (k_len|rsi|stc|src) — NOT band_r(3), which would land in the s8 band.
ov.update(bbline('s3am', 3, length=6, mult=0.45)); ov.update(bbline('s3aM', 3, length=37, mult=0.83))
ov.update(kline('s3ar', 3, k_len=7, rsi=5, stc=8, src='close'))
ov.update(bbline('s3x', 3, length=R.S3A_X_LEN, mult=R.S3A_X_MULT, src='close'))   # config, not a literal (0728)
ov.update(bbline('s3m', 3, length=5, mult=0.45)); ov.update(bbline('s3M', 3, length=37, mult=0.83))
ov.update(bbline('s4m', 4, length=5, mult=0.45)); ov.update(bbline('s4M', 4, length=37, mult=0.83))
ov.update(bbline('s1M', 1, length=37, mult=0.83)); ov.update(bbline('hs60x', 60, length=4, mult=0.37))
J3 = Jig(JUNE_END, hours=40, warmup=600, overrides=ov)
gts = np.asarray(R.L0['ts'], np.int64); gN = len(gts); gidx = np.arange(gN)
assert np.array_equal(np.asarray(J3.ts, np.int64), gts), "J3 grid must match the climb-engine grid"
hs60x = np.asarray(J3.W.line('hs60x'), float)
SIG = gate_signals(J3.W, J3.cfg)                                                                # fence = centroid (patched)
E = R.L0['E']
gf = lambda i: dt.datetime.utcfromtimestamp(gts[i] / 1000).strftime('%m-%d %H:%M:%S')
hms = lambda tms: dt.datetime.fromtimestamp(tms / 1000, dt.timezone.utc).strftime('%H:%M:%S')   # for in-decision stamps
r1 = lambda v: round(float(v), 1)                                            # all recorded line values -> 1 dp
_GATELN = ('s2r', 's3r', 's3m', 's3M', 's4r', 's4m', 's4M', 's1M')          # every line the s3s4 gate reads
GL = {nm: np.asarray(J3.W.line(nm), float) for nm in _GATELN}
def glines(k): return {nm: r1(GL[nm][k]) for nm in _GATELN}                  # full set @ bar k, 1 dp


# s3a pre-finisher stage (Joe 0727). S3A=False -> the chain is exactly as before (the A/B baseline).
S3A = True
S3A_EV = {es: J3.causal.s3a_cross(es, R.S3A_R_LB, R.S3A_CROSS_WOB) for es in (+1, -1)} if S3A else {}


def cap_of(gbar, es):
    opp = (hs60x <= LO) if es > 0 else (hs60x >= HI)
    hit = np.flatnonzero(opp & (gidx > gbar))
    return int(hit[0]) if len(hit) else gN


def trace_fire(oi, de, ti, tf, br, tev, ncol=1):
    """Full ordered mechanism-decision list for ONE A/B fire. Returns (mode, [record,...]) where each record is
    (seq, mechanic, time_ms, decision_text, {line: value}). `tev` = the trigger walk's own event stream (RGATE
    latch bar + the firing cross pair) — read, never re-derived. NOT `ev`: that name is rebound below by
    _climb_to_prov's return."""
    rec = []; seq = [0]
    def add(mech, tms, dec, lines): rec.append((seq[0], mech, int(tms), dec, lines)); seq[0] += 1
    add('qualify', BP.te[oi], 's4M OOB %s sustained>240s & hs60x OOB%s' % (
            'HI' if de > 0 else 'LO', '' if ncol < 2 else ' [+%d overlapping setups collapsed]' % (ncol - 1)),
        {'s4M': r1(BP.s4M[oi]), 'hs60x': r1(BP.hs[oi])})
    rgb = next((e for e in tev if e[1] == 'rgate'), None)                         # (bar, 'rgate', -, -, gtr2@latch)
    pair = next((e[3] for e in tev if e[1] == 'fire'), '?')
    mg = ' '.join('s%dM=%.1f' % (t, BP.L[t]['M'][ti]) for t in BP.HTFS
                  if BP.L[t]['M'][ti] >= HI or BP.L[t]['M'][ti] <= LO) or 'none'
    add('trigger', BP.te[ti], 'branch-%s s%d %s; MageOOB %s; RGATE latched %s gtr2=%.1f (now %.1f)' % (
            br, tf, pair, mg, hms(BP.te[rgb[0]]) if rgb else '—', rgb[4] if rgb else float('nan'), BP._gater[ti]),
        {'gtr2_r': r1(BP._gater[ti]), 'gtr2_latch': r1(rgb[4]) if rgb else None,
         **{f's{t}_{k}': r1(BP.L[t][k][ti]) for t in BP.HTFS for k in ('x', 'm', 'M', 'r')}})
    fts = int(BP.te[ti])
    if fts < gts[0] or fts > gts[-1]:
        add('out-of-grid', fts, 'fire spills past June grid -> skip', {}); return 'out-of-grid', rec
    gbar = int(np.searchsorted(gts, fts))
    bias = 'bull' if de > 0 else 'bear'
    ict, dTF, ev = R._climb_to_prov(bias, gbar)          # xpred_thresh/band default to rpl_config (0727)
    for (t, name, tfn, desc) in ev:
        k = int(np.searchsorted(gts, t))
        if name == 'r-pred':                                        # predict_breach reads r,m,M -> record all 3
            lines = {f'E[s{tfn}].r': r1(E[tfn]['r'][k]), f'E[s{tfn}].m': r1(E[tfn]['m'][k]), f'E[s{tfn}].M': r1(E[tfn]['M'][k])}
        elif name == 'x-cross-pred':                                # fcross(x-r) & near_ib(r) & s2r_es(s2r)
            lines = {f'E[s{tfn}].x': r1(E[tfn]['x'][k]), f'E[s{tfn}].r': r1(E[tfn]['r'][k]), 's2r': r1(E[2]['r'][k])}
        elif name == 'flip_provisional':                            # delegate cross_wob(xD - rD)
            lines = {f'E[s{tfn}].x': r1(E[tfn]['x'][k]), f'E[s{tfn}].r': r1(E[tfn]['r'][k])}
        else:
            lines = {}
        add(name, t, f's{tfn}: {desc}', lines)
    first_rung = next((e[2] for e in ev if e[1] == 'r-pred'), 0)
    if not (first_rung >= TF5_FLOOR and ict is not None):
        add('release', fts, f'first rung {first_rung} < {TF5_FLOOR} or no provisional -> A/B released', {})
        arm = gbar; mode = 'release'
    else:
        arm = ict; mode = 'takeover'
    es, bd = de, -de; cap = cap_of(arm, es)
    # s3s4 gate a/b/c
    p3 = p4 = b3 = b4 = rtr = False; xin2 = xin3 = xin4 = False; opened = None
    for k in range(arm + 1, cap):
        if SIG['pred3'][k] == es and SIG['s3m_oob'][k] and not p3: p3 = True; add('gate', gts[k], 'p3 armed', glines(k))
        if SIG['pred4'][k] == es and SIG['s4m_oob'][k] and not p4: p4 = True; add('gate', gts[k], 'p4 armed', glines(k))
        if p3 and SIG['brc3'][k] == es and not b3: b3 = True; add('gate', gts[k], 'b3 (s3 breached)', glines(k))
        if p4 and SIG['brc4'][k] == es and not b4: b4 = True; add('gate', gts[k], 'b4 (s4 breached)', glines(k))
        nrtr = b3 or b4 or (not p3 and not p4 and (SIG['rev3m'][k] == bd or SIG['rev4m'][k] == bd))
        if nrtr and not rtr: rtr = True; add('gate', gts[k], 'ready-to-reverse latched', glines(k))
        if (p3 and not b3 and SIG['rev3r'][k] == bd) or (p4 and not b4 and SIG['rev4r'][k] == bd): opened = (k, 'b'); break
        if rtr and SIG['rev2M'][k] == bd: opened = (k, 'c'); break
        if SIG['oob2'][k - 1] and not SIG['oob2'][k]: xin2 = True
        if SIG['oob3'][k - 1] and not SIG['oob3'][k]: xin3 = True
        if SIG['oob4'][k - 1] and not SIG['oob4'][k]: xin4 = True
        if xin2 and xin3 and xin4: opened = (k, 'a'); break
    if opened is None:
        add('gate', gts[min(cap, gN - 1)], 'NO GATE OPEN in [arm,cap] -> drop', {}); return mode, rec
    ok, path = opened
    add('gate-open', gts[ok], f'*** GATE OPEN path {path} ***', glines(ok))
    # rpl_fin_6of9
    sd = 'hi' if es > 0 else 'lo'
    parts = {s: J3.causal.finisher_parts(s, r_lb=rlb) for (s, rlb) in FIN6}
    fire = J3.causal.rpl_fin_6of9(ok, cap, es, sets=FIN6, N=R.FIN_N_OF9, bind_tol=R.FIN_BIND_TOL)   # knobs from rpl_config
    if S3A:                                                  # s3a PRE-FINISHER stage — the cross is REQUIRED
        xk = np.flatnonzero(S3A_EV[es][ok:cap]) + ok         # first s3a-qualified s3x cross in [gate-open, cap)
        if not len(xk):
            add('s3a', gts[min(cap, gN - 1)], 'no s3a x-cross in [gate-open,cap) -> DROP', {}); return mode, rec
        xb = int(xk[0])
        tol = int(R.S3A_TOL_TF_BARS * 3 * 60 // 5)           # tolerance: TF3 bars -> 5s grid bars (4 -> 144 = 12 min)
        if tol and fire is not None and (xb - tol) <= fire <= xb:
            add('s3a', gts[xb], 'x-cross s3x*s3am; flip_finisher %s captured within %d TF3 bars -> stamped at cross'
                % (gf(fire), R.S3A_TOL_TF_BARS), {'s3x': r1(J3.W.line('s3x')[xb]), 's3am': r1(J3.W.line('s3am')[xb])})
            fire = xb                                        # no time travel: the trade cannot predate the cross
        else:
            add('s3a', gts[xb], 'x-cross s3x*s3am; finisher RE-ARMED at the cross',
                {'s3x': r1(J3.W.line('s3x')[xb]), 's3am': r1(J3.W.line('s3am')[xb])})
            fire = J3.causal.rpl_fin_6of9(xb, cap, es, sets=FIN6, N=R.FIN_N_OF9, bind_tol=R.FIN_BIND_TOL)
    def vote(P, k):
        m = int(P['m_' + sd][k]); Mo = int(P['Moob_' + sd][k]); rl = int(P['rlb_' + sd][k] and (P['r_' + sd][k] or P['m_' + sd][k] or P['Moob_' + sd][k]))
        return m, Mo, rl
    for k in range(ok, (fire + 1) if fire else min(cap, ok + 300)):
        vs = [vote(parts[s], k) for (s, _) in FIN6]; tot = sum(sum(v) for v in vs)
        if tot >= 4 or (fire and k == fire):
            lines = {f'{s}_{c}': r1(J3.W.line(f'{s}{c}')[k]) for (s, _) in FIN6 for c in ('m', 'M', 'r')}
            # the FIRE bar is its own mechanic: 'flip_finisher' (Joe 0727) — queryable, no '<<FIRE' text marker
            add('flip_finisher' if (fire and k == fire) else 'fin6of9', gts[k],
                'vote %d/9 [%s]' % (tot, ' '.join(f'{s[0]}:{v[0]}/{v[1]}/{v[2]}' for (s, _), v in zip(FIN6, vs))), lines)
    if not fire: add('fin6of9', gts[min(cap, gN - 1)], f'no >={R.FIN_N_OF9}-of-9 before cap -> DROP', {})
    return mode, rec


def _fires(S, E):
    for oi, de in BP.qualify():
        if not (S <= BP.te[oi] < E):
            continue
        trig, ev = BP.trigger(oi, de, trace=True)          # ONE walk: the report reads its events, never re-derives
        for ti, tf, br in trig:
            yield oi, de, ti, tf, br, ev


def persist_day(day):
    S = int(dt.datetime.strptime(day, '%Y-%m-%d').replace(tzinfo=dt.timezone.utc).timestamp() * 1000); E = S + 24 * 3600 * 1000
    mmdd = dt.datetime.strptime(day, '%Y-%m-%d').strftime('%m%d')
    fmt = lambda tms: dt.datetime.fromtimestamp(tms / 1000, dt.timezone.utc).strftime('%m%d %H:%M:%S')   # UTC "mmdd hh:mm:ss"
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute('''CREATE TABLE IF NOT EXISTS rpl_micro (m_id INT AUTO_INCREMENT PRIMARY KEY, m_tid VARCHAR(9), m_tf INT,
        m_day VARCHAR(10), m_fire VARCHAR(14), m_branch VARCHAR(2), m_de INT, m_mode VARCHAR(12), m_seq INT,
        m_mechanic VARCHAR(24), m_time VARCHAR(14), m_decision VARCHAR(400), m_lines TEXT, m_built TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    d.execute('DELETE FROM rpl_micro WHERE m_day=%s', (day,))
    # DEDUP (Joe 0727): overlapping setups all latch and converge on the SAME cross, so collapse chains sharing
    # (fire_ts, tf) — the deduped_trades key — keeping the EARLIEST onset. Write-time only: the engine is untouched
    # and no trade changes; suppressing at qualify() instead would delete setups and move the fires.
    grp = {}
    for f in _fires(S, E):
        grp.setdefault((int(BP.te[f[2]]), f[3]), []).append(f)           # key = (fire_ts, tf)
    chains = []                                                          # collect first — id needs the finisher time
    for g in grp.values():
        (oi, de, ti, tf, br, ev), ncol = min(g, key=lambda f: f[0]), len(g)   # earliest onset survives
        mode, rec = trace_fire(oi, de, ti, tf, br, ev, ncol)
        fin = next((tms for (seq, mech, tms, dec, lines) in rec if mech == 'flip_finisher'), None)
        chains.append({'fire': int(BP.te[ti]), 'tf': tf, 'br': br, 'de': de, 'mode': mode, 'rec': rec, 'fin': fin, 'tid': None})
    for n, c in enumerate(sorted([c for c in chains if c['fin'] is not None], key=lambda c: c['fin']), 1):   # id = flip_finisher order
        c['tid'] = f'{mmdd}_{n:02d}'
    rows = 0
    for c in chains:                                                     # one chain per (fire_ts, tf) after dedup
        for (seq, mech, tms, dec, lines) in c['rec']:
            d.execute('INSERT INTO rpl_micro (m_tid,m_tf,m_day,m_fire,m_branch,m_de,m_mode,m_seq,m_mechanic,m_time,m_decision,m_lines) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                      (c['tid'], c['tf'], day, fmt(c['fire']), c['br'], int(c['de']), c['mode'], seq, mech, fmt(tms), dec, json.dumps(lines)))
            rows += 1
    d.disconnect()
    print(f"persisted {rows} rows / {len(chains)} chains ({sum(1 for c in chains if c['tid'])} trades) for {day}")


def report_day(day, tid=None):
    d = DatabaseManager(**get_db_config()); d.connect()
    where = 'm_day=%s'; args = [day]
    if tid:                                                             # filter by trade-id (mmdd_NN)
        where += ' AND m_tid=%s'; args.append(tid)
    rows = d.execute('SELECT * FROM rpl_micro WHERE ' + where + ' ORDER BY m_fire, m_tf, m_seq', tuple(args), fetch=True)
    d.disconnect()
    if not rows: print(f'no rpl_micro rows for {day}{" "+tid if tid else ""} — run --persist first'); return
    cur = None
    for r in rows:
        ck = (r['m_fire'], r['m_tf'])                                   # a chain = (fire time, TF); dups differ by TF
        if ck != cur:
            cur = ck
            print('\n== %s  tid=%s  tf=s%s  (%s) de%+d  %s ==' % (r['m_fire'], r['m_tid'] or '—', r['m_tf'], r['m_branch'], r['m_de'], r['m_mode']))
            print('  seq  mechanic          time            decision / lines')
        lv = json.loads(r['m_lines']); ls = '  '.join(f'{k}={v}' for k, v in lv.items())
        print('  %-3d  %-16s  %s  %s %s' % (r['m_seq'], r['m_mechanic'], r['m_time'], r['m_decision'], ('| ' + ls) if ls else ''))


if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == '--persist':
        persist_day(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == '--report':
        report_day(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    else:
        print(__doc__)
