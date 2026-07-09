"""greenfield_producer.py — the CAUSAL entry producer (Joe 0708), a drop-in for o9-live's look-ahead v2_walk_ad.

Same tuple contract as v2_walk_ad:  (W, cfg) -> [(entry_ms, es, bd, bar_idx)].
Entry = s2m breach + tide filter (s3r/s4r proximal · s5M/s7M/s2M vs MID) -> strict s30a+s15a finisher (1,1 box via
_rolling_any co-occurrence) -> trade on the next s15a >= arm -> reval (tide still aligned at the entry bar). There is
NO arm_delay / forward scan, so the entry is window-invariant (causal) — which is what makes o9-live's
'window-ending-at-now == backtest' invariant actually hold. Reuses s_qualify + _rolling_any (no forked logic); the
entry bars are byte-equivalent to tide_machine.run_config's (verified).
"""
import numpy as np
from optimus9.analysis.lr_v2 import s_qualify, _rolling_any, gate_signals, gate_open, finisher


def greenfield_walk(W, cfg, PROX=33, MID=50, fin_lb=6, fin_fwd=6):
    ts = W.ts; n = len(ts); HI, LO = cfg.hi, cfg.lo
    L = {k: np.asarray(W.line(k), float) for k in ('s2m', 's3r', 's4r', 's2M', 's5M', 's7M')}
    s2s = np.where(L['s2m'] >= HI, 1, np.where(L['s2m'] <= LO, -1, 0))
    q15h, q15l = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
    q30h, q30l = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
    box = fin_lb + fin_fwd
    ep_hi = _rolling_any(q15h, box) & _rolling_any(q30h, box)         # s30a+s15a co-occurrence, short side
    ep_lo = _rolling_any(q15l, box) & _rolling_any(q30l, box)         # long side
    seen, out = set(), []
    for i in range(1, n):
        for side in ('long', 'short'):                               # s2m breach + tide filter (the arm)
            if side == 'long':
                arm = (s2s[i] == -1 and s2s[i - 1] != -1 and (L['s3r'][i] < PROX or L['s4r'][i] < PROX)
                       and L['s5M'][i] > MID and L['s7M'][i] > MID and L['s2M'][i] > MID)
            else:
                arm = (s2s[i] == 1 and s2s[i - 1] != 1 and (L['s3r'][i] > 100 - PROX or L['s4r'][i] > 100 - PROX)
                       and L['s5M'][i] < MID and L['s7M'][i] < MID and L['s2M'][i] < MID)
            if not arm:
                continue
            ep = ep_hi if side == 'short' else ep_lo                 # strict s30a+s15a co-occur in [a-fin_lb, a+fin_fwd]?
            if not ep[min(n - 1, i + fin_fwd)]:
                continue
            q15 = q15l if side == 'long' else q15h                   # trade on the next s15a >= arm
            e = next((k for k in range(i, n) if q15[k]), None)
            if e is None or e in seen:
                continue
            ok = (L['s5M'][e] > MID and L['s7M'][e] > MID and L['s2M'][e] > MID) if side == 'long' \
                else (L['s5M'][e] < MID and L['s7M'][e] < MID and L['s2M'][e] < MID)     # reval
            if not ok:
                continue
            seen.add(e)
            bd = 1 if side == 'long' else -1                         # bd +1 long/Buy, -1 short/Sell ; es = -bd
            out.append((int(ts[e]), -bd, bd, int(e)))
    out.sort()
    return out


