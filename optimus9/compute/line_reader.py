"""line_reader — turn a resolved line config into VALUES. Nothing else. (0717)

SRP companion to line_config. That module answers *what an indicator config is* and *how to obtain
one* (LineStore); this one answers *how to read it into a value series* — resample, build, align,
and the emerging/closed dispatch. Both jobs used to live inside bias_machine.BiasWindow; the config
half left in 0714 (LineStore), the value half stayed behind until now.

bias_machine CONSUMES lines (anchor/floater, pk verdict, entry gating). It should not also BUILD them.
BiasWindow now holds a LineReader and delegates every _raw/_aligned/_line/_line_emerging/line call to it,
so the public read surface (W.line / C.line) is unchanged.

ANCHOR (the reason this refactor surfaced): higher-TF bars are resampled on a grid. `epoch` (the raw
f_*_lookahead default) aligns bar boundaries to the unix epoch; `midnight` aligns them to UTC midnight,
which is what TradingView plots. They diverge on TFs that do NOT divide a day (1440 min) — 7, 11, 13,
14, 17, 19, 21, 22, 23, 25, 26, ... — and agree on day-divisors (30s, 1m, 2m, 5m, 15m, 30m, ...). The
reader anchors on `midnight` for every TF: correct on TV for all, identical to epoch where they coincide.
"""
from optimus9.compute.indicator_computer import IndicatorComputer as IC


class LineReader:
    """Reads a line config (via LineStore) into a value series against a pinned base tape.

    store       — LineStore: name -> (tf_seconds, cfg-tuple, value_mode).
    base        — the full 5s grid every line aligns back onto.
    lbase       — the tape lines COMPUTE on (== base, or the event tape when filler-invisible).
    evt_remap   — full-grid -> last-real-bar index map (filler-invisible), or None.
    anchor      — resample base for the higher-TF grid ('midnight' = TV-aligned, the correct default).
    force_emerging — read every line emerging regardless of its DB value_mode (was the
                     `W._line = W._line_emerging` monkey-patch; now a flag, no private reassignment)."""

    def __init__(self, store, base, lbase, evt_remap, anchor='midnight', force_emerging=False):
        self._store = store
        self._base = base
        self._lbase = lbase
        self._evt_remap = evt_remap
        self._anchor = anchor
        self.force_emerging = force_emerging

    # ── closed (base-aligned) ──
    def _raw(self, tf_sec, cfg):
        fr = IC.resample(self._lbase, tf_sec, self._anchor)   # event tape (filler-invisible) → align_to_base forward-fills onto the full grid
        if cfg[0] == 'bb':
            v = IC.f_bb(IC.build_source(fr, cfg[3]), cfg[1], cfg[2])
        else:
            v = IC.f_k(IC.build_source(fr, cfg[4]), cfg[1], cfg[2], cfg[3])
        return v, fr

    def _aligned(self, tf_sec, cfg):
        v, fr = self._raw(tf_sec, cfg)
        return IC.align_to_base(v, fr, self._base)

    def closed(self, ind_name):
        """Base-aligned line from its LIVE config (vw_indicator_configs_live)."""
        return self._aligned(*self._store.resolve(ind_name))

    # ── emerging (developing, one value per 5s bar against the forming higher-TF bar) ──
    def emerging(self, ind_name, anchor=None):
        tf_sec, cfg = self._store.resolve(ind_name)
        anc = anchor if anchor is not None else self._anchor
        b = self._lbase                                       # event tape when filler-invisible
        if cfg[0] == 'bb':
            out = IC.f_bb_lookahead(b, tf_sec, cfg[1], cfg[2], cfg[3], anchor=anc)
        else:
            out = IC.f_k_lookahead(b, tf_sec, cfg[3], cfg[1], cfg[2], cfg[4], anchor=anc)
        return out[self._evt_remap] if self._evt_remap is not None else out   # remap event grid → full 5s grid

    # ── THE value_mode-honouring read (#42) — the one place every consumer should land ──
    def line(self, ind_name):
        """'emerging' → developing (f_*_lookahead); 'closed' → base-aligned. The toggle lives in the DB
        (value_mode), never baked into the caller. force_emerging overrides it (test/sweep hook)."""
        emerging = self.force_emerging or self._store.value_mode(ind_name) == 'emerging'
        return self.emerging(ind_name) if emerging else self.closed(ind_name)
