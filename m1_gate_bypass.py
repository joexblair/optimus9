"""m1_gate_bypass.py — does M1 (fin_unlatch) fire without the s3s4 gate?

Joe's spec sec.4: "Gate open -> FINISHERS." The finisher may only trigger after the s3s4 gate opens, and the
gate can only open on an arm. The build (v2_cascade) instead tries fin_unlatch FIRST, off the ARM bar, with no
gate reference at all, and only falls through to the gate-dependent fin_gate when fin_unlatch returns None:

    tk = fin_unlatch(q15, q30, i, cap, ...); path = 'M1'   # M1: no gate
    if tk is None and o is not None:
        tk = fin_gate(q15, q30, gb, cap);    path = 'M2'   # M2 only if M1 didn't fire AND gate opened

So M1 both BYPASSES and PRE-EMPTS the gate. This script quantifies the bypass, three ways:
  no_gate      M1 traded and the arm's gate NEVER opened          -> off-spec: no gate existed
  before_gate  M1 traded at tk < gate_bar                         -> off-spec: traded ahead of the gate
  after_gate   M1 traded at tk >= gate_bar                        -> spec-compatible ordering
and reports how many M1 trades PRE-EMPTED an M2 that would otherwise have fired.

Read-only. Run:  python3 m1_gate_bypass.py"""
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_arm, arm_delay, gate_open, s_qualify, fin_unlatch, fin_gate

SPAN_D = 42


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000) - 3_600_000
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)

    setups = v2_arm(W, lr)
    if lr.arm_bigleg:
        setups = arm_delay(W, lr, setups)
    opens = {o[0]: o for o in gate_open(W, lr, setups)}
    q15h, q15l = s_qualify(W, lr, 's15m', 's15M', 's15r', lr.s15r_lb)
    q30h, q30l = s_qualify(W, lr, 's30m', 's30M', 's30r', lr.s30r_lb)

    n_arms = len(setups)
    no_gate = before_gate = after_gate = 0
    preempt = 0                 # M1 fired AND an M2 would also have fired for that arm
    m2_only = 0
    lead = []                   # bars by which M1 beat the gate
    for (i, es, bd, cap, src) in setups:
        q15, q30 = (q15h, q30h) if es == 1 else (q15l, q30l)
        o = opens.get(i)
        gb = o[3] if o else None
        tk = fin_unlatch(q15, q30, i, cap, lr.fin_lb, lr.fin_fwd)
        if tk is None:
            if o is not None and fin_gate(q15, q30, gb, cap) is not None:
                m2_only += 1
            continue
        if gb is None:
            no_gate += 1
        elif tk < gb:
            before_gate += 1; lead.append(gb - tk)
        else:
            after_gate += 1
        if o is not None and fin_gate(q15, q30, gb, cap) is not None:
            preempt += 1

    m1 = no_gate + before_gate + after_gate
    print("=== M1 (fin_unlatch) vs the s3s4 gate — %dd, %d arms ===\n" % (SPAN_D, n_arms))
    print("M1 trades (pre-dedup)      : %d" % m1)
    print("  no_gate     (gate NEVER opened for that arm) : %5d  (%.1f%%)  <- off-spec" % (no_gate, 100.0 * no_gate / max(m1, 1)))
    print("  before_gate (traded AHEAD of the gate open)  : %5d  (%.1f%%)  <- off-spec" % (before_gate, 100.0 * before_gate / max(m1, 1)))
    print("  after_gate  (gate opened first)              : %5d  (%.1f%%)  <- spec-compatible order" % (after_gate, 100.0 * after_gate / max(m1, 1)))
    off = no_gate + before_gate
    print("\nOFF-SPEC M1 trades: %d / %d  (%.1f%% of M1)" % (off, m1, 100.0 * off / max(m1, 1)))
    if lead:
        L = np.array(lead)
        print("  when it beat the gate, it led by (5s bars): p50=%d p90=%d max=%d  (=%ds / %ds / %ds)"
              % (int(np.percentile(L, 50)), int(np.percentile(L, 90)), L.max(),
                 int(np.percentile(L, 50)) * 5, int(np.percentile(L, 90)) * 5, L.max() * 5))
    print("\nM1 PRE-EMPTED an M2 that would have fired : %d" % preempt)
    print("M2-only arms (M1 silent, gate fired M2)   : %d" % m2_only)
    dev.disconnect()


if __name__ == "__main__":
    main()
