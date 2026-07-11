###
es = entry-side sign — the arm's breach side: +1 = high breach, −1 = low breach. Set when the arm fires.

- Its partner is bd = bias/trade direction = −es — a hi breach (es=+1) → SHORT (bd=−1); a lo breach (es=−1) → LONG (bd=+1).
- In s5Mage_arm the fire returns (k, br, −br) = (bar, es, bd).

So "predict_breach(s3r) == es" = s3r is predicted to breach on the same side as the arm — i.e. the market's predicted to keep pushing the way the arm already broke (more leg coming), which is exactly the "veto the premature reversal" signal.

