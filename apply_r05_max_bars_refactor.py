#!/usr/bin/env python3
"""
apply_r05_max_bars_refactor.py — single-shot in-place editor.

Applies the r05 260521 refactor to existing files:
  • outlier_reporter.py    — fix dropped pko_result column reference
  • report_exporter.py     — remove dropped columns from SELECT
  • swing_analyzer.py      — use OutcomeWalker, drop max_bars cap
  • fold_manager.py        — use KlineLoader + OutcomeWalker, drop _MAX_BARS
  • report_manager.py      — use KlineLoader, drop max_bars arg
  • optimizer_runner.py    — pass timestamps to analyze()
  • analyze_manager.py     — _walk_equity splits resolved/unrealized
  • validate_centroid.py   — mirror analyze_manager change

The two new files (outcome_walker.py, kline_loader.py) are assumed already
placed in optimus9/compute/ and optimus9/db/ respectively.

Idempotent: each edit checks for either the old-form text (transforms) or
the new-form text (skips with "already applied"). Safe to re-run.

Run from repo root:
    python3 apply_r05_max_bars_refactor.py

Pass --dry-run to see what would change without writing:
    python3 apply_r05_max_bars_refactor.py --dry-run
"""

import argparse
import pathlib
import sys


# ─── Edit helpers ───────────────────────────────────────────────────────────

class Edit:
    """One find-and-replace operation against one file."""

    def __init__(self, path: str, name: str, old: str, new: str,
                 skip_if_contains: str = None) -> None:
        self.path = pathlib.Path(path)
        self.name = name
        self.old  = old
        self.new  = new
        # If the file already contains this string, the edit is considered
        # done. Defaults to a distinctive substring of `new`.
        self.skip_if_contains = skip_if_contains

    def apply(self, dry_run: bool) -> str:
        """Apply this edit; return status string for the summary."""
        if not self.path.exists():
            return f'✗ MISSING  {self.path}'

        src = self.path.read_text()

        # Check idempotency: if the new content is already present, skip
        marker = self.skip_if_contains or self.new[:60].strip()
        if marker in src:
            return f'⊝ skip     {self.name} (already applied)'

        if self.old not in src:
            return f'⚠ NOMATCH  {self.name} (old text not found)'

        new_src = src.replace(self.old, self.new, 1)
        if dry_run:
            return f'· dry-run  {self.name}'

        self.path.write_text(new_src)
        return f'✓ applied  {self.name}'


# ─── The edits ──────────────────────────────────────────────────────────────

EDITS = []

# 01 — outlier_reporter.py: fix dropped pko_result column ref
EDITS.append(Edit(
    'optimus9/analysis/outlier_reporter.py',
    '01 outlier_reporter: drop pko_result ref',
    old="                      SUM(pko_result = 'won') AS won,\n",
    new=(
        '                      -- pko_result column was dropped; derive \'won\' from\n'
        '                      -- max_profit_pct vs profit_zone (hardcoded 0.60 here\n'
        '                      -- because OutlierReporter is currently orphaned).\n'
        '                      SUM(o.pko_max_profit_pct >= 0.60) AS won,\n'
    ),
    skip_if_contains='SUM(o.pko_max_profit_pct >= 0.60) AS won',
))

# 02 — report_exporter.py: remove dropped columns from SELECT
EDITS.append(Edit(
    'optimus9/orchestration/report_exporter.py',
    '02 report_exporter: drop pko_result + pko_stop_pct from SELECT',
    old='                      o.pko_bars_to_max_profit, o.pko_result, o.pko_stop_pct\n',
    new='                      o.pko_bars_to_max_profit\n',
    skip_if_contains='o.pko_bars_to_max_profit\n               FROM pk_signals',
))

