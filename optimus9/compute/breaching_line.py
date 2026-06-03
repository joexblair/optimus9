"""
breaching_line — per-line 4-state breach machine (BL). Spec: bl_machine_design.md.

States: 0 idle · 1 breached · 2 curled · 3 complete.
  0→1  K breaches (actual) or is predicted to, while outside the 30:70 fence
  1→2  the K line curls (ROC reverses past floor) — MANDATORY
  2→3  any exit method completes (BB OB→IB / BB non-subtle ROC / BB×K toward IB)
  2→1  re-breach (the bobbing)
  3→1  re-breach / re-predict while completing (re-pulled)
  3→0  reset (single-line: next bar; multi-line gate-hold is parked)

Harvested from the Pine (260604 BL machine.txt): states, ROC/curl, prediction.
Dropped: the Pine's exit logic (→ the 3 new methods) + the 7-bar fresh-breach hack.
Thresholds are tunable — calibrated against the manual Pine application (Target 1).
"""
import numpy as np

from ..constants import BOUNDARY_HI, BOUNDARY_LO, FENCE_HI, FENCE_LO

HI, LO = BOUNDARY_HI, BOUNDARY_LO    # OOB breach detection (85/15)
# FENCE_HI/FENCE_LO (30:70) are the no-engagement base, imported from constants —
# its own tuning concern, NOT the RSI rescale. bl_detect pads it via --fence_pad.


def predict_breach(k, bb_m, bb_M, hi=HI, lo=LO, fence_hi=FENCE_HI, fence_lo=FENCE_LO):
    """Per-bar predicted-breach direction {+1 hi, -1 lo, 0 none}.

    A K breach is predicted when the BB anchor overshoots the boundary by MORE than
    K undershoots it (the BB's pull carries K through), while K sits in the engage
    band (outside the 30:70 fence) and is not yet breached. The anchor uses BOTH BB
    lines: max(m,M) for a hi breach, min(m,M) for a lo breach (hand-curated lines).

    Direction confirmed by Joe's examples (HI=85, K=75):
      m=56/M=120 → anchor 120, (120-85)=35 > (85-75)=10 → True
      m=56/M=90  → anchor 90,  (90-85)=5  > 10           → False
    """
    k, bb_m, bb_M = np.asarray(k, float), np.asarray(bb_m, float), np.asarray(bb_M, float)
    anchor_hi = np.maximum(bb_m, bb_M)
    anchor_lo = np.minimum(bb_m, bb_M)
    pred_hi = ((k >= fence_hi) & (k < hi) & (anchor_hi >= hi) &
               ((anchor_hi - hi) > (hi - k)))
    pred_lo = ((k <= fence_lo) & (k > lo) & (anchor_lo <= lo) &
               ((lo - anchor_lo) > (k - lo)))
    out = np.zeros(len(k), dtype=np.int8)
    out[pred_hi] =  1
    out[pred_lo] = -1
    return out


