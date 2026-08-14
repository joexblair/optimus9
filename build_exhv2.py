"""build_exhv2 — exhaustion v2. Spec: docs/exhv2_spec.md. Notes: transfer/260730_exhv2_notes.csv

Adjunct to RPL, not part of it. TF <= 22 only (s4, s15, s22), standalone predict_breach on those lines.
One evaluation per rpl_exh_stat row.

  WALK      forward on s4 from the exhaustion bar until s4Mage is OOB. Nothing terminates it before that.
            The walk destination is where EVERYTHING downstream is read - not the exhaustion bar.
  MFE SIDE  if that first s4Mage OOB is opposite to the bias, the signal was on the MFE side: bias reverses.
  MOMENTUM  on s15r / s22r at the walk bar: r past 50, slope sign bias-aligned, |slope| >= floor, R2 >= min.
            9 point-samples, 1 per 5 min, ending at the walk bar.
  BRANCH    momentum -> rev on s15/s22 (r-pred'd TF if either is, else lowest momo TF)
            sideways -> EXIT   (a sideways market is unstable; rev is too risky - Joe)
            dirty or no momentum -> fall through to s4: s4x X s4m, over/under Moob
  RACE      s15/s22: boundary, r, Mage - first to fire. Tie-break r -> Mage -> boundary, explicit.
            s4: x X m only (Mage is s15/s22 only), positionally over/under s4Mage.

    python3 build_exhv2.py [--persist] [--r2 0.50] [--slope 1.0]
"""
import sys, csv, os, datetime as dt
import numpy as np
import build_exhaust as X
import build_rplwalk2 as W
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.breaching_line import predict_breach
from optimus9.analysis.jig import _latch_with_reset, bbline, kline
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

# THE MOMENTUM VERDICT MOVED OUT 0813. momo() and its MOMO_*/CURL_*/LEVEL_SLACK constants now live
# in optimus9/compute/momo_core.py, so consumers of the verdict no longer import this file and,
# through it, build_exhaust / build_rplwalk2 / rpl_walk. Joe 0813: "RPL is in sunset, so we need to
# salvage". SAME 50 lines, relocated, not copied.
#
# The module __getattr__ below re-exports them LIVE. `import build_exhv2 as B; B.MOMO_R2_MIN` still
# works and still sees a rebind — by momo_gated.momo_window() or by main()'s argv flags — because
# the lookup falls through to momo_core each time. A plain `from ... import MOMO_R2_MIN` would have
# snapshotted the value here and gone stale inside a momo_window() block.
from optimus9.compute import momo_core as _MC
from optimus9.compute.momo_core import momo                       # noqa: F401  re-export

_MC_NAMES = ('MOMO_R2_MIN', 'MOMO_SLOPE_MIN', 'MOMO_WINDOW_MIN', 'MOMO_SAMPLES', 'MOMO_STEP_MIN',
             'MOMO_STEP_BARS', 'CURL_ARC_MIN', 'CURL_VTX_LO', 'CURL_VTX_HI', 'LEVEL_SLACK')


def __getattr__(name):
    """PEP 562 fallthrough to momo_core for the relocated constants. Reached only when `name` is not
    a global of this module, so nothing here may assign to those names."""
    if name in _MC_NAMES:
        return getattr(_MC, name)
    raise AttributeError(f'module {__name__!r} has no attribute {name!r}')