# 03 — swing_analyzer.py: full body replacement (multiple edits in sequence)
EDITS.append(Edit(
    'optimus9/compute/swing_analyzer.py',
    '03a swing_analyzer: add OutcomeWalker import',
    old='from logger import get_logger\n',
    new=(
        'from logger import get_logger\n'
        '\n'
        '# ── cross-package imports ─────────────────────────────────────────────────\n'
        'from .outcome_walker import walk_outcome\n'
    ),
    skip_if_contains='from .outcome_walker import walk_outcome',
))

EDITS.append(Edit(
    'optimus9/compute/swing_analyzer.py',
    '03b swing_analyzer: replace __init__ + analyze + _evaluate',
    old=(
        '    def __init__(self, stop_pct: float = 0.33, max_bars: int = 1080) -> None:\n'
        '        # r04: dropped drag_pct, profit_long, profit_short — classification\n'
        '        # moved to AnalyzeManager (max_profit_pct >= tc.tc_profit_zone).\n'
        '        self._stop_long  = 1.0 - stop_pct / 100.0\n'
        '        self._stop_short = 1.0 + stop_pct / 100.0\n'
        '        self._stop_pct   = stop_pct\n'
        '        self._max_bars   = max_bars\n'
        '        self._log        = get_logger(self.__class__.__name__)\n'
        '\n'
        '    def analyze(self, signals: list, close: np.ndarray) -> list:\n'
        '        return [self._evaluate(sig, close) for sig in signals]\n'
        '\n'
        '    def _evaluate(self, sig: dict, close: np.ndarray) -> dict:\n'
        '        i, direction = sig[\'bar_index\'], sig[\'direction\']\n'
        '        entry        = close[i]\n'
        '        cap          = min(i + self._max_bars, len(close) - 1)\n'
        '\n'
        '        stop_level = entry * (self._stop_long if direction == 1 else self._stop_short)\n'
        '\n'
        '        best_price         = entry\n'
        '        max_profit_pct     = 0.0\n'
        '        bars_to_max_profit = None\n'
        '        bars_to_stop       = None\n'
        '\n'
        '        for j in range(i + 1, cap + 1):\n'
        '            c = close[j]\n'
        '\n'
        '            if direction == 1:\n'
        '                if c > best_price:\n'
        '                    best_price         = c\n'
        '                    max_profit_pct     = (best_price / entry - 1.0) * 100.0\n'
        '                    bars_to_max_profit = j - i\n'
        '                if c <= stop_level:\n'
        '                    bars_to_stop = j - i\n'
        '                    break\n'
        '            else:\n'
        '                if c < best_price:\n'
        '                    best_price         = c\n'
        '                    max_profit_pct     = (entry / best_price - 1.0) * 100.0\n'
        '                    bars_to_max_profit = j - i\n'
        '                if c >= stop_level:\n'
        '                    bars_to_stop = j - i\n'
        '                    break\n'
        '\n'
        '        return {\n'
        '            **sig,\n'
        '            \'max_profit_pct\':     round(max_profit_pct, 6),\n'
        '            \'bars_to_stop\':       bars_to_stop,\n'
        '            \'bars_to_max_profit\': bars_to_max_profit,\n'
        '        }\n'
    ),
    new=(
        '    def __init__(self, stop_pct: float = 0.33, max_bars: int = None) -> None:\n'
        '        """\n'
        '        max_bars is deprecated as of r05 260521. Accepted for back-compat\n'
        '        with callers that still pass tc_max_bars, but ignored. A trade\n'
        '        either stops or runs off the dataset — no time cap.\n'
        '        """\n'
        '        self._stop_pct = stop_pct\n'
        '        self._log      = get_logger(self.__class__.__name__)\n'
        '        if max_bars is not None:\n'
        '            self._log.debug(f\'max_bars={max_bars} ignored (deprecated)\')\n'
        '\n'
        '    def analyze(self, signals: list, close: np.ndarray,\n'
        '                timestamps: np.ndarray = None) -> list:\n'
        '        """\n'
        '        Walk each signal\'s outcome via outcome_walker.walk_outcome.\n'
        '\n'
        '        timestamps is optional — when provided, threaded through to\n'
        '        outcome_walker for future per-call debug instrumentation.\n'
        '        """\n'
        '        return [\n'
        '            {**sig, **walk_outcome(\n'
        '                close, sig[\'bar_index\'], sig[\'direction\'],\n'
        '                self._stop_pct, timestamps,\n'
        '            )}\n'
        '            for sig in signals\n'
        '        ]\n'
    ),
    skip_if_contains='walk_outcome(\n                close, sig[\'bar_index\']',
))

