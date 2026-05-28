#!/usr/bin/env python3
"""
emit_pine_strategy.py — standalone CLI to emit a Pine v6 strategy file
from a completed analyze_manager run.
"""

import argparse
import sys

from optimus9.config                     import get_db_config
from optimus9.db.database_manager        import DatabaseManager
from optimus9.emit.pine_strategy_emitter import PineStrategyEmitter


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Emit Pine v6 strategy from PROVEN combo of an or_pk'
    )
    parser.add_argument('--or_pk',      type=int, required=True,
                        help='optimizer_run primary key to emit from')
    parser.add_argument('--output_dir', type=str, default='.',
                        help='Directory containing analysis_or<N>.csv (default: current)')
    args = parser.parse_args()

    db = DatabaseManager(**get_db_config())
    db.connect()
    try:
        emitter = PineStrategyEmitter(db)
        output_path = emitter.emit(args.or_pk, output_dir=args.output_dir)
        if output_path is None:
            return 1
        print(f'\nPine strategy emitted: {output_path}')
        print(f'Drop into TradingView: chart=FARTCOINUSDT, timeframe=5s, paste source.')
        return 0
    finally:
        db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
