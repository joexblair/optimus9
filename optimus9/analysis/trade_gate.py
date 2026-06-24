"""
trade_gate.py (Joe 0624, #32 D) — the table-driven trade-gate cascade walker (BOILERPLATE).

Reads the ACTIVE gates from trade_gate / trade_gate_line (a gate is data; A/B via tg_active), walks
them in tg_seq order on the bias side within SEQ_CAP, and emits the gate-ok events + the s30-wob
entry — the same cascade that produces the bias-pk metric trades. Self-contained: each line's sign is
computed from its ic_pk (resolve config → f_bb/f_k → align_to_base → _sign), so a NEW gate = an
INSERT into the tables and zero code. The slight duplication of the engine's signs is deliberate
(Joe: easier to debug).
"""
import numpy as np
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from bias_machine import OOB_HI, OOB_LO, SEQ_CAP


class TradeGateWalker:
    def __init__(self, W, db):
        self._W = W
        self._db = db
        self._ts = W.ts
        self._n = len(W.ts)
        self._sign_cache = {}
        self._gates = self._load_gates()

    def _load_gates(self):
        gates = self._db.execute(
            'SELECT tg_pk, tg_seq, tg_name, tg_op FROM trade_gate WHERE tg_active=1 ORDER BY tg_seq', fetch=True)
        for g in gates:
            g['lines'] = [r['tgl_ic_pk'] for r in self._db.execute(
                'SELECT tgl_ic_pk FROM trade_gate_line WHERE tgl_tg_pk=%s', (g['tg_pk'],), fetch=True)]
        return gates

    def _sign(self, ic_pk):
        """Any line's OOB sign (+1 hi / -1 lo / 0 IB), base-aligned — replicates the engine's _line+_sign."""
        if ic_pk in self._sign_cache:
            return self._sign_cache[ic_pk]
        c = self._db.execute(
            '''SELECT ic_line_type lt, ic_src src, ic_bb_len, ic_bb_mult, ic_rsi_len, ic_stc_len,
                      ic_k_len, itf_seconds tf FROM vw_indicator_configs_live WHERE ic_pk=%s''',
            (ic_pk,), fetch=True)[0]
        fr = IC.resample(self._W.base, int(c['tf']))
        if c['lt'] == 'bb':
            v = IC.f_bb(IC.build_source(fr, c['src']), c['ic_bb_len'], float(c['ic_bb_mult']))
        else:
            v = IC.f_k(IC.build_source(fr, c['src']), c['ic_rsi_len'], c['ic_stc_len'], c['ic_k_len'])
        aligned = IC.align_to_base(v, fr, self._W.base)
        sign = np.where(aligned >= OOB_HI, 1, np.where(aligned <= OOB_LO, -1, 0))
        self._sign_cache[ic_pk] = sign
        return sign

    def _gate_ok(self, gate, lo, hi, es):
        """First base bar in [lo, hi) where the gate's lines (composed by tg_op) are OOB on side `es`."""
        sats = [(self._sign(ic)[lo:hi] == es) for ic in gate['lines']]
        sat = np.all(sats, axis=0) if gate['tg_op'] == 'AND' else np.any(sats, axis=0)
        w = np.where(sat)[0]
        return lo + int(w[0]) if len(w) else None

    def walk(self, t_up, bd, deadline=None):
        """One cascade from a bias pk update (t_up, bd). Returns (gate_oks, entry):
        gate_oks = [(t_ms, gate_name), …] · entry = (t_ms, side) of the s30-wob, or None."""
        es = -bd
        j0 = self._W._at(t_up); cap = min(j0 + SEQ_CAP, self._n)
        cursor, oks = j0, []
        for g in self._gates:
            ok = self._gate_ok(g, cursor, cap, es)
            if ok is None:
                return oks, None
            oks.append((int(self._ts[ok]), g['tg_name']))
            cursor = ok
        ET, EJ = self._W._wob_side(-bd)
        ei = int(np.searchsorted(ET, int(self._ts[cursor]), 'right'))
        if ei >= len(EJ):
            return oks, None
        et, ej = int(ET[ei]), int(EJ[ei])
        if ej > cap or (deadline is not None and et >= deadline):
            return oks, None
        return oks, (et, -bd)

    def events(self):
        """All cascade events over the pk updates: [(t_ms, kind, side), …].
        kind = 'gate:<name>' (gate satisfied, side None) | 'entry' (s30-wob entry, side ±1)."""
        ups = sorted((int(u['t']), 1 if u['call'] == 'BULL' else -1)
                     for u in self._W.signals() if u['call'] in ('BULL', 'BEAR'))
        out = []
        for i, (t_up, bd) in enumerate(ups):
            deadline = next((tt for tt, dd in ups[i + 1:] if dd != bd), None)   # next opposite pk
            oks, entry = self.walk(t_up, bd, deadline)
            out += [(t, 'gate:' + nm, -bd) for t, nm in oks]    # side = the cascade entry side (es)
            if entry:
                out.append((entry[0], 'entry', entry[1]))
        return out