# 04 — fold_manager.py: KlineLoader + OutcomeWalker
EDITS.append(Edit(
    'optimus9/analysis/fold_manager.py',
    '04a fold_manager: add KlineLoader import',
    old='from ..db.database_manager import DatabaseManager\n',
    new=(
        'from ..db.database_manager import DatabaseManager\n'
        'from ..db.kline_loader     import KlineLoader\n'
    ),
    skip_if_contains='from ..db.kline_loader',
))

EDITS.append(Edit(
    'optimus9/analysis/fold_manager.py',
    '04b fold_manager: add outcome_walker import',
    old='from ..compute.swing_analyzer import SwingAnalyzer\n',
    new=(
        'from ..compute.swing_analyzer import SwingAnalyzer\n'
        'from ..compute.outcome_walker import walk_outcome\n'
    ),
    skip_if_contains='from ..compute.outcome_walker',
))

EDITS.append(Edit(
    'optimus9/analysis/fold_manager.py',
    '04c fold_manager: drop _MAX_BARS class constant',
    old='    _MAX_BARS = 1080  # match production tc.tc_max_bars default\n',
    new=(
        '    # r05 (260521): _MAX_BARS dropped — outcome_walker now uses no cap.\n'
        '    # bars_to_stop=None ⇔ trade ran off the end of available klines.\n'
    ),
    skip_if_contains='_MAX_BARS dropped',
))

EDITS.append(Edit(
    'optimus9/analysis/fold_manager.py',
    '04d fold_manager: add self._kl in __init__',
    old=(
        '    def __init__(self, db: DatabaseManager) -> None:\n'
        '        self._db  = db\n'
        '        self._log = get_logger(self.__class__.__name__)\n'
    ),
    new=(
        '    def __init__(self, db: DatabaseManager) -> None:\n'
        '        self._db  = db\n'
        '        self._kl  = KlineLoader(db)\n'
        '        self._log = get_logger(self.__class__.__name__)\n'
    ),
    skip_if_contains='self._kl  = KlineLoader',
))

