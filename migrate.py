#!/usr/bin/env python3
"""
migrate.py — one-shot restructure of managers.py into the optimus9 package.

Usage:
    python3 migrate.py              # dry-run, prints planned changes
    python3 migrate.py --commit     # applies changes

Round 260515 — see round spec 260514_pk5s_spec.md for context.

What it does (--commit):
    1. Backs up managers.py → managers.py.bak
    2. Parses managers.py via ast, extracts each top-level class
    3. Writes each class to optimus9/<subpackage>/<module>.py with
       cross-package imports already in place
    4. Creates __init__.py at every package level with re-exports
    5. Updates run.py imports from `managers` → `optimus9`
    6. Creates tests/ scaffold with conftest.py + example tests
    7. Validates the resulting package imports cleanly

What it does NOT do:
    • Apply the compare workflow additions (sections 7-9 from the 260514
      patches doc). Those land via `optimus9_post_migration_patches.md`,
      operating on the new analyze_manager.py and report_manager.py.
    • Apply the optimus9_data_cleanup.sql historical-flags update.

Rollback if something goes wrong:
    mv managers.py.bak managers.py
    rm -rf optimus9 tests
    git checkout run.py
"""

import ast
import shutil
import sys
import importlib
import textwrap
from pathlib import Path

# ─── class → (subpackage, module_file, dependencies) ────────────────────────
#
# Each class lands in one module file. Dependencies are other optimus9
# classes this class references — used to generate cross-package imports.
# External deps (pandas, numpy, requests, etc.) flow through via the
# preserved module-level imports at the top of each file.

CLASS_MAP = {
    # db layer (foundation)
    'DatabaseManager':       ('db',            'database_manager.py',     []),

    # data layer (exchange clients, ingestion, builders)
    'BinanceClient':         ('data',          'binance_client.py',          []),
    'BinanceBackfiller':     ('data',          'binance_backfiller.py',      ['DatabaseManager', 'BinanceClient']),
    'BybitKlineClient':      ('data',          'bybit_kline_client.py',      []),
    'BybitWebSocketClient':  ('data',          'bybit_websocket_client.py',  []),
    'SyntheticBarBuilder':   ('data',          'synthetic_bar_builder.py',   []),
    'SyntheticBackfiller':   ('data',          'synthetic_backfiller.py',    ['DatabaseManager', 'BybitKlineClient', 'SyntheticBarBuilder']),
    'TickCollector':         ('data',          'tick_collector.py',          ['DatabaseManager', 'BybitWebSocketClient']),
    'BarBuilder':            ('data',          'bar_builder.py',             ['DatabaseManager']),
    'IndicatorMonitor':      ('data',          'indicator_monitor.py',       ['DatabaseManager']),

    # compute layer (numerical machinery, stateless)
    'IndicatorComputer':     ('compute',       'indicator_computer.py',      []),
    'PKDetector':            ('compute',       'pk_detector.py',             []),
    'Pk5sGateComputer':      ('compute',       'pk5s_gate_computer.py',      ['DatabaseManager', 'IndicatorComputer']),
    'SwingAnalyzer':         ('compute',       'swing_analyzer.py',          []),
    'ParameterGridBuilder':  ('compute',       'parameter_grid_builder.py',  ['DatabaseManager']),

    # orchestration layer (drives compute via data)
    'OptimizerRunner':       ('orchestration', 'optimizer_runner.py',        ['DatabaseManager', 'PKDetector', 'SwingAnalyzer', 'IndicatorComputer']),
    'ReportExporter':        ('orchestration', 'report_exporter.py',         ['DatabaseManager']),
    'ReportManager':         ('orchestration', 'report_manager.py',          ['DatabaseManager', 'IndicatorComputer', 'PKDetector', 'Pk5sGateComputer', 'SwingAnalyzer', 'OptimizerRunner', 'ParameterGridBuilder', 'ReportExporter']),
    'WorkerSpec':            ('orchestration', 'process_manager.py',         []),     # paired with ProcessManager
    'ProcessManager':        ('orchestration', 'process_manager.py',         ['WorkerSpec']),

    # analysis layer (post-run reporting)
    'AnalyzeManager':        ('analysis',      'analyze_manager.py',         ['DatabaseManager']),
    'OutlierReporter':       ('analysis',      'outlier_reporter.py',        ['DatabaseManager']),
}

