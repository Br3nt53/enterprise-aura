# aura_v2/domain/value_objects/position_2d.py
from dataclasses import dataclass
import numpy as np

@dataclass(slots=True)
class Position2D:
    """Represents a mutable position in 2D space."""
    x: float
    y: float

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=float)

    def distance_to(self, other: 'Position2D') -> float:
        return float(np.linalg.norm(self.to_array() - other.to_array()))

# aura_v2/domain/value_objects/velocity_2d.py
@dataclass(slots=True)
class Velocity2D:
    """Represents a mutable velocity in 2D space."""
    vx: float = 0.0
    vy: float = 0.0

    @property
    def magnitude(self) -> float:
        return float(np.linalg.norm([self.vx, self.vy]))