WALK_DWELL_BARS = 48        # Joe 0731: "if s4M has crossed to oob AND STAYED CONSISTENTLY OOB FOR 240
#                             SECONDS". 240 s = 48 bars at the 5 s grid. CONTIGUOUS - a single dip inside
#                             the 240 s disqualifies that crossing and the walk moves to the next one that
#                             holds. s4Mage chatters across HI: 6 crossings in the 27 min after the
#                             0522 11:54 r-pred, runs of 0.2-19.2 min. SWEEP KNOB.
TFS = (4, 15, 22)
# Joe 0731: "4,15,22 Mage configs 37|0.7|close". The live rpl_config baseline has M at mult 0.83, so every
# Mage reading in exhv2 was on the wrong line. On 0522 the first s4Mage OOB crossing after the 11:54 r-pred
# moves 11:55:40 -> 12:22:35 at 0.7, and a 24.2-min run opens at 12:44:15. exhv2 builds its OWN Mage lines
# rather than touching rpl_config, which the whole engine reads.
# Joe 0731, the FULL exhv2 line set. Four of the five differ from the live rpl_config baseline, and s4r
# differs from s15r/s22r. exhv2 builds all of these itself - nothing here reads E[tf] any more.
#   x  bb  4|0.37|close   (live: length 5)
#   m  bb  6|0.45|close   (matches live)
#   M  bb 37|0.70|close   (live: mult 0.83)
#   r  s4      kline  7|6|11|close   (live: rsi 5)
#   r  s15,s22 kline 10|4|11|close   (live: k_len 7, rsi 5)
LINE_SPEC = {
    'x': ('bb', dict(length=4, mult=0.37, src='close')),
    'm': ('bb', dict(length=6, mult=0.45, src='close')),
    'M': ('bb', dict(length=37, mult=0.7, src='close')),
}
R_SPEC = {4: dict(k_len=7, rsi=6, stc=11, src='close'),
          15: dict(k_len=10, rsi=4, stc=11, src='close'),
          22: dict(k_len=10, rsi=4, stc=11, src='close')}
# LEVEL_SLACK 13.9 moved to momo_core 0813. Joe 0731 "coin-toss it"; drawn uniform 0-15 on urandom.
#                             The level gate slackens by LEVEL_SLACK * T, where the tracking score
#                             T = R2 * min(1, |slope|/momo_slope_min) clipped to [0,1]. A perfectly
#                             tracking line earns the full slack; a flat one (T~0) earns none. Rescues
#                             0520 06:26 s15 at r 50.63 slope -1.891 R2 0.818, which misses a hard gate
#                             by 0.63 while unambiguously in motion. SWEEP KNOB.
NOTES = 'transfer/260730_exhv2_notes.csv'
REWALK = 2                  # Joe 0801: "walk to the next s4M cycle when s22 has momentum, then let the
#                             mechanism run". ADOPTED 0801 at 2 - measured on all 87 rows at
#                             swing_detect 1.00%: MAE median 0.49 -> 0.38, MAE max 3.75 -> 2.97,
#                             ratio median 2.13 -> 3.30, MFE median flat 1.08 -> 1.09; vs Joe's 14
#                             marked targets mean|err| 55.2 -> 53.1, median|err| 38.4 -> 34.5. 28 of 87
#                             rows move, hop counts median 2 max 7. Only regression: MAE p90 1.52 ->
#                             1.61. NO NEW KNOB - it is the existing walk detector re-applied.
#                             0 = off (the pre-0801 behaviour). 1 = one hop. 2 = repeat while
#                             s22 still reads momo at each new walk bar. A hop moves the walk to the NEXT
#                             s4Mage OOB crossing that holds WALK_DWELL_BARS, then re-derives side,
#                             MFE-side, eff_bias, momentum, branch, act and signal at that bar.
REWALK_HOPS = {}            # es_conf_utc -> hops taken, for the report

def oob_qualified(M, hi, lo, dwell=None):
    """THE 240-SECOND TEST, per Joe's spec wording: "IF s4Mage has been OOB for 240s" — tested ON EACH BAR.

    Returns a bool array, True at the RISING EDGE of "M has been continuously OOB for WALK_DWELL_BARS".
    That bar is `z + WALK_DWELL_BARS - 1` for a clean run starting at z, i.e. the first bar at which the
    condition is knowable. THE SAME RUNS QUALIFY as before — only the stamp moves, by 47 bars = 235 s.

    THE DEFECT THIS REPLACES (Joe 0802). The old form found a crossing z, walked FORWARD to the run's end,
    and stamped held[z]=True at the CROSSING. That verdict needs 240 s of future, so it is a forward peek:
    17 of 147 signals fired BEFORE their own walk bar was confirmable, the tightest at 1.25 min. §9(4)
    recorded the walk-bar use as harmless; it was not. Reading the spec as written removes the peek at the
    walk AND at the exit in one change, which collapses the dm_ret / dm_cret pair into one causal column.

    SINGLE PRODUCER (SRP). This test previously existed as three hand-copied forward loops — here,
    build_dominoes_db and emit_dominoes_pine. That is how the defect survived. Precedent: momo() below,
    lifted to module level for the same reason.

    dwell=None uses the module global so a --dwell CLI override still reaches callers.
    """
    d = WALK_DWELL_BARS if dwell is None else int(dwell)
    o = (M >= hi) | (M <= lo)
    if d <= 1:
        return o & ~np.r_[False, o[:-1]]
    idx = np.arange(len(o))
    rst = np.where(o, 0, idx + 1)
    run = (idx + 1) - np.maximum.accumulate(rst)       # consecutive OOB bars ending AT i — backward, causal
    q = run >= d
    return q & ~np.r_[False, q[:-1]]


