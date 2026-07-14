"""bias_emit.py — Joe's 0713 cascade, as a Pine bgcolor emit. EMIT ONLY — not a spec, not a mechanic.

ONE artefact, one labelling scheme (Joe 0713 — a separate A/B pine is a human-error trap):

  RED     HI, BASE knobs          BLUE    HI, added by the CANDIDATE knobs
  GREEN   LO, BASE knobs          YELLOW  LO, added by the CANDIDATE knobs

Blue/yellow are exactly what the candidate BUYS over the base. Paint order is candidate-first,
base-over, so no bar is double-claimed. The config block is baked into the .pine header — the chart
is read hours later beside a newer run, and it must be able to say which knobs produced it.

Causal/emerging throughout. Every read via the jig; the primitives (seam_prev, seam_hold, seam_since,
grid_any, hold_at_start, cross) live IN the jig, not here.

  python3 bias_emit.py [hours] [end_YYYY-MM-DD_HH:MM]     (defaults: 24h, now)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
import arm_walk as AW

# ---- knobs --------------------------------------------------------------------------------------
EVAL_MS = 30_000          # the firing grid — the cascade is tested here, and s1m x s1r is measured here
TF_MID, TF_FAST = 8, 1
PREDICT_TOL = 0.0
S1M_OOB_MEM = 4           # "s1m WAS OOB" — eval samples of memory. 1 = 'is OOB', which never fires (s1m
                          # leaves OOB on the same sample it crosses s1r). 4 catches the 09:22 turn.
DEFAULT_HOURS = 24

# ---- ladder-delay entry (Joe 0714) ---------------------------------------------------------------
# A cascade fire LATCHES; it does not print. The ladder then walks forward for a better entry.
DELAY_ON = True
RUNGS = list(range(8, 23))                  # the ladder — 8..22 step 1
CURL_BANDS = AW.parse_bands(AW.DEFAULT_BANDS)   # coarse-curl seam = tf*60 // curl_div(tf)  — SWEEPABLE (Joe)
RUNG_MIDLINE_RESET = True    # a rung that has completed an OOB excursion on es may NOT be picked as the
                             #   apex again until its r has crossed the 50 midline (Joe 0714). Without it the
                             #   mini's next dive re-predicts a breach the r has just finished making.
CLIMB = 'highest'                           # at a curl: 'highest' predicting rung above current | 'next' rung up
S2MAGE = (60, ('bb', 37, 0.72, 'hlcc4'))    # THE established s2Mage (itf 60s), NOT this cascade's uniform
                                            # s2 (itf 120, bb 37|0.83|ohlc4). Joe named the proven producer.
PRINT_WOB = 1     # s2Mage reversal wobble for the PRINT trigger (lr_v2 _mage_rev). SPLIT from STAY_WOB:
                  #   one knob was timing the entry AND gating the cancel — two jobs, one dial (SRP).
STAY_WOB = 1      # s2Mage reversal wobble for the cancel's STAY test.
PRINT_MODE = 'wob'   # how the s2Mage turn is DETECTED for the print:
                     #   'wob'  = bar-by-bar slope-flip after PRINT_WOB same-direction steps (lr_v2 _mage_rev).
                     #            s2Mage flips 5846x/24h at wob=1 — it needs a big wob to find a real turn.
                     #   'curl' = coarse trough/peak on a seam-sampled series (jig.coarse + jig.curl) — the
                     #            SAME mechanism the ladder uses for every rung. Finds the turn, ignores wiggle.
PRINT_CURL_SEAM_S = 30   # 'curl' mode: the coarse seam for s2Mage (a 60s line -> 30s = 2 samples/bar). SWEEPABLE.
PRINT_REV = 'oob'   # the print trigger — the next s2Mage reversal toward the trade (rev == -es) that is ALSO
                    #   OOB on es (Joe 0714).  'anywhere' = boundary-agnostic (the canonical gate rule, which
                    #   explicitly forbids an OOB requirement — but that rule governs the GATE, not the print).
CANCEL_MODE = 'opp_breach'   # the latch's only death: s{tf_coarse}m goes OOB on the OPPOSING side — the reason
                    #   for the trade no longer exists.  Mirrors arm_walk.arm_cancel.  NO TIME CAP, EVER (Joe).
                    #   'off' = no cancel.  ('all_ib'/'breached_then_ib' are dead — see the 0714 knife-edge.)
CANCEL_STAY = True  # arm_walk's proven refinement: the opposing breach does NOT kill the latch if s2Mage
                    #   reverses back toward es within CANCEL_STAY_WIN bars of it (survive the twitch).
CANCEL_STAY_WIN = 60
NO_PRED_AT_FIRE = 'print'   # no rung predicting at the fire bar (Joe 0714): 'print' the trade immediately —
                            # there is no ladder to delay on, so there is nothing to wait for.
                            # 'wait' for a rung to predict | 'cancel' the latch.

# BASE = promoted / committed.  CAND = under test; its extra fires paint blue/yellow.
#   tf_coarse : the regime line — s{tf_coarse}m OOB is rung 1.
#   seam_div  : the intra-bar seam = TF / seam_div.
#   seam_mode : 'hold'  = sample the rung AT the seam and freeze it until the next seam. A breach landing
#                         mid-bucket is invisible for up to a full seam-width (it dropped 18:42 and 10:22).
#               'since' = has the rung held at ANY point since the seam opened (Joe's running min/max).
#                         Answers within one 30s sample of the breach, and still resets on the seam.
BASE = dict(tf_coarse=15, seam_div=8, seam_mode='since')     # promoted 0714: seam 8/since, then s20m -> s15m
CAND = dict(tf_coarse=15, seam_div=8, seam_mode='since')     # == BASE: no A/B in flight, nothing paints blue/yellow

# ---- line configs (Joe 0713, uniform across every TF) --------------------------------------------
#
# !! NOTATION vs DB TUPLE — they are NOT the same order (Joe 0714).  Getting this wrong is silent. !!
#
#   Joe writes a k-line as   k_len | rsi_len | stc_len | src        e.g. s{}r = 5|7|7|ohlc4
#   the DB tuple is         ('k',  rsi_len,  stc_len,  k_len, src)  e.g.        ('k', 7, 7, 5, 'ohlc4')
#                                   ^^^^^^^ the FIRST number in Joe's notation is the LAST in the tuple.
#
#   Verified against TV (transfer/BYBIT_FARTCOINUSDT.P_s120.csv, 54 bars): s120r built this way matches
#   TradingView to a mean absolute error of 0.03.  Built the other way round it is off by 9.33.
#   The DB tuple order is queued for a consistency fix — until then, TRANSLATE, don't assume.
#
R_CFG = ('k', 5, 7, 7, 'ohlc4')          # Joe's  k_len 7 | rsi 5 | stc 7   (Joe 0714 — A/B'd: the trades
                                         # are better positioned on this than on the TV chart's 5|7|7).
                                         # NOTE this is NOT the chart's s120r line (that is k_len 5|rsi 7|stc 7
                                         # = ('k',7,7,5), TV-verified MAE 0.03). We deliberately run a different r.
M_CFG = ('bb', 6, 0.56, 'ohlc4')         # bb: len | mult | src  (notation and tuple agree)
MAGE_CFG = ('bb', 37, 0.83, 'ohlc4')


def overrides(tfs):
    o = {}
    for tf in tfs:
        s = tf * 60
        o[f's{tf}r'] = (s, R_CFG, 'emerging')
        o[f's{tf}m'] = (s, M_CFG, 'emerging')
        o[f's{tf}Mage'] = (s, MAGE_CFG, 'emerging')
    o['s2Mage'] = (S2MAGE[0], S2MAGE[1], 'emerging')     # the established s2Mage, not the uniform s2
    return o


def delay_entry(j, es, fires, tf_coarse=15, print_wob=None, stay_wob=None,
                print_mode=None, curl_seam_s=None):
    """[Joe 0714] A cascade fire LATCHES and does NOT print. The ladder-delay then hunts a better entry.

      at the fire   sample the NON-SEAMED emerging r of every rung (8..22) -> current_tf = the HIGHEST
                    rung predicting on es.  (no rung predicting -> NO_PRED_AT_FIRE)
      walk forward  s{current_tf}r coarse-curls (toward -es):
                        a higher rung is predicting  -> climb: current_tf = that rung, keep walking
                        otherwise                    -> UNLATCH; print on the next s2Mage reversal (== -es)
                    all s1 lines in-band             -> CANCEL the latch, no print
      While a latch is open, further fires on the same side are absorbed by it — the latch prints ONCE.

    Returns (print_bars, trace) — trace is one dict per latch, so a consumer can ask what happened.
    Every read via the jig; the curl is jig.curl on jig.coarse, the reversal is jig.reversal (lr_v2)."""
    C = j.causal
    n = len(j.ts)

    ts = np.asarray(j.ts, np.int64)
    pred = {tf: C.predict_set(f's{tf}', tol=PREDICT_TOL, maj='Mage') == es for tf in RUNGS}
    if RUNG_MIDLINE_RESET:                                  # the r must cross 50 since its last OOB on es
        for tf in RUNGS:
            rr = C.line(f's{tf}r')
            oob_es = (rr >= 85.0) if es == 1 else (rr <= 15.0)
            crossed = (rr <= 50.0) if es == 1 else (rr >= 50.0)
            pred[tf] = pred[tf] & C.reset_since(oob_es, crossed)
    seam = {tf: tf * 60 // AW.curl_div(tf, CURL_BANDS) for tf in RUNGS}
    curl = {tf: {int(np.searchsorted(ts, t)) for t in C.curl(*C.coarse(f's{tf}r', seam[tf] * 1000), -es)}
            for tf in RUNGS}

    pw = PRINT_WOB if print_wob is None else print_wob
    sw = STAY_WOB if stay_wob is None else stay_wob
    pm = PRINT_MODE if print_mode is None else print_mode
    cs = PRINT_CURL_SEAM_S if curl_seam_s is None else curl_seam_s
    s2M = C.line('s2Mage')
    if pm == 'curl':                                               # coarse turn — the ladder's own mechanism
        rev_to_trade = np.zeros(n, bool)
        for t in C.curl(*C.coarse('s2Mage', cs * 1000), -es):
            rev_to_trade[int(np.searchsorted(ts, t))] = True
    else:
        rev_to_trade = C.reversal(s2M, pw) == -es                  # s2Mage turns toward the trade (bd = -es)
    s2M_oob_es = C.sign('s2Mage') == es                            # ...while OOB on the breach side
    printable = rev_to_trade & s2M_oob_es if PRINT_REV == 'oob' else rev_to_trade

    # the cancel: the regime line breaches the OPPOSING side. STAY: s2Mage turning back toward es within
    # CANCEL_STAY_WIN bars of that breach means the sell-off is reversing — the latch survives the twitch.
    opp = C.sign(f"s{tf_coarse}m") == -es
    opp_new = opp & ~np.concatenate([[False], opp[:-1]])
    stay = C.reversal(s2M, sw) == es
    kill = np.zeros(n, bool)
    for b in np.flatnonzero(opp_new):
        if CANCEL_STAY and stay[b:b + CANCEL_STAY_WIN + 1].any():
            continue
        kill[b] = True

    top = lambda k, above=0: next((tf for tf in reversed(RUNGS) if tf > above and pred[tf][k]), None)
    nxt = lambda k, above: next((tf for tf in RUNGS if tf > above and pred[tf][k]), None)
    climb = top if CLIMB == 'highest' else nxt

    out, trace = [], []
    k = 0
    while k < n:
        if not fires[k]:
            k += 1
            continue
        cur = top(k)
        if cur is None and NO_PRED_AT_FIRE != 'wait':
            if NO_PRED_AT_FIRE == 'print':                             # no ladder to delay on -> print now
                out.append(k)
                trace.append(dict(fire=k, cur=None, climbs=[], absorbed=0, end=k,
                                  why='PRINT (no rung predicting)', apex=None, print_bar=k))
            else:
                trace.append(dict(fire=k, cur=None, climbs=[], absorbed=0, end=k,
                                  why='cancelled — no rung predicting', apex=None, print_bar=None))
            k += 1
            continue
        t = dict(fire=k, cur=cur, climbs=[], absorbed=0)
        end, why, pk = n - 1, 'ran out of tape', None
        for w in range(k + 1, n):
            if fires[w]:
                t['absorbed'] += 1                                    # a later fire the latch swallowed
            if CANCEL_MODE == 'opp_breach' and kill[w]:
                end, why = w, f'cancelled — s{tf_coarse}m breached the opposing side'
                break
            if cur is None:                                           # NO_PRED_AT_FIRE == 'wait'
                cur = top(w)
                if cur is not None:
                    t['cur'] = cur
                    t['climbs'].append(('wait', w, cur))
                continue
            if w in curl[cur]:
                h = climb(w, above=cur)
                if h is not None:
                    t['climbs'].append(('curl', w, h))
                    cur = h
                    continue
                p = next((b for b in range(w, n) if printable[b]), None)   # unlatch -> next s2Mage reversal
                if p is None:
                    end, why = w, 'unlatched, no s2Mage reversal before the tape end'
                    break
                out.append(p)
                end, why, pk = p, 'PRINT', p
                break
        t.update(end=end, why=why, apex=cur, print_bar=pk)
        trace.append(t)
        k = end + 1                                                   # the latch owned everything up to here
    return np.array(sorted(out), int), trace


def spec_block(kn, label):
    """The cascade, in Joe's own shape, for the .pine header and the console. One source for both."""
    tc, sd, sm = kn['tf_coarse'], kn['seam_div'], kn['seam_mode']
    seam_c, seam_m = tc * 60 // sd, TF_MID * 60 // sd
    mode = 'running min/max since the seam' if sm == 'since' else 'sampled-and-held at the seam'
    return [
        f'{label}',
        f's{tc}m  OOB (es)                                       seam {seam_c}s, {mode}',
        f'  s{TF_MID}r already breached (OOB on es)',
        f'    OR was predicted when s{tc}m went OOB (latched)',
        f'    OR predicted now',
        f'    OR s{TF_MID}Mage OOB on es                              seam {seam_m}s, {mode}',
        f'      s{TF_MID}m closer to s{TF_MID}r than at the previous seam',
        f'        s1m was OOB (es) within {S1M_OOB_MEM} eval samples',
        f'          AND s1m crosses s1r toward 50               {EVAL_MS // 1000}s grid',
        f'Lines: r = k {"|".join(str(x) for x in R_CFG[1:])} · m = bb {"|".join(str(x) for x in M_CFG[1:])} '
        f'· Mage = bb {"|".join(str(x) for x in MAGE_CFG[1:])}.  TFs {tc} / {TF_MID} / {TF_FAST}.',
    ]


