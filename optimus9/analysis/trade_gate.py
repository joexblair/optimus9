"""
trade_gate.py (Joe 0624, #32 D) — the table-driven trade-gate cascade walker (BOILERPLATE).

Reads the ACTIVE gates from trade_gate / trade_gate_line (a gate is data; A/B via tg_active), walks
them in tg_seq order on the bias side within SEQ_CAP, and emits the gate-ok events + the s30-wob
entry — the same cascade that produces the bias-pk metric trades. Each gate line's sign comes from
W.line (#42, 0627) — the one value_mode-honouring reader, config from vw_indicator_configs_live — so
emerging gates read REALTIME and a NEW gate = an INSERT into trade_gate/trade_gate_line, zero code.
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
        """A gate line's OOB sign (+1 hi / -1 lo / 0 IB), base-aligned — via W.line (#42), which honours
        the line's DB value_mode: emerging gates read REALTIME (the developing bar, validated 99.89% vs TV),
        closed gates read the aligned closed bar. The toggle lives in vw_indicator_configs_live, not here."""
        if ic_pk in self._sign_cache:
            return self._sign_cache[ic_pk]
        name = self._db.execute('SELECT ind_name FROM vw_indicator_configs_live WHERE ic_pk=%s',
                                 (ic_pk,), fetch=True)[0]['ind_name']
        aligned = self._W.line(name)                              # value_mode-honoured, config from the view
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

    def cascade(self, bias_arr):
        """DECOUPLED lp cascade (alchemy BRD 0626) — NOT pk-triggered. The pk-walked `events()` could
        only ride a pk-driven bias; this rides the COMPOSITE bias (bias sets the scene, cascade rides).

        Walk the window: at each s6m OOB-ONSET (IB/other-side → es), walk the remaining gates
        (xm45a, gcs15a) in tg_seq within SEQ_CAP, then the xm45min wob (the reversal turn off the OOB
        extreme). The entry fires ONLY if `bias_arr` (composite BiasState dir per base bar) permits the
        direction. Polarity: OOB-low (es=-1) → LONG (+1, needs bias +1); OOB-high (es=+1) → SHORT.
        MULTIPLE entries per s6m run (Joe 0627): after each entry the cascade RE-ARMS — re-walks the
        gate-chain from past the entry and fires again on the next gate-completion + wob, while s6m holds.
        Every re-completion (e.g. s30r re-breaching) is a fresh candidate; the gate machine downstream
        singles out the winners (≥1 of a run's entries will stop — that's the feedback signal).
        Returns [(t_ms, kind, side)]: 'pl_cas_start' (s6m onset, side=es, ONCE per run) | 'pl_cas_end'
        (each entry, side=-es). s6m must be tg_seq 1. The re-arm/wob LINE is DB-selected (lp_cascade_rearm_ic,
        the UI dropdown; default xm45m) and its wob length is that line's own ic_wobble (emerging)."""
        g = self._gates
        s6 = self._sign(g[0]['lines'][0])                         # s6m OOB sign per base bar
        ra = self._db.execute(                                    # the re-arm / wob line — DB-selected (UI dropdown)
            '''SELECT CONCAT(s.is_prefix, itf.itf_label, il.il_suffix) nm, ic.ic_wobble
               FROM indicator_configs ic JOIN indicator_series s ON s.is_pk = ic.ic_is_pk
               JOIN indicator_lines il ON il.il_pk = ic.ic_il_pk
               JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk
               WHERE ic.ic_pk = (SELECT val FROM lp_config WHERE name = 'lp_cascade_rearm_ic')''', fetch=True)[0]
        if ra['ic_wobble'] is None or int(ra['ic_wobble']) < 1:   # the entry wob never fires at n<1 (silent no-trades)
            raise ValueError(f"cascade re-arm line {ra['nm']} needs ic_wobble >= 1 (set it in the ic fold) — "
                             f"the entry wob is the trigger; 0/null means it never fires")
        N = int(ra['ic_wobble'])                                  # the re-arm line's own wobble (per-line ic_wobble)
        xm = self._W._line_emerging(ra['nm'])                     # emerging re-arm line (5s) — default xm45m
        wob = IC.wobble_slayer(xm, N, OOB_HI, OOB_LO, anchored=True, strict=True)
        out, i, n = [], 1, self._n
        while i < n:
            if s6[i] != 0 and s6[i] != s6[i - 1]:                 # s6m OOB-onset
                es = int(s6[i])
                run_end = i                                       # (b) cascade is ARMED while s6m holds OOB
                while run_end + 1 < n and s6[run_end + 1] == es:  # ...not capped 21min from onset
                    run_end += 1
                cap = run_end + 1; entry = -es; cursor = i; started = False
                while cursor < cap:                               # RE-ARM loop — multiple entries per run
                    c = cursor; ok_all = True
                    for gate in g[1:]:                            # re-walk s30a, xm45a, gcs15a from cursor
                        ok = self._gate_ok(gate, c, cap, es)
                        if ok is None:
                            ok_all = False; break
                        c = ok
                    if not ok_all:
                        break                                     # no further gate-chain completion this run
                    wj = next((j for j in range(c, cap) if wob[j] == entry), None)   # next reversal turn
                    if wj is None:
                        break                                     # no further wob
                    if bias_arr[wj] == entry:                     # BIAS GATE — composite bias permits
                        if not started:
                            out.append((int(self._ts[i]), 'pl_cas_start', es)); started = True
                        out.append((int(self._ts[wj]), 'pl_cas_end', entry))
                    cursor = wj + 1                               # re-arm past this entry
                i = run_end
            i += 1
        return out

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