SUBPACKAGE_DESCRIPTIONS = {
    'db':             'Database connection and query layer.',
    'data':           'Exchange clients and data ingestion (Binance, Bybit, kline builders).',
    'compute':        'Stateless numerical machinery — indicators, PK detection, vote machines, swing analysis.',
    'orchestration':  'Run drivers — wires compute over data, persists results.',
    'analysis':       'Post-run reporting — single-run analysis, comparison across runs, outlier detection.',
}


# ─── parsing ─────────────────────────────────────────────────────────────────

def parse_managers(path):
    """
    Parse managers.py and return:
        module_preamble: imports + module-level constants (everything before
                         first class), with the module docstring stripped
        class_sources:   {class_name: raw_source_with_decorators}
        helper_funcs:    list of module-level helper function sources
    """
    with open(path) as f:
        source = f.read()
    tree = ast.parse(source)
    lines = source.split('\n')

    # Strip module docstring if present
    preamble_start = 0
    if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Constant):
        preamble_start = tree.body[0].end_lineno  # 1-based, after docstring

    first_class_line = min(
        (n.lineno for n in tree.body if isinstance(n, ast.ClassDef)),
        default=len(lines)
    )
    module_preamble = '\n'.join(lines[preamble_start:first_class_line - 1]).rstrip()

    # Strip trailing comment block / blanks. The section divider just before
    # the first class in managers.py (e.g. `# ── DatabaseManager ──`)
    # belongs to that class, not to every module file. Walk backwards
    # dropping blank/comment lines until we hit a real statement.
    preamble_lines = module_preamble.split('\n')
    while preamble_lines and (
        not preamble_lines[-1].strip()
        or preamble_lines[-1].lstrip().startswith('#')
    ):
        preamble_lines.pop()
    module_preamble = '\n'.join(preamble_lines)

    class_sources = {}
    helper_funcs = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            # Include any decorators (e.g. @dataclass on WorkerSpec)
            start = (node.decorator_list[0].lineno - 1) if node.decorator_list else (node.lineno - 1)
            end = node.end_lineno
            class_sources[node.name] = '\n'.join(lines[start:end])
        elif isinstance(node, ast.FunctionDef):
            start = node.lineno - 1
            end = node.end_lineno
            helper_funcs.append((node.name, '\n'.join(lines[start:end])))

    return module_preamble, class_sources, helper_funcs


# ─── per-file content builders ───────────────────────────────────────────────

def build_module_file(class_names, class_sources, deps, module_preamble):
    """
    Build the full source for one optimus9 module file.

    class_names is a list because some files contain a pair (e.g.
    WorkerSpec + ProcessManager in process_manager.py).
    """
    cross_imports = []
    seen = set(class_names)  # don't import classes already defined in this file
    for cls_in_file in class_names:
        for dep in deps.get(cls_in_file, []):
            if dep in seen or dep not in CLASS_MAP:
                continue
            seen.add(dep)
            sub, mod, _ = CLASS_MAP[dep]
            cross_imports.append(f'from ..{sub}.{mod[:-3]} import {dep}')

    # Module docstring — short, names what's in the file
    docstring_body = ', '.join(class_names)
    docstring = f'"""\n{docstring_body} — see class docstring for purpose, Pine alignment, and design notes.\n"""'

    parts = [docstring, '']
    parts.append(module_preamble.rstrip())
    if cross_imports:
        parts.extend(['', '# ── cross-package imports ─────────────────────────────────────────────────'])
        parts.extend(cross_imports)
    parts.extend(['', ''])
    parts.extend(class_sources)
    return '\n'.join(parts).rstrip() + '\n'


def build_top_init():
    """Optimus9 top-level __init__.py — re-exports every class."""
    lines = [
        '"""',
        'Optimus9 — parameter optimizer and (eventual) trading bot.',
        '',
        'This package replaces the monolithic managers.py from earlier rounds.',
        'Layers:',
        '',
    ]
    for sub, desc in SUBPACKAGE_DESCRIPTIONS.items():
        lines.append(f'  optimus9.{sub}  — {desc}')
    lines.extend([
        '',
        'See round spec 260514_pk5s_spec.md and onward for design notes.',
        '"""',
        '',
        '# ── class re-exports ─────────────────────────────────────────────────',
        '#',
        '# Classes are re-exported at top level so `from optimus9 import X`',
        '# works regardless of which subpackage X lives in.',
        '',
    ])
    # Group re-exports by subpackage for readability
    by_subpkg = {}
    for cls, (sub, mod, _) in CLASS_MAP.items():
        by_subpkg.setdefault(sub, []).append((cls, mod))
    for sub in SUBPACKAGE_DESCRIPTIONS:
        if sub not in by_subpkg:
            continue
        lines.append(f'# {sub}')
        # group by module file (some modules contain multiple classes)
        by_mod = {}
        for cls, mod in by_subpkg[sub]:
            by_mod.setdefault(mod, []).append(cls)
        for mod, classes in by_mod.items():
            lines.append(f'from .{sub}.{mod[:-3]} import {", ".join(classes)}')
        lines.append('')

    lines.extend([
        '__all__ = [',
        *(f"    '{cls}'," for cls in CLASS_MAP),
        ']',
        '',
    ])
    return '\n'.join(lines)