# momo() moved to optimus9/compute/momo_core.py 0813 and is re-exported by the import above.
# predict_board.py:170 unpacks its 4-tuple; vmomo.py and build_trades2.py:93 are vectorised mirrors
# that must match it. One implementation, new address.


DDL = '''CREATE TABLE IF NOT EXISTS rpl_exhv2 (
    v2_pk        BIGINT AUTO_INCREMENT PRIMARY KEY, v2_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    v2_conf_ms   BIGINT, v2_conf_utc VARCHAR(11),      -- the v1 exhaustion this ran from
    v2_cur_tf    INT, v2_bias VARCHAR(4),
    v2_walk_ms   BIGINT, v2_walk_utc VARCHAR(11),      -- first bar s4Mage is OOB
    v2_walk_side VARCHAR(2),                           -- hi | lo
    v2_mfe_side  TINYINT,                              -- 1 = walk side opposite the bias -> bias reversed
    v2_eff_bias  VARCHAR(4),                           -- bias after any MFE-side reversal
    v2_s15_state VARCHAR(8), v2_s15_slope DOUBLE, v2_s15_r2 DOUBLE, v2_s15_r DOUBLE,
    v2_s22_state VARCHAR(8), v2_s22_slope DOUBLE, v2_s22_r2 DOUBLE, v2_s22_r DOUBLE,
    v2_rp4 TINYINT, v2_rp15 TINYINT, v2_rp22 TINYINT,  -- standalone r-pred at the walk bar
    v2_d4 TINYINT, v2_d15 TINYINT, v2_d22 TINYINT,     -- exhv2 clean/dirty at the walk bar
    v2_branch    VARCHAR(16),                          -- momo | sideways | s4
    v2_action    VARCHAR(4),                           -- rev | EXIT
    v2_cross_tf  INT, v2_cross_tgt VARCHAR(8),         -- the winning line and target
    v2_cross_all VARCHAR(24),                          -- every target firing on the winning bar
    v2_sig_ms    BIGINT, v2_sig_utc VARCHAR(11),       -- THE SIGNAL
    v2_lead_min  DOUBLE,                               -- signal - v1 exhaustion, minutes
    v2_target_utc VARCHAR(11), v2_err_min DOUBLE,      -- Joe's corrected_conf, and signal - target
    v2_race_ms   BIGINT, v2_race_utc VARCHAR(11),      -- the branch race bar A replaced (diagnostic)
    KEY (v2_conf_ms), KEY (v2_branch))'''


