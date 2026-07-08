"""tide_machine.py — the tide-trigger machine as ONE parameterized function `run_config(J, K)`, so the sweep and the
wireframe consume the SAME machine (no fork). J = a Jig built with the right line overrides (s10r, s1); K = the
non-line knob dict (defaults below). Returns metrics: entries + entry-quality (exit-independent) + realised-at-exit.
Causal/emerging throughout (reads via the jig). Spec: docs/tide_exit_design.md."""
import numpy as np
from optimus9.analysis.lr_v2 import gate_open, gate_signals

DEFAULTS = dict(
    PROX=33, MID=50,
    ad_anchor='rev', ad_line='s5M', ad_wob=None, ad_predict=True, arm_max=1080,      # ad_wob None -> cfg.arm_wob
    use_gate=False, gate_horizon=1080,                                               # arm -> s3s4 gate (required) -> finisher
    fin_mode='nof9', fin_sets=('s2', 's15', 's30'), N=6, tol=12, box_lb=None, rev_sets=(),   # rev_sets: which sets require the Mage REVERSING (precise); the rest fire at the Mage BREACH (early)
    seam=300000, stall_floor=0.0, wait_breach=True, s2r_lb=None,                      # s2r_lb None -> cfg.s15r_lb
)


def _sgn(v, hi, lo):
    return np.where(v >= hi, 1, np.where(v <= lo, -1, 0))


def run_config(J, K0):
    K = dict(DEFAULTS); K.update(K0)
    cfg = J.cfg; n = J.n; ts = J.ts; px = J.px; HI, LO = J.hi, J.lo
    PROX, MID, SEAM = K['PROX'], K['MID'], K['seam']
    s2r_lb = K['s2r_lb'] if K['s2r_lb'] is not None else cfg.s15r_lb
    ad_wob = K['ad_wob'] if K['ad_wob'] is not None else cfg.arm_wob
    box_lb = K['box_lb'] if K['box_lb'] is not None else cfg.fin_lb
    L = {k: J.causal.line(k) for k in set(('s2m', 's3r', 's4r', 's2M', 's5M', 's7M', 's5m', 's5r', 's10r', K['ad_line']))}
    s2s, s5s = _sgn(L['s2m'], HI, LO), _sgn(L['s5m'], HI, LO)
    pred10 = J.causal.predict(L['s10r'], L['s5m'], L['s5M'])
    pred5 = J.causal.predict(L['s5r'], L['s5m'], L['s5M'])
    adL = L[K['ad_line']]; adrev = J.causal.reversal(adL, ad_wob); adoob = _sgn(adL, HI, LO)
    q15h, q15l = J.causal.finishers('s15'); q30h, q30l = J.causal.finishers('s30')
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

    def arm_delay(i, side):
        if not K['ad_predict']:
            return i
        mv = -1 if side == 'long' else 1; cap = min(n, i + K['arm_max'])
        oob = next((k for k in range(i, cap) if adoob[k] == mv), None)       # adL OOB on the faded-move side
        if oob is None:
            return i
        a = oob if K['ad_anchor'] == 'brk' else next((k for k in range(oob, cap) if adrev[k] == -mv), None)
        if a is None:
            return i
        return a if any(pred5[k] == mv for k in range(i, a + 1)) else i

    def reval(e, side):
        return (L['s5M'][e] > MID and L['s7M'][e] > MID and L['s2M'][e] > MID) if side == 'long' \
            else (L['s5M'][e] < MID and L['s7M'][e] < MID and L['s2M'][e] < MID)

    def finisher(a, side):
        if K['fin_mode'] == 'strict':
            q15, q30 = (q15l, q30l) if side == 'long' else (q15h, q30h)
            w0, w1 = max(0, a - cfg.fin_lb), min(n, a + cfg.fin_fwd + 1)
            if q15[w0:w1].any() and q30[w0:w1].any():
                return next((k for k in range(a, n) if q15[k]), None)
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

    def exit_walk(e, side):
        d = 1 if side == 'long' else -1
        exq = exq_h if side == 'long' else exq_l; both = both_h if side == 'long' else both_l
        f15, f30 = ((q15h, q30h) if side == 'long' else (q15l, q30l))
        b2 = None; pos = e + 1
        while pos < n:
            b1 = next((k for k in range(pos, n) if s5s[k] == d and s5s[k - 1] != d), None)
            if b1 is None:
                break
            w1 = min(n, b1 + 43); a15 = np.flatnonzero(f15[b1:w1]); a30 = np.flatnonzero(f30[b1:w1])
            if a15.size and a30.size:
                b2 = b1 + int(max(a15[0], a30[0])); break
            pos = b1 + 1
        if b2 is None:
            return n - 1
        pt = next((k for k in range(b2, n) if pred10[k] == d), None)
        if pt is not None:
            start = next((k for k in range(pt, n) if (L['s10r'][k] >= HI if d == 1 else L['s10r'][k] <= LO)), b2) if K['wait_breach'] else b2
            m = tsc >= ts[start]; tc, s10 = tsc[m], s10c[m]
            fl = K['stall_floor']
            stall = {int(tc[k]) for k in range(1, len(s10)) if (s10[k] - s10[k - 1] >= -fl if d == 1 else s10[k] - s10[k - 1] <= fl)}
            curl = J.causal.curl(tc, s10, -d)
            for st in sorted(curl | stall):
                x = next((k for k in range(int(np.searchsorted(ts, st)), n) if exq[k]), None)
                if x is not None:
                    return x
            return n - 1
        m = tsc >= ts[b2]; tc, s5r = tsc[m], s5rc[m]
        for st in sorted(J.causal.curl(tc, s5r, -d)):
            x = next((k for k in range(int(np.searchsorted(ts, st)), n) if both[k]), None)
            if x is not None:
                return x
        return n - 1

    armed = [(arm_delay(i, side), side) for i, side in ent]
    opens = None
    if K['use_gate']:                                            # arm -> s3s4 gate (REQUIRED) -> finisher runs from gate-open bar
        sig = gate_signals(J.W, cfg)
        setups = [(a, (-1 if s == 'long' else 1), (1 if s == 'long' else -1), min(n, a + K['gate_horizon']), 't') for a, s in armed]
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
        return dict(n=0, e_mae=0, e_mfe=0, mfeside=0, r_ret=0, win=0)
    lr_ent = [(int(ts[e]), (1 if side == 'short' else -1), (1 if side == 'long' else -1), e) for e, side in entries]
    eq = J.score.entry_quality(lr_ent)
    e_mae = np.median([r[4] for r in eq]); e_mfe = np.median([r[5] for r in eq]); mfeside = sum(int(r[7]) for r in eq)
    rets = []; rmae = []; rmfe = []; trades = []
    for e, side in entries:
        x = exit_walk(e, side); d = 1 if side == 'long' else -1
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * d          # realized excursion entry->exit (signed favourable)
        rets.append(float(seg[-1])); rmae.append(float(np.nanmin(seg))); rmfe.append(float(np.nanmax(seg)))
        trades.append((int(e), int(x), side, round(float(seg[-1]), 3), round(float(np.nanmin(seg)), 3)))
    rets = np.array(rets)
    return dict(n=len(entries), e_mae=round(float(e_mae), 3), e_mfe=round(float(e_mfe), 3), mfeside=mfeside,
                r_ret=round(float(np.median(rets)), 3), win=round(float((rets > 0).mean()), 3),
                r_mae=round(float(np.median(rmae)), 3), r_mfe=round(float(np.median(rmfe)), 3), trades=trades)