EDITS.append(Edit(
    'optimus9/analysis/fold_manager.py',
    '04e fold_manager: replace _evaluate_outcome body',
    old=(
        '    def _evaluate_outcome(self, base_df: pd.DataFrame, entry_idx: int,\n'
        '                          direction: int, stop_pct: float) -> dict:\n'
        '        """\n'
        '        Walk forward from entry_idx, capture max_profit_pct and bars_to_stop\n'
        '        against stop_pct. Returns dict with max_profit_pct and bars_to_stop\n'
        '        (bars_to_stop = None if trade never stopped within MAX_BARS).\n'
        '        """\n'
        '        close = base_df[\'close\'].to_numpy()\n'
        '        entry = float(close[entry_idx])\n'
        '        cap   = min(entry_idx + self._MAX_BARS, len(close) - 1)\n'
        '\n'
        '        max_profit_pct = 0.0\n'
        '        bars_to_stop   = None\n'
        '\n'
        '        if direction == 1:\n'
        '            stop_level = entry * (1.0 - stop_pct / 100.0)\n'
        '            for j in range(entry_idx + 1, cap + 1):\n'
        '                c = float(close[j])\n'
        '                if c > entry:\n'
        '                    profit = (c / entry - 1.0) * 100.0\n'
        '                    if profit > max_profit_pct:\n'
        '                        max_profit_pct = profit\n'
        '                if c <= stop_level:\n'
        '                    bars_to_stop = j - entry_idx\n'
        '                    break\n'
        '        else:\n'
        '            stop_level = entry * (1.0 + stop_pct / 100.0)\n'
        '            for j in range(entry_idx + 1, cap + 1):\n'
        '                c = float(close[j])\n'
        '                if c < entry:\n'
        '                    profit = (1.0 - c / entry) * 100.0\n'
        '                    if profit > max_profit_pct:\n'
        '                        max_profit_pct = profit\n'
        '                if c >= stop_level:\n'
        '                    bars_to_stop = j - entry_idx\n'
        '                    break\n'
        '\n'
        '        return {\n'
        '            \'max_profit_pct\': round(max_profit_pct, 4),\n'
        '            \'bars_to_stop\':   bars_to_stop,\n'
        '        }\n'
    ),
    new=(
        '    def _evaluate_outcome(self, base_df: pd.DataFrame, entry_idx: int,\n'
        '                          direction: int, stop_pct: float) -> dict:\n'
        '        """\n'
        '        Walk forward from entry_idx via shared outcome_walker.walk_outcome.\n'
        '\n'
        '        r05 (260521): per-bar walk moved to compute.outcome_walker, shared\n'
        '        with SwingAnalyzer. _MAX_BARS cap dropped — bars_to_stop=None now\n'
        '        strictly means the trade ran off the end of available klines.\n'
        '        """\n'
        '        close = base_df[\'close\'].to_numpy()\n'
        '        outcome = walk_outcome(close, entry_idx, direction, stop_pct)\n'
        '        # FoldManager only consumes max_profit_pct and bars_to_stop;\n'
        '        # drop bars_to_max_profit to keep the call-site stable.\n'
        '        return {\n'
        '            \'max_profit_pct\': outcome[\'max_profit_pct\'],\n'
        '            \'bars_to_stop\':   outcome[\'bars_to_stop\'],\n'
        '        }\n'
    ),
    skip_if_contains="outcome = walk_outcome(close, entry_idx, direction, stop_pct)",
))

EDITS.append(Edit(
    'optimus9/analysis/fold_manager.py',
    '04f fold_manager: replace _load_klines body',
    old=(
        '    def _load_klines(self, tp_pk: int, start_ms: int,\n'
        '                     end_ms: int) -> pd.DataFrame:\n'
        '        rows = self._db.execute(\n'
        '            \'\'\'SELECT kc_timestamp AS timestamp, kc_open  AS open,\n'
        '                      kc_high      AS high,      kc_low   AS low,\n'
        '                      kc_close     AS close,     kc_volume AS volume\n'
        '               FROM kline_collection\n'
        '               WHERE kc_tp_pk    = %s\n'
        '                 AND kc_timestamp >= %s\n'
        '                 AND kc_timestamp <  %s\n'
        '               ORDER BY kc_timestamp ASC\'\'\',\n'
        '            (tp_pk, start_ms, end_ms), fetch=True,\n'
        '        )\n'
        '        if not rows:\n'
        '            raise RuntimeError(f\'No klines for tp_pk={tp_pk} in window\')\n'
        '        return pd.DataFrame(rows)\n'
    ),
    new=(
        '    def _load_klines(self, tp_pk: int, start_ms: int,\n'
        '                     end_ms: int) -> pd.DataFrame:\n'
        '        """Delegates to shared KlineLoader (r05 260521 refactor)."""\n'
        '        return self._kl.load_window(tp_pk, start_ms, end_ms)\n'
    ),
    skip_if_contains='return self._kl.load_window(tp_pk, start_ms, end_ms)',
))

