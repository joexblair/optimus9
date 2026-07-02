"""Bybit v5 error codes the mock reproduces (so the adapter meets the SAME failures as prod).
Bybit returns HTTP 200 with a non-zero retCode for business/auth errors — not an HTTP error status."""


class FakeApiError(Exception):
    """Carries a Bybit retCode/retMsg → serialized into the envelope by the app's handler."""

    def __init__(self, ret_code: int, ret_msg: str):
        super().__init__(f"[{ret_code}] {ret_msg}")
        self.ret_code = ret_code
        self.ret_msg = ret_msg


# the subset we emulate (extend as routes grow)
TS_OUT_OF_WINDOW = 10002   # req timestamp outside recv_window (clock skew)
API_KEY_INVALID = 10003    # unknown api key
SIGN_ERROR = 10004         # signature mismatch / missing auth headers
LEVERAGE_UNCHANGED = 110043  # set-leverage to the current value