def rungs(j, es, tf_coarse=20, seam_div=8, seam_mode='since', oob_mem=None):
    """The four rungs as SEPARATE per-bar bools, for side es (+1 hi / -1 lo). Kept separate so a consumer
    can ask WHERE the cascade died — never fused into a single verdict (SRP)."""
    C = j.causal
    mem = S1M_OOB_MEM if oob_mem is None else oob_mem
    seam_c = tf_coarse * 60 // seam_div * 1000
    seam_m = TF_MID * 60 // seam_div * 1000
    gate = C.seam_since if seam_mode == 'since' else C.seam_hold

    breach = C.sign(f's{tf_coarse}m') == es             # rung 1's underlying OOB episode
    pred = C.predict_set(f's{TF_MID}', tol=PREDICT_TOL, maj='Mage') == es
    brc = C.sign(f's{TF_MID}r') == es                   # "already breached" — the r's OOB side (lr_v2 brc)

    c1 = gate(breach, seam_c)
    c2 = gate(brc | C.hold_at_start(breach, pred) | pred | (C.sign(f's{TF_MID}Mage') == es), seam_m)

    m_now, r_now = C.line(f's{TF_MID}m'), C.line(f's{TF_MID}r')
    m_pre, r_pre = C.seam_prev(f's{TF_MID}m', seam_m), C.seam_prev(f's{TF_MID}r', seam_m)
    c3 = np.abs(m_now - r_now) < np.abs(m_pre - r_pre)                # NaN at the tape head -> False

    # hi (es=+1): s1m was above s1r, now below -> cross == -1 == -es.  lo: mirrored.
    c4 = (C.grid_any(C.sign(f's{TF_FAST}m') == es, EVAL_MS, mem)
          & (C.cross(f's{TF_FAST}m', f's{TF_FAST}r', EVAL_MS) == -es))
    return c1, c2, c3, c4