# 05 — report_manager.py
EDITS.append(Edit(
    'optimus9/orchestration/report_manager.py',
    '05a report_manager: add KlineLoader import',
    old=(
        'from ..db.database_manager import DatabaseManager\n'
        'from ..compute.indicator_computer import IndicatorComputer\n'
    ),
    new=(
        'from ..db.database_manager import DatabaseManager\n'
        'from ..db.kline_loader     import KlineLoader\n'
        'from ..compute.indicator_computer import IndicatorComputer\n'
    ),
    skip_if_contains='from ..db.kline_loader',
))

EDITS.append(Edit(
    'optimus9/orchestration/report_manager.py',
    '05b report_manager: drop max_bars from SwingAnalyzer ctor',
    old="            SwingAnalyzer(float(config['tc_stop_pct']), int(config['tc_max_bars'])),\n",
    new=(
        '            # r05 (260521): tc_max_bars deprecated — column kept for back-compat\n'
        '            # but no longer plumbed in. "Always a stop" principle means\n'
        '            # bars_to_stop=NULL ⇔ trade ran off the end of available klines.\n'
        "            SwingAnalyzer(float(config['tc_stop_pct'])),\n"
    ),
    skip_if_contains='tc_max_bars deprecated',
))

EDITS.append(Edit(
    'optimus9/orchestration/report_manager.py',
    '05c report_manager: replace _load_klines body',
    old=(
        '    def _load_klines(self, tp_pk: int, lookback_days: int = None) -> pd.DataFrame:\n'
        '        if lookback_days:\n'
        '            cutoff = int((datetime.now(timezone.utc) - timedelta(days=lookback_days)).timestamp() * 1000)\n'
        "            where, params = 'kc_tp_pk = %s AND kc_timestamp >= %s', (tp_pk, cutoff)\n"
        '        else:\n'
        "            where, params = 'kc_tp_pk = %s', (tp_pk,)\n"
        '        rows = self._db.execute(\n'
        "            f'''SELECT kc_timestamp AS timestamp, kc_open AS open, kc_high AS high,\n"
        '                       kc_low AS low, kc_close AS close, kc_volume AS volume\n'
        "                FROM kline_collection WHERE {where} ORDER BY kc_timestamp ASC''',\n"
        '            params, fetch=True,\n'
        '        )\n'
        '        if not rows:\n'
        "            raise RuntimeError(f'No klines for tp_pk={tp_pk}')\n"
        '        return pd.DataFrame(rows)\n'
    ),
    new=(
        '    def _load_klines(self, tp_pk: int, lookback_days: int = None) -> pd.DataFrame:\n'
        '        """Delegates to shared KlineLoader (r05 260521 refactor)."""\n'
        '        return KlineLoader(self._db).load_recent(tp_pk, lookback_days)\n'
    ),
    skip_if_contains='return KlineLoader(self._db).load_recent',
))

# 06 — optimizer_runner.py: pass timestamps to analyze()
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '06 optimizer_runner: pass timestamps to analyze()',
    old=(
        '            signals = self._extract_transitions(s5_pk_final)\n'
        '            outcomes = self._analyzer.analyze(signals, close)\n'
    ),
    new=(
        '            signals = self._extract_transitions(s5_pk_final)\n'
        '            # timestamps threaded through for future debug instrumentation\n'
        '            # inside SwingAnalyzer / outcome_walker.\n'
        '            outcomes = self._analyzer.analyze(signals, close, timestamps)\n'
    ),
    skip_if_contains='self._analyzer.analyze(signals, close, timestamps)',
))

