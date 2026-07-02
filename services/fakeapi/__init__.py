"""fake-API — a mock of the Bybit v5 contract, fed by the REAL order book, so the o9-live
adapter is a true drop-in (swap base_url → real Bybit, zero strategy change). Test-only container.
Contract skeleton here; fill model (OrderBookWalker) + position store (MatchingEngine/FxStore) = milestone ③.
See docs/o9_live_classes.md."""