def cascade(j, es, **kn):
    c1, c2, c3, c4 = rungs(j, es, **kn)
    return ((np.asarray(j.ts, np.int64) % EVAL_MS) == 0) & c1 & c2 & c3 & c4


# ---- the A/B in flight: how the s2Mage turn is detected for the PRINT ----------------------------
BASE_DELAY = dict(print_mode='wob', print_wob=10, stay_wob=1)     # red / green
CAND_DELAY = dict(print_mode='curl', curl_seam_s=30, stay_wob=1)  # blue / yellow


def delay_spec(d, label):
    if d['print_mode'] == 'curl':
        how = f"coarse curl on a {d['curl_seam_s']}s seam (jig.coarse + jig.curl)"
    else:
        how = f"bar-by-bar slope-flip, wob {d['print_wob']}"
    return [
        label,
        f'a cascade fire LATCHES — it does not print. Later same-side fires are absorbed.',
        f'  at the fire   current_tf = the HIGHEST rung 8..22 predicting on es (none -> print now)',
        f'  walk forward  s{{current_tf}}r coarse-curls -> a higher rung predicting?  climb, keep walking',
        f'                                             -> nothing above?             UNLATCH',
        f'  PRINT         the next s2Mage turn toward the trade, while s2Mage is OOB on es',
        f'                turn detected by: {how}',
        f'  CANCEL        s{{tf_coarse}}m breaches the OPPOSING side (stay: s2Mage turns back within '
        f'{CANCEL_STAY_WIN} bars, wob {d["stay_wob"]})',
        f'  NO TIME CAP. EVER.',
    ]


