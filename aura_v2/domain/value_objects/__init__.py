"""
Value objects for the AURA domain.

This package defines immutable value‑object types used throughout the
tracking domain.  Value objects encapsulate primitive values (e.g. numbers)
and provide convenience methods such as vector arithmetic, distance
computation or array conversion.  Using value objects promotes clarity in
function signatures and guards against unit/coordinate confusion.
"""

from .position import Position3D
from .velocity import Velocity3D
from .confidence import Confidence

__all__ = ["Position3D", "Velocity3D", "Confidence"]