def main(argv):
    # THE FLAGS WRITE TO momo_core. momo() reads its constants at call time from ITS OWN module, so
    # rebinding a copy here would leave --r2 / --slope / --window / --arc / --slack ineffective.
    global WALK_DWELL_BARS, REWALK
    for i, a in enumerate(argv):
        if a == '--r2' and i + 1 < len(argv):
            _MC.MOMO_R2_MIN = float(argv[i + 1])
        if a == '--slope' and i + 1 < len(argv):
            _MC.MOMO_SLOPE_MIN = float(argv[i + 1])
        if a == '--window' and i + 1 < len(argv):
            _MC.MOMO_WINDOW_MIN = int(argv[i + 1])
            _MC.MOMO_SAMPLES = _MC.MOMO_WINDOW_MIN // _MC.MOMO_STEP_MIN
        if a == '--arc' and i + 1 < len(argv):
            _MC.CURL_ARC_MIN = float(argv[i + 1])
        if a == '--dwell' and i + 1 < len(argv):
            WALK_DWELL_BARS = int(argv[i + 1])
        if a == '--slack' and i + 1 < len(argv):
            _MC.LEVEL_SLACK = float(argv[i + 1])
        if a == '--rewalk' and i + 1 < len(argv):
            REWALK = int(argv[i + 1])
    X.rebuild_cache(120)
    ts = np.asarray(R.L0['ts'], np.int64); E = R.L0['E']; S = R.L0['src']
    n = R.L0['n']
    # exhv2's OWN line set (Joe 0731). The rpl_config baseline stays untouched for RPL.
    ovr = {}
    for _tf in TFS:
        for _k, (_kind, _sp) in LINE_SPEC.items():
            ovr.update(bbline('exhv2%s%d' % (_k, _tf), _tf, **_sp))
        ovr.update(kline('exhv2r%d' % _tf, _tf, **R_SPEC[_tf]))
    _J = cache_jig_perline(R.end_ms, R.HOURS, R.WARMUP, ovr, pxs_cfg=R.PXS_CFG)
    EX = {_tf: {_k: np.asarray(_J.W.line('exhv2%s%d' % (_k, _tf)), float)
                for _k in ('x', 'm', 'M', 'r')} for _tf in TFS}
    MG = {_tf: EX[_tf]['M'] for _tf in TFS}
    if len(MG[4]) != n:
        raise RuntimeError('exhv2 tape %d bars vs L0 %d - tapes must align' % (len(MG[4]), n))
    E = EX                      # everything below reads exhv2's lines, not the RPL baseline
    u = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%m%d %H:%M')

    # --- per-line arrays: standalone r-pred, the exhv2 clean/dirty flag, and the debounced crosses -------
    d = DatabaseManager(**get_db_config()); d.connect()
    EXH = {}
    for r_ in d.execute('SELECT DISTINCT ea_conf_ms, ea_cur_tf, ea_bias FROM rpl_exh_applied', fetch=True):
        EXH.setdefault(1 if r_['ea_bias'] == 'bull' else -1, []).append((int(r_['ea_conf_ms']), int(r_['ea_cur_tf'])))
    for k in EXH:
        EXH[k].sort()
    RP, DIRTY = {}, {}
    for tf in TFS:
        for dr in (1, -1):
            e = E[tf]
            P = predict_breach(e['r'], e['m'], e['M'], R.HI, R.LO, R.FH, R.FL, 0.0)
            pr = (P == dr)
            fx = np.asarray((R.L0['fx_bull'] if dr > 0 else R.L0['fx_bear'])[tf], bool)
            RP[(tf, dr)] = _latch_with_reset(pr & ~np.r_[False, pr[:-1]], fx)
            # exhv2 clean/dirty: same logic as RPL, SEPARATE instance for all three lines (Joe: SRP).
            # s22 does not reuse the RPL flag even though the two compute the same thing on the same spend
            # set - the RPL flag belongs to the ladder, this one belongs to exhv2.
            DIRTY[(tf, dr)] = S.causal.clean_dirty(e['r'], e['x'], dr, R.HI, R.LO, R.FH, R.FL,
                                                   R.WOBN, mode='exhv2')
    d.disconnect()

    # --- debounced crosses, per line, both directions ---------------------------------------------------
    XC = {}
    def cross(tf, tgt, dr):
        """rising edge of x crossing the target. dr -1 = x crosses DOWN through it (hi breach)."""
        k = (tf, tgt, dr)
        if k not in XC:
            e = E[tf]
            line = {'r': e['r'], 'Mage': MG[tf], 'm': e['m'],
                    'boundary': np.full(n, R.HI if dr < 0 else R.LO, float)}[tgt]
            c = S.causal.cross_wob(e['x'] - line, 0.0, dr, R.WOBN)
            XC[k] = c & ~np.r_[False, c[:-1]]
        return XC[k]

    tgt_order = ('r', 'Mage', 'boundary')      # explicit tie-break, matches build_exhaust's append order

    def race(tf, w, dr, targets):
        """first bar after w where any target fires. Returns (bar, winner, all_firing)."""
        best = None
        for t in targets:
            e = np.flatnonzero(cross(tf, t, dr)[w + 1:])
            if len(e):
                b = int(e[0]) + w + 1
                if best is None or b < best[0]:
                    best = (b, t)
        if best is None:
            return None, None, ''
        b = best[0]
        firing = [t for t in tgt_order if t in targets and cross(tf, t, dr)[b]]
        return b, (firing[0] if firing else best[1]), '+'.join(firing)

    # --- events ------------------------------------------------------------------------------------------
    d = DatabaseManager(**get_db_config()); d.connect()
    rows = d.execute('''SELECT es_conf_ms, es_conf_utc, es_cur_tf, es_bias, es_rpred_ms
                        FROM rpl_exh_stat ORDER BY es_conf_ms''', fetch=True)
    d.disconnect()
    TARGET = {}
    if os.path.exists(NOTES):
        for r_ in csv.DictReader(open(NOTES, encoding='utf-8-sig')):
            TARGET[r_['es_conf_utc'].strip()] = r_['corrected_conf (estimate)'].strip()
    OUT = []; blocked_by_rp = []
    for r_ in rows:
        c = int(r_['es_conf_ms'])
        # THE WALK STARTS AT THE R-PRED, NOT THE EXHAUSTION (spec: "unless there is not an es_rpred_utc
        # signal / walk forward on s4"). All 14 of Joe's targets land AFTER es_rpred_utc (+8..+132 min,
        # mean +33) while 9 of 14 land BEFORE es_conf_utc - so a walk from the exhaustion cannot reach them.
        if not r_['es_rpred_ms']:
            continue
        i = int(np.searchsorted(ts, int(r_['es_rpred_ms'])))
        dr = 1 if r_['es_bias'] == 'bull' else -1
        # WALK: forward on s4 until s4Mage is OOB. No terminator.
        # THE WALK is the first OOB *CROSSING* after the r-pred, not the first bar that happens to be OOB.
        # Joe 0731 on 0522 11:54: s4Mage is already 98.16 (HI-OOB) at the r-pred bar, drops inside at
        # 12:40 and crosses back out at 12:48 - "12:48 - first s4M hi". The level test stopped at 11:54.
        # 8 of 14 marked rows had a zero-length walk, which is the signature of this repeating.
        M4 = MG[4]
        oob = np.flatnonzero(oob_qualified(M4, R.HI, R.LO)[i + 1:])
        if not len(oob):
            continue
        cand = (oob + i + 1).tolist()                  # every QUALIFIED bar after the r-pred

        def _derive(b):
            """side / MFE-side / eff-bias dir / momentum, all read AT bar b."""
            sd = 'hi' if M4[b] >= R.HI else 'lo'
            wt = 'hi' if dr > 0 else 'lo'
            mf = int(sd != wt)
            ed = -dr if mf else dr                     # MFE side -> bias reverses
            return sd, mf, ed, {tf: momo(E[tf]['r'], ed, b) for tf in (15, 22)}

        k = hops = 0
        w = cand[0]
        while True:
            side, mfe, edr, st = _derive(w)
            if not REWALK or st[22][0] != 'momo' or k + 1 >= len(cand):
                break
            if REWALK == 1 and hops >= 1:              # one hop only
                break
            k += 1; hops += 1; w = cand[k]
        # REWALK 3 (Joe 0801): the loop above settles on the first bar s22 is NO LONGER momo, which is the
        # moment momentum ends. Take ONE more s4Mage cycle past it, unconditionally, so the walk lands on a
        # bar that has been quiet for a full cycle. 38 of 87 settle on `sideways`/`curl` rather than `none`,
        # i.e. the line has flattened or turned rather than died. One cycle only - it does not re-enter the
        # loop, and it is skipped when there is no next crossing to walk to.
        # REWALK 4 = the CONDITIONAL overshoot: one extra cycle only on rows that actually hopped, i.e.
        # only where momentum was genuinely running and then stopped. REWALK 3's unconditional version
        # moved 85 of 87 rows and scored WORSE than no re-walk at all (MAE median 0.56 vs 0.49, p90 2.33
        # vs 1.52, median|err| vs Joe's 14 targets 93.5 vs 38.4) because it pushed the 58 rows REWALK 2
        # had correctly left alone.
        if REWALK in (3, 4) and k + 1 < len(cand) and (REWALK == 3 or hops > 0):
            k += 1; hops += 1; w = cand[k]
            side, mfe, edr, st = _derive(w)
        REWALK_HOPS[r_['es_conf_utc']] = hops
        rp = {tf: bool(RP[(tf, edr)][w]) for tf in TFS}
        dy = {tf: bool(DIRTY[(tf, edr)][w]) for tf in TFS}
        xdr = -1 if side == 'hi' else 1                # hi breach: x crosses DOWN through the target
        # momentum is EITHER line (Joe: "the distinction defines which TF holds the final cross").
        # sideways is BOTH (Joe 0731: "both lines need to be flat before a sideways verdict").
        # a DIRTY line votes for neither - it routes the row to s4 (Joe 0731 on 0520 07:42).
        momos = [tf for tf in (15, 22) if st[tf][0] == 'momo' and not dy[tf]]
        # a DIRTY line cannot r-pred - same gating rp_matrix applies to the predict term. Joe 0731 on
        # 0520 07:42: "1522 dirty. 0rp" - the lines carry a predict_breach state but are spent, so 0rp.
        rp1522 = [tf for tf in (15, 22) if rp[tf] and not dy[tf]]
        # Joe 0731: BRANCH (which line holds the cross) and ACTION (rev vs EXIT) are separate decisions.
        # "if 1 or more sideways is present at walk_forward, the signal needs to exit (with finishers),
        # not rev with finishers" - so ANY sideways line forces EXIT, whichever line carries the cross.
        any_sidew = any(st[tf][0] == 'sideways' for tf in (15, 22))
        # ...but momentum on either line OVERRIDES it: momo+sideways is rev on 5 of 5 marked rows
        # (06:26, 11:31, 17:58, 05:13, 08:50). So EXIT only when NO line carries momentum.
        act = 'EXIT' if (any_sidew and not momos) else 'rev'
        if momos:
            branch, action = 'momo', act
            rpd = [tf for tf in momos if rp[tf]]
            ctf = min(rpd) if rpd else min(momos)      # r-pred'd TF wins, else the lowest momo TF
            b, win, allf = race(ctf, w, xdr, ('boundary', 'r', 'Mage'))
        else:
            # s4 is the ELSE. Joe 0731: "if (none + sideways) then 15 and 22 are exhausted, delegate to s4
            # cross". The mixed state IS exhaustion, so the earlier "IF no rp and no momo" reading is
            # superseded - an r-pred on s15/s22 no longer blocks the fallback. blocked_by_rp counts the
            # rows the old gate would have swallowed, so the change stays visible.
            branch, action, ctf = 's4', act, 4
            if rp1522:
                blocked_by_rp.append(r_['es_conf_utc'])
            b, win, allf = race(4, w, xdr, ('m',))
            win = 'm'; allf = 'm' if b is not None else ''
        if b is not None and ctf == 4:
            # over/under Moob - OPEN, see docs/exhv2_spec.md §6. The strict reading (s4Mage must STILL be
            # OOB on the walk side at the cross bar) pushed 0520 06:26 and 07:42 from 07:58 to 0523 14:10 -
            # three days - because an s4x x s4m cross rarely coincides with s4Mage being OOB. Reverted to
            # the value test pending Joe's ruling. KNOWN WEAKNESS: when s4Mage has crossed to the far side
            # by the cross bar the test is vacuous - 0520 07:42 fires SHORT at 07:58 where s4Mage is -3.71
            # (LO-OOB), and x > -3.71 passes for almost any x (Joe 0731).
            def _moob(z):
                return (E[4]['x'][z] > MG[4][z]) if side == 'hi' else (E[4]['x'][z] < MG[4][z])
            if not _moob(b):
                b2 = None
                for z in np.flatnonzero(cross(4, 'm', xdr)[b + 1:]).tolist():
                    if _moob(z + b + 1):
                        b2 = z + b + 1; break
                b = b2
        # --- A UNGATED IS THE SIGNAL (Joe 0731: "let's adopt A ungated as the exit signal") ---
        # A = the FIRST s15x x s15m cross at or after the WALK bar, in the trade direction, with no
        # qualify and no gate. It replaces the branch race on ALL 87 rows, not just the EXIT ones -
        # Joe 0731 pointed at 0525 20:56 (branch momo, action rev, race "22 Mage" at 21:20) and asked
        # for 21:50, which is A. over/under Moob does not apply: A is ungated by definition.
        # Evidence, distance to the next swing_detect 1.00% pivot inside each of the 87 [walk, signal]
        # windows: |err| median 16.7 min vs the race at 34.4; 51 of 87 inside 30 min vs 38.
        # The branch/race result is STILL COMPUTED and stored (v2_race_*) - it decides `action`
        # (rev vs EXIT) and stays visible for validation. SWEEP KNOB: race-vs-A per branch.
        race_bar = b
        _a = np.flatnonzero(cross(15, 'm', xdr)[w:])
        b = int(_a[0]) + w if len(_a) else None
        sig = int(ts[b]) if b is not None else None
        race_ms = int(ts[race_bar]) if race_bar is not None else None
        tgt_utc = TARGET.get(r_['es_conf_utc'])
        err = None
        if sig and tgt_utc:
            # corrected_conf is TIME ONLY in the notes; the date comes from es_conf_utc. No correction in
            # the 14 crosses a day boundary - if one ever does this raises rather than silently rolling.
            mmdd = r_['es_conf_utc'].split()[0]
            tms = int(dt.datetime.strptime('2026' + mmdd + tgt_utc, '%Y%m%d%H:%M')
                      .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
            err = (sig - tms) / 60000
            tgt_utc = mmdd + ' ' + tgt_utc
        OUT.append((c, r_['es_conf_utc'], int(r_['es_cur_tf']), r_['es_bias'],
                    int(ts[w]), u(int(ts[w])), side, mfe, 'bull' if edr > 0 else 'bear',
                    st[15][0], st[15][1], st[15][2], st[15][3],
                    st[22][0], st[22][1], st[22][2], st[22][3],
                    int(rp[4]), int(rp[15]), int(rp[22]), int(dy[4]), int(dy[15]), int(dy[22]),
                    branch, action, ctf, win, allf, sig, u(sig) if sig else None,
                    (sig - c) / 60000 if sig else None, tgt_utc, err,
                    race_ms, u(race_ms) if race_ms else None))
    print('exhv2: %d of %d rows produced a walk  |  momo_r2_min %.2f  momo_slope_min %.2f'
          % (len(OUT), len(rows), _MC.MOMO_R2_MIN, _MC.MOMO_SLOPE_MIN))
    print('  reached s4 WITH an r-pred on s15/s22 (the old "no rp" gate would have blocked these): %d'
          % len(blocked_by_rp))
    if '--persist' in argv:
        d = DatabaseManager(**get_db_config()); d.connect()
        d.execute(DDL)
        for col, typ in (('v2_race_ms', 'BIGINT'), ('v2_race_utc', 'VARCHAR(11)')):
            try: d.execute('ALTER TABLE rpl_exhv2 ADD COLUMN %s %s' % (col, typ))
            except Exception: pass          # already present
        d.execute('DELETE FROM rpl_exhv2')
        d.executemany('''INSERT INTO rpl_exhv2 (v2_conf_ms,v2_conf_utc,v2_cur_tf,v2_bias,v2_walk_ms,
            v2_walk_utc,v2_walk_side,v2_mfe_side,v2_eff_bias,v2_s15_state,v2_s15_slope,v2_s15_r2,v2_s15_r,
            v2_s22_state,v2_s22_slope,v2_s22_r2,v2_s22_r,v2_rp4,v2_rp15,v2_rp22,v2_d4,v2_d15,v2_d22,
            v2_branch,v2_action,v2_cross_tf,v2_cross_tgt,v2_cross_all,v2_sig_ms,v2_sig_utc,v2_lead_min,
            v2_target_utc,v2_err_min,v2_race_ms,v2_race_utc)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', OUT)
        print('persisted %d rows to rpl_exhv2' % len(OUT))
        d.disconnect()
    return OUT


if __name__ == '__main__':
    main(sys.argv[1:])
