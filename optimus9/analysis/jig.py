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
from optimus9.analysis.lr_v2 import (s_qualify, s_qualify_parts, v2_arm, gate_open, _mage_rev, _rolling_any,
                                     _curl_detect, fin_unlatch_nof9, fin_box_qualified)
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from optimus9.compute.line_config import KLine, BBLine, override as _override   # noqa: F401
from optimus9.compute.swing_detect import find_pivots, legs, swing_mask
from sweep_eval import BASE_BIAS


def kline(name, tf_min, *, k_len, rsi, stc, src='close', value_mode='emerging'):
    """A K-line override, BY NAME. The only sanctioned way to build one — you cannot transpose it.

        overrides = {**kline('s45r', 45, k_len=7, rsi=5, stc=7, src='ohlc4')}
        with Jig(end_ms, hours=24, overrides=overrides) as j: ...

    Joe's notation is k_len | rsi | stc | src; the DB tuple is ('k', rsi, stc, k_len, src) — REVERSED, and
    transposing it is SILENT (the line still computes, and is a different line: TV MAE 0.03 vs 9.33).
    optimus9.compute.line_config is the only module that knows that. Nothing else may hand-build a tuple."""
    return {name: _override(tf_min * 60, KLine(k_len=k_len, rsi=rsi, stc=stc, src=src), value_mode)}