def build_subpkg_init(sub):
    desc = SUBPACKAGE_DESCRIPTIONS.get(sub, '')
    return f'"""\noptimus9.{sub} — {desc}\n"""\n'


def build_helpers_file(helper_funcs, module_preamble):
    """Module-level helpers from managers.py end up in optimus9/_helpers.py."""
    parts = [
        '"""',
        'Module-level helper functions preserved from the original managers.py.',
        'Kept at package root since they\'re used across multiple subpackages.',
        '"""',
        '',
        module_preamble.rstrip(),
        '',
        '',
    ]
    for _, source in helper_funcs:
        parts.append(source)
        parts.append('')
    return '\n'.join(parts)


# ─── tests scaffold ──────────────────────────────────────────────────────────

TESTS_CONFTEST = '''"""
Shared pytest fixtures for optimus9 tests.

Round 260515 — minimal scaffold establishing the testing pattern. Add
fixtures as needed when new tests require shared setup.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_5s_df():
    """
    Synthetic 5s OHLCV — 720 bars = 1 hour. Random-walk close with
    derived O/H/L. Useful for testing resample / lookahead / build_source.
    """
    np.random.seed(42)
    n = 720
    start_ms = 1_700_000_000_000  # arbitrary fixed timestamp for determinism
    ts = np.arange(n) * 5_000 + start_ms
    rw = np.cumsum(np.random.randn(n) * 0.01) + 100.0
    return pd.DataFrame({
        'timestamp': ts,
        'open':   rw,
        'high':   rw + 0.02,
        'low':    rw - 0.02,
        'close':  rw,
        'volume': np.random.uniform(100, 1000, n),
    })


@pytest.fixture
def decimal_5s_df(sample_5s_df):
    """
    5s OHLCV with Decimal OHLC columns (object dtype) — simulates what
    comes back from pymysql against DECIMAL(20,8) kline_collection columns.
    Regression coverage for the 260515 lookahead_resample dtype fix.
    """
    from decimal import Decimal
    df = sample_5s_df.copy()
    for col in ['open', 'high', 'low', 'close']:
        df[col] = df[col].apply(Decimal).astype(object)
    return df
'''

TEST_INDICATOR_COMPUTER = '''"""Tests for optimus9.compute.indicator_computer."""

import numpy as np
import pandas as pd
import pytest

from optimus9 import IndicatorComputer


def test_lookahead_resample_developing_high_is_cummax(sample_5s_df):
    """
    Developing high at each 5s bar should equal the running max of 5s
    highs within its containing higher-TF window. 30s windows = 6 × 5s.
    """
    result = IndicatorComputer.lookahead_resample(sample_5s_df, target_seconds=30)

    # First 6 bars are in window 0 — developing high should be cummax of the
    # first 6 5s highs.
    first_window_highs = sample_5s_df['high'].iloc[:6].astype(float).cummax().to_numpy()
    np.testing.assert_array_almost_equal(result['high'].iloc[:6].to_numpy(),
                                          first_window_highs)


def test_lookahead_resample_developing_open_is_window_first(sample_5s_df):
    """Every 5s bar in a developing window shares the window's first open."""
    result = IndicatorComputer.lookahead_resample(sample_5s_df, target_seconds=30)
    # All 6 bars of window 0 should have the same open value
    first_open = float(sample_5s_df['open'].iloc[0])
    assert all(result['open'].iloc[:6] == first_open)


def test_lookahead_resample_accepts_decimal_dtype(decimal_5s_df):
    """
    Regression test for 260515 fix: kline_collection's DECIMAL columns
    come through pymysql as object dtype. lookahead_resample must cast
    before groupby cython ops.
    """
    # Should not raise NotImplementedError ("cummax is not supported
    # for object dtype")
    result = IndicatorComputer.lookahead_resample(decimal_5s_df, target_seconds=30)
    assert len(result) == len(decimal_5s_df)
    assert result['high'].dtype == float
'''

