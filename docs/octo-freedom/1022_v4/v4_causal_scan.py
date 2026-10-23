"""A causality audit of the v4 backstop + lineage + scoring chain. Measures, does not fix.

Joe 1023: *"deeply scan the code for any causal issues"*. After the 1023 repair this file is the
VERIFICATION: the counts that were non-zero are expected to read zero, and the ones Joe ruled to
keep (overlapping positions, the close-based stop) are reported rather than flagged.

Every row is a MEASURED count on the banked r-config over the full tape, not a code reading.

usage: v4_causal_scan.py <out.md>
"""
import sys, io, os
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_deferred_trades as DT
import v4_rcfg_sweep as RS
from v4_equity import ledger, CAPTURE, PCT, CAP, COINS, START, DRAG_22K
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e


def walk_trace(R, start_tf, side, A, B):
    """v4_fast.walk, but it also returns the TF of the rider the verdict came from.

    It mirrors the repaired walk: STAMPS and CONFIRM bars only. Kept as a third copy ONLY because
    it carries the rider TF the verdict came from, which the mech itself has no use for.
    """
    ST = {}
    for t in range(start_tf, K.TF_CEILING + 3):
        if t in R:
            _, _, ST[t] = F.first_rev_at_or_after(R[t], t, side, A, B)
    rid = start_tf
    if ST.get(rid) is None:
        return 'NO REVERSAL', None, None
    _, pas, _ = F.ib_cross(R[rid], rid, ST[rid], B)
    if pas is None:
        return 'NO IB CROSS', None, None
    while True:
        nxt = rid + 1
        if nxt > K.TF_CEILING:
            return 'EXHAUST', pas, rid
        if not K.ex_fence(R[nxt][pas], side):
            return 'EXHAUST', pas, rid
        if ST.get(nxt) is None:
            return 'NO REVERSAL', None, None
        if ST[nxt] > pas:
            rid = nxt
            _, pas, _ = F.ib_cross(R[rid], rid, ST[rid], B)
            if pas is None:
                return 'NO IB CROSS', None, None
            continue
        _, p2, _ = F.ib_cross(R[nxt], nxt, pas, B)
        if p2 is None:
            return 'NO IB CROSS', None, None
        n2 = nxt + 1
        if n2 > K.TF_CEILING:
            return 'EXHAUST', p2, nxt
        if not K.ex_fence(R[n2][p2], side):
            return 'EXHAUST', p2, nxt
        if ST.get(n2) is None:
            return 'NO REVERSAL', None, None
        if ST[n2] <= p2:
            return 'EXHAUST', p2, nxt
        rid = n2
        _, pas, _ = F.ib_cross(R[rid], rid, ST[rid], B)
        if pas is None:
            return 'NO IB CROSS', None, None


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    trip = (RS.K0, RS.R0, RS.S0)
    R = RS.load(trip)
    F.reset()
    f = F.scan(A, B, R, MG, 'window')
    rows = []
    for d in f:
        v, bar, rtf = walk_trace(R, 5, d['side'], d['rev'], B)
        un = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
        rows.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'], 'side': d['side'],
                     'dir': d['dir'], 'oob_bar': d['oob_bar'], 'rider_tf': rtf,
                     'verdict': 'UNRESOLVED' if un else v, 'exh': None if un else bar})
    acc = DT.accept(rows)
    L = ledger(acc, close, piv)
    # keyed on the EXHAUST bar, not zipped: `ledger` can drop a row (p0 <= 0, or an entry past the
    # tape end), and the 1023 audit flagged this zip as a latent misalignment in the audit tool.
    by_exh = {int(a['exh']): a for a in acc}
    for r in L:
        a = by_exh[int(r['exh'])]
        r.update({'rev': a['rev'], 'rider_tf': a['rider_tf'], 'side': a['side']})
    n = len(L)

    log('# A CAUSALITY AUDIT of v4-ws5rbackstop + v4-lineage + the scoring. banked k%d rsi%d stc%d.'
        % trip)
    log('# RULED_OK %s. the full tape, %d bars = %.0f days. %d trades.'
        % (K.RULED_OK, ln.N, ln.N * 5 / 86400.0, n))
    log('# every number below is MEASURED on those trades.')
    log('')

    # 1 the entry against the backstop's own stamp
    log('## 1  the entry against the bar the ws5r reversal becomes knowable')
    log('')
    log('# the backstop stamps its reversal at rev + LIFT_WOB - 1 = rev + %d bars = %d s.'
        % (K.LIFT_WOB - 1, (K.LIFT_WOB - 1) * 5))
    log('# REPAIRED 1023: the walk acts on the stamp, and the entry is max(fire, confirm) + 1.')
    log('#   The first two rows below must read 0. If either is non-zero the repair has regressed.')
    gap_st = np.array([r['en'] - r['stamp'] for r in L])
    gap_fi = np.array([r['en'] - r['fire'] for r in L])
    log('')
    log('| test | trades | share % |')
    log('|---|---|---|')
    log('| entry at or before the reversal stamp | %d | %.1f |'
        % (int((gap_st <= 0).sum()), 100.0 * (gap_st <= 0).sum() / n))
    log('| entry at or before the backstop fire bar | %d | %.1f |'
        % (int((gap_fi <= 0).sum()), 100.0 * (gap_fi <= 0).sum() / n))
    log('| entry strictly after the fire bar | %d | %.1f |'
        % (int((gap_fi > 0).sum()), 100.0 * (gap_fi > 0).sum() / n))
    log('')
    log('| statistic | bars | seconds |')
    log('|---|---|---|')
    log('| entry minus stamp, min | %d | %d |' % (gap_st.min(), gap_st.min() * 5))
    log('| entry minus stamp, median | %d | %d |' % (int(np.median(gap_st)),
                                                     int(np.median(gap_st)) * 5))
    log('| entry minus fire, min | %d | %d |' % (gap_fi.min(), gap_fi.min() * 5))
    log('| entry minus fire, median | %d | %d |' % (int(np.median(gap_fi)),
                                                    int(np.median(gap_fi)) * 5))
    log('')

    # 2 the ib dwell
    log('## 2  the ib dwell is proven on future bars')
    log('')
    log('# REPAIRED 1023: F.ib_cross returns the CONFIRM bar k + need - 1, and the walk acts on')
    log('#   that. These are the dwell SIZES the repair now waits out, per final rider TF.')
    log('#   need = int(TF x %.1f) bars.' % K.LIN_IB_DWELL)
    need = np.array([K.lin_ib_dwell(r['rider_tf']) for r in L if r['rider_tf']])
    log('')
    log('| statistic | bars | seconds |')
    log('|---|---|---|')
    log('| the final rider dwell, min | %d | %d |' % (need.min(), need.min() * 5))
    log('| the final rider dwell, median | %d | %d |' % (int(np.median(need)),
                                                         int(np.median(need)) * 5))
    log('| the final rider dwell, max | %d | %d |' % (need.max(), need.max() * 5))
    log('| the unknowable lead, median = dwell - 1 | %d | %d |'
        % (int(np.median(need)) - 1, (int(np.median(need)) - 1) * 5))
    log('')
    log('| the final rider TF | trades |')
    log('|---|---|')
    for t in sorted(set(r['rider_tf'] for r in L if r['rider_tf'])):
        log('| ws%d | %d |' % (t, sum(1 for r in L if r['rider_tf'] == t)))
    log('')

    # 3 concurrency, and whether the two sides overlap
    log('## 3  concurrent positions, and opposite directions held at once')
    log('')
    log('# RULED 1023, Joe: *"let\'s see how that plays out. if hedging is profitable and causal,')
    log('#   I\'m not against it. it will need a safe max_pyramid setting that only the account')
    log('#   (leverage) can provide"*. So overlap is reported, not flagged. max_pyramid is his knob.')
    ov = 0
    opp = 0
    for i, a in enumerate(L):
        for b in L[i + 1:]:
            if b['en'] > a['xb']:
                break
            ov += 1
            if b['dir'] != a['dir']:
                opp += 1
    log('')
    log('| test | count |')
    log('|---|---|')
    log('| overlapping trade pairs | %d |' % ov)
    log('| overlapping pairs in OPPOSITE directions | %d |' % opp)
    holds = np.array([r['xb'] - r['en'] + 1 for r in L])
    log('| the hold, median bars | %d |' % int(np.median(holds)))
    log('| the hold, max bars | %d |' % int(holds.max()))
    log('| the hold, max seconds | %d |' % (int(holds.max()) * 5))
    log('')

    # 4 the stop is tested on closes only
    log('## 4  the -%.3f%% stop is tested on CLOSES, not on the bar lows' % CAP)
    log('')
    log('# RULED 1023, Joe: *"we\'re not feeding the ticks to the machine ... the only option we')
    log('#   have is `close`. ... it\'s a close-based check for now. posting a stop order is on the')
    log('#   roadmap"*. The low/high row is the side column, carried so it cannot drift.')
    st_close = sum(1 for r in L if r['why'] == 'STOP')
    st_intra, moved, g_close, g_intra = 0, 0, 0.0, 0.0
    for r in L:
        d = 1 if r['dir'] == 'LONG' else -1
        en, xb = r['en'], r['xb']
        p0 = r['px']
        adv = (np.asarray(lo[en:xb + 1], float) - p0) / p0 * 100.0 if d > 0 \
            else (p0 - np.asarray(hi[en:xb + 1], float)) / p0 * 100.0
        worst = float(np.nanmin(adv)) if np.isfinite(adv).any() else 0.0
        hit = worst <= -CAP
        st_intra += 1 if hit else 0
        g_close += r['od_g']
        g_intra += (-CAP if hit else r['od_g'])
        if hit and r['why'] != 'STOP':
            moved += 1
    log('')
    log('| test | trades | share % |')
    log('|---|---|---|')
    log('| stopped, measured on closes | %d | %.1f |' % (st_close, 100.0 * st_close / n))
    log('| stopped, measured on the bar lows and highs | %d | %.1f |'
        % (st_intra, 100.0 * st_intra / n))
    log('| trades the intrabar stop would have caught and the close test missed | %d | %.1f |'
        % (moved, 100.0 * moved / n))
    log('')
    log('| reading | gross %% | drag at %.4f%% | NET %% |' % DRAG_22K)
    log('|---|---|---|---|')
    for nm, g in (('close only, as reported', g_close), ('the bar lows and highs', g_intra)):
        log('| %s | %+.2f | %.2f | %+.2f |' % (nm, g, n * DRAG_22K, g - n * DRAG_22K))
    usd_close = sum((r['od_g'] / 100.0 - DRAG_22K / 100.0) * COINS * r['px'] for r in L)
    log('')
    log('| reading | net USDT at %d coins |' % COINS)
    log('|---|---|')
    log('| close only, as reported | %+.2f |' % usd_close)
    usd_intra = 0.0
    for r in L:
        d = 1 if r['dir'] == 'LONG' else -1
        en, xb, p0 = r['en'], r['xb'], r['px']
        adv = (np.asarray(lo[en:xb + 1], float) - p0) / p0 * 100.0 if d > 0 \
            else (p0 - np.asarray(hi[en:xb + 1], float)) / p0 * 100.0
        worst = float(np.nanmin(adv)) if np.isfinite(adv).any() else 0.0
        g = -CAP if worst <= -CAP else r['od_g']
        usd_intra += (g / 100.0 - DRAG_22K / 100.0) * COINS * p0
    log('| the bar lows and highs | %+.2f |' % usd_intra)
    log('| the difference | %+.2f |' % (usd_intra - usd_close))
    log('')

    # 5 the segment that has no further pivot
    log('## 5  trades whose excursion runs to the end of the tape')
    nop = sum(1 for r in L if r['why'] == 'PIVOT')
    log('')
    log('| test | count |')
    log('|---|---|')
    log('| exits booked at the segment end, no 90%% level and no stop | %d |' % nop)
    log('| the last trade entry | %s |' % ln.U(max(r['en'] for r in L)))
    log('| the last trade exit | %s |' % ln.U(max(r['xb'] for r in L)))
    log('| the tape end | %s |' % ln.U(ln.N - 1))
    out.close()