def greenfield_arm(W, cfg, PROX=33, MID=50):
    """WITHOUT greenfield's own s30a+s15a finisher — entry fires at the tide-filtered s2m breach directly, leaving the
    s30a+s15a finishing to o9-live's baked-in machinery. Same (W,cfg)->[(entry_ms, es, bd, bar_idx)] contract. Use this
    variant to A/B against greenfield_walk when the finishers already live downstream (Joe 0708)."""
    ts = W.ts; n = len(ts); HI, LO = cfg.hi, cfg.lo
    L = {k: np.asarray(W.line(k), float) for k in ('s2m', 's3r', 's4r', 's2M', 's5M', 's7M')}
    s2s = np.where(L['s2m'] >= HI, 1, np.where(L['s2m'] <= LO, -1, 0))
    out = []
    for i in range(1, n):
        long_arm = (s2s[i] == -1 and s2s[i - 1] != -1 and (L['s3r'][i] < PROX or L['s4r'][i] < PROX)
                    and L['s5M'][i] > MID and L['s7M'][i] > MID and L['s2M'][i] > MID)
        short_arm = (s2s[i] == 1 and s2s[i - 1] != 1 and (L['s3r'][i] > 100 - PROX or L['s4r'][i] > 100 - PROX)
                     and L['s5M'][i] < MID and L['s7M'][i] < MID and L['s2M'][i] < MID)
        if long_arm:
            out.append((int(ts[i]), -1, 1, int(i)))
        elif short_arm:
            out.append((int(ts[i]), 1, -1, int(i)))
    return out


def greenfield_setups(W, cfg, PROX=33, MID=50, horizon=None):
    """The greenfield CAUSAL arm in v2_arm's setup format [(i, es, bd, cap, src)] so it can feed o9-live's
    gate_open + finisher unchanged. Arm = tide-filtered s2m breach; cap = min(opposite s2m breach, i+horizon)
    (the arm cancels on the other-side breach — spec-legal, causal). src='gf'."""
    horizon = horizon or cfg.horizon
    n = len(W.ts); hi, lo = cfg.hi, cfg.lo
    L = {k: np.asarray(W.line(k), float) for k in ('s2m', 's3r', 's4r', 's2M', 's5M', 's7M')}
    s2s = np.where(L['s2m'] >= hi, 1, np.where(L['s2m'] <= lo, -1, 0))
    m = {}
    for i in range(1, n):
        if (s2s[i] == -1 and s2s[i - 1] != -1 and (L['s3r'][i] < PROX or L['s4r'][i] < PROX)
                and L['s5M'][i] > MID and L['s7M'][i] > MID and L['s2M'][i] > MID):
            m[i] = (-1, 1, 'gf')                                     # long: es=-1, bd=+1
        elif (s2s[i] == 1 and s2s[i - 1] != 1 and (L['s3r'][i] > 100 - PROX or L['s4r'][i] > 100 - PROX)
              and L['s5M'][i] < MID and L['s7M'][i] < MID and L['s2M'][i] < MID):
            m[i] = (1, -1, 'gf')                                    # short: es=+1, bd=-1
    idx = np.arange(n)
    nxt_hi = np.minimum.accumulate(np.where(s2s == 1, idx, n)[::-1])[::-1]    # next hi breach >= k (opposite for long)
    nxt_lo = np.minimum.accumulate(np.where(s2s == -1, idx, n)[::-1])[::-1]   # next lo breach >= k (opposite for short)
    out = []
    for i, (es, bd, src) in sorted(m.items()):
        opp = (nxt_lo[i + 1] if es == 1 else nxt_hi[i + 1]) if i + 1 < n else n
        out.append((i, es, bd, min(opp, i + horizon), src))
    return out


def greenfield_cascade(W, cfg, PROX=33, MID=50):
    """THE o9-live drop-in (Joe 0708): greenfield CAUSAL arm → o9-live's s3s4 gate → o9-live's finisher. Reuses
    gate_signals / gate_open / finisher verbatim (no forked logic); only the arm is swapped for the causal one.
    Same (W,cfg)->[(entry_ms, es, bd, bar_idx)] contract as v2_walk_ad."""
    setups = greenfield_setups(W, cfg, PROX, MID)
    sig = gate_signals(W, cfg)
    seen, out = set(), []
    for e in finisher(W, cfg, gate_open(W, cfg, setups, sig)):
        if e[3] not in seen:
            seen.add(e[3]); out.append(e)
    return out
