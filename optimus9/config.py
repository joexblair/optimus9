"""
optimus9.config — centralized configuration loader.

Looks for `optimus9_config.json` in (in order):
  1. Current working directory (./optimus9_config.json)
  2. Repo root (one level up from this file's parent: optimus9/../)
  3. User home (~/.optimus9_config.json)

Environment variables override file values for backward compat with the
older PK_DB_* env-var pattern used by analyze_manager, run, etc.

Usage:
    from optimus9.config import get_db_config
    db = DatabaseManager(**get_db_config())

Or for direct access to the parsed config:
    from optimus9.config import load_config
    cfg = load_config()
    archive_dir = cfg.get('archive', {}).get('path', '/mnt/archive/optimus9')
"""

import json
import os
from pathlib import Path
from typing import Optional


_CACHED_CONFIG: Optional[dict] = None


def _candidate_paths() -> list:
    """Search locations, in priority order."""
    return [
        Path.cwd() / 'optimus9_config.json',
        Path(__file__).resolve().parent.parent / 'optimus9_config.json',
        Path.home() / '.optimus9_config.json',
    ]


def load_config(force_reload: bool = False) -> dict:
    """Load config from disk (cached). Returns empty dict if no file found."""
    global _CACHED_CONFIG
    if _CACHED_CONFIG is not None and not force_reload:
        return _CACHED_CONFIG

    for path in _candidate_paths():
        if path.exists():
            with open(path) as f:
                _CACHED_CONFIG = json.load(f)
            return _CACHED_CONFIG

    # No file found — return empty dict, callers fall back to env vars + defaults
    _CACHED_CONFIG = {}
    return _CACHED_CONFIG


def get_db_config() -> dict:
    """
    Return DB kwargs suitable for `DatabaseManager(**get_db_config())`.

    Resolution order per field:
      1. Environment variable (PK_DB_HOST, PK_DB_USER, etc.) — highest
      2. optimus9_config.json `db.<field>` value
      3. Built-in default
    """
    cfg = load_config()
    db  = cfg.get('db', {})

    return {
        'host':     os.environ.get('PK_DB_HOST', db.get('host',     'localhost')),
        'user':     os.environ.get('PK_DB_USER', db.get('user',     'root')),
        'password': os.environ.get('PK_DB_PASS', db.get('password', '')),
        'database': os.environ.get('PK_DB_NAME', db.get('database', 'pk_optimizer')),
        'port':     int(os.environ.get('PK_DB_PORT', db.get('port', 3306))),
    }


def get_archive_config() -> dict:
    """Future use — archive util settings."""
    cfg = load_config()
    arch = cfg.get('archive', {})
    return {
        'path':        arch.get('path', '/mnt/archive/optimus9'),
        'enabled':     arch.get('enabled', False),
        'keep_recent': int(arch.get('keep_recent', 3)),
    }
