# aura_v2/domain/value_objects/position.py
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True)  # <-- CRITICAL FIX: `frozen=True` has been REMOVED.
class Position3D:
    """Represents a mutable position in 3D space."""
    x: float
    y: float
    z: float

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)

    def distance_to(self, other: 'Position3D') -> float:
        return float(np.linalg.norm(self.to_array() - other.to_array()))