# 07 — analyze_manager.py: _walk_equity split resolved/unrealized
EDITS.append(Edit(
    'optimus9/analysis/analyze_manager.py',
    '07 analyze_manager: _walk_equity resolved/unrealized split',
    old=(
        '        equity = seed\n'
        '        peak   = seed\n'
        '        max_dd = 0.0\n'
        '\n'
        '        won_pcts     = []\n'
        '        stopped      = 0\n'
        '        inconc       = 0\n'
        '        gross_wins   = 0.0\n'
        '        gross_losses = 0.0\n'
        '        pnls         = []\n'
        '\n'
        '        for s in signals:\n'
        "            mp  = float(s['max_pct']) if s['max_pct'] is not None else None\n"
        "            bts = s['bts']\n"
        '\n'
        '            if mp is not None and mp >= profit_zone:\n'
        '                pnl = mp\n'
        '                won_pcts.append(mp)\n'
        '                gross_wins += mp\n'
        '            elif bts is not None:\n'
        '                pnl = -stop_pct\n'
        '                stopped += 1\n'
        '                gross_losses += stop_pct\n'
        '            else:\n'
        '                pnl = 0.0\n'
        '                inconc += 1\n'
        '\n'
        '            pnls.append(pnl)\n'
        '            equity *= (1.0 + pnl / 100.0)\n'
        '            peak    = max(peak, equity)\n'
        '            if peak > 0:\n'
        '                dd = (peak - equity) / peak\n'
        '                if dd > max_dd:\n'
        '                    max_dd = dd\n'
    ),
    new=(
        '        # RESOLVED equity walk\n'
        '        equity = seed\n'
        '        peak   = seed\n'
        '        max_dd = 0.0\n'
        '\n'
        '        won_pcts     = []\n'
        '        stopped      = 0\n'
        '        unrealized   = 0     # was \'inconc\'; renamed locally for clarity\n'
        '        gross_wins   = 0.0\n'
        '        gross_losses = 0.0\n'
        '        pnls         = []\n'
        '\n'
        '        # UNREALIZED parallel equity walk (r05 260521)\n'
        '        u_equity     = seed\n'
        '        u_peak       = seed\n'
        '        u_max_dd     = 0.0\n'
        '        u_pnls       = []\n'
        '        u_max_pcts   = []\n'
        '\n'
        '        for s in signals:\n'
        "            mp  = float(s['max_pct']) if s['max_pct'] is not None else None\n"
        "            bts = s['bts']\n"
        '\n'
        '            if bts is not None:\n'
        '                # RESOLVED — stop fired at some point during the trade\n'
        '                if mp is not None and mp >= profit_zone:\n'
        '                    pnl = mp\n'
        '                    won_pcts.append(mp)\n'
        '                    gross_wins += mp\n'
        '                else:\n'
        '                    pnl = -stop_pct\n'
        '                    stopped += 1\n'
        '                    gross_losses += stop_pct\n'
        '\n'
        '                pnls.append(pnl)\n'
        '                equity *= (1.0 + pnl / 100.0)\n'
        '                peak    = max(peak, equity)\n'
        '                if peak > 0:\n'
        '                    dd = (peak - equity) / peak\n'
        '                    if dd > max_dd:\n'
        '                        max_dd = dd\n'
        '            else:\n'
        '                # UNREALIZED — trade ran off the end of available klines.\n'
        '                u_pnl = mp if mp is not None else 0.0\n'
        '                unrealized += 1\n'
        '                u_pnls.append(u_pnl)\n'
        '                if mp is not None and mp > 0:\n'
        '                    u_max_pcts.append(mp)\n'
        '                u_equity *= (1.0 + u_pnl / 100.0)\n'
        '                u_peak    = max(u_peak, u_equity)\n'
        '                if u_peak > 0:\n'
        '                    u_dd = (u_peak - u_equity) / u_peak\n'
        '                    if u_dd > u_max_dd:\n'
        '                        u_max_dd = u_dd\n'
    ),
    skip_if_contains='# UNREALIZED parallel equity walk',
))

