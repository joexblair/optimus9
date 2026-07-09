"""tide_machine.py — the tide-trigger machine as ONE parameterized function `run_config(J, K)`, so the sweep and the
wireframe consume the SAME machine (no fork). J = a Jig built with the right line overrides (s10r, s1); K = the
non-line knob dict (defaults below). Returns metrics: entries + entry-quality (exit-independent) + realised-at-exit.
Causal/emerging throughout (reads via the jig). Spec: docs/tide_exit_design.md."""
import numpy as np
from optimus9.analysis.lr_v2 import gate_open, gate_signals

DEFAULTS = dict(
    PROX=33, MID=50,                                                                 # NO arm_delay — greenfield build, the entry arms on the s2m breach directly (arm_delay was look-ahead, removed 0708)
    use_gate=False,                                                                  # arm -> s3s4 gate (required) -> finisher  [dormant path, uncapped]
    fin_mode='strict', fin_sets=('s2', 's15', 's30'), N=6, tol=12, box_lb=None, rev_sets=(),   # nof9 knobs kept for A/B; rev_sets = sets requiring the Mage REVERSING
    fin_lb=6, fin_fwd=6,                                                              # entry s30a+s15a box = 1,1 (1x30s back, 1x30s fwd) — PLACEHOLDER pending an arm-placement A/B (Joe 0708); the answer's in where the arm lands
    exit_fin_lb=None,                                                                # RESERVED (7,2 exit box dropped 0708) — returns only if an s3s4 A/B proves viable
    seam=300000, stall_floor=0.0, wait_breach=True, s2r_lb=None,                      # s2r_lb None -> cfg.s15r_lb
    exit_gate='oob',                                                                  # exit trigger must turn on the trade's TARGET side: 'oob' (>=HI/<=LO), 'mid' (past MID), 'off' (any turn)
    pair_box=12,                                                                      # s30a+s15a co-occurrence box (5s bars, 12 = 2x30s) via jig.causal.finisher_pair — shared by entry(strict) + exit
)


def _sgn(v, hi, lo):
    return np.where(v >= hi, 1, np.where(v <= lo, -1, 0))


