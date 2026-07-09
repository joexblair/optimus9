"""jig.py — the test-jig facade (Joe 0707). ONE object over a pinned window that exposes the STANDARD test
requirements, so analysis scripts stop hand-rolling what the engine already packages (the recurring drift tax:
fin_unlatch, s_qualify, lr_walk mfe_side, MAE-to-exit-vs-swing).

TWO namespaces — the split is the guardrail, not tidiness:
  jig.causal.*  — LIVE-LEGAL. Everything a strategy may use (klines, lines, finishers, arm/gate events, predict,
                  coarse-sample, curl). Every method DELEGATES to the real producer; it never re-implements logic.
  jig.score.*   — HARNESS / SCORING, NON-CAUSAL. find_pivots swings, lr_walk entry-quality (mae/mfe-to-swing +
                  mfe_side), report + pine emit. Reaching for jig.score.* inside a strategy is the tell you've
                  crossed into look-ahead.

DELEGATION RULE (absolute): the jig only CALLS existing producers. If something isn't packaged yet, split the
producer first, then expose it here — never fork the logic into the jig.
"""
import numpy as np
import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis.lr_v2 import s_qualify, s_qualify_parts, v2_arm, gate_open, _mage_rev, _rolling_any, _curl_detect
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from optimus9.compute.swing_detect import find_pivots, legs, swing_mask
from sweep_eval import BASE_BIAS


def _ffb(x):
    """Forward-then-back fill NaN (find_pivots stalls on the DEMA-warmup NaN; every caller cleans first)."""
    x = np.asarray(x, float).copy(); m = np.isfinite(x)
    if not m.any():
        return x
    idx = np.where(m, np.arange(len(x)), 0); np.maximum.accumulate(idx, out=idx)
    x = x[idx]; f = int(np.argmax(m)); x[:f] = x[f]
    return x


class _Causal:
    """LIVE-LEGAL reads — delegate to the real producers, honour value_mode (emerging = causal)."""
    def __init__(self, j):
        self.j = j

    def line(self, name):
        return np.asarray(self.j.W.line(name), float)                       # W.line = THE value_mode-honoured read

    def sign(self, name):
        v = self.line(name)                                                 # OOB sign: +1 hi / -1 lo / 0 in-band
        return np.where(v >= self.j.hi, 1, np.where(v <= self.j.lo, -1, 0))

    def finishers(self, tf, r_lb=None):
        """s{tf}a via the packaged s_qualify -> (qhi, qlo). qhi=short-side, qlo=long-side. r_lb defaults to
        cfg.{tf}r_lb (s15/s30); for tf without a DB lookback (e.g. s2) pass r_lb=."""
        lb = r_lb if r_lb is not None else getattr(self.j.cfg, '%sr_lb' % tf, None)
        if lb is None:
            raise ValueError("no r_lb for %s — pass r_lb=" % tf)
        return s_qualify(self.j.W, self.j.cfg, '%sm' % tf, '%sM' % tf, '%sr' % tf, lb)

    def finisher_pair(self, box=12, tf_a='s15', tf_b='s30', r_lb_a=None, r_lb_b=None):
        """CAUSAL co-occurrence event: at bar k, True iff BOTH s{tf_a}a and s{tf_b}a fired within the trailing box
        [k-box, k]. box in 5s bars (default 12 = 2x30s, the finisher tolerance). Returns (hi, lo) per-bar bools.
        This is the s30a+s15a EVENT — feed it to a consumer; don't re-bake the conjunction in a window inline."""
        ah, al = self.finishers(tf_a, r_lb_a); bh, bl = self.finishers(tf_b, r_lb_b)
        hi = _rolling_any(ah, box) & _rolling_any(bh, box)
        lo = _rolling_any(al, box) & _rolling_any(bl, box)
        return hi, lo

    def finisher_parts(self, tf, r_lb=None):
        """The per-bar COMPONENTS of s{tf}a (s_qualify_parts) for N-of-9: dict of per-side bools
        m_hi/lo, Moob_hi/lo (Mage OOB), Mrev_hi/lo (Mage reversed), rlb_hi/lo (r OOB within r_lb back).
        r_lb defaults to cfg.{tf}r_lb; pass r_lb= for a tf without a DB lookback (e.g. s2)."""
        lb = r_lb if r_lb is not None else getattr(self.j.cfg, '%sr_lb' % tf, None)
        if lb is None:
            raise ValueError("no r_lb for %s — pass r_lb=" % tf)
        return s_qualify_parts(self.j.W, self.j.cfg, '%sm' % tf, '%sM' % tf, '%sr' % tf, lb)

    def arms(self):
        return v2_arm(self.j.W, self.j.cfg)                                 # [(i, es, bd, cap, src)]

    def gates(self, arms=None):
        return gate_open(self.j.W, self.j.cfg, arms if arms is not None else self.arms())

    def predict(self, k, m, M):
        return predict_breach(k, m, M, self.j.hi, self.j.lo, FENCE_HI, FENCE_LO)

    def reversal(self, line, wob):
        """Boundary-agnostic reversal of a line (lr_v2._mage_rev): +1 up-turn / -1 down-turn confirmed after `wob`
        consecutive same-direction steps (wob<=0 = first slope-flip). Causal — fires from steps <= the bar."""
        return np.asarray(_mage_rev(np.asarray(line, float), wob))

    def coarse(self, name, seam_ms):
        """Sample an EMERGING line at every seam_ms boundary (e.g. 300000 = 5-min). -> (ts_c, vals)."""
        v = self.line(name); mask = (self.j.ts % seam_ms) == 0
        return self.j.ts[mask], v[mask]

    def curl(self, ts_c, c, direction, with_val=False):
        """Causal trough(direction +1)/peak(-1) on a coarse series: fires one seam AFTER the turn, past data only.
        Returns the set of 5s-timestamps at which a curl is confirmed. with_val=True -> {ts: turn_value} (the value at
        the turn point c[k-1]) so the consumer can gate a curl by which side of the board it turned on.
        Delegates to lr_v2._curl_detect — the single curl-detection impl (SRP; also used by lr_exit_v2)."""
        return _curl_detect(np.asarray(ts_c), np.asarray(c, float), direction, with_val)