EDITS.append(Edit(
    'optimus9/analysis/analyze_manager.py',
    '07b analyze_manager: extend return dict with unrealized metrics',
    old=(
        "            'n_won':         n_won,\n"
        "            'n_stopped':     stopped,\n"
        "            'n_inconc':      inconc,\n"
        "            'win_rate_walked': win_rate,\n"
    ),
    new=(
        "            'n_won':         n_won,\n"
        "            'n_stopped':     stopped,\n"
        "            'n_inconc':      unrealized,    # alias for n_unrealized (back-compat)\n"
        "            'n_unrealized':  unrealized,\n"
        "            'win_rate_walked': win_rate,\n"
    ),
    skip_if_contains="'n_unrealized':  unrealized",
))

EDITS.append(Edit(
    'optimus9/analysis/analyze_manager.py',
    '07c analyze_manager: add unrealized aggregates + return fields',
    old=(
        "            'min_won_pct':   min_won_pct,\n"
        "            'win95_flag':    1 if win_rate > 0.95 else 0,\n"
        '        }\n'
    ),
    new=(
        "            'min_won_pct':   min_won_pct,\n"
        "            'win95_flag':    1 if win_rate > 0.95 else 0,\n"
        '            # UNREALIZED shadow metrics (trades still open at dataset end)\n'
        "            'unrealized_gross_banked': u_equity,\n"
        "            'unrealized_max_drawdown': u_max_dd,\n"
        "            'unrealized_mean_pnl':     float(np.mean(u_pnls)) if u_pnls else 0.0,\n"
        "            'unrealized_avg_max_pct':  float(np.mean(u_max_pcts)) if u_max_pcts else 0.0,\n"
        '        }\n'
    ),
    skip_if_contains='unrealized_gross_banked',
))

# 08 — validate_centroid.py: mirror analyze_manager change
EDITS.append(Edit(
    'validate_centroid.py',
    '08a validate_centroid: _walk_equity split',
    old=(
        '    import numpy as np\n'
        '    equity, peak, max_dd = seed, seed, 0.0\n'
        '    won_pcts, stopped, inconc = [], 0, 0\n'
        '    gross_wins, gross_losses = 0.0, 0.0\n'
        '    pnls = []\n'
        '    for s in signals:\n'
        "        mp  = float(s['max_pct']) if s['max_pct'] is not None else None\n"
        "        bts = s['bts'] if 'bts' in s else s.get('bars_to_stop')\n"
        '        if mp is not None and mp >= profit_zone:\n'
        '            pnl = mp\n'
        '            won_pcts.append(mp)\n'
        '            gross_wins += mp\n'
        '        elif bts is not None:\n'
        '            pnl = -stop_pct\n'
        '            stopped += 1\n'
        '            gross_losses += stop_pct\n'
        '        else:\n'
        '            pnl = 0.0\n'
        '            inconc += 1\n'
        '        pnls.append(pnl)\n'
        '        equity *= (1.0 + pnl / 100.0)\n'
        '        peak = max(peak, equity)\n'
        '        if peak > 0:\n'
        '            dd = (peak - equity) / peak\n'
        '            if dd > max_dd:\n'
        '                max_dd = dd\n'
    ),
    new=(
        '    import numpy as np\n'
        '    equity, peak, max_dd = seed, seed, 0.0\n'
        '    won_pcts, stopped, unrealized = [], 0, 0\n'
        '    gross_wins, gross_losses = 0.0, 0.0\n'
        '    pnls = []\n'
        '    # UNREALIZED parallel set (r05 260521)\n'
        '    u_equity, u_peak, u_max_dd = seed, seed, 0.0\n'
        '    u_pnls, u_max_pcts = [], []\n'
        '\n'
        '    for s in signals:\n'
        "        mp  = float(s['max_pct']) if s['max_pct'] is not None else None\n"
        "        bts = s['bts'] if 'bts' in s else s.get('bars_to_stop')\n"
        '\n'
        '        if bts is not None:\n'
        '            # RESOLVED — stop fired\n'
        '            if mp is not None and mp >= profit_zone:\n'
        '                pnl = mp\n'
        '                won_pcts.append(mp)\n'
        '                gross_wins += mp\n'
        '            else:\n'
        '                pnl = -stop_pct\n'
        '                stopped += 1\n'
        '                gross_losses += stop_pct\n'
        '            pnls.append(pnl)\n'
        '            equity *= (1.0 + pnl / 100.0)\n'
        '            peak = max(peak, equity)\n'
        '            if peak > 0:\n'
        '                dd = (peak - equity) / peak\n'
        '                if dd > max_dd:\n'
        '                    max_dd = dd\n'
        '        else:\n'
        '            # UNREALIZED — ran off dataset end\n'
        '            u_pnl = mp if mp is not None else 0.0\n'
        '            unrealized += 1\n'
        '            u_pnls.append(u_pnl)\n'
        '            if mp is not None and mp > 0:\n'
        '                u_max_pcts.append(mp)\n'
        '            u_equity *= (1.0 + u_pnl / 100.0)\n'
        '            u_peak = max(u_peak, u_equity)\n'
        '            if u_peak > 0:\n'
        '                u_dd = (u_peak - u_equity) / u_peak\n'
        '                if u_dd > u_max_dd:\n'
        '                    u_max_dd = u_dd\n'
    ),
    skip_if_contains='# UNREALIZED parallel set',
))