class BreachingLine:
    def __init__(self, mult=1, curl_floor=1.0, curl_lookback=7, exit_lookback=2,
                 flatten=0.5, pseudo_cross=15.0, grace=2,
                 hi=HI, lo=LO, fence_hi=FENCE_HI, fence_lo=FENCE_LO):
        self.mult          = int(mult)
        self.curl_floor    = float(curl_floor)
        self.curl_lookback = int(curl_lookback)   # curl slope window (~bars before K reverses)
        self.exit_lookback = int(exit_lookback)
        self.flatten       = float(flatten)
        self.pseudo_cross  = float(pseudo_cross)
        self.grace         = int(grace)           # bars to wait for a curl after an early exit3
        self.hi, self.lo   = float(hi), float(lo)
        self.fence_hi, self.fence_lo = float(fence_hi), float(fence_lo)

    # ── public ───────────────────────────────────────────────────────────────
    def run(self, k, bb_m, bb_M) -> dict:
        """Walk the bars; return per-bar arrays: state, breach_dir, predicted,
        exit1/exit2/exit3 (the bools the persistence table needs).

        Dormancy model (Target-1 review): a line inside the 30:70 fence is dormant
        (state 0). Re-arming to 1 needs a FRESH breach (an IB→OOB crossing or a
        fresh prediction) — so a *pegged* OOB line stays at 3 instead of bobbing,
        while a line genuinely moving in and out re-arms on each re-entry. Curl is
        evaluated only while OOB. Curl + an exit on the same bar cascades 1→2→3.
        """
        k    = np.asarray(k, float)
        bb_m = np.asarray(bb_m, float)
        bb_M = np.asarray(bb_M, float)
        n    = len(k)
        m    = self.mult

        pred = predict_breach(k, bb_m, bb_M, self.hi, self.lo, self.fence_hi, self.fence_lo)
        oob  = (k >= self.hi) | (k <= self.lo)
        in_fence = (k > self.fence_lo) & (k < self.fence_hi)
        sig  = np.zeros(n, np.int8)
        sig[(k >= self.hi) | (pred == 1)]  =  1
        sig[(k <= self.lo) | (pred == -1)] = -1

        cl = self.curl_lookback                              # curl: short local slope (7)
        slope_k = np.full(n, np.nan); slope_k[cl:] = k[cl:]  - k[:-cl]
        slope_M = np.full(n, np.nan); slope_M[m:] = bb_M[m:] - bb_M[:-m]
        bbM_oob = (bb_M >= self.hi) | (bb_M <= self.lo)
        bbM_ib  = ~bbM_oob

        state, bdir = 0, 0
        pend3 = 0                                             # exit3-before-curl grace countdown
        o_state = np.zeros(n, np.int8); o_dir = np.zeros(n, np.int8)
        o_e1 = np.zeros(n, bool); o_e2 = np.zeros(n, bool); o_e3 = np.zeros(n, bool)

        for i in range(n):
            cur_dir   = int(sig[i]) if sig[i] != 0 else bdir
            fresh_oob = bool(oob[i]      and (i == 0 or not oob[i - 1]))
            fresh_prd = bool(pred[i] != 0 and (i == 0 or pred[i - 1] == 0))
            fresh_eng = fresh_oob or fresh_prd                 # a genuinely new breach
            curl = bool(oob[i] and (                           # curl only while OOB
                (cur_dir == 1  and slope_k[i] < -self.curl_floor) or
                (cur_dir == -1 and slope_k[i] >  self.curl_floor)))
            e1 = self._exit_ob_to_ib(bbM_ib, bbM_oob, i)
            e2 = self._exit_nonsubtle_roc(slope_M, i)
            e3 = self._exit_cross_toward_ib(cur_dir, bb_M, k, i)
            any_exit = e1 or e2 or e3

            if in_fence[i]:
                ns, nb = 0, 0                                  # dead zone → dormant
            else:
                ns, nb = state, bdir
                if state == 0:
                    if fresh_eng:
                        ns, nb = 1, cur_dir
                elif state == 1:
                    nb = cur_dir
                    if curl:
                        ns = 2
                        if any_exit or pend3 > 0:              # curl + an exit now, OR an exit3
                            ns = 3                             # within the grace window → complete
                    elif e3:
                        pend3 = self.grace                     # exit3 before curl → wait for it
                    elif pend3 > 0:
                        pend3 -= 1                             # tick the grace window down
                elif state == 2:
                    nb = cur_dir
                    if fresh_oob:
                        ns = 1                                 # re-breach (bobbing)
                    elif any_exit:
                        ns = 3
                elif state == 3:
                    if fresh_eng:
                        ns, nb = 1, cur_dir                    # re-armed by a fresh breach
                    # else stay 3 (pegged → dormant)
            if ns != 1:
                pend3 = 0                                      # grace only lives inside state 1
            state, bdir = ns, nb
            o_state[i], o_dir[i] = state, bdir
            o_e1[i], o_e2[i], o_e3[i] = e1, e2, e3

        return {'state': o_state, 'breach_dir': o_dir, 'predicted': pred != 0,
                'exit1': o_e1, 'exit2': o_e2, 'exit3': o_e3, 'slope_k': slope_k}

    # ── exit methods (parameterised; calibrated against Pine) ─────────────────
    def _exit_ob_to_ib(self, bbM_ib, bbM_oob, i) -> bool:
        """(1) BB was OB within the lookback and is now IB."""
        return bool(bbM_ib[i] and bbM_oob[max(0, i - self.exit_lookback):i].any())

    def _exit_nonsubtle_roc(self, slope_M, i) -> bool:
        """(2) BB has a non-subtle ROC — a sharp change: slope reverses (up→down)
        or flattens (|slope| collapses below the floor)."""
        if i == 0 or np.isnan(slope_M[i]) or np.isnan(slope_M[i - 1]):
            return False
        reversed_ = np.sign(slope_M[i]) != np.sign(slope_M[i - 1]) and slope_M[i - 1] != 0
        flattened = abs(slope_M[i]) <= self.flatten and abs(slope_M[i - 1]) > self.flatten
        return bool(reversed_ or flattened)

    def _exit_cross_toward_ib(self, cur_dir, bb_M, k, i) -> bool:
        """(3) BB × K toward IB — the BB cuts through the K heading in-boundary.
        Pseudo-cross: counts when within `pseudo_cross` and converging."""
        if i == 0 or cur_dir == 0:
            return False
        gap_prev = bb_M[i - 1] - k[i - 1]
        if cur_dir == 1:                            # BB above K, cutting down through it
            crossed = bb_M[i] < k[i] and bb_M[i - 1] >= k[i - 1]
            pseudo  = bb_M[i] < bb_M[i - 1] and 0 < gap_prev <= self.pseudo_cross
        else:                                       # BB below K, cutting up through it
            crossed = bb_M[i] > k[i] and bb_M[i - 1] <= k[i - 1]
            pseudo  = bb_M[i] > bb_M[i - 1] and 0 < -gap_prev <= self.pseudo_cross
        return bool(crossed or pseudo)
