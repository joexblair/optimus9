"""line_config — WHAT an indicator config IS, and HOW to obtain one. Nothing else. (0714)

SRP. This module is the ONLY place in the system that knows the DB column order or the positional
tuple layout. `bias_machine` CONSUMES configs; it stops DEFINING them. The jig re-exports the builders
so no script ever hand-writes a tuple again.

────────────────────────────────────────────────────────────────────────────────────────────────────
THE BUG THIS EXISTS TO KILL (0714)

Joe writes a k-line as       k_len | rsi_len | stc_len | src        e.g. s{}r = 5|7|7|ohlc4
The legacy tuple was        ('k',  rsi_len,  stc_len,  k_len, src)  e.g.        ('k', 7, 7, 5, 'ohlc4')
                                    ^^^^^^^ Joe's FIRST number is the tuple's LAST.

Transposing it is SILENT. The line still computes, still looks plausible, and is a DIFFERENT LINE.
Verified against TV (transfer/BYBIT_FARTCOINUSDT.P_s120.csv, 54 bars): s120r built the right way round
matches TradingView to MAE 0.03. Transposed, it is off by 9.33. A whole day of tuning ran on the wrong r
before anyone noticed.

The fix is NOT to reorder the tuple — that relocates the bug and gives you one more chance to transpose
during the migration. The fix is to make the order UNSAYABLE:

    KLine(k_len=7, rsi=5, stc=7, src='ohlc4')      # you must name what you mean
    BBLine(length=6, mult=0.56, src='ohlc4')

Legacy positional tuples still work everywhere — `as_tuple`/`coerce` bridge them — so no existing script
breaks. New code uses the named form and CANNOT transpose.
────────────────────────────────────────────────────────────────────────────────────────────────────
"""
from typing import NamedTuple, Union


class KLine(NamedTuple):
    """A K-chain line (RSI -> Stoch -> SMA). Fields in JOE'S notation order: k_len | rsi | stc | src."""
    k_len: int
    rsi: int
    stc: int
    src: str = 'close'

    def as_tuple(self):
        """The legacy positional form the builders still speak: ('k', rsi, stc, k_len, src)."""
        return ('k', self.rsi, self.stc, self.k_len, self.src)

    def __str__(self):
        return f'{self.k_len}|{self.rsi}|{self.stc}|{self.src}'


class BBLine(NamedTuple):
    """A Bollinger-position line. Notation and tuple already agree: length | mult | src."""
    length: int
    mult: float
    src: str = 'close'

    def as_tuple(self):
        return ('bb', self.length, float(self.mult), self.src)

    def __str__(self):
        return f'{self.length}|{self.mult}|{self.src}'


LineCfg = Union[KLine, BBLine, tuple]


def coerce(cfg) -> tuple:
    """Any config -> the positional tuple the builders consume. The ONE bridge; nothing else unpacks."""
    return cfg.as_tuple() if isinstance(cfg, (KLine, BBLine)) else tuple(cfg)


def from_tuple(cfg) -> LineCfg:
    """Positional tuple -> the named form. For reading a legacy config back out."""
    if isinstance(cfg, (KLine, BBLine)):
        return cfg
    kind = cfg[0]
    if kind == 'k':
        _, rsi, stc, k_len, src = cfg
        return KLine(k_len=k_len, rsi=rsi, stc=stc, src=src)
    if kind == 'bb':
        _, length, mult, src = cfg
        return BBLine(length=length, mult=float(mult), src=src)
    raise ValueError(f'unknown line type {kind!r}')


def from_db_row(c) -> tuple:
    """A vw_indicator_configs_live row -> the positional tuple. The ONLY place the DB column order is read."""
    if c['lt'] == 'bb':
        return BBLine(length=c['ic_bb_len'], mult=float(c['ic_bb_mult']), src=c['src']).as_tuple()
    return KLine(k_len=c['ic_k_len'], rsi=c['ic_rsi_len'], stc=c['ic_stc_len'], src=c['src']).as_tuple()


def override(tf_seconds: int, cfg: LineCfg, value_mode: str = 'emerging') -> tuple:
    """Build ONE line-override entry: (tf_seconds, cfg_tuple, value_mode).

    This is the shape BiasWindow(line_overrides=...) / Jig(overrides=...) expect. Use the jig's
    kline()/bbline() helpers rather than calling this directly — they name the TF in minutes too."""
    return (int(tf_seconds), coerce(cfg), value_mode)


class LineStore:
    """SRP: resolve `ind_name` -> (tf_seconds, cfg-tuple, value_mode), from the DB or an in-memory override.

    Moved out of bias_machine 0714: bias_machine is the bias ENGINE; it consumes configs, it does not own
    them. This class already had exactly one job — it was just filed in the wrong module."""

    def __init__(self, db):
        self._db = db
        self._cache = {}

    def _fetch(self, ind_name):
        if ind_name not in self._cache:
            r = self._db.execute(
                '''SELECT ic_line_type lt, ic_src src, ic_bb_len, ic_bb_mult, ic_rsi_len,
                          ic_stc_len, ic_k_len, itf_seconds, value_mode
                   FROM vw_indicator_configs_live WHERE ind_name = %s''', (ind_name,), fetch=True)
            if not r:
                raise ValueError(f'no live indicator_configs for {ind_name!r}')
            c = r[0]
            self._cache[ind_name] = (int(c['itf_seconds']), from_db_row(c), c['value_mode'] or 'closed')
        return self._cache[ind_name]

    def inject(self, overrides):
        """Sweep/test hook: {ind_name: (tf_seconds, cfg, value_mode)}. `cfg` may be named OR a legacy tuple —
        it is coerced here, so a caller can never leave an un-bridged named cfg in the cache."""
        for name, (tf, cfg, vm) in (overrides or {}).items():
            self._cache[name] = (int(tf), coerce(cfg), vm)

    def resolve(self, ind_name):
        return self._fetch(ind_name)[:2]                  # (tf_seconds, cfg-tuple)

    def value_mode(self, ind_name):
        """'emerging' | 'closed' from vw_indicator_configs_live (#42). Null -> 'closed' (the conservative
        historical default; set ic_ivm_pk to make it explicit)."""
        return self._fetch(ind_name)[2]