EDITS.append(Edit(
    'validate_centroid.py',
    '08b validate_centroid: update return dict',
    old=(
        "        'n_won':         n_won,\n"
        "        'n_stopped':     stopped,\n"
        "        'n_inconc':      inconc,\n"
    ),
    new=(
        "        'n_won':         n_won,\n"
        "        'n_stopped':     stopped,\n"
        "        'n_inconc':      unrealized,\n"
        "        'n_unrealized':  unrealized,\n"
    ),
    skip_if_contains="'n_unrealized':  unrealized",
))

EDITS.append(Edit(
    'validate_centroid.py',
    '08c validate_centroid: add unrealized fields to return dict',
    old=(
        "        'win95_flag':    1 if decided and (n_won / decided) > 0.95 else 0,\n"
        '    }\n'
    ),
    new=(
        "        'win95_flag':    1 if decided and (n_won / decided) > 0.95 else 0,\n"
        '        # UNREALIZED shadow metrics\n'
        "        'unrealized_gross_banked': u_equity,\n"
        "        'unrealized_max_drawdown': u_max_dd,\n"
        "        'unrealized_mean_pnl':     float(np.mean(u_pnls)) if u_pnls else 0.0,\n"
        "        'unrealized_avg_max_pct':  float(np.mean(u_max_pcts)) if u_max_pcts else 0.0,\n"
        '    }\n'
    ),
    skip_if_contains='unrealized_gross_banked',
))


# ─── Main ───────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without writing')
    args = parser.parse_args()

    print(f'r05 260521 refactor — {"DRY-RUN" if args.dry_run else "APPLYING"}')
    print('=' * 70)

    nomatches = 0
    skipped   = 0
    applied   = 0
    missing   = 0

    for edit in EDITS:
        status = edit.apply(args.dry_run)
        print(status)
        if status.startswith('⚠'):
            nomatches += 1
        elif status.startswith('⊝'):
            skipped += 1
        elif status.startswith('✓') or status.startswith('·'):
            applied += 1
        elif status.startswith('✗'):
            missing += 1

    print('=' * 70)
    print(f'Total: {len(EDITS)} edits  |  '
          f'applied: {applied}  skipped: {skipped}  '
          f'nomatch: {nomatches}  missing: {missing}')

    if nomatches > 0:
        print()
        print('⚠  Some edits did not find their target text. This usually means')
        print('   the source file has drifted from what this script expects.')
        print('   Inspect the file and either fix manually or update this script.')
        return 1
    if missing > 0:
        print()
        print('✗  Some files were missing. Check paths.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
