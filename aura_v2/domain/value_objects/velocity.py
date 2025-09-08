# aura_v2/domain/value_objects/velocity.py
from dataclasses import dataclass
import numpy as np


@dataclass(slots=True)
class Velocity2D:
    """Represents a mutable velocity in 2D space."""

    vx: float = 0.0
    vy: float = 0.0

    @property
    def magnitude(self) -> float:
        return float(np.linalg.norm([self.vx, self.vy]))


@dataclass(slots=True)
class Velocity3D:
    """Represents a mutable velocity in 3D space."""

    vx: float = 0.0
    vy: float = 0.0
    vz: float = 0.0

    @property
    def magnitude(self) -> float:
        return float(np.linalg.norm([self.vx, self.vy, self.vz]))
