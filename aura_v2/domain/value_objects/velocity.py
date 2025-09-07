"""
Velocity value objects.

Provides immutable three dimensional velocities.  Velocities
express rates of change in metres per second.  Convenience methods are
provided to compute the speed (magnitude) and convert the velocity to a
NumPy array.
"""

from dataclasses import dataclass
import numpy as np  # type: ignore

@dataclass(frozen=True, slots=True)
class Velocity3D:
    """Immutable three‑dimensional velocity."""
    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0

    @property
    def magnitude(self) -> float:
        """Return the magnitude (speed) of the velocity vector."""
        return float((self.vx * self.vx + self.vy * self.vy + self.vz * self.vz) ** 0.5)

    def to_array(self) -> np.ndarray:
        """Return the velocity as a length‑3 NumPy array."""
        return np.array([self.vx, self.vy, self.vz], dtype=float)