TEST_PK5S_GATE = '''"""Tests for optimus9.compute.pk5s_gate_computer state-machine pieces."""

import numpy as np

from optimus9 import Pk5sGateComputer


def test_decision_delay_fires_after_n_consecutive():
    """A direction must persist for `delay` bars before firing."""
    pk_raw = np.array([0, 1, 1, 1, 1, 0, 0], dtype=np.int8)
    # delay=3 means: bar 1 starts countdown, bars 2 and 3 decrement, bar 4 fires
    out = Pk5sGateComputer._apply_decision_delay(pk_raw, delay=3)
    assert out[4] == 1, f'expected fire at bar 4, got {out}'
    assert out[3] == 0
    assert out[1] == 0


def test_decision_delay_direction_change_resets_countdown():
    """A flip mid-countdown restarts the count with the new direction."""
    pk_raw = np.array([0, 1, 1, -1, -1, -1, -1], dtype=np.int8)
    out = Pk5sGateComputer._apply_decision_delay(pk_raw, delay=3)
    # bar 3 flips to -1 → countdown restart; bars 4,5 decrement; bar 6 fires
    assert out[6] == -1
    assert all(out[:6] == 0)


def test_decision_delay_zero_clears_pending():
    """Returning to neutral clears the pending state — no implicit re-arm."""
    pk_raw = np.array([1, 1, 0, 1, 1, 1, 1], dtype=np.int8)
    out = Pk5sGateComputer._apply_decision_delay(pk_raw, delay=3)
    # bar 2 resets; bar 3 starts fresh countdown; bars 4,5 decrement; bar 6 fires
    assert out[6] == 1
    assert all(out[:6] == 0)
'''

TEST_ANALYZE_MANAGER = '''"""Tests for optimus9.analysis.analyze_manager centroid math."""

import pandas as pd

from optimus9 import AnalyzeManager


class _DummyDB:
    """Minimal DB stub — AnalyzeManager only needs an attribute presence."""
    def execute(self, *args, **kwargs):
        return []


def test_compute_centroid_int_params_round_to_int():
    """
    Regression for 260515: int params (len, pool_c, pool_w, pool_range,
    multiplier) must come out as Python ints, not floats like 18.25.
    """
    am = AnalyzeManager(_DummyDB())
    df = pd.DataFrame({
        'len':         [19, 20, 21],
        'mult':        [0.6, 0.7, 0.8],
        'pool_c':      [8, 10, 12],
        'pool_w':      [50, 55, 60],
        'pool_range':  [2, 2, 4],
        'slope_floor': [2.5, 2.5, 2.5],
        'multiplier':  [3, 3, 3],
        'src':         ['close', 'close', 'hl2'],
        'expectancy':  [0.1, 0.2, 0.3],
    })
    cent = am._compute_centroid(df, n=3)
    for p in ['len', 'pool_c', 'pool_w', 'pool_range', 'multiplier']:
        assert isinstance(cent[p], int), f'{p}={cent[p]!r} should be int'
    # mult and slope_floor stay float
    assert isinstance(cent['mult'], float)


def test_compute_centroid_all_negative_uses_uniform_weights():
    """
    When every expectancy is non-positive, the weighted-by-expectancy
    fallback should produce a uniform-weighted centroid rather than NaN.
    """
    am = AnalyzeManager(_DummyDB())
    df = pd.DataFrame({
        'len':         [10, 20],
        'mult':        [0.5, 0.7],
        'pool_c':      [5, 10],
        'pool_w':      [30, 50],
        'pool_range':  [2, 4],
        'slope_floor': [2.5, 2.5],
        'multiplier':  [3, 3],
        'src':         ['close', 'hl2'],
        'expectancy':  [-0.33, -0.33],
    })
    cent = am._compute_centroid(df, n=2)
    assert cent['len'] == 15  # (10 + 20) / 2 = 15, rounded
    assert cent['mult'] == 0.6  # (0.5 + 0.7) / 2 = 0.6
'''

PYTEST_INI = '''[pytest]
testpaths = tests
python_files = test_*.py
addopts = -ra --strict-markers
'''


# ─── main ────────────────────────────────────────────────────────────────────