def bbline(name, tf_min, *, length, mult, src='close', value_mode='emerging'):
    """A Bollinger-position override, BY NAME. Notation and tuple agree here (length|mult|src), but this is
    the one door so a caller never has to know which configs are safe to hand-build and which are not."""
    return {name: _override(tf_min * 60, BBLine(length=length, mult=mult, src=src), value_mode)}


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

    def fin_unlatch_6of9(self, arm, cap, side, q15, q30, sets=(('gcs5', 29), ('s15', None), ('s30', None)),
                         N=6, box_lb=None, tol=None, bind_tol=6, anchor='breach'):
        """Two-stage arm-unlatch entry (Joe 0710):
          QUALIFIER  fin_box_qualified — s15a AND s30a in the box [arm-box_lb, arm+tol]. Validates the trade.
          TRIGGER    fin_unlatch_nof9 — the >=N-of-9 confluence at/after the arm, bound within bind_tol.
        gcs5a is only in the TRIGGER (preens the entry delay), never the qualifier.  Returns the trade bar or None.
        sets = ((set_name, r_lb_override), ...); r_lb None -> cfg.{set}r_lb.  box_lb/tol None -> cfg.fin_lb/fin_fwd."""
        blb = self.j.cfg.fin_lb if box_lb is None else box_lb
        tl = self.j.cfg.fin_fwd if tol is None else tol
        if not fin_box_qualified(q15, q30, arm, blb, tl):          # QUALIFIER owns box_lb/tol
            return None
        parts = {s: self.finisher_parts(s, r_lb=rlb) for (s, rlb) in sets}
        return fin_unlatch_nof9(parts, arm, cap, side, N=N, bind_tol=bind_tol, anchor=anchor)  # cap = the arm cancel

    def arms(self):
        return v2_arm(self.j.W, self.j.cfg)                                 # [(i, es, bd, cap, src)]

    def gates(self, arms=None):
        return gate_open(self.j.W, self.j.cfg, arms if arms is not None else self.arms())

    def predict(self, k, m, M, tol=0.0):
        return predict_breach(k, m, M, self.j.hi, self.j.lo, FENCE_HI, FENCE_LO, tol)

    def predict_set(self, prefix, tol=0.0, maj='M'):
        """Predicted-breach direction for a whole line SET, by name: predict_set('s3') reads s3r/s3m/s3M.
        maj='Mage' for the sets whose Major is named s{n}Mage. `tol` is the sweepable value-point allowance
        (0.0 = spec).  Ungated — the "test while the mini is OOB" gate is the CONSUMER's (see mini_oob);
        lr_v2.gate_signals keeps them separate for the same reason."""
        return self.predict(self.line(prefix + 'r'), self.line(prefix + 'm'),
                            self.line(prefix + maj), tol)

    def mini_oob(self, prefix):
        """+1/-1/0 OOB sign of the set's mini — the gate lr_v2.gate_signals applies to a prediction
        ('test r predict while s{n}m is OOB'). Kept separate from predict_set (SRP)."""
        return self.sign(prefix + 'm')

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

    def seam_prev(self, name, seam_ms):
        """Per-5s-bar: the value of `name` at the most recent seam boundary STRICTLY BEFORE this bar.
        Causal (never reads the current seam's own sample). The seam grid is global (ts % seam_ms == 0), so a
        bar at the start of a coarse bar reads the last seam of the PREVIOUS coarse bar — no intra-bar gap and
        no special case at the open (Joe 0713).

        Companion to coarse(): coarse() gives the seam samples, seam_prev() holds the last one per bar so a
        consumer can compare a LIVE value against where the line stood one seam ago."""
        v = self.line(name); ts = self.j.ts
        seams = np.flatnonzero((ts % seam_ms) == 0)
        if not len(seams):
            return np.full(len(ts), np.nan)
        i = np.searchsorted(ts[seams], ts, side='left') - 1        # last seam with ts_seam < ts[k]
        out = np.full(len(ts), np.nan)
        ok = i >= 0
        out[ok] = v[seams[i[ok]]]
        return out

    def cross(self, a, b, grid_ms):
        """Causal line-vs-line CROSS on a grid: +1 where `a` crossed ABOVE `b`, -1 where it crossed BELOW,
        comparing each grid boundary to the previous one. Non-grid bars are 0.

        Distinct from sign() (a-vs-BOUNDARY) and reversal() (a-vs-its-own-slope) — this is a-vs-ANOTHER-LINE.
        `grid_ms` is the evaluation cadence and is a sweepable knob: a coarser grid filters 5s chop out of the
        cross moment (Joe 0713: "fire every 30 seconds — this improves the timing of the s1m x s1r moment").
        a/b are line NAMES or value arrays."""
        av = self.line(a) if isinstance(a, str) else np.asarray(a, float)
        bv = self.line(b) if isinstance(b, str) else np.asarray(b, float)
        ts = self.j.ts
        g = np.flatnonzero((ts % grid_ms) == 0)
        out = np.zeros(len(ts), int)
        if len(g) < 2:
            return out
        d = av[g] - bv[g]
        prev, cur = d[:-1], d[1:]
        out[g[1:]] = np.where((prev <= 0) & (cur > 0), 1, np.where((prev >= 0) & (cur < 0), -1, 0))
        return out

    def seam_since(self, cond, seam_ms):
        """Causal: at every 5s bar, True iff `cond` held at ANY bar since the CURRENT seam bucket opened
        (inclusive of the seam bar and of now). Resets at each seam.

        The running-extreme gate (Joe 0713: "test at the seams, but between the seams collect the min/max").
        seam_hold() samples the condition AT the seam and freezes it, so a breach landing mid-bucket is
        invisible until the next seam — up to a full seam-width late (5 min on TF20/4; it dropped the 18:42
        and 10:22 turns). seam_since() instead asks whether the line has touched the state at any point in
        the bucket so far, so the gate answers within one bar of the breach and still resets on the seam.

        cond is any per-bar bool: pass (sign(name) == es) and this IS the running max/min test."""
        c = np.asarray(cond, bool)
        ts = self.j.ts
        bucket = ts // int(seam_ms)                                  # which seam interval each bar is in
        new = np.concatenate([[True], bucket[1:] != bucket[:-1]])    # first bar of each bucket
        # running OR within the bucket: cumulative count of True, minus the count at the bucket's start
        cc = np.cumsum(c)
        base_idx = np.maximum.accumulate(np.where(new, np.arange(len(c)), 0))
        base = cc[base_idx] - c[base_idx]                            # count strictly before the bucket start
        return (cc - base) > 0

    def reset_since(self, event, reset):
        """Causal: True at bar k iff `reset` has occurred at or after the most recent `event` — i.e. the
        thing has been RE-ARMED since it last fired. True before any event ever occurs.

        The re-fire guard (Joe 0714): an r that has completed an OOB excursion on a side must return to
        neutral ground before it may be counted as setting up for that SAME side again. Without it, the
        mini's next dive re-predicts a breach the r has just finished making — s19r spent 87 min OOB-low,
        left at 10:26, and was re-predicted low at 10:47 from 28.4, never having crossed 50.

        event = the OOB-on-es state.  reset = the midline cross (or whatever neutral test the caller wants)."""
        e = np.asarray(event, bool)
        r = np.asarray(reset, bool)
        n = len(e)
        idx = np.arange(n)
        last_e = np.maximum.accumulate(np.where(e, idx, -1))
        last_r = np.maximum.accumulate(np.where(r, idx, -1))
        return last_r >= last_e

    def hold_at_start(self, episode, sample):
        """Causal: while `episode` is True, carry the value `sample` held on the bar the episode BEGAN.
        False outside the episode, and False for an episode already running at the tape head.

        'Was it already true when the thing started?' (Joe 0713: "previously predicted = was predicted when
        s20m went OOB"). Not a rolling memory — the state is sampled ONCE, at the breach, and latched for
        that breach's life. Reads only the episode's own start bar, so it is causal from the start bar on."""
        e = np.asarray(episode, bool)
        s = np.asarray(sample, bool)
        start = e & ~np.concatenate([[False], e[:-1]])          # IB->OOB transition
        idx = np.where(start, np.arange(len(e)), -1)
        idx = np.maximum.accumulate(idx)                        # most recent start at/before each bar
        out = np.zeros(len(e), bool)
        ok = e & (idx >= 0)
        out[ok] = s[idx[ok]]
        return out

    def grid_any(self, cond, grid_ms, n):
        """Causal: at each grid boundary, True iff `cond` held at ANY of the last `n` grid samples
        (inclusive of this one). Non-grid bars are False.

        'WAS x and now y' (Joe 0713) — a fast line can leave a state in the same step that produces the
        event you want to catch (s1m drops out of OOB on the very sample it crosses s1r), so the state test
        must look back a sample, not read the event bar. `n` is the sweepable memory: n=1 is 'is', n=2 is
        'is or was one sample ago'."""
        c = np.asarray(cond, bool)
        ts = self.j.ts
        g = np.flatnonzero((ts % grid_ms) == 0)
        out = np.zeros(len(ts), bool)
        if not len(g):
            return out
        cg = c[g]
        acc = np.zeros(len(g), bool)
        for i in range(int(n)):
            acc |= np.concatenate([np.zeros(i, bool), cg[:len(cg) - i]]) if i else cg
        out[g] = acc
        return out

    def seam_hold(self, cond, seam_ms):
        """Per-5s-bar: a per-bar condition SAMPLED at each seam boundary and HELD until the next one.
        'Tested at each intra-bar seam' (Joe 0713) — the gate has a value between seams, and that value is the
        one the seam last saw. Causal. `cond` = any per-bar array (bool/int/float)."""
        c = np.asarray(cond)
        ts = self.j.ts
        seams = np.flatnonzero((ts % seam_ms) == 0)
        if not len(seams):
            return np.zeros(len(ts), c.dtype)
        i = np.searchsorted(ts[seams], ts, side='right') - 1        # last seam with ts_seam <= ts[k]
        out = np.zeros(len(ts), c.dtype)
        ok = i >= 0
        out[ok] = c[seams[i[ok]]]
        return out


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

    def emit_bgcolor(self, streams, path, title, opacity=0, notes=None):
        """Pine bgcolor overlay from named 5s-timestamp streams (the array-bgcolor pattern — arm_gate_emit,
        lp_cascade_emit, og_arm_emit all hand-rolled this; now it lives once here).

        streams = [{'name': str, 'ts': [int-ms...], 'color': 'color.green'}, ...].
        Order is PRIORITY: later streams paint over earlier ones on a shared bar. Each stream gets an
        input.bool toggle. Arrays are chunked at 400 (TV op-limit) and looked up with array.binary_search
        on `time`, so the whole thing evaluates on the last bar only.
        Returns the total number of painted bars."""
        arr = lambda v: ("array.from(" + ", ".join(str(int(z)) for z in v) + ")") if v else "array.new_int(0)"

        def emit_arr(nm, vals):
            vals = sorted(set(int(v) for v in vals))                 # binary_search needs sorted, unique
            if len(vals) <= 400:
                return "f_%s() =>\n    %s" % (nm, arr(vals)), "%s = f_%s()" % (nm, nm), len(vals)
            chunks = [vals[i:i + 400] for i in range(0, len(vals), 400)]
            d = "\n".join("f_%s_%d() =>\n    %s" % (nm, i, arr(c)) for i, c in enumerate(chunks))
            d += "\nf_%s() =>\n    a = f_%s_0()\n" % (nm, nm)
            d += "".join("    array.concat(a, f_%s_%d())\n" % (nm, i) for i in range(1, len(chunks)))
            d += "    a"
            return d, "%s = f_%s()" % (nm, nm), len(vals)

        defs, calls, toggles, paints, total = [], [], [], [], 0
        for s in streams:
            label = s['name']
            nm = 's_' + label                                        # prefix: never collide with a Pine keyword
            d, c, cnt = emit_arr(nm, s['ts']); total += cnt
            defs.append(d); calls.append(c)
            toggles.append('show_%s = input.bool(true, "%s (%s)")' % (nm, label, s['color'].split('.')[-1]))
            paints.append('if show_%s and array.binary_search(%s, time) >= 0\n'
                          '    bg := color.new(%s, %d)' % (nm, nm, s['color'], opacity))
        # `notes` = the config the emit was BUILT from, carried into the .pine as a comment block (Joe 0713).
        # The chart is read hours later, often beside a newer run — a pine that cannot say which knobs
        # produced it is a human-error trap. The header travels with the artefact.
        hdr = ''
        if notes:
            lines = notes.split('\n') if isinstance(notes, str) else list(notes)
            hdr = "\n".join('// ' + ln for ln in lines) + "\n"
        body = ('//@version=5\n' + hdr + 'indicator("%s", overlay = true)\n' % title
                + "\n".join(toggles) + "\n" + "\n".join(defs) + "\n" + "\n".join(calls)
                + "\nbg = color(na)\n" + "\n".join(paints) + "\nbgcolor(bg)\n")
        open(path, "w").write(body)
        return total


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
