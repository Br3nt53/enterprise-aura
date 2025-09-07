from __future__ import annotations
from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True, slots=True)
class Position3D:
    x: float
    y: float
    z: float = 0.0

    def distance_to(self, other: "Position3D") -> float:
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        return float((dx*dx + dy*dy + dz*dz) ** 0.5)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=float)
