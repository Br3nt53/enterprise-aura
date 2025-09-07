"""
Position value objects.

Defines two and three dimensional positions with convenience methods for
distance computation and conversion to NumPy arrays.  Position objects
are immutable dataclasses to ensure that once created they are not
accidentally mutated.  The ``distance_to`` method computes Euclidean
distance between two positions.  The ``to_array`` method returns a
``numpy.ndarray`` representing the coordinate in row vector form.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np  # type: ignore

@dataclass(frozen=True, slots=True)
class Position3D:
    """Immutable three‑dimensional position.

    Coordinates are expressed in metres.  The default value for ``z``
    is zero, so you can omit it for planar problems.
    """
    x: float
    y: float
    z: float = 0.0

    def distance_to(self, other: "Position3D") -> float:
        """Return the Euclidean distance to another position."""
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return float((dx * dx + dy * dy + dz * dz) ** 0.5)

    def to_array(self) -> np.ndarray:
        """Return the position as a length‑3 NumPy array."""
        return np.array([self.x, self.y, self.z], dtype=float)