def run_config(J, K0):
    K = dict(DEFAULTS); K.update(K0)
    cfg = J.cfg; n = J.n; ts = J.ts; px = J.px; HI, LO = J.hi, J.lo
    PROX, MID, SEAM = K['PROX'], K['MID'], K['seam']
    s2r_lb = K['s2r_lb'] if K['s2r_lb'] is not None else cfg.s15r_lb
    box_lb = K['box_lb'] if K['box_lb'] is not None else cfg.fin_lb
    L = {k: J.causal.line(k) for k in ('s2m', 's3r', 's4r', 's2M', 's5M', 's7M', 's5m', 's5r', 's10r')}
    s2s, s5s = _sgn(L['s2m'], HI, LO), _sgn(L['s5m'], HI, LO)
    pred10 = J.causal.predict(L['s10r'], L['s5m'], L['s5M'])
    q15h, q15l = J.causal.finishers('s15'); q30h, q30l = J.causal.finishers('s30')
    pair_hi, pair_lo = J.causal.finisher_pair(box=K['pair_box'])                     # THE s30a+s15a event (jig) — exit stage-1 confirm
    epair_hi, epair_lo = J.causal.finisher_pair(box=K['fin_lb'] + K['fin_fwd'])      # entry s30a+s15a co-occurrence over the [a-fin_lb, a+fin_fwd] box
    fsets = set(K['fin_sets']) | {'s15', 's30'}
    parts = {tf: J.causal.finisher_parts(tf, r_lb=(s2r_lb if tf in ('s2', 's1') else None)) for tf in fsets}
    cm = (ts % SEAM) == 0; tsc = ts[cm]; s10c = L['s10r'][cm]; s5rc = L['s5r'][cm]

    cutoff = J.end_ms - J.hours * 3600 * 1000                    # trade window only (exclude warmup)
    ent = []
    for i in range(1, n):
        if ts[i] < cutoff:
            continue
        if s2s[i] == -1 and s2s[i - 1] != -1 and (L['s3r'][i] < PROX or L['s4r'][i] < PROX) and L['s5M'][i] > MID and L['s7M'][i] > MID and L['s2M'][i] > MID:
            ent.append((i, 'long'))
        if s2s[i] == 1 and s2s[i - 1] != 1 and (L['s3r'][i] > 100 - PROX or L['s4r'][i] > 100 - PROX) and L['s5M'][i] < MID and L['s7M'][i] < MID and L['s2M'][i] < MID:
            ent.append((i, 'short'))

    def reval(e, side):
        return (L['s5M'][e] > MID and L['s7M'][e] > MID and L['s2M'][e] > MID) if side == 'long' \
            else (L['s5M'][e] < MID and L['s7M'][e] < MID and L['s2M'][e] < MID)

    def finisher(a, side):
        if K['fin_mode'] == 'strict':
            epair = epair_hi if side == 'short' else epair_lo   # long enters a dip (lo finishers), short fades a pop (hi)
            if epair[min(n - 1, a + K['fin_fwd'])]:             # s30a+s15a co-occur in [a-fin_lb, a+fin_fwd] via the jig event
                q15 = q15l if side == 'long' else q15h
                return next((k for k in range(a, n) if q15[k]), None)  # trade on the next s15a >= arm
            return None
        sd = 'lo' if side == 'long' else 'hi'; w0, w1 = max(0, a - box_lb), min(n, a + K['tol'] + 1); events = []
        for tf in K['fin_sets']:
            P = parts[tf]; Moob = P['Moob_' + sd]; Mrev = P['Mrev_' + sd]; rlb = P['rlb_' + sd]
            if tf in K['rev_sets']:
                ev = [k for k in range(w0, w1) if Moob[k] and Mrev[k]]                    # reversal (precise, later)
            else:
                ev = [k for k in range(max(1, w0), w1) if Moob[k] and not Moob[k - 1]]     # breach (early)
            if ev:
                events.append((ev[0], 2 + (1 if any(rlb[k] for k in ev) else 0)))
        events.sort(); cum = 0
        for k0, lines in events:
            cum += lines
            if cum >= K['N']:
                return max(k0, a)
        return None

    exq_l, exq_h = q15l, q15h
    both_l, both_h = q15l & q30l, q15h & q30h

    def fav_side(val, d):                                        # is a turn on the trade's TARGET (favourable) side?
        if K['exit_gate'] == 'off':
            return True
        lo, hi = (LO, HI) if K['exit_gate'] == 'oob' else (MID, MID)
        return val <= lo if d == -1 else val >= hi              # short covers on a LO trough; long sells a HI peak

    def exit_walk(e, side):
        d = 1 if side == 'long' else -1
        exq = exq_h if side == 'long' else exq_l; both = both_h if side == 'long' else both_l
        # STAGE 1: s5m breach to the trade side (the exit-arm) confirmed by the s30a+s15a EVENT within pair_box (jig
        # finisher_pair, box=12=2x30s trailing — the causal replacement for the dropped 42-fwd hand-rolled box).
        pair = pair_hi if side == 'long' else pair_lo
        b2 = next((k for k in range(e + 1, n) if s5s[k] == d and s5s[k - 1] != d and pair[k]), None)
        if b2 is None:
            return n - 1, 'nocasc'
        pt = next((k for k in range(b2, n) if pred10[k] == d), None)
        if pt is not None:
            start = next((k for k in range(pt, n) if (L['s10r'][k] >= HI if d == 1 else L['s10r'][k] <= LO)), b2) if K['wait_breach'] else b2
            m = tsc >= ts[start]; tc, s10 = tsc[m], s10c[m]
            fl = K['stall_floor']
            stall = {int(tc[k]) for k in range(1, len(s10)) if (s10[k] - s10[k - 1] >= -fl if d == 1 else s10[k] - s10[k - 1] <= fl) and fav_side(s10[k], d)}
            curl = {st for st, v in J.causal.curl(tc, s10, -d, with_val=True).items() if fav_side(v, d)}
            for st in sorted(curl | stall):
                x = next((k for k in range(int(np.searchsorted(ts, st)), n) if exq[k]), None)
                if x is not None:
                    return x, 's10r'
            return n - 1, 'r1bound'
        m = tsc >= ts[b2]; tc, s5r = tsc[m], s5rc[m]
        curl5 = {st for st, v in J.causal.curl(tc, s5r, -d, with_val=True).items() if fav_side(v, d)}
        for st in sorted(curl5):
            x = next((k for k in range(int(np.searchsorted(ts, st)), n) if both[k]), None)
            if x is not None:
                return x, 's5r'
        return n - 1, 'r2bound'

    armed = list(ent)                                            # greenfield: the s2m breach IS the arm — no arm_delay, no forward scan
    opens = None
    if K['use_gate']:                                            # arm -> s3s4 gate (REQUIRED) -> finisher runs from gate-open bar
        sig = gate_signals(J.W, cfg)
        setups = [(a, (-1 if s == 'long' else 1), (1 if s == 'long' else -1), n, 't') for a, s in armed]
        opens = {}
        for o in gate_open(J.W, cfg, setups, sig):
            opens.setdefault(o[0], o[3])                         # arm_bar -> gate-open bar (ok)
    entries = []
    for a, side in armed:
        if opens is not None:
            if a not in opens:
                continue                                        # no s3s4 gate opened -> groomed out
            a = opens[a]
        e = finisher(a, side)
        if e is None or not reval(e, side):
            continue
        entries.append((e, side))
    if not entries:
        return dict(n=0, e_mae=0, e_mfe=0, mfeside=0, r_ret=0, r_mean=0, win=0, r_mae=0, mae_tail=0, r_mfe=0, trades=[])
    lr_ent = [(int(ts[e]), (1 if side == 'short' else -1), (1 if side == 'long' else -1), e) for e, side in entries]
    eq = J.score.entry_quality(lr_ent)
    e_mae = np.median([r[4] for r in eq]); e_mfe = np.median([r[5] for r in eq]); mfeside = sum(int(r[7]) for r in eq)
    rets = []; rmae = []; rmfe = []; trades = []
    for e, side in entries:
        x, route = exit_walk(e, side); d = 1 if side == 'long' else -1
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * d          # realized excursion entry->exit (signed favourable)
        rets.append(float(seg[-1])); rmae.append(float(np.nanmin(seg))); rmfe.append(float(np.nanmax(seg)))
        trades.append((int(e), int(x), side, round(float(seg[-1]), 3), round(float(np.nanmin(seg)), 3), route))
    rets = np.array(rets); rmae_a = np.array(rmae)
    tk = max(1, len(rmae_a) // 10)                              # worst-decile (CVaR10) of realized MAE = the honest adverse tail
    mae_tail = float(np.sort(rmae_a)[:tk].mean())
    return dict(n=len(entries), e_mae=round(float(e_mae), 3), e_mfe=round(float(e_mfe), 3), mfeside=mfeside,
                r_ret=round(float(np.median(rets)), 3), r_mean=round(float(rets.mean()), 3), win=round(float((rets > 0).mean()), 3),
                r_mae=round(float(np.median(rmae)), 3), mae_tail=round(mae_tail, 3), r_mfe=round(float(np.median(rmfe)), 3),
                trades=trades)