class _Score:
    """HARNESS / SCORING — NON-CAUSAL. Never call these inside a strategy."""
    def __init__(self, j):
        self.j = j

    def swings(self, price=None, pct=None):
        p = _ffb(self.j.px if price is None else price)
        return find_pivots(p, pct if pct is not None else self.j.cfg.swing_pct)

    def legs(self, pivots=None, price=None):
        p = _ffb(self.j.px if price is None else price)
        return legs(p, pivots if pivots is not None else find_pivots(p, self.j.cfg.swing_pct))

    def entry_quality(self, entries):
        """Packaged entry-quality verdict (lr_walk): MAE/MFE from entry to the next FAVOURABLE swing (exit-INDEPENDENT)
        + mfe_side (did the trade open on the MFE side of the swing?). entries = [(trade_ms, es, bd, bar_idx)] ->
        [(trade_ms, dt, es, bd, mae, mfe, mfe_ok, mfe_side, price)]."""
        return lr_walk(self.j.W, entries, self.j.cfg)

    def table(self, rows, headers, row_fmt):
        print("  ".join(headers))
        for r in rows:
            print(row_fmt % tuple(r))

    def emit_labels(self, labels, path, title):
        """Pine emit: labels = [{ts:int-ms, y:float, text:str, green:bool, up:bool}]. green->green/red bg-tone,
        up->style_label_up/down. Function-wrapped arrays + barstate.islast loop (TV op-limit safe)."""
        T = [int(l['ts']) for l in labels]; Y = [round(float(l['y']), 6) for l in labels]
        TXT = [str(l['text']) for l in labels]
        UP = ['true' if l.get('up') else 'false' for l in labels]
        GRN = ['true' if l.get('green') else 'false' for l in labels]
        ai = lambda v: "array.from(" + ", ".join(str(int(z)) for z in v) + ")" if v else "array.new_int(0)"
        af = lambda v: "array.from(" + ", ".join(str(z) for z in v) + ")" if v else "array.new_float(0)"
        as_ = lambda v: "array.from(" + ", ".join('"%s"' % z for z in v) + ")" if v else "array.new_string(0)"
        ab = lambda v: "array.from(" + ", ".join(v) + ")" if v else "array.new_bool(0)"
        body = ('''//@version=5
indicator("%s", overlay = true, max_labels_count = 500)''' % title + '''
f_t()   => %s
f_y()   => %s
f_txt() => %s
f_up()  => %s
f_grn() => %s
if barstate.islast
    tt = f_t()
    yy = f_y()
    tx = f_txt()
    up = f_up()
    gr = f_grn()
    for i = 0 to array.size(tt) - 1
        col = array.get(gr, i) ? color.new(color.green, 15) : color.new(color.red, 15)
        stl = array.get(up, i) ? label.style_label_up : label.style_label_down
        label.new(array.get(tt, i), array.get(yy, i), array.get(tx, i), xloc = xloc.bar_time, color = col, style = stl, textcolor = color.white, size = size.normal)
''' % (ai(T), af(Y), as_(TXT), ab(UP), ab(GRN)))
        open(path, "w").write(body)
        return len(labels)


class Jig:
    """Pinned-window test bench. Build once, reuse across a script. `overrides` = BiasWindow line_overrides for
    non-DB lines (e.g. {'s10r': (600, ('k',6,6,5,'hl2'), 'emerging')})."""
    def __init__(self, end_ms, hours=48, warmup=24, overrides=None, dev=None, bias=None):
        self._owns_dev = dev is None
        self.dev = dev or DatabaseManager(**get_db_config())
        if self._owns_dev:
            self.dev.connect()
        self.cfg = lr_config(self.dev)
        self.hi, self.lo = self.cfg.hi, self.cfg.lo
        self.end_ms = int(end_ms)
        bcfg = bias if bias is not None else bm.BiasConfig(**BASE_BIAS)
        self.W = bm.BiasWindow(self.dev, self.end_ms, lookback=hours + warmup, warmup=warmup,
                               cfg=bcfg, line_overrides=overrides or {})
        self.ts = np.asarray(self.W.ts); self.px = np.asarray(self.W.px, float); self.n = len(self.ts)
        self.hours = hours
        self.causal = _Causal(self)
        self.score = _Score(self)

    def close(self):
        if self._owns_dev:
            self.dev.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
