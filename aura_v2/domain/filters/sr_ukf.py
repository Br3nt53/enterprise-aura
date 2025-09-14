from __future__ import annotations
# Compatibility shim: delegate to the standard UKF for tests.
from .ukf import UKF as _BaseUKF

class SquareRootUKF(_BaseUKF):
    """Expose the same API as UKF; backed by UKF implementation."""
    pass
