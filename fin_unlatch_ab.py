"""fin_unlatch_ab.py — D3, the A/B that is build-as-shipped vs spec-as-written.

ARM A (BUILD)  fin_unlatch enters at e = first q15 >= unlatch. For 217 of 1897 M1 trades the authorising
               q30 fires AFTER e -> the entry used a bar from its own future. Live can never fire these.
ARM B (SPEC)   spec sec.4: "walk FORWARD with 2x30s tolerance for a late line" -> wait for the late line,
               i.e. enter at max(e, j30). Exactly what the sibling fin_gate already does via max(j15,j30).
               Causal by construction. The 217 do NOT vanish; they fire a median 20s later, at a worse price.

Question: does the later, causal entry still make money? If yes, the spec repair RECOVERS ~5 trades/day that
o9-live currently forfeits. If no, the 42d book is inflated by trades that only ever paid because they
entered before their own signal -- and every number fitted on it (exit curl, stop optimum, risk cap) inherits
that inflation.

strand_rescue is deliberately NOT applied: it is gated on the completed x[6]=='SL' outcome (register B3), so
it cannot run live and would contaminate a causality experiment. Exits are lr_exit_v2 raw.

Per-trade net % (bd-signed, minus COST round-trip) -- reported for both arms and split by cohort, so the 217
can be read on their own. Read-only. Run:  python3 fin_unlatch_ab.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import (v2_arm, arm_delay, gate_open, s_qualify,
                                     fin_unlatch, fin_gate, lr_exit_v2)

SPAN_D = 42
COST = 0.20            # % round trip, the established estimate


def build_chain(W, lr):
    """v2_cascade, but recording for each M1 trade: the built entry e, the causal entry max(e,j30), dirty?"""
    setups = v2_arm(W, lr)
    if lr.arm_bigleg:
        setups = arm_delay(W, lr, setups)
    opens = {o[0]: o for o in gate_open(W, lr, setups)}
    q15h, q15l = s_qualify(W, lr, 's15m', 's15M', 's15r', lr.s15r_lb)
    q30h, q30l = s_qualify(W, lr, 's30m', 's30M', 's30r', lr.s30r_lb)

    rows = []                                                   # (e_build, e_spec, es, bd, dirty)
    for (i, es, bd, cap, src) in setups:
        q15, q30 = (q15h, q30h) if es == 1 else (q15l, q30l)
        tk = fin_unlatch(q15, q30, i, cap, lr.fin_lb, lr.fin_fwd)
        if tk is None:
            o = opens.get(i)
            if o is not None:
                g = fin_gate(q15, q30, o[3], cap)
                if g is not None:
                    rows.append((g, g, es, bd, False))          # M2: causal, identical in both arms
            continue
        w0, w1 = max(0, i - lr.fin_lb), min(cap, i + lr.fin_fwd + 1)
        p30 = np.flatnonzero(q30[w0:w1]) + w0
        j30 = int(p30.min()) if p30.size else tk
        dirty = j30 > tk
        # ARM B: wait for the late line. The entry is the first q15 at/after the authorising q30.
        e_spec = tk if not dirty else next((k for k in range(j30, cap) if q15[k]), None)
        rows.append((tk, e_spec, es, bd, dirty))
    return rows


def pnl(W, lr, entries):
    """lr_exit_v2 (no strand_rescue) -> per-trade net %, keyed by entry bar."""
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    ent = [(int(ts[k]), es, bd, k) for (k, es, bd) in entries]
    out = {}
    for (tms, exms, bd, epx, xpx, r, reason) in lr_exit_v2(W, lr, ent, predict=False):
        k = int(np.searchsorted(ts, int(tms)))
        out[k] = bd * (xpx - epx) / epx * 100.0 - COST
    return out


def stats(v):
    a = np.asarray(v, float)
    if not a.size:
        return "n=0"
    return ("n=%-5d net=%+8.2f%%  mean=%+.4f%%  med=%+.4f%%  win=%.1f%%"
            % (a.size, a.sum(), a.mean(), np.median(a), 100.0 * (a > 0).mean()))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    rows = [r for r in build_chain(W, lr) if r[1] is not None]

    # dedup by entry bar, per arm, exactly as v2_walk_ad does
    A, B, seenA, seenB = [], [], set(), set()
    dirty_bars = set()
    for (ea, eb, es, bd, dirty) in rows:
        if ea not in seenA:
            seenA.add(ea); A.append((ea, es, bd))
            if dirty:
                dirty_bars.add(ea)
        if eb not in seenB:
            seenB.add(eb); B.append((eb, es, bd))
    pA, pB = pnl(W, lr, A), pnl(W, lr, B)

    # map each dirty trade to its arm-B counterpart
    pair = [(ea, eb) for (ea, eb, _, _, d) in rows if d and ea in pA and eb in pB]

    print("=== D3: fin_unlatch  BUILD (enter at first q15) vs SPEC (wait for the late line) ===")
    print("window %dd, cost %.2f%% RT, lr_exit_v2 raw (no strand_rescue)\n" % (SPAN_D, COST))
    print("ARM A  BUILD  all : %s" % stats(list(pA.values())))
    print("ARM B  SPEC   all : %s" % stats(list(pB.values())))

    clean = [v for k, v in pA.items() if k not in dirty_bars]
    print("\n-- cohort split (ARM A) --")
    print("  causal trades   : %s" % stats(clean))
    print("  CONTAMINATED    : %s   <- unreachable live" % stats([pA[k] for k in dirty_bars if k in pA]))

    if pair:
        a = np.array([pA[x] for x, _ in pair]); b = np.array([pB[y] for _, y in pair])
        print("\n-- the 217, entered EARLY (look-ahead) vs LATE (causal, spec) --")
        print("  early (A) : %s" % stats(a))
        print("  late  (B) : %s" % stats(b))
        print("  delta     : net %+.2f%%  mean %+.4f%%/trade   (n=%d matched)"
              % (b.sum() - a.sum(), b.mean() - a.mean(), len(pair)))
        print("\n  VERDICT: %s" % ("the late causal entry STILL PAYS -> the spec repair recovers these trades"
                                   if b.mean() > 0 else
                                   "the late causal entry LOSES -> the early edge was the look-ahead itself"))
    dev.disconnect()


if __name__ == "__main__":
    main()