if __name__ == '__main__':
    HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_HOURS
    end = (dtm.datetime.strptime(sys.argv[2], '%Y-%m-%d_%H:%M').replace(tzinfo=timezone.utc)
           if len(sys.argv) > 2 else dtm.datetime.now(timezone.utc))
    end_ms = int(end.timestamp() * 1000)
    TFS = sorted(set([TF_FAST, TF_MID, BASE['tf_coarse']] + RUNGS))

    with Jig(end_ms, hours=HOURS, warmup=90, overrides=overrides(TFS)) as j:
        ts = np.asarray(j.ts, np.int64)
        win = ts >= (end_ms - HOURS * 3600_000)
        dt = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')

        P, TR, F = {}, {}, {}
        for nm, dk in (('base', BASE_DELAY), ('cand', CAND_DELAY)):
            for es in (+1, -1):
                F[es] = cascade(j, es, **BASE) & win
                pb, tr = delay_entry(j, es, F[es], tf_coarse=BASE['tf_coarse'], **dk)
                a = np.zeros(len(ts), bool)
                a[[k for k in pb if win[k]]] = True
                P[(nm, es)], TR[(nm, es)] = a, tr

        w0 = int(np.flatnonzero(win)[0])
        notes = ([f'bias cascade + LADDER-DELAY ENTRY — {dt(w0)} -> {dt(len(ts)-1)} UTC ({HOURS}h)', '',
                  'RED = HI base print · GREEN = LO base print · BLUE = HI candidate · YELLOW = LO candidate',
                  'These are DELAYED PRINTS, not the raw cascade fires.', '']
                 + spec_block(BASE, 'THE CASCADE (identical for both arms)') + ['']
                 + delay_spec(BASE_DELAY, 'BASE delay  (red / green)') + ['']
                 + delay_spec(CAND_DELAY, 'CANDIDATE delay  (blue / yellow)'))

        streams = [
            {'name': 'HI_cand', 'ts': ts[P[('cand', +1)]].tolist(), 'color': 'color.blue'},
            {'name': 'LO_cand', 'ts': ts[P[('cand', -1)]].tolist(), 'color': 'color.yellow'},
            {'name': 'HI_base', 'ts': ts[P[('base', +1)]].tolist(), 'color': 'color.red'},
            {'name': 'LO_base', 'ts': ts[P[('base', -1)]].tolist(), 'color': 'color.green'},
        ]
        path = '/home/joe/thecodes/transfer/bias_emit.pine'
        n = j.score.emit_bgcolor(streams, path, 'bias cascade + ladder-delay — wob vs curl print',
                                 opacity=0, notes=notes)
        print('\n'.join(notes))
        print()
        for nm in ('base', 'cand'):
            c = 'red/green' if nm == 'base' else 'blue/yellow'
            print(f"  {nm:<5} ({c:<11})  HI {int(P[(nm, +1)].sum()):>3}   LO {int(P[(nm, -1)].sum()):>3}")
        print(f'  raw cascade fires:      HI {int(F[+1].sum()):>3}   LO {int(F[-1].sum()):>3}')
        print(f'  painted {n}  ->  {path}')
        print()
        print(f"  {'fire':<16} {'apex':>4} {'abs':>3}  {'BASE print (wob)':<18} {'CAND print (curl)':<18} delta")
        for es, sd in ((+1, 'HI'), (-1, 'LO')):
            bt = {t['fire']: t for t in TR[('base', es)]}
            ct = {t['fire']: t for t in TR[('cand', es)]}
            for f in sorted(set(bt) | set(ct)):
                if not win[f]:
                    continue
                b, c = bt.get(f), ct.get(f)
                pb = dt(b['print_bar'])[6:] if b and b['print_bar'] is not None else (b['why'][:14] if b else '-')
                pc = dt(c['print_bar'])[6:] if c and c['print_bar'] is not None else (c['why'][:14] if c else '-')
                d = ''
                if b and c and b['print_bar'] is not None and c['print_bar'] is not None:
                    d = f"{(ts[b['print_bar']] - ts[c['print_bar']]) / 60000:+.1f}m"
                ap = b['apex'] if b else (c['apex'] if c else None)
                ab = b['absorbed'] if b else 0
                print(f"  {dt(f):<16} {str(ap):>4} {ab:>3}  {sd} {pb:<16} {sd} {pc:<16} {d}")