def main():
    commit = '--commit' in sys.argv
    root = Path('.')
    managers_path = root / 'managers.py'

    if not managers_path.exists():
        print('ERROR: managers.py not found in current directory')
        print('       Run from the project root.')
        return 1

    print('=' * 64)
    print(f'  optimus9 migration  —  {"COMMIT mode" if commit else "DRY RUN"}')
    print('=' * 64)
    print()

    preamble, class_sources, helper_funcs = parse_managers(managers_path)
    print(f'Parsed managers.py: {len(class_sources)} classes, {len(helper_funcs)} helper functions')
    print()

    # Validation: every class in CLASS_MAP must exist in source, and vice versa
    src_classes = set(class_sources)
    mapped = set(CLASS_MAP)
    unmapped = src_classes - mapped
    missing = mapped - src_classes
    if unmapped:
        print(f'⚠  Classes in managers.py NOT in CLASS_MAP — will be skipped:')
        for c in unmapped: print(f'     • {c}')
        print()
    if missing:
        print(f'⚠  Classes in CLASS_MAP NOT in managers.py — likely a stale map:')
        for c in missing: print(f'     • {c}')
        print()
        if commit:
            print('Refusing to commit with missing classes. Fix CLASS_MAP first.')
            return 1

    # Group classes by their target module file
    by_module = {}  # (subpkg, module) → [class names]
    for cls, (sub, mod, _) in CLASS_MAP.items():
        if cls not in src_classes:
            continue
        by_module.setdefault((sub, mod), []).append(cls)

    print('Planned package structure:')
    for (sub, mod), classes in sorted(by_module.items()):
        cls_str = ' + '.join(classes)
        print(f'  optimus9/{sub}/{mod:<28}  ←  {cls_str}')
    if helper_funcs:
        print(f'  optimus9/_helpers.py              ←  {len(helper_funcs)} module-level helpers')
    print()

    if not commit:
        print('Dry run complete. Re-run with --commit to apply.')
        return 0

    # ── apply ─────────────────────────────────────────────────────────────
    print('Applying:')

    # Backup
    bak = root / 'managers.py.bak'
    shutil.copy(managers_path, bak)
    print(f'  backed up managers.py → managers.py.bak')

    # Package skeleton
    pkg = root / 'optimus9'
    pkg.mkdir(exist_ok=True)
    for sub in SUBPACKAGE_DESCRIPTIONS:
        sub_dir = pkg / sub
        sub_dir.mkdir(exist_ok=True)
        (sub_dir / '__init__.py').write_text(build_subpkg_init(sub))

    # Deps lookup for the file-builder
    deps_lookup = {cls: deps for cls, (_, _, deps) in CLASS_MAP.items()}

    # Write each module file
    for (sub, mod), classes in by_module.items():
        sources = [class_sources[c] for c in classes]
        content = build_module_file(classes, sources, deps_lookup, preamble)
        target = pkg / sub / mod
        target.write_text(content)
        print(f'  wrote optimus9/{sub}/{mod}')

    # Helpers
    if helper_funcs:
        (pkg / '_helpers.py').write_text(build_helpers_file(helper_funcs, preamble))
        print(f'  wrote optimus9/_helpers.py')

    # Top-level __init__
    (pkg / '__init__.py').write_text(build_top_init())
    print(f'  wrote optimus9/__init__.py')

    # Patch run.py
    run_path = root / 'run.py'
    if run_path.exists():
        run_src = run_path.read_text()
        new_src = run_src.replace('from managers import', 'from optimus9 import')
        if new_src != run_src:
            run_path.write_text(new_src)
            print(f'  patched run.py: from managers → from optimus9')
        else:
            print(f'  run.py imports already use optimus9 (no change)')

    # Tests
    tests_dir = root / 'tests'
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / '__init__.py').write_text('')
    (tests_dir / 'conftest.py').write_text(TESTS_CONFTEST)
    (tests_dir / 'test_indicator_computer.py').write_text(TEST_INDICATOR_COMPUTER)
    (tests_dir / 'test_pk5s_gate_computer.py').write_text(TEST_PK5S_GATE)
    (tests_dir / 'test_analyze_manager.py').write_text(TEST_ANALYZE_MANAGER)
    (root / 'pytest.ini').write_text(PYTEST_INI)
    print(f'  wrote tests/ scaffold (conftest + 3 example tests)')
    print(f'  wrote pytest.ini')

    print()
    print('Migration complete. Next steps:')
    print('  1. Sanity import:   python3 -c "from optimus9 import AnalyzeManager; print(123)"')
    print('  2. Run tests:       pytest')
    print('  3. Smoke pipeline:  python3 run.py smoke --tc_pk 1 --lookback_days 1')
    print('  4. Apply optimus9_post_migration_patches.md (compare workflow + or_completed_at)')
    print('  5. Apply optimus9_data_cleanup.sql (historical flags + abandoned rows)')
    print('  6. Once verified:   rm managers.py.bak  (or keep until next round, your call)')

    return 0


if __name__ == '__main__':
    sys.exit(main